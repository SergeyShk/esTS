from collections import Counter
from collections.abc import Sequence
from functools import cached_property
from math import nan, sqrt

import anyts
from anyts.utils import check_integer, check_words, iter_doc_tokens, iter_doc_words, safe_divide
from spacy.language import Language
from spacy.tokens import Doc

from .constants import (
    COMPOUND_PREPOSITIONS,
    IRREGULAR_VERB_FORMS,
    NAUSEA_TOP_N,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORDS,
    STYLE_STATS_DESC,
)
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import WordsExtractor
from .utils import find_phrases, get_nlp, is_verbal_noun, iter_text_sents, lemmatize

# Components the parts of speech and the lemmas of the nouns do not need
UNUSED_COMPONENTS = ["parser", "ner"]
# One-word parenthetical expressions, which the water counts as stopwords
PARENTHETICAL_WORDS = frozenset(phrase for phrase in PARENTHETICALS if " " not in phrase)
# Endings of the infinitive, whose phrases stand for the forms of the verb
INFINITIVE_ENDINGS = ("ar", "er", "ir", "ír")


def check_params(top_n: int) -> None:
    """
    Checking the parameters of the style metrics

    Arguments:
        top_n (int): Number of the most frequent words

    Raises:
        ParameterError: If the number of the most frequent words is not an integer or is below one
    """
    check_integer(top_n, "number of the most frequent words")
    if top_n < 1:
        raise ParameterError("The number of the most frequent words must be greater than 0")


class StyleStats:
    """
    Class for computing the style metrics of a text

    Description:
        The SEO metrics follow the indicators of Advego and Text.ru (nausea,
        water content, spam score, naturalness by Zipf's law, keyword density),
        whose exact formulas are not published. The words are extracted in
        lower case without lemmatization by default; for the SEO metrics by
        lemmas, pass WordsExtractor(use_lexemes=True, lowercase=True)
        The markers of the officialese style - the verbal nouns, the compound
        prepositions, the parenthetical expressions and the clichés - are
        counted over the unfiltered word forms (forms), whatever the extractor.
        The verbal nouns need the parts of speech and the lemmas: a string is
        parsed by the model only when they are first read, in parts of whole
        sentences if it is longer than the max_length of the pipeline

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
        words_extractor (WordsExtractor): Word extraction tool
        stopwords (list[str]): Stopwords for the water content; STOPWORDS and
            the one-word parenthetical expressions if not set
        top_n (int): Number of the most frequent words for the academic nausea
            and the naturalness by Zipf's law
        cliches (list[str]): List of clichés; OFFICIALESE_CLICHES if not set
        nlp (Language): Pipeline that parses a string for the verbal nouns;
            get_nlp() if not set

    Attributes:
        words (tuple[str]): Tuple of the extracted words
        forms (tuple[str]): Tuple of the unfiltered word forms in lower case
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
        get_stats: Getting the computed style metrics of the text
        print_stats: Printing the computed style metrics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc, or the
            stopwords or the clichés are not a list of strings, or the extractor or the
            pipeline is of another type
        SourceError: If the source has no words; when the verbal nouns are read,
            if the source lacks the parts of speech or the lemmas or a sentence
            of a string is longer than the max_length of the pipeline
        ParameterError: If the number of the most frequent words is not an integer or is
            below one
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        stopwords: Sequence[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
        cliches: Sequence[str] | None = None,
        nlp: Language | None = None,
    ):
        if words_extractor is not None and not isinstance(words_extractor, anyts.WordsExtractor):
            raise SourceTypeError("The word extractor must be a WordsExtractor")
        if nlp is not None and not isinstance(nlp, Language):
            raise SourceTypeError("The pipeline must be a spaCy Language")
        check_params(top_n)
        if stopwords is not None:
            check_words(stopwords, "stopwords")
        if cliches is not None:
            check_words(cliches, "clichés")
        # The Doc is not kept: this object in an extension of the Doc would make a cycle
        self._text: str | None = None
        self._nouns: list[str] | None = None
        self._annotation_error = ""
        if isinstance(source, Doc):
            self.words = tuple(text.lower() for _, _, text in iter_doc_words(source))
            self.forms = self.words
            try:
                self._nouns = noun_lemmas(source)
            except SourceError as error:
                self._annotation_error = str(error)
        elif isinstance(source, str):
            forms = WordsExtractor(lowercase=True).extract(source)
            self.words = words_extractor.extract(source) if words_extractor else forms
            self.forms = forms
            self._text = source
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not self.words:
            raise SourceError("The data source has no words")
        self.stopwords = tuple(stopwords) if stopwords is not None else None
        self.top_n = top_n
        self.cliches_list = tuple(cliches) if cliches is not None else OFFICIALESE_CLICHES
        self.nlp = nlp

    @property
    def classic_nausea(self) -> float:
        return calc_classic_nausea(self.words)

    @property
    def academic_nausea(self) -> float:
        return calc_academic_nausea(self.words, self.top_n)

    @property
    def water(self) -> float:
        return calc_water(self.words, self.stopwords)

    @property
    def spam(self) -> float:
        return calc_spam(self.words)

    @property
    def zipf_naturalness(self) -> float:
        return calc_zipf_naturalness(self.words, self.top_n)

    @cached_property
    def verbal_nouns(self) -> float:
        if self._nouns is None:
            if self._text is None:
                raise SourceError(self._annotation_error)
            self._nouns = self._parse(self._text)
        return calc_verbal_nouns(self._nouns)

    @property
    def compound_prepositions(self) -> float:
        return calc_phrase_density(self.forms, COMPOUND_PREPOSITIONS)

    @property
    def parentheticals(self) -> float:
        return calc_parentheticals(self.forms)

    @property
    def cliches(self) -> float:
        return calc_phrase_density(self.forms, self.cliches_list)

    def _parse(self, text: str) -> list[str]:
        """
        Parsing a string for the lemmas of the nouns

        Description:
            The pipeline of nlp or get_nlp(), without the parser and the named
            entities; a text longer than the max_length of the pipeline is
            parsed in parts of whole sentences

        Arguments:
            text (str): Text

        Returns:
            list[str]: Lemmas of the tokens tagged NOUN

        Raises:
            SourceError: If a sentence is longer than the max_length of the pipeline
        """
        pipeline = self.nlp or get_nlp()
        parts = _split_text(text, pipeline.max_length)
        return [
            lemma
            for doc in pipeline.pipe(parts, disable=UNUSED_COMPONENTS)
            for lemma in noun_lemmas(doc)
        ]

    def keyword_density(self, *keywords: str) -> dict[str, float]:
        """
        Computing the density of keywords and phrases

        Arguments:
            keywords (tuple[str]): Keywords or phrases of several words separated by spaces

        Returns:
            dict[str, float]: Density of every keyword in percent
        """
        return calc_keyword_density(self.words, keywords)

    def get_stats(self) -> dict[str, float]:
        """
        Getting the computed style metrics of the text

        Returns:
            dict[str, float]: Dictionary of the computed style metrics
        """
        return {stat: getattr(self, stat) for stat in STYLE_STATS_DESC}

    def print_stats(self) -> None:
        """Printing the computed style metrics of the text with descriptions"""
        print(f"{'Metric':^50}|{'Value':^10}")
        print("-" * 60)
        stats = self.get_stats()
        for stat, desc in STYLE_STATS_DESC.items():
            print(f"{desc:50}|{stats[stat]:^10.2f}")


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
        SourceError: If the Doc lacks the parts of speech or the lemmas
    """
    if not doc.has_annotation("POS"):
        raise SourceError(
            "The data source has no annotation of the parts of speech: "
            "parse the text with a model instead of a blank pipeline"
        )
    if not doc.has_annotation("LEMMA"):
        raise SourceError(
            "The data source has no lemmas: parse the text with a pipeline that has a lemmatizer"
        )
    return [token.lemma_ for token in iter_doc_tokens(doc) if token.pos_ == "NOUN"]


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

    Example:
        >>> from ests.style_stats import is_stopword
        >>> is_stopword("Aquel"), is_stopword("sin"), is_stopword("trigo")
        (True, True, False)
    """
    word = word.lower()
    return word in STOPWORDS or word in PARENTHETICAL_WORDS


def calc_classic_nausea(text: Sequence[str]) -> float:
    """
    Computing the classic nausea

    Description:
        The square root of the number of occurrences of the most frequent word
        (Advego); it grows with the text. The norm of Advego is at most 7, 1-5
        in practice

    References:
        https://advego.com/text/seo/

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Value of the nausea

    Raises:
        SourceTypeError: If the words are not a list of strings
    """
    check_words(text)
    if not text:
        return 0.0
    return sqrt(max(Counter(text).values()))


def calc_academic_nausea(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Computing the academic nausea

    Description:
        The summed frequency of the top_n most frequent words per 100 words
        (Advego). The norm of Advego is 5-15%

    References:
        https://advego.com/text/seo/

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words

    Returns:
        float: Value of the nausea in percent

    Raises:
        SourceTypeError: If the words are not a list of strings
        ParameterError: If top_n is not an integer or is below one
    """
    check_words(text)
    check_params(top_n)
    top_freqs = sum(freq for _, freq in Counter(text).most_common(top_n))
    return safe_divide(100 * top_freqs, len(text))


def calc_water(text: Sequence[str], stopwords: Sequence[str] | None = None) -> float:
    """
    Computing the water content

    Description:
        The share of the words that carry no content in percent (Text.ru): the
        stopwords of is_stopword or of the list passed, in any case. The norms
        of Text.ru are set for Russian, which has no articles, so a Spanish
        text has more water by its grammar alone

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words
        stopwords (list[str]): List of stopwords; is_stopword if not set

    Returns:
        float: Value of the water content in percent

    Raises:
        SourceTypeError: If the words or the stopwords are not a list of strings
    """
    check_words(text)
    if stopwords is not None:
        check_words(stopwords, "stopwords")
    if stopwords is not None:
        stopwords_set = {word.lower() for word in stopwords}
        n_stopwords = sum(1 for word in text if word.lower() in stopwords_set)
    else:
        n_stopwords = sum(1 for word in text if is_stopword(word))
    return safe_divide(100 * n_stopwords, len(text))


def calc_spam(text: Sequence[str]) -> float:
    """
    Computing the spam score

    Description:
        The share of the repeated words in percent (Text.ru), every occurrence
        of a word after the first: 100 · (1 - TTR). The norms of Text.ru: up to
        30% - natural, 30-60% - SEO-optimized, above 60% - spammed

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Value of the spam score in percent

    Raises:
        SourceTypeError: If the words are not a list of strings
    """
    check_words(text)
    n_words = len(text)
    return safe_divide(100 * (n_words - len(set(text))), n_words)


def calc_zipf_naturalness(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Computing the naturalness of a text by Zipf's law

    Description:
        100 · (1 - the mean relative deviation of the frequencies from the
        ideal f_r = f_1 / r), where f_1 is the frequency of the most frequent
        word, over the ranks r from 2 to min(top_n, V, f_1), V the number of
        word types, clipped to 0 (pr-cy, megaindex); the norm of the services
        is at least 50%. Undefined when there are no ranks to compare: every
        word is a hapax, the text has one word type or top_n is below 2

    References:
        https://en.wikipedia.org/wiki/Zipf's_law

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words

    Returns:
        float: Value of the naturalness in percent, nan if there are no ranks to compare

    Raises:
        SourceTypeError: If the words are not a list of strings
        ParameterError: If top_n is not an integer or is below one
    """
    check_words(text)
    check_params(top_n)
    frequencies = sorted(Counter(text).values(), reverse=True)
    if not frequencies:
        return nan
    top_freq = frequencies[0]
    n_ranks = min(top_n, len(frequencies), top_freq)
    if n_ranks < 2:
        return nan
    deviation = sum(
        abs(freq - top_freq / rank) / (top_freq / rank)
        for rank, freq in enumerate(frequencies[1:n_ranks], start=2)
    ) / (n_ranks - 1)
    return max(0.0, 100 * (1 - deviation))


def calc_keyword_density(text: Sequence[str], keywords: Sequence[str]) -> dict[str, float]:
    """
    Computing the density of keywords

    Description:
        The frequency of every keyword per 100 words of the text (Text.ru). A
        keyword of several words separated by spaces is looked for as a
        sequence of words, and its occurrences may overlap. The words are
        compared in any case

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words
        keywords (list[str]): Keywords or phrases

    Returns:
        dict[str, float]: Density of every keyword in percent

    Raises:
        SourceTypeError: If the words or the keywords are not a list of strings
    """
    check_words(text)
    check_words(keywords, "keywords")
    n_words = len(text)
    lowered = [word.lower() for word in text]
    density = {}
    for keyword in keywords:
        parts = keyword.lower().split()
        size = len(parts)
        if not size:
            density[keyword] = 0.0
            continue
        count = sum(1 for i in range(n_words - size + 1) if lowered[i : i + size] == parts)
        density[keyword] = safe_divide(100 * count, n_words)
    return density


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
    """
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


def expand_phrases(text: Sequence[str], phrases: Sequence[str]) -> dict[str, str]:
    """
    Spelling out the phrases in the forms a text has

    Description:
        A phrase ending in a or de also takes al or del (conforme al). A phrase
        whose first word is an infinitive (dar cumplimiento) takes the forms of
        the text with that lemma (dio cumplimiento): the lemma of lemmatize, a
        pronominal one counting for its verb (llevarse - llevar), or of
        IRREGULAR_VERB_FORMS (dado, hecho, dese)

    Arguments:
        text (list[str]): List of words
        phrases (list[str]): Phrases, words separated by spaces

    Returns:
        dict[str, str]: Phrases with their contractions and the forms of their
            verbs, each with the phrase of the list it spells out

    Raises:
        SourceTypeError: If the words or the phrases are not a list of strings

    Example:
        >>> from ests.style_stats import expand_phrases
        >>> expanded = expand_phrases(["se", "procedió", "al", "cierre"], ["proceder a"])
        >>> sorted(expanded)
        ['proceder a', 'proceder al', 'procedió a', 'procedió al']
        >>> expanded["procedió al"]
        'proceder a'
    """
    check_words(text)
    check_words(phrases, "phrases")
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
    expanded: dict[str, str] = {}
    for phrase in phrases:
        words = phrase.lower().split()
        if not words:
            continue
        endings = [words[-1]]
        if words[-1] == "a":
            endings.append("al")
        elif words[-1] == "de":
            endings.append("del")
        firsts = forms.get(words[0], {words[0]})
        if len(words) == 1:
            expanded.update(dict.fromkeys(firsts, phrase))
            continue
        for first in firsts:
            for ending in endings:
                expanded.setdefault(" ".join([first, *words[1:-1], ending]), phrase)
    return expanded


def calc_phrase_density(text: Sequence[str], phrases: Sequence[str]) -> float:
    """
    Computing the density of the phrases of a list

    Description:
        The number of occurrences of the phrases (find_phrases) per 100 words,
        with the contractions and the forms of the verbs of expand_phrases;
        used for the compound prepositions (COMPOUND_PREPOSITIONS), the
        parenthetical expressions (PARENTHETICALS) and the clichés
        (OFFICIALESE_CLICHES)

    Arguments:
        text (list[str]): List of words
        phrases (list[str]): Phrases, words separated by spaces

    Returns:
        float: Occurrences per 100 words

    Raises:
        SourceTypeError: If the words or the phrases are not a list of strings
    """
    check_words(text)
    check_words(phrases, "phrases")
    return safe_divide(len(find_phrases(text, expand_phrases(text, phrases))), len(text)) * 100


def calc_parentheticals(text: Sequence[str]) -> float:
    """
    Computing the density of the parenthetical expressions

    Description:
        The expressions of PARENTHETICALS (sin embargo, es decir, por ejemplo,
        finalmente) per 100 words, whatever the punctuation

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Parenthetical expressions per 100 words

    Raises:
        SourceTypeError: If the words are not a list of strings
    """
    check_words(text)
    return calc_phrase_density(text, PARENTHETICALS)
