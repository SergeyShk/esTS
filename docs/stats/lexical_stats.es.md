# Estadísticas de complejidad léxica

``` {.python .signature}
LexicalStats(source, freq_dict=None)
```

<!-- core: stats/lexical_stats.md:LexicalStats dfdfd1b -->
Complejidad léxica a la manera de TAALES (Kyle, Crossley y Berger, 2018) - cuán raras son las palabras de un texto: estadísticas según un diccionario de frecuencias y su modelo de unigramas, las proporciones de las bandas de frecuencia de una lista de los lemas más frecuentes, la densidad léxica y las proporciones de los nombres propios y de las abreviaturas. Las estadísticas según el diccionario se calculan la primera vez que se leen, así que las bandas y las proporciones no necesitan los datos del diccionario. La fuente de datos es un texto, un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy) o un `Document` de [anySeg](https://github.com/SergeyShk/anySeg), que se lee a través de su [documento](https://sergeyshk.github.io/anyTS/document/): por defecto, sus palabras de Universal Dependencies sin los números, con sus lemas, sus categorías gramaticales y sus rasgos.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena, ni un `Doc`, ni un `Document`, un `parse` que no devuelve un `Document`, un diccionario de otra clase que la de la biblioteca o, sin `freq_dict_class`, uno sin `lookup` e `ipm` o ninguno; un `analyze` que no da objetos `LexicalWord`;
- `SourceError` - palabras sin categorías gramaticales, una fuente sin palabras.

En esTS las métricas según el diccionario sin el diccionario descargado lanzan `DatasetNotFoundError`. Un `Doc` conserva una contracción o un verbo con clíticos como una sola palabra, que una cadena divide, así que la perplejidad y la frecuencia media de un `Doc` y de su cadena difieren en un 5-10 % ([`load_pipeline`](../components.md#load_pipeline)).

A diferencia de las [métricas de diversidad léxica](diversity_stats.md), que comparan las palabras de un texto entre sí, aquí las palabras se comparan con las frecuencias de la lengua ([TAALES](https://doi.org/10.3758/s13428-017-0924-4)).

La clase extiende el `LexicalStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/lexical_stats/) con la capa del español: el diccionario es el [`FreqDict`](../datasets/freqdict.md) de Google Books Ngram (`freq_dict_class`), y las posiciones de los lemas y el tamaño de la lista (`rank`, `top_size`) salen de la lista integrada de sus 10 000 lemas más frecuentes ([`get_rank`](#bands)). Si una palabra es un nombre propio, y si es una palabra con contenido, sale de la anotación, así que la fuente tiene que estar anotada: una cadena recibe los análisis de [esMorph](https://github.com/SergeyShk/esMorph) en el contexto de sus oraciones, sin spaCy, y un `Doc` debe llevar las categorías gramaticales (`esmorph` de [`load_pipeline`](../components.md#load_pipeline), un `morphologizer`, o un `tagger` con un `attribute_ruler`). Los números (`2020`, `5,5`, `3.º`) no son palabras. Los lemas salen de [`lemma_key`](../datasets/freqdict.md#lemma_key) con la categoría gramatical de la palabra, el lema de esMorph en minúsculas, el lematizador con el que se construye el diccionario, no del modelo; un nombre propio conserva su forma en minúsculas. Una palabra con contenido se define como en [`CohesionStats`](cohesion_stats.md): una de `CONTENT_UD_POS` (sustantivos, nombres propios, adjetivos, verbos, adverbios) y no demostrativa. La tabla de `print_stats` lleva las descripciones de `LEXICAL_STATS_DESC` de `ests.constants`, con el rango en años de 40.

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
    Mean frequency (ipm)                             | 34473.85
    Mean frequency of content words (ipm)            |  806.61
    Mean log frequency (lg ipm)                      |   3.56
    Mean log frequency of content words              |   2.17
    Mean range (years out of 40)                     |  40.00
    Mean dispersion (D)                              |  97.18
    Mean surprisal (bits)                            |   8.10
    Unigram perplexity                               |  275.08
    Share of words in the top 1000                   |   0.73
    Share of words in the top 2000                   |   0.82
    Share of words in the top 5000                   |   1.00
    Share of words in the top 10000                  |   1.00
    Share of words beyond the top 10000              |   0.00
    Lexical density                                  |   0.45
    Share of proper nouns                            |   0.00
    Share of abbreviations                           |   0.00
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` / `Document` | - | Fuente de datos |
| `freq_dict` | `FreqDict` | `None` | Diccionario de frecuencias; `FreqDict()` del directorio por defecto si no se indica |

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

En esTS el diccionario es un `FreqDict`, y sus entradas son las tuplas con nombre [`Entry`](../datasets/freqdict.md). Las claves de las palabras en el diccionario (`keys`, `dictionary_keys`) son sus lemas, y un nombre propio se busca por su forma cuando el diccionario la tiene (`París` como `parís`) y por su lema si no (`Estados` de *Estados Unidos* como `estado`). Una palabra se busca sin el punto de una abreviatura (`Sr.` como `sr`, `pág.` como `pág`); una inicial (`D.`, `J.`) lo conserva y queda fuera del diccionario.

=== "Código"

    ``` python
    ls = LexicalStats("Miró desde París hacia los Estados Unidos")
    ls.lemmas
    ls.keys
    ```

=== "Resultado"

    ```
    ('mirar', 'desde', 'parís', 'hacia', 'el', 'estados', 'unidos')
    ('mirar', 'desde', 'parís', 'hacia', 'el', 'estado', 'unidos')
    ```

## Métricas

<!-- core: stats/lexical_stats.md:LexicalStats-metrics 72e0b6e -->
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
| `p_proper_nouns` | Proporción de los nombres propios | 0-1 | Más nombres de personas, lugares y organizaciones |
| `p_abbreviations` | Proporción de las abreviaturas | 0-1 | Más abreviaturas, como en los textos oficiales y científicos |

Las métricas se apoyan en dos recursos; lea siempre las medias según el diccionario junto a `coverage`.

| Recurso | Métricas | Disponibilidad |
| :------ | :------- | :------------- |
| [`FreqDict`](../datasets/freqdict.md) - 86 091 lemas de Google Books Ngram (1980-2019) con ipm, rango y dispersión | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | se descarga una vez con `FreqDict().download()` o `ests download` |
| La lista integrada de los 10 000 lemas más frecuentes del mismo diccionario (`ests/resources/google_books_top10000.txt`, CC BY 3.0) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | siempre |

<div class="metric-card" markdown>

### Frecuencia según el diccionario { #frequency }

`coverage` · `mean_ipm` · `mean_ipm_content` · `mean_log_ipm` · `mean_log_ipm_content` · `mean_range` · `mean_dispersion` · [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html)
{ .metric-meta }

Las métricas se calculan a partir de las entradas del `FreqDict` para las claves de las palabras (`keys`, `entries`): las medias se toman sobre las palabras encontradas en el diccionario, sobre todas ellas o solo sobre las palabras con contenido. El rango es el número de años, de 40 (1980-2019), en que el lema aparece en los libros, y la dispersión es la D de Juilland sobre los años, de 0 a 100. La frecuencia media en ipm es sensible a las palabras funcionales (`el` - 97 000 ipm, `de` - 84 000), así que para comparar textos conviene más la frecuencia logarítmica o la media sobre las palabras con contenido.

Las palabras raras bajan la cobertura y la frecuencia logarítmica y suben la sorpresa y la proporción fuera del top 10000:

=== "Código"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
    ls.coverage, ls.mean_log_ipm, ls.surprisal, ls.p_beyond_top10000
    ```

=== "Resultado"

    ```
    (0.875, 2.8003912324040754, 12.20694855853567, 0.375)
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
    15.554044709914342
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

La posición de un lema según la lista integrada, `None` para un lema fuera de la lista; el lema puede ir en cualquier caja. Un lema que no es una cadena, como un `Token` de spaCy en lugar de su `lemma_`, lanza `SourceTypeError`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `lemma` | `str` | - | Lema - la clave de `lemma_key` |

``` {.python .signature}
load_top_lemmas()
```

La lista entera del fichero `ests/resources/google_books_top10000.txt`, derivado de Google Books Ngram con licencia CC BY 3.0: la posición de cada lema, empezando por 1. La lista recoge los 10 000 lemas más frecuentes del [diccionario de frecuencias](../datasets/freqdict.md) por frecuencia decreciente, con las categorías gramaticales de un lema sumadas; deja fuera los nombres propios y los lemas cuyas filas de nombres propios pesan más que las demás (`garcía`), las letras sueltas salvo las palabras del español `a`, `e`, `o`, `u`, `y`, `á`, `é`, `ó`, y los lemas de dos letras y los números romanos que esMorph no conoce o que no tienen vocal (`pp`, `km`, `xix`), mientras que las abreviaturas de las referencias (`cit`) y las palabras inglesas de las bibliografías (`the`) se quedan.

=== "Código"

    ``` python
    from ests.lexical_stats import get_rank, load_top_lemmas

    get_rank("el"), get_rank("gato"), get_rank("felinólogo")
    len(load_top_lemmas())
    ```

=== "Resultado"

    ```
    (1, 3122, None)
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

<div class="metric-card" markdown>

### Nombres propios y abreviaturas { #proper_abbreviations }

`p_proper_nouns` · `p_abbreviations`
{ .metric-meta }

Las proporciones de los nombres propios y de las abreviaturas entre las palabras. Un nombre propio es una palabra con la etiqueta `PROPN` de esMorph o del modelo de un `Doc`. Una abreviatura es una palabra que termina en un punto, o en un punto y una letra volada (`ABBREVIATION_ENDINGS` de `ests.constants`). anySeg conserva el punto en las abreviaturas que conoce (`Sr.`, `pág.`, `EE. UU.`, `D.ª`, `n.º`) y en las iniciales (`J.`), así que una inicial cuenta en las dos proporciones; una dirección o un nombre de fichero (`www.rae.es`, `datos.csv`) no es una abreviatura. esMorph también etiqueta los tratamientos como nombres propios (`Sr.`, `D.`, `Ud.`); son cerca del 3% de los nombres propios del [corpus de literatura](../datasets/spanishliterature.md). Dos clases de abreviatura no se cuentan:

- las siglas y los acrónimos (`ONU`, `DNI`), porque ningún signo los distingue: las palabras en mayúsculas del corpus son los nombres de los personajes de las obras de teatro, los títulos de obras y el énfasis;
- una abreviatura al final de una oración (`etc.`), cuyo punto cierra la oración.

En 300 fragmentos del corpus, de 6000 caracteres cada uno, la mediana de la proporción de los nombres propios es del 3,2%, y solo 101 fragmentos tienen una abreviatura.

=== "Código"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El Sr. García y la Dra. Pérez viajaron a EE. UU. con la ONU")
    ls.p_proper_nouns, ls.p_abbreviations
    ```

=== "Resultado"

    ```
    (0.5, 0.2857142857142857)
    ```

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

Los demás métodos, `get_stats`, `to_dataframe`, [`by_parts`](basic_stats.md#by_parts), `print_stats` y `describe`, son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas de complejidad léxica no tienen escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    ls.get_stats()
    ```

=== "Resultado"

    ```
    {'coverage': 1.0,
     'mean_ipm': 34473.85272727273,
     'mean_ipm_content': 806.61,
     'mean_log_ipm': 3.5605446870314252,
     'mean_log_ipm_content': 2.1726800882059627,
     'mean_range': 40.0,
     'mean_dispersion': 97.18181818181819,
     'surprisal': 8.103695140372553,
     'perplexity': 275.0776547370405,
     'p_top1000': 0.7272727272727273,
     'p_top2000': 0.8181818181818182,
     'p_top5000': 1.0,
     'p_top10000': 1.0,
     'p_beyond_top10000': 0.0,
     'lexical_density': 0.45454545454545453,
     'p_proper_nouns': 0.0,
     'p_abbreviations': 0.0}
    ```
