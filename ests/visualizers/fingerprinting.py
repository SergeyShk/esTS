from collections.abc import Callable, Sequence

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.patches import Rectangle

from ..diversity_stats import calc_ttr
from ..exceptions import ParameterError, SourceTypeError
from ..utils import check_sequence


def fingerprinting(
    texts: list[list[str]],
    segment_len: int = 10,
    metric: Callable[[Sequence[str]], float] | None = None,
    x_size: int = 800,
    y_size: int = 600,
    cmap: str = "PuOr",
    ax: Axes | None = None,
) -> Axes:
    """
    Visualizing literature fingerprinting

    Description:
        Every text is cut into segments of segment_len words with a sliding
        step of a tenth of a segment, a measure of lexical diversity is
        computed for every segment, and the squares are coloured by its value
        relative to the greatest finite one; segments with an undefined
        measure (nan on segments too short for it) are drawn as zeros

    References:
        https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf

    Arguments:
        texts (list[list[str]]): List of lists of words
        segment_len (int): Size of a segment
        metric (callable): Function of a measure of lexical diversity; calc_ttr by default
        x_size (int): Width of the drawing area
        y_size (int): Height of the drawing area
        cmap (str): Colour map
        ax (Axes): Axes for the plot; if not given, a 15×10 figure is created

    Returns:
        Axes: Axes with the fingerprinting

    Raises:
        SourceTypeError: If the texts are not a list of lists of words or the
            measure is not callable
        ParameterError: If the size of a segment is below one
    """
    check_sequence(texts, "lists of words")
    if not all(isinstance(text, (list, tuple)) for text in texts):
        raise SourceTypeError("The texts must be a list of lists of words")
    if metric is not None and not callable(metric):
        raise SourceTypeError("The measure must be callable")
    if segment_len < 1:
        raise ParameterError("The size of a segment must be greater than 0")
    metrics = {}
    metric_func = metric if metric is not None else calc_ttr
    for i, text in enumerate(texts):
        start = 0
        end = segment_len
        window_len = int(0.1 * segment_len)
        if window_len == 0:
            window_len = 1
        n_words = len(text)
        segments = []
        while end <= n_words:
            segment = text[start:end]
            metric_value = metric_func(segment)
            segments.append(metric_value)
            start += window_len
            end += window_len
        final_segment = text[start:]
        segments.append(metric_func(final_segment))
        metrics[i] = segments

    if ax is None:
        _, ax = plt.subplots(figsize=(15, 10))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    cmaps = plt.get_cmap(cmap)
    cmap_list = [cmaps(i) for i in range(cmaps.N)]
    cx = ax.imshow(cmap_list, interpolation="nearest", cmap=cmap, visible=None)
    ax.figure.colorbar(cx, ax=ax)
    x = -x_size + 30
    y = y_size - 50
    finite = [value for segments in metrics.values() for value in segments if np.isfinite(value)]
    max_metric = max(finite) if finite else 1.0
    n_cols = 0
    n_rows = 0
    for segments in metrics.values():
        n_segments = len(segments)
        n_cols = int(n_segments / 8) if (n_segments % 8) == 0 else int(n_segments / 8) + 1
        n_rows = 8 if n_cols > 1 else n_segments
        b = np.zeros((n_rows, n_cols))
        pos = 0
        for i in range(n_rows):
            for j in range(n_cols):
                if pos <= (n_segments - 1):
                    b[i][j] = segments[pos] if np.isfinite(segments[pos]) else 0
                    pos += 1
                else:
                    b[i][j] = 0
        tam_quad = 15
        x_max = x_size - 25
        margin = 25
        x_accum = n_cols * tam_quad
        if (x + x_accum + margin) > x_max:
            y = y - ((8 * tam_quad) + margin)
            x = -x_size + 25
        for i in range(n_rows):
            for j in range(n_cols):
                if b[i][j] == 0:
                    rect = Rectangle((x, y), tam_quad, tam_quad, color="Black")
                    ax.add_patch(rect)
                else:
                    rect = Rectangle((x, y), tam_quad, tam_quad, color=cmaps(b[i][j] / max_metric))
                    ax.add_patch(rect)
                x += tam_quad
            x -= n_cols * tam_quad
            y -= tam_quad
        x += (n_cols * tam_quad) + margin
        y += n_rows * tam_quad
    ax.set_xlim(-x_size, x_size)
    ax.set_ylim(-y_size, y_size)
    ax.set_title("Literature fingerprinting")
    return ax
