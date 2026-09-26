import re
import string
import unicodedata
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from itertools import pairwise
from math import nan
from typing import Any, NamedTuple

from spacy.tokens import Doc

from .constants import (
    ACCENTED_VOWELS,
    HIATUS_VOWELS,
    RHYME_MIN_ASSONANCE,
    RHYME_MIN_ASSONANT_LINES,
    RHYME_MIN_FREE,
    RHYME_WINDOW,
    VERSE_ARTE_MAYOR,
    VERSE_CLAUSULAS,
    VERSE_HEMISTICHS,
    VERSE_MAX_DEVIATIONS,
    VERSE_METERS,
    VERSE_MIN_LINES,
    VERSE_PROCLITICS,
    VERSE_RHYMES,
    VERSE_RHYTHMS,
    VERSE_STATS_DESC,
    VERSE_STROPHES,
    VOWELS,
)
from .exceptions import SourceError, SourceTypeError
from .syllables import WORD_PARTS, syllabify, word_stresses
from .utils import safe_divide

ACUTE = "\u0301"
LETTER = re.compile(r"[^\W\d_]")
# A roman numeral of a part of a poem on a line of its own: II, IV., (VII)
ROMAN_NUMERAL = re.compile(r"\(?[IVXLCDM]+[.)]?")
WORD_PATTERN = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")
PATTERN_STRESSED = "+"
PATTERN_UNSTRESSED = "-"
# Mark of a synalepha between two words in a metrical syllable
SYNALEPHA = "‿"
METER_NAMES = {length: name for name, length in VERSE_METERS.items()}
STRONG_VOWELS = frozenset("aeoáéóàèòâêôãõäëö")
# Spellings of the sounds of a rhyme: the silent u of gue and gui, the soft c and g, the
# consonant y, the digraphs and the letters of one sound
RHYME_SILENT_U = re.compile(r"gu(?=[eéií])")
RHYME_SOFT_C = re.compile(r"c(?=[eéií])")
RHYME_SOFT_G = re.compile(r"g(?=[eéií])")
RHYME_CONSONANT_Y = re.compile(r"y(?=[aeiouáéíóú])")
RHYME_DIGRAPHS = (("gü", "gw"), ("ch", "ʧ"), ("ll", "ʝ"), ("rr", "R"), ("qu", "k"), ("x", "ks"))
RHYME_LETTERS = str.maketrans("ckzvjGyáéíóúüàèìòùâêîôûäëïö", "kkθbxgiaeiouuaeiouaeiouaeio", "h")
MAX_STROPHE_LINES = max(n_lines for n_lines, *_ in VERSE_STROPHES.values())
# Scheme of a sonnet, letters from a: quatrains ABBA or ABAB, the second on the rhymes of
# the first or on its own, the tercets on rhymes of their own
SONNET_SCHEME = re.compile(r"(abba|abab)(abba|abab|baab|baba|cddc|cdcd)[c-h]{6}")
# The final unstressed i and u of an assonance sound as e and o: fácil - valle, Venus - lento
ASSONANT_FINALS = {"i": "e", "u": "o"}
# Boundaries between the units of a line: none can be joined, a diphthong split by a
# dieresis, a synalepha between two words, a hiatus in a word joined by a synaeresis
HARD, DIPHTHONG, SYNALEPHA_BOUNDARY, SYNAERESIS = range(4)


@dataclass(slots=True)
class _Word:
    """Word of a line of verse"""

    text: str
    start: int
    tonic: bool


@dataclass(slots=True)
class _Unit:
    """Syllable of a word or a part of a diphthong that a dieresis can split"""

    text: str
    word: int
    stressed: bool


class _Scansion(NamedTuple):
    """
    Scansion of a line

    Description:
        The syllables as the verse reads them, the indices of the stressed
        ones, the stressed metrical syllables, the length in metrical
        syllables, the syllables after the last stress and the first syllable
        of the second hemistich; in a compound verse each hemistich counts its
        own metrical syllables
    """

    syllables: tuple[str, ...]
    stresses: tuple[int, ...]
    metrical: tuple[int, ...]
    length: int
    tail: int
    caesura: int | None = None


@dataclass(slots=True)
class _Line:
    """Line of verse"""

    text: str
    words: list[_Word]
    units: list[_Unit]
    bounds: list[int]
    stanza: int
    scansion: _Scansion


class VerseStats:
    """
    Class for computing the verse statistics of a text

    Description:
        Stanzas are separated by blank lines. A line is measured in metrical
        syllables: a synalepha joins the vowels of two words, the unstressed
        words (VERSE_PROCLITICS) take no stress except at the end of a line, and
        by the law of the final stress a line counts up to its last stress and
        one syllable more. The meter is the most common length, every line
        fitted to it by the fewest hiatuses, diereses and synaereses, a compound
        verse (VERSE_HEMISTICHS) by its hemistichs; it is None if more than a
        tenth of the lines (VERSE_MAX_DEVIATIONS) are off it. A line rhymes with
        a line of the RHYME_WINDOW lines before it in full (consonante) or, in
        a poem rhymed by assonance or on alternate lines, by assonance
        (asonante). A rhyme scheme is upper case for arte mayor
        (VERSE_ARTE_MAYOR syllables and more), lower case for arte menor and a
        hyphen for an unrhymed line: ABBA ABBA CDC DCD, aBabB, -a-a. Stanzas
        are named by VERSE_STROPHES, the poem by its form. A text without
        Spanish syllables gives n_lines 0, the meter None and nan shares

    References:
        Quilis A. Métrica española. Barcelona: Ariel, 1984
        Navarro Tomás T. Métrica española. Madrid: Guadarrama, 1972
        https://github.com/linhd-postdata/rantanplan

    Example:
        >>> from ests import VerseStats
        >>> text = '''Cuando me paro a contemplar mi estado
        ... y a ver los pasos por do me han traído,
        ... hallo, según por do anduve perdido,
        ... que a mayor mal pudiera haber llegado.'''
        >>> vs = VerseStats(text)
        >>> vs.meter, vs.n_feet, vs.p_deviations, vs.p_pyrrhics
        ('endecasílabo', 11, 0.0, 0.0)
        >>> vs.patterns[0], vs.syllables[0]
        ('---+---+-+-', ('cuan', 'do', 'me', 'pa', 'ro‿a', 'con', 'tem', 'plar', 'mi‿es', 'ta', 'do'))
        >>> vs.c_rhythms, vs.c_clausulas
        ({'4-8-10': 2, '4-7-10': 1, '3-6-10': 1}, {'llana': 4})
        >>> vs.rhyme_schemes, vs.strophes, vs.c_rhymes
        (('ABBA',), ('cuarteto',), {'consonante': 4})
        >>> print(vs.accentuate())
        Cuando me páro a contemplár mi estádo
        y a vér los pásos por do me hán traído,
        hállo, según por do andúve perdído,
        que a mayór mál pudiéra habér llegádo.

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        seseo (bool): Pronounce c and z before e and i as s in the rhyme, as in
            Andalusia and in America: voz - dos, caza - casa

    Attributes:
        lines (tuple[str]): Lines with Spanish words
        stanzas (tuple[tuple[str, ...], ...]): Lines by stanza
        n_lines (int): Number of lines
        n_stanzas (int): Number of stanzas
        meter (str|None): Meter - the name of the verse by its syllables
            (octosílabo, endecasílabo, alejandrino...) or None
        n_feet (int|None): Number of metrical syllables of the meter
        c_feet (dict[int, int]): Distribution of the lines by metrical syllables
        p_deviations (float): Share of the lines off the meter, nan without a meter
        p_pyrrhics (float): Share of the lines of the meter without its rhythmic
            stresses (VERSE_RHYTHMS), 0 for a meter with the last stress alone,
            nan without a meter
        stress_profile (tuple[float, ...]): Share of the stressed lines of the
            meter by syllable
        c_rhythms (dict[str, int]): Distribution of the endecasílabos by type:
            the first stress before the 6th (1-6-10 enfático, 2-6-10 heroico,
            3-6-10 melódico, 4-6-10), 6-10, 4-8-10 (sáfico), 4-7-10 (dactílico)
        syllables (tuple[tuple[str, ...], ...]): Syllables of every line as the
            verse reads them, a synalepha marked with ‿ (ro‿a)
        stresses (tuple[tuple[int, ...], ...]): Indices of the stressed syllables
            of every line in syllables, from zero
        caesuras (tuple[int|None, ...]): Index of the first syllable of the
            second hemistich of every line in syllables, None for a simple verse
        patterns (tuple[str, ...]): Patterns of the lines of + (a stressed
            metrical syllable) and - (an unstressed one), a syllable longer than
            the line after an aguda and shorter after an esdrújula, at the end of
            a line and of a hemistich
        c_clausulas (dict[str, int]): Distribution of the endings of the lines by type
        p_masculine (float): Share of oxytone endings (aguda)
        p_feminine (float): Share of paroxytone endings (llana)
        p_dactylic (float): Share of proparoxytone endings (esdrújula)
        c_stressed_vowels (dict[str, int]): Distribution of the stressed vowels
        mean_line_len (float): Mean length of a line in metrical syllables
        rhyme_schemes (tuple[str, ...]): Rhyme schemes of the stanzas
        p_rhymed (float): Share of the rhymed lines
        c_rhymes (dict[str, int]): Distribution of the rhymed lines by the kind of
            the rhyme: consonante, asonante
        strophes (tuple[str|None, ...]): Names of the stanzas: cuarteto,
            redondilla, lira, octava real, décima... (VERSE_STROPHES)
        form (str|None): Form of the poem: soneto, romance, the strophe of all its
            stanzas, silva
        seseo (bool): Whether the rhyme is read with seseo

    Methods:
        get_stats: Getting the computed verse statistics
        print_stats: Printing the computed verse statistics with descriptions
        accentuate: Getting the text with the stresses marked

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc
        SourceError: If the source has no words
    """

    def __init__(self, source: str | Doc, seseo: bool = False):
        if isinstance(source, Doc):
            text = source.text
        elif isinstance(source, str):
            text = source
        else:
            raise SourceTypeError("The data source is set incorrectly")
        if not LETTER.search(text):
            raise SourceError("The data source has no words")
        lines = _parse_lines(text)
        self._lines = lines
        self.lines = tuple(line.text for line in lines)
        stanzas = _stanza_ranges(lines)
        self._stanzas = stanzas
        n_stanzas = len(stanzas)
        self.stanzas = tuple(tuple(self.lines[number] for number in stanza) for stanza in stanzas)
        self.n_lines = len(lines)
        self.n_stanzas = n_stanzas

        fitted = _fit_meter(lines)
        meter = None
        length = hemistich = None
        p_deviations = nan
        if fitted is not None:
            length, hemistich, scansions = fitted
            meter = METER_NAMES.get(length)
            p_deviations = sum(scansion.length != length for scansion in scansions) / len(lines)
            if meter is None or p_deviations > VERSE_MAX_DEVIATIONS:
                meter = None
                p_deviations = nan
                scansions = _fit_polymetric(lines)
            for line, scansion in zip(lines, scansions, strict=True):
                line.scansion = scansion
        self.meter = meter
        self.n_feet = length if meter is not None else None
        self.p_deviations = p_deviations

        self.seseo = seseo
        endings = [_ending(line.words[-1].text, seseo) for line in lines]
        groups, kinds = _rhyme_groups(endings, stanzas)
        strophes = []
        for numbers in stanzas:
            name, refitted = _strophe(
                [lines[number] for number in numbers],
                [groups[number] for number in numbers],
                [kinds[number] for number in numbers],
                refit=meter is None,
            )
            strophes.append(name)
            for number, refit in zip(numbers, refitted, strict=True):
                lines[number].scansion = refit
        self.strophes = tuple(strophes)
        scansions = [line.scansion for line in lines]
        self.syllables = tuple(scansion.syllables for scansion in scansions)
        self.stresses = tuple(scansion.stresses for scansion in scansions)
        self.caesuras = tuple(scansion.caesura for scansion in scansions)
        self.patterns = tuple(_pattern(scansion) for scansion in scansions)
        self.c_feet = dict(sorted(Counter(scansion.length for scansion in scansions).items()))
        self.mean_line_len = safe_divide(
            sum(scansion.length for scansion in scansions), len(scansions), nan
        )

        metrical = [scansion for scansion in scansions if scansion.length == self.n_feet]
        self.stress_profile: tuple[float, ...] = ()
        self.p_pyrrhics = nan
        if self.n_feet is not None:
            self.stress_profile = tuple(
                sum(position in scansion.metrical for scansion in metrical) / len(metrical)
                for position in range(self.n_feet)
            )
            rhythms = _rhythms(self.meter, hemistich)
            self.p_pyrrhics = sum(
                bool(rhythms) and not _has_rhythm(scansion, rhythms) for scansion in metrical
            ) / len(metrical)
        rhythm_types = Counter(
            rhythm
            for scansion in scansions
            if scansion.length == VERSE_METERS["endecasílabo"]
            and (rhythm := _endecasyllable_type(scansion.metrical)) is not None
        )
        self.c_rhythms = dict(rhythm_types.most_common())

        clausulas = Counter(
            VERSE_CLAUSULAS[min(scansion.tail, len(VERSE_CLAUSULAS) - 1)] for scansion in scansions
        )
        self.c_clausulas = {name: clausulas[name] for name in VERSE_CLAUSULAS if clausulas[name]}
        n_clausulas = sum(clausulas.values())
        self.p_masculine = safe_divide(clausulas[VERSE_CLAUSULAS[0]], n_clausulas, nan)
        self.p_feminine = safe_divide(clausulas[VERSE_CLAUSULAS[1]], n_clausulas, nan)
        self.p_dactylic = safe_divide(clausulas[VERSE_CLAUSULAS[2]], n_clausulas, nan)

        vowels = Counter(
            _nucleus(unit.text) for line in lines for unit in line.units if unit.stressed
        )
        self.c_stressed_vowels = dict(vowels.most_common())

        labels = _scheme_labels(groups, [scansion.length for scansion in scansions])
        self.rhyme_schemes = tuple(
            "".join(labels[number] for number in stanza) for stanza in stanzas
        )
        rhymes = Counter(kind for kind in kinds if kind is not None)
        self.c_rhymes = {kind: rhymes[kind] for kind in VERSE_RHYMES if rhymes[kind]}
        self.p_rhymed = safe_divide(sum(rhymes.values()), len(lines), nan)
        self.form = _form(self, labels, kinds)

    def get_stats(self) -> dict[str, Any]:
        """
        Getting the computed verse statistics of the text

        Returns:
            dict[str, object]: Dictionary of the computed verse statistics
        """
        return {stat: getattr(self, stat) for stat in VERSE_STATS_DESC}

    def print_stats(self) -> None:
        """Printing the computed verse statistics of the text with descriptions"""
        print(f"{'Statistic':^46}|{'Value':^14}")
        print("-" * 60)
        for stat, value in self.get_stats().items():
            text = f"{value:.2f}" if isinstance(value, float) else str(value)
            print(f"{VERSE_STATS_DESC[stat]:46}|{text:^14}")

    def accentuate(self) -> str:
        """
        Getting the text with the stresses marked

        Description:
            A combining acute accent (U+0301) is put after the stressed vowel of
            every stressed word without a written accent, so NFC normalization
            turns it into an accented letter; the unstressed words
            (VERSE_PROCLITICS) stay unmarked, except the last word of a line.
            The lines are the ones of lines, the stanzas separated by a blank line

        Returns:
            str: Text with the stresses
        """
        return "\n\n".join(
            "\n".join(_accentuate_line(self._lines[number]) for number in stanza)
            for stanza in self._stanzas
        )


def split_stanzas(text: str) -> list[list[str]]:
    """
    Splitting a text into stanzas and lines

    Description:
        The stanzas are separated by blank lines; the lines without a Spanish
        syllable (numbers, asterisks, other alphabets) and the roman numerals of
        the parts of a poem (II, IV.) are left out. The text is normalized to NFC

    Arguments:
        text (str): Text of a poem

    Returns:
        list[list[str]]: Lines by stanza
    """
    stanzas = []
    text = unicodedata.normalize("NFC", text)
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.strip() for line in block.split("\n") if _has_syllables(line)]
        if lines:
            stanzas.append(lines)
    return stanzas


def _has_syllables(line: str) -> bool:
    """Checking that a line has a word with syllables and is no roman numeral"""
    if ROMAN_NUMERAL.fullmatch(line.strip()):
        return False
    return any(syllabify(match.group()) for match in WORD_PATTERN.finditer(line))


def _stanza_ranges(lines: Sequence[_Line]) -> list[range]:
    """Numbers of the lines of every stanza - the lines of a stanza follow one another"""
    starts = [
        number
        for number, line in enumerate(lines)
        if not number or line.stanza != lines[number - 1].stanza
    ]
    return [range(start, end) for start, end in pairwise([*starts, len(lines)])]


def _parse_lines(text: str) -> list[_Line]:
    """Splitting a text into lines of words and units with the plain reading"""
    lines = []
    for number, stanza in enumerate(split_stanzas(text)):
        for line_text in stanza:
            words, units, bounds = _parse_line(line_text)
            default = _scan(units, _default_joins(bounds))
            lines.append(_Line(line_text, words, units, bounds, number, default))
    return lines


def _parse_line(text: str) -> tuple[list[_Word], list[_Unit], list[int]]:
    """Words of a line, their units and the boundaries between the units"""
    matches = [match for match in WORD_PATTERN.finditer(text) if syllabify(match.group())]
    words = []
    units: list[_Unit] = []
    bounds: list[int] = []
    for number, match in enumerate(matches):
        word = match.group()
        tonic = number == len(matches) - 1 or word.lower() not in VERSE_PROCLITICS
        words.append(_Word(word, match.start(), tonic))
        stresses = set(word_stresses(word)) if tonic else set()
        for index, syllable in enumerate(syllabify(word)):
            if units:
                bounds.append(_boundary(units[-1], syllable, number))
            cut = _dieresis(syllable) if index in stresses else None
            if cut is None:
                units.append(_Unit(syllable, number, index in stresses))
            else:
                units.append(_Unit(syllable[:cut], number, False))
                bounds.append(DIPHTHONG)
                units.append(_Unit(syllable[cut:], number, True))
    return words, units, bounds


def _boundary(previous: _Unit, syllable: str, word: int) -> int:
    """Kind of the boundary between a unit and the next syllable"""
    if not (_ends_in_vowel(previous.text) and _starts_with_vowel(syllable)):
        return HARD
    if previous.word != word:
        return SYNALEPHA_BOUNDARY
    # A diaeresis is the mark of a hiatus that no synaeresis joins (sü-a-ve, glo-rï-o-sa)
    if previous.text[-1] in HIATUS_VOWELS or syllable.lstrip("h")[:1] in HIATUS_VOWELS:
        return HARD
    return SYNAERESIS


def _ends_in_vowel(syllable: str) -> bool:
    """Checking that a syllable ends in a vowel sound: a vowel, y (rey, muy) or a vowel and h"""
    if syllable[-1] in VOWELS or syllable[-1] == "y":
        return True
    return syllable[-1] == "h" and len(syllable) > 1 and syllable[-2] in VOWELS


def _starts_with_vowel(syllable: str) -> bool:
    """
    Checking that a syllable starts with a vowel sound

    Description:
        A silent h is skipped; hi and hu before a vowel (hierba, hueso) and y
        before a vowel (ya, yo) are consonants, the conjunction y is a vowel
    """
    if syllable[0] == "h":
        syllable = syllable[1:]
        if len(syllable) > 1 and syllable[0] in "iu" and syllable[1] in VOWELS:
            return False
    if syllable[0] == "y":
        return len(syllable) == 1
    return syllable[0] in VOWELS


def _dieresis(syllable: str) -> int | None:
    """
    Position where a dieresis splits a rising diphthong of a syllable

    Description:
        A weak vowel (i, u, ü) before another vowel is split from it (su-a-ve,
        ru-i-do, con-fi-a-do); the silent u of que and gui is no vowel, and a
        weak vowel after a vowel belongs to a falling diphthong or a triphthong
    """
    for index in range(len(syllable) - 1):
        letter, following = syllable[index], syllable[index + 1]
        if letter not in "iuü" or following not in VOWELS or following == letter:
            continue
        if letter == "u" and index and syllable[index - 1] in "qg" and following in "eéií":
            continue
        if index and syllable[index - 1] in VOWELS:
            continue
        return index + 1
    return None


def _default_joins(bounds: Sequence[int]) -> set[int]:
    """Boundaries joined in the plain reading: the diphthongs and every synalepha"""
    return {index for index, kind in enumerate(bounds) if kind in (DIPHTHONG, SYNALEPHA_BOUNDARY)}


def _scan(units: Sequence[_Unit], joins: set[int]) -> _Scansion:
    """
    Metrical syllables of units with the joined boundaries

    Description:
        A metrical syllable is stressed if a unit in it is stressed; the line
        counts up to its last stress and one syllable more (the law of the
        final stress)
    """
    syllables: list[str] = []
    flags: list[bool] = []
    for index, unit in enumerate(units):
        if index and index - 1 in joins:
            mark = SYNALEPHA if units[index - 1].word != unit.word else ""
            syllables[-1] += mark + unit.text
            flags[-1] = flags[-1] or unit.stressed
        else:
            syllables.append(unit.text)
            flags.append(unit.stressed)
    stresses = tuple(index for index, flag in enumerate(flags) if flag)
    last = stresses[-1] if stresses else len(flags) - 1
    return _Scansion(tuple(syllables), stresses, stresses, last + 2, len(flags) - 1 - last)


def _fit(units: Sequence[_Unit], bounds: Sequence[int], length: int) -> _Scansion:
    """
    Scansion of units fitted to a length

    Description:
        A longer plain reading joins the hiatuses in a word (synaeresis), the
        ones with an accented i or u last; a shorter one breaks the synalephas
        from the end of the line (hiatus), then splits the diphthongs
        (dieresis). A change is kept if it moves the length; a length out of
        reach returns the plain reading
    """
    joins = _default_joins(bounds)
    plain = _scan(units, joins)
    if plain.length == length:
        return plain
    if plain.length < length:
        # Every join is before the stressed last word, so breaking one adds a syllable
        order = sorted(joins, key=lambda index: (bounds[index] != SYNALEPHA_BOUNDARY, -index))
        if length - plain.length > len(order):
            return plain
        return _scan(units, joins.difference(order[: length - plain.length]))
    order = sorted(
        (index for index, kind in enumerate(bounds) if kind == SYNAERESIS),
        key=lambda index: (_accented_weak(units[index], units[index + 1]), index),
    )
    if plain.length - length > len(order):
        return plain
    scansion = plain
    for index in order:
        trial = _scan(units, joins | {index})
        if trial.length < scansion.length:
            joins.add(index)
            scansion = trial
        if scansion.length == length:
            return scansion
    return plain


def _accented_weak(first: _Unit, second: _Unit) -> bool:
    """Checking that a hiatus has an accented i or u (dí-a, ba-úl)"""
    return first.text[-1] in "íú" or second.text.lstrip("h")[:1] in "íú"


def _caesuras(line: _Line) -> list[int]:
    """Units where a word starts after a stressed word - the places of a caesura"""
    return [
        index
        for index in range(1, len(line.units))
        if line.units[index].word != line.units[index - 1].word
        and line.words[line.units[index - 1].word].tonic
    ]


def _hemistichs(line: _Line, cut: int) -> tuple[tuple[list[_Unit], list[int]], ...]:
    """Units and boundaries of the two hemistichs of a line cut by a caesura"""
    return (
        (line.units[:cut], line.bounds[: cut - 1]),
        (line.units[cut:], line.bounds[cut:]),
    )


def _fit_compound(line: _Line, hemistich: int) -> _Scansion | None:
    """
    Scansion of a line as two hemistichs of a length

    Description:
        Every caesura after a stressed word is tried; each hemistich is fitted
        to the length on its own, and the caesura with the fewest changes of
        the plain readings wins
    """
    if not _reaches(line, 2 * hemistich):
        return None
    best: tuple[int, _Scansion] | None = None
    for cut in _caesuras(line):
        parts = []
        cost = 0
        for units, bounds in _hemistichs(line, cut):
            scansion = _fit(units, bounds, hemistich)
            if scansion.length != hemistich:
                break
            cost += abs(_scan(units, _default_joins(bounds)).length - hemistich)
            parts.append(scansion)
        else:
            first, second = parts
            caesura = len(first.syllables)
            joined = _Scansion(
                first.syllables + second.syllables,
                first.stresses + tuple(caesura + index for index in second.stresses),
                first.metrical + tuple(hemistich + position for position in second.metrical),
                2 * hemistich,
                second.tail,
                caesura,
            )
            if best is None or cost < best[0]:
                best = (cost, joined)
    return best[1] if best is not None else None


def _reaches(line: _Line, compound: int, fitted: bool = True) -> bool:
    """
    Checking that a line may split into two hemistichs of a compound verse

    Description:
        The hemistichs differ from the plain reading of the whole line by two
        syllables at most - the synalepha at the caesura and the aguda or the
        esdrújula before it - and a fitted line by one syllable more for every
        join it breaks and one less for every synaeresis
    """
    low = high = line.scansion.length
    if fitted:
        low -= sum(kind == SYNAERESIS for kind in line.bounds)
        high += sum(kind in (DIPHTHONG, SYNALEPHA_BOUNDARY) for kind in line.bounds)
    return low - 2 <= compound <= high + 2


def _scan_line(line: _Line, length: int, hemistich: int | None) -> _Scansion:
    """Scansion of a line fitted to the meter, by hemistichs for a compound verse"""
    if hemistich is not None:
        compound = _fit_compound(line, hemistich)
        if compound is not None:
            return compound
    return _fit(line.units, line.bounds, length)


def _fit_meter(lines: Sequence[_Line]) -> tuple[int, int | None, list[_Scansion]] | None:
    """
    Length of the meter of the lines, the length of its hemistich and the fitted lines

    Description:
        The candidates are the lengths of most plain readings - on a tie the
        shortest of two lines, the named ones (or the shortest) from three
        lines up - and a compound verse (VERSE_HEMISTICHS) within one syllable
        of such a length if more than half of the plain readings split into its
        hemistichs. The lines are fitted to each, and the one with the fewest
        lines off it wins, the shorter length and the compound verse on a tie.
        Fewer lines than VERSE_MIN_LINES have no meter
    """
    if len(lines) < VERSE_MIN_LINES:
        return None
    lengths = Counter(line.scansion.length for line in lines)
    most = max(lengths.values())
    tied = sorted(length for length, count in lengths.items() if count == most)
    if len(lines) < 3:
        tied = tied[:1]
    else:
        # A length with no name gives no meter, and prose would tie many of them
        tied = [length for length in tied if length in METER_NAMES] or tied[:1]
    candidates: list[tuple[int, int | None]] = []
    for length in tied:
        candidates += [
            (compound, hemistich)
            for compound, hemistich in VERSE_HEMISTICHS.items()
            if abs(compound - length) <= 1
            and (compound, hemistich) not in candidates
            and sum(_splits(line, hemistich) for line in lines) > len(lines) / 2
        ]
        candidates.append((length, None))
    _, length, hemistich, scansions = _best_fit(lines, candidates)
    return length, hemistich, scansions


def _fit_polymetric(lines: Sequence[_Line]) -> list[_Scansion]:
    """
    Scansions of the lines of a poem with no meter, fitted to its common lengths

    Description:
        The common lengths are the named lengths of the plain readings of at
        least two lines and a tenth of them (VERSE_MAX_DEVIATIONS), as the 7
        and 11 syllables of a silva. If they take more than half of the lines,
        every other line is fitted to the nearest of them it reaches, the
        longer on a tie; otherwise the lines keep their plain readings
    """
    lengths = Counter(line.scansion.length for line in lines)
    common = [
        length
        for length, count in lengths.items()
        if length in METER_NAMES and count >= max(2, VERSE_MAX_DEVIATIONS * len(lines))
    ]
    if sum(lengths[length] for length in common) <= len(lines) / 2:
        return [line.scansion for line in lines]
    scansions = []
    for line in lines:
        scansion = line.scansion
        plain = scansion.length
        if plain not in common:
            for length in sorted(common, key=lambda value: (abs(value - plain), -value)):
                fitted = _fit(line.units, line.bounds, length)
                if fitted.length == length:
                    scansion = fitted
                    break
        scansions.append(scansion)
    return scansions


def _best_fit(
    lines: Sequence[_Line], candidates: Sequence[tuple[int, int | None]]
) -> tuple[int, int, int | None, list[_Scansion]]:
    """The candidate meter with the fewest lines off it and its fitted lines, the first on a tie"""
    best: tuple[int, int, int | None, list[_Scansion]] | None = None
    for length, hemistich in candidates:
        scansions = [_scan_line(line, length, hemistich) for line in lines]
        n_off = sum(scansion.length != length for scansion in scansions)
        if best is None or n_off < best[0]:
            best = (n_off, length, hemistich, scansions)
    assert best is not None
    return best


def _splits(line: _Line, hemistich: int) -> bool:
    """Checking that the plain reading of a line splits into two hemistichs of a length"""
    if not _reaches(line, 2 * hemistich, fitted=False):
        return False
    return any(
        all(
            _scan(units, _default_joins(bounds)).length == hemistich
            for units, bounds in _hemistichs(line, cut)
        )
        for cut in _caesuras(line)
    )


def _pattern(scansion: _Scansion) -> str:
    """Pattern of a line: + for a stressed metrical syllable, - for an unstressed one"""
    return "".join(
        PATTERN_STRESSED if position in scansion.metrical else PATTERN_UNSTRESSED
        for position in range(scansion.length)
    )


def _rhythms(meter: str | None, hemistich: int | None) -> tuple[tuple[int, ...], ...]:
    """Rhythmic stresses of a meter, 1-based: one of the sets"""
    if meter in VERSE_RHYTHMS:
        return VERSE_RHYTHMS[meter]
    if hemistich is not None:
        return ((hemistich - 1,),)
    return ()


def _has_rhythm(scansion: _Scansion, rhythms: Sequence[Sequence[int]]) -> bool:
    """Checking that a line has one of the sets of rhythmic stresses"""
    return any(all(position - 1 in scansion.metrical for position in rhythm) for rhythm in rhythms)


def _endecasyllable_type(stresses: Sequence[int]) -> str | None:
    """
    Type of an endecasílabo by its stresses

    Description:
        With the 6th syllable stressed - by the first stress before it
        (1-6-10 enfático, 2-6-10 heroico, 3-6-10 melódico, 4-6-10, 5-6-10) or
        6-10 without one; otherwise 4-8-10 (sáfico) and 4-7-10 (dactílico);
        None for a line without the rhythmic stresses
    """
    positions = {position + 1 for position in stresses}
    if 6 in positions:
        first = min(positions)
        return f"{first}-6-10" if first < 6 else "6-10"
    if 4 in positions and 8 in positions:
        return "4-8-10"
    if 4 in positions and 7 in positions:
        return "4-7-10"
    return None


class _Ending(NamedTuple):
    """Rhyme ending of a line: its sounds from the stressed vowel and its assonance"""

    consonant: str
    assonant: tuple[str, ...]


def _ending(word: str, seseo: bool) -> _Ending:
    """
    Rhyme ending of the last word of a line

    Description:
        The sounds from the stressed vowel to the end of the word
        (_rhyme_sounds), and the assonance: the stressed vowel and the vowel
        of the last syllable, the one of an aguda alone; a diphthong gives its
        stressed vowel (cie-lo - e, gra-cia - a), the vowels between them are
        left out (pá-li-do - a, o), and a final i and u sound as e and o
        (fá-cil - a, e)
    """
    syllables = syllabify(word)
    stress = word_stresses(word)[-1]
    syllable = syllables[stress]
    tail = syllable[_nucleus_index(syllable) :] + "".join(syllables[stress + 1 :])
    sounds = _rhyme_sounds(tail, seseo)
    if stress == len(syllables) - 1:
        return _Ending(sounds, (_nucleus(syllable),))
    final = _nucleus(syllables[-1])
    return _Ending(sounds, (_nucleus(syllable), ASSONANT_FINALS.get(final, final)))


def _rhyme_sounds(tail: str, seseo: bool) -> str:
    """
    Sounds of the end of a word for a full rhyme

    Description:
        The letters of one sound are one symbol: b and v, c, k and qu, c and z
        before e and i (s with seseo), g before e and i and j, ll and y before
        a vowel (yeísmo); h is silent, as the u of gue and gui, the tap r and
        the trill rr differ, and the accents are left out
    """
    for spelling, sound in RHYME_DIGRAPHS:
        tail = tail.replace(spelling, sound)
    tail = RHYME_SILENT_U.sub("G", tail)
    tail = RHYME_SOFT_C.sub("θ", tail)
    tail = RHYME_SOFT_G.sub("x", tail)
    tail = RHYME_CONSONANT_Y.sub("ʝ", tail).translate(RHYME_LETTERS)
    return tail.replace("θ", "s") if seseo else tail


def _chains(keys: Sequence[object]) -> list[int | None]:
    """
    Groups of the lines with an equal key in the window

    Description:
        Every line joins the group of the nearest line before it in the window
        of RHYME_WINDOW lines with the same key; the groups are numbered in
        the order of appearance, a line with no such line has none
    """
    groups: list[int | None] = [None] * len(keys)
    n_groups = 0
    for number, key in enumerate(keys):
        for previous in range(number - 1, max(-1, number - 1 - RHYME_WINDOW), -1):
            if keys[previous] == key:
                if groups[previous] is None:
                    groups[previous] = n_groups
                    n_groups += 1
                groups[number] = groups[previous]
                break
    return groups


def _rhyme_groups(
    endings: Sequence[_Ending], stanzas: Sequence[range]
) -> tuple[list[int | None], list[str | None]]:
    """
    Groups of rhyming lines and the kind of the rhyme of every line

    Description:
        The lines rhyme by their full endings (consonante), and by assonance
        (asonante) in two cases. If lines with no full rhyme sharing one
        assonance make a third of the poem (RHYME_MIN_ASSONANCE) and at least
        RHYME_MIN_ASSONANT_LINES, the groups follow the assonances of all the
        lines, the full rhymes of the same vowels included. Otherwise the
        assonance counts on alternate lines with unrhymed lines between them
        (_alternations), the full rhymes of those lines joining them. A group
        of different full endings is asonante; an assonance of neighbouring
        lines alone is no rhyme
    """
    full = _chains([ending.consonant for ending in endings])
    free = Counter(
        ending.assonant for ending, group in zip(endings, full, strict=True) if group is None
    )
    if free and max(free.values()) >= max(
        RHYME_MIN_ASSONANT_LINES, RHYME_MIN_ASSONANCE * len(endings)
    ):
        groups = _chains([ending.assonant for ending in endings])
    else:
        links = _alternations(endings, full, stanzas)
        if not links:
            return full, [VERSE_RHYMES[0] if group is not None else None for group in full]
        groups = _join(full, links)
    consonants: dict[int, set[str]] = {}
    for ending, group in zip(endings, groups, strict=True):
        if group is not None:
            consonants.setdefault(group, set()).add(ending.consonant)
    kinds = [
        None if group is None else VERSE_RHYMES[len(consonants[group]) > 1] for group in groups
    ]
    return groups, kinds


def _alternations(
    endings: Sequence[_Ending], full: Sequence[int | None], stanzas: Sequence[range]
) -> list[tuple[int, int]]:
    """
    Pairs of alternate lines that rhyme by assonance

    Description:
        A run of lines two apart with one assonance - the even lines of a
        romance - rhymes if it has at least RHYME_MIN_ASSONANT_LINES lines and
        three in four of the lines between them have no full rhyme
        (RHYME_MIN_FREE), or if it is all the even lines of a stanza of an even
        number of lines with the lines between them unrhymed, as the second and
        the fourth line of a copla or a seguidilla
    """
    evens = {
        tuple(range(stanza.start + 1, stanza.stop, 2))
        for stanza in stanzas
        if len(stanza) >= 4 and len(stanza) % 2 == 0
    }
    links = []
    for start in (0, 1):
        run = [start]
        for number in [*range(start + 2, len(endings), 2), None]:
            if number is not None and endings[number].assonant == endings[run[-1]].assonant:
                run.append(number)
                continue
            between = [line + 1 for line in run[:-1]]
            n_free = sum(full[line] is None for line in between)
            if (
                len(run) >= RHYME_MIN_ASSONANT_LINES and n_free >= RHYME_MIN_FREE * len(between)
            ) or (tuple(run) in evens and n_free == len(between)):
                links += list(pairwise(run))
            if number is not None:
                run = [number]
    return links


def _join(full: Sequence[int | None], links: Sequence[tuple[int, int]]) -> list[int | None]:
    """Groups of the full rhymes joined by the links of assonance, numbered by their first line"""
    parent = list(range(len(full)))

    def root(line: int) -> int:
        while parent[line] != line:
            parent[line] = parent[parent[line]]
            line = parent[line]
        return line

    first_of_group: dict[int, int] = {}
    pairs = list(links)
    for line, group in enumerate(full):
        if group is not None:
            pairs.append((first_of_group.setdefault(group, line), line))
    for first, second in pairs:
        parent[root(second)] = root(first)
    linked = {line for pair in pairs for line in pair}
    numbers: dict[int, int] = {}
    return [
        numbers.setdefault(root(line), len(numbers)) if line in linked else None
        for line in range(len(full))
    ]


def _scheme_labels(groups: Sequence[int | None], lengths: Sequence[int]) -> list[str]:
    """
    Letters of the rhyme groups in the order of appearance, - for an unrhymed line

    Description:
        The letter is upper-case for a line of arte mayor (VERSE_ARTE_MAYOR
        syllables and more) and lower-case for one of arte menor: a lira is
        aBabB. When the 26 letters run out, the letter of a closed group is
        taken again - of a group that no line in the window can join any more
    """
    last_lines = {group: number for number, group in enumerate(groups) if group is not None}
    letters: dict[int, str] = {}
    used: dict[str, int] = {}
    labels = []
    for number, (group, length) in enumerate(zip(groups, lengths, strict=True)):
        if group is None:
            labels.append("-")
            continue
        if group not in letters:
            free = [letter for letter in string.ascii_lowercase if letter not in used]
            closed = [
                letter
                for letter, other in used.items()
                if last_lines[other] < number - RHYME_WINDOW
            ]
            letter = free[0] if free else min(closed, default="z")
            letters[group] = letter
            used[letter] = group
        letter = letters[group]
        labels.append(letter.upper() if length >= VERSE_ARTE_MAYOR else letter)
    return labels


def _relabel(labels: Sequence[str]) -> str:
    """Scheme in lower case with the letters from a in the order of their appearance"""
    letters: dict[str, str] = {}
    for label in labels:
        if label != "-" and label.lower() not in letters:
            letters[label.lower()] = string.ascii_lowercase[len(letters)]
    return "".join("-" if label == "-" else letters[label.lower()] for label in labels)


def _strophe(
    lines: Sequence[_Line],
    groups: Sequence[int | None],
    kinds: Sequence[str | None],
    refit: bool,
) -> tuple[str | None, list[_Scansion]]:
    """
    Name of a stanza by its lines, their lengths and its rhyme (VERSE_STROPHES)

    Description:
        The first strophe with the number of lines, one of the schemes (letters
        from a in the order of the stanza), the kind of the rhyme (asonante if
        a line rhymes so) and the lengths: all of arte mayor, all of arte menor
        or the syllables of every line. With refit (a poem with no meter) the
        lines are fitted to the syllables a strophe asks for. None for a stanza
        of no known form; the scansions of the lines are returned either way
    """
    scansions = [line.scansion for line in lines]
    if len(lines) > MAX_STROPHE_LINES:
        return None, scansions
    scheme = _relabel(["-" if group is None else str(group) for group in groups])
    kind = VERSE_RHYMES[1] if VERSE_RHYMES[1] in kinds else VERSE_RHYMES[0]
    for name, (n_lines, measure, schemes, rhyme) in VERSE_STROPHES.items():
        if len(lines) != n_lines or scheme not in schemes or rhyme not in (None, kind):
            continue
        if _has_lengths([scansion.length for scansion in scansions], measure):
            return name, scansions
        if refit and isinstance(measure, tuple):
            fitted = [
                _fit(line.units, line.bounds, length)
                for line, length in zip(lines, measure, strict=True)
            ]
            if all(
                scansion.length == length for scansion, length in zip(fitted, measure, strict=True)
            ):
                return name, fitted
    return None, scansions


def _has_lengths(lengths: Sequence[int], measure: str | tuple[int, ...] | None) -> bool:
    """Checking that the lengths of lines are of arte mayor, of arte menor or the given ones"""
    if measure is None:
        return True
    if measure == "mayor":
        return all(length >= VERSE_ARTE_MAYOR for length in lengths)
    if measure == "menor":
        return all(length < VERSE_ARTE_MAYOR for length in lengths)
    return tuple(lengths) == measure


def _form(verse: "VerseStats", labels: Sequence[str], kinds: Sequence[str | None]) -> str | None:
    """
    Form of a poem

    Description:
        soneto - 14 lines of a meter of arte mayor in full rhyme, the quatrains
        ABBA or ABAB and the tercets on rhymes of their own (CDC DCD, CDE CDE);
        romance - octosílabos from 8 lines, three in four of the even lines of
        the stanzas rhymed by assonance and three in four of the odd ones
        unrhymed; the strophe of all the stanzas; silva - heptasílabos and
        endecasílabos with no meter, longer than a strophe and with no pattern
        of lengths repeated by all its stanzas; None otherwise
    """
    scheme = _relabel(labels)
    if (
        verse.n_lines == 14
        and verse.n_feet is not None
        and verse.n_feet >= VERSE_ARTE_MAYOR
        and VERSE_RHYMES[1] not in kinds
        and SONNET_SCHEME.fullmatch(scheme)
        and all(scheme[8:].count(letter) >= 2 for letter in scheme[8:])
    ):
        return "soneto"
    # Counted by stanza, so that a title of a part on a line of its own shifts nothing
    even = [kinds[stanza.start + i] for stanza in verse._stanzas for i in range(1, len(stanza), 2)]
    odd = [kinds[stanza.start + i] for stanza in verse._stanzas for i in range(0, len(stanza), 2)]
    if (
        verse.n_lines >= 8
        and verse.meter == "octosílabo"
        and even.count(VERSE_RHYMES[1]) >= 0.75 * len(even)
        and odd.count(None) >= 0.75 * len(odd)
    ):
        return "romance"
    if len(set(verse.strophes)) == 1 and verse.strophes[0] is not None:
        return verse.strophes[0]
    patterns = {
        tuple(len(verse.patterns[number]) for number in stanza) for stanza in verse._stanzas
    }
    if (
        verse.meter is None
        and set(verse.c_feet) == {7, 11}
        and verse.n_lines > MAX_STROPHE_LINES
        and (len(patterns) > 1 or verse.n_stanzas == 1)
    ):
        return "silva"
    return None


def _nucleus(syllable: str) -> str:
    """Stressed vowel of a syllable without the accent, y read as i"""
    vowel = syllable[_nucleus_index(syllable)]
    return "i" if vowel == "y" else unicodedata.normalize("NFD", vowel)[0]


def _accentuate_word(word: str, stresses: Sequence[int]) -> str:
    """Word with an acute accent after the stressed vowel of every stressed syllable"""
    marks = []
    offset = 0
    lower = word.lower()
    syllable_number = 0
    for part in WORD_PARTS.finditer(lower):
        position = part.start()
        for syllable in syllabify(part.group()):
            if syllable_number in stresses and not any(
                letter in ACCENTED_VOWELS for letter in syllable
            ):
                nucleus = _nucleus_index(syllable)
                marks.append(position + nucleus + 1)
            position += len(syllable)
            syllable_number += 1
    pieces = []
    for mark in marks:
        pieces.append(word[offset:mark] + ACUTE)
        offset = mark
    pieces.append(word[offset:])
    return "".join(pieces)


def _nucleus_index(syllable: str) -> int:
    """
    Index of the stressed vowel of a syllable

    Description:
        The accented vowel, else the strong one (a, e, o), else the last weak
        one after the silent u of qu and gu (cui-da, qui-so); a y before no
        vowel is a weak vowel (muy, the conjunction y)
    """
    following = [*syllable[1:], ""]
    indices = [
        index
        for index, (letter, after) in enumerate(zip(syllable, following, strict=True))
        if letter in VOWELS or (letter == "y" and (not after or after not in VOWELS))
    ]
    if syllable.startswith(("qu", "gu")) and len(indices) > 1:
        indices = indices[1:]
    accented = [index for index in indices if syllable[index] in ACCENTED_VOWELS]
    strong = [index for index in indices if syllable[index] in STRONG_VOWELS]
    return (accented or strong or indices)[-1]


def _accentuate_line(line: _Line) -> str:
    """Line with the stresses of its stressed words marked"""
    pieces = []
    position = 0
    for word in line.words:
        if not word.tonic:
            continue
        pieces.append(line.text[position : word.start])
        pieces.append(_accentuate_word(word.text, word_stresses(word.text)))
        position = word.start + len(word.text)
    pieces.append(line.text[position:])
    return "".join(pieces)


def accentuate(text: str) -> str:
    """
    Marking the stresses in a text by the orthographic rules

    Description:
        An acute accent (U+0301) is put after the stressed vowel of every word
        without a written accent (word_stresses), both stresses of an adverb
        in -mente and of a hyphenated compound; the unstressed words of the
        verse (VERSE_PROCLITICS) stay unmarked. The text is normalized to NFC.
        For a poem, where the last word of a line is always stressed, use
        VerseStats.accentuate

    Arguments:
        text (str): Text

    Returns:
        str: Text with the stresses
    """

    def mark(match: re.Match[str]) -> str:
        word = match.group()
        if word.lower() in VERSE_PROCLITICS:
            return word
        return _accentuate_word(word, word_stresses(word))

    return WORD_PATTERN.sub(mark, unicodedata.normalize("NFC", text))


def detect_meter(text: str) -> str | None:
    """
    Detecting the meter of a poem

    Arguments:
        text (str): Text of a poem

    Returns:
        str|None: Meter - the name of the verse by its metrical syllables
            (octosílabo, endecasílabo, alejandrino...); None if most lines
            have no common length
    """
    return VerseStats(text).meter


def rhyme_scheme(text: str, seseo: bool = False) -> str:
    """
    Detecting the rhyme scheme of a poem

    Arguments:
        text (str): Text of a poem
        seseo (bool): Pronounce c and z before e and i as s in the rhyme

    Returns:
        str: Schemes of the stanzas separated by spaces, the letters in the
            order of the rhyme groups, upper-case for the lines of arte mayor,
            unrhymed lines as a hyphen: ABBA ABBA CDC DCD, abba cddc, -a-a
    """
    return " ".join(VerseStats(text, seseo=seseo).rhyme_schemes)
