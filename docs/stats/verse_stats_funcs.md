# Statistic functions

## Algorithm { #algorithm }

A line of Spanish verse is measured by its metrical syllables, which are not the syllables of its words one by one:

1.  **Syllables and stresses.** Every word is split into syllables by [`syllabify`](../syllables.md) and stressed by [`word_stresses`](../syllables.md#word_stresses): a written accent marks the stress, otherwise the orthographic rules (llana after a vowel, `n` or `s`, aguda after another consonant); an adverb in `-mente` has two stresses. The unstressed words of the verse (`VERSE_PROCLITICS`) take no stress: the articles, the prepositions except `según`, the conjunctions, the relatives (`que`, `cual`, `donde`, `como`, `cuanto`), the clitic pronouns (`me`, `te`, `se`, `le`, `nos`), the possessives before a noun (`mi`, `tu`, `su`, `nuestro`, `vuestro`), the titles before a name (`don`, `fray`, `san`), `tan`, `aun`, and the interjections `oh`, `ay`, `ah`, which the scansions of DISCO and rantanplan leave unstressed as well. The last word of a line is always stressed.
2.  **The plain reading.** The final vowel of a word and the first one of the next make one syllable - a synalepha (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). A silent `h` lets it through (*oh‿al-ma*), while `hi` and `hu` before a vowel (*hierba*, *hueso*) and `y` before a vowel (*ya*, *yo*) are consonants and stop it; a consonant at the end of a word stops it too (*el | al-ma*).
3.  **The law of the final stress.** A line counts up to its last stressed syllable and one syllable more: a line that ends in an aguda gets a syllable (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), a line that ends in an esdrújula loses one (*el pá-ja-ro* - 3).
4.  **The meter.** The meter of a poem is the length of most plain readings; on a tie from three lines up every tied length with a name is tried (a line of prose of 40 syllables gives no meter anyway), and the one with the fewest lines off it wins (a quatrain of two lines of 10 and two of 11 syllables in the plain reading is a quatrain of endecasílabos). Every line is fitted to it with the fewest changes of its plain reading: a longer line joins two vowels of a hiatus in a word - a synaeresis (*poe-ta*), the ones with an accented `i` or `u` (*dí-a*) last; a shorter line breaks its synalephas from the end of the line - a hiatus, then splits a diphthong of a stressed syllable - a dieresis (*su-a-ve*, *ru-i-do*, *con-fi-a-do*). A written diaeresis is the poet's mark of a hiatus (*sü-a-ve*, *glo-rï-o-sa*), and no synaeresis joins it. A line that cannot reach the meter keeps its plain reading and counts as off it. A poem without a meter fits its lines to its common lengths instead (the 7 and the 11 syllables of a lira), if they take more than half of the lines.
5.  **Compound verse.** A compound verse of two equal hemistichs (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) is tried when more than half of the plain readings split into its hemistichs and its length is one syllable off the one of most lines or equal to it; the reading with fewer lines off the meter wins, the compound verse on a tie. The caesura falls after a stressed word, blocks the synalepha, and each hemistich follows the law of the final stress on its own: the alejandrino *La princesa está pálida | en su silla de oro* is 7 + 7, the esdrújula before the caesura losing a syllable and the hiatus *de | oro* giving one.

The accuracy was checked on the 60,209 lines of the 4,259 sonnets of [SpanishSonnets](../datasets/spanishsonnets.md), against the automatic scansion of DISCO and against the one of [rantanplan](https://github.com/linhd-postdata/rantanplan) (run apart: it needs spaCy 2.2.4, which runs on Python 3.8 at most). The length of a line agrees with DISCO in 97.0% of the lines and with rantanplan in 97.7%, the stress of a metrical syllable of the lines of equal length in 97.4% and 99.6%, the whole pattern of a line in 77% and 96%. On the lines of simple verse the lengths agree in 98.2% and 99.1%; most of the rest are alejandrinos, which both count as simple verse, without the hemistichs. Most of the other differences with DISCO are its own choices: it stresses the clitic pronouns `me`, `te` and `le` in 84% of their occurrences and `tan` in 96%, and it gives the words with an enclitic `-os` (*encareceros*, *quereros*) a second stress and a syllable too many.

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
