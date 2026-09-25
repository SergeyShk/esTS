# Estadísticas del verso

!!! info ""
    **ests.verse_stats.VerseStats**

## Descripción

Módulo para calcular las estadísticas del verso de un texto: la escansión de los versos, el metro y el número de sílabas métricas, los acentos rítmicos y el perfil acentual, los tipos del endecasílabo, las terminaciones de los versos y las estrofas. La fuente de datos puede ser un texto con sus saltos de línea o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy); no hacen falta ni un modelo entrenado ni un diccionario.

El metro del verso español es silábico: un verso se mide por sus sílabas métricas, y los acentos dan forma a su ritmo. Las palabras se dividen en sílabas y se acentúan por las reglas ortográficas de [`syllabify`](../syllables.md) y [`word_stresses`](../syllables.md#word_stresses), dejando aparte las palabras átonas del verso. Después las sílabas de un verso se cuentan como las lee el verso: las vocales en el límite de dos palabras forman una sílaba (la sinalefa), la ley del acento final fija la medida por la última sílaba acentuada, y un verso puede deshacer una sinalefa, dividir un diptongo o unir un hiato para alcanzar el metro de su poema. Un verso compuesto, ante todo el alejandrino, se lee como dos hemistiquios. El algoritmo y su precisión sobre los sonetos de [DISCO](../datasets/spanishsonnets.md) se describen en la [sección](verse_stats_funcs.md) de las funciones.

!!! note "Nota"
    Las estadísticas se calculan al crear el objeto `VerseStats`. La rima y las estrofas llegarán después.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `lines` | tuple[str] | Versos con palabras españolas |
| `stanzas` | tuple[tuple[str, ...], ...] | Versos por estrofa |
| `n_lines` | int | Número de versos |
| `n_stanzas` | int | Número de estrofas |
| `meter` | str/None | Metro - el nombre del verso por sus sílabas métricas: `octosílabo`, `endecasílabo`, `alejandrino`... (`VERSE_METERS`), o `None` |
| `n_feet` | int/None | Número de sílabas métricas del metro |
| `c_feet` | dict[int, int] | Distribución de los versos por sílabas métricas |
| `p_deviations` | float | Proporción de los versos fuera del metro, `nan` sin metro |
| `p_pyrrhics` | float | Proporción de los versos del metro sin sus acentos rítmicos, `nan` sin metro |
| `stress_profile` | tuple[float, ...] | Proporción de los versos del metro acentuados en cada sílaba métrica |
| `c_rhythms` | dict[str, int] | Distribución de los endecasílabos por tipo |
| `syllables` | tuple[tuple[str, ...], ...] | Sílabas de cada verso como las lee el verso, con la sinalefa marcada con `‿` |
| `stresses` | tuple[tuple[int, ...], ...] | Índices de las sílabas acentuadas de cada verso en `syllables`, desde cero |
| `caesuras` | tuple[int/None, ...] | Índice de la primera sílaba del segundo hemistiquio de cada verso en `syllables`, `None` para un verso simple |
| `patterns` | tuple[str, ...] | Esquemas de los versos de `+` (una sílaba métrica acentuada) y `-` (una átona), tan largos como el verso en sílabas métricas |
| `c_clausulas` | dict[str, int] | Distribución de las terminaciones de los versos por tipo: `aguda`, `llana`, `esdrújula`, `sobresdrújula` |
| `p_masculine` | float | Proporción de terminaciones agudas (el acento en la última sílaba) |
| `p_feminine` | float | Proporción de terminaciones llanas (una sílaba tras el acento) |
| `p_dactylic` | float | Proporción de terminaciones esdrújulas (dos sílabas tras el acento) |
| `c_stressed_vowels` | dict[str, int] | Distribución de las vocales acentuadas |
| `mean_line_len` | float | Longitud media de un verso en sílabas métricas |

El metro es la medida de la mayoría de los versos, y no se determina (`None`) si más de una décima parte de los versos (`VERSE_MAX_DEVIATIONS`) quedan fuera de él tras el ajuste: un poema polimétrico (una silva de heptasílabos y endecasílabos, un soneto con estrambote de más de una décima parte de heptasílabos), el verso libre y la prosa. Un solo verso tampoco tiene metro (`VERSE_MIN_LINES`): cualquier línea de hasta 18 sílabas tiene una medida con nombre, y lo tendría el 36% de las oraciones de doce obras en prosa del [corpus de literatura](../datasets/spanishliterature.md), frente al 1,4% de dos oraciones como dos versos y al 0,1% de tres. Los versos de un poema sin metro se ajustan a sus medidas comunes - las de al menos dos versos y una décima parte de ellos, como las 7 y las 11 sílabas de una lira o una silva - si estas ocupan más de la mitad de los versos, de modo que la distribución de las medidas y los tipos del endecasílabo cuentan las medidas reales de un poema polimétrico; los versos del verso libre y de la prosa conservan su lectura llana.

Los acentos rítmicos (`VERSE_RHYTHMS`) son los que un metro pide además del último, que todo verso tiene por la ley del acento final: el endecasílabo se acentúa en la 6.ª sílaba (a maiore) o en la 4.ª y la 8.ª (sáfico) o la 7.ª (dactílico); un verso compuesto, en el último acento de su primer hemistiquio. Un metro con solo el último acento, el octosílabo entre otros, tiene `p_pyrrhics` 0.

| Tipo | Acentos | Nombre |
| :--: | :-----: | :----- |
| `1-6-10` | 1.ª, 6.ª | enfático |
| `2-6-10` | 2.ª, 6.ª | heroico |
| `3-6-10` | 3.ª, 6.ª | melódico |
| `4-6-10`, `5-6-10` | el primer acento en la 4.ª o la 5.ª, 6.ª | a maiore |
| `6-10` | 6.ª, sin acento antes | a maiore |
| `4-8-10` | 4.ª, 8.ª, sin 6.ª | sáfico |
| `4-7-10` | 4.ª, 7.ª, sin 6.ª ni 8.ª | dactílico, de gaita gallega |

Un verso con la 6.ª sílaba acentuada toma su tipo de su primer acento; `4-6-10` cuenta como sáfico en algunos tratados. Un verso sin ninguno de los tres conjuntos queda fuera de `c_rhythms` y se cuenta en `p_pyrrhics`. Las sílabas métricas de `stress_profile` se cuentan desde cero, así que la 6.ª sílaba es el número 5. `stresses` indexa `syllables`, y ambos coinciden con `patterns` hasta el último acento de un verso simple; en un verso compuesto cada hemistiquio tiene su propia medida, así que tras una aguda o una esdrújula en la cesura `patterns` y `syllables` se separan, y `caesuras` dice dónde empieza el segundo hemistiquio.

!!! note "Nota"
    La escansión, el metro y los acentos se pueden obtener por separado con las funciones del módulo. El algoritmo y las funciones se describen en la [sección](verse_stats_funcs.md) correspondiente.

## Métodos

### get_stats

Devuelve un diccionario con las estadísticas del verso calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import VerseStats

    # El comienzo del soneto I de Garcilaso de la Vega
    text = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado."""

    vs = VerseStats(text)
    vs.get_stats()
    ```

    _Resultado_:

    ``` bash
    {'n_lines': 4,
     'n_stanzas': 1,
     'meter': 'endecasílabo',
     'n_feet': 11,
     'p_deviations': 0.0,
     'p_pyrrhics': 0.0,
     'p_masculine': 0.0,
     'p_feminine': 1.0,
     'p_dactylic': 0.0}
    ```

La escansión de cada verso, el perfil acentual y las distribuciones son atributos:

!!! example "Ejemplo"

    ``` python
    vs.syllables[1]
    # ('y‿a', 'ver', 'los', 'pa', 'sos', 'por', 'do', 'me‿han', 'tra', 'í', 'do')
    vs.patterns
    # ('---+---+-+-', '-+-+---+-+-', '+--+--+--+-', '--++-+-+-+-')
    vs.stresses[0]
    # (3, 7, 9)
    vs.stress_profile
    # (0.25, 0.25, 0.25, 1.0, 0.0, 0.25, 0.25, 0.75, 0.0, 1.0, 0.0)
    vs.c_rhythms, vs.c_clausulas
    # ({'4-8-10': 2, '4-7-10': 1, '3-6-10': 1}, {'llana': 4})
    vs.c_stressed_vowels
    # {'a': 8, 'e': 3, 'i': 2, 'u': 2, 'o': 1}
    ```

### print_stats

Muestra una tabla con las estadísticas del verso calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import VerseStats

    # La primera estrofa de Sonatina de Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    vs = VerseStats(sonatina)
    vs.print_stats()
    ```

    _Resultado_:

    ``` bash
                      Statistic                   |    Value
    ------------------------------------------------------------
    Number of lines                               |      6
    Number of stanzas                             |      1
    Meter                                         | alejandrino
    Number of metrical syllables                  |      14
    Share of lines off the meter                  |     0.00
    Share of lines without the rhythmic stresses  |     0.00
    Share of oxytone endings (aguda)              |     0.33
    Share of paroxytone endings (llana)           |     0.67
    Share of proparoxytone endings (esdrújula)    |     0.00
    ```

El alejandrino se lee por hemistiquios de 7 sílabas. La cesura impide la sinalefa, y cada hemistiquio sigue la ley del acento final: *La princesa está pálida* termina en esdrújula y cuenta 7, *que ha perdido el color* termina en aguda y cuenta 7 también.

!!! example "Ejemplo"

    ``` python
    vs.syllables[3]
    # ('la', 'prin', 'ce', 'sa‿es', 'tá', 'pá', 'li', 'da', 'en', 'su', 'si', 'lla', 'de', 'o', 'ro')
    vs.patterns[2], vs.patterns[3]
    # ('+-+--+-+-+--+-', '--+-++---+--+-')
    vs.stresses[3], vs.caesuras
    # ((2, 4, 5, 10, 13), (7, 7, 7, 8, 7, 7))
    ```

### accentuate { #accentuate }

Devuelve el texto con los acentos marcados: se pone un acento agudo (U+0301) tras la vocal acentuada de cada palabra tónica sin tilde; las palabras con tilde la conservan, y las palabras átonas del verso (`VERSE_PROCLITICS`) quedan sin marca, salvo la última palabra de un verso. Las marcas son caracteres combinantes aparte de las tildes, así que `unicodedata.normalize("NFC", ...)` las convierte en letras acentuadas. Solo se devuelven los versos con palabras españolas (como en `lines`), con las estrofas separadas por una línea en blanco.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    print(VerseStats(text).accentuate())
    ```

    _Resultado_:

    ``` bash
    Cuando me páro a contemplár mi estádo
    y a vér los pásos por do me hán traído,
    hállo, según por do andúve perdído,
    que a mayór mál pudiéra habér llegádo.
    ```

!!! note "Sobre los sonetos de DISCO"
    En los 4259 sonetos de [SpanishSonnets](../datasets/spanishsonnets.md) el metro es el endecasílabo en 3874, el alejandrino en 316, y 27 sonetos no tienen metro, entre ellos diálogos con los nombres de los interlocutores en los versos y sonetos con estrambote. Los tipos del endecasílabo cambian del Siglo de Oro al siglo XIX: el heroico `2-6-10` encabeza los siglos XV-XVII (el 32% de los versos con tipo, el sáfico `4-8-10` el 18%), y el sáfico encabeza el XIX (el 25%, el heroico el 25%, el melódico `3-6-10` el 21%).
