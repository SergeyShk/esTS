from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from itertools import pairwise
from math import floor, isnan, nan, sqrt
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from spacy.language import Language
from spacy.tokens import Doc

from ..basic_stats import BasicStats, punctuation_profile
from ..constants import MORPHOLOGY_STATS_DESC, OPENING_MARKS, SYMMETRIC_MARKS
from ..diversity_stats import DiversityStats
from ..exceptions import ParameterError, SourceError
from ..extractors import SentsExtractor, WordsExtractor
from ..morph_stats import FINITE_MOODS, MorphStats
from ..readability_stats import ReadabilityStats
from ..utils import (
    check_sequence,
    count_words_by_spans,
    get_nlp,
    iter_text_sents,
    iter_text_words,
)

Features = Callable[[str], Mapping[str, float]]
Values = Sequence[float] | np.ndarray[Any, Any]

COMPARISON_COLUMNS = (
    "mean_a",
    "mean_b",
    "median_a",
    "median_b",
    "median_diff",
    "ci_low",
    "ci_high",
    "cohen_d",
    "cliff_delta",
    "auc",
    "u",
    "p_value",
    "p_holm",
    "n_a",
    "n_b",
    "n_texts_a",
    "n_texts_b",
)


def split_windows(text: str, window: int | None = 1000, min_words: int | None = None) -> list[str]:
    """
    Splitting a text into windows of words

    Description:
        The number of windows is the ratio of the number of words to the size
        of a window rounded half up (2500 words at a window of 1000 - three
        windows), at least one, and the parts are equal, as the segments of
        zeta: the tail is not dropped, and a text of more than half a window
        gives windows of half a window to one and a half (1500 words - two of
        750, 1499 - one), within a few percent of the size for long texts.
        Windows of fewer than min_words words are dropped: by default half a
        window, which drops the texts shorter than that, so that a comparison
        does not set windows of very different sizes against each other.
        The first window starts at the first non-space character of the text,
        a boundary between windows goes before the first word of the next
        window and the opening marks before it (OPENING_MARKS: quotes,
        brackets, dashes, the inverted ¿ and ¡), except a straight quote or a
        dash glued to the end of the previous word, which closes it
        (SYMMETRIC_MARKS: "cuatro", —dijo Juan—), and the last window lasts to
        the end of the text; the windows are stripped of whitespace, so the
        punctuation before the first word, after the last word of a window
        and at the end of the text stays in the windows; with window=None the
        window is the whole text stripped of whitespace

    Arguments:
        text (str): Text string
        window (int): Size of a window in words; None - the whole text
        min_words (int): Smallest number of words in a window; None - half a
            window, or one when window is None

    Returns:
        list[str]: Windows of the text; an empty list for a text without words
            or shorter than min_words

    Raises:
        ParameterError: If the size of a window or min_words is below one

    Example:
        >>> from ests.corpus import split_windows
        >>> split_windows("El gato duerme mucho. ¿Dónde está el perro?", 4)
        ['El gato duerme mucho.', '¿Dónde está el perro?']
        >>> split_windows('Dijo "adiós" y se fue ya', 2)
        ['Dijo "adiós"', 'y se', 'fue ya']
    """
    if window is not None and window < 1:
        raise ParameterError("The size of a window must be greater than 0")
    if min_words is not None and min_words < 1:
        raise ParameterError("The smallest number of words in a window must be greater than 0")
    if min_words is None:
        min_words = 1 if window is None else max(1, window // 2)
    words = list(iter_text_words(text))
    if not words:
        return []
    n_windows = 1 if window is None else max(1, floor(len(words) / window + 0.5))
    chunks = np.array_split(np.arange(len(words)), n_windows)
    boundaries = [0]
    for chunk in chunks[1:]:
        start = words[chunk[0]][0]
        previous_end = words[chunk[0] - 1][1]
        boundary = start
        while boundary > previous_end and (
            text[boundary - 1].isspace() or text[boundary - 1] in OPENING_MARKS
        ):
            boundary -= 1
        while boundary == previous_end < start and text[boundary] in SYMMETRIC_MARKS:
            boundary += 1
            previous_end += 1
        boundaries.append(boundary)
    boundaries.append(len(text))
    return [
        text[start:end].strip()
        for (start, end), chunk in zip(pairwise(boundaries), chunks, strict=True)
        if len(chunk) >= min_words
    ]


def text_features(text: str, nlp: Language | None = None) -> dict[str, float]:
    """
    Computing the features of a text for the comparison of corpora

    Description:
        Features prefixed by their source: basic_ - the shares of long,
        complex, simple, mono- and polysyllabic words, of letters, spaces and
        punctuation marks, the mean number of letters and syllables per word
        (BasicStats); readability_ - every readability formula and the
        consensus grade (ReadabilityStats); diversity_ - every measure of
        lexical diversity (DiversityStats); morph_ - the shares of the values
        of every morphological feature of MORPHOLOGY_STATS_DESC and the markers
        of Spanish of MorphStats.get_markers; sents_ - the mean length of a
        sentence in words, its standard deviation, the coefficient of
        variation and the autocorrelation of neighbouring lengths - the rhythm
        of the text; punct_ - the frequencies of the marks by type per 1000
        words and the share of the inverted marks (punctuation_profile)
        Every feature is counted once: the reading time, which only follows
        the number of words, is left out, as are the share of unique words
        (diversity_ttr), the words per sentence (sents_mean) and the markers
        of the moods (morph_mood_*), which repeat other features
        The morphological shares are taken over the full list of values: a
        value that does not occur gives 0, a feature absent from the window
        altogether (no verbs - no tense) nan. The parts of speech and the
        features of a single value (polarity, polite, poss, reflex) are shares
        of all the words (morph_pos_NOUN, morph_polarity_Neg - the negations),
        the other features shares of the words that carry them
        (morph_mood_Sub - the subjunctive among the moods); a value of several
        values (PronType=Int,Rel of que, Case=Acc,Nom of usted) is shared
        equally among its parts, so the shares of a feature still sum to one
        The text is tokenized and split into sentences once: the words with
        their positions and the sentences of sentenize go to every class
        through extractors with the ready result, and the lengths of the
        sentences are counted from them; the basic statistics are computed
        once (ReadabilityStats gets the ready BasicStats). The morphology is
        parsed by the model es_core_news_sm without its parser, which takes
        most of the time: about 0.07 s for a window of 1000 words. The parse
        of dependencies would add a third to that for one marker, p_ser,
        which reads the copulas from it: a pipeline passed in nlp runs whole
        but for the entity recognizer, and with a parser it adds morph_p_ser.
        A text longer than the max_length of the pipeline raises SourceError
        The shares of spaces, letters and marks (basic_p_spaces,
        basic_p_letters, basic_p_punctuations) count the characters as they
        are: indents, double and non-breaking spaces of the files reflect the
        typesetting of an edition and not the text, and in a corpus from
        different sources they are best collapsed beforehand

    Arguments:
        text (str): Text string
        nlp (Language): Pipeline for the morphology; None - the default model
            without its parser

    Returns:
        dict[str, float]: Features; the undefined values are nan

    Raises:
        SourceError: If the text has no words or is longer than the max_length
            of the pipeline
        DatasetNotFoundError: If the default model is not installed

    Example:
        >>> from ests.corpus import text_features
        >>> features = text_features("El gato duerme. El perro come y juega en el jardín.")
        >>> features["sents_mean"], round(features["morph_pos_DET"], 3)
        (5.5, 0.273)
    """
    positions = list(iter_text_words(text))
    spans = [(start, stop) for start, stop, _ in iter_text_sents(text)]
    words = _FixedWordsExtractor(tuple(word for _, _, word in positions))
    sents = _FixedSentsExtractor(tuple(text[start:stop] for start, stop in spans))
    basic = BasicStats(text, sents, words, normalize=True)
    features: dict[str, float] = {}
    for key in (
        "p_long_words",
        "p_complex_words",
        "p_simple_words",
        "p_monosyllable_words",
        "p_polysyllable_words",
        "p_letters",
        "p_spaces",
        "p_punctuations",
    ):
        features[f"basic_{key}"] = float(getattr(basic, key))
    features["basic_letters_per_word"] = basic.n_letters / basic.n_words
    features["basic_syllables_per_word"] = basic.n_syllables / basic.n_words
    for key, score in ReadabilityStats(basic).get_stats().items():
        if key != "reading_time":
            features[f"readability_{key}"] = float(score)
    for key, score in DiversityStats(text, words_extractor=words).get_stats().items():
        features[f"diversity_{key}"] = float(score)
    doc = _parse(text, nlp)
    features.update(_morph_features(MorphStats(doc), doc.has_annotation("DEP")))
    features.update(
        sentence_rhythm(count_words_by_spans([start for start, _, _ in positions], spans))
    )
    features.update(
        (f"punct_{key}", float(value))
        for key, value in punctuation_profile(text, basic.n_words).items()
    )
    return features


def _parse(text: str, nlp: Language | None) -> Doc:
    """Parsing a text for the morphology: the default model without its parser, or the pipeline"""
    pipeline = nlp or get_nlp()
    if len(text) > pipeline.max_length:
        raise SourceError(
            f"The text of {len(text)} characters is longer than the limit of the "
            f"pipeline ({pipeline.max_length}): split it into windows or raise "
            "max_length on a pipeline of your own and pass it in nlp"
        )
    return pipeline(text, disable=["parser", "ner"] if nlp is None else ["ner"])


def _morph_features(morph: MorphStats, parsed: bool) -> dict[str, float]:
    """
    Morphological features of text_features: the shares of the values of every feature
    (of all the words for the parts of speech and the features of a single value, of the
    words that carry the feature for the others, a value of several values shared equally
    among its parts) and the markers but the ones of the moods; p_ser only for a parse
    with dependencies
    """
    n_words = len(morph.words)
    features: dict[str, float] = {}
    for category, desc in MORPHOLOGY_STATS_DESC.items():
        labels: Any = desc["values"]
        counts: defaultdict[str, float] = defaultdict(float)
        for tag, count in morph.get_stats(category, filter_none=True)[category].items():
            parts = tag.split(",")
            for part in parts:
                counts[part] += count / len(parts)
        denominator = n_words if category == "pos" or len(labels) == 1 else sum(counts.values())
        for label in labels:
            features[f"morph_{category}_{label}"] = (
                counts[label] / denominator if denominator else nan
            )
    for marker, share in morph.get_markers().items():
        if marker not in FINITE_MOODS and (parsed or marker != "p_ser"):
            features[f"morph_{marker}"] = float(share)
    return features


class _FixedWordsExtractor(WordsExtractor):
    """Extractor with ready words, so that the text is not tokenized twice"""

    def __init__(self, words: tuple[str, ...]) -> None:
        super().__init__()
        self.words = words

    def extract(self, text: str) -> tuple[str, ...]:
        return self.words


class _FixedSentsExtractor(SentsExtractor):
    """Extractor with ready sentences, so that the text is not split twice"""

    def __init__(self, sents: tuple[str, ...]) -> None:
        super().__init__()
        self.sents = sents

    def extract(self, text: str) -> tuple[str, ...]:
        return self.sents


def sentence_rhythm(lengths: Sequence[int]) -> dict[str, float]:
    """
    Computing the features of the rhythm of the sentences

    Description:
        The mean length of a sentence in words, the standard deviation, the
        coefficient of variation and the autocorrelation at lag 1 - the link
        between the lengths of neighbouring sentences (Yule 1939); the
        autocorrelation needs at least three sentences

    Arguments:
        lengths (list[int]): Lengths of the sentences in words

    Returns:
        dict[str, float]: Features sents_mean, sents_std, sents_cv, sents_autocorr

    Example:
        >>> from ests.corpus import sentence_rhythm
        >>> {key: round(value, 3) for key, value in sentence_rhythm([4, 8, 2, 7]).items()}
        {'sents_mean': 5.25, 'sents_std': 2.754, 'sents_cv': 0.525, 'sents_autocorr': -0.794}
    """
    values = np.asarray(lengths, dtype=float)
    if not len(values):
        return dict.fromkeys(("sents_mean", "sents_std", "sents_cv", "sents_autocorr"), nan)
    mean = float(values.mean())
    std = float(values.std(ddof=1)) if len(values) > 1 else nan
    centered = values - mean
    variance = float((centered**2).sum())
    autocorr = (
        float((centered[:-1] * centered[1:]).sum() / variance)
        if len(values) > 2 and variance
        else nan
    )
    return {
        "sents_mean": mean,
        "sents_std": std,
        "sents_cv": std / mean if mean and not isnan(std) else nan,
        "sents_autocorr": autocorr,
    }


def corpus_features(
    texts: Sequence[str],
    window: int | None = 1000,
    features: Features = text_features,
    min_words: int | None = None,
) -> pd.DataFrame:
    """
    Computing the features of the windows of a corpus

    Description:
        Every text is split into windows (split_windows), and the features are
        computed for every window; rows are the windows indexed by (number of
        the text, number of the window), columns the features. Texts without
        words or shorter than min_words are skipped

    Arguments:
        texts (list[str]): Texts of the corpus
        window (int): Size of a window in words; None - the whole texts
        features (callable): Function of the features of a text; text_features by default
        min_words (int): Smallest number of words in a window; None - half a
            window, or one when window is None

    Returns:
        DataFrame: Features of the windows

    Raises:
        SourceTypeError: If a string is passed instead of a list of texts
        SourceError: If the corpus has no window of enough words
        ParameterError: If the size of a window or min_words is below one

    Example:
        >>> from ests.corpus import corpus_features
        >>> texts = ["El gato duerme. El perro come.", "Llueve."]
        >>> corpus_features(texts, window=3, features=lambda text: {"chars": len(text)}, min_words=1)
                     chars
        text window
        0    0        15.0
             1        14.0
        1    0         7.0
    """
    check_sequence(texts, "texts")
    rows = {}
    for text_index, text in enumerate(texts):
        for window_index, chunk in enumerate(split_windows(text, window, min_words)):
            rows[text_index, window_index] = dict(features(chunk))
    if not rows:
        raise SourceError("The data source has no window of enough words")
    table = pd.DataFrame.from_dict(rows, orient="index").astype(float)
    table.index = pd.MultiIndex.from_tuples(table.index, names=["text", "window"])
    return table


def compare_corpora(
    a: Sequence[str],
    b: Sequence[str],
    window: int | None = 1000,
    features: Features | None = None,
    labels: tuple[str, str] = ("A", "B"),
    n_bootstrap: int = 1000,
    seed: int | None = 0,
    min_words: int | None = None,
) -> pd.DataFrame:
    """
    Comparing two corpora by every feature of a text

    Description:
        The texts of both corpora are split into windows of about the same
        size, so that the features do not depend on the length, the features
        are computed for every window (text_features or a function of one's
        own), and for every feature the two sets of values are compared: the
        means and the medians, the difference of the medians with its 95%
        percentile bootstrap interval, Cohen's d, Cliff's delta, the AUC of
        the feature as a classifier on its own (the share of the pairs of
        windows where the value in A is greater than in B, ties counted as
        half; Cliff's delta equals 2·AUC − 1), the Mann-Whitney U test with a
        two-sided p-value and Holm's correction for the number of features.
        Undefined and infinite values of a feature are dropped, and with fewer
        than two values on a side the statistics of the feature are nan. The
        rows are sorted by descending absolute Cliff's delta, the features
        without statistics go last
        The test and the effect sizes take the windows as independent, and
        the windows of one text are not: they share its plot, characters,
        narrator and edition. With few texts in a corpus the p-values are too
        small and reflect the texts chosen as much as the corpora - two novels
        of one author differ in dozens of features by the same test. The
        bootstrap resamples whole texts instead (a cluster bootstrap over the
        level text of the index of corpus_features), so its interval accounts
        for the spread between texts; n_texts_<name> gives the number of texts
        behind the windows
        One tool for authorship attribution, the comparison of genres and of
        translations, telling generated texts from human ones; keyness does
        the same for single words

    References:
        https://doi.org/10.1037/0033-2909.114.3.494
        https://en.wikipedia.org/wiki/Mann–Whitney_U_test

    Arguments:
        a (list[str]): Texts of the first corpus
        b (list[str]): Texts of the second corpus
        window (int): Size of a window in words; None - the whole texts
        features (callable): Function of the features of a text; None - text_features
        labels (tuple[str, str]): Names of the corpora for the columns (mean_<a>, ...)
        n_bootstrap (int): Number of bootstrap samples
        seed (int): Seed of the random number generator; None - a random one
        min_words (int): Smallest number of words in a window; None - half a
            window, or one when window is None

    Returns:
        DataFrame: Features × statistics of the comparison (COMPARISON_COLUMNS
            with the names of the corpora in the columns)

    Raises:
        SourceTypeError: If a string is passed instead of a list of texts
        SourceError: If one of the corpora has no window of enough words
        ParameterError: If the number of samples, the size of a window or
            min_words is below one

    Example:
        >>> from ests.corpus import compare_corpora
        >>> short = ["El gato duerme.", "Llueve mucho.", "El perro come."]
        >>> long = ["El gato duerme en la cama grande.", "El perro come carne en la cocina."]
        >>> result = compare_corpora(short, long, window=None, features=lambda text: {"chars": len(text)})
        >>> result.loc["chars", ["mean_A", "mean_B", "cliff_delta"]].tolist()
        [14.0, 33.0, -1.0]
    """
    if n_bootstrap < 1:
        raise ParameterError("The number of bootstrap samples must be greater than 0")
    feature_function = features or text_features
    table_a = corpus_features(a, window, feature_function, min_words)
    table_b = corpus_features(b, window, feature_function, min_words)
    return compare_features(table_a, table_b, labels, n_bootstrap, seed)


def compare_features(
    table_a: pd.DataFrame,
    table_b: pd.DataFrame,
    labels: tuple[str, str] = ("A", "B"),
    n_bootstrap: int = 1000,
    seed: int | None = 0,
) -> pd.DataFrame:
    """
    Comparing two corpora by ready tables of the features of their windows

    Description:
        The second half of compare_corpora: the tables of features
        (corpus_features or one's own) are compared column by column, as
        described there. It serves when the features are computed once for
        several corpora and pairs of them are to be compared - all the authors
        pairwise, for instance. The windows of a text are told by the level
        text of the index, which corpus_features sets: the bootstrap resamples
        whole texts; a table without that level takes every row for a text of
        its own. A column missing from one of the tables is compared with an
        empty set of values and gives nan

    Arguments:
        table_a (DataFrame): Features of the windows of the first corpus (rows - the windows)
        table_b (DataFrame): Features of the windows of the second corpus
        labels (tuple[str, str]): Names of the corpora for the columns (mean_<a>, ...)
        n_bootstrap (int): Number of bootstrap samples
        seed (int): Seed of the random number generator; None - a random one

    Returns:
        DataFrame: Features × statistics of the comparison (COMPARISON_COLUMNS
            with the names of the corpora in the columns)

    Raises:
        ParameterError: If the number of samples is below one
    """
    if n_bootstrap < 1:
        raise ParameterError("The number of bootstrap samples must be greater than 0")
    rng = np.random.default_rng(seed)
    rows = {}
    for name in table_a.columns.union(table_b.columns, sort=False):
        values_a, texts_a = _finite(table_a, name)
        values_b, texts_b = _finite(table_b, name)
        rows[name] = compare_values(values_a, values_b, n_bootstrap, rng, texts_a, texts_b)
    result = pd.DataFrame.from_dict(rows, orient="index", columns=list(COMPARISON_COLUMNS))
    result["p_holm"] = holm_correction(result["p_value"].to_numpy())
    result = result.iloc[(-result["cliff_delta"].abs()).fillna(np.inf).argsort(kind="stable")]
    counts = ["n_a", "n_b", "n_texts_a", "n_texts_b"]
    result[counts] = result[counts].astype(int)
    label_a, label_b = labels
    return result.rename(
        columns={
            "mean_a": f"mean_{label_a}",
            "mean_b": f"mean_{label_b}",
            "median_a": f"median_{label_a}",
            "median_b": f"median_{label_b}",
            "n_a": f"n_{label_a}",
            "n_b": f"n_{label_b}",
            "n_texts_a": f"n_texts_{label_a}",
            "n_texts_b": f"n_texts_{label_b}",
        }
    )


def _finite(table: pd.DataFrame, name: str) -> tuple[np.ndarray, np.ndarray | None]:
    """
    Finite values of a column of a table and the texts of their windows

    Description:
        The texts come from the level text of the index; without it they are
        None, and every row is a text of its own. A missing column gives an
        empty array
    """
    if name not in table:
        return np.array([]), None
    values = table[name].to_numpy(dtype=float)
    finite = np.isfinite(values)
    texts = (
        table.index.get_level_values("text").to_numpy()[finite]
        if "text" in table.index.names
        else None
    )
    return np.asarray(values[finite], dtype=float), texts


def compare_values(
    values_a: np.ndarray,
    values_b: np.ndarray,
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
    texts_a: np.ndarray | None = None,
    texts_b: np.ndarray | None = None,
) -> tuple[float, ...]:
    """
    Comparing two sets of values of a feature

    Arguments:
        values_a (ndarray): Finite values in the first corpus
        values_b (ndarray): Finite values in the second corpus
        n_bootstrap (int): Number of bootstrap samples
        rng (Generator): Random number generator
        texts_a (ndarray): Texts of the values in the first corpus for the
            bootstrap; None - every value a text of its own
        texts_b (ndarray): Texts of the values in the second corpus

    Returns:
        tuple[float, ...]: Values in the order of COMPARISON_COLUMNS, p_holm - nan
    """
    n_a, n_b = len(values_a), len(values_b)
    n_texts_a = n_a if texts_a is None else len(np.unique(texts_a))
    n_texts_b = n_b if texts_b is None else len(np.unique(texts_b))
    if n_a < 2 or n_b < 2:
        return (*(nan,) * 13, n_a, n_b, n_texts_a, n_texts_b)
    u, p_value = mannwhitneyu(values_a, values_b, alternative="two-sided")
    auc = float(u) / (n_a * n_b)
    ci_low, ci_high = bootstrap_median_diff(
        values_a, values_b, n_bootstrap, rng, texts_a=texts_a, texts_b=texts_b
    )
    return (
        float(values_a.mean()),
        float(values_b.mean()),
        float(np.median(values_a)),
        float(np.median(values_b)),
        float(np.median(values_a) - np.median(values_b)),
        ci_low,
        ci_high,
        calc_cohen_d(values_a, values_b),
        2 * auc - 1,
        auc,
        float(u),
        float(p_value),
        nan,
        n_a,
        n_b,
        n_texts_a,
        n_texts_b,
    )


def calc_cohen_d(values_a: Values, values_b: Values) -> float:
    """
    Computing Cohen's d - the standardized difference of the means

    Description:
        (mean_a − mean_b) / s, where s is the pooled standard deviation with
        the sample variances (ddof=1); by Cohen 0.2 is a small effect, 0.5
        a medium one, 0.8 a large one

    Arguments:
        values_a (list[float]): Values in the first corpus
        values_b (list[float]): Values in the second corpus

    Returns:
        float: Cohen's d, nan with fewer than two values on a side or a zero variance

    Example:
        >>> from ests.corpus import calc_cohen_d
        >>> round(calc_cohen_d([2, 4, 6, 8], [1, 3, 5, 7]), 3)
        0.387
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if len(a) < 2 or len(b) < 2:
        return nan
    pooled = ((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2)
    if not pooled:
        return nan
    return float((a.mean() - b.mean()) / sqrt(pooled))


def calc_cliff_delta(values_a: Values, values_b: Values) -> float:
    """
    Computing Cliff's delta - a probabilistic effect size

    Description:
        The share of the pairs (x from A, y from B) with x > y minus the share
        of the pairs with x < y (Cliff 1993); from −1 to 1, 0 - the
        distributions do not differ; |δ| < 0.147 - a negligible effect,
        < 0.33 - small, < 0.474 - medium, a large one otherwise (Romano et al. 2006)

    Arguments:
        values_a (list[float]): Values in the first corpus
        values_b (list[float]): Values in the second corpus

    Returns:
        float: Cliff's delta, nan for an empty set

    Example:
        >>> from ests.corpus import calc_cliff_delta
        >>> calc_cliff_delta([2, 4, 6, 8], [1, 3, 5, 7])
        0.25
    """
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if not len(a) or not len(b):
        return nan
    comparison = np.sign(a[:, None] - b[None, :])
    return float(comparison.mean())


def bootstrap_median_diff(
    values_a: Values,
    values_b: Values,
    n_bootstrap: int = 1000,
    rng: np.random.Generator | None = None,
    confidence: float = 0.95,
    texts_a: Values | None = None,
    texts_b: Values | None = None,
) -> tuple[float, float]:
    """
    Computing the percentile bootstrap interval of the difference of the medians

    Description:
        Both sets are resampled with replacement n_bootstrap times, for every
        pair of samples median_a − median_b is computed, and the bounds of the
        interval are the percentiles (1 − confidence) / 2 and
        1 − (1 − confidence) / 2. With the texts of the values given, whole
        texts are resampled with all their values (a cluster bootstrap), so
        that the interval accounts for the spread between the texts and not
        only between the windows of a text; it then needs at least two texts
        on each side

    Arguments:
        values_a (list[float]): Values in the first corpus
        values_b (list[float]): Values in the second corpus
        n_bootstrap (int): Number of samples
        rng (Generator): Random number generator; None - a new one without a seed
        confidence (float): Confidence level
        texts_a (list): Texts of the values in the first corpus; None - every
            value is resampled on its own
        texts_b (list): Texts of the values in the second corpus

    Returns:
        tuple[float, float]: Lower and upper bounds, nan for an empty set or,
            with the texts given, fewer than two texts on a side

    Raises:
        ParameterError: If the number of samples is below one or the confidence
            level is outside the interval (0, 1)

    Example:
        >>> from ests.corpus import bootstrap_median_diff
        >>> bootstrap_median_diff([3.0, 3.0, 3.0], [1.0, 1.0, 1.0], n_bootstrap=10)
        (2.0, 2.0)
    """
    if n_bootstrap < 1:
        raise ParameterError("The number of bootstrap samples must be greater than 0")
    if not 0 < confidence < 1:
        raise ParameterError("The confidence level must lie in the interval (0, 1)")
    a = np.asarray(values_a, dtype=float)
    b = np.asarray(values_b, dtype=float)
    if not len(a) or not len(b):
        return nan, nan
    if any(texts is not None and len(np.unique(texts)) < 2 for texts in (texts_a, texts_b)):
        return nan, nan
    generator = rng if rng is not None else np.random.default_rng()
    differences = _resampled_medians(a, texts_a, n_bootstrap, generator) - _resampled_medians(
        b, texts_b, n_bootstrap, generator
    )
    tail = (1 - confidence) / 2 * 100
    low, high = np.percentile(differences, [tail, 100 - tail])
    return float(low), float(high)


def _resampled_medians(
    values: np.ndarray, texts: Values | None, n_bootstrap: int, generator: np.random.Generator
) -> np.ndarray:
    """
    Medians of bootstrap samples of values, drawn one by one or by whole texts

    Description:
        A draw of texts is the number of times every text is taken; the median
        of the sample is read from the sorted values weighted by those numbers:
        the values of ranks (N − 1) // 2 and N // 2 of the N values of the
        sample, averaged, as np.median of the sample itself
    """
    if texts is None:
        return np.asarray(
            np.median(generator.choice(values, size=(n_bootstrap, len(values))), axis=1)
        )
    labels, inverse = np.unique(np.asarray(texts), return_inverse=True)
    draws = generator.multinomial(len(labels), np.full(len(labels), 1 / len(labels)), n_bootstrap)
    order = np.argsort(values, kind="stable")
    cumulative = draws[:, inverse[order]].cumsum(axis=1)
    total = cumulative[:, -1:]
    lower = (cumulative > (total - 1) // 2).argmax(axis=1)
    upper = (cumulative > total // 2).argmax(axis=1)
    ordered = values[order]
    return np.asarray((ordered[lower] + ordered[upper]) / 2)


def holm_correction(p_values: Sequence[float]) -> np.ndarray:
    """
    Holm's correction for multiple comparisons

    Description:
        The p-values are sorted in ascending order, the i-th is multiplied by
        (m − i + 1), where m is the number of defined values, then the
        running maximum is taken and capped at one; nan stays nan

    Arguments:
        p_values (list[float]): p-values

    Returns:
        ndarray: Corrected p-values in the original order

    Example:
        >>> from ests.corpus import holm_correction
        >>> holm_correction([0.01, 0.04, 0.03]).round(3).tolist()
        [0.03, 0.06, 0.06]
    """
    values = np.asarray(p_values, dtype=float)
    adjusted = np.full(len(values), nan)
    defined = np.flatnonzero(~np.isnan(values))
    if not len(defined):
        return adjusted
    order = defined[np.argsort(values[defined], kind="stable")]
    m = len(order)
    scaled = values[order] * (m - np.arange(m))
    adjusted[order] = np.minimum(np.maximum.accumulate(scaled), 1.0)
    return adjusted
