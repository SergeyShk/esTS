# Fórmulas de otros idiomas

``` {.python .signature}
UnadaptedReadabilityStats(source, sents_extractor=None, words_extractor=None)
```

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats 0fc386b -->
Fórmulas de legibilidad creadas para el inglés, el alemán o el italiano, calculadas a partir de las estadísticas básicas de un texto con los coeficientes con que se publicaron (Linsear Write en la forma de textstat), sin calibración para su idioma. Sus valores comparan entre sí los textos de un mismo idioma; no son grados escolares de otro idioma. Una palabra sin sílabas (un número, una preposición de una sola consonante) cuenta como monosílaba en FORCAST y en las Wiener Sachtextformeln y como fácil en Linsear Write, como en textstat. La fuente de datos es un texto, un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy) o un objeto `BasicStats` ya calculado, como para `ReadabilityStats`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena, ni un `Doc`, ni un objeto `BasicStats`, unas estadísticas básicas de otra clase, un extractor de otro tipo, una cadena o un `Doc` pasados a una clase sin `basic_stats_class`;
- `SourceError` - una fuente sin palabras o sin oraciones.

La clase extiende el `UnadaptedReadabilityStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/unadapted_readability_stats/) con las [estadísticas básicas](basic_stats.md) de esTS, que cuentan las sílabas y las letras de las palabras españolas y toman por defecto los [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) del español. La tabla de `print_stats` lleva las descripciones inglesas del núcleo, `anyts.constants.UNADAPTED_READABILITY_STATS_DESC`. Una cadena con un carácter sin forma UTF-8 también lanza `SourceError`.

Las fórmulas no están calibradas para el español. Sus valores sirven para comparar textos españoles entre sí y con los resultados de estas fórmulas en otras herramientas, pero no dan un grado español: una palabra española tiene más sílabas que las inglesas con que se ajustaron las fórmulas, así que las fórmulas que cuentan sílabas leen un texto español como más difícil - en 60 ventanas de 1000 palabras de la prosa del [corpus de literatura](../datasets/spanishliterature.md), con 1.96 sílabas por palabra, la mediana de FORCAST es 13.2 y la de Linsear Write 13.7, frente a un [grado de consenso](readability_stats.md#consensus_grade) de 5.0 de las fórmulas españolas. Por eso estas fórmulas no tienen escalas de lectura, `describe` da `None` para ellas y no entran en el grado de consenso. Las fórmulas con coeficientes para el español están en [`ReadabilityStats`](readability_stats.md).

En español las palabras sin sílabas son los números, las abreviaturas sin vocal (`D.`, `Sr.`, `km`) y las interjecciones sin vocal (`pst`, `sh`); las conjunciones `y` y `e`, así como la preposición `a`, tienen una sílaba.

=== "Código"

    ``` python
    from ests import UnadaptedReadabilityStats

    text = (
        "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, "
        "cuándo empezar labores"
    )
    urs = UnadaptedReadabilityStats(text)
    urs.print_stats()
    ```

=== "Resultado"

    ```
               Metric            |  Value
    ----------------------------------------
    FORCAST grade                |  17.00
    Linsear Write grade          |  10.50
    Powers-Sumner-Kearl grade    |   8.37
    McAlpine EFLAW score         |  17.00
    Wiener Sachtextformel 1      |   7.44
    Wiener Sachtextformel 2      |   6.50
    Wiener Sachtextformel 3      |   7.67
    Wiener Sachtextformel 4      |   7.78
    Dickes-Steiwer index         |  30.42
    Gulpease index               |  56.33
    Fucks index                  |  31.00
    Strain index                 |   9.30
    Easy listening formula (ELF) |  16.00
    Wheeler-Smith index          |  120.00
    ```

## Parámetros

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-parameters 2f3854b -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` / `BasicStats` | - | Fuente de datos |
| `sents_extractor` | `SentsExtractor` | `None` | Herramienta de extracción de oraciones, que no se usa con unas estadísticas básicas ya calculadas |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras, que no se usa con unas estadísticas básicas ya calculadas |

## Atributos

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-attributes 569ba31 -->
| Atributo | Tipo | Descripción |
| :-------- | :--- | :---------- |
| `bs` | `BasicStats` | Estadísticas básicas del texto |

Las estadísticas básicas ya calculadas pueden tomarse de un objeto [`ReadabilityStats`](readability_stats.md), para no calcularlas otra vez:

=== "Código"

    ``` python
    from ests import ReadabilityStats

    rs = ReadabilityStats(text)
    urs = UnadaptedReadabilityStats(rs.bs)
    urs.bs is rs.bs, urs.forcast
    ```

=== "Resultado"

    ```
    (True, 17.0)
    ```

## Métricas

<!-- core: stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-metrics 87d03dd -->
Cada métrica es una propiedad del objeto, calculada en cada acceso a partir de `bs`, y `get_stats` las da todas. Una palabra difícil tiene `complex_syl_factor` sílabas o más (3), una palabra larga, `long_word_letter_factor` letras o más (7).

| Métrica | Idioma y lectores | Rango | Un valor mayor indica |
| :------ | :---------------- | :---- | :-------------------- |
| [`forcast`](#forcast) | Textos técnicos en inglés, un grado | 5-20 | Un texto más difícil |
| [`linsear_write`](#linsear_write) | Inglés, un grado | -1 o más | Un texto más difícil |
| [`powers_sumner_kearl`](#powers_sumner_kearl) | Textos de primaria en inglés, un grado | Cualquiera | Un texto más difícil |
| [`eflaw`](#eflaw) | Inglés para estudiantes extranjeros | 1 o más | Un texto más difícil |
| [`wiener_sachtextformel_1`](#wiener_sachtextformel) ... [`wiener_sachtextformel_4`](#wiener_sachtextformel) | Textos de no ficción en alemán, un grado de 4 a 15 | Cualquiera | Un texto más difícil |
| [`dickes_steiwer`](#dickes_steiwer) | Alemán, sin sílabas | Cualquiera | Un texto más fácil |
| [`gulpease`](#gulpease) | Italiano, por letras | 0-100 para la mayoría de los textos | Un texto más fácil |
| [`fucks`](#fucks) | Alemán, sílabas por oración | 0 o más | Un texto más difícil |
| [`strain_index`](#strain_index) | Inglés | 0 o más | Un texto más difícil |
| [`elf`](#elf) | Textos en inglés leídos en voz alta | 0 o más | Un texto más difícil |
| [`wheeler_smith`](#wheeler_smith) | Textos de primaria en inglés | 0 o más | Un texto más difícil |

Aquí ASL es el número medio de palabras por oración y ASW el número medio de sílabas por palabra. Las funciones de las fórmulas se importan de `ests.unadapted_readability_stats` y calculan un valor a partir de recuentos:

=== "Código"

    ``` python
    from ests.unadapted_readability_stats import calc_forcast, calc_gulpease

    calc_forcast(n_monosyllable_words=30, n_words=150)
    calc_gulpease(n_letters=550, n_words=100, n_sents=8)
    ```

=== "Resultado"

    ```
    17.0
    58.0
    ```

<div class="metric-card" markdown>

### FORCAST { #forcast }

`forcast` · Caylor et al., 1973
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_forcast f1c7568 -->
``` {.python .signature}
calc_forcast(n_monosyllable_words, n_words)
```

El grado de Caylor et al. (1973) para textos técnicos: 20 menos la décima parte de las palabras monosílabas por cada 150 palabras, de 5 (todas las palabras monosílabas) a 20; `nan` sin palabras.

$$
\textrm{FORCAST} = 20 - \frac{150 \times \textrm{Palabras monosílabas}}{10 \times \textrm{Palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_monosyllable_words` | `int` | - | Número de palabras monosílabas |
| `n_words` | `int` | - | Número de palabras |

Un recuento que no es un entero no negativo y más palabras monosílabas que palabras lanzan `ParameterError`.

</div>

<div class="metric-card" markdown>

### Linsear Write { #linsear_write }

`linsear_write`
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_linsear_write fe19083 -->
``` {.python .signature}
calc_linsear_write(n_easy_words, n_hard_words, n_sents)
```

El grado de Linsear Write en la forma de textstat; la Lensear Write Formula de O'Hayre (1966) es otra fórmula, de las palabras monosílabas y las oraciones de una muestra de 100 palabras. Una palabra fácil, de dos sílabas como mucho, pesa 1 y una difícil 3; su suma por oración $r$ se divide entre 2 por encima de 20 y, en otro caso, pierde 2 antes de dividirse entre 2. Se calcula sobre todo el texto en lugar de una muestra de 100 palabras; `nan` sin oraciones.

$$
r = \frac{\textrm{Palabras fáciles} + 3 \times \textrm{Palabras difíciles}}{\textrm{Oraciones}}, \quad \textrm{LW} = \begin{cases} r / 2 & r > 20 \\ (r - 2) / 2 & r \le 20 \end{cases}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_easy_words` | `int` | - | Número de palabras de una o dos sílabas |
| `n_hard_words` | `int` | - | Número de palabras de tres o más sílabas |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Grado de Powers-Sumner-Kearl { #powers_sumner_kearl }

`powers_sumner_kearl` · [Powers et al., 1958](https://doi.org/10.1037/h0043254)
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_powers_sumner_kearl 700718e -->
``` {.python .signature}
calc_powers_sumner_kearl(n_syllables, n_words, n_sents)
```

El nuevo cálculo de la fórmula de Flesch de Powers, Sumner y Kearl (1958) como grado, para textos de primaria; `nan` sin palabras o sin oraciones.

$$
\textrm{PSK} = 0.0778 \times \textrm{ASL} + 4.55 \times \textrm{ASW} - 2.2029
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### EFLAW de McAlpine { #eflaw }

`eflaw` · McAlpine, 2005
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_eflaw d9e0be5 -->
``` {.python .signature}
calc_eflaw(n_mini_words, n_words, n_sents)
```

La puntuación de McAlpine (2005) para los lectores del inglés como lengua extranjera: las palabras y las minipalabras, de una a tres letras (`mini_word_letters`), por oración; 20 o menos es muy fácil, 30 o más, confuso. `nan` sin oraciones.

$$
\textrm{EFLAW} = \frac{\textrm{Palabras} + \textrm{Minipalabras}}{\textrm{Oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_mini_words` | `int` | - | Número de palabras de una a tres letras |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Wiener Sachtextformel { #wiener_sachtextformel }

`wiener_sachtextformel_1` · `wiener_sachtextformel_2` · `wiener_sachtextformel_3` · `wiener_sachtextformel_4` · Bamberger y Vanecek, 1984
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_wiener_sachtextformel a66d708 -->
``` {.python .signature}
calc_wiener_sachtextformel(n_complex, n_long_words, n_monosyllable_words, n_words, n_sents, variant=1)
```

Las cuatro fórmulas de Bamberger y Vanecek (1984) para textos de no ficción en alemán, un grado de 4 a 15, según los porcentajes de palabras de tres o más sílabas (MS), de más de seis letras (IW) y de una sílaba (ES) y la longitud media de la oración (SL); `nan` sin palabras o sin oraciones. Una variante que no es un entero de 1 a 4 lanza `ParameterError`.

$$
\begin{aligned} \textrm{WSTF}_1 &= 0.1935 \cdot \textrm{MS} + 0.1672 \cdot \textrm{SL} + 0.1297 \cdot \textrm{IW} - 0.0327 \cdot \textrm{ES} - 0.875 \\ \textrm{WSTF}_2 &= 0.2007 \cdot \textrm{MS} + 0.1682 \cdot \textrm{SL} + 0.1373 \cdot \textrm{IW} - 2.779 \\ \textrm{WSTF}_3 &= 0.2963 \cdot \textrm{MS} + 0.1905 \cdot \textrm{SL} - 1.1144 \\ \textrm{WSTF}_4 &= 0.2744 \cdot \textrm{MS} + 0.2656 \cdot \textrm{SL} - 1.693 \end{aligned}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Número de palabras de tres o más sílabas |
| `n_long_words` | `int` | - | Número de palabras de más de seis letras |
| `n_monosyllable_words` | `int` | - | Número de palabras monosílabas |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |
| `variant` | `int` | `1` | Variante de la fórmula, de 1 a 4 |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice de Dickes-Steiwer { #dickes_steiwer }

`dickes_steiwer` · Dickes y Steiwer, 1977
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_dickes_steiwer 0fea097 -->
``` {.python .signature}
calc_dickes_steiwer(n_letters, n_words, n_sents, n_types)
```

La fórmula corta de Dickes y Steiwer (1977) para el alemán, tal como la dan Bamberger y Vanecek (1984), según las letras por palabra, las palabras por oración y la proporción de lexemas entre las palabras (TTR), sin sílabas; un valor mayor indica un texto más fácil. `nan` sin palabras o sin oraciones.

$$
\textrm{DS} = 235.95993 - 73.021 \ln\left(\frac{\textrm{Letras}}{\textrm{Palabras}} + 1\right) - 12.56438 \ln\left(\frac{\textrm{Palabras}}{\textrm{Oraciones}} + 1\right) - 50.03293 \cdot \textrm{TTR}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Número de letras de las palabras |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |
| `n_types` | `int` | - | Número de palabras distintas |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice Gulpease { #gulpease }

`gulpease` · Lucisano y Piemontese, 1988
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_gulpease 837f4d6 -->
``` {.python .signature}
calc_gulpease(n_letters, n_words, n_sents)
```

El índice de Lucisano y Piemontese (1988) para el italiano, por letras en lugar de sílabas: cerca de 0 para los textos más difíciles y de 100 para los más fáciles, más allá de esos valores para los textos extremos; por debajo de 80 un texto es difícil para un lector de primaria, por debajo de 40 para un lector con estudios secundarios. `nan` sin palabras.

$$
\textrm{Gulpease} = 89 + \frac{300 \times \textrm{Oraciones} - 10 \times \textrm{Letras}}{\textrm{Palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Número de letras de las palabras |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice de Fucks { #fucks }

`fucks` · Fucks, 1955
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_fucks 17d3ed9 -->
``` {.python .signature}
calc_fucks(n_syllables, n_sents)
```

La característica de estilo de Fucks (1955): la longitud media de la palabra en sílabas por la longitud media de la oración en palabras, es decir, las sílabas por oración; `nan` sin oraciones.

$$
\textrm{Fucks} = \textrm{ASW} \times \textrm{ASL} = \frac{\textrm{Sílabas}}{\textrm{Oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice Strain { #strain_index }

`strain_index` · Nathaniel, 2009
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_strain_index d371c89 -->
``` {.python .signature}
calc_strain_index(n_syllables, n_sents)
```

El índice de Nathaniel (2009): las sílabas de tres oraciones divididas entre 10, aquí las de tres oraciones de media en todo el texto; `nan` sin oraciones.

$$
\textrm{Strain} = \frac{3 \times \textrm{Sílabas}}{10 \times \textrm{Oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Fórmula de escucha fácil { #elf }

`elf` · [Fang, 1966](https://doi.org/10.1080/08838156609363529)
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_elf 59941bf -->
``` {.python .signature}
calc_elf(n_syllables, n_syllabic_words, n_sents)
```

La fórmula de Fang (1966) para textos leídos en voz alta: las sílabas que pasan de una por palabra, por oración, sin que una palabra sin sílabas (un número) añada ninguna; 12 o menos es fácil de escuchar. `nan` sin oraciones.

$$
\textrm{ELF} = \frac{\textrm{Sílabas} - \textrm{Palabras de una o más sílabas}}{\textrm{Oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_syllabic_words` | `int` | - | Número de palabras de una o más sílabas |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

<div class="metric-card" markdown>

### Índice de Wheeler-Smith { #wheeler_smith }

`wheeler_smith` · Wheeler y Smith, 1954
{ .metric-meta }

<!-- core: stats/unadapted_readability_stats.md:calc_wheeler_smith de9b424 -->
``` {.python .signature}
calc_wheeler_smith(n_polysyllable_words, n_sents)
```

El índice de Wheeler y Smith (1954) para textos de primaria: la longitud media de la oración por la proporción de palabras de dos o más sílabas, por 10, es decir, 10 veces esas palabras por oración; cuenta oraciones donde el original cuenta unidades terminadas por cualquier signo final. `nan` sin oraciones.

$$
\textrm{WS} = 10 \times \textrm{ASL} \times \frac{\textrm{Palabras de dos o más sílabas}}{\textrm{Palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_polysyllable_words` | `int` | - | Número de palabras de dos o más sílabas |
| `n_sents` | `int` | - | Número de oraciones |

Un recuento que no es un entero no negativo lanza `ParameterError`.

</div>

## Métodos

Los métodos `get_stats`, `to_dataframe`, `print_stats` y `describe` son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las fórmulas no tienen escalas, y `describe` da `None` para cualquiera de ellas.

=== "Código"

    ``` python
    urs = UnadaptedReadabilityStats(text)
    urs.describe("forcast"), urs.describe("gulpease")
    urs.get_stats()
    ```

=== "Resultado"

    ```
    (None, None)
    {'forcast': 17.0,
     'linsear_write': 10.5,
     'powers_sumner_kearl': 8.367433333333333,
     'eflaw': 17.0,
     'wiener_sachtextformel_1': 7.443000000000001,
     'wiener_sachtextformel_2': 6.504,
     'wiener_sachtextformel_3': 7.6691,
     'wiener_sachtextformel_4': 7.779,
     'dickes_steiwer': 30.42186181527815,
     'gulpease': 56.333333333333336,
     'fucks': 31.0,
     'strain_index': 9.3,
     'elf': 16.0,
     'wheeler_smith': 120.0}
    ```
