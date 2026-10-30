# Formulas of other languages

``` {.python .signature}
UnadaptedReadabilityStats(source, sents_extractor=None, words_extractor=None)
```

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats"

The class extends the `UnadaptedReadabilityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/unadapted_readability_stats/) core with the [basic statistics](basic_stats.md) of esTS, which count the syllables and the letters of Spanish words and take the Spanish [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) by default. The `print_stats` table takes the English descriptions of the core, `anyts.constants.UNADAPTED_READABILITY_STATS_DESC`. A string with a character without a UTF-8 form raises `SourceError` as well.

The formulas are not calibrated for Spanish. Their values serve to compare Spanish texts with each other and with the results of these formulas in other tools, but they give no Spanish grade: a Spanish word has more syllables than the English ones the formulas were fitted on, so the formulas of syllables read a Spanish text as harder - on 60 windows of 1000 words of the prose of the [corpus of literature](../datasets/spanishliterature.md), with 1.96 syllables per word, the median FORCAST is 13.2 and the median Linsear Write 13.7, against a [consensus grade](readability_stats.md#consensus_grade) of 5.0 of the Spanish formulas. These formulas therefore have no reading scales, `describe` gives `None` for them, and they do not enter the consensus grade. The formulas with coefficients for Spanish are in [`ReadabilityStats`](readability_stats.md).

In Spanish the words without syllables are the numbers and the abbreviations without a vowel (`Sr`, `pst`); the conjunctions `y` and `e` and the preposition `a` have one syllable.

=== "Code"

    ``` python
    from ests import UnadaptedReadabilityStats

    text = (
        "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, "
        "cuándo empezar labores"
    )
    urs = UnadaptedReadabilityStats(text)
    urs.print_stats()
    ```

=== "Result"

    ```
               Metric            |  Value
    ----------------------------------------
    FORCAST grade                |  17.00
    Linsear Write grade          |  10.50
    Powers-Sumner-Kearl grade    |   8.37
    McAlpine EFLAW score         |  17.00
    Wiener Sachtextformel 1      |   7.44
    Wiener Sachtextformel 2      |   6.50
    Wiener Sachtextformel 3      |   7.67
    Wiener Sachtextformel 4      |   7.78
    Dickes-Steiwer index         |  30.42
    Gulpease index               |  56.33
    Fucks index                  |  31.00
    Strain index                 |   9.30
    Easy listening formula (ELF) |  16.00
    Wheeler-Smith index          |  120.00
    ```

## Parameters

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-parameters"

## Attributes

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-attributes"

Ready basic statistics can be taken from a [`ReadabilityStats`](readability_stats.md) object, so as not to compute them again:

=== "Code"

    ``` python
    from ests import ReadabilityStats

    rs = ReadabilityStats(text)
    urs = UnadaptedReadabilityStats(rs.bs)
    urs.bs is rs.bs, urs.forcast
    ```

=== "Result"

    ```
    (True, 17.0)
    ```

## Metrics

--8<-- "stats/unadapted_readability_stats.md:UnadaptedReadabilityStats-metrics"

Here ASL is the mean number of words per sentence, ASW the mean number of syllables per word. The functions of the formulas are imported from `ests.unadapted_readability_stats` and compute a value from counts:

=== "Code"

    ``` python
    from ests.unadapted_readability_stats import calc_forcast, calc_gulpease

    calc_forcast(n_monosyllable_words=30, n_words=150)
    calc_gulpease(n_letters=550, n_words=100, n_sents=8)
    ```

=== "Result"

    ```
    17.0
    58.0
    ```

<div class="metric-card" markdown>

### FORCAST { #forcast }

`forcast` · Caylor et al., 1973
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_forcast"

</div>

<div class="metric-card" markdown>

### Linsear Write { #linsear_write }

`linsear_write`
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_linsear_write"

</div>

<div class="metric-card" markdown>

### Powers-Sumner-Kearl grade { #powers_sumner_kearl }

`powers_sumner_kearl` · [Powers et al., 1958](https://doi.org/10.1037/h0043254)
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_powers_sumner_kearl"

</div>

<div class="metric-card" markdown>

### McAlpine EFLAW { #eflaw }

`eflaw` · McAlpine, 2005
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_eflaw"

</div>

<div class="metric-card" markdown>

### Wiener Sachtextformel { #wiener_sachtextformel }

`wiener_sachtextformel_1` · `wiener_sachtextformel_2` · `wiener_sachtextformel_3` · `wiener_sachtextformel_4` · Bamberger and Vanecek, 1984
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_wiener_sachtextformel"

</div>

<div class="metric-card" markdown>

### Dickes-Steiwer index { #dickes_steiwer }

`dickes_steiwer` · Dickes and Steiwer, 1977
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_dickes_steiwer"

</div>

<div class="metric-card" markdown>

### Gulpease index { #gulpease }

`gulpease` · Lucisano and Piemontese, 1988
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_gulpease"

</div>

<div class="metric-card" markdown>

### Fucks index { #fucks }

`fucks` · Fucks, 1955
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_fucks"

</div>

<div class="metric-card" markdown>

### Strain index { #strain_index }

`strain_index` · Nathaniel, 2009
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_strain_index"

</div>

<div class="metric-card" markdown>

### Easy listening formula { #elf }

`elf` · [Fang, 1966](https://doi.org/10.1080/08838156609363529)
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_elf"

</div>

<div class="metric-card" markdown>

### Wheeler-Smith index { #wheeler_smith }

`wheeler_smith` · Wheeler and Smith, 1954
{ .metric-meta }

--8<-- "stats/unadapted_readability_stats.md:calc_wheeler_smith"

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the formulas have no scales, and `describe` gives `None` for any of them.

=== "Code"

    ``` python
    urs = UnadaptedReadabilityStats(text)
    urs.describe("forcast"), urs.describe("gulpease")
    urs.get_stats()
    ```

=== "Result"

    ```
    (None, None)
    {'forcast': 17.0,
     'linsear_write': 10.5,
     'powers_sumner_kearl': 8.367433333333333,
     'eflaw': 17.0,
     'wiener_sachtextformel_1': 7.443000000000001,
     'wiener_sachtextformel_2': 6.504,
     'wiener_sachtextformel_3': 7.6691,
     'wiener_sachtextformel_4': 7.779,
     'dickes_steiwer': 30.42186181527815,
     'gulpease': 56.333333333333336,
     'fucks': 31.0,
     'strain_index': 9.3,
     'elf': 16.0,
     'wheeler_smith': 120.0}
    ```
