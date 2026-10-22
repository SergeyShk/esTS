# Collocations

--8<-- "corpus/collocations.md:collocations"

`ests.corpus` re-exports the function of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) core. Words are extracted with [`WordsExtractor`](../extractors/words.md); for Spanish fixed expressions such as `punto de vista` or `llevar a cabo` take its lemmas (`use_lexemes=True`).

=== "Code"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )

    collocations(words, window=2, top_n=1)
    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="gato", min_freq=1, measure="mi")[:2]
    ]
    ```

=== "Result"

    ```
    [Collocation(left='en', right='ventana', freq_left=3, freq_right=3, freq_pair=3, score=13.0)]
    [('gato', 'volver', 3.62), ('gato', 'estar', 2.62)]
    ```

## Parameters

--8<-- "corpus/collocations.md:collocations-parameters"

## Result

--8<-- "corpus/collocations.md:Collocation"

## Measures

--8<-- "corpus/collocations.md:collocations-measures"

The module `ests.corpus.collocations` re-exports the functions of the measures (`from ests.corpus.collocations import calc_logdice`).

<div class="metric-card" markdown>

### Mutual information { #mi }

`mi` · Church and Hanks (1990)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_mi"

</div>

<div class="metric-card" markdown>

### MI³ { #mi3 }

`mi3` · Oakes (1998)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_mi3"

</div>

<div class="metric-card" markdown>

### t-score { #t_score }

`t_score` · Church et al. (1991)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_t_score"

</div>

<div class="metric-card" markdown>

### Dice coefficient { #dice }

`dice`
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_dice"

</div>

<div class="metric-card" markdown>

### logDice { #logdice }

`logdice` · [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_logdice"

</div>

<div class="metric-card" markdown>

### Log-likelihood { #log_likelihood }

`log_likelihood` · Dunning (1993)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_log_likelihood"

</div>

<div class="metric-card" markdown>

### NPMI { #npmi }

`npmi` · Bouma (2009)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_npmi"

</div>

<div class="metric-card" markdown>

### Minimum sensitivity { #min_sensitivity }

`min_sensitivity` · Pedersen (1998)
{ .metric-meta }

--8<-- "corpus/collocations.md:calc_min_sensitivity"

</div>
