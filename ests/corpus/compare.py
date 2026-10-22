from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from math import nan
from typing import Any

import anyts.corpus.compare
import numpy as np
import pandas as pd
from anyts.corpus.compare import (
    COMPARISON_COLUMNS as COMPARISON_COLUMNS,
    bootstrap_median_diff as bootstrap_median_diff,
    calc_cliff_delta as calc_cliff_delta,
    calc_cohen_d as calc_cohen_d,
    check_comparison_params as check_comparison_params,
    compare_features as compare_features,
    holm_correction as holm_correction,
    sentence_rhythm as sentence_rhythm,
)
from anyts.extractors import FixedSentsExtractor, FixedWordsExtractor
from anyts.utils import check_words
from spacy.language import Language
from spacy.tokens import Doc

from ..basic_stats import BasicStats, punctuation_profile
from ..constants import MORPHOLOGY_STATS_DESC, OPENING_MARKS, SYMMETRIC_MARKS
from ..diversity_stats import DiversityStats
from ..exceptions import SourceError, SourceTypeError
from ..morph_stats import FINITE_MOODS, MorphStats
from ..readability_stats import ReadabilityStats
from ..utils import (
    count_words_by_spans,
    get_nlp,
    iter_text_sents,
    iter_text_words,
)

Features = Callable[[str], Mapping[str, float]]


def split_windows(text: str, window: int | None = 1000, min_words: int | None = None) -> list[str]:
    """
    Splitting a text into windows of words

    Description:
        Consecutive windows of exactly window words, so the features that
        depend on length are comparable between texts; the rest at the end is a
        window only with at least min_words words (by default a whole window, so
        the rest is dropped). A boundary goes before the first word of a window
        and the opening marks before it (OPENING_MARKS); a straight quote or a
        dash glued to the last word of the previous window or after a closing
        mark closes that window (SYMMETRIC_MARKS). The windows are stripped of
        whitespace and keep their punctuation; window=None gives the whole text.
        The split_windows of the core with the words of iter_text_words and the
        Spanish marks

    Arguments:
        text (str): Text string
        window (int): Size of a window in words; None - the whole text
        min_words (int): Smallest number of words in a window; None - a whole
            window, or one word when window is None

    Returns:
        list[str]: Windows of the text; an empty list for a text without words
            or shorter than min_words

    Raises:
        SourceTypeError: If the text is not a string
        ParameterError: If the size of a window or min_words is not an integer or is
            below one, or min_words is greater than the window

    Example:
        >>> from ests.corpus import split_windows
        >>> split_windows("El gato duerme mucho. ¿Dónde está el perro?", 4)
        ['El gato duerme mucho.', '¿Dónde está el perro?']
        >>> split_windows('Dijo "adiós" y se fue ya', 2)
        ['Dijo "adiós"', 'y se', 'fue ya']
    """
    return anyts.corpus.compare.split_windows(
        text,
        window,
        min_words,
        tokenize=iter_text_words,
        opening_marks=OPENING_MARKS,
        symmetric_marks=SYMMETRIC_MARKS,
    )


def _check_windows(window: int | None, min_words: int | None) -> None:
    """Checking the size of a window and the smallest number of words in it before the texts"""
    split_windows("", window, min_words)


def text_features(text: str, nlp: Language | None = None) -> dict[str, float]:
    """
    Computing the features of a text for the comparison of corpora

    Description:
        Features prefixed by their source: basic_ - the shares of long,
        complex, simple, mono- and polysyllabic words, of letters, spaces and
        punctuation marks, the mean number of letters and syllables per word
        (BasicStats); readability_ - every readability formula and the
        consensus grade except the reading time (ReadabilityStats); diversity_ -
        every measure of lexical diversity (DiversityStats); morph_ - the
        shares of the values of every feature of MORPHOLOGY_STATS_DESC and the
        markers of MorphStats.get_markers except the moods; sents_ - the rhythm
        of the sentences (sentence_rhythm); punct_ - punctuation_profile
        A morphological value that does not occur gives 0, a feature absent
        from the window (no verbs - no tense) nan. The parts of speech and the
        features of a single value (polarity, polite, poss, reflex) are shares
        of all the words, the other features shares of the words that carry
        them; a value of several values (PronType=Int,Rel) is shared equally
        among its parts. The default model runs without its parser; a
        pipeline passed in nlp runs whole except the entity recognizer, and
        with a parser it adds morph_p_ser
        The shares of spaces, letters and marks count the characters as they
        are: in a corpus from different editions collapse the whitespace beforehand

    Arguments:
        text (str): Text string
        nlp (Language): Pipeline for the morphology; None - the default model
            without its parser

    Returns:
        dict[str, float]: Features; the undefined values are nan

    Raises:
        SourceTypeError: If the text is not a string or the pipeline is not a spaCy Language
        SourceError: If the text has no words or is longer than the max_length
            of the pipeline
        DatasetNotFoundError: If the default model is not installed

    Example:
        >>> from ests.corpus import text_features
        >>> features = text_features("El gato duerme. El perro come y juega en el jardín.")
        >>> features["sents_mean"], round(features["morph_pos_DET"], 3)
        (5.5, 0.273)
    """
    if not isinstance(text, str):
        raise SourceTypeError(f"A text string is expected, not {type(text).__name__}")
    if nlp is not None and not isinstance(nlp, Language):
        raise SourceTypeError("The pipeline must be a spaCy Language")
    positions = list(iter_text_words(text))
    spans = [(start, stop) for start, stop, _ in iter_text_sents(text)]
    words = FixedWordsExtractor([word for _, _, word in positions])
    sents = FixedSentsExtractor([text[start:stop] for start, stop in spans])
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
    """Parsing a text: the default model without its parser, or the pipeline without ner"""
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
    Morphological features of text_features: the shares of the values of every feature and
    the markers except the moods; p_ser only for a parse with dependencies
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
        min_words (int): Smallest number of words in a window; None - a whole
            window, or one word when window is None

    Returns:
        DataFrame: Features of the windows

    Raises:
        SourceTypeError: If the texts are not a list of strings or the features are not a function
        SourceError: If the corpus has no window of enough words
        ParameterError: If the size of a window or min_words is not an integer or is
            below one, or min_words is greater than the window
        DatasetNotFoundError: If the default features need the model and it is not installed

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
    check_words(texts, "texts")
    if not callable(features):
        raise SourceTypeError(f"The features must be a function, not {type(features).__name__}")
    _check_windows(window, min_words)
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
    seed: int | np.random.Generator | None = 0,
    min_words: int | None = None,
) -> pd.DataFrame:
    """
    Comparing two corpora by every feature of a text

    Description:
        The texts are split into windows (split_windows), the features are
        computed for every window, and for every feature the two sets of
        values are compared: the means and the medians, the difference of the
        medians with its 95% bootstrap interval, Cohen's d, Cliff's delta,
        the AUC (the share of the pairs of windows where the value in A is
        greater than in B, ties counted as half; Cliff's delta = 2·AUC − 1),
        the two-sided Mann-Whitney U test and Holm's correction for the number
        of features. Undefined and infinite values are dropped; with fewer
        than two values on a side the statistics are nan. The rows are sorted
        by descending absolute Cliff's delta, the features without statistics
        last
        The test and the effect sizes take the windows as independent, while
        the windows of one text are not: with few texts the p-values are too
        small. The bootstrap resamples whole texts, so its interval accounts
        for the spread between texts; n_texts_<name> gives the number of texts

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
        seed (int|Generator): Seed of the random number generator or the generator
            itself; None - a random one
        min_words (int): Smallest number of words in a window; None - a whole
            window, or one word when window is None

    Returns:
        DataFrame: Features × statistics of the comparison (COMPARISON_COLUMNS
            with the names of the corpora in the columns)

    Raises:
        SourceTypeError: If the texts are not a list of strings or the features are not a function
        SourceError: If one of the corpora has no window of enough words
        ParameterError: If the names of the corpora are not two strings that give
            distinct columns, the number of samples, the size of a window or min_words
            is not an integer or is below one, min_words is greater than the window, or
            the seed is set incorrectly

    Example:
        >>> from ests.corpus import compare_corpora
        >>> short = ["El gato duerme.", "Llueve mucho.", "El perro come."]
        >>> long = ["El gato duerme en la cama grande.", "El perro come carne en la cocina."]
        >>> result = compare_corpora(short, long, window=None, features=lambda text: {"chars": len(text)})
        >>> result.loc["chars", ["mean_A", "mean_B", "cliff_delta"]].tolist()
        [14.0, 33.0, -1.0]
    """
    check_comparison_params(labels, n_bootstrap, seed)
    check_words(a, "texts")
    check_words(b, "texts")
    _check_windows(window, min_words)
    feature_function = text_features if features is None else features
    table_a = corpus_features(a, window, feature_function, min_words)
    table_b = corpus_features(b, window, feature_function, min_words)
    return compare_features(table_a, table_b, labels, n_bootstrap, seed)
