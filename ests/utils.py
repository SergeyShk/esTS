import re
import unicodedata
from collections.abc import Iterator
from functools import lru_cache

import simplemma
import spacy
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc, Span

from .constants import ABBREVIATIONS, PUNCTUATIONS, SENTENCE_OPENERS

# End of a sentence: terminal marks, optionally closing quotes or brackets,
# before whitespace or the end of the text; or a blank line
SENTENCE_END = re.compile(
    r"(?P<marks>[.!?…]+)(?P<closers>[»”’\"')\]]*)(?=\s|$)|(?P<break>\n[ \t\r\f\v]*\n)"
)
NON_SPACE = re.compile(r"\S")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
# Marker of a numbered or lettered list (1. 2.1. b. IV.) that opens a sentence
# or a line, at the end of the examined window
LIST_MARKER = re.compile(r"(?:^|\n)[ \t]*(?:\d+(?:\.\d+)*|[a-z]|[IVXLC]+)\.\Z")
OPENING_CHARS = "(«“\"'["
# Characters looked back from a period for an abbreviation: enough for the two
# tokens that are checked, so that the scan stays linear in the text length.
# A token cut by the window is at least 61 characters long and matches
# neither an abbreviation nor an initial
LOOKBACK = 64


def is_punctuation(token: str) -> bool:
    """
    Checking whether a token consists only of punctuation marks and symbols

    Description:
        Marks are the characters of PUNCTUATIONS and the Unicode characters
        of the categories P (punctuation) and S (symbols), so multi-character
        tokens like "?!", "!..", "--", "…", "«", "€" are filtered as well

    Arguments:
        token (str): Token

    Returns:
        bool: Result of the check
    """
    return all(char in PUNCTUATIONS or unicodedata.category(char)[0] in "PS" for char in token)


def _ends_sentence(text: str, start: int, match: re.Match[str]) -> bool:
    """
    Checking whether the terminal marks found in a text end a sentence

    Description:
        The next non-space character must open a sentence: an upper-case
        letter, a digit or one of SENTENCE_OPENERS; a lower-case continuation
        after an ellipsis or an exclamation mark keeps the sentence going.
        A single period does not end a sentence after an abbreviation from
        ABBREVIATIONS, after a capital initial or after a list marker that
        opens the sentence or a line. Opening quotes and brackets are
        stripped from the tokens before the check, so "(EE. UU. Es grande)"
        stays together. Only the last LOOKBACK characters before the period
        are examined

    Arguments:
        text (str): Text string
        start (int): Position where the current sentence starts
        match (Match): Match of SENTENCE_END in the text

    Returns:
        bool: Result of the check
    """
    following = NON_SPACE.search(text, match.end())
    if following is None:
        return True
    first = following.group()
    if not (first.isupper() or first.isdigit() or first in SENTENCE_OPENERS):
        return False
    if match.group("marks") != "." or match.group("closers"):
        return True
    window_start = max(start, match.end() - LOOKBACK)
    window = text[window_start : match.end()]
    if LIST_MARKER.search(window):
        return False
    tokens = [stripped for token in window.split() if (stripped := token.lstrip(OPENING_CHARS))]
    last = tokens[-1]
    return not (
        INITIAL.fullmatch(last)
        or last.lower() in ABBREVIATIONS
        or " ".join(tokens[-2:]).lower() in ABBREVIATIONS
    )


def sentenize(text: str) -> Iterator[str]:
    """
    Splitting a text into sentences by rules

    Description:
        A sentence ends with a period, an exclamation or question mark or
        an ellipsis, possibly followed by closing quotes or brackets, when
        the next word starts with an upper-case letter, a digit, an inverted
        mark, an opening quote or bracket or a dash; a blank line ends
        a sentence too. Abbreviations (Sr., Dra., p. ej., EE. UU., a. m.),
        capital initials and list markers at the start of a sentence or
        a line (1. 2.1. IV.) do not end a sentence. A single line break
        does not split a sentence, so hard-wrapped texts are handled.
        The text is scanned once, the sentences are yielded as they are
        found, stripped of surrounding whitespace

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of sentences
    """
    start = 0
    for match in SENTENCE_END.finditer(text):
        if match.group("break") is None and not _ends_sentence(text, start, match):
            continue
        sent = text[start : match.end()].strip()
        if sent:
            yield sent
        start = match.end()
    tail = text[start:].strip()
    if tail:
        yield tail


@lru_cache(maxsize=1)
def get_tokenizer() -> Tokenizer:
    """
    Getting the rule-based tokenizer of the spaCy Spanish language class

    Description:
        The tokenizer of a blank "es" pipeline does not need a trained
        model; it is created once per process

    Returns:
        Tokenizer: spaCy tokenizer
    """
    return spacy.blank("es").tokenizer


def tokenize(text: str) -> Iterator[str]:
    """
    Splitting a text into tokens with the spaCy Spanish tokenizer

    Description:
        Whitespace tokens are dropped; punctuation marks, including "¿"
        and "¡", numbers like "1.500,50", "3.º", "1990-1995" and
        abbreviations like "Sr.", "EE. UU." are single tokens; words
        with enclitic pronouns (dámelo) are not split

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of tokens
    """
    return (token.text for token in get_tokenizer()(text) if not token.is_space)


@lru_cache(maxsize=131072)
def lemmatize(word: str) -> str:
    """
    Lemmatizing a word form with simplemma, with caching

    Description:
        simplemma works from a dictionary without a trained model: a known
        form is mapped to its lower-case lemma (Tienes - tener, NIÑOS -
        niño), an unknown form is returned unchanged (Madrid, dámelo).
        Verbs with enclitic pronouns are handled when the form is in the
        dictionary (cantándole - cantar). The results are cached by form:
        a text has far fewer distinct forms than tokens

    Arguments:
        word (str): Word form

    Returns:
        str: Lemma
    """
    return simplemma.lemmatize(word, lang="es")


def iter_doc_words(source: Doc | Span) -> Iterator[tuple[int, int, str]]:
    """
    Extracting words with positions from a Doc or Span object

    Description:
        Whitespace tokens are skipped, punctuation marks and symbols are
        dropped by the same is_punctuation check as for a string (%, €, §
        and other symbols of the category S are not words, although spaCy
        does not treat them as punctuation). The Spanish tokenizer keeps
        hyphenated words (teórico-práctico) and abbreviations (EE. UU.)
        as single tokens, so a word is always one token

    Arguments:
        source (Doc|Span): Doc or Span object

    Returns:
        generator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each word
    """
    for token in source:
        if not token.is_space and not is_punctuation(token.text):
            yield token.idx, token.idx + len(token), token.text


def count_letters(word: str) -> int:
    """
    Counting the letters of a string

    Description:
        Letters of any alphabet (str.isalpha), without digits, hyphens
        and marks; the ordinal indicators º and ª are letters for
        str.isalpha, so 3.º is a one-letter word

    Arguments:
        word (str): Word form

    Returns:
        int: Number of letters
    """
    return sum(map(str.isalpha, word))


def safe_divide(num: float | int, den: float | int, default: float | int = 0) -> float:
    """
    Dividing two numbers safely

    Arguments:
        num (float|int): Numerator
        den (float|int): Denominator
        default (float|int): Value returned for a zero denominator

    Returns:
        float: Result of the division
    """
    if not den:
        return default
    return num / den
