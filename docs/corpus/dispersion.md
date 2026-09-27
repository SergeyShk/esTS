# Word dispersion

!!! info ""
    **ests.corpus.dispersion()**, **ests.corpus.Dispersion**

## Description

--8<-- "corpus/dispersion.md:dispersion"

The module `ests.corpus.dispersion` re-exports the function and the measures of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/) core (`from ests.corpus.dispersion import calc_dp`). Words are extracted with [`WordsExtractor`](../extractors/words.md).

## Measures

--8<-- "corpus/dispersion.md:dispersion-measures"

## Parameters

--8<-- "corpus/dispersion.md:dispersion-parameters"

## Result

--8<-- "corpus/dispersion.md:Dispersion"

## Example

!!! example "Example"

    ``` python
    from ests import SentsExtractor, WordsExtractor
    from ests.corpus import dispersion

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    we = WordsExtractor(use_lexemes=True, lowercase=True)
    words = we.extract(text)
    sizes = [len(we.extract(sent)) for sent in SentsExtractor().extract(text)]
    sizes
    # [11, 12, 14]

    dispersion(words, parts=sizes, word="gato")
    # [Dispersion(word='gato', freq=3, dp=0.04504504504504503, dp_norm=0.06410256410256408,
    #  juilland_d=0.9307654905484509, carroll_d2=0.9955884389001025,
    #  rosengren_s=0.9974825285744621, kl_divergence=0.007241184435774255)]

    # Three equal parts: a and pájaro are gathered at the edges of the text
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    # [('el', 0.1), ('gato', 0.02), ('en', 0.02), ('ventana', 0.02), ('y', 0.02), ('a', 0.34), ('pájaro', 0.32)]
    ```
