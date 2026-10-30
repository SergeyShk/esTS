# Extracción de oraciones

``` {.python .signature}
SentsExtractor(tokenizer=None, min_len=0, max_len=0)
```

<!-- core: extractors/sentences.md:SentsExtractor d5ffb52 -->
Clase para extraer oraciones de un texto.

Excepciones:

- `ParameterError` - un límite de longitud que no es un entero, un límite negativo, un mínimo mayor que el máximo.

La clase extiende el `SentsExtractor` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) con el gancho del español: su tokenizador por defecto, el método `sentenize(text)`, es el divisor por reglas `ests.utils.sentenize`.

!!! note "Nota"
    Una oración termina con un punto, un signo de exclamación o de interrogación o unos puntos suspensivos, seguidos opcionalmente de comillas o paréntesis de cierre, cuando la palabra siguiente empieza por mayúscula, cifra, signo de apertura `¿ ¡`, comilla o paréntesis de apertura o raya, también una raya pegada al signo cuando le sigue una letra o un signo de apertura en la misma línea (`baja.--Tiene`, como en las ediciones de Project Gutenberg), mientras que una raya pegada al signo ante un espacio o un salto de línea cierra su parlamento y se queda con él (`¡Traidores!--`, `viuda.-- El niño`); una línea en blanco también cierra la oración. Una raya ante una palabra en minúscula abre un inciso del narrador y la oración continúa: `¿Vienes? —preguntó él.` es una oración, `¿Vienes? —Sí.` son dos. Las abreviaturas (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`), las iniciales (`J. L. Borges`) y los marcadores de lista al principio de la oración o de la línea (`1.`, `2.1.`, `IV.`) no cierran la oración, ni siquiera ante una mayúscula: `Llegó a las 5 p. m. Luego se fue.` queda como una sola oración. Una palabra en minúscula tras puntos suspensivos o signo de exclamación continúa la oración, y un salto de línea simple no la divide, así que los textos con líneas cortadas se tratan bien.

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

<!-- core: extractors/sentences.md:SentsExtractor-parameters df5b0a4 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `tokenizer` | `Pattern` / `Callable` | `None` | Tokenizador o expresión regular; por defecto, el método `sentenize` |
| `min_len` | `int` | `0` | Longitud mínima de la oración extraída en caracteres, `0` sin límite |
| `max_len` | `int` | `0` | Longitud máxima de la oración extraída en caracteres, `0` sin límite |

!!! note "Nota"
    Una expresión regular como tokenizador es un separador para `re.split`. Una línea en blanco - un salto de línea, espacios opcionales y otro salto de línea - termina una oración con cualquier tokenizador: el texto se divide primero por las líneas en blanco y cada parte pasa al tokenizador, así que un título o un párrafo sin signo final es una oración propia, y también lo es una parte sin palabras, como una línea de asteriscos, que las estadísticas descartan. A las oraciones se les quitan los espacios de los extremos antes de aplicar los límites de longitud, y las vacías se descartan.

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

    SentsExtractor().extract("Novedades\n\nImportación más rápida\nMenos errores\n\n¡Gracias!")
    SentsExtractor(tokenizer=re.compile(r", ")).extract("No tengas 100 euros, ten 100 amigos")
    ```

=== "Resultado"

    ```
    ('Novedades', 'Importación más rápida\nMenos errores', '¡Gracias!')
    ('No tengas 100 euros', 'ten 100 amigos')
    ```

## Párrafos { #split_paragraphs }

<!-- core: extractors/sentences.md:split_paragraphs 3fe9d43 -->
``` {.python .signature}
split_paragraphs(text)
```

Los párrafos de un texto: sus partes entre líneas en blanco, sin los espacios de sus extremos; una parte solo de espacios no es un párrafo. Una línea en blanco (`BLANK_LINE`) son dos saltos de línea - `\n`, `\r\n`, `\r`, U+0085 o U+2028 - con solo espacios entre ellos, donde el espacio de anchura cero y la marca de orden de bytes cuentan como espacios, o un separador de párrafo U+2029; también termina las oraciones de `SentsExtractor` y los párrafos de `CohesionStats`. Las palabras de los párrafos dan los tamaños de las partes de `dispersion` por párrafo; un párrafo sin palabras, como una separación de escenas con asteriscos, sigue siendo un párrafo. Un texto que no es una cadena lanza `SourceTypeError`.

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
