# Extracción de N-gramas de caracteres

``` {.python .signature}
CharNgramsExtractor(n=2, lowercase=False, within_words=False, tokenizer=None)
```

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor afcd43e -->
Clase para extraer N-gramas de caracteres de un texto: secuencias de N caracteres tomadas con una ventana deslizante sobre la cadena. Los N-gramas de caracteres son un rasgo clásico de la estilometría y la atribución de autoría (Stamatatos 2009) y pueden sustituir a las palabras en medidas como la Delta de Burrows.

Las secuencias de espacios se reducen a un solo espacio y los signos de puntuación se conservan. Con `within_words=True` los N-gramas no cruzan los límites de las palabras: el texto se divide en palabras con el tokenizador, la puntuación se descarta y las palabras más cortas que N no producen N-gramas.

Excepciones:

- `ParameterError` - un `n` que no es un entero de al menos uno.

La clase extiende el `CharNgramsExtractor` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/extractors/char_ngrams/) con el gancho del español: su tokenizador de palabras por defecto para `within_words`, el método `tokenize(text)`, es el tokenizador por defecto de [`WordsExtractor`](words.md), el tokenizador por reglas de la clase de idioma español de [spaCy](https://github.com/explosion/spaCy) `ests.utils.tokenize`. La lista de N-gramas se pasa a [`delta`](../corpus/stylometry.md) como unidades del texto en lugar de las palabras.

=== "Código"

    ``` python
    from ests import CharNgramsExtractor

    text = "El gato dormía  en la ventana, y el perro - en el suelo."

    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)[:6]
    CharNgramsExtractor().extract(text)[:8]
    CharNgramsExtractor(n=4, lowercase=True, within_words=True).extract(text)
    ```

=== "Resultado"

    ```
    ('el ', 'l g', ' ga', 'gat', 'ato', 'to ')
    ('El', 'l ', ' g', 'ga', 'at', 'to', 'o ', ' d')
    ('gato', 'dorm', 'ormí', 'rmía', 'vent', 'enta', 'ntan', 'tana', 'perr', 'erro', 'suel', 'uelo')
    ```

## Parámetros

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-parameters 20eb078 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n` | `int` | `2` | Longitud del N-grama en caracteres |
| `lowercase` | `bool` | `False` | Convertir el texto a minúsculas |
| `within_words` | `bool` | `False` | Tomar los N-gramas solo dentro de las palabras |
| `tokenizer` | `Pattern` / `Callable` | `None` | Tokenizador de palabras para `within_words` o expresión regular; por defecto, el método `tokenize` |

## Métodos

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-extract 8089d17 -->
`extract(text)` extrae los N-gramas de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Cadena de texto |

Un texto que no es una cadena lanza `SourceTypeError`, y también, con `within_words`, un tokenizador que no es invocable o no devuelve cadenas.

<!-- core: extractors/char_ngrams.md:CharNgramsExtractor-get_most_common 660dfe8 -->
`get_most_common(n=10)` devuelve los N-gramas más frecuentes del texto como una lista de pares (N-grama, frecuencia), el más frecuente primero.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n` | `int` | `10` | Número de N-gramas más frecuentes |

Un número que no es un entero de al menos uno lanza `ParameterError`.

!!! warning "Aviso"
    El método debe llamarse después de extraer los N-gramas con `extract`.

=== "Código"

    ``` python
    ce.get_most_common(2)
    ```

=== "Resultado"

    ```
    [('el ', 3), (' en', 2)]
    ```
