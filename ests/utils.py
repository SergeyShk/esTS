import re
import unicodedata
from collections.abc import Iterator
from functools import lru_cache

import simplemma
import spacy
from spacy.tokenizer import Tokenizer

from .constants import ABBREVIATIONS, PUNCTUATIONS, SENTENCE_OPENERS

# End of a sentence: terminal marks, optionally closing quotes or brackets,
# before whitespace or the end of the text
SENTENCE_END = re.compile(r"(?P<marks>[.!?…]+)(?P<closers>[»”’\"')\]]*)(?=\s|$)")
PARAGRAPH_BREAK = re.compile(r"\n[ \t\r\f\v]*\n")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
OPENING_CHARS = "(«“\"'["


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


def _ends_sentence(paragraph: str, match: re.Match[str]) -> bool:
    """
    Checking whether the terminal marks found in a paragraph end a sentence

    Description:
        The next non-space character must open a sentence: an upper-case
        letter, a digit or one of SENTENCE_OPENERS; a lower-case continuation
        after an ellipsis or an exclamation mark keeps the sentence going.
        A single period after an abbreviation from ABBREVIATIONS or after
        a capital initial does not end a sentence either

    Arguments:
        paragraph (str): Paragraph of text
        match (Match): Match of SENTENCE_END in the paragraph

    Returns:
        bool: Result of the check
    """
    after = paragraph[match.end() :].lstrip()
    if not after:
        return True
    first = after[0]
    if not (first.isupper() or first.isdigit() or first in SENTENCE_OPENERS):
        return False
    if match.group("marks") != "." or match.group("closers"):
        return True
    tokens = paragraph[: match.end()].split()[-2:]
    last = tokens[-1].lstrip(OPENING_CHARS)
    return not (
        INITIAL.fullmatch(last)
        or last.lower() in ABBREVIATIONS
        or " ".join(tokens).lower() in ABBREVIATIONS
    )


def sentenize(text: str) -> Iterator[str]:
    """
    Splitting a text into sentences by rules

    Description:
        A sentence ends with a period, an exclamation or question mark or
        an ellipsis, possibly followed by closing quotes or brackets, when
        the next word starts with an upper-case letter, a digit, an inverted
        mark, an opening quote or bracket or a dash; a blank line ends
        a sentence too. Abbreviations (Sr., Dra., p. ej., EE. UU., a. m.)
        and capital initials do not end a sentence. A single line break
        does not split a sentence, so hard-wrapped texts are handled.
        The sentences are returned stripped of surrounding whitespace

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of sentences
    """
    for paragraph in PARAGRAPH_BREAK.split(text):
        start = 0
        for match in SENTENCE_END.finditer(paragraph):
            if not _ends_sentence(paragraph, match):
                continue
            yield paragraph[start : match.end()].strip()
            start = match.end()
        tail = paragraph[start:].strip()
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
