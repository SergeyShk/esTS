# Extracción de oraciones

``` {.python .signature}
SentsExtractor(tokenizer=None, min_len=0, max_len=0)
```

<!-- core: extractors/sentences.md:SentsExtractor d5ffb52 -->
Clase para extraer oraciones de un texto.

Excepciones:

- `ParameterError` - un límite de longitud que no es un entero, un límite negativo, un mínimo mayor que el máximo.

La clase extiende el `SentsExtractor` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) con el gancho del español: su tokenizador por defecto, el método `sentenize(text)`, es el segmentador [anySeg](https://github.com/SergeyShk/anySeg) (`ests.utils.iter_text_sents`).

!!! note "Nota"
    Una oración termina con un punto, un signo de exclamación o de interrogación o unos puntos suspensivos, seguidos opcionalmente de comillas o paréntesis de cierre, cuando la palabra siguiente empieza por mayúscula, cifra, signo de apertura `¿ ¡`, comilla o paréntesis de apertura o raya, también una raya pegada al signo cuando le sigue una letra o un signo de apertura en la misma línea (`baja.--Tiene`, como en las ediciones de Project Gutenberg), mientras que una raya pegada al signo ante un espacio o un salto de línea cierra su parlamento y se queda con él (`¡Traidores!--`, `viuda.-- El niño`). Una raya ante una palabra en minúscula abre un inciso del narrador y la oración continúa: `¿Vienes? —preguntó él.` es una oración, `¿Vienes? —Sí.` son dos. Las abreviaturas (`Sr.`, `Dra.`, `p. ej.`), las iniciales (`J. L. Borges`) y los marcadores de lista al principio de la oración o de la línea (`1.`, `IV.`) no cierran la oración; una abreviatura que puede cerrarla (`etc.`, `p. m.`, `EE. UU.`) la cierra ante una mayúscula, y su punto sirve de punto final: `Llegó a las 5 p. m. Luego se fue.` son dos oraciones. Una palabra en minúscula tras puntos suspensivos o signo de exclamación continúa la oración. Una línea en blanco cierra la oración, y también una línea sin signo final ante una línea que empieza por mayúscula, raya o marcador de lista (un título, un elemento de una lista); un salto de línea ante una palabra en minúscula no divide la oración, así que los textos con líneas cortadas se tratan bien.

=== "Código"

    ``` python
    from ests import SentsExtractor

    text = "¿No tienes cien euros? ¡Ten cien amigos! El Sr. García lo dijo... Y se fue."
    SentsExtractor().extract(text)
    ```

=== "Resultado"

    ```
    ('¿No tienes cien euros?', '¡Ten cien amigos!', 'El Sr. García lo dijo...', 'Y se fue.')
    ```

## Parámetros

<!-- core: extractors/sentences.md:SentsExtractor-parameters b09d3ad -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `tokenizer` | `Pattern` / `Callable` | `None` | Tokenizador o expresión regular; por defecto, el método `sentenize` |
| `min_len` | `int` | `0` | Longitud mínima de la oración extraída en caracteres, `0` sin límite |
| `max_len` | `int` | `0` | Longitud máxima de la oración extraída en caracteres, `0` sin límite |

!!! note "Nota"
    Una expresión regular como tokenizador es un separador para `re.split`. Una línea en blanco (`BLANK_LINE`) termina una oración con cualquier tokenizador: el texto se divide primero por las líneas en blanco y cada parte pasa al tokenizador, así que un título o un párrafo sin signo final es una oración propia, y también lo es una parte sin palabras, como una línea de asteriscos, que las estadísticas descartan. A las oraciones se les quitan los espacios, los caracteres de control y los separadores invisibles (el guion blando, los caracteres de anchura cero, la marca de orden de bytes) de los extremos antes de aplicar los límites de longitud, y las vacías se descartan.

<!-- core: extractors/sentences.md:SentsExtractor-pipeline 13ed66c -->
!!! note "Nota"
    Se puede pasar un pipeline de spaCy como tokenizador: `tokenizer=lambda text: (sent.text for sent in nlp(text).sents)`.

## Métodos

<!-- core: extractors/sentences.md:SentsExtractor-extract 10444dc -->
`extract(text)` extrae las oraciones de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Cadena de texto |

Un texto que no es una cadena y un tokenizador que no es invocable o no devuelve cadenas lanzan `SourceTypeError`.

=== "Código"

    ``` python
    import re

    SentsExtractor().extract("Novedades\n\nImportación más\nrápida. Menos errores\n\n¡Gracias!")
    SentsExtractor(tokenizer=re.compile(r", ")).extract("No tengas 100 euros, ten 100 amigos")
    ```

=== "Resultado"

    ```
    ('Novedades', 'Importación más\nrápida.', 'Menos errores', '¡Gracias!')
    ('No tengas 100 euros', 'ten 100 amigos')
    ```

## Párrafos { #split_paragraphs }

<!-- core: extractors/sentences.md:split_paragraphs db688fc -->
``` {.python .signature}
split_paragraphs(text)
```

Los párrafos de un texto: sus partes entre líneas en blanco, sin los espacios, los caracteres de control y los separadores invisibles (el guion blando, los caracteres de anchura cero, la marca de orden de bytes) de sus extremos; una parte sin nada más no es un párrafo. Una línea en blanco (`BLANK_LINE`) son dos saltos de línea - `\n`, `\r\n`, `\r`, la tabulación vertical, el salto de página, U+0085 o U+2028 - sin nada más que esos caracteres entre ellos, o un separador de párrafo U+2029: un salto de párrafo de anySeg, así que estos son también los párrafos de un [documento](https://sergeyshk.github.io/anyTS/document/); también termina las oraciones de `SentsExtractor` y los párrafos de `CohesionStats` con `blank_lines`. Las palabras de los párrafos dan los tamaños de las partes de `dispersion` por párrafo; un párrafo sin palabras, como una separación de escenas con asteriscos, sigue siendo un párrafo. Un texto que no es una cadena lanza `SourceTypeError`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Cadena de texto |

En esTS la función se importa de `ests.extractors`; las palabras de los párrafos dan a [`dispersion`](../corpus/dispersion.md) los tamaños de sus partes.

=== "Código"

    ``` python
    from ests.extractors import split_paragraphs

    split_paragraphs("Capítulo I\n\nEra una noche oscura.\nLlovía.\n\n* * *\n\nAmaneció.")
    ```

=== "Resultado"

    ```
    ['Capítulo I', 'Era una noche oscura.\nLlovía.', '* * *', 'Amaneció.']
    ```
