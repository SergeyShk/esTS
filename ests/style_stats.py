from collections import Counter
from collections.abc import Sequence
from functools import cached_property
from math import nan, sqrt

from spacy.language import Language
from spacy.tokens import Doc

from .constants import (
    COMPOUND_PREPOSITIONS,
    NAUSEA_TOP_N,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORDS,
    STYLE_STATS_DESC,
)
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import WordsExtractor
from .utils import (
    find_phrases,
    get_nlp,
    is_verbal_noun,
    iter_doc_tokens,
    iter_doc_words,
    lemmatize,
    safe_divide,
)

# Components the parts of speech and the lemmas of the nouns do not need
UNUSED_COMPONENTS = ["parser", "ner"]
# One-word parenthetical expressions, which the water counts as stopwords
PARENTHETICAL_WORDS = frozenset(phrase for phrase in PARENTHETICALS if " " not in phrase)
# Endings of the infinitive, whose phrases stand for every form of the verb
INFINITIVE_ENDINGS = ("ar", "er", "ir", "ír")


def check_params(top_n: int) -> None:
    """
    Checking the parameters of the style metrics

    Arguments:
        top_n (int): Number of the most frequent words

    Raises:
        ParameterError: If the number of the most frequent words is below one
    """
    if top_n < 1:
        raise ParameterError("The number of the most frequent words must be greater than 0")


class StyleStats:
    """
    Class for computing the style metrics of a text

    Description:
        The SEO metrics repeat the indicators of the services Advego and
        Text.ru: nausea, water content, spam score, naturalness of the
        distribution of words by Zipf's law and keyword density. The exact
        formulas of the services are not published, so the commonly accepted
        definitions are implemented; they are described in the docstrings of
        the functions
        The lexical markers of the officialese style: the nouns derived from a
        verb, the compound prepositions of the administrative style, the
        parenthetical expressions and the clichés, by the lists of constants
        The words are extracted in lower case without lemmatization by default;
        to compute the SEO metrics by lemmas, pass
        WordsExtractor(use_lexemes=True, lowercase=True). The words of a Doc are
        taken without punctuation (iter_doc_words)
        The markers of the officialese style are counted over the unfiltered
        word forms (forms), whatever the extractor passed. The verbal nouns
        need the parts of speech and the lemmas: they are read from a Doc, and
        a string is parsed by the model when they are first read, so the other
        metrics of a string need no model

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
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words; when the verbal nouns are read,
            if a Doc lacks the parts of speech or a string is longer than the
            max_length of the pipeline
        ParameterError: If the number of the most frequent words is below one
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
        if isinstance(source, Doc):
            self.words = tuple(text.lower() for _, _, text in iter_doc_words(source))
            self.forms = self.words
        elif isinstance(source, str):
            forms = WordsExtractor(lowercase=True).extract(source)
            self.words = words_extractor.extract(source) if words_extractor else forms
            self.forms = forms
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not self.words:
            raise SourceError("The data source has no words")
        check_params(top_n)
        self.source = source
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
        return calc_verbal_nouns(self._noun_lemmas())

    @property
    def compound_prepositions(self) -> float:
        return calc_phrase_density(self.forms, COMPOUND_PREPOSITIONS)

    @property
    def parentheticals(self) -> float:
        return calc_parentheticals(self.forms)

    @property
    def cliches(self) -> float:
        return calc_phrase_density(self.forms, self.cliches_list)

    def _noun_lemmas(self) -> list[str]:
        """
        Lemmas of the nouns of the text

        Description:
            A Doc gives its own annotation; a string is parsed by the pipeline,
            without the parser and the named entities

        Returns:
            list[str]: Lemmas of the tokens tagged NOUN

        Raises:
            SourceError: If a Doc lacks the parts of speech or a string is longer
                than the max_length of the pipeline
        """
        doc = self.source
        if isinstance(doc, str):
            pipeline = self.nlp or get_nlp()
            if len(doc) > pipeline.max_length:
                raise SourceError(
                    f"The text of {len(doc)} characters is longer than the limit of the "
                    f"pipeline ({pipeline.max_length}): split it into parts or raise "
                    "max_length on a pipeline of your own and pass it in nlp"
                )
            doc = pipeline(doc, disable=UNUSED_COMPONENTS)
        if not doc.has_annotation("POS"):
            raise SourceError(
                "The data source has no annotation of the parts of speech: "
                "parse the text with a model instead of a blank pipeline"
            )
        return [token.lemma_ for token in iter_doc_tokens(doc) if token.pos_ == "NOUN"]

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


def is_stopword(word: str) -> bool:
    """
    Checking whether a word is a stopword

    Description:
        The word forms of STOPWORDS - determiners, pronouns, prepositions,
        conjunctions, interjections, the adverbs that point, relate or ask and
        the ones that negate, affirm or focus - and the one-word parenthetical
        expressions of PARENTHETICALS (finalmente, naturalmente), in any case

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
        (Advego). It measures how insistent one word is regardless of the length
        of the text, so it grows with the text. The norm of Advego is at most 7,
        1-5 in practice

    References:
        https://advego.com/text/seo/

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Value of the nausea
    """
    if not text:
        return 0.0
    return sqrt(max(Counter(text).values()))


def calc_academic_nausea(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Computing the academic nausea

    Description:
        The share of the occurrences of the most frequent words of the text in
        percent (Advego). The exact formula of Advego is not published: the
        summed frequency of the top_n most frequent words is divided by the
        number of words. The norm of Advego is 5-15%

    References:
        https://advego.com/text/seo/

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words

    Returns:
        float: Value of the nausea in percent
    """
    top_freqs = sum(freq for _, freq in Counter(text).most_common(top_n))
    return safe_divide(100 * top_freqs, len(text))


def calc_water(text: Sequence[str], stopwords: Sequence[str] | None = None) -> float:
    """
    Computing the water content

    Description:
        The share of the words that carry no content in percent (Text.ru): the
        stopwords of is_stopword or of the list passed, in any case. The norms
        of Text.ru are set for Russian, which has no articles: a Spanish text
        has more water by its grammar alone: the texts of the corpus of
        literature have 42-54% of it, the prose 49% by the median

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words
        stopwords (list[str]): List of stopwords; is_stopword if not set

    Returns:
        float: Value of the water content in percent
    """
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
        The share of the repeated words of the text in percent (Text.ru): every
        occurrence of a word but the first is a repetition, so the spam score
        is 100 · (1 - TTR). To compute it by lemmas, extract the words with
        lemmatization. The norms of Text.ru: up to 30% - natural, 30-60% -
        SEO-optimized, above 60% - spammed

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Value of the spam score in percent
    """
    n_words = len(text)
    return safe_divide(100 * (n_words - len(set(text))), n_words)


def calc_zipf_naturalness(text: Sequence[str], top_n: int = NAUSEA_TOP_N) -> float:
    """
    Computing the naturalness of a text by Zipf's law

    Description:
        How well the frequencies of the most frequent words agree with the
        ideal distribution f_r = f_1 / r, where f_1 is the frequency of the most
        frequent word and r is the rank of a word (pr-cy, megaindex). It is
        100 · (1 - the mean relative deviation of the frequencies from the
        ideal ones) over the ranks from 2 to min(top_n, V, f_1): rank 1 matches
        the ideal by construction, and above the rank f_1 the ideal frequency
        is below one and the deviation of the hapaxes grows without a bound.
        Negative values are clipped to 0; the norm of the services is at least
        50%. It is undefined when there are no ranks to compare: every word is
        a hapax, the text has one word type or top_n is below 2

    References:
        https://en.wikipedia.org/wiki/Zipf's_law

    Arguments:
        text (list[str]): List of words
        top_n (int): Number of the most frequent words

    Returns:
        float: Value of the naturalness in percent, nan if there are no ranks to compare
    """
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
        compared in any case; to compare by lemmas, extract the words with
        lemmatization and pass lemmas

    References:
        https://text.ru/seo

    Arguments:
        text (list[str]): List of words
        keywords (list[str]): Keywords or phrases

    Returns:
        dict[str, float]: Density of every keyword in percent
    """
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
        nombramiento, aprendizaje, uso) among the lemmas of the nouns of a text
        in percent; nan for a text without nouns. Spanish tells a noun from a
        verb form by the annotation only (uso, viaje, dura), so the lemmas of the
        tokens tagged NOUN are passed, not the words

    Arguments:
        nouns (list[str]): Lemmas of the nouns

    Returns:
        float: Share in percent

    Example:
        >>> from ests.style_stats import calc_verbal_nouns
        >>> calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
        50.0
    """
    verbal = sum(1 for lemma in nouns if is_verbal_noun(lemma))
    return safe_divide(verbal, len(nouns), nan) * 100


def expand_phrases(text: Sequence[str], phrases: Sequence[str]) -> list[str]:
    """
    Spelling out the phrases in the forms a text has

    Description:
        A phrase ending in a or de also takes the contraction with the article,
        al or del (a efectos del, conforme al). A phrase whose first word is an
        infinitive (proceder a, dar cumplimiento, ser de aplicación) takes the
        forms of the text whose lemma (lemmatize) is that infinitive: procedió
        a, dio cumplimiento, es de aplicación; the lemmas are those of
        simplemma, so a form it does not know (llevarse) is not found

    Arguments:
        text (list[str]): List of words
        phrases (list[str]): Phrases, words separated by spaces

    Returns:
        list[str]: Phrases with their contractions and the forms of their verbs

    Example:
        >>> from ests.style_stats import expand_phrases
        >>> sorted(expand_phrases(["se", "procedió", "al", "cierre"], ["proceder a"]))
        ['proceder a', 'proceder al', 'procedió a', 'procedió al']
    """
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
            lemma = lemmatize(form)
            if lemma in forms:
                forms[lemma].add(form)
    expanded = []
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
        middle = words[1:-1] if len(words) > 1 else []
        for first in firsts:
            if len(words) == 1:
                expanded.append(first)
                continue
            for ending in endings:
                expanded.append(" ".join([first, *middle, ending]))
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
    """
    return safe_divide(len(find_phrases(text, expand_phrases(text, phrases))), len(text)) * 100


def calc_parentheticals(text: Sequence[str]) -> float:
    """
    Computing the density of the parenthetical expressions

    Description:
        The expressions of PARENTHETICALS (sin embargo, es decir, por ejemplo,
        finalmente) per 100 words. The punctuation is not looked at: the list
        holds the expressions that stand apart in most of their occurrences

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Parenthetical expressions per 100 words
    """
    return calc_phrase_density(text, PARENTHETICALS)
