# Vocabulary growth and frequency spectrum

!!! info ""
    **ests.visualizers.heaps_plot()**, **ests.visualizers.frequency_spectrum_plot()**

## Description

Two plots of the distribution of the words of a text that complement [Zipf's law](zipf.md): the growth of the vocabulary with the length of the text by Heaps' law and the frequency spectrum - how many word types occur exactly once, twice, three times. The functions take the axes `ax` and return `Axes`.

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/vocabulary/) core; the fit of Heaps' law is described in [`fit_heaps`](../stats/diversity_stats_funcs.md#heaps_beta) and the spectrum in [`calc_frequency_spectrum`](../stats/diversity_stats_funcs.md#frequency_spectrum). The default labels are the English ones of `VISUALIZER_LABELS` in `anyts.constants`; `labels` replaces any of them.

## Heaps' law { #heaps_plot }

--8<-- "visualizers/vocabulary.md:heaps_plot"

## Frequency spectrum { #frequency_spectrum_plot }

--8<-- "visualizers/vocabulary.md:frequency_spectrum_plot"

## Usage example

The lemmas of *Marianela* by Galdós from the [corpus of literature](../datasets/spanishliterature.md).

!!! example "Example"

    _Code_:

    ``` python
    import matplotlib.pyplot as plt

    from ests import WordsExtractor
    from ests.datasets import SpanishLiterature
    from ests.visualizers import frequency_spectrum_plot, heaps_plot

    sl = SpanishLiterature()
    sl.download()
    text = next(
        record["text"] for record in sl.get_records(author="galdos") if record["title"] == "Marianela"
    )
    lemmas = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True).extract(text)

    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 4.5))
    heaps_plot(lemmas, ax=left)
    frequency_spectrum_plot(lemmas, ax=right)
    ```

    _Result_:

    ![ests](../img/vocabulary.png){: .center }
