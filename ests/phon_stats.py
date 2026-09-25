from collections import Counter
from collections.abc import Sequence
from functools import lru_cache
from itertools import pairwise
from math import log2, nan

import numpy as np
from spacy.tokens import Doc

from .constants import (
    PHON_STATS_DESC,
    PHON_WINDOW_LEN,
    SONORANT_SOUNDS,
    VOICED_SOUNDS,
    VOICELESS_SOUNDS,
    VOWEL_SOUNDS,
)
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import WordsExtractor
from .syllables import syllabify
from .utils import iter_doc_words, safe_divide

CONSONANT_SOUNDS = SONORANT_SOUNDS | VOICED_SOUNDS | VOICELESS_SOUNDS
SOUNDS = VOWEL_SOUNDS | CONSONANT_SOUNDS
SOUNDS_ORDER = sorted(SOUNDS)
CONSONANT_COLUMNS = [i for i, sound in enumerate(SOUNDS_ORDER) if sound in CONSONANT_SOUNDS]
VOWEL_COLUMNS = [i for i, sound in enumerate(SOUNDS_ORDER) if sound in VOWEL_SOUNDS]
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


def check_params(window_len: int) -> None:
    """
    Checking the parameters of the phonostatistics

    Arguments:
        window_len (int): Window in words for the alliteration and the assonance

    Raises:
        ParameterError: If the window is below 2
    """
    if window_len < 2:
        raise ParameterError("The window must be at least 2")


class PhonStats:
    """
    Class for computing the phonostatistics of a text

    Description:
        The statistics are counted over the sounds of the transcription of the
        words (transcribe), since Spanish writes some sounds with two letters
        (ch, ll, rr, qu), some letters with no sound (h, the u of que and gui)
        and one letter for two sounds (x): vowels - a, e, i, o, u; sonorants -
        m, n, ɲ, l, r; voiced obstruents - b, d, g, ʝ; voiceless obstruents - p,
        t, k, f, θ, s, x, tʃ. The pronunciation is the one of the standard of
        Spain, with yeísmo and distinción. The syllables are the ones of
        syllabify, by the orthographic rules

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
        'alliteration': 0.917...,
        'assonance': 0.670...,
        'p_open_syllables': 0.428...,
        'mean_syllable_len': 2.857...}
        >>> ps.sounds[0], ps.syllables[-1]
        (('t', 'r', 'e', 's'), ('tri', 'gal'))

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        words_extractor (WordsExtractor): Word extraction tool
        window_len (int): Window in words for the alliteration and the assonance

    Attributes:
        words (tuple[str]): Tuple of the extracted words in lower case
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
        get_stats: Getting the computed phonostatistics of the text
        print_stats: Printing the computed phonostatistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words
        ParameterError: If the window is below 2
    """

    def __init__(
        self,
        source: str | Doc,
        words_extractor: WordsExtractor | None = None,
        window_len: int = PHON_WINDOW_LEN,
    ):
        if isinstance(source, Doc):
            words = tuple(word.lower() for _, _, word in iter_doc_words(source))
        elif isinstance(source, str):
            if not words_extractor:
                words_extractor = WordsExtractor(lowercase=True)
            words = tuple(word.lower() for word in words_extractor.extract(source))
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not words:
            raise SourceError("The data source has no words")
        check_params(window_len)
        self.words = words
        self.window_len = window_len
        self.syllables = tuple(tuple(syllabify(word)) for word in words)
        self.sounds = tuple(transcribe(word) for word in words)

        counts = Counter(words)
        sounds: Counter[str] = Counter()
        syllables: Counter[tuple[str, ...]] = Counter()
        for word, count in counts.items():
            for sound, number in Counter(transcribe(word)).items():
                sounds[sound] += number * count
            for syllable in _syllable_sounds(word):
                syllables[syllable] += count
        self.n_vowels = sum(sounds[sound] for sound in VOWEL_SOUNDS)
        self.n_sonorants = sum(sounds[sound] for sound in SONORANT_SOUNDS)
        self.n_voiced = sum(sounds[sound] for sound in VOICED_SOUNDS)
        self.n_voiceless = sum(sounds[sound] for sound in VOICELESS_SOUNDS)
        self.n_consonants = self.n_sonorants + self.n_voiced + self.n_voiceless
        n_sounds = self.n_vowels + self.n_consonants
        self.c_clusters = _consonant_clusters(counts)
        patterns: Counter[str] = Counter()
        for syllable, count in syllables.items():
            patterns[cv_pattern(syllable)] += count
        self.c_syllable_patterns = dict(sorted(patterns.items()))

        self.p_vowels = safe_divide(self.n_vowels, n_sounds)
        self.p_sonorants = safe_divide(self.n_sonorants, n_sounds)
        self.p_voiced = safe_divide(self.n_voiced, n_sounds)
        self.p_voiceless = safe_divide(self.n_voiceless, n_sounds)
        self.consonant_vowel_ratio = safe_divide(self.n_consonants, self.n_vowels, nan)
        n_clusters = sum(self.c_clusters.values())
        self.p_heavy_clusters = safe_divide(
            sum(count for size, count in self.c_clusters.items() if size >= 3), n_clusters
        )
        self.p_hiatus = _hiatus(counts) / len(words)
        self.cv_entropy = _cv_entropy(counts)
        self.hardness = safe_divide(self.n_voiceless, self.n_vowels + self.n_sonorants, nan)
        windows = _sound_windows(self.sounds, SOUNDS_ORDER, window_len)
        self.alliteration = _repetition_index(windows, CONSONANT_COLUMNS, len(words), window_len)
        self.assonance = _repetition_index(windows, VOWEL_COLUMNS, len(words), window_len)
        n_syllables = sum(syllables.values())
        self.p_open_syllables = safe_divide(
            sum(count for syllable, count in syllables.items() if is_open_syllable(syllable)),
            n_syllables,
            nan,
        )
        self.mean_syllable_len = safe_divide(
            sum(len(syllable) * count for syllable, count in syllables.items()),
            n_syllables,
            nan,
        )

    def get_stats(self) -> dict[str, float]:
        """
        Getting the computed phonostatistics of the text

        Returns:
            dict[str, float]: Dictionary of the computed phonostatistics
        """
        return {stat: getattr(self, stat) for stat in PHON_STATS_DESC}

    def print_stats(self) -> None:
        """Printing the computed phonostatistics of the text with descriptions"""
        print(f"{'Statistic':^46}|{'Value':^10}")
        print("-" * 56)
        stats = self.get_stats()
        for stat, desc in PHON_STATS_DESC.items():
            print(f"{desc:46}|{stats[stat]:^10.2f}")


def transcribe(word: str) -> tuple[str, ...]:
    """
    Transcribing a word into its sounds

    Description:
        The word is split into syllables (syllabify) and every syllable is read
        by the rules of the Spanish orthography, which are regular enough to go
        without a dictionary:
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
        The characters that are no Spanish letters (digits, hyphens) are left
        out. The results are cached by word form

    Arguments:
        word (str): Word

    Returns:
        tuple[str]: Sounds of the word

    Example:
        >>> from ests.phon_stats import transcribe
        >>> transcribe("hechizo"), transcribe("guerrilla"), transcribe("examen")
        (('e', 'tʃ', 'i', 'θ', 'o'), ('g', 'e', 'r', 'i', 'ʝ', 'a'), ('e', 'k', 's', 'a', 'm', 'e', 'n'))
    """
    return tuple(sound for syllable in _syllable_sounds(word) for sound in syllable)


@lru_cache(maxsize=CACHE_SIZE)
def _syllable_sounds(word: str) -> tuple[tuple[str, ...], ...]:
    """Sounds of every syllable of a word, with a cache by word - see transcribe"""
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


def cv_pattern(sounds: Sequence[str]) -> str:
    """
    Getting the CV pattern of a word or a syllable

    Description:
        The vowels are written V and the consonants C, over the sounds of the
        transcription (transcribe): queso is CVCV, hora is VCV, examen VCCVCVC

    Arguments:
        sounds (tuple[str]): Sounds of a word or a syllable

    Returns:
        str: CV pattern

    Example:
        >>> from ests.phon_stats import cv_pattern, transcribe
        >>> cv_pattern(transcribe("queso")), cv_pattern(transcribe("instrumento"))
        ('CVCV', 'VCCCCVCVCCV')
    """
    return "".join("V" if sound in VOWEL_SOUNDS else "C" for sound in sounds)


def is_open_syllable(syllable: Sequence[str]) -> bool:
    """
    Checking whether a syllable is open

    Description:
        An open syllable ends in a vowel sound: ca, que, hoy (the final y is
        the vowel i); car and pan are closed

    Arguments:
        syllable (tuple[str]): Sounds of the syllable

    Returns:
        bool: Result of the check
    """
    return bool(syllable) and syllable[-1] in VOWEL_SOUNDS


def calc_consonant_clusters(text: Sequence[str]) -> dict[int, int]:
    """
    Computing the distribution of the consonant clusters by length

    Description:
        A cluster is a run of consonant sounds inside a word, across the
        syllables: instrumento has the clusters n s t r (4), m (1) and n t (2).
        The clusters of length 1 are the single consonants between vowels or at
        the edges of a word. The digraphs are one sound (calle, perro, chico),
        and x is two (extra - k s t r)

    Arguments:
        text (list[str]): List of words

    Returns:
        dict[int, int]: Number of the clusters of every length

    Example:
        >>> from ests.phon_stats import calc_consonant_clusters
        >>> calc_consonant_clusters(["instrumento", "calle"])
        {1: 3, 2: 1, 4: 1}
    """
    return _consonant_clusters(Counter(text))


def _consonant_clusters(counts: Counter[str]) -> dict[int, int]:
    """Distribution of the clusters by length by a counter of word forms"""
    counter: Counter[int] = Counter()
    for word, count in counts.items():
        for size in _clusters(word):
            counter[size] += count
    return dict(sorted(counter.items()))


@lru_cache(maxsize=CACHE_SIZE)
def _clusters(word: str) -> tuple[int, ...]:
    """Lengths of the consonant clusters of a word in order, with a cache by word"""
    sizes = []
    size = 0
    for sound in transcribe(word):
        if sound in CONSONANT_SOUNDS:
            size += 1
        else:
            if size:
                sizes.append(size)
            size = 0
    if size:
        sizes.append(size)
    return tuple(sizes)


def calc_hiatus(text: Sequence[str]) -> int:
    """
    Computing the number of hiatuses

    Description:
        A hiatus is two vowels next to each other in two syllables of a word,
        as syllabify splits them: po-e-ta, dí-a, le-er, a-é-re-o (two). A
        silent h between the vowels does not break the hiatus (bú-ho, a-ho-ra),
        and the vowels of a diphthong are one syllable and no hiatus (cie-lo,
        ciu-dad)

    Arguments:
        text (list[str]): List of words

    Returns:
        int: Number of hiatuses

    Example:
        >>> from ests.phon_stats import calc_hiatus
        >>> calc_hiatus(["poeta", "búho", "cielo", "aéreo"])
        4
    """
    return _hiatus(Counter(text))


def _hiatus(counts: Counter[str]) -> int:
    """Number of hiatuses by a counter of word forms"""
    return sum(_word_hiatus(word) * count for word, count in counts.items())


@lru_cache(maxsize=CACHE_SIZE)
def _word_hiatus(word: str) -> int:
    """Number of hiatuses of a word, with a cache by word"""
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
    """
    return _cv_entropy(Counter(text))


def _cv_entropy(counts: Counter[str]) -> float:
    """Entropy of the CV patterns by a counter of word forms"""
    patterns: Counter[str] = Counter()
    for word, count in counts.items():
        if pattern := cv_pattern(transcribe(word)):
            patterns[pattern] += count
    total = sum(patterns.values())
    if not total:
        return nan
    return -sum(count / total * log2(count / total) for count in patterns.values())


def _calc_repetition_index(text: Sequence[str], sounds: frozenset[str], window_len: int) -> float:
    """
    Ratio of the observed number of windows with a sound repeated in different
    words to the number expected if the sounds were spread over the words at random
    """
    alphabet = sorted(sounds)
    windows = _sound_windows([transcribe(word) for word in text], alphabet, window_len)
    return _repetition_index(windows, list(range(len(alphabet))), len(text), window_len)


def _sound_windows(
    words: Sequence[tuple[str, ...]], alphabet: Sequence[str], window_len: int
) -> tuple[np.ndarray, np.ndarray] | None:
    """
    Numbers of the words with every sound in every window and in the whole text

    Description:
        A matrix of word forms by sounds is indexed by the words of the text,
        and the cumulative sums over the words give the counts of the windows as
        a difference with a shift of a window; None for a text shorter than the
        window
    """
    n_words = len(words)
    if n_words < window_len:
        return None
    unique = list(dict.fromkeys(words))
    presence = np.array(
        [[sound in word for sound in alphabet] for word in unique], dtype=np.int32
    ).reshape(len(unique), len(alphabet))
    indices = dict(zip(unique, range(len(unique)), strict=True))
    rows = np.fromiter(map(indices.__getitem__, words), dtype=np.int64, count=n_words)
    cumulative = np.zeros((n_words + 1, len(alphabet)), dtype=np.int32)
    np.cumsum(presence[rows], axis=0, out=cumulative[1:])
    return cumulative[window_len:] - cumulative[:-window_len], cumulative[-1]


def _repetition_index(
    windows: tuple[np.ndarray, np.ndarray] | None,
    columns: Sequence[int],
    n_words: int,
    window_len: int,
) -> float:
    """Index of the repetitions by the counts of the windows for the columns of some sounds"""
    if windows is None:
        return nan
    in_window, totals = windows
    n_windows = n_words - window_len + 1
    observed = int((in_window[:, columns] >= 2).sum())
    expected = 0.0
    for count in totals[columns]:
        if not count:
            continue
        p = int(count) / n_words
        p_single = window_len * p * (1 - p) ** (window_len - 1)
        expected += n_windows * (1 - (1 - p) ** window_len - p_single)
    return safe_divide(observed, expected, nan)


def calc_alliteration(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Computing the alliteration index

    Description:
        The ratio of the observed number of windows of window_len neighbouring
        words where one consonant sound occurs in two words or more to the
        number expected if the consonants were spread over the words at
        random, summed over the consonants. The expected number comes from the
        frequencies of the consonants in the text itself, so the index tells
        whether the repetitions cluster in neighbouring words, not how frequent
        a sound is: about 1 - the repetitions are random, well above 1 -
        alliteration. The consonants are the sounds of the transcription, so
        casa and queso repeat k, and cena and casa do not

    Arguments:
        text (list[str]): List of words
        window_len (int): Window in words

    Returns:
        float: Value of the index, nan for a text shorter than the window
    """
    return _calc_repetition_index(text, CONSONANT_SOUNDS, window_len)


def calc_assonance(text: Sequence[str], window_len: int = PHON_WINDOW_LEN) -> float:
    """
    Computing the assonance index

    Description:
        The ratio of the observed number of windows of window_len neighbouring
        words where one vowel occurs in two words or more to the number
        expected if the vowels were spread over the words at random, summed
        over the vowels. The expected number comes from the frequencies of the
        vowels in the text itself, so the index tells whether the repetitions
        cluster in neighbouring words, not how frequent a sound is. Every vowel
        counts, stressed or not

    Arguments:
        text (list[str]): List of words
        window_len (int): Window in words

    Returns:
        float: Value of the index, nan for a text shorter than the window
    """
    return _calc_repetition_index(text, VOWEL_SOUNDS, window_len)
