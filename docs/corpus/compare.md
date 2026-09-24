# Corpus comparison

!!! info ""
    **ests.corpus.compare_corpora()**, **ests.corpus.compare_features()**, **ests.corpus.corpus_features()**, **ests.corpus.text_features()**, **ests.corpus.split_windows()**, **ests.corpus.sentence_rhythm()**

## Description

Comparison of two corpora by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart, and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta).

The texts of both corpora are split into windows of the same size, so that the features do not depend on the length of a text (`split_windows`: the number of windows is the ratio of the number of words to the size of a window rounded half up, at least one, and the parts are equal; a boundary goes before the opening marks of the first word of a window - dashes, quotes, brackets, the inverted `¿` and `¡` - so that no punctuation is lost). The features are computed for every window (`text_features` or a function of one's own), and for every feature the two sets of values are compared. The result is a `DataFrame` feature × statistics sorted by descending absolute Cliff's delta.

## Features

`text_features(text, nlp=None)` returns 140 features prefixed by their source:

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of unique, long, complex, simple, mono- and polysyllabic words, of letters, spaces and punctuation marks; letters and syllables per word, words per sentence | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | every readability formula, the consensus grade, the reading time | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | every measure of lexical diversity | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of the parts of speech among the words (`morph_pos_NOUN`), shares of the values within every feature (`morph_mood_Sub`, `morph_tense_Past`) and the markers of Spanish (`morph_p_ser`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) by the spaCy model |
| `sents_` | mean length of a sentence in words, standard deviation, coefficient of variation, autocorrelation of neighbouring lengths (`sentence_rhythm`) - the rhythm of the text | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frequencies of the punctuation marks by type per 1000 words and the share of the inverted marks | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

A value of a morphological feature that does not occur in a window gives 0, a feature absent from the window altogether (no verbs - no tense) gives `nan`. The morphology needs the parse of the model [`es_core_news_sm`](../installation.md#model) or of the pipeline in `nlp`, which takes most of the time: a window of 1000 words takes about 0.1 s. A text longer than the `max_length` of the pipeline raises `SourceError`, so a novel is compared by windows and not whole. Another pipeline goes into the comparison with `functools.partial(text_features, nlp=nlp)`.

`corpus_features(texts, window, features)` returns the matrix of the features of the windows indexed by (number of the text, number of the window) - for classifiers of one's own - and `compare_features(table_a, table_b, labels, n_bootstrap, seed)` compares two such tables: `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`. The split serves when the features are computed once for several corpora and pairs of them are to be compared, all the authors pairwise for instance.

The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count the characters as they are: indents, double and non-breaking spaces of the files reflect the typesetting of an edition and not the text. In a corpus from different sources collapse them beforehand, for instance with `re.sub(r"[^\S\n]+", " ", text)`.

## Statistics

For a feature with the values $x_1 \dots x_{n_A}$ in corpus A and $y_1 \dots y_{n_B}$ in corpus B (undefined and infinite values dropped; with fewer than two values on a side - `nan`):

| Column | Description |
| :----- | :---------- |
| `mean_A`, `mean_B`, `median_A`, `median_B` | means and medians |
| `median_diff`, `ci_low`, `ci_high` | the difference of the medians and its 95% percentile bootstrap interval: both sets are resampled `n_bootstrap` times (`bootstrap_median_diff`) |
| `cohen_d` | $d = (\bar{x} - \bar{y}) / s$, $s$ - the pooled standard deviation; 0.2 - a small effect, 0.5 - medium, 0.8 - large (`calc_cohen_d`) |
| `cliff_delta` | $\delta = P(x > y) - P(x < y)$ from −1 to 1; $\lvert\delta\rvert$ < 0.147 - a negligible effect, < 0.33 - small, < 0.474 - medium, large otherwise (Romano et al. 2006; `calc_cliff_delta`) |
| `auc` | the feature as a classifier on its own: the share of the pairs of windows where the value in A is greater than in B, ties counted as half; $\delta = 2 \cdot AUC - 1$, 0.5 - the feature does not tell the corpora apart |
| `u`, `p_value` | the Mann-Whitney U statistic and the two-sided p-value (`scipy.stats.mannwhitneyu`) |
| `p_holm` | the p-value with Holm's correction for the number of features (`holm_correction`): a table of a hundred rows without a correction invites false discoveries |
| `n_A`, `n_B` | number of windows with a defined value |

Cliff's delta and the AUC come from the same U statistic and agree with each other; Cohen's d is sensitive to outliers and to departures from normality, so it is best read next to the delta.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `a` | list[str] | `-` | Texts of the first corpus |
| `b` | list[str] | `-` | Texts of the second corpus |
| `window` | int | `1000` | Size of a window in words; `None` - the whole texts |
| `features` | callable | `None` | Function of the features of a text; `None` - `text_features` |
| `labels` | tuple[str, str] | `("A", "B")` | Names of the corpora for the columns |
| `n_bootstrap` | int | `1000` | Number of bootstrap samples |
| `seed` | int | `0` | Seed of the random number generator; `None` - a random one |

## Usage example

Galdós against Unamuno, three novels each from [Project Gutenberg](https://www.gutenberg.org): *Marianela*, *Misericordia* and *Torquemada en la hoguera* against *Niebla*, *Abel Sánchez* and *La tía Tula* - 197 and 117 windows of 1000 words, about half a minute after the download.

!!! example "Example"

    _Code_:

    ``` python
    from urllib.request import urlopen

    from ests.corpus import compare_corpora


    def gutenberg(number):
        url = f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
        text = urlopen(url).read().decode("utf-8")
        start = text.index("\n", text.index("*** START OF"))
        return text[start : text.index("*** END OF")]


    galdos = [gutenberg(number) for number in (17340, 21831, 15206)]
    unamuno = [gutenberg(number) for number in (49836, 44512, 44358)]

    result = compare_corpora(galdos, unamuno, window=1000, labels=("Galdós", "Unamuno"))
    columns = [
        "median_Galdós",
        "median_Unamuno",
        "ci_low",
        "ci_high",
        "cohen_d",
        "cliff_delta",
        "auc",
        "p_holm",
    ]
    result[columns].head(5).round(3)

    features = [
        "basic_letters_per_word",
        "readability_lix",
        "morph_p_gerund",
        "sents_mean",
        "punct_dash",
        "punct_exclamation",
    ]
    result.loc[features, columns].round(3)
    ```

    _Result_:

    ``` bash
                          median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_p_unique_words          0.494           0.420   0.069    0.084    3.159        0.976  0.988     0.0
    diversity_ttr                 0.494           0.420   0.069    0.084    3.159        0.976  0.988     0.0
    diversity_httr                0.898           0.874   0.022    0.027    3.118        0.975  0.988     0.0
    diversity_brunet_w           10.775          11.528  -0.857   -0.695   -3.073       -0.975  0.012     0.0
    diversity_dttr               29.349          23.840   5.077    6.113    3.048        0.975  0.987     0.0

                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.499           4.152   0.290    0.383    1.734        0.784  0.892     0.0
    readability_lix                40.006          30.074   8.446   11.936    1.285        0.743  0.872     0.0
    morph_p_gerund                  0.070           0.037   0.027    0.040    1.475        0.734  0.867     0.0
    sents_mean                     17.386          11.364   4.892    7.499    1.016        0.672  0.836     0.0
    punct_dash                      9.045          39.157 -34.148  -26.955   -1.810       -0.722  0.139     0.0
    punct_exclamation               9.970          24.096 -20.040  -11.960   -1.323       -0.634  0.183     0.0
    ```

Galdós has the richer vocabulary: in 99% of the pairs of windows his window has the larger share of unique words (AUC 0.988). The measures built on the number of distinct words - TTR and its transformations, MATTR, MTLD, the hapaxes - tell the authors apart with a delta above 0.9, while Simpson's index, Yule's K and Herdan's Vm, which weigh the frequent words, hardly do (below 0.12): the difference lies in the rare vocabulary and not in the repetition of the frequent words. His words and sentences are longer, and he uses nearly twice as many gerunds among the verb forms. Unamuno writes in dialogue: four times as many dashes per 1000 words, more than twice as many exclamation and question marks. Of the 140 features, 92 have a corrected p-value below 0.01 and 63 show a large effect by Cliff's delta - with hundreds of windows significance is cheap, and the size of the effect matters more.

Features of one's own, for instance the syntactic ones, are passed as a function:

!!! example "Example"

    ``` python
    from ests import SyntaxStats
    from ests.corpus import compare_corpora, text_features
    from ests.utils import get_nlp

    nlp = get_nlp()


    def features(text):
        stats = SyntaxStats(nlp(text)).get_stats()
        return {**text_features(text), **{f"syntax_{key}": value for key, value in stats.items()}}


    compare_corpora(galdos, unamuno, window=1000, features=features, labels=("Galdós", "Unamuno"))
    ```
