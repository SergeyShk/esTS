import shutil
import unicodedata
from collections import Counter
from math import isnan
from pathlib import Path

import pytest
import spacy

from ests import VerseStats
from ests.constants import VERSE_STATS_DESC
from ests.datasets import SpanishSonnets
from ests.datasets import spanish_sonnets as sonnets_module
from ests.exceptions import SourceError, SourceTypeError
from ests.verse_stats import (
    _default_joins,
    _endecasyllable_type,
    _fit,
    _parse_line,
    _scan,
    accentuate,
    detect_meter,
    split_stanzas,
)

GARCILASO = """Cuando me paro a contemplar mi estado
y a ver los pasos por do me han traído,
hallo, según por do anduve perdido,
que a mayor mal pudiera haber llegado."""
SONATINA = """La princesa está triste... ¿qué tendrá la princesa?
Los suspiros se escapan de su boca de fresa,
que ha perdido la risa, que ha perdido el color.
La princesa está pálida en su silla de oro,
está mudo el teclado de su clave sonoro,
y en un vaso olvidada se desmaya una flor."""
ROMANCE = """Que por mayo era, por mayo,
cuando hace la calor,
cuando los trigos encañan
y están los campos en flor,"""
SONNETS_ARCHIVE = Path(__file__).parents[1] / "ests" / "datasets" / "data" / sonnets_module.ARCHIVE


def scan(text, length=None):
    """Syllables, stresses, length and tail of a line, fitted to a length if one is given"""
    _, units, bounds = _parse_line(text)
    return _fit(units, bounds, length) if length else _scan(units, _default_joins(bounds))


def nfc(text):
    return unicodedata.normalize("NFC", text)


@pytest.fixture(scope="module")
def sonnets(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_data")
    shutil.copy(SONNETS_ARCHIVE, path / sonnets_module.ARCHIVE)
    dataset = SpanishSonnets(data_dir=path)
    # The archive is in the repository next to the code, the network is not needed
    dataset.download()
    return dataset


@pytest.mark.parametrize("source", ["", "¿? ...", "1810"])
def test_init_source_error(source):
    with pytest.raises(SourceError):
        VerseStats(source)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(SourceTypeError):
        VerseStats(source)


def test_no_spanish_syllables():
    vs = VerseStats("цвет и свет")
    assert (vs.n_lines, vs.n_stanzas, vs.meter, vs.n_feet) == (0, 0, None, None)
    assert vs.lines == vs.patterns == vs.stress_profile == ()
    assert vs.c_feet == vs.c_rhythms == vs.c_clausulas == vs.c_stressed_vowels == {}
    for stat in ("p_deviations", "p_pyrrhics", "p_masculine", "mean_line_len"):
        assert isnan(getattr(vs, stat))


def test_endecasyllables():
    vs = VerseStats(GARCILASO)
    assert (vs.n_lines, vs.n_stanzas, vs.meter, vs.n_feet) == (4, 1, "endecasílabo", 11)
    assert (vs.p_deviations, vs.p_pyrrhics) == (0.0, 0.0)
    assert vs.c_feet == {11: 4}
    assert vs.mean_line_len == 11.0
    assert vs.syllables[0] == (
        "cuan", "do", "me", "pa", "ro‿a", "con", "tem", "plar", "mi‿es", "ta", "do"
    )  # fmt: skip
    # cuando and me are unstressed: 4-8-10
    assert vs.stresses[0] == (3, 7, 9)
    assert vs.patterns == ("---+---+-+-", "-+-+---+-+-", "+--+--+--+-", "--++-+-+-+-")
    assert vs.c_rhythms == {"4-8-10": 2, "4-7-10": 1, "3-6-10": 1}
    assert vs.stress_profile[9] == 1.0
    assert vs.stress_profile[10] == 0.0
    assert vs.stress_profile[3] == 1.0
    assert vs.stress_profile[5] == 0.25
    assert vs.c_clausulas == {"llana": 4}
    assert (vs.p_masculine, vs.p_feminine, vs.p_dactylic) == (0.0, 1.0, 0.0)
    assert vs.c_stressed_vowels == {"a": 8, "e": 3, "i": 2, "u": 2, "o": 1}


def test_alexandrines():
    vs = VerseStats(SONATINA)
    assert (vs.meter, vs.n_feet, vs.p_deviations, vs.p_pyrrhics) == ("alejandrino", 14, 0.0, 0.0)
    assert vs.c_feet == {14: 6}
    # An aguda at the end of a hemistich adds a syllable: que ha perdido el color is 6 + 1
    assert vs.syllables[2][7:] == ("que‿ha", "per", "di", "do‿el", "co", "lor")
    # An esdrújula takes one off, and the caesura blocks the synalepha: pálida | en
    assert vs.syllables[3] == (
        "la", "prin", "ce", "sa‿es", "tá", "pá", "li", "da", "en", "su", "si", "lla", "de", "o", "ro"
    )  # fmt: skip
    assert vs.patterns[3] == "--+-++---+--+-"
    # The last syllables of the hemistichs are always stressed
    assert vs.stress_profile[5] == vs.stress_profile[12] == 1.0
    assert vs.c_clausulas == {"aguda": 2, "llana": 4}
    assert vs.c_rhythms == {}


def test_octosyllables():
    vs = VerseStats(ROMANCE)
    assert (vs.meter, vs.n_feet, vs.p_deviations, vs.p_pyrrhics) == ("octosílabo", 8, 0.0, 0.0)
    # The synalepha cuando‿hace is broken to reach 8 syllables
    assert vs.syllables[1] == ("cuan", "do", "ha", "ce", "la", "ca", "lor")
    assert vs.c_clausulas == {"aguda": 2, "llana": 2}
    assert vs.p_masculine == 0.5


@pytest.mark.parametrize(
    ("text", "syllables"),
    [
        # a silent h lets the synalepha through, hi and hu before a vowel are consonants
        ("oh alma mía", ("oh‿al", "ma", "mí", "a")),
        ("hierba y hueso", ("hier", "ba‿y", "hue", "so")),
        ("la hierba", ("la", "hier", "ba")),
        # y before a vowel is a consonant, the conjunction y joins both neighbours
        ("mira ya", ("mi", "ra", "ya")),
        ("tierra y agua", ("tie", "rra‿y‿a", "gua")),
        # no synalepha after a consonant
        ("el alma", ("el", "al", "ma")),
    ],
)
def test_synalepha(text, syllables):
    assert scan(text).syllables == syllables


@pytest.mark.parametrize(
    ("text", "length", "syllables"),
    [
        # a dieresis splits the diphthong of a stressed syllable
        (
            "Hacer con un rocín mucho ruido",
            11,
            ("ha", "cer", "con", "un", "ro", "cín", "mu", "cho", "ru", "i", "do"),
        ),
        ("vuestra suave musa", 7, ("vues", "tra", "su", "a", "ve", "mu", "sa")),
        # a synaeresis joins the hiatus of a word
        ("el poeta cantaba", 6, ("el", "poe", "ta", "can", "ta", "ba")),
        # a synalepha is broken from the end of the line
        ("cuando hace la calor", 8, ("cuan", "do", "ha", "ce", "la", "ca", "lor")),
        ("que a mí me mira a veces", 8, ("que‿a", "mí", "me", "mi", "ra", "a", "ve", "ces")),
        # the silent u of que is no vowel to split
        ("que quiero", 4, ("que", "quie", "ro")),
        # a length out of reach leaves the plain reading
        ("el perro ladra", 10, ("el", "pe", "rro", "la", "dra")),
        ("que a mí me mira a veces", 12, ("que‿a", "mí", "me", "mi", "ra‿a", "ve", "ces")),
        ("el poeta cantaba", 4, ("el", "po", "e", "ta", "can", "ta", "ba")),
    ],
)
def test_fit(text, length, syllables):
    assert scan(text, length).syllables == syllables


@pytest.mark.parametrize(
    ("text", "length", "tail"),
    [
        # the law of the final stress: a line counts up to its last stress and one more
        ("la calor", 4, 0),
        ("el árbol", 3, 1),
        ("el pájaro", 3, 2),
        ("dígamelo", 2, 3),
        # the last word is always stressed, an unstressed word inside is not
        ("dime que", 4, 0),
        ("la casa de mi padre", 7, 1),
    ],
)
def test_final_stress(text, length, tail):
    scansion = scan(text)
    assert (scansion.length, scansion.tail) == (length, tail)


def test_unstressed_words():
    assert scan("la casa de mi padre").stresses == (1, 5)
    assert scan("fácilmente").stresses == (0, 2)


def test_no_meter():
    polymetric = "Cuando me paro a contemplar mi estado\nla luz del día\nque a mayor mal pudiera haber llegado\nen la ventana"
    vs = VerseStats(polymetric)
    assert (vs.meter, vs.n_feet) == (None, None)
    assert isnan(vs.p_deviations)
    assert isnan(vs.p_pyrrhics)
    assert vs.stress_profile == ()
    assert vs.c_feet == {5: 2, 11: 2}
    # the lines of 11 syllables still have their types
    assert sum(vs.c_rhythms.values()) == 2
    # a single line has no meter
    assert VerseStats("Cuando me paro a contemplar mi estado").meter is None


def test_pyrrhics():
    vs = VerseStats("Cuando me paro a contemplar mi estado\nsólo el serviros de encarecimiento")
    assert vs.meter == "endecasílabo"
    assert vs.patterns[1] == "+--+-----+-"
    assert vs.p_pyrrhics == 0.5
    assert vs.c_rhythms == {"4-8-10": 1}


@pytest.mark.parametrize(
    ("stresses", "rhythm"),
    [
        ((0, 5, 9), "1-6-10"),
        ((1, 5, 9), "2-6-10"),
        ((2, 5, 9), "3-6-10"),
        ((3, 5, 9), "4-6-10"),
        ((5, 9), "6-10"),
        ((1, 3, 7, 9), "4-8-10"),
        ((3, 6, 9), "4-7-10"),
        ((0, 4, 9), None),
    ],
)
def test_endecasyllable_type(stresses, rhythm):
    assert _endecasyllable_type(stresses) == rhythm


def test_stanzas():
    vs = VerseStats(GARCILASO + "\n\n\n" + ROMANCE)
    assert vs.n_stanzas == 2
    assert vs.stanzas[1][0] == "Que por mayo era, por mayo,"
    assert vs.accentuate().count("\n\n") == 1


def test_accentuate():
    assert nfc(VerseStats(GARCILASO).accentuate()).split("\n")[0] == (
        "Cuando me páro a contemplár mi estádo"
    )
    # the marks are combining characters apart from the written accents
    assert VerseStats(GARCILASO).accentuate().count("\u0301") == 14
    text = "El gato duerme tranquilamente en la ventana, muy teórico-práctico"
    assert nfc(accentuate(text)) == (
        "El gáto duérme tranquílaménte en la ventána, muý teórico-práctico"
    )
    assert nfc(accentuate("quiso la guerra, cuida la ley")) == "quíso la guérra, cuída la léy"


def test_split_stanzas():
    assert split_stanzas("uno dos\n\n\n  tres  \n1810\n***\nцвет\ncuatro") == [
        ["uno dos"],
        ["tres", "cuatro"],
    ]


def test_detect_meter():
    assert detect_meter(GARCILASO) == "endecasílabo"
    assert detect_meter(SONATINA) == "alejandrino"


def test_doc():
    doc = spacy.blank("es")(ROMANCE)
    assert VerseStats(doc).get_stats() == VerseStats(ROMANCE).get_stats()


def test_get_stats():
    vs = VerseStats(GARCILASO)
    stats = vs.get_stats()
    assert list(stats) == list(VERSE_STATS_DESC)
    assert stats["meter"] == "endecasílabo"


def test_print_stats(capsys):
    VerseStats(GARCILASO).print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(VERSE_STATS_DESC) + 1
    assert "endecasílabo" in captured.out


def test_sonnets(sonnets):
    # The scansion agrees with the automatic one of DISCO on the length of the lines
    # and on the stresses of the metrical syllables
    meters = Counter()
    lengths = syllables = agreed = 0
    n_lines = 0
    for record in sonnets:
        vs = VerseStats(record["text"])
        meters[vs.meter] += 1
        assert vs.n_lines == len(record["meter"])
        for pattern, reference in zip(vs.patterns, record["meter"], strict=True):
            n_lines += 1
            if len(pattern) == len(reference):
                lengths += 1
                syllables += len(reference)
                agreed += sum(a == b for a, b in zip(pattern, reference, strict=True))
    assert n_lines == 60209
    assert lengths / n_lines > 0.965
    assert agreed / syllables > 0.97
    assert meters["endecasílabo"] > 3850
    assert meters["alejandrino"] > 310
    assert meters[None] < 30
