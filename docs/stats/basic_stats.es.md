# Estadísticas básicas

``` {.python .signature}
BasicStats(source, sents_extractor=None, words_extractor=None, normalize=False, complex_syl_factor=3, long_word_letter_factor=7)
```

<!-- core: stats/basic_stats.md:BasicStats c1092e0 -->
Las estadísticas básicas de un texto: el número de sus oraciones, palabras, caracteres, sílabas y signos de puntuación y las distribuciones de sus palabras. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy). Las letras se cuentan con `str.isalpha`, así que las cifras, los guiones y los signos dentro de una palabra no son letras.

Las palabras y las oraciones de una cadena salen de los extractores. Un `Doc` da sus tokens como palabras, sin los signos de puntuación ni los símbolos como `€` o `%`, y sus límites como oraciones, o los del extractor de oraciones cuando no los tiene o solo tiene algunos (`has_sents`); un extractor indicado se usa en su lugar, sobre su texto. Una línea en blanco termina una oración de una cadena y de un `Doc` sin límites; un `Doc` con límites también, cuando su pipeline tiene `start_sents_after_blank_lines` (que una biblioteca del idioma registra con su propio nombre) antes del parser, `senter` o `sentencizer`. Una oración sin palabras, como una de pura puntuación, no se cuenta.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un extractor de otro tipo;
- `SourceError` - una fuente sin palabras;
- `ParameterError` - un umbral que no es un entero de al menos uno, un `normalize` que no es un `bool`.

La clase extiende el `BasicStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/basic_stats/) con los ganchos del español: las sílabas de una palabra se cuentan con [`count_syllables`](../syllables.md#count_syllables), y los extractores por defecto son los [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) del español. Los indicadores ordinales `º` y `ª` son letras (`3.º` es una palabra de una letra). El componente de líneas en blanco de esTS se llama [`ests_blank_lines`](../components.md#blank_lines): `nlp.add_pipe("ests_blank_lines", before="parser")`. Las estadísticas se calculan al crear el objeto. Una cadena con un carácter sin forma UTF-8, como la de un fichero leído con una codificación errónea, lanza `SourceError` desde el tokenizador del español.

=== "Código"

    ``` python
    from ests import BasicStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    bs = BasicStats(text, normalize=True)
    bs.print_stats()
    ```

=== "Resultado"

    ```
                       Statistic                    |  Value
    -----------------------------------------------------------
    Sentences                                       |    1
    Words                                           |    10
    Unique words                                    |    8
    Long words                                      |    5
    Complex words                                   |    5
    Simple words                                    |    5
    Monosyllabic words                              |    4
    Polysyllabic words                              |    6
    Characters                                      |    71
    Letters                                         |    60
    Spaces                                          |    9
    Syllables                                       |    23
    Punctuation marks                               |    2
    Entropy of the word lengths in letters (bits)   |   2.52
    Entropy of the word lengths in syllables (bits) |   1.72
    ```

## Parámetros

<!-- core: stats/basic_stats.md:BasicStats-parameters 362b585 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos (cadena u objeto Doc) |
| `sents_extractor` | `SentsExtractor` | `None` | Herramienta de extracción de oraciones; se usa también con un Doc, sobre su texto |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras; se usa también con un Doc, sobre su texto |
| `normalize` | `bool` | `False` | Calcular las estadísticas normalizadas |
| `complex_syl_factor` | `int` | `COMPLEX_SYL_FACTOR` | Número mínimo de sílabas de una palabra compleja |
| `long_word_letter_factor` | `int` | `LONG_WORD_LETTER_FACTOR` | Número mínimo de letras de una palabra larga |

El objeto guarda `normalize`, `complex_syl_factor` y `long_word_letter_factor` con sus nombres.

En esTS los umbrales son los del núcleo y de las fórmulas de legibilidad: una palabra compleja tiene tres o más sílabas, como en SMOG, y una palabra larga siete o más letras, como en LIX y RIX (`COMPLEX_SYL_FACTOR = 3` y `LONG_WORD_LETTER_FACTOR = 7` de `anyts.constants`).

## Estadísticas

<!-- core: stats/basic_stats.md:BasicStats-attributes d457364 -->
| Estadística | Tipo | Descripción | Normalizada |
| :-------- | :--- | :---------- | :--------- |
| `c_letters` | `dict[int, int]` | Distribución de las palabras por número de letras | - |
| `c_syllables` | `dict[int, int]` | Distribución de las palabras por número de sílabas | - |
| `n_sents` | `int` | Número de oraciones con palabras | - |
| `n_words` | `int` | Número de palabras | - |
| `n_unique_words` | `int` | Número de palabras únicas, sin distinguir mayúsculas | `p_unique_words` |
| `n_long_words` | `int` | Número de palabras largas, de al menos `long_word_letter_factor` letras | `p_long_words` |
| `n_complex_words` | `int` | Número de palabras complejas, de al menos `complex_syl_factor` sílabas | `p_complex_words` |
| `n_simple_words` | `int` | Número de palabras simples: con alguna sílaba, por debajo de las complejas | `p_simple_words` |
| `n_monosyllable_words` | `int` | Número de palabras monosílabas | `p_monosyllable_words` |
| `n_polysyllable_words` | `int` | Número de palabras polisílabas, de dos o más sílabas | `p_polysyllable_words` |
| `n_chars` | `int` | Número de caracteres sin los saltos de línea | - |
| `n_letters` | `int` | Número de letras | `p_letters` |
| `n_spaces` | `int` | Número de espacios de Unicode (categoría Zs), como el espacio de no separación, y tabulaciones | `p_spaces` |
| `n_syllables` | `int` | Número de sílabas | - |
| `n_punctuations` | `int` | Número de signos de puntuación | `p_punctuations` |
| `letters_entropy` | `float` | Entropía de Shannon en bits de las longitudes de las palabras en letras, de `c_letters`: 0 cuando las palabras tienen una sola longitud; la estimación a partir de las proporciones sale más baja en un texto corto, en décimas de bit con decenas de palabras | - |
| `syllables_entropy` | `float` | Entropía de Shannon en bits de las longitudes de las palabras en sílabas, de `c_syllables`, con el mismo sesgo | - |
| `c_punctuations` | `dict[str, int]` | Distribución de los signos de puntuación por tipo ([`count_punctuations`](#count_punctuations)) | - |

Con `normalize=True` el objeto tiene también las estadísticas normalizadas, de tipo `float`: los recuentos de palabras divididos por el número de palabras, los de caracteres por el número de caracteres.

## Métodos

<!-- core: stats/basic_stats.md:BasicStats-count_words_by abc6821 -->
`count_words_by_syllables(min_syllables)` y `count_words_by_letters(min_letters)` devuelven el número de palabras con al menos el número de sílabas o de letras indicado; un mínimo que no es un entero lanza `ParameterError`.

Los métodos vuelven a contar las palabras complejas y largas con un umbral distinto del fijado al crear el objeto; [`ReadabilityStats`](readability_stats.md) cuenta con ellos las palabras polisílabas de SOL y las palabras largas de LIX y RIX, así que estas no dependen de los umbrales del objeto.

<!-- core: stats/basic_stats.md:BasicStats-get_stats 5352c3c -->
`get_stats(flat)` devuelve un diccionario con las distribuciones `c_letters` y `c_syllables`, las estadísticas de `stats_desc`, la distribución `c_punctuations` y, con `normalize=True`, los recuentos normalizados, como una copia: editarlo no cambia el objeto. Con `flat=True` las distribuciones dan una clave por cada valor que tiene el texto, como `c_letters_3` y `c_punctuations_comma`.

<!-- core: stats/basic_stats.md:BasicStats-print_stats 129bbf6 -->
`print_stats()` muestra una tabla con las estadísticas de `stats_desc`, sus descripciones y los encabezados de `stats_headers`.

Las estadísticas normalizadas `p_*` no están en la tabla.

<!-- core: stats/stats.md:Stats-to_dataframe fb70c9b -->
`to_dataframe()` devuelve las estadísticas planas, `get_stats(flat=True)`, como un `DataFrame` de [pandas](https://pandas.pydata.org/) de una fila con una columna por cada clave. Una estadística de diccionario da columnas solo para las claves que tiene el texto, así que en los marcos de varios textos unidos con `pandas.concat` un recuento que le falta a un texto es `NaN`. Solo estas columnas pueden rellenarse con 0: en las demás `NaN` es un valor no definido.

=== "Código"

    ``` python
    bs.count_words_by_syllables(4), bs.count_words_by_letters(8)
    bs.get_stats()
    ```

=== "Resultado"

    ```
    (1, 5)
    {'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
     'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
     'n_sents': 1,
     'n_words': 10,
     'n_unique_words': 8,
     'n_long_words': 5,
     'n_complex_words': 5,
     'n_simple_words': 5,
     'n_monosyllable_words': 4,
     'n_polysyllable_words': 6,
     'n_chars': 71,
     'n_letters': 60,
     'n_spaces': 9,
     'n_syllables': 23,
     'n_punctuations': 2,
     'letters_entropy': 2.5219280948873624,
     'syllables_entropy': 1.7219280948873623,
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0},
     'p_unique_words': 0.8,
     'p_long_words': 0.5,
     'p_complex_words': 0.5,
     'p_simple_words': 0.5,
     'p_monosyllable_words': 0.4,
     'p_polysyllable_words': 0.6,
     'p_letters': 0.8450704225352113,
     'p_spaces': 0.1267605633802817,
     'p_punctuations': 0.028169014084507043}
    ```

El método `describe` es el de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas básicas no tienen escalas, así que da `None` para las estadísticas de `get_stats`.

## Signos de puntuación { #count_punctuations }

<!-- core: stats/basic_stats.md:count_punctuations b982de2 -->
``` {.python .signature}
count_punctuations(text, marks=PUNCTUATION_MARKS, dash_pattern=DASH_PATTERN)
```

Cuenta los signos de puntuación por tipo, la distribución de `c_punctuations`: comas, puntos, signos de interrogación y de exclamación, puntos suspensivos, dos puntos, puntos y comas, rayas, guiones, comillas latinas, comillas, paréntesis y otros signos. Primero se cuentan las rayas escritas con guiones (`dash_pattern`), luego los puntos suspensivos - `…`, tres o más puntos, o dos tras `?` y `!`, un solo signo cuyos puntos no se cuentan como puntos (`¿Quién?..` es una interrogación y unos puntos suspensivos) - y después cada signo por su tipo en `marks`; cualquier otro carácter de las categorías Unicode P y S es otro signo (`§`, `€`, `°`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Cadena de texto |
| `marks` | `dict[str, str]` | `PUNCTUATION_MARKS` | Tipo de cada signo, uno de `PUNCTUATION_TYPES` |
| `dash_pattern` | `Pattern` | `DASH_PATTERN` | Rayas escritas con guiones |

Un signo de `marks` que no es un solo carácter o tiene un tipo desconocido lanza `ParameterError`; un texto que no es una cadena, unos `marks` que no son un mapeo y un `dash_pattern` que no es una expresión regular compilada lanzan `SourceTypeError`.

esTS cuenta con los signos y el patrón de rayas del núcleo, `PUNCTUATION_MARKS` y `DASH_PATTERN` de `anyts.basic_stats`, que siguen la ortografía española: los signos de apertura `¿` y `¡` son de interrogación y de exclamación (`¿Qué?` lleva dos signos de interrogación), `—`, `–` y la barra horizontal `―` son rayas, y también la raya escrita con guiones - una serie de dos o más guiones, un guion tras espacio, al principio de línea o tras un signo de cierre, ante un espacio o entre una letra y un signo de apertura o de cierre (`--Hola --dijo Juan`, `- Se fueron - dijo`, `cuatro.-¿Cinco?`); un guion dentro de una palabra, ante una cifra o al final de línea dentro de una palabra es un guion (`teórico-práctico`, `-5`), `«»` son comillas latinas y `"“”‘’` las comillas de los tres niveles de la ortografía. Los signos combinantes y los caracteres invisibles de formato (Unicode M y Cf) se descartan de las palabras, pero no se cuentan como signos.

=== "Código"

    ``` python
    from ests.basic_stats import count_punctuations

    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    ```

=== "Resultado"

    ```
    {'comma': 2,
     'exclamation': 2,
     'ellipsis': 1,
     'semicolon': 1,
     'dash': 3,
     'angle_quotes': 2,
     'parentheses': 2}
    ```

## Perfil de puntuación { #punctuation }

``` {.python .signature}
punctuation_profile(text, n_words=None)
```

Las frecuencias de los signos de puntuación por tipo (`count_punctuations`) por cada 1000 palabras e `inverted_share` - la proporción de signos de apertura entre todos los signos de interrogación y exclamación: `0.5` cuando toda pregunta y exclamación empieza con `¿` o `¡` como exige la ortografía, menor cuando quien escribe los omite. Sin palabras las frecuencias son `nan`, y también `inverted_share` sin signos de interrogación y exclamación.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Cadena de texto |
| `n_words` | `int` | `None` | Número de palabras; sin él las palabras se extraen con `WordsExtractor` |

Excepciones:

- `SourceTypeError` - un texto que no es una cadena;
- `SourceError` - sin `n_words`, un texto con un carácter sin forma UTF-8;
- `ParameterError` - un número de palabras que no es un entero no negativo.

El perfil depende del formato del texto (comillas y rayas tipográficas, signos de apertura), así que conviene leerlo aparte de los rasgos lingüísticos.

=== "Código"

    ``` python
    from ests.basic_stats import punctuation_profile

    profile = punctuation_profile(text)
    round(profile["dash"], 1), profile["inverted_share"]
    ```

=== "Resultado"

    ```
    (230.8, 0.5)
    ```
