# Estadísticas de complejidad léxica

``` {.python .signature}
LexicalStats(source, freq_dict=None, nlp=None)
```

<!-- core: stats/lexical_stats.md:LexicalStats baa1034 -->
Complejidad léxica a la manera de TAALES (Kyle, Crossley y Berger, 2018) - cuán raras son las palabras de un texto: estadísticas según un diccionario de frecuencias y su modelo de unigramas, las proporciones de las bandas de frecuencia de una lista de los lemas más frecuentes y la densidad léxica. Las estadísticas según el diccionario se calculan la primera vez que se leen, así que las bandas y la densidad léxica no necesitan los datos del diccionario.

Excepciones:

- `SourceTypeError` - un diccionario de otra clase que la de la biblioteca o, sin `freq_dict_class`, uno sin `lookup` e `ipm` o ninguno; un `analyze` que no da objetos `LexicalWord`;
- `SourceError` - una fuente sin palabras.

En esTS una fuente que no es ni una cadena ni un `Doc` y un pipeline en `nlp` que no es un `Language` de spaCy también lanzan `SourceTypeError`; una fuente sin las categorías gramaticales, una cadena más larga que el `max_length` del pipeline y una cadena con un carácter sin forma UTF-8, `SourceError`; y las métricas según el diccionario sin el diccionario descargado, `DatasetNotFoundError`.

A diferencia de las [métricas de diversidad léxica](diversity_stats.md), que comparan las palabras de un texto entre sí, aquí las palabras se comparan con las frecuencias de la lengua ([TAALES](https://doi.org/10.3758/s13428-017-0924-4)). La fuente de datos es un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

La clase extiende el `LexicalStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/lexical_stats/) con la capa del español: el diccionario es el [`FreqDict`](../datasets/freqdict.md) de Google Books Ngram (`freq_dict_class`), y las posiciones de los lemas y el tamaño de la lista (`rank`, `top_size`) salen de la lista integrada de sus 10 000 lemas más frecuentes ([`get_rank`](#bands)). Si una palabra es un nombre propio, y si es una palabra con contenido, sale de la anotación, así que la fuente tiene que estar anotada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline pasado en `nlp`, sin el parser, el lematizador ni las entidades nombradas, y un `Doc` debe llevar las categorías gramaticales (un `morphologizer`, o un `tagger` con un `attribute_ruler`). Los números (`2020`, `5,5`, `3.º`) no son palabras. Los lemas salen de [`lemma_key`](../datasets/freqdict.md#lemma_key), el lema de simplemma en minúsculas, no del modelo; un nombre propio conserva su forma en minúsculas. Una palabra con contenido se define como en [`CohesionStats`](cohesion_stats.md): una de `CONTENT_UD_POS` (sustantivos, nombres propios, adjetivos, verbos, adverbios) y no demostrativa. La tabla de `print_stats` lleva las descripciones de `LEXICAL_STATS_DESC` de `ests.constants`, con el rango en años de 40.

El `max_length` del pipeline es de un millón de caracteres por defecto: divida un texto más largo en partes, o suba `max_length` en un pipeline propio y páselo en `nlp`.

=== "Código"

    ``` python
    from ests import LexicalStats
    from ests.datasets import FreqDict

    FreqDict().download()
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.print_stats()
    ```

=== "Resultado"

    ```
                        Statistic                    |  Value
    ------------------------------------------------------------
    Share of words found in the frequency dictionary |   1.00
    Mean frequency (ipm)                             | 34283.75
    Mean frequency of content words (ipm)            |  956.33
    Mean log frequency (lg ipm)                      |   3.56
    Mean log frequency of content words              |   2.19
    Mean range (years out of 40)                     |  40.00
    Mean dispersion (D)                              |  97.64
    Mean surprisal (bits)                            |   8.11
    Unigram perplexity                               |  275.44
    Share of words in the top 1000                   |   0.73
    Share of words in the top 2000                   |   0.82
    Share of words in the top 5000                   |   1.00
    Share of words in the top 10000                  |   1.00
    Share of words beyond the top 10000              |   0.00
    Lexical density                                  |   0.45
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `freq_dict` | `FreqDict` | `None` | Diccionario de frecuencias; `FreqDict()` del directorio por defecto si no se indica |
| `nlp` | `Language` | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Atributos

<!-- core: stats/lexical_stats.md:LexicalStats-attributes 40e73ab -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `freq_dict` | `FrequencyDictionary` | Diccionario de frecuencias |
| `words`, `lemmas` | `tuple[str]` | Palabras y sus lemas; las bandas se cuentan por los lemas |
| `keys` | `tuple[str]` | Claves de las palabras en el diccionario |
| `entries` | `tuple[FrequencyEntry / None]` | Entradas del diccionario, `None` para una palabra fuera de él |
| `ranks` | `tuple[int / None]` | Posiciones de los lemas, `None` fuera de la lista |
| `n_words`, `n_content_words`, `n_found` | `int` | Número de palabras, de palabras con contenido y de palabras encontradas en el diccionario |

En esTS el diccionario es un `FreqDict`, y sus entradas son las tuplas con nombre [`Entry`](../datasets/freqdict.md). Las claves de las palabras en el diccionario (`keys`, `dictionary_keys`) son sus lemas, y un nombre propio se busca por su forma cuando el diccionario la tiene (`París` como `parís`, no como el verbo `parir`) y por su lema si no (`Estados` de *Estados Unidos* como `estado`, un `Miró` a principio de oración etiquetado `PROPN` como `mirar`). Una palabra se busca sin el punto de una abreviatura (`Sr.` como `sr`, `pág.` como `página`); una inicial (`D.`, `J.`) lo conserva y queda fuera del diccionario.

=== "Código"

    ``` python
    ls = LexicalStats("Miró desde París hacia los Estados Unidos")
    ls.lemmas
    ls.keys
    ```

=== "Resultado"

    ```
    ('miró', 'desde', 'parís', 'hacia', 'el', 'estados', 'unidos')
    ('mirar', 'desde', 'parís', 'hacia', 'el', 'estado', 'unidos')
    ```

## Métricas

<!-- core: stats/lexical_stats.md:LexicalStats-metrics aa10b9c -->
Cada métrica es un atributo o una propiedad del objeto, y `get_stats` las da todas. Una media se toma sobre las palabras encontradas en el diccionario, y sin ellas es `nan`.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| `coverage` | Proporción de las palabras encontradas en el diccionario | 0-1 | Más palabras conocidas por el diccionario |
| `mean_ipm`, `mean_ipm_content` | Frecuencia media por millón de palabras de las palabras encontradas, de las palabras con contenido encontradas | Más de 0 | Palabras más frecuentes |
| `mean_log_ipm`, `mean_log_ipm_content` | Media del logaritmo decimal de la frecuencia de las palabras encontradas, de las palabras con contenido encontradas | Hasta 6 | Palabras más frecuentes |
| `mean_range` | Rango medio de las palabras encontradas | 0 o más | Palabras usadas en más partes del corpus |
| `mean_dispersion` | Dispersión media de las palabras encontradas | La del diccionario | Según la medida del diccionario |
| [`surprisal`](#surprisal) | Sorpresa media de las palabras según el modelo de unigramas del diccionario, en bits | 0 o más | Palabras más raras |
| [`perplexity`](#surprisal) | 2 elevado a la sorpresa | 1 o más | Palabras más raras |
| [`p_top1000`](#bands), [`p_top2000`](#bands), [`p_top5000`](#bands), [`p_top10000`](#bands) | Proporción de las palabras con un lema en el top 1000, 2000, 5000 y 10000 de la lista | 0-1, `nan` para una banda más allá de `top_size` | Palabras más frecuentes |
| [`p_beyond_top10000`](#bands) | Proporción de las palabras con un lema fuera del top 10000 | 0-1, `nan` para una lista de menos de 10000 | Palabras más raras |
| `lexical_density` | Proporción de las palabras con contenido | 0-1 | Más palabras con contenido |

Las métricas se apoyan en dos recursos; lea siempre las medias según el diccionario junto a `coverage`.

| Recurso | Métricas | Disponibilidad |
| :------ | :------- | :------------- |
| [`FreqDict`](../datasets/freqdict.md) - 83 785 lemas de Google Books Ngram (1980-2019) con ipm, rango y dispersión | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | se descarga una vez con `FreqDict().download()` |
| La lista integrada de los 10 000 lemas más frecuentes del mismo diccionario (`ests/resources/google_books_top10000.txt`, CC BY 3.0) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | siempre |

<div class="metric-card" markdown>

### Frecuencia según el diccionario { #frequency }

`coverage` · `mean_ipm` · `mean_ipm_content` · `mean_log_ipm` · `mean_log_ipm_content` · `mean_range` · `mean_dispersion` · [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html)
{ .metric-meta }

Las métricas se calculan a partir de las entradas del `FreqDict` para las claves de las palabras (`keys`, `entries`): las medias se toman sobre las palabras encontradas en el diccionario, sobre todas ellas o solo sobre las palabras con contenido. El rango es el número de años, de 40 (1980-2019), en que el lema aparece en los libros, y la dispersión es la D de Juilland sobre los años, de 0 a 100. La frecuencia media en ipm es sensible a las palabras funcionales (`el` - 98 000 ipm, `de` - 71 000), así que para comparar textos conviene más la frecuencia logarítmica o la media sobre las palabras con contenido.

Las palabras raras bajan la cobertura y la frecuencia logarítmica y suben la sorpresa y la proporción fuera del top 10000:

=== "Código"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
    ls.coverage, ls.mean_log_ipm, ls.surprisal, ls.p_beyond_top10000
    ```

=== "Resultado"

    ```
    (0.8571428571428571, 2.3529196195453976, 13.70650419215419, 0.4285714285714286)
    ```

</div>

<div class="metric-card" markdown>

### Sorpresa y perplejidad { #surprisal }

`surprisal` · `perplexity`
{ .metric-meta }

<!-- core: stats/lexical_stats.md:calc_surprisal 0ce80d8 -->
``` {.python .signature}
calc_surprisal(lemmas, freq_dict)
```

La sorpresa media de las palabras según el modelo de unigramas de un diccionario de frecuencias, en bits; una palabra fuera del diccionario recibe su frecuencia más baja `min_ipm`. La perplejidad es 2 elevado a ella.

$$
\frac{1}{N} \sum_{w} -\log_2 \frac{\max(\textrm{ipm}_w, \textrm{min\_ipm})}{10^6}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `lemmas` | `list[str]` | - | Claves de las palabras en el diccionario |
| `freq_dict` | `FrequencyDictionary` | - | Diccionario de frecuencias |

Sin palabras da `nan`; unas claves que no son una lista de cadenas y un diccionario sin `ipm` y `min_ipm` lanzan `SourceTypeError`, una frecuencia más baja que no es mayor que cero, `ParameterError`.

En esTS el diccionario es un `FreqDict` con la frecuencia más baja de 0,1 ipm: un diccionario de otra clase lanza `SourceTypeError`.

=== "Código"

    ``` python
    from ests.datasets import FreqDict
    from ests.lexical_stats import calc_surprisal

    calc_surprisal(["gato", "estar", "felinólogo"], FreqDict())
    ```

=== "Resultado"

    ```
    15.392368319318606
    ```

</div>

<div class="metric-card" markdown>

### Bandas de frecuencia { #bands }

`p_top1000` · `p_top2000` · `p_top5000` · `p_top10000` · `p_beyond_top10000` · `band_coverage(bands, unique)`
{ .metric-meta }

<!-- core: stats/lexical_stats.md:LexicalStats-bands 9a6c3b6 -->
La proporción de las palabras cuyo lema tiene una posición (`rank`) dentro del top $N$ de la lista, para los límites 1000, 2000, 5000 y 10000 de `FREQUENCY_BANDS`; la proporción fuera del top 10000 es el resto, incluidas las palabras fuera de la lista. Una banda más allá del tamaño de la lista (`top_size`) es `nan`, y también la proporción fuera del top 10000 para una lista de menos de 10000.

$$
\frac{\textrm{Número de palabras con una posición hasta } N}{\textrm{Número de palabras}}
$$

Así se construye un perfil de bandas de frecuencia a la manera del Lexical Frequency Profile. Las bandas toman la forma en minúsculas de un nombre propio: un nombre propio cuya forma es un lema común recibe su posición (`Gobierno` 106), mientras que los nombres y sus partes flexionadas (`Madrid`, `Estados`) quedan fuera del top 10000, así que un texto lleno de nombres tiene una proporción mayor ahí.

``` {.python .signature}
get_rank(lemma)
```

La posición de un lema según la lista integrada, `None` para un lema fuera de la lista; el lema puede ir en cualquier caja.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `lemma` | `str` | - | Lema - la clave de `lemma_key` |

``` {.python .signature}
load_top_lemmas()
```

La lista entera del fichero `ests/resources/google_books_top10000.txt`, derivado de Google Books Ngram con licencia CC BY 3.0: la posición de cada lema, empezando por 1. La lista recoge los 10 000 lemas más frecuentes del [diccionario de frecuencias](../datasets/freqdict.md) por frecuencia decreciente, con las categorías gramaticales de un lema sumadas; deja fuera los nombres propios, las letras sueltas salvo las palabras del español `a`, `e`, `o`, `u`, `y`, `á`, `é`, `ó`, y los lemas de dos letras y los números romanos que simplemma no conoce (`pp`, `xix`), mientras que las abreviaturas de las referencias (`cit`) y las palabras inglesas de las bibliografías (`the`) se quedan.

=== "Código"

    ``` python
    from ests.lexical_stats import get_rank, load_top_lemmas

    get_rank("el"), get_rank("gato"), get_rank("felinólogo")
    len(load_top_lemmas())
    ```

=== "Resultado"

    ```
    (1, 2851, None)
    10000
    ```

</div>

<div class="metric-card" markdown>

### Densidad léxica { #lexical_density }

`lexical_density`
{ .metric-meta }

La proporción de palabras con contenido entre todas las palabras; una palabra con contenido es una de `CONTENT_UD_POS` (sustantivos, nombres propios, adjetivos, verbos, adverbios) y no demostrativa, como en [`CohesionStats`](cohesion_stats.md), así que los auxiliares (`es`, `ha`) no son palabras con contenido.

$$
\frac{\textrm{Número de palabras con contenido}}{\textrm{Número de palabras}}
$$

</div>

## Métodos

<!-- core: stats/lexical_stats.md:LexicalStats-band_coverage 065e9e9 -->
`band_coverage(bands, unique)` da la proporción de las palabras con un lema en el top N de la lista para cada límite N de `bands` (`FREQUENCY_BANDS` por defecto), o con `unique=True` la proporción de los lemas distintos. Unos límites que no son una lista de enteros o un límite fuera de 1 y `top_size()` lanzan `ParameterError`.

=== "Código"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.band_coverage(unique=True)
    ls.band_coverage(bands=(100, 500))
    ```

=== "Resultado"

    ```
    {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}
    {100: 0.6363636363636364, 500: 0.7272727272727273}
    ```

Los demás métodos, `get_stats`, `to_dataframe`, `print_stats` y `describe`, son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas de complejidad léxica no tienen escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    ls.get_stats()
    ```

=== "Resultado"

    ```
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
