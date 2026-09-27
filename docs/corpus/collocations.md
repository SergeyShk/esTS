# Collocations

!!! info ""
    **ests.corpus.collocations()**, **ests.corpus.Collocation**

## Description

--8<-- "corpus/collocations.md:collocations"

The module `ests.corpus.collocations` re-exports the function and the measures of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/) core (`from ests.corpus.collocations import calc_logdice`). Words are extracted with [`WordsExtractor`](../extractors/words.md); for Spanish fixed expressions such as `punto de vista` or `llevar a cabo` take its lemmas (`use_lexemes=True`).

## Measures

--8<-- "corpus/collocations.md:collocations-measures"

## Parameters

--8<-- "corpus/collocations.md:collocations-parameters"

## Result

--8<-- "corpus/collocations.md:Collocation"

## Example

!!! example "Example"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )

    collocations(words, window=2, top_n=1)
    # [Collocation(left='en', right='ventana', freq_left=3, freq_right=3, freq_pair=3, score=13.0)]

    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="gato", min_freq=1, measure="mi")[:2]
    ]
    # [('gato', 'volver', 3.62), ('gato', 'estar', 2.62)]
    ```
