# Funciones de las métricas

## Facilidad de lectura de Flesch { #calc_flesch_reading_easy }

!!! info ""
    **ests.readability_stats.calc_flesch_reading_easy()**

<!-- core: stats/readability_stats_funcs.md:calc_flesch_reading_easy 978f8ef -->
Cálculo de la facilidad de lectura de Flesch (Flesch, 1948).

Cuanto mayor es el valor, más fácil es el texto; la escala va nominalmente de 0 a 100, aunque los textos más sencillos pasan de 100 y los más difíciles bajan de 0.

Fórmula:

$$
c - a \cdot \frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}} - b \cdot \frac{\textrm{Número de sílabas}}{\textrm{Número de palabras}}
$$

Los coeficientes por defecto de esTS son los de la *fórmula de perspicuidad* de Szigriszt-Pazos (1993), que se lee en la escala INFLESZ de Barrio-Cantalejo et al. (2008):

| Valor | Nivel | Tipo de texto |
| :---: | :---: | :------------ |
| `80-100` | muy fácil | cómics, libros infantiles |
| `65-80` | bastante fácil | libros de texto de primaria |
| `55-65` | normal | prensa general |
| `40-55` | algo difícil | libros de texto de secundaria |
| `0-40` | muy difícil | textos científicos y técnicos |

Los coeficientes de Fernández Huerta (1959) están disponibles con el [preajuste](readability_stats.md#presets) `classic`, con la corrección de Law (2011): el último término toma la longitud media de la oración.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_syllables` | int | `-` | Número de sílabas |
| `n_words` | int | `-` | Número de palabras |
| `n_sents` | int | `-` | Número de oraciones |
| `a` | float | `1.0` | Coeficiente a, de la longitud media de la oración |
| `b` | float | `62.3` | Coeficiente b, de la longitud media de la palabra en sílabas |
| `c` | float | `206.835` | Coeficiente c, la constante |

Fuentes: Szigriszt Pazos, F. *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad*. Universidad Complutense de Madrid, 1993. Barrio-Cantalejo, I. M. et al. Validación de la Escala INFLESZ para evaluar la legibilidad de los textos dirigidos a pacientes. *Anales del Sistema Sanitario de Navarra*, 31(2), 2008. Fernández Huerta, J. Medidas sencillas de lecturabilidad. *Consigna*, 214, 1959. Law, G. Error in the Fernández Huerta readability formula. *LINGUIST List* 22.2332, 2011.

## Comprensibilidad de Gutiérrez de Polini { #calc_gutierrez_polini_index }

!!! info ""
    **ests.readability_stats.calc_gutierrez_polini_index()**

Cálculo de la *fórmula de comprensibilidad* de Gutiérrez de Polini (1972). Cuanto mayor es el valor, más fácil es el texto. Se ajustó con textos escolares de sexto grado y no tiene escala propia: la prosa corriente está entre 30 y 50, y un texto por encima de 70 lo lee un niño pequeño.

Fórmula:

$$
95.2-9.7\times\frac{\textrm{Número de letras}}{\textrm{Número de palabras}}-0.35\times\frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_letters` | int | `-` | Número de letras |
| `n_words` | int | `-` | Número de palabras |
| `n_sents` | int | `-` | Número de oraciones |

Fuente: Gutiérrez de Polini, L. E. *Investigación sobre lectura en Venezuela*. Ministerio de Educación, Caracas, 1972.

## Grado de Crawford { #calc_crawford_grade }

!!! info ""
    **ests.readability_stats.calc_crawford_grade()**

Cálculo de la fórmula de Crawford (1989): los años de escolaridad necesarios para leer el texto, ajustada con lecturas de primaria de los cursos 1-6, por lo que los valores altos se saturan. Cuanto mayor es el valor, más difícil es el texto.

Fórmula:

$$
-0.205\times\frac{100\times\textrm{Número de oraciones}}{\textrm{Número de palabras}}+0.049\times\frac{100\times\textrm{Número de sílabas}}{\textrm{Número de palabras}}-3.407
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_syllables` | int | `-` | Número de sílabas |
| `n_words` | int | `-` | Número de palabras |
| `n_sents` | int | `-` | Número de oraciones |

Fuente: Crawford, A. N. Fórmula y gráfico para determinar la comprensibilidad de textos del nivel primario en castellano. *Lectura y Vida*, 10(4), 1989.

## Legibilidad µ { #calc_mu_index }

!!! info ""
    **ests.readability_stats.calc_mu_index()**

<!-- core: stats/readability_stats_funcs.md:calc_mu_index cec1984 -->
Cálculo de la Legibilidad µ (Muñoz Baquedano y Muñoz Urra, 2006).

La media del número de letras por palabra dividida por su varianza muestral, por 100; no hay coeficientes que ajustar, y cuanto mayor es el valor, más fácil es el texto. Las palabras sin letras (los números) quedan fuera; con menos de dos palabras o sin variabilidad el índice no está definido (`nan`).

Fórmula:

$$
100 \cdot \frac{\bar{x}}{s^2}, \quad s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}
$$

donde $x_i$ es el número de letras de una palabra y $n$ el número de palabras.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `c_letters` | dict[int, int] | `-` | Distribución de las palabras por número de letras |

La varianza dividida por `n − 1` es la *cuasivarianza* de los autores, que reproduce el ejemplo resuelto de su manual; la distribución es `BasicStats.c_letters`. Las bandas de los autores:

| Valor | Nivel |
| :---: | :---: |
| `91-100` | muy fácil |
| `81-90` | fácil |
| `71-80` | un poco fácil |
| `61-70` | adecuado |
| `51-60` | un poco difícil |
| `31-50` | difícil |
| `0-30` | muy difícil |

Fuente: Muñoz Baquedano, M. Legibilidad y variabilidad de los textos. *Boletín de Investigación Educacional*, 21(2), 2006; el programa y el manual en [legibilidadmu.cl](https://www.legibilidadmu.cl/).

## Índice SMOG { #calc_smog_index }

!!! info ""
    **ests.readability_stats.calc_smog_index()**

<!-- core: stats/readability_stats_funcs.md:calc_smog_index b721fe1 -->
Cálculo del índice SMOG (McLaughlin, 1969).

Los años de escolaridad necesarios para leer el texto a partir de las palabras polisílabas por oración; cuanto mayor es el valor, más difícil es el texto. En la fórmula original las palabras polisílabas tienen tres o más sílabas y `b` lleva su número a una muestra de 30 oraciones.

Fórmula:

$$
a \cdot \sqrt{b \cdot \frac{\textrm{Número de palabras polisílabas}}{\textrm{Número de oraciones}}} + c
$$

Ajustado para el inglés; para el español es la entrada de la [fórmula SOL](#calc_sol_grade), y `ReadabilityStats` pasa las palabras de tres o más sílabas.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_complex` | int | `-` | Número de palabras polisílabas |
| `n_sents` | int | `-` | Número de oraciones |
| `a` | float | `1.043` | Coeficiente a, ante la raíz cuadrada |
| `b` | float | `30` | Coeficiente b, el número de oraciones de la muestra |
| `c` | float | `3.1291` | Coeficiente c, la constante |

## Grado SOL { #calc_sol_grade }

!!! info ""
    **ests.readability_stats.calc_sol_grade()**

Cálculo del grado SOL de Contreras et al. (1999), la conversión `E = −2.51 + 0.74·S`, donde `S` es el índice SMOG del texto español y `E` el grado de la escala inglesa, los años de escolaridad. Cuanto mayor es el valor, más difícil es el texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_complex` | int | `-` | Número de palabras de tres o más sílabas |
| `n_sents` | int | `-` | Número de oraciones |
| `a` | float | `0.74` | Coeficiente a, del índice SMOG |
| `b` | float | `-2.51` | Coeficiente b, la constante |

Fuente: Contreras, A., García-Alonso, R., Echenique, M., Daye-Contreras, F. The SOL formulas for converting SMOG readability scores between health education materials written in Spanish, English, and French. *Journal of Health Communication*, 4(1), 1999.

## Índice de legibilidad LIX { #calc_lix }

!!! info ""
    **ests.readability_stats.calc_lix()**

<!-- core: stats/readability_stats_funcs.md:calc_lix 65d7ed6 -->
Cálculo del índice de legibilidad LIX (Björnsson, 1968).

La longitud media de la oración más el porcentaje de palabras largas, las de más de seis letras; no hay coeficientes que ajustar. Cuanto mayor es el valor, más difícil es el texto:

| Valor | Texto |
| :---: | :---- |
| `0-30` | textos muy fáciles, libros infantiles |
| `30-40` | textos fáciles, narrativa, artículos de periódico |
| `40-50` | textos de dificultad media, artículos de revista |
| `50-60` | textos difíciles, divulgación científica, textos oficiales |
| `60-100` | textos muy difíciles, leyes y lenguaje burocrático |

Fórmula:

$$
\frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}} + \frac{100 \cdot \textrm{Número de palabras largas}}{\textrm{Número de palabras}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_long_words` | int | `-` | Número de palabras largas |
| `n_words` | int | `-` | Número de palabras |
| `n_sents` | int | `-` | Número de oraciones |

## Índice de legibilidad RIX { #calc_rix }

!!! info ""
    **ests.readability_stats.calc_rix()**

<!-- core: stats/readability_stats_funcs.md:calc_rix ab7c550 -->
Cálculo del índice de legibilidad RIX (Anderson, 1983).

Las palabras largas, de más de seis letras, por oración; no hay coeficientes que ajustar. Cuanto mayor es el valor, más difícil es el texto:

| Valor | Curso |
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
| `> 7.2` | universidad |

Fórmula:

$$
\frac{\textrm{Número de palabras largas}}{\textrm{Número de oraciones}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_long_words` | int | `-` | Número de palabras largas |
| `n_sents` | int | `-` | Número de oraciones |

## Nivel de la facilidad de lectura { #flesch_reading_easy_to_level }

!!! info ""
    **ests.readability_stats.flesch_reading_easy_to_level()**

El nivel de una escala para la facilidad de lectura de Flesch. Las escalas de `ests.constants.READING_EASE_SCALES`: `inflesz` (Barrio-Cantalejo et al., 2008, cinco niveles para los coeficientes de Szigriszt-Pazos), `szigriszt` (Szigriszt-Pazos, 1993, niveles enteros: `muy difícil` 0-15, `árido` 16-35, `bastante difícil` 36-50, `normal` 51-65, `bastante fácil` 66-75, `fácil` 76-85, `muy fácil` 86-100) y `fernandez_huerta` (Fernández Huerta, 1959: `muy difícil` por debajo de 30, `difícil` 30-50, `bastante difícil` 50-60, `normal` 60-70, `bastante fácil` 70-80, `fácil` 80-90, `muy fácil` por encima de 90).

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `flesch_reading_easy` | float | `-` | Valor de la facilidad de lectura |
| `scale` | str | `inflesz` | Nombre de la escala; `ReadabilityStats.describe_level` pasa la escala del preajuste |

!!! example "Ejemplo"

    ``` python
    from ests.readability_stats import flesch_reading_easy_to_level

    flesch_reading_easy_to_level(53.5), flesch_reading_easy_to_level(53.5, "szigriszt")
    # ('algo difícil', 'normal')
    ```

## Nivel µ { #mu_to_level }

!!! info ""
    **ests.readability_stats.mu_to_level()**

El nivel de la escala µ de Muñoz Baquedano y Muñoz Urra (2006) para la Legibilidad µ; un índice no definido (`nan`) no tiene nivel y devuelve una cadena vacía.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `mu_index` | float | `-` | Valor de la Legibilidad µ |

## De facilidad de lectura a grado { #flesch_reading_easy_to_grade }

!!! info ""
    **ests.readability_stats.flesch_reading_easy_to_grade()**

Conversión de la facilidad de lectura de Flesch en años de escolaridad para el grado de consenso. Los umbrales son los de la escala del preajuste.

Con el preajuste `general`, a través de los tipos de texto de los niveles INFLESZ y las etapas escolares de España:

| Valor | Grado | Tipo de texto |
| :---: | :---: | :------------ |
| `80-100` | 3 | cómics y libros infantiles, primaria cursos 1-3 |
| `65-80` | 5 | libros de texto de primaria, cursos 4-6 |
| `55-65` | 8 | prensa general, ESO |
| `40-55` | 11 | libros de texto de secundaria, bachillerato |
| `menos de 40` | 13 | textos científicos, universidad |

Con el preajuste `classic`, a través de la tabla de interpretación de Flesch que conservó Fernández Huerta: `90-100` - 5, `80-90` - 6, `70-80` - 7, `60-70` - 8.5, `50-60` - 10, `40-50` - 11, `30-40` - 12, por debajo de `30` - 13.

Los valores por encima de 100 corresponden al primer grado de la escala.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `flesch_reading_easy` | float | `-` | Valor de la facilidad de lectura |
| `preset` | str | `general` | Preajuste de coeficientes cuya escala se lee |

## Grado de consenso { #calc_consensus_grade }

!!! info ""
    **ests.readability_stats.calc_consensus_grade()**

Cálculo del grado de consenso: la mediana de los valores de las fórmulas de grado, cada uno redondeado con el medio hacia arriba. La facilidad de lectura se convierte con `flesch_reading_easy_to_grade` según la escala del preajuste y se añade sin redondear. La ausencia de valores, un grado que no es un número finito y un preajuste desconocido lanzan `ParameterError`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `grades` | list[float] | `-` | Valores de las fórmulas de grado |
| `flesch_reading_easy` | float | `None` | Valor de la facilidad de lectura |
| `preset` | str | `general` | Preajuste de coeficientes de la facilidad de lectura |

!!! example "Ejemplo"

    ``` python
    from ests.readability_stats import calc_consensus_grade

    calc_consensus_grade([5.813, 9.258], 53.545)
    # 9.0
    ```

## De grado a edad { #grade_to_age }

!!! info ""
    **ests.readability_stats.grade_to_age()**

La etapa del sistema educativo español y la edad del lector según el valor de una fórmula de grado (véase la tabla de la [interpretación](readability_stats.md#interpretation)). El valor se redondea con el medio hacia arriba, los valores por debajo de 1 corresponden a los cursos 1-3; un grado que no es un número finito lanza `ParameterError`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `grade` | float | `-` | Valor de una fórmula de grado |

!!! example "Ejemplo"

    ``` python
    from ests.readability_stats import grade_to_age

    grade_to_age(9.0)
    # 'ESO (12-16 years)'
    ```

## Tiempo de lectura { #calc_reading_time }

!!! info ""
    **ests.readability_stats.calc_reading_time()**

<!-- core: stats/readability_stats_funcs.md:calc_reading_time 725bd9c -->
Cálculo del tiempo de lectura de un texto en minutos: el número de palabras dividido por la velocidad de lectura; una velocidad que no es un número positivo lanza `ParameterError`.

La velocidad por defecto es la de lectura silenciosa de los adultos en español, 278 palabras por minuto, según el metaanálisis de Brysbaert (2019). Las normas por curso del metaanálisis de Ripoll, Tapia y Aguado (2020) están en `ests.constants.READING_SPEED_NORMS` como pares (en voz alta, en silencio):

| Norma | En voz alta | En silencio |
| :---: | :---------: | :---------: |
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

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `n_words` | int | `-` | Número de palabras |
| `wpm` | float | `278` | Velocidad de lectura, palabras por minuto |

Fuentes: Brysbaert, M. How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 2019. Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado hispanohablante: un metaanálisis. *Revista de Psicodidáctica*, 25(2), 2020.
