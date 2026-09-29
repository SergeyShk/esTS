# Corpus comparison

!!! info ""
    **ests.corpus.compare_corpora()**, **ests.corpus.compare_features()**, **ests.corpus.check_comparison_params()**, **ests.corpus.corpus_features()**, **ests.corpus.text_features()**, **ests.corpus.split_windows()**, **ests.corpus.sentence_rhythm()**, **ests.corpus.calc_cohen_d()**, **ests.corpus.calc_cliff_delta()**, **ests.corpus.bootstrap_median_diff()**, **ests.corpus.holm_correction()**

## Description

`compare_corpora` compares two corpora of Spanish texts by every feature of a text at once - which statistics tell the corpora apart, and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta). It builds the tables of the features of the windows of both corpora and compares them with the `compare_features` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core:

--8<-- "corpus/compare.md:compare_features"

In `split_windows` the number of windows is the ratio of the number of words to the size of a window rounded half up, at least one, and the parts are equal: at a window of 1000 a text of one to two windows gives windows of 750 to 1499 words, and a text shorter than `min_words` - half a window by default - gives none. A boundary goes before the opening marks of the first word of a window - dashes, quotes, brackets, `¿` and `¡` - while a straight quote or a dash glued to the end of the previous word stays with it (`"cuatro"`, `—dijo Juan—`). The features of every window are computed by `text_features` or a function of one's own.

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

Left out are the reading time, which only follows the number of words in a window, and the features that repeat others: the share of unique words (`diversity_ttr`), the words per sentence (`sents_mean`) and the markers of the moods (`morph_mood_*`).

The parts of speech and the features of a single value - polarity, polite, poss, reflex - are shares of all the words (`morph_polarity_Neg` is the share of the negations), the other features shares of the words that carry them (`morph_mood_Sub` is the subjunctive among the moods). A value that does not occur in a window gives 0, a feature absent from the window altogether (no verbs - no tense) gives `nan`. A value of several values (`PronType=Int,Rel` of *que*) is shared equally among its parts, so the shares of a feature still sum to one.

The morphology is parsed by the model [`es_core_news_sm`](../installation.md#model) without its parser, so the marker `morph_p_ser`, which reads the copulas from the dependencies, is left out; a pipeline passed in `nlp` runs whole but for the entity recognizer, so `functools.partial(text_features, nlp=get_nlp())` brings the parser and `morph_p_ser` back, and another model goes into the comparison the same way. A text longer than the `max_length` of the pipeline raises `SourceError`, so a novel is compared by windows and not whole.

`corpus_features(texts, window, features)` returns the matrix of the features of the windows indexed by (number of the text, number of the window), for classifiers of one's own as well; the level `text` of the index is what the bootstrap of `compare_features` resamples. `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`, and the split lets the features of several corpora be computed once and compared in pairs.

The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count the characters as they are: indents, double and non-breaking spaces of the files reflect the typesetting of an edition and not the text. In a corpus from different sources collapse them beforehand, for instance with `re.sub(r"[^\S\n]+", " ", text)`.

## Statistics

--8<-- "corpus/compare.md:compare_features-statistics"

## Parameters

Parameters of `compare_corpora`:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `a` | list[str] | `-` | Texts of the first corpus |
| `b` | list[str] | `-` | Texts of the second corpus |
| `window` | int | `1000` | Size of a window in words; `None` - the whole texts |
| `features` | callable | `None` | Function of the features of a text; `None` - `text_features` |
| `min_words` | int | `None` | Smallest number of words in a window; `None` - half a window, or one when `window` is `None` |

`labels`, `n_bootstrap` and `seed` go on to `compare_features`, whose parameters are:

--8<-- "corpus/compare.md:compare_features-parameters"

--8<-- "corpus/compare.md:check_comparison_params"

`compare_corpora` calls it first, so a wrong name of a corpus or seed fails before any text is parsed.

## Functions of the statistics

The statistics of a row are available one by one from `ests.corpus`:

--8<-- "corpus/compare.md:calc_cohen_d"

--8<-- "corpus/compare.md:calc_cliff_delta"

--8<-- "corpus/compare.md:bootstrap_median_diff"

--8<-- "corpus/compare.md:holm_correction"

## Usage example

Galdós against Unamuno, three novels each from the [corpus of literature](../datasets/spanishliterature.md): *Marianela*, *Misericordia* and *Torquemada en la hoguera* against *Niebla*, *Abel Sánchez* and *La tía Tula*.

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
    readability_lix                38.220          29.469   7.437   10.668    1.088        0.703  0.852     0.0
    morph_p_gerund                  0.068           0.036   0.028    0.036    1.503        0.736  0.868     0.0
    morph_polarity_Neg              0.018           0.028  -0.013   -0.010   -1.130       -0.547  0.226     0.0
    sents_mean                     16.650          11.409   3.219    6.998    0.844        0.623  0.811     0.0
    punct_dash                     19.019          46.351 -40.474  -15.844   -1.315       -0.618  0.191     0.0
    punct_exclamation               8.016          23.928 -23.896   -3.779   -1.271       -0.629  0.186     0.0
    diversity_yule_k              104.859         110.355 -14.143   -1.203   -0.625       -0.318  0.341     0.0

    {'n_Galdós': 157, 'n_Unamuno': 117, 'n_texts_Galdós': 3, 'n_texts_Unamuno': 3}
    ```

Galdós has the richer vocabulary: the measures built on the number of distinct words - TTR and its transformations, MATTR, MTLD, the hapaxes - tell the authors apart with a delta near or above 0.9, while Yule's K, which weighs the frequent words, gives a small effect (0.32), so the difference lies mostly in the rare vocabulary. His words and sentences are longer, with nearly twice as many gerunds among the verb forms. Unamuno writes in dialogue: two and a half times as many dashes per 1000 words, three times as many exclamation marks, and more negations.

The p-values take the 274 windows of six novels for independent (see the warning above), and by the same test two novels of Galdós, *Marianela* and *Misericordia*, differ in 41 features. The interval of the difference of the medians resamples whole novels and is the safer guide: for the length of a sentence it spans 3.2 to 7.0 words, where the windows alone would give 3.7 to 6.3.

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
