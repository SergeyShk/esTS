# Word extraction

!!! info ""
    **ests.extractors.WordsExtractor**

## Description

A module for extracting words from a text. It allows using different tokenizers, filtering stop words, numbers and punctuation, lemmatizing, building N-grams, and setting the minimum and maximum length of extracted words.

!!! note "Note"
    The default tokenizer is the rule-based tokenizer of the [spaCy](https://github.com/explosion/spaCy) Spanish language class (`ests.utils.tokenize`); it needs no trained model. Punctuation marks, including `¿` and `¡`, numbers like `1.500,50`, `3.º`, `1990-1995` and abbreviations like `Sr.`, `EE. UU.` are single tokens; words with enclitic pronouns (`dámelo`, `decírselo`) are not split.

!!! note "Note"
    Lemmas come from [simplemma](https://github.com/adbar/simplemma) (`ests.utils.lemmatize`), which works from a dictionary without a trained model: a known form is mapped to its lower-case lemma (`Tienes` - `tener`, `NIÑOS` - `niño`), an unknown form is returned unchanged (`Madrid`, `dámelo`).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizer or regular expression |
| `filter_punct` | bool | `True` | Filter punctuation marks |
| `filter_nums` | bool | `False` | Filter numbers, including ranges, fractions, dates, times, percentages and ordinals (1990-1995, 1.500,50, 12/03/2020, 3:30, 10%, 3.º, 1.ª, 2do) |
| `use_lexemes` | bool | `False` | Use word lemmas |
| `stopwords` | Collection[str] | `None` | Stop words |
| `lowercase` | bool | `False` | Convert words to lower case |
| `ngram_range` | Tuple[int, int] | `(1, 1)` | Lower and upper bound of the N-gram size |
| `min_len` | int | `0` | Minimum length of an extracted word |
| `max_len` | int | `0` | Maximum length of an extracted word |

!!! note "Note"
    The filters are applied in order: punctuation, numbers, lemmatization, lower case, stop words, word length. Stop words are compared after lowercasing, so with `lowercase=True` the stop word list only needs to be in lower case. A punctuation mark is a token consisting entirely of marks and symbols, including multi-character ones: `?!`, `!..`, `--`, `…`, `€`. A ready stop word list is `spacy.lang.es.stop_words.STOP_WORDS`; note that it also holds frequent verbs like `tener`.

## Methods

### extract

Extracts words from a text.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

An example of word extraction with bigrams as tokens, after filtering numbers and stop words and lemmatizing:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import WordsExtractor

    # Prepare the data
    text = "No tengas 100 euros, ten 100 amigos"

    # Extract words
    we = WordsExtractor(use_lexemes=True, stopwords=["no"], filter_nums=True, ngram_range=(1, 2))
    we.extract(text)
    ```

    _Result_:

    ``` bash
    ('tener', 'euro', 'tener', 'amigo', 'tener_euro', 'euro_tener', 'tener_amigo')
    ```

### get_most_common

Returns a counter of the top words of the text. It takes the number of top words to return as a parameter.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the top words
    we.get_most_common(3)
    ```

    _Result_:

    ``` bash
    [('tener', 2), ('euro', 1), ('amigo', 1)]
    ```

!!! warning "Warning"
    The method must be called after words have been extracted with `extract`.
