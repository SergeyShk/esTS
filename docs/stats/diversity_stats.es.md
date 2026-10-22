# Métricas de diversidad léxica

``` {.python .signature}
DiversityStats(source, words_extractor=None, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

<!-- core: stats/diversity_stats.md:DiversityStats 62610fe -->
Las principales métricas de [diversidad léxica](https://en.wikipedia.org/wiki/Lexical_diversity) de un texto, calculadas a partir de sus palabras.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un extractor de otro tipo;
- `SourceError` - una fuente sin palabras;
- `ParameterError` - un parámetro que `check_params` rechaza.

La clase extiende el `DiversityStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/): en lugar de una lista de palabras recibe un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy). Las palabras de un texto las extrae el [`WordsExtractor`](../extractors/words.md) español o uno indicado, que para un `Doc` se aplica a su texto; sin extractor, las palabras de un `Doc` salen de sus tokens. Las palabras siempre se pasan a minúsculas, porque todas las métricas cuentan lexemas. La tabla de `print_stats` lleva las descripciones inglesas de las métricas del núcleo, `anyts.constants.DIVERSITY_STATS_DESC`.

=== "Código"

    ``` python
    from ests import DiversityStats

    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
    ds = DiversityStats(text)
    ds.print_stats()
    ```

=== "Resultado"

    ```
                                    Metric                                 |  Value
    ----------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                 |   0.73
    Root Type-Token Ratio (RTTR)                                           |   2.84
    Corrected Type-Token Ratio (CTTR)                                      |   2.01
    Herdan Type-Token Ratio (HTTR)                                         |   0.89
    Summer Type-Token Ratio (STTR)                                         |   0.25
    Maas Type-Token Ratio (MTTR)                                           |   0.10
    Dugast Type-Token Ratio (DTTR)                                         |  10.27
    Moving Average Type-Token Ratio (MATTR)                                |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                |   0.73
    Measure of Textual Lexical Diversity (MTLD)                            |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)          |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W) |  13.25
    Hypergeometric Distribution D (HD-D)                                   |   nan
    Simpson's index (D)                                                    |   0.05
    Inverse Simpson's index (1/D)                                          |  21.00
    Gini-Simpson index (1-D)                                               |   0.95
    Hapax index (Honoré's R)                                               |  992.95
    Yule's characteristic K                                                |  444.44
    Yule's inverse characteristic I                                        |   8.64
    Herdan's Vm                                                            |   0.14
    Sichel's S                                                             |   0.18
    Michéa's M                                                             |   5.50
    Brunet's W                                                             |   6.01
    Dugast's k                                                             |  14.78
    Baayen's P                                                             |   0.53
    Hapax ratio                                                            |   0.73
    Exponent α₂                                                            |   0.50
    Shannon entropy (bits)                                                 |   3.32
    Evenness                                                               |   0.96
    Perplexity                                                             |  10.01
    Zipf's law slope (α)                                                   |   0.49
    Heaps' law exponent (β)                                                |   0.84
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras; para un `Doc` se aplica a su texto |
| `window_len` | `int` | `50` | Tamaño de la ventana para MATTR y del segmento para MSTTR (`MATTR_WINDOW_LEN`) |
| `mtld_threshold` | `float` | `0.72` | Umbral de TTR para MTLD, MA-MTLD y MTLD-W (`MTLD_TTR_THRESHOLD`) |
| `mtld_min_len` | `int` | `10` | Longitud mínima del factor para MTLD, MA-MTLD y MTLD-W (`MTLD_MIN_LEN`) |
| `hdd_sample_size` | `int` | `42` | Tamaño de la muestra para HD-D (`HDD_SAMPLE_SIZE`) |
| `log_base` | `float` | `10` | Base del logaritmo para las métricas de Summer, Maas y Dugast (`DIVERSITY_LOG_BASE`) |

Las constantes de los valores por defecto entre paréntesis, aquí y en las tarjetas, son las de `anyts.constants`.

<!-- core: stats/diversity_stats.md:DiversityStats-attributes 2e73f9a -->
El objeto guarda las palabras en `words`, una tupla, y los cinco parámetros con sus nombres, modificables en el objeto. `frequency_spectrum` es el espectro de frecuencias de las palabras (`calc_frequency_spectrum`), y `honore_r`, un alias de `hapax_index`.

``` {.python .signature}
check_params(window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10, *, messages=MESSAGES)
```

<!-- core: stats/diversity_stats.md:check_params 84612a6 -->
Comprueba los parámetros de las métricas: un `window_len` o un `hdd_sample_size` que no es un entero de al menos uno, un `mtld_min_len` que no es un entero no negativo, un `mtld_threshold` que no es un número en (0, 1) y un `log_base` que no es un número finito mayor que 1 lanzan `ParameterError`. Llamada antes de extraer las palabras, señala un parámetro erróneo antes que un texto vacío.

## Convenciones { #conventions }

<!-- core: stats/diversity_stats.md:DiversityStats-conventions 22cd78d -->
Algunas métricas dependen de convenciones que difieren entre bibliotecas. Todas salvo la comparación con el umbral de MTLD son parámetros de la clase:

| Parámetro | Por defecto | Otras bibliotecas |
| :-------- | :------ | :-------------- |
| Base del logaritmo para Summer, Maas, U de Dugast y k de Dugast | `10` | LexicalRichness, textcomplexity y zipfR: natural |
| Ventana de MATTR y segmento de MSTTR | `50` | quanteda y koRpus: 100 |
| Umbral de TTR para MTLD | `0.72` | 0.66-0.75 en la bibliografía |
| Comparación con el umbral de MTLD | un factor se cierra con TTR ≤ 0.72 (McCarthy & Jarvis, 2010) | lexical-diversity y TAALED: `<` estricto; los valores difieren cuando el TTR da exactamente el umbral |
| Longitud mínima del factor de MTLD | `10` | koRpus: solo en MTLD-MA, descartando los factores más cortos en lugar de extenderlos; LexicalRichness y textcomplexity: no se aplica |
| Tamaño de la muestra de HD-D | `42` | 35-50 en la bibliografía |

Según Zenker y Kyle (2021), MATTR, MTLD y HD-D son estables en textos de 50-200 palabras o más, MTLD-W, MA-MTLD y Maas son inestables en textos cortos, y la familia de TTR nunca se estabiliza. Los textos de distinta longitud se comparan mediante el [cálculo por ventanas](#windowed) con intervalos de confianza.

## Métricas

<!-- core: stats/diversity_stats.md:DiversityStats-metrics bc5ee7c -->
Cada métrica es una propiedad del objeto, calculada en cada acceso por la función de su tarjeta con los parámetros del objeto, y `get_stats` las da todas.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`ttr`](#ttr) | Proporción de lexemas entre las palabras | 0-1 | Un vocabulario más rico |
| [`rttr`](#rttr) | Lexemas frente a la raíz cuadrada de las palabras | 0 o más | Un vocabulario más rico |
| [`cttr`](#cttr) | Lexemas frente a la raíz cuadrada del doble de las palabras | 0 o más | Un vocabulario más rico |
| [`httr`](#httr) | Lexemas frente a las palabras en logaritmos | 0-1 | Un vocabulario más rico |
| [`sttr`](#sttr) | Lexemas frente a las palabras en logaritmos dobles | 1 o menos, `nan` con un solo lexema o en un texto no más largo que la base | Un vocabulario más rico |
| [`mttr`](#mttr) | Repetición de las palabras en logaritmos | 0 o más | Un vocabulario más pobre |
| [`dttr`](#dttr) | Recíproco de la métrica de Maas | 0 o más, `inf` sin palabras repetidas | Un vocabulario más rico |
| [`mattr`](#mattr) | TTR medio de una ventana móvil | 0-1 | Un vocabulario más rico |
| [`msttr`](#msttr) | TTR medio de segmentos consecutivos | 0-1 | Un vocabulario más rico |
| [`mtld`](#mtld) | Palabras por factor, un tramo en el que el TTR baja hasta el umbral | Más de 0, `inf` sin palabras repetidas | Un vocabulario más rico |
| [`mamtld`](#mamtld) | Longitud media de los factores que empiezan en cada palabra | Hasta el número de palabras, `nan` si ningún factor se completa | Un vocabulario más rico |
| [`mtldw`](#mtldw) | Longitud media de los factores que empiezan en cada palabra, con vuelta al inicio del texto | Hasta el número de palabras, `nan` si ningún factor se completa | Un vocabulario más rico |
| [`hdd`](#hdd) | TTR esperado de una muestra aleatoria | 0-1, `nan` con menos de 50 palabras o menos palabras que la muestra | Un vocabulario más rico |
| [`simpson_index`](#simpson_index) | Probabilidad de que dos palabras sean el mismo lexema | 0-1, `nan` con menos de dos palabras | Un vocabulario más pobre |
| [`inverse_simpson_index`](#inverse_simpson_index) | Número efectivo de lexemas de orden dos | 1 o más, `inf` sin palabras repetidas, `nan` con menos de dos palabras | Un vocabulario más rico |
| [`gini_simpson_index`](#gini_simpson_index) | Probabilidad de que dos palabras sean lexemas distintos | 0-1, `nan` con menos de dos palabras | Un vocabulario más rico |
| [`hapax_index`](#hapax_index) | Proporción de hápax entre los lexemas frente a la longitud | 0 o más, `inf` sin palabras repetidas, `nan` con menos de dos palabras | Un vocabulario más rico |
| [`yule_k`](#yule_k) | Repetición de las palabras | 0-10 000, `nan` con menos de dos palabras | Un vocabulario más pobre |
| [`yule_i`](#yule_i) | Inversa de la K de Yule | Más de 0, `inf` sin palabras repetidas, `nan` con menos de dos palabras | Un vocabulario más rico |
| [`herdan_vm`](#herdan_vm) | Desigualdad de las frecuencias | 0-1, `nan` con menos de dos palabras | Un vocabulario más pobre |
| [`sichel_s`](#sichel_s) | Proporción de dis legomena entre los lexemas | 0-1 | Más lexemas usados dos veces |
| [`michea_m`](#michea_m) | Lexemas por dis legomenon | 1 o más, `inf` sin dis legomena | Menos lexemas usados dos veces |
| [`brunet_w`](#brunet_w) | Palabras frente a los lexemas | De 1 al número de palabras | Un vocabulario más pobre |
| [`dugast_k`](#dugast_k) | Lexemas frente a las palabras en logaritmos | 0 o más, `nan` en un texto no más largo que la base | Un vocabulario más rico |
| [`baayen_p`](#baayen_p) | Proporción de hápax entre las palabras | 0-1 | Un vocabulario que crece más deprisa |
| [`hapax_ratio`](#hapax_ratio) | Proporción de hápax entre los lexemas | 0-1 | Más lexemas usados una sola vez |
| [`alpha2`](#alpha2) | Forma de la parte baja del espectro de frecuencias | 1 o menos, `nan` sin hápax | Más hápax frente a dis legomena |
| [`entropy`](#entropy) | Información por palabra en bits | 0 o más | Un vocabulario más rico |
| [`evenness`](#evenness) | Entropía frente a su máximo | 0-1, `nan` con un solo lexema | Frecuencias más uniformes |
| [`perplexity`](#perplexity) | Número efectivo de lexemas | De 1 al número de lexemas | Un vocabulario más rico |
| [`zipf_alpha`](#zipf_alpha) | Caída de la frecuencia con el rango | 0 o más, `nan` con un solo lexema | Frecuencias que caen más deprisa |
| [`heaps_beta`](#heaps_beta) | Crecimiento del vocabulario con la longitud | 0 o más, `nan` con menos de dos palabras | Un vocabulario que crece más deprisa |

Las funciones y las tuplas con nombre de las tarjetas se importan de `ests.diversity_stats`.

<div class="metric-card" markdown>

### Type-Token Ratio (TTR) { #ttr }

`ttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_ttr 4982ca2 -->
``` {.python .signature}
calc_ttr(text)
```

La medida más simple de la diversidad léxica; no está corregida por la longitud del texto.

$$
\frac{\textrm{Número de lexemas}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Root Type-Token Ratio (RTTR) { #rttr }

`rttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_rttr 565f2bc -->
``` {.python .signature}
calc_rttr(text)
```

Una modificación del TTR (Guiraud, 1960).

$$
\frac{\textrm{Número de lexemas}}{\sqrt{\textrm{(Número de palabras)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Corrected Type-Token Ratio (CTTR) { #cttr }

`cttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_cttr 06c97ca -->
``` {.python .signature}
calc_cttr(text)
```

Una modificación del TTR (Carroll, 1964).

$$
\frac{\textrm{Número de lexemas}}{\sqrt{2\times\textrm{(Número de palabras)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Herdan Type-Token Ratio (HTTR) { #httr }

`httr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_httr 42487d4 -->
``` {.python .signature}
calc_httr(text)
```

Una modificación logarítmica del TTR (Herdan, 1960).

$$
\frac{\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Summer Type-Token Ratio (STTR) { #sttr }

`sttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_sttr 1847a8d -->
``` {.python .signature}
calc_sttr(text, base=10)
```

Una modificación logarítmica del TTR (Summer, 1966). El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)). Es `nan` en un texto de un solo lexema, donde el numerador no está definido, y en un texto no más largo que la base ($\log \log N \le 0$), incluidas las ventanas así de cortas de `calc_windowed`.

$$
\frac{\log_{10} {\log_{10} {\textrm{(Número de lexemas)}}}}{\log_{10} {\log_{10} {{\textrm{(Número de palabras)}}}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Maas Type-Token Ratio (MTTR) { #mttr }

`mttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mttr 4d5f1b1 -->
``` {.python .signature}
calc_mttr(text, base=10)
```

Una modificación logarítmica del TTR (Maas, 1972). El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)).

$$
\frac{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}^2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Dugast Type-Token Ratio (DTTR) { #dttr }

`dttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_dttr 654db67 -->
``` {.python .signature}
calc_dttr(text, base=10)
```

Una modificación logarítmica del TTR (Dugast, 1978), el recíproco de la métrica de Maas. El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)). Un texto sin palabras repetidas tiene un valor infinito.

$$
\frac{\log_{10} {{\textrm{(Número de palabras)}}}^2}{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Moving Average Type-Token Ratio (MATTR) { #mattr }

`mattr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mattr e57be40 -->
``` {.python .signature}
calc_mattr(text, window_len=50)
```

Una modificación del TTR con media móvil (Covington & McFall, 2010), independiente de la longitud del texto: una ventana de tamaño fijo se desliza por el texto y se promedia el TTR de cada ventana. En los textos más cortos que la ventana se devuelve el TTR de todo el texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `window_len` | `int` | `50` | Tamaño de la ventana (`MATTR_WINDOW_LEN`) |

Un `window_len` que no es un entero de al menos uno lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Mean Segmental Type-Token Ratio (MSTTR) { #msttr }

`msttr`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_msttr 21799ac -->
``` {.python .signature}
calc_msttr(text, segment_len=50)
```

Una modificación del TTR por segmentación (Johnson, 1944), independiente de la longitud del texto: el texto se divide en segmentos de tamaño fijo y se promedia el TTR de cada segmento; un último segmento incompleto se descarta. En los textos más cortos que el segmento se devuelve el TTR de todo el texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `segment_len` | `int` | `50` | Tamaño del segmento (`MATTR_WINDOW_LEN`) |

Un `segment_len` que no es un entero de al menos uno lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Measure of Textual Lexical Diversity (MTLD) { #mtld }

`mtld`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mtld 427e11b -->
``` {.python .signature}
calc_mtld(text, min_len=10, threshold=0.72)
```

Una modificación del MSTTR (McCarthy, 2005), independiente de la longitud del texto: el número de palabras dividido por el número de factores, los tramos en los que el TTR baja hasta el umbral (`TTR <= threshold`, véanse las [convenciones](#conventions)). Un último factor incompleto cuenta en proporción a lo que su TTR se acercó al umbral. El valor es la media de una pasada hacia delante y otra hacia atrás (McCarthy & Jarvis, 2010). La longitud mínima del factor no es estándar (lexical-diversity de Kyle), y un `min_len` de 0 la desactiva. Si ningún factor se completa y el TTR nunca baja de 1, el valor es infinito.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

</div>

<div class="metric-card" markdown>

### Moving Average Measure of Textual Lexical Diversity (MA-MTLD) { #mamtld }

`mamtld`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mamtld c845458 -->
``` {.python .signature}
calc_mamtld(text, min_len=10, threshold=0.72)
```

Una modificación de MTLD con ventana móvil según el MTLD-MA de koRpus: un factor empieza en cada posición del texto, y el valor es la longitud media de los factores completados en una pasada hacia delante y otra hacia atrás. koRpus hace solo la pasada hacia delante, cierra un factor con un TTR estrictamente menor que el umbral y descarta los factores más cortos que la longitud mínima en lugar de extenderlos. Si ningún factor se completa, el valor es `nan`. La métrica es inestable en textos cortos.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

</div>

<div class="metric-card" markdown>

### MTLD con ventana móvil y vuelta al inicio del texto (MTLD-W) { #mtldw }

`mtldw`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_mtldw 6e0e9fe -->
``` {.python .signature}
calc_mtldw(text, min_len=10, threshold=0.72)
```

Una modificación de MA-MTLD según `mtld_ma_wrap` de lexical-diversity y TAALED: los factores no completados al final del texto continúan desde su principio, así que todas las posiciones tienen el mismo peso. Un factor no puede ser más largo que el texto. Si ningún factor se completa, porque el texto es más corto que `min_len` o porque el TTR no baja hasta el umbral desde ningún inicio, el valor es `nan`. La métrica es inestable en textos de menos de 100 palabras.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

</div>

<div class="metric-card" markdown>

### Hypergeometric Distribution D (HD-D) { #hdd }

`hdd`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hdd 44ad1ca -->
``` {.python .signature}
calc_hdd(text, sample_size=42)
```

Una alternativa a vocd-D (McCarthy & Jarvis, 2010): el TTR esperado exacto de una muestra aleatoria de `sample_size` palabras, sin extraer muestras. La distribución hipergeométrica da la probabilidad de que la muestra contenga cada lexema al menos una vez; HD-D es la suma de estas probabilidades dividida por el tamaño de la muestra. En los textos de menos de 50 palabras o más cortos que el tamaño de la muestra la métrica no está definida, y el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `sample_size` | `int` | `42` | Tamaño de la muestra en palabras (`HDD_SAMPLE_SIZE`) |

Un `sample_size` que no es un entero de al menos uno lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice de Simpson (D) { #simpson_index }

`simpson_index` · [Wikipedia](https://es.wikipedia.org/wiki/Índice_de_diversidad#Índice_de_Simpson)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_simpson_index 5c0c871 -->
``` {.python .signature}
calc_simpson_index(text)
```

La probabilidad de que dos palabras extraídas del texto al azar sin reemplazo sean el mismo lexema; $n$ es el número de apariciones de un lexema en el texto. En los textos de menos de dos palabras el índice no está definido, y el valor es `nan`; lo mismo vale para el índice de Simpson inverso y el índice de Gini-Simpson.

$$
\frac{\sum n\times(n-1)}{\textrm{(Número de palabras)}\times(\textrm{Número de palabras}-1)}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Índice de Simpson inverso (1/D) { #inverse_simpson_index }

`inverse_simpson_index` · [Wikipedia](https://es.wikipedia.org/wiki/Índice_de_diversidad#Índice_de_Simpson_inverso)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_inverse_simpson_index 370880d -->
``` {.python .signature}
calc_inverse_simpson_index(text)
```

Una estimación del número de Hill de orden dos ($1/\sum_k p_k^2$) a partir de pares extraídos sin reposición. Si todas las palabras del texto son únicas, el índice de Simpson es 0 y el índice inverso es infinito.

$$
\frac{1}{D}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Índice de Gini-Simpson (1-D) { #gini_simpson_index }

`gini_simpson_index` · [Wikipedia](https://es.wikipedia.org/wiki/Índice_de_diversidad#Índice_de_Gini-Simpson)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_gini_simpson_index 00e1184 -->
``` {.python .signature}
calc_gini_simpson_index(text)
```

La probabilidad de que dos palabras del texto elegidas al azar sean distintas.

$$
1-D
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Índice de hápax (R de Honoré) { #hapax_index }

`hapax_index` · `honore_r` · [Wikipedia](https://es.wikipedia.org/wiki/Hápax)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hapax_index debfb9b -->
``` {.python .signature}
calc_hapax_index(text)
```

Un hápax (del griego ἅπαξ λεγόμενον, «dicho una sola vez») es una palabra que aparece una sola vez en un corpus: *baciyelmo*, la palabra con que Sancho Panza llama a la bacía que don Quijote toma por yelmo, es un hápax de Cervantes (capítulo 44 de la primera parte del *Quijote*). El índice coincide con la medida de Honoré (1979), con el logaritmo natural. Si todas las palabras del texto son hápax, el índice es infinito; en los textos de menos de dos palabras no está definido, y el valor es `nan`. `calc_honore_r` es la misma función.

$$
100\times\frac{\ln {\textrm{(Número de palabras)}}}{1-\frac{\textrm{Número de hápax}}{\textrm{Número de lexemas}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Espectro de frecuencias { #frequency_spectrum }

`frequency_spectrum`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_frequency_spectrum 5ca9622 -->
``` {.python .signature}
calc_frequency_spectrum(text)
```

El número de lexemas $V_i$ que aparecen exactamente $i$ veces en el texto, como un diccionario por la frecuencia $i$ en orden ascendente. A partir de él se calculan el índice de hápax, la K y la I de Yule, la Vm de Herdan, la S de Sichel, la M de Michéa, la P de Baayen, la proporción de hápax y el exponente α₂, con las fórmulas de Tweedie y Baayen (1998).

Notación: $N$ es el número de palabras, $V$ el número de lexemas, $V_i$ el número de lexemas con frecuencia $i$, $V_1$ los hápax, $V_2$ los dis legomena, $p_k$ la frecuencia relativa de un lexema.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Característica de Yule (K de Yule) { #yule_k }

`yule_k`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_yule_k baaaa5a -->
``` {.python .signature}
calc_yule_k(text)
```

La característica de Yule (Yule, 1944), una de las pocas medidas teóricamente independientes de la longitud del texto (Tweedie & Baayen, 1998); en la práctica converge a medida que el texto crece. Es proporcional al índice de Simpson: $K \approx 10^4 \cdot D$. En los textos de menos de dos palabras el valor es `nan`.

$$
K = 10^4\times\frac{\sum_i i^2 V_i - N}{N^2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Característica inversa de Yule (I de Yule) { #yule_i }

`yule_i`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_yule_i e6ed7d8 -->
``` {.python .signature}
calc_yule_i(text)
```

La característica inversa de Yule. Si todas las palabras del texto son únicas, el valor es infinito; en los textos de menos de dos palabras es `nan`.

$$
I = \frac{V^2}{\sum_i i^2 V_i - V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Vm de Herdan { #herdan_vm }

`herdan_vm`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_herdan_vm a9088dd -->
``` {.python .signature}
calc_herdan_vm(text)
```

La medida de Herdan (Herdan, 1955), teóricamente independiente de la longitud del texto. En los textos de menos de dos palabras el valor es `nan`.

$$
V_m = \sqrt{\sum_i V_i \left(\frac{i}{N}\right)^2 - \frac{1}{V}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### S de Sichel { #sichel_s }

`sichel_s`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_sichel_s 5485001 -->
``` {.python .signature}
calc_sichel_s(text)
```

La medida de Sichel (Sichel, 1975): la proporción de dis legomena, lexemas con frecuencia 2, entre todos los lexemas. Estable en textos de distinta longitud.

$$
S = \frac{V_2}{V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### M de Michéa { #michea_m }

`michea_m`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_michea_m 8e3f6f5 -->
``` {.python .signature}
calc_michea_m(text)
```

La medida de Michéa (Michéa, 1969): el recíproco de la medida de Sichel. Si el texto no tiene dis legomena, el valor es infinito.

$$
M = \frac{V}{V_2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### W de Brunet { #brunet_w }

`brunet_w`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_brunet_w 2ac7def -->
``` {.python .signature}
calc_brunet_w(text, a=0.172)
```

La medida de Brunet (Brunet, 1978). Los valores de los textos suelen estar entre 10 y 20.

$$
W = N^{V^{-a}}, \quad a = 0.172
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `a` | `float` | `0.172` | Exponente (`BRUNET_W_EXPONENT`) |

Un `a` que no es un número finito lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### k de Dugast { #dugast_k }

`dugast_k`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_dugast_k a8d476b -->
``` {.python .signature}
calc_dugast_k(text, base=10)
```

La medida de Dugast (Dugast, 1979), que no debe confundirse con la U de Dugast, la métrica [DTTR](#dttr). El valor depende de la base del logaritmo. En los textos no más largos que la base ($\log N \le 1$) la medida no está definida, y el valor es `nan`.

$$
k = \frac{\log V}{\log \log N}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### P de Baayen { #baayen_p }

`baayen_p`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_baayen_p 3754bfb -->
``` {.python .signature}
calc_baayen_p(text)
```

La medida de Baayen (Baayen, 1991): la proporción de hápax entre todas las palabras del texto. Es la pendiente de la curva de crecimiento del vocabulario al final del texto: la probabilidad de que la siguiente palabra sea nueva (Evert, 2004).

$$
P = \frac{V_1}{N}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Proporción de hápax { #hapax_ratio }

`hapax_ratio`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_hapax_ratio d3c3e24 -->
``` {.python .signature}
calc_hapax_ratio(text)
```

La proporción de hápax entre todos los lexemas del texto.

$$
\frac{V_1}{V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### El exponente α₂ { #alpha2 }

`alpha2`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_alpha2 69486ad -->
``` {.python .signature}
calc_alpha2(text)
```

Una estimación del parámetro de Zipf-Mandelbrot a partir de la parte baja del espectro de frecuencias (Evert, 2004). Si el texto no tiene hápax, el valor es `nan`.

$$
\alpha_2 = 1 - \frac{2 V_2}{V_1}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Entropía de Shannon { #entropy }

`entropy` · [Wikipedia](https://es.wikipedia.org/wiki/Índice_de_diversidad#Índice_de_Shannon)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_entropy 507c0b8 -->
``` {.python .signature}
calc_entropy(text)
```

La entropía de la distribución de lexemas en bits. El número de Hill de orden uno es $2^H$ ([perplejidad](#perplexity)), y el de orden cero, $V$; el [índice de Simpson inverso](#inverse_simpson_index) estima el de orden dos.

$$
H = -\sum_k p_k \log_2 p_k
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Equitatividad { #evenness }

`evenness`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_evenness d6817c3 -->
``` {.python .signature}
calc_evenness(text)
```

La equitatividad de Pielou: el cociente entre la entropía de Shannon y su máximo para el número de lexemas dado. En los textos de un solo lexema no está definida, y el valor es `nan`.

$$
\frac{H}{\log_2 V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Perplejidad { #perplexity }

`perplexity`
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_perplexity b5c954f -->
``` {.python .signature}
calc_perplexity(text)
```

El número de Hill de orden uno, el número efectivo de lexemas del texto.

$$
2^H
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Pendiente de la ley de Zipf { #zipf_alpha }

`zipf_alpha` · [Wikipedia](https://es.wikipedia.org/wiki/Ley_de_Zipf)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_zipf_alpha a63837a -->
``` {.python .signature}
calc_zipf_alpha(text)
```

El exponente $\alpha$ de la ley de Zipf $f(r) \propto r^{-\alpha}$, donde $r$ es el rango de frecuencia de un lexema, estimado por regresión lineal del logaritmo de la frecuencia sobre el logaritmo del rango. En los textos naturales $\alpha$ está cerca de 1. La estimación por mínimos cuadrados sobre los rangos está sesgada; la máxima verosimilitud es más precisa. En los textos de un solo lexema el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

</div>

<div class="metric-card" markdown>

### Ajuste de Zipf-Mandelbrot { #fit_zipf_mandelbrot }

[Wikipedia](https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:fit_zipf_mandelbrot 41b2359 -->
``` {.python .signature}
fit_zipf_mandelbrot(text)
```

Ajusta la ley de Zipf-Mandelbrot $f(r) = C / (r + q)^s$ a la distribución rango-frecuencia. Con $q = 0$ es la ley de Zipf con exponente $s$; el desplazamiento $q$ recoge el aplanamiento de la curva en las palabras más frecuentes. El ajuste se hace por mínimos cuadrados en coordenadas logarítmicas con $q \ge 0$, $s \ge 0$; los lexemas de frecuencia cero de un contador se dejan fuera. El resultado es una tupla con nombre `ZipfMandelbrot` con los campos `c`, `q`, `s` y `r2`, el coeficiente de determinación del ajuste en coordenadas logarítmicas. Todos los campos son `nan` en los textos de menos de tres lexemas, con frecuencias idénticas de todos los lexemas o cuando el ajuste diverge. En textos cortos los parámetros son inestables: la ley describe corpus grandes.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` / `Counter` | - | Lista de palabras o un contador de sus frecuencias |

Un contador cuyas palabras no son cadenas o cuyas frecuencias no son números lanza `SourceTypeError`, y una frecuencia negativa, `nan` o infinita, `SourceError` (`check_counts`).

El visualizador de la [ley de Zipf](../visualizers/zipf.md) dibuja este ajuste con `show_fit=True`.

=== "Código"

    ``` python
    from ests.diversity_stats import fit_zipf_mandelbrot

    # las frecuencias 12, 6, 4, 3 siguen exactamente la ley f = 12 / r
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    ```

=== "Resultado"

    ```
    (12.001, 0.0, 1.0, 1.0)
    ```

</div>

<div class="metric-card" markdown>

### Exponente de la ley de Heaps { #heaps_beta }

`heaps_beta` · [Wikipedia](https://es.wikipedia.org/wiki/Ley_de_Heaps)
{ .metric-meta }

<!-- core: stats/diversity_stats.md:calc_heaps_beta 6aaa64a -->
``` {.python .signature}
calc_heaps_beta(text)
```

El exponente $\beta$ de la ley de Heaps $V(N) = K \cdot N^{\beta}$ del crecimiento del vocabulario con la longitud del texto, estimado por regresión lineal del logaritmo del tamaño del vocabulario sobre el logaritmo de la longitud del texto a lo largo de la curva de crecimiento. En corpus de millones de palabras $\beta$ está entre 0.4 y 0.6, en un solo texto entre 0.6 y 0.9, así que los valores solo son comparables entre textos de longitud parecida. El valor depende del orden de las palabras y necesita varios cientos de palabras o más. En los textos de menos de dos palabras el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

<!-- core: stats/diversity_stats.md:vocabulary_growth d1f1d6d -->
``` {.python .signature}
vocabulary_growth(text)
```

La curva de crecimiento del vocabulario de una lista de palabras: el tamaño del vocabulario tras cada palabra del texto.

<!-- core: stats/diversity_stats.md:fit_heaps eefb450 -->
``` {.python .signature}
fit_heaps(text)
```

Ajusta la ley de Heaps sobre la curva de crecimiento del vocabulario de una lista de palabras, como hace `calc_heaps_beta`, y devuelve una tupla con nombre `HeapsFit` con los parámetros `k`, `beta` y el coeficiente de determinación `r2`, todos `nan` en los textos de menos de dos palabras; `r2` es `nan` también en un texto de un solo lexema.

El gráfico de la [ley de Heaps](../visualizers/vocabulary.md) se construye a partir de `fit_heaps`.

</div>

<div class="metric-card" markdown>

### Cálculo por ventanas { #windowed }

`windowed(stat)`
{ .metric-meta }

``` {.python .signature}
calc_windowed(text, func, window_len=100, step=None, confidence=0.95, *, messages=MESSAGES)
```

<!-- core: stats/diversity_stats.md:calc_windowed 40fa4f2 -->
Los valores de una métrica en ventanas consecutivas de igual longitud dan su media, su desviación típica muestral y el intervalo de confianza de la media por la distribución de Student. Es la forma estándar de comparar textos de distinta longitud; el TTR estandarizado de Kubát y Milička (no el STTR de Summer) es un TTR por ventanas de 1000 palabras con un intervalo del 95 %. Un texto más corto que la ventana es una sola ventana; las ventanas con valor `nan` se ignoran. Con menos de dos ventanas de valor definido la desviación y el intervalo son `nan`, y sin ninguna también la media. Una métrica infinita en alguna ventana (por ejemplo, el índice de Simpson inverso en una ventana de palabras únicas) hace la media infinita y la desviación y el intervalo `nan`. El resultado es una tupla con nombre `WindowStats` con los campos `mean`, `std`, `lower`, `upper` y `n_windows`, el número de ventanas de valor definido.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `func` | `Callable` | - | Función que calcula la métrica a partir de una lista de palabras |
| `window_len` | `int` | `100` | Tamaño de la ventana |
| `step` | `int` | `None` | Paso de la ventana; por defecto, el tamaño de la ventana, así que las ventanas no se solapan |
| `confidence` | `float` | `0.95` | Nivel de confianza |
| `messages` | `dict[str, str]` | `MESSAGES` | Mensajes de los errores por clave |

Un `func` que no es invocable lanza `SourceTypeError`; un `window_len` o un `step` que no es un entero de al menos uno y un `confidence` que no es un número en (0, 1) lanzan `ParameterError`.

</div>

<!-- core: stats/diversity_stats.md:diversity-checks 518d85e -->
Cada función comprueba sus palabras con `check_words`: un `text` que es una cadena, un `Doc`, un iterador, un conjunto o una tabla, o cuyas palabras no son cadenas, lanza `SourceTypeError`; `fit_zipf_mandelbrot` admite también un contador.

## Métodos

<!-- core: stats/diversity_stats.md:DiversityStats-windowed da979e4 -->
`windowed(stat, window_len=100, step=None, confidence=0.95)` calcula por ventanas una métrica de `get_stats` por su nombre: `calc_windowed` con la función de la métrica y los parámetros del objeto. Los demás argumentos, el resultado y los errores son los de `calc_windowed`; un nombre desconocido lanza `UnknownStatError`.

=== "Código"

    ``` python
    ds.windowed("ttr", window_len=5)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    ```

=== "Resultado"

    ```
    WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    6
    ```

<!-- core: stats/diversity_stats.md:DiversityStats-get_stats fa25bfe -->
`get_stats()` devuelve un diccionario con las métricas calculadas de `stats_desc`.

<!-- core: stats/diversity_stats.md:DiversityStats-print_stats 8d60982 -->
`print_stats()` muestra una tabla de las métricas calculadas con sus descripciones de `stats_desc` bajo los encabezados de `stats_headers`.

=== "Código"

    ``` python
    ds.get_stats()
    ```

=== "Resultado"

    ```
    {'ttr': 0.7333333333333333,
     'rttr': 2.840187787218772,
     'cttr': 2.008316044185609,
     'httr': 0.8854692840710255,
     'sttr': 0.2500605793160848,
     'mttr': 0.09738250756232528,
     'dttr': 10.268784661968118,
     'mattr': 0.7333333333333333,
     'msttr': 0.7333333333333333,
     'mtld': 15.0,
     'mamtld': 12.0,
     'mtldw': 13.25,
     'hdd': nan,
     'simpson_index': 0.047619047619047616,
     'inverse_simpson_index': 21.0,
     'gini_simpson_index': 0.9523809523809523,
     'hapax_index': 992.9517404041437,
     'yule_k': 444.44444444444446,
     'yule_i': 8.642857142857142,
     'herdan_vm': 0.1421338109037403,
     'sichel_s': 0.18181818181818182,
     'michea_m': 5.5,
     'brunet_w': 6.00637847898991,
     'dugast_k': 14.783895126869226,
     'baayen_p': 0.5333333333333333,
     'hapax_ratio': 0.7272727272727273,
     'alpha2': 0.5,
     'entropy': 3.3232314287976203,
     'evenness': 0.9606293157795304,
     'perplexity': 10.009038104159247,
     'zipf_alpha': 0.4884512334695912,
     'heaps_beta': 0.8366147342060046}
    ```

Los demás métodos, `to_dataframe` y `describe`, son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las métricas de diversidad léxica no tienen escalas, así que `describe` da `None` para las métricas de `get_stats`.
