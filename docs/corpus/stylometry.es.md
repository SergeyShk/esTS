# Estilometría

<!-- core: corpus/stylometry.md:stylometry e6b2525 -->
Medidas de estilometría y de atribución de autoría: distancias entre textos por las frecuencias de las palabras más frecuentes (la Delta de Burrows y sus variantes, como en [stylo](https://github.com/computationalstylistics/stylo)) y a lo largo de un texto por sus ventanas (la Delta móvil), marcadores de palabras preferidas y evitadas (Zeta) y sus proporciones en los segmentos de los corpus, la distancia ji cuadrado de Kilgarriff entre corpus y la curva de Mendenhall. Las funciones trabajan con listas de unidades de un texto: formas de palabra en minúsculas (la elección habitual para Delta), lemas o N-gramas de caracteres; las mayúsculas y minúsculas y la lematización corresponden a los extractores.

Las funciones son las del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/stylometry/), con el [perfil de las palabras funcionales](#function_words_profile) del español añadido como rasgo de un autor. Las unidades de un texto las dan [`WordsExtractor`](../extractors/words.md) - formas de palabra y lemas - y [`CharNgramsExtractor`](../extractors/char_ngrams.md).

## Delta de Burrows { #delta }

<!-- core: corpus/stylometry.md:frequency_table 1b6144d -->
``` {.python .signature}
frequency_table(corpus, n_mfw=100, culling=0.0)
```

Construye la tabla de frecuencias relativas de un corpus, un diccionario «nombre de un texto → unidades»: las filas son los textos, las columnas las `n_mfw` unidades más frecuentes por frecuencia relativa media descendente (alfabéticamente si empatan); `culling` conserva las unidades que aparecen al menos en la proporción de textos dada, como en stylo.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `corpus` | `dict[str, list[str]]` | - | Unidades de los textos por los nombres de los textos |
| `n_mfw` | `int` | `100` | Número de las unidades más frecuentes; `None` - todas |
| `culling` | `float` | `0.0` | Menor proporción de textos en la que aparece una unidad |

Un corpus que no es un mapeo de listas de cadenas lanza `SourceTypeError`; un corpus vacío, un texto sin unidades y un filtrado que no deja ninguna unidad lanzan `SourceError`, y un `n_mfw` que no es un entero de al menos uno y un `culling` que no es un número dentro de [0, 1], `ParameterError`.

<!-- core: corpus/stylometry.md:z_scores d9b43d3 -->
``` {.python .signature}
z_scores(table)
```

Estandariza las columnas de una tabla de frecuencias con la desviación típica muestral, como `scale()` de R; una columna con la misma frecuencia en todos los textos da ceros.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `table` | `DataFrame` | - | Tabla de frecuencias relativas |

<!-- core: corpus/stylometry.md:delta 07de161 -->
``` {.python .signature}
delta(corpus, n_mfw=100, variant='burrows', culling=0.0)
```

Calcula a partir de las puntuaciones z una matriz simétrica de distancias (un `DataFrame` con los nombres de los textos); hacen falta al menos tres textos: con dos, las puntuaciones z degeneran en ±1/√2 y las distancias no dependen de las frecuencias.

Las variantes (`anyts.constants.DELTA_VARIANTS`), con las fórmulas de las fuentes de stylo; $n$ es el número de unidades, $z_A$ y $z_B$ los vectores de puntuaciones z de los textos:

| Variante | Clave | Fórmula | Fuente |
| :------- | :---- | :------ | :----- |
| Delta de Burrows | `burrows` | $\frac{1}{n} \sum_i \lvert z_{A,i} - z_{B,i} \rvert$ | Burrows (2002), `dist.delta` |
| Delta cuadrática | `quadratic` | $\frac{1}{n} \sqrt{\sum_i (z_{A,i} - z_{B,i})^2}$ | Argamon (2008), `dist.argamon` |
| Delta de Eder | `eder` | $\sum_i \frac{n - i + 2}{n} \lvert z_{A,i} - z_{B,i} \rvert$, $i$ - rango de la unidad por frecuencia | Eder, `dist.eder` |
| Delta coseno | `cosine` | $1 - \frac{z_A \cdot z_B}{\lVert z_A \rVert \lVert z_B \rVert}$ | Smith y Aldridge (2011), [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf), `dist.wurzburg` |

La Delta coseno es la que mejor agrupa los textos por autor en los experimentos de Evert et al. El número habitual de unidades es de 100 a 500 palabras más frecuentes, de 100 a 200 para los N-gramas de caracteres.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `corpus` | `dict[str, list[str]]` | - | Unidades de los textos por los nombres de los textos |
| `n_mfw` | `int` | `100` | Número de las unidades más frecuentes; `None` - todas |
| `variant` | `str` | `'burrows'` | Variante de Delta de `anyts.constants.DELTA_VARIANTS` |
| `culling` | `float` | `0.0` | Menor proporción de textos en la que aparece una unidad |

El corpus, `n_mfw` y `culling` lanzan los errores de `frequency_table`; menos de tres textos lanzan `SourceError`, y una variante desconocida, `ParameterError`.

<!-- core: corpus/stylometry.md:delta_profiles 1c5b7e6 -->
``` {.python .signature}
delta_profiles(reference, samples, n_mfw=100, variant='burrows', culling=0.0, statistics=None)
```

Distancias de Delta para la atribución de autoría. Las unidades más frecuentes, el filtrado y las estadísticas de las puntuaciones z se toman de los textos de referencia (los perfiles de los autores) o de un conjunto aparte `statistics`, como las ventanas de entrenamiento cuando los perfiles son demasiado pocos para estimar la dispersión de las frecuencias; los textos a examinar `samples` reciben las mismas unidades y el mismo escalado. El resultado son las distancias de los textos examinados (filas) a los de referencia (columnas); la referencia más cercana es el autor presunto. A diferencia de `delta`, un texto examinado no influye ni en las unidades ni en el escalado, así que su resultado no depende de los demás textos examinados.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `reference` | `dict[str, list[str]]` | - | Unidades de los textos de referencia por los nombres de los textos |
| `samples` | `dict[str, list[str]]` | - | Unidades de los textos a examinar por los nombres de los textos |
| `n_mfw` | `int` | `100` | Número de las unidades más frecuentes; `None` - todas |
| `variant` | `str` | `'burrows'` | Variante de Delta de `anyts.constants.DELTA_VARIANTS` |
| `culling` | `float` | `0.0` | Menor proporción de textos en la que aparece una unidad |
| `statistics` | `dict[str, list[str]]` | `None` | Textos de las unidades y de las estadísticas del escalado; `None` - los textos de referencia |

Los corpus, `n_mfw` y `culling` lanzan los errores de `frequency_table`; menos de tres textos para las estadísticas lanzan `SourceError`, y una variante desconocida, `ParameterError`.

=== "Código"

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
    delta(corpus, n_mfw=5).round(3)
    delta(corpus, n_mfw=5, variant="cosine").round(3)

    sample = {"?": we.extract("El gato despertó en la ventana y otra vez miraba los pájaros.")}
    delta_profiles(corpus, sample, n_mfw=5).round(3)
    ```

=== "Resultado"

    ```
          el      y     en  perro   gato
    A  0.095  0.095  0.095  0.000  0.095
    B  0.211  0.105  0.105  0.105  0.000
    C  0.133  0.067  0.000  0.067  0.067

           A      B      C
    A  0.000  1.312  1.110
    B  1.312  0.000  1.428
    C  1.110  1.428  0.000

           A      B      C
    A  0.000  1.637  1.241
    B  1.637  0.000  1.594
    C  1.241  1.594  0.000

           A      B      C
    ?  0.249  1.464  0.942
    ```

## Delta móvil { #rolling_delta }

<!-- core: corpus/stylometry.md:rolling_delta c80e9bf -->
``` {.python .signature}
rolling_delta(reference, text, window=5000, step=1000, n_mfw=100, variant='burrows', culling=0.0, statistics=None)
```

La Delta a lo largo de un texto, a la manera de `rolling.delta` de stylo: los textos de referencia y el texto a examinar se cortan en ventanas de `window` unidades cada `step` unidades, y el resto más corto que una ventana se descarta. Las unidades más frecuentes, el filtrado y las estadísticas de las puntuaciones z se toman de las ventanas de los textos de referencia o de un conjunto aparte `statistics`, y cada ventana del texto se compara por la variante de Delta con el centroide de las ventanas de cada texto de referencia. El resultado son las distancias de las ventanas (filas, por la posición de su centro en unidades) a las referencias (columnas); donde la referencia más cercana cambia a lo largo del texto, cambia también el estilo: otro autor de una parte de un texto escrito en colaboración, un pasaje tomado de otro texto. A diferencia de stylo, que suma las diferencias de las frecuencias brutas, las distancias son las de `delta_profiles` sobre puntuaciones z.

Escalados por sus propias ventanas, los centroides de las referencias se equilibran entre sí, y la Delta coseno pierde su sentido: las distancias coseno de una ventana a las referencias promedian 1 (ponderadas por sus ventanas y las longitudes de sus centroides); con dos referencias suman 2 y las líneas son simétricas entre sí, así que un pasaje de un tercer autor parece a medio camino entre ellas. Con pocas referencias, la Delta coseno necesita unas `statistics` de más textos - otros autores, otras obras; las Deltas de Burrows y de Eder no tienen esa limitación. Con `statistics` basta una sola referencia.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `reference` | `dict[str, list[str]]` | - | Unidades de los textos de referencia por los nombres de los textos |
| `text` | `list[str]` | - | Unidades del texto a examinar |
| `window` | `int` | `5000` | Tamaño de una ventana en unidades |
| `step` | `int` | `1000` | Distancia entre los inicios de las ventanas en unidades |
| `n_mfw` | `int` | `100` | Número de las unidades más frecuentes; `None` - todas |
| `variant` | `str` | `'burrows'` | Variante de Delta de `anyts.constants.DELTA_VARIANTS` |
| `culling` | `float` | `0.0` | Menor proporción de ventanas en la que aparece una unidad |
| `statistics` | `dict[str, list[str]]` | `None` | Textos cuyas ventanas dan las unidades y las estadísticas del escalado; `None` - los textos de referencia |

Un corpus que no es un mapeo de listas de cadenas y unas unidades del texto que no son una lista de cadenas lanzan `SourceTypeError`. La falta de textos de referencia, menos de dos sin `statistics`, un texto sin unidades o más corto que una ventana, menos de tres ventanas de las estadísticas y un filtrado que no deja ninguna unidad lanzan `SourceError`. Una variante desconocida, un `window`, un `step` o un `n_mfw` que no es un entero de al menos uno, un `step` mayor que la ventana y un `culling` que no es un número dentro de [0, 1] lanzan `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import rolling_delta

    rolling_delta(corpus, corpus["A"] + corpus["B"], window=6, step=3, n_mfw=10).round(3)
    ```

=== "Resultado"

    ```
            A      B      C
    3   0.830  1.181  0.954
    6   0.709  1.166  0.845
    9   0.957  1.225  0.942
    12  0.799  1.067  0.784
    15  0.761  0.687  0.757
    18  0.830  1.181  0.954
    21  1.048  0.919  0.954
    24  1.216  0.610  1.123
    27  1.003  0.381  1.087
    30  1.221  0.377  0.999
    33  0.980  0.425  0.757
    36  1.003  0.381  1.087
    ```

## Zeta { #zeta }

<!-- core: corpus/stylometry.md:zeta 1b7460b -->
``` {.python .signature}
zeta(target, comparison, segment_size=2000, top_n=None)
```

Marcadores de palabras preferidas y evitadas según Burrows (2007) y Craig y Kinney (2009). Cada texto de ambos corpus se divide en segmentos de unas `segment_size` palabras (la longitud dividida por el tamaño, redondeada al entero más próximo con las mitades hacia arriba, al menos un segmento); $DP$ es la proporción de segmentos de un corpus con la palabra. Zeta es $DP_{target} - DP_{comparison}$, de −1 a 1 (`zeta.craig` en stylo; la Zeta clásica de Craig, $DP_{target} + (1 - DP_{comparison})$, es mayor en uno); la Zeta logarítmica es $\log_2 \frac{DP_{target}}{DP_{comparison}}$ ([Schöch et al. 2018](https://zeta-project.eu/en/keyness-measures/burrows-zeta-logarithmic-zeta/)), con una proporción nula sustituida por medio segmento. La lista va de las palabras que prefiere el corpus objetivo a las que evita.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `target` | `list[str]` / `list[list[str]]` | - | Palabras del corpus objetivo: un texto o una lista de textos |
| `comparison` | `list[str]` / `list[list[str]]` | - | Palabras del corpus de comparación |
| `segment_size` | `int` | `2000` | Tamaño de un segmento en palabras |
| `top_n` | `int` | `None` | Número de palabras desde el principio de la lista; `None` - todas |

El resultado es una lista de tuplas con nombre `ZetaScore(word, dp_target, dp_comparison, zeta, log_zeta)` por Zeta descendente, por Zeta logarítmica descendente y alfabéticamente si empatan. Un corpus que no es ni una lista de cadenas ni una lista de tales listas lanza `SourceTypeError`, y un corpus sin palabras, `SourceError`; un `segment_size` o un `top_n` que no es un entero de al menos uno lanza `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import zeta

    zeta(corpus["A"], corpus["B"], segment_size=5, top_n=2)
    zeta(corpus["A"], corpus["B"], segment_size=5)[-1]
    ```

=== "Resultado"

    ```
    [ZetaScore(word='gato', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0), ZetaScore(word='la', dp_target=0.5, dp_comparison=0.0, zeta=0.5, log_zeta=2.0)]
    ZetaScore(word='suelo', dp_target=0.0, dp_comparison=0.5, zeta=-0.5, log_zeta=-2.0)
    ```

<!-- core: corpus/stylometry.md:zeta_segments 89aea5c -->
``` {.python .signature}
zeta_segments(corpora, preferred, avoided, segment_size=2000)
```

Las proporciones de los marcadores de Zeta en los segmentos de los corpus, tal como `oppose` de stylo sitúa los segmentos: cada texto se divide en segmentos como en `zeta`, y un segmento recibe las proporciones de las palabras de las listas `preferred` y `avoided` presentes en él. Con los marcadores de un corpus objetivo frente a un corpus de comparación, los segmentos del objetivo quedan arriba a la izquierda del plano de las dos proporciones y los de la comparación abajo a la derecha; los segmentos de un texto de autoría disputada muestran a qué grupo se acerca (`zeta_scatter_plot`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `corpora` | `dict[str, list[str] / list[list[str]]]` | - | Palabras de los corpus por nombre - un texto o una lista de textos cada uno |
| `preferred` | `Collection[str]` | - | Palabras que prefiere el corpus objetivo - el principio de la lista de `zeta` |
| `avoided` | `Collection[str]` | - | Palabras que evita el corpus objetivo - el final de la lista |
| `segment_size` | `int` | `2000` | Tamaño de un segmento en palabras |

El resultado es un `DataFrame` de los segmentos en el orden de los corpus y de sus textos, con las columnas `corpus` (el nombre del corpus), `preferred` y `avoided` (las proporciones de las listas). Unos corpus que no son un mapeo y un corpus o una lista de marcadores que no es una lista de cadenas lanzan `SourceTypeError`; la falta de corpus, una lista de marcadores vacía y un corpus sin palabras, `SourceError`, y un `segment_size` que no es un entero de al menos uno, `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import zeta_segments

    scores = zeta(corpus["A"], corpus["B"], segment_size=5)
    preferred = [score.word for score in scores if score.zeta > 0]
    avoided = [score.word for score in scores if score.zeta < 0]
    zeta_segments(corpus, preferred, avoided, segment_size=5).round(3)
    ```

=== "Resultado"

    ```
       corpus  preferred  avoided
    0       A      0.333    0.125
    1       A      0.333    0.000
    2       A      0.333    0.125
    3       A      0.444    0.000
    4       B      0.000    0.250
    5       B      0.000    0.500
    6       B      0.000    0.500
    7       B      0.000    0.375
    8       C      0.111    0.125
    9       C      0.333    0.000
    10      C      0.111    0.250
    ```

## Ji cuadrado de Kilgarriff { #kilgarriff_chi2 }

<!-- core: corpus/stylometry.md:kilgarriff_chi2 33184e9 -->
``` {.python .signature}
kilgarriff_chi2(words_a, words_b, n_mfw=500)
```

La distancia entre dos corpus según [Kilgarriff (2001)](https://www.sketchengine.eu/wp-content/uploads/comparing_corpora_2001.pdf): para las `n_mfw` palabras más frecuentes del corpus conjunto las frecuencias esperadas en los corpus son proporcionales a sus tamaños, $\chi^2 = \sum (O - E)^2 / E$ sobre las palabras y ambos corpus. Cuanto mayor es el valor, más difieren los corpus; crece con el tamaño de los corpus, así que solo son comparables los pares de tamaños iguales.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words_a` | `list[str]` | - | Palabras del primer corpus |
| `words_b` | `list[str]` | - | Palabras del segundo corpus |
| `n_mfw` | `int` | `500` | Número de las palabras más frecuentes del corpus conjunto |

Unas palabras que no son una lista de cadenas lanzan `SourceTypeError`, un corpus sin palabras, `SourceError`, y un `n_mfw` que no es un entero de al menos uno, `ParameterError`.

=== "Código"

    ``` python
    from ests.corpus import kilgarriff_chi2

    round(kilgarriff_chi2(corpus["A"], corpus["B"], n_mfw=5), 3)
    ```

=== "Resultado"

    ```
    3.119
    ```

## Curva de Mendenhall { #mendenhall }

<!-- core: corpus/stylometry.md:mendenhall_curve be1fbeb -->
``` {.python .signature}
mendenhall_curve(words)
```

Las proporciones de las palabras de cada longitud en caracteres por longitud ascendente (Mendenhall 1887), un perfil del autor comparable entre textos sea cual sea su tamaño.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[str]` | - | Palabras del texto |

Unas palabras que no son una lista de cadenas lanzan `SourceTypeError`, y la falta de palabras, `SourceError`.

<!-- core: corpus/stylometry.md:mendenhall_distance 187c51f -->
``` {.python .signature}
mendenhall_distance(words_a, words_b)
```

La distancia de Jensen-Shannon con base 2 entre las curvas de Mendenhall de dos textos, de 0 (las distribuciones coinciden) a 1.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words_a` | `list[str]` | - | Palabras del primer texto |
| `words_b` | `list[str]` | - | Palabras del segundo texto |

Unas palabras que no son una lista de cadenas lanzan `SourceTypeError`, y un texto sin palabras, `SourceError`.

=== "Código"

    ``` python
    from ests.corpus import mendenhall_curve, mendenhall_distance

    {length: round(share, 3) for length, share in mendenhall_curve(corpus["A"]).items()}
    round(mendenhall_distance(corpus["A"], corpus["B"]), 3)
    ```

=== "Resultado"

    ```
    {1: 0.095, 2: 0.333, 3: 0.095, 4: 0.095, 6: 0.19, 7: 0.19}
    0.415
    ```

## Perfil de las palabras funcionales { #function_words_profile }

``` {.python .signature}
function_words_profile(source, nlp=None)
```

Las proporciones de las adposiciones, las conjunciones coordinantes y subordinantes, las partículas, los pronombres, los determinantes y las interjecciones (`ests.constants.FUNCTION_UD_POS`: `ADP`, `CCONJ`, `SCONJ`, `PART`, `PRON`, `DET`, `INTJ`) entre las palabras del texto. Las palabras funcionales no dependen del tema, así que su perfil es un rasgo clásico de autoría desde Mosteller y Wallace (1964).

Las categorías gramaticales son las de la anotación de un `Doc` que las lleva. Las palabras de una lista o de un `Doc` sin categorías gramaticales las etiqueta el modelo en su contexto, así que han de pasarse en el orden del texto; la puntuación de la lista ayuda al etiquetado y no se cuenta. El pipeline es el modelo [`es_core_news_sm`](../installation.md#model) o el que se pasa en `nlp`, sin el analizador sintáctico, el lematizador ni el reconocedor de entidades. En las Universal Dependencies del español la negación *no* es un adverbio y no una partícula, así que `PART` es rara.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `list[str]` / `Doc` | - | Palabras del texto u objeto Doc |
| `nlp` | `Language` | `None` | Pipeline para una lista de palabras; `None` - el modelo por defecto |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas, un pipeline que no es un `Language` de spaCy;
- `SourceError` - una fuente sin palabras, un pipeline que no etiqueta las categorías gramaticales (`spacy.blank("es")`), un carácter sin forma UTF-8;
- `DatasetNotFoundError` - el modelo por defecto no está instalado.

=== "Código"

    ``` python
    from ests.corpus import function_words_profile

    {pos: round(share, 3) for pos, share in function_words_profile(corpus["A"]).items()}
    ```

=== "Resultado"

    ```
    {'ADP': 0.095, 'CCONJ': 0.095, 'SCONJ': 0.0, 'PART': 0.0, 'PRON': 0.048, 'DET': 0.286, 'INTJ': 0.0}
    ```
