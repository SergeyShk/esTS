# Palabras clave

!!! info ""
    **ests.corpus.keyness()**, **ests.corpus.Keyword**, **ests.corpus.FrequencyReference**

## Descripción

<!-- core: corpus/keyness.md:keyness 0018a96 -->
Extracción de palabras clave (keyness) de un corpus objetivo frente a uno de referencia: las palabras que aparecen significativamente más a menudo en el corpus objetivo que en el de referencia.

Para cada palabra se calculan dos valores que [Gabrielatos y Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) y [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recomiendan leer juntos: la razón de verosimilitud $G^2$ con su valor p (la significación de la diferencia: si la hay) y Log Ratio (el tamaño del efecto: cuán grande es). Se calcula además la medida elegida `score`, que sirve para ordenar. Las medidas de significación ($G^2$, ji cuadrado, BIC) y ELL, el tamaño del efecto de $G^2$, llevan signo: negativo cuando la palabra es más frecuente en la referencia; las demás medidas de efecto (%DIFF, Log Ratio, razón de momios) tienen dirección por construcción.

La referencia puede ser una lista de palabras, una correspondencia de frecuencias (su tamaño es la suma de los recuentos) o una `FrequencyReference`. Las palabras se comparan tal cual: las mayúsculas y minúsculas, la lematización y las palabras vacías corresponden al extractor de palabras, y los dos corpus tienen que extraerse del mismo modo.

La función envuelve `keyness` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/keyness/) y admite además como referencia el [diccionario de frecuencias](../datasets/freqdict.md) `FreqDict`; `FrequencyReference` está en `ests.corpus` junto a ella, y las funciones de las medidas, en `ests.corpus.keyness`. Las palabras se extraen con [`WordsExtractor`](../extractors/words.md).

## Medidas

<!-- core: corpus/keyness.md:keyness-measures 7d98aa3 -->
Para una palabra de frecuencia $a$ en un corpus objetivo de tamaño $c$ y de frecuencia $b$ en un corpus de referencia de tamaño $d$, $N = c + d$:

| Medida | Clave | Fórmula | Descripción |
| :----- | :---- | :------ | :---------- |
| Razón de verosimilitud | `log_likelihood` | $G^2 = 2\,(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2})$, $E_1 = \frac{c\,(a+b)}{N}$, $E_2 = \frac{d\,(a+b)}{N}$ | [Rayson y Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html); valores críticos `anyts.constants.G2_CRITICAL_VALUES`: 3.84 para p < 0.05, 6.63 para p < 0.01, 10.83 para p < 0.001, 15.13 para p < 0.0001 |
| Ji cuadrado | `chi2` | $\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}$ | con la corrección de Yates sobre la tabla de contingencia 2×2; si la corrección supera la diferencia, el estadístico es cero |
| %DIFF | `diff` | $\frac{NF_a - NF_b}{NF_b} \cdot 100$ | [Gabrielatos y Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf); $NF$ - frecuencia por millón de palabras |
| Log Ratio | `log_ratio` | $\log_2 \frac{NF_a}{NF_b}$ | [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/); uno significa que la palabra es el doble de frecuente en el corpus objetivo |
| BIC | `bic` | $\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)$ | Wilson (2013); en valor absoluto, por encima de 2 - indicio positivo de diferencia, de 6 - fuerte, de 10 - muy fuerte; un valor negativo con $\lvert G^2 \rvert < \ln N$ significa ausencia de indicio, no la dirección contraria |
| ELL | `ell` | $\frac{G^2}{N \ln \min(E_1, E_2)}$ | Johnston, Berry y Mielke (2006); tamaño del efecto de $G^2$, la proporción de la mayor desviación posible respecto de las frecuencias esperadas, de 0 a 1; `nan` cuando la menor frecuencia esperada es como máximo uno - entonces el logaritmo es cero o negativo; justo por encima de uno la medida crece sin límite |
| Razón de momios | `odds_ratio` | $\frac{a / (c - a)}{b / (d - b)}$ | uno significa momios iguales; `inf` si la palabra ocupa todo el corpus objetivo, 0 - toda la referencia |

Una frecuencia nula en uno de los corpus se sustituye por 0.5 para %DIFF, Log Ratio y la razón de momios (Hardie 2014). El valor p de $G^2$ sale de la distribución ji cuadrado con un grado de libertad (`calc_p_value`). Las medidas están disponibles como las funciones `calc_log_likelihood`, `calc_chi2`, `calc_diff`, `calc_log_ratio`, `calc_bic`, `calc_ell` y `calc_odds_ratio` con los argumentos `(a, b, c, d)` del módulo `anyts.corpus.keyness`; sus nombres y descripciones están en `anyts.constants.KEYNESS_MEASURES`.

## Parámetros

<!-- core: corpus/keyness.md:keyness-parameters 6f31f0b -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `target` | list[str]/dict[str, int] | `-` | Palabras del corpus objetivo o sus frecuencias |
| `reference` | list[str]/dict[str, float]/FrequencyReference | `-` | Palabras del corpus de referencia, sus frecuencias o una referencia por frecuencias |
| `measure` | str | `log_likelihood` | Medida de `anyts.constants.KEYNESS_MEASURES` para `score` y el orden |
| `min_freq` | int | `1` | Frecuencia mínima de una palabra clave en su propio corpus |
| `positive` | bool | `True` | Palabras clave positivas (más frecuentes en el corpus objetivo) o negativas (más frecuentes en la referencia) |
| `top_n` | int | `None` | Número de palabras clave; `None` - todas |

`reference` también puede ser `FreqDict`, frente al cual `target` son formas.

## Referencia por frecuencias

<!-- core: corpus/keyness.md:FrequencyReference 3fc867c -->
`FrequencyReference(counts, size, missing=0.0, key=None, keep=None)` describe un corpus de referencia solo por sus frecuencias, como un diccionario de frecuencias construido a partir de un corpus demasiado grande para pasarlo como palabras:

| Campo | Tipo | Por defecto | Descripción |
| :---: | :--: | :---------: | :---------- |
| `counts` | dict[str, float] | `-` | Frecuencias de las claves en el corpus de referencia |
| `size` | float | `-` | Tamaño del corpus de referencia en palabras |
| `missing` | float | `0.0` | Frecuencia de una clave que falta en `counts` |
| `key` | callable | `None` | Clave de una palabra del corpus objetivo en `counts`, como su lema; `None` - la propia palabra |
| `keep` | callable | `None` | Si una palabra del corpus objetivo se cuenta; `None` - todas las palabras |

Las palabras del objetivo que `keep` deja pasar se cuentan bajo su `key`, y las que deja fuera tampoco cuentan en el tamaño del objetivo; las palabras clave negativas salen solo de las claves de `counts` que `keep` deja pasar. La frecuencia de una clave que falta en `counts` es `missing`: un diccionario da su frecuencia mínima, una cota superior de la real, así que esa palabra puede ser palabra clave positiva pero nunca negativa.

El diccionario de frecuencias `FreqDict` de Google Books Ngram pasado como `reference` se convierte en una referencia así:

| Campo | `FreqDict` |
| :---: | :--------- |
| `counts` | los ipm de `FreqDict.word_ipm`, incluidos los nombres propios, convertidos en apariciones en el corpus del diccionario |
| `size` | `CORPUS_SIZE`, 63 000 millones de palabras de los libros de 1980-2019 |
| `missing` | la frecuencia mínima del diccionario, 0,1 ipm (unas 6300 apariciones) |
| `key` | [`lemma_key`](../datasets/freqdict.md#lemma_key): una palabra clave puede llevar la etiqueta de otro lema, *Roma* se cuenta bajo `romo` |
| `keep` | las formas hechas de las letras de `WORD_PATTERN`; los números y las palabras con guion o con punto quedan fuera |

El corpus objetivo tiene que contarse como se contó el diccionario: formas con las palabras vacías, no lemas - `lemma_key` no es idempotente (`estado` - `estar`), así que `WordsExtractor(use_lexemes=True)` no sirve. El diccionario describe el registro de los libros, así que las palabras clave negativas de un texto son las de la prosa académica (`de`, `social`, `país`).

## Resultado

<!-- core: corpus/keyness.md:Keyword 33ab9a7 -->
Una lista de tuplas con nombre `Keyword` por keyness descendente (los empates por frecuencia descendente y alfabéticamente, las palabras de medida indefinida al final); `pd.DataFrame(keywords)` da una tabla.

| Campo | Tipo | Descripción |
| :---: | :--: | :---------- |
| `word` | str | Palabra |
| `freq_target` | int | Frecuencia en el corpus objetivo |
| `freq_reference` | float | Frecuencia en el corpus de referencia |
| `ipm_target` | float | Frecuencia en el corpus objetivo por millón de palabras |
| `ipm_reference` | float | Frecuencia en el corpus de referencia por millón de palabras |
| `g2` | float | $G^2$ con signo |
| `p_value` | float | Valor p de $G^2$ |
| `log_ratio` | float | Log Ratio |
| `score` | float | Valor de la medida elegida |

## Ejemplo

!!! example "Ejemplo"

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
    # [Keyword(word='gato', freq_target=3, freq_reference=0.0, ipm_target=81081.08108108108,
    #  ipm_reference=0.0, g2=2.79971718756897, p_value=0.09428093556593176,
    #  log_ratio=1.8349407537295037, score=2.79971718756897)]

    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    # [('perro', -5.92), ('comer', -1.97)]
    ```

Frente al [diccionario de frecuencias](../datasets/freqdict.md) las palabras de una comedia de Lope de Vega del [corpus de literatura](../datasets/spanishliterature.md) dan sus personajes:

!!! example "Ejemplo"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness
    from ests.datasets import FreqDict, SpanishLiterature

    text = next(SpanishLiterature().get_texts(author="lope", genre="drama"))
    words = WordsExtractor(lowercase=True).extract(text)
    for k in keyness(words, FreqDict(), top_n=5):
        print(k.word, k.freq_target, round(k.ipm_reference, 2), round(k.g2, 1), round(k.log_ratio, 2))
    # laurencia 135 0.32 2528.7 14.96
    # mengo 105 0.13 2102.5 15.9
    # comendador 154 5.33 2059.9 11.09
    # frondoso 113 3.84 1515.6 11.12
    # barrildo 52 0.1 995.7 15.26
    ```
