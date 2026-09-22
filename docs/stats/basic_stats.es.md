# Estadísticas básicas

!!! info ""
    **ests.basic_stats.BasicStats**

## Descripción

Módulo para calcular las estadísticas básicas de un texto. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

El módulo permite usar objetos [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) ya configurados para la segmentación en oraciones y palabras que precede al cálculo. Las sílabas se cuentan con [`count_syllables`](../syllables.md#count_syllables) y las letras con `str.isalpha`, así que las cifras, los guiones y los signos dentro de una palabra no son letras, mientras que los indicadores ordinales `º` y `ª` sí lo son (`3.º` es una palabra de una letra).

Para un objeto `Doc` las palabras se toman de los tokens (los signos de puntuación y los símbolos como `€` o `%` se descartan) y las oraciones de la anotación; sin límites de oración (`spacy.blank`, un pipeline sin `parser` ni `senter`) las oraciones se extraen del texto con `SentsExtractor`.

!!! note "Nota"
    Las estadísticas se calculan al inicializar el objeto `BasicStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (cadena u objeto Doc) |
| `sents_extractor` | SentsExtractor | `None` | Herramienta de extracción de oraciones |
| `words_extractor` | WordsExtractor | `None` | Herramienta de extracción de palabras |
| `normalize` | bool | `False` | Calcular las estadísticas normalizadas |
| `complex_syl_factor` | int | `3` | Número mínimo de sílabas de una palabra compleja |
| `long_word_letter_factor` | int | `7` | Número mínimo de letras de una palabra larga |

!!! note "Nota"
    Los umbrales por defecto siguen la tradición española de la legibilidad: una palabra compleja tiene tres o más sílabas, como en las adaptaciones españolas de SMOG y de la niebla de Gunning, y una palabra larga siete o más letras, como en LIX y RIX.

## Atributos

| Atributo | Tipo | Descripción |
| :-------: | :--: | :---------: |
| `c_letters` | dict[int, int] | Distribución de las palabras por número de letras |
| `c_syllables` | dict[int, int] | Distribución de las palabras por número de sílabas |
| `n_sents` | int | Número de oraciones |
| `n_words` | int | Número de palabras |
| `n_unique_words` | int | Número de palabras únicas |
| `n_long_words` | int | Número de palabras largas |
| `n_complex_words` | int | Número de palabras complejas |
| `n_simple_words` | int | Número de palabras simples |
| `n_monosyllable_words` | int | Número de palabras monosílabas |
| `n_polysyllable_words` | int | Número de palabras polisílabas |
| `n_chars` | int | Número de caracteres |
| `n_letters` | int | Número de letras |
| `n_spaces` | int | Número de espacios |
| `n_syllables` | int | Número de sílabas |
| `n_punctuations` | int | Número de signos de puntuación |
| `c_punctuations` | dict[str, int] | Distribución de los signos de puntuación por tipo |
| `p_unique_words` | float | Número normalizado de palabras únicas |
| `p_long_words` | float | Número normalizado de palabras largas |
| `p_complex_words` | float | Número normalizado de palabras complejas |
| `p_simple_words` | float | Número normalizado de palabras simples |
| `p_monosyllable_words` | float | Número normalizado de palabras monosílabas |
| `p_polysyllable_words` | float | Número normalizado de palabras polisílabas |
| `p_letters` | float | Número normalizado de letras |
| `p_spaces` | float | Número normalizado de espacios |
| `p_punctuations` | float | Número normalizado de signos de puntuación |

!!! warning "Aviso"
    Los atributos de estadísticas normalizadas `p_*` solo existen cuando el objeto se inicializa con `normalize=True`.

## Métodos

### count_words_by_syllables

Devuelve el número de palabras con al menos el número de sílabas indicado.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `min_syllables` | int | `-` | Número mínimo de sílabas de la palabra |

### count_words_by_letters

Devuelve el número de palabras con al menos el número de letras indicado.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `min_letters` | int | `-` | Número mínimo de letras de la palabra |

!!! note "Nota"
    Estos métodos vuelven a contar las palabras complejas y largas con un umbral distinto del fijado al inicializar, que es lo que necesitan las fórmulas de legibilidad con umbrales propios.

### get_stats

Devuelve un diccionario con las estadísticas calculadas del texto.

Ejemplo de cálculo de las estadísticas básicas con normalización:

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import BasicStats

    # Preparar los datos
    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

    # Calcular las estadísticas
    bs = BasicStats(text, normalize=True)
    bs.get_stats()
    ```

    _Resultado_:

    ``` bash
    {'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
    'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0, 'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0, 'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0, 'parentheses': 0, 'other': 0},
    'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
    'n_chars': 71,
    'n_complex_words': 5,
    'n_letters': 60,
    'n_long_words': 5,
    'n_monosyllable_words': 4,
    'n_polysyllable_words': 6,
    'n_punctuations': 2,
    'n_sents': 1,
    'n_simple_words': 5,
    'n_spaces': 9,
    'n_syllables': 23,
    'n_unique_words': 8,
    'n_words': 10,
    'p_complex_words': 0.5,
    'p_letters': 0.8450704225352113,
    'p_long_words': 0.5,
    'p_monosyllable_words': 0.4,
    'p_polysyllable_words': 0.6,
    'p_punctuations': 0.028169014084507043,
    'p_simple_words': 0.5,
    'p_spaces': 0.1267605633802817,
    'p_unique_words': 0.8}
    ```

### print_stats

Muestra una tabla con las estadísticas calculadas del texto.

Para ilustrar el método reutilizamos el código del ejemplo anterior:

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de estadísticas calculadas
    bs.print_stats()
    ```

    _Resultado_:

    ``` bash
         Statistic      |  Value
    ------------------------------
    Sentences           |    1
    Words               |    10
    Unique words        |    8
    Long words          |    5
    Complex words       |    5
    Simple words        |    5
    Monosyllabic words  |    4
    Polysyllabic words  |    6
    Characters          |    71
    Letters             |    60
    Spaces              |    9
    Syllables           |    23
    Punctuation marks   |    2
    ```

!!! warning "Aviso"
    El método no muestra los atributos de estadísticas normalizadas `p_*`.

## Perfil de puntuación { #punctuation }

!!! info ""
    **ests.basic_stats.count_punctuations()**, **ests.basic_stats.punctuation_profile()**

`count_punctuations(text)` cuenta los signos de puntuación por los tipos de `PUNCTUATION_TYPES`, la misma distribución que guarda el atributo `c_punctuations`: comas, puntos, signos de interrogación y de exclamación (incluidos los de apertura `¿` y `¡`, así que `¿Qué?` lleva dos signos de interrogación), puntos suspensivos (el carácter `…`, tres o más puntos, o dos puntos tras `?` y `!`: un solo signo cuyos puntos no cuentan como puntos, `¿Quién?..` es una interrogación y unos puntos suspensivos), dos puntos, puntos y comas, rayas (`—` y `–`, y también un guion tras espacio o al principio de línea, o ante un espacio, como se escribe la raya en los corpus de texto plano: `-Hola -dijo Juan`, `- Se fueron - dijo`), guiones dentro de palabras, ante cifras y al final de línea dentro de una palabra (`teórico-práctico`, `1990-1995`, `-5`, `pala-` en un salto de línea), comillas latinas `«»`, comillas rectas, inglesas y simples `"“”‘’` de los tres niveles de la ortografía, paréntesis y los demás signos: cualquier otro carácter de `PUNCTUATIONS` o de las categorías Unicode P y S (`‹›`, `§`, `€`, `°`), el mismo conjunto que `is_punctuation` descarta de las palabras, de modo que ningún signo se pierde entre las palabras y los tipos. `punctuation_profile(text, n_words=None)` los convierte en frecuencias por cada 1000 palabras y añade `inverted_share`, la proporción de signos de apertura entre todos los signos de interrogación y exclamación: `0.5` cuando toda pregunta y exclamación empieza con `¿` o `¡` como exige la ortografía, menos cuando quien escribe los omite, como en textos informales y mensajes.

El perfil es un rasgo editorial y estilométrico. Depende del formato del texto (comillas y rayas tipográficas, signos de apertura) y es fácil de falsear, así que conviene leerlo aparte de los rasgos lingüísticos.

!!! example "Ejemplo"

    ``` python
    from ests.basic_stats import count_punctuations, punctuation_profile

    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    {kind: count for kind, count in count_punctuations(text).items() if count}
    # {'comma': 2, 'exclamation': 2, 'ellipsis': 1, 'semicolon': 1, 'dash': 3, 'angle_quotes': 2, 'parentheses': 2}

    round(punctuation_profile(text)["dash"], 1), punctuation_profile(text)["inverted_share"]
    # (230.8, 0.5)
    ```
