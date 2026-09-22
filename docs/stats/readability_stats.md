# Readability metrics

!!! info ""
    **ests.readability_stats.ReadabilityStats**

## Description

A module for computing the main text [readability](https://en.wikipedia.org/wiki/Readability) metrics of the Spanish tradition. The data source can be a text, a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library, or already computed [basic statistics](basic_stats.md) `BasicStats` - then the text is not parsed again.

!!! quote "Definition"

    Readability is a property of text material characterizing how easily a person perceives it while reading.

    Text readability should be distinguished from the point of view of:

    *   the typographic design of the text;
    *   the linguistic features of the text material (complexity of syntactic constructions, vocabulary hard to perceive, etc.).

Readability in this module is computed from linguistic measures: the mean sentence length in words, the mean word length in syllables or letters, the share of long words and of words with three or more syllables, and the variability of word length. The formulas are the ones published for Spanish, with the coefficients of their sources:

| Formula | Year | Result | Interpretation |
| :------ | :--: | :----- | :------------- |
| Fernández Huerta | 1959 | Flesch reading ease, 0-100 | seven bands of the author |
| Szigriszt-Pazos (fórmula de perspicuidad) | 1993 | Flesch reading ease, 0-100 | INFLESZ scale (Barrio-Cantalejo et al., 2008), five bands |
| Gutiérrez de Polini (fórmula de comprensibilidad) | 1972 | 0-100, higher is easier | no scale of its own; fitted on sixth-grade texts |
| Crawford | 1989 | years of schooling | Spanish primary school, grades 1-6 |
| Legibilidad µ (Muñoz Baquedano and Muñoz Urra) | 2006 | 0-100, higher is easier | seven bands of the authors |
| SOL (Contreras et al.) | 1999 | years of schooling | SMOG converted to Spanish |
| LIX, RIX | 1968, 1983 | index, long words per sentence | language-independent bands and grades |

The Flesch family is set by a preset (see [below](#presets)): by default the coefficients of Szigriszt-Pazos, validated with the INFLESZ scale, and alternatively the coefficients of Fernández Huerta. The other formulas do not depend on the preset.

The main presumptions of readability metrics:

*   short sentences are easier to read than long ones;
*   long words make reading harder;
*   a reader slows down at low-frequency and/or unfamiliar words.

The module allows using pre-built [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) objects for the sentence and word tokenization needed before computing the statistics.

!!! note "Note"
    The metrics are computed by accessing the corresponding attribute or by calling the `get_stats` method of the `ReadabilityStats` object.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc/BasicStats | `-` | Data source (a string, a Doc object or ready basic statistics) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `preset` | str | `general` | Coefficient preset (`general`, `classic`) |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `flesch_reading_easy` | float | Flesch reading ease with the coefficients of the preset |
| `gutierrez_polini_index` | float | Comprehensibility formula of Gutiérrez de Polini |
| `crawford_grade` | float | Crawford formula, years of schooling |
| `mu_index` | float | Legibilidad µ |
| `sol_grade` | float | SOL grade, SMOG converted to Spanish |
| `lix` | float | LIX readability index |
| `rix` | float | RIX readability index |
| `consensus_grade` | float | Consensus grade over the grade formulas and the reading ease |
| `reading_time` | float | Reading time in minutes at 278 words per minute |
| `bs` | BasicStats | Basic text statistics |
| `preset` | str | Name of the coefficient preset |
| `coefficients` | dict[str, tuple[float, float, float]] | Formula coefficients of the preset |

## Coefficient presets { #presets }

A preset sets the coefficients `a`, `b`, `c` of the Flesch reading ease `c − a·ASL − b·ASW`, where ASL is the mean number of words per sentence and ASW the mean number of syllables per word. The other formulas do not depend on the preset.

| Preset | Source | Formula | Scale |
| :----: | :----: | :-----: | :---: |
| `general` | Szigriszt-Pazos (1993), fórmula de perspicuidad | `206.835 − 1.0·ASL − 62.3·ASW` | INFLESZ (Barrio-Cantalejo et al., 2008), validated on texts for patients |
| `classic` | Fernández Huerta (1959), the first adaptation of Flesch to Spanish | `206.84 − 1.02·ASL − 60·ASW` | the seven bands of the author |

Fernández Huerta printed the last term as `1.02` times the number of sentences per 100 words. Law (2011) showed that this inverts the fraction of the Flesch formula the adaptation was based on, so the mean sentence length is used here, as koRpus, textstat and legible.es do. The table of all coefficients is available as `ests.constants.READABILITY_PRESETS`.

!!! example "Example"

    ``` python
    from ests import ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    ReadabilityStats(text).flesch_reading_easy
    # 53.545000000000016
    ReadabilityStats(text, preset="classic").flesch_reading_easy
    # 58.640000000000015
    ```

!!! note "Note"
    Every metric can be computed separately by calling the corresponding function. Detailed information on the readability metrics and the functions used to compute them is available in the corresponding [section](readability_stats_funcs.md).

## Interpretation { #interpretation }

The [`describe_level`](#describe_level) method places the reading ease on a scale: INFLESZ by default (`muy difícil` below 40, `algo difícil` 40-55, `normal` 55-65, `bastante fácil` 65-80, `muy fácil` above 80), the seven bands of Szigriszt-Pazos or of Fernández Huerta on request; Legibilidad µ has the seven bands of its authors (`muy difícil` 0-30, `difícil` 31-50, `un poco difícil` 51-60, `adecuado` 61-70, `un poco fácil` 71-80, `fácil` 81-90, `muy fácil` 91-100).

The formulas that yield years of schooling (Crawford, SOL) are summarized in the `consensus_grade` attribute - the median of the rounded values plus the reading ease converted to a grade through the text types of the INFLESZ bands. The [`describe_grade`](#describe_grade) method translates the consensus grade or an individual formula into a stage of the Spanish school system and reader age:

| Grade | Stage | Age |
| :---: | :---: | :-: |
| 1-3 | primary school, grades 1-3 | 6-9 years |
| 4-6 | primary school, grades 4-6 | 9-12 years |
| 7-10 | ESO | 12-16 years |
| 11-12 | bachillerato | 16-18 years |
| 13-16 | university | 18-22 years |
| above 16 | postgraduate | over 22 years |

!!! warning "Warning"
    Crawford was fitted on primary school readers and saturates for adult texts; SOL was fitted on health education materials. The consensus grade of a technical text mostly reflects the reading ease band.

The `reading_time` attribute estimates silent reading time at 278 words per minute, the mean of six studies of adult readers of Spanish in the meta-analysis of Brysbaert (2019). A different speed is accepted by the [`reading_time_by_speed`](#reading_time_by_speed) method, and the [`reading_time_by_norm`](#reading_time_by_norm) method computes the time aloud and silently by the norms of the `ests.constants.READING_SPEED_NORMS` table: the mean speeds of Spanish-speaking students by school year from the meta-analysis of Ripoll, Tapia and Aguado (2020) and of adults from Brysbaert (2019).

## Methods

### describe_level

Returns the band of a readability scale for the reading ease or Legibilidad µ.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `stat` | str | `flesch_reading_easy` | Name of the metric (`flesch_reading_easy`, `mu_index`) |
| `scale` | str | `None` | Scale for the reading ease (`inflesz` by default, `szigriszt`, `fernandez_huerta`); Legibilidad µ has a single scale and accepts no other |

!!! example "Example"

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

Returns the school stage and reader age for the consensus grade or an individual grade formula.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `stat` | str | `consensus_grade` | Name of the grade formula (`consensus_grade`, `crawford_grade`, `sol_grade`) |

!!! example "Example"

    ``` python
    rs.describe_grade()
    # 'ESO (12-16 years)'
    rs.describe_grade("crawford_grade")
    # 'primary school, grades 4-6 (9-12 years)'
    ```

### reading_time_by_speed

Returns the reading time of the text in minutes at the given speed.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `wpm` | int | `-` | Reading speed, words per minute |

### reading_time_by_norm

Returns the reading time of the text in minutes aloud and silently by a norm of the `ests.constants.READING_SPEED_NORMS` table: `grade_1` to `grade_11` (years of schooling: primary school 1-6, ESO 7-10, bachillerato 11) or `adult`.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `norm` | str | `-` | Name of the reading speed norm |

!!! example "Example"

    ``` python
    rs.reading_time_by_speed(200)
    # 0.05
    rs.reading_time_by_norm("grade_4")
    # (0.09615384615384616, 0.08)
    ```

### get_stats

Returns a dictionary with the computed readability metrics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import ReadabilityStats

    # Prepare the data
    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

    # Compute the metrics
    rs = ReadabilityStats(text)
    rs.get_stats()
    ```

    _Result_:

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

Prints a table with the computed readability metrics.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    rs.print_stats()
    ```

    _Result_:

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
