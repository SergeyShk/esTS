# Stylometry

!!! info ""
    **ests.corpus.delta()**, **ests.corpus.delta_profiles()**, **ests.corpus.frequency_table()**, **ests.corpus.z_scores()**, **ests.corpus.zeta()**, **ests.corpus.kilgarriff_chi2()**, **ests.corpus.mendenhall_curve()**, **ests.corpus.mendenhall_distance()**, **ests.corpus.function_words_profile()**

## Description

--8<-- "corpus/stylometry.md:stylometry"

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/stylometry/) core, with the [profile of the function words](#function_words_profile) of Spanish added as a feature of an author. The units of a text come from [`WordsExtractor`](../extractors/words.md) - word forms and lemmas - and [`CharNgramsExtractor`](../extractors/char_ngrams.md).

## Burrows's Delta { #delta }

--8<-- "corpus/stylometry.md:frequency_table"

--8<-- "corpus/stylometry.md:z_scores"

--8<-- "corpus/stylometry.md:delta"

--8<-- "corpus/stylometry.md:delta_profiles"

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

--8<-- "corpus/stylometry.md:zeta"

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

--8<-- "corpus/stylometry.md:kilgarriff_chi2"

!!! example "Example"

    ``` python
    from ests.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["A"], corpus["B"], n_mfw=5), 3)
    # 3.119
    ```

## Mendenhall curve { #mendenhall }

--8<-- "corpus/stylometry.md:mendenhall_curve"

--8<-- "corpus/stylometry.md:mendenhall_distance"

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

The parts of speech are those of the annotation of a `Doc` that carries them. The words of a list or of a `Doc` without parts of speech are tagged by the model in their context, so they are to be passed in the order of the text; the punctuation of the list helps the tagging and is not counted. The pipeline is the model [`es_core_news_sm`](../installation.md#model) or the one passed in `nlp`, without the parser, the lemmatizer and the entity recognizer; a pipeline that does not tag them (`spacy.blank("es")`) raises `SourceError`. In Spanish Universal Dependencies the negation *no* is an adverb and not a particle, so `PART` is rare.

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
