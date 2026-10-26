# Lexical diversity metrics

``` {.python .signature}
DiversityStats(source, words_extractor=None, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

--8<-- "stats/diversity_stats.md:DiversityStats"

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type;
- `SourceError` - a source without words, a string with a character without a UTF-8 form;
- `ParameterError` - a parameter that `check_params` rejects.

The class extends the `DiversityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/) core: instead of a list of words it takes a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library. The words of a text are extracted by the Spanish [`WordsExtractor`](../extractors/words.md) or by a given one, which for a `Doc` is applied to its text; without an extractor the words of a `Doc` come from its tokens. The words are always lower-cased, since every metric counts lexemes. The `print_stats` table has the English descriptions of the metrics of the core, `anyts.constants.DIVERSITY_STATS_DESC`.

=== "Code"

    ``` python
    from ests import DiversityStats

    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
    ds = DiversityStats(text)
    ds.print_stats()
    ```

=== "Result"

    ```
                                    Metric                                 |  Value
    ----------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                 |   0.73
    Root Type-Token Ratio (RTTR)                                           |   2.84
    Corrected Type-Token Ratio (CTTR)                                      |   2.01
    Herdan Type-Token Ratio (HTTR)                                         |   0.89
    Summer Type-Token Ratio (STTR)                                         |   0.25
    Maas Type-Token Ratio (MTTR)                                           |   0.10
    Dugast Type-Token Ratio (DTTR)                                         |  10.27
    Moving Average Type-Token Ratio (MATTR)                                |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                |   0.73
    Measure of Textual Lexical Diversity (MTLD)                            |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)          |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W) |  13.25
    Hypergeometric Distribution D (HD-D)                                   |   nan
    Simpson's index (D)                                                    |   0.05
    Inverse Simpson's index (1/D)                                          |  21.00
    Gini-Simpson index (1-D)                                               |   0.95
    Hapax index (Honoré's R)                                               |  992.95
    Yule's characteristic K                                                |  444.44
    Yule's inverse characteristic I                                        |   8.64
    Herdan's Vm                                                            |   0.14
    Sichel's S                                                             |   0.18
    Michéa's M                                                             |   5.50
    Brunet's W                                                             |   6.01
    Dugast's k                                                             |  14.78
    Baayen's P                                                             |   0.53
    Orlov's Z (words)                                                      |   nan
    Hapax ratio                                                            |   0.73
    Exponent α₂                                                            |   0.50
    Shannon entropy (bits)                                                 |   3.32
    Evenness                                                               |   0.96
    Perplexity                                                             |  10.01
    Zipf's law slope (α)                                                   |   0.49
    Heaps' law exponent (β)                                                |   0.84
    Burstiness of the frequent lexemes                                     |   nan
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; for a `Doc` it is applied to its text |
| `window_len` | `int` | `50` | Window size for MATTR and segment size for MSTTR (`MATTR_WINDOW_LEN`) |
| `mtld_threshold` | `float` | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W (`MTLD_TTR_THRESHOLD`) |
| `mtld_min_len` | `int` | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W (`MTLD_MIN_LEN`) |
| `hdd_sample_size` | `int` | `42` | Sample size for HD-D (`HDD_SAMPLE_SIZE`) |
| `log_base` | `float` | `10` | Logarithm base for the Summer, Maas and Dugast metrics (`DIVERSITY_LOG_BASE`) |

The constants of the defaults in parentheses, here and in the cards, are those of `anyts.constants`.

--8<-- "stats/diversity_stats.md:DiversityStats-attributes"

``` {.python .signature}
check_params(window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10, *, messages=MESSAGES)
```

--8<-- "stats/diversity_stats.md:check_params"

## Conventions { #conventions }

--8<-- "stats/diversity_stats.md:DiversityStats-conventions"

## Metrics

--8<-- "stats/diversity_stats.md:DiversityStats-metrics"

The functions and the named tuples of the cards are imported from `ests.diversity_stats`.

<div class="metric-card" markdown>

### Type-Token Ratio (TTR) { #ttr }

`ttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_ttr"

</div>

<div class="metric-card" markdown>

### Root Type-Token Ratio (RTTR) { #rttr }

`rttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_rttr"

</div>

<div class="metric-card" markdown>

### Corrected Type-Token Ratio (CTTR) { #cttr }

`cttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_cttr"

</div>

<div class="metric-card" markdown>

### Herdan Type-Token Ratio (HTTR) { #httr }

`httr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_httr"

</div>

<div class="metric-card" markdown>

### Summer Type-Token Ratio (STTR) { #sttr }

`sttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_sttr"

</div>

<div class="metric-card" markdown>

### Maas Type-Token Ratio (MTTR) { #mttr }

`mttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mttr"

</div>

<div class="metric-card" markdown>

### Dugast Type-Token Ratio (DTTR) { #dttr }

`dttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_dttr"

</div>

<div class="metric-card" markdown>

### Moving Average Type-Token Ratio (MATTR) { #mattr }

`mattr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mattr"

</div>

<div class="metric-card" markdown>

### Mean Segmental Type-Token Ratio (MSTTR) { #msttr }

`msttr`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_msttr"

</div>

<div class="metric-card" markdown>

### Measure of Textual Lexical Diversity (MTLD) { #mtld }

`mtld`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mtld"

</div>

<div class="metric-card" markdown>

### Moving Average Measure of Textual Lexical Diversity (MA-MTLD) { #mamtld }

`mamtld`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mamtld"

</div>

<div class="metric-card" markdown>

### MTLD with a moving window and text wrap (MTLD-W) { #mtldw }

`mtldw`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_mtldw"

</div>

<div class="metric-card" markdown>

### Hypergeometric Distribution D (HD-D) { #hdd }

`hdd`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hdd"

</div>

<div class="metric-card" markdown>

### Simpson's index (D) { #simpson_index }

`simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_simpson_index"

</div>

<div class="metric-card" markdown>

### Inverse Simpson's index (1/D) { #inverse_simpson_index }

`inverse_simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Inverse_Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_inverse_simpson_index"

</div>

<div class="metric-card" markdown>

### Gini-Simpson index (1-D) { #gini_simpson_index }

`gini_simpson_index` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Gini–Simpson_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_gini_simpson_index"

</div>

<div class="metric-card" markdown>

### Hapax index (Honoré's R) { #hapax_index }

`hapax_index` · `honore_r` · [Wikipedia](https://en.wikipedia.org/wiki/Hapax_legomenon)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hapax_index"

</div>

<div class="metric-card" markdown>

### Frequency spectrum { #frequency_spectrum }

`frequency_spectrum`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_frequency_spectrum"

</div>

<div class="metric-card" markdown>

### Yule's characteristic (Yule's K) { #yule_k }

`yule_k`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_yule_k"

</div>

<div class="metric-card" markdown>

### Inverse Yule's characteristic (Yule's I) { #yule_i }

`yule_i`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_yule_i"

</div>

<div class="metric-card" markdown>

### Herdan's Vm { #herdan_vm }

`herdan_vm`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_herdan_vm"

</div>

<div class="metric-card" markdown>

### Sichel's S { #sichel_s }

`sichel_s`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_sichel_s"

</div>

<div class="metric-card" markdown>

### Michéa's M { #michea_m }

`michea_m`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_michea_m"

</div>

<div class="metric-card" markdown>

### Brunet's W { #brunet_w }

`brunet_w`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_brunet_w"

</div>

<div class="metric-card" markdown>

### Dugast's k { #dugast_k }

`dugast_k`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_dugast_k"

</div>

<div class="metric-card" markdown>

### Baayen's P { #baayen_p }

`baayen_p`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_baayen_p"

</div>

<div class="metric-card" markdown>

### Orlov's Z { #orlov_z }

`orlov_z` · [Tweedie and Baayen 1998](https://doi.org/10.1023/A:1001749303137)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_orlov_z"

=== "Code"

    ``` python
    from ests.diversity_stats import calc_orlov_z

    words = (
        "en un lugar de la mancha de cuyo nombre no quiero acordarme no ha mucho tiempo que "
        "vivía un hidalgo de los de lanza en astillero adarga antigua rocín flaco y galgo corredor"
    ).split()
    round(calc_orlov_z(words), 2)
    ```

=== "Result"

    ```
    15733.38
    ```

</div>

<div class="metric-card" markdown>

### Hapax ratio { #hapax_ratio }

`hapax_ratio`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_hapax_ratio"

</div>

<div class="metric-card" markdown>

### The α₂ exponent { #alpha2 }

`alpha2`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_alpha2"

</div>

<div class="metric-card" markdown>

### Shannon entropy { #entropy }

`entropy` · [Wikipedia](https://en.wikipedia.org/wiki/Diversity_index#Shannon_index)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_entropy"

</div>

<div class="metric-card" markdown>

### Evenness { #evenness }

`evenness`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_evenness"

</div>

<div class="metric-card" markdown>

### Perplexity { #perplexity }

`perplexity`
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_perplexity"

</div>

<div class="metric-card" markdown>

### Zipf's law slope { #zipf_alpha }

`zipf_alpha` · [Wikipedia](https://en.wikipedia.org/wiki/Zipf's_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_zipf_alpha"

</div>

<div class="metric-card" markdown>

### Zipf-Mandelbrot fit { #fit_zipf_mandelbrot }

[Wikipedia](https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:fit_zipf_mandelbrot"

The [Zipf's law](../visualizers/zipf.md) visualizer draws this fit with `show_fit=True`.

=== "Code"

    ``` python
    from ests.diversity_stats import fit_zipf_mandelbrot

    # the frequencies 12, 6, 4, 3 follow the law f = 12 / r exactly
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    ```

=== "Result"

    ```
    (12.001, 0.0, 1.0, 1.0)
    ```

</div>

<div class="metric-card" markdown>

### Heaps' law exponent { #heaps_beta }

`heaps_beta` · [Wikipedia](https://en.wikipedia.org/wiki/Heaps'_law)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_heaps_beta"

--8<-- "stats/diversity_stats.md:vocabulary_growth"

--8<-- "stats/diversity_stats.md:fit_heaps"

The [Heaps' law](../visualizers/vocabulary.md) plot is built from `fit_heaps`.

</div>

<div class="metric-card" markdown>

### Burstiness { #burstiness }

`burstiness` · [Kim and Jo 2016](https://doi.org/10.1103/PhysRevE.94.032311)
{ .metric-meta }

--8<-- "stats/diversity_stats.md:calc_burstiness"

=== "Code"

    ``` python
    from ests.diversity_stats import calc_burstiness

    (
        calc_burstiness("sí no sí no sí no sí no sí no".split()),
        calc_burstiness("sí sí sí sí sí no no no no no".split()),
    )
    ```

=== "Result"

    ```
    (-1.0, 0.18350341907227388)
    ```

</div>

<div class="metric-card" markdown>

### Windowed computation { #windowed }

`windowed(stat)`
{ .metric-meta }

``` {.python .signature}
calc_windowed(text, func, window_len=100, step=None, confidence=0.95, *, messages=MESSAGES)
```

--8<-- "stats/diversity_stats.md:calc_windowed"

</div>

--8<-- "stats/diversity_stats.md:diversity-checks"

## Methods

--8<-- "stats/diversity_stats.md:DiversityStats-windowed"

=== "Code"

    ``` python
    ds.windowed("ttr", window_len=5)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    ```

=== "Result"

    ```
    WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    6
    ```

--8<-- "stats/diversity_stats.md:DiversityStats-get_stats"

--8<-- "stats/diversity_stats.md:DiversityStats-print_stats"

=== "Code"

    ``` python
    ds.get_stats()
    ```

=== "Result"

    ```
    {'ttr': 0.7333333333333333,
     'rttr': 2.840187787218772,
     'cttr': 2.008316044185609,
     'httr': 0.8854692840710255,
     'sttr': 0.2500605793160848,
     'mttr': 0.09738250756232528,
     'dttr': 10.268784661968118,
     'mattr': 0.7333333333333333,
     'msttr': 0.7333333333333333,
     'mtld': 15.0,
     'mamtld': 12.0,
     'mtldw': 13.25,
     'hdd': nan,
     'simpson_index': 0.047619047619047616,
     'inverse_simpson_index': 21.0,
     'gini_simpson_index': 0.9523809523809523,
     'hapax_index': 992.9517404041437,
     'yule_k': 444.44444444444446,
     'yule_i': 8.642857142857142,
     'herdan_vm': 0.1421338109037403,
     'sichel_s': 0.18181818181818182,
     'michea_m': 5.5,
     'brunet_w': 6.00637847898991,
     'dugast_k': 14.783895126869226,
     'baayen_p': 0.5333333333333333,
     'orlov_z': nan,
     'hapax_ratio': 0.7272727272727273,
     'alpha2': 0.5,
     'entropy': 3.3232314287976203,
     'evenness': 0.9606293157795304,
     'perplexity': 10.009038104159247,
     'zipf_alpha': 0.4884512334695912,
     'heaps_beta': 0.8366147342060046,
     'burstiness': nan}
    ```

The other methods - `to_dataframe` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the lexical diversity metrics have no scales, so `describe` gives `None` for the metrics of `get_stats`.
