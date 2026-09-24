# Estadísticas de complejidad léxica

!!! info ""
    **ests.lexical_stats.LexicalStats**

## Descripción

Un módulo para calcular las estadísticas de complejidad léxica de un texto a la manera de [TAALES](https://doi.org/10.3758/s13428-017-0924-4) - cuán raras son las palabras del texto en la lengua: la frecuencia media, el rango y la dispersión de los lemas según el [diccionario de frecuencias](../datasets/freqdict.md) de Google Books Ngram, las proporciones de palabras de las bandas de frecuencia top-1000, 2000, 5000 y 10000 según la lista integrada de los lemas más frecuentes, la sorpresa (surprisal) y la perplejidad según el modelo de unigramas del diccionario, la densidad léxica. A diferencia de las [métricas de diversidad léxica](diversity_stats.md), que comparan las palabras del texto entre sí, aquí las palabras se comparan con las frecuencias de la lengua.

Una palabra se busca por [`lemma_key`](../datasets/freqdict.md#lemma_key), la clave con la que se construye el diccionario: el lema de simplemma de la palabra en minúsculas, y la forma en minúsculas para un nombre propio, así que `París` se encuentra como `parís` y no como el verbo `parir`. Si una palabra es un nombre propio, y si es una palabra con contenido, sale de la anotación, así que la fuente tiene que estar anotada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline pasado en `nlp`, y un `Doc` debe llevar las categorías gramaticales (un `morphologizer`, o un `tagger` con un `attribute_ruler`); una fuente sin ellas levanta `SourceError`. Los lemas del modelo no se usan. La última palabra sobre los nombres propios la tiene el etiquetador: un verbo con mayúscula al principio de una oración etiquetado `PROPN` se busca por su forma. Una palabra con contenido se define como en [`CohesionStats`](cohesion_stats.md): una de `CONTENT_UD_POS` (sustantivos, nombres propios, adjetivos, verbos, adverbios) y no demostrativa. Los números (`2020`, `5,5`, `3.º`) no son palabras: el diccionario y la lista no los tienen, y parecerían las palabras más raras del texto.

Un texto más largo que el `max_length` del pipeline - un millón de caracteres por defecto - levanta `SourceError`: divídalo en partes, o suba `max_length` en un pipeline propio y páselo en `nlp`.

Recursos:

| Recurso | Estadísticas | Disponibilidad |
| :------ | :----------- | :------------- |
| [`FreqDict`](../datasets/freqdict.md) - 83 785 lemas de Google Books Ngram (1980-2019) con ipm, rango y dispersión | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | se descarga una vez con `FreqDict().download()`; sin el diccionario, leer estas estadísticas y `get_stats` levanta `DatasetNotFoundError` |
| La lista integrada de los 10 000 lemas más frecuentes del mismo diccionario (`ests/resources/google_books_top10000.txt`, CC BY 3.0) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | siempre |

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `freq_dict` | FreqDict | `None` | Diccionario de frecuencias; si no se indica, se usa `FreqDict()` del directorio por defecto |
| `nlp` | Language | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[str] | Tupla de las palabras |
| `lemmas` | tuple[str] | Tupla de las claves de las palabras en el diccionario (`lemma_key`) |
| `ranks` | tuple[int/None] | Tupla de los rangos de los lemas según la lista integrada, `None` fuera del top 10000 |
| `entries` | tuple[Entry/None] | Tupla de las entradas del diccionario para cada palabra, `None` para una palabra fuera de él |
| `n_words` | int | Número de palabras |
| `n_content_words` | int | Número de palabras con contenido |
| `n_found` | int | Número de palabras encontradas en el diccionario |
| `coverage` | float | Proporción de palabras encontradas en el diccionario |
| `mean_ipm` | float | Frecuencia media de las palabras encontradas |
| `mean_ipm_content` | float | Frecuencia media de las palabras con contenido encontradas |
| `mean_log_ipm` | float | Media del logaritmo decimal de la frecuencia de las palabras encontradas |
| `mean_log_ipm_content` | float | Lo mismo sobre las palabras con contenido |
| `mean_range` | float | Rango medio de las palabras encontradas - años de 40 |
| `mean_dispersion` | float | Dispersión D media de las palabras encontradas |
| `surprisal` | float | Sorpresa media de las palabras según el modelo de unigramas del diccionario, en bits |
| `perplexity` | float | Perplejidad de unigramas |
| `p_top1000` | float | Proporción de palabras con un lema del top 1000 |
| `p_top2000` | float | Proporción de palabras con un lema del top 2000 |
| `p_top5000` | float | Proporción de palabras con un lema del top 5000 |
| `p_top10000` | float | Proporción de palabras con un lema del top 10000 |
| `p_beyond_top10000` | float | Proporción de palabras con un lema fuera del top 10000 |
| `lexical_density` | float | Proporción de palabras con contenido |

Las medias según el diccionario se calculan solo sobre las palabras encontradas, `nan` sin ellas; léalas junto a `coverage`. La frecuencia media en ipm la dominan las palabras funcionales (`el` - 97 000 ipm, `de` - 71 000), así que para comparar textos conviene más la frecuencia logarítmica o la media sobre las palabras con contenido. El rango es el número de años, de 40, en que el lema aparece en los libros, no el número de partes de un corpus de 100.

!!! note "Nota"
    Cada estadística se puede calcular aparte llamando a su función. Las estadísticas y las funciones que las calculan se describen en la [sección](lexical_stats_funcs.md) correspondiente.

## Métodos

### band_coverage

Devuelve las proporciones de palabras con un lema del top N para cada límite N.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `bands` | list[int] | `(1000, 2000, 5000, 10000)` | Límites de las bandas - los tamaños de las listas top |
| `unique` | bool | `False` | Contar los lemas distintos en lugar de las palabras |

!!! example "Ejemplo"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.band_coverage(unique=True)
    # {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}
    ls.band_coverage(bands=(100, 500))
    # {100: 0.6363636363636364, 500: 0.7272727272727273}
    ```

### get_stats

Devuelve un diccionario con las estadísticas de complejidad léxica calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar las bibliotecas
    from ests import LexicalStats
    from ests.datasets import FreqDict

    # Descargar el diccionario (una vez)
    FreqDict().download()

    # Calcular las estadísticas
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.get_stats()
    ```

    _Resultado_:

    ``` bash
    {'coverage': 1.0,
     'mean_ipm': 34283.74818181818,
     'mean_ipm_content': 956.3320000000001,
     'mean_log_ipm': 3.559971676175293,
     'mean_log_ipm_content': 2.1916598821626314,
     'mean_range': 40.0,
     'mean_dispersion': 97.63636363636364,
     'surprisal': 8.105598641234213,
     'perplexity': 275.4408334528846,
     'p_top1000': 0.7272727272727273,
     'p_top2000': 0.8181818181818182,
     'p_top5000': 1.0,
     'p_top10000': 1.0,
     'p_beyond_top10000': 0.0,
     'lexical_density': 0.45454545454545453}
    ```

Las palabras raras suben la sorpresa y bajan la cobertura y las bandas:

!!! example "Ejemplo"

    ``` python
    ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
    ls.coverage, ls.p_top1000, ls.p_beyond_top10000, ls.surprisal
    # (0.8571428571428571, 0.42857142857142855, 0.4285714285714286, 13.70650419215419)
    ```

### print_stats

Muestra una tabla con las estadísticas de complejidad léxica calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Crear el objeto de las estadísticas
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")

    # Mostrar la tabla de las estadísticas calculadas
    ls.print_stats()
    ```

    _Resultado_:

    ``` bash
                            Statistic                         |  Value
    --------------------------------------------------------------------
    Share of words found in the frequency dictionary          |   1.00
    Mean frequency (ipm)                                      | 34283.75
    Mean frequency of content words (ipm)                     |  956.33
    Mean log frequency (lg ipm)                               |   3.56
    Mean log frequency of content words                       |   2.19
    Mean range (years out of 40)                              |  40.00
    Mean dispersion (D)                                       |  97.64
    Mean surprisal (bits)                                     |   8.11
    Unigram perplexity                                        |  275.44
    Share of words in the top 1000                            |   0.73
    Share of words in the top 2000                            |   0.82
    Share of words in the top 5000                            |   1.00
    Share of words in the top 10000                           |   1.00
    Share of words beyond the top 10000                       |   0.00
    Lexical density                                           |   0.45
    ```
