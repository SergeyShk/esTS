# Character N-gram extraction

!!! info ""
    **ests.extractors.CharNgramsExtractor**

## Description

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor"

## Language hooks

The class extends the `CharNgramsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) core with the hook of Spanish: its default word tokenizer for `within_words`, the method `tokenize(text)`, is the default tokenizer of [WordsExtractor](words.md), the rule-based tokenizer of the [spaCy](https://github.com/explosion/spaCy) Spanish language class `ests.utils.tokenize`.

## Parameters

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-parameters"

## Methods

### extract

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-extract"

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

--8<-- "extractors/char_ngrams.md:CharNgramsExtractor-get_most_common"

!!! example "Example"

    ``` python
    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)
    ce.get_most_common(2)
    # [('el ', 3), (' en', 2)]
    ```
