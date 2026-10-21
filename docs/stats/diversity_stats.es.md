# Métricas de diversidad léxica

!!! info ""
    **ests.diversity_stats.DiversityStats**

## Descripción

<!-- core: stats/diversity_stats.md:DiversityStats 62610fe -->
Las principales métricas de [diversidad léxica](https://en.wikipedia.org/wiki/Lexical_diversity) de un texto, calculadas a partir de sus palabras.

La clase extiende el `DiversityStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/): en lugar de una lista de palabras recibe un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

Las palabras pueden extraerse con un [`WordsExtractor`](../extractors/words.md) ya configurado; para un `Doc`, el extractor indicado se aplica a su texto, y sin él las palabras salen de sus tokens. Las palabras siempre se pasan a minúsculas, porque todas las métricas cuentan lexemas.

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

## Atributos

<!-- core: stats/diversity_stats.md:DiversityStats-attributes 2e73f9a -->
El objeto guarda las palabras en `words`, una tupla, y los cinco parámetros con sus nombres, modificables en el objeto. `frequency_spectrum` es el espectro de frecuencias de las palabras (`calc_frequency_spectrum`), y `honore_r`, un alias de `hapax_index`.

## Métodos

### windowed

<!-- core: stats/diversity_stats.md:DiversityStats-windowed da979e4 -->
`windowed(stat, window_len=100, step=None, confidence=0.95)` calcula por ventanas una métrica de `get_stats` por su nombre: `calc_windowed` con la función de la métrica y los parámetros del objeto. Los demás argumentos, el resultado y los errores son los de `calc_windowed`; un nombre desconocido lanza `UnknownStatError`.

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

<!-- core: stats/diversity_stats.md:DiversityStats-get_stats fa25bfe -->
`get_stats()` devuelve un diccionario con las métricas calculadas de `stats_desc`.

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

<!-- core: stats/diversity_stats.md:DiversityStats-print_stats 8d60982 -->
`print_stats()` muestra una tabla de las métricas calculadas con sus descripciones de `stats_desc` bajo los encabezados de `stats_headers`.

El ejemplo continúa el anterior:

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
