from collections.abc import Sequence
from typing import NamedTuple

from anyts.utils import check_integer, iter_doc_tokens
from spacy.tokens import Doc

from ..exceptions import ParameterError, SourceTypeError
from ..utils import get_tokenizer, lemmatize


class Concordance(NamedTuple):
    """
    Line of a concordance - an occurrence of the keyword with its context

    Attributes:
        start (int): Position of the first character of the occurrence in the text
        end (int): Position after the last character of the occurrence
        left (str): Context on the left
        keyword (str): Occurrence as written in the text
        right (str): Context on the right
    """

    start: int
    end: int
    left: str
    keyword: str
    right: str


def kwic(
    source: str | Doc,
    keyword: str,
    window: int = 5,
    by_lemma: bool = False,
    ignore_case: bool = True,
) -> list[Concordance]:
    """
    Building a KWIC concordance (keyword in context)

    Description:
        The occurrences of a word or a phrase are looked for among the words of
        the text by the word form, ignoring case or not, or by the lemma (gatos
        is found by gato). The text and the keyword are tokenized the same way
        (EE. UU. is one word); punctuation and symbols are not words. By lemma,
        a word matches by its lemma of simplemma and, in a Doc with lemmas, by
        the lemma of the model too; the keyword is lemmatized by simplemma
        The context is window words on each side as written, with the
        punctuation between them; whitespace collapses to one space;
        occurrences do not overlap. Accents are part of the word form: solo and
        sólo are two forms

    Arguments:
        source (str|Doc): Text or Doc object
        keyword (str): Word or phrase
        window (int): Number of words of context on each side
        by_lemma (bool): Compare lemmas instead of word forms
        ignore_case (bool): Ignore case when comparing word forms

    Returns:
        list[Concordance]: Occurrences in the order of the text

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object or the keyword
            is not a string
        ParameterError: If the keyword is empty or the window is not an integer or is negative

    Example:
        >>> from ests.corpus import kwic
        >>> text = "El gato duerme. Los gatos juegan en el jardín."
        >>> [line.keyword for line in kwic(text, "gato", by_lemma=True)]
        ['gato', 'gatos']
    """
    if not isinstance(keyword, str):
        raise SourceTypeError(f"The keyword must be a string, not {type(keyword).__name__}")
    pattern = [token.text for token in iter_doc_tokens(get_tokenizer()(keyword))]
    if not pattern:
        raise ParameterError("The keyword is not set")
    check_integer(window, "window")
    if window < 0:
        raise ParameterError("The window cannot be negative")
    if isinstance(source, Doc):
        text = source.text
        tokens = list(iter_doc_tokens(source))
        lemmatized = source.has_annotation("LEMMA")
    elif isinstance(source, str):
        text = source
        tokens = list(iter_doc_tokens(get_tokenizer()(source)))
        lemmatized = False
    else:
        raise SourceTypeError("The data source is set incorrectly")
    words = [(token.idx, token.idx + len(token), token.text) for token in tokens]
    readings = [
        _readings(token.text, by_lemma, ignore_case, token.lemma_ if lemmatized else "")
        for token in tokens
    ]
    target = [_readings(word, by_lemma, ignore_case) for word in pattern]
    found = []
    index = 0
    while index <= len(words) - len(target):
        candidates = readings[index : index + len(target)]
        if not all(wanted & met for wanted, met in zip(target, candidates, strict=True)):
            index += 1
            continue
        last = index + len(target) - 1
        start = words[index][0]
        end = words[last][1]
        left = text[words[max(index - window, 0)][0] : start] if window else ""
        right = text[end : words[min(last + window, len(words) - 1)][1]] if window else ""
        found.append(
            Concordance(
                start,
                end,
                " ".join(left.split()),
                " ".join(text[start:end].split()),
                " ".join(right.split()),
            )
        )
        index = last + 1
    return found


def _readings(word: str, by_lemma: bool, ignore_case: bool, lemma: str = "") -> set[str]:
    """Readings a word is matched by: its form, or its lemmas of simplemma and of the model"""
    if not by_lemma:
        return {word.lower() if ignore_case else word}
    return {lemmatize(word).lower(), *([lemma.lower()] if lemma else [])}


def format_kwic(concordances: Sequence[Concordance], width: int = 40) -> str:
    """
    Formatting a concordance aligned on the keyword

    Description:
        The left context is cut from the left and aligned to the right, the
        right one is cut from the right; lines are separated by line breaks

    Arguments:
        concordances (list[Concordance]): Lines of the concordance
        width (int): Width of a context in characters

    Returns:
        str: Concordance as text

    Raises:
        ParameterError: If the width of a context is not an integer or is below one

    Example:
        >>> from ests.corpus import format_kwic, kwic
        >>> print(format_kwic(kwic("El gato duerme y el gato come.", "gato", window=1), width=6))
            El  gato  duerme
            el  gato  come
    """
    check_integer(width, "width of a context")
    if width < 1:
        raise ParameterError("The width of a context must be greater than 0")
    keyword_width = max((len(line.keyword) for line in concordances), default=0)
    return "\n".join(
        f"{line.left[-width:]:>{width}}  {line.keyword:<{keyword_width}}  {line.right[:width]}"
        for line in concordances
    )


def print_kwic(concordances: Sequence[Concordance], width: int = 40) -> None:
    """
    Printing a concordance aligned on the keyword

    Arguments:
        concordances (list[Concordance]): Lines of the concordance
        width (int): Width of a context in characters
    """
    print(format_kwic(concordances, width))
