# Estadísticas del verso

``` {.python .signature}
VerseStats(source, seseo=False)
```

Las estadísticas del verso de un texto: la escansión de los versos, el metro y el número de sílabas métricas, los acentos rítmicos y el perfil acentual, los tipos del endecasílabo, las terminaciones de los versos, la rima, su esquema y las estrofas. La fuente de datos es un texto con sus saltos de línea o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy); las estadísticas se calculan al crear el objeto, y no hacen falta ni un modelo entrenado ni un diccionario.

El metro del verso español es silábico: un verso se mide por sus sílabas métricas, y los acentos dan forma a su ritmo. El texto se divide en versos y estrofas (por las líneas en blanco), las palabras se dividen en sílabas y se acentúan con [`syllabify`](../syllables.md) y [`word_stresses`](../syllables.md#word_stresses), y las sílabas de un verso se cuentan con las sinalefas y la ley del acento final; un verso compuesto, ante todo el alejandrino, se lee como dos hemistiquios ([algoritmo](#algorithm)). Un texto con letras pero sin sílabas españolas (otro alfabeto) da estadísticas vacías: `n_lines` 0, el metro `None`, las proporciones `nan`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`;
- `SourceError` - una fuente sin letras (vacía, solo cifras y signos de puntuación);
- `ParameterError` - un `seseo` que no es un `bool`.

=== "Código"

    ``` python
    from ests import VerseStats

    # El comienzo del soneto I de Garcilaso de la Vega
    text = """Cuando me paro a contemplar mi estado
    y a ver los pasos por do me han traído,
    hallo, según por do anduve perdido,
    que a mayor mal pudiera haber llegado."""

    vs = VerseStats(text)
    vs.print_stats()
    ```

=== "Resultado"

    ```
                      Statistic                  |    Value
    ------------------------------------------------------------
    Number of lines                              |      4
    Number of stanzas                            |      1
    Meter                                        | endecasílabo
    Number of metrical syllables                 |      11
    Share of lines off the meter                 |     0.00
    Share of lines without the rhythmic stresses |     0.00
    Share of rhymed lines                        |     1.00
    Share of oxytone endings (aguda)             |     0.00
    Share of paroxytone endings (llana)          |     1.00
    Share of proparoxytone endings (esdrújula)   |     0.00
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `seseo` | `bool` | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima, como en Andalucía y en América: `voz` - `dos` |

## Atributos

| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `lines` | `tuple[str]` | Versos con palabras españolas |
| `stanzas` | `tuple[tuple[str, ...], ...]` | Versos por estrofa |
| `syllables` | `tuple[tuple[str, ...], ...]` | Sílabas de cada verso como las lee el verso, con la sinalefa marcada con `‿` |
| `stresses` | `tuple[tuple[int, ...], ...]` | Índices de las sílabas acentuadas de cada verso en `syllables`, desde cero |
| `caesuras` | `tuple[int / None, ...]` | Índice de la primera sílaba del segundo hemistiquio de cada verso en `syllables`, `None` para un verso simple |
| `patterns` | `tuple[str, ...]` | Esquemas de los versos de `+` (una sílaba métrica acentuada) y `-` (una átona), tan largos como el verso en sílabas métricas |
| `mean_line_len` | `float` | Longitud media de un verso en sílabas métricas |
| `c_stressed_vowels` | `dict[str, int]` | Distribución de las vocales acentuadas |
| `seseo` | `bool` | Si la rima se lee con seseo |
| `c_feet` | `dict[int, int]` | Distribución de los versos por sílabas métricas ([metro](#meter)) |
| `stress_profile` | `tuple[float, ...]` | Proporción de los versos del metro acentuados en cada sílaba métrica ([metro](#meter)) |
| `c_rhythms` | `dict[str, int]` | Distribución de los endecasílabos por tipo ([acentos rítmicos](#pyrrhics)) |
| `rhyme_schemes` | `tuple[str, ...]` | Esquemas de rima de las estrofas ([rima](#rhyme_scheme)) |
| `c_rhymes` | `dict[str, int]` | Distribución de los versos con rima por el tipo de la rima: `consonante`, `asonante` ([rima](#rhyme_scheme)) |
| `strophes` | `tuple[str / None, ...]` | Nombres de las estrofas, `VERSE_STROPHES` ([estrofas](#strophes)) |
| `form` | `str / None` | Forma del poema: `soneto`, `romance`, la estrofa de todas sus estrofas, `silva` ([estrofas](#strophes)) |
| `c_clausulas` | `dict[str, int]` | Distribución de las terminaciones de los versos por tipo: `aguda`, `llana`, `esdrújula`, `sobresdrújula` ([terminaciones](#clausulas)) |

`stresses` indexa `syllables`, y ambos coinciden con `patterns` hasta el último acento de un verso simple; en un [verso compuesto](#meter) cada hemistiquio tiene su propia medida, así que tras una aguda o una esdrújula en la cesura `patterns` y `syllables` se separan, y `caesuras` dice dónde empieza el segundo hemistiquio.

=== "Código"

    ``` python
    vs.syllables[1]
    vs.patterns
    vs.stresses[0]
    vs.c_stressed_vowels
    ```

=== "Resultado"

    ```
    ('y‿a', 'ver', 'los', 'pa', 'sos', 'por', 'do', 'me‿han', 'tra', 'í', 'do')
    ('---+---+-+-', '-+-+---+-+-', '+--+--+--+-', '--++-+-+-+-')
    (3, 7, 9)
    {'a': 8, 'e': 3, 'i': 2, 'u': 2, 'o': 1}
    ```

## Métricas

Cada métrica es un atributo del objeto, calculado al crearlo; `get_stats` devuelve las métricas de la tabla, mientras que las distribuciones, los esquemas y los nombres de las tarjetas son solo atributos.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| `n_lines`, `n_stanzas` | Número de los versos con palabras españolas y de las estrofas | 0 o más | Un texto más largo |
| [`meter`](#meter) | Metro silábico: el nombre del verso por sus sílabas métricas | de `bisílabo` a `octodecasílabo` (`VERSE_METERS`), `None` sin metro | - |
| [`n_feet`](#meter) | Sílabas métricas del metro | 2-18, `None` sin metro | Versos más largos |
| [`p_deviations`](#meter) | Proporción de los versos fuera del metro | 0-0,1, `nan` sin metro | Más versos fuera del metro |
| [`p_pyrrhics`](#pyrrhics) | Proporción de los versos del metro sin sus acentos rítmicos | 0-1, `nan` sin metro | Más versos sin los acentos rítmicos |
| [`p_rhymed`](#rhyme_scheme) | Proporción de los versos con rima | 0-1, `nan` sin versos | Más rimas |
| [`p_masculine`](#clausulas), [`p_feminine`](#clausulas), [`p_dactylic`](#clausulas) | Proporciones de las terminaciones agudas, llanas y esdrújulas | 0-1, `nan` sin versos | Más terminaciones del tipo |

<div class="metric-card" markdown>

### Metro y sílabas métricas { #meter }

`meter` · `n_feet` · `c_feet` · `p_deviations` · Quilis, 1984
{ .metric-meta }

``` {.python .signature}
detect_meter(text)
```

El metro de un poema según el [algoritmo](#algorithm): el nombre del verso por sus sílabas métricas - `octosílabo`, `endecasílabo`, `alejandrino`... (`VERSE_METERS`), y `n_feet` su número de sílabas métricas. `c_feet` es la distribución de los versos por sílabas métricas, y `p_deviations` la proporción de los versos fuera del metro.

El metro es la medida de la mayoría de los versos, y no se determina (`None`) si más de una décima parte de los versos (`VERSE_MAX_DEVIATIONS`) quedan fuera de él tras el ajuste - un poema polimétrico (una silva, un soneto con estrambote de heptasílabos), el verso libre, la prosa - o si el texto tiene un solo verso (`VERSE_MIN_LINES`). Los versos de un poema sin metro se ajustan a sus medidas comunes - las de al menos dos versos y una décima parte de ellos, como las 7 y las 11 sílabas de una lira o una silva - si estas ocupan más de la mitad de los versos; si no, como en el verso libre y la prosa, los versos conservan su lectura llana.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Texto de un poema |

Las excepciones son las de `VerseStats`.

=== "Código"

    ``` python
    from ests.verse_stats import detect_meter

    # El comienzo del Romance del prisionero
    detect_meter(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    # El soneto de Garcilaso del principio de la página
    vs.c_feet, vs.p_deviations
    ```

=== "Resultado"

    ```
    'octosílabo'
    ({11: 4}, 0.0)
    ```

Un verso compuesto se lee por sus hemistiquios, cada uno por la ley del acento final: en el alejandrino de 7 + 7 sílabas *La princesa está pálida* (una esdrújula) y *que ha perdido el color* (una aguda) cuentan 7 cada uno.

=== "Código"

    ``` python
    # La primera estrofa de Sonatina de Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    vs_sonatina = VerseStats(sonatina)
    vs_sonatina.meter, vs_sonatina.n_feet
    vs_sonatina.syllables[3]
    vs_sonatina.patterns[2], vs_sonatina.patterns[3]
    vs_sonatina.stresses[3], vs_sonatina.caesuras
    ```

=== "Resultado"

    ```
    ('alejandrino', 14)
    ('la', 'prin', 'ce', 'sa‿es', 'tá', 'pá', 'li', 'da', 'en', 'su', 'si', 'lla', 'de', 'o', 'ro')
    ('+-+--+-+-+--+-', '--+-++---+--+-')
    ((2, 4, 5, 10, 13), (7, 7, 7, 8, 7, 7))
    ```

</div>

<div class="metric-card" markdown>

### Acentos rítmicos { #pyrrhics }

`p_pyrrhics` · `stress_profile` · `c_rhythms` · Navarro Tomás, 1972
{ .metric-meta }

Los acentos rítmicos (`VERSE_RHYTHMS`) son los que un metro pide además del último, que todo verso tiene por la ley del acento final: el endecasílabo se acentúa en la 6.ª sílaba (a maiore) o en la 4.ª y la 8.ª (sáfico) o la 7.ª (dactílico); un verso compuesto, en el último acento de su primer hemistiquio. `p_pyrrhics` es la proporción de los versos del metro sin ellos, y un metro con solo el último acento, el octosílabo entre otros, tiene `p_pyrrhics` 0.

$$
\frac{\textrm{Número de versos del metro sin sus acentos rítmicos}}{\textrm{Número de versos del metro}}
$$

`stress_profile` es la proporción de los versos del metro acentuados en cada sílaba métrica; las sílabas se cuentan desde cero, así que la 6.ª sílaba es el número 5. Sin metro `p_pyrrhics` es `nan` y el perfil está vacío. `c_rhythms` es la distribución de los endecasílabos por tipo:

| Tipo | Acentos | Nombre |
| :--- | :------ | :----- |
| `1-6-10` | 1.ª, 6.ª | enfático |
| `2-6-10` | 2.ª, 6.ª | heroico |
| `3-6-10` | 3.ª, 6.ª | melódico |
| `4-6-10`, `5-6-10` | el primer acento en la 4.ª o la 5.ª, 6.ª | a maiore |
| `6-10` | 6.ª, sin acento antes | a maiore |
| `4-8-10` | 4.ª, 8.ª, sin 6.ª | sáfico |
| `4-7-10` | 4.ª, 7.ª, sin 6.ª ni 8.ª | dactílico, de gaita gallega |

Un verso con la 6.ª sílaba acentuada toma su tipo de su primer acento; `4-6-10` cuenta como sáfico en algunos tratados. Un verso sin ninguno de los tres conjuntos queda fuera de `c_rhythms` y se cuenta en `p_pyrrhics`.

=== "Código"

    ``` python
    vs.p_pyrrhics, vs.stress_profile
    vs.c_rhythms
    ```

=== "Resultado"

    ```
    (0.0, (0.25, 0.25, 0.25, 1.0, 0.0, 0.25, 0.25, 0.75, 0.0, 1.0, 0.0))
    {'4-8-10': 2, '4-7-10': 1, '3-6-10': 1}
    ```

</div>

<div class="metric-card" markdown>

### Rima { #rhyme_scheme }

`p_rhymed` · `rhyme_schemes` · `c_rhymes`
{ .metric-meta }

``` {.python .signature}
rhyme_scheme(text, seseo=False)
```

El esquema de rima de un poema: los esquemas de las estrofas separados por espacios. El objeto guarda los esquemas por estrofa en `rhyme_schemes`, la proporción de los versos con rima en `p_rhymed` y la distribución de los versos con rima por el tipo de la rima, `consonante` o `asonante`, en `c_rhymes`.

Un verso rima por su terminación desde la última vocal acentuada: en consonante si los sonidos son iguales, en asonante si lo son la vocal acentuada y la última. Los sonidos son los del oído: `b` y `v`, `c` y `z` (`s` con `seseo`), `ll` e `y` son un solo sonido, la `h` es muda, la vibrante simple `r` y la múltiple `rr` se distinguen. La asonancia deja fuera las vocales entre la acentuada y la última (*pálido* - a, o), toma la vocal acentuada de un diptongo (*cielo* - e, o; *gracia* - a, a), lee la `i` y la `u` finales como `e` y `o` (*fácil* - a, e) y da a una aguda solo su vocal acentuada. Un verso rima con los versos de la ventana de `RHYME_WINDOW` (4) versos anteriores, por encima de las estrofas, de modo que los cuartetos de un soneto riman ABBA ABBA.

La asonancia cuenta en dos casos. Un poema cuya rima es la asonancia - al menos un tercio de sus versos sin rima consonante, y al menos cuatro de ellos, comparten una (`RHYME_MIN_ASSONANCE`, `RHYME_MIN_ASSONANT_LINES`) - rima por las asonancias de todos sus versos, que abarcan las rimas consonantes de las mismas vocales, como un soneto asonantado. Si no, la asonancia cuenta en versos alternos con versos sin rima entre ellos: una serie de al menos cuatro versos de dos en dos con tres de cada cuatro de los versos intermedios sin rima consonante (`RHYME_MIN_FREE`), o todos los versos pares de una estrofa de un número par de versos, como el segundo y el cuarto de una copla. Así un romance rima aunque cambie de asonancia de una parte a otra o sus versos asonantes rimen además en consonante de dos en dos. Una asonancia de versos vecinos no es rima: en un soneto de `-ado` y `-ano` los dos grupos se mantienen aparte.

El esquema de rima sigue el uso español: las letras van en el orden de los grupos de rima de todo el poema, mayúsculas para los versos de arte mayor (9 sílabas o más, `VERSE_ARTE_MAYOR`) y minúsculas para los de arte menor, con un guion para un verso sin rima: un soneto es ABBA ABBA CDC DCD, una redondilla abba, una lira aBabB, un romance -a-a-a-a. Cuando se acaban las 26 letras, se vuelve a tomar la letra de un grupo al que ya no puede unirse ningún verso de la ventana.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Texto de un poema |
| `seseo` | `bool` | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima |

Las excepciones son las de `VerseStats`.

=== "Código"

    ``` python
    from ests.verse_stats import rhyme_scheme

    # Sor Juana Inés de la Cruz
    rhyme_scheme(
        "Hombres necios que acusáis\na la mujer sin razón,\nsin ver que sois la ocasión\nde lo mismo que culpáis."
    )
    # El soneto de Garcilaso del principio de la página
    vs.rhyme_schemes, vs.p_rhymed, vs.c_rhymes

    # El comienzo de La tierra de Alvargonzález de Antonio Machado
    romance = """Siendo mozo Alvargonzález,
    dueño de mediana hacienda,
    que en otras tierras se dice
    bienestar y aquí, opulencia,
    en la feria de Berlanga
    prendóse de una doncella,
    y la tomó por mujer
    al año de conocerla."""
    rhyme_scheme(romance), VerseStats(romance).c_rhymes
    ```

=== "Resultado"

    ```
    'abba'
    (('ABBA',), 1.0, {'consonante': 4})
    ('-a-a-a-a', {'asonante': 4})
    ```

</div>

<div class="metric-card" markdown>

### Estrofas y forma { #strophes }

`strophes` · `form`
{ .metric-meta }

Una estrofa se nombra por sus versos, sus medidas, su esquema y su rima (`VERSE_STROPHES`, la primera que encaja), `None` si no encaja ninguna:

| Estrofa | Versos | Medidas | Esquemas | Rima |
| :------ | :----- | :------ | :------- | :--- |
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

Una estrofa de un poema sin metro se ajusta a las sílabas de una estrofa que las pide, de modo que una lira sola recibe sus 7 y 11 sílabas. La forma de un poema es `soneto` para 14 versos de un metro de arte mayor en rima consonante con los cuartetos ABBA o ABAB y los tercetos en rimas propias; `romance` para octosílabos desde 8 versos con tres de cada cuatro de los versos pares de las estrofas en asonante, que puede cambiar, y tres de cada cuatro de los impares sin rima; la estrofa de todas las estrofas; `silva` para heptasílabos y endecasílabos sin metro, más largos que una estrofa (más de 10 versos) y sin un patrón de medidas repetido por todas sus estrofas; si no, `None`.

=== "Código"

    ``` python
    # El soneto I de Garcilaso de la Vega
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
    vs_sonnet = VerseStats(sonnet)
    vs_sonnet.rhyme_schemes, vs_sonnet.strophes, vs_sonnet.form
    vs_sonatina.strophes, VerseStats(romance).form
    ```

=== "Resultado"

    ```
    (('ABBA', 'ABBA', 'CDE', 'DCE'), ('cuarteto', 'cuarteto', 'terceto', 'terceto'), 'soneto')
    (('sexteto',), 'romance')
    ```

</div>

<div class="metric-card" markdown>

### Terminaciones de los versos { #clausulas }

`p_masculine` · `p_feminine` · `p_dactylic` · `c_clausulas`
{ .metric-meta }

El tipo de la terminación (cláusula) de un verso por las sílabas tras su último acento: `aguda` - el acento en la última sílaba, `llana` - una sílaba tras el acento, `esdrújula` - dos, `sobresdrújula` - tres o más (`VERSE_CLAUSULAS`, como [`stress_type`](../syllables.md#stress_type) de una palabra). `c_clausulas` es la distribución de los versos por tipo, y las proporciones se toman sobre todos los versos: `p_masculine` de las agudas, `p_feminine` de las llanas y `p_dactylic` de las esdrújulas.

=== "Código"

    ``` python
    vs.c_clausulas, vs_sonatina.c_clausulas
    vs_sonatina.p_masculine, vs_sonatina.p_feminine
    ```

=== "Resultado"

    ```
    ({'llana': 4}, {'aguda': 2, 'llana': 4})
    (0.3333333333333333, 0.6666666666666666)
    ```

</div>

## Métodos

`accentuate()` devuelve el texto con los acentos marcados: se pone un acento agudo (U+0301) tras la vocal acentuada de cada palabra tónica sin tilde; las palabras con tilde la conservan, y las palabras átonas del verso (`VERSE_PROCLITICS`) quedan sin marca, salvo la última palabra de un verso. Las marcas son caracteres combinantes aparte de las tildes, así que `unicodedata.normalize("NFC", ...)` las convierte en letras acentuadas. Solo se devuelven los versos con palabras españolas (como en `lines`), con las estrofas separadas por una línea en blanco. A diferencia de la función [`accentuate`](#accentuate), la última palabra de un verso siempre es tónica.

=== "Código"

    ``` python
    print(vs.accentuate())
    ```

=== "Resultado"

    ```
    Cuando me páro a contemplár mi estádo
    y a vér los pásos por do me hán traído,
    hállo, según por do andúve perdído,
    que a mayór mál pudiéra habér llegádo.
    ```

Los métodos `get_stats`, `to_dataframe`, `print_stats` y `describe` son los de la [interfaz de las estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS: `get_stats()` devuelve las métricas como un diccionario, y `print_stats()` las muestra como una tabla con sus descripciones (`VERSE_STATS_DESC`), como en el ejemplo del principio de la página. Las estadísticas del verso no tienen escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    vs.get_stats()
    ```

=== "Resultado"

    ```
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

## Algoritmo { #algorithm }

Un verso español se mide por sus sílabas métricas, que no son las sílabas de sus palabras una por una:

1.  **Sílabas y acentos.** Cada palabra se divide en sílabas con [`syllabify`](../syllables.md) y se acentúa por las reglas ortográficas de [`word_stresses`](../syllables.md#word_stresses); un adverbio en `-mente` tiene dos acentos. Las palabras átonas del verso (`VERSE_PROCLITICS`) no llevan acento: los artículos, las preposiciones salvo `según`, las conjunciones, los relativos (`que`, `cual`, `donde`, `como`, `cuanto`), los pronombres clíticos (`me`, `te`, `se`, `le`, `nos`), los posesivos antepuestos (`mi`, `tu`, `su`, `nuestro`, `vuestro`), los tratamientos ante un nombre (`don`, `fray`, `san`), `tan`, `aun` y las interjecciones `oh`, `ay`, `ah`. La última palabra de un verso siempre es tónica.
2.  **La lectura llana.** La vocal final de una palabra y la primera de la siguiente forman una sílaba - la sinalefa (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). La `h` muda la deja pasar (*oh‿al-ma*), mientras que `hi` y `hu` ante vocal (*hierba*, *hueso*) e `y` ante vocal (*ya*, *yo*) son consonantes y la impiden; una consonante al final de la palabra la impide también (*el | al-ma*).
3.  **La ley del acento final.** Un verso cuenta hasta su última sílaba acentuada y una sílaba más: un verso que termina en aguda gana una sílaba (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), uno que termina en esdrújula pierde una (*el pá-ja-ro* - 3).
4.  **El metro.** El metro de un poema es la medida de la mayoría de las lecturas llanas; en caso de empate, desde tres versos, gana la medida empatada con nombre que deja menos versos fuera de ella. Cada verso se ajusta a él con los menos cambios de su lectura llana: un verso más largo une dos vocales de un hiato en una palabra - la sinéresis (*poe-ta*), las que tienen una `i` o una `u` con tilde (*dí-a*) al final; uno más corto deshace sus sinalefas desde el final del verso - el hiato, y después divide un diptongo de una sílaba acentuada - la diéresis (*su-a-ve*, *ru-i-do*). La diéresis escrita marca un hiato (*sü-a-ve*) que ninguna sinéresis une. Un verso que no alcanza el metro conserva su lectura llana y cuenta como fuera de él. Un poema sin metro ajusta en cambio sus versos a sus medidas comunes, si estas ocupan más de la mitad de los versos.
5.  **El verso compuesto.** Un verso compuesto de dos hemistiquios iguales (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) se prueba cuando más de la mitad de las lecturas llanas se dividen en sus hemistiquios y su medida es igual a la de la mayoría de los versos o difiere de ella en una sílaba; gana la lectura con menos versos fuera del metro, el verso compuesto en caso de empate. La cesura cae tras una palabra tónica e impide la sinalefa, y cada hemistiquio sigue la ley del acento final por su cuenta: el alejandrino *La princesa está pálida | en su silla de oro* es 7 + 7.

Sobre los 60 209 versos de los 4259 sonetos de [SpanishSonnets](../datasets/spanishsonnets.md), la medida de un verso coincide con la escansión automática de DISCO en el 97,0% de los versos y con la de [rantanplan](https://github.com/linhd-postdata/rantanplan) en el 97,7%, y el acento de una sílaba métrica de los versos de igual medida en el 97,4% y el 99,6%.

La rima se describe en su [tarjeta](#rhyme_scheme). Frente a la rima automática de DISCO (RhymeTagger), el 99,1% de los pares de versos que riman que encontramos son pares suyos, y encontramos el 97,9% de sus pares.

## Acentuación { #accentuate }

``` {.python .signature}
accentuate(text)
```

Marca los acentos de un texto por las reglas ortográficas: se pone un acento agudo (U+0301) tras la vocal acentuada de cada palabra sin tilde, los dos acentos de un adverbio en `-mente` y de un compuesto con guion; las palabras átonas del verso (`VERSE_PROCLITICS`) quedan sin marca. El texto se normaliza a NFC. Para los versos de un poema, donde la última palabra siempre es tónica, sirve el método `VerseStats.accentuate`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Texto |

=== "Código"

    ``` python
    import unicodedata

    from ests.verse_stats import accentuate

    text = "Yo soy aquel que ayer no más decía el verso azul y la canción profana"
    unicodedata.normalize("NFC", accentuate(text))
    ```

=== "Resultado"

    ```
    'Yó sóy aquél que ayér nó más decía el vérso azúl y la canción profána'
    ```

## Estrofas { #split_stanzas }

``` {.python .signature}
split_stanzas(text)
```

Divide un texto en estrofas y versos: las estrofas se separan por líneas en blanco, y los versos sin una sílaba española (números, asteriscos, otros alfabetos) y los números romanos de las partes de un poema (`II`, `IV.`) se omiten. El texto se normaliza a NFC.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `str` | - | Texto de un poema |

=== "Código"

    ``` python
    from ests.verse_stats import split_stanzas

    split_stanzas(
        "Cuando me paro a contemplar mi estado\n"
        "y a ver los pasos por do me han traído,\n\n* * *\n\n"
        "hallo, según por do anduve perdido,"
    )
    ```

=== "Resultado"

    ```
    [['Cuando me paro a contemplar mi estado', 'y a ver los pasos por do me han traído,'],
     ['hallo, según por do anduve perdido,']]
    ```
