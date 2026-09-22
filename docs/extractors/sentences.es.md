# Extracción de oraciones

!!! info ""
    **ests.extractors.SentsExtractor**

## Descripción

Módulo para extraer oraciones de un texto. Permite usar distintos tokenizadores y fijar la longitud mínima y máxima de las oraciones extraídas.

!!! note "Nota"
    El tokenizador por defecto es la función `sentenize` de `ests.utils`, basada en reglas. Una oración termina con un punto, un signo de exclamación o de interrogación o unos puntos suspensivos, seguidos opcionalmente de comillas o paréntesis de cierre, cuando la palabra siguiente empieza por mayúscula, cifra, signo de apertura `¿ ¡`, comilla o paréntesis de apertura o raya; una línea en blanco también cierra la oración. Las abreviaturas (`Sr.`, `Dra.`, `p. ej.`, `EE. UU.`, `a. m.`) y las iniciales (`J. L. Borges`) no cierran la oración, una palabra en minúscula tras puntos suspensivos o signo de exclamación la continúa, y un salto de línea simple no la divide, así que los textos con líneas cortadas se tratan bien. Las oraciones se devuelven sin espacios en los extremos.

!!! note "Nota"
    El `sentencizer` de spaCy no se usa a propósito: pega `¡` y `«` a la oración anterior y no corta en `...`. Aun así se puede pasar un pipeline de spaCy como tokenizador: `tokenizer=lambda text: (sent.text for sent in nlp(text).sents)`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizador o expresión regular |
| `min_len` | int | `0` | Longitud mínima de la oración extraída |
| `max_len` | int | `0` | Longitud máxima de la oración extraída |

## Métodos

### extract

Extrae las oraciones de un texto.

Parámetros:

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
