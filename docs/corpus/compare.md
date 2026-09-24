# Corpus comparison

!!! info ""
    **ests.corpus.compare_corpora()**, **ests.corpus.compare_features()**, **ests.corpus.corpus_features()**, **ests.corpus.text_features()**, **ests.corpus.split_windows()**, **ests.corpus.sentence_rhythm()**

## Description

Comparison of two corpora by every feature of a text at once: which statistics tell authors, genres, translations, human and generated texts apart, and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta).

The texts of both corpora are split into windows of about the same size, so that the features do not depend on the length of a text. In `split_windows` the number of windows is the ratio of the number of words to the size of a window rounded half up, at least one, and the parts are equal: a long text gives windows within a few percent of the size, a text of one to two windows gives windows of 750 to 1499 words at a window of 1000, and a text shorter than `min_words` - half a window by default - gives none, so that short texts do not set windows of very different sizes against the others. A boundary goes before the opening marks of the first word of a window - dashes, quotes, brackets, the inverted `¿` and `¡` - so that no punctuation is lost, while a straight quote or a dash glued to the end of the previous word closes it and stays behind (`"cuatro"`, `—dijo Juan—`). The features are computed for every window (`text_features` or a function of one's own), and for every feature the two sets of values are compared. The result is a `DataFrame` feature × statistics sorted by descending absolute Cliff's delta.

## Features

`text_features(text, nlp=None)` returns 132 features prefixed by their source:

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of long, complex, simple, mono- and polysyllabic words, of letters, spaces and punctuation marks; letters and syllables per word | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | every readability formula and the consensus grade | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | every measure of lexical diversity | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of the values of every morphological feature (`morph_pos_NOUN`, `morph_mood_Sub`, `morph_polarity_Neg`) and the markers of Spanish (`morph_p_gerund`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) by the spaCy model |
| `sents_` | mean length of a sentence in words, standard deviation, coefficient of variation, autocorrelation of neighbouring lengths (`sentence_rhythm`) - the rhythm of the text | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frequencies of the punctuation marks by type per 1000 words and the share of the inverted marks | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |

Every feature is counted once. The reading time only follows the number of words in a window and is left out; the share of unique words repeats `diversity_ttr`, the words per sentence repeat `sents_mean`, and the markers of the moods repeat `morph_mood_*`, so they are left out as well.

The parts of speech and the features of a single value - polarity, polite, poss, reflex - are shares of all the words (`morph_polarity_Neg` is the share of the negations), the other features shares of the words that carry them (`morph_mood_Sub` is the subjunctive among the moods). A value that does not occur in a window gives 0, a feature absent from the window altogether (no verbs - no tense) gives `nan`. A value of several values, as the model writes `PronType=Int,Rel` of *que* and `Case=Acc,Nom` of *usted*, is shared equally among its parts, so the shares of a feature still sum to one.

The morphology is parsed by the model [`es_core_news_sm`](../installation.md#model) without its parser, which takes most of the time: a window of 1000 words takes about 0.07 s. The parse of dependencies would add a third to that for a single marker, `morph_p_ser`, which reads the copulas from it; a pipeline passed in `nlp` runs whole but for the entity recognizer, so `functools.partial(text_features, nlp=get_nlp())` brings the parser and `morph_p_ser` back, and another model goes into the comparison the same way. A text longer than the `max_length` of the pipeline raises `SourceError`, so a novel is compared by windows and not whole.

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
| `n_texts_A`, `n_texts_B` | number of texts behind those windows |

Cliff's delta and the AUC come from the same U statistic and agree with each other; Cohen's d is sensitive to outliers and to departures from normality, so it is best read next to the delta.

!!! warning "Windows of one text are not independent"
    The test and the effect sizes take every window for an independent observation, and the windows of one text are not: they share its plot, characters, narrator and edition. With few texts in a corpus the p-values are too small and reflect the texts chosen as much as the corpora - in the example below two novels of one author differ in 32 features by the same test. The bootstrap resamples whole texts instead, the level `text` of the index that `corpus_features` sets (a cluster bootstrap), so its interval accounts for the spread between the texts; it needs at least two texts on each side and is rough with only a few. A table of one's own without that level has every row taken for a text of its own.

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
| `min_words` | int | `None` | Smallest number of words in a window; `None` - half a window, or one when `window` is `None` |

## Usage example

Galdós against Unamuno, three novels each from the [corpus of literature](../datasets/spanishliterature.md): *Marianela*, *Misericordia* and *Torquemada en la hoguera* against *Niebla*, *Abel Sánchez* and *La tía Tula* - 157 and 117 windows of 1000 words, under half a minute.

!!! example "Example"

    _Code_:

    ``` python
    from ests.corpus import compare_corpora
    from ests.datasets import SpanishLiterature

    sl = SpanishLiterature()
    sl.download()
    galdos = [
        record["text"]
        for record in sl.get_records(author="galdos")
        if record["title"] in ("Marianela", "Misericordia", "Torquemada en la hoguera")
    ]
    unamuno = [
        record["text"]
        for record in sl.get_records(author="unamuno")
        if record["title"] in ("Niebla", "Abel Sánchez", "La tía Tula")
    ]

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
        "morph_polarity_Neg",
        "sents_mean",
        "punct_dash",
        "punct_exclamation",
        "diversity_yule_k",
    ]
    result.loc[features, columns].round(3)

    result.loc["sents_mean", ["n_Galdós", "n_Unamuno", "n_texts_Galdós", "n_texts_Unamuno"]].to_dict()
    ```

    _Result_:

    ``` bash
                      median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    diversity_mtldw         104.034          66.540  35.976   43.701    3.243        0.988  0.994     0.0
    diversity_mamtld        102.044          64.410  36.302   44.519    3.130        0.982  0.991     0.0
    diversity_mattr           0.816           0.769   0.045    0.053    2.964        0.981  0.991     0.0
    diversity_mtld          103.668          63.774  37.093   44.947    2.978        0.979  0.989     0.0
    diversity_msttr           0.817           0.770   0.045    0.054    2.839        0.973  0.987     0.0

                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.437           4.132   0.255    0.356    1.676        0.782  0.891     0.0
    readability_lix                38.221          29.469   7.443   10.806    1.085        0.700  0.850     0.0
    morph_p_gerund                  0.068           0.036   0.028    0.036    1.503        0.736  0.868     0.0
    morph_polarity_Neg              0.018           0.028  -0.013   -0.010   -1.130       -0.547  0.226     0.0
    sents_mean                     16.650          11.409   3.129    7.173    0.841        0.618  0.809     0.0
    punct_dash                     19.019          46.351 -40.474  -15.844   -1.315       -0.618  0.191     0.0
    punct_exclamation               8.016          23.928 -23.896   -3.779   -1.271       -0.629  0.186     0.0
    diversity_yule_k              104.859         110.355 -14.143   -1.203   -0.625       -0.318  0.341     0.0

    {'n_Galdós': 157, 'n_Unamuno': 117, 'n_texts_Galdós': 3, 'n_texts_Unamuno': 3}
    ```

Galdós has the richer vocabulary: in 98.4% of the pairs of windows his has the larger share of distinct words (the AUC of `diversity_ttr` is 0.984). The measures built on the number of distinct words - TTR and its transformations, MATTR, MTLD, the hapaxes - tell the authors apart with a delta near or above 0.9, while Simpson's index and Yule's K, which weigh the frequent words, do far less (0.32, a small effect) and Herdan's Vm hardly at all (0.15): the difference lies mostly in the rare vocabulary and not in the repetition of the frequent words. His words and sentences are longer, and he uses nearly twice as many gerunds among the verb forms. Unamuno writes in dialogue and in negations: two and a half times as many dashes per 1000 words, three times as many exclamation marks and twice as many question marks, and more negations among the words.

Of the 132 features, 94 have a corrected p-value below 0.01 and 63 show a large effect by Cliff's delta, but the test takes the 274 windows for independent, and they come from six novels: by the same test *Marianela* and *Misericordia*, two novels of Galdós, differ in 32 features. The interval of the difference of the medians resamples whole novels and is the safer guide - for the length of a sentence it spans 3.1 to 7.2 words, where the windows alone would give 3.8 to 6.3 - though three texts on a side are few for a bootstrap as well, and a comparison of authors wants as many texts as can be found.

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
