import html
import re
from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass
from itertools import pairwise
from typing import NamedTuple

from spacy.tokens import Doc, Token

from ..cohesion_stats import find_connectors
from ..constants import (
    COMPLEX_SYL_FACTOR,
    COMPOUND_PREPOSITIONS,
    CONNECTOR_CLASSES,
    CONNECTOR_TYPES,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYERS_DESC,
    HIGHLIGHT_SYNTAX_LAYERS,
    HIGHLIGHT_TAGGED_LAYERS,
    LONG_SENT_WORD_FACTOR,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    PASSIVE_AUX,
    SE_PASSIVE_DEP,
)
from ..datasets.freq_dict import lemma_key
from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..lexical_stats import get_rank
from ..style_stats import expand_phrases, is_stopword
from ..syllables import count_syllables
from ..syntax_stats import (
    AUXILIARY_DEPS,
    base_dep,
    find_split_predicates,
    get_words,
    is_agentless,
    is_de_modifier,
    is_gerund_clause,
    is_participle_clause,
    is_passive,
    is_word,
)
from ..utils import (
    check_sequence,
    find_phrases,
    is_verbal_noun,
    iter_doc_tokens,
    iter_text_sents,
    iter_text_words,
)

SPANISH_WORD = re.compile(r"[a-záéíóúüñ]{2,}", re.IGNORECASE)
CSS = """\
.ests-highlight { line-height: 1.7; }
.ests-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ests-highlight-legend .ests-hl { padding: 0 0.3em; }
.ests-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ests-highlight-text { white-space: pre-wrap; }
.ests-highlight .ests-hl.ests-hl-long_sents, .ests-highlight .ests-hl.ests-hl-complex_words, .ests-highlight .ests-hl.ests-hl-rare_words, .ests-highlight .ests-hl.ests-hl-stopwords, .ests-highlight .ests-hl.ests-hl-passive, .ests-highlight .ests-hl.ests-hl-verbal_nouns, .ests-highlight .ests-hl.ests-hl-compound_prepositions, .ests-highlight .ests-hl.ests-hl-cliches, .ests-highlight .ests-hl.ests-hl-parentheticals { color: #1f2328; border-radius: 2px; }
.ests-hl-long_sents { background: #fef9c3; }
.ests-hl-complex_words { background: #fed7aa; }
.ests-hl-rare_words { background: #e5e7eb; }
.ests-hl-passive { background: #fecaca; }
.ests-hl-verbal_nouns { background: #e9d5ff; }
.ests-hl-compound_prepositions { background: #a7f3d0; }
.ests-hl-cliches { background: #fbcfe8; }
.ests-hl-stopwords { background: #bae6fd; }
.ests-hl-parentheticals { background: #d9f99d; }
.ests-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ests-hl-gerund_clauses { border-bottom: 2px solid #0d9488; }
.ests-hl-de_chains { border-bottom: 2px solid #b45309; }
.ests-hl-split_predicates { border-bottom: 2px solid #dc2626; }
.ests-hl-connectors { border-bottom: 2px dashed #2563eb; }
"""


class Word(NamedTuple):
    start: int
    end: int
    text: str
    pos: str | None = None
    lemma: str | None = None


class Sent(NamedTuple):
    start: int
    end: int
    n_words: int


@dataclass(frozen=True)
class Highlight:
    """
    Highlighted fragment of a text

    Arguments:
        start (int): Position of the first character of the fragment
        end (int): Position after the last character of the fragment
        layer (str): Layer of the highlighting
        note (str): Explanation of the fragment for the tooltip
    """

    start: int
    end: int
    layer: str
    note: str = ""


class HighlightedText:
    """
    Class for highlighting a text by layers, in the manner of the style checkers

    Description:
        Every layer marks the fragments the statistics of the library count:
            long_sents - sentences of long_sent_word_factor words or more (BasicStats)
            complex_words - words of complex_syl_factor syllables or more (BasicStats)
            rare_words - words with a lemma beyond the embedded top 10000 (LexicalStats)
            passive - passive verb forms with their auxiliary or se (SyntaxStats)
            participle_clauses - participial clauses (SyntaxStats)
            gerund_clauses - gerund clauses (SyntaxStats)
            de_chains - chains of complements with de and their head (SyntaxStats)
            split_predicates - split predicates from the verb to the noun (SyntaxStats)
            verbal_nouns - nouns derived from a verb (StyleStats)
            compound_prepositions - compound prepositions (StyleStats)
            cliches - clichés of OFFICIALESE_CLICHES or of the list passed (StyleStats)
            stopwords - stopwords of STOPWORDS or of the list passed, the water (StyleStats)
            parentheticals - parenthetical expressions (StyleStats)
            connectors - discourse markers, with the class and the kind in the note
                (CohesionStats)
        The layers are grouped in HIGHLIGHT_LAYER_GROUPS: readability, syntax,
        officialese, style. The syntactic layers are read from the dependency
        tree and need a Doc with a parse, verbal_nouns needs a Doc with the
        parts of speech and the lemmas, long_sents of a Doc needs the sentence
        boundaries. The layers of HIGHLIGHT_DEFAULT_LAYERS the source allows are
        on by default (long sentences, complex words, passive, chains of de,
        split predicates, clichés); layers="all" turns on every layer allowed
        The result shows in Jupyter as HTML with styles and a legend; to_html
        returns the same markup for documentation and web applications. The
        fragments of different layers may overlap: the text is cut into
        segments with a set of CSS classes each

    Example:
        >>> from ests.visualizers import highlight
        >>> text = (
        ...     "Se procedió a la revisión del expediente en el marco del plan a la mayor "
        ...     "brevedad. Sin embargo, el gato duerme."
        ... )
        >>> ht = highlight(text)
        >>> ht.counts
        {'long_sents': 0, 'complex_words': 5, 'cliches': 2}
        >>> ht = highlight(text, layers=["cliches", "compound_prepositions"])
        >>> ht.highlights[0]
        Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»')
        >>> highlight(text, layers="parentheticals").to_html(legend=False, css=False)
        '<div class="ests-highlight"><div class="ests-highlight-text">Se procedió ... <span class="ests-hl ests-hl-parentheticals" title="parenthetical expression: «sin embargo»">Sin embargo</span>, el gato duerme.</div></div>'

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        layers (list[str]|str): Layers of the highlighting; the layers of
            HIGHLIGHT_DEFAULT_LAYERS the source allows if not set; "all" - every
            layer the source allows
        long_sent_word_factor (int): Minimum number of words of a long sentence
        complex_syl_factor (int): Minimum number of syllables of a complex word
        stopwords (list[str]): Stopwords; STOPWORDS and the one-word parenthetical
            expressions if not set
        cliches (list[str]): List of clichés; OFFICIALESE_CLICHES if not set

    Attributes:
        text (str): Text of the source
        layers (tuple[str]): Layers turned on, in the order of drawing
        highlights (tuple[Highlight]): Highlighted fragments in the order of the text
        counts (dict[str, int]): Number of fragments of every layer

    Methods:
        to_html: Getting the HTML markup of the highlighted text

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words
        ParameterError: If a layer is unknown or not allowed by the source
        ParameterError: If a threshold of a layer is below one
    """

    def __init__(
        self,
        source: str | Doc,
        layers: Sequence[str] | str | None = None,
        long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        stopwords: Sequence[str] | None = None,
        cliches: Sequence[str] | None = None,
    ):
        tagged = False
        doc = None
        if isinstance(source, Doc):
            self.text = source.text
            tagged = source.has_annotation("POS") and source.has_annotation("LEMMA")
            words = get_doc_words(source, tagged)
            sents = get_doc_sents(source) if source.has_annotation("SENT_START") else None
            doc = source if source.has_annotation("DEP") else None
        elif isinstance(source, str):
            self.text = source
            words = get_text_words(source)
            sents = get_text_sents(source, words)
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not words:
            raise SourceError("The data source has no words")
        if long_sent_word_factor < 1:
            raise ParameterError("The number of words of a long sentence must be greater than 0")
        if complex_syl_factor < 1:
            raise ParameterError(
                "The number of syllables of a complex word must be greater than 0"
            )
        if stopwords is not None:
            check_sequence(stopwords, "stopwords")
            stopwords = tuple(stopwords)
        if cliches is not None:
            check_sequence(cliches, "clichés")
            cliches = tuple(cliches)
        available = [
            layer
            for layer in HIGHLIGHT_LAYERS_DESC
            if not (layer == "long_sents" and sents is None)
            and not (layer in HIGHLIGHT_SYNTAX_LAYERS and doc is None)
            and not (layer in HIGHLIGHT_TAGGED_LAYERS and not tagged)
        ]
        self.layers = select_layers(layers, available)

        finders: dict[str, Callable[[], list[Highlight]]] = {
            "long_sents": lambda: find_long_sents(sents or [], long_sent_word_factor),
            "complex_words": lambda: find_complex_words(words, complex_syl_factor),
            "rare_words": lambda: find_rare_words(words),
            "stopwords": lambda: find_stopwords(words, stopwords),
            "verbal_nouns": lambda: find_verbal_nouns(words),
            "compound_prepositions": lambda: find_compound_prepositions(words),
            "cliches": lambda: find_cliches(words, cliches),
            "parentheticals": lambda: find_parentheticals(words),
            "connectors": lambda: find_connector_highlights(words, sents),
            "passive": lambda: find_passive(doc) if doc else [],
            "participle_clauses": lambda: find_participle_clauses(doc) if doc else [],
            "gerund_clauses": lambda: find_gerund_clauses(doc) if doc else [],
            "de_chains": lambda: find_de_chains(doc) if doc else [],
            "split_predicates": lambda: find_split_predicate_highlights(doc) if doc else [],
        }
        highlights = [h for layer in self.layers for h in finders[layer]()]
        self.highlights = tuple(sorted(highlights, key=lambda h: (h.start, -h.end)))

    @property
    def counts(self) -> dict[str, int]:
        return {
            layer: sum(1 for h in self.highlights if h.layer == layer) for layer in self.layers
        }

    def to_html(self, legend: bool = True, css: bool = True) -> str:
        """
        Getting the HTML markup of the highlighted text

        Description:
            The markup is a div of the class ests-highlight with the legend and
            its counts and the text, where the highlighted segments are wrapped
            in a span of the classes ests-hl and ests-hl-<layer>; the notes of
            the fragments go to the title attribute. Line breaks are kept as
            character references, so the markup can be put into Markdown with no
            blank line inside the block

        Arguments:
            legend (bool): Add the legend with the counts of the fragments
            css (bool): Add the styles of the layers

        Returns:
            str: HTML markup
        """
        parts = ['<div class="ests-highlight">']
        if css:
            parts.append(f"<style>{CSS}</style>")
        if legend:
            items = "".join(
                f'<span><span class="ests-hl ests-hl-{layer}">{HIGHLIGHT_LAYERS_DESC[layer]}</span>'
                f'<span class="ests-highlight-count">{count}</span></span>'
                for layer, count in self.counts.items()
            )
            parts.append(f'<div class="ests-highlight-legend">{items}</div>')
        parts.append(f'<div class="ests-highlight-text">{self._render_text()}</div></div>')
        return "".join(parts)

    def _repr_html_(self) -> str:
        return self.to_html()

    def __repr__(self) -> str:
        return f"HighlightedText(counts={self.counts})"

    def _render_text(self) -> str:
        chunks = []
        for start, end, active in split_segments(len(self.text), self.highlights):
            chunk = html.escape(self.text[start:end]).replace("\n", "&#10;")
            if active:
                active.sort(key=lambda h: self.layers.index(h.layer))
                classes = " ".join(f"ests-hl-{h.layer}" for h in active)
                notes = "; ".join(dict.fromkeys(h.note for h in active if h.note))
                title = f' title="{html.escape(notes)}"' if notes else ""
                chunk = f'<span class="ests-hl {classes}"{title}>{chunk}</span>'
            chunks.append(chunk)
        return "".join(chunks)


def highlight(
    source: str | Doc,
    layers: Sequence[str] | str | None = None,
    long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
    complex_syl_factor: int = COMPLEX_SYL_FACTOR,
    stopwords: Sequence[str] | None = None,
    cliches: Sequence[str] | None = None,
) -> HighlightedText:
    """
    Highlighting a text by layers, in the manner of the style checkers

    Description:
        The layers of HIGHLIGHT_LAYERS_DESC: long sentences, complex and rare
        words, passive, participial and gerund clauses, chains of de, split
        predicates, verbal nouns, compound prepositions, clichés, stopwords,
        parenthetical expressions, connectors; the syntactic layers need a Doc
        with a parse, the verbal nouns a Doc with the parts of speech and the
        lemmas, see HighlightedText

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        layers (list[str]|str): Layers of the highlighting; the layers of
            HIGHLIGHT_DEFAULT_LAYERS the source allows if not set; "all" - every
            layer the source allows
        long_sent_word_factor (int): Minimum number of words of a long sentence
        complex_syl_factor (int): Minimum number of syllables of a complex word
        stopwords (list[str]): Stopwords; STOPWORDS and the one-word parenthetical
            expressions if not set
        cliches (list[str]): List of clichés; OFFICIALESE_CLICHES if not set

    Returns:
        HighlightedText: Highlighted text with an HTML view for Jupyter
    """
    return HighlightedText(
        source,
        layers,
        long_sent_word_factor=long_sent_word_factor,
        complex_syl_factor=complex_syl_factor,
        stopwords=stopwords,
        cliches=cliches,
    )


def select_layers(layers: Sequence[str] | str | None, available: Sequence[str]) -> tuple[str, ...]:
    """
    Selecting the layers of the highlighting

    Arguments:
        layers (list[str]|str): Layers asked for; the layers of
            HIGHLIGHT_DEFAULT_LAYERS among the available ones if not set, "all" -
            every available layer
        available (list[str]): Layers the data source allows

    Returns:
        tuple[str]: Layers in the order of drawing

    Raises:
        ParameterError: If a layer is unknown or not allowed by the source, or
            the layers are not a list of names
    """
    if layers is None:
        return tuple(layer for layer in HIGHLIGHT_DEFAULT_LAYERS if layer in available)
    if layers == "all":
        return tuple(available)
    if isinstance(layers, str):
        layers = [layers]
    try:
        layers = list(layers)
    except TypeError as e:
        raise ParameterError("The layers must be a list of names or a string") from e
    for layer in layers:
        if layer not in HIGHLIGHT_LAYERS_DESC:
            raise ParameterError(f"Unknown layer of the highlighting: {layer}")
        if layer not in available:
            if layer == "long_sents":
                requirement = "the sentence boundaries in the Doc"
            elif layer in HIGHLIGHT_TAGGED_LAYERS:
                requirement = "a Doc with the parts of speech and the lemmas"
            else:
                requirement = "a Doc with a dependency parse"
            raise ParameterError(f"The layer {layer} needs {requirement}")
    return tuple(layer for layer in HIGHLIGHT_LAYERS_DESC if layer in layers)


def get_text_words(text: str) -> list[Word]:
    """
    Extracting the words of a string with their positions

    Description:
        The tokenizer of the blank Spanish pipeline, the punctuation dropped as in
        WordsExtractor (iter_text_words)

    Arguments:
        text (str): Text string

    Returns:
        list[Word]: Words with their positions
    """
    return [Word(start, end, text) for start, end, text in iter_text_words(text)]


def get_text_sents(text: str, words: Sequence[Word]) -> list[Sent]:
    """
    Extracting the sentences of a string with their positions and numbers of words

    Description:
        The sentences of SentsExtractor (iter_text_sents); a word belongs to the
        sentence of its first character

    Arguments:
        text (str): Text string
        words (list[Word]): Words of the text with their positions

    Returns:
        list[Sent]: Sentences with their positions and numbers of words
    """
    sents = []
    index = 0
    for start, end, _ in iter_text_sents(text):
        n_words = 0
        while index < len(words) and words[index].start < end:
            n_words += words[index].start >= start
            index += 1
        sents.append(Sent(start, end, n_words))
    return sents


def get_doc_words(doc: Doc, tagged: bool) -> list[Word]:
    """
    Extracting the words of a Doc object with their positions

    Description:
        The words of iter_doc_tokens; a Doc with the parts of speech and the
        lemmas gives both to every word

    Arguments:
        doc (Doc): Doc object
        tagged (bool): Whether the Doc has the parts of speech and the lemmas

    Returns:
        list[Word]: Words with their positions
    """
    return [
        Word(
            token.idx,
            token.idx + len(token),
            token.text,
            token.pos_ if tagged else None,
            token.lemma_ if tagged else None,
        )
        for token in iter_doc_tokens(doc)
    ]


def get_doc_sents(doc: Doc) -> list[Sent]:
    """
    Extracting the sentences of a Doc object with their positions and numbers of words

    Description:
        The whitespace tokens at the edges of a sentence are left out of its
        positions: the sentencizer puts a boundary at the line break after a
        period

    Arguments:
        doc (Doc): Doc object with the sentence boundaries

    Returns:
        list[Sent]: Sentences with their positions and numbers of words
    """
    sents = []
    for sent in doc.sents:
        tokens = [token for token in sent if not token.is_space]
        if tokens:
            start = min(token.idx for token in tokens)
            end = max(token.idx + len(token) for token in tokens)
            sents.append(Sent(start, end, sum(1 for _ in iter_doc_tokens(sent))))
    return sents


def plural(n: int, noun: str) -> str:
    """
    Writing a number with its noun in the singular or the plural

    Arguments:
        n (int): Number
        noun (str): Noun in the singular, whose plural adds s

    Returns:
        str: Number with the noun
    """
    return f"{n} {noun}" if n == 1 else f"{n} {noun}s"


def find_long_sents(sents: Iterable[Sent], long_sent_word_factor: int) -> list[Highlight]:
    """
    Finding the long sentences

    Arguments:
        sents (list[Sent]): Sentences with their positions and numbers of words
        long_sent_word_factor (int): Minimum number of words of a long sentence

    Returns:
        list[Highlight]: Fragments of the layer long_sents
    """
    return [
        Highlight(
            sent.start, sent.end, "long_sents", f"long sentence, {plural(sent.n_words, 'word')}"
        )
        for sent in sents
        if sent.n_words >= long_sent_word_factor
    ]


def find_complex_words(words: Iterable[Word], complex_syl_factor: int) -> list[Highlight]:
    """
    Finding the complex words

    Arguments:
        words (list[Word]): Words with their positions
        complex_syl_factor (int): Minimum number of syllables of a complex word

    Returns:
        list[Highlight]: Fragments of the layer complex_words
    """
    highlights = []
    for word in words:
        n_syllables = count_syllables(word.text)
        if n_syllables >= complex_syl_factor:
            note = f"complex word, {plural(n_syllables, 'syllable')}"
            highlights.append(Highlight(word.start, word.end, "complex_words", note))
    return highlights


def find_stopwords(
    words: Iterable[Word], stopwords: Sequence[str] | None = None
) -> list[Highlight]:
    """
    Finding the stopwords

    Description:
        The stopwords of is_stopword or of the list passed, in any case, as the
        water content of StyleStats counts them

    Arguments:
        words (list[Word]): Words with their positions
        stopwords (list[str]): List of stopwords; is_stopword if not set

    Returns:
        list[Highlight]: Fragments of the layer stopwords
    """
    if stopwords is not None:
        stopwords_set = {word.lower() for word in stopwords}
        matches = [word for word in words if word.text.lower() in stopwords_set]
    else:
        matches = [word for word in words if is_stopword(word.text)]
    return [Highlight(word.start, word.end, "stopwords", "stopword") for word in matches]


def find_rare_words(words: Iterable[Word]) -> list[Highlight]:
    """
    Finding the rare words

    Description:
        The words with a lemma beyond the embedded list of the 10,000 most
        frequent lemmas (get_rank), as the share p_beyond_top10000 of
        LexicalStats counts them: the key of lemma_key, the lower-case form for
        a proper noun of a tagged Doc. Only the words of two Spanish letters or
        more are looked at, and the stopwords are not: numbers, words with a
        hyphen or a digit and the words of other alphabets are not highlighted

    Arguments:
        words (list[Word]): Words with their positions

    Returns:
        list[Highlight]: Fragments of the layer rare_words
    """
    return [
        Highlight(word.start, word.end, "rare_words", "rare word: beyond the top 10000")
        for word in words
        if SPANISH_WORD.fullmatch(word.text)
        and not is_stopword(word.text)
        and get_rank(lemma_key(word.text, word.pos == "PROPN")) is None
    ]


def find_verbal_nouns(words: Iterable[Word]) -> list[Highlight]:
    """
    Finding the verbal nouns

    Description:
        The words tagged NOUN with a lemma derived from a verb (is_verbal_noun),
        as the share verbal_nouns of StyleStats counts them

    Arguments:
        words (list[Word]): Words with their parts of speech and lemmas

    Returns:
        list[Highlight]: Fragments of the layer verbal_nouns
    """
    return [
        Highlight(word.start, word.end, "verbal_nouns", "verbal noun")
        for word in words
        if word.pos == "NOUN" and word.lemma and is_verbal_noun(word.lemma)
    ]


def find_phrase_highlights(
    words: Sequence[Word], phrases: Iterable[str], layer: str, label: str
) -> list[Highlight]:
    """
    Finding the phrases of a list

    Description:
        The phrases are looked for in the forms of the text (expand_phrases,
        find_phrases), with their contractions and the forms of their verbs; a
        fragment covers the words from the first to the last with the marks
        between them, and the note gives the phrase of the list

    Arguments:
        words (list[Word]): Words with their positions
        phrases (list[str]): Phrases, words separated by spaces
        layer (str): Layer of the highlighting
        label (str): Label of the fragment in the note

    Returns:
        list[Highlight]: Fragments of the layer
    """
    texts = [word.text for word in words]
    expanded = expand_phrases(texts, list(phrases))
    highlights = []
    for start, end in find_phrases(texts, expanded):
        phrase = expanded[" ".join(text.lower() for text in texts[start:end])]
        note = f"{label}: «{phrase}»"
        highlights.append(Highlight(words[start].start, words[end - 1].end, layer, note))
    return highlights


def find_compound_prepositions(words: Sequence[Word]) -> list[Highlight]:
    """
    Finding the compound prepositions of COMPOUND_PREPOSITIONS

    Arguments:
        words (list[Word]): Words with their positions

    Returns:
        list[Highlight]: Fragments of the layer compound_prepositions
    """
    return find_phrase_highlights(
        words, COMPOUND_PREPOSITIONS, "compound_prepositions", "compound preposition"
    )


def find_cliches(words: Sequence[Word], cliches: Sequence[str] | None = None) -> list[Highlight]:
    """
    Finding the clichés

    Arguments:
        words (list[Word]): Words with their positions
        cliches (list[str]): List of clichés; OFFICIALESE_CLICHES if not set

    Returns:
        list[Highlight]: Fragments of the layer cliches
    """
    phrases = OFFICIALESE_CLICHES if cliches is None else cliches
    return find_phrase_highlights(words, phrases, "cliches", "cliché")


def find_parentheticals(words: Sequence[Word]) -> list[Highlight]:
    """
    Finding the parenthetical expressions of PARENTHETICALS

    Arguments:
        words (list[Word]): Words with their positions

    Returns:
        list[Highlight]: Fragments of the layer parentheticals
    """
    return find_phrase_highlights(
        words, PARENTHETICALS, "parentheticals", "parenthetical expression"
    )


def find_connector_highlights(
    words: Sequence[Word], sents: Sequence[Sent] | None
) -> list[Highlight]:
    """
    Finding the connectors

    Description:
        The connectors are looked for inside every sentence (find_connectors),
        in the whole text without the sentence boundaries; a one-word connector
        is checked by the part of speech of the word when a tagged Doc gives it;
        the note gives the class and the kind of the connector

    Arguments:
        words (list[Word]): Words with their positions
        sents (list[Sent]): Sentences with their positions; None if the boundaries
            are unknown

    Returns:
        list[Highlight]: Fragments of the layer connectors
    """
    groups = group_words_by_sents(words, sents) if sents else [list(words)]
    highlights = []
    for group in groups:
        texts = [word.text for word in group]
        pos = [word.pos for word in group] if any(word.pos for word in group) else None
        for connector in find_connectors(texts, sent_index=0, pos=pos):
            note = (
                f"connector «{connector.text}»: {CONNECTOR_CLASSES[connector.cls]}, "
                f"{CONNECTOR_TYPES[connector.kind]}"
            )
            highlights.append(
                Highlight(
                    group[connector.start].start, group[connector.end - 1].end, "connectors", note
                )
            )
    return highlights


def group_words_by_sents(words: Sequence[Word], sents: Sequence[Sent]) -> list[list[Word]]:
    """
    Grouping the words by sentences

    Description:
        The words and the sentences are ordered by position, so one pass is
        enough; a word belongs to the sentence of its first character, and the
        words out of the sentences are skipped

    Arguments:
        words (list[Word]): Words with their positions
        sents (list[Sent]): Sentences with their positions

    Returns:
        list[list[Word]]: Words of every sentence
    """
    groups: list[list[Word]] = [[] for _ in sents]
    index = 0
    for word in words:
        while index < len(sents) and sents[index].end <= word.start:
            index += 1
        if index < len(sents) and sents[index].start <= word.start:
            groups[index].append(word)
    return groups


def tokens_span(tokens: Iterable[Token]) -> tuple[int, int]:
    """
    Computing the positions of the fragment of a text that covers some words

    Description:
        The punctuation marks and the whitespace tokens are left out, so the
        commas at the edges of a clause stay out of the fragment

    Arguments:
        tokens (Doc|Span|list[Token]): Sequence of tokens

    Returns:
        tuple[int, int]: Position of the first character and position after the last one
    """
    words = get_words(tokens)
    return min(token.idx for token in words), max(token.idx + len(token) for token in words)


def find_passive(doc: Doc) -> list[Highlight]:
    """
    Finding the passive verb forms

    Description:
        A form is highlighted with its auxiliary ser (fue construida) or its se
        (se construyó), as is_passive finds them; the note tells the passive
        with se from the one with ser, and a passive with ser without an agent

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer passive
    """
    highlights = []
    for token in doc:
        if not (is_word(token) and is_passive(token)):
            continue
        se = [child for child in token.children if child.dep_ == SE_PASSIVE_DEP]
        auxiliaries = [
            child
            for child in token.children
            if base_dep(child) in AUXILIARY_DEPS and child.lemma_ == PASSIVE_AUX
        ]
        start, end = tokens_span([token, *se, *auxiliaries])
        if se:
            note = "passive with se"
        else:
            note = "passive with ser, no agent" if is_agentless(token) else "passive with ser"
        highlights.append(Highlight(start, end, "passive", note))
    return highlights


def find_participle_clauses(doc: Doc) -> list[Highlight]:
    """
    Finding the participial clauses

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer participle_clauses
    """
    highlights = []
    for token in doc:
        if is_participle_clause(token):
            start, end = tokens_span(token.subtree)
            n_words = len(get_words(token.subtree))
            note = f"participial clause, {plural(n_words, 'word')}"
            highlights.append(Highlight(start, end, "participle_clauses", note))
    return highlights


def find_gerund_clauses(doc: Doc) -> list[Highlight]:
    """
    Finding the gerund clauses

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer gerund_clauses
    """
    highlights = []
    for token in doc:
        if is_gerund_clause(token):
            start, end = tokens_span(token.subtree)
            n_words = len(get_words(token.subtree))
            note = f"gerund clause, {plural(n_words, 'word')}"
            highlights.append(Highlight(start, end, "gerund_clauses", note))
    return highlights


def find_split_predicate_highlights(doc: Doc) -> list[Highlight]:
    """
    Finding the split predicates

    Description:
        The pairs of a light verb and a noun of find_split_predicates; a fragment
        covers the words from the first to the last of the pair (hacer una
        revisión)

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer split_predicates
    """
    highlights = []
    for verb, noun in find_split_predicates(doc):
        start, end = tokens_span([verb, noun])
        note = f"split predicate: {verb.lemma_.lower()} {noun.lemma_.lower()}"
        highlights.append(Highlight(start, end, "split_predicates", note))
    return highlights


def _de_chain(token: Token) -> tuple[list[Token], int]:
    tokens = [token]
    depth = 1
    for child in token.children:
        if is_de_modifier(child):
            child_tokens, child_depth = _de_chain(child)
            tokens += child_tokens
            depth = max(depth, child_depth + 1)
    return tokens, depth


def find_de_chains(doc: Doc) -> list[Highlight]:
    """
    Finding the chains of de

    Description:
        A chain is two or more nested complements with de, as calc_de_chains
        counts them; a fragment covers the head and every complement of the
        chain: el aumento de la eficiencia del uso de los recursos

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer de_chains
    """
    highlights = []
    for token in doc:
        if not is_de_modifier(token) or is_de_modifier(token.head):
            continue
        chain, depth = _de_chain(token)
        if depth < 2:
            continue
        start, end = tokens_span([token.head, *chain])
        note = f"chain of {plural(depth, 'complement')} with de"
        highlights.append(Highlight(start, end, "de_chains", note))
    return highlights


def split_segments(
    length: int, highlights: Sequence[Highlight]
) -> Iterator[tuple[int, int, list[Highlight]]]:
    """
    Splitting a text into segments with the same set of fragments

    Description:
        The bounds of the segments are the starts and the ends of all the
        fragments; overlapping and nested fragments of different layers give
        segments with several layers

    Arguments:
        length (int): Length of the text
        highlights (list[Highlight]): Fragments sorted by their start

    Returns:
        iterator[tuple[int, int, list[Highlight]]]: Positions of a segment and
            the fragments that cover it
    """
    bounds = sorted({0, length, *(h.start for h in highlights), *(h.end for h in highlights)})
    pending = sorted(highlights, key=lambda h: h.start)
    active: list[Highlight] = []
    index = 0
    for start, end in pairwise(bounds):
        while index < len(pending) and pending[index].start <= start:
            active.append(pending[index])
            index += 1
        active = [h for h in active if h.end > start]
        yield start, end, list(active)
