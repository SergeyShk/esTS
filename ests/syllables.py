import re
import unicodedata
from functools import lru_cache
from itertools import pairwise

from .constants import (
    ACCENTED_VOWELS,
    DIGRAPHS,
    HIATUS_VOWELS,
    NASAL_VOWELS,
    NON_ADVERBS_MENTE,
    ONSET_CLUSTERS,
    VOWELS,
    WEAK_VOWELS,
)

CACHE_SIZE = 1 << 16
WORD_PARTS = re.compile(r"[^\W\d_]+")
STRESS_TYPES = ("aguda", "llana", "esdrújula", "sobresdrújula")


def syllabify(word: str) -> list[str]:
    """
    Division of a word into syllables by the orthographic rules of Spanish

    Description:
        A syllable is built around a vowel nucleus: a single vowel,
        a diphthong or a triphthong. A weak vowel (unaccented i, u, ü)
        next to another vowel joins it into a diphthong (ai-re, puen-te,
        rui-do, ciu-dad), a strong vowel next to a strong one forms
        a hiatus (po-e-ta, le-er, a-é-re-o), and an accented weak vowel
        is strong (dí-a, pa-ís, ba-úl), while two close vowels of the same
        letter are a hiatus with or without a tilde (chi-i-ta, chi-í-es);
        a weak vowel between two others
        gives a triphthong (a-ve-ri-guáis, buey). An h between vowels does
        not break a diphthong (ahu-ma-do, prohi-bir). The u of qu and of
        gu before e and i is silent (que-so, gue-rra) and ü is a vowel
        (pin-güi-no); y is a vowel at the end of a word (rey, U-ru-guay)
        and a consonant before a vowel (ma-yo).
        Consonants between two nuclei are distributed by these rules:
            a single consonant or digraph goes to the next syllable: ca-sa, mu-cho, pe-rro
            an obstruent with l or r goes to the next syllable: ha-blar, o-tro
            other pairs are split: ac-to, is-la, at-las, rit-mo
            of three or more consonants the last two go to the next syllable
                when they form such a cluster: com-pra, cons-truir; otherwise
                only the last one goes: ins-ti-tu-to, obs-tá-cu-lo, tungs-te-no
        The rules follow the Ortografía de la lengua española (RAE, 2010),
        where two weak vowels always form a diphthong (huir, cons-truir,
        je-sui-ta, guion) and tl is split as in Spain (at-las).
        The word is normalized to NFC (a decomposed accent is one letter
        with its base) and lower-cased; it is split into parts at digits,
        hyphens and other non-letters, each part is syllabified on its
        own (te-ó-ri-co-prác-ti-co), and a part without vowels
        (an abbreviation like sh) yields no syllables. Vowels with foreign
        diacritics count as accented strong vowels (Björk); a diaeresis
        other than ü marks a hiatus (Llu-ï-sa, Ci-tro-ën) and the
        Portuguese ão and õe are diphthongs (São, Ca-mões)

    References:
        Real Academia Española. Ortografía de la lengua española. 2010, §§ 2.2, 4.1

    Arguments:
        word (str): Word

    Returns:
        list[str]: List of syllables
    """
    return list(_syllables(word))


def count_syllables(word: str) -> int:
    """
    Counting the syllables of a word

    Description:
        The number of syllables by syllabify, cached by word form

    Arguments:
        word (str): Word

    Returns:
        int: Number of syllables
    """
    return len(_syllables(word))


def word_stress(word: str) -> int | None:
    """
    Getting the stressed syllable of a word

    Description:
        Syllables are counted from zero as in syllabify. A written accent
        marks the stressed syllable (ca-mión, ár-bol, mur-cié-la-go);
        otherwise a word ending in a vowel, in n or s after a vowel or
        in y after a consonant is stressed on the penultimate syllable
        (ca-sa, jo-ven, lu-nes, whis-ky), and any other word on the last
        one (pa-pel, re-loj, ro-bots, U-ru-guay). A monosyllable is
        stressed on its only syllable.
        Enclitic pronouns need no special treatment: their forms carry
        the accent by the same rules (dí-ga-me-lo, de-cír-se-lo).
        For an adverb in -mente and for a hyphenated compound the main
        stress is the last of word_stresses (fá-cil-men-te - 2)

    Arguments:
        word (str): Word

    Returns:
        int|None: Index of the stressed syllable, None for a word without vowels
    """
    stresses = _stresses(word)
    return stresses[-1] if stresses else None


def word_stresses(word: str) -> list[int]:
    """
    Getting all stressed syllables of a word

    Description:
        A single index for most words - see word_stress. Two indices for
        an adverb in -mente, which keeps the stress of its adjective
        (fá-cil-men-te - 0 and 2, fe-liz-men-te - 1 and 2), and one index
        per part of a hyphenated compound (te-ó-ri-co-prác-ti-co - 1 and 4).
        An adverb is recognized by its shape: a stem of at least one
        syllable before -mente that ends like an adjective (in a vowel, l,
        r, z, n or s) or carries an accent, so cruel-men-te counts too.
        Words of the same shape that are not adverbs are listed in
        NON_ADVERBS_MENTE: adjectives and nouns (demente, vehemente) and
        subjunctives of verbs in -mentar (fundamente, complemente); an
        unlisted subjunctive of that kind gets a second stress

    Arguments:
        word (str): Word

    Returns:
        list[int]: Indices of the stressed syllables in ascending order
    """
    return list(_stresses(word))


def stress_type(word: str) -> str | None:
    """
    Classifying a word by the position of its stress

    Description:
        "aguda" for the stress on the last syllable (ca-mión), "llana" on
        the penultimate (ca-sa), "esdrújula" on the antepenultimate
        (mur-cié-la-go), "sobresdrújula" earlier (dí-ga-me-lo); the main
        stress is that of word_stress

    Arguments:
        word (str): Word

    Returns:
        str|None: Type of the word, None for a word without vowels
    """
    syllables = _syllables(word)
    stress = word_stress(word)
    if stress is None:
        return None
    return STRESS_TYPES[min(len(syllables) - stress - 1, 3)]


def _syllables(word: str) -> tuple[str, ...]:
    """Syllables of a word as a tuple - see syllabify"""
    return _analyze(word)[0]


def _stresses(word: str) -> tuple[int, ...]:
    """Stressed syllables of a word - see word_stresses"""
    return _analyze(word)[1]


@lru_cache(maxsize=CACHE_SIZE)
def _analyze(word: str) -> tuple[tuple[str, ...], tuple[int, ...]]:
    """Syllables and stressed syllables of a word, cached by word form"""
    syllables: list[str] = []
    stresses: list[int] = []
    for part in WORD_PARTS.findall(unicodedata.normalize("NFC", word).lower()):
        part_syllables = _syllabify_part(part)
        if not part_syllables:
            continue
        offset = len(syllables)
        if _is_adverb(part, part_syllables):
            stresses.append(offset + _part_stress(part_syllables[:-2]))
            stresses.append(offset + len(part_syllables) - 2)
        else:
            stresses.append(offset + _part_stress(part_syllables))
        syllables.extend(part_syllables)
    return tuple(syllables), tuple(stresses)


def _syllabify_part(part: str) -> list[str]:
    """Syllables of a run of letters"""
    nuclei = _nuclei(part)
    if not nuclei:
        return []
    boundaries = [0]
    for (_, end), (start, _) in pairwise(nuclei):
        boundaries.append(_boundary(part, end, start))
    boundaries.append(len(part))
    return [part[a:b] for a, b in pairwise(boundaries)]


def _nuclei(part: str) -> list[tuple[int, int]]:
    """Positions of vowel nuclei: [start, end) of each vowel, diphthong or triphthong"""
    vowels = [i for i, letter in enumerate(part) if _is_vowel(part, i)]
    nuclei: list[tuple[int, int]] = []
    index = 0
    while index < len(vowels):
        start = vowels[index]
        end = start + 1
        if index + 1 < len(vowels) and _joins(part, vowels, index):
            index += 1
            end = vowels[index] + 1
            if (
                _is_weak(part, start)
                and not _is_weak(part, vowels[index])
                and index + 1 < len(vowels)
                and _joins(part, vowels, index)
            ):
                index += 1
                end = vowels[index] + 1
        nuclei.append((start, end))
        index += 1
    return nuclei


def _is_vowel(part: str, index: int) -> bool:
    """Whether the letter at the index is pronounced as a vowel"""
    letter = part[index]
    if letter == "y":
        return index + 1 >= len(part) or part[index + 1] not in VOWELS
    if letter == "u" and index > 0:
        if part[index - 1] == "q":
            return False
        if part[index - 1] == "g" and index + 1 < len(part) and part[index + 1] in "eéií":
            return False
    return letter in VOWELS


def _base(letter: str) -> str:
    """The letter without its diacritic: í - i, ü - u"""
    return unicodedata.normalize("NFD", letter)[0]


def _is_close(letter: str) -> bool:
    """Whether the letter is a close vowel, with or without a diacritic"""
    return _base(letter) in WEAK_VOWELS


def _is_weak(part: str, index: int) -> bool:
    """Whether the vowel at the index is weak: an unaccented i, u, ü or a vocalic y"""
    return part[index] in WEAK_VOWELS or part[index] == "y"


def _adjacent(part: str, first: int, second: int) -> bool:
    """Whether two vowels touch, directly or across an h"""
    return second - first == 1 or (second - first == 2 and part[first + 1] == "h")


def _joins(part: str, vowels: list[int], index: int) -> bool:
    """
    Whether the vowel at the index forms a diphthong with the next one

    Description:
        Two close vowels join unless they are the same letter, with or
        without a tilde (chi-i-ta, chi-í-es), a weak and a strong vowel
        join, two strong vowels do not. A weak
        vowel followed by a strong one is left to that vowel
        (chi-hua-hua, ca-ca-hue-te). The same check adds the third vowel
        of a triphthong (buey, a-ve-ri-guáis). A vowel with a diaeresis
        other than ü never joins (Llu-ï-sa), a Portuguese nasal vowel
        joins a following o or e (São, Ca-mões)
    """
    first, second = vowels[index], vowels[index + 1]
    if not _adjacent(part, first, second):
        return False
    if part[first] in HIATUS_VOWELS or part[second] in HIATUS_VOWELS:
        return False
    if part[first] in NASAL_VOWELS:
        return part[second] in "oe"
    first_weak, second_weak = _is_weak(part, first), _is_weak(part, second)
    if not first_weak and not second_weak:
        return False
    if (
        _is_close(part[first])
        and _is_close(part[second])
        and _base(part[first]) == _base(part[second])
    ):
        return False
    if second_weak and index + 2 < len(vowels):
        third = vowels[index + 2]
        if not _is_weak(part, third) and _adjacent(part, second, third):
            return False
    return True


def _boundary(part: str, end: int, start: int) -> int:
    """Syllable boundary inside the consonants between two nuclei [end, start)"""
    units = _consonant_units(part[end:start])
    if len(units) < 2:
        return end
    # an onset cluster goes to the next syllable whole, otherwise only the last unit does
    cut = len(units) - 2 if units[-2] + units[-1] in ONSET_CLUSTERS else len(units) - 1
    return end + sum(len(unit) for unit in units[:cut])


def _consonant_units(consonants: str) -> list[str]:
    """Consonant letters grouped into units: digraphs and the silent u stay together"""
    units: list[str] = []
    index = 0
    while index < len(consonants):
        pair = consonants[index : index + 2]
        if pair in DIGRAPHS:
            units.append(pair)
            index += 2
        else:
            units.append(consonants[index])
            index += 1
    return units


def _part_stress(syllables: list[str]) -> int:
    """Stressed syllable of a run of letters by its written accent or ending"""
    for index, syllable in enumerate(syllables):
        if any(letter in ACCENTED_VOWELS for letter in syllable):
            return index
    if len(syllables) == 1:
        return 0
    last = syllables[-1]
    if last[-1] in VOWELS or (
        last[-1] in "nsy" and len(last) > 1 and (last[-2] in VOWELS) == (last[-1] != "y")
    ):
        return len(syllables) - 2
    return len(syllables) - 1


def _is_adverb(part: str, syllables: list[str]) -> bool:
    """Whether a run of letters is an adverb in -mente with the stress of its adjective"""
    if not part.endswith("mente") or len(syllables) < 3 or part in NON_ADVERBS_MENTE:
        return False
    stem = part[:-5]
    return stem[-1] in "aelrzns" or any(letter in ACCENTED_VOWELS for letter in stem)
