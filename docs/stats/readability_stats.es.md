# Métricas de legibilidad

``` {.python .signature}
ReadabilityStats(source, sents_extractor=None, words_extractor=None, preset='general')
```

<!-- core: stats/readability_stats.md:ReadabilityStats 5dd9076 -->
Las métricas de [legibilidad](https://es.wikipedia.org/wiki/Legibilidad) de un texto a partir de sus estadísticas básicas: la longitud media de la oración en palabras, la longitud media de la palabra en sílabas o en letras, la proporción de palabras polisílabas y de palabras largas y la variabilidad de la longitud de las palabras. La fuente de datos es un texto, un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy) o unas estadísticas básicas ya calculadas, que se reutilizan tal cual; los extractores se pasan a las estadísticas básicas de un texto o de un `Doc`. Las fórmulas solo cuentan las letras de las palabras contadas, así que un extractor de palabras que descarta palabras no alarga la palabra media.

Las métricas son propiedades que se calculan en cada acceso, así que un cambio de los `coefficients` de un objeto se aplica en el acto.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena, ni un `Doc`, ni unas estadísticas básicas, unas estadísticas básicas de una clase distinta de las de la biblioteca, un extractor de otro tipo, una cadena o un `Doc` pasados a una clase sin `basic_stats_class`;
- `SourceError` - una fuente sin palabras o sin oraciones;
- `ParameterError` - un preajuste desconocido o que no es una cadena.

Las métricas evalúan la legibilidad desde el lado de la lengua - la complejidad de las palabras y de las construcciones sintácticas, no el diseño tipográfico del texto. Suponen que las oraciones cortas se leen con más facilidad que las largas, que las palabras largas dificultan la lectura y que el lector se frena ante palabras poco frecuentes o desconocidas.

La clase extiende el `ReadabilityStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) con las fórmulas y las tablas del español, descritas en las tarjetas de las métricas: las [estadísticas básicas](basic_stats.md) de esTS, que toman por defecto los [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) del español, los [preajustes](#presets) de coeficientes de la facilidad de lectura de Flesch, las fórmulas de Gutiérrez de Polini, Crawford y SOL, el grado de consenso entre Crawford, SOL y la facilidad de lectura, las etapas escolares de España, las escalas de interpretación y las velocidades de lectura de los lectores en español. Una cadena con un carácter sin forma UTF-8, como la de un fichero leído con una codificación errónea, lanza `SourceError` desde el tokenizador del español.

=== "Código"

    ``` python
    from ests import ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    rs = ReadabilityStats(text)
    rs.print_stats()
    ```

=== "Resultado"

    ```
                    Metric                |  Value
    -------------------------------------------------
    Flesch reading ease (Szigriszt-Pazos) |  53.55
    Gutiérrez de Polini comprehensibility |  33.50
    Crawford grade                        |   5.81
    Legibilidad µ                         |  50.94
    SOL grade (SMOG for Spanish)          |   9.26
    LIX readability index                 |  60.00
    RIX readability index                 |   5.00
    Consensus grade                       |   9.00
    Reading time (min)                    |   0.04
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` / `BasicStats` | - | Fuente de datos (cadena, objeto Doc o estadísticas básicas ya calculadas) |
| `sents_extractor` | `SentsExtractor` | `None` | Herramienta de extracción de oraciones |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras |
| `preset` | `str` | `'general'` | Preajuste de coeficientes: `general` o `classic` |

El objeto guarda las estadísticas básicas del texto en `bs`, el nombre del preajuste en `preset`, de solo lectura, y los coeficientes del preajuste por fórmula en `coefficients`, una copia que se puede cambiar para un objeto. Un objeto de otro preajuste puede reutilizar las estadísticas básicas: `ReadabilityStats(rs.bs, preset="classic")`.

## Preajustes de coeficientes { #presets }

Un preajuste fija los coeficientes `a`, `b`, `c` de la facilidad de lectura de Flesch `c − a·ASL − b·ASW`, donde ASL es el número medio de palabras por oración y ASW el número medio de sílabas por palabra, y la escala con que la leen `describe_level`, `describe` y el grado de consenso. Las demás fórmulas no dependen del preajuste.

| Preajuste | Fuente | Fórmula | Escala |
| :-------- | :----- | :------ | :----- |
| `general` | Szigriszt-Pazos (1993), fórmula de perspicuidad | `206.835 − 1.0·ASL − 62.3·ASW` | INFLESZ (Barrio-Cantalejo et al., 2008) |
| `classic` | Fernández Huerta (1959) | `206.84 − 1.02·ASL − 60·ASW` | los siete niveles del autor |

La fórmula de Fernández Huerta toma la longitud media de la oración, con la corrección de Law (2011). La tabla de todos los coeficientes es `ests.constants.READABILITY_PRESETS`, y la escala de cada preajuste está en `PRESET_SCALES`.

=== "Código"

    ``` python
    classic = ReadabilityStats(rs.bs, preset="classic")
    rs.flesch_reading_easy, classic.flesch_reading_easy
    rs.describe_level(), classic.describe_level()
    ```

=== "Resultado"

    ```
    (53.545000000000016, 58.640000000000015)
    ('algo difícil', 'bastante difícil')
    ```

## Métricas

Una fórmula se calcula con la función de su tarjeta sobre los recuentos de `bs`. La facilidad de lectura toma sus coeficientes de `coefficients`, que fija el preajuste; las fórmulas de Gutiérrez de Polini, Crawford y SOL se calculan con los coeficientes de sus funciones, y `coefficients` no las afecta. Una fórmula de recuentos da `nan` cuando el número de palabras o de oraciones por el que divide es cero.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`flesch_reading_easy`](#flesch_reading_easy) | Facilidad de lectura según la longitud de la oración y las sílabas por palabra | En principio 0-100, por encima de 100 para los textos más simples y por debajo de 0 para los más difíciles | Un texto más fácil |
| [`gutierrez_polini_index`](#gutierrez_polini_index) | Comprensibilidad según las letras por palabra y la longitud de la oración | Por debajo de 95.2, la prosa corriente 30-50 | Un texto más fácil |
| [`crawford_grade`](#crawford_grade) | Grado según las oraciones y las sílabas por cada 100 palabras | Años de escolaridad, por debajo de 0 para los textos más simples; fórmula ajustada con los cursos 1-6 | Un texto más difícil |
| [`mu_index`](#mu_index) | Longitud media de la palabra en letras frente a su varianza | Por encima de 0, `nan` con menos de dos palabras o sin variabilidad | Un texto más fácil |
| [`sol_grade`](#sol_grade) | Grado según las palabras polisílabas por oración, SMOG convertido al español | Años de escolaridad, algo por debajo de 0 para los textos más simples | Un texto más difícil |
| [`lix`](#lix) | Longitud de la oración y proporción de palabras largas | 0 o más | Un texto más difícil |
| [`rix`](#rix) | Palabras largas por oración | 0 o más | Un texto más difícil |
| [`consensus_grade`](#consensus_grade) | Mediana de las fórmulas de grado y de la facilidad de lectura como grado | Años de escolaridad | Un texto más difícil |
| [`reading_time`](#reading_time) | Tiempo de lectura a la velocidad de lectura (`reading_speed`) | Minutos, por encima de 0 | Un texto más largo |
| [`smog_index`](#smog_index) | Grado según las palabras polisílabas por oración, coeficientes ingleses; fuera de `get_stats` | Años de escolaridad | Un texto más difícil |

Las demás fórmulas del núcleo con sus coeficientes ingleses - `flesch_kincaid_grade`, `coleman_liau_index`, `automated_readability_index` y `gunning_fog_index` - también son propiedades del objeto fuera de `get_stats`, porque están ajustadas con textos ingleses; sus tarjetas están en la [página de anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/).

<div class="metric-card" markdown>

### Facilidad de lectura de Flesch { #flesch_reading_easy }

`flesch_reading_easy` · Szigriszt-Pazos, 1993 · Fernández Huerta, 1959
{ .metric-meta }

``` {.python .signature}
calc_flesch_reading_easy(n_syllables, n_words, n_sents, a=1.0, b=62.3, c=206.835)
```

<!-- core: stats/readability_stats.md:calc_flesch_reading_easy b94d937 -->
La facilidad de lectura de un texto según la longitud media de la oración en palabras y la longitud media de la palabra en sílabas.

$$
c - a \cdot \frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}} - b \cdot \frac{\textrm{Número de sílabas}}{\textrm{Número de palabras}}
$$

Los coeficientes por defecto son los de la *fórmula de perspicuidad* de Szigriszt-Pazos (1993). Los coeficientes de Fernández Huerta (1959) los da el [preajuste](#presets) `classic`, con la corrección de Law (2011): el último término toma la longitud media de la oración, no el número de oraciones por cada 100 palabras que imprimió Fernández Huerta.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |
| `a` | `float` | `1.0` | Coeficiente a, de la longitud media de la oración |
| `b` | `float` | `62.3` | Coeficiente b, de la longitud media de la palabra en sílabas |
| `c` | `float` | `206.835` | Coeficiente c, la constante |

La escala de `describe_level` y `describe` sigue el preajuste: el atributo `preset_level_scales` del núcleo da para cada preajuste la escala de `ests.constants.READING_EASE_SCALES` que nombra `PRESET_SCALES` - la escala INFLESZ de Barrio-Cantalejo et al. (2008) para `general` y los niveles de Fernández Huerta para `classic`. La escala INFLESZ:

| Valor | Nivel | Tipo de texto |
| :---- | :---- | :------------ |
| `[80, ∞)` | muy fácil | cómics, libros infantiles |
| `[65, 80)` | bastante fácil | libros de texto de primaria |
| `[55, 65)` | normal | prensa general |
| `[40, 55)` | algo difícil | libros de texto de secundaria |
| `(−∞, 40)` | muy difícil | textos científicos y técnicos |

``` {.python .signature}
flesch_reading_easy_to_level(flesch_reading_easy, scale='inflesz')
```

El nivel de una escala de `READING_EASE_SCALES` para la facilidad de lectura: `inflesz` (arriba), `szigriszt` (Szigriszt-Pazos, 1993, niveles enteros: `muy difícil` 0-15, `árido` 16-35, `bastante difícil` 36-50, `normal` 51-65, `bastante fácil` 66-75, `fácil` 76-85, `muy fácil` 86-100) y `fernandez_huerta` (Fernández Huerta, 1959: `muy difícil` por debajo de 30, `difícil` 30-50, `bastante difícil` 50-60, `normal` 60-70, `bastante fácil` 70-80, `fácil` 80-90, `muy fácil` por encima de 90). El método `describe_level` lee la facilidad de lectura del objeto con cualquiera de ellas mediante su parámetro `scale`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `flesch_reading_easy` | `float` | - | Valor de la facilidad de lectura |
| `scale` | `str` | `'inflesz'` | Nombre de la escala: `inflesz`, `szigriszt` o `fernandez_huerta` |

Excepciones:

- `ParameterError` - una escala desconocida o que no es una cadena, un valor que no es un número finito.

=== "Código"

    ``` python
    from ests.readability_stats import flesch_reading_easy_to_level

    flesch_reading_easy_to_level(53.5), flesch_reading_easy_to_level(53.5, "szigriszt")
    ```

=== "Resultado"

    ```
    ('algo difícil', 'normal')
    ```

Fuentes: Szigriszt Pazos, F. *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad*. Universidad Complutense de Madrid, 1993. Barrio-Cantalejo, I. M. et al. Validación de la Escala INFLESZ para evaluar la legibilidad de los textos dirigidos a pacientes. *Anales del Sistema Sanitario de Navarra*, 31(2), 2008. Fernández Huerta, J. Medidas sencillas de lecturabilidad. *Consigna*, 214, 1959. Law, G. Error in the Fernández Huerta readability formula. *LINGUIST List* 22.2332, 2011.

</div>

<div class="metric-card" markdown>

### Comprensibilidad de Gutiérrez de Polini { #gutierrez_polini_index }

`gutierrez_polini_index` · Gutiérrez de Polini, 1972
{ .metric-meta }

``` {.python .signature}
calc_gutierrez_polini_index(n_letters, n_words, n_sents)
```

La *fórmula de comprensibilidad* de Gutiérrez de Polini, según la longitud media de la palabra en letras y la longitud media de la oración. Cuanto mayor es el valor, más fácil es el texto. Se ajustó con textos escolares de sexto grado y no tiene escala propia: la prosa corriente está entre 30 y 50, y un texto por encima de 70 lo lee un niño pequeño.

$$
95.2 - 9.7 \cdot \frac{\textrm{Número de letras}}{\textrm{Número de palabras}} - 0.35 \cdot \frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_letters` | `int` | - | Número de letras de las palabras |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

=== "Código"

    ``` python
    from ests.readability_stats import calc_gutierrez_polini_index

    calc_gutierrez_polini_index(n_letters=60, n_words=10, n_sents=1)
    ```

=== "Resultado"

    ```
    33.5
    ```

Fuente: Gutiérrez de Polini, L. E. *Investigación sobre lectura en Venezuela*. Ministerio de Educación, Caracas, 1972.

</div>

<div class="metric-card" markdown>

### Grado de Crawford { #crawford_grade }

`crawford_grade` · Crawford, 1989
{ .metric-meta }

``` {.python .signature}
calc_crawford_grade(n_syllables, n_words, n_sents)
```

Los años de escolaridad necesarios para leer el texto, según las oraciones y las sílabas por cada 100 palabras. La fórmula se ajustó con lecturas de primaria en español de los cursos 1-6, por lo que los valores altos se saturan. Cuanto mayor es el valor, más difícil es el texto.

$$
-0.205 \cdot \frac{100 \cdot \textrm{Número de oraciones}}{\textrm{Número de palabras}} + 0.049 \cdot \frac{100 \cdot \textrm{Número de sílabas}}{\textrm{Número de palabras}} - 3.407
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_syllables` | `int` | - | Número de sílabas |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

=== "Código"

    ``` python
    from ests.readability_stats import calc_crawford_grade

    calc_crawford_grade(n_syllables=23, n_words=10, n_sents=1)
    ```

=== "Resultado"

    ```
    5.812999999999999
    ```

Fuente: Crawford, A. N. Fórmula y gráfico para determinar la comprensibilidad de textos del nivel primario en castellano. *Lectura y Vida*, 10(4), 1989.

</div>

<div class="metric-card" markdown>

### Legibilidad µ { #mu_index }

`mu_index` · Muñoz Baquedano y Muñoz Urra, 2006
{ .metric-meta }

<!-- core: stats/readability_stats.md:calc_mu_index 8da809c -->
``` {.python .signature}
calc_mu_index(c_letters)
```

La media del número de letras por palabra dividida por su varianza muestral, por 100; no hay coeficientes que ajustar. Las palabras sin letras (los números) quedan fuera; con menos de dos palabras o sin variabilidad el índice no está definido (`nan`).

$$
100 \cdot \frac{\bar{x}}{s^2}, \quad s^2 = \frac{\sum (x_i - \bar{x})^2}{n - 1}
$$

donde $x_i$ es el número de letras de una palabra y $n$ el número de palabras.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `c_letters` | `dict[int, int]` | - | Distribución de las palabras por número de letras |

Un `c_letters` que no es un mapeo lanza `SourceTypeError`.

La varianza dividida por `n − 1` es la *cuasivarianza* de los autores, que reproduce el ejemplo resuelto de su manual; `ReadabilityStats` pasa `BasicStats.c_letters`. Los niveles de los autores, `ests.constants.MU_SCALE`, son la escala de `describe_level` y `describe`:

| Valor | Nivel |
| :---- | :---- |
| `[91, ∞)` | muy fácil |
| `[81, 91)` | fácil |
| `[71, 81)` | un poco fácil |
| `[61, 71)` | adecuado |
| `[51, 61)` | un poco difícil |
| `[31, 51)` | difícil |
| `(−∞, 31)` | muy difícil |

``` {.python .signature}
mu_to_level(mu_index)
```

El nivel de la escala `MU_SCALE` para un valor de la Legibilidad µ.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `mu_index` | `float` | - | Valor de la Legibilidad µ |

Excepciones:

- `ParameterError` - un valor que no es un número finito, como el índice no definido (`nan`).

=== "Código"

    ``` python
    from ests import BasicStats
    from ests.readability_stats import calc_mu_index, mu_to_level

    mu = calc_mu_index(BasicStats(text).c_letters)
    mu, mu_to_level(mu)
    ```

=== "Resultado"

    ```
    (50.943396226415096, 'difícil')
    ```

Fuente: Muñoz Baquedano, M. Legibilidad y variabilidad de los textos. *Boletín de Investigación Educacional*, 21(2), 2006; el programa y el manual en [legibilidadmu.cl](https://www.legibilidadmu.cl/).

</div>

<div class="metric-card" markdown>

### Grado SOL { #sol_grade }

`sol_grade` · Contreras et al., 1999
{ .metric-meta }

``` {.python .signature}
calc_sol_grade(n_complex, n_sents, a=0.74, b=-2.51)
```

Los años de escolaridad necesarios para leer un texto en español: la conversión de Contreras et al. de su [índice SMOG](#smog_index) `S`, calculado con los coeficientes originales, en el grado de la escala inglesa. Cuanto mayor es el valor, más difícil es el texto. `ReadabilityStats` pasa el número de palabras de tres o más sílabas.

$$
b + a \cdot S
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_complex` | `int` | - | Número de palabras de tres o más sílabas |
| `n_sents` | `int` | - | Número de oraciones |
| `a` | `float` | `0.74` | Coeficiente a, del índice SMOG |
| `b` | `float` | `-2.51` | Coeficiente b, la constante |

Excepciones:

- `ParameterError` - un número de palabras o de oraciones que no es un entero no negativo.

=== "Código"

    ``` python
    from ests.readability_stats import calc_smog_index, calc_sol_grade

    calc_smog_index(n_complex=5, n_sents=1), calc_sol_grade(n_complex=5, n_sents=1)
    ```

=== "Resultado"

    ```
    (15.903189008614273, 9.258359866374562)
    ```

Fuente: Contreras, A., García-Alonso, R., Echenique, M., Daye-Contreras, F. The SOL formulas for converting SMOG readability scores between health education materials written in Spanish, English, and French. *Journal of Health Communication*, 4(1), 1999.

</div>

<div class="metric-card" markdown>

### Índice de legibilidad LIX { #lix }

`lix` · Björnsson, 1968
{ .metric-meta }

<!-- core: stats/readability_stats.md:calc_lix 4fc8ad4 -->
``` {.python .signature}
calc_lix(n_long_words, n_words, n_sents)
```

La longitud media de la oración más el porcentaje de palabras largas, las de más de seis letras; no hay coeficientes que ajustar. Los valores se leen como tipos de texto:

| Valor | Texto |
| :---- | :--- |
| `0-30` | textos muy fáciles, libros infantiles |
| `30-40` | textos fáciles, narrativa, artículos de periódico |
| `40-50` | textos de dificultad media, artículos de revista |
| `50-60` | textos difíciles, divulgación científica, textos oficiales |
| `60-100` | textos muy difíciles, leyes y lenguaje burocrático |

$$
\frac{\textrm{Número de palabras}}{\textrm{Número de oraciones}} + \frac{100 \cdot \textrm{Número de palabras largas}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_long_words` | `int` | - | Número de palabras largas |
| `n_words` | `int` | - | Número de palabras |
| `n_sents` | `int` | - | Número de oraciones |

Estos niveles, `anyts.constants.LIX_LEVELS` con etiquetas en inglés, son la escala de `describe_level` y `describe`; su último nivel queda abierto por arriba.

</div>

<div class="metric-card" markdown>

### Índice de legibilidad RIX { #rix }

`rix` · Anderson, 1983
{ .metric-meta }

<!-- core: stats/readability_stats.md:calc_rix 139557a -->
``` {.python .signature}
calc_rix(n_long_words, n_sents)
```

Las palabras largas, de más de seis letras, por oración; no hay coeficientes que ajustar. Los valores se leen como cursos:

| Valor | Curso |
| :---- | :---- |
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

$$
\frac{\textrm{Número de palabras largas}}{\textrm{Número de oraciones}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `n_long_words` | `int` | - | Número de palabras largas |
| `n_sents` | `int` | - | Número de oraciones |

En esTS RIX no tiene escala de niveles, así que `describe_level("rix")` lanza `ParameterError`; `describe` toma los grados de Anderson como años de escolaridad (`anyts.constants.RIX_GRADES`, la universidad como 13) y da la etapa del sistema educativo español y la edad del lector con [`grade_to_age`](#grade_to_age).

</div>

<div class="metric-card" markdown>

### Grado de consenso { #consensus_grade }

`consensus_grade`
{ .metric-meta }

<!-- core: stats/readability_stats.md:ReadabilityStats-consensus c4a6ea5 -->
El atributo `consensus_grade` es la mediana de los valores de las fórmulas de grado (`grade_stats`) redondeados al entero más próximo (las mitades hacia arriba), junto con la facilidad de lectura en años de escolaridad (`reading_ease_to_grade`), sin redondear. Una biblioteca alinea los límites de `reading_ease_grades`, y de cada escala de `preset_reading_ease_grades`, con su escala de la facilidad de lectura, para que el grado de consenso y `describe` lean el valor igual.

Las fórmulas de grado de esTS (`ests.constants.READABILITY_GRADE_STATS`) son Crawford y SOL. esTS convierte la facilidad de lectura en años de escolaridad según la escala del preajuste: el atributo `preset_reading_ease_grades` del núcleo da para cada preajuste los límites de `READING_EASE_GRADES` y 13 por debajo de ellos, la escala de `flesch_reading_easy_to_grade`, así que los `reading_ease_grades` del núcleo no se usan.

!!! warning "Aviso"
    Crawford se ajustó con lecturas de primaria y se satura en los textos para adultos; SOL se ajustó con materiales de educación sanitaria. El grado de consenso de un texto técnico refleja sobre todo el nivel de la facilidad de lectura.

``` {.python .signature}
calc_consensus_grade(grades, flesch_reading_easy=None, preset='general')
```

La mediana de los valores de las fórmulas de grado redondeados al entero más próximo (las mitades hacia arriba), junto con la facilidad de lectura convertida en años de escolaridad con `flesch_reading_easy_to_grade` según la escala del preajuste, sin redondear.

$$
\textrm{mediana}\left(\lfloor g_1 + 0.5 \rfloor, \ldots, \lfloor g_k + 0.5 \rfloor, \textrm{grado}(\textrm{facilidad de lectura})\right)
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `grades` | `list[float]` | - | Valores de las fórmulas de grado |
| `flesch_reading_easy` | `float` | `None` | Valor de la facilidad de lectura |
| `preset` | `str` | `'general'` | Preajuste de coeficientes de la facilidad de lectura |

Excepciones:

- `ParameterError` - la ausencia de valores, un grado o una facilidad de lectura que no es un número finito, un preajuste desconocido o que no es una cadena;
- `SourceTypeError` - unos grados que no son una lista.

``` {.python .signature}
flesch_reading_easy_to_grade(flesch_reading_easy, preset='general')
```

Conversión de la facilidad de lectura de Flesch en años de escolaridad para el grado de consenso según los niveles de la escala del preajuste, `ests.constants.READING_EASE_GRADES`: el grado del primer nivel cuyo límite inferior alcanza el valor, o 13 por debajo del último límite; los valores por encima de 100 corresponden al primer nivel. Con el preajuste `general`, a través de los tipos de texto de los niveles INFLESZ y las etapas escolares de España:

| Facilidad de lectura | Grado | Tipo de texto |
| :------------------- | :---- | :------------ |
| `[80, ∞)` | 3 | cómics y libros infantiles, primaria cursos 1-3 |
| `[65, 80)` | 5 | libros de texto de primaria, cursos 4-6 |
| `[55, 65)` | 8 | prensa general, ESO |
| `[40, 55)` | 11 | libros de texto de secundaria, bachillerato |
| `(−∞, 40)` | 13 | textos científicos, universidad |

Con el preajuste `classic`, a través de la tabla de interpretación de Flesch que conservó Fernández Huerta: `90-100` - 5, `80-90` - 6, `70-80` - 7, `60-70` - 8.5, `50-60` - 10, `40-50` - 11, `30-40` - 12, por debajo de `30` - 13.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `flesch_reading_easy` | `float` | - | Valor de la facilidad de lectura |
| `preset` | `str` | `'general'` | Preajuste de coeficientes cuya escala se lee |

Excepciones:

- `ParameterError` - una facilidad de lectura que no es un número finito (el `nan` de un texto sin palabras u oraciones, un infinito), un preajuste desconocido o que no es una cadena.

=== "Código"

    ``` python
    from ests.readability_stats import calc_consensus_grade, flesch_reading_easy_to_grade

    flesch_reading_easy_to_grade(53.545), flesch_reading_easy_to_grade(53.545, "classic")
    calc_consensus_grade([5.813, 9.258], 53.545)
    ```

=== "Resultado"

    ```
    (11, 10)
    9.0
    ```

</div>

<div class="metric-card" markdown>

### Tiempo de lectura { #reading_time }

`reading_time` · `reading_time_by_speed(wpm)` · `reading_time_by_norm(norm)` · Brysbaert, 2019 · Ripoll, Tapia y Aguado, 2020
{ .metric-meta }

``` {.python .signature}
calc_reading_time(n_words, wpm=278)
```

<!-- core: stats/readability_stats.md:calc_reading_time a9233be -->
El tiempo de lectura de un texto en minutos: el número de palabras dividido por la velocidad de lectura.

$$
\frac{\textrm{Número de palabras}}{\textrm{wpm}}
$$

Un número de palabras que no es un entero no negativo y una velocidad que no es un número positivo lanzan `ParameterError`.

La velocidad por defecto es la de lectura silenciosa de los adultos en español, 278 palabras por minuto, según el metaanálisis de Brysbaert (2019). Las normas de `reading_time_by_norm`, `ests.constants.READING_SPEED_NORMS`, son las velocidades medias del alumnado hispanohablante por curso del metaanálisis de Ripoll, Tapia y Aguado (2020) - de `grade_1` a `grade_11`, es decir, primaria 1-6, ESO 7-10 y bachillerato 11 - y las de los adultos según Brysbaert (2019), como pares (en voz alta, en silencio):

| Norma | En voz alta | En silencio |
| :---- | :---------- | :---------- |
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

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_words` | `int` | - | Número de palabras |
| `wpm` | `float` | `278` | Velocidad de lectura, palabras por minuto (`READING_SPEED_WPM`) |

Fuentes: Brysbaert, M. How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 2019. Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado hispanohablante: un metaanálisis. *Revista de Psicodidáctica*, 25(2), 2020.

</div>

<div class="metric-card" markdown>

### Índice SMOG { #smog_index }

`smog_index` · McLaughlin, 1969
{ .metric-meta }

``` {.python .signature}
calc_smog_index(n_complex, n_sents, a=1.043, b=30, c=3.1291)
```

<!-- core: stats/readability_stats.md:calc_smog_index 8eac9a0 -->
Los años de escolaridad necesarios para leer el texto, según las palabras polisílabas por oración. En la fórmula original las palabras polisílabas tienen tres o más sílabas y `b` lleva su número a una muestra de 30 oraciones.

$$
a \cdot \sqrt{b \cdot \frac{\textrm{Número de palabras polisílabas}}{\textrm{Número de oraciones}}} + c
$$

Un número de palabras o de oraciones que no es un entero no negativo lanza `ParameterError`.

El índice está ajustado para el inglés y queda fuera de `get_stats`; para el español es la entrada del [grado SOL](#sol_grade). `ReadabilityStats` pasa el número de palabras de tres o más sílabas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `n_complex` | `int` | - | Número de palabras polisílabas |
| `n_sents` | `int` | - | Número de oraciones |
| `a` | `float` | `1.043` | Coeficiente a, ante la raíz cuadrada |
| `b` | `float` | `30` | Coeficiente b, el número de oraciones de la muestra |
| `c` | `float` | `3.1291` | Coeficiente c, la constante |

</div>

## Métodos

<!-- core: stats/readability_stats.md:ReadabilityStats-describe_grade 01276a5 -->
`describe_grade(stat)` devuelve la etapa escolar y la edad del lector para el grado de consenso o la fórmula de grado `stat`, `consensus_grade` por defecto; otra métrica lanza `ParameterError`.

Las fórmulas de grado de esTS son `crawford_grade` y `sol_grade`.

<!-- core: stats/readability_stats.md:ReadabilityStats-describe_level d50eec4 -->
`describe_level(stat)` devuelve el nivel de la escala de interpretación (`level_scale`) de la métrica `stat`, `flesch_reading_easy` por defecto; una métrica sin escala de niveles y un valor no definido (nan) lanzan `ParameterError`.

En esTS las métricas con escala de niveles son `flesch_reading_easy`, `mu_index` y `lix`, y `describe_level(stat, scale)` acepta además una escala `scale` de `READING_EASE_SCALES` para la facilidad de lectura - `inflesz`, `szigriszt` o `fernandez_huerta` - en lugar de la escala del preajuste, `None` por defecto; una escala indicada para otra métrica y una escala desconocida lanzan `ParameterError`. `level_scale(stat)` devuelve la escala de una métrica como límites inferiores y sus niveles - para la facilidad de lectura, la escala del preajuste - o `None` para una métrica sin escala de niveles, RIX incluido.

<!-- core: stats/readability_stats.md:ReadabilityStats-describe 3fed408 -->
`describe(stat)` devuelve la lectura de cualquier métrica según su escala: para el grado de consenso y una fórmula de grado, la etapa escolar y la edad del lector (`describe_grade`); para una métrica con escala de niveles (`level_scale`), su nivel; para otra métrica de `grade_scales`, la etapa y la edad de los años de escolaridad que da su escala; y `None` para una métrica sin escala o con un valor no definido (nan). Un nombre que no está en `stats_desc` ni es una propiedad pública de la clase lanza `UnknownStatError`.

En esTS las fórmulas de grado se leen como etapas del sistema educativo español, y también RIX a través de los grados de Anderson; la fórmula de Gutiérrez de Polini, el tiempo de lectura y las fórmulas del núcleo con sus coeficientes ingleses no tienen escala.

<!-- core: stats/readability_stats.md:ReadabilityStats-reading_time_by_speed 02714c8 -->
`reading_time_by_speed(wpm)` devuelve el tiempo de lectura del texto en minutos a la velocidad `wpm`, en palabras por minuto; una velocidad que no es un número positivo lanza `ParameterError`.

<!-- core: stats/readability_stats.md:ReadabilityStats-reading_time_by_norm 8a24e05 -->
`reading_time_by_norm(norm)` devuelve los tiempos de lectura del texto en minutos a las velocidades de la norma `norm` de `reading_speed_norms`, en su orden; una norma desconocida lanza `ParameterError`.

Las normas de esTS dan las velocidades en voz alta y en silencio, así que el método devuelve los tiempos de lectura en voz alta y en silencio.

<!-- core: stats/readability_stats.md:ReadabilityStats-get_stats 0cb58e2 -->
`get_stats()` devuelve un diccionario con las métricas de legibilidad de `stats_desc`.

<!-- core: stats/readability_stats.md:ReadabilityStats-print_stats ac340b3 -->
`print_stats()` muestra una tabla con las métricas de legibilidad y sus descripciones de `stats_desc` bajo los encabezados de `stats_headers`.

=== "Código"

    ``` python
    rs.describe_grade(), rs.describe_grade("crawford_grade")
    rs.describe_level(scale="szigriszt"), rs.describe_level("mu_index")
    rs.level_scale("flesch_reading_easy")
    rs.reading_time_by_speed(200), rs.reading_time_by_norm("grade_4")
    {stat: rs.describe(stat) for stat in rs.get_stats()}
    rs.get_stats()
    ```

=== "Resultado"

    ```
    ('ESO (12-16 years)', 'primary school, grades 4-6 (9-12 years)')
    ('normal', 'difícil')
    ((80, 'muy fácil'),
     (65, 'bastante fácil'),
     (55, 'normal'),
     (40, 'algo difícil'),
     (0, 'muy difícil'))
    (0.05, (0.09615384615384616, 0.08))
    {'flesch_reading_easy': 'algo difícil',
     'gutierrez_polini_index': None,
     'crawford_grade': 'primary school, grades 4-6 (9-12 years)',
     'mu_index': 'difícil',
     'sol_grade': 'ESO (12-16 years)',
     'lix': 'very hard texts, laws and bureaucratic language',
     'rix': 'ESO (12-16 years)',
     'consensus_grade': 'ESO (12-16 years)',
     'reading_time': None}
    {'flesch_reading_easy': 53.545000000000016,
     'gutierrez_polini_index': 33.5,
     'crawford_grade': 5.812999999999999,
     'mu_index': 50.943396226415096,
     'sol_grade': 9.258359866374562,
     'lix': 60.0,
     'rix': 5.0,
     'consensus_grade': 9.0,
     'reading_time': 0.03597122302158273}
    ```

El método `to_dataframe` es el de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS.

## Escalas { #scales }

El método `describe_level` lee la facilidad de lectura, la Legibilidad µ y LIX con las escalas de niveles de sus tarjetas, y `describe` lee cualquier métrica: estas tres con las mismas escalas, y las fórmulas de grado, el grado de consenso y RIX con las etapas escolares de [`grade_to_age`](#grade_to_age); para una métrica sin escala da `None`.

### Etapa escolar y edad { #grade_to_age }

``` {.python .signature}
grade_to_age(grade)
```

La etapa del sistema educativo español y la edad del lector según el valor de una fórmula de grado, en años de escolaridad contados desde el primer curso de primaria a los seis años: el valor se redondea al entero más próximo (las mitades hacia arriba) y cae en la primera etapa cuyo último curso no supera, los valores por debajo de 1 en los cursos 1-3. Las etapas son `ests.constants.GRADE_AGE_LEVELS` y `POSTGRADUATE_LEVEL`, con etiquetas en inglés (`'postgraduate (over 22 years)'`); la tabla las traduce:

| Grado | Etapa | Edad |
| :---- | :---- | :--- |
| 1-3 | primaria, cursos 1-3 | 6-9 años |
| 4-6 | primaria, cursos 4-6 | 9-12 años |
| 7-10 | ESO | 12-16 años |
| 11-12 | bachillerato | 16-18 años |
| 13-16 | universidad | 18-22 años |
| más de 16 | posgrado | más de 22 años |

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `grade` | `float` | - | Valor de una fórmula de grado |

Excepciones:

- `ParameterError` - un grado que no es un número finito.

=== "Código"

    ``` python
    from ests.readability_stats import grade_to_age

    grade_to_age(9.0), grade_to_age(17)
    ```

=== "Resultado"

    ```
    ('ESO (12-16 years)', 'postgraduate (over 22 years)')
    ```

### Nivel de una escala { #scale_level }

<!-- core: stats/readability_stats.md:scale_level ad443b9 -->
``` {.python .signature}
scale_level(value, scale)
```

El nivel de una escala para un valor: la escala se da como los límites inferiores de sus niveles en orden descendente, el valor cae en el primer nivel cuyo límite alcanza, y el nivel más bajo queda abierto por debajo.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `value` | `float` | - | Valor de una métrica |
| `scale` | `list[tuple[float, Any]]` | - | Límites inferiores y sus niveles en orden descendente |

Un valor que no es un número finito y una escala vacía, que no es una lista de pares de un límite inferior finito y un nivel o con límites que no descienden lanzan `ParameterError`.

Las escalas de esTS son `READING_EASE_SCALES` y `MU_SCALE` de `ests.constants`; LIX se lee con los `LIX_LEVELS` del núcleo.

=== "Código"

    ``` python
    from ests.constants import MU_SCALE, READING_EASE_SCALES
    from ests.readability_stats import scale_level

    scale_level(50.9, MU_SCALE), scale_level(50.9, READING_EASE_SCALES["fernandez_huerta"])
    ```

=== "Resultado"

    ```
    ('difícil', 'bastante difícil')
    ```
