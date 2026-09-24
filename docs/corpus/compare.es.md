# Comparación de corpus

!!! info ""
    **ests.corpus.compare_corpora()**, **ests.corpus.compare_features()**, **ests.corpus.corpus_features()**, **ests.corpus.text_features()**, **ests.corpus.split_windows()**, **ests.corpus.sentence_rhythm()**

## Descripción

Comparación de dos corpus por todos los rasgos de un texto a la vez: qué estadísticas distinguen autores, géneros, traducciones, textos humanos y generados, y en qué medida. Para palabras sueltas hace lo mismo [`keyness`](keyness.md), para las distancias entre textos, [`delta`](stylometry.md#delta).

Los textos de ambos corpus se dividen en ventanas de un tamaño parecido para que los rasgos no dependan de la longitud de un texto. En `split_windows` el número de ventanas es la razón del número de palabras al tamaño de una ventana redondeada al entero más próximo, al menos una, y las partes son iguales: un texto largo da ventanas a pocos puntos porcentuales del tamaño, un texto de una a dos ventanas da ventanas de 750 a 1499 palabras con una ventana de 1000, y un texto más corto que `min_words` - media ventana por defecto - no da ninguna, para que los textos cortos no enfrenten ventanas de tamaños muy distintos a las demás. Un límite pasa antes de los signos de apertura de la primera palabra de una ventana - rayas, comillas, paréntesis, los signos `¿` y `¡` - para que no se pierda ninguna puntuación, mientras que unas comillas rectas o una raya pegadas al final de la palabra anterior la cierran y se quedan con ella (`"cuatro"`, `—dijo Juan—`). Los rasgos se calculan para cada ventana (`text_features` o una función propia), y para cada rasgo se comparan los dos conjuntos de valores. El resultado es un `DataFrame` rasgo × estadísticas ordenado por el valor absoluto descendente de la delta de Cliff.

## Rasgos

`text_features(text, nlp=None)` devuelve 132 rasgos con un prefijo según su fuente:

| Prefijo | Rasgos | Fuente |
| :------ | :----- | :----- |
| `basic_` | proporciones de palabras largas, complejas, simples, monosílabas y polisílabas, de letras, espacios y signos de puntuación; letras y sílabas por palabra | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | todas las fórmulas de legibilidad y el grado de consenso | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | todas las medidas de diversidad léxica | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | proporciones de los valores de cada rasgo morfológico (`morph_pos_NOUN`, `morph_mood_Sub`, `morph_polarity_Neg`) y los marcadores del español (`morph_p_gerund`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) con el modelo de spaCy |
| `sents_` | longitud media de una oración en palabras, desviación típica, coeficiente de variación, autocorrelación de las longitudes vecinas (`sentence_rhythm`): el ritmo del texto | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frecuencias de los signos de puntuación por tipo por cada 1000 palabras y la proporción de los signos de apertura | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

Cada rasgo se cuenta una sola vez. El tiempo de lectura solo sigue el número de palabras de una ventana y se deja fuera; la proporción de palabras únicas repite `diversity_ttr`, las palabras por oración repiten `sents_mean` y los marcadores de los modos repiten `morph_mood_*`, así que también se dejan fuera.

Las categorías gramaticales y los rasgos de un solo valor - polaridad, cortesía, posesivo, reflexivo - son proporciones de todas las palabras (`morph_polarity_Neg` es la proporción de las negaciones), los demás rasgos, proporciones de las palabras que los llevan (`morph_mood_Sub` es el subjuntivo entre los modos). Un valor que no aparece en una ventana da 0; un rasgo ausente de la ventana por completo (sin verbos no hay tiempo) da `nan`. Un valor de varios valores, como el modelo escribe `PronType=Int,Rel` de *que* y `Case=Acc,Nom` de *usted*, se reparte a partes iguales entre sus partes, así que las proporciones de un rasgo siguen sumando uno.

La morfología la analiza el modelo [`es_core_news_sm`](../installation.md#model) sin su analizador sintáctico, lo que se lleva la mayor parte del tiempo: una ventana de 1000 palabras tarda unos 0.07 s. El análisis de dependencias añadiría un tercio más para un solo marcador, `morph_p_ser`, que lee de él las cópulas; un pipeline pasado en `nlp` se ejecuta entero salvo el reconocedor de entidades, así que `functools.partial(text_features, nlp=get_nlp())` devuelve el analizador sintáctico y `morph_p_ser`, y otro modelo entra en la comparación del mismo modo. Un texto más largo que el `max_length` del pipeline lanza `SourceError`, así que una novela se compara por ventanas y no entera.

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
| `n_texts_A`, `n_texts_B` | número de textos detrás de esas ventanas |

La delta de Cliff y el AUC salen del mismo estadístico U y concuerdan entre sí; la d de Cohen es sensible a los valores atípicos y a la falta de normalidad, así que conviene leerla junto a la delta.

!!! warning "Las ventanas de un texto no son independientes"
    La prueba y los tamaños del efecto toman cada ventana por una observación independiente, y las ventanas de un texto no lo son: comparten su trama, sus personajes, su narrador y su edición. Con pocos textos en un corpus los valores p salen demasiado pequeños y reflejan los textos elegidos tanto como los corpus: en el ejemplo de abajo dos novelas de un mismo autor difieren en 32 rasgos según la misma prueba. El bootstrap, en cambio, remuestrea textos enteros, el nivel `text` del índice que pone `corpus_features` (un bootstrap por conglomerados), así que su intervalo tiene en cuenta la dispersión entre los textos; necesita al menos dos textos en cada lado y es aproximado con solo unos pocos. Una tabla propia sin ese nivel toma cada fila por un texto aparte.

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
| `min_words` | int | `None` | Menor número de palabras de una ventana; `None` - media ventana, o una cuando `window` es `None` |

## Ejemplo de uso

Galdós frente a Unamuno, tres novelas de cada uno del [corpus de literatura](../datasets/spanishliterature.md): *Marianela*, *Misericordia* y *Torquemada en la hoguera* frente a *Niebla*, *Abel Sánchez* y *La tía Tula*: 157 y 117 ventanas de 1000 palabras, menos de medio minuto.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests.corpus import compare_corpora
    from ests.datasets import SpanishLiterature

    sl = SpanishLiterature()
    sl.download()
    galdos = [
        record["text"]
        for record in sl.get_records(author="galdos")
        if record["title"] in ("Marianela", "Misericordia", "Torquemada en la hoguera")
    ]
    unamuno = [
        record["text"]
        for record in sl.get_records(author="unamuno")
        if record["title"] in ("Niebla", "Abel Sánchez", "La tía Tula")
    ]

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
        "morph_polarity_Neg",
        "sents_mean",
        "punct_dash",
        "punct_exclamation",
        "diversity_yule_k",
    ]
    result.loc[features, columns].round(3)

    result.loc["sents_mean", ["n_Galdós", "n_Unamuno", "n_texts_Galdós", "n_texts_Unamuno"]].to_dict()
    ```

    _Resultado_:

    ``` bash
                      median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    diversity_mtldw         104.034          66.540  35.976   43.701    3.243        0.988  0.994     0.0
    diversity_mamtld        102.044          64.410  36.302   44.519    3.130        0.982  0.991     0.0
    diversity_mattr           0.816           0.769   0.045    0.053    2.964        0.981  0.991     0.0
    diversity_mtld          103.668          63.774  37.093   44.947    2.978        0.979  0.989     0.0
    diversity_msttr           0.817           0.770   0.045    0.054    2.839        0.973  0.987     0.0

                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.437           4.132   0.255    0.356    1.676        0.782  0.891     0.0
    readability_lix                38.221          29.469   7.443   10.806    1.085        0.700  0.850     0.0
    morph_p_gerund                  0.068           0.036   0.028    0.036    1.503        0.736  0.868     0.0
    morph_polarity_Neg              0.018           0.028  -0.013   -0.010   -1.130       -0.547  0.226     0.0
    sents_mean                     16.650          11.409   3.129    7.173    0.841        0.618  0.809     0.0
    punct_dash                     19.019          46.351 -40.474  -15.844   -1.315       -0.618  0.191     0.0
    punct_exclamation               8.016          23.928 -23.896   -3.779   -1.271       -0.629  0.186     0.0
    diversity_yule_k              104.859         110.355 -14.143   -1.203   -0.625       -0.318  0.341     0.0

    {'n_Galdós': 157, 'n_Unamuno': 117, 'n_texts_Galdós': 3, 'n_texts_Unamuno': 3}
    ```

Galdós tiene el vocabulario más rico: en el 98.4% de los pares de ventanas la suya tiene la mayor proporción de palabras distintas (el AUC de `diversity_ttr` es 0.984). Las medidas basadas en el número de palabras distintas - el TTR y sus transformaciones, MATTR, MTLD, los hápax - distinguen a los autores con una delta cercana a 0.9 o mayor, mientras que el índice de Simpson y la K de Yule, que ponderan las palabras frecuentes, lo hacen mucho menos (0.32, un efecto pequeño) y la Vm de Herdan apenas (0.15): la diferencia está sobre todo en el vocabulario raro y no en la repetición de las palabras frecuentes. Sus palabras y oraciones son más largas, y usa casi el doble de gerundios entre las formas verbales. Unamuno escribe en diálogo y en negaciones: dos veces y media más rayas por cada 1000 palabras, el triple de signos de exclamación y el doble de signos de interrogación, y más negaciones entre las palabras.

De los 132 rasgos, 94 tienen un valor p corregido por debajo de 0.01 y 63 muestran un efecto grande según la delta de Cliff, pero la prueba toma las 274 ventanas por independientes, y salen de seis novelas: según la misma prueba *Marianela* y *Misericordia*, dos novelas de Galdós, difieren en 32 rasgos. El intervalo de la diferencia de las medianas remuestrea novelas enteras y es la guía más segura - para la longitud de una oración va de 3.1 a 7.2 palabras, donde las ventanas solas darían de 3.8 a 6.3 -, aunque tres textos por lado también son pocos para un bootstrap, y una comparación de autores pide tantos textos como se puedan reunir.

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
