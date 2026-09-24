from collections.abc import Iterable
from numbers import Integral

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from spacy.tokens import Doc

from ..exceptions import ParameterError, SourceError, SourceTypeError
from ..utils import count_words_by_spans, iter_doc_words, iter_text_sents, iter_text_words


def sentence_lengths_plot(
    source: str | Doc | Iterable[int],
    window: int = 10,
    inset: bool = True,
    ax: Axes | None = None,
) -> Axes:
    """
    Plotting the curve of the lengths of the sentences

    Description:
        The length of every sentence in words in the order of the text, the
        moving average over a window of sentences and an inset with the
        histogram of the lengths - the rhythm of the text; the lengths come
        from sentence_lengths

    Arguments:
        source (str|Doc|Iterable[int]): Text, Doc object or lengths of the
            sentences (a list, a numpy array, a Series)
        window (int): Window of the moving average in sentences
        inset (bool): Show the inset with the histogram
        ax (Axes): Axes for the plot; if not given, a new figure is created

    Returns:
        Axes: Axes with the plot

    Raises:
        SourceTypeError: If the data source is set incorrectly
        ParameterError: If the window is below one
        SourceError: If there are no sentences
    """
    if window < 1:
        raise ParameterError("The window must be at least one")
    lengths = sentence_lengths(source)
    if not lengths:
        raise SourceError("The data source has no sentences")
    if ax is None:
        _, ax = plt.subplots(figsize=(9, 4))
    numbers = np.arange(1, len(lengths) + 1)
    ax.plot(numbers, lengths, marker=".", linewidth=1, color="tab:blue", label="Sentence length")
    if len(lengths) >= window:
        average = np.convolve(lengths, np.ones(window) / window, mode="valid")
        ax.plot(
            numbers[window - 1 :] - (window - 1) / 2,
            average,
            linewidth=2,
            color="tab:red",
            label=f"Moving average ({window})",
        )
    ax.set_xlabel("Number of the sentence")
    ax.set_ylabel("Words in the sentence")
    ax.set_title("Sentence lengths")
    ax.legend(loc="upper left")
    if inset:
        ax.set_ylim(top=max(lengths) * 1.7)
        histogram = ax.inset_axes((0.7, 0.62, 0.28, 0.33))
        histogram.hist(lengths, bins="auto", color="tab:gray")
        histogram.set_title("Distribution", fontsize=8)
        histogram.tick_params(labelsize=7)
    return ax


def sentence_lengths(source: str | Doc | Iterable[int]) -> list[int]:
    """
    Extracting the lengths of the sentences in words

    Description:
        The sentences of a string come from sentenize and its words from the
        tokenizer of the blank Spanish pipeline, a word belonging to the
        sentence it starts in; the sentences of a Doc come from its sentence
        boundaries, or from its text without them; ready lengths - any
        sequence of integers, a numpy array and a Series included - are used
        as they are. Sentences without words are skipped

    Arguments:
        source (str|Doc|Iterable[int]): Text, Doc object or ready lengths

    Returns:
        list[int]: Lengths of the sentences in order

    Raises:
        SourceTypeError: If the data source is set incorrectly

    Example:
        >>> from ests.visualizers import sentence_lengths
        >>> sentence_lengths("El gato duerme. ¿Y el perro? —Come —dijo ella.")
        [3, 3, 3]
    """
    if isinstance(source, str):
        starts = [start for start, _, _ in iter_text_words(source)]
        spans = [(start, stop) for start, stop, _ in iter_text_sents(source)]
        return count_words_by_spans(starts, spans)
    if isinstance(source, Doc):
        if source.has_annotation("SENT_START"):
            lengths = [sum(1 for _ in iter_doc_words(sent)) for sent in source.sents]
            return [length for length in lengths if length]
        return sentence_lengths(source.text)
    if isinstance(source, Iterable):
        lengths = list(source)
        if all(isinstance(length, Integral) for length in lengths):
            return [int(length) for length in lengths]
    raise SourceTypeError("The data source is set incorrectly")
