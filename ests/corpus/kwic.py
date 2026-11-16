from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import anyts.corpus
from anyts.corpus.kwic import (
    Concordance as Concordance,
    format_kwic as format_kwic,
    print_kwic as print_kwic,
)

from ..utils import _annotate_text, get_morph_analyzer, iter_text_sents, iter_text_words, lemmatize

if TYPE_CHECKING:
    from anyseg import Document, Word
    from spacy.tokens import Doc


def kwic(
    source: str | Doc | Document,
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
        is found by gato). The text and the keyword are tokenized the same way;
        punctuation and symbols are not words, and a word is compared without
        the period of an abbreviation, which the end of a sentence splits off
        (Sr. and Sr in "Vino el Sr." are one word). By lemma, a word matches
        by the lemma of lemmatize with its part of speech - of esMorph in the
        context of its sentence for a string, of the pipeline for a Doc -, a word
        of a Doc or a Document without the parts of speech by its first
        analysis, and a word of the keyword, which has no context, by the
        lemmas of all its analyses (vino finds vino and venir).
        A phrase does not run across the end of a paragraph or of a sentence -
        a sentence of the document of the text (get_document) - unless the
        keyword has one in the same place.
        The context is window words on each side as written, with the
        punctuation between them; whitespace collapses to one space;
        occurrences do not overlap. Accents are part of the word form: solo and
        sólo are two forms

    Arguments:
        source (str|Doc|Document): Text, Doc object or Document
        keyword (str): Word or phrase
        window (int): Number of words of context on each side
        by_lemma (bool): Compare lemmas instead of word forms
        ignore_case (bool): Ignore case when comparing word forms

    Returns:
        list[Concordance]: Occurrences in the order of the text

    Raises:
        SourceTypeError: If the source is neither a string, a Doc nor a Document or the keyword
            is not a string
        ParameterError: If the keyword has no words, the window is not an integer or is
            negative, or by_lemma or ignore_case is not a bool

    Example:
        >>> from ests.corpus import kwic
        >>> text = "El gato duerme. Los gatos juegan en el jardín."
        >>> [line.keyword for line in kwic(text, "gato", by_lemma=True)]
        ['gato', 'gatos']
    """
    if by_lemma is True and isinstance(source, str):
        source = _annotate_text(source)
    return anyts.corpus.kwic(
        source,
        keyword,
        window,
        by_lemma,
        ignore_case,
        tokenize=iter_text_words,
        lemmatize=_lemmas,
        sentenize=iter_text_sents,
    )


def _lemmas(word: str, words: Sequence[Word]) -> str | tuple[str, ...]:
    """
    Lemmas of a word without the period of an abbreviation, which the end of a sentence
    splits off, so that Sr. has the lemmas of Sr anywhere: lemmatize with the part of speech
    of its first word (Dime is a verb), and the lemmas of all the analyses for a word of the
    keyword
    """
    form = word.removesuffix(".")
    if not words:
        analyses = get_morph_analyzer().analyze(form)
        return tuple(dict.fromkeys(analysis.lemma for analysis in analyses)) or (form,)
    return lemmatize(form, words[0].upos or "")
