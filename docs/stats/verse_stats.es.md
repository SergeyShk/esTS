# Estadísticas del verso

!!! info ""
    **ests.verse_stats.VerseStats**

## Descripción

Módulo para calcular las estadísticas del verso de un texto: la escansión de los versos, el metro y el número de sílabas métricas, los acentos rítmicos y el perfil acentual, los tipos del endecasílabo, las terminaciones de los versos, la rima, su esquema y las estrofas. La fuente de datos puede ser un texto con sus saltos de línea o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy); no hacen falta ni un modelo entrenado ni un diccionario.

El metro del verso español es silábico: un verso se mide por sus sílabas métricas, y los acentos dan forma a su ritmo. Las palabras se dividen en sílabas y se acentúan por las reglas ortográficas de [`syllabify`](../syllables.md) y [`word_stresses`](../syllables.md#word_stresses), dejando aparte las palabras átonas del verso. Después las sílabas de un verso se cuentan como las lee el verso: las vocales en el límite de dos palabras forman una sílaba (la sinalefa), la ley del acento final fija la medida por la última sílaba acentuada, y un verso puede deshacer una sinalefa, dividir un diptongo o unir un hiato para alcanzar el metro de su poema. Un verso compuesto, ante todo el alejandrino, se lee como dos hemistiquios. Los versos riman por su terminación desde la última vocal acentuada, en consonante o en asonante, y las estrofas y el poema se nombran por sus versos y sus esquemas. El algoritmo y su precisión sobre los sonetos de [DISCO](../datasets/spanishsonnets.md) se describen en la [sección](verse_stats_funcs.md) de las funciones.

!!! note "Nota"
    Las estadísticas se calculan al crear el objeto `VerseStats`.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `seseo` | bool | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima, como en Andalucía y en América: `voz` - `dos` |

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
| `rhyme_schemes` | tuple[str, ...] | Esquemas de rima de las estrofas |
| `p_rhymed` | float | Proporción de los versos con rima |
| `c_rhymes` | dict[str, int] | Distribución de los versos con rima por el tipo de la rima: `consonante`, `asonante` |
| `strophes` | tuple[str/None, ...] | Nombres de las estrofas (`VERSE_STROPHES`) |
| `form` | str/None | Forma del poema: `soneto`, `romance`, la estrofa de todas sus estrofas, `silva` |
| `seseo` | bool | Si la rima se lee con seseo |

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

### Rima y estrofas { #rhyme }

Un verso rima por su terminación desde la última vocal acentuada: en consonante si los sonidos son iguales, en asonante si lo son la vocal acentuada y la última. Los sonidos son los del oído: `b` y `v`, `c` y `z` (`s` con `seseo`), `ll` e `y` son un solo sonido, la `h` es muda, la vibrante simple `r` y la múltiple `rr` se distinguen. La asonancia deja fuera las vocales entre la acentuada y la última (*pálido* - a, o), toma la vocal acentuada de un diptongo (*cielo* - e, o; *gracia* - a, a), lee la `i` y la `u` finales como `e` y `o` (*fácil* - a, e) y da a una aguda solo su vocal acentuada. Un verso rima con los versos de la ventana de `RHYME_WINDOW` (4) versos anteriores, por encima de las estrofas, de modo que los cuartetos de un soneto riman ABBA ABBA.

La asonancia cuenta en dos casos. Un poema cuya rima es la asonancia - al menos un tercio de sus versos sin rima consonante, y al menos cuatro de ellos, comparten una (`RHYME_MIN_ASSONANCE`, `RHYME_MIN_ASSONANT_LINES`) - rima por las asonancias de todos sus versos, que abarcan las rimas consonantes de las mismas vocales: los sonetos asonantados de DISCO. Si no, la asonancia cuenta en versos alternos con versos sin rima entre ellos: una serie de al menos cuatro versos de dos en dos con tres de cada cuatro de los versos intermedios sin rima consonante (`RHYME_MIN_FREE`), o todos los versos pares de una estrofa de un número par de versos, como el segundo y el cuarto de una copla. Así un romance rima aunque cambie de asonancia de una parte a otra (*La tierra de Alvargonzález* de Machado va en é-a, á-a, é-o...) y aunque sus versos asonantes rimen además en consonante de dos en dos (*colgar* - *contemplar* en la rima LIII de Bécquer). Una asonancia de versos vecinos no es rima: en un soneto de `-ado` y `-ano` cada verso tiene su rima consonante y los grupos se mantienen aparte, y los renglones de la prosa no riman por azar - las oraciones de prosa como versos comparten una asonancia que cuenta en el 0,1-3,6% de los textos de 5 a 40 versos y en el 6,5% de los de 4, donde bastan los dos versos de una copla.

El esquema de rima sigue el uso español: las letras van en el orden de los grupos de rima de todo el poema, mayúsculas para los versos de arte mayor (9 sílabas o más, `VERSE_ARTE_MAYOR`) y minúsculas para los de arte menor, con un guion para un verso sin rima: un soneto es ABBA ABBA CDC DCD, una redondilla abba, una lira aBabB, un romance -a-a-a-a. Cuando se acaban las 26 letras, se vuelve a tomar la letra de un grupo al que ya no puede unirse ningún verso de la ventana.

Una estrofa se nombra por sus versos, sus medidas, su esquema y su rima (`VERSE_STROPHES`, la primera que encaja):

| Estrofa | Versos | Medidas | Esquemas | Rima |
| :------ | :----: | :------ | :------- | :--: |
| pareado | 2 | cualquiera | aa | cualquiera |
| terceto | 3 | arte mayor | aba, a-a, abc, aab, abb | cualquiera |
| tercerilla | 3 | arte menor | aba, a-a | cualquiera |
| cuaderna vía | 4 | 14 cada uno | aaaa | consonante |
| cuarteto, serventesio | 4 | arte mayor | abba; abab | consonante |
| redondilla, cuarteta | 4 | arte menor | abba; abab | consonante |
| seguidilla | 4 | 7-5-7-5 | -a-a | cualquiera |
| copla | 4 | 8 cada uno | -a-a | asonante |
| lira | 5 | 7-11-7-7-11 | ababb | consonante |
| quinteto, quintilla | 5 | arte mayor; arte menor | ababa, abaab, abbab, aabab, aabba | consonante |
| estrofa manriqueña | 6 | 8-8-4-8-8-4 | abcabc | consonante |
| sexta rima | 6 | arte mayor | ababcc | consonante |
| sexteto | 6 | arte mayor | aabccb, abcabc, abbacc, aabbcc | consonante |
| sextilla | 6 | arte menor | aabccb, ababcc, abcabc, aabaab | consonante |
| octava real | 8 | 11 cada uno | abababcc | consonante |
| décima | 10 | 8 cada uno | abbaaccddc | consonante |

Una estrofa de un poema sin metro se ajusta a las sílabas de una estrofa que las pide, de modo que una lira sola recibe sus 7 y 11 sílabas. La forma de un poema es `soneto` para 14 versos de un metro de arte mayor en rima consonante con los cuartetos ABBA o ABAB y los tercetos en rimas propias; `romance` para octosílabos desde 8 versos con tres de cada cuatro de los versos pares de las estrofas en asonante, que puede cambiar, y tres de cada cuatro de los impares sin rima; la estrofa de todas las estrofas; `silva` para heptasílabos y endecasílabos sin metro, más largos que una estrofa (más de 10 versos) y sin un patrón de medidas repetido por todas sus estrofas.

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
     'p_rhymed': 1.0,
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

La rima del soneto entero y de un romance:

!!! example "Ejemplo"

    ``` python
    from ests.verse_stats import rhyme_scheme

    sonnet = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado;

    mas cuando del camino estó olvidado,
    a tanto mal no sé por dó he venido;
    sé que me acabo, y más he yo sentido
    ver acabar comigo mi cuidado.

    Yo acabaré, que me entregué sin arte
    a quien sabrá perderme y acabarme
    si quisiere, y aún sabrá querello;

    que pues mi voluntad puede matarme,
    la suya, que no es tanto de mi parte,
    pudiendo, ¿qué hará sino hacello?"""
    vs = VerseStats(sonnet)
    vs.rhyme_schemes, vs.strophes, vs.form
    # (('ABBA', 'ABBA', 'CDE', 'DCE'), ('cuarteto', 'cuarteto', 'terceto', 'terceto'), 'soneto')

    # El comienzo de La tierra de Alvargonzález de Antonio Machado
    romance = """Siendo mozo Alvargonzález,
    dueño de mediana hacienda,
    que en otras tierras se dice
    bienestar y aquí, opulencia,
    en la feria de Berlanga
    prendóse de una doncella,
    y la tomó por mujer
    al año de conocerla."""
    vs = VerseStats(romance)
    rhyme_scheme(romance), vs.form, vs.c_rhymes
    # ('-a-a-a-a', 'romance', {'asonante': 4})
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
    Share of rhymed lines                         |     1.00
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
