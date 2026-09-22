# Métricas de legibilidad

!!! info ""
    **ests.readability_stats.ReadabilityStats**

## Descripción

Módulo para calcular las principales métricas de [legibilidad](https://es.wikipedia.org/wiki/Legibilidad) de la tradición española. La fuente de datos puede ser un texto, un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy) o unas [estadísticas básicas](basic_stats.md) `BasicStats` ya calculadas; en ese caso el texto no se vuelve a analizar.

!!! quote "Definición"

    La legibilidad es la propiedad de un texto que caracteriza la facilidad con que una persona lo percibe al leerlo.

    Conviene distinguir la legibilidad desde dos puntos de vista:

    *   el diseño tipográfico del texto;
    *   los rasgos lingüísticos del material textual (complejidad de las construcciones sintácticas, vocabulario difícil de percibir, etc.).

La legibilidad en este módulo se calcula a partir de medidas lingüísticas: la longitud media de la oración en palabras, la longitud media de la palabra en sílabas o letras, la proporción de palabras largas y de palabras de tres o más sílabas, y la variabilidad de la longitud de las palabras. Las fórmulas son las publicadas para el español, con los coeficientes de sus fuentes:

| Fórmula | Año | Resultado | Interpretación |
| :------ | :-: | :-------- | :------------- |
| Fernández Huerta | 1959 | facilidad de lectura de Flesch, 0-100 | siete niveles del autor |
| Szigriszt-Pazos (fórmula de perspicuidad) | 1993 | facilidad de lectura de Flesch, 0-100 | escala INFLESZ (Barrio-Cantalejo et al., 2008), cinco niveles |
| Gutiérrez de Polini (fórmula de comprensibilidad) | 1972 | 0-100, más alto es más fácil | sin escala propia; ajustada con textos de sexto grado |
| Crawford | 1989 | años de escolaridad | primaria española, cursos 1-6 |
| Legibilidad µ (Muñoz Baquedano y Muñoz Urra) | 2006 | 0-100, más alto es más fácil | siete niveles de los autores |
| SOL (Contreras et al.) | 1999 | años de escolaridad | SMOG convertido al español |
| LIX, RIX | 1968, 1983 | índice, palabras largas por oración | niveles y cursos independientes de la lengua |

La familia de Flesch se fija con un preajuste (véase [más abajo](#presets)): por defecto los coeficientes de Szigriszt-Pazos, validados con la escala INFLESZ, y como alternativa los de Fernández Huerta. Las demás fórmulas no dependen del preajuste.

Los supuestos principales de las métricas de legibilidad:

*   las oraciones cortas se leen con más facilidad que las largas;
*   las palabras largas dificultan la lectura;
*   el lector se frena ante palabras poco frecuentes o desconocidas.

El módulo permite usar objetos [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) ya configurados para la segmentación en oraciones y palabras que precede al cálculo.

!!! note "Nota"
    Las métricas se calculan al acceder al atributo correspondiente o al llamar al método `get_stats` del objeto `ReadabilityStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc/BasicStats | `-` | Fuente de datos (cadena, objeto Doc o estadísticas básicas ya calculadas) |
| `sents_extractor` | SentsExtractor | `None` | Herramienta de extracción de oraciones |
| `words_extractor` | WordsExtractor | `None` | Herramienta de extracción de palabras |
| `preset` | str | `general` | Preajuste de coeficientes (`general`, `classic`) |

## Atributos

| Atributo | Tipo | Descripción |
| :-------: | :--: | :---------: |
| `flesch_reading_easy` | float | Facilidad de lectura de Flesch con los coeficientes del preajuste |
| `gutierrez_polini_index` | float | Fórmula de comprensibilidad de Gutiérrez de Polini |
| `crawford_grade` | float | Fórmula de Crawford, años de escolaridad |
| `mu_index` | float | Legibilidad µ |
| `sol_grade` | float | Grado SOL, SMOG convertido al español |
| `lix` | float | Índice de legibilidad LIX |
| `rix` | float | Índice de legibilidad RIX |
| `consensus_grade` | float | Grado de consenso entre las fórmulas de grado y la facilidad de lectura |
| `reading_time` | float | Tiempo de lectura en minutos a 278 palabras por minuto |
| `bs` | BasicStats | Estadísticas básicas del texto |
| `preset` | str | Nombre del preajuste de coeficientes |
| `coefficients` | dict[str, tuple[float, float, float]] | Coeficientes de las fórmulas del preajuste |

## Preajustes de coeficientes { #presets }

Un preajuste fija los coeficientes `a`, `b`, `c` de la facilidad de lectura de Flesch `c − a·ASL − b·ASW`, donde ASL es el número medio de palabras por oración y ASW el número medio de sílabas por palabra. Las demás fórmulas no dependen del preajuste.

| Preajuste | Fuente | Fórmula | Escala |
| :-------: | :----: | :-----: | :----: |
| `general` | Szigriszt-Pazos (1993), fórmula de perspicuidad | `206.835 − 1.0·ASL − 62.3·ASW` | INFLESZ (Barrio-Cantalejo et al., 2008), validada con textos para pacientes |
| `classic` | Fernández Huerta (1959), la primera adaptación de Flesch al español | `206.84 − 1.02·ASL − 60·ASW` | los siete niveles del autor |

Fernández Huerta imprimió el último término como `1.02` por el número de frases por cada 100 palabras. Law (2011) mostró que eso invierte la fracción de la fórmula de Flesch en la que se basó la adaptación, así que aquí se usa la longitud media de la oración, como hacen koRpus, textstat y legible.es. La tabla de todos los coeficientes está disponible como `ests.constants.READABILITY_PRESETS`.

!!! example "Ejemplo"

    ``` python
    from ests import ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    ReadabilityStats(text).flesch_reading_easy
    # 53.545000000000016
    ReadabilityStats(text, preset="classic").flesch_reading_easy
    # 58.640000000000015
    ```

!!! note "Nota"
    Cada métrica puede calcularse por separado llamando a la función correspondiente. La información detallada sobre las métricas de legibilidad y las funciones que las calculan está en la [sección](readability_stats_funcs.md) correspondiente.

## Interpretación { #interpretation }

El método [`describe_level`](#describe_level) sitúa la facilidad de lectura en una escala: INFLESZ por defecto (`muy difícil` por debajo de 40, `algo difícil` 40-55, `normal` 55-65, `bastante fácil` 65-80, `muy fácil` por encima de 80), y a petición los siete niveles de Szigriszt-Pazos o de Fernández Huerta; la Legibilidad µ tiene los siete niveles de sus autores (`muy difícil` 0-30, `difícil` 31-50, `un poco difícil` 51-60, `adecuado` 61-70, `un poco fácil` 71-80, `fácil` 81-90, `muy fácil` 91-100).

Las fórmulas que dan años de escolaridad (Crawford, SOL) se resumen en el atributo `consensus_grade`: la mediana de los valores redondeados más la facilidad de lectura convertida en grado a través de los tipos de texto de los niveles INFLESZ. El método [`describe_grade`](#describe_grade) traduce el grado de consenso o una fórmula concreta en una etapa del sistema educativo español y la edad del lector:

| Grado | Etapa | Edad |
| :---: | :---: | :--: |
| 1-3 | primaria, cursos 1-3 | 6-9 años |
| 4-6 | primaria, cursos 4-6 | 9-12 años |
| 7-10 | ESO | 12-16 años |
| 11-12 | bachillerato | 16-18 años |
| 13-16 | universidad | 18-22 años |
| más de 16 | posgrado | más de 22 años |

!!! warning "Aviso"
    Crawford se ajustó con lecturas de primaria y se satura en los textos para adultos; SOL se ajustó con materiales de educación sanitaria. El grado de consenso de un texto técnico refleja sobre todo el nivel de la facilidad de lectura.

El atributo `reading_time` estima el tiempo de lectura silenciosa a 278 palabras por minuto, la media de seis estudios con lectores adultos de español en el metaanálisis de Brysbaert (2019). El método [`reading_time_by_speed`](#reading_time_by_speed) acepta otra velocidad, y el método [`reading_time_by_norm`](#reading_time_by_norm) calcula el tiempo en voz alta y en silencio según las normas de la tabla `ests.constants.READING_SPEED_NORMS`: las velocidades medias del alumnado hispanohablante por curso del metaanálisis de Ripoll, Tapia y Aguado (2020) y las de los adultos según Brysbaert (2019).

## Métodos

### describe_level

Devuelve el nivel de una escala de legibilidad para la facilidad de lectura o la Legibilidad µ.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `stat` | str | `flesch_reading_easy` | Nombre de la métrica (`flesch_reading_easy`, `mu_index`) |
| `scale` | str | `None` | Escala para la facilidad de lectura (`inflesz` por defecto, `szigriszt`, `fernandez_huerta`); la Legibilidad µ tiene una sola escala y no admite otra |

!!! example "Ejemplo"

    ``` python
    from ests import ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    rs = ReadabilityStats(text)
    rs.describe_level()
    # 'algo difícil'
    rs.describe_level(scale="szigriszt")
    # 'normal'
    rs.describe_level("mu_index")
    # 'un poco difícil'
    ```

### describe_grade

Devuelve la etapa escolar y la edad del lector para el grado de consenso o una fórmula de grado concreta.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `stat` | str | `consensus_grade` | Nombre de la fórmula de grado (`consensus_grade`, `crawford_grade`, `sol_grade`) |

!!! example "Ejemplo"

    ``` python
    rs.describe_grade()
    # 'ESO (12-16 years)'
    rs.describe_grade("crawford_grade")
    # 'primary school, grades 4-6 (9-12 years)'
    ```

### reading_time_by_speed

Devuelve el tiempo de lectura del texto en minutos a la velocidad indicada.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `wpm` | int | `-` | Velocidad de lectura, palabras por minuto |

### reading_time_by_norm

Devuelve el tiempo de lectura del texto en minutos en voz alta y en silencio según una norma de la tabla `ests.constants.READING_SPEED_NORMS`: de `grade_1` a `grade_11` (años de escolaridad: primaria 1-6, ESO 7-10, bachillerato 11) o `adult`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `norm` | str | `-` | Nombre de la norma de velocidad de lectura |

!!! example "Ejemplo"

    ``` python
    rs.reading_time_by_speed(200)
    # 0.05
    rs.reading_time_by_norm("grade_4")
    # (0.09615384615384616, 0.08)
    ```

### get_stats

Devuelve un diccionario con las métricas de legibilidad calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import ReadabilityStats

    # Preparar los datos
    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

    # Calcular las métricas
    rs = ReadabilityStats(text)
    rs.get_stats()
    ```

    _Resultado_:

    ``` bash
    {'flesch_reading_easy': 53.545000000000016,
    'gutierrez_polini_index': 33.5,
    'crawford_grade': 5.812999999999999,
    'mu_index': 56.60377358490566,
    'sol_grade': 9.258359866374562,
    'lix': 60.0,
    'rix': 5.0,
    'consensus_grade': 9.0,
    'reading_time': 0.03597122302158273}
    ```

### print_stats

Muestra una tabla con las métricas de legibilidad calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de métricas calculadas
    rs.print_stats()
    ```

    _Resultado_:

    ``` bash
                       Metric                    |  Value
    -------------------------------------------------------
    Flesch reading ease (Szigriszt-Pazos)        |  53.55
    Gutiérrez de Polini comprehensibility        |  33.50
    Crawford grade                               |   5.81
    Legibilidad µ                                |  56.60
    SOL grade (SMOG for Spanish)                 |   9.26
    LIX readability index                        |  60.00
    RIX readability index                        |   5.00
    Consensus grade                              |   9.00
    Reading time (min)                           |   0.04
    ```
