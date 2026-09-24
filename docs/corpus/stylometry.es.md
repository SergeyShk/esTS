# Estilometría

!!! info ""
    **ests.corpus.delta()**, **ests.corpus.delta_profiles()**, **ests.corpus.frequency_table()**, **ests.corpus.z_scores()**, **ests.corpus.zeta()**, **ests.corpus.kilgarriff_chi2()**, **ests.corpus.mendenhall_curve()**, **ests.corpus.mendenhall_distance()**, **ests.corpus.function_words_profile()**

## Descripción

Medidas de estilometría y de atribución de autoría: distancias entre textos por las frecuencias de las palabras más frecuentes (la Delta de Burrows y sus variantes, como en [stylo](https://github.com/computationalstylistics/stylo)), marcadores de palabras preferidas y evitadas (Zeta), la distancia ji cuadrado de Kilgarriff entre corpus, la curva de Mendenhall y el perfil de las palabras funcionales como rasgos de un autor. Las funciones trabajan con listas de unidades de un texto: formas de palabra en minúsculas (la elección habitual para Delta), lemas o N-gramas de caracteres ([`CharNgramsExtractor`](../extractors/char_ngrams.md)); la caja y la lematización corresponden a [`WordsExtractor`](../extractors/words.md).

## Delta de Burrows { #delta }

Un corpus es un diccionario «nombre de un texto → unidades». `frequency_table` construye la tabla de frecuencias relativas: las filas son los textos, las columnas las `n_mfw` unidades más frecuentes por frecuencia relativa media descendente (alfabéticamente si empatan); `culling` conserva las unidades que aparecen al menos en la proporción de textos dada, como en stylo. `z_scores` estandariza las columnas con la desviación típica muestral, como `scale()` de R; una columna con la misma frecuencia en todos los textos da ceros. `delta` calcula a partir de las puntuaciones z una matriz simétrica de distancias (un `DataFrame` con los nombres de los textos), apta para el agrupamiento y el PCA; hacen falta al menos tres textos: con dos, las puntuaciones z degeneran en ±1/√2 y las distancias no dependen de las frecuencias.

Variantes (`DELTA_VARIANTS`), con las fórmulas de las fuentes de stylo; $n$ es el número de unidades, $z_A$ y $z_B$ los vectores de puntuaciones z de los textos:

| Variante | Clave | Fórmula | Fuente |
| :------- | :---- | :------ | :----- |
| Delta de Burrows | `burrows` | $\frac{1}{n} \sum_i \lvert z_{A,i} - z_{B,i} \rvert$ | Burrows (2002), `dist.delta` |
| Delta cuadrática | `quadratic` | $\frac{1}{n} \sqrt{\sum_i (z_{A,i} - z_{B,i})^2}$ | Argamon (2008), `dist.argamon` |
| Delta de Eder | `eder` | $\sum_i \frac{n - i + 2}{n} \lvert z_{A,i} - z_{B,i} \rvert$, $i$ - rango de la unidad por frecuencia | Eder, `dist.eder` |
| Delta coseno | `cosine` | $1 - \frac{z_A \cdot z_B}{\lVert z_A \rVert \lVert z_B \rVert}$ | Smith y Aldridge (2011), [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf), `dist.wurzburg` |

La Delta coseno es la que mejor agrupa los textos por autor en los experimentos de Evert et al.; la Delta de Burrows es la elección clásica. El número habitual de unidades es de 100 a 500 palabras más frecuentes, de 100 a 200 para los N-gramas de caracteres.

Parámetros de `delta`:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Unidades de los textos por los nombres de los textos |
| `n_mfw` | int | `100` | Número de las unidades más frecuentes; `None` - todas |
| `variant` | str | `burrows` | Variante de Delta de `DELTA_VARIANTS` |
| `culling` | float | `0.0` | Menor proporción de textos en la que aparece una unidad |

`frequency_table(corpus, n_mfw=100, culling=0.0)` recibe los mismos parámetros, `z_scores(table)` la tabla.

Para la atribución de autoría está `delta_profiles(reference, samples, n_mfw, variant, culling, statistics)`: las unidades más frecuentes, el filtrado y las estadísticas de las puntuaciones z se toman de los textos de referencia `reference` (los perfiles de los autores) o de un conjunto aparte `statistics` - por ejemplo, de las ventanas de entrenamiento, cuando los perfiles se unen a partir de ellas y son demasiado pocos para estimar la dispersión de las frecuencias; los textos a examinar `samples` se describen con las mismas unidades y se escalan con las mismas estadísticas. El resultado son las distancias de los textos examinados a los de referencia, y la referencia más cercana de una fila es el autor presunto. A diferencia de `delta` sobre un vocabulario común, los textos examinados no influyen ni en la lista de unidades ni en el escalado, así que el resultado para un texto no depende de los textos que se pasan con él.

!!! example "Ejemplo"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import delta, delta_profiles, frequency_table

    texts = {
        "A": (
            "El gato estaba en la ventana y miraba los pájaros. "
            "Los pájaros se fueron y el gato durmió en la ventana."
        ),
        "B": "El perro estaba en el suelo y dormía. Después el perro comió y otra vez dormía en el suelo.",
        "C": "Mañana el gato volverá a la ventana y mirará los pájaros, pero el perro dormirá.",
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(text) for name, text in texts.items()}

    frequency_table(corpus, n_mfw=5).round(3)
    #       el      y     en  perro   gato
    # A  0.095  0.095  0.095  0.000  0.095
    # B  0.211  0.105  0.105  0.105  0.000
    # C  0.133  0.067  0.000  0.067  0.067

    delta(corpus, n_mfw=5).round(3)
    #        A      B      C
    # A  0.000  1.312  1.110
    # B  1.312  0.000  1.428
    # C  1.110  1.428  0.000

    delta(corpus, n_mfw=5, variant="cosine").round(3)
    #        A      B      C
    # A  0.000  1.637  1.241
    # B  1.637  0.000  1.594
    # C  1.241  1.594  0.000

    sample = {"?": we.extract("El gato despertó en la ventana y otra vez miraba los pájaros.")}
    delta_profiles(corpus, sample, n_mfw=5).round(3)
    #        A      B      C
    # ?  0.249  1.464  0.942
    ```

## Zeta { #zeta }

Marcadores de palabras preferidas y evitadas según Burrows (2007) y Craig y Kinney (2009). Cada texto de ambos corpus se divide en segmentos de unas `segment_size` palabras (el número de segmentos es la razón de la longitud al tamaño redondeada al entero más próximo, al menos uno), y para una palabra se calcula la proporción de segmentos de cada corpus en los que aparece ($DP$). Zeta es la diferencia de las proporciones $DP_{target} - DP_{comparison}$, de −1 a 1 (`zeta.craig` en la notación de stylo; la Zeta clásica de Craig $DP_{target} + (1 - DP_{comparison})$ es mayor en uno), la Zeta logarítmica es $\log_2 \frac{DP_{target}}{DP_{comparison}}$ ([Schöch et al. 2018](https://zeta-project.eu/en/keyness-measures/burrows-zeta-logarithmic-zeta/)), con una proporción nula sustituida por medio segmento. La lista empieza por las palabras que prefiere el corpus objetivo y termina por las evitadas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `target` | list[str]/list[list[str]] | `-` | Palabras del corpus objetivo: un texto o una lista de textos |
| `comparison` | list[str]/list[list[str]] | `-` | Palabras del corpus de comparación |
| `segment_size` | int | `2000` | Tamaño de un segmento en palabras |
| `top_n` | int | `None` | Número de palabras desde el principio de la lista; `None` - todas |

El resultado es una lista de tuplas con nombre `ZetaScore(word, dp_target, dp_comparison, zeta, log_zeta)` por Zeta descendente, por Zeta logarítmica descendente y alfabéticamente si empatan.

!!! example "Ejemplo"

    ``` python
    from ests.corpus import zeta

    zeta(corpus["A"], corpus["B"], segment_size=5, top_n=2)
    # [ZetaScore(word='gato', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0),
    #  ZetaScore(word='la', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0)]

    zeta(corpus["A"], corpus["B"], segment_size=5)[-1]
    # ZetaScore(word='suelo', dp_target=0.0, dp_comparison=0.5, zeta=-0.5, log_zeta=-2.0)
    ```

## Ji cuadrado de Kilgarriff { #kilgarriff_chi2 }

La distancia entre dos corpus según [Kilgarriff (2001)](https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf): para las `n_mfw` palabras más frecuentes del corpus conjunto las frecuencias esperadas en los corpus son proporcionales a sus tamaños, $\chi^2 = \sum (O - E)^2 / E$ sobre las palabras y ambos corpus. Cuanto mayor es el valor, más difieren los corpus; el valor crece con el tamaño de los corpus, así que los pares de corpus son comparables entre sí con tamaños iguales, como en los experimentos de Kilgarriff.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `words_a` | list[str] | `-` | Palabras del primer corpus |
| `words_b` | list[str] | `-` | Palabras del segundo corpus |
| `n_mfw` | int | `500` | Número de las palabras más frecuentes del corpus conjunto |

!!! example "Ejemplo"

    ``` python
    from ests.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["A"], corpus["B"], n_mfw=5), 3)
    # 3.119
    ```

## Curva de Mendenhall { #mendenhall }

`mendenhall_curve(words)` - las proporciones de las palabras de cada longitud en caracteres (Mendenhall 1887), un perfil del autor comparable entre textos sea cual sea su tamaño; `mendenhall_distance(words_a, words_b)` - la distancia de Jensen-Shannon con base 2 entre las curvas, de 0 (las distribuciones coinciden) a 1.

!!! example "Ejemplo"

    ``` python
    from ests.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["A"]).items()}
    # {1: 0.095, 2: 0.333, 3: 0.095, 4: 0.095, 6: 0.19, 7: 0.19}

    round(mendenhall_distance(corpus["A"], corpus["B"]), 3)
    # 0.415
    ```

## Perfil de las palabras funcionales { #function_words_profile }

Las proporciones de las adposiciones, las conjunciones coordinantes y subordinantes, las partículas, los pronombres, los determinantes y las interjecciones (`FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) entre las palabras del texto. Las palabras funcionales no dependen del tema, así que su perfil es un rasgo clásico de autoría desde Mosteller y Wallace (1964).

Las categorías gramaticales son las de la anotación de un `Doc` que las lleva. Las palabras de una lista o de un `Doc` sin categorías gramaticales las etiqueta el modelo como una sola secuencia, en su contexto, así que han de pasarse en el orden del texto; la puntuación de la lista ayuda al etiquetado y no se cuenta. El pipeline es el modelo [`es_core_news_sm`](../installation.md#model) o el que se pasa en `nlp`, sin el analizador sintáctico, el lematizador ni el reconocedor de entidades, que las categorías gramaticales no necesitan; un pipeline que no las etiqueta (`spacy.blank("es")`) lanza `SourceError`. En las Universal Dependencies del español la negación *no* es un adverbio y no una partícula, así que `PART` es rara.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | list[str]/Doc | `-` | Palabras del texto u objeto Doc |
| `nlp` | Language | `None` | Pipeline para una lista de palabras; `None` - el modelo por defecto |

!!! example "Ejemplo"

    ``` python
    from ests.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["A"]).items()}
    # {'ADP': 0.095, 'CCONJ': 0.095, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.048, 'DET': 0.286, 'INTJ': 0.0}
    ```
