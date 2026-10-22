# Métricas de legibilidad

!!! info ""
    **ests.readability_stats.ReadabilityStats**

## Descripción

Las métricas de legibilidad de la tradición española.

<!-- core: stats/readability_stats.md:ReadabilityStats 5dd9076 -->
Las métricas de [legibilidad](https://es.wikipedia.org/wiki/Legibilidad) de un texto a partir de sus estadísticas básicas: la longitud media de la oración en palabras, la longitud media de la palabra en sílabas o en letras, la proporción de palabras polisílabas y de palabras largas y la variabilidad de la longitud de las palabras. La fuente de datos es un texto, un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy) o unas estadísticas básicas ya calculadas, que se reutilizan tal cual; los extractores se pasan a las estadísticas básicas de un texto o de un `Doc`. Las fórmulas solo cuentan las letras de las palabras contadas, así que un extractor de palabras que descarta palabras no alarga la palabra media.

Las métricas son propiedades que se calculan en cada acceso, así que un cambio de los `coefficients` de un objeto se aplica en el acto.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena, ni un `Doc`, ni unas estadísticas básicas, unas estadísticas básicas de una clase distinta de las de la biblioteca, un extractor de otro tipo, una cadena o un `Doc` pasados a una clase sin `basic_stats_class`;
- `SourceError` - una fuente sin palabras o sin oraciones;
- `ParameterError` - un preajuste desconocido o que no es una cadena.

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
| Crawford | 1989 | años de escolaridad | primaria en español, cursos 1-6 |
| Legibilidad µ (Muñoz Baquedano y Muñoz Urra) | 2006 | 0-100, más alto es más fácil | siete niveles de los autores |
| SOL (Contreras et al.) | 1999 | años de escolaridad | SMOG convertido al español |
| LIX, RIX | 1968, 1983 | índice, palabras largas por oración | niveles y cursos independientes de la lengua |

Los coeficientes de la facilidad de lectura de Flesch se fijan con un preajuste (véase [más abajo](#presets)): Szigriszt-Pazos por defecto, Fernández Huerta como alternativa.

Los supuestos principales de las métricas de legibilidad:

*   las oraciones cortas se leen con más facilidad que las largas;
*   las palabras largas dificultan la lectura;
*   el lector se frena ante palabras poco frecuentes o desconocidas.

## Ganchos del idioma

La clase extiende el `ReadabilityStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) con las fórmulas y las tablas del español: las [estadísticas básicas](basic_stats.md) de esTS, que toman por defecto los [`SentsExtractor`](../extractors/sentences.md) y [`WordsExtractor`](../extractors/words.md) del español, los preajustes de la facilidad de lectura de Flesch, las fórmulas de Gutiérrez de Polini, Crawford y SOL, las fórmulas de grado del grado de consenso (Crawford y SOL), las etapas escolares de España, las escalas de interpretación y las velocidades de lectura de los lectores en español. La escala de la facilidad de lectura sigue el preajuste (`level_scale`), así que `describe_level` y `describe` leen el valor igual que el grado de consenso.

Las fórmulas del núcleo con sus coeficientes ingleses - `flesch_kincaid_grade`, `coleman_liau_index`, `automated_readability_index`, `smog_index` y `gunning_fog_index` - siguen siendo atributos del objeto, fuera de `get_stats`: están ajustadas con textos ingleses, y `smog_index` es la entrada de SOL.

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
| `coefficients` | dict[str, tuple[float, float, float]] | Coeficientes de las fórmulas del preajuste, una copia que se puede cambiar para un objeto |

## Preajustes de coeficientes { #presets }

Un preajuste fija los coeficientes `a`, `b`, `c` de la facilidad de lectura de Flesch `c − a·ASL − b·ASW`, donde ASL es el número medio de palabras por oración y ASW el número medio de sílabas por palabra. Las demás fórmulas no dependen del preajuste.

| Preajuste | Fuente | Fórmula | Escala |
| :-------: | :----: | :-----: | :----: |
| `general` | Szigriszt-Pazos (1993), fórmula de perspicuidad | `206.835 − 1.0·ASL − 62.3·ASW` | INFLESZ (Barrio-Cantalejo et al., 2008) |
| `classic` | Fernández Huerta (1959) | `206.84 − 1.02·ASL − 60·ASW` | los siete niveles del autor |

La fórmula de Fernández Huerta toma la longitud media de la oración, con la corrección de Law (2011). La tabla de todos los coeficientes está disponible como `ests.constants.READABILITY_PRESETS`.

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

El método [`describe_level`](#describe_level) sitúa la facilidad de lectura en la escala del preajuste: INFLESZ para `general` (`muy difícil` por debajo de 40, `algo difícil` 40-55, `normal` 55-65, `bastante fácil` 65-80, `muy fácil` por encima de 80) y los siete niveles de Fernández Huerta para `classic`, y a petición las escalas de Szigriszt-Pazos o del otro autor; la Legibilidad µ tiene los siete niveles de sus autores (`muy difícil` 0-30, `difícil` 31-50, `un poco difícil` 51-60, `adecuado` 61-70, `un poco fácil` 71-80, `fácil` 81-90, `muy fácil` 91-100), y LIX los tipos de texto de Björnsson ([`calc_lix`](readability_stats_funcs.md#calc_lix)). RIX no tiene aquí niveles propios: sus grados de Anderson ([`calc_rix`](readability_stats_funcs.md#calc_rix)) son años de escolaridad, y [`describe`](#describe) los lee como una etapa del sistema educativo español.

<!-- core: stats/readability_stats.md:ReadabilityStats-consensus c4a6ea5 -->
El atributo `consensus_grade` es la mediana de los valores de las fórmulas de grado (`grade_stats`) redondeados al entero más próximo (las mitades hacia arriba), junto con la facilidad de lectura en años de escolaridad (`reading_ease_to_grade`), sin redondear. Una biblioteca alinea los límites de `reading_ease_grades`, y de cada escala de `preset_reading_ease_grades`, con su escala de la facilidad de lectura, para que el grado de consenso y `describe` lean el valor igual.

Las fórmulas de grado de esTS son Crawford y SOL, y la facilidad de lectura se [convierte en grado](readability_stats_funcs.md#flesch_reading_easy_to_grade) según la escala del preajuste. El método [`describe_grade`](#describe_grade) traduce el grado de consenso o una fórmula concreta en una etapa del sistema educativo español y la edad del lector:

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

El atributo `reading_time` estima el tiempo de lectura silenciosa a 278 palabras por minuto, la velocidad de los lectores adultos de español en el metaanálisis de Brysbaert (2019). El método [`reading_time_by_speed`](#reading_time_by_speed) acepta otra velocidad, y el método [`reading_time_by_norm`](#reading_time_by_norm) calcula el tiempo en voz alta y en silencio según las normas de la tabla `ests.constants.READING_SPEED_NORMS`: las velocidades medias del alumnado hispanohablante por curso del metaanálisis de Ripoll, Tapia y Aguado (2020) y las de los adultos según Brysbaert (2019).

## Métodos

### describe_level

Devuelve el nivel de la escala de interpretación de la facilidad de lectura, la Legibilidad µ o LIX. Una métrica sin escala de niveles, un valor no definido (nan) y una escala indicada para una métrica que no es la facilidad de lectura lanzan `ParameterError`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `stat` | str | `flesch_reading_easy` | Nombre de la métrica (`flesch_reading_easy`, `mu_index`, `lix`) |
| `scale` | str | `None` | Escala para la facilidad de lectura (`inflesz`, `szigriszt`, `fernandez_huerta`); sin ella se usa la escala del preajuste |

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
    # 'difícil'
    rs.describe_level("lix")
    # 'very hard texts, laws and bureaucratic language'
    ```

### level_scale

Devuelve la escala de interpretación de una métrica como límites inferiores y sus niveles, la que leen `describe_level` y `describe`: para la facilidad de lectura la escala del preajuste (INFLESZ para `general`, Fernández Huerta para `classic`), `MU_SCALE` para la Legibilidad µ, los tipos de texto de Björnsson para LIX, y `None` para una métrica sin escala de niveles, RIX incluido.

!!! example "Ejemplo"

    ``` python
    rs.level_scale("flesch_reading_easy")
    # ((80, 'muy fácil'), (65, 'bastante fácil'), (55, 'normal'), (40, 'algo difícil'), (0, 'muy difícil'))
    ```

### describe_grade

<!-- core: stats/readability_stats.md:ReadabilityStats-describe_grade 01276a5 -->
`describe_grade(stat)` devuelve la etapa escolar y la edad del lector para el grado de consenso o la fórmula de grado `stat`, `consensus_grade` por defecto; otra métrica lanza `ParameterError`.

Las fórmulas de grado son `consensus_grade`, `crawford_grade` y `sol_grade`.

!!! example "Ejemplo"

    ``` python
    rs.describe_grade()
    # 'ESO (12-16 years)'
    rs.describe_grade("crawford_grade")
    # 'primary school, grades 4-6 (9-12 years)'
    ```

### describe

<!-- core: stats/readability_stats.md:ReadabilityStats-describe 3fed408 -->
`describe(stat)` devuelve la lectura de cualquier métrica según su escala: para el grado de consenso y una fórmula de grado, la etapa escolar y la edad del lector (`describe_grade`); para una métrica con escala de niveles (`level_scale`), su nivel; para otra métrica de `grade_scales`, la etapa y la edad de los años de escolaridad que da su escala; y `None` para una métrica sin escala o con un valor no definido (nan). Un nombre que no está en `stats_desc` ni es una propiedad pública de la clase lanza `UnknownStatError`.

En esTS las fórmulas de grado se leen como etapas del sistema educativo español, y también RIX a través de los grados de Anderson; la fórmula de Gutiérrez de Polini, el tiempo de lectura y las fórmulas del núcleo con sus coeficientes ingleses (`flesch_kincaid_grade`, `coleman_liau_index`, `automated_readability_index`, `smog_index`, `gunning_fog_index`) no tienen escala.

!!! example "Ejemplo"

    ``` python
    {stat: rs.describe(stat) for stat in rs.get_stats()}
    # {'flesch_reading_easy': 'algo difícil',
    #  'gutierrez_polini_index': None,
    #  'crawford_grade': 'primary school, grades 4-6 (9-12 years)',
    #  'mu_index': 'difícil',
    #  'sol_grade': 'ESO (12-16 years)',
    #  'lix': 'very hard texts, laws and bureaucratic language',
    #  'rix': 'ESO (12-16 years)',
    #  'consensus_grade': 'ESO (12-16 years)',
    #  'reading_time': None}
    ```

### reading_time_by_speed

<!-- core: stats/readability_stats.md:ReadabilityStats-reading_time_by_speed 02714c8 -->
`reading_time_by_speed(wpm)` devuelve el tiempo de lectura del texto en minutos a la velocidad `wpm`, en palabras por minuto; una velocidad que no es un número positivo lanza `ParameterError`.

### reading_time_by_norm

<!-- core: stats/readability_stats.md:ReadabilityStats-reading_time_by_norm 8a24e05 -->
`reading_time_by_norm(norm)` devuelve los tiempos de lectura del texto en minutos a las velocidades de la norma `norm` de `reading_speed_norms`, en su orden; una norma desconocida lanza `ParameterError`.

Las normas de la tabla `ests.constants.READING_SPEED_NORMS` son de `grade_1` a `grade_11` (años de escolaridad: primaria 1-6, ESO 7-10, bachillerato 11) y `adult`, cada una con las velocidades en voz alta y en silencio, así que el método devuelve los tiempos de lectura en voz alta y en silencio.

!!! example "Ejemplo"

    ``` python
    rs.reading_time_by_speed(200)
    # 0.05
    rs.reading_time_by_norm("grade_4")
    # (0.09615384615384616, 0.08)
    ```

### get_stats

<!-- core: stats/readability_stats.md:ReadabilityStats-get_stats 0cb58e2 -->
`get_stats()` devuelve un diccionario con las métricas de legibilidad de `stats_desc`.

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
    'mu_index': 50.943396226415096,
    'sol_grade': 9.258359866374562,
    'lix': 60.0,
    'rix': 5.0,
    'consensus_grade': 9.0,
    'reading_time': 0.03597122302158273}
    ```

### print_stats

<!-- core: stats/readability_stats.md:ReadabilityStats-print_stats ac340b3 -->
`print_stats()` muestra una tabla con las métricas de legibilidad y sus descripciones de `stats_desc` bajo los encabezados de `stats_headers`.

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
    Legibilidad µ                                |  50.94
    SOL grade (SMOG for Spanish)                 |   9.26
    LIX readability index                        |  60.00
    RIX readability index                        |   5.00
    Consensus grade                              |   9.00
    Reading time (min)                           |   0.04
    ```
