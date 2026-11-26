from __future__ import annotations

from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING

import anyts
import anyts.lexical_stats
from anyts.constants import FREQUENCY_BANDS as FREQUENCY_BANDS
from anyts.document import get_tree
from anyts.lexical_stats import LexicalWord
from anyts.utils import has_words, is_number

from .cohesion_stats import _token_info
from .constants import LEXICAL_STATS_DESC
from .datasets.freq_dict import FreqDict, lemma_key
from .exceptions import SourceError, SourceTypeError
from .extractors import NUMBER_PATTERN
from .utils import _annotate_text, get_document

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc

TOP_LEMMAS_FILE = Path(__file__).parent / "resources" / "google_books_top10000.txt"


def _without_period(word: str) -> str:
    """
    A word without the period of an abbreviation (Sr., pág.), the form the dictionary has;
    an initial (D., J.) keeps it, since its letter is another word
    """
    return word[:-1] if len(word) > 2 and word.endswith(".") else word


class LexicalStats(anyts.lexical_stats.LexicalStats):
    """
    Class for computing the lexical sophistication statistics of a text

    Description:
        Extends the LexicalStats of the anyTS core with the Spanish layer: the
        frequency dictionary of Google Books Ngram (FreqDict) with its embedded
        list of the 10000 most frequent lemmas, the lemmas of lemma_key by the
        part of speech of every word and the content words, as in
        CohesionStats. The source needs the parts of speech: a string gets
        those of esMorph in the context of its sentences, a Doc must carry them. Numbers (2020, 5,5,
        3.º) are no words. The statistics by the dictionary need a downloaded
        FreqDict, the bands and the lexical density do not

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
        (0.727, 2.173, 8.104)
        >>> ls.band_coverage(unique=True)
        {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}

    Arguments:
        source (str|Doc|Document): Data source (a string, a Doc or a Document)
        freq_dict (FreqDict): Frequency dictionary; FreqDict() of the default
            directory if not given

    Attributes:
        freq_dict (FreqDict): Frequency dictionary
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
        describe: Reading of a statistic by its scale, None for every statistic
        get_stats: Getting the computed lexical sophistication statistics
        to_dataframe: Getting the statistics as a table of one row
        by_parts: Getting the statistics of every sentence, line or paragraph
        print_stats: Printing the computed statistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string, a Doc nor a Document, or the
            dictionary is of another type
        SourceError: If the source has no words or lacks the parts of speech
        DatasetNotFoundError: When a statistic by the dictionary is read and the
            dictionary is not downloaded
    """

    freq_dict: FreqDict
    freq_dict_class = FreqDict
    stats_desc = LEXICAL_STATS_DESC

    def __init__(self, source: str | Doc | Document, freq_dict: FreqDict | None = None):
        super().__init__(source, freq_dict)
        # analyze can be called again on the object; the keys read the words of the source
        self._proper = self._found_proper

    def parse(self, source: str | Doc | Document) -> Document:
        """
        Getting the document of a source

        Description:
            A string is segmented by anySeg and analyzed by esMorph in the
            context of its sentences; a Doc or a Document goes to get_document

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            Document: Document of anySeg

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
        """
        if isinstance(source, str):
            return _annotate_text(source)
        return get_document(source)

    def analyze(self, source: str | Doc | Document) -> list[LexicalWord]:
        """
        Getting the words of a source with their lemmas and their kind

        Description:
            The words of the tree of the document of parse with a letter or a
            digit, without the numbers of NUMBER_PATTERN; the lemma of lemma_key by the
            part of speech of the word, a proper noun in lower case, and the content
            words of token_info

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            list[LexicalWord]: Word, lemma and whether it is a content word

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
            SourceError: If the words lack the parts of speech
        """
        words = [
            word
            for word in get_tree(self._document(source)).words
            if has_words(word.form) and not is_number(word.form, NUMBER_PATTERN)
        ]
        if words and not any(word.upos for word in words):
            raise SourceError(self.messages["no_pos"])
        self._found_proper = tuple(word.upos == "PROPN" for word in words)
        return [
            LexicalWord(
                word.form,
                lemma_key(_without_period(word.form), proper, word.upos or ""),
                _token_info(word).content,
            )
            for word, proper in zip(words, self._found_proper, strict=True)
        ]

    def dictionary_keys(self) -> tuple[str, ...]:
        """
        Getting the keys of the words in the frequency dictionary

        Description:
            A proper noun is looked up by its form when the dictionary has it
            (París - parís) and by its lemma otherwise (Estados - estado, a verb
            tagged PROPN as Miró - mirar)

        Returns:
            tuple[str]: Key of every word
        """
        return tuple(
            lemma_key(_without_period(word)) if proper and lemma not in self.freq_dict else lemma
            for word, lemma, proper in zip(self.words, self.lemmas, self._proper, strict=True)
        )

    def rank(self, lemma: str) -> int | None:
        """Rank of a lemma by the embedded list of FreqDict (get_rank)"""
        return get_rank(lemma)

    def top_size(self) -> int:
        """Size of the embedded list, 10000"""
        return len(load_top_lemmas())


@cache
def load_top_lemmas() -> dict[str, int]:
    """
    Loading the embedded list of the most frequent lemmas

    Description:
        The 10000 most frequent lemmas of FreqDict by decreasing frequency, the
        parts of speech summed, without the proper nouns and the lemmas where
        they outweigh the others (garcía), the letters that are no words, and
        the lemmas of two letters or Roman numerals unknown to esMorph or
        without a vowel (pp, km, xix). The file resources/google_books_top10000.txt
        is derived from Google Books Ngram under CC BY 3.0

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
        (1, 3122, None)
    """
    return load_top_lemmas().get(lemma.lower())


def calc_surprisal(lemmas: Sequence[str], freq_dict: FreqDict) -> float:
    """
    Computing the mean surprisal of the words by the unigram model of the frequency dictionary

    Description:
        The mean over the words of −log2 P(w), where P(w) = ipm / 10⁶; a word
        out of the dictionary gets its minimum frequency (0.1 ipm). The
        perplexity is 2 to the power of the surprisal. The calc_surprisal of the
        core for FreqDict

    Arguments:
        lemmas (list[str]): Keys of the words (lemma_key)
        freq_dict (FreqDict): Frequency dictionary

    Returns:
        float: Mean surprisal in bits, nan for an empty list

    Raises:
        SourceTypeError: If the lemmas are not a list of strings or the dictionary is not
            a FreqDict
    """
    if not isinstance(freq_dict, FreqDict):
        raise SourceTypeError("The frequency dictionary must be a FreqDict")
    return anyts.lexical_stats.calc_surprisal(lemmas, freq_dict)
