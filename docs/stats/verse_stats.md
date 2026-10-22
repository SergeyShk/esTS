# Verse statistics

``` {.python .signature}
VerseStats(source, seseo=False)
```

The verse statistics of a text: the scansion of the lines, the meter and the number of metrical syllables, the rhythmic stresses and the stress profile, the types of the endecasílabo, the endings of the lines, the rhyme, its scheme and the strophes. The data source is a text with its line breaks or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library; the statistics are computed when the object is created, and no trained model and no dictionary are needed.

The meter of Spanish verse is syllabic: a line is measured by its metrical syllables, and the stresses shape its rhythm. The text is split into lines and stanzas (by blank lines), the words are split into syllables and stressed by [`syllabify`](../syllables.md) and [`word_stresses`](../syllables.md#word_stresses), and the syllables of a line are counted with the synalephas and the law of the final stress; a compound verse, the alejandrino above all, is read as two hemistichs ([algorithm](#algorithm)). A text with letters but without Spanish syllables (another alphabet) gives empty statistics - `n_lines` 0, meter `None`, shares `nan`.

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`;
- `SourceError` - a source without letters (empty, digits and punctuation only).

=== "Code"

    ``` python
    from ests import VerseStats

    # The beginning of the sonnet I by Garcilaso de la Vega
    text = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado."""

    vs = VerseStats(text)
    vs.print_stats()
    ```

=== "Result"

    ```
                      Statistic                   |    Value
    ------------------------------------------------------------
    Number of lines                               |      4
    Number of stanzas                             |      1
    Meter                                         | endecasílabo
    Number of metrical syllables                  |      11
    Share of lines off the meter                  |     0.00
    Share of lines without the rhythmic stresses  |     0.00
    Share of rhymed lines                         |     1.00
    Share of oxytone endings (aguda)              |     0.00
    Share of paroxytone endings (llana)           |     1.00
    Share of proparoxytone endings (esdrújula)    |     0.00
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `seseo` | `bool` | `False` | Pronounce `c` and `z` before `e` and `i` as `s` in the rhyme, as in Andalusia and in America: `voz` - `dos` |

## Attributes

| Attribute | Type | Description |
| :-------- | :--- | :---------- |
| `lines` | `tuple[str]` | Lines with Spanish words |
| `stanzas` | `tuple[tuple[str, ...], ...]` | Lines by stanza |
| `syllables` | `tuple[tuple[str, ...], ...]` | Syllables of every line as the verse reads them, a synalepha marked with `‿` |
| `stresses` | `tuple[tuple[int, ...], ...]` | Indices of the stressed syllables of every line in `syllables`, from zero |
| `caesuras` | `tuple[int / None, ...]` | Index of the first syllable of the second hemistich of every line in `syllables`, `None` for a simple verse |
| `patterns` | `tuple[str, ...]` | Patterns of the lines of `+` (a stressed metrical syllable) and `-` (an unstressed one), as long as the line in metrical syllables |
| `mean_line_len` | `float` | Mean length of a line in metrical syllables |
| `c_stressed_vowels` | `dict[str, int]` | Distribution of the stressed vowels |
| `seseo` | `bool` | Whether the rhyme is read with seseo |

`stresses` indexes `syllables`, and the two agree with `patterns` up to the last stress of a simple verse; in a [compound verse](#meter) each hemistich takes its own length, so after an aguda or an esdrújula at the caesura `patterns` and `syllables` part, and `caesuras` tells where the second hemistich begins.

=== "Code"

    ``` python
    vs.syllables[1]
    vs.patterns
    vs.stresses[0]
    vs.c_stressed_vowels
    ```

=== "Result"

    ```
    ('y‿a', 'ver', 'los', 'pa', 'sos', 'por', 'do', 'me‿han', 'tra', 'í', 'do')
    ('---+---+-+-', '-+-+---+-+-', '+--+--+--+-', '--++-+-+-+-')
    (3, 7, 9)
    {'a': 8, 'e': 3, 'i': 2, 'u': 2, 'o': 1}
    ```

## Metrics

Every metric is an attribute of the object, computed when it is created, and `get_stats` gives them all.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| `n_lines`, `n_stanzas` | Number of the lines with Spanish words and of the stanzas | 0 and above | A longer text |
| [`meter`](#meter) | Syllabic meter: the name of the verse by its metrical syllables | `bisílabo` to `octodecasílabo` (`VERSE_METERS`), `None` without a meter | - |
| [`n_feet`](#meter) | Metrical syllables of the meter | 2-18, `None` without a meter | Longer lines |
| [`p_deviations`](#meter) | Share of the lines off the meter | 0-0.1, `nan` without a meter | More lines off the meter |
| [`p_pyrrhics`](#pyrrhics) | Share of the lines of the meter without its rhythmic stresses | 0-1, `nan` without a meter | More lines without the rhythmic stresses |
| [`p_rhymed`](#rhyme_scheme) | Share of the rhymed lines | 0-1, `nan` without lines | More rhymes |
| [`p_masculine`](#clausulas), [`p_feminine`](#clausulas), [`p_dactylic`](#clausulas) | Shares of the endings aguda, llana and esdrújula | 0-1, `nan` without lines | More endings of the type |

<div class="metric-card" markdown>

### Meter and metrical syllables { #meter }

`meter` · `n_feet` · `c_feet` · `p_deviations` · Quilis, 1984
{ .metric-meta }

``` {.python .signature}
detect_meter(text)
```

The meter of a poem by the [algorithm](#algorithm): the name of the verse by its metrical syllables - `octosílabo`, `endecasílabo`, `alejandrino`... (`VERSE_METERS`), and `n_feet` its number of metrical syllables. `c_feet` is the distribution of the lines by metrical syllables, and `p_deviations` the share of the lines off the meter.

The meter is the length of most lines, and it is not determined (`None`) if more than a tenth of the lines (`VERSE_MAX_DEVIATIONS`) stay off it after the fitting - a polymetric poem (a silva, a sonnet with an estrambote of heptasílabos), free verse, prose - or if the text has a single line (`VERSE_MIN_LINES`). The lines of a poem without a meter are fitted to its common lengths - the ones of at least two lines and a tenth of them, as the 7 and the 11 syllables of a lira or a silva - if these take more than half of the lines; otherwise, as in free verse and prose, the lines keep their plain readings.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of a poem |

The errors are those of `VerseStats`.

=== "Code"

    ``` python
    from ests.verse_stats import detect_meter

    # The beginning of the Romance del prisionero
    detect_meter(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    vs.c_feet, vs.p_deviations
    ```

=== "Result"

    ```
    'octosílabo'
    ({11: 4}, 0.0)
    ```

A compound verse is read by its hemistichs, each by the law of the final stress: in the alejandrino of 7 + 7 syllables *La princesa está pálida* (an esdrújula) and *que ha perdido el color* (an aguda) count 7 each.

=== "Code"

    ``` python
    # The first stanza of Sonatina by Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    vs_sonatina = VerseStats(sonatina)
    vs_sonatina.meter, vs_sonatina.n_feet
    vs_sonatina.syllables[3]
    vs_sonatina.patterns[2], vs_sonatina.patterns[3]
    vs_sonatina.stresses[3], vs_sonatina.caesuras
    ```

=== "Result"

    ```
    ('alejandrino', 14)
    ('la', 'prin', 'ce', 'sa‿es', 'tá', 'pá', 'li', 'da', 'en', 'su', 'si', 'lla', 'de', 'o', 'ro')
    ('+-+--+-+-+--+-', '--+-++---+--+-')
    ((2, 4, 5, 10, 13), (7, 7, 7, 8, 7, 7))
    ```

</div>

<div class="metric-card" markdown>

### Rhythmic stresses { #pyrrhics }

`p_pyrrhics` · `stress_profile` · `c_rhythms` · Navarro Tomás, 1972
{ .metric-meta }

The rhythmic stresses (`VERSE_RHYTHMS`) are the ones a meter asks for besides the last stress, which every line has by the law of the final stress: the endecasílabo is stressed on the 6th syllable (a maiore) or on the 4th and the 8th (sáfico) or the 7th (dactílico); a compound verse on the last stress of its first hemistich. `p_pyrrhics` is the share of the lines of the meter without them, and a meter with the last stress alone, the octosílabo among others, has `p_pyrrhics` 0.

$$
\frac{\textrm{Number of lines of the meter without its rhythmic stresses}}{\textrm{Number of lines of the meter}}
$$

`stress_profile` is the share of the lines of the meter stressed on each metrical syllable; the syllables are counted from zero, so the 6th syllable is the number 5. Without a meter `p_pyrrhics` is `nan` and the profile is empty. `c_rhythms` is the distribution of the endecasílabos by type:

| Type | Stresses | Name |
| :--- | :------- | :--- |
| `1-6-10` | 1st, 6th | enfático |
| `2-6-10` | 2nd, 6th | heroico |
| `3-6-10` | 3rd, 6th | melódico |
| `4-6-10`, `5-6-10` | the first stress on the 4th or the 5th, 6th | a maiore |
| `6-10` | 6th, no stress before it | a maiore |
| `4-8-10` | 4th, 8th, no 6th | sáfico |
| `4-7-10` | 4th, 7th, no 6th nor 8th | dactílico, de gaita gallega |

A line with the 6th syllable stressed takes its type from its first stress; `4-6-10` counts as sáfico in some treatises. A line with none of the three sets is left out of `c_rhythms` and counted in `p_pyrrhics`.

=== "Code"

    ``` python
    vs.p_pyrrhics, vs.stress_profile
    vs.c_rhythms
    ```

=== "Result"

    ```
    (0.0, (0.25, 0.25, 0.25, 1.0, 0.0, 0.25, 0.25, 0.75, 0.0, 1.0, 0.0))
    {'4-8-10': 2, '4-7-10': 1, '3-6-10': 1}
    ```

</div>

<div class="metric-card" markdown>

### Rhyme { #rhyme_scheme }

`p_rhymed` · `rhyme_schemes` · `c_rhymes`
{ .metric-meta }

``` {.python .signature}
rhyme_scheme(text, seseo=False)
```

The rhyme scheme of a poem: the schemes of the stanzas separated by spaces. The object has the schemes by stanza in `rhyme_schemes`, the share of the rhymed lines in `p_rhymed` and the distribution of the rhymed lines by the kind of the rhyme, `consonante` or `asonante`, in `c_rhymes`.

A line rhymes by its ending from the last stressed vowel: in full (consonante) if the sounds are the same, by assonance (asonante) if the stressed and the last vowels are. The sounds are the ones of the ear: `b` and `v`, `c` and `z` (`s` with `seseo`), `ll` and `y` are one sound, `h` is silent, the tap `r` and the trill `rr` differ. The assonance leaves out the vowels between the stressed and the last one (*pálido* - a, o), takes the stressed vowel of a diphthong (*cielo* - e, o; *gracia* - a, a), reads a final `i` and `u` as `e` and `o` (*fácil* - a, e) and gives an aguda its stressed vowel alone. A line rhymes with the lines of the window of `RHYME_WINDOW` (4) lines before it, across the stanzas, so that the quatrains of a sonnet rhyme ABBA ABBA.

The assonance counts in two cases. A poem whose rhyme is the assonance - at least a third of its lines with no full rhyme, and at least four of them, share one (`RHYME_MIN_ASSONANCE`, `RHYME_MIN_ASSONANT_LINES`) - rhymes by the assonances of all its lines, which take in the full rhymes of the same vowels, as an assonant sonnet does. Otherwise the assonance counts on alternate lines with unrhymed lines between them: a run of at least four lines two apart with three in four of the lines between them free of a full rhyme (`RHYME_MIN_FREE`), or all the even lines of a stanza of an even number of lines, as the second and the fourth line of a copla. So a romance rhymes even when its assonance changes from part to part or its assonant lines also rhyme in full two by two. An assonance of neighbouring lines is no rhyme: in a sonnet of `-ado` and `-ano` the two groups stay apart.

The rhyme scheme follows the Spanish usage: the letters go in the order of the rhyme groups of the whole poem, upper-case for the lines of arte mayor (9 syllables and more, `VERSE_ARTE_MAYOR`) and lower-case for the lines of arte menor, a hyphen for an unrhymed line: a sonnet is ABBA ABBA CDC DCD, a redondilla abba, a lira aBabB, a romance -a-a-a-a. When the 26 letters run out, the letter of a group that no line in the window can join any more is taken again.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of a poem |
| `seseo` | `bool` | `False` | Pronounce `c` and `z` before `e` and `i` as `s` in the rhyme |

The errors are those of `VerseStats`.

=== "Code"

    ``` python
    from ests.verse_stats import rhyme_scheme

    # Sor Juana Inés de la Cruz
    rhyme_scheme(
        "Hombres necios que acusáis\na la mujer sin razón,\nsin ver que sois la ocasión\nde lo mismo que culpáis."
    )
    vs.rhyme_schemes, vs.p_rhymed, vs.c_rhymes

    # The beginning of La tierra de Alvargonzález by Antonio Machado
    romance = """Siendo mozo Alvargonzález,
    dueño de mediana hacienda,
    que en otras tierras se dice
    bienestar y aquí, opulencia,
    en la feria de Berlanga
    prendóse de una doncella,
    y la tomó por mujer
    al año de conocerla."""
    rhyme_scheme(romance), VerseStats(romance).c_rhymes
    ```

=== "Result"

    ```
    'abba'
    (('ABBA',), 1.0, {'consonante': 4})
    ('-a-a-a-a', {'asonante': 4})
    ```

</div>

<div class="metric-card" markdown>

### Strophes and form { #strophes }

`strophes` · `form`
{ .metric-meta }

A stanza is named by its lines, their lengths, its scheme and its rhyme (`VERSE_STROPHES`, the first that fits), `None` if no strophe fits:

| Strophe | Lines | Lengths | Schemes | Rhyme |
| :------ | :---- | :------ | :------ | :---- |
| pareado | 2 | any | aa | any |
| terceto | 3 | arte mayor | aba, a-a, abc, aab, abb | any |
| tercerilla | 3 | arte menor | aba, a-a | any |
| cuaderna vía | 4 | 14 each | aaaa | consonante |
| cuarteto, serventesio | 4 | arte mayor | abba; abab | consonante |
| redondilla, cuarteta | 4 | arte menor | abba; abab | consonante |
| seguidilla | 4 | 7-5-7-5 | -a-a | any |
| copla | 4 | 8 each | -a-a | asonante |
| lira | 5 | 7-11-7-7-11 | ababb | consonante |
| quinteto, quintilla | 5 | arte mayor; arte menor | ababa, abaab, abbab, aabab, aabba | consonante |
| estrofa manriqueña | 6 | 8-8-4-8-8-4 | abcabc | consonante |
| sexta rima | 6 | arte mayor | ababcc | consonante |
| sexteto | 6 | arte mayor | aabccb, abcabc, abbacc, aabbcc | consonante |
| sextilla | 6 | arte menor | aabccb, ababcc, abcabc, aabaab | consonante |
| octava real | 8 | 11 each | abababcc | consonante |
| décima | 10 | 8 each | abbaaccddc | consonante |

A stanza of a poem with no meter is fitted to the syllables of a strophe that asks for them, so that a single lira gets its 7 and 11 syllables. The form of a poem is `soneto` for 14 lines of a meter of arte mayor in full rhyme with the quatrains ABBA or ABAB and the tercets on rhymes of their own; `romance` for octosílabos from 8 lines with three in four of the even lines of the stanzas rhymed by assonance, which may change, and three in four of the odd ones unrhymed; the strophe of all the stanzas; `silva` for heptasílabos and endecasílabos with no meter, longer than a strophe (more than 10 lines) and with no pattern of lengths repeated by all its stanzas; otherwise `None`.

=== "Code"

    ``` python
    # The sonnet I by Garcilaso de la Vega
    sonnet = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado;

    mas cuando del camino estó olvidado,
    a tanto mal no sé por dó he venido;
    sé que me acabo, y más he yo sentido
    ver acabar comigo mi cuidado.

    Yo acabaré, que me entregué sin arte
    a quien sabrá perderme y acabarme
    si quisiere, y aún sabrá querello;

    que pues mi voluntad puede matarme,
    la suya, que no es tanto de mi parte,
    pudiendo, ¿qué hará sino hacello?"""
    vs_sonnet = VerseStats(sonnet)
    vs_sonnet.rhyme_schemes, vs_sonnet.strophes, vs_sonnet.form
    vs_sonatina.strophes, VerseStats(romance).form
    ```

=== "Result"

    ```
    (('ABBA', 'ABBA', 'CDE', 'DCE'), ('cuarteto', 'cuarteto', 'terceto', 'terceto'), 'soneto')
    (('sexteto',), 'romance')
    ```

</div>

<div class="metric-card" markdown>

### Line endings { #clausulas }

`p_masculine` · `p_feminine` · `p_dactylic` · `c_clausulas`
{ .metric-meta }

The type of the ending (cláusula) of a line by the syllables after its last stress: `aguda` - the stress on the last syllable, `llana` - one syllable after the stress, `esdrújula` - two, `sobresdrújula` - three or more (`VERSE_CLAUSULAS`, as [`stress_type`](../syllables.md#stress_type) of a word). `c_clausulas` is the distribution of the lines by type, and the shares are taken over all the lines: `p_masculine` of the agudas, `p_feminine` of the llanas and `p_dactylic` of the esdrújulas.

=== "Code"

    ``` python
    vs.c_clausulas, vs_sonatina.c_clausulas
    vs_sonatina.p_masculine, vs_sonatina.p_feminine
    ```

=== "Result"

    ```
    ({'llana': 4}, {'aguda': 2, 'llana': 4})
    (0.3333333333333333, 0.6666666666666666)
    ```

</div>

## Methods

`accentuate()` returns the text with the stresses marked: an acute accent (U+0301) is put after the stressed vowel of every stressed word that has no written accent; the words with a written accent keep it, and the unstressed words of the verse (`VERSE_PROCLITICS`) stay unmarked, except the last word of a line. The marks are combining characters apart from the written accents, so `unicodedata.normalize("NFC", ...)` turns them into accented letters. Only the lines with Spanish words are returned (as in `lines`), the stanzas separated by a blank line. Unlike the [`accentuate`](#accentuate) function, the last word of a line is always stressed.

=== "Code"

    ``` python
    print(vs.accentuate())
    ```

=== "Result"

    ```
    Cuando me páro a contemplár mi estádo
    y a vér los pásos por do me hán traído,
    hállo, según por do andúve perdído,
    que a mayór mál pudiéra habér llegádo.
    ```

`get_stats()` returns the metrics as a dictionary, and `print_stats()` prints them as a table with their descriptions (`VERSE_STATS_DESC`), as in the example at the top of the page.

=== "Code"

    ``` python
    vs.get_stats()
    ```

=== "Result"

    ```
    {'n_lines': 4,
     'n_stanzas': 1,
     'meter': 'endecasílabo',
     'n_feet': 11,
     'p_deviations': 0.0,
     'p_pyrrhics': 0.0,
     'p_rhymed': 1.0,
     'p_masculine': 0.0,
     'p_feminine': 1.0,
     'p_dactylic': 0.0}
    ```

## Algorithm { #algorithm }

A line of Spanish verse is measured by its metrical syllables, which are not the syllables of its words one by one:

1.  **Syllables and stresses.** Every word is split into syllables by [`syllabify`](../syllables.md) and stressed by the orthographic rules of [`word_stresses`](../syllables.md#word_stresses); an adverb in `-mente` has two stresses. The unstressed words of the verse (`VERSE_PROCLITICS`) take no stress: the articles, the prepositions except `según`, the conjunctions, the relatives (`que`, `cual`, `donde`, `como`, `cuanto`), the clitic pronouns (`me`, `te`, `se`, `le`, `nos`), the possessives before a noun (`mi`, `tu`, `su`, `nuestro`, `vuestro`), the titles before a name (`don`, `fray`, `san`), `tan`, `aun` and the interjections `oh`, `ay`, `ah`. The last word of a line is always stressed.
2.  **The plain reading.** The final vowel of a word and the first one of the next make one syllable - a synalepha (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). A silent `h` lets it through (*oh‿al-ma*), while `hi` and `hu` before a vowel (*hierba*, *hueso*) and `y` before a vowel (*ya*, *yo*) are consonants and stop it; a consonant at the end of a word stops it too (*el | al-ma*).
3.  **The law of the final stress.** A line counts up to its last stressed syllable and one syllable more: a line that ends in an aguda gets a syllable (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), a line that ends in an esdrújula loses one (*el pá-ja-ro* - 3).
4.  **The meter.** The meter of a poem is the length of most plain readings; on a tie from three lines up, the tied length with a name that leaves the fewest lines off it wins. Every line is fitted to it with the fewest changes of its plain reading: a longer line joins two vowels of a hiatus in a word - a synaeresis (*poe-ta*), the ones with an accented `i` or `u` (*dí-a*) last; a shorter line breaks its synalephas from the end of the line - a hiatus, then splits a diphthong of a stressed syllable - a dieresis (*su-a-ve*, *ru-i-do*). A written diaeresis marks a hiatus (*sü-a-ve*) that no synaeresis joins. A line that cannot reach the meter keeps its plain reading and counts as off it. A poem without a meter fits its lines to its common lengths instead, if they take more than half of the lines.
5.  **Compound verse.** A compound verse of two equal hemistichs (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) is tried when more than half of the plain readings split into its hemistichs and its length equals the one of most lines or is one syllable off it; the reading with fewer lines off the meter wins, the compound verse on a tie. The caesura falls after a stressed word and blocks the synalepha, and each hemistich follows the law of the final stress on its own: the alejandrino *La princesa está pálida | en su silla de oro* is 7 + 7.

On the 60,209 lines of the 4,259 sonnets of [SpanishSonnets](../datasets/spanishsonnets.md), the length of a line agrees with the automatic scansion of DISCO in 97.0% of the lines and with [rantanplan](https://github.com/linhd-postdata/rantanplan) in 97.7%, and the stress of a metrical syllable of the lines of equal length in 97.4% and 99.6%.

The rhyme is described in its [card](#rhyme_scheme). Against the automatic rhyme of DISCO (RhymeTagger), 99.1% of the pairs of rhyming lines we find are its pairs, and we find 97.9% of its pairs.

## Accentuation { #accentuate }

``` {.python .signature}
accentuate(text)
```

Marks the stresses of a text by the orthographic rules: an acute accent (U+0301) is put after the stressed vowel of every word without a written accent, both stresses of an adverb in `-mente` and of a hyphenated compound; the unstressed words of the verse (`VERSE_PROCLITICS`) stay unmarked. The text is normalized to NFC. For the lines of a poem, where the last word is always stressed, the `VerseStats.accentuate` method serves.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text |

=== "Code"

    ``` python
    import unicodedata

    from ests.verse_stats import accentuate

    text = "Yo soy aquel que ayer no más decía el verso azul y la canción profana"
    unicodedata.normalize("NFC", accentuate(text))
    ```

=== "Result"

    ```
    'Yó sóy aquél que ayér nó más decía el vérso azúl y la canción profána'
    ```

## Stanzas { #split_stanzas }

``` {.python .signature}
split_stanzas(text)
```

Splits a text into stanzas and lines: the stanzas are separated by blank lines, and the lines without a Spanish syllable (numbers, asterisks, other alphabets) and the roman numerals of the parts of a poem (`II`, `IV.`) are left out. The text is normalized to NFC.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text of a poem |

=== "Code"

    ``` python
    from ests.verse_stats import split_stanzas

    split_stanzas(
        "Cuando me paro a contemplar mi estado\n"
        "y a ver los pasos por do me han traído,\n\n* * *\n\n"
        "hallo, según por do anduve perdido,"
    )
    ```

=== "Result"

    ```
    [['Cuando me paro a contemplar mi estado', 'y a ver los pasos por do me han traído,'],
     ['hallo, según por do anduve perdido,']]
    ```
