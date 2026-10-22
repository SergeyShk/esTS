# Readability metrics

``` {.python .signature}
ReadabilityStats(source, sents_extractor=None, words_extractor=None, preset='general')
```

--8<-- "stats/readability_stats.md:ReadabilityStats"

The metrics assess readability on the side of the language - the complexity of words and syntactic constructions, not the typographic design of the text. They presume that short sentences are easier to read than long ones, long words make reading harder, and low-frequency and unfamiliar words slow a reader down.

The class extends the `ReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/readability_stats/) core with the formulas and tables of Spanish, given in the cards of the metrics: the [basic statistics](basic_stats.md) of esTS, which take the Spanish [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default, the coefficient [presets](#presets) of the Flesch reading ease, the formulas of Gutiérrez de Polini, Crawford and SOL, the consensus grade over Crawford and SOL, the school stages of Spain, the interpretation scales and the reading speeds of Spanish readers.

=== "Code"

    ``` python
    from ests import ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    rs = ReadabilityStats(text)
    rs.print_stats()
    ```

=== "Result"

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

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` / `BasicStats` | - | Data source (a string, a Doc object or ready basic statistics) |
| `sents_extractor` | `SentsExtractor` | `None` | Sentence extraction tool |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool |
| `preset` | `str` | `'general'` | Coefficient preset: `general` or `classic` |

The object keeps the basic statistics of the text in `bs`, the name of the preset in `preset`, read-only, and the coefficients of the preset by formula in `coefficients`, a copy that can be changed for one object. An object of another preset can reuse the basic statistics: `ReadabilityStats(rs.bs, preset="classic")`.

## Coefficient presets { #presets }

A preset sets the coefficients `a`, `b`, `c` of the Flesch reading ease `c − a·ASL − b·ASW`, where ASL is the mean number of words per sentence and ASW the mean number of syllables per word, and the scale by which `describe_level`, `describe` and the consensus grade read it. The other formulas do not depend on the preset.

| Preset | Source | Formula | Scale |
| :----- | :----- | :------ | :---- |
| `general` | Szigriszt-Pazos (1993), fórmula de perspicuidad | `206.835 − 1.0·ASL − 62.3·ASW` | INFLESZ (Barrio-Cantalejo et al., 2008) |
| `classic` | Fernández Huerta (1959) | `206.84 − 1.02·ASL − 60·ASW` | the seven bands of the author |

The formula of Fernández Huerta takes the mean sentence length, with the correction of Law (2011). The table of all coefficients is `ests.constants.READABILITY_PRESETS`, and the scale of each preset is in `PRESET_SCALES`.

=== "Code"

    ``` python
    classic = ReadabilityStats(rs.bs, preset="classic")
    rs.flesch_reading_easy, classic.flesch_reading_easy
    rs.describe_level(), classic.describe_level()
    ```

=== "Result"

    ```
    (53.545000000000016, 58.640000000000015)
    ('algo difícil', 'bastante difícil')
    ```

## Metrics

A formula is computed by the function of its card on the counts of `bs`. The reading ease takes its coefficients from `coefficients`, set by the preset; the formulas of Gutiérrez de Polini, Crawford and SOL are computed with the coefficients of their functions, and `coefficients` does not affect them. A formula of counts gives `nan` when the number of words or of sentences it divides by is zero.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| [`flesch_reading_easy`](#flesch_reading_easy) | Ease of reading by the sentence length and the syllables per word | Nominally 0-100, above 100 for the simplest texts and below 0 for the hardest | An easier text |
| [`gutierrez_polini_index`](#gutierrez_polini_index) | Comprehensibility by the letters per word and the sentence length | Below 95.2, ordinary prose 30-50 | An easier text |
| [`crawford_grade`](#crawford_grade) | Grade by the sentences and the syllables per 100 words | Years of schooling, fitted on grades 1-6 | A harder text |
| [`mu_index`](#mu_index) | Mean word length in letters against its variance | Above 0, `nan` with fewer than two words or without variability | An easier text |
| [`sol_grade`](#sol_grade) | Grade by the polysyllabic words per sentence, SMOG converted to Spanish | Years of schooling | A harder text |
| [`lix`](#lix) | Sentence length and the share of long words | 0 and above | A harder text |
| [`rix`](#rix) | Long words per sentence | 0 and above | A harder text |
| [`consensus_grade`](#consensus_grade) | Median of the grade formulas and the reading ease as a grade | Years of schooling | A harder text |
| [`reading_time`](#reading_time) | Reading time at the reading speed (`reading_speed`) | Minutes, above 0 | A longer text |
| [`smog_index`](#smog_index) | Grade by the polysyllabic words per sentence, English coefficients; outside `get_stats` | Years of schooling | A harder text |

The other formulas of the core with their English coefficients - `flesch_kincaid_grade`, `coleman_liau_index`, `automated_readability_index` and `gunning_fog_index` - are properties of the object outside `get_stats` as well, since they are fitted on English texts; their cards are on the [anyTS page](https://sergeyshk.github.io/anyTS/stats/readability_stats/).

<div class="metric-card" markdown>

### Flesch reading ease { #flesch_reading_easy }

`flesch_reading_easy` · Szigriszt-Pazos, 1993 · Fernández Huerta, 1959
{ .metric-meta }

``` {.python .signature}
calc_flesch_reading_easy(n_syllables, n_words, n_sents, a=1.0, b=62.3, c=206.835)
```

--8<-- "stats/readability_stats.md:calc_flesch_reading_easy"

The default coefficients are those of the *fórmula de perspicuidad* of Szigriszt-Pazos (1993). The coefficients of Fernández Huerta (1959) are given by the `classic` [preset](#presets), with the correction of Law (2011): the last term takes the mean sentence length, not the number of sentences per 100 words that Fernández Huerta printed.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Number of syllables |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `1.0` | Coefficient a, at the mean sentence length |
| `b` | `float` | `62.3` | Coefficient b, at the mean word length in syllables |
| `c` | `float` | `206.835` | Coefficient c, the constant |

The scale of `describe_level` and `describe` follows the preset: the `level_scale` method of esTS gives the scale of `ests.constants.READING_EASE_SCALES` named in `PRESET_SCALES` - the INFLESZ scale of Barrio-Cantalejo et al. (2008) for `general` and the bands of Fernández Huerta for `classic`. The INFLESZ scale:

| Value | Level | Text type |
| :---- | :---- | :-------- |
| `[80, ∞)` | muy fácil | comics, children's books |
| `[65, 80)` | bastante fácil | primary school textbooks |
| `[55, 65)` | normal | general press |
| `[40, 55)` | algo difícil | secondary school textbooks |
| `(−∞, 40)` | muy difícil | scientific and technical texts |

``` {.python .signature}
flesch_reading_easy_to_level(flesch_reading_easy, scale='inflesz')
```

The band of a scale of `READING_EASE_SCALES` for the reading ease: `inflesz` (above), `szigriszt` (Szigriszt-Pazos, 1993, integer bands: `muy difícil` 0-15, `árido` 16-35, `bastante difícil` 36-50, `normal` 51-65, `bastante fácil` 66-75, `fácil` 76-85, `muy fácil` 86-100) and `fernandez_huerta` (Fernández Huerta, 1959: `muy difícil` below 30, `difícil` 30-50, `bastante difícil` 50-60, `normal` 60-70, `bastante fácil` 70-80, `fácil` 80-90, `muy fácil` above 90). The `describe_level` method reads the reading ease of the object by any of them with its `scale` parameter.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `flesch_reading_easy` | `float` | - | Value of the reading ease |
| `scale` | `str` | `'inflesz'` | Name of the scale: `inflesz`, `szigriszt` or `fernandez_huerta` |

Raises:

- `ParameterError` - an unknown scale or one that is not a string, a value that is not a finite number.

=== "Code"

    ``` python
    from ests.readability_stats import flesch_reading_easy_to_level

    flesch_reading_easy_to_level(53.5), flesch_reading_easy_to_level(53.5, "szigriszt")
    ```

=== "Result"

    ```
    ('algo difícil', 'normal')
    ```

Sources: Szigriszt Pazos, F. *Sistemas predictivos de legibilidad del mensaje escrito: fórmula de perspicuidad*. Universidad Complutense de Madrid, 1993. Barrio-Cantalejo, I. M. et al. Validación de la Escala INFLESZ para evaluar la legibilidad de los textos dirigidos a pacientes. *Anales del Sistema Sanitario de Navarra*, 31(2), 2008. Fernández Huerta, J. Medidas sencillas de lecturabilidad. *Consigna*, 214, 1959. Law, G. Error in the Fernández Huerta readability formula. *LINGUIST List* 22.2332, 2011.

</div>

<div class="metric-card" markdown>

### Gutiérrez de Polini comprehensibility { #gutierrez_polini_index }

`gutierrez_polini_index` · Gutiérrez de Polini, 1972
{ .metric-meta }

``` {.python .signature}
calc_gutierrez_polini_index(n_letters, n_words, n_sents)
```

The *fórmula de comprensibilidad* of Gutiérrez de Polini, by the mean word length in letters and the mean sentence length. The higher the value, the easier the text. It was fitted on sixth-grade school texts and has no scale of its own: ordinary prose lies between 30 and 50, and a text above 70 is read by a young child.

$$
95.2 - 9.7 \cdot \frac{\textrm{Number of letters}}{\textrm{Number of words}} - 0.35 \cdot \frac{\textrm{Number of words}}{\textrm{Number of sentences}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_letters` | `int` | - | Number of letters of the words |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |

=== "Code"

    ``` python
    from ests.readability_stats import calc_gutierrez_polini_index

    calc_gutierrez_polini_index(n_letters=60, n_words=10, n_sents=1)
    ```

=== "Result"

    ```
    33.5
    ```

Source: Gutiérrez de Polini, L. E. *Investigación sobre lectura en Venezuela*. Ministerio de Educación, Caracas, 1972.

</div>

<div class="metric-card" markdown>

### Crawford grade { #crawford_grade }

`crawford_grade` · Crawford, 1989
{ .metric-meta }

``` {.python .signature}
calc_crawford_grade(n_syllables, n_words, n_sents)
```

The years of schooling needed to read the text, by the sentences and the syllables per 100 words. The formula was fitted on Spanish primary school readers of grades 1-6, so higher values saturate. The higher the value, the harder the text.

$$
-0.205 \cdot \frac{100 \cdot \textrm{Number of sentences}}{\textrm{Number of words}} + 0.049 \cdot \frac{100 \cdot \textrm{Number of syllables}}{\textrm{Number of words}} - 3.407
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_syllables` | `int` | - | Number of syllables |
| `n_words` | `int` | - | Number of words |
| `n_sents` | `int` | - | Number of sentences |

=== "Code"

    ``` python
    from ests.readability_stats import calc_crawford_grade

    calc_crawford_grade(n_syllables=23, n_words=10, n_sents=1)
    ```

=== "Result"

    ```
    5.812999999999999
    ```

Source: Crawford, A. N. Fórmula y gráfico para determinar la comprensibilidad de textos del nivel primario en castellano. *Lectura y Vida*, 10(4), 1989.

</div>

<div class="metric-card" markdown>

### Legibilidad µ { #mu_index }

`mu_index` · Muñoz Baquedano and Muñoz Urra, 2006
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_mu_index"

The variance divided by `n − 1` is the *cuasivarianza* of the authors, which reproduces the worked example of their manual; `ReadabilityStats` passes `BasicStats.c_letters`. The bands of the authors, `ests.constants.MU_SCALE`, are the scale of `describe_level` and `describe`:

| Value | Level |
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

The band of the scale `MU_SCALE` for a value of Legibilidad µ.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `mu_index` | `float` | - | Value of Legibilidad µ |

Raises:

- `ParameterError` - a value that is not a finite number, such as the undefined index (`nan`).

=== "Code"

    ``` python
    from ests import BasicStats
    from ests.readability_stats import calc_mu_index, mu_to_level

    mu = calc_mu_index(BasicStats(text).c_letters)
    mu, mu_to_level(mu)
    ```

=== "Result"

    ```
    (50.943396226415096, 'difícil')
    ```

Source: Muñoz Baquedano, M. Legibilidad y variabilidad de los textos. *Boletín de Investigación Educacional*, 21(2), 2006; the program and manual at [legibilidadmu.cl](https://www.legibilidadmu.cl/).

</div>

<div class="metric-card" markdown>

### SOL grade { #sol_grade }

`sol_grade` · Contreras et al., 1999
{ .metric-meta }

``` {.python .signature}
calc_sol_grade(n_complex, n_sents, a=0.74, b=-2.51)
```

The years of schooling needed to read a Spanish text: the conversion of Contreras et al. of its [SMOG index](#smog_index) `S`, computed with the original coefficients, into the grade of the English scale. The higher the value, the harder the text. `ReadabilityStats` passes the number of words of three or more syllables.

$$
b + a \cdot S
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of words of three or more syllables |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `0.74` | Coefficient a, at the SMOG index |
| `b` | `float` | `-2.51` | Coefficient b, the constant |

Raises:

- `ParameterError` - a number of words or sentences that is not a non-negative integer.

=== "Code"

    ``` python
    from ests.readability_stats import calc_smog_index, calc_sol_grade

    calc_smog_index(n_complex=5, n_sents=1), calc_sol_grade(n_complex=5, n_sents=1)
    ```

=== "Result"

    ```
    (15.903189008614273, 9.258359866374562)
    ```

Source: Contreras, A., García-Alonso, R., Echenique, M., Daye-Contreras, F. The SOL formulas for converting SMOG readability scores between health education materials written in Spanish, English, and French. *Journal of Health Communication*, 4(1), 1999.

</div>

<div class="metric-card" markdown>

### LIX readability index { #lix }

`lix` · Björnsson, 1968
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_lix"

These bands, `anyts.constants.LIX_LEVELS` with English labels, are the scale of `describe_level` and `describe`; its last band is open above.

</div>

<div class="metric-card" markdown>

### RIX readability index { #rix }

`rix` · Anderson, 1983
{ .metric-meta }

--8<-- "stats/readability_stats.md:calc_rix"

In esTS RIX has no scale of bands, so `describe_level("rix")` raises `ParameterError`; `describe` takes the grades of Anderson as years of schooling (`anyts.constants.RIX_GRADES`, college as 13) and gives the stage of the Spanish school system and the reader age by [`grade_to_age`](#grade_to_age).

</div>

<div class="metric-card" markdown>

### Consensus grade { #consensus_grade }

`consensus_grade`
{ .metric-meta }

--8<-- "stats/readability_stats.md:ReadabilityStats-consensus"

The grade formulas of esTS (`ests.constants.READABILITY_GRADE_STATS`) are Crawford and SOL. esTS converts the reading ease by the scale of the preset with its own `reading_ease_to_grade(flesch_reading_easy)` method, which calls `flesch_reading_easy_to_grade` with the preset of the object, so the `reading_ease_grades` of the core are not used.

!!! warning "Warning"
    Crawford was fitted on primary school readers and saturates for adult texts; SOL was fitted on health education materials. The consensus grade of a technical text mostly reflects the reading ease band.

``` {.python .signature}
calc_consensus_grade(grades, flesch_reading_easy=None, preset='general')
```

The median of the values of the grade formulas rounded half up, together with the reading ease converted into years of schooling by `flesch_reading_easy_to_grade` with the scale of the preset, not rounded.

$$
\textrm{median}\left(\lfloor g_1 + 0.5 \rfloor, \ldots, \lfloor g_k + 0.5 \rfloor, \textrm{grade}(\textrm{reading ease})\right)
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `grades` | `list[float]` | - | Values of the grade formulas |
| `flesch_reading_easy` | `float` | `None` | Value of the reading ease |
| `preset` | `str` | `'general'` | Coefficient preset of the reading ease |

Raises:

- `ParameterError` - no values at all, a grade or a reading ease that is not a finite number, an unknown preset or one that is not a string;
- `SourceTypeError` - grades that are not a list.

``` {.python .signature}
flesch_reading_easy_to_grade(flesch_reading_easy, preset='general')
```

Conversion of the Flesch reading ease into years of schooling for the consensus grade by the bands of the scale of the preset, `ests.constants.READING_EASE_GRADES`: the grade of the first band whose lower bound the value reaches, or 13 below the last bound; values above 100 belong to the first band. With the `general` preset, through the text types of the INFLESZ bands and the school stages of Spain:

| Reading ease | Grade | Text type |
| :----------- | :---- | :-------- |
| `[80, ∞)` | 3 | comics and children's books, primary school grades 1-3 |
| `[65, 80)` | 5 | primary school textbooks, grades 4-6 |
| `[55, 65)` | 8 | general press, ESO |
| `[40, 55)` | 11 | secondary school textbooks, bachillerato |
| `(−∞, 40)` | 13 | scientific texts, university |

With the `classic` preset, through the interpretation table of Flesch kept by Fernández Huerta: `90-100` - 5, `80-90` - 6, `70-80` - 7, `60-70` - 8.5, `50-60` - 10, `40-50` - 11, `30-40` - 12, below `30` - 13.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `flesch_reading_easy` | `float` | - | Value of the reading ease |
| `preset` | `str` | `'general'` | Coefficient preset whose scale is read |

Raises:

- `ParameterError` - a reading ease that is not a finite number (the `nan` of a text without words or sentences, an infinity), an unknown preset or one that is not a string.

=== "Code"

    ``` python
    from ests.readability_stats import calc_consensus_grade, flesch_reading_easy_to_grade

    flesch_reading_easy_to_grade(53.545), flesch_reading_easy_to_grade(53.545, "classic")
    calc_consensus_grade([5.813, 9.258], 53.545)
    ```

=== "Result"

    ```
    (11, 10)
    9.0
    ```

</div>

<div class="metric-card" markdown>

### Reading time { #reading_time }

`reading_time` · `reading_time_by_speed(wpm)` · `reading_time_by_norm(norm)` · Brysbaert, 2019 · Ripoll, Tapia and Aguado, 2020
{ .metric-meta }

``` {.python .signature}
calc_reading_time(n_words, wpm=278)
```

--8<-- "stats/readability_stats.md:calc_reading_time"

The default speed is the silent reading speed of adults in Spanish, 278 words per minute, from the meta-analysis of Brysbaert (2019). The norms of `reading_time_by_norm`, `ests.constants.READING_SPEED_NORMS`, are the mean speeds of Spanish-speaking students by school year from the meta-analysis of Ripoll, Tapia and Aguado (2020) - `grade_1` to `grade_11`, that is primary school 1-6, ESO 7-10 and bachillerato 11 - and of adults from Brysbaert (2019), as pairs (aloud, silent):

| Norm | Aloud | Silent |
| :--- | :---- | :----- |
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

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_words` | `int` | - | Number of words |
| `wpm` | `float` | `278` | Reading speed, words per minute (`READING_SPEED_WPM`) |

Sources: Brysbaert, M. How many words do we read per minute? A review and meta-analysis of reading rate. *Journal of Memory and Language*, 109, 2019. Ripoll, J. C., Tapia, M. M., Aguado, G. Velocidad lectora en alumnado hispanohablante: un metaanálisis. *Revista de Psicodidáctica*, 25(2), 2020.

</div>

<div class="metric-card" markdown>

### SMOG index { #smog_index }

`smog_index` · McLaughlin, 1969
{ .metric-meta }

``` {.python .signature}
calc_smog_index(n_complex, n_sents, a=1.043, b=30, c=3.1291)
```

--8<-- "stats/readability_stats.md:calc_smog_index"

The index is fitted on English and stays outside `get_stats`; for Spanish it is the input of the [SOL grade](#sol_grade). `ReadabilityStats` passes the number of words of three or more syllables.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `n_complex` | `int` | - | Number of polysyllabic words |
| `n_sents` | `int` | - | Number of sentences |
| `a` | `float` | `1.043` | Coefficient a, at the square root |
| `b` | `float` | `30` | Coefficient b, the number of sentences of the sample |
| `c` | `float` | `3.1291` | Coefficient c, the constant |

</div>

## Methods

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_grade"

The grade formulas of esTS are `crawford_grade` and `sol_grade`.

--8<-- "stats/readability_stats.md:ReadabilityStats-describe_level"

In esTS the metrics with a scale of bands are `flesch_reading_easy`, `mu_index` and `lix`, and `describe_level(stat, scale)` also takes a `scale` of `READING_EASE_SCALES` for the reading ease - `inflesz`, `szigriszt` or `fernandez_huerta` - in place of the scale of the preset, `None` by default; a scale given for another metric and an unknown scale raise `ParameterError`. `level_scale(stat)` returns the scale of a metric as lower bounds and their bands - for the reading ease the scale of the preset - or `None` for a metric without a scale of bands, RIX included.

--8<-- "stats/readability_stats.md:ReadabilityStats-describe"

In esTS the grade formulas are read as stages of the Spanish school system, and so is RIX through the grades of Anderson; the formula of Gutiérrez de Polini, the reading time and the formulas of the core with their English coefficients have no scale.

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_speed"

--8<-- "stats/readability_stats.md:ReadabilityStats-reading_time_by_norm"

The norms of esTS give the speeds aloud and silently, so the method returns the reading times aloud and silently.

--8<-- "stats/readability_stats.md:ReadabilityStats-get_stats"

--8<-- "stats/readability_stats.md:ReadabilityStats-print_stats"

=== "Code"

    ``` python
    rs.describe_grade(), rs.describe_grade("crawford_grade")
    rs.describe_level(scale="szigriszt"), rs.describe_level("mu_index")
    rs.level_scale("flesch_reading_easy")
    rs.reading_time_by_speed(200), rs.reading_time_by_norm("grade_4")
    {stat: rs.describe(stat) for stat in rs.get_stats()}
    rs.get_stats()
    ```

=== "Result"

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

The `to_dataframe` method is that of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core.

## Scales { #scales }

The `describe_level` method reads the reading ease, Legibilidad µ and LIX by the scales of bands of their cards, and `describe` reads any metric: these three by the same scales, the grade formulas, the consensus grade and RIX by the school stages of [`grade_to_age`](#grade_to_age); for a metric without a scale it gives `None`.

### School stage and age { #grade_to_age }

``` {.python .signature}
grade_to_age(grade)
```

The stage of the Spanish school system and the reader age by the value of a grade formula, in years of schooling counted from the first year of primary school at the age of six: the value is rounded half up and falls into the first stage whose last year it does not exceed, values below 1 into grades 1-3. The stages are `ests.constants.GRADE_AGE_LEVELS` and `POSTGRADUATE_LEVEL`:

| Grade | Stage | Age |
| :---- | :---- | :-- |
| 1-3 | primary school, grades 1-3 | 6-9 years |
| 4-6 | primary school, grades 4-6 | 9-12 years |
| 7-10 | ESO | 12-16 years |
| 11-12 | bachillerato | 16-18 years |
| 13-16 | university | 18-22 years |
| above 16 | postgraduate | over 22 years |

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `grade` | `float` | - | Value of a grade formula |

Raises:

- `ParameterError` - a grade that is not a finite number.

=== "Code"

    ``` python
    from ests.readability_stats import grade_to_age

    grade_to_age(9.0), grade_to_age(17)
    ```

=== "Result"

    ```
    ('ESO (12-16 years)', 'postgraduate (over 22 years)')
    ```

### Band of a scale { #scale_level }

--8<-- "stats/readability_stats.md:scale_level"

The scales of esTS are `READING_EASE_SCALES` and `MU_SCALE` of `ests.constants`; LIX is read by the `LIX_LEVELS` of the core.

=== "Code"

    ``` python
    from ests.constants import MU_SCALE, READING_EASE_SCALES
    from ests.readability_stats import scale_level

    scale_level(50.9, MU_SCALE), scale_level(50.9, READING_EASE_SCALES["fernandez_huerta"])
    ```

=== "Result"

    ```
    ('difícil', 'bastante difícil')
    ```
