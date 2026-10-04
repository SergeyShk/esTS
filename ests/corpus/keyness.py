from collections.abc import Mapping, Sequence

import anyts.corpus
from anyts.corpus.keyness import (
    FrequencyReference as FrequencyReference,
    Keyword as Keyword,
    calc_bic as calc_bic,
    calc_chi2 as calc_chi2,
    calc_diff as calc_diff,
    calc_ell as calc_ell,
    calc_log_likelihood as calc_log_likelihood,
    calc_log_ratio as calc_log_ratio,
    calc_odds_ratio as calc_odds_ratio,
    calc_p_value as calc_p_value,
    check_keyness_params,
)

from ..datasets.freq_dict import CORPUS_SIZE, WORD_PATTERN, FreqDict, lemma_key


def keyness(
    target: Sequence[str] | Mapping[str, int],
    reference: Sequence[str] | Mapping[str, float] | FreqDict | FrequencyReference,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
) -> list[Keyword]:
    """
    Finding the keywords of a target corpus against a reference one

    Description:
        For every word the log-likelihood G² with its p-value (significance)
        and Log Ratio (effect size) are computed, as Gabrielatos and Hardie
        recommend, with the chosen measure score, which sorts the list. The
        measures of significance (G², chi-square, BIC, ELL) are negative when
        the word is more frequent in the reference. A zero frequency is
        replaced with 0.5 for %DIFF, Log Ratio and the odds ratio (Hardie 2014)
        The reference may be a list of words, their frequencies (the size is
        their sum), FreqDict or a FrequencyReference. Against FreqDict the
        target is to be word forms, not lemmas, with the stop words kept; the
        forms not made of the letters of WORD_PATTERN are left out, and both
        sides go to keys by lemma_key, so the keywords are lemmas, some with
        the label of another lemma (Roma - romo). The reference frequency of
        a key is its ipm times CORPUS_SIZE; a word out of the dictionary gets
        its least frequency, an upper bound, so it may be a positive keyword
        but never a negative one
        Positive keywords are more frequent in the target corpus, negative ones
        in the reference; min_freq is the least frequency of a word in the
        corpus where it is more frequent

    References:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Arguments:
        target (list[str]|dict[str, int]): Words of the target corpus or their
            frequencies; word forms against the frequency dictionary
        reference (list[str]|dict[str, float]|FreqDict|FrequencyReference): Words
            of the reference corpus, their frequencies, the frequency dictionary
            or a reference by frequencies
        measure (str): Measure of KEYNESS_MEASURES for score and the sorting
        min_freq (int): Minimum frequency of a keyword in its own corpus
        positive (bool): Positive keywords (True) or negative ones (False)
        top_n (int): Number of keywords; None - all of them

    Returns:
        list[Keyword]: Keywords by descending keyness, then by descending
            frequency and alphabetically; words of an undefined measure last

    Raises:
        SourceTypeError: If the words are not a list of strings
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
    if isinstance(reference, FreqDict):
        check_keyness_params(measure, min_freq, top_n, target)
        reference = _frequency_reference(reference)
    return anyts.corpus.keyness(target, reference, measure, min_freq, positive, top_n)


def _frequency_reference(freq_dict: FreqDict) -> FrequencyReference:
    """The reference corpus of the frequency dictionary, as the docstring of keyness describes it"""
    size = float(CORPUS_SIZE)
    return FrequencyReference(
        {key: ipm * size / 1e6 for key, ipm in freq_dict.word_ipm.items()},
        size,
        freq_dict.min_ipm * size / 1e6,
        lemma_key,
        _is_dictionary_word,
    )


def _is_dictionary_word(word: str) -> bool:
    """Whether a word is made of the letters of the forms the frequency dictionary counts"""
    return WORD_PATTERN.fullmatch(word.lower()) is not None
