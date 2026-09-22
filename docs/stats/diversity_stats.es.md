# Métricas de diversidad léxica

!!! info ""
    **ests.diversity_stats.DiversityStats**

## Descripción

Módulo para calcular las principales métricas de [diversidad léxica](https://en.wikipedia.org/wiki/Lexical_diversity) de un texto. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

El módulo permite usar un objeto [`WordsExtractor`](../extractors/words.md) ya configurado para la segmentación en palabras que precede al cálculo; para un `Doc`, el extractor indicado se aplica al texto del `Doc`, y sin él las palabras salen de sus tokens. Sea cual sea la fuente y el extractor, las palabras se pasan a minúsculas, porque todas las métricas cuentan lexemas.

!!! note "Nota"
    Las métricas se calculan al acceder al atributo correspondiente o al llamar al método `get_stats` del objeto `DiversityStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (cadena u objeto Doc) |
| `words_extractor` | WordsExtractor | `None` | Herramienta de extracción de palabras; para un Doc se aplica a su texto cuando se indica |
| `window_len` | int | `50` | Tamaño de la ventana para MATTR y del segmento para MSTTR |
| `mtld_threshold` | float | `0.72` | Umbral de TTR para MTLD, MA-MTLD y MTLD-W |
| `mtld_min_len` | int | `10` | Longitud mínima del factor para MTLD, MA-MTLD y MTLD-W |
| `hdd_sample_size` | int | `42` | Tamaño de la muestra para HD-D |
| `log_base` | float | `10` | Base del logaritmo para las métricas de Summer, Maas y Dugast |

## Convenciones { #conventions }

Los valores de algunas métricas dependen de parámetros que cada biblioteca elige de forma distinta. Los valores por defecto coinciden con koRpus y con lexical-diversity de Kyle, y todos son parámetros de la clase. La comparación con el umbral de MTLD es la única convención que no es un parámetro:

| Parámetro | esTS | Otras bibliotecas |
| :-------: | :--: | :---------------: |
| Base del logaritmo para Summer, Maas, U de Dugast y k de Dugast | 10 | LexicalRichness, textcomplexity y zipfR: natural |
| Ventana de MATTR y segmento de MSTTR | 50 | quanteda y koRpus: 100 |
| Umbral de TTR para MTLD | 0.72 | 0.66-0.75 en la bibliografía |
| Comparación con el umbral de MTLD | un factor se cierra con TTR ≤ 0.72; en McCarthy y Jarvis (2010) el factor termina cuando el TTR «alcanza» 0.720 | lexical-diversity y TAALED: `<` estricto, así que en los factores donde el TTR da exactamente el umbral (18/25, 36/50) los valores de MTLD, MA-MTLD y MTLD-W divergen |
| Longitud mínima del factor de MTLD | 10 | koRpus la aplica solo a MA-MTLD, LexicalRichness y textcomplexity no la aplican |
| Tamaño de la muestra de HD-D | 42 | 35-50 en la bibliografía |

Según Zenker y Kyle (2021), MATTR, MTLD y HD-D son estables en textos de 50-200 palabras o más, MTLD-W, MA-MTLD y Maas son inestables en textos cortos, y la familia de TTR nunca se estabiliza. Para comparar textos de distinta longitud use el [cálculo por ventanas](#windowed) con intervalos de confianza.

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[str] | Tupla de las palabras extraídas en minúsculas |
| `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` | int/float | Los parámetros de las métricas; cambiarlos en el objeto cambia las métricas |
| `frequency_spectrum` | dict[int, int] | Espectro de frecuencias: número de lexemas con una frecuencia dada |
| `ttr` | float | Type-Token Ratio (TTR) |
| `rttr` | float | Root Type-Token Ratio (RTTR) |
| `cttr` | float | Corrected Type-Token Ratio (CTTR) |
| `httr` | float | Herdan Type-Token Ratio (HTTR) |
| `sttr` | float | Summer Type-Token Ratio (STTR) |
| `mttr` | float | Maas Type-Token Ratio (MTTR) |
| `dttr` | float | Dugast Type-Token Ratio (DTTR) |
| `mattr` | float | Moving Average Type-Token Ratio (MATTR) |
| `msttr` | float | Mean Segmental Type-Token Ratio (MSTTR) |
| `mtld` | float | Measure of Textual Lexical Diversity (MTLD) |
| `mamtld` | float | Moving Average Measure of Textual Lexical Diversity (MA-MTLD) |
| `mtldw` | float | MTLD con ventana móvil y texto envuelto (MTLD-W) |
| `hdd` | float | Hypergeometric Distribution D (HD-D) |
| `simpson_index` | float | Índice de Simpson (D) |
| `inverse_simpson_index` | float | Índice de Simpson inverso (1/D) |
| `gini_simpson_index` | float | Índice de Gini-Simpson (1-D) |
| `hapax_index` | float | Índice de hápax, también R de Honoré |
| `honore_r` | float | Alias del índice de hápax |
| `yule_k` | float | Característica de Yule (K de Yule) |
| `yule_i` | float | Característica inversa de Yule (I de Yule) |
| `herdan_vm` | float | Vm de Herdan |
| `sichel_s` | float | S de Sichel |
| `michea_m` | float | M de Michéa |
| `brunet_w` | float | W de Brunet |
| `dugast_k` | float | k de Dugast |
| `baayen_p` | float | P de Baayen |
| `hapax_ratio` | float | Proporción de hápax entre los lexemas |
| `alpha2` | float | Exponente α₂ |
| `entropy` | float | Entropía de Shannon en bits |
| `evenness` | float | Equitatividad: cociente entre la entropía y su máximo |
| `perplexity` | float | Perplejidad |
| `zipf_alpha` | float | Pendiente de la ley de Zipf |
| `heaps_beta` | float | Exponente de la ley de Heaps |

!!! note "Nota"
    Cada métrica puede calcularse por separado llamando a la función correspondiente. La información detallada sobre las métricas de diversidad léxica y las funciones que las calculan está en la [sección](diversity_stats_funcs.md) correspondiente.

## Métodos

### windowed

Cálculo por ventanas de una métrica: su valor en ventanas consecutivas del texto de igual longitud, la media, la desviación típica muestral y el intervalo de confianza de la media por la distribución de Student. Es la forma estándar de comparar textos de distinta longitud; el STTR de Kubát y Milička es un TTR por ventanas de 1000 palabras con un intervalo de confianza del 95 %. En los textos más cortos que la ventana la métrica se calcula sobre todo el texto como una sola ventana; las ventanas con un valor no definido (`nan`) se ignoran. Si la métrica es infinita en al menos una ventana, la media es infinita y la desviación típica y el intervalo de confianza no están definidos.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `stat` | str | `-` | Nombre de la métrica de `get_stats` |
| `window_len` | int | `100` | Tamaño de la ventana |
| `step` | int | `None` | Paso de la ventana, por defecto igual a su tamaño (las ventanas no se solapan) |
| `confidence` | float | `0.95` | Nivel de confianza |

Devuelve una tupla con nombre `WindowStats` con los campos `mean`, `std`, `lower`, `upper` y `n_windows`. Un nombre de métrica desconocido lanza `UnknownStatError`.

!!! example "Ejemplo"

    ``` python
    from ests import DiversityStats

    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
    ds = DiversityStats(text)
    ds.windowed("ttr", window_len=5)
    # WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    # 6
    ```

### get_stats

Devuelve un diccionario con las métricas de diversidad léxica calculadas.

Ejemplo de cálculo de las métricas de diversidad léxica:

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import DiversityStats

    # Preparar los datos
    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"

    # Calcular las métricas
    ds = DiversityStats(text)
    ds.get_stats()
    ```

    _Resultado_:

    ``` bash
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

### print_stats

Muestra una tabla con las métricas de diversidad léxica calculadas.

Para ilustrar el método reutilizamos el código del ejemplo anterior:

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de métricas calculadas
    ds.print_stats()
    ```

    _Resultado_:

    ``` bash
                                      Metric                                   |  Value
    -------------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                     |   0.73
    Root Type-Token Ratio (RTTR)                                               |   2.84
    Corrected Type-Token Ratio (CTTR)                                          |   2.01
    Herdan Type-Token Ratio (HTTR)                                             |   0.89
    Summer Type-Token Ratio (STTR)                                             |   0.25
    Maas Type-Token Ratio (MTTR)                                               |   0.10
    Dugast Type-Token Ratio (DTTR)                                             |  10.27
    Moving Average Type-Token Ratio (MATTR)                                    |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                    |   0.73
    Measure of Textual Lexical Diversity (MTLD)                                |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)              |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)     |  13.25
    Hypergeometric Distribution D (HD-D)                                       |   nan
    Simpson's index (D)                                                        |   0.05
    Inverse Simpson's index (1/D)                                              |  21.00
    Gini-Simpson index (1-D)                                                   |   0.95
    Hapax index (Honoré's R)                                                   |  992.95
    Yule's characteristic K                                                    |  444.44
    Yule's inverse characteristic I                                            |   8.64
    Herdan's Vm                                                                |   0.14
    Sichel's S                                                                 |   0.18
    Michéa's M                                                                 |   5.50
    Brunet's W                                                                 |   6.01
    Dugast's k                                                                 |  14.78
    Baayen's P                                                                 |   0.53
    Hapax ratio                                                                |   0.73
    Exponent α₂                                                                |   0.50
    Shannon entropy (bits)                                                     |   3.32
    Evenness                                                                   |   0.96
    Perplexity                                                                 |  10.01
    Zipf's law slope (α)                                                       |   0.49
    Heaps' law exponent (β)                                                    |   0.84
    ```
