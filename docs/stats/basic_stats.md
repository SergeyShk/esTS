# Basic statistics

!!! info ""
    **ests.basic_stats.BasicStats**

## Description

A module for computing basic text statistics. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The module allows using pre-built [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) objects for the sentence and word tokenization needed before computing the statistics. Syllables are counted by [`count_syllables`](../syllables.md#count_syllables), letters by `str.isalpha`, so digits, hyphens and marks inside a word are not letters, while the ordinal indicators `º` and `ª` are (`3.º` is a one-letter word).

For a `Doc` object words are taken from the tokens (punctuation marks and symbols such as `€` or `%` are dropped), sentences - from the annotation; without sentence boundaries (`spacy.blank`, a pipeline without `parser` and `senter`) sentences are extracted from the text by `SentsExtractor`.

!!! note "Note"
    The statistics are computed when the `BasicStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `normalize` | bool | `False` | Compute normalized statistics |
| `complex_syl_factor` | int | `3` | Minimum number of syllables in a complex word |
| `long_word_letter_factor` | int | `7` | Minimum number of letters in a long word |

!!! note "Note"
    The default thresholds follow the Spanish readability tradition: a complex word has three or more syllables, as in the Spanish adaptations of SMOG and Gunning fog, and a long word seven or more letters, as in LIX and RIX.

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `c_letters` | dict[int, int] | Distribution of words by number of letters |
| `c_syllables` | dict[int, int] | Distribution of words by number of syllables |
| `n_sents` | int | Number of sentences |
| `n_words` | int | Number of words |
| `n_unique_words` | int | Number of unique words |
| `n_long_words` | int | Number of long words |
| `n_complex_words` | int | Number of complex words |
| `n_simple_words` | int | Number of simple words |
| `n_monosyllable_words` | int | Number of monosyllabic words |
| `n_polysyllable_words` | int | Number of polysyllabic words |
| `n_chars` | int | Number of characters |
| `n_letters` | int | Number of letters |
| `n_spaces` | int | Number of spaces |
| `n_syllables` | int | Number of syllables |
| `n_punctuations` | int | Number of punctuation marks |
| `c_punctuations` | dict[str, int] | Distribution of punctuation marks by type |
| `p_unique_words` | float | Normalized number of unique words |
| `p_long_words` | float | Normalized number of long words |
| `p_complex_words` | float | Normalized number of complex words |
| `p_simple_words` | float | Normalized number of simple words |
| `p_monosyllable_words` | float | Normalized number of monosyllabic words |
| `p_polysyllable_words` | float | Normalized number of polysyllabic words |
| `p_letters` | float | Normalized number of letters |
| `p_spaces` | float | Normalized number of spaces |
| `p_punctuations` | float | Normalized number of punctuation marks |

!!! warning "Warning"
    The normalized statistics attributes `p_*` are available only when the object is initialized with `normalize=True`.

## Methods

### count_words_by_syllables

Returns the number of words with at least the given number of syllables.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `min_syllables` | int | `-` | Minimum number of syllables in a word |

### count_words_by_letters

Returns the number of words with at least the given number of letters.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `min_letters` | int | `-` | Minimum number of letters in a word |

!!! note "Note"
    These methods recount complex and long words with a threshold different from the one set at initialization, which is what readability formulas with their own thresholds need.

### get_stats

Returns a dictionary with the computed text statistics.

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
    'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0, 'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0, 'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0, 'parentheses': 0, 'other': 0},
    'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
    'n_chars': 71,
    'n_complex_words': 5,
    'n_letters': 60,
    'n_long_words': 5,
    'n_monosyllable_words': 4,
    'n_polysyllable_words': 6,
    'n_punctuations': 2,
    'n_sents': 1,
    'n_simple_words': 5,
    'n_spaces': 9,
    'n_syllables': 23,
    'n_unique_words': 8,
    'n_words': 10,
    'p_complex_words': 0.5,
    'p_letters': 0.8450704225352113,
    'p_long_words': 0.5,
    'p_monosyllable_words': 0.4,
    'p_polysyllable_words': 0.6,
    'p_punctuations': 0.028169014084507043,
    'p_simple_words': 0.5,
    'p_spaces': 0.1267605633802817,
    'p_unique_words': 0.8}
    ```

### print_stats

Prints a table with the computed text statistics.

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

`count_punctuations(text)` counts punctuation marks by the types of `PUNCTUATION_TYPES` - the same distribution lives in the `c_punctuations` attribute: commas, periods, question and exclamation marks (the inverted `¿` and `¡` included, so `¿Qué?` carries two question marks), ellipses (the `…` character, three or more periods, or two periods after `?` and `!` - one mark whose periods do not count as periods: `¿Quién?..` is a question and an ellipsis), colons, semicolons, dashes (`—` and `–`, as well as a hyphen after whitespace or at the start of a line, or before a space, the way the raya is typed in plain-text corpora: `-Hola -dijo Juan`, `- Se fueron - dijo`), hyphens inside words, before digits and at the end of a line inside a word (`teórico-práctico`, `1990-1995`, `-5`, `pala-` at a line break), guillemets `«»`, straight and curly quotation marks `"“”‘’` of the three levels of the orthography, parentheses and the other marks: every remaining character of `PUNCTUATIONS` or of the Unicode categories P and S (`‹›`, `§`, `€`, `°`), the same set that `is_punctuation` removes from the words, so no mark is lost between the words and the types. `punctuation_profile(text, n_words=None)` turns them into frequencies per 1000 words and adds `inverted_share` - the share of inverted marks among all question and exclamation marks: `0.5` when every question and exclamation opens with `¿` or `¡` as the orthography requires, lower when the writer drops them, as in informal texts and messages.

The profile is an editorial and stylometric feature. It depends on text formatting - typographic quotation marks and dashes, the inverted marks - and is easy to fake, so it is best read separately from linguistic features.

!!! example "Example"

    ``` python
    from ests.basic_stats import count_punctuations, punctuation_profile

    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    # {'comma': 2, 'exclamation': 2, 'ellipsis': 1, 'semicolon': 1, 'dash': 3, 'angle_quotes': 2, 'parentheses': 2}

    round(punctuation_profile(text)["dash"], 1), punctuation_profile(text)["inverted_share"]
    # (230.8, 0.5)
    ```
