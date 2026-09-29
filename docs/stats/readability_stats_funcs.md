# Metric functions

## Flesch reading ease { #calc_flesch_reading_easy }

!!! info ""
    **ests.readability_stats.calc_flesch_reading_easy()**

--8<-- "stats/readability_stats_funcs.md:calc_flesch_reading_easy"

The default coefficients of esTS are those of the *fórmula de perspicuidad* of Szigriszt-Pazos (1993), read on the INFLESZ scale of Barrio-Cantalejo et al. (2008):

| Value | Level | Text type |
| :---: | :---: | :-------- |
| `80-100` | muy fácil | comics, children's books |
| `65-80` | bastante fácil | primary school textbooks |
| `55-65` | normal | general press |
| `40-55` | algo difícil | secondary school textbooks |
| `0-40` | muy difícil | scientific and technical texts |

The coefficients of Fernández Huerta (1959) are available through the `classic` [preset](readability_stats.md#presets), with the correction of Law (2011): the last term takes the mean sentence length.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `1.0` | Coefficient a, at the mean sentence length |
| `b` | float | `62.3` | Coefficient b, at the mean word length in syllables |
| `c` | float | `206.835` | Coefficient c, the constant |

Sources: Szigriszt Pazos, F. *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad*. Universidad Complutense de Madrid, 1993. Barrio-Cantalejo, I. M. et al. Validación de la Escala INFLESZ para evaluar la legibilidad de los textos dirigidos a pacientes. *Anales del Sistema Sanitario de Navarra*, 31(2), 2008. Fernández Huerta, J. Medidas sencillas de lecturabilidad. *Consigna*, 214, 1959. Law, G. Error in the Fernández Huerta readability formula. *LINGUIST List* 22.2332, 2011.

## Gutiérrez de Polini comprehensibility { #calc_gutierrez_polini_index }

!!! info ""
    **ests.readability_stats.calc_gutierrez_polini_index()**

Computation of the *fórmula de comprensibilidad* of Gutiérrez de Polini (1972). The higher the value, the easier the text. It was fitted on sixth-grade school texts and has no scale of its own: ordinary prose lies between 30 and 50, and a text above 70 is read by a young child.

Formula:

$$
95.2-9.7\times\frac{\textrm{Number of letters}}{\textrm{Number of words}}-0.35\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_letters` | int | `-` | Number of letters |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |

Source: Gutiérrez de Polini, L. E. *Investigación sobre lectura en Venezuela*. Ministerio de Educación, Caracas, 1972.

## Crawford grade { #calc_crawford_grade }

!!! info ""
    **ests.readability_stats.calc_crawford_grade()**

Computation of the Crawford formula (1989): the years of schooling needed to read the text, fitted on Spanish primary school readers of grades 1-6, so higher values saturate. The higher the value, the harder the text.

Formula:

$$
-0.205\times\frac{100\times\textrm{Number of sentences}}{\textrm{Number of words}}+0.049\times\frac{100\times\textrm{Number of syllables}}{\textrm{Number of words}}-3.407
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_syllables` | int | `-` | Number of syllables |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |

Source: Crawford, A. N. Fórmula y gráfico para determinar la comprensibilidad de textos del nivel primario en castellano. *Lectura y Vida*, 10(4), 1989.

## Legibilidad µ { #calc_mu_index }

!!! info ""
    **ests.readability_stats.calc_mu_index()**

--8<-- "stats/readability_stats_funcs.md:calc_mu_index"

The variance divided by `n − 1` is the *cuasivarianza* of the authors, which reproduces the worked example of their manual; the distribution is `BasicStats.c_letters`. The bands of the authors:

| Value | Level |
| :---: | :---: |
| `91-100` | muy fácil |
| `81-90` | fácil |
| `71-80` | un poco fácil |
| `61-70` | adecuado |
| `51-60` | un poco difícil |
| `31-50` | difícil |
| `0-30` | muy difícil |

Source: Muñoz Baquedano, M. Legibilidad y variabilidad de los textos. *Boletín de Investigación Educacional*, 21(2), 2006; the program and manual at [legibilidadmu.cl](https://www.legibilidadmu.cl/).

## SMOG index { #calc_smog_index }

!!! info ""
    **ests.readability_stats.calc_smog_index()**

--8<-- "stats/readability_stats_funcs.md:calc_smog_index"

Fitted on English; for Spanish it is the input of the [SOL formula](#calc_sol_grade), and `ReadabilityStats` passes the words of three or more syllables.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of polysyllabic words |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `1.043` | Coefficient a, at the square root |
| `b` | float | `30` | Coefficient b, the number of sentences of the sample |
| `c` | float | `3.1291` | Coefficient c, the constant |

## SOL grade { #calc_sol_grade }

!!! info ""
    **ests.readability_stats.calc_sol_grade()**

Computation of the SOL grade of Contreras et al. (1999), the conversion `E = −2.51 + 0.74·S`, where `S` is the SMOG index of the Spanish text and `E` the grade of the English scale, the years of schooling. The higher the value, the harder the text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of words of three or more syllables |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `0.74` | Coefficient a, at the SMOG index |
| `b` | float | `-2.51` | Coefficient b, the constant |

Source: Contreras, A., García-Alonso, R., Echenique, M., Daye-Contreras, F. The SOL formulas for converting SMOG readability scores between health education materials written in Spanish, English, and French. *Journal of Health Communication*, 4(1), 1999.

## LIX readability index { #calc_lix }

!!! info ""
    **ests.readability_stats.calc_lix()**

--8<-- "stats/readability_stats_funcs.md:calc_lix"

## RIX readability index { #calc_rix }

!!! info ""
    **ests.readability_stats.calc_rix()**

--8<-- "stats/readability_stats_funcs.md:calc_rix"

## Reading ease level { #flesch_reading_easy_to_level }

!!! info ""
    **ests.readability_stats.flesch_reading_easy_to_level()**

The band of a scale for the Flesch reading ease. The scales of `ests.constants.READING_EASE_SCALES`: `inflesz` (Barrio-Cantalejo et al., 2008, five bands for the Szigriszt-Pazos coefficients), `szigriszt` (Szigriszt-Pazos, 1993, integer bands: `muy difícil` 0-15, `árido` 16-35, `bastante difícil` 36-50, `normal` 51-65, `bastante fácil` 66-75, `fácil` 76-85, `muy fácil` 86-100) and `fernandez_huerta` (Fernández Huerta, 1959: `muy difícil` below 30, `difícil` 30-50, `bastante difícil` 50-60, `normal` 60-70, `bastante fácil` 70-80, `fácil` 80-90, `muy fácil` above 90).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Value of the reading ease |
| `scale` | str | `inflesz` | Name of the scale; `ReadabilityStats.describe_level` passes the scale of the preset |

!!! example "Example"

    ``` python
    from ests.readability_stats import flesch_reading_easy_to_level

    flesch_reading_easy_to_level(53.5), flesch_reading_easy_to_level(53.5, "szigriszt")
    # ('algo difícil', 'normal')
    ```

## µ level { #mu_to_level }

!!! info ""
    **ests.readability_stats.mu_to_level()**

The band of the µ scale of Muñoz Baquedano and Muñoz Urra (2006) for Legibilidad µ; an undefined index (`nan`) has no band and gives an empty string.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `mu_index` | float | `-` | Value of Legibilidad µ |

## Reading ease to grade { #flesch_reading_easy_to_grade }

!!! info ""
    **ests.readability_stats.flesch_reading_easy_to_grade()**

Conversion of the Flesch reading ease into years of schooling for the consensus grade. The thresholds belong to the scale of the preset.

With the `general` preset, through the text types of the INFLESZ bands and the school stages of Spain:

| Value | Grade | Text type |
| :---: | :---: | :-------- |
| `80-100` | 3 | comics and children's books, primary school grades 1-3 |
| `65-80` | 5 | primary school textbooks, grades 4-6 |
| `55-65` | 8 | general press, ESO |
| `40-55` | 11 | secondary school textbooks, bachillerato |
| `below 40` | 13 | scientific texts, university |

With the `classic` preset, through the interpretation table of Flesch kept by Fernández Huerta: `90-100` - 5, `80-90` - 6, `70-80` - 7, `60-70` - 8.5, `50-60` - 10, `40-50` - 11, `30-40` - 12, below `30` - 13.

Values above 100 belong to the first grade of the scale.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Value of the reading ease |
| `preset` | str | `general` | Coefficient preset whose scale is read |

## Consensus grade { #calc_consensus_grade }

!!! info ""
    **ests.readability_stats.calc_consensus_grade()**

Computation of the consensus grade: the median of the values of the grade formulas, each rounded half up. The reading ease is converted with `flesch_reading_easy_to_grade` by the scale of the preset and added without rounding. No values at all, a grade that is not a finite number and an unknown preset raise `ParameterError`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grades` | list[float] | `-` | Values of the grade formulas |
| `flesch_reading_easy` | float | `None` | Value of the reading ease |
| `preset` | str | `general` | Coefficient preset of the reading ease |

!!! example "Example"

    ``` python
    from ests.readability_stats import calc_consensus_grade

    calc_consensus_grade([5.813, 9.258], 53.545)
    # 9.0
    ```

## Grade to age { #grade_to_age }

!!! info ""
    **ests.readability_stats.grade_to_age()**

The school stage of the Spanish school system and reader age by the value of a grade formula (see the [interpretation](readability_stats.md#interpretation) table). The value is rounded half up, values below 1 belong to grades 1-3; a grade that is not a finite number raises `ParameterError`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grade` | float | `-` | Value of a grade formula |

!!! example "Example"

    ``` python
    from ests.readability_stats import grade_to_age

    grade_to_age(9.0)
    # 'ESO (12-16 years)'
    ```

## Reading time { #calc_reading_time }

!!! info ""
    **ests.readability_stats.calc_reading_time()**

--8<-- "stats/readability_stats_funcs.md:calc_reading_time"

The default speed is the silent reading speed of adults in Spanish, 278 words per minute, from the meta-analysis of Brysbaert (2019). The norms of school years from the meta-analysis of Ripoll, Tapia and Aguado (2020) are available in `ests.constants.READING_SPEED_NORMS` as pairs (aloud, silent):

| Norm | Aloud | Silent |
| :--: | :---: | :----: |
| `grade_1` | 49 | 30 |
| `grade_2` | 73 | 79 |
| `grade_3` | 85 | 95 |
| `grade_4` | 104 | 125 |
| `grade_5` | 114 | 137 |
| `grade_6` | 124 | 155 |
| `grade_7` | 134 | 180 |
| `grade_8` | 136 | 176 |
| `grade_9` | 143 | 180 |
| `grade_10` | 164 | 200 |
| `grade_11` | 161 | 186 |
| `adult` | 191 | 278 |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_words` | int | `-` | Number of words |
| `wpm` | float | `278` | Reading speed, words per minute |

Sources: Brysbaert, M. How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 2019. Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado hispanohablante: un metaanálisis. *Revista de Psicodidáctica*, 25(2), 2020.
