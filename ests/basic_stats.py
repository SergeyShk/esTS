import anyts.basic_stats
from anyts.basic_stats import count_punctuations as count_punctuations
from anyts.utils import check_integer

from .exceptions import ParameterError
from .extractors import SentsExtractor, WordsExtractor
from .syllables import count_syllables


class BasicStats(anyts.basic_stats.BasicStats):
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
            without sentence boundaries they come from SentsExtractor
        sents_extractor (SentsExtractor): Sentence extraction tool; if given,
            used on the text of a Doc too
        words_extractor (WordsExtractor): Word extraction tool; if given,
            used on the text of a Doc too
        normalize (bool): Compute the normalized statistics
        complex_syl_factor (int): Minimum number of syllables in a complex word
        long_word_letter_factor (int): Minimum number of letters in a long word

    Attributes:
        c_letters (dict[int, int]): Distribution of words by number of letters
        c_syllables (dict[int, int]): Distribution of words by number of syllables
        n_sents (int): Number of sentences containing words
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
        count_syllables: Counting the syllables of a word by the rules of Spanish
        count_punctuations: Counting the punctuation marks of a text by type
        count_words_by_syllables: Number of words with at least the given number of syllables
        count_words_by_letters: Number of words with at least the given number of letters
        get_stats: Getting the computed statistics of the text
        print_stats: Printing the computed statistics of the text with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object, or an extractor
            is of another type
        SourceError: If the source has no words
        ParameterError: If a factor is not an integer or is below one
    """

    sents_extractor_class = SentsExtractor
    words_extractor_class = WordsExtractor

    def count_syllables(self, word: str) -> int:
        """
        Counting the syllables of a word by the rules of Spanish

        Arguments:
            word (str): Word

        Returns:
            int: Number of syllables
        """
        return count_syllables(word)


def punctuation_profile(text: str, n_words: int | None = None) -> dict[str, float]:
    """
    Computing the punctuation profile - frequencies of marks by type per 1000 words

    Description:
        Frequencies of the types of count_punctuations per 1000 words and
        inverted_share, the share of ¿ and ¡ among all question and
        exclamation marks: 0.5 when every question and exclamation opens with
        one, lower when the writer drops them

    Arguments:
        text (str): Text string
        n_words (int): Number of words; if not given, the words are extracted
            with WordsExtractor

    Returns:
        dict[str, float]: Frequencies of the types per 1000 words and
            inverted_share; nan without words or without question and
            exclamation marks

    Raises:
        SourceTypeError: If the text is not a string
        ParameterError: If the number of words is not an integer or is negative
    """
    if n_words is not None:
        check_integer(n_words, "number of words")
        if n_words < 0:
            raise ParameterError("The number of words cannot be negative")
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
