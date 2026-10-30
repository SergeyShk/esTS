# Word dispersion

--8<-- "corpus/dispersion.md:dispersion"

`ests.corpus` re-exports the function of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/) core. Words are extracted with [`WordsExtractor`](../extractors/words.md).

=== "Code"

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
    dispersion(words, parts=sizes, word="gato")

    # Three equal parts: a and pájaro are gathered at the edges of the text
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    ```

=== "Result"

    ```
    [11, 12, 14]
    [Dispersion(word='gato', freq=3, dp=0.04504504504504503, dp_norm=0.06410256410256408, juilland_d=0.9307654905484509, carroll_d2=0.9955884389001025, rosengren_s=0.9974825285744621, kl_divergence=0.007241184435774255)]
    [('el', 0.1), ('gato', 0.02), ('en', 0.02), ('ventana', 0.02), ('y', 0.02), ('a', 0.34), ('pájaro', 0.32)]
    ```

The paragraphs of a text come from [`split_paragraphs`](../extractors/sentences.md#split_paragraphs), imported from `ests.extractors`; a scene break of asterisks has no words and is dropped:

=== "Code"

    ``` python
    from ests.extractors import split_paragraphs

    text = (
        "Capítulo I\n\nEl gato estaba en la ventana y miraba a los pájaros.\n\n* * *\n\n"
        "Los pájaros se fueron y el gato se durmió en la ventana.\n\n"
        "Mañana el gato volverá a estar en la ventana."
    )
    sizes = [n for n in (len(we.extract(part)) for part in split_paragraphs(text)) if n]
    sizes
    [(d.word, round(d.dp, 2)) for d in dispersion(we.extract(text), parts=sizes, min_freq=3)]
    ```

=== "Result"

    ```
    [2, 11, 12, 9]
    [('el', 0.07), ('gato', 0.08), ('en', 0.08), ('ventana', 0.08)]
    ```

## Parameters

--8<-- "corpus/dispersion.md:dispersion-parameters"

## Result

--8<-- "corpus/dispersion.md:Dispersion"

## Measures

--8<-- "corpus/dispersion.md:dispersion-measures"

The module `ests.corpus.dispersion` re-exports the functions of the measures (`from ests.corpus.dispersion import calc_dp`).

<div class="metric-card" markdown>

### Deviation of proportions DP { #dp }

`dp` · [Gries (2008)](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_dp"

</div>

<div class="metric-card" markdown>

### Normalized DP { #dp_norm }

`dp_norm` · Lijffijt and Gries (2012)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_dp_norm"

</div>

<div class="metric-card" markdown>

### Juilland's D { #juilland_d }

`juilland_d` · Juilland and Chang-Rodríguez (1964)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_juilland_d"

</div>

<div class="metric-card" markdown>

### Carroll's D2 { #carroll_d2 }

`carroll_d2` · Carroll (1970)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_carroll_d2"

</div>

<div class="metric-card" markdown>

### Rosengren's S { #rosengren_s }

`rosengren_s` · Rosengren (1971)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_rosengren_s"

</div>

<div class="metric-card" markdown>

### Kullback-Leibler divergence { #kl_divergence }

`kl_divergence` · [Gries (2020)](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)
{ .metric-meta }

--8<-- "corpus/dispersion.md:calc_kl_divergence"

</div>
