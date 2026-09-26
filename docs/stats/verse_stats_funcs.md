# Statistic functions

## Algorithm { #algorithm }

A line of Spanish verse is measured by its metrical syllables, which are not the syllables of its words one by one:

1.  **Syllables and stresses.** Every word is split into syllables by [`syllabify`](../syllables.md) and stressed by the orthographic rules of [`word_stresses`](../syllables.md#word_stresses); an adverb in `-mente` has two stresses. The unstressed words of the verse (`VERSE_PROCLITICS`) take no stress: the articles, the prepositions except `según`, the conjunctions, the relatives (`que`, `cual`, `donde`, `como`, `cuanto`), the clitic pronouns (`me`, `te`, `se`, `le`, `nos`), the possessives before a noun (`mi`, `tu`, `su`, `nuestro`, `vuestro`), the titles before a name (`don`, `fray`, `san`), `tan`, `aun` and the interjections `oh`, `ay`, `ah`. The last word of a line is always stressed.
2.  **The plain reading.** The final vowel of a word and the first one of the next make one syllable - a synalepha (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). A silent `h` lets it through (*oh‿al-ma*), while `hi` and `hu` before a vowel (*hierba*, *hueso*) and `y` before a vowel (*ya*, *yo*) are consonants and stop it; a consonant at the end of a word stops it too (*el | al-ma*).
3.  **The law of the final stress.** A line counts up to its last stressed syllable and one syllable more: a line that ends in an aguda gets a syllable (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), a line that ends in an esdrújula loses one (*el pá-ja-ro* - 3).
4.  **The meter.** The meter of a poem is the length of most plain readings; on a tie from three lines up, the tied length with a name that leaves the fewest lines off it wins. Every line is fitted to it with the fewest changes of its plain reading: a longer line joins two vowels of a hiatus in a word - a synaeresis (*poe-ta*), the ones with an accented `i` or `u` (*dí-a*) last; a shorter line breaks its synalephas from the end of the line - a hiatus, then splits a diphthong of a stressed syllable - a dieresis (*su-a-ve*, *ru-i-do*). A written diaeresis marks a hiatus (*sü-a-ve*) that no synaeresis joins. A line that cannot reach the meter keeps its plain reading and counts as off it. A poem without a meter fits its lines to its common lengths instead, if they take more than half of the lines.
5.  **Compound verse.** A compound verse of two equal hemistichs (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) is tried when more than half of the plain readings split into its hemistichs and its length equals the one of most lines or is one syllable off it; the reading with fewer lines off the meter wins, the compound verse on a tie. The caesura falls after a stressed word and blocks the synalepha, and each hemistich follows the law of the final stress on its own: the alejandrino *La princesa está pálida | en su silla de oro* is 7 + 7.

On the 60,209 lines of the 4,259 sonnets of [SpanishSonnets](../datasets/spanishsonnets.md), the length of a line agrees with the automatic scansion of DISCO in 97.0% of the lines and with [rantanplan](https://github.com/linhd-postdata/rantanplan) in 97.7%, and the stress of a metrical syllable of the lines of equal length in 97.4% and 99.6%.

The rhyme is described in the [module](verse_stats.md#rhyme). Against the automatic rhyme of DISCO (RhymeTagger), 99.1% of the pairs of rhyming lines we find are its pairs, and we find 97.9% of its pairs.

## Accentuation { #accentuate }

!!! info ""
    **ests.verse_stats.accentuate()**

Marks the stresses of a text by the orthographic rules: an acute accent (U+0301) is put after the stressed vowel of every word without a written accent, both stresses of an adverb in `-mente` and of a hyphenated compound; the unstressed words of the verse (`VERSE_PROCLITICS`) stay unmarked. The text is normalized to NFC. For the lines of a poem, where the last word is always stressed, the method [`VerseStats.accentuate`](verse_stats.md#accentuate) serves.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text |

!!! example "Example"

    ``` python
    import unicodedata
    from ests.verse_stats import accentuate

    text = "Yo soy aquel que ayer no más decía el verso azul y la canción profana"
    unicodedata.normalize("NFC", accentuate(text))
    # 'Yó sóy aquél que ayér nó más decía el vérso azúl y la canción profána'
    ```

## Meter { #detect_meter }

!!! info ""
    **ests.verse_stats.detect_meter()**

Detects the meter of a poem: the name of the verse by its metrical syllables (`octosílabo`, `endecasílabo`, `alejandrino`...), or `None` if more than a tenth of the lines have another length or the text has a single line.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of a poem |

!!! example "Example"

    ``` python
    from ests.verse_stats import detect_meter

    # The beginning of the Romance del prisionero
    detect_meter(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    # 'octosílabo'
    ```

## Rhyme scheme { #rhyme_scheme }

!!! info ""
    **ests.verse_stats.rhyme_scheme()**

Detects the rhyme scheme of a poem: the schemes of the stanzas separated by spaces, the letters in the order of the rhyme groups of the poem, upper-case for the lines of arte mayor and lower-case for the lines of arte menor, unrhymed lines as a hyphen.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of a poem |
| `seseo` | bool | `False` | Pronounce `c` and `z` before `e` and `i` as `s` in the rhyme |

!!! example "Example"

    ``` python
    from ests.verse_stats import rhyme_scheme

    # Sor Juana Inés de la Cruz
    rhyme_scheme(
        "Hombres necios que acusáis\na la mujer sin razón,\nsin ver que sois la ocasión\nde lo mismo que culpáis."
    )
    # 'abba'
    ```

## Stanzas { #split_stanzas }

!!! info ""
    **ests.verse_stats.split_stanzas()**

Splits a text into stanzas and lines: the stanzas are separated by blank lines, and the lines without a Spanish syllable (numbers, asterisks, other alphabets) are left out. The text is normalized to NFC.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text of a poem |

!!! example "Example"

    ``` python
    from ests.verse_stats import split_stanzas

    split_stanzas(
        "Cuando me paro a contemplar mi estado\n"
        "y a ver los pasos por do me han traído,\n\n* * *\n\n"
        "hallo, según por do anduve perdido,"
    )
    # [['Cuando me paro a contemplar mi estado', 'y a ver los pasos por do me han traído,'],
    #  ['hallo, según por do anduve perdido,']]
    ```
