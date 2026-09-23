# Sentence extraction

!!! info ""
    **ests.extractors.SentsExtractor**

## Description

A module for extracting sentences from a text. It allows using different tokenizers and setting the minimum and maximum length of extracted sentences.

!!! note "Note"
    The default tokenizer is the rule-based function `sentenize` from `ests.utils`. A sentence ends with a period, an exclamation or question mark or an ellipsis, optionally followed by closing quotes or brackets, when the next word starts with an upper-case letter, a digit, an inverted mark `¿ ¡`, an opening quote or bracket or a dash; a blank line ends a sentence too. Abbreviations (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`), capital initials (`J. L. Borges`) and list markers at the start of a sentence or a line (`1.`, `2.1.`, `IV.`) do not end a sentence - which is a deliberate trade: `Llegó a las 5 p. m. Luego se fue.` stays one sentence, because no rule can tell it from `a las 5 p. m. del jueves`, and joining two sentences costs less than cutting one in half - a lower-case word after an ellipsis or an exclamation mark continues it, and a single line break does not split it, so hard-wrapped texts are handled. The sentences are returned without surrounding whitespace.

!!! note "Note"
    The `sentencizer` of spaCy is not used on purpose: it attaches `¡` and `«` to the previous sentence and does not split at `...`. A spaCy pipeline can still be passed as the tokenizer: `tokenizer=lambda text: (sent.text for sent in nlp(text).sents)`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizer or regular expression |
| `min_len` | int | `0` | Minimum length of an extracted sentence |
| `max_len` | int | `0` | Maximum length of an extracted sentence |

## Methods

### extract

Extracts sentences from a text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | str | `-` | Text string |

An example of sentence extraction with the default tokenizer:

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import SentsExtractor

    # Prepare the data
    text = "¿No tienes cien euros? ¡Ten cien amigos! El Sr. García lo dijo... Y se fue."

    # Extract sentences
    se = SentsExtractor()
    se.extract(text)
    ```

    _Result_:

    ``` bash
    ('¿No tienes cien euros?', '¡Ten cien amigos!', 'El Sr. García lo dijo...', 'Y se fue.')
    ```

An example of sentence extraction with a regular expression as the tokenizer:

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import re
    from ests import SentsExtractor

    # Prepare the data
    text = "No tengas 100 euros, ten 100 amigos"

    # Extract sentences
    se = SentsExtractor(tokenizer=re.compile(r", "))
    se.extract(text)
    ```

    _Result_:

    ``` bash
    ('No tengas 100 euros', 'ten 100 amigos')
    ```
