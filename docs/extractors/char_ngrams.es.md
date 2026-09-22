# Extracción de N-gramas de caracteres

!!! info ""
    **ests.extractors.CharNgramsExtractor**

## Descripción

Módulo para extraer N-gramas de caracteres de un texto: secuencias de N caracteres tomadas con una ventana deslizante sobre la cadena. Los N-gramas de caracteres son un rasgo clásico de la estilometría y la atribución de autoría (Stamatatos 2009): recogen morfología, puntuación y combinaciones de letras típicas sin lematizar. La lista de N-gramas se pasa a la Delta de Burrows como unidades del texto en lugar de las palabras.

Las secuencias de espacios se reducen antes a un solo espacio y los signos de puntuación se conservan: un espacio o un signo dentro de un N-grama también es una señal de estilo. Con `within_words=True` los N-gramas no cruzan los límites de las palabras: el texto se divide en palabras con el tokenizador, la puntuación se descarta y las palabras más cortas que N no producen N-gramas.

!!! note "Nota"
    El tokenizador de palabras por defecto para `within_words` es el de la clase de idioma español de [spaCy](https://github.com/explosion/spaCy) (`ests.utils.tokenize`).

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n` | int | `2` | Longitud del N-grama en caracteres |
| `lowercase` | bool | `False` | Convertir el texto a minúsculas |
| `within_words` | bool | `False` | Tomar los N-gramas solo dentro de las palabras |
| `tokenizer` | Pattern/Callable | `None` | Tokenizador de palabras para `within_words` o expresión regular |

## Métodos

### extract

Extrae los N-gramas de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | str | `-` | Cadena de texto |

!!! example "Ejemplo"

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

Devuelve los N-gramas más frecuentes de la última extracción.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n` | int | `10` | Número de N-gramas |

!!! example "Ejemplo"

    ``` python
    ce = CharNgramsExtractor(n=3, lowercase=True)
    ce.extract(text)
    ce.get_most_common(2)
    # [('el ', 3), (' en', 2)]
    ```
