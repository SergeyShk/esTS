# Colocaciones

<!-- core: corpus/collocations.md:collocations c290cd8 -->
``` {.python .signature}
collocations(words, window=5, measure='logdice', min_freq=2, node=None, top_n=None)
```

Extracción de colocaciones: pares de palabras que aparecen juntas más a menudo de lo que daría la independencia - expresiones fijas, terminología, la combinatoria de una palabra. Las medidas de asociación son las de [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) y de [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html).

Los pares son ordenados, como en NLTK: la palabra de la derecha aparece como mucho `window` palabras después de la de la izquierda, y cada par de posiciones se cuenta una vez; `window=1` da bigramas. Las medidas toman la frecuencia del par dividida por la ventana (Church y Hanks 1990, como en NLTK), lo que mantiene la frecuencia esperada independiente de la ventana y Dice y la sensibilidad mínima en uno como máximo; `freq_pair` queda sin dividir. Así, con `window > 1` un par siempre contiguo recibe un logDice de $14 - \log_2 window$ (13 con una ventana de 2), no 14 como en Sketch Engine con su coocurrencia sin dividir; para 14 hace falta un par a todas las distancias dentro de la ventana. `node` conserva los pares con la palabra dada a cualquiera de los dos lados.

Las palabras se comparan tal cual: las mayúsculas y minúsculas, la lematización y las palabras vacías corresponden al extractor de palabras; los lemas convienen a las expresiones fijas, las formas a las construcciones gramaticales.

`ests.corpus` reexporta la función del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/collocations/). Las palabras se extraen con [`WordsExtractor`](../extractors/words.md); para las expresiones fijas del español como `punto de vista` o `llevar a cabo` conviene usar sus lemas (`use_lexemes=True`).

=== "Código"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )

    collocations(words, window=2, top_n=1)
    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="gato", min_freq=1, measure="mi")[:2]
    ]
    ```

=== "Resultado"

    ```
    [Collocation(left='en', right='ventana', freq_left=3, freq_right=3, freq_pair=3, score=13.0)]
    [('gato', 'volver', 3.62), ('gato', 'estar', 2.62)]
    ```

## Parámetros

<!-- core: corpus/collocations.md:collocations-parameters be13ed1 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[str]` | - | Palabras del texto en orden |
| `window` | `int` | `5` | Mayor distancia entre las palabras de un par |
| `measure` | `str` | `'logdice'` | Medida de `anyts.constants.COLLOCATION_MEASURES` |
| `min_freq` | `int` | `2` | Frecuencia mínima de un par |
| `node` | `str` | `None` | Palabra cuya combinatoria se busca; `None` - todos los pares |
| `top_n` | `int` | `None` | Número de colocaciones; `None` - todas |

Unas palabras que no son una lista de cadenas lanzan `SourceTypeError`, y la falta de palabras, `SourceError`. Una medida desconocida, un `window` o un `top_n` que no es un entero de al menos uno, un `min_freq` que no es un entero y un `node` que no es una cadena lanzan `ParameterError`.

## Resultado

<!-- core: corpus/collocations.md:Collocation f1761f5 -->
``` {.python .signature}
Collocation(left, right, freq_left, freq_right, freq_pair, score)
```

Una lista de tuplas con nombre `Collocation` por orden descendente de la medida y de la frecuencia del par (los empates, alfabéticamente); `pd.DataFrame(found)` da una tabla.

| Campo | Tipo | Descripción |
| :---- | :--- | :---------- |
| `left` | `str` | Palabra de la izquierda |
| `right` | `str` | Palabra de la derecha, dentro de la ventana tras la de la izquierda |
| `freq_left` | `int` | Frecuencia de la palabra de la izquierda |
| `freq_right` | `int` | Frecuencia de la palabra de la derecha |
| `freq_pair` | `int` | Frecuencia de la coocurrencia |
| `score` | `float` | Valor de la medida elegida |

## Medidas

<!-- core: corpus/collocations.md:collocations-measures e3fd7a0 -->
Las medidas de `measure` por clave, con sus nombres y descripciones en `anyts.constants.COLLOCATION_MEASURES`:

| Clave | Qué mide | Rango | Un valor mayor indica |
| :---- | :------- | :---- | :-------------------- |
| [`mi`](#mi) | Frecuencia del par frente a la esperada, en bits | Cualquier número | Una asociación más fuerte |
| [`mi3`](#mi3) | MI con la frecuencia del par al cubo | Cualquier número | Una asociación más fuerte |
| [`t_score`](#t_score) | Diferencia entre la frecuencia observada y la esperada del par | Cualquier número | Una asociación más segura |
| [`dice`](#dice) | Proporción del par en las apariciones de las dos palabras | 0-1 | Una asociación más fuerte |
| [`logdice`](#logdice) | Coeficiente de Dice en escala logarítmica | 14 o menos | Una asociación más fuerte |
| [`log_likelihood`](#log_likelihood) | Significación de la asociación | 0 o más, `nan` cuando una palabra ocupa todo el texto o una celda es negativa | Una desviación más significativa respecto de la independencia, tanto para los pares que se atraen como para los que se evitan |
| [`npmi`](#npmi) | MI normalizada por la información del par | De −1 a 1 | Una asociación más fuerte |
| [`min_sensitivity`](#min_sensitivity) | Menor proporción del par en las apariciones de una u otra palabra | 0-1 | Una asociación más fuerte |

Cada medida es una función del módulo `anyts.corpus.collocations` de las frecuencias de las palabras y del par y del número de palabras:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `freq_a` | `int` | - | Frecuencia $f_a$ de la primera palabra |
| `freq_b` | `int` | - | Frecuencia $f_b$ de la segunda palabra |
| `freq_ab` | `float` | - | Frecuencia $f_{ab}$ del par |
| `n` | `int` | - | Número de palabras $N$ del texto |

Un par de frecuencia nula da `nan` para MI, MI³, el t-score, logDice y NPMI.

El módulo `ests.corpus.collocations` reexporta las funciones de las medidas (`from ests.corpus.collocations import calc_logdice`).

<div class="metric-card" markdown>

### Información mutua { #mi }

`mi` · Church y Hanks (1990)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_mi b0aa7c7 -->
``` {.python .signature}
calc_mi(freq_a, freq_b, freq_ab, n)
```

La información mutua puntual de las dos palabras; sobrevalora los pares raros.

$$
\log_2 \frac{f_{ab} N}{f_a f_b}
$$

</div>

<div class="metric-card" markdown>

### MI³ { #mi3 }

`mi3` · Oakes (1998)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_mi3 92d7122 -->
``` {.python .signature}
calc_mi3(freq_a, freq_b, freq_ab, n)
```

La información mutua con la frecuencia del par al cubo, que favorece los pares frecuentes.

$$
\log_2 \frac{f_{ab}^3 N}{f_a f_b}
$$

</div>

<div class="metric-card" markdown>

### t-score { #t_score }

`t_score` · Church et al. (1991)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_t_score f89d062 -->
``` {.python .signature}
calc_t_score(freq_a, freq_b, freq_ab, n)
```

La diferencia entre la frecuencia observada y la esperada del par dividida por la raíz de la observada; favorece los pares frecuentes.

$$
\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}
$$

</div>

<div class="metric-card" markdown>

### Coeficiente de Dice { #dice }

`dice`
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_dice 7a8289e -->
``` {.python .signature}
calc_dice(freq_a, freq_b, freq_ab, n)
```

La proporción del par en las apariciones de las dos palabras; no depende del tamaño del texto.

$$
\frac{2 f_{ab}}{f_a + f_b}
$$

</div>

<div class="metric-card" markdown>

### logDice { #logdice }

`logdice` · [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_logdice a3020bb -->
``` {.python .signature}
calc_logdice(freq_a, freq_b, freq_ab, n)
```

El coeficiente de Dice en una escala logarítmica binaria, la medida por defecto, como en Sketch Engine. No depende del tamaño del texto; por debajo de cero el vínculo es débil.

$$
14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}
$$

</div>

<div class="metric-card" markdown>

### Razón de verosimilitud { #log_likelihood }

`log_likelihood` · Dunning (1993)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_log_likelihood 0ed2f9e -->
``` {.python .signature}
calc_log_likelihood(freq_a, freq_b, freq_ab, n)
```

$G^2$ sobre la tabla de contingencia 2×2 de las dos palabras: las frecuencias observadas $O$ - $f_{ab}$, $f_a - f_{ab}$, $f_b - f_{ab}$ y $N - f_a - f_b + f_{ab}$ - frente a las esperadas $E$ bajo independencia. Una palabra que ocupa todo el texto, o una celda negativa, como la de una palabra emparejada consigo misma en una ventana mayor que uno, da `nan`.

$$
G^2 = 2 \sum O \ln \frac{O}{E}
$$

</div>

<div class="metric-card" markdown>

### NPMI { #npmi }

`npmi` · Bouma (2009)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_npmi a88529b -->
``` {.python .signature}
calc_npmi(freq_a, freq_b, freq_ab, n)
```

La información mutua normalizada por la información del par: uno significa que las palabras solo aparecen juntas. Un par tan frecuente como largo es el texto da `nan`.

$$
\frac{MI}{-\log_2 (f_{ab} / N)}
$$

</div>

<div class="metric-card" markdown>

### Sensibilidad mínima { #min_sensitivity }

`min_sensitivity` · Pedersen (1998)
{ .metric-meta }

<!-- core: corpus/collocations.md:calc_min_sensitivity e3bdac7 -->
``` {.python .signature}
calc_min_sensitivity(freq_a, freq_b, freq_ab, n)
```

La menor de las proporciones del par en las apariciones de cada palabra.

$$
\min\left(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b}\right)
$$

</div>
