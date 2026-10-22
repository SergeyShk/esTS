# Phonostatistics

``` {.python .signature}
PhonStats(source, words_extractor=None, window_len=3)
```

--8<-- "stats/phon_stats.md:PhonStats"

Besides the errors above, a string with a character without a UTF-8 form raises `SourceError` from the Spanish tokenizer.

The class extends the `PhonStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/phon_stats/) core with the sounds of Spanish. The sounds are those of the transcription of the words ([`transcribe`](#transcribe)), not their letters: `ch`, `ll`, `rr` and `qu` are one sound, `h` and the `u` of `que` and `gui` none, and `x` two. The pronunciation is the one of the standard of Spain: yeísmo (`ll` and `y` are one sound) and distinción (`c` before `e` and `i` and `z` are θ, apart from `s`). The classes of the sounds are the constants of `ests.constants` in the table below. The syllables are those of [`syllabify`](../syllables.md#syllabify), by the orthographic rules, and a hiatus is two vowels in two neighbouring syllables of a word (`po-e-ta`, `dí-a`, `bú-ho`). The words of a string are extracted by the Spanish [`WordsExtractor`](../extractors/words.md); without an extractor the words of a `Doc` come from its tokens. No trained model is needed. The `print_stats` table has the English descriptions of the core, `anyts.constants.PHON_STATS_DESC`.

| Class | Sounds | Constant |
| :---- | :----- | :------- |
| Vowels | a, e, i, o, u | `VOWEL_SOUNDS` |
| Sonorants | m, n, ɲ (`ñ`), l, r (the tap and the trill are one sound) | `SONORANT_SOUNDS` |
| Voiced obstruents | b (`b`, `v`), d, g, ʝ (`y`, `ll`) | `VOICED_SOUNDS` |
| Voiceless obstruents | p, t, k (`c`, `qu`, `k`), f, θ (`c`, `z`), s, x (`j`, `g`), tʃ (`ch`) | `VOICELESS_SOUNDS` |

=== "Code"

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
    ps = PhonStats(sonatina)
    ps.print_stats()
    ```

=== "Result"

    ```
                     Statistic                 |  Value
    ------------------------------------------------------
    Share of vowels                            |   0.46
    Share of sonorant consonants               |   0.19
    Share of voiced obstruents                 |   0.10
    Share of voiceless obstruents              |   0.25
    Ratio of consonants to vowels              |   1.19
    Share of clusters of 3 consonants or more  |   0.01
    Hiatuses per word                          |   0.00
    Entropy of the CV patterns of words (bits) |   3.55
    Hardness                                   |   0.39
    Alliteration index                         |   0.87
    Assonance index                            |   0.87
    Share of open syllables                    |   0.74
    Mean length of a syllable (sounds)         |   2.19
    ```

## Parameters

--8<-- "stats/phon_stats.md:PhonStats-parameters"

`PHON_WINDOW_LEN` is a constant of `anyts.constants`.

--8<-- "stats/phon_stats.md:PhonStats-check_params"

## Attributes

--8<-- "stats/phon_stats.md:PhonStats-attributes"

=== "Code"

    ``` python
    ps.syllables[:4]
    ps.sounds[:2]
    ps.c_clusters
    ps.c_syllable_patterns
    ```

=== "Result"

    ```
    (('la',), ('prin', 'ce', 'sa'), ('es', 'tá'), ('tris', 'te'))
    (('l', 'a'), ('p', 'r', 'i', 'n', 'θ', 'e', 's', 'a'))
    {1: 66, 2: 21, 3: 1}
    {'CCV': 4, 'CCVC': 5, 'CV': 60, 'CVC': 9, 'V': 5, 'VC': 10}
    ```

## Transcription { #transcribe }

``` {.python .signature}
transcribe(word)
```

Transcribes a word into its sounds, those `PhonStats` counts. The word is split into syllables ([`syllabify`](../syllables.md#syllabify)) and every syllable is read by the rules of the Spanish orthography; the characters that are no Spanish letters (digits, hyphens) are left out.

| Spelling | Sound | Example |
| :------- | :---- | :------ |
| `a`, `á`; `e`, `é`; `i`, `í`; `o`, `ó`; `u`, `ú`, `ü` | a, e, i, o, u | `canción` - k a n θ i o n |
| `h` | none; `hi` before a vowel at the start of a syllable is ʝ | `ahora` - a o r a, `hielo` - ʝ e l o |
| `ch` | tʃ | `hechizo` - e tʃ i θ o |
| `c` before `e`, `i`; `z` | θ | `cena` - θ e n a |
| `c` elsewhere, `qu` before `e`, `i`, `k` | k | `queso` - k e s o |
| `g` before `e`, `i`; `j` | x | `gente` - x e n t e |
| `g` elsewhere, `gu` before `e`, `i` | g | `guerra` - g e r a |
| `ll`; `y` before a vowel | ʝ | `calle` - k a ʝ e |
| `y` at the end of a syllable | i | `hoy` - o i |
| `r`, `rr` | r | `perro` - p e r o |
| `ñ` | ɲ | `niño` - n i ɲ o |
| `v` | b | `vaca` - b a k a |
| `x`; `x` at the start of a word | k s; s | `examen` - e k s a m e n, `xilófono` - s i l o f o n o |
| `w` | u | `whisky` - u i s k i |

The pronunciation is the one of the standard of Spain, with yeísmo and distinción. A rule reads the spelling of a word, not its history: the `x` of `México` is k s, as in `examen`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

Raises:

- `SourceTypeError` - a word that is not a string.

=== "Code"

    ``` python
    from ests.phon_stats import transcribe

    transcribe("hechizo")
    transcribe("guerrilla")
    transcribe("examen")
    ```

=== "Result"

    ```
    ('e', 'tʃ', 'i', 'θ', 'o')
    ('g', 'e', 'r', 'i', 'ʝ', 'a')
    ('e', 'k', 's', 'a', 'm', 'e', 'n')
    ```

## Metrics

--8<-- "stats/phon_stats.md:PhonStats-metrics"

The functions of the cards are imported from `ests.phon_stats`; they take words as strings and count over the sounds of their transcription.

<div class="metric-card" markdown>

### Shares of the classes of the sounds { #sound_shares }

`p_vowels` · `p_sonorants` · `p_voiced` · `p_voiceless`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-sound_shares"

</div>

<div class="metric-card" markdown>

### Ratio of the consonants to the vowels { #consonant_vowel_ratio }

`consonant_vowel_ratio`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-consonant_vowel_ratio"

</div>

<div class="metric-card" markdown>

### Consonant clusters { #consonant_clusters }

`p_heavy_clusters` · `c_clusters`
{ .metric-meta }

``` {.python .signature}
calc_consonant_clusters(text)
```

The distribution of the consonant clusters of the words by length, the attribute `c_clusters`. A cluster is a run of consonant sounds inside a word, across the syllables, a single consonant between vowels or at the edge of a word included: `instrumento` has the clusters n s t r (4), m (1) and n t (2). The digraphs are one sound (`calle`, `perro`, `chico`), and `x` is two (`extra` - k s t r). `p_heavy_clusters` is the share of the heavy clusters:

$$
\frac{\textrm{Number of clusters of 3 consonants or more}}{\textrm{Number of clusters}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

Raises:

- `SourceTypeError` - words that are not a list of strings.

=== "Code"

    ``` python
    from ests.phon_stats import calc_consonant_clusters

    calc_consonant_clusters(["instrumento", "calle"])
    ```

=== "Result"

    ```
    {1: 3, 2: 1, 4: 1}
    ```

</div>

<div class="metric-card" markdown>

### Hiatuses { #hiatus }

`p_hiatus`
{ .metric-meta }

``` {.python .signature}
calc_hiatus(text)
```

The number of hiatuses: two vowels next to each other in two syllables of a word, as [`syllabify`](../syllables.md#syllabify) splits them - `po-e-ta`, `dí-a`, `le-er`, `a-é-re-o` (two). A silent `h` between the vowels does not break the hiatus (`bú-ho`, `a-ho-ra`), and the vowels of a diphthong are one syllable and no hiatus (`cie-lo`, `ciu-dad`). `p_hiatus` is the number of hiatuses of the text per word.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

Raises:

- `SourceTypeError` - words that are not a list of strings.

=== "Code"

    ``` python
    from ests.phon_stats import calc_hiatus

    calc_hiatus(["poeta", "búho", "cielo", "aéreo"])
    ```

=== "Result"

    ```
    4
    ```

</div>

<div class="metric-card" markdown>

### Entropy of the CV patterns { #cv_entropy }

`cv_entropy`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-cv_entropy"

``` {.python .signature}
calc_cv_entropy(text)
```

The entropy of the CV patterns of a list of words: the higher it is, the more varied the phonetic shape of the words of the text. Words without sounds (numbers) are left out; `nan` for a text without other words.

``` {.python .signature}
cv_pattern(word)
```

The CV pattern of a word or a syllable: the vowels are written V and the consonants C, over the sounds of the transcription - `queso` is CVCV, `hora` VCV, `examen` VCCVCVC. A syllable is read as a word of its own, so its initial `x` is s, as at the start of a word: `xi` is CV, while the syllable `xi` of `México` counts as CCV in `PhonStats`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words (`calc_cv_entropy`) |
| `word` | `str` | - | Word or syllable (`cv_pattern`) |

Raises:

- `SourceTypeError` - words that are not a list of strings (`calc_cv_entropy`), a word that is not a string (`cv_pattern`).

=== "Code"

    ``` python
    from ests.phon_stats import calc_cv_entropy, cv_pattern

    cv_pattern("queso"), cv_pattern("examen")
    calc_cv_entropy(["poeta", "búho", "cielo", "aéreo"])
    ```

=== "Result"

    ```
    ('CVCV', 'VCCVCVC')
    1.5
    ```

</div>

<div class="metric-card" markdown>

### Hardness { #hardness }

`hardness`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-hardness"

A text of p, t, k, s and θ sounds harder than a text of vowels and m, n, l, r.

</div>

<div class="metric-card" markdown>

### Alliteration and assonance { #repetition_index }

`alliteration` · `assonance`
{ .metric-meta }

``` {.python .signature}
calc_alliteration(text, window_len=3)
```

``` {.python .signature}
calc_assonance(text, window_len=3)
```

The alliteration and assonance indices of a list of words: the repetition index `calc_repetition_index` of `anyts.phon_stats` over the consonant and over the vowel sounds of the transcription of the words. The sounds count, not the letters: `casa` and `queso` repeat k, `cena` and `casa` do not; every vowel counts, stressed or not.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `window_len` | `int` | `3` | Window in words (`PHON_WINDOW_LEN`) |

Raises:

- `SourceTypeError` - words that are not a list of strings;
- `ParameterError` - a window that is not an integer of at least 2.

--8<-- "stats/phon_stats.md:calc_repetition_index"

--8<-- "stats/phon_stats.md:calc_repetition_index-parameters"

For words in random order the indices average to 1: the 150 books of the [corpus of literature](../datasets/spanishliterature.md) with their words shuffled give 0.98 to 1.02. On the books as written the index of alliteration is a little below 1 for verse and prose alike, 0.90 to 0.99 with a median of 0.95, and the index of assonance about 1, 0.99 to 1.01: over a whole book neighbouring words share a consonant a little less often than chance. The 4,259 [sonnets](../datasets/spanishsonnets.md) give medians of 0.92 and 0.98, with a wide spread over such short texts (0.59 to 1.30 for alliteration). The repetitions of a poem are local, and the places where they gather are shown by the layer `alliteration` of the [highlighting](../visualizers/highlight.md).

=== "Code"

    ``` python
    from ests.phon_stats import calc_alliteration, calc_assonance

    # Garcilaso de la Vega, Égloga III
    words = "en el silencio sólo se escuchaba un susurro de abejas que sonaba".split()
    calc_alliteration(words), calc_assonance(words)
    ```

=== "Result"

    ```
    (1.0232558139534884, 1.115942028985507)
    ```

</div>

<div class="metric-card" markdown>

### Syllables { #syllables }

`p_open_syllables` · `mean_syllable_len`
{ .metric-meta }

--8<-- "stats/phon_stats.md:PhonStats-syllables"

The sounds of a syllable are its transcription, the first syllable of a word read as the start of the word: the `xi` of `xilófono` is s i, the `xi` of `México` k s i.

``` {.python .signature}
is_open_syllable(syllable)
```

Checks whether a syllable is open: an open syllable ends in a vowel sound - `ca`, `que`, `hoy` (the final `y` is the vowel i); `car` and `pan` are closed. The syllable is read as a word of its own.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `syllable` | `str` | - | Syllable |

Raises:

- `SourceTypeError` - a syllable that is not a string.

=== "Code"

    ``` python
    from ests.phon_stats import is_open_syllable

    is_open_syllable("hoy"), is_open_syllable("car")
    ```

=== "Result"

    ```
    (True, False)
    ```

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the phonostatistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    from ests import PhonStats

    PhonStats("Tres tristes tigres tragaban trigo en un trigal").get_stats()
    ```

=== "Result"

    ```
    {'p_vowels': 0.35,
     'p_sonorants': 0.25,
     'p_voiced': 0.125,
     'p_voiceless': 0.275,
     'consonant_vowel_ratio': 1.8571428571428572,
     'p_heavy_clusters': 0.0,
     'p_hiatus': 0.0,
     'cv_entropy': 2.75,
     'hardness': 0.4583333333333333,
     'alliteration': 0.9333333333333333,
     'assonance': 0.7526881720430108,
     'p_open_syllables': 0.42857142857142855,
     'mean_syllable_len': 2.857142857142857}
    ```
