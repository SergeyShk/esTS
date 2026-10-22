# Sentence extraction

``` {.python .signature}
SentsExtractor(tokenizer=None, min_len=0, max_len=0)
```

--8<-- "extractors/sentences.md:SentsExtractor"

The class extends the `SentsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) core with the hook of Spanish: its default tokenizer, the method `sentenize(text)`, is the rule-based splitter `ests.utils.sentenize`.

!!! note "Note"
    A sentence ends with a period, an exclamation or question mark or an ellipsis, optionally followed by closing quotes or brackets, when the next word starts with an upper-case letter, a digit, an inverted mark `¿ ¡`, an opening quote or bracket or a dash, a dash glued to the mark included when a letter or an opening mark follows it on the same line (`baja.--Tiene`, as in the editions of Project Gutenberg), while a dash glued to the mark before whitespace closes its line of dialogue and stays with it (`¡Traidores!--`, `viuda.-- El niño`); a blank line ends a sentence too. A dash before a lower-case word opens a remark of the narrator and keeps the sentence going: `¿Vienes? —preguntó él.` is one sentence, `¿Vienes? —Sí.` two. Abbreviations (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`), capital initials (`J. L. Borges`) and list markers at the start of a sentence or a line (`1.`, `2.1.`, `IV.`) do not end a sentence, even before an upper-case word: `Llegó a las 5 p. m. Luego se fue.` stays one sentence. A lower-case word after an ellipsis or an exclamation mark continues the sentence, and a single line break does not split it, so hard-wrapped texts are handled.

=== "Code"

    ``` python
    from ests import SentsExtractor

    text = "¿No tienes cien euros? ¡Ten cien amigos! El Sr. García lo dijo... Y se fue."
    SentsExtractor().extract(text)
    ```

=== "Result"

    ```
    ('¿No tienes cien euros?', '¡Ten cien amigos!', 'El Sr. García lo dijo...', 'Y se fue.')
    ```

## Parameters

--8<-- "extractors/sentences.md:SentsExtractor-parameters"

--8<-- "extractors/sentences.md:SentsExtractor-pipeline"

## Methods

--8<-- "extractors/sentences.md:SentsExtractor-extract"

=== "Code"

    ``` python
    import re

    SentsExtractor().extract("Novedades\n\nImportación más rápida\nMenos errores\n\n¡Gracias!")
    SentsExtractor(tokenizer=re.compile(r", ")).extract("No tengas 100 euros, ten 100 amigos")
    ```

=== "Result"

    ```
    ('Novedades', 'Importación más rápida\nMenos errores', '¡Gracias!')
    ('No tengas 100 euros', 'ten 100 amigos')
    ```
