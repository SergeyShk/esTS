# Character N-gram extraction

!!! info ""
    **ests.extractors.CharNgramsExtractor**

## Description

A module for extracting character N-grams from a text - sequences of N characters taken with a sliding window over the string. Character N-grams are a standard feature of stylometry and authorship attribution (Stamatatos 2009): they capture morphology, punctuation and typical letter combinations without lemmatization. The list of N-grams serves as the units of a text instead of words in stylometric measures such as Burrows's Delta.

Whitespace runs are collapsed into a single space beforehand, punctuation marks are kept: a space or a mark inside an N-gram is a stylistic signal too. With `within_words=True` N-grams do not cross word boundaries: the text is split into words by the tokenizer, punctuation is dropped, and words shorter than N yield no N-grams.

!!! note "Note"
    The default word tokenizer for `within_words` is the tokenizer of the [spaCy](https://github.com/explosion/spaCy) Spanish language class (`ests.utils.tokenize`).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n` | int | `2` | N-gram length in characters |
| `lowercase` | bool | `False` | Convert the text to lower case |
| `within_words` | bool | `False` | Take N-grams only inside words |
| `tokenizer` | Pattern/Callable | `None` | Word tokenizer for `within_words` or a regular expression |

## Methods

### extract

Extracts N-grams from a text.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

!!! example "Example"

    ``` python
    from ests import CharNgramsExtractor

    text = "El gato dormía  en la ventana, y el perro - en el suelo."

    ce = CharNgramsExtractor()
    ce.extract(text)[:8]
    # ('El', 'l ', ' g', 'ga', 'at', 'to', 'o ', ' d')

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    # ('el ', 'l g', ' ga', 'gat', 'ato', 'to ')

    CharNgramsExtractor(n=4, lowercase=True, within_words=True).extract(text)
    # ('gato', 'dorm', 'ormí', 'rmía', 'vent', 'enta', 'ntan', 'tana', 'perr', 'erro', 'suel', 'uelo')
    ```

### get_most_common

Returns the most frequent N-grams of the last extraction.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n` | int | `10` | Number of N-grams |

!!! example "Example"

    ``` python
    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)
    ce.get_most_common(2)
    # [('el ', 3), (' en', 2)]
    ```
