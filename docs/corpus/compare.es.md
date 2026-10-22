# Comparación de corpus

``` {.python .signature}
compare_corpora(a, b, window=1000, features=None, labels=('A', 'B'), n_bootstrap=1000, seed=0, min_words=None)
```

Compara dos corpus de textos en español por todos los rasgos de un texto a la vez: qué estadísticas distinguen los corpus y en qué medida. Para palabras sueltas hace lo mismo [`keyness`](keyness.md), para las distancias entre textos, [`delta`](stylometry.md#delta).

Los textos se cortan seguidos en ventanas de exactamente `window` palabras con [`split_windows`](#split_windows), así que las ventanas de todos los textos tienen la misma longitud; el resto incompleto al final de un texto y un texto más corto que una ventana se descartan salvo que `min_words` admita ventanas más cortas. Los rasgos de cada ventana los calcula [`text_features`](#text_features) o una función propia, y las tablas de los dos corpus las compara [`compare_features`](#compare_features) del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/).

Galdós frente a Unamuno, tres novelas de cada uno del [corpus de literatura](../datasets/spanishliterature.md): *Marianela*, *Misericordia* y *Torquemada en la hoguera* frente a *Niebla*, *Abel Sánchez* y *La tía Tula*.

=== "Código"

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

=== "Resultado"

    ```
                      median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    diversity_mtldw         105.455          66.179  37.104   43.850    3.260        0.988  0.994     0.0
    diversity_mamtld        103.316          64.814  35.081   45.200    3.083        0.981  0.990     0.0
    diversity_mtld          103.655          63.851  38.320   47.911    3.110        0.981  0.990     0.0
    diversity_mattr           0.817           0.769   0.046    0.057    2.952        0.979  0.990     0.0
    diversity_msttr           0.819           0.769   0.047    0.059    2.929        0.979  0.989     0.0

                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.441           4.130   0.243    0.356    1.695        0.784  0.892     0.0
    readability_lix                37.906          29.721   6.954   11.023    1.084        0.694  0.847     0.0
    morph_p_gerund                  0.069           0.037   0.026    0.035    1.533        0.742  0.871     0.0
    morph_polarity_Neg              0.019           0.028  -0.011   -0.009   -1.122       -0.559  0.221     0.0
    sents_mean                     16.393          11.494   3.078    6.688    0.833        0.610  0.805     0.0
    punct_dash                     19.000          46.000 -39.012  -14.000   -1.287       -0.605  0.197     0.0
    punct_exclamation               9.000          24.000 -22.000   -2.975   -1.251       -0.637  0.181     0.0
    diversity_yule_k              103.620         112.500 -17.620   -3.740   -0.676       -0.351  0.324     0.0

    {'n_Galdós': 155, 'n_Unamuno': 117, 'n_texts_Galdós': 3, 'n_texts_Unamuno': 3}
    ```

Galdós tiene el vocabulario más rico: las medidas basadas en el número de palabras distintas - el TTR y sus transformaciones, MATTR, MTLD, los hápax - distinguen a los autores con una delta cercana a 0.9 o mayor, mientras que la K de Yule, que pondera las palabras frecuentes, da un efecto mediano (0.35), así que la diferencia está sobre todo en el vocabulario raro. Sus palabras y oraciones son más largas, con casi el doble de gerundios entre las formas verbales. Unamuno escribe en diálogo: dos veces y media más rayas y signos de exclamación por cada 1000 palabras, y más negaciones.

Los valores p toman las 272 ventanas de seis novelas por independientes (véase el [aviso](#statistics) de abajo), y según la misma prueba dos novelas de Galdós, *Marianela* y *Misericordia*, difieren en 42 rasgos. El intervalo de la diferencia de las medianas remuestrea novelas enteras y es la guía más segura: para la longitud de una oración va de 3.1 a 6.7 palabras, donde las ventanas solas darían de 3.9 a 6.0.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `a` | `list[str]` | - | Textos del primer corpus |
| `b` | `list[str]` | - | Textos del segundo corpus |
| `window` | `int` | `1000` | Tamaño de una ventana en palabras; `None` - los textos enteros |
| `features` | `Callable` | `None` | Función de los rasgos de un texto; `None` - `text_features` |
| `min_words` | `int` | `None` | Menor número de palabras de una ventana, como mucho `window`; `None` - una ventana entera, o una palabra cuando `window` es `None` |

`labels`, `n_bootstrap` y `seed` pasan a [`compare_features`](#compare_features). `compare_corpora` los comprueba antes con `check_comparison_params`, así que un nombre de corpus o una semilla erróneos fallan antes de analizar ningún texto.

Excepciones:

- `SourceTypeError` - unos textos que no son una lista de cadenas, unos `features` que no se pueden llamar;
- `SourceError` - un corpus sin una ventana de `min_words` palabras o más, un texto con un carácter sin forma UTF-8;
- `ParameterError` - un `window` o un `min_words` que no es un entero de al menos uno, un `min_words` mayor que `window`, unas etiquetas, un número de remuestras o una semilla que rechaza `check_comparison_params`;
- `DatasetNotFoundError` - los rasgos por defecto sin el modelo instalado.

## Rasgos { #text_features }

``` {.python .signature}
text_features(text, nlp=None)
```

Devuelve 132 rasgos de un texto con un prefijo según su fuente; un rasgo indefinido es `nan`.

| Prefijo | Rasgos | Fuente |
| :------ | :----- | :----- |
| `basic_` | proporciones de palabras largas, complejas, simples, monosílabas y polisílabas, de letras, espacios y signos de puntuación; letras y sílabas por palabra | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | todas las fórmulas de legibilidad y el grado de consenso | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | todas las medidas de diversidad léxica | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | proporciones de los valores de cada rasgo morfológico (`morph_pos_NOUN`, `morph_mood_Sub`, `morph_polarity_Neg`) y los marcadores del español (`morph_p_gerund`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) con el modelo de spaCy |
| `sents_` | longitud media de una oración en palabras, desviación típica, coeficiente de variación, autocorrelación de las longitudes vecinas ([`sentence_rhythm`](#sentence_rhythm)): el ritmo del texto | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frecuencias de los signos de puntuación por tipo por cada 1000 palabras y la proporción de los signos de apertura | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

Se dejan fuera el tiempo de lectura, que solo sigue el número de palabras de una ventana, y los rasgos que repiten otros: la proporción de palabras únicas de `BasicStats`, que repite `diversity_ttr`, sus palabras por oración, que repiten `sents_mean`, y los marcadores de los modos de `get_markers`, que repiten `morph_mood_*`.

Las categorías gramaticales y los rasgos de un solo valor - polaridad, cortesía, posesivo, reflexivo - son proporciones de todas las palabras (`morph_polarity_Neg` es la proporción de las negaciones), los demás rasgos, proporciones de las palabras que los llevan (`morph_mood_Sub` es el subjuntivo entre los modos). Un valor que no aparece en una ventana da 0; un rasgo ausente de la ventana por completo (sin verbos no hay tiempo) da `nan`. Un valor de varios valores (`PronType=Int,Rel` de *que*) se reparte a partes iguales entre sus partes, así que las proporciones de un rasgo siguen sumando uno.

La morfología la analiza el modelo [`es_core_news_sm`](../installation.md#model) sin su analizador sintáctico, así que el marcador `morph_p_ser`, que lee las cópulas de las dependencias, se deja fuera; un pipeline pasado en `nlp` se ejecuta entero salvo el reconocedor de entidades, así que `functools.partial(text_features, nlp=get_nlp())` recupera el analizador sintáctico y `morph_p_ser`, y otro modelo entra en la comparación del mismo modo. Una novela se compara por ventanas y no entera, ya que el pipeline admite como mucho `max_length` caracteres.

Las proporciones de espacios, letras y signos de puntuación (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) cuentan los caracteres tal cual: las sangrías, los espacios dobles y los de no separación de los archivos reflejan la composición de una edición y no el texto. En un corpus de fuentes distintas conviene colapsarlos antes, por ejemplo, con `re.sub(r"[^\S\n]+", " ", text)`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Cadena de texto |
| `nlp` | `Language` | `None` | Pipeline para la morfología; `None` - el modelo por defecto sin su analizador sintáctico |

Excepciones:

- `SourceTypeError` - un texto que no es una cadena, un pipeline que no es un `Language` de spaCy;
- `SourceError` - un texto sin palabras, con un carácter sin forma UTF-8 o más largo que el `max_length` del pipeline;
- `DatasetNotFoundError` - el modelo por defecto no está instalado.

``` {.python .signature}
corpus_features(texts, window=1000, features=text_features, min_words=None)
```

Devuelve la matriz de rasgos de las ventanas con el índice (número del texto, número de la ventana), también para clasificadores propios; el nivel `text` del índice es el que remuestrea el bootstrap de `compare_features`. Los textos sin palabras y las ventanas más cortas que `min_words` se omiten. `compare_corpora` es `corpus_features` para cada corpus seguido de `compare_features`, y la división permite calcular una vez los rasgos de varios corpus y compararlos por pares.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `texts` | `list[str]` | - | Textos del corpus |
| `window` | `int` | `1000` | Tamaño de una ventana en palabras; `None` - los textos enteros |
| `features` | `Callable` | `text_features` | Función de los rasgos de un texto |
| `min_words` | `int` | `None` | Menor número de palabras de una ventana, como mucho `window`; `None` - una ventana entera, o una palabra cuando `window` es `None` |

Excepciones:

- `SourceTypeError` - unos textos que no son una lista de cadenas, unos `features` que no se pueden llamar;
- `SourceError` - un corpus sin una ventana de `min_words` palabras o más, un texto con un carácter sin forma UTF-8;
- `ParameterError` - un `window` o un `min_words` que no es un entero de al menos uno, un `min_words` mayor que `window`;
- `DatasetNotFoundError` - los rasgos por defecto sin el modelo instalado.

Los rasgos propios, por ejemplo los sintácticos, se pasan como una función:

=== "Código"

    ``` python
    from ests import SyntaxStats
    from ests.corpus import compare_corpora, text_features
    from ests.utils import get_nlp

    nlp = get_nlp()


    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}


    result = compare_corpora(
        galdos, unamuno, window=1000, features=features, labels=("Galdós", "Unamuno")
    )
    result.filter(like="syntax_", axis=0)[columns].head(5).round(3)
    ```

=== "Resultado"

    ```
                                        median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    syntax_gerund_clauses_per_sent              0.156           0.047   0.091    0.131    1.493        0.854  0.927     0.0
    syntax_tree_depth                           3.870           3.012   0.625    1.134    1.113        0.661  0.830     0.0
    syntax_subtrees_per_sent                    7.193           4.864   1.500    3.352    0.975        0.648  0.824     0.0
    syntax_p_complex_sents                      0.632           0.494   0.093    0.187    1.248        0.637  0.819     0.0
    syntax_participle_clauses_per_sent          0.114           0.059   0.028    0.070    0.805        0.570  0.785     0.0
    ```

## Comparación de tablas de rasgos { #compare_features }

<!-- core: corpus/compare.md:compare_features 96478f4 -->
``` {.python .signature}
compare_features(table_a, table_b, labels=('A', 'B'), n_bootstrap=1000, seed=0)
```

Compara dos corpus rasgo por rasgo. Cada corpus es una tabla de los rasgos de sus ventanas, partes de los textos de un tamaño parecido, así que los rasgos no dependen de la longitud de los textos. El resultado tiene una fila por columna, por el valor absoluto descendente de la delta de Cliff, con los rasgos sin estadísticas al final. El bootstrap remuestrea textos enteros según el nivel `text` del índice; sin él cada fila es un texto aparte. Una columna que falta en una de las tablas da `nan`.

<!-- core: corpus/compare.md:compare_features-parameters 2ed21c1 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `table_a` | `DataFrame` | - | Rasgos de las ventanas del primer corpus, una fila por ventana |
| `table_b` | `DataFrame` | - | Rasgos de las ventanas del segundo corpus |
| `labels` | `tuple[str, str]` | `('A', 'B')` | Nombres de los corpus para las columnas, dos cadenas que den columnas distintas |
| `n_bootstrap` | `int` | `1000` | Número de remuestras bootstrap |
| `seed` | `int` / `Generator` | `0` | Semilla del generador de números aleatorios, un entero no negativo, o un `Generator` de numpy; `None` - una aleatoria |

Una tabla que no es un `DataFrame`, que repite el nombre de una columna o que tiene una columna no numérica lanza `SourceTypeError`; los demás parámetros los comprueba `check_comparison_params`.

<!-- core: corpus/compare.md:check_comparison_params a56a706 -->
``` {.python .signature}
check_comparison_params(labels=('A', 'B'), n_bootstrap=1000, seed=0)
```

Comprueba los parámetros de `compare_features` antes de procesar los textos: lanza `ParameterError` salvo que las etiquetas sean dos cadenas que den columnas distintas (`("diff", "B")` repetiría `median_diff`), el número de remuestras bootstrap sea un entero de al menos uno y la semilla sea `None`, un entero no negativo o un `Generator` de numpy.

## Estadísticas { #statistics }

<!-- core: corpus/compare.md:compare_features-statistics 99869be -->
Para un rasgo con los valores $x_1 \dots x_{n_A}$ en el corpus A y $y_1 \dots y_{n_B}$ en el corpus B (sin los valores indefinidos e infinitos; con menos de dos valores en un lado, `nan`):

| Columna | Descripción |
| :------ | :---------- |
| `mean_A`, `mean_B`, `median_A`, `median_B` | medias y medianas |
| `median_diff`, `ci_low`, `ci_high` | la diferencia de las medianas y su intervalo bootstrap de percentiles al 95%: ambos conjuntos se remuestrean `n_bootstrap` veces (`bootstrap_median_diff`) |
| `cohen_d` | $d = (\bar{x} - \bar{y}) / s$, $s$ - la desviación típica combinada; 0.2 - un efecto pequeño, 0.5 - mediano, 0.8 - grande (`calc_cohen_d`) |
| `cliff_delta` | $\delta = P(x > y) - P(x < y)$ de −1 a 1; $\lvert\delta\rvert$ < 0.147 - un efecto despreciable, < 0.33 - pequeño, < 0.474 - mediano, grande en otro caso (Romano et al. 2006; `calc_cliff_delta`) |
| `auc` | el rasgo como clasificador: la proporción de pares de ventanas con el valor en A mayor que en B, con los empates a la mitad; $\delta = 2 \cdot AUC - 1$, 0.5 - el rasgo no distingue los corpus |
| `u`, `p_value` | el estadístico U de Mann-Whitney y el valor p bilateral (`scipy.stats.mannwhitneyu`) |
| `p_holm` | el valor p con la corrección de Holm por el número de rasgos (`holm_correction`) |
| `n_A`, `n_B` | número de ventanas con un valor definido |
| `n_texts_A`, `n_texts_B` | número de textos detrás de esas ventanas |

Las columnas son `anyts.corpus.COMPARISON_COLUMNS` con los sufijos `a` y `b` sustituidos por las etiquetas de los corpus. La delta de Cliff y el AUC salen del mismo estadístico U y concuerdan; la d de Cohen es sensible a los valores atípicos y a la falta de normalidad, así que conviene leerla junto a la delta.

!!! warning "Las ventanas de un texto no son independientes"
    La prueba y los tamaños del efecto toman las ventanas por observaciones independientes, cosa que las ventanas de un texto no son: con pocos textos los valores p salen demasiado pequeños y reflejan los textos elegidos tanto como los corpus. El bootstrap remuestrea textos enteros (un bootstrap por conglomerados), así que su intervalo abarca la dispersión entre los textos; necesita al menos dos textos en cada lado y es aproximado con pocos.

## Funciones de las estadísticas

Las estadísticas de una fila están disponibles una a una desde `ests.corpus`:

<!-- core: corpus/compare.md:calc_cohen_d 198b504 -->
``` {.python .signature}
calc_cohen_d(values_a, values_b)
```

La d de Cohen con las varianzas muestrales combinadas (ddof=1); `nan` con menos de dos valores en un lado o sin dispersión.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `values_a` | `list[float]` | - | Valores en el primer corpus |
| `values_b` | `list[float]` | - | Valores en el segundo corpus |

Un valor que no es un número o que falta (`None`, `NA`) y unos valores que no son una lista plana lanzan `SourceTypeError`.

<!-- core: corpus/compare.md:calc_cliff_delta ccd5938 -->
``` {.python .signature}
calc_cliff_delta(values_a, values_b)
```

La delta de Cliff, la proporción de pares en que el primer valor es mayor menos la proporción en que es menor; `nan` para un conjunto vacío o un valor indefinido. Se calcula por ordenación, en tiempo $O((n_A + n_B) \log n_B)$ y memoria lineal.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `values_a` | `list[float]` | - | Valores en el primer corpus |
| `values_b` | `list[float]` | - | Valores en el segundo corpus |

Un valor que no es un número o que falta (`None`, `NA`) y unos valores que no son una lista plana lanzan `SourceTypeError`.

<!-- core: corpus/compare.md:bootstrap_median_diff b20d95f -->
``` {.python .signature}
bootstrap_median_diff(values_a, values_b, n_bootstrap=1000, rng=None, confidence=0.95, texts_a=None, texts_b=None)
```

El intervalo bootstrap de percentiles de la diferencia de las medianas. Con `texts_a` y `texts_b` se remuestrean textos enteros, y la mediana de una extracción se toma sobre los valores de sus textos; con menos de dos textos en un lado el intervalo es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `values_a` | `list[float]` | - | Valores en el primer corpus |
| `values_b` | `list[float]` | - | Valores en el segundo corpus |
| `n_bootstrap` | `int` | `1000` | Número de remuestras bootstrap |
| `rng` | `Generator` | `None` | Generador de números aleatorios de numpy; `None` - uno nuevo sin semilla |
| `confidence` | `float` | `0.95` | Nivel de confianza |
| `texts_a` | `list` | `None` | Textos de los valores en el primer corpus; `None` - cada valor se remuestrea por separado |
| `texts_b` | `list` | `None` | Textos de los valores en el segundo corpus |

Un valor que no es un número o que falta, unos valores que no son una lista plana y unos textos que no son etiquetas de un mismo tipo lanzan `SourceTypeError`; un `n_bootstrap` que no es un entero de al menos uno, un `confidence` que no es un número en (0, 1), unos textos que no son tantos como los valores y un `rng` que no es un `Generator` de numpy lanzan `ParameterError`.

<!-- core: corpus/compare.md:holm_correction 7006482 -->
``` {.python .signature}
holm_correction(p_values)
```

La corrección de Holm para comparaciones múltiples: los valores p se ordenan de menor a mayor, el i-ésimo se multiplica por (m − i + 1), donde m es el número de valores definidos, luego se toma el máximo acumulado y se limita a uno; `nan` sigue siendo `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `p_values` | `list[float]` | - | Valores p |

Un valor p que no es un número o que falta y unos valores p que no son una lista plana lanzan `SourceTypeError`, y un valor p fuera de [0, 1], `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import calc_cliff_delta, calc_cohen_d, holm_correction

    round(calc_cohen_d([2, 4, 6, 8], [1, 3, 5, 7]), 3)
    calc_cliff_delta([2, 4, 6, 8], [1, 3, 5, 7])
    holm_correction([0.01, 0.04, 0.03]).round(3).tolist()
    ```

=== "Resultado"

    ```
    0.387
    0.25
    [0.03, 0.06, 0.06]
    ```

## Ventanas de un texto { #split_windows }

``` {.python .signature}
split_windows(text, window=1000, min_words=None)
```

Corta un texto en ventanas consecutivas de exactamente `window` palabras, así que los rasgos que dependen de la longitud son comparables entre textos. El resto es una ventana solo con al menos `min_words` palabras (por defecto una ventana entera, así que se descarta). Un límite pasa antes de la primera palabra de una ventana y de sus signos de apertura; unas comillas rectas o una raya pegadas a la última palabra de la ventana anterior o tras un signo de cierre se quedan con ella (`"cuatro"`, `—dijo Juan—`, `"adiós."`). A las ventanas se les quitan los espacios de los extremos; `window=None` da el texto entero. Es el `split_windows` del núcleo con las palabras de [`WordsExtractor`](../extractors/words.md) y los signos de `ests.constants`: las comillas, los paréntesis, las rayas, `¿` y `¡` abren una frase (`OPENING_MARKS`), las comillas rectas y las rayas son simétricas (`SYMMETRIC_MARKS`); los signos que cierran una frase son los del núcleo.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Cadena de texto |
| `window` | `int` | `1000` | Tamaño de una ventana en palabras; `None` - el texto entero |
| `min_words` | `int` | `None` | Menor número de palabras de una ventana; `None` - una ventana entera, o una palabra cuando `window` es `None` |

Un texto sin palabras o más corto que `min_words` da una lista vacía.

Excepciones:

- `SourceTypeError` - un texto que no es una cadena;
- `SourceError` - un carácter sin forma UTF-8;
- `ParameterError` - un `window` o un `min_words` que no es un entero de al menos uno, un `min_words` mayor que la ventana.

=== "Código"

    ``` python
    from ests.corpus import split_windows

    split_windows("Uno dos tres cuatro cinco", 2, min_words=1)
    split_windows("El gato duerme mucho. ¿Dónde está el perro?", 4)
    split_windows('Dijo "adiós" y se fue ya', 2)
    ```

=== "Resultado"

    ```
    ['Uno dos', 'tres cuatro', 'cinco']
    ['El gato duerme mucho.', '¿Dónde está el perro?']
    ['Dijo "adiós"', 'y se', 'fue ya']
    ```

## Ritmo de las oraciones { #sentence_rhythm }

``` {.python .signature}
sentence_rhythm(lengths, *, messages=MESSAGES)
```

<!-- core: corpus/compare.md:sentence_rhythm 9e57614 -->
Da el ritmo de las oraciones a partir de sus longitudes en palabras: la media `sents_mean`, la desviación típica `sents_std`, el coeficiente de variación `sents_cv` y la autocorrelación de retardo 1 de las longitudes vecinas `sents_autocorr` (Yule, 1939). La desviación necesita dos oraciones, la autocorrelación tres de longitudes desiguales y el coeficiente de variación una media mayor que cero; si no, y sin oraciones, un rasgo es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `lengths` | `list[int]` | - | Longitudes de las oraciones en palabras |
| `messages` | `dict[str, str]` | `MESSAGES` | Mensajes de los errores por clave |

Unas longitudes que no son una lista de enteros lanzan `SourceTypeError`, y una longitud negativa, `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import sentence_rhythm

    {key: round(value, 3) for key, value in sentence_rhythm([4, 8, 2, 7]).items()}
    ```

=== "Resultado"

    ```
    {'sents_mean': 5.25, 'sents_std': 2.754, 'sents_cv': 0.525, 'sents_autocorr': -0.794}
    ```
