# Character N-gram extraction

``` {.python .signature}
CharNgramsExtractor(n=2, lowercase=False, within_words=False, tokenizer=None)
```

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor"

The class extends the `CharNgramsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) core with the hook of Spanish: its default word tokenizer for `within_words`, the method `tokenize(text)`, is the default tokenizer of [`WordsExtractor`](words.md), the rule-based tokenizer of the [spaCy](https://github.com/explosion/spaCy) Spanish language class `ests.utils.tokenize`. The list of N-grams is passed to [`delta`](../corpus/stylometry.md) as text units instead of words.

=== "Code"

    ``` python
    from ests import CharNgramsExtractor

    text = "El gato dormía  en la ventana, y el perro - en el suelo."

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    CharNgramsExtractor().extract(text)[:8]
    CharNgramsExtractor(n=4, lowercase=True, within_words=True).extract(text)
    ```

=== "Result"

    ```
    ('el ', 'l g', ' ga', 'gat', 'ato', 'to ')
    ('El', 'l ', ' g', 'ga', 'at', 'to', 'o ', ' d')
    ('gato', 'dorm', 'ormí', 'rmía', 'vent', 'enta', 'ntan', 'tana', 'perr', 'erro', 'suel', 'uelo')
    ```

## Parameters

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-parameters"

## Methods

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-extract"

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-get_most_common"

=== "Code"

    ``` python
    ce.get_most_common(2)
    ```

=== "Result"

    ```
    [('el ', 3), (' en', 2)]
    ```
