# Palabras clave

``` {.python .signature}
keyness(target, reference, measure='log_likelihood', min_freq=1, positive=True, top_n=None)
```

<!-- core: corpus/keyness.md:keyness bbbd1ba -->
Extracción de palabras clave (keyness) de un corpus objetivo frente a uno de referencia: las palabras que aparecen significativamente más a menudo en el corpus objetivo que en el de referencia.

Cada palabra recibe dos valores que [Gabrielatos y Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) y [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recomiendan leer juntos: la razón de verosimilitud $G^2$ con su valor p (si hay una diferencia) y Log Ratio (cuán grande es), además de la medida elegida `score`, que ordena la lista. Las medidas de significación ($G^2$, ji cuadrado, BIC) y ELL, el tamaño del efecto de $G^2$, son negativas cuando la palabra es más frecuente en la referencia; %DIFF, Log Ratio y la razón de momios tienen dirección por construcción.

La referencia puede ser una lista de palabras, un mapeo de frecuencias (su tamaño es la suma de los recuentos) o una `FrequencyReference`. Las palabras se comparan tal cual: las mayúsculas y minúsculas, la lematización y las palabras vacías corresponden al extractor de palabras, y los dos corpus tienen que extraerse del mismo modo.

La función envuelve `keyness` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/keyness/) y admite además como referencia el [diccionario de frecuencias](../datasets/freqdict.md) `FreqDict`; `FrequencyReference` está en `ests.corpus` junto a ella. Las palabras se extraen con [`WordsExtractor`](../extractors/words.md).

=== "Código"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness

    we = WordsExtractor(use_lexemes=True, lowercase=True)
    target = we.extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    reference = we.extract(
        "El perro estaba en el suelo y dormía. Después el perro comió y volvió a dormir. "
        "Mañana el perro saldrá a pasear."
    )

    keyness(target, reference, top_n=1)
    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    ```

=== "Resultado"

    ```
    [Keyword(word='gato', freq_target=3, freq_reference=0.0, ipm_target=81081.08108108108, ipm_reference=0.0, g2=2.79971718756897, p_value=0.09428093556593176, log_ratio=1.8349407537295037, score=2.79971718756897)]
    [('perro', -5.92), ('comer', -1.97)]
    ```

## Parámetros

<!-- core: corpus/keyness.md:keyness-parameters c87c5b2 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `target` | `list[str]` / `dict[str, int]` | - | Palabras del corpus objetivo o sus frecuencias |
| `reference` | `list[str]` / `dict[str, float]` / `FrequencyReference` | - | Palabras del corpus de referencia, sus frecuencias o una referencia por frecuencias |
| `measure` | `str` | `'log_likelihood'` | Medida de `anyts.constants.KEYNESS_MEASURES` para `score` y el orden |
| `min_freq` | `int` | `1` | Frecuencia mínima de una palabra clave en su propio corpus |
| `positive` | `bool` | `True` | Palabras clave positivas (más frecuentes en el corpus objetivo) o negativas (más frecuentes en la referencia) |
| `top_n` | `int` | `None` | Número de palabras clave; `None` - todas |

Los parámetros y el corpus objetivo los comprueba `check_keyness_params`. Una referencia que no es una lista de cadenas, un contador ni una `FrequencyReference` lanza `SourceTypeError`, y una frecuencia negativa, `nan` o infinita de un contador y un corpus vacío lanzan `SourceError`.

`reference` también puede ser `FreqDict`, frente al cual `target` son formas. Un diccionario de frecuencias que no está descargado lanza `DatasetNotFoundError`. `keyness` comprueba sus parámetros y el corpus objetivo con `check_keyness_params` antes de leer `FreqDict`, así que un argumento erróneo falla antes de cargar el diccionario.

<!-- core: corpus/keyness.md:check_keyness_params 9ffcaab -->
``` {.python .signature}
check_keyness_params(measure='log_likelihood', min_freq=1, top_n=None, target=None)
```

Comprueba los parámetros de `keyness` antes de leer un diccionario de frecuencias: lanza `ParameterError` salvo que la medida sea una de `KEYNESS_MEASURES`, la frecuencia mínima un entero y el número de palabras clave `None` o un entero de al menos uno. Con `target` lanza además `SourceTypeError` salvo que el corpus objetivo sea una lista de cadenas o un mapeo de cadenas a frecuencias enteras, y `SourceError` para una frecuencia negativa, nan o infinita.

## Referencia por frecuencias

<!-- core: corpus/keyness.md:FrequencyReference 02046dc -->
``` {.python .signature}
FrequencyReference(counts, size, missing=0.0, key=None, keep=None)
```

Un corpus de referencia descrito solo por sus frecuencias, como un diccionario de frecuencias construido a partir de un corpus demasiado grande para pasarlo como palabras:

| Campo | Tipo | Por defecto | Descripción |
| :---- | :--- | :------ | :---------- |
| `counts` | `dict[str, float]` | - | Frecuencias de las claves en el corpus de referencia |
| `size` | `float` | - | Tamaño del corpus de referencia en palabras |
| `missing` | `float` | `0.0` | Frecuencia de una clave que falta en `counts` |
| `key` | `Callable` | `None` | Clave de una palabra del corpus objetivo en `counts`, como su lema; `None` - la propia palabra |
| `keep` | `Callable` | `None` | Si una palabra del corpus objetivo se cuenta; `None` - todas las palabras |

Solo se cuentan las palabras del objetivo que `keep` deja pasar, bajo su `key`, tanto en las frecuencias como en el tamaño. Una clave que falta en `counts` tiene la frecuencia `missing`, como la frecuencia mínima de un diccionario: una cota superior, así que su palabra puede ser palabra clave positiva pero nunca negativa. Las palabras clave negativas salen solo de las claves de `counts` que `keep` deja pasar. Una frecuencia se comprueba al leerla, así que para las palabras clave positivas no se recorre un diccionario grande: una que no es un número lanza `SourceTypeError`, y una negativa, `nan` o infinita, `SourceError`. Un `size` o un `missing` que no es un número finito o es negativo lanza `ParameterError`, y un `key` o un `keep` que no se puede invocar, `SourceTypeError`.

El diccionario de frecuencias `FreqDict` de Google Books Ngram pasado como `reference` se convierte en una referencia así:

| Campo | `FreqDict` |
| :---- | :--------- |
| `counts` | los ipm de `FreqDict.word_ipm`, incluidos los nombres propios, convertidos en apariciones en el corpus del diccionario |
| `size` | `CORPUS_SIZE`, 63 000 millones de palabras de los libros de 1980-2019 |
| `missing` | la frecuencia mínima del diccionario `FreqDict.min_ipm`, 0,1 ipm (unas 6300 apariciones) |
| `key` | [`lemma_key`](../datasets/freqdict.md#lemma_key): una palabra clave puede llevar la etiqueta de otro lema, *Roma* se cuenta bajo `romo` |
| `keep` | las formas hechas de las letras de `WORD_PATTERN`; los números y las palabras con guion o con punto quedan fuera |

El corpus objetivo tiene que contarse como se contó el diccionario: formas con las palabras vacías, no lemas - `lemma_key` no es idempotente (`estado` - `estar`), así que `WordsExtractor(use_lexemes=True)` no sirve. El diccionario describe el registro de los libros, así que las palabras clave negativas de un texto son las de la prosa académica (`de`, `social`, `país`).

Frente al diccionario las palabras de una comedia de Lope de Vega del [corpus de literatura](../datasets/spanishliterature.md) dan sus personajes:

=== "Código"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness
    from ests.datasets import FreqDict, SpanishLiterature

    text = next(SpanishLiterature().get_texts(author="lope", genre="drama"))
    words = WordsExtractor(lowercase=True).extract(text)
    for k in keyness(words, FreqDict(), top_n=5):
        print(k.word, k.freq_target, round(k.ipm_reference, 2), round(k.g2, 1), round(k.log_ratio, 2))
    ```

=== "Resultado"

    ```
    laurencia 135 0.32 2528.7 14.96
    mengo 105 0.13 2102.5 15.9
    comendador 154 5.33 2059.9 11.09
    frondoso 113 3.84 1515.6 11.12
    barrildo 52 0.1 995.7 15.26
    ```

## Resultado

<!-- core: corpus/keyness.md:Keyword 8a09d1b -->
``` {.python .signature}
Keyword(word, freq_target, freq_reference, ipm_target, ipm_reference, g2, p_value, log_ratio, score)
```

Una lista de tuplas con nombre `Keyword` por keyness descendente (los empates por frecuencia descendente y alfabéticamente, las palabras de medida indefinida al final); `pd.DataFrame(keywords)` da una tabla.

| Campo | Tipo | Descripción |
| :---- | :--- | :---------- |
| `word` | `str` | Palabra |
| `freq_target` | `int` | Frecuencia en el corpus objetivo |
| `freq_reference` | `float` | Frecuencia en el corpus de referencia |
| `ipm_target` | `float` | Frecuencia en el corpus objetivo por millón de palabras |
| `ipm_reference` | `float` | Frecuencia en el corpus de referencia por millón de palabras |
| `g2` | `float` | $G^2$ con signo |
| `p_value` | `float` | Valor p de $G^2$ |
| `log_ratio` | `float` | Log Ratio |
| `score` | `float` | Valor de la medida elegida |

## Medidas

<!-- core: corpus/keyness.md:keyness-measures 62bf3c6 -->
Las medidas de `measure` por clave, con sus nombres y descripciones en `anyts.constants.KEYNESS_MEASURES`:

| Clave | Qué mide | Rango | Un valor mayor indica |
| :---- | :------- | :---- | :-------------------- |
| [`log_likelihood`](#log_likelihood) | Significación de la diferencia de las frecuencias | Cualquier número | Un exceso más significativo en el corpus objetivo |
| [`chi2`](#chi2) | Significación de la diferencia, con la corrección de Yates | Cualquier número | Un exceso más significativo en el corpus objetivo |
| [`diff`](#diff) | Diferencia de las frecuencias por millón, en porcentaje de la referencia | Por encima de −100 | Un exceso mayor en el corpus objetivo |
| [`log_ratio`](#log_ratio) | Logaritmo binario de la razón de las frecuencias por millón | Cualquier número | Un exceso mayor en el corpus objetivo |
| [`bic`](#bic) | Indicio de la diferencia: $G^2$ penalizado por el tamaño de los corpus | Cualquier número | Un indicio más fuerte de un exceso en el corpus objetivo, para una palabra más frecuente en él |
| [`ell`](#ell) | Tamaño del efecto de $G^2$ | De −1 a 1 por lo general, `nan` para frecuencias esperadas pequeñas | Un exceso mayor en el corpus objetivo |
| [`odds_ratio`](#odds_ratio) | Razón de los momios de la palabra en los corpus | De 0 a `inf`, `nan` si la palabra ocupa los dos corpus | Momios más altos en el corpus objetivo |

Cada medida es una función del módulo `anyts.corpus.keyness` de las frecuencias de una palabra y de los tamaños de los corpus, $N = c + d$:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `a` | `float` | - | Frecuencia de la palabra en el corpus objetivo |
| `b` | `float` | - | Frecuencia de la palabra en el corpus de referencia |
| `c` | `float` | - | Tamaño del corpus objetivo |
| `d` | `float` | - | Tamaño del corpus de referencia |

Una frecuencia nula en uno de los corpus se sustituye por 0.5 para %DIFF, Log Ratio y la razón de momios (Hardie 2014).

El módulo `ests.corpus.keyness` reexporta las funciones de las medidas (`from ests.corpus.keyness import calc_log_likelihood`).

<div class="metric-card" markdown>

### Razón de verosimilitud { #log_likelihood }

`log_likelihood` · `g2` · `p_value` · [Rayson y Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html)
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_log_likelihood 0a8ca96 -->
``` {.python .signature}
calc_log_likelihood(a, b, c, d)
```

La razón de verosimilitud de las frecuencias de la palabra frente a las esperadas $E_1$ y $E_2$; un término de frecuencia nula es cero. Los valores críticos son `anyts.constants.G2_CRITICAL_VALUES`: 3.84 para p < 0.05, 6.63 para p < 0.01, 10.83 para p < 0.001, 15.13 para p < 0.0001. El signo es negativo cuando la palabra es más frecuente en la referencia.

$$
G^2 = 2 \left(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2}\right), \quad E_1 = \frac{c\,(a+b)}{N}, \quad E_2 = \frac{d\,(a+b)}{N}
$$

<!-- core: corpus/keyness.md:calc_p_value 9f1c270 -->
``` {.python .signature}
calc_p_value(g2)
```

El valor p de un $G^2$ o de un ji cuadrado, sea cual sea su signo, según la distribución ji cuadrado con un grado de libertad; un array de valores da un array.

</div>

<div class="metric-card" markdown>

### Ji cuadrado { #chi2 }

`chi2`
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_chi2 9925633 -->
``` {.python .signature}
calc_chi2(a, b, c, d)
```

El ji cuadrado con la corrección de Yates sobre la tabla de contingencia 2×2 de la palabra y las demás palabras de cada corpus. Cuando la corrección supera la diferencia, el estadístico es cero. El signo es negativo cuando la palabra es más frecuente en la referencia.

$$
\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}
$$

</div>

<div class="metric-card" markdown>

### %DIFF { #diff }

`diff` · [Gabrielatos y Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf)
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_diff d06d112 -->
``` {.python .signature}
calc_diff(a, b, c, d)
```

La diferencia de las frecuencias $NF$ por millón de palabras, en porcentaje de la frecuencia en la referencia.

$$
\frac{NF_a - NF_b}{NF_b} \cdot 100
$$

</div>

<div class="metric-card" markdown>

### Log Ratio { #log_ratio }

`log_ratio` · [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/)
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_log_ratio dfc5efc -->
``` {.python .signature}
calc_log_ratio(a, b, c, d)
```

El logaritmo binario de la razón de las frecuencias $NF$ por millón de palabras: uno significa que la palabra es el doble de frecuente en el corpus objetivo.

$$
\log_2 \frac{NF_a}{NF_b}
$$

</div>

<div class="metric-card" markdown>

### BIC { #bic }

`bic` · Wilson (2013)
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_bic 1d500ea -->
``` {.python .signature}
calc_bic(a, b, c, d)
```

El criterio de información bayesiano de $G^2$. En valor absoluto, por encima de 2 es un indicio positivo de una diferencia, por encima de 6 un indicio fuerte, por encima de 10 muy fuerte; un valor de signo contrario al de $G^2$, cuando $\lvert G^2 \rvert < \ln N$, significa ausencia de indicio, no la dirección contraria.

$$
\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)
$$

</div>

<div class="metric-card" markdown>

### ELL { #ell }

`ell` · Johnston, Berry y Mielke (2006)
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_ell 43cc977 -->
``` {.python .signature}
calc_ell(a, b, c, d)
```

El tamaño del efecto de $G^2$: la proporción de la mayor desviación posible respecto de las frecuencias esperadas $E_1$ y $E_2$. Crece sin límite a medida que la menor frecuencia esperada se acerca a uno y es `nan` cuando esa frecuencia es como mucho uno (un logaritmo nulo o negativo). El signo es negativo cuando la palabra es más frecuente en la referencia.

$$
\frac{G^2}{N \ln \min(E_1, E_2)}
$$

</div>

<div class="metric-card" markdown>

### Razón de momios { #odds_ratio }

`odds_ratio`
{ .metric-meta }

<!-- core: corpus/keyness.md:calc_odds_ratio 836cc61 -->
``` {.python .signature}
calc_odds_ratio(a, b, c, d)
```

La razón de los momios de la palabra en los dos corpus: uno significa momios iguales. Una palabra que ocupa todo el corpus objetivo da `inf`, toda la referencia, 0, los dos, `nan`.

$$
\frac{a / (c - a)}{b / (d - b)}
$$

</div>
