# Comparación de corpus

!!! info ""
    **ests.corpus.compare_corpora()**, **ests.corpus.compare_features()**, **ests.corpus.corpus_features()**, **ests.corpus.text_features()**, **ests.corpus.split_windows()**, **ests.corpus.sentence_rhythm()**

## Descripción

Comparación de dos corpus por todos los rasgos de un texto a la vez: qué estadísticas distinguen autores, géneros, traducciones, textos humanos y generados, y en qué medida. Para palabras sueltas hace lo mismo [`keyness`](keyness.md), para las distancias entre textos, [`delta`](stylometry.md#delta).

Los textos de ambos corpus se dividen en ventanas del mismo tamaño para que los rasgos no dependan de la longitud de un texto (`split_windows`: el número de ventanas es la razón del número de palabras al tamaño de una ventana redondeada al entero más próximo, al menos una, y las partes son iguales; un límite pasa antes de los signos de apertura de la primera palabra de una ventana - rayas, comillas, paréntesis, los signos `¿` y `¡` - para que no se pierda ninguna puntuación). Los rasgos se calculan para cada ventana (`text_features` o una función propia), y para cada rasgo se comparan los dos conjuntos de valores. El resultado es un `DataFrame` rasgo × estadísticas ordenado por el valor absoluto descendente de la delta de Cliff.

## Rasgos

`text_features(text, nlp=None)` devuelve 140 rasgos con un prefijo según su fuente:

| Prefijo | Rasgos | Fuente |
| :------ | :----- | :----- |
| `basic_` | proporciones de palabras únicas, largas, complejas, simples, monosílabas y polisílabas, de letras, espacios y signos de puntuación; letras y sílabas por palabra, palabras por oración | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | todas las fórmulas de legibilidad, el grado de consenso, el tiempo de lectura | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | todas las medidas de diversidad léxica | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | proporciones de las categorías gramaticales entre las palabras (`morph_pos_NOUN`), proporciones de los valores dentro de cada rasgo (`morph_mood_Sub`, `morph_tense_Past`) y los marcadores del español (`morph_p_ser`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) con el modelo de spaCy |
| `sents_` | longitud media de una oración en palabras, desviación típica, coeficiente de variación, autocorrelación de las longitudes vecinas (`sentence_rhythm`): el ritmo del texto | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frecuencias de los signos de puntuación por tipo por cada 1000 palabras y la proporción de los signos de apertura | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

Un valor de un rasgo morfológico que no aparece en una ventana da 0; un rasgo ausente de la ventana por completo (sin verbos no hay tiempo) da `nan`. La morfología necesita el análisis del modelo [`es_core_news_sm`](../installation.md#model) o del pipeline de `nlp`, que se lleva la mayor parte del tiempo: una ventana de 1000 palabras tarda unos 0.1 s. Un texto más largo que el `max_length` del pipeline lanza `SourceError`, así que una novela se compara por ventanas y no entera. Otro pipeline entra en la comparación con `functools.partial(text_features, nlp=nlp)`.

`corpus_features(texts, window, features)` devuelve la matriz de rasgos de las ventanas con el índice (número del texto, número de la ventana), para clasificadores propios, y `compare_features(table_a, table_b, labels, n_bootstrap, seed)` compara dos tablas así: `compare_corpora` es `corpus_features` para cada corpus seguido de `compare_features`. La división sirve cuando los rasgos se calculan una vez para varios corpus y hay que comparar pares, por ejemplo, todos los autores dos a dos.

Las proporciones de espacios, letras y signos de puntuación (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) cuentan los caracteres tal cual: las sangrías, los espacios dobles y los de no separación de los archivos reflejan la composición de una edición y no el texto. En un corpus de fuentes distintas conviene colapsarlos antes, por ejemplo, con `re.sub(r"[^\S\n]+", " ", text)`.

## Estadísticas

Para un rasgo con los valores $x_1 \dots x_{n_A}$ en el corpus A y $y_1 \dots y_{n_B}$ en el corpus B (sin los valores indefinidos e infinitos; con menos de dos valores en un lado, `nan`):

| Columna | Descripción |
| :------ | :---------- |
| `mean_A`, `mean_B`, `median_A`, `median_B` | medias y medianas |
| `median_diff`, `ci_low`, `ci_high` | la diferencia de las medianas y su intervalo bootstrap de percentiles al 95%: ambos conjuntos se remuestrean `n_bootstrap` veces (`bootstrap_median_diff`) |
| `cohen_d` | $d = (\bar{x} - \bar{y}) / s$, $s$ - la desviación típica combinada; 0.2 - un efecto pequeño, 0.5 - mediano, 0.8 - grande (`calc_cohen_d`) |
| `cliff_delta` | $\delta = P(x > y) - P(x < y)$ de −1 a 1; $\lvert\delta\rvert$ < 0.147 - un efecto despreciable, < 0.33 - pequeño, < 0.474 - mediano, grande en otro caso (Romano et al. 2006; `calc_cliff_delta`) |
| `auc` | el rasgo como clasificador por sí solo: la proporción de pares de ventanas en los que el valor en A es mayor que en B, con los empates a la mitad; $\delta = 2 \cdot AUC - 1$, 0.5 - el rasgo no distingue los corpus |
| `u`, `p_value` | el estadístico U de Mann-Whitney y el valor p bilateral (`scipy.stats.mannwhitneyu`) |
| `p_holm` | el valor p con la corrección de Holm por el número de rasgos (`holm_correction`): una tabla de cien filas sin corrección invita a falsos descubrimientos |
| `n_A`, `n_B` | número de ventanas con un valor definido |

La delta de Cliff y el AUC salen del mismo estadístico U y concuerdan entre sí; la d de Cohen es sensible a los valores atípicos y a la falta de normalidad, así que conviene leerla junto a la delta.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `a` | list[str] | `-` | Textos del primer corpus |
| `b` | list[str] | `-` | Textos del segundo corpus |
| `window` | int | `1000` | Tamaño de una ventana en palabras; `None` - los textos enteros |
| `features` | callable | `None` | Función de los rasgos de un texto; `None` - `text_features` |
| `labels` | tuple[str, str] | `("A", "B")` | Nombres de los corpus para las columnas |
| `n_bootstrap` | int | `1000` | Número de remuestras bootstrap |
| `seed` | int | `0` | Semilla del generador de números aleatorios; `None` - una aleatoria |

## Ejemplo de uso

Galdós frente a Unamuno, tres novelas de cada uno de [Project Gutenberg](https://www.gutenberg.org): *Marianela*, *Misericordia* y *Torquemada en la hoguera* frente a *Niebla*, *Abel Sánchez* y *La tía Tula*: 197 y 117 ventanas de 1000 palabras, alrededor de medio minuto tras la descarga.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from urllib.request import urlopen

    from ests.corpus import compare_corpora


    def gutenberg(number):
        url = f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
        text = urlopen(url).read().decode("utf-8")
        start = text.index("\n", text.index("*** START OF"))
        return text[start : text.index("*** END OF")]


    galdos = [gutenberg(number) for number in (17340, 21831, 15206)]
    unamuno = [gutenberg(number) for number in (49836, 44512, 44358)]

    result = compare_corpora(galdos, unamuno, window=1000, labels=("Galdós", "Unamuno"))
    columns = [
        "median_Galdós",
        "median_Unamuno",
        "ci_low",
        "ci_high",
        "cohen_d",
        "cliff_delta",
        "auc",
        "p_holm",
    ]
    result[columns].head(5).round(3)

    features = [
        "basic_letters_per_word",
        "readability_lix",
        "morph_p_gerund",
        "sents_mean",
        "punct_dash",
        "punct_exclamation",
    ]
    result.loc[features, columns].round(3)
    ```

    _Resultado_:

    ``` bash
                          median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_p_unique_words          0.494           0.420   0.069    0.084    3.159        0.976  0.988     0.0
    diversity_ttr                 0.494           0.420   0.069    0.084    3.159        0.976  0.988     0.0
    diversity_httr                0.898           0.874   0.022    0.027    3.118        0.975  0.988     0.0
    diversity_brunet_w           10.775          11.528  -0.857   -0.695   -3.073       -0.975  0.012     0.0
    diversity_dttr               29.349          23.840   5.077    6.113    3.048        0.975  0.987     0.0

                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.499           4.152   0.290    0.383    1.734        0.784  0.892     0.0
    readability_lix                40.006          30.074   8.446   11.936    1.285        0.743  0.872     0.0
    morph_p_gerund                  0.070           0.037   0.027    0.040    1.475        0.734  0.867     0.0
    sents_mean                     17.386          11.364   4.892    7.499    1.016        0.672  0.836     0.0
    punct_dash                      9.045          39.157 -34.148  -26.955   -1.810       -0.722  0.139     0.0
    punct_exclamation               9.970          24.096 -20.040  -11.960   -1.323       -0.634  0.183     0.0
    ```

Galdós tiene el vocabulario más rico: en el 99% de los pares de ventanas la suya tiene la mayor proporción de palabras únicas (AUC 0.988). Las medidas basadas en el número de palabras distintas - el TTR y sus transformaciones, MATTR, MTLD, los hápax - distinguen a los autores con una delta por encima de 0.9, mientras que el índice de Simpson, la K de Yule y la Vm de Herdan, que ponderan las palabras frecuentes, apenas lo hacen (por debajo de 0.12): la diferencia está en el vocabulario raro y no en la repetición de las palabras frecuentes. Sus palabras y oraciones son más largas, y usa casi el doble de gerundios entre las formas verbales. Unamuno escribe en diálogo: cuatro veces más rayas por cada 1000 palabras y más del doble de signos de exclamación y de interrogación. De los 140 rasgos, 92 tienen un valor p corregido por debajo de 0.01 y 63 muestran un efecto grande según la delta de Cliff: con cientos de ventanas la significación sale barata, y lo que importa es el tamaño del efecto.

Los rasgos propios, por ejemplo los sintácticos, se pasan como una función:

!!! example "Ejemplo"

    ``` python
    from ests import SyntaxStats
    from ests.corpus import compare_corpora, text_features
    from ests.utils import get_nlp

    nlp = get_nlp()


    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}


    compare_corpora(galdos, unamuno, window=1000, features=features, labels=("Galdós", "Unamuno"))
    ```
