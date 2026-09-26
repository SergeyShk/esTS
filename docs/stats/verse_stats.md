# Verse statistics

!!! info ""
    **ests.verse_stats.VerseStats**

## Description

A module for computing the verse statistics of a text: the scansion of the lines, the meter and the number of metrical syllables, the rhythmic stresses and the stress profile, the types of the endecasílabo, the endings of the lines, the rhyme, its scheme and the strophes. The data source can be either a text with its line breaks or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library; no trained model and no dictionary are needed.

The meter of Spanish verse is syllabic: a line is measured by its metrical syllables, and the stresses shape its rhythm. The words are split into syllables and stressed by the orthographic rules of [`syllabify`](../syllables.md) and [`word_stresses`](../syllables.md#word_stresses), the unstressed words of the verse left aside. The syllables of a line are then counted as the verse reads them: the vowels at the boundary of two words make one syllable (a synalepha), the law of the final stress sets the length by the last stressed syllable, and a line may break a synalepha, split a diphthong or join a hiatus to reach the meter of its poem. A compound verse, the alejandrino above all, is read as two hemistichs. The lines rhyme by their endings from the last stressed vowel, in full (consonante) or by assonance (asonante), and the stanzas and the poem are named by their lines and schemes. The algorithm and its accuracy on the sonnets of [DISCO](../datasets/spanishsonnets.md) are described in the [functions](verse_stats_funcs.md) section.

!!! note "Note"
    The statistics are computed when the `VerseStats` object is made.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `seseo` | bool | `False` | Pronounce `c` and `z` before `e` and `i` as `s` in the rhyme, as in Andalusia and in America: `voz` - `dos` |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `lines` | tuple[str] | Lines with Spanish words |
| `stanzas` | tuple[tuple[str, ...], ...] | Lines by stanza |
| `n_lines` | int | Number of lines |
| `n_stanzas` | int | Number of stanzas |
| `meter` | str/None | Meter - the name of the verse by its metrical syllables: `octosílabo`, `endecasílabo`, `alejandrino`... (`VERSE_METERS`), or `None` |
| `n_feet` | int/None | Number of metrical syllables of the meter |
| `c_feet` | dict[int, int] | Distribution of the lines by metrical syllables |
| `p_deviations` | float | Share of the lines off the meter, `nan` without a meter |
| `p_pyrrhics` | float | Share of the lines of the meter without its rhythmic stresses, `nan` without a meter |
| `stress_profile` | tuple[float, ...] | Share of the stressed lines of the meter by metrical syllable |
| `c_rhythms` | dict[str, int] | Distribution of the endecasílabos by type |
| `syllables` | tuple[tuple[str, ...], ...] | Syllables of every line as the verse reads them, a synalepha marked with `‿` |
| `stresses` | tuple[tuple[int, ...], ...] | Indices of the stressed syllables of every line in `syllables`, from zero |
| `caesuras` | tuple[int/None, ...] | Index of the first syllable of the second hemistich of every line in `syllables`, `None` for a simple verse |
| `patterns` | tuple[str, ...] | Patterns of the lines of `+` (a stressed metrical syllable) and `-` (an unstressed one), as long as the line in metrical syllables |
| `c_clausulas` | dict[str, int] | Distribution of the endings of the lines by type: `aguda`, `llana`, `esdrújula`, `sobresdrújula` |
| `p_masculine` | float | Share of oxytone endings (`aguda`, the stress on the last syllable) |
| `p_feminine` | float | Share of paroxytone endings (`llana`, one syllable after the stress) |
| `p_dactylic` | float | Share of proparoxytone endings (`esdrújula`, two syllables after the stress) |
| `c_stressed_vowels` | dict[str, int] | Distribution of the stressed vowels |
| `mean_line_len` | float | Mean length of a line in metrical syllables |
| `rhyme_schemes` | tuple[str, ...] | Rhyme schemes of the stanzas |
| `p_rhymed` | float | Share of the rhymed lines |
| `c_rhymes` | dict[str, int] | Distribution of the rhymed lines by the kind of the rhyme: `consonante`, `asonante` |
| `strophes` | tuple[str/None, ...] | Names of the stanzas (`VERSE_STROPHES`) |
| `form` | str/None | Form of the poem: `soneto`, `romance`, the strophe of all its stanzas, `silva` |
| `seseo` | bool | Whether the rhyme is read with seseo |

The meter is the length of most lines, and it is not determined (`None`) if more than a tenth of the lines (`VERSE_MAX_DEVIATIONS`) stay off it after the fitting: a polymetric poem (a silva of heptasílabos and endecasílabos, a sonnet with an estrambote of more than a tenth of heptasílabos), free verse and prose. A single line has no meter either (`VERSE_MIN_LINES`): any line of up to 18 syllables has a length with a name, and 36% of the sentences of twelve prose works of the [corpus of literature](../datasets/spanishliterature.md) would get one, against 1.4% of two sentences as two lines and 0.1% of three. The lines of a poem without a meter are fitted to its common lengths - the ones of at least two lines and a tenth of them, as the 7 and the 11 syllables of a lira or a silva - if these take more than half of the lines, so that the distribution of the lengths and the types of the endecasílabo count the real lengths of a polymetric poem; the lines of free verse and prose keep their plain readings.

The rhythmic stresses (`VERSE_RHYTHMS`) are the ones a meter asks for besides the last stress, which every line has by the law of the final stress: the endecasílabo is stressed on the 6th syllable (a maiore) or on the 4th and the 8th (sáfico) or the 7th (dactílico); a compound verse on the last stress of its first hemistich. A meter with the last stress alone, the octosílabo among others, has `p_pyrrhics` 0.

| Type | Stresses | Name |
| :--: | :------: | :--- |
| `1-6-10` | 1st, 6th | enfático |
| `2-6-10` | 2nd, 6th | heroico |
| `3-6-10` | 3rd, 6th | melódico |
| `4-6-10`, `5-6-10` | the first stress on the 4th or the 5th, 6th | a maiore |
| `6-10` | 6th, no stress before it | a maiore |
| `4-8-10` | 4th, 8th, no 6th | sáfico |
| `4-7-10` | 4th, 7th, no 6th nor 8th | dactílico, de gaita gallega |

A line with the 6th syllable stressed takes its type from its first stress; `4-6-10` counts as sáfico in some treatises. A line with none of the three sets is left out of `c_rhythms` and counted in `p_pyrrhics`. The metrical syllables of `stress_profile` are counted from zero, so the 6th syllable is the number 5. `stresses` indexes `syllables`, and the two agree with `patterns` up to the last stress of a simple verse; in a compound verse each hemistich takes its own length, so after an aguda or an esdrújula at the caesura `patterns` and `syllables` part, and `caesuras` tells where the second hemistich begins.

### Rhyme and strophes { #rhyme }

A line rhymes by its ending from the last stressed vowel: in full (consonante) if the sounds are the same, by assonance (asonante) if the stressed and the last vowels are. The sounds are the ones of the ear: `b` and `v`, `c` and `z` (`s` with `seseo`), `ll` and `y` are one sound, `h` is silent, the tap `r` and the trill `rr` differ. The assonance leaves out the vowels between the stressed and the last one (*pálido* - a, o), takes the stressed vowel of a diphthong (*cielo* - e, o; *gracia* - a, a), reads a final `i` and `u` as `e` and `o` (*fácil* - a, e) and gives an aguda its stressed vowel alone. A line rhymes with the lines of the window of `RHYME_WINDOW` (4) lines before it, across the stanzas, so that the quatrains of a sonnet rhyme ABBA ABBA.

The assonance counts in two cases. A poem whose rhyme is the assonance - at least a third of its lines with no full rhyme, and at least four of them, share one (`RHYME_MIN_ASSONANCE`, `RHYME_MIN_ASSONANT_LINES`) - rhymes by the assonances of all its lines, which take in the full rhymes of the same vowels: the assonant sonnets of DISCO. Otherwise the assonance counts on alternate lines with unrhymed lines between them: a run of at least four lines two apart with three in four of the lines between them free of a full rhyme (`RHYME_MIN_FREE`), or all the even lines of a stanza of an even number of lines, as the second and the fourth line of a copla. So a romance rhymes even when its assonance changes from part to part (*La tierra de Alvargonzález* of Machado goes é-a, á-a, é-o...) and when its assonant lines also rhyme in full two by two (*colgar* - *contemplar* in the rima LIII of Bécquer). An assonance of neighbouring lines is no rhyme: in a sonnet of `-ado` and `-ano` every line has its full rhyme and the groups stay apart, and the lines of prose do not rhyme by chance - sentences of prose as lines share an assonance that counts in 0.1-3.6% of the texts of 5 to 40 lines and in 6.5% of the ones of 4, where two lines of a copla are enough.

The rhyme scheme follows the Spanish usage: the letters go in the order of the rhyme groups of the whole poem, upper-case for the lines of arte mayor (9 syllables and more, `VERSE_ARTE_MAYOR`) and lower-case for the lines of arte menor, a hyphen for an unrhymed line: a sonnet is ABBA ABBA CDC DCD, a redondilla abba, a lira aBabB, a romance -a-a-a-a. When the 26 letters run out, the letter of a group that no line in the window can join any more is taken again.

A stanza is named by its lines, their lengths, its scheme and its rhyme (`VERSE_STROPHES`, the first that fits):

| Strophe | Lines | Lengths | Schemes | Rhyme |
| :------ | :---: | :------ | :------ | :---: |
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

A stanza of a poem with no meter is fitted to the syllables of a strophe that asks for them, so that a single lira gets its 7 and 11 syllables. The form of a poem is `soneto` for 14 lines of a meter of arte mayor in full rhyme with the quatrains ABBA or ABAB and the tercets on rhymes of their own; `romance` for octosílabos from 8 lines with three in four of the even lines of the stanzas rhymed by assonance, which may change, and three in four of the odd ones unrhymed; the strophe of all the stanzas; `silva` for heptasílabos and endecasílabos with no meter, longer than a strophe (more than 10 lines) and with no pattern of lengths repeated by all its stanzas.

!!! note "Note"
    The scansion, the meter and the stresses can be obtained apart with the functions of the module. The algorithm and the functions are described in the corresponding [section](verse_stats_funcs.md).

## Methods

### get_stats

Returns a dictionary with the computed verse statistics.

!!! example "Example"

    _Code_:

    ``` python
    from ests import VerseStats

    # The beginning of the sonnet I by Garcilaso de la Vega
    text = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado."""

    vs = VerseStats(text)
    vs.get_stats()
    ```

    _Result_:

    ``` bash
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

The scansion of every line, the stress profile and the distributions are attributes:

!!! example "Example"

    ``` python
    vs.syllables[1]
    # ('y‿a', 'ver', 'los', 'pa', 'sos', 'por', 'do', 'me‿han', 'tra', 'í', 'do')
    vs.patterns
    # ('---+---+-+-', '-+-+---+-+-', '+--+--+--+-', '--++-+-+-+-')
    vs.stresses[0]
    # (3, 7, 9)
    vs.stress_profile
    # (0.25, 0.25, 0.25, 1.0, 0.0, 0.25, 0.25, 0.75, 0.0, 1.0, 0.0)
    vs.c_rhythms, vs.c_clausulas
    # ({'4-8-10': 2, '4-7-10': 1, '3-6-10': 1}, {'llana': 4})
    vs.c_stressed_vowels
    # {'a': 8, 'e': 3, 'i': 2, 'u': 2, 'o': 1}
    ```

The rhyme of the whole sonnet and of a romance:

!!! example "Example"

    ``` python
    from ests.verse_stats import rhyme_scheme

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
    vs = VerseStats(sonnet)
    vs.rhyme_schemes, vs.strophes, vs.form
    # (('ABBA', 'ABBA', 'CDE', 'DCE'), ('cuarteto', 'cuarteto', 'terceto', 'terceto'), 'soneto')

    # The beginning of La tierra de Alvargonzález by Antonio Machado
    romance = """Siendo mozo Alvargonzález,
    dueño de mediana hacienda,
    que en otras tierras se dice
    bienestar y aquí, opulencia,
    en la feria de Berlanga
    prendóse de una doncella,
    y la tomó por mujer
    al año de conocerla."""
    vs = VerseStats(romance)
    rhyme_scheme(romance), vs.form, vs.c_rhymes
    # ('-a-a-a-a', 'romance', {'asonante': 4})
    ```

### print_stats

Prints a table with the computed verse statistics.

!!! example "Example"

    _Code_:

    ``` python
    from ests import VerseStats

    # The first stanza of Sonatina by Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    vs = VerseStats(sonatina)
    vs.print_stats()
    ```

    _Result_:

    ``` bash
                      Statistic                   |    Value
    ------------------------------------------------------------
    Number of lines                               |      6
    Number of stanzas                             |      1
    Meter                                         | alejandrino
    Number of metrical syllables                  |      14
    Share of lines off the meter                  |     0.00
    Share of lines without the rhythmic stresses  |     0.00
    Share of rhymed lines                         |     1.00
    Share of oxytone endings (aguda)              |     0.33
    Share of paroxytone endings (llana)           |     0.67
    Share of proparoxytone endings (esdrújula)    |     0.00
    ```

The alejandrino is read by hemistichs of 7 syllables. The caesura blocks the synalepha, and each hemistich follows the law of the final stress: *La princesa está pálida* ends in an esdrújula and counts 7, *que ha perdido el color* ends in an aguda and counts 7 as well.

!!! example "Example"

    ``` python
    vs.syllables[3]
    # ('la', 'prin', 'ce', 'sa‿es', 'tá', 'pá', 'li', 'da', 'en', 'su', 'si', 'lla', 'de', 'o', 'ro')
    vs.patterns[2], vs.patterns[3]
    # ('+-+--+-+-+--+-', '--+-++---+--+-')
    vs.stresses[3], vs.caesuras
    # ((2, 4, 5, 10, 13), (7, 7, 7, 8, 7, 7))
    ```

### accentuate { #accentuate }

Returns the text with the stresses marked: an acute accent (U+0301) is put after the stressed vowel of every stressed word that has no written accent; the words with a written accent keep it, and the unstressed words of the verse (`VERSE_PROCLITICS`) stay unmarked, except the last word of a line. The marks are combining characters apart from the written accents, so `unicodedata.normalize("NFC", ...)` turns them into accented letters. Only the lines with Spanish words are returned (as in `lines`), the stanzas separated by a blank line.

!!! example "Example"

    _Code_:

    ``` python
    ...

    print(VerseStats(text).accentuate())
    ```

    _Result_:

    ``` bash
    Cuando me páro a contemplár mi estádo
    y a vér los pásos por do me hán traído,
    hállo, según por do andúve perdído,
    que a mayór mál pudiéra habér llegádo.
    ```

!!! note "On the sonnets of DISCO"
    Over the 4,259 sonnets of [SpanishSonnets](../datasets/spanishsonnets.md) the meter is the endecasílabo for 3,874, the alejandrino for 316, and 27 sonnets have none, among them dialogues with the names of the speakers in the lines and sonnets with an estrambote. The types of the endecasílabo shift from the Golden Age to the 19th century: the heroico `2-6-10` leads in the 15th-17th centuries (32% of the typed lines, the sáfico `4-8-10` 18%), and the sáfico leads in the 19th (25%, the heroico 25%, the melódico `3-6-10` 21%).
