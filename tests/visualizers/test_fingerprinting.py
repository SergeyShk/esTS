from functools import partial
from math import nan

import matplotlib
import matplotlib.pyplot as plt
import pytest
from matplotlib.axes import Axes

from ests.diversity_stats import calc_simpson_index
from ests.exceptions import ParameterError, SourceTypeError
from ests.visualizers import fingerprinting

matplotlib.use("Agg")


@pytest.fixture(scope="module")
def texts():
    return [["el", "gato", "duerme"], ["el", "perro", "come", "pan"]]


def test_fingerprinting_type_error(texts):
    with pytest.raises(TypeError):
        fingerprinting(1)
    with pytest.raises(SourceTypeError):
        fingerprinting(["el gato duerme", ["el", "perro"]])
    with pytest.raises(SourceTypeError):
        fingerprinting("el gato duerme")
    with pytest.raises(SourceTypeError):
        fingerprinting(texts, metric=42)
    for segment_len in (0, -1):
        with pytest.raises(ParameterError):
            fingerprinting(texts, segment_len=segment_len)
    assert plt.get_fignums() == []


def test_fingerprinting(texts):
    ax = fingerprinting(texts, x_size=600, y_size=500)
    assert isinstance(ax, Axes)
    assert len(ax.figure.axes) == 2
    assert ax.get_title() == "Literature fingerprinting"
    assert ax.figure.axes[1].get_label() == "<colorbar>"
    assert ax.get_xlim() == (-600.0, 600.0)
    assert ax.get_ylim() == (-500.0, 500.0)
    assert len(ax.patches) == 2
    plt.close("all")


def test_fingerprinting_ax(texts):
    _, given = plt.subplots()
    ax = fingerprinting(texts, ax=given)
    assert ax is given
    assert len(ax.figure.axes) == 2
    plt.close("all")


def test_fingerprinting_metric(texts):
    ax = fingerprinting(texts, metric=calc_simpson_index)
    assert isinstance(ax, Axes)
    plt.close("all")


def test_fingerprinting_callable_metric(texts):
    # Any callable object and not only a function: a partial, a method, a class
    by_length = partial(lambda segment, scale: scale * len(segment), scale=0.1)
    colors = [patch.get_facecolor() for patch in fingerprinting(texts, metric=by_length).patches]
    plt.close("all")
    ttr_colors = [patch.get_facecolor() for patch in fingerprinting(texts).patches]
    plt.close("all")
    assert len(set(ttr_colors)) == 1
    assert len(set(colors)) == 2


def test_fingerprinting_layout():
    # 95 words in segments of 5 with a step of 1: 91 segments and the tail, 12 columns of 8;
    # 40 words: 36 and the tail, 5 columns; the tails of fewer than 5 words give nan
    words = [f"palabra{index % 7}" for index in range(95)]

    def metric(segment):
        return nan if len(segment) < 5 else len(set(segment)) / len(segment)

    ax = fingerprinting([words, words[:40]], segment_len=5, metric=metric, x_size=100, y_size=500)
    assert len(ax.patches) == 96 + 40
    black = [patch for patch in ax.patches if tuple(patch.get_facecolor()) == (0, 0, 0, 1)]
    assert len(black) == 4 + 3 + 2
    # Both texts are wider than the area and start a new row of their own
    assert ax.patches[0].get_xy() == (-75, 305)
    assert ax.patches[96].get_xy() == (-75, 160)
    plt.close("all")
