# Vocabulary growth and frequency spectrum

!!! info ""
    **ests.visualizers.heaps_plot()**, **ests.visualizers.frequency_spectrum_plot()**

## Description

Two plots of the distribution of the words of a text that complement [Zipf's law](zipf.md): the growth of the vocabulary with the length of the text by Heaps' law and the frequency spectrum - how many word types occur exactly once, twice, three times. Both plots are in zipfR (`plot.vgc`, `plot.spc`). The functions take the axes `ax` and return `Axes`.

## Heaps' law { #heaps_plot }

The size of the vocabulary $V$ after every word of the text and the fitted curve $V(N) = K \cdot N^{\beta}$ of [`fit_heaps`](../stats/diversity_stats_funcs.md#heaps_beta) with its parameters in the legend. On corpora of millions of words $\beta$ lies around 0.4-0.6; over the whole curve of a single text it comes out higher, 0.6-0.9, since almost every word is new at the start of a text; the curve depends on the order of the words.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text in order |
| `ax` | Axes | `None` | Axes for the plot |

## Frequency spectrum { #frequency_spectrum_plot }

The number of word types $V(m)$ that occur exactly $m$ times ([`calc_frequency_spectrum`](../stats/diversity_stats_funcs.md#frequency_spectrum)) in logarithmic coordinates; the left edge is the hapaxes. The spectrum underlies the measures of diversity of Yule, Sichel, Michéa and Honoré, and its shape shows how far the vocabulary of the text is from being exhausted.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text |
| `ax` | Axes | `None` | Axes for the plot |

## Usage example

The lemmas of *Marianela* by Galdós from [Project Gutenberg](https://www.gutenberg.org).

!!! example "Example"

    _Code_:

    ``` python
    from urllib.request import urlopen

    import matplotlib.pyplot as plt

    from ests import WordsExtractor
    from ests.visualizers import frequency_spectrum_plot, heaps_plot

    url = "https://www.gutenberg.org/cache/epub/17340/pg17340.txt"
    text = urlopen(url).read().decode("utf-8")
    text = text[text.index("\n", text.index("*** START OF")) : text.index("*** END OF")]
    lemmas = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True).extract(text)

    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.5))
    heaps_plot(lemmas, ax=left)
    frequency_spectrum_plot(lemmas, ax=right)
    ```

    _Result_:

    ![ests](../img/vocabulary.png){: .center }
