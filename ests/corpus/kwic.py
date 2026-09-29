from collections.abc import Sequence

import anyts.corpus
from anyts.corpus.kwic import (
    Concordance as Concordance,
    format_kwic as format_kwic,
    print_kwic as print_kwic,
)
from spacy.tokens import Doc, Token

from ..utils import iter_text_words, lemmatize


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
        the lemma of the model too; the keyword is lemmatized by simplemma.
        A phrase does not run across the end of a paragraph or of a sentence
        unless the keyword has one in the same place
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
        ParameterError: If the keyword has no words or the window is not an integer or is
            negative

    Example:
        >>> from ests.corpus import kwic
        >>> text = "El gato duerme. Los gatos juegan en el jardín."
        >>> [line.keyword for line in kwic(text, "gato", by_lemma=True)]
        ['gato', 'gatos']
    """
    return anyts.corpus.kwic(
        source,
        keyword,
        window,
        by_lemma,
        ignore_case,
        tokenize=iter_text_words,
        lemmatize=_lemmas,
    )


def _lemmas(word: str, tokens: Sequence[Token]) -> tuple[str, ...]:
    """The lemma of simplemma and, for a word of a Doc with lemmas, the lemma of the model"""
    lemma = tokens[0].lemma_ if tokens else ""
    return (lemmatize(word), lemma) if lemma else (lemmatize(word),)
