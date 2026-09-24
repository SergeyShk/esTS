# Palabras clave

!!! info ""
    **ests.corpus.keyness()**, **ests.corpus.Keyword**

## Descripción

Extracción de palabras clave (keyness) de un corpus objetivo frente a uno de referencia: las palabras que aparecen significativamente más a menudo en el corpus objetivo que en el de referencia. Una herramienta clásica de la lingüística de corpus para comparar géneros, autores, traducciones y épocas ([AntConc](https://www.laurenceanthony.net/software/antconc/), [Sketch Engine](https://www.sketchengine.eu/), quanteda `textstat_keyness`).

Para cada palabra se calculan dos valores que [Gabrielatos y Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) y [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recomiendan leer juntos: la razón de verosimilitud $G^2$ con su valor p (la significación de la diferencia: si la hay) y Log Ratio (el tamaño del efecto: cuán grande es). Se calcula además la medida elegida `score`, que sirve para ordenar. Las medidas de significación ($G^2$, ji cuadrado, BIC, ELL) llevan signo: negativo cuando la palabra es más frecuente en la referencia; las medidas de efecto (%DIFF, Log Ratio, razón de momios) tienen dirección por construcción.

La referencia puede ser una lista de palabras o una correspondencia de frecuencias, con el tamaño de la referencia tomado como la suma de los recuentos, o el [diccionario de frecuencias](../datasets/freqdict.md) `FreqDict` de Google Books Ngram. Frente al diccionario el corpus objetivo tiene que contarse como se contó el diccionario: formas, no lemas - [`lemma_key`](../datasets/freqdict.md#lemma_key) no es idempotente, así que un lema puede seguir moviéndose (`estado` - `estar`) y `WordsExtractor(use_lexemes=True)` no sirve -, con las palabras vacías, ya que el tamaño del corpus del diccionario las conserva. Las formas que no están hechas de las letras de `WORD_PATTERN` - números, palabras con guion o con punto - quedan fuera del objetivo y de su tamaño, ya que el diccionario no tiene ninguna. Una forma va a su clave por `lemma_key`, y las filas de los nombres propios del diccionario, que conservan sus formas, van también a `lemma_key` de las formas (`FreqDict.word_ipm`), así que los dos lados cuentan las mismas formas bajo una clave: las apariciones de *Roma* en los libros se cuentan bajo la clave `romo` a la que llega la palabra `Roma`, y la etiqueta de otro lema (`romo`, `parir`) es todo lo que queda de la falta de categorías gramaticales. La frecuencia de una clave en la referencia es su ipm por el tamaño del corpus del diccionario (`CORPUS_SIZE`, 63 000 millones de palabras de los libros de 1980-2019). Una palabra fuera del diccionario recibe su frecuencia mínima, 0,1 ipm (unas 6300 apariciones): el diccionario deja fuera las palabras más raras, así que su frecuencia real queda algo por debajo, y un cero pondría todas las palabras fuera del diccionario antes de las verdaderas palabras clave. El diccionario describe el registro de los libros, así que las palabras clave negativas de un texto son las de la prosa académica (`de`, `social`, `país`).

Frente a una lista o una correspondencia, las palabras se comparan tal cual: la caja, la lematización y las palabras vacías corresponden a [`WordsExtractor`](../extractors/words.md), y los dos corpus tienen que extraerse del mismo modo.

## Medidas

Para una palabra de frecuencia $a$ en un corpus objetivo de tamaño $c$ y de frecuencia $b$ en un corpus de referencia de tamaño $d$, $N = c + d$:

| Medida | Clave | Fórmula | Descripción |
| :----- | :---- | :------ | :---------- |
| Razón de verosimilitud | `log_likelihood` | $G^2 = 2\,(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2})$, $E_1 = \frac{c\,(a+b)}{N}$, $E_2 = \frac{d\,(a+b)}{N}$ | [Rayson y Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html); valores críticos `G2_CRITICAL_VALUES`: 3.84 para p < 0.05, 6.63 para p < 0.01, 10.83 para p < 0.001, 15.13 para p < 0.0001 |
| Ji cuadrado | `chi2` | $\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}$ | con la corrección de Yates sobre la tabla de contingencia 2×2; si la corrección supera la diferencia, el estadístico es cero |
| %DIFF | `diff` | $\frac{NF_a - NF_b}{NF_b} \cdot 100$ | [Gabrielatos y Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf); $NF$ - frecuencia por millón de palabras |
| Log Ratio | `log_ratio` | $\log_2 \frac{NF_a}{NF_b}$ | [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/); uno significa que la palabra es el doble de frecuente en el corpus objetivo |
| BIC | `bic` | $\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)$ | Wilson (2013); en valor absoluto, por encima de 2 - indicio positivo de diferencia, de 6 - fuerte, de 10 - muy fuerte; un valor negativo con $\lvert G^2 \rvert < \ln N$ significa ausencia de indicio, no la dirección contraria |
| ELL | `ell` | $\frac{G^2}{N \ln \min(E_1, E_2)}$ | Johnson, Culpeper y Rayson (2007); tamaño del efecto de $G^2$ de 0 a 1, `nan` cuando la menor frecuencia esperada es inferior a $e$ - entonces $\ln \min(E_1, E_2) < 1$ y la medida supera uno |
| Razón de momios | `odds_ratio` | $\frac{a / (c - a)}{b / (d - b)}$ | uno significa momios iguales; `inf` si la palabra ocupa todo el corpus objetivo, 0 - toda la referencia |

Una frecuencia nula en uno de los corpus se sustituye por 0.5 para %DIFF, Log Ratio y la razón de momios (Hardie 2014). El valor p de $G^2$ sale de la distribución ji cuadrado con un grado de libertad (`calc_p_value`). Las medidas están disponibles como las funciones `calc_log_likelihood`, `calc_chi2`, `calc_diff`, `calc_log_ratio`, `calc_bic`, `calc_ell`, `calc_odds_ratio` con los argumentos `(a, b, c, d)` del módulo `ests.corpus.keyness` (`from ests.corpus.keyness import calc_log_likelihood`); sus nombres y descripciones están en `ests.constants.KEYNESS_MEASURES`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `target` | list[str]/dict[str, int] | `-` | Palabras del corpus objetivo o sus frecuencias; formas frente al diccionario de frecuencias |
| `reference` | list[str]/dict[str, float]/FreqDict | `-` | Palabras del corpus de referencia, sus frecuencias o el diccionario de frecuencias |
| `measure` | str | `log_likelihood` | Medida de `KEYNESS_MEASURES` para `score` y el orden |
| `min_freq` | int | `1` | Frecuencia mínima de una palabra clave en su propio corpus |
| `positive` | bool | `True` | Palabras clave positivas (más frecuentes en el corpus objetivo) o negativas (más frecuentes en la referencia) |
| `top_n` | int | `None` | Número de palabras clave; `None` - todas |

## Resultado

Una lista de tuplas con nombre `Keyword` por orden descendente de clave (los empates por frecuencia descendente y alfabéticamente, las palabras de medida indefinida al final); `pd.DataFrame(keywords)` da una tabla.

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
    # [Keyword(word='gato', freq_target=3, freq_reference=0, ipm_target=81081.08108108108,
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
