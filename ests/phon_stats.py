from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from itertools import pairwise

import anyts.phon_stats
from anyts.constants import PHON_STATS_DESC as PHON_STATS_DESC, PHON_WINDOW_LEN
from anyts.phon_stats import (
    calc_repetition_index,
    check_params as check_params,
    consonant_clusters,
)
from anyts.utils import check_words, shannon_entropy

from .constants import SONORANT_SOUNDS, VOICED_SOUNDS, VOICELESS_SOUNDS, VOWEL_SOUNDS
from .exceptions import SourceTypeError
from .extractors import WordsExtractor
from .syllables import syllabify

CONSONANT_SOUNDS = SONORANT_SOUNDS | VOICED_SOUNDS | VOICELESS_SOUNDS
CACHE_SIZE = 1 << 16
# Vowel letters by their sound, the accents and the diaeresis dropped
VOWEL_LETTERS = {
    **dict.fromkeys("aáàâä", "a"),
    **dict.fromkeys("eéèêë", "e"),
    **dict.fromkeys("iíìîï", "i"),
    **dict.fromkeys("oóòôö", "o"),
    **dict.fromkeys("uúùûü", "u"),
}
FRONT_VOWELS = frozenset("eéèêëiíìîï")
# Consonant letters that stand for one sound whatever follows them
CONSONANT_LETTERS = {
    "b": "b",
    "v": "b",
    "d": "d",
    "f": "f",
    "j": "x",
    "k": "k",
    "m": "m",
    "n": "n",
    "ñ": "ɲ",
    "p": "p",
    "s": "s",
    "t": "t",
    "z": "θ",
}


class PhonStats(anyts.phon_stats.PhonStats):
    """
    Class for computing the phonostatistics of a text

    Description:
        Extends the PhonStats of the anyTS core with the sounds of Spanish: the
        statistics are counted over the sounds of the transcription
        (transcribe), not the letters, in the standard of Spain with yeísmo and
        distinción: vowels - a, e, i, o, u; sonorants - m, n, ɲ, l, r; voiced
        obstruents - b, d, g, ʝ; voiceless obstruents - p, t, k, f, θ, s, x,
        tʃ. The syllables are the ones of syllabify, a hiatus is two vowels in
        two syllables of a word (calc_hiatus). A text without sounds (numbers)
        has every share and ratio undefined (nan), a text without consonants
        the share of the heavy clusters

    Example:
        >>> from ests import PhonStats
        >>> text = "Tres tristes tigres tragaban trigo en un trigal"
        >>> ps = PhonStats(text)
        >>> ps.get_stats()
        {'p_vowels': 0.35,
        'p_sonorants': 0.25,
        'p_voiced': 0.125,
        'p_voiceless': 0.275,
        'consonant_vowel_ratio': 1.857...,
        'p_heavy_clusters': 0.0,
        'p_hiatus': 0.0,
        'cv_entropy': 2.75,
        'hardness': 0.458...,
        'alliteration': 0.933...,
        'assonance': 0.752...,
        'p_open_syllables': 0.428...,
        'mean_syllable_len': 2.857...}
        >>> ps.sounds[0], ps.syllables[-1]
        (('t', 'r', 'e', 's'), ('tri', 'gal'))

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        words_extractor (WordsExtractor): Word extraction tool; for a Doc it is applied
            to its text
        window_len (int): Window in words for the alliteration and the assonance

    Attributes:
        words (tuple[str]): Tuple of the extracted words in lower case
        window_len (int): Window in words for the alliteration and the assonance
        syllables (tuple[tuple[str, ...], ...]): Tuple of the syllables of every word
        sounds (tuple[tuple[str, ...], ...]): Tuple of the sounds of every word
        n_vowels (int): Number of vowels
        n_consonants (int): Number of consonants
        n_sonorants (int): Number of sonorant consonants
        n_voiced (int): Number of voiced obstruents
        n_voiceless (int): Number of voiceless obstruents
        c_clusters (dict[int, int]): Distribution of the consonant clusters by length
        c_syllable_patterns (dict[str, int]): Distribution of the syllables by CV pattern
        p_vowels (float): Share of vowels among the sounds
        p_sonorants (float): Share of sonorant consonants among the sounds
        p_voiced (float): Share of voiced obstruents among the sounds
        p_voiceless (float): Share of voiceless obstruents among the sounds
        consonant_vowel_ratio (float): Ratio of consonants to vowels
        p_heavy_clusters (float): Share of the clusters of 3 consonants or more
        p_hiatus (float): Hiatuses per word
        cv_entropy (float): Entropy of the CV patterns of the words in bits
        hardness (float): Hardness - ratio of the voiceless obstruents to the
            vowels and the sonorants
        alliteration (float): Alliteration index
        assonance (float): Assonance index
        p_open_syllables (float): Share of open syllables
        mean_syllable_len (float): Mean length of a syllable in sounds

    Methods:
        describe: Reading of a statistic by its scale, None for every statistic
        get_stats: Getting the computed phonostatistics of the text
        to_dataframe: Getting the statistics as a table of one row
        print_stats: Printing the computed phonostatistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc, or the extractor is
            not a WordsExtractor
        SourceError: If the source has no words or a string has a character without a
            UTF-8 form
        ParameterError: If the window is not an integer or is below 2
    """

    words_extractor_class = WordsExtractor
    vowels = VOWEL_SOUNDS
    sonorants = SONORANT_SOUNDS
    voiced = VOICED_SOUNDS
    voiceless = VOICELESS_SOUNDS

    def transcribe(self, word: str) -> tuple[str, ...]:
        """Sounds of a word by the Spanish orthography (transcribe)"""
        return transcribe(word)

    def syllabify(self, word: str) -> list[str]:
        """Syllables of a word (ests.syllables.syllabify)"""
        return syllabify(word)

    def syllable_sounds(self, word: str) -> tuple[tuple[str, ...], ...]:
        """Sounds of every syllable, the first one read as the start of the word"""
        return _syllable_sounds(word)

    def word_hiatus(self, word: str) -> int:
        """Hiatuses of a word by its syllables (calc_hiatus)"""
        return _word_hiatus(word)


def transcribe(word: str) -> tuple[str, ...]:
    """
    Transcribing a word into its sounds

    Description:
        The word is split into syllables (syllabify) and every syllable is read
        by the rules of the Spanish orthography:
            the vowels lose their accents and their diaeresis (á - a, ü - u);
            h has no sound (hora - o r a), but hi before a vowel at the start of
            a syllable is ʝ (hielo, deshielo), and ch is one sound, tʃ;
            c and g before e and i are θ and x, elsewhere k and g (cena, gente);
            qu and gu before e and i are k and g, the u silent (queso, guerra);
            ll and y are ʝ (yeísmo), but y at the end of a syllable is the vowel
            i (hoy, rey, the conjunction y);
            rr and r are one r; ñ is ɲ, j is x, v is b, z is θ;
            x is k s, and s at the start of a word (examen, xilófono);
            w is the vowel u (whisky)
        The characters that are no Spanish letters (digits, hyphens) are left out

    Arguments:
        word (str): Word

    Returns:
        tuple[str]: Sounds of the word

    Raises:
        SourceTypeError: If the word is not a string

    Example:
        >>> from ests.phon_stats import transcribe
        >>> transcribe("hechizo"), transcribe("guerrilla"), transcribe("examen")
        (('e', 'tʃ', 'i', 'θ', 'o'), ('g', 'e', 'r', 'i', 'ʝ', 'a'), ('e', 'k', 's', 'a', 'm', 'e', 'n'))
    """
    if not isinstance(word, str):
        raise SourceTypeError(f"The word must be a string, not {type(word).__name__}")
    return tuple(sound for syllable in _syllable_sounds(word) for sound in syllable)


@lru_cache(maxsize=CACHE_SIZE)
def _syllable_sounds(word: str) -> tuple[tuple[str, ...], ...]:
    """Sounds of every syllable of a word - see transcribe"""
    syllables = syllabify(word)
    return tuple(
        sounds
        for index, syllable in enumerate(syllables)
        if (sounds := _transcribe_syllable(syllable.lower(), index == 0))
    )


def _transcribe_syllable(syllable: str, initial: bool) -> tuple[str, ...]:
    """Sounds of one syllable; initial tells the first syllable of a word"""
    sounds: list[str] = []
    index = 0
    while index < len(syllable):
        letter = syllable[index]
        read: tuple[str, ...]
        if letter in VOWEL_LETTERS:
            read, step = (VOWEL_LETTERS[letter],), 1
        elif letter in CONSONANT_LETTERS:
            read, step = (CONSONANT_LETTERS[letter],), 1
        else:
            read, step = _read_letter(syllable, index, initial)
        sounds.extend(read)
        index += step
    return tuple(sounds)


def _read_letter(syllable: str, index: int, initial: bool) -> tuple[tuple[str, ...], int]:
    """Sounds of a letter whose reading depends on its neighbours, with the letters it takes"""
    letter = syllable[index]
    following = syllable[index + 1 : index + 2]
    after = syllable[index + 2 : index + 3]
    if letter == "h":
        if index == 0 and following == "i" and after in VOWEL_LETTERS:
            return ("ʝ",), 2
        return (), 1
    if letter == "c":
        if following == "h":
            return ("tʃ",), 2
        return ("θ" if following in FRONT_VOWELS else "k",), 1
    if letter == "g":
        if following in FRONT_VOWELS:
            return ("x",), 1
        return ("g",), 2 if following == "u" and after in FRONT_VOWELS else 1
    if letter == "q":
        return ("k",), 2 if following == "u" else 1
    if letter in ("l", "r"):
        doubled = following == letter
        return ("ʝ" if letter == "l" and doubled else letter,), 2 if doubled else 1
    if letter == "y":
        return ("i" if index == len(syllable) - 1 else "ʝ",), 1
    if letter == "x":
        return ("s",) if initial and index == 0 else ("k", "s"), 1
    if letter == "w":
        return ("u",), 1
    return (), 1


def cv_pattern(word: str) -> str:
    """
    Getting the CV pattern of a word or a syllable

    Description:
        The vowels are written V and the consonants C, over the sounds of the
        transcription (transcribe): hora is VCV, examen VCCVCVC. A syllable is
        read as a word of its own, so its initial x is s: xi is CV, while the
        syllable xi of México counts as CCV in PhonStats

    Arguments:
        word (str): Word or syllable

    Returns:
        str: CV pattern

    Raises:
        SourceTypeError: If the word is not a string

    Example:
        >>> from ests.phon_stats import cv_pattern
        >>> cv_pattern("queso"), cv_pattern("instrumento")
        ('CVCV', 'VCCCCVCVCCV')
    """
    return anyts.phon_stats.cv_pattern(transcribe(word), VOWEL_SOUNDS, CONSONANT_SOUNDS)


def is_open_syllable(syllable: str) -> bool:
    """
    Checking whether a syllable is open

    Description:
        An open syllable ends in a vowel sound: ca, que, hoy (the final y is
        the vowel i); car and pan are closed. The syllable is read as a word
        of its own (transcribe)

    Arguments:
        syllable (str): Syllable

    Returns:
        bool: Result of the check

    Raises:
        SourceTypeError: If the syllable is not a string
    """
    sounds = transcribe(syllable)
    return bool(sounds) and sounds[-1] in VOWEL_SOUNDS


def calc_consonant_clusters(text: Sequence[str]) -> dict[int, int]:
    """
    Computing the distribution of the consonant clusters by length

    Description:
        A cluster is a run of consonant sounds inside a word, across the
        syllables, a single consonant included: instrumento has n s t r, m and
        n t. The digraphs are one sound (calle, chico), x is two (extra - k s t r)

    Arguments:
        text (list[str]): List of words

    Returns:
        dict[int, int]: Number of the clusters of every length

    Raises:
        SourceTypeError: If the words are not a list of strings

    Example:
        >>> from ests.phon_stats import calc_consonant_clusters
        >>> calc_consonant_clusters(["instrumento", "calle"])
        {1: 3, 2: 1, 4: 1}
    """
    check_words(text)
    counter: Counter[int] = Counter()
    for word, count in Counter(text).items():
        for size in _clusters(word):
            counter[size] += count
    return dict(sorted(counter.items()))


@lru_cache(maxsize=CACHE_SIZE)
def _clusters(word: str) -> tuple[int, ...]:
    """Lengths of the consonant clusters of a word in order"""
    return consonant_clusters(transcribe(word), CONSONANT_SOUNDS)


def calc_hiatus(text: Sequence[str]) -> int:
    """
    Computing the number of hiatuses

    Description:
        A hiatus is two vowels next to each other in two syllables of a word,
        as syllabify splits them: po-e-ta, dí-a, a-é-re-o (two). A silent h
        between the vowels keeps the hiatus (bú-ho), a diphthong is none (cie-lo)

    Arguments:
        text (list[str]): List of words

    Returns:
        int: Number of hiatuses

    Raises:
        SourceTypeError: If the words are not a list of strings

    Example:
        >>> from ests.phon_stats import calc_hiatus
        >>> calc_hiatus(["poeta", "búho", "cielo", "aéreo"])
        4
    """
    check_words(text)
    return sum(_word_hiatus(word) * count for word, count in Counter(text).items())


@lru_cache(maxsize=CACHE_SIZE)
def _word_hiatus(word: str) -> int:
    """Number of hiatuses of a word"""
    return sum(
        1
        for previous, following in pairwise(_syllable_sounds(word))
        if previous[-1] in VOWEL_SOUNDS and following[0] in VOWEL_SOUNDS
    )


def calc_cv_entropy(text: Sequence[str]) -> float:
    """
    Computing the entropy of the CV patterns of the words

    Description:
        The Shannon entropy of the distribution of the words by CV pattern in
        bits: the higher it is, the more varied the phonetic shape of the words
        of the text. Words without sounds (numbers) are left out

    Arguments:
        text (list[str]): List of words

    Returns:
        float: Value of the entropy, nan if the text has no word with sounds

    Raises:
        SourceTypeError: If the words are not a list of strings
    """
    check_words(text)
    patterns: Counter[str] = Counter()
    for word, count in Counter(text).items():
        if pattern := cv_pattern(word):
            patterns[pattern] += count
    return shannon_entropy(patterns)


def calc_alliteration(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Computing the alliteration index

    Description:
        The number of windows of window_len neighbouring words where a
        consonant sound occurs in two words or more, summed over the
        consonants, to the number expected if the words stood in random order
        (calc_repetition_index of anyts.phon_stats): about 1 - random
        repetitions, well above 1 - alliteration. The sounds count, not the
        letters: casa and queso repeat k, cena and casa do not

    Arguments:
        text (list[str]): List of words
        window_len (int): Window in words

    Returns:
        float: Value of the index, nan for a text shorter than the window or
            without a consonant shared by two words

    Raises:
        SourceTypeError: If the words are not a list of strings
        ParameterError: If the window is not an integer or is below 2
    """
    check_words(text)
    check_params(window_len)
    return calc_repetition_index(list(map(transcribe, text)), window_len, CONSONANT_SOUNDS)


def calc_assonance(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Computing the assonance index

    Description:
        The index of calc_alliteration over the vowels, stressed or not: about
        1 - random repetitions, well above 1 - assonance

    Arguments:
        text (list[str]): List of words
        window_len (int): Window in words

    Returns:
        float: Value of the index, nan for a text shorter than the window or
            without a vowel shared by two words

    Raises:
        SourceTypeError: If the words are not a list of strings
        ParameterError: If the window is not an integer or is below 2
    """
    check_words(text)
    check_params(window_len)
    return calc_repetition_index(list(map(transcribe, text)), window_len, VOWEL_SOUNDS)
