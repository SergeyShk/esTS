# Corpus comparison

``` {.python .signature}
compare_corpora(a, b, window=1000, features=None, labels=('A', 'B'), n_bootstrap=1000, seed=0, min_words=None)
```

Compares two corpora of Spanish texts by every feature of a text at once: which statistics tell the corpora apart, and by how much. For single words [`keyness`](keyness.md) does the same, for the distances between texts - [`delta`](stylometry.md#delta).

The texts are cut in a row into windows of exactly `window` words by [`split_windows`](#split_windows), so the windows of all texts have one length; an incomplete remainder at the end of a text and a text shorter than a window are dropped unless `min_words` allows shorter windows. The features of every window are computed by [`text_features`](#text_features) or a function of one's own, and the tables of the two corpora are compared by [`compare_features`](#compare_features) of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/compare/) core.

Galdós against Unamuno, three novels each from the [corpus of literature](../datasets/spanishliterature.md): *Marianela*, *Misericordia* and *Torquemada en la hoguera* against *Niebla*, *Abel Sánchez* and *La tía Tula*.

=== "Code"

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

=== "Result"

    ```
                      median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    diversity_mtld         103.655          64.594  37.536   47.169    3.107        0.981  0.990     0.0
    diversity_mattr          0.817           0.769   0.046    0.057    2.951        0.979  0.990     0.0
    diversity_msttr          0.819           0.769   0.047    0.059    2.927        0.979  0.989     0.0
    diversity_ttr            0.479           0.399   0.068    0.087    3.118        0.970  0.985     0.0
    diversity_rttr          15.147          12.617   2.150    2.690    3.118        0.970  0.985     0.0
                            median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    basic_letters_per_word          4.441           4.130   0.243    0.358    1.695        0.784  0.892     0.0
    readability_lix                38.482          29.858   7.094   11.176    1.093        0.696  0.848     0.0
    morph_p_gerund                  0.069           0.037   0.031    0.033    1.509        0.726  0.863     0.0
    morph_polarity_Neg              0.019           0.029  -0.011   -0.009   -1.136       -0.564  0.218     0.0
    sents_mean                     16.393          11.494   3.321    6.688    0.845        0.615  0.808     0.0
    punct_dash                     19.000          46.000 -39.000  -14.000   -1.287       -0.605  0.197     0.0
    punct_exclamation               9.000          24.000 -23.000   -2.000   -1.251       -0.637  0.181     0.0
    diversity_yule_k              103.620         112.500 -17.620   -2.660   -0.675       -0.351  0.325     0.0
    {'n_Galdós': 155, 'n_Unamuno': 117, 'n_texts_Galdós': 3, 'n_texts_Unamuno': 3}
    ```

Galdós has the richer vocabulary: the measures built on the number of distinct words - TTR and its transformations, MATTR, MTLD, the hapaxes - tell the authors apart with a delta near or above 0.9, while Yule's K, which weighs the frequent words, gives a medium effect (0.35), so the difference lies mostly in the rare vocabulary. His words and sentences are longer, with nearly twice as many gerunds among the verb forms. Unamuno writes in dialogue: two and a half times as many dashes and exclamation marks per 1000 words, and more negations. The cohesion tells them apart as well (`result.filter(like="cohesion_", axis=0)`): per 1000 words Unamuno opens more than three times as many sentences with a connector (`cohesion_connectors_inter`, 20 against 6) - about 2.3 times as many per sentence, his sentences being shorter - and he repeats more of the content words of a sentence in the next two (0.125 against 0.072). Part of the cohesion follows the length of the sentences: Spearman's ρ with `sents_mean` over the windows is 0.75 for Galdós and 0.73 for Unamuno for `cohesion_content_overlap_all`, the binary overlap of all the pairs of sentences, and -0.50 and -0.61 for the connectors opening a sentence, while the share of the content words repeated in the next two sentences is not tied to it (-0.06 and -0.12).

The p-values take the 272 windows of six novels for independent (see the [warning](#statistics) below), and by the same test two novels of Galdós, *Marianela* and *Misericordia*, differ in 56 features. The interval of the difference of the medians resamples whole novels and is the safer guide: for the length of a sentence it spans 3.3 to 6.7 words, where the windows alone would give 4.1 to 6.2.

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `a` | `list[str]` | - | Texts of the first corpus |
| `b` | `list[str]` | - | Texts of the second corpus |
| `window` | `int` | `1000` | Size of a window in words; `None` - the whole texts |
| `features` | `Callable` | `None` | Function of the features of a text; `None` - `text_features` |
| `min_words` | `int` | `None` | Smallest number of words in a window, at most `window`; `None` - a whole window, or one word when `window` is `None` |

`labels`, `n_bootstrap` and `seed` go on to [`compare_features`](#compare_features). `compare_corpora` checks them with `check_comparison_params` first, so a wrong name of a corpus or seed fails before any text is parsed.

Raises:

- `SourceTypeError` - texts that are not a list of strings, `features` that cannot be called or give no mapping of numbers by name;
- `SourceError` - a corpus without a window of `min_words` words or more;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above `window`, labels, a number of samples or a seed that `check_comparison_params` rejects;
- `DatasetNotFoundError` - the default features without the model installed.

## Features { #text_features }

``` {.python .signature}
text_features(text, nlp=None)
```

Returns 164 features of a text prefixed by their source, 209 with a pipeline that has a parser; an undefined feature is `nan`.

| Prefix | Features | Source |
| :----- | :------- | :----- |
| `basic_` | shares of long, complex, simple, mono- and polysyllabic words, of letters, spaces and punctuation marks; letters and syllables per word | [`BasicStats`](../stats/basic_stats.md) |
| `readability_` | every readability formula and the consensus grade, without the numbers among the words (`filter_nums`) | [`ReadabilityStats`](../stats/readability_stats.md) |
| `diversity_` | every measure of lexical diversity but those unstable on a window of a thousand words, `WINDOW_UNSTABLE_DIVERSITY` of `ests.corpus.compare`: Orlov's Z, and MA-MTLD and MTLD-W, which average a few completed factors | [`DiversityStats`](../stats/diversity_stats.md) |
| `morph_` | shares of the values of every morphological feature (`morph_pos_NOUN`, `morph_mood_Sub`, `morph_polarity_Neg`) and the markers of Spanish (`morph_p_gerund`, `morph_p_mente_adverbs`) | [`MorphStats`](../stats/morph_stats.md) by the pipeline of `load_pipeline` |
| `sents_` | mean length of a sentence in words, standard deviation, coefficient of variation, autocorrelation of neighbouring lengths ([`sentence_rhythm`](#sentence_rhythm)) - the rhythm of the text | [`SentsExtractor`](../extractors/sentences.md) |
| `punct_` | frequencies of the punctuation marks by type per 1000 words and the share of the inverted marks | [`punctuation_profile`](../stats/basic_stats.md#punctuation) |
| `cohesion_` | overlaps of the nouns, arguments and content words of the sentences, givenness, temporal cohesion and the densities of the connectors by class, kind and place, but the overlaps between paragraphs, which the windows cut | [`CohesionStats`](../stats/cohesion_stats.md) by the pipeline of `load_pipeline` |
| `syntax_` | every syntactic statistic, with a pipeline that has a parser | [`SyntaxStats`](../stats/syntax_stats.md) |

Left out are the reading time, which only follows the number of words in a window, and the features that repeat others: the share of unique words of `BasicStats`, which repeats `diversity_ttr`, its words per sentence, which repeat `sents_mean`, and the markers of the moods of `get_markers`, which repeat `morph_mood_*`.

The parts of speech and the features of a single value - polarity, polite, poss, reflex - are shares of all the words (`morph_polarity_Neg` is the share of the negations), the other features shares of the words that carry them (`morph_mood_Sub` is the subjunctive among the moods). A value that does not occur in a window gives 0, a feature absent from the window altogether (no verbs - no tense) gives `nan`. A value of several values (`Case=Acc,Nom` of *usted*) is shared equally among its parts, so the shares of a feature still sum to one.

The morphology and the cohesion are parsed by the pipeline of [`load_pipeline`](../components.md#load_pipeline) - [`es_core_news_sm`](../installation.md#model) with the analyses of esMorph - without its parser, so the group `syntax_` is left out; a pipeline passed in `nlp` runs whole but for the entity recognizer, so `functools.partial(text_features, nlp=get_nlp())` brings the parser and the syntax in, and another model goes into the comparison the same way. The pipeline of [`load_pipeline`](../components.md#load_pipeline), the default one, splits the text into the sentences of the group `sents_`, so the cohesion and the syntax count the same sentences as the rhythm; a pipeline of one's own gives its own sentences. A novel is compared by windows and not whole, as the pipeline takes at most `max_length` characters. The group `morph_` reads the `Doc`, where a contraction or a verb with clitics is one word, so its shares differ from those of `MorphStats` on the string ([`load_pipeline`](../components.md#load_pipeline)).

The shares of spaces, letters and punctuation marks (`basic_p_spaces`, `basic_p_letters`, `basic_p_punctuations`) count the characters as they are: indents, double and non-breaking spaces of the files reflect the typesetting of an edition and not the text. In a corpus from different sources collapse them beforehand, for instance with `re.sub(r"[^\S\n]+", " ", text)`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `nlp` | `Language` | `None` | Pipeline for the morphology, the cohesion and, with a parser, the syntax; `None` - the default model without its parser |

Raises:

- `SourceTypeError` - a text that is not a string, a pipeline that is not a spaCy `Language`;
- `SourceError` - a text without words or longer than the `max_length` of the pipeline, a pipeline that gives no parts of speech or no lemmas;
- `DatasetNotFoundError` - the default model is not installed.

``` {.python .signature}
corpus_features(texts, window=1000, features=text_features, min_words=None)
```

Returns the matrix of the features of the windows indexed by (number of the text, number of the window), for classifiers of one's own as well; the level `text` of the index is what the bootstrap of `compare_features` resamples. Texts without words and windows shorter than `min_words` are skipped. `compare_corpora` is `corpus_features` for each corpus followed by `compare_features`, and the split lets the features of several corpora be computed once and compared in pairs.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `texts` | `list[str]` | - | Texts of the corpus |
| `window` | `int` | `1000` | Size of a window in words; `None` - the whole texts |
| `features` | `Callable` | `text_features` | Function of the features of a text |
| `min_words` | `int` | `None` | Smallest number of words in a window, at most `window`; `None` - a whole window, or one word when `window` is `None` |

Raises:

- `SourceTypeError` - texts that are not a list of strings, `features` that cannot be called or give no mapping of numbers by name;
- `SourceError` - a corpus without a window of `min_words` words or more;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above `window`;
- `DatasetNotFoundError` - the default features without the model installed.

The syntactic features come with a pipeline that has a parser, passed in a function of the features; features of one's own are passed the same way:

=== "Code"

    ``` python
    from functools import partial

    from ests.corpus import compare_corpora, text_features
    from ests.utils import get_nlp

    features = partial(text_features, nlp=get_nlp())
    result = compare_corpora(
        galdos, unamuno, window=1000, features=features, labels=("Galdós", "Unamuno")
    )
    result.filter(like="syntax_", axis=0)[columns].head(5).round(3)
    ```

=== "Result"

    ```
                                        median_Galdós  median_Unamuno  ci_low  ci_high  cohen_d  cliff_delta    auc  p_holm
    syntax_gerund_clauses_per_sent              0.151           0.049   0.081    0.117    1.481        0.859  0.929     0.0
    syntax_complex_nominals_per_clause          0.768           0.520   0.211    0.305    1.134        0.668  0.834     0.0
    syntax_tree_depth                           3.780           2.888   0.597    1.062    1.083        0.666  0.833     0.0
    syntax_subtrees_per_sent                    6.833           4.563   1.574    2.894    0.944        0.659  0.830     0.0
    syntax_t_units_per_sent                     1.075           1.008   0.028    0.150    1.361        0.646  0.823     0.0
    ```

## Comparison of feature tables { #compare_features }

--8<-- "corpus/compare.md:compare_features"

--8<-- "corpus/compare.md:compare_features-parameters"

--8<-- "corpus/compare.md:check_comparison_params"

## Statistics { #statistics }

--8<-- "corpus/compare.md:compare_features-statistics"

## Functions of the statistics

The statistics of a row are available one by one from `ests.corpus`:

--8<-- "corpus/compare.md:calc_cohen_d"

--8<-- "corpus/compare.md:calc_cliff_delta"

--8<-- "corpus/compare.md:bootstrap_median_diff"

--8<-- "corpus/compare.md:holm_correction"

=== "Code"

    ``` python
    from ests.corpus import calc_cliff_delta, calc_cohen_d, holm_correction

    round(calc_cohen_d([2, 4, 6, 8], [1, 3, 5, 7]), 3)
    calc_cliff_delta([2, 4, 6, 8], [1, 3, 5, 7])
    holm_correction([0.01, 0.04, 0.03]).round(3).tolist()
    ```

=== "Result"

    ```
    0.387
    0.25
    [0.03, 0.06, 0.06]
    ```

## Windows of a text { #split_windows }

``` {.python .signature}
split_windows(text, window=1000, min_words=None)
```

Cuts a text into consecutive windows of exactly `window` words, so the features that depend on length are comparable between texts. The rest is a window only with at least `min_words` words (by default a whole window, so it is dropped). A boundary goes before the first word of a window and its opening marks; a straight quote or a dash glued to the last word of the previous window stays with it, and so does one after a closing mark when whitespace follows it (`"cuatro"`, `—dijo Juan—`, `"adiós."`); a dash glued to the next word opens its line of dialogue (`cuatro.—¿Cinco?`). Windows are stripped of whitespace; `window=None` gives the whole text. It is the `split_windows` of the core with the words of [`WordsExtractor`](../extractors/words.md) and the marks of `ests.constants`: quotes, brackets, dashes, `¿` and `¡` open a phrase (`OPENING_MARKS`), the straight quote and the dashes are symmetric (`SYMMETRIC_MARKS`); the marks that close a phrase are those of the core.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `str` | - | Text string |
| `window` | `int` | `1000` | Size of a window in words; `None` - the whole text |
| `min_words` | `int` | `None` | Smallest number of words in a window; `None` - a whole window, or one word when `window` is `None` |

A text without words or shorter than `min_words` gives an empty list.

Raises:

- `SourceTypeError` - a text that is not a string;
- `ParameterError` - a `window` or `min_words` that is not an integer of at least one, `min_words` above the window.

=== "Code"

    ``` python
    from ests.corpus import split_windows

    split_windows("Uno dos tres cuatro cinco", 2, min_words=1)
    split_windows("El gato duerme mucho. ¿Dónde está el perro?", 4)
    split_windows('Dijo "adiós" y se fue ya', 2)
    ```

=== "Result"

    ```
    ['Uno dos', 'tres cuatro', 'cinco']
    ['El gato duerme mucho.', '¿Dónde está el perro?']
    ['Dijo "adiós"', 'y se', 'fue ya']
    ```

## Rhythm of the sentences { #sentence_rhythm }

``` {.python .signature}
sentence_rhythm(lengths, *, messages=None)
```

--8<-- "corpus/compare.md:sentence_rhythm"

=== "Code"

    ``` python
    from ests.corpus import sentence_rhythm

    {key: round(value, 3) for key, value in sentence_rhythm([4, 8, 2, 7]).items()}
    ```

=== "Result"

    ```
    {'sents_mean': 5.25, 'sents_std': 2.754, 'sents_cv': 0.525, 'sents_autocorr': -0.794}
    ```
