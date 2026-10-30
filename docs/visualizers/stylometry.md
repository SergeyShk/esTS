# Stylometric plots

Plots for [stylometry](../corpus/stylometry.md): a dendrogram, the multidimensional scaling and the histograms of the distances within and between authors of the matrix of distances of [`delta`](../corpus/stylometry.md#delta), the principal components of the frequencies of the most frequent words, the distances of rolling Delta along a text, the segments of corpora by the markers of Zeta and the Mendenhall curves of several texts. The functions take the axes `ax` and return `Axes`.

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/stylometry/) core; the frequencies of the principal components come from [`frequency_table`](../corpus/stylometry.md#delta), the distances along a text from [`rolling_delta`](../corpus/stylometry.md#rolling_delta), the segments from [`zeta_segments`](../corpus/stylometry.md#zeta) and the curves from [`mendenhall_curve`](../corpus/stylometry.md#mendenhall). The default labels are the English ones of `VISUALIZER_LABELS` in `anyts.constants`; `labels` replaces any of them.

## Dendrogram { #dendrogram_plot }

--8<-- "visualizers/stylometry.md:dendrogram_plot"

## Principal components { #pca_plot }

--8<-- "visualizers/stylometry.md:pca_plot"

## Multidimensional scaling { #mds_plot }

--8<-- "visualizers/stylometry.md:mds_plot"

## Distances within and between authors { #delta_histogram_plot }

--8<-- "visualizers/stylometry.md:delta_histogram_plot"

## Rolling Delta { #rolling_delta_plot }

--8<-- "visualizers/stylometry.md:rolling_delta_plot"

## Zeta scatter { #zeta_scatter_plot }

--8<-- "visualizers/stylometry.md:zeta_scatter_plot"

## Mendenhall curves { #mendenhall_plot }

--8<-- "visualizers/stylometry.md:mendenhall_plot"

The plots of six novels from the [corpus of literature](../datasets/spanishliterature.md), three by Galdós and three by Unamuno:

``` python
import matplotlib.pyplot as plt

from ests import WordsExtractor
from ests.corpus import delta
from ests.datasets import SpanishLiterature
from ests.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

sl = SpanishLiterature()
sl.download()
titles = (
    "Marianela",
    "Misericordia",
    "Torquemada en la hoguera",
    "Niebla",
    "Abel Sánchez",
    "La tía Tula",
)
novels = {
    record["title"]: record["text"]
    for author in ("galdos", "unamuno")
    for record in sl.get_records(author=author)
    if record["title"] in titles
}
we = WordsExtractor(lowercase=True)
corpus = {title: we.extract(novels[title]) for title in titles}
distances = delta(corpus, n_mfw=100, variant="cosine")

# Dendrogram and principal components on one figure
fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
dendrogram_plot(distances, ax=left)
pca_plot(corpus, n_mfw=100, ax=right)

# Multidimensional scaling and Mendenhall curves
fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
mds_plot(distances, ax=left)
mendenhall_plot(
    {title: corpus[title] for title in ("Marianela", "Niebla", "La tía Tula")}, ax=right
)
```

![ests](../img/stylometry.png){: .center }

![ests](../img/mds_mendenhall.png){: .center }

Cosine Delta over the 100 most frequent words separates the authors: the dendrogram joins the novels of each author before it joins the two groups, and the first principal component puts Galdós on one side and Unamuno on the other. The Mendenhall curves hardly differ - word length is a weak feature on its own.

The plots of twelve novels and stories of the `prose` genre of the [corpus of literature](../datasets/spanishliterature.md), four by Galdós, four by Pardo Bazán and four by Unamuno: the distances between all the works, rolling Delta over the first work of Galdós followed by the first work of Unamuno with the other three works of each author as the references, and the segments by the markers of Zeta of Galdós against Unamuno:

``` python
from ests.corpus import rolling_delta, zeta, zeta_segments
from ests.visualizers import delta_histogram_plot, rolling_delta_plot, zeta_scatter_plot

names = {"galdos": "Galdós", "pardo": "Pardo Bazán", "unamuno": "Unamuno"}
corpus, authors = {}, {}
for key, author in names.items():
    texts = sl.get_texts(genre="prose", author=key, min_len=40000, max_len=400000, limit=4)
    for i, text in enumerate(texts, 1):
        corpus[f"{author} {i}"] = we.extract(text)
        authors[f"{author} {i}"] = author
known = {author: [corpus[f"{author} {i}"] for i in (2, 3, 4)] for author in names.values()}
reference = {author: [word for words in known[author] for word in words] for author in known}
scores = zeta(known["Galdós"], known["Unamuno"], segment_size=1000)
preferred = [score.word for score in scores[:200]]
avoided = [score.word for score in scores[-200:]]
corpora = {
    "Galdós": known["Galdós"],
    "Unamuno": known["Unamuno"],
    "Galdós 1": corpus["Galdós 1"],
    "Unamuno 1": corpus["Unamuno 1"],
}

fig, axes = plt.subplots(1, 3, figsize=(19, 5))
delta_histogram_plot(delta(corpus, n_mfw=100, variant="cosine"), authors, ax=axes[0])
rolling_delta_plot(
    rolling_delta(reference, corpus["Galdós 1"] + corpus["Unamuno 1"], window=5000, step=1000),
    ax=axes[1],
)
zeta_scatter_plot(zeta_segments(corpora, preferred, avoided, segment_size=1000), ax=axes[2])
```

![ests](../img/stylometry_authors.png){: .center }

The distances between the works of one author lie mostly below those between the works of different authors. Along the novel of Galdós its nearest author is Galdós in 57 windows of 61, along that of Unamuno Unamuno in 26 of 42, Pardo Bazán in the others: a window of 5000 words is short for Delta. On the markers of Zeta the segments of the two unseen works fall into the clouds of their authors.
