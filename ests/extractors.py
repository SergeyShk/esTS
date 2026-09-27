import re
from collections.abc import Iterable
from typing import ClassVar

import anyts
from anyts.extractors import Extractor as Extractor, Tokenizer as Tokenizer

from .utils import lemmatize, sentenize, tokenize

NUMBER_PATTERN = re.compile(
    r"[+\-−]?\d+(?:[.,:/-]\d+)*"
    r"(?:\.?(?:[ºª°]|[ᵃᵉᵒʳˢ]+|(?:er|d[oa]|r[oa]|t[oa]|v[oa]|n[oa]|m[oa])s?))?%?"
)


class SentsExtractor(anyts.SentsExtractor):
    """
    Class for extracting sentences from a text

    Example:
        >>> import re
        >>> from ests import SentsExtractor
        >>> text = "No tengas 100 euros, ten 100 amigos"
        >>> se = SentsExtractor(tokenizer=re.compile(r', '))
        >>> se.extract(text)
        ('No tengas 100 euros', 'ten 100 amigos')

    Description:
        The default tokenizer is the rule-based splitter ests.utils.sentenize

    Arguments:
        tokenizer (pattern|callable): Tokenizer or regular expression
        min_len (int): Minimum length of an extracted sentence
        max_len (int): Maximum length of an extracted sentence

    Methods:
        extract: Extracting sentences from a text

    Raises:
        ParameterError: If a length bound is not an integer, is negative or the minimum
            is greater than the maximum
    """

    def sentenize(self, text: str) -> Iterable[str]:
        """Splitting a text into sentences with ests.utils.sentenize"""
        return sentenize(text)


class WordsExtractor(anyts.WordsExtractor):
    """
    Class for extracting words from a text

    Example:
        >>> from ests import WordsExtractor
        >>> text = "No tengas 100 euros, ten 100 amigos"
        >>> we = WordsExtractor(use_lexemes=True, stopwords=["no"],
        ...                     filter_nums=True, ngram_range=(1, 2))
        >>> we.extract(text)
        ('tener', 'euro', 'tener', 'amigo', 'tener_euro', 'euro_tener', 'tener_amigo')

    Description:
        The default tokenizer is ests.utils.tokenize, the lemmas come from
        ests.utils.lemmatize. The filters are applied in order: punctuation,
        numbers, lemmatization, lower case, stop words, word length. Numbers
        include signed numbers, ranges, fractions, dates, times, percentages
        and ordinals: -5, 1990-1995, 1.500,50, 12/03/2020, 3:30, 10%, 3.º, 2do

    Arguments:
        tokenizer (pattern|callable): Tokenizer or regular expression
        filter_punct (bool): Filter punctuation marks
        filter_nums (bool): Filter numbers
        use_lexemes (bool): Use word lemmas
        stopwords (collection[str]): Stop words, compared case-insensitively
        lowercase (bool): Convert words to lower case
        ngram_range (tuple[int, int]): Lower and upper bound of the N-gram size
        min_len (int): Minimum length of an extracted word
        max_len (int): Maximum length of an extracted word

    Methods:
        extract: Extracting words from a text
        get_most_common: Getting a counter of the top words

    Raises:
        ParameterError: If the N-gram range is not a pair of integers, its lower bound
            is less than one or greater than the upper
        ParameterError: If a length bound is not an integer, is negative or the minimum
            is greater than the maximum
        SourceTypeError: If the stop words are not a list of strings
    """

    number_pattern: ClassVar[re.Pattern[str]] = NUMBER_PATTERN

    def tokenize(self, text: str) -> Iterable[str]:
        """Splitting a text into tokens with ests.utils.tokenize"""
        return tokenize(text)

    def lemmatize(self, word: str) -> str:
        """Lemma of a word by ests.utils.lemmatize"""
        return lemmatize(word)


class CharNgramsExtractor(anyts.CharNgramsExtractor):
    """
    Class for extracting character N-grams from a text

    Example:
        >>> from ests import CharNgramsExtractor
        >>> text = "El gato dormía  en la ventana, y el perro - en el suelo."
        >>> ce = CharNgramsExtractor(n=3, lowercase=True)
        >>> ce.extract(text)[:6]
        ('el ', 'l g', ' ga', 'gat', 'ato', 'to ')
        >>> ce.get_most_common(2)
        [('el ', 3), (' en', 2)]
        >>> CharNgramsExtractor(n=4, lowercase=True, within_words=True).extract(text)
        ('gato', 'dorm', 'ormí', 'rmía', 'vent', 'enta', 'ntan', 'tana', 'perr', 'erro', 'suel', 'uelo')

    Description:
        A sliding window over the text with whitespace runs collapsed into one
        space and punctuation kept (Stamatatos 2009); with within_words, over
        each word of the tokenizer, ests.utils.tokenize by default, punctuation
        dropped, so words shorter than N yield no N-grams

    Arguments:
        n (int): N-gram length in characters
        lowercase (bool): Convert the text to lower case
        within_words (bool): Take N-grams only inside words
        tokenizer (pattern|callable): Word tokenizer for within_words
            or a regular expression

    Methods:
        extract: Extracting N-grams from a text
        get_most_common: Getting a counter of the top N-grams

    Raises:
        ParameterError: If the N-gram length is not an integer or is less than one
    """

    def tokenize(self, text: str) -> Iterable[str]:
        """Splitting a text into tokens with ests.utils.tokenize"""
        return tokenize(text)
