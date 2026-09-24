# Stylometry

!!! info ""
    **ests.corpus.delta()**, **ests.corpus.delta_profiles()**, **ests.corpus.frequency_table()**, **ests.corpus.z_scores()**, **ests.corpus.zeta()**, **ests.corpus.kilgarriff_chi2()**, **ests.corpus.mendenhall_curve()**, **ests.corpus.mendenhall_distance()**, **ests.corpus.function_words_profile()**

## Description

Measures of stylometry and authorship attribution: distances between texts by the frequencies of the most frequent words (Burrows's Delta and its variants, as in [stylo](https://github.com/computationalstylistics/stylo)), markers of preferred and avoided words (Zeta), Kilgarriff's chi-square distance between corpora, the Mendenhall curve and the profile of the function words as features of an author. The functions work on lists of units of a text: lower-case word forms (the usual choice for Delta), lemmas or character N-grams ([`CharNgramsExtractor`](../extractors/char_ngrams.md)) - case and lemmatization belong to [`WordsExtractor`](../extractors/words.md).

## Burrows's Delta { #delta }

A corpus is a dictionary "name of a text → units". `frequency_table` builds the table of relative frequencies: rows are the texts, columns the `n_mfw` most frequent units by descending mean relative frequency (alphabetically when equal); `culling` keeps the units that occur in at least the given share of the texts, as in stylo. `z_scores` standardizes the columns with the sample standard deviation, like `scale()` of R; a column with the same frequency in every text gives zeros. `delta` computes a symmetric matrix of distances from the z-scores (a `DataFrame` with the names of the texts), fit for clustering and PCA; at least three texts are needed - with two, the z-scores degenerate to ±1/√2 and the distances do not depend on the frequencies.

Variants (`DELTA_VARIANTS`), with the formulas of the sources of stylo; $n$ is the number of units, $z_A$ and $z_B$ the vectors of z-scores of the texts:

| Variant | Key | Formula | Source |
| :------ | :-- | :------ | :----- |
| Burrows's Delta | `burrows` | $\frac{1}{n} \sum_i \lvert z_{A,i} - z_{B,i} \rvert$ | Burrows (2002), `dist.delta` |
| Quadratic Delta | `quadratic` | $\frac{1}{n} \sqrt{\sum_i (z_{A,i} - z_{B,i})^2}$ | Argamon (2008), `dist.argamon` |
| Eder's Delta | `eder` | $\sum_i \frac{n - i + 2}{n} \lvert z_{A,i} - z_{B,i} \rvert$, $i$ - rank of the unit by frequency | Eder, `dist.eder` |
| Cosine Delta | `cosine` | $1 - \frac{z_A \cdot z_B}{\lVert z_A \rVert \lVert z_B \rVert}$ | Smith and Aldridge (2011), [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf), `dist.wurzburg` |

Cosine Delta clusters the texts by author best in the experiments of Evert et al.; Burrows's Delta is the classic choice. The usual number of units is 100 to 500 most frequent words, 100-200 for character N-grams.

Parameters of `delta`:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Units of the texts by the names of the texts |
| `n_mfw` | int | `100` | Number of the most frequent units; `None` - all of them |
| `variant` | str | `burrows` | Variant of Delta of `DELTA_VARIANTS` |
| `culling` | float | `0.0` | Smallest share of the texts a unit occurs in |

`frequency_table(corpus, n_mfw=100, culling=0.0)` takes the same parameters, `z_scores(table)` the table.

For authorship attribution there is `delta_profiles(reference, samples, n_mfw, variant, culling, statistics)`: the most frequent units, the culling and the statistics of the z-scores come from the reference texts `reference` (the profiles of the authors) or from a separate set `statistics` - for instance, from the training windows, when the profiles are joined from them and are too few to estimate the spread of the frequencies; the texts under test `samples` are described by the same units and scaled by the same statistics. The result is the distances from the texts under test to the reference ones, and the nearest reference in a row is the presumed author. Unlike `delta` over a joint vocabulary, the texts under test affect neither the list of units nor the scaling, so the result for a text does not depend on the texts passed along with it.

!!! example "Example"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import delta, delta_profiles, frequency_table

    texts = {
        "A": (
            "El gato estaba en la ventana y miraba los pájaros. "
            "Los pájaros se fueron y el gato durmió en la ventana."
        ),
        "B": "El perro estaba en el suelo y dormía. Después el perro comió y otra vez dormía en el suelo.",
        "C": "Mañana el gato volverá a la ventana y mirará los pájaros, pero el perro dormirá.",
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(text) for name, text in texts.items()}

    frequency_table(corpus, n_mfw=5).round(3)
    #       el      y     en  perro   gato
    # A  0.095  0.095  0.095  0.000  0.095
    # B  0.211  0.105  0.105  0.105  0.000
    # C  0.133  0.067  0.000  0.067  0.067

    delta(corpus, n_mfw=5).round(3)
    #        A      B      C
    # A  0.000  1.312  1.110
    # B  1.312  0.000  1.428
    # C  1.110  1.428  0.000

    delta(corpus, n_mfw=5, variant="cosine").round(3)
    #        A      B      C
    # A  0.000  1.637  1.241
    # B  1.637  0.000  1.594
    # C  1.241  1.594  0.000

    sample = {"?": we.extract("El gato despertó en la ventana y otra vez miraba los pájaros.")}
    delta_profiles(corpus, sample, n_mfw=5).round(3)
    #        A      B      C
    # ?  0.249  1.464  0.942
    ```

## Zeta { #zeta }

Markers of preferred and avoided words after Burrows (2007) and Craig and Kinney (2009). Every text of both corpora is split into segments of about `segment_size` words (the number of segments is the ratio of the length to the size rounded half up, at least one), and for a word the share of the segments of each corpus where it occurs ($DP$) is computed. Zeta is the difference of the shares $DP_{target} - DP_{comparison}$ from −1 to 1 (`zeta.craig` in the notation of stylo; the classic Zeta of Craig $DP_{target} + (1 - DP_{comparison})$ is greater by one), the logarithmic Zeta is $\log_2 \frac{DP_{target}}{DP_{comparison}}$ ([Schöch et al. 2018](https://zeta-project.eu/en/keyness-measures/burrows-zeta-logarithmic-zeta/)), a zero share replaced by half a segment. The list starts with the words the target corpus prefers and ends with the avoided ones.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `target` | list[str]/list[list[str]] | `-` | Words of the target corpus - one text or a list of texts |
| `comparison` | list[str]/list[list[str]] | `-` | Words of the comparison corpus |
| `segment_size` | int | `2000` | Size of a segment in words |
| `top_n` | int | `None` | Number of words from the start of the list; `None` - all of them |

The result is a list of `ZetaScore(word, dp_target, dp_comparison, zeta, log_zeta)` named tuples by descending Zeta, by descending logarithmic Zeta and alphabetically when equal.

!!! example "Example"

    ``` python
    from ests.corpus import zeta

    zeta(corpus["A"], corpus["B"], segment_size=5, top_n=2)
    # [ZetaScore(word='gato', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0),
    #  ZetaScore(word='la', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0)]

    zeta(corpus["A"], corpus["B"], segment_size=5)[-1]
    # ZetaScore(word='suelo', dp_target=0.0, dp_comparison=0.5, zeta=-0.5, log_zeta=-2.0)
    ```

## Kilgarriff's chi-square { #kilgarriff_chi2 }

The distance between two corpora after [Kilgarriff (2001)](https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf): for the `n_mfw` most frequent words of the joint corpus the expected frequencies in the corpora are proportional to their sizes, $\chi^2 = \sum (O - E)^2 / E$ over the words and both corpora. The greater the value, the more the corpora differ; the value grows with the size of the corpora, so pairs of corpora are comparable with each other at equal sizes, as in the experiments of Kilgarriff.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words_a` | list[str] | `-` | Words of the first corpus |
| `words_b` | list[str] | `-` | Words of the second corpus |
| `n_mfw` | int | `500` | Number of the most frequent words of the joint corpus |

!!! example "Example"

    ``` python
    from ests.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["A"], corpus["B"], n_mfw=5), 3)
    # 3.119
    ```

## Mendenhall curve { #mendenhall }

`mendenhall_curve(words)` - the shares of the words of every length in characters (Mendenhall 1887), a profile of the author comparable between texts whatever their size; `mendenhall_distance(words_a, words_b)` - the Jensen-Shannon distance with base 2 between the curves, from 0 (the distributions coincide) to 1.

!!! example "Example"

    ``` python
    from ests.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["A"]).items()}
    # {1: 0.095, 2: 0.333, 3: 0.095, 4: 0.095, 6: 0.19, 7: 0.19}

    round(mendenhall_distance(corpus["A"], corpus["B"]), 3)
    # 0.415
    ```

## Function word profile { #function_words_profile }

The shares of the adpositions, the coordinating and subordinating conjunctions, the particles, the pronouns, the determiners and the interjections (`FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) among the words of the text. Function words do not depend on the topic, so their profile is a classic feature of authorship since Mosteller and Wallace (1964).

The parts of speech are those of the annotation of a `Doc` that carries them. The words of a list or of a `Doc` without parts of speech are tagged by the model as one sequence, in their context, so they are to be passed in the order of the text; the punctuation of the list helps the tagging and is not counted. The pipeline is the model [`es_core_news_sm`](../installation.md#model) or the one passed in `nlp`, without the parser, the lemmatizer and the entity recognizer, which the parts of speech do not need; a pipeline that does not tag them (`spacy.blank("es")`) raises `SourceError`. In Spanish Universal Dependencies the negation *no* is an adverb and not a particle, so `PART` is rare.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | list[str]/Doc | `-` | Words of the text or Doc object |
| `nlp` | Language | `None` | Pipeline for a list of words; `None` - the default model |

!!! example "Example"

    ``` python
    from ests.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["A"]).items()}
    # {'ADP': 0.095, 'CCONJ': 0.095, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.048, 'DET': 0.286, 'INTJ': 0.0}
    ```
