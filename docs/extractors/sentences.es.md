# Extracción de oraciones

!!! info ""
    **ests.extractors.SentsExtractor**

## Descripción

<!-- core: extractors/sentences.md:SentsExtractor 491dff1 -->
Clase para extraer oraciones de un texto. Permite usar distintos tokenizadores y fijar la longitud mínima y máxima de las oraciones extraídas.

## Ganchos del idioma

La clase extiende el `SentsExtractor` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/extractors/sentences/) con el gancho del español: su tokenizador por defecto, el método `sentenize(text)`, es el divisor por reglas `ests.utils.sentenize`.

!!! note "Nota"
    Una oración termina con un punto, un signo de exclamación o de interrogación o unos puntos suspensivos, seguidos opcionalmente de comillas o paréntesis de cierre, cuando la palabra siguiente empieza por mayúscula, cifra, signo de apertura `¿ ¡`, comilla o paréntesis de apertura o raya; una línea en blanco también cierra la oración. Una raya ante una palabra en minúscula abre un inciso del narrador y la oración continúa: `¿Vienes? —preguntó él.` es una oración, `¿Vienes? —Sí.` son dos. Las abreviaturas (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`), las iniciales (`J. L. Borges`) y los marcadores de lista al principio de la oración o de la línea (`1.`, `2.1.`, `IV.`) no cierran la oración, ni siquiera ante una mayúscula: `Llegó a las 5 p. m. Luego se fue.` queda como una sola oración. Una palabra en minúscula tras puntos suspensivos o signo de exclamación continúa la oración, y un salto de línea simple no la divide, así que los textos con líneas cortadas se tratan bien.

!!! note "Nota"
    Se puede pasar un pipeline de spaCy como tokenizador: `tokenizer=lambda text: (sent.text for sent in nlp(text).sents)`.

## Parámetros

<!-- core: extractors/sentences.md:SentsExtractor-parameters d136320 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizador o expresión regular; por defecto, el método `sentenize` |
| `min_len` | int | `0` | Longitud mínima de la oración extraída en caracteres, `0` sin límite |
| `max_len` | int | `0` | Longitud máxima de la oración extraída en caracteres, `0` sin límite |

!!! note "Nota"
    Una expresión regular como tokenizador es un separador: el texto se divide con `re.split`. A las oraciones de cualquier tokenizador se les quitan los espacios de los extremos antes de aplicar los límites de longitud, y las vacías se descartan.

## Métodos

### extract

<!-- core: extractors/sentences.md:SentsExtractor-extract 6c0a509 -->
Extrae las oraciones de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | str | `-` | Cadena de texto |

Ejemplo de extracción de oraciones con el tokenizador por defecto:

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import SentsExtractor

    # Preparar los datos
    text = "¿No tienes cien euros? ¡Ten cien amigos! El Sr. García lo dijo... Y se fue."

    # Extraer las oraciones
    se = SentsExtractor()
    se.extract(text)
    ```

    _Resultado_:

    ``` bash
    ('¿No tienes cien euros?', '¡Ten cien amigos!', 'El Sr. García lo dijo...', 'Y se fue.')
    ```

Ejemplo de extracción de oraciones con una expresión regular como tokenizador:

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar las bibliotecas
    import re
    from ests import SentsExtractor

    # Preparar los datos
    text = "No tengas 100 euros, ten 100 amigos"

    # Extraer las oraciones
    se = SentsExtractor(tokenizer=re.compile(r", "))
    se.extract(text)
    ```

    _Resultado_:

    ``` bash
    ('No tengas 100 euros', 'ten 100 amigos')
    ```
