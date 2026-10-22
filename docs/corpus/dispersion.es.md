# Dispersión de las palabras

!!! info ""
    **ests.corpus.dispersion()**, **ests.corpus.Dispersion**

## Descripción

<!-- core: corpus/dispersion.md:dispersion f0bdceb -->
``` {.python .signature}
dispersion(words, parts=10, word=None, min_freq=1)
```

La dispersión de una palabra es lo uniformemente que se reparte por las partes de un texto o de un corpus. La frecuencia no distingue una palabra que aparece una vez en cada capítulo de otra reunida en un solo capítulo; las medidas de dispersión ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) la complementan.

`parts` es el número de partes de tamaño aproximadamente igual o los tamaños de las partes en orden (oraciones, párrafos, capítulos, documentos de un corpus), que suman el número de palabras. Se calculan seis medidas a partir de las frecuencias de cada palabra por parte; Gries recomienda DP como la principal.

Las palabras se comparan tal cual: las mayúsculas y minúsculas y la lematización corresponden al extractor de palabras.

El módulo `ests.corpus.dispersion` reexporta la función y las medidas del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/dispersion/) (`from ests.corpus.dispersion import calc_dp`). Las palabras se extraen con [`WordsExtractor`](../extractors/words.md).

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
