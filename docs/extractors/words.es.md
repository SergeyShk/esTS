# Extracción de palabras

!!! info ""
    **ests.extractors.WordsExtractor**

## Descripción

Módulo para extraer palabras de un texto. Permite usar distintos tokenizadores, filtrar palabras vacías, números y signos de puntuación, lematizar, construir N-gramas y fijar la longitud mínima y máxima de las palabras extraídas.

!!! note "Nota"
    El tokenizador por defecto es el tokenizador por reglas de la clase de idioma español de [spaCy](https://github.com/explosion/spaCy) (`ests.utils.tokenize`); no necesita un modelo entrenado. Los signos de puntuación, incluidos `¿` y `¡`, los números como `1.500,50`, `3.º`, `1990-1995` y las abreviaturas como `Sr.`, `EE. UU.` son tokens únicos; las palabras con pronombres enclíticos (`dámelo`, `decírselo`) no se separan.

!!! note "Nota"
    Los lemas provienen de [simplemma](https://github.com/adbar/simplemma) (`ests.utils.lemmatize`), que trabaja con un diccionario sin modelo entrenado: una forma conocida se convierte en su lema en minúsculas (`Tienes` - `tener`, `NIÑOS` - `niño`), una forma desconocida se devuelve sin cambios (`Madrid`, `dámelo`).

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `tokenizer` | Pattern/Callable | `None` | Tokenizador o expresión regular |
| `filter_punct` | bool | `True` | Filtrar los signos de puntuación |
| `filter_nums` | bool | `False` | Filtrar los números, incluidos rangos, fracciones, fechas, horas, porcentajes y ordinales (1990-1995, 1.500,50, 12/03/2020, 3:30, 10%, 3.º, 1.ª, 2do) |
| `use_lexemes` | bool | `False` | Usar los lemas de las palabras |
| `stopwords` | Collection[str] | `None` | Palabras vacías |
| `lowercase` | bool | `False` | Convertir las palabras a minúsculas |
| `ngram_range` | Tuple[int, int] | `(1, 1)` | Límite inferior y superior del tamaño de los N-gramas |
| `min_len` | int | `0` | Longitud mínima de la palabra extraída |
| `max_len` | int | `0` | Longitud máxima de la palabra extraída |

!!! note "Nota"
    Los filtros se aplican en este orden: puntuación, números, lematización, minúsculas, palabras vacías, longitud de la palabra. Las palabras vacías se comparan después de pasar a minúsculas, así que con `lowercase=True` basta con que la lista esté en minúsculas. Un signo de puntuación es un token formado solo por signos y símbolos, también de varios caracteres: `?!`, `!..`, `--`, `…`, `€`. Una lista de palabras vacías ya hecha es `spacy.lang.es.stop_words.STOP_WORDS`; téngase en cuenta que incluye verbos frecuentes como `tener`.

## Métodos

### extract

Extrae las palabras de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | str | `-` | Cadena de texto |

Ejemplo de extracción de palabras con bigramas como tokens, tras filtrar números y palabras vacías y lematizar:

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import WordsExtractor

    # Preparar los datos
    text = "No tengas 100 euros, ten 100 amigos"

    # Extraer las palabras
    we = WordsExtractor(use_lexemes=True, stopwords=["no"], filter_nums=True, ngram_range=(1, 2))
    we.extract(text)
    ```

    _Resultado_:

    ``` bash
    ('tener', 'euro', 'tener', 'amigo', 'tener_euro', 'euro_tener', 'tener_amigo')
    ```

### get_most_common

Devuelve un contador de las palabras más frecuentes del texto. Recibe como parámetro el número de palabras a devolver.

Para ilustrar el método reutilizamos el código del ejemplo anterior:

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar las palabras más frecuentes
    we.get_most_common(3)
    ```

    _Resultado_:

    ``` bash
    [('tener', 2), ('euro', 1), ('amigo', 1)]
    ```

!!! warning "Aviso"
    El método debe llamarse después de extraer las palabras con `extract`.
