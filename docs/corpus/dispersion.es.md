# Dispersión de las palabras

<!-- core: corpus/dispersion.md:dispersion 37e70ea -->
``` {.python .signature}
dispersion(words, parts=10, word=None, min_freq=1)
```

La dispersión de una palabra es lo uniformemente que se reparte por las partes de un texto o de un corpus. La frecuencia no distingue una palabra que aparece una vez en cada capítulo de otra reunida en un solo capítulo; las medidas de dispersión ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) la complementan.

`parts` es el número de partes de tamaño aproximadamente igual o los tamaños de las partes en orden (oraciones, párrafos, capítulos, documentos de un corpus), que suman el número de palabras; `split_paragraphs` de `anyts.extractors` da los párrafos de un texto, cuyas palabras dan los tamaños; los párrafos sin palabras, como una separación de escenas con asteriscos, se descartan antes, ya que una parte necesita una palabra. Se calculan seis medidas a partir de las frecuencias de cada palabra por parte; Gries recomienda DP como la principal.

Las palabras se comparan tal cual: las mayúsculas y minúsculas y la lematización corresponden al extractor de palabras.

`ests.corpus` reexporta la función del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/). Las palabras se extraen con [`WordsExtractor`](../extractors/words.md).

=== "Código"

    ``` python
    from ests import SentsExtractor, WordsExtractor
    from ests.corpus import dispersion

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    we = WordsExtractor(use_lexemes=True, lowercase=True)
    words = we.extract(text)
    sizes = [len(we.extract(sent)) for sent in SentsExtractor().extract(text)]
    sizes
    dispersion(words, parts=sizes, word="gato")

    # Tres partes iguales: a y pájaro se reúnen en los extremos del texto
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    ```

=== "Resultado"

    ```
    [11, 12, 14]
    [Dispersion(word='gato', freq=3, dp=0.04504504504504503, dp_norm=0.06410256410256408, juilland_d=0.9307654905484509, carroll_d2=0.9955884389001025, rosengren_s=0.9974825285744621, kl_divergence=0.007241184435774255)]
    [('el', 0.1), ('gato', 0.02), ('en', 0.02), ('ventana', 0.02), ('y', 0.02), ('a', 0.34), ('pájaro', 0.32)]
    ```

Los párrafos de un texto los da [`split_paragraphs`](../extractors/sentences.md#split_paragraphs), que se importa de `ests.extractors`; una separación de escenas con asteriscos no tiene palabras y se descarta:

=== "Código"

    ``` python
    from ests.extractors import split_paragraphs

    text = (
        "Capítulo I\n\nEl gato estaba en la ventana y miraba a los pájaros.\n\n* * *\n\n"
        "Los pájaros se fueron y el gato se durmió en la ventana.\n\n"
        "Mañana el gato volverá a estar en la ventana."
    )
    sizes = [n for n in (len(we.extract(part)) for part in split_paragraphs(text)) if n]
    sizes
    [(d.word, round(d.dp, 2)) for d in dispersion(we.extract(text), parts=sizes, min_freq=3)]
    ```

=== "Resultado"

    ```
    [2, 11, 12, 9]
    [('el', 0.07), ('gato', 0.08), ('en', 0.08), ('ventana', 0.08)]
    ```

## Parámetros

<!-- core: corpus/dispersion.md:dispersion-parameters 2fdf192 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[str]` | - | Palabras del texto en orden |
| `parts` | `int` / `list[int]` | `10` | Número de partes (de 2 al número de palabras) o tamaños de las partes |
| `word` | `str` | `None` | Palabra cuya dispersión se busca; `None` - todas las palabras |
| `min_freq` | `int` | `1` | Frecuencia mínima de una palabra |

Unas palabras que no son una lista de cadenas lanzan `SourceTypeError`, y la falta de palabras, `SourceError`. Un `parts` que no es ni un entero de 2 al número de palabras ni dos o más enteros positivos que lo sumen, un `word` que no es una cadena y un `min_freq` que no es un entero lanzan `ParameterError`.

## Resultado

<!-- core: corpus/dispersion.md:Dispersion 536c09a -->
``` {.python .signature}
Dispersion(word, freq, dp, dp_norm, juilland_d, carroll_d2, rosengren_s, kl_divergence)
```

Una lista de tuplas con nombre `Dispersion` por frecuencia descendente: la palabra, su frecuencia y las medidas; `pd.DataFrame(result)` da una tabla.

## Medidas

<!-- core: corpus/dispersion.md:dispersion-measures dc6c36a -->
Las medidas, los campos de `Dispersion`, con sus nombres en `anyts.constants.DISPERSION_STATS_DESC`:

| Campo | Qué mide | Rango | Un valor mayor indica |
| :---- | :------- | :---- | :-------------------- |
| [`dp`](#dp) | Desviación de las proporciones de las apariciones respecto de las proporciones de las partes | De 0 a $1 - \min s_i$ | Más desigual |
| [`dp_norm`](#dp_norm) | DP sobre su mayor valor posible | 0-1 | Más desigual |
| [`juilland_d`](#juilland_d) | Variación de las frecuencias relativas por parte | 0-1 | Más uniforme |
| [`carroll_d2`](#carroll_d2) | Entropía de las frecuencias relativas por parte | 0-1 | Más uniforme |
| [`rosengren_s`](#rosengren_s) | Reparto de las apariciones frente a los tamaños de las partes | De $\min s_i$ a 1 | Más uniforme |
| [`kl_divergence`](#kl_divergence) | Divergencia de las proporciones de las apariciones respecto de las proporciones de las partes, en bits | De 0 a $-\log_2 \min s_i$ | Más desigual |

Cada medida es una función del módulo `anyts.corpus.dispersion` de las frecuencias de la palabra por parte y de los tamaños de las partes. Para $n$ partes de tamaños $n_i$ y proporciones $s_i$ del texto, frecuencias de la palabra por parte $v_i$ y una frecuencia total $f = \sum v_i$, $p_i = v_i / n_i$ es la frecuencia relativa en una parte:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `frequencies` | `list[int]` | - | Frecuencias de la palabra por parte |
| `sizes` | `list[int]` | - | Tamaños de las partes |

Para una palabra de frecuencia nula todas las medidas son `nan`.

El módulo `ests.corpus.dispersion` reexporta las funciones de las medidas (`from ests.corpus.dispersion import calc_dp`).

<div class="metric-card" markdown>

### Desviación de proporciones DP { #dp }

`dp` · [Gries (2008)](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_dp 6c51955 -->
``` {.python .signature}
calc_dp(frequencies, sizes)
```

Cuánto se alejan las proporciones de las apariciones de la palabra por parte de las proporciones de las partes: 0 significa que la palabra se reparte en proporción a los tamaños de las partes, $1 - s_i$, que está toda en la parte $i$.

$$
DP = \frac{1}{2} \sum \left\lvert \frac{v_i}{f} - s_i \right\rvert
$$

</div>

<div class="metric-card" markdown>

### DP normalizada { #dp_norm }

`dp_norm` · Lijffijt y Gries (2012)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_dp_norm bab9d44 -->
``` {.python .signature}
calc_dp_norm(frequencies, sizes)
```

DP dividida por su mayor valor posible, así que el máximo es uno sea cual sea la división.

$$
\frac{DP}{1 - \min s_i}
$$

</div>

<div class="metric-card" markdown>

### D de Juilland { #juilland_d }

`juilland_d` · Juilland y Chang-Rodríguez (1964)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_juilland_d c172dee -->
``` {.python .signature}
calc_juilland_d(frequencies, sizes)
```

Uno menos el coeficiente de variación $V$ de las frecuencias relativas $p_i$ dividido por su mayor valor $\sqrt{n - 1}$: 1 significa uniforme, 0, toda en una parte. La desviación típica $\sigma$ es la de la población, como en Gries (2020); Gries (2008) toma la muestral.

$$
1 - \frac{V}{\sqrt{n - 1}}, \quad V = \frac{\sigma(p)}{\mu(p)}
$$

</div>

<div class="metric-card" markdown>

### D2 de Carroll { #carroll_d2 }

`carroll_d2` · Carroll (1970)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_carroll_d2 82075b3 -->
``` {.python .signature}
calc_carroll_d2(frequencies, sizes)
```

La entropía de la distribución de las frecuencias relativas $p_i$ por las partes, dividida por su mayor valor: 1 significa uniforme, 0, toda en una parte.

$$
\frac{H(p)}{\log_2 n}
$$

</div>

<div class="metric-card" markdown>

### S de Rosengren { #rosengren_s }

`rosengren_s` · Rosengren (1971)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_rosengren_s 29fcb9c -->
``` {.python .signature}
calc_rosengren_s(frequencies, sizes)
```

1 significa que la palabra se reparte en proporción a los tamaños de las partes; toda en la parte $i$, da $s_i$, así que $1/n$ en una de $n$ partes iguales.

$$
\frac{(\sum \sqrt{s_i v_i})^2}{f}
$$

</div>

<div class="metric-card" markdown>

### Divergencia de Kullback-Leibler { #kl_divergence }

`kl_divergence` · [Gries (2020)](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)
{ .metric-meta }

<!-- core: corpus/dispersion.md:calc_kl_divergence f5095d5 -->
``` {.python .signature}
calc_kl_divergence(frequencies, sizes)
```

La divergencia de las proporciones de las apariciones de la palabra por parte respecto de las proporciones de las partes: 0 significa en proporción; crece cuando la palabra se reúne en partes pequeñas.

$$
\sum \frac{v_i}{f} \log_2 \frac{v_i / f}{s_i}
$$

</div>
