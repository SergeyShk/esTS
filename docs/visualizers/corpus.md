# Corpus plots

!!! info ""
    **ests.visualizers.dispersion_plot()**, **ests.visualizers.keyness_plot()**, **ests.visualizers.collocation_network()**

## Description

Plots for the [corpus measures](../corpus/keyness.md): the lexical dispersion - where in a text a word occurs, a chart of the keywords found by [`keyness`](../corpus/keyness.md) and a network of the collocations found by [`collocations`](../corpus/collocations.md). The matplotlib functions take the axes `ax` and return `Axes`: without `ax` a new figure is created, with it the plot goes into a grid of one's own; the network of collocations is built by graphviz and returns a `Graph`, as the [word tree](word_tree.md) returns a `Digraph`.

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/corpus/) core. The default labels of the matplotlib plots are the English ones of `VISUALIZER_LABELS` in `anyts.constants`; `labels` replaces any of them.

## Lexical dispersion { #dispersion_plot }

--8<-- "visualizers/corpus.md:dispersion_plot"

The words are extracted by [`WordsExtractor`](../extractors/words.md): lower case with `lowercase=True`, lemmas with `use_lexemes=True`.

## Chart of keywords { #keyness_plot }

--8<-- "visualizers/corpus.md:keyness_plot"

## Network of collocations { #collocation_network }

--8<-- "visualizers/corpus.md:collocation_network"

## Usage example

*Marianela* by Galdós and six novels from the [corpus of literature](../datasets/spanishliterature.md): *Marianela*, *Misericordia* and *Torquemada en la hoguera* against *Niebla*, *Abel Sánchez* and *La tía Tula* by Unamuno.

!!! example "Example"

    _Code_:

    ``` python
    from spacy.lang.es.stop_words import STOP_WORDS

    from ests import WordsExtractor
    from ests.corpus import collocations, keyness
    from ests.datasets import SpanishLiterature
    from ests.visualizers import collocation_network, dispersion_plot, keyness_plot

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

    # Where the characters and the motifs of Marianela occur
    words = WordsExtractor(lowercase=True).extract(novels["Marianela"])
    dispersion_plot(words, ["nela", "pablo", "florentina", "golfín", "ciego", "luz"])

    # Keywords of Galdós against Unamuno, lemmas without stop words
    we = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True, stopwords=STOP_WORDS)
    galdos = [lemma for title in titles[:3] for lemma in we.extract(novels[title])]
    unamuno = [lemma for title in titles[3:] for lemma in we.extract(novels[title])]
    keyness_plot(
        keyness(galdos, unamuno, min_freq=5, top_n=10),
        keyness(galdos, unamuno, positive=False, min_freq=5, top_n=10),
        labels=("Galdós", "Unamuno"),
    )

    # Network of collocations of Marianela
    graph = collocation_network(
        collocations(we.extract(novels["Marianela"]), window=3, min_freq=5, top_n=25)
    )
    graph.render("network", format="png")
    ```

    _Result_:

    ![ests](../img/dispersion.png){: .center }

    ![ests](../img/keyness.png){: .center }

    ![ests](../img/network.png){: .center }

Nela runs through the whole novel, Florentina enters in its second half, and the doctor Golfín opens and closes it; the blindness of Pablo (`ciego`) belongs mostly to the first half. Beside the names of the characters, the keywords show the old spelling of the editions (`á`, `fué`) and words of the themes of Unamuno: `acaso`, `hijo`. The network of collocations gathers the names and the places of *Marianela* around `d.`, the abbreviated *don*: Teodoro Golfín, Aldeacorba de Suso, the mines of Socartes.
