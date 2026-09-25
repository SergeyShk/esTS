# Syllables and stress

!!! info ""
    **ests.syllables**

## Description

A module that divides a Spanish word into syllables and finds its stressed syllable from the spelling alone. Spanish orthography encodes both: syllable boundaries follow from the vowels and consonant clusters, and the stress follows from the written accent or, without one, from the ending of the word. No dictionary or trained model is needed. The functions are the foundation of the basic statistics (syllable counts), readability formulas, phonostatistics and metre.

The rules follow the *Ortografía de la lengua española* (RAE, 2010). Two conventions are worth knowing: two weak vowels always form a diphthong, as the spelling rules require (`huir`, `cons-truir`, `je-sui-ta`, `guion` are one syllable shorter than in some phonetic syllabifiers), and `tl` is split as in Spain (`at-las`).

## Syllabification { #syllabify }

!!! info ""
    **ests.syllables.syllabify()**

Division of a word into syllables. A syllable is built around a vowel nucleus: a single vowel, a diphthong or a triphthong.

| Rule | Example |
| :--- | :-----: |
| a weak vowel (unaccented `i`, `u`, `ü`) next to another vowel forms a diphthong | ai-re, puen-te, rui-do, ciu-dad |
| two strong vowels form a hiatus, as do two close vowels of the same letter, with or without a tilde | po-e-ta, le-er, a-é-re-o, chi-i-ta, chi-í-es |
| an accented weak vowel is strong | dí-a, pa-ís, ba-úl |
| a weak vowel between two others gives a triphthong | a-ve-ri-guáis, buey |
| a weak vowel before a strong one goes with that vowel | chi-hua-hua, ca-ca-hue-te |
| an `h` between vowels does not break a diphthong | ahu-ma-do, prohi-bir, de-sahu-cio |
| the `u` of `qu`, and of `gu` before `e` and `i`, is silent; `ü` is a vowel | que-so, gue-rra, pin-güi-no |
| `y` is a vowel at the end of a word and a consonant before a vowel | rey, U-ru-guay, ma-yo |
| a single consonant or digraph goes to the next syllable | ca-sa, mu-cho, pe-rro |
| an obstruent with `l` or `r` goes to the next syllable | ha-blar, o-tro |
| other consonant pairs are split | ac-to, is-la, at-las, rit-mo |
| of three or more consonants the last two go to the next syllable when they form such a cluster, otherwise only the last one does | com-pra, cons-truir, ins-ti-tu-to, obs-tá-cu-lo, tungs-te-no |

The word is normalized to NFC (a decomposed accent becomes one letter with its base) and lower-cased. It is split into parts at digits, hyphens and other non-letters, each part is syllabified on its own (`te-ó-ri-co-prác-ti-co`), and a part without vowels (an abbreviation like `sh`) yields no syllables. Vowels with foreign diacritics count as accented strong vowels (`Björk`). A diaeresis marks a hiatus: the `ü` of verse outside `gü` and `qü` and the `ï` (`sü-a-ve`, `rü-i-do`, `glo-rï-o-sa`, `Llu-ï-sa`), which leave the stress to the rules of the word, and the `ë` of French (`Ci-tro-ën`), which takes it; the Portuguese `ão` and `õe` are diphthongs (`São`, `Ca-mões`).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ests.syllables import syllabify

    syllabify("murciélago")
    # ['mur', 'cié', 'la', 'go']

    syllabify("averiguáis")
    # ['a', 've', 'ri', 'guáis']
    ```

## Syllable count { #count_syllables }

!!! info ""
    **ests.syllables.count_syllables()**

The number of syllables by `syllabify`, cached by word form.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ests.syllables import count_syllables

    count_syllables("Uruguay")
    # 3
    ```

## Word stress { #word_stress }

!!! info ""
    **ests.syllables.word_stress()**

The index of the stressed syllable, counted from zero as in `syllabify`; `None` for a word without vowels.

| Rule | Example |
| :--- | :-----: |
| a written accent marks the stressed syllable | ca-**mión**, **ár**-bol, mur-**cié**-la-go |
| a word ending in a vowel, in `n` or `s` after a vowel, or in `y` after a consonant is stressed on the penultimate syllable | **ca**-sa, **jo**-ven, **lu**-nes, **whis**-ky |
| any other word is stressed on the last syllable | pa-**pel**, re-**loj**, ro-**bots**, U-ru-**guay** |
| a monosyllable is stressed on its only syllable | rey, y |

Enclitic pronouns need no special treatment: their forms carry the accent by the same rules (`dí-ga-me-lo`, `de-cír-se-lo`). For an adverb in `-mente` and for a hyphenated compound the main stress is the last of `word_stresses` (`fá-cil-men-te` - 2).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ests.syllables import word_stress

    word_stress("camión"), word_stress("casa"), word_stress("murciélago")
    # (1, 0, 1)
    ```

## All stresses { #word_stresses }

!!! info ""
    **ests.syllables.word_stresses()**

All stressed syllables of a word in ascending order. A single index for most words. Two indices for an adverb in `-mente`, which keeps the stress of its adjective (`fá-cil-men-te` - 0 and 2, `fe-liz-men-te` - 1 and 2), and one index per part of a hyphenated compound (`te-ó-ri-co-prác-ti-co` - 1 and 4).

An adverb is recognized by its shape: a stem of at least one syllable before `-mente` that ends like an adjective (in a vowel, `l`, `r`, `z`, `n` or `s`) or carries an accent, so `cruel-men-te` counts too. Words of the same shape that are not adverbs are listed in `NON_ADVERBS_MENTE`: adjectives and nouns (`demente`, `vehemente`) and subjunctives of verbs in `-mentar` (`fundamente`, `complemente`); an unlisted subjunctive of that kind gets a second stress.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ests.syllables import word_stresses

    word_stresses("fácilmente")
    # [0, 2]
    ```

## Stress type { #stress_type }

!!! info ""
    **ests.syllables.stress_type()**

The class of a word by the position of its main stress: `aguda` on the last syllable (`ca-mión`), `llana` on the penultimate (`ca-sa`), `esdrújula` on the antepenultimate (`mur-cié-la-go`), `sobresdrújula` earlier (`dí-ga-me-lo`); `None` for a word without vowels.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

!!! example "Example"

    ``` python
    from ests.syllables import stress_type

    stress_type("dígamelo")
    # 'sobresdrújula'
    ```
