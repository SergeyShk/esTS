from collections.abc import Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes

from ..diversity_stats import calc_frequency_spectrum, fit_heaps, vocabulary_growth
from ..exceptions import SourceError
from ..utils import check_sequence


def heaps_plot(words: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Plotting Heaps' law - the growth of the vocabulary with the length of a text

    Description:
        The size of the vocabulary V after every word of the text
        (vocabulary_growth) and the fitted curve V(N) = K · N^β (fit_heaps)
        with its parameters in the legend

    Arguments:
        words (list[str]): Words of the text in order
        ax (Axes): Axes for the plot; if not given, a new figure is created

    Returns:
        Axes: Axes with the plot

    Raises:
        SourceTypeError: If a string or a Doc is passed instead of a list of words
        SourceError: If there are fewer than two words
    """
    check_sequence(words)
    if len(words) < 2:
        raise SourceError("The growth of the vocabulary needs at least two words")
    if ax is None:
        _, ax = plt.subplots()
    lengths = np.arange(1, len(words) + 1)
    ax.plot(lengths, vocabulary_growth(words), label="Vocabulary growth")
    fit = fit_heaps(words)
    ax.plot(
        lengths,
        fit.k * lengths**fit.beta,
        linestyle="--",
        color="r",
        label=f"K·N^β: K={fit.k:.2f}, β={fit.beta:.2f}",
    )
    ax.set_xlabel("Length of the text, words")
    ax.set_ylabel("Size of the vocabulary")
    ax.set_title("Heaps' law")
    ax.grid()
    ax.legend()
    return ax


def frequency_spectrum_plot(words: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Plotting the frequency spectrum - the number of word types by frequency

    Description:
        The number of word types V(m) that occur exactly m times
        (calc_frequency_spectrum) in logarithmic coordinates, as plot.spc of
        zipfR; the left edge is the hapaxes

    Arguments:
        words (list[str]): Words of the text
        ax (Axes): Axes for the plot; if not given, a new figure is created

    Returns:
        Axes: Axes with the plot

    Raises:
        SourceTypeError: If a string or a Doc is passed instead of a list of words
        SourceError: If there are no words
    """
    check_sequence(words)
    if not words:
        raise SourceError("The data source has no words")
    if ax is None:
        _, ax = plt.subplots()
    spectrum = calc_frequency_spectrum(words)
    frequencies = sorted(spectrum)
    ax.loglog(frequencies, [spectrum[m] for m in frequencies], marker="o", linestyle="")
    ax.set_xlabel("Frequency of a word type m")
    ax.set_ylabel("Number of word types V(m)")
    ax.set_title("Frequency spectrum")
    ax.grid()
    return ax
