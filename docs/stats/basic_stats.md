# Basic statistics

``` {.python .signature}
BasicStats(source, sents_extractor=None, words_extractor=None, normalize=False, complex_syl_factor=3, long_word_letter_factor=7)
```

--8<-- "stats/basic_stats.md:BasicStats"

The class extends the `BasicStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) core with the hooks of Spanish: the syllables of a word are counted by [`count_syllables`](../syllables.md#count_syllables), and the default extractors are the Spanish [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md). The ordinal indicators `º` and `ª` are letters (`3.º` is a one-letter word). The blank line component of esTS is called [`ests_blank_lines`](../components.md#blank_lines): `nlp.add_pipe("ests_blank_lines", before="parser")`. The statistics are computed when the object is created. A string with a character without a UTF-8 form, as a file read with the wrong encoding gives, raises `SourceError` from the Spanish tokenizer.

=== "Code"

    ``` python
    from ests import BasicStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    bs = BasicStats(text, normalize=True)
    bs.print_stats()
    ```

=== "Result"

    ```
         Statistic     |  Value
    ------------------------------
    Sentences          |    1
    Words              |    10
    Unique words       |    8
    Long words         |    5
    Complex words      |    5
    Simple words       |    5
    Monosyllabic words |    4
    Polysyllabic words |    6
    Characters         |    71
    Letters            |    60
    Spaces             |    9
    Syllables          |    23
    Punctuation marks  |    2
    ```

## Parameters

--8<-- "stats/basic_stats.md:BasicStats-parameters"

In esTS the thresholds are those of the core and of the readability formulas: a complex word has three or more syllables, as in SMOG, and a long word seven or more letters, as in LIX and RIX (`COMPLEX_SYL_FACTOR = 3` and `LONG_WORD_LETTER_FACTOR = 7` of `anyts.constants`).

## Statistics

--8<-- "stats/basic_stats.md:BasicStats-attributes"

## Methods

--8<-- "stats/basic_stats.md:BasicStats-count_words_by"

The methods recount complex and long words with a threshold other than the one set when the object was created; [`ReadabilityStats`](readability_stats.md) counts the polysyllabic words of SOL and the long words of LIX and RIX by them, so these do not depend on the thresholds of the object.

--8<-- "stats/basic_stats.md:BasicStats-get_stats"

--8<-- "stats/basic_stats.md:BasicStats-print_stats"

The normalized statistics `p_*` are not in the table.

--8<-- "stats/stats.md:Stats-to_dataframe"

=== "Code"

    ``` python
    bs.count_words_by_syllables(4), bs.count_words_by_letters(8)
    bs.get_stats()
    ```

=== "Result"

    ```
    (1, 5)
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
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0},
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

The `describe` method is that of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the basic statistics have no scales, so it gives `None` for the statistics of `get_stats`.

## Punctuation marks { #count_punctuations }

--8<-- "stats/basic_stats.md:count_punctuations"

esTS counts with the marks and the dash pattern of the core, `PUNCTUATION_MARKS` and `DASH_PATTERN` of `anyts.basic_stats`, which follow Spanish orthography: the inverted `¿` and `¡` are question and exclamation marks (`¿Qué?` carries two question marks), `—`, `–` and the horizontal bar `―` are dashes, and so is the raya typed with hyphens - a run of two or more hyphens, a hyphen after whitespace, at the start of a line or after a closing mark, before a space or between a letter and an opening or a closing mark (`--Hola --dijo Juan`, `- Se fueron - dijo`, `cuatro.-¿Cinco?`); a hyphen inside a word, before a digit or at the end of a line inside a word is a hyphen (`teórico-práctico`, `-5`), `«»` are guillemets and `"“”‘’` the quotation marks of the three levels of the orthography. The combining marks and the invisible format characters (Unicode M and Cf) are removed from the words but are not counted as marks.

=== "Code"

    ``` python
    from ests.basic_stats import count_punctuations

    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    ```

=== "Result"

    ```
    {'comma': 2,
     'exclamation': 2,
     'ellipsis': 1,
     'semicolon': 1,
     'dash': 3,
     'angle_quotes': 2,
     'parentheses': 2}
    ```

## Punctuation profile { #punctuation }

``` {.python .signature}
punctuation_profile(text, n_words=None)
```

The frequencies of the punctuation marks by type (`count_punctuations`) per 1000 words and `inverted_share` - the share of the inverted marks among all question and exclamation marks: `0.5` when every question and exclamation opens with `¿` or `¡` as the orthography requires, lower when the writer drops them. Without words the frequencies are `nan`, and so is `inverted_share` without question and exclamation marks.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `n_words` | `int` | `None` | Number of words; without it the words are extracted by `WordsExtractor` |

Raises:

- `SourceTypeError` - a text that is not a string;
- `SourceError` - without `n_words`, a text with a character without a UTF-8 form;
- `ParameterError` - a number of words that is not a non-negative integer.

The profile depends on text formatting (typographic quotation marks and dashes, the inverted marks), so it is best read separately from linguistic features.

=== "Code"

    ``` python
    from ests.basic_stats import punctuation_profile

    profile = punctuation_profile(text)
    round(profile["dash"], 1), profile["inverted_share"]
    ```

=== "Result"

    ```
    (230.8, 0.5)
    ```
