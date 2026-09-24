import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.axes import Axes

from ests import WordsExtractor
from ests.corpus import delta, mendenhall_curve
from ests.exceptions import SourceError
from ests.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

matplotlib.use("Agg")

texts = {
    "A": (
        "El gato estaba en la ventana y miraba los pájaros. "
        "Los pájaros se fueron y el gato durmió en la ventana."
    ),
    "B": "El perro estaba en el suelo y dormía. Después el perro comió y otra vez dormía en el suelo.",
    "C": "Mañana el gato volverá a la ventana y mirará los pájaros, pero el perro dormirá.",
}
extractor = WordsExtractor(lowercase=True)
corpus = {name: extractor.extract(text) for name, text in texts.items()}
distances = delta(corpus, n_mfw=10)


def test_dendrogram_plot():
    ax = dendrogram_plot(distances)
    assert isinstance(ax, Axes)
    assert sorted(label.get_text() for label in ax.get_yticklabels()) == ["A", "B", "C"]
    assert ax.get_xlabel() == "Distance"
    assert ax.get_title() == "Clustering of the texts"
    assert len(ax.collections) >= 2
    _, given = plt.subplots()
    assert dendrogram_plot(distances, method="average", ax=given) is given
    plt.close("all")
    with pytest.raises(SourceError):
        dendrogram_plot(distances.iloc[:1, :1])
    with pytest.raises(SourceError, match="square matrix"):
        dendrogram_plot(distances.iloc[:2, :3])
    with pytest.raises(SourceError, match="finite"):
        dendrogram_plot(distances.replace(0.0, np.nan))
    assert len(plt.get_fignums()) == 0


def test_pca_plot():
    ax = pca_plot(corpus, n_mfw=10)
    assert isinstance(ax, Axes)
    assert [text.get_text() for text in ax.texts] == ["A", "B", "C"]
    offsets = ax.collections[0].get_offsets()
    assert offsets.shape == (3, 2)
    assert np.allclose(offsets.mean(axis=0), 0, atol=1e-9)
    assert ax.get_xlabel().startswith("Component 1 (")
    assert ax.get_ylabel().startswith("Component 2 (")
    with pytest.raises(SourceError):
        pca_plot({name: corpus[name] for name in ("A", "B")}, n_mfw=10)
    _, given = plt.subplots()
    assert pca_plot(corpus, n_mfw=10, ax=given) is given
    ax = pca_plot(corpus, n_mfw=1)
    assert ax.get_xlabel() == "Component 1 (100.0%)"
    assert np.allclose(ax.collections[0].get_offsets()[:, 1], 0)
    # A table of constant columns has no variance to explain
    same = dict.fromkeys(("A", "B", "C"), corpus["A"])
    assert pca_plot(same, n_mfw=5).get_xlabel() == "Component 1 (0.0%)"
    plt.close("all")


def test_mds_plot():
    ax = mds_plot(distances)
    assert isinstance(ax, Axes)
    assert [text.get_text() for text in ax.texts] == ["A", "B", "C"]
    offsets = np.asarray(ax.collections[0].get_offsets())
    assert offsets.shape == (3, 2)
    assert np.allclose(offsets.mean(axis=0), 0, atol=1e-9)
    recovered = np.linalg.norm(offsets[0] - offsets[1])
    assert recovered <= distances.loc["A", "B"] + 1e-9
    assert ax.get_title() == "Multidimensional scaling"
    _, given = plt.subplots()
    assert mds_plot(distances, ax=given) is given
    with pytest.raises(SourceError):
        mds_plot(distances.iloc[:1, :1])
    with pytest.raises(SourceError):
        mds_plot(distances.replace(0.0, np.inf))
    plt.close("all")


def test_mds_plot_exact():
    exact = distances.copy()
    exact.loc[:, :] = [[0, 3, 4], [3, 0, 5], [4, 5, 0]]
    offsets = np.asarray(mds_plot(exact).collections[0].get_offsets())
    for i, j, expected in ((0, 1, 3), (0, 2, 4), (1, 2, 5)):
        assert np.linalg.norm(offsets[i] - offsets[j]) == pytest.approx(expected)
    plt.close("all")


def test_mendenhall_plot_missing_lengths():
    # A length that no word has is drawn at zero, not between its neighbours
    ax = mendenhall_plot({"A": ["a", "abc", "abc"]})
    assert ax.get_lines()[0].get_xydata().tolist() == [[1, 1 / 3], [2, 0.0], [3, 2 / 3]]
    plt.close("all")


def test_mendenhall_plot():
    ax = mendenhall_plot(corpus)
    assert isinstance(ax, Axes)
    assert [line.get_label() for line in ax.get_lines()] == ["A", "B", "C"]
    curve = mendenhall_curve(corpus["A"])
    lengths = list(range(1, max(curve) + 1))
    assert list(ax.get_lines()[0].get_xdata()) == lengths
    assert list(ax.get_lines()[0].get_ydata()) == [curve.get(n, 0.0) for n in lengths]
    assert ax.get_legend() is not None
    _, given = plt.subplots()
    assert mendenhall_plot(corpus, ax=given) is given
    with pytest.raises(SourceError):
        mendenhall_plot({})
    plt.close("all")
    with pytest.raises(SourceError):
        mendenhall_plot({"A": []})
    assert len(plt.get_fignums()) == 0
