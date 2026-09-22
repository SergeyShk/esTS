import re
import unicodedata
from collections import Counter
from collections.abc import Iterable
from typing import Any

from spacy.tokens import Doc, Span

from .constants import (
    BASIC_STATS_DESC,
    COMPLEX_SYL_FACTOR,
    LONG_WORD_LETTER_FACTOR,
    PUNCTUATION_TYPES,
    PUNCTUATIONS,
    SPACES,
)
from .exceptions import SourceError, SourceTypeError
from .extractors import SentsExtractor, WordsExtractor
from .syllables import count_syllables
from .utils import count_letters, iter_doc_words

ELLIPSIS_PATTERN = re.compile(r"…|\.{3,}|(?<=[?!])\.{2}")
# A hyphen after whitespace or at the start of a line, or before a space, is
# a dash, the way the raya is typed in plain-text corpora (-Hola -dijo Juan);
# a hyphen before a digit is a sign, a hyphen at the end of a line inside
# a word (pala-\nbra) is a hyphen
DASH_PATTERN = re.compile(r"(?:(?<=\s)|^)-(?!\d)|-(?=[ \t]|\Z)", re.MULTILINE)
_DELETE_SPACES = str.maketrans("", "", "".join(SPACES))
PUNCTUATION_CHARS = {
    ",": "comma",
    ".": "period",
    "?": "question",
    "¿": "question",
    "!": "exclamation",
    "¡": "exclamation",
    ":": "colon",
    ";": "semicolon",
    "—": "dash",
    "–": "dash",
    "-": "hyphen",
    "«": "angle_quotes",
    "»": "angle_quotes",
    '"': "straight_quotes",
    "“": "straight_quotes",
    "”": "straight_quotes",
    "‘": "straight_quotes",
    "’": "straight_quotes",
    "(": "parentheses",
    ")": "parentheses",
}


class BasicStats:
    """
    Class for computing the basic statistics of a text

    Example:
        >>> from ests import BasicStats
        >>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
        >>> bs = BasicStats(text)
        >>> bs.get_stats()
        {'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
         'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
         'n_sents': 1,
         'n_words': 10,
         'n_unique_words': 8,
         'n_long_words': 5,
         'n_complex_words': 5,
         'n_simple_words': 5,
         'n_monosyllable_words': 4,
         'n_polysyllable_words': 6,
         'n_chars': 71,
         'n_letters': 60,
         'n_spaces': 9,
         'n_syllables': 23,
         'n_punctuations': 2,
         'c_punctuations': {'comma': 1,
                            'period': 0,
                            'question': 0,
                            'exclamation': 0,
                            'ellipsis': 0,
                            'colon': 1,
                            'semicolon': 0,
                            'dash': 0,
                            'hyphen': 0,
                            'angle_quotes': 0,
                            'straight_quotes': 0,
                            'parentheses': 0,
                            'other': 0}}

    Arguments:
        source (str|Doc): Data source (a string or a Doc object); for a Doc the
            words come from the tokens and the sentences from the annotation,
            without sentence boundaries they come from sents_extractor
        sents_extractor (SentsExtractor): Sentence extraction tool
        words_extractor (WordsExtractor): Word extraction tool
        normalize (bool): Compute the normalized statistics
        complex_syl_factor (int): Minimum number of syllables in a complex word
        long_word_letter_factor (int): Minimum number of letters in a long word

    Attributes:
        c_letters (dict[int, int]): Distribution of words by number of letters
        c_syllables (dict[int, int]): Distribution of words by number of syllables
        n_sents (int): Number of sentences
        n_words (int): Number of words
        n_unique_words (int): Number of unique words
        n_long_words (int): Number of long words
        n_complex_words (int): Number of complex words
        n_simple_words (int): Number of simple words
        n_monosyllable_words (int): Number of monosyllabic words
        n_polysyllable_words (int): Number of polysyllabic words
        n_chars (int): Number of characters
        n_letters (int): Number of letters
        n_spaces (int): Number of spaces
        n_syllables (int): Number of syllables
        n_punctuations (int): Number of punctuation marks
        c_punctuations (dict[str, int]): Distribution of punctuation marks by type
        p_unique_words (float): Normalized number of unique words
        p_long_words (float): Normalized number of long words
        p_complex_words (float): Normalized number of complex words
        p_simple_words (float): Normalized number of simple words
        p_monosyllable_words (float): Normalized number of monosyllabic words
        p_polysyllable_words (float): Normalized number of polysyllabic words
        p_letters (float): Normalized number of letters
        p_spaces (float): Normalized number of spaces
        p_punctuations (float): Normalized number of punctuation marks

    Methods:
        get_stats: Getting the computed statistics of the text
        print_stats: Printing the computed statistics of the text with descriptions
        count_words_by_syllables: Number of words with at least the given number of syllables
        count_words_by_letters: Number of words with at least the given number of letters

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object
        SourceError: If the source has no words
    """

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        words_extractor: WordsExtractor | None = None,
        normalize: bool = False,
        complex_syl_factor: int = COMPLEX_SYL_FACTOR,
        long_word_letter_factor: int = LONG_WORD_LETTER_FACTOR,
    ):
        sents: Iterable[Span] | Iterable[str]
        if isinstance(source, Doc):
            text = source.text
            if source.has_annotation("SENT_START"):
                sents = source.sents
            else:
                sents = (sents_extractor or SentsExtractor()).extract(text)
            words = tuple(word for _, _, word in iter_doc_words(source))
        elif isinstance(source, str):
            text = source
            if not sents_extractor:
                sents_extractor = SentsExtractor()
            sents = sents_extractor.extract(text)
            if not words_extractor:
                words_extractor = WordsExtractor()
            words = words_extractor.extract(text)
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not words:
            raise SourceError("The data source has no words")

        letters_per_word = tuple(count_letters(word) for word in words)
        syllables_per_word = tuple(count_syllables(word) for word in words)
        self.c_letters = dict(sorted(Counter(letters_per_word).items()))
        self.c_syllables = dict(sorted(Counter(syllables_per_word).items()))
        self.n_sents = sum(1 for sent in sents)
        self.n_words = len(words)
        self.n_unique_words = len({word.lower() for word in words})
        self.n_long_words = self.count_words_by_letters(long_word_letter_factor)
        self.n_complex_words = self.count_words_by_syllables(complex_syl_factor)
        self.n_simple_words = sum(
            count for spw, count in self.c_syllables.items() if complex_syl_factor > spw > 0
        )
        self.n_monosyllable_words = self.c_syllables.get(1, 0)
        self.n_polysyllable_words = (
            self.n_words - self.c_syllables.get(1, 0) - self.c_syllables.get(0, 0)
        )
        self.n_chars = len(text) - text.count("\n") - text.count("\r")
        self.n_letters = sum(map(str.isalpha, text))
        self.n_spaces = len(text) - len(text.translate(_DELETE_SPACES))
        self.n_syllables = sum(syllables_per_word)
        punctuations = count_punctuations(text)
        self.n_punctuations = sum(punctuations.values())
        self.c_punctuations = punctuations

        if normalize:
            self.p_unique_words = self.n_unique_words / self.n_words
            self.p_long_words = self.n_long_words / self.n_words
            self.p_complex_words = self.n_complex_words / self.n_words
            self.p_simple_words = self.n_simple_words / self.n_words
            self.p_monosyllable_words = self.n_monosyllable_words / self.n_words
            self.p_polysyllable_words = self.n_polysyllable_words / self.n_words
            self.p_letters = self.n_letters / self.n_chars
            self.p_spaces = self.n_spaces / self.n_chars
            self.p_punctuations = self.n_punctuations / self.n_chars

    def count_words_by_syllables(self, min_syllables: int) -> int:
        """
        Getting the number of words with at least the given number of syllables

        Arguments:
            min_syllables (int): Minimum number of syllables in a word

        Returns:
            int: Number of words
        """
        return sum(count for spw, count in self.c_syllables.items() if spw >= min_syllables)

    def count_words_by_letters(self, min_letters: int) -> int:
        """
        Getting the number of words with at least the given number of letters

        Arguments:
            min_letters (int): Minimum number of letters in a word

        Returns:
            int: Number of words
        """
        return sum(count for cpw, count in self.c_letters.items() if cpw >= min_letters)

    def get_stats(self) -> dict[str, Any]:
        """
        Getting the computed statistics of the text

        Returns:
            dict[str, Any]: Dictionary of the computed statistics - a copy,
                editing it does not change the object
        """
        return {
            key: dict(value) if isinstance(value, dict) else value
            for key, value in vars(self).items()
        }

    def print_stats(self):
        """Printing the computed statistics of the text with descriptions"""
        print(f"{'Statistic':^20}|{'Value':^10}")
        print("-" * 30)
        stats = self.get_stats()
        for stat, value in BASIC_STATS_DESC.items():
            print(f"{value:20}|{stats[stat]:^10}")


def count_punctuations(text: str) -> dict[str, int]:
    """
    Counting punctuation marks by type

    Description:
        The types of PUNCTUATION_TYPES: commas, periods, question and
        exclamation marks (the inverted ¿ and ¡ included, so "¿Qué?" has two
        question marks), ellipses (the character …, three or more periods,
        or two periods after ? and ! count as one mark whose periods are not
        periods: "¿Quién?.." is a question and an ellipsis), colons,
        semicolons, dashes (— and –, as well as a hyphen after whitespace
        or at the start of a line, or before a space, the way the raya is
        typed in plain-text corpora: "-Hola -dijo Juan", "- Se fueron -
        dijo"), hyphens inside words, before digits and at the end of
        a line inside a word (teórico-práctico, 1990-1995, -5, pala-\nbra),
        guillemets «», straight and curly quotes "“”‘’ of the three
        levels of the orthography, parentheses and the other marks: every
        remaining character of PUNCTUATIONS or of the Unicode categories P
        and S, the same set that is_punctuation removes from the words,
        so that no mark is lost between the words and the types

    Arguments:
        text (str): Text string

    Returns:
        dict[str, int]: Number of marks of each type in the order of PUNCTUATION_TYPES
    """
    counts = dict.fromkeys(PUNCTUATION_TYPES, 0)
    rest, counts["ellipsis"] = ELLIPSIS_PATTERN.subn("", text)
    rest, counts["dash"] = DASH_PATTERN.subn("", rest)
    chars = Counter(rest)
    for char, kind in PUNCTUATION_CHARS.items():
        counts[kind] += chars[char]
    counts["other"] = sum(
        count
        for char, count in chars.items()
        if char not in PUNCTUATION_CHARS
        and (char in PUNCTUATIONS or unicodedata.category(char)[0] in "PS")
    )
    return counts


def punctuation_profile(text: str, n_words: int | None = None) -> dict[str, float]:
    """
    Computing the punctuation profile - frequencies of marks by type per 1000 words

    Description:
        Frequencies of the types of PUNCTUATION_TYPES (count_punctuations)
        per 1000 words and the share of inverted marks among all question
        and exclamation marks (inverted_share): 0.5 when every question and
        exclamation opens with ¿ or ¡ as the orthography requires, lower
        when the writer drops them, as in informal texts and messages.
        The profile is an editorial and stylometric feature: it depends on
        the formatting of the text (typographic quotes and dashes, inverted
        marks) and is easy to fake, so it is best read separately from
        linguistic features

    Arguments:
        text (str): Text string
        n_words (int): Number of words; if not given, the words are extracted
            with WordsExtractor

    Returns:
        dict[str, float]: Frequencies of the types per 1000 words and
            inverted_share; nan without words or without question and
            exclamation marks
    """
    if n_words is None:
        n_words = len(WordsExtractor().extract(text))
    counts = count_punctuations(text)
    profile = {
        kind: count / n_words * 1000 if n_words else float("nan") for kind, count in counts.items()
    }
    n_marks = counts["question"] + counts["exclamation"]
    n_inverted = text.count("¿") + text.count("¡")
    profile["inverted_share"] = n_inverted / n_marks if n_marks else float("nan")
    return profile
