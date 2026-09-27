# Metric functions

## Type-Token Ratio (TTR)

!!! info ""
    **ests.diversity_stats.calc_ttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_ttr"

## Root Type-Token Ratio (RTTR)

!!! info ""
    **ests.diversity_stats.calc_rttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_rttr"

## Corrected Type-Token Ratio (CTTR)

!!! info ""
    **ests.diversity_stats.calc_cttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_cttr"

## Herdan Type-Token Ratio (HTTR)

!!! info ""
    **ests.diversity_stats.calc_httr()**

--8<-- "stats/diversity_stats_funcs.md:calc_httr"

## Summer Type-Token Ratio (STTR)

!!! info ""
    **ests.diversity_stats.calc_sttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_sttr"

## Maas Type-Token Ratio (MTTR)

!!! info ""
    **ests.diversity_stats.calc_mttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_mttr"

## Dugast Type-Token Ratio (DTTR)

!!! info ""
    **ests.diversity_stats.calc_dttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_dttr"

## Moving Average Type-Token Ratio (MATTR)

!!! info ""
    **ests.diversity_stats.calc_mattr()**

--8<-- "stats/diversity_stats_funcs.md:calc_mattr"

## Mean Segmental Type-Token Ratio (MSTTR)

!!! info ""
    **ests.diversity_stats.calc_msttr()**

--8<-- "stats/diversity_stats_funcs.md:calc_msttr"

## Measure of Textual Lexical Diversity (MTLD)

!!! info ""
    **ests.diversity_stats.calc_mtld()**

--8<-- "stats/diversity_stats_funcs.md:calc_mtld"

## Moving Average Measure of Textual Lexical Diversity (MA-MTLD)

!!! info ""
    **ests.diversity_stats.calc_mamtld()**

--8<-- "stats/diversity_stats_funcs.md:calc_mamtld"

## MTLD with a moving window and text wrap (MTLD-W)

!!! info ""
    **ests.diversity_stats.calc_mtldw()**

--8<-- "stats/diversity_stats_funcs.md:calc_mtldw"

## Hypergeometric Distribution D (HD-D)

!!! info ""
    **ests.diversity_stats.calc_hdd()**

--8<-- "stats/diversity_stats_funcs.md:calc_hdd"

## Simpson's index (D)

!!! info ""
    **ests.diversity_stats.calc_simpson_index()**

--8<-- "stats/diversity_stats_funcs.md:calc_simpson_index"

## Inverse Simpson's index (1/D) { #inverse_simpson_index }

!!! info ""
    **ests.diversity_stats.calc_inverse_simpson_index()**

--8<-- "stats/diversity_stats_funcs.md:calc_inverse_simpson_index"

## Gini-Simpson index (1-D)

!!! info ""
    **ests.diversity_stats.calc_gini_simpson_index()**

--8<-- "stats/diversity_stats_funcs.md:calc_gini_simpson_index"

## Hapax index (Honoré's R)

!!! info ""
    **ests.diversity_stats.calc_hapax_index()**, alias **ests.diversity_stats.calc_honore_r()**

--8<-- "stats/diversity_stats_funcs.md:calc_hapax_index"

## Frequency spectrum { #frequency_spectrum }

!!! info ""
    **ests.diversity_stats.calc_frequency_spectrum()**

--8<-- "stats/diversity_stats_funcs.md:calc_frequency_spectrum"

## Yule's characteristic (Yule's K)

!!! info ""
    **ests.diversity_stats.calc_yule_k()**

--8<-- "stats/diversity_stats_funcs.md:calc_yule_k"

## Inverse Yule's characteristic (Yule's I)

!!! info ""
    **ests.diversity_stats.calc_yule_i()**

--8<-- "stats/diversity_stats_funcs.md:calc_yule_i"

## Herdan's Vm

!!! info ""
    **ests.diversity_stats.calc_herdan_vm()**

--8<-- "stats/diversity_stats_funcs.md:calc_herdan_vm"

## Sichel's S

!!! info ""
    **ests.diversity_stats.calc_sichel_s()**

--8<-- "stats/diversity_stats_funcs.md:calc_sichel_s"

## Michéa's M

!!! info ""
    **ests.diversity_stats.calc_michea_m()**

--8<-- "stats/diversity_stats_funcs.md:calc_michea_m"

## Brunet's W

!!! info ""
    **ests.diversity_stats.calc_brunet_w()**

--8<-- "stats/diversity_stats_funcs.md:calc_brunet_w"

## Dugast's k

!!! info ""
    **ests.diversity_stats.calc_dugast_k()**

--8<-- "stats/diversity_stats_funcs.md:calc_dugast_k"

## Baayen's P

!!! info ""
    **ests.diversity_stats.calc_baayen_p()**

--8<-- "stats/diversity_stats_funcs.md:calc_baayen_p"

## Hapax ratio { #hapax_ratio }

!!! info ""
    **ests.diversity_stats.calc_hapax_ratio()**

--8<-- "stats/diversity_stats_funcs.md:calc_hapax_ratio"

## The α₂ exponent { #alpha2 }

!!! info ""
    **ests.diversity_stats.calc_alpha2()**

--8<-- "stats/diversity_stats_funcs.md:calc_alpha2"

## Shannon entropy { #entropy }

!!! info ""
    **ests.diversity_stats.calc_entropy()**

--8<-- "stats/diversity_stats_funcs.md:calc_entropy"

## Evenness { #evenness }

!!! info ""
    **ests.diversity_stats.calc_evenness()**

--8<-- "stats/diversity_stats_funcs.md:calc_evenness"

## Perplexity { #perplexity }

!!! info ""
    **ests.diversity_stats.calc_perplexity()**

--8<-- "stats/diversity_stats_funcs.md:calc_perplexity"

## Zipf's law slope { #zipf_alpha }

!!! info ""
    **ests.diversity_stats.calc_zipf_alpha()**

--8<-- "stats/diversity_stats_funcs.md:calc_zipf_alpha"

## Zipf-Mandelbrot fit { #fit_zipf_mandelbrot }

!!! info ""
    **ests.diversity_stats.fit_zipf_mandelbrot()**, **ests.diversity_stats.ZipfMandelbrot**

--8<-- "stats/diversity_stats_funcs.md:fit_zipf_mandelbrot"

!!! example "Example"

    ``` python
    from ests.diversity_stats import fit_zipf_mandelbrot

    # the frequencies 12, 6, 4, 3 follow the law f = 12 / r exactly
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    # (12.001, 0.0, 1.0, 1.0)
    ```

## Heaps' law exponent { #heaps_beta }

!!! info ""
    **ests.diversity_stats.calc_heaps_beta()**, **ests.diversity_stats.fit_heaps()**, **ests.diversity_stats.vocabulary_growth()**

--8<-- "stats/diversity_stats_funcs.md:calc_heaps_beta"

--8<-- "stats/diversity_stats_funcs.md:vocabulary_growth"

--8<-- "stats/diversity_stats_funcs.md:fit_heaps"

## Windowed computation { #calc_windowed }

!!! info ""
    **ests.diversity_stats.calc_windowed()**

--8<-- "stats/diversity_stats_funcs.md:calc_windowed"
