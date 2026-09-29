from collections.abc import Iterable, Mapping

import anyts.visualizers
from matplotlib.axes import Axes
from spacy.tokens import Doc

from ..extractors import SentsExtractor, WordsExtractor


def sentence_lengths_plot(
    source: str | Doc | Iterable[int],
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
        source (str|Doc|Iterable[int]): Text, Doc object or lengths of the
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
            labels are set incorrectly
        SourceError: If there are no sentences or a length is negative
    """
    return anyts.visualizers.sentence_lengths_plot(
        source,
        window,
        inset,
        ax,
        labels,
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
    )


def sentence_lengths(
    source: str | Doc | Iterable[int],
    sents_extractor: SentsExtractor | None = None,
    words_extractor: WordsExtractor | None = None,
) -> list[int]:
    """
    Extracting the lengths of the sentences in words

    Description:
        A string is split into sentences by sents_extractor and every sentence
        into words by words_extractor, the Spanish SentsExtractor and
        WordsExtractor by default; a Doc by its sentence boundaries, or as its
        text without them; ready lengths (a sequence or an iterator of integers
        that are not negative) are used as they are. Sentences without words
        are skipped

    Arguments:
        source (str|Doc|Iterable[int]): Text, Doc object or ready lengths
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
        source,
        SentsExtractor() if sents_extractor is None else sents_extractor,
        WordsExtractor() if words_extractor is None else words_extractor,
    )
