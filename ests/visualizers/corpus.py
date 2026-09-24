from collections import Counter
from collections.abc import Sequence
from math import isfinite, isnan, log2, nan

import matplotlib.pyplot as plt
from graphviz import Graph, nohtml
from matplotlib.axes import Axes
from matplotlib.patches import Patch

from ..corpus.collocations import Collocation
from ..corpus.keyness import Keyword
from ..exceptions import ParameterError, SourceError
from ..utils import check_sequence


def dispersion_plot(words: Sequence[str], targets: Sequence[str], ax: Axes | None = None) -> Axes:
    """
    Plotting the lexical dispersion of words over a text

    Description:
        A row for every word of targets and a tick at the position of each of
        its occurrences in the text (dispersion_plot of NLTK, textplot_xray of
        quanteda); words are compared as they are - case and lemmatization
        belong to the extraction

    Arguments:
        words (list[str]): Words of the text in order
        targets (list[str]): Words whose occurrences are shown
        ax (Axes): Axes for the plot; if not given, a new figure is created

    Returns:
        Axes: Axes with the plot

    Raises:
        SourceTypeError: If a string or a Doc is passed instead of a list of words
        SourceError: If there are no words or no target words
    """
    check_sequence(words)
    check_sequence(targets, "target words")
    if not words or not targets:
        raise SourceError("The data source has no words")
    positions = [
        [index for index, word in enumerate(words) if word == target] for target in targets
    ]
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 0.4 * len(targets) + 1.5))
    ax.eventplot(
        positions,
        lineoffsets=range(len(targets)),
        linelengths=0.8,
        linewidths=0.8,
        colors="tab:blue",
    )
    ax.set_yticks(range(len(targets)), labels=list(targets))
    ax.invert_yaxis()
    ax.set_xlim(0, len(words))
    ax.set_xlabel("Position of the word in the text")
    ax.set_title("Lexical dispersion")
    return ax


def keyness_plot(
    positive: Sequence[Keyword],
    negative: Sequence[Keyword] = (),
    top_n: int = 20,
    labels: tuple[str, str] = ("target corpus", "reference corpus"),
    field: str = "score",
    log: bool = False,
    ax: Axes | None = None,
) -> Axes:
    """
    Plotting a chart of keywords

    Description:
        Diverging horizontal bars (textplot_keyness of quanteda): the words of
        positive to the right, of negative to the left, the length of a bar is
        the absolute value of the field (score, g2, log_ratio), so the side is
        set by the list and not by the sign of the measure; top_n words on
        each side, the words with an undefined or infinite value are skipped.
        For the odds ratio (score from 0 to infinity, one - equal odds) set
        log=True: the absolute log2 of the value is plotted, symmetric
        around one

    Arguments:
        positive (list[Keyword]): Positive keywords (keyness)
        negative (list[Keyword]): Negative keywords (keyness with positive=False)
        top_n (int): Number of words on each side
        labels (tuple[str, str]): Labels of the legend for the target and the reference corpus
        field (str): Field of Keyword whose values are plotted
        log (bool): Plot log2 of the value - for the odds ratio
        ax (Axes): Axes for the plot; if not given, a new figure is created

    Returns:
        Axes: Axes with the chart

    Raises:
        ParameterError: If the field is unknown or top_n is below one
        SourceError: If there are no keywords or the measure of every one is undefined
    """
    if field not in Keyword._fields[1:]:
        raise ParameterError(f"Unknown field of a keyword: {field}")
    if top_n < 1:
        raise ParameterError("The number of words must be greater than 0")
    top = _bars(positive, field, log, 1)[:top_n]
    bottom = _bars(negative, field, log, -1)[:top_n]
    keywords = top + bottom[::-1]
    if not keywords:
        raw = list(positive) + list(negative)
        raise SourceError(
            "The data source has no words" if not raw else "The measure is undefined"
        )
    if ax is None:
        _, ax = plt.subplots(figsize=(8, 0.3 * len(keywords) + 1.5))
    rows = range(len(keywords))
    colors = ["tab:blue"] * len(top) + ["tab:red"] * len(bottom)
    ax.barh(rows, [value for _, value in keywords], color=colors)
    ax.set_yticks(rows, labels=[keyword.word for keyword, _ in keywords])
    ax.invert_yaxis()
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel(f"|log2({field})|" if log else f"|{field}|")
    ax.set_title("Keywords")
    handles = []
    legend_labels = []
    if top:
        handles.append(Patch(color="tab:blue"))
        legend_labels.append(labels[0])
    if bottom:
        handles.append(Patch(color="tab:red"))
        legend_labels.append(labels[1])
    ax.legend(handles, legend_labels)
    return ax


def _bars(
    keywords: Sequence[Keyword], field: str, log: bool, sign: int
) -> list[tuple[Keyword, float]]:
    """Keywords with the signed length of their bars, those with an undefined value skipped"""
    bars = []
    for keyword in keywords:
        value = float(getattr(keyword, field))
        if log:
            value = log2(value) if value > 0 else nan
        if isfinite(value):
            bars.append((keyword, sign * abs(value)))
    return bars


def collocation_network(collocations: Sequence[Collocation], top_n: int | None = None) -> Graph:
    """
    Building the network of collocations

    Description:
        An undirected graph (textplot_network of quanteda): the nodes are the
        words with the size of the font by the frequency of the word, the
        edges the pairs with the width and the label by the value of the
        measure; the neato layout. The nodes get generated identifiers and the
        words go to their labels, as a colon in a word (10:30) would read as a
        port of graphviz. Rendering needs the executables of Graphviz

    Arguments:
        collocations (list[Collocation]): Collocations (collocations)
        top_n (int): Number of pairs from the start of the list; None - all of them

    Returns:
        Graph: Graph of graphviz

    Raises:
        ParameterError: If top_n is below one
        SourceError: If there are no collocations

    Example:
        >>> from ests.corpus import collocations
        >>> from ests.visualizers import collocation_network
        >>> words = "vino tinto y vino blanco pero vino tinto".split()
        >>> print(collocation_network(collocations(words, window=1)).source)
        graph collocations {
            graph [overlap=false splines=true]
            node [fontname=Helvetica margin=0 shape=plaintext]
            edge [color=gray50 fontname=Helvetica fontsize=9]
            n0 [label=vino fontsize=24]
            n1 [label=tinto fontsize=10]
            n0 -- n1 [label=13.68 penwidth=2.25]
        }
        <BLANKLINE>
    """
    if top_n is not None and top_n < 1:
        raise ParameterError("The number of pairs must be greater than 0")
    pairs = list(collocations)[:top_n] if top_n else list(collocations)
    if not pairs:
        raise SourceError("The data source has no collocations")
    frequencies: Counter[str] = Counter()
    for pair in pairs:
        frequencies[pair.left] = max(frequencies[pair.left], pair.freq_left)
        frequencies[pair.right] = max(frequencies[pair.right], pair.freq_right)
    scores = [pair.score for pair in pairs if not isnan(pair.score)]
    min_score, max_score = (min(scores), max(scores)) if scores else (0.0, 0.0)
    min_freq, max_freq = min(frequencies.values()), max(frequencies.values())
    graph = Graph("collocations", engine="neato")
    graph.attr("graph", overlap="false", splines="true")
    graph.attr("node", shape="plaintext", margin="0", fontname="Helvetica")
    graph.attr("edge", color="gray50", fontsize="9", fontname="Helvetica")
    nodes = {word: f"n{index}" for index, word in enumerate(frequencies)}
    for word, frequency in frequencies.items():
        graph.node(
            nodes[word],
            label=nohtml(word),
            fontsize=f"{_scale(frequency, min_freq, max_freq, 10, 24):.0f}",
        )
    for pair in pairs:
        score = 0.0 if isnan(pair.score) else pair.score
        graph.edge(
            nodes[pair.left],
            nodes[pair.right],
            label=f"{score:.2f}",
            penwidth=f"{_scale(score, min_score, max_score, 0.5, 4):.2f}",
        )
    return graph


def _scale(value: float, low: float, high: float, out_low: float, out_high: float) -> float:
    """Linear map of a value from [low, high] to [out_low, out_high], the middle when low = high"""
    if high <= low:
        return (out_low + out_high) / 2
    return out_low + (value - low) / (high - low) * (out_high - out_low)
