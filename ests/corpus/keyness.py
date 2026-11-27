from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import cast

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
    check_keyness_params as check_keyness_params,
)
from anyts.utils import has_words

from ..datasets.freq_dict import CORPUS_SIZE, WORD_PATTERN, FreqDict, lemma_key
from ..exceptions import ParameterError
from ..utils import _annotate_text, get_morph_analyzer


def keyness(
    target: str | Sequence[str] | Sequence[Sequence[str]] | Mapping[str, int],
    reference: Sequence[str]
    | Sequence[Sequence[str]]
    | Mapping[str, float]
    | FreqDict
    | FrequencyReference,
    measure: str = "log_likelihood",
    min_freq: int = 1,
    positive: bool = True,
    top_n: int | None = None,
    n: int = 1,
    *,
    messages: Mapping[str, str] | None = None,
) -> list[Keyword]:
    """
    Finding the keywords of a target corpus against a reference one

    Description:
        For every word the log-likelihood G² with its p-value (significance)
        and Log Ratio (effect size) are computed, as Gabrielatos and Hardie
        recommend, with the chosen measure score, which sorts the list. The
        measures of significance (G², chi-square, BIC) and ELL, the effect size
        of G², are negative when the word is more frequent in the reference. A zero frequency is
        replaced with 0.5 for %DIFF, Log Ratio and the odds ratio (Hardie 2014)
        A corpus of several texts is a list of their lists of words; with n
        above 1 the keywords are the n-grams of the words of every text, not
        across two texts
        A target text is split into the words of WordsExtractor, analyzed by
        esMorph in the context of its sentences. The reference may be a list of
        words, their frequencies (the size is their sum), FreqDict or a
        FrequencyReference. Against FreqDict the target is to be word forms, not
        lemmas, in their case and with the stop words kept (a name in lower case
        may be read as another word in context: carolina - carolino); the forms
        not made of the letters of WORD_PATTERN are left out, and both sides go
        to keys by lemma_key, so the keywords are lemmas, some with the label of
        another lemma (Roma - romo). The words of a text, or of every list of
        words, take the lemma of their part of speech by esMorph in context
        (vino de Rioja - vino, vino a casa - venir), a proper noun and the words
        of frequencies the key of a word alone, to which the rows of the proper
        nouns go. The reference frequency of a key is its ipm times CORPUS_SIZE;
        a word out of the dictionary gets its least frequency, an upper bound,
        so it may be a positive keyword but never a negative one
        Positive keywords are more frequent in the target corpus, negative ones
        in the reference; min_freq is the least frequency of a word in the
        corpus where it is more frequent

    References:
        https://ucrel.lancs.ac.uk/llwizard.html
        http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf
        http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/

    Arguments:
        target (str|list[str]|list[list[str]]|dict[str, int]): Text of the target
            corpus, its words - one text or a list of texts - or their frequencies;
            word forms against the frequency dictionary
        reference (list[str]|list[list[str]]|dict[str, float]|FreqDict|FrequencyReference):
            Words of the reference corpus - one text or a list of texts, not a
            string - their frequencies, the frequency dictionary or a reference by
            frequencies
        measure (str): Measure of KEYNESS_MEASURES for score and the sorting
        min_freq (int): Minimum frequency of a keyword in its own corpus
        positive (bool): Positive keywords (True) or negative ones (False)
        top_n (int): Number of keywords; None - all of them
        n (int): Length of the n-grams of the words of every text, joined by
            underscores as the n-grams of WordsExtractor; 1 - the words
        messages (dict[str, str]): Messages of the errors by key; None - MESSAGES of
            the core

    Returns:
        list[Keyword]: Keywords by descending keyness, then by descending
            frequency and alphabetically; words of an undefined measure last

    Raises:
        SourceTypeError: If a corpus is not of the types of its argument, or its words are
            mostly texts holding a space
        ParameterError: If the measure is unknown, top_n or n is below one, or n is above
            one with frequencies, a FrequencyReference or the frequency dictionary
        SourceError: If one of the corpora is empty or shorter than n words
        DatasetNotFoundError: If the frequency dictionary is not downloaded

    Example:
        >>> from ests.corpus import keyness
        >>> target = "el gato duerme y el gato come".split()
        >>> reference = "el perro duerme y el perro come".split()
        >>> [(k.word, round(k.g2, 2)) for k in keyness(target, reference)]
        [('gato', 2.77)]
    """
    context: dict[tuple[str, ...], tuple[str, ...]] | None = None
    if isinstance(target, str):
        words, tags = _text_words(target)
        context = {words: tags}
        target = list(words)
    if isinstance(reference, FreqDict):
        check_keyness_params(measure, min_freq, top_n, target, n, positive, messages=messages)
        if n > 1:
            raise ParameterError(
                "The frequency dictionary holds words: the n-grams need the words of both "
                f"corpora, not n={n}"
            )
        keys = None
        if not isinstance(target, Mapping):
            tags_of = context if context is not None else _target_tags(_target_texts(target))
            keys = _dictionary_keys(tags_of)
        reference = _frequency_reference(reference, keys)
    return anyts.corpus.keyness(
        target, reference, measure, min_freq, positive, top_n, n, messages=messages
    )


def _text_words(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Words of a text, the tokens of WordsExtractor, with the part of speech of the first word
    of every token by esMorph in the context of its sentence"""
    tokens = [token for token in _annotate_text(text).tokens if has_words(token.text)]
    return (
        tuple(token.text for token in tokens),
        tuple(token.words[0].upos or "" for token in tokens),
    )


def _target_texts(target: Sequence[str] | Sequence[Sequence[str]]) -> tuple[tuple[str, ...], ...]:
    """Texts of a target, one list of words or a list of texts"""
    if not target or isinstance(target[0], str):
        return (tuple(cast(Sequence[str], target)),)
    return tuple(tuple(text) for text in target)


@lru_cache(maxsize=1)
def _target_tags(texts: tuple[tuple[str, ...], ...]) -> dict[tuple[str, ...], tuple[str, ...]]:
    """Parts of speech of the words of every text of a target by esMorph in the context of the
    text; the last target is kept, so the positive and the negative keywords of one target
    analyze it once"""
    analyzer = get_morph_analyzer()
    return {
        text: tuple(found[0].pos if found else "" for found in analyzer.analyze_sentence(text))
        for text in texts
    }


def _dictionary_keys(
    tags_of: Mapping[tuple[str, ...], tuple[str, ...]],
) -> Callable[[Sequence[str]], list[str]]:
    """Keys of the words of a text of the target by their parts of speech in context; a proper
    noun takes the key of the word alone, to which word_ipm brings the rows of proper nouns"""

    def keys(words: Sequence[str]) -> list[str]:
        return [
            lemma_key(word, pos="" if tag == "PROPN" else tag)
            for word, tag in zip(words, tags_of[tuple(words)], strict=True)
        ]

    return keys


def _frequency_reference(
    freq_dict: FreqDict, keys: Callable[[Sequence[str]], list[str]] | None
) -> FrequencyReference:
    """The reference corpus of the frequency dictionary, as the docstring of keyness describes it"""
    size = float(CORPUS_SIZE)
    return FrequencyReference(
        {key: ipm * size / 1e6 for key, ipm in freq_dict.word_ipm.items()},
        size,
        freq_dict.min_ipm * size / 1e6,
        lemma_key,
        _is_dictionary_word,
        keys,
    )


def _is_dictionary_word(word: str) -> bool:
    """Whether a word is made of the letters of the forms the frequency dictionary counts"""
    return WORD_PATTERN.fullmatch(word.lower()) is not None
