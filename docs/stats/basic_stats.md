# Basic statistics

!!! info ""
    **ests.basic_stats.BasicStats**

## Description

--8<-- "stats/basic_stats.md:BasicStats"

!!! note "Note"
    The statistics are computed when the `BasicStats` object is initialized.

## Language hooks

The class extends the `BasicStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) core with the hooks of Spanish: the syllables of a word are counted by [`count_syllables`](../syllables.md#count_syllables), and the default extractors are the Spanish [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md). The ordinal indicators `º` and `ª` are letters (`3.º` is a one-letter word). A `Doc` without sentence boundaries (`spacy.blank`, a pipeline without `parser` and `senter`) takes its sentences from the text by `SentsExtractor`.

## Parameters

--8<-- "stats/basic_stats.md:BasicStats-parameters"

!!! note "Note"
    The default thresholds are those of the readability formulas: a complex word has three or more syllables, as in SMOG, and a long word seven or more letters, as in LIX and RIX.

## Attributes

--8<-- "stats/basic_stats.md:BasicStats-attributes"

## Methods

### count_words_by_syllables, count_words_by_letters

--8<-- "stats/basic_stats.md:BasicStats-count_words_by"

!!! note "Note"
    These methods recount complex and long words with a threshold different from the one set at initialization.

### get_stats

--8<-- "stats/basic_stats.md:BasicStats-get_stats"

An example of computing basic text statistics with normalization:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import BasicStats

    # Prepare the data
    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

    # Compute the statistics
    bs = BasicStats(text, normalize=True)
    bs.get_stats()
    ```

    _Result_:

    ``` bash
    {'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
     'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
     'n_sents': 1,
     'n_words': 10,
     'n_unique_words': 8,
     'n_long_words': 5,
     'n_complex_words': 5,
     'n_simple_words': 5,
     'n_monosyllable_words': 4,
     'n_polysyllable_words': 6,
     'n_chars': 71,
     'n_letters': 60,
     'n_spaces': 9,
     'n_syllables': 23,
     'n_punctuations': 2,
     'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0, 'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0, 'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0, 'parentheses': 0, 'other': 0},
     'p_unique_words': 0.8,
     'p_long_words': 0.5,
     'p_complex_words': 0.5,
     'p_simple_words': 0.5,
     'p_monosyllable_words': 0.4,
     'p_polysyllable_words': 0.6,
     'p_letters': 0.8450704225352113,
     'p_spaces': 0.1267605633802817,
     'p_punctuations': 0.028169014084507043}
    ```

### print_stats

--8<-- "stats/basic_stats.md:BasicStats-print_stats"

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    bs.print_stats()
    ```

    _Result_:

    ``` bash
         Statistic      |  Value
    ------------------------------
    Sentences           |    1
    Words               |    10
    Unique words        |    8
    Long words          |    5
    Complex words       |    5
    Simple words        |    5
    Monosyllabic words  |    4
    Polysyllabic words  |    6
    Characters          |    71
    Letters             |    60
    Spaces              |    9
    Syllables           |    23
    Punctuation marks   |    2
    ```

!!! warning "Warning"
    The method does not print the normalized statistics attributes `p_*`.

## Punctuation profile { #punctuation }

!!! info ""
    **ests.basic_stats.count_punctuations()**, **ests.basic_stats.punctuation_profile()**

--8<-- "stats/basic_stats.md:count_punctuations"

The default marks and dashes are those of Spanish orthography: the inverted `¿` and `¡` are question and exclamation marks (`¿Qué?` carries two question marks), `—`, `–` and the horizontal bar `―` are dashes, and so is the raya typed with hyphens - a run of two or more hyphens, a hyphen after whitespace, at the start of a line or after a closing mark, before a space or between a letter and an opening or a closing mark (`--Hola --dijo Juan`, `- Se fueron - dijo`, `cuatro.-¿Cinco?`); a hyphen inside a word, before a digit or at the end of a line inside a word is a hyphen (`teórico-práctico`, `-5`), `«»` are guillemets and `"“”‘’` the quotation marks of the three levels of the orthography. The combining marks and the invisible format characters (Unicode M and Cf) are removed from the words but are not counted as marks.

`punctuation_profile(text, n_words=None)` turns the counts into frequencies per 1000 words and adds `inverted_share` - the share of inverted marks among all question and exclamation marks: `0.5` when every question and exclamation opens with `¿` or `¡` as the orthography requires, lower when the writer drops them; without words or without question and exclamation marks it is `nan`.

The profile depends on text formatting (typographic quotation marks and dashes, the inverted marks), so it is best read separately from linguistic features.

!!! example "Example"

    ``` python
    from ests.basic_stats import count_punctuations, punctuation_profile

    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    # {'comma': 2, 'exclamation': 2, 'ellipsis': 1, 'semicolon': 1, 'dash': 3, 'angle_quotes': 2, 'parentheses': 2}

    round(punctuation_profile(text)["dash"], 1), punctuation_profile(text)["inverted_share"]
    # (230.8, 0.5)
    ```
