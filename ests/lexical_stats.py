from collections.abc import Sequence
from functools import cache, cached_property
from math import log2, log10, nan
from pathlib import Path
from statistics import fmean

from spacy.language import Language
from spacy.tokens import Doc

from .cohesion_stats import token_info
from .constants import FREQUENCY_BANDS, LEXICAL_STATS_DESC
from .datasets.freq_dict import Entry, FreqDict, lemma_key
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import NUMBER_PATTERN
from .utils import get_nlp, iter_doc_tokens, safe_divide

TOP_LEMMAS_FILE = Path(__file__).parent / "resources" / "google_books_top10000.txt"
# Components a parse of the text does not need: the lemmas come from lemma_key
UNUSED_COMPONENTS = ["parser", "lemmatizer", "ner"]


class LexicalStats:
    """
    Class for computing the lexical sophistication statistics of a text

    Description:
        Lexical sophistication in the manner of TAALES - how rare the words of
        the text are in the language: the mean frequency, range and dispersion
        of the lemmas by the frequency dictionary of Google Books Ngram
        (FreqDict), the shares of the words of the frequency bands top-1000,
        2000, 5000 and 10000 by the embedded list of the dictionary, the
        surprisal and the perplexity by the unigram model of the dictionary,
        the lexical density
        A word is looked up by lemma_key, the key the dictionary is built with:
        the lemma of simplemma of the word in lower case, and for a proper noun
        (PROPN) the lower-case form when the dictionary has it, so París is
        found as parís and not as the verb parir, while Estados of Estados
        Unidos, which the dictionary counts under estado, falls back to its
        lemma. The bands take the lower-case form of a proper noun, as the list
        alone cannot tell París from parir. The parts of speech come from the
        annotation, so the
        source has to be annotated: a string is parsed with the model
        es_core_news_sm or with the pipeline given in nlp, and a Doc must carry
        the parts of speech. A content word is one of CONTENT_UD_POS and no
        demonstrative, as in CohesionStats
        Numbers (2020, 5,5, 3.º) are no words: the dictionary and the list do
        not have them, and they would look like the rarest words of the text.
        The statistics by the dictionary need a downloaded FreqDict, the bands
        and the lexical density are computed without it

    References:
        https://doi.org/10.3758/s13428-017-0924-4 (Kyle, Crossley, Berger 2018, TAALES)
        https://storage.googleapis.com/books/ngrams/books/datasetsv3.html

    Example:
        >>> from ests import LexicalStats
        >>> text = "El gato estaba en la ventana y miraba a los pájaros"
        >>> ls = LexicalStats(text)
        >>> ls.lemmas
        ('el', 'gato', 'estar', 'en', 'el', 'ventana', 'y', 'mirar', 'a', 'el', 'pájaro')
        >>> round(ls.p_top1000, 3), round(ls.mean_log_ipm_content, 3), round(ls.surprisal, 3)
        (0.727, 2.192, 8.106)
        >>> ls.band_coverage(unique=True)
        {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        freq_dict (FreqDict): Frequency dictionary; FreqDict() of the default
            directory if not given
        nlp (Language): Pipeline of spaCy that parses a string; without it the
            model of SPACY_MODEL is loaded

    Attributes:
        words (tuple[str]): Tuple of the words
        lemmas (tuple[str]): Tuple of the lemmas of the words by lemma_key, the
            lower-case form for a proper noun; the bands are counted by them
        keys (tuple[str]): Tuple of the keys of the words in the frequency
            dictionary: the lemma of a proper noun when its form is not there
        n_words (int): Number of words
        n_content_words (int): Number of content words
        n_found (int): Number of words found in the frequency dictionary
        ranks (tuple[int|None]): Tuple of the ranks of the lemmas by the embedded
            list, None beyond the top 10000
        entries (tuple[Entry|None]): Tuple of the entries of the dictionary, None
            for a word out of it
        coverage (float): Share of words found in the frequency dictionary
        mean_ipm (float): Mean frequency of the words found
        mean_ipm_content (float): Mean frequency of the content words found
        mean_log_ipm (float): Mean decimal logarithm of the frequency of the words found
        mean_log_ipm_content (float): The same over the content words
        mean_range (float): Mean range of the words found - years out of 40
        mean_dispersion (float): Mean dispersion D of the words found
        surprisal (float): Mean surprisal of the words by the unigram model of
            the dictionary, in bits
        perplexity (float): Unigram perplexity - 2 to the power of the surprisal
        p_top1000 (float): Share of words with a lemma of the top 1000
        p_top2000 (float): Share of words with a lemma of the top 2000
        p_top5000 (float): Share of words with a lemma of the top 5000
        p_top10000 (float): Share of words with a lemma of the top 10000
        p_beyond_top10000 (float): Share of words with a lemma beyond the top 10000
        lexical_density (float): Share of content words

    Methods:
        band_coverage: Shares of the words or of the lemmas by frequency bands
        get_stats: Getting the computed lexical sophistication statistics
        print_stats: Printing the computed statistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words, lacks the parts of speech or
            is a string longer than the max_length of the pipeline
        DatasetNotFoundError: When a statistic by the dictionary is read and the
            dictionary is not downloaded
    """

    def __init__(
        self,
        source: str | Doc,
        freq_dict: FreqDict | None = None,
        nlp: Language | None = None,
    ):
        if isinstance(source, str):
            pipeline = nlp or get_nlp()
            if len(source) > pipeline.max_length:
                raise SourceError(
                    f"The text of {len(source)} characters is longer than the limit of the "
                    f"pipeline ({pipeline.max_length}): split it into parts or raise "
                    "max_length on a pipeline of your own and pass it in nlp"
                )
            source = pipeline(source, disable=UNUSED_COMPONENTS)
        elif not isinstance(source, Doc):
            raise SourceTypeError("The data source is set incorrectly")
        tokens = [token for token in iter_doc_tokens(source) if not is_number(token.text)]
        if not tokens:
            raise SourceError("The data source has no words")
        if not source.has_annotation("POS"):
            raise SourceError(
                "The data source has no annotation of the parts of speech: "
                "parse the text with a model instead of a blank pipeline"
            )
        self.freq_dict = freq_dict if freq_dict is not None else FreqDict()
        self.words = tuple(token.text for token in tokens)
        self._proper = tuple(token.pos_ == "PROPN" for token in tokens)
        self.lemmas = tuple(
            lemma_key(token.text, proper)
            for token, proper in zip(tokens, self._proper, strict=True)
        )
        self._content = tuple(token_info(token).content for token in tokens)
        self.n_words = len(self.words)
        self.n_content_words = sum(self._content)
        self.ranks = tuple(get_rank(lemma) for lemma in self.lemmas)
        self.lexical_density = self.n_content_words / self.n_words
        bands = self.band_coverage()
        self.p_top1000 = bands[1000]
        self.p_top2000 = bands[2000]
        self.p_top5000 = bands[5000]
        self.p_top10000 = bands[10000]
        self.p_beyond_top10000 = 1 - bands[10000]

    @cached_property
    def keys(self) -> tuple[str, ...]:
        """
        Keys of the words in the frequency dictionary

        Description:
            A proper noun is looked up by its form when the dictionary has it
            (París - parís) and by its lemma otherwise, as the dictionary was
            built: a form that is not capitalized in 90% of its occurrences
            is counted under its lemma, so Estados of Estados Unidos is in
            estado, and a verb tagged PROPN at the start of a sentence (Miró)
            is in mirar
        """
        return tuple(
            lemma_key(word) if proper and lemma not in self.freq_dict else lemma
            for word, lemma, proper in zip(self.words, self.lemmas, self._proper, strict=True)
        )

    @cached_property
    def entries(self) -> tuple[Entry | None, ...]:
        """
        Entries of the frequency dictionary for every word, None for the words out of it
        """
        return tuple(self.freq_dict.lookup(key) for key in self.keys)

    @property
    def n_found(self) -> int:
        return sum(1 for entry in self.entries if entry)

    @property
    def coverage(self) -> float:
        return self.n_found / self.n_words

    @property
    def mean_ipm(self) -> float:
        return _mean([entry.ipm for entry in self.entries if entry])

    @property
    def mean_ipm_content(self) -> float:
        return _mean([entry.ipm for entry in self._content_entries()])

    @property
    def mean_log_ipm(self) -> float:
        return _mean([log10(entry.ipm) for entry in self.entries if entry])

    @property
    def mean_log_ipm_content(self) -> float:
        return _mean([log10(entry.ipm) for entry in self._content_entries()])

    @property
    def mean_range(self) -> float:
        return _mean([entry.range for entry in self.entries if entry])

    @property
    def mean_dispersion(self) -> float:
        return _mean([entry.dispersion for entry in self.entries if entry])

    @cached_property
    def surprisal(self) -> float:
        return calc_surprisal(self.keys, self.freq_dict)

    @property
    def perplexity(self) -> float:
        return 2**self.surprisal

    def _content_entries(self) -> list[Entry]:
        """Entries of the content words found in the dictionary"""
        return [
            entry
            for entry, content in zip(self.entries, self._content, strict=True)
            if entry and content
        ]

    def band_coverage(
        self, bands: Sequence[int] = FREQUENCY_BANDS, unique: bool = False
    ) -> dict[int, float]:
        """
        Shares of the words by the frequency bands of the embedded list

        Arguments:
            bands (list[int]): Bounds of the bands - the sizes of the top lists
            unique (bool): Count the distinct lemmas instead of the words

        Returns:
            dict[int, float]: Share of the words with a lemma of the top N for every bound N

        Raises:
            ParameterError: If a bound is out of 1 and the size of the list (10000):
                beyond the list every share would be the one of the top 10000
        """
        size = len(load_top_lemmas())
        for band in bands:
            if not 1 <= band <= size:
                raise ParameterError(f"A bound of a band must be between 1 and {size} - {band}")
        ranks = [get_rank(lemma) for lemma in set(self.lemmas)] if unique else list(self.ranks)
        return {
            band: safe_divide(sum(1 for rank in ranks if rank and rank <= band), len(ranks))
            for band in bands
        }

    def get_stats(self) -> dict[str, float]:
        """
        Getting the computed lexical sophistication statistics of the text

        Returns:
            dict[str, float]: Dictionary of the computed statistics
        """
        return {stat: getattr(self, stat) for stat in LEXICAL_STATS_DESC}

    def print_stats(self) -> None:
        """Printing the computed lexical sophistication statistics with descriptions"""
        print(f"{'Statistic':^58}|{'Value':^10}")
        print("-" * 68)
        stats = self.get_stats()
        for stat, desc in LEXICAL_STATS_DESC.items():
            print(f"{desc:58}|{stats[stat]:^10.2f}")


def is_number(word: str) -> bool:
    """
    Checking whether a word is a number by NUMBER_PATTERN

    Arguments:
        word (str): Word

    Returns:
        bool: Result of the check
    """
    return NUMBER_PATTERN.fullmatch(word.lower()) is not None


def _mean(values: Sequence[float]) -> float:
    return fmean(values) if values else nan


@cache
def load_top_lemmas() -> dict[str, int]:
    """
    Loading the embedded list of the most frequent lemmas

    Description:
        The 10000 most frequent lemmas of the frequency dictionary of Google
        Books Ngram (FreqDict) by decreasing frequency, the parts of speech
        summed and the proper nouns left out; letters other than the Spanish
        words (a, e, o, u, y, á, é, ó) and lemmas of two letters or Roman
        numerals unknown to simplemma (pp, vs, xix) are left out too. The file
        resources/google_books_top10000.txt is derived from Google Books Ngram
        under CC BY 3.0

    Returns:
        dict[str, int]: Rank of every lemma, from 1
    """
    with TOP_LEMMAS_FILE.open(encoding="utf-8") as file:
        lemmas = [line.strip() for line in file if line.strip()]
    return {lemma: rank for rank, lemma in enumerate(lemmas, 1)}


def get_rank(lemma: str) -> int | None:
    """
    Getting the rank of a lemma by the embedded list of the most frequent lemmas

    Arguments:
        lemma (str): Lemma - the key of lemma_key

    Returns:
        int|None: Rank from 1 to 10000, None if the lemma is not in the list

    Example:
        >>> from ests.lexical_stats import get_rank
        >>> get_rank("el"), get_rank("gato"), get_rank("gatuno")
        (1, 2851, None)
    """
    return load_top_lemmas().get(lemma.lower())


def calc_surprisal(lemmas: Sequence[str], freq_dict: FreqDict) -> float:
    """
    Computing the mean surprisal of the words by the unigram model of the frequency dictionary

    Description:
        The mean over the words of −log2 P(w), where P(w) = ipm / 10⁶; a word
        out of the dictionary gets the minimum frequency of the dictionary
        (0.1 ipm), so the surprisal is defined for every word. The perplexity
        of the text is 2 to the power of the surprisal

    Arguments:
        lemmas (list[str]): Keys of the words (lemma_key)
        freq_dict (FreqDict): Frequency dictionary

    Returns:
        float: Mean surprisal in bits, nan for an empty list
    """
    floor = freq_dict.min_ipm
    return _mean([-log2(max(freq_dict.ipm(lemma), floor) / 1_000_000) for lemma in lemmas])
