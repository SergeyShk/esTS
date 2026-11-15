from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any

import anyts.visualizers
from anyts.utils import is_doc, is_document
from matplotlib.axes import Axes

from ..extractors import SentsExtractor, WordsExtractor
from ..utils import get_document

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc


def sentence_lengths_plot(
    source: str | Doc | Document | Iterable[int],
    window: int = 10,
    inset: bool = True,
    ax: Axes | None = None,
    labels: Mapping[str, str] | None = None,
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> Axes:
    """
    Plotting the curve of the lengths of the sentences

    Description:
        The length of every sentence in words in the order of the text, the
        moving average over a window of sentences and an inset with the
        histogram of the lengths; the lengths come from sentence_lengths

    Arguments:
        source (str|Doc|Document|Iterable[int]): Text, Doc object, Document or lengths of the
            sentences (a list, a numpy array, a Series)
        window (int): Window of the moving average in sentences
        inset (bool): Show the inset with the histogram
        ax (Axes): Axes for the plot; if not given, a new figure is created
        labels (dict[str, str]): Labels over VISUALIZER_LABELS["sentence_lengths_plot"]
            of anyts.constants
        sents_extractor (SentsExtractor): Extractor of the sentences of a string
        words_extractor (WordsExtractor): Extractor of the words of a sentence of a string

    Returns:
        Axes: Axes with the plot

    Raises:
        SourceTypeError: If the data source or an extractor is set incorrectly
        ParameterError: If the window is not an integer or is below one, or the
            labels are set incorrectly or ax is not a matplotlib Axes (check_axes)
        SourceError: If there are no sentences or a length is negative
    """
    source, sents_extractor, words_extractor = _lengths_args(
        source, sents_extractor, words_extractor
    )
    return anyts.visualizers.sentence_lengths_plot(
        source, window, inset, ax, labels, sents_extractor, words_extractor
    )


def sentence_lengths(
    source: str | Doc | Document | Iterable[int],
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> list[int]:
    """
    Extracting the lengths of the sentences in words

    Description:
        A string, a Doc or a Document gives the sentences of its document
        (get_document) and their words with a letter or a digit; with an
        extractor, the text is split by sents_extractor and words_extractor, the
        Spanish SentsExtractor and WordsExtractor for the one not given. Ready
        lengths (a sequence or an iterator of integers that are not negative)
        are used as they are. Sentences without words are skipped

    Arguments:
        source (str|Doc|Document|Iterable[int]): Text, Doc object, Document or ready lengths
        sents_extractor (SentsExtractor): Extractor of the sentences of a string
        words_extractor (WordsExtractor): Extractor of the words of a sentence of a string

    Returns:
        list[int]: Lengths of the sentences in order

    Raises:
        SourceTypeError: If the data source or an extractor is set incorrectly
        SourceError: If a length is negative

    Example:
        >>> from ests.visualizers import sentence_lengths
        >>> sentence_lengths("El gato duerme. ¿Y el perro? —Come —dijo ella.")
        [3, 3, 3]
    """
    return anyts.visualizers.sentence_lengths(
        *_lengths_args(source, sents_extractor, words_extractor)
    )


def _lengths_args(
    source: Any,
    sents_extractor: SentsExtractor | None,
    words_extractor: WordsExtractor | None,
) -> tuple[Any, SentsExtractor | None, WordsExtractor | None]:
    """The document of a text, a Doc or a Document of get_document when no extractor is given;
    with one given the text is split by the extractors, the Spanish one for the missing one"""
    if sents_extractor is None and words_extractor is None:
        if isinstance(source, str) or is_doc(source) or is_document(source):
            return get_document(source), None, None
        return source, None, None
    return (
        source,
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
    )
