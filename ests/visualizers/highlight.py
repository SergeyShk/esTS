import re
from collections.abc import Callable, Collection, Iterable, Iterator, Sequence

import anyts.visualizers.highlight
from anyts.syntax import base_dep, is_word, subtree_len
from anyts.utils import check_integer, check_number, check_words
from anyts.visualizers.highlight import (
    Highlight as Highlight,
    Sent,
    Word,
    group_words_by_sents,
    tokens_span,
)
from spacy.tokens import Doc, Token

from ..cohesion_stats import find_connectors
from ..constants import (
    ALLITERATION_MIN_WORD_LEN,
    ALLITERATION_THRESHOLD,
    COMPOUND_PREPOSITIONS,
    CONNECTOR_CLASSES,
    CONNECTOR_TYPES,
    HIGHLIGHT_COMPLEX_SYL_FACTOR,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_ANNOTATIONS,
    HIGHLIGHT_LAYER_STYLES,
    HIGHLIGHT_LAYERS_DESC,
    LONG_SENT_WORD_FACTOR,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    PASSIVE_AUX,
    SE_PASSIVE_DEP,
    SOUND_FREQUENCIES,
    SOUND_SPELLINGS,
    VOWEL_SOUNDS,
)
from ..datasets.freq_dict import lemma_key
from ..exceptions import ParameterError
from ..lexical_stats import get_rank
from ..phon_stats import CONSONANT_SOUNDS, transcribe
from ..style_stats import expand_phrases, in_order, is_stopword
from ..syllables import count_syllables
from ..syntax_stats import (
    AUXILIARY_DEPS,
    find_split_predicates,
    is_agentless,
    is_de_modifier,
    is_gerund_clause,
    is_participle_clause,
    is_passive,
)
from ..utils import find_phrases, is_verbal_noun, iter_text_sents, iter_text_words, lemmatize

SPANISH_WORD = re.compile(r"[a-záéíóúüñ]{2,}", re.IGNORECASE)


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
            stopwords - stopwords of STOPWORDS or of the list passed, the water (StyleStats)
            parentheticals - parenthetical expressions (StyleStats)
            connectors - discourse markers, with the class and the kind in the note
                (CohesionStats)
            alliteration - repetitions of a consonant sound in neighbouring words,
                unlikely by the frequencies of the Spanish sounds (PhonStats)
        HIGHLIGHT_LAYER_GROUPS groups the layers. The syntactic layers need a Doc
        with a dependency parse and the lemmas, verbal_nouns a Doc with the parts
        of speech and the lemmas; a Doc without the sentence boundaries is split
        by the rules of SentsExtractor. By default the layers of
        HIGHLIGHT_DEFAULT_LAYERS the source allows are on (long sentences, complex
        words, passive, chains of de, split predicates, clichés)
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
        SourceError: If the source has no words
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
        check_integer(long_sent_word_factor, "number of words of a long sentence")
        check_integer(complex_syl_factor, "number of syllables of a complex word")
        if long_sent_word_factor < 1:
            raise ParameterError("The number of words of a long sentence must be greater than 0")
        if complex_syl_factor < 1:
            raise ParameterError(
                "The number of syllables of a complex word must be greater than 0"
            )
        check_number(alliteration_threshold, "threshold of the alliteration")
        if not 0 < alliteration_threshold <= 1:
            raise ParameterError(
                "The threshold of the alliteration must lie in the interval (0, 1]"
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
            "connectors": lambda: find_connector_highlights(words, sents),
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
        The words whose lemma_key is beyond the 10,000 most frequent lemmas
        (get_rank), as p_beyond_top10000 of LexicalStats counts them; a proper
        noun of a tagged Doc keeps its form. Only the words of two Spanish
        letters or more that are not stopwords are looked at

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
        The words tagged NOUN with a lemma derived from a verb (is_verbal_noun)

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
        The phrases are matched with their contractions and the forms of their
        verbs (expand_phrases); a fragment covers the words from the first to the
        last, and the note gives the phrase of the list

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


def find_cliches(words: Sequence[Word], cliches: Collection[str] | None = None) -> list[Highlight]:
    """
    Finding the clichés

    Arguments:
        words (list[Word]): Words with their positions
        cliches (list[str]|set[str]): List or set of clichés; OFFICIALESE_CLICHES if not set

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


def find_connector_highlights(words: Sequence[Word], sents: Sequence[Sent]) -> list[Highlight]:
    """
    Finding the connectors

    Description:
        The connectors are looked for inside every sentence (find_connectors), a
        one-word one checked by its part of speech when the words have it; the
        note gives the class and the kind of the connector

    Arguments:
        words (list[Word]): Words with their positions
        sents (list[Sent]): Sentences with their positions

    Returns:
        list[Highlight]: Fragments of the layer connectors
    """
    groups = group_words_by_sents(words, sents)
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
        probability is below the threshold

    Arguments:
        text (list[str]): List of words
        threshold (float): Probability threshold

    Returns:
        list[tuple[int, int, str]]: Positions of the first word and after the last
            word of every run and its consonant, in the order of the text
    """
    words = [word.lower() for word in text]
    transparent = [
        len(word) < ALLITERATION_MIN_WORD_LEN
        or is_stopword(word)
        or not any(sound in VOWEL_SOUNDS for sound in transcribe(word))
        for word in words
    ]
    stems = [get_stem_sounds(word) for word in words]
    runs = []
    for consonant in sorted(CONSONANT_SOUNDS):
        frequency = SOUND_FREQUENCIES[consonant]
        start = None
        stop = 0
        probability = 1.0
        for i, stem in enumerate(stems):
            if transparent[i]:
                continue
            if consonant in stem:
                if start is None:
                    start, probability = i, 1.0
                stop = i + 1
                probability *= 1 - (1 - frequency) ** len(stem)
            elif start is not None:
                if stop - start >= 2 and probability < threshold:
                    runs.append((start, stop, consonant))
                start = None
        if start is not None and stop - start >= 2 and probability < threshold:
            runs.append((start, stop, consonant))
    return sorted(runs)


def find_alliteration(
    words: Sequence[Word],
    threshold: float = ALLITERATION_THRESHOLD,
    sents: Sequence[Sent] | None = None,
) -> list[Highlight]:
    """
    Finding the alliterations

    Description:
        The repetitions are looked for inside the sentences, in the whole text
        without them; the note gives the sound and the letters that write it

    Arguments:
        words (list[Word]): Words with their positions
        threshold (float): Probability threshold, see calc_alliteration_runs
        sents (list[Sent]): Sentences with their positions

    Returns:
        list[Highlight]: Fragments of the layer alliteration
    """
    groups = [list(words)] if sents is None else group_words_by_sents(words, sents)
    highlights = []
    for group in groups:
        for start, stop, sound in calc_alliteration_runs([word.text for word in group], threshold):
            spellings = SOUND_SPELLINGS[sound]
            note = f"alliteration on /{sound}/"
            if spellings != sound:
                note += f" ({spellings})"
            highlights.append(
                Highlight(group[start].start, group[stop - 1].end, "alliteration", note)
            )
    return highlights


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


# Finders of the layers read from the dependency tree of a Doc
SYNTAX_FINDERS: dict[str, Callable[[Doc], list[Highlight]]] = {
    "passive": find_passive,
    "participle_clauses": find_participle_clauses,
    "gerund_clauses": find_gerund_clauses,
    "de_chains": find_de_chains,
    "split_predicates": find_split_predicate_highlights,
}
