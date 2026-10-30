from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence
from itertools import islice
from typing import TYPE_CHECKING

import anyts.visualizers.highlight
from anyts.constants import ALLITERATION_MIN_WORD_LEN, ALLITERATION_THRESHOLD, AUXILIARY_DEPS
from anyts.syntax_stats import base_dep, get_children, get_words, is_root, subtree_len
from anyts.utils import check_words, has_feature, in_order, is_word
from anyts.visualizers.highlight import (
    Highlight as Highlight,
    Sent as Sent,
    Word as Word,
    find_words,
    group_words_by_sents as group_words_by_sents,
    tokens_span,
)

from ..cohesion_stats import CohesionStats, is_connector_blocked
from ..constants import (
    COMPOUND_PREPOSITIONS,
    CONNECTOR_CLASSES,
    CONNECTOR_TYPES,
    HIGHLIGHT_COMPLEX_SYL_FACTOR,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_ANNOTATIONS,
    HIGHLIGHT_LAYER_STYLES,
    HIGHLIGHT_LAYERS_DESC,
    LONG_SENT_WORD_FACTOR,
    MISMO_ARTICLES,
    MISMO_COMPARATIVE,
    MISMO_FORMS,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    PASSIVE_AUX,
    PREDICATIVE_VERBS,
    SE_PASSIVE_DEP,
    SOUND_FREQUENCIES,
    SOUND_SPELLINGS,
    VOWEL_SOUNDS,
)
from ..datasets.freq_dict import lemma_key
from ..lexical_stats import get_rank
from ..phon_stats import CONSONANT_SOUNDS, transcribe
from ..style_stats import INFINITIVE_ENDINGS, expand_phrases, is_stopword
from ..syllables import count_syllables
from ..syntax_stats import (
    find_split_predicates,
    is_agentless,
    is_de_modifier,
    is_gerund_clause,
    is_participle_clause,
    is_passive,
)
from ..utils import is_verbal_noun, iter_text_sents, iter_text_words, lemmatize

if TYPE_CHECKING:
    from spacy.tokens import Doc, Token

SPANISH_WORD = re.compile(r"[a-záéíóúüñ]{2,}", re.IGNORECASE)
# Frequencies of the consonant sounds for the alliteration
ALLITERATION_FREQUENCIES = {sound: SOUND_FREQUENCIES[sound] for sound in CONSONANT_SOUNDS}
# Relations of an anaphoric el mismo to its head, of the words of its noun phrase, and the parts of
# speech that go on a noun phrase after a mismo the models attach to its article
ARGUMENT_DEPS = frozenset({"nsubj", "obj", "iobj", "obl", "nmod", "conj"})
NP_DEPS = frozenset({"det", "case", "cc"})
NOMINAL_POS = frozenset({"NOUN", "PROPN", "ADJ", "NUM", "PRON"})
# Pronoun types of a determiner that opens a noun phrase of its own, not a modifier coordinated
# with mismo before their noun (de la misma o distinta categoría)
NP_OPENING_PRON_TYPES = frozenset({"Art", "Prs"})


class HighlightedText(anyts.visualizers.highlight.HighlightedText):
    """
    Class for highlighting a text by layers, in the manner of the style checkers

    Description:
        Every layer marks the fragments a statistic of the library counts:
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
            anaphoric_mismo - the anaphoric el mismo with its article, of no statistic
            stopwords - stopwords of STOPWORDS or of the list passed, the water (StyleStats)
            parentheticals - parenthetical expressions (StyleStats)
            connectors - discourse markers, with the class and the kind in the note
                (CohesionStats)
            alliteration - repetitions of a consonant sound in neighbouring words,
                unlikely by the frequencies of the Spanish sounds (PhonStats)
        HIGHLIGHT_LAYER_GROUPS groups the layers. The syntactic layers need a Doc
        with a dependency parse and the lemmas, verbal_nouns a Doc with the parts
        of speech and the lemmas, anaphoric_mismo one with all three; a Doc
        without the sentence boundaries is split by the rules of SentsExtractor.
        By default the layers of HIGHLIGHT_DEFAULT_LAYERS the source allows are on
        (long sentences, complex words, passive, chains of de, split predicates,
        clichés)
        A word is complex from 4 syllables here; complex_syl_factor=3 shows the
        words of n_complex_words
        The result shows in Jupyter as HTML with a legend (to_html); fragments of
        different layers may overlap

    Example:
        >>> from ests.visualizers import highlight
        >>> text = (
        ...     "Se procedió a la revisión del expediente en el marco del plan a la mayor "
        ...     "brevedad. Sin embargo, el gato duerme."
        ... )
        >>> ht = highlight(text)
        >>> ht.counts
        {'long_sents': 0, 'complex_words': 1, 'cliches': 2}
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
        stopwords (list[str]|set[str]): Stopwords; STOPWORDS and the one-word parenthetical
            expressions if not set
        cliches (list[str]|set[str]): List or set of clichés; OFFICIALESE_CLICHES if not set
        alliteration_threshold (float): Probability of a repetition of a consonant
            under an independent spread of the sounds, below which the repetition
            is alliteration

    Attributes:
        text (str): Text of the source
        layers (tuple[str]): Layers turned on, in the order of drawing
        highlights (tuple[Highlight]): Highlighted fragments in the order of the text
        counts (dict[str, int]): Number of fragments of every layer

    Methods:
        to_html: Getting the HTML markup of the highlighted text
        css: Getting the styles of the layers

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words or is a string with a character without a
            UTF-8 form
        SourceTypeError: If the stopwords or the clichés are not a list or a set of strings
        ParameterError: If a layer is unknown or not allowed by the source, or a
            threshold of a layer is out of its range
    """

    layers_desc = HIGHLIGHT_LAYERS_DESC
    default_layers = HIGHLIGHT_DEFAULT_LAYERS
    layer_annotations = HIGHLIGHT_LAYER_ANNOTATIONS
    layer_styles = HIGHLIGHT_LAYER_STYLES
    css_prefix = "ests"

    def __init__(
        self,
        source: str | Doc,
        layers: Sequence[str] | str | None = None,
        long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
        complex_syl_factor: int = HIGHLIGHT_COMPLEX_SYL_FACTOR,
        stopwords: Collection[str] | None = None,
        cliches: Collection[str] | None = None,
        alliteration_threshold: float = ALLITERATION_THRESHOLD,
    ):
        anyts.visualizers.highlight.check_params(
            long_sent_word_factor,
            complex_syl_factor,
            alliteration_threshold,
            messages=self.messages,
        )
        if stopwords is not None:
            check_words(stopwords, "stopwords", ordered=False)
            stopwords = in_order(stopwords)
        if cliches is not None:
            check_words(cliches, "clichés", ordered=False)
            cliches = in_order(cliches)
        self._long_sent_word_factor = long_sent_word_factor
        self._complex_syl_factor = complex_syl_factor
        self._stopwords = stopwords
        self._cliches = cliches
        self._alliteration_threshold = alliteration_threshold
        super().__init__(source, layers)

    def iter_words(self, text: str) -> Iterator[tuple[int, int, str]]:
        """The words of a string by iter_text_words, without the punctuation"""
        return iter_text_words(text)

    def iter_sents(self, text: str) -> Iterator[tuple[int, int, str]]:
        """The sentences of a string by iter_text_sents"""
        return iter_text_sents(text)

    def find(
        self, layer: str, words: Sequence[Word], sents: Sequence[Sent], doc: Doc | None
    ) -> list[Highlight]:
        """
        Finding the fragments of a layer

        Arguments:
            layer (str): Layer of the highlighting
            words (list[Word]): Words of the text with their positions
            sents (list[Sent]): Sentences of the text with their positions
            doc (Doc): Doc object of the source; None for a string

        Returns:
            list[Highlight]: Fragments of the layer
        """
        if layer in SYNTAX_FINDERS:
            return SYNTAX_FINDERS[layer](doc) if doc is not None else []
        finders: dict[str, Callable[[], list[Highlight]]] = {
            "long_sents": lambda: find_long_sents(sents, self._long_sent_word_factor),
            "complex_words": lambda: find_complex_words(words, self._complex_syl_factor),
            "rare_words": lambda: find_rare_words(words),
            "stopwords": lambda: find_stopwords(words, self._stopwords),
            "verbal_nouns": lambda: find_verbal_nouns(words),
            "compound_prepositions": lambda: find_compound_prepositions(words),
            "cliches": lambda: find_cliches(words, self._cliches),
            "parentheticals": lambda: find_parentheticals(words),
            "connectors": lambda: find_connector_highlights(words, sents, self.text, doc),
            "alliteration": lambda: find_alliteration(words, self._alliteration_threshold, sents),
        }
        return finders[layer]()


def highlight(
    source: str | Doc,
    layers: Sequence[str] | str | None = None,
    long_sent_word_factor: int = LONG_SENT_WORD_FACTOR,
    complex_syl_factor: int = HIGHLIGHT_COMPLEX_SYL_FACTOR,
    stopwords: Collection[str] | None = None,
    cliches: Collection[str] | None = None,
    alliteration_threshold: float = ALLITERATION_THRESHOLD,
) -> HighlightedText:
    """
    Highlighting a text by layers, in the manner of the style checkers

    Description:
        The layers and the annotations of the Doc they need are described in
        HighlightedText

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        layers (list[str]|str): Layers of the highlighting; the layers of
            HIGHLIGHT_DEFAULT_LAYERS the source allows if not set; "all" - every
            layer the source allows
        long_sent_word_factor (int): Minimum number of words of a long sentence
        complex_syl_factor (int): Minimum number of syllables of a complex word
        stopwords (list[str]|set[str]): Stopwords; STOPWORDS and the one-word parenthetical
            expressions if not set
        cliches (list[str]|set[str]): List or set of clichés; OFFICIALESE_CLICHES if not set
        alliteration_threshold (float): Probability of a repetition of a consonant
            under an independent spread of the sounds, below which the repetition
            is alliteration

    Returns:
        HighlightedText: Highlighted text with an HTML view for Jupyter

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words or is a string with a character without a
            UTF-8 form
        SourceTypeError: If the stopwords or the clichés are not a list or a set of strings
        ParameterError: If a layer is unknown or not allowed by the source, or a
            threshold of a layer is out of its range
    """
    return HighlightedText(
        source,
        layers,
        long_sent_word_factor=long_sent_word_factor,
        complex_syl_factor=complex_syl_factor,
        stopwords=stopwords,
        cliches=cliches,
        alliteration_threshold=alliteration_threshold,
    )


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

    Description:
        The find_long_sents of the core with the note of the number of words

    Arguments:
        sents (list[Sent]): Sentences with their positions and numbers of words
        long_sent_word_factor (int): Minimum number of words of a long sentence

    Returns:
        list[Highlight]: Fragments of the layer long_sents

    Raises:
        ParameterError: If the number of words is not an integer of at least one
    """
    return anyts.visualizers.highlight.find_long_sents(
        sents, long_sent_word_factor, lambda n: f"long sentence, {plural(n, 'word')}"
    )


def find_complex_words(words: Iterable[Word], complex_syl_factor: int) -> list[Highlight]:
    """
    Finding the complex words

    Description:
        The find_complex_words of the core with the syllables of count_syllables

    Arguments:
        words (list[Word]): Words with their positions
        complex_syl_factor (int): Minimum number of syllables of a complex word

    Returns:
        list[Highlight]: Fragments of the layer complex_words

    Raises:
        ParameterError: If the number of syllables is not an integer of at least one
    """
    return anyts.visualizers.highlight.find_complex_words(
        words,
        complex_syl_factor,
        count_syllables,
        lambda n: f"complex word, {plural(n, 'syllable')}",
    )


def find_stopwords(
    words: Iterable[Word], stopwords: Collection[str] | None = None
) -> list[Highlight]:
    """
    Finding the stopwords

    Description:
        The words are matched in any case

    Arguments:
        words (list[Word]): Words with their positions
        stopwords (list[str]|set[str]): List or set of stopwords; is_stopword if not set

    Returns:
        list[Highlight]: Fragments of the layer stopwords

    Raises:
        SourceTypeError: If the stopwords are not a list or a set of strings
    """
    if stopwords is None:
        return find_words(words, lambda word: is_stopword(word.text), "stopwords", "stopword")
    check_words(stopwords, "stopwords", ordered=False)
    chosen = {word.lower() for word in stopwords}
    return find_words(words, lambda word: word.text.lower() in chosen, "stopwords", "stopword")


def find_rare_words(words: Iterable[Word]) -> list[Highlight]:
    """
    Finding the rare words

    Description:
        The words whose lemma_key is beyond the 10,000 most frequent lemmas
        (get_rank), as p_beyond_top10000 of LexicalStats counts them; a proper
        noun of a tagged Doc keeps its form. Only the words of two Spanish
        letters or more that are not stopwords are looked at

    Arguments:
        words (list[Word]): Words with their positions

    Returns:
        list[Highlight]: Fragments of the layer rare_words
    """
    return find_words(
        words,
        lambda word: (
            SPANISH_WORD.fullmatch(word.text) is not None
            and not is_stopword(word.text)
            and get_rank(lemma_key(word.text, word.pos == "PROPN")) is None
        ),
        "rare_words",
        "rare word: beyond the top 10000",
    )


def find_verbal_nouns(words: Iterable[Word]) -> list[Highlight]:
    """
    Finding the verbal nouns

    Description:
        The words tagged NOUN with a lemma derived from a verb (is_verbal_noun)

    Arguments:
        words (list[Word]): Words with their parts of speech and lemmas

    Returns:
        list[Highlight]: Fragments of the layer verbal_nouns
    """
    return find_words(
        words,
        lambda word: word.pos == "NOUN" and word.lemma is not None and is_verbal_noun(word.lemma),
        "verbal_nouns",
        "verbal noun",
    )


def find_phrase_highlights(
    words: Sequence[Word], phrases: Collection[str], layer: str, label: str
) -> list[Highlight]:
    """
    Finding the phrases of a list

    Description:
        The phrases are matched with their contractions and the forms of their
        verbs (expand_phrases); a fragment covers the words from the first to the
        last, and the note gives the phrase of the list. The
        find_phrase_highlights of the core

    Arguments:
        words (list[Word]): Words with their positions
        phrases (list[str]|set[str]): Phrases, words separated by spaces
        layer (str): Layer of the highlighting
        label (str): Label of the fragment in the note

    Returns:
        list[Highlight]: Fragments of the layer

    Raises:
        SourceTypeError: If the phrases are not a list or a set of strings
    """
    expanded = expand_phrases([word.text for word in words], phrases)
    return anyts.visualizers.highlight.find_phrase_highlights(
        words, expanded, layer, lambda phrase: f"{label}: «{phrase}»"
    )


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


def find_cliches(words: Sequence[Word], cliches: Collection[str] | None = None) -> list[Highlight]:
    """
    Finding the clichés

    Arguments:
        words (list[Word]): Words with their positions
        cliches (list[str]|set[str]): List or set of clichés; OFFICIALESE_CLICHES if not set

    Returns:
        list[Highlight]: Fragments of the layer cliches

    Raises:
        SourceTypeError: If the clichés are not a list or a set of strings
    """
    if cliches is None:
        return find_phrase_highlights(words, OFFICIALESE_CLICHES, "cliches", "cliché")
    check_words(cliches, "clichés", ordered=False)
    return find_phrase_highlights(words, cliches, "cliches", "cliché")


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
    words: Sequence[Word],
    sents: Sequence[Sent],
    text: str | None = None,
    doc: Doc | None = None,
) -> list[Highlight]:
    """
    Finding the connectors

    Description:
        The connectors are looked for inside every sentence by the matcher of
        CohesionStats (SpanishConnectorMatcher), a one-word one checked by its
        part of speech when the words have it; with the text, the rules read
        no word across a punctuation mark between the words, and with the Doc
        no connector starts at a si that opens no condition, as in
        CohesionStats (is_connector_blocked). The note gives the class and the
        kind of the connector. The find_connector_highlights of the core

    Arguments:
        words (list[Word]): Words with their positions
        sents (list[Sent]): Sentences with their positions
        text (str): Text of the words, for the punctuation marks between them
        doc (Doc): Doc object of the words, for the rules by its tokens

    Returns:
        list[Highlight]: Fragments of the layer connectors

    Raises:
        SourceTypeError: If the text is not a string
    """
    return anyts.visualizers.highlight.find_connector_highlights(
        words,
        sents,
        CohesionStats.connector_matcher(),
        lambda connector: (
            f"connector «{connector.text}»: {CONNECTOR_CLASSES[connector.cls]}, "
            f"{CONNECTOR_TYPES[connector.kind]}"
        ),
        text=text,
        blocked=None if doc is None else _blocked_words(doc),
    )


def _blocked_words(doc: Doc) -> Callable[[Word], bool]:
    """Whether no connector starts at a word of a Doc, by the position of its token"""
    starts = frozenset(token.idx for token in doc if is_connector_blocked(token))
    return lambda word: word.start in starts


def get_stem_sounds(word: str) -> tuple[str, ...]:
    """
    Getting the sounds of the stem of a word form

    Description:
        The common start of the transcriptions of the word form and of its
        lemma (transcribe, lemmatize): hacía - a θ, cogió - k o x. When it is
        shorter than two sounds, as for the suppletive forms (fue - ser), the
        stem is the whole word form

    Arguments:
        word (str): Word form in lower case

    Returns:
        tuple[str]: Sounds of the stem

    Raises:
        SourceTypeError: If the word is not a string
    """
    sounds, lemma_sounds = transcribe(word), transcribe(lemmatize(word))
    length = 0
    for sound, lemma_sound in zip(sounds, lemma_sounds, strict=False):
        if sound != lemma_sound:
            break
        length += 1
    return sounds[:length] if length >= 2 else sounds


def calc_alliteration_runs(
    text: Sequence[str], threshold: float = ALLITERATION_THRESHOLD
) -> list[tuple[int, int, str]]:
    """
    Finding the repetitions of a consonant sound in neighbouring words

    Description:
        A repetition is a run of two neighbouring words or more with the same
        consonant sound in the stem of each (get_stem_sounds); the words shorter
        than three letters, the stopwords and the words without vowels neither
        break nor continue a run. The probability of a run under an independent
        spread of the sounds is the product over its words of 1 - (1 - f)^n,
        where f is the frequency of the consonant in SOUND_FREQUENCIES and n the
        number of the sounds of the stem; a run is alliteration when the
        probability is below the threshold. The calc_alliteration_runs of the core

    Arguments:
        text (list[str]): List of words
        threshold (float): Probability threshold

    Returns:
        list[tuple[int, int, str]]: Positions of the first word and after the last
            word of every run and its consonant, in the order of the text

    Raises:
        SourceTypeError: If the words are not a list of strings
        ParameterError: If the threshold does not lie in (0, 1]
    """
    return anyts.visualizers.highlight.calc_alliteration_runs(
        text,
        ALLITERATION_FREQUENCIES,
        threshold,
        get_stem_sounds,
        _is_transparent,
    )


def _is_transparent(word: str) -> bool:
    """A word that neither breaks nor continues a run: short, a stopword or without vowels"""
    return (
        len(word) < ALLITERATION_MIN_WORD_LEN
        or is_stopword(word)
        or not any(sound in VOWEL_SOUNDS for sound in transcribe(word))
    )


def find_alliteration(
    words: Sequence[Word],
    threshold: float = ALLITERATION_THRESHOLD,
    sents: Sequence[Sent] | None = None,
) -> list[Highlight]:
    """
    Finding the alliterations

    Description:
        The repetitions are looked for inside the sentences, in the whole text
        without them; the note gives the sound and the letters that write it.
        The find_alliteration of the core

    Arguments:
        words (list[Word]): Words with their positions
        threshold (float): Probability threshold, see calc_alliteration_runs
        sents (list[Sent]): Sentences with their positions

    Returns:
        list[Highlight]: Fragments of the layer alliteration

    Raises:
        ParameterError: If the threshold does not lie in (0, 1]
    """
    return anyts.visualizers.highlight.find_alliteration(
        words,
        sents,
        ALLITERATION_FREQUENCIES,
        threshold,
        get_stem_sounds,
        _is_transparent,
        _alliteration_note,
    )


def _alliteration_note(sound: str) -> str:
    """Note of an alliteration: the sound and the letters that write it"""
    spellings = SOUND_SPELLINGS[sound]
    return f"alliteration on /{sound}/" + (f" ({spellings})" if spellings != sound else "")


def find_passive(doc: Doc) -> list[Highlight]:
    """
    Finding the passive verb forms

    Description:
        A form of is_passive is highlighted with its auxiliary ser (fue
        construida) or its se (se construyó); the note tells the passive with se
        from the one with ser, and a passive with ser without an agent

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


def _subtree(token: Token) -> list[Token]:
    """
    Getting the tokens of the subtree of a token

    Description:
        Unlike Token.subtree, the walk keeps the tokens it has visited, so it
        ends on a broken parse whose heads form a loop

    Arguments:
        token (Token): Token

    Returns:
        list[Token]: Tokens of the subtree
    """
    tokens = []
    stack = [token]
    seen = {token.i}
    while stack:
        current = stack.pop()
        tokens.append(current)
        for child in current.children:
            if child.i not in seen:
                seen.add(child.i)
                stack.append(child)
    return tokens


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
            start, end = tokens_span(_subtree(token))
            n_words = subtree_len(token)
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
            start, end = tokens_span(_subtree(token))
            n_words = subtree_len(token)
            note = f"gerund clause, {plural(n_words, 'word')}"
            highlights.append(Highlight(start, end, "gerund_clauses", note))
    return highlights


def find_split_predicate_highlights(doc: Doc) -> list[Highlight]:
    """
    Finding the split predicates

    Description:
        The pairs of a light verb and a noun of find_split_predicates; a fragment
        covers the words from the first to the last of the pair (hacer una
        revisión). The find_split_predicate_highlights of the core

    Arguments:
        doc (Doc): Doc object with a dependency parse

    Returns:
        list[Highlight]: Fragments of the layer split_predicates
    """
    return anyts.visualizers.highlight.find_split_predicate_highlights(find_split_predicates(doc))


def is_anaphoric_mismo(token: Token) -> bool:
    """
    Checking whether a token is an anaphoric el mismo

    Description:
        A form of MISMO_FORMS that heads a noun phrase of its own with an
        article of MISMO_ARTICLES and no other dependent but a clause after a
        comma, as an argument (se archivó el mismo, la duración del mismo,
        contra la misma, que pone fin...), but not as the subject or the
        object after a verb of PREDICATIVE_VERBS by the lemma of the model or
        of simplemma, where it means the same one (no parecía la misma,
        serás el mismo), right before que (el mismo que el año pasado) or
        before a conjunction and an adjective or a determiner that shares its
        noun (de la misma o distinta categoría). The models attach some of
        them to their article (en la misma hay oficinas): such a form counts
        when no noun, adjective, numeral or pronoun follows it in its
        sentence, a singular adjective without gender whose lemma of
        simplemma is an infinitive being a verb (contra la misma cabe
        recurso). The identity of el mismo día, es el mismo, lo mismo and él
        mismo is no anaphora; a token without a parse is none

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if token.lower_ not in MISMO_FORMS or not token.dep_:
        return False
    sent_end = token.sent.end
    after = list(
        islice((word for word in token.doc[token.i + 1 : sent_end] if not word.is_space), 2)
    )
    if after and after[0].lower_ == MISMO_COMPARATIVE:
        return False
    if len(after) == 2 and after[0].pos_ == "CCONJ" and _is_modifier(after[1]):
        return False
    children = get_children(token)
    if any(child.lower_ in MISMO_ARTICLES and base_dep(child) in NP_DEPS for child in children):
        # A clause after a comma explains the noun phrase (contra la misma, que pone fin a...)
        explained = bool(after) and after[0].text == ","
        if base_dep(token) not in ARGUMENT_DEPS or any(
            base_dep(child) not in NP_DEPS and not (explained and base_dep(child) == "acl")
            for child in children
        ):
            return False
        head = token.head
        return not (
            base_dep(token) in ("nsubj", "obj")
            and head.i < token.i
            and PREDICATIVE_VERBS & {head.lemma_, lemmatize(head.lower_)}
        )
    head = token.head
    if children or head.i != token.i - 1 or head.lower_ not in MISMO_ARTICLES:
        return False
    following = next((word for word in token.doc[token.i + 1 : sent_end] if is_word(word)), None)
    return following is None or not _is_nominal(following)


def _is_nominal(word: Token) -> bool:
    """Whether a word goes on a noun phrase; a singular form without gender the model tags as
    an adjective is a verb when simplemma gives it an infinitive of another form (contra la
    misma cabe; la misma amarga ironía agrees in gender)"""
    if word.pos_ not in NOMINAL_POS:
        return False
    if (
        word.pos_ != "ADJ"
        or not has_feature(word, "Number", "Sing")
        or word.morph.get("Gender", [])
    ):
        return True
    lemma = lemmatize(word.lower_)
    return lemma == word.lower_ or not lemma.endswith(INFINITIVE_ENDINGS)


def _is_modifier(word: Token) -> bool:
    """Whether a word after a conjunction modifies a noun with the word before it: an adjective,
    or a determiner other than an article or a possessive"""
    if word.pos_ == "ADJ":
        return True
    return word.pos_ == "DET" and not any(
        has_feature(word, "PronType", value) for value in NP_OPENING_PRON_TYPES
    )


def find_anaphoric_mismo(doc: Doc) -> list[Highlight]:
    """
    Finding the anaphoric el mismo

    Description:
        Every form of is_anaphoric_mismo with its article (la misma, del
        mismo); the note gives the two words

    Arguments:
        doc (Doc): Doc object with a dependency parse, the parts of speech and the
            lemmas

    Returns:
        list[Highlight]: Fragments of the layer anaphoric_mismo
    """
    highlights = []
    for token in doc:
        if not is_anaphoric_mismo(token):
            continue
        article = next(
            (child for child in token.children if child.lower_ in MISMO_ARTICLES),
            token.head,
        )
        start, end = tokens_span([article, token])
        note = f"anaphoric {article.lower_} {token.lower_}"
        highlights.append(Highlight(start, end, "anaphoric_mismo", note))
    return highlights


def _de_chain(token: Token) -> tuple[list[Token], int]:
    tokens = [token]
    depth = 1
    for child in get_children(token):
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
    for token in get_words(doc):
        if not is_de_modifier(token):
            continue
        head = token.head
        if not is_root(token) and is_word(head) and is_de_modifier(head):
            continue
        chain, depth = _de_chain(token)
        if depth < 2:
            continue
        start, end = tokens_span([token.head, *chain])
        note = f"chain of {plural(depth, 'complement')} with de"
        highlights.append(Highlight(start, end, "de_chains", note))
    return highlights


# Finders of the layers read from the dependency tree of a Doc
SYNTAX_FINDERS: dict[str, Callable[[Doc], list[Highlight]]] = {
    "passive": find_passive,
    "participle_clauses": find_participle_clauses,
    "gerund_clauses": find_gerund_clauses,
    "de_chains": find_de_chains,
    "split_predicates": find_split_predicate_highlights,
    "anaphoric_mismo": find_anaphoric_mismo,
}
