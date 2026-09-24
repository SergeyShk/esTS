from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from math import e, inf, isnan, log, log2, nan
from typing import Any, NamedTuple

import numpy as np
from scipy.stats import chi2 as chi2_distribution

from ..constants import KEYNESS_MEASURES
from ..datasets.freq_dict import CORPUS_SIZE, FreqDict, lemma_key
from ..exceptions import ParameterError, SourceError
from ..utils import check_sequence

ZERO_ADJUSTMENT = 0.5


class Keyword(NamedTuple):
    """
    Keyword - the result of comparing the frequencies of two corpora

    Attributes:
        word (str): Word
        freq_target (int): Frequency in the target corpus
        freq_reference (float): Frequency in the reference corpus
        ipm_target (float): Frequency in the target corpus per million words
        ipm_reference (float): Frequency in the reference corpus per million words
        g2 (float): Log-likelihood G² signed by its direction
        p_value (float): p-value of G² by the chi-square distribution with one
            degree of freedom
        log_ratio (float): Binary logarithm of the ratio of normalized frequencies
        score (float): Value of the chosen measure
    """

    word: str
    freq_target: int
    freq_reference: float
    ipm_target: float
    ipm_reference: float
    g2: float
    p_value: float
    log_ratio: float
    score: float


def keyness(
    target: Sequence[str] | Mapping[str, int],
    reference: Sequence[str] | Mapping[str, float] | FreqDict,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
) -> list[Keyword]:
    """
    Finding the keywords of a target corpus against a reference one

    Description:
        Words are compared by their frequencies in the two corpora: for every
        word the log-likelihood G² with its p-value (the significance of the
        difference) and Log Ratio (the size of the effect) are computed, as
        Gabrielatos and Hardie recommend, together with the chosen measure
        score, which the list is sorted by. The measures of significance (G²,
        chi-square, BIC, ELL) are signed: negative when the word is more
        frequent in the reference
        The reference may be a list of words or their frequencies, with the
        size of the reference taken as their sum, or the frequency dictionary
        FreqDict: then the words of the target corpus go to the keys of the
        dictionary by lemma_key (a word form to its lemma, a lemma stays as it
        is), so the keywords are lemmas, and the frequency of a lemma in the
        reference is its ipm times the size of the corpus of the dictionary
        (CORPUS_SIZE, 63 billion words of books of 1980-2019). Without the
        parts of speech a proper noun goes to its lemma too (París - parir),
        while an unknown name stays as it is (Madrid - madrid)
        A zero frequency in one of the corpora is replaced with 0.5 for %DIFF,
        Log Ratio and the odds ratio (Hardie 2014)
        Positive keywords are more frequent in the target corpus, negative ones
        in the reference; min_freq is the least frequency of a word in the
        corpus where it is more frequent

    References:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Arguments:
        target (list[str]|dict[str, int]): Words of the target corpus or their frequencies
        reference (list[str]|dict[str, float]|FreqDict): Words of the reference
            corpus, their frequencies or the frequency dictionary
        measure (str): Measure of KEYNESS_MEASURES for score and the sorting
        min_freq (int): Minimum frequency of a keyword in its own corpus
        positive (bool): Positive keywords (True) or negative ones (False)
        top_n (int): Number of keywords; None - all of them

    Returns:
        list[Keyword]: Keywords by descending keyness, then by descending
            frequency and alphabetically; words of an undefined measure last

    Raises:
        SourceTypeError: If a string is passed instead of a list of words
        ParameterError: If the measure is unknown or top_n is below one
        SourceError: If one of the corpora is empty
        DatasetNotFoundError: If the frequency dictionary is not downloaded

    Example:
        >>> from ests.corpus import keyness
        >>> target = "el gato duerme y el gato come".split()
        >>> reference = "el perro duerme y el perro come".split()
        >>> [(k.word, round(k.g2, 2)) for k in keyness(target, reference)]
        [('gato', 2.77)]
    """
    if measure not in KEYNESS_MEASURES:
        raise ParameterError(f"Unknown measure of keyness: {measure}")
    if top_n is not None and top_n < 1:
        raise ParameterError("The number of keywords must be greater than 0")
    check_sequence(target)
    check_sequence(reference)
    counts_reference: Mapping[str, float]
    if isinstance(reference, FreqDict):
        counts_target = _count(target, key=lemma_key)
        size_reference = float(CORPUS_SIZE)
        counts_reference = {
            lemma: entry.ipm * size_reference / 1e6 for lemma, entry in reference.entries.items()
        }
    else:
        counts_target = _count(target)
        counts_reference = _count(reference)
        size_reference = float(sum(counts_reference.values()))
    size_target = float(sum(counts_target.values()))
    if not size_target or not size_reference:
        raise SourceError("The data source has no words")
    calc = MEASURES[measure]
    rows = []
    words = set(counts_target) | set(counts_reference)
    for word in words:
        a = counts_target.get(word, 0)
        b = counts_reference.get(word, 0)
        ipm_target = a / size_target * 1e6
        ipm_reference = b / size_reference * 1e6
        if ipm_target == ipm_reference or (ipm_target > ipm_reference) != positive:
            continue
        if (a if positive else b) < min_freq:
            continue
        rows.append(
            (
                word,
                int(a),
                b,
                ipm_target,
                ipm_reference,
                calc_log_likelihood(a, b, size_target, size_reference),
                calc_log_ratio(a, b, size_target, size_reference),
                calc(a, b, size_target, size_reference),
            )
        )
    p_values = calc_p_value(np.array([row[5] for row in rows]))
    keywords = [
        Keyword(*row[:6], float(p_value), *row[6:])
        for row, p_value in zip(rows, p_values, strict=True)
    ]
    sign = -1 if positive else 1
    keywords.sort(
        key=lambda keyword: (
            isnan(keyword.score),
            sign * (0.0 if isnan(keyword.score) else keyword.score),
            -(keyword.freq_target if positive else keyword.freq_reference),
            keyword.word,
        )
    )
    return keywords[:top_n] if top_n else keywords


def _count(
    words: Sequence[str] | Mapping[str, float], key: Callable[[str], str] | None = None
) -> Mapping[str, float]:
    """Frequencies of the words, summed by key when one is given"""
    if key is None:
        return words if isinstance(words, Mapping) else Counter(words)
    counts: dict[str, float] = {}
    pairs = words.items() if isinstance(words, Mapping) else ((word, 1) for word in words)
    for word, count in pairs:
        counts[key(word)] = counts.get(key(word), 0) + count
    return counts


def _sign(a: float, b: float, c: float, d: float) -> int:
    return 1 if a / c >= b / d else -1


def _adjust(a: float, b: float) -> tuple[float, float]:
    return a or ZERO_ADJUSTMENT, b or ZERO_ADJUSTMENT


def calc_log_likelihood(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the log-likelihood G² of the frequencies of a word in two corpora

    Description:
        By Rayson and Garside (2000): the expected frequencies
        E1 = c·(a + b)/(c + d) and E2 = d·(a + b)/(c + d),
        G² = 2·(a·ln(a/E1) + b·ln(b/E2)); a term of zero frequency is zero.
        The critical values are in G2_CRITICAL_VALUES (3.84 for p < 0.05, 6.63
        for p < 0.01, 10.83 for p < 0.001, 15.13 for p < 0.0001)
        The sign is negative when the word is more frequent in the reference

    References:
        https://ucrel.lancs.ac.uk/llwizard.html

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Signed G²

    Example:
        >>> from ests.corpus.keyness import calc_log_likelihood
        >>> round(calc_log_likelihood(10, 2, 1000, 1000), 3)
        5.822
    """
    total = a + b
    if not total:
        return 0.0
    expected_a = c * total / (c + d)
    expected_b = d * total / (c + d)
    value = 2 * (_xlog(a, expected_a) + _xlog(b, expected_b))
    return _sign(a, b, c, d) * value


def _xlog(observed: float, expected: float) -> float:
    return observed * log(observed / expected) if observed else 0.0


def calc_p_value(g2: float | np.ndarray) -> Any:
    """
    Computing the p-value of a G² or a chi-square

    Arguments:
        g2 (float|ndarray): Value of G² or of the chi-square (the sign is not
            taken into account) or an array of values

    Returns:
        float|ndarray: p-value by the chi-square distribution with one degree of freedom
    """
    p_value = chi2_distribution.sf(np.abs(g2), 1)
    return float(p_value) if np.isscalar(g2) else p_value


def calc_chi2(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the chi-square with Yates's correction for the frequencies of a word in two corpora

    Description:
        Over the 2×2 contingency table of the word and the other words of each
        corpus, χ² = N·(|a·(d − b) − b·(c − a)| − N/2)² / ((a + b)·(c − a + d − b)·c·d),
        N = c + d
        The sign is negative when the word is more frequent in the reference

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Signed chi-square
    """
    total = c + d
    rest_a = c - a
    rest_b = d - b
    denominator = (a + b) * (rest_a + rest_b) * c * d
    if not denominator:
        return 0.0
    difference = max(abs(a * rest_b - b * rest_a) - total / 2, 0.0)
    return _sign(a, b, c, d) * total * difference**2 / denominator


def calc_diff(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the difference of normalized frequencies %DIFF

    Description:
        By Gabrielatos and Marchi (2011): (NF_a − NF_b) / NF_b · 100, where NF
        is the frequency per million words; a zero frequency is replaced with 0.5

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: %DIFF
    """
    a, b = _adjust(a, b)
    return (a / c - b / d) / (b / d) * 100


def calc_log_ratio(a: float, b: float, c: float, d: float) -> float:
    """
    Computing Log Ratio - the binary logarithm of the ratio of normalized frequencies

    Description:
        By Hardie (2014): log2(NF_a / NF_b); one - the word is twice as frequent
        in the target corpus; a zero frequency is replaced with 0.5

    References:
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Log Ratio
    """
    a, b = _adjust(a, b)
    return log2((a / c) / (b / d))


def calc_bic(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the Bayesian information criterion for G²

    Description:
        By Wilson (2013): BIC = G² − ln(N), N = c + d; values above 2 are
        positive evidence of a difference, above 6 strong, above 10 very strong
        Computed as sign(G²) · (|G²| − ln N): a positive value is evidence of a
        difference in the direction of the sign of G², a negative one no
        evidence, and then the sign of BIC differs from the sign of G²

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Signed BIC
    """
    g2 = calc_log_likelihood(a, b, c, d)
    return _sign(a, b, c, d) * (abs(g2) - log(c + d))


def calc_ell(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the effect size for the log-likelihood ELL

    Description:
        By Johnson, Culpeper and Rayson (2007): ELL = G² / (N · ln(min(E1, E2))),
        N = c + d; lies between 0 and 1. Signed as G²

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Signed ELL, nan when the least expected frequency is below e -
            there the denominator is below N and ELL leaves the interval from 0 to 1
    """
    total = a + b
    expected_min = min(c, d) * total / (c + d)
    if expected_min < e:
        return nan
    return calc_log_likelihood(a, b, c, d) / ((c + d) * log(expected_min))


def calc_odds_ratio(a: float, b: float, c: float, d: float) -> float:
    """
    Computing the odds ratio of a word in two corpora

    Description:
        (a / (c − a)) / (b / (d − b)); one - equal odds, a zero frequency is
        replaced with 0.5

    Arguments:
        a (float): Frequency of the word in the target corpus
        b (float): Frequency of the word in the reference corpus
        c (float): Size of the target corpus
        d (float): Size of the reference corpus

    Returns:
        float: Odds ratio; inf if the word fills the whole target corpus, 0 if
            it fills the whole reference, nan if both
    """
    a, b = _adjust(a, b)
    if a >= c and b >= d:
        return nan
    if a >= c:
        return inf
    if b >= d:
        return 0.0
    return (a / (c - a)) / (b / (d - b))


MEASURES = {
    "log_likelihood": calc_log_likelihood,
    "chi2": calc_chi2,
    "diff": calc_diff,
    "log_ratio": calc_log_ratio,
    "bic": calc_bic,
    "ell": calc_ell,
    "odds_ratio": calc_odds_ratio,
}
