# Statistic functions

## Transcription { #transcribe }

!!! info ""
    **ests.phon_stats.transcribe()**

Transcribes a word into its sounds. The word is split into syllables ([`syllabify`](../syllables.md)) and every syllable is read by the rules of the Spanish orthography; the characters that are no Spanish letters (digits, hyphens) are left out, and the results are cached by word form.

| Spelling | Sound | Example |
| :------- | :---: | :------ |
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

!!! example "Example"

    ``` python
    from ests.phon_stats import transcribe

    transcribe("hechizo"), transcribe("guerrilla"), transcribe("examen")
    # (('e', 'tʃ', 'i', 'θ', 'o'), ('g', 'e', 'r', 'i', 'ʝ', 'a'),
    #  ('e', 'k', 's', 'a', 'm', 'e', 'n'))
    ```

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## CV pattern { #cv_pattern }

!!! info ""
    **ests.phon_stats.cv_pattern()**

The CV pattern of a word or a syllable: the vowels are written V and the consonants C, over the sounds of the transcription - `queso` is CVCV, `hora` VCV, `examen` VCCVCVC.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `sounds` | tuple[str] | `-` | Sounds of a word or a syllable |

## Open syllable { #is_open_syllable }

!!! info ""
    **ests.phon_stats.is_open_syllable()**

Checks whether a syllable is open: an open syllable ends in a vowel sound - `ca`, `que`, `hoy` (the final `y` is the vowel i); `car` and `pan` are closed.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `syllable` | tuple[str] | `-` | Sounds of the syllable |

## Consonant clusters { #calc_consonant_clusters }

!!! info ""
    **ests.phon_stats.calc_consonant_clusters()**

The distribution of the consonant clusters by length. A cluster is a run of consonant sounds inside a word, across the syllables: `instrumento` has the clusters n s t r (4), m (1) and n t (2). The clusters of length 1 are the single consonants between vowels or at the edges of a word. The digraphs are one sound (`calle`, `perro`, `chico`), and `x` is two (`extra` - k s t r).

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Hiatuses { #calc_hiatus }

!!! info ""
    **ests.phon_stats.calc_hiatus()**

The number of hiatuses: two vowels next to each other in two syllables of a word, as [`syllabify`](../syllables.md) splits them - `po-e-ta`, `dí-a`, `le-er`, `a-é-re-o` (two). A silent `h` between the vowels does not break the hiatus (`bú-ho`, `a-ho-ra`), and the vowels of a diphthong are one syllable and no hiatus (`cie-lo`, `ciu-dad`).

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Entropy of the CV patterns { #calc_cv_entropy }

!!! info ""
    **ests.phon_stats.calc_cv_entropy()**

The Shannon entropy of the distribution of the words by CV pattern in bits: the higher it is, the more varied the phonetic shape of the words of the text. Words without sounds (numbers) are left out; `nan` for a text without them.

$$
H = -\sum_{k} p_k \log_2 p_k
$$

where $p_k$ is the share of the words with the CV pattern $k$.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Hardness { #hardness }

The ratio of the voiceless obstruents to the vowels and the sonorants: a text of p, t, k, s and θ sounds harder than a text of vowels and m, n, l, r.

$$
\frac{n_{voiceless}}{n_{vowels} + n_{sonorants}}
$$

## Alliteration index { #calc_alliteration }

!!! info ""
    **ests.phon_stats.calc_alliteration()**

The ratio of the observed number of windows of `window_len` neighbouring words where one consonant sound occurs in two words or more to the number expected if the consonants were spread over the words at random, summed over the consonants. The expected number comes from the frequencies of the consonants in the text itself, so the index tells whether the repetitions cluster in neighbouring words, not how frequent a sound is: about 1 - the repetitions are random, well above 1 - alliteration. The consonants are the sounds of the transcription, so `casa` and `queso` repeat k, and `cena` and `casa` do not; `nan` for a text shorter than the window.

$$
\frac{\sum_c O_c}{\sum_c (W - w + 1) \left(1 - (1 - p_c)^w - w p_c (1 - p_c)^{w - 1}\right)}
$$

where $O_c$ is the number of windows with the consonant $c$ in two words or more, $W$ the number of words, $w$ the window and $p_c$ the share of the words with the consonant $c$.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `window_len` | int | `3` | Window in words |

## Assonance index { #calc_assonance }

!!! info ""
    **ests.phon_stats.calc_assonance()**

The same ratio over the vowels: the observed number of windows of `window_len` neighbouring words where one vowel occurs in two words or more against the number expected by the frequencies of the vowels in the text. Every vowel counts, stressed or not; `nan` for a text shorter than the window.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `window_len` | int | `3` | Window in words |
