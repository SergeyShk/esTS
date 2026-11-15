# Extracción de palabras

``` {.python .signature}
WordsExtractor(tokenizer=None, filter_punct=True, filter_nums=False, use_lexemes=False, stopwords=None, lowercase=False, ngram_range=(1, 1), min_len=0, max_len=0)
```

<!-- core: extractors/words.md:WordsExtractor ee077d8 -->
Clase para extraer palabras de un texto.

Excepciones:

- `ParameterError` - un `ngram_range` que no es un par de enteros o cuyo límite inferior es menor que uno o mayor que el superior, un límite de longitud que no es un entero, un límite negativo, un mínimo mayor que el máximo, un interruptor que no es un `bool`;
- `SourceTypeError` - palabras vacías que no son una colección de cadenas.

La clase extiende el `WordsExtractor` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/extractors/words/) con los ganchos del español:

| Gancho | Español |
| :----- | :------ |
| `tokenize(text)` | los tokens del segmentador [anySeg](https://github.com/SergeyShk/anySeg), `ests.utils.iter_tokens` |
| `lemmatize(word)` | los lemas de simplemma, `ests.utils.lemmatize` |
| `number_pattern` | números con signo, rangos, fracciones, fechas, horas, porcentajes y ordinales: `-5`, `+7`, `1990-1995`, `1.500,50`, `12/03/2020`, `3:30`, `10%`, `3.º`, `1.ª`, `2do` |

!!! note "Nota"
    El segmentador no necesita un modelo entrenado; sus tokens siguen las convenciones de UD para el español (AnCora). Los signos de puntuación, incluidos `¿` y `¡`, los números como `1.500,50`, `3.º`, `1990-1995`, las contracciones `del` y `al` y las abreviaturas como `Sr.`, `p.ej.` son tokens únicos; una abreviatura escrita con espacios da un token por cada parte (`EE.`, `UU.`), y una en mayúsculas conserva su punto ante mayúsculas o una cifra (`VÉASE PÁG. 5`). El punto de una abreviatura que cierra una oración es un token aparte: `etc.` al final de una oración da la palabra `etc`. Las palabras con pronombres enclíticos (`dámelo`) no se separan. Las rayas de un diálogo pegadas a las palabras se separan: `--No`, `sí--dijo`, `―dijo él―.` dan las palabras `No`, `sí`, `dijo`, `él`, también junto a los guiones bajos de la cursiva (`--_Siguro_`), mientras que un guion entre letras (`franco-alemán`) o ante una cifra (`-5`) se queda en su token; un sufijo citado con su guion (`-mente`) también lo pierde, y lo mismo el número de un punto de una lista (`Artículo 1.- El objeto` da el número `1`). Una marca de orden de bytes, como en un fichero leído con `utf-8` en lugar de `utf-8-sig`, no es un token, y un sustituto (surrogate) aislado es un token propio. `ests.utils.add_dash_rules(nlp)` añade reglas para las rayas y las abreviaturas al tokenizador de un pipeline de spaCy propio; el modelo de `get_nlp` ya las tiene, y los [componentes](../components.md) de la biblioteca las añaden a su pipeline.

!!! note "Nota"
    [simplemma](https://github.com/adbar/simplemma) trabaja con un diccionario sin modelo entrenado: una forma conocida se convierte en su lema en minúsculas (`Tienes` - `tener`, `NIÑOS` - `niño`), una forma desconocida se devuelve sin cambios (`Madrid`, `dámelo`).

=== "Código"

    ``` python
    from ests import WordsExtractor

    text = "No tengas 100 euros, ten 100 amigos"

    we = WordsExtractor(use_lexemes=True, stopwords=["no"], filter_nums=True, ngram_range=(1, 2))
    we.extract(text)
    ```

=== "Resultado"

    ```
    ('tener', 'euro', 'tener', 'amigo', 'tener_euro', 'euro_tener', 'tener_amigo')
    ```

## Parámetros

<!-- core: extractors/words.md:WordsExtractor-parameters 234b185 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `tokenizer` | `Pattern` / `Callable` | `None` | Tokenizador o expresión regular; por defecto, el método `tokenize` |
| `filter_punct` | `bool` | `True` | Filtrar los signos de puntuación |
| `filter_nums` | `bool` | `False` | Filtrar los números que reconoce `number_pattern` |
| `use_lexemes` | `bool` | `False` | Usar los lemas de las palabras del método `lemmatize` |
| `stopwords` | `Collection[str]` | `None` | Palabras vacías, comparadas sin distinguir mayúsculas |
| `lowercase` | `bool` | `False` | Convertir las palabras a minúsculas |
| `ngram_range` | `tuple[int, int]` | `(1, 1)` | Límite inferior y superior del tamaño de los N-gramas |
| `min_len` | `int` | `0` | Longitud mínima de la palabra extraída en caracteres, `0` sin límite |
| `max_len` | `int` | `0` | Longitud máxima de la palabra extraída en caracteres, `0` sin límite |

!!! note "Nota"
    Una expresión regular como tokenizador es un separador para `re.split`. Los filtros se aplican en este orden: puntuación, números, lematización, minúsculas, palabras vacías, longitud de la palabra. Un signo de puntuación es un token solo de signos y símbolos, también de varios caracteres: `?!`, `--`, `…`, `€` (`anyts.utils.is_punctuation`). Los tokens vacíos y de espacios se descartan antes de los filtros. Los N-gramas unen las palabras con `_`.

!!! note "Nota"
    Una lista de palabras vacías ya hecha es `spacy.lang.es.stop_words.STOP_WORDS`; téngase en cuenta que incluye verbos frecuentes como `tener`.

## Métodos

<!-- core: extractors/words.md:WordsExtractor-extract 383f135 -->
`extract(text)` extrae las palabras de un texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Cadena de texto |

Un texto que no es una cadena y un tokenizador que no es invocable o no devuelve cadenas lanzan `SourceTypeError`.

<!-- core: extractors/words.md:WordsExtractor-get_most_common 7c47d0f -->
`get_most_common(n=10)` devuelve las palabras más frecuentes del texto como una lista de pares (palabra, frecuencia), la más frecuente primero.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n` | `int` | `10` | Número de palabras más frecuentes |

Un número que no es un entero de al menos uno lanza `ParameterError`.

!!! warning "Aviso"
    El método debe llamarse después de extraer las palabras con `extract`.

=== "Código"

    ``` python
    we.get_most_common(3)
    ```

=== "Resultado"

    ```
    [('tener', 2), ('euro', 1), ('amigo', 1)]
    ```
