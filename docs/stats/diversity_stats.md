# Lexical diversity metrics

!!! info ""
    **ests.diversity_stats.DiversityStats**

## Description

--8<-- "stats/diversity_stats.md:DiversityStats"

The class extends the `DiversityStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/diversity_stats/) core: instead of a list of words it takes a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The words can be extracted by a pre-built [`WordsExtractor`](../extractors/words.md); for a `Doc` a given extractor is applied to its text, without one the words come from its tokens. The words are always lower-cased, since every metric counts lexemes.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool; for a Doc it is applied to its text when given |
| `window_len` | int | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | float | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | int | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | int | `42` | Sample size for HD-D |
| `log_base` | float | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

--8<-- "stats/diversity_stats.md:check_params"

## Conventions { #conventions }

--8<-- "stats/diversity_stats.md:DiversityStats-conventions"

## Attributes

--8<-- "stats/diversity_stats.md:DiversityStats-attributes"

## Methods

### windowed

--8<-- "stats/diversity_stats.md:DiversityStats-windowed"

!!! example "Example"

    ``` python
    from ests import DiversityStats

    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"
    ds = DiversityStats(text)
    ds.windowed("ttr", window_len=5)
    # WindowStats(mean=0.9333333333333332, std=0.11547005383792512, lower=0.6464898180167025, upper=1.220176848649964, n_windows=3)
    ds.windowed("ttr", window_len=5, step=2).n_windows
    # 6
    ```

### get_stats

--8<-- "stats/diversity_stats.md:DiversityStats-get_stats"

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import DiversityStats

    # Prepare the data
    text = "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse, cuándo empezar labores"

    # Compute the metrics
    ds = DiversityStats(text)
    ds.get_stats()
    ```

    _Result_:

    ``` bash
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
    'hapax_ratio': 0.7272727272727273,
    'alpha2': 0.5,
    'entropy': 3.3232314287976203,
    'evenness': 0.9606293157795304,
    'perplexity': 10.009038104159247,
    'zipf_alpha': 0.4884512334695912,
    'heaps_beta': 0.8366147342060046}
    ```

### print_stats

--8<-- "stats/diversity_stats.md:DiversityStats-print_stats"

The example continues the previous one:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed metrics
    ds.print_stats()
    ```

    _Result_:

    ``` bash
                                      Metric                                   |  Value
    -------------------------------------------------------------------------------------
    Type-Token Ratio (TTR)                                                     |   0.73
    Root Type-Token Ratio (RTTR)                                               |   2.84
    Corrected Type-Token Ratio (CTTR)                                          |   2.01
    Herdan Type-Token Ratio (HTTR)                                             |   0.89
    Summer Type-Token Ratio (STTR)                                             |   0.25
    Maas Type-Token Ratio (MTTR)                                               |   0.10
    Dugast Type-Token Ratio (DTTR)                                             |  10.27
    Moving Average Type-Token Ratio (MATTR)                                    |   0.73
    Mean Segmental Type-Token Ratio (MSTTR)                                    |   0.73
    Measure of Textual Lexical Diversity (MTLD)                                |  15.00
    Moving Average Measure of Textual Lexical Diversity (MA-MTLD)              |  12.00
    Moving Average Measure of Textual Lexical Diversity with Wrap (MTLD-W)     |  13.25
    Hypergeometric Distribution D (HD-D)                                       |   nan
    Simpson's index (D)                                                        |   0.05
    Inverse Simpson's index (1/D)                                              |  21.00
    Gini-Simpson index (1-D)                                                   |   0.95
    Hapax index (Honoré's R)                                                   |  992.95
    Yule's characteristic K                                                    |  444.44
    Yule's inverse characteristic I                                            |   8.64
    Herdan's Vm                                                                |   0.14
    Sichel's S                                                                 |   0.18
    Michéa's M                                                                 |   5.50
    Brunet's W                                                                 |   6.01
    Dugast's k                                                                 |  14.78
    Baayen's P                                                                 |   0.53
    Hapax ratio                                                                |   0.73
    Exponent α₂                                                                |   0.50
    Shannon entropy (bits)                                                     |   3.32
    Evenness                                                                   |   0.96
    Perplexity                                                                 |  10.01
    Zipf's law slope (α)                                                       |   0.49
    Heaps' law exponent (β)                                                    |   0.84
    ```
