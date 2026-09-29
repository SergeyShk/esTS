# Sentence extraction

!!! info ""
    **ests.extractors.SentsExtractor**

## Description

--8<-- "extractors/sentences.md:SentsExtractor"

## Language hooks

The class extends the `SentsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) core with the hook of Spanish: its default tokenizer, the method `sentenize(text)`, is the rule-based splitter `ests.utils.sentenize`.

!!! note "Note"
    A sentence ends with a period, an exclamation or question mark or an ellipsis, optionally followed by closing quotes or brackets, when the next word starts with an upper-case letter, a digit, an inverted mark `¿ ¡`, an opening quote or bracket or a dash, a dash glued to the mark included (`baja.--Tiene`, as in the editions of Project Gutenberg); a blank line ends a sentence too. A dash before a lower-case word opens a remark of the narrator and keeps the sentence going: `¿Vienes? —preguntó él.` is one sentence, `¿Vienes? —Sí.` two. Abbreviations (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`), capital initials (`J. L. Borges`) and list markers at the start of a sentence or a line (`1.`, `2.1.`, `IV.`) do not end a sentence, even before an upper-case word: `Llegó a las 5 p. m. Luego se fue.` stays one sentence. A lower-case word after an ellipsis or an exclamation mark continues the sentence, and a single line break does not split it, so hard-wrapped texts are handled.

!!! note "Note"
    A spaCy pipeline can be passed as the tokenizer: `tokenizer=lambda text: (sent.text for sent in nlp(text).sents)`.

## Parameters

--8<-- "extractors/sentences.md:SentsExtractor-parameters"

## Methods

### extract

--8<-- "extractors/sentences.md:SentsExtractor-extract"

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
