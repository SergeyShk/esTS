# Metric functions

## Flesch reading ease { #calc_flesch_reading_easy }

!!! info ""
    **ests.readability_stats.calc_flesch_reading_easy()**

Computation of the Flesch reading ease with Spanish coefficients. The higher the value, the easier the text is to read; the scale runs from 0 to 100.

The default coefficients are those of the *fórmula de perspicuidad* of Szigriszt-Pazos (1993), which Barrio-Cantalejo et al. (2008) validated on texts for patients and provided with the INFLESZ scale:

| Value | Level | Text type |
| :---: | :---: | :-------- |
| `80-100` | muy fácil | comics, children's books |
| `65-80` | bastante fácil | primary school textbooks |
| `55-65` | normal | general press |
| `40-55` | algo difícil | secondary school textbooks |
| `0-40` | muy difícil | scientific and technical texts |

The coefficients of Fernández Huerta (1959) are available through the `classic` [preset](readability_stats.md#presets). He printed the last term as `1.02` times the number of sentences per 100 words; Law (2011) showed that this inverts the fraction of the Flesch formula the adaptation was based on, so the mean sentence length is used, as in koRpus and textstat.

Formula:

$$
c-a\times\frac{\textrm{Number of words}}{\textrm{Number of sentences}}-b\times\frac{\textrm{Number of syllables}}{\textrm{Number of words}}
$$

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

Computation of the *fórmula de comprensibilidad* of Gutiérrez de Polini (1972), the first formula written for Spanish rather than adapted from English. The higher the value, the easier the text. It was fitted on school texts for the sixth grade and has no scale of its own: the values of ordinary prose lie between 30 and 50, and a text above 70 is read by a young child.

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

Computation of Legibilidad µ of Muñoz Baquedano and Muñoz Urra (2006), which measures the variability of word length: the mean and the variance of the number of letters per word. The variance is the population one, which the factor `n / (n − 1)` corrects, as the authors explain. Words without letters (numbers) are left out; with fewer than two words or without variability the index is undefined (`nan`). The higher the value, the easier the text:

| Value | Level |
| :---: | :---: |
| `91-100` | muy fácil |
| `81-90` | fácil |
| `71-80` | un poco fácil |
| `61-70` | adecuado |
| `51-60` | un poco difícil |
| `31-50` | difícil |
| `0-30` | muy difícil |

Formula:

$$
\frac{n}{n-1}\times\frac{\bar{x}}{\sigma^2}\times100
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `c_letters` | dict[int, int] | `-` | Distribution of words by number of letters (`BasicStats.c_letters`) |

Source: Muñoz Baquedano, M. Legibilidad y variabilidad de los textos. *Boletín de Investigación Educacional*, 21(2), 2006; the program and manual at [legibilidadmu.cl](https://www.legibilidadmu.cl/).

## SMOG index { #calc_smog_index }

!!! info ""
    **ests.readability_stats.calc_smog_index()**

Computation of the SMOG index of McLaughlin (1969) with the polysyllables being the words of three or more syllables. Fitted on English; for Spanish it is the input of the SOL formula.

Formula:

$$
a\times\sqrt{30\times\frac{\textrm{Number of polysyllables}}{\textrm{Number of sentences}}}+b
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_complex` | int | `-` | Number of words of three or more syllables |
| `n_sents` | int | `-` | Number of sentences |
| `a` | float | `1.043` | Coefficient a |
| `b` | float | `3.1291` | Coefficient b |

## SOL grade { #calc_sol_grade }

!!! info ""
    **ests.readability_stats.calc_sol_grade()**

Computation of the SOL grade. Contreras et al. (1999) applied the SMOG index to Spanish texts and their English translations and fitted the conversion `E = −2.51 + 0.74·S`, where `S` is the SMOG index of the Spanish text and `E` the grade of the English scale, the years of schooling; the SOL formulas are named after the Spanish word for sun. The higher the value, the harder the text.

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

Computation of the [LIX readability index](https://en.wikipedia.org/wiki/Lix_(readability_test)) of Björnsson (1968), which does not depend on the language. The higher the value, the harder the text:

| Value | Difficulty level |
| :---: | :--------------- |
| `0-30` | very easy texts, children's books |
| `30-40` | easy texts, fiction, newspaper articles |
| `40-50` | texts of medium difficulty, magazine articles |
| `50-60` | hard texts, popular science, official texts |
| `60-100` | very hard texts, laws and bureaucratic language |

A long word has more than six letters, so `ReadabilityStats` passes the number of words of seven or more letters.

Formula:

$$
\frac{\textrm{Number of words}}{\textrm{Number of sentences}}+\frac{100\times\textrm{Number of long words}}{\textrm{Number of words}}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_long_words` | int | `-` | Number of long words |
| `n_words` | int | `-` | Number of words |
| `n_sents` | int | `-` | Number of sentences |

## RIX readability index { #calc_rix }

!!! info ""
    **ests.readability_stats.calc_rix()**

Computation of the RIX readability index (Anderson, 1983), the simplified companion of LIX: long words per sentence. The higher the value, the harder the text:

| Value | Grade |
| :---: | :---: |
| `< 0.2` | 1 |
| `0.2-0.5` | 2 |
| `0.5-0.8` | 3 |
| `0.8-1.3` | 4 |
| `1.3-1.8` | 5 |
| `1.8-2.4` | 6 |
| `2.4-3.0` | 7 |
| `3.0-3.7` | 8 |
| `3.7-4.5` | 9 |
| `4.5-5.3` | 10 |
| `5.3-6.2` | 11 |
| `6.2-7.2` | 12 |
| `> 7.2` | college |

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `n_long_words` | int | `-` | Number of long words |
| `n_sents` | int | `-` | Number of sentences |

## Reading ease level { #flesch_reading_easy_to_level }

!!! info ""
    **ests.readability_stats.flesch_reading_easy_to_level()**

The band of a scale for the Flesch reading ease. The scales of `ests.constants.READING_EASE_SCALES`: `inflesz` (Barrio-Cantalejo et al., 2008, five bands for the Szigriszt-Pazos coefficients), `szigriszt` (Szigriszt-Pazos, 1993: `muy difícil` below 15, `árido` 15-35, `bastante difícil` 35-50, `normal` 50-65, `bastante fácil` 65-75, `fácil` 75-85, `muy fácil` above 85) and `fernandez_huerta` (Fernández Huerta, 1959: `muy difícil` below 30, `difícil` 30-50, `bastante difícil` 50-60, `normal` 60-70, `bastante fácil` 70-80, `fácil` 80-90, `muy fácil` above 90).

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Value of the reading ease |
| `scale` | str | `inflesz` | Name of the scale |

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

Conversion of the Flesch reading ease into a school grade, used to include the reading ease in the consensus grade by analogy with `text_standard` of textstat, through the text types of the INFLESZ bands and the school stages of Spain:

| Value | Grade | Text type |
| :---: | :---: | :-------- |
| `80-100` | 3 | comics and children's books, primary school grades 1-3 |
| `65-80` | 5 | primary school textbooks, grades 4-6 |
| `55-65` | 8 | general press, ESO |
| `40-55` | 11 | secondary school textbooks, bachillerato |
| `below 40` | 13 | scientific texts, university |

Values above 100 belong to grade 3.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `flesch_reading_easy` | float | `-` | Value of the reading ease |

## Consensus grade { #calc_consensus_grade }

!!! info ""
    **ests.readability_stats.calc_consensus_grade()**

Computation of the consensus grade: the median of the rounded values of the grade formulas by analogy with `text_standard` of textstat, which uses the mode; the median is more robust to an outlying formula. The values are rounded half up. The reading ease is converted with `flesch_reading_easy_to_grade` and added without rounding.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `grades` | list[float] | `-` | Values of the grade formulas |
| `flesch_reading_easy` | float | `None` | Value of the reading ease |

!!! example "Example"

    ``` python
    from ests.readability_stats import calc_consensus_grade

    calc_consensus_grade([5.813, 9.258], 53.545)
    # 9.0
    ```

## Grade to age { #grade_to_age }

!!! info ""
    **ests.readability_stats.grade_to_age()**

The school stage and reader age by the value of a grade formula, by the stages of the Spanish school system counted in years of schooling from the first year of primary school at the age of six (see the [interpretation](readability_stats.md#interpretation) table). The value is rounded half up, values below 1 belong to grades 1-3.

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

Computation of the reading time of a text in minutes. The default speed is the silent reading speed of adults in Spanish, 278 words per minute: the mean of six studies in the meta-analysis of Brysbaert (2019), where reading aloud gives 191. The norms of school years from the meta-analysis of Ripoll, Tapia and Aguado (2020) are available in `ests.constants.READING_SPEED_NORMS` as pairs (aloud, silent):

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
| `wpm` | int | `278` | Reading speed, words per minute |

Sources: Brysbaert, M. How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 2019. Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado hispanohablante: un metaanálisis. *Revista de Psicodidáctica*, 25(2), 2020.
