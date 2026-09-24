import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
import spacy
from matplotlib.axes import Axes

from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp
from ests.visualizers import sentence_lengths, sentence_lengths_plot

matplotlib.use("Agg")

text = (
    "El gato estaba en la ventana. Miraba los pájaros, pero los pájaros se fueron. "
    "¿Durmió? Mañana volverá a estar en la ventana."
)


def test_sentence_lengths():
    assert sentence_lengths(text) == [6, 8, 1, 7]
    assert sentence_lengths(spacy.blank("es")(text)) == [6, 8, 1, 7]
    nlp = spacy.blank("es")
    nlp.add_pipe("sentencizer")
    assert sentence_lengths(nlp(text)) == [6, 8, 1, 7]
    assert sentence_lengths(get_nlp()(text)) == [6, 8, 1, 7]
    # A remark of the narrator after a dash stays in the sentence of the line
    assert sentence_lengths("—¿Vienes? —preguntó ella. —Sí.") == [3, 1]
    assert sentence_lengths([3, 5, 2]) == [3, 5, 2]
    assert sentence_lengths(np.array([3, 5, 2])) == [3, 5, 2]
    assert sentence_lengths(pd.Series([3, 5, 2])) == [3, 5, 2]
    assert sentence_lengths((np.int64(3), np.int32(5))) == [3, 5]
    assert sentence_lengths(iter([3, 5])) == [3, 5]
    assert sentence_lengths("") == []
    assert sentence_lengths("¿? ... ¡!") == []
    with pytest.raises(SourceTypeError):
        sentence_lengths(["gato", "duerme"])
    with pytest.raises(SourceTypeError):
        sentence_lengths([3.5, 2])
    with pytest.raises(SourceTypeError):
        sentence_lengths(42)


def test_sentence_lengths_plot():
    ax = sentence_lengths_plot(text, window=2)
    assert isinstance(ax, Axes)
    series, average = ax.get_lines()
    assert list(series.get_ydata()) == [6, 8, 1, 7]
    assert list(average.get_ydata()) == [7.0, 4.5, 4.0]
    assert list(average.get_xdata()) == [1.5, 2.5, 3.5]
    assert average.get_label() == "Moving average (2)"
    assert len(ax.child_axes) == 1
    assert ax.child_axes[0].get_title() == "Distribution"
    assert ax.get_ylim()[1] == pytest.approx(8 * 1.7)
    assert ax.get_title() == "Sentence lengths"
    ax = sentence_lengths_plot([3, 5, 2], window=10, inset=False)
    assert len(ax.get_lines()) == 1
    assert not ax.child_axes
    _, given = plt.subplots()
    assert sentence_lengths_plot([3, 5, 2], ax=given) is given
    with pytest.raises(SourceError):
        sentence_lengths_plot("")
    with pytest.raises(ParameterError):
        sentence_lengths_plot(text, window=0)
    plt.close("all")
