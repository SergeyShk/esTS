# Dispersión de las palabras

!!! info ""
    **ests.corpus.dispersion()**, **ests.corpus.Dispersion**

## Descripción

La dispersión de una palabra es lo uniformemente que se reparte por las partes de un texto o de un corpus. La frecuencia no distingue una palabra que aparece una vez en cada capítulo de otra reunida en uno solo; las medidas de dispersión ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) completan la frecuencia y sirven para elegir el vocabulario de diccionarios y de listas de palabras para estudiantes.

El texto se divide en partes: `parts` es el número de partes de tamaño aproximadamente igual o los tamaños de las partes en orden (oraciones, párrafos, capítulos, documentos de un corpus), que suman el número de palabras. Para cada palabra se calculan sus frecuencias por parte y seis medidas; Gries recomienda DP como la principal.

Las palabras se comparan tal cual: la caja y la lematización corresponden a [`WordsExtractor`](../extractors/words.md).

## Medidas

Para $n$ partes de proporciones $s_i$ del texto, frecuencias de la palabra por parte $v_i$ y una frecuencia total $f = \sum v_i$; $p_i = v_i / n_i$ es la frecuencia relativa en una parte de tamaño $n_i$:

| Medida | Campo | Fórmula | Valores |
| :----- | :---- | :------ | :------ |
| Desviación de proporciones DP | `dp` | $\frac{1}{2} \sum \left\lvert \frac{v_i}{f} - s_i \right\rvert$ | 0 - en proporción a los tamaños de las partes, tiende a 1 - en una parte; Gries (2008) |
| DP normalizada | `dp_norm` | $\frac{DP}{1 - \min s_i}$ | el máximo es uno sea cual sea la división; Lijffijt y Gries (2012) |
| D de Juilland | `juilland_d` | $1 - \frac{V}{\sqrt{n - 1}}$, $V = \frac{\sigma(p)}{\mu(p)}$ | 1 - uniforme, 0 - en una parte; Juilland y Chang-Rodríguez (1964) |
| D2 de Carroll | `carroll_d2` | $\frac{H(p)}{\log_2 n}$ | entropía de la distribución $p_i$; 1 - uniforme, 0 - en una parte; Carroll (1970) |
| S de Rosengren | `rosengren_s` | $\frac{(\sum \sqrt{s_i v_i})^2}{f}$ | 1 - en proporción, tiende a $1/n$ cuando se reúne en una de partes iguales; Rosengren (1971) |
| Divergencia de Kullback-Leibler | `kl_divergence` | $\sum \frac{v_i}{f} \log_2 \frac{v_i / f}{s_i}$ | en bits; 0 - en proporción, crece cuando se reúne en partes pequeñas; Gries (2020) |

Las medidas están disponibles como las funciones `calc_dp`, `calc_dp_norm`, `calc_juilland_d`, `calc_carroll_d2`, `calc_rosengren_s`, `calc_kl_divergence` con los argumentos `(frequencies, sizes)` - las frecuencias de la palabra por parte y los tamaños de las partes - del módulo `ests.corpus.dispersion` (`from ests.corpus.dispersion import calc_dp`); sus nombres están en `ests.constants.DISPERSION_STATS_DESC`. Para una palabra de frecuencia nula todas las medidas son `nan`. La función `dispersion` calcula las mismas medidas para todas las palabras a la vez sobre las celdas no nulas de la matriz palabra × parte, así que la memoria es lineal en el número de palabras y una división por oraciones cuesta poco.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `words` | list[str] | `-` | Palabras del texto en orden |
| `parts` | int/list[int] | `10` | Número de partes (de 2 al número de palabras) o tamaños de las partes |
| `word` | str | `None` | Palabra cuya dispersión se busca; `None` - todas las palabras |
| `min_freq` | int | `1` | Frecuencia mínima de una palabra |

## Resultado

Una lista de tuplas con nombre `Dispersion` por frecuencia descendente: `word`, `freq` y las seis medidas de la tabla; `pd.DataFrame(result)` da una tabla.

## Ejemplo

!!! example "Ejemplo"

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
    # [11, 12, 14]

    dispersion(words, parts=sizes, word="gato")
    # [Dispersion(word='gato', freq=3, dp=0.04504504504504503, dp_norm=0.06410256410256408,
    #  juilland_d=0.9307654905484509, carroll_d2=0.9955884389001025,
    #  rosengren_s=0.9974825285744621, kl_divergence=0.007241184435774255)]

    # Tres partes iguales: a y pájaro se reúnen en los extremos del texto
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    # [('el', 0.1), ('gato', 0.02), ('en', 0.02), ('ventana', 0.02), ('y', 0.02), ('a', 0.34), ('pájaro', 0.32)]
    ```
