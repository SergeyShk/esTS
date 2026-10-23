from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from contextlib import suppress
from math import nan
from typing import TYPE_CHECKING, Any

import anyts.style_stats
from anyts.constants import MESSAGES, NAUSEA_TOP_N
from anyts.style_stats import (
    calc_classic_nausea as calc_classic_nausea,
    calc_keyword_density as calc_keyword_density,
    calc_spam as calc_spam,
    calc_zipf_naturalness as calc_zipf_naturalness,
    check_params as check_params,
)
from anyts.utils import check_words, in_order, is_doc, iter_doc_tokens, safe_divide

from .constants import (
    COMPOUND_PREPOSITIONS,
    IRREGULAR_VERB_FORMS,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORDS,
    STYLE_STATS_DESC,
)
from .exceptions import SourceError, SourceTypeError
from .extractors import WordsExtractor
from .utils import _check_nlp, get_nlp, is_verbal_noun, iter_text_sents, lemmatize

if TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokens import Doc

# Components the parts of speech and the lemmas of the nouns do not need
UNUSED_COMPONENTS = ["parser", "ner"]
# One-word parenthetical expressions, which the water counts as stopwords
PARENTHETICAL_WORDS = frozenset(phrase for phrase in PARENTHETICALS if " " not in phrase)
# The word forms of is_stopword
STOPWORD_FORMS = STOPWORDS | PARENTHETICAL_WORDS
# Endings of the infinitive, whose phrases stand for the forms of the verb
INFINITIVE_ENDINGS = ("ar", "er", "ir", "ír")


class StyleStats(anyts.style_stats.StyleStats):
    """
    Class for computing the style metrics of a text

    Description:
        Extends the StyleStats of the anyTS core with the hooks of Spanish: the
        stopwords and the one-word parenthetical expressions (is_stopword), the
        phrases with their contractions and the forms of their verbs
        (expand_phrases), the lists COMPOUND_PREPOSITIONS, PARENTHETICALS and
        OFFICIALESE_CLICHES, and the verbal nouns among the nouns of the spaCy
        model. The nouns of a string are parsed by the model only when they
        are first read, in parts of whole sentences if it is longer than the
        max_length of the pipeline

    Example:
        >>> from ests import StyleStats
        >>> text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
        >>> ss = StyleStats(text)
        >>> ss.classic_nausea, ss.spam, round(ss.water, 2)
        (1.4142135623730951, 25.0, 25.0)
        >>> ss.keyword_density("tres tristes", "trigo")
        {'tres tristes': 16.666666666666668, 'trigo': 8.333333333333334}

    The markers of the officialese style, 1 of 12 words each:
        >>> ss = StyleStats("Sin embargo, se procedió a la revisión en el marco del proyecto")
        >>> ss.parentheticals, ss.cliches, ss.compound_prepositions
        (8.333333333333332, 8.333333333333332, 8.333333333333332)

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        words_extractor (WordsExtractor): Word extraction tool; for a Doc it is applied
            to its text
        stopwords (list[str]|set[str]): Stopwords for the water content; is_stopword if
            not set
        top_n (int): Number of the most frequent words for the academic nausea
            and the naturalness by Zipf's law
        cliches (list[str]|set[str]): List or set of clichés; OFFICIALESE_CLICHES if not set
        nlp (Language): Pipeline that parses a string for the verbal nouns;
            get_nlp() if not set
        nausea_stopwords (list[str]|set[str]): Stopwords left out of the most frequent words
            of the academic nausea; is_stopword if not set

    Attributes:
        words (tuple[str]): Tuple of the extracted words
        forms (tuple[str]): Tuple of the unfiltered word forms in lower case
        nlp (Language|None): Pipeline of the verbal nouns
        classic_nausea (float): Classic nausea
        academic_nausea (float): Academic nausea in percent
        water (float): Water content in percent
        spam (float): Spam score in percent
        zipf_naturalness (float): Naturalness by Zipf's law in percent
        verbal_nouns (float): Share of the verbal nouns among the nouns in percent
        compound_prepositions (float): Compound prepositions per 100 words
        parentheticals (float): Parenthetical expressions per 100 words
        cliches (float): Clichés per 100 words

    Methods:
        keyword_density: Density of keywords and phrases
        nausea_words: Most frequent significant words of the academic nausea
        markers: Markers of the officialese style found in the text
        describe: Reading of a metric by its scale, None for every metric
        get_stats: Getting the computed style metrics of the text
        to_dataframe: Getting the metrics as a table of one row
        print_stats: Printing the computed style metrics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc, the stopwords,
            the nausea stopwords or the clichés are not a list or a set of strings, or
            the extractor or the pipeline is of another type
        SourceError: If the source has no words or a string has a character without a
            UTF-8 form; when the verbal nouns or the markers are read, if the source lacks
            the parts of speech or the lemmas or a sentence of a string is longer than the
            max_length of the pipeline
        ParameterError: If the number of the most frequent words is not an integer or is
            below one
    """

    words_extractor_class = WordsExtractor
    compound_prepositions_list = COMPOUND_PREPOSITIONS
    parentheticals_list = PARENTHETICALS
    cliches_list = OFFICIALESE_CLICHES
    stats_desc = STYLE_STATS_DESC

    def __init__(
        self,
        source: str | Doc,
        words_extractor: anyts.WordsExtractor | None = None,
        stopwords: Collection[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
        cliches: Collection[str] | None = None,
        nlp: Language | None = None,
        nausea_stopwords: Collection[str] | None = None,
    ):
        _check_nlp(nlp)
        super().__init__(source, words_extractor, stopwords, top_n, cliches, nausea_stopwords)
        self.nlp = nlp
        # The Doc is not kept: this object in an extension of the Doc would make a cycle
        self._text: str | None = None
        self._nouns: list[tuple[str, str]] | None = None
        self._annotation_error = ""
        if isinstance(source, str):
            self._text = source
        else:
            try:
                self._nouns = _doc_nouns(source, self.messages)
            except SourceError as error:
                self._annotation_error = str(error)

    def is_stopword(self, word: str) -> bool:
        """Stopword of STOPWORD_FORMS (is_stopword)"""
        return is_stopword(word)

    def is_parenthetical(self, word: str) -> bool:
        """One-word expression of PARENTHETICALS (is_parenthetical)"""
        return is_parenthetical(word)

    def expand_phrases(self, text: Sequence[str], phrases: Collection[str]) -> dict[str, str]:
        """Phrases with their contractions and the forms of their verbs (expand_phrases)"""
        return expand_phrases(text, phrases)

    def __getstate__(self) -> dict[str, Any]:
        """
        State for pickle and copy without the pipeline: the nouns of a string are read by
        it first, so the copy keeps them
        """
        state = self.__dict__.copy()
        if state.get("nlp") is not None:
            with suppress(SourceError):
                state["_nouns"] = self.nouns()
            state["nlp"] = None
        return state

    def nouns(self) -> list[tuple[str, str]]:
        """
        Getting the nouns of the text with their lemmas

        Description:
            The tokens tagged NOUN of a Doc, or of a string parsed by nlp or
            get_nlp() when they are first read, without the parser and the named
            entities; a string longer than the max_length of the pipeline is
            parsed in parts of whole sentences

        Returns:
            list[tuple[str, str]]: Nouns in lower case with their lemmas

        Raises:
            SourceError: If the source lacks the parts of speech or the lemmas, or a
                sentence of a string is longer than the max_length of the pipeline
        """
        if self._nouns is None:
            if self._text is None:
                raise SourceError(self._annotation_error)
            pipeline = self.nlp or get_nlp()
            parts = _split_text(self._text, pipeline.max_length)
            self._nouns = [
                noun
                for doc in pipeline.pipe(parts, disable=UNUSED_COMPONENTS)
                for noun in _doc_nouns(doc, self.messages)
            ]
        return self._nouns

    def is_verbal_noun(self, lemma: str) -> bool:
        """Noun derived from a verb (ests.utils.is_verbal_noun)"""
        return is_verbal_noun(lemma)


def _split_text(text: str, max_length: int) -> list[str]:
    """
    Splitting a text into parts of whole sentences no longer than a limit

    Description:
        A text within the limit is one part; a longer one is cut at the ends
        of the sentences of sentenize, every part as long as the limit allows

    Arguments:
        text (str): Text
        max_length (int): Maximum length of a part in characters

    Returns:
        list[str]: Parts of the text

    Raises:
        SourceError: If a sentence is longer than the limit
    """
    if len(text) <= max_length:
        return [text]
    parts = []
    start = stop = -1
    for begin, end, _ in iter_text_sents(text):
        if end - begin > max_length:
            raise SourceError(
                f"A sentence of {end - begin} characters is longer than the limit of the "
                f"pipeline ({max_length}): raise max_length on a pipeline of your own "
                "and pass it in nlp"
            )
        if start < 0:
            start = begin
        elif end - start > max_length:
            parts.append(text[start:stop])
            start = begin
        stop = end
    parts.append(text[start:stop])
    return parts


def noun_lemmas(doc: Doc) -> list[str]:
    """
    Getting the lemmas of the nouns of a Doc

    Arguments:
        doc (Doc): Doc object

    Returns:
        list[str]: Lemmas of the tokens tagged NOUN

    Raises:
        SourceTypeError: If the source is not a Doc
        SourceError: If the Doc lacks the parts of speech or the lemmas
    """
    if not is_doc(doc):
        raise SourceTypeError(f"A Doc is expected, not {type(doc).__name__}")
    return [lemma for _, lemma in _doc_nouns(doc)]


def _doc_nouns(doc: Doc, messages: Mapping[str, str] = MESSAGES) -> list[tuple[str, str]]:
    """The tokens of a Doc tagged NOUN, in lower case, with their lemmas"""
    if not doc.has_annotation("POS"):
        raise SourceError(messages["no_pos"])
    if not doc.has_annotation("LEMMA"):
        raise SourceError(messages["no_lemmas"])
    return [
        (token.text.lower(), token.lemma_)
        for token in iter_doc_tokens(doc)
        if token.pos_ == "NOUN"
    ]


def is_stopword(word: str) -> bool:
    """
    Checking whether a word is a stopword

    Description:
        The word forms of STOPWORDS and the one-word parenthetical expressions
        of PARENTHETICALS (finalmente, naturalmente), in any case

    Arguments:
        word (str): Word

    Returns:
        bool: Result of the check

    Raises:
        SourceTypeError: If the word is not a string

    Example:
        >>> from ests.style_stats import is_stopword
        >>> is_stopword("Aquel"), is_stopword("sin"), is_stopword("trigo")
        (True, True, False)
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"The word must be a string, not {type(word).__name__}")
    return word.lower() in STOPWORD_FORMS


def is_parenthetical(word: str) -> bool:
    """
    Checking whether a word is a parenthetical expression by itself

    Description:
        The one-word expressions of PARENTHETICALS (finalmente, naturalmente,
        verbigracia), in any case

    Arguments:
        word (str): Word

    Returns:
        bool: Result of the check

    Raises:
        SourceTypeError: If the word is not a string
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"The word must be a string, not {type(word).__name__}")
    return word.lower() in PARENTHETICAL_WORDS


def calc_verbal_nouns(nouns: Sequence[str]) -> float:
    """
    Computing the share of the verbal nouns

    Description:
        The share of the nouns derived from a verb (is_verbal_noun: revisión,
        aprendizaje, uso) among the lemmas of the nouns in percent; nan without
        nouns. Pass the lemmas of the tokens tagged NOUN (noun_lemmas), not the
        words: a noun and a verb form may be spelt alike (uso, viaje)

    Arguments:
        nouns (list[str]): Lemmas of the nouns

    Returns:
        float: Share in percent

    Raises:
        SourceTypeError: If the nouns are not a list of strings

    Example:
        >>> from ests.style_stats import calc_verbal_nouns
        >>> calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
        50.0
    """
    check_words(nouns, "nouns")
    verbal = sum(1 for lemma in nouns if is_verbal_noun(lemma))
    return safe_divide(verbal, len(nouns), nan) * 100


def expand_phrases(text: Sequence[str], phrases: Collection[str]) -> dict[str, str]:
    """
    Spelling out the phrases in the forms a text has

    Description:
        A phrase ending in a or de also takes al or del (conforme al). A phrase
        whose first word is an infinitive (dar cumplimiento) takes the forms of
        the text with that lemma (dio cumplimiento): the lemma of lemmatize, a
        pronominal one counting for its verb (llevarse - llevar), or of
        IRREGULAR_VERB_FORMS (dado, hecho, dese). When phrases spell out the
        same words, a phrase written so wins over the forms of another, then
        the first phrase of a list or of a set in sorted order

    Arguments:
        text (list[str]): List of words
        phrases (list[str]|set[str]): Phrases, words separated by spaces

    Returns:
        dict[str, str]: Phrases with their contractions and the forms of their
            verbs, each with the phrase of the list it spells out

    Raises:
        SourceTypeError: If the words are not a list of strings or the phrases are not
            a list or a set of strings

    Example:
        >>> from ests.style_stats import expand_phrases
        >>> expanded = expand_phrases(["se", "procedió", "al", "cierre"], ["proceder a"])
        >>> sorted(expanded)
        ['proceder a', 'proceder al', 'procedió a', 'procedió al']
        >>> expanded["procedió al"]
        'proceder a'
    """
    check_words(text)
    check_words(phrases, "phrases", ordered=False)
    heads = {
        words[0]
        for phrase in phrases
        if (words := phrase.lower().split())
        and words[0].endswith(INFINITIVE_ENDINGS)
        and lemmatize(words[0]) == words[0]
    }
    forms: dict[str, set[str]] = {head: {head} for head in heads}
    if heads:
        for form in {word.lower() for word in text}:
            lemma = IRREGULAR_VERB_FORMS.get(form) or lemmatize(form)
            if lemma not in forms:
                lemma = lemma.removesuffix("se")
            if lemma in forms:
                forms[lemma].add(form)
    ordered = [
        (phrase, words) for phrase in in_order(phrases) if (words := phrase.lower().split())
    ]
    # The spelling of a phrase itself wins over the forms of another phrase
    expanded: dict[str, str] = {}
    for phrase, words in ordered:
        expanded.setdefault(" ".join(words), phrase)
    for phrase, words in ordered:
        firsts = forms.get(words[0], {words[0]})
        if len(words) == 1:
            for first in sorted(firsts):
                expanded.setdefault(first, phrase)
            continue
        endings = [words[-1]]
        if words[-1] == "a":
            endings.append("al")
        elif words[-1] == "de":
            endings.append("del")
        for first in sorted(firsts):
            for ending in endings:
                expanded.setdefault(" ".join([first, *words[1:-1], ending]), phrase)
    return expanded


def calc_academic_nausea(
    text: Sequence[str],
    top_n: int = NAUSEA_TOP_N,
    stopwords: Collection[str] | None = None,
) -> float:
    """
    Computing the academic nausea

    Description:
        The summed frequency of the top_n most frequent significant words
        (find_nausea_words) per 100 words of the text (Advego); the exact
        formula of Advego is not published. The norm of Advego is 5-15%, for
        texts of several hundred words. The calc_academic_nausea of the core
        with is_stopword

    References:
        https://advego.com/text/seo/

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words
        stopwords (list[str]|set[str]): Stopwords left out of the most frequent words;
            is_stopword if not set

    Returns:
        float: Value of the nausea in percent

    Raises:
        SourceTypeError: If the words are not a list of strings or the stopwords are not
            a list or a set of strings
        ParameterError: If top_n is not an integer or is below one
    """
    return anyts.style_stats.calc_academic_nausea(text, top_n, stopwords, is_stopword=is_stopword)


def find_nausea_words(
    text: Sequence[str],
    top_n: int = NAUSEA_TOP_N,
    stopwords: Collection[str] | None = None,
) -> dict[str, int]:
    """
    Finding the most frequent significant words of the academic nausea

    Description:
        The top_n most frequent words without the stopwords - those of the
        list passed, in any case, or of is_stopword - with their occurrences,
        the most frequent first and words of equal frequency in the order of
        the text. The find_nausea_words of the core with is_stopword

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words
        stopwords (list[str]|set[str]): Stopwords; is_stopword if not set

    Returns:
        dict[str, int]: Occurrences of every word

    Raises:
        SourceTypeError: If the words are not a list of strings or the stopwords are not
            a list or a set of strings
        ParameterError: If top_n is not an integer or is below one

    Example:
        >>> from ests.style_stats import find_nausea_words
        >>> find_nausea_words(["gato", "y", "gato", "y", "perro"], top_n=1)
        {'gato': 2}
    """
    return anyts.style_stats.find_nausea_words(text, top_n, stopwords, is_stopword=is_stopword)


def calc_water(text: Sequence[str], stopwords: Collection[str] | None = None) -> float:
    """
    Computing the water content

    Description:
        The share of the words that carry no content in percent (Text.ru): the
        stopwords of is_stopword or of the list passed, in any case. The norms
        of Text.ru are set for Russian, which has no articles, so a Spanish
        text has more water by its grammar alone. The calc_water of the core
        with is_stopword

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words
        stopwords (list[str]|set[str]): List or set of stopwords; is_stopword if not set

    Returns:
        float: Value of the water content in percent

    Raises:
        SourceTypeError: If the words are not a list of strings or the stopwords are not
            a list or a set of strings
    """
    return anyts.style_stats.calc_water(text, stopwords, is_water_word=is_stopword)


def calc_phrase_density(text: Sequence[str], phrases: Collection[str]) -> float:
    """
    Computing the density of the phrases of a list

    Description:
        The number of occurrences of the phrases per 100 words, with the
        contractions and the forms of the verbs of expand_phrases; used for
        the compound prepositions (COMPOUND_PREPOSITIONS) and the clichés
        (OFFICIALESE_CLICHES). The calc_phrase_density of the core with
        expand_phrases

    Arguments:
        text (list[str]): List of words
        phrases (list[str]|set[str]): Phrases, words separated by spaces

    Returns:
        float: Occurrences per 100 words

    Raises:
        SourceTypeError: If the words are not a list of strings or the phrases are not
            a list or a set of strings
    """
    return anyts.style_stats.calc_phrase_density(text, phrases, expand=expand_phrases)


def calc_parentheticals(text: Sequence[str]) -> float:
    """
    Computing the density of the parenthetical expressions

    Description:
        The expressions of PARENTHETICALS (sin embargo, es decir, por ejemplo,
        finalmente) per 100 words, whatever the punctuation. The
        calc_parentheticals of the core with the Spanish expressions

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Parenthetical expressions per 100 words

    Raises:
        SourceTypeError: If the words are not a list of strings
    """
    return anyts.style_stats.calc_parentheticals(
        text, PARENTHETICALS, is_parenthetical=is_parenthetical, expand=expand_phrases
    )


def find_parentheticals(text: Sequence[str]) -> list[tuple[int, int]]:
    """
    Finding the parenthetical expressions

    Description:
        The expressions of PARENTHETICALS with the contractions of
        expand_phrases, as in calc_parentheticals

    Arguments:
        text (list[str]): List of words

    Returns:
        list[tuple[int, int]]: Bounds of the expressions found as slices of text, in order

    Raises:
        SourceTypeError: If the words are not a list of strings

    Example:
        >>> from ests.style_stats import find_parentheticals
        >>> find_parentheticals(["sin", "embargo", "el", "gato", "finalmente", "duerme"])
        [(0, 2), (4, 5)]
    """
    return anyts.style_stats.find_parentheticals(
        text, PARENTHETICALS, is_parenthetical=is_parenthetical, expand=expand_phrases
    )
