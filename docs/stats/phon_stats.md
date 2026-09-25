# Phonostatistics

!!! info ""
    **ests.phon_stats.PhonStats**

## Description

A module for computing the phonostatistics of a text: the shares of the classes of sounds, the consonant clusters, the hiatuses, the variety of the phonetic shape of the words, the open syllables, and the indices of alliteration and assonance, which tell whether the repetitions of a sound gather in neighbouring words. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library; no trained model is needed.

The statistics are counted over the sounds of the transcription of the words ([`transcribe`](phon_stats_funcs.md#transcribe)), not over the letters: Spanish writes some sounds with two letters (`ch`, `ll`, `rr`, `qu`), some letters with no sound (`h`, the `u` of `que` and `gui`) and one letter for two sounds (`x`), so a count of letters would make `calle` a cluster of two consonants and `queso` a word of three vowels. The spelling of Spanish is regular enough to be read by rules, without a dictionary. The pronunciation is the one of the standard of Spain: yeísmo (`ll` and `y` are one sound) and distinción (`c` before `e` and `i` and `z` are θ, apart from `s`).

| Class | Sounds |
| :---- | :----- |
| Vowels | a, e, i, o, u |
| Sonorants | m, n, ɲ (`ñ`), l, r (the tap and the trill are one sound) |
| Voiced obstruents | b (`b`, `v`), d, g, ʝ (`y`, `ll`) |
| Voiceless obstruents | p, t, k (`c`, `qu`, `k`), f, θ (`c`, `z`), s, x (`j`, `g`), tʃ (`ch`) |

The syllables are the ones of [`syllabify`](../syllables.md), by the orthographic rules, and a hiatus is two vowels in two neighbouring syllables of a word (`po-e-ta`, `dí-a`, `bú-ho`).

!!! note "Note"
    The statistics are computed when the `PhonStats` object is made. The statistics and the functions that compute them are described in the corresponding [section](phon_stats_funcs.md).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `window_len` | int | `3` | Window in words for the alliteration and the assonance |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of the extracted words in lower case |
| `syllables` | tuple[tuple[str]] | Tuple of the syllables of every word |
| `sounds` | tuple[tuple[str]] | Tuple of the sounds of every word |
| `n_vowels` | int | Number of vowels |
| `n_consonants` | int | Number of consonants |
| `n_sonorants` | int | Number of sonorant consonants |
| `n_voiced` | int | Number of voiced obstruents |
| `n_voiceless` | int | Number of voiceless obstruents |
| `c_clusters` | dict[int, int] | Distribution of the consonant clusters by length |
| `c_syllable_patterns` | dict[str, int] | Distribution of the syllables by CV pattern |
| `p_vowels` | float | Share of vowels among the sounds |
| `p_sonorants` | float | Share of sonorant consonants among the sounds |
| `p_voiced` | float | Share of voiced obstruents among the sounds |
| `p_voiceless` | float | Share of voiceless obstruents among the sounds |
| `consonant_vowel_ratio` | float | Ratio of consonants to vowels |
| `p_heavy_clusters` | float | Share of the clusters of 3 consonants or more |
| `p_hiatus` | float | Hiatuses per word |
| `cv_entropy` | float | Entropy of the CV patterns of the words in bits |
| `hardness` | float | Ratio of the voiceless obstruents to the vowels and the sonorants |
| `alliteration` | float | Alliteration index |
| `assonance` | float | Assonance index |
| `p_open_syllables` | float | Share of open syllables |
| `mean_syllable_len` | float | Mean length of a syllable in sounds |

## Methods

### get_stats

Returns a dictionary with the computed phonostatistics.

!!! example "Example"

    ``` python
    from ests import PhonStats

    ps = PhonStats("Tres tristes tigres tragaban trigo en un trigal")
    ps.get_stats()
    # {'p_vowels': 0.35,
    #  'p_sonorants': 0.25,
    #  'p_voiced': 0.125,
    #  'p_voiceless': 0.275,
    #  'consonant_vowel_ratio': 1.8571428571428572,
    #  'p_heavy_clusters': 0.0,
    #  'p_hiatus': 0.0,
    #  'cv_entropy': 2.75,
    #  'hardness': 0.4583333333333333,
    #  'alliteration': 0.9175627240143369,
    #  'assonance': 0.6708595387840671,
    #  'p_open_syllables': 0.42857142857142855,
    #  'mean_syllable_len': 2.857142857142857}

    ps.syllables[:3], ps.sounds[:2]
    # ((('tres',), ('tris', 'tes'), ('ti', 'gres')),
    #  (('t', 'r', 'e', 's'), ('t', 'r', 'i', 's', 't', 'e', 's')))
    ```

### print_stats

Prints a table with the computed phonostatistics.

!!! example "Example"

    _Code_:

    ``` python
    from ests import PhonStats

    # The first stanza of Sonatina by Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    PhonStats(sonatina).print_stats()
    ```

    _Result_:

    ``` bash
                      Statistic                   |  Value
    --------------------------------------------------------
    Share of vowels                               |   0.46
    Share of sonorant consonants                  |   0.19
    Share of voiced obstruents                    |   0.10
    Share of voiceless obstruents                 |   0.25
    Ratio of consonants to vowels                 |   1.19
    Share of clusters of 3 consonants or more     |   0.01
    Hiatuses per word                             |   0.00
    Entropy of the CV patterns of words (bits)    |   3.55
    Hardness                                      |   0.39
    Alliteration index                            |   0.83
    Assonance index                               |   0.86
    Share of open syllables                       |   0.74
    Mean length of a syllable (sounds)            |   2.19
    ```

The indices of alliteration and assonance compare the repetitions with the ones expected from the frequencies of the sounds of the text itself, so they tell whether a text gathers its repetitions in neighbouring words. Over a whole book they come near 1 for verse and for prose alike (0.95-0.98 for *Prosas profanas*, the poems of Machado, *En las orillas del Sar*, *Marianela* and *Niebla* in the [corpus of literature](../datasets/spanishliterature.md)): the repetitions of a poem are local, and the places where they gather are shown by the layer `alliteration` of the [highlighting](../visualizers/highlight.md).
