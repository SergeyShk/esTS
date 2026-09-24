# Funciones de las estadísticas

## Frecuencia según el diccionario { #frequency }

Los atributos `coverage`, `mean_ipm`, `mean_ipm_content`, `mean_log_ipm`, `mean_log_ipm_content`, `mean_range` y `mean_dispersion` de `LexicalStats` se calculan a partir de las entradas del [`FreqDict`](../datasets/freqdict.md) para las palabras del texto (`entries`), buscadas por [`lemma_key`](../datasets/freqdict.md#lemma_key): las medias se toman sobre las palabras encontradas en el diccionario, sobre todas ellas o solo sobre las palabras con contenido. La frecuencia media en ipm es sensible a las palabras funcionales (`el` - 98 000 ipm, `de` - 71 000), así que para comparar textos conviene más la frecuencia logarítmica o la media sobre las palabras con contenido.

## Sorpresa y perplejidad { #calc_surprisal }

!!! info ""
    **ests.lexical_stats.calc_surprisal()**

Cálculo de la sorpresa media de las palabras según el modelo de unigramas del diccionario de frecuencias. Una palabra fuera del diccionario recibe la frecuencia mínima del diccionario (0,1 ipm), así que la sorpresa está definida para todas las palabras; cuantas más palabras raras tiene un texto, más alta es. La perplejidad del texto `perplexity` es $2^{H}$.

Fórmula:

$$
H = -\frac{1}{N} \sum_{i=1}^{N} \log_2 \frac{\mathrm{ipm}(w_i)}{10^6}
$$

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `lemmas` | list[str] | `-` | Claves de las palabras (`lemma_key`) |
| `freq_dict` | FreqDict | `-` | Diccionario de frecuencias |

## Bandas de frecuencia { #get_rank }

!!! info ""
    **ests.lexical_stats.get_rank()**, **ests.lexical_stats.load_top_lemmas()**

Obtención del rango de un lema según la lista integrada de los 10 000 lemas más frecuentes del [diccionario de frecuencias](../datasets/freqdict.md) (el fichero `ests/resources/google_books_top10000.txt`, derivado de Google Books Ngram con licencia CC BY 3.0), `None` para un lema fuera de la lista. Las categorías gramaticales de un lema se suman y los nombres propios se dejan fuera; también las letras que no son palabras del español (`a`, `e`, `o`, `u`, `y`, `á`, `é`, `ó`) - las letras de las enumeraciones y las iniciales - y los lemas de dos letras y los números romanos que simplemma no conoce (`pp`, `vs`, `xix`). Las abreviaturas de las referencias (`cit`, `vol`) y las palabras inglesas de las bibliografías (`the`, `of`) se quedan, como tokens frecuentes de los libros. `LexicalStats` deduce de los rangos las proporciones de palabras del top 1000, 2000, 5000 y 10000 (`FREQUENCY_BANDS`) y fuera del top 10000 - un perfil de bandas de frecuencia a la manera del Lexical Frequency Profile; el método `band_coverage` da las proporciones para cualquier límite y sobre los lemas distintos. Las bandas toman la forma en minúsculas de un nombre propio, ya que la lista sola no distingue `París` de `parir`: un nombre propio cuya forma es un lema común recibe su rango (`Unión` 798, `Gobierno` 106, `Guerra` 240), mientras que los nombres y las partes flexionadas de los nombres (`Madrid`, `Estados`, `Naciones`) quedan fuera del top 10000, así que un texto lleno de nombres tiene una proporción mayor ahí. Un límite fuera de 1 y 10000 levanta `ParameterError`: más allá de la lista toda proporción sería la del top 10000.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `lemma` | str | `-` | Lema - la clave de `lemma_key` |

!!! example "Ejemplo"

    ``` python
    from ests.lexical_stats import get_rank

    get_rank("el"), get_rank("gato"), get_rank("felinólogo")
    # (1, 2851, None)
    ```

## Densidad léxica { #lexical_density }

El atributo `lexical_density` de `LexicalStats` es la proporción de palabras con contenido entre todas las palabras: una palabra con contenido es una de `CONTENT_UD_POS` (sustantivos, nombres propios, adjetivos, verbos, adverbios) y no demostrativa, como en [`CohesionStats`](cohesion_stats.md); los auxiliares (`es`, `ha`) no son palabras con contenido.
