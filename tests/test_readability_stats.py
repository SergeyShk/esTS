from math import isnan

import pytest
import spacy

from ests import BasicStats, ReadabilityStats, SentsExtractor
from ests.constants import (
    READABILITY_GRADE_STATS,
    READABILITY_PRESETS,
    READABILITY_STATS_DESC,
    READING_SPEED_NORMS,
)
from ests.readability_stats import (
    calc_consensus_grade,
    calc_crawford_grade,
    calc_flesch_reading_easy,
    calc_gutierrez_polini_index,
    calc_lix,
    calc_mu_index,
    calc_reading_time,
    calc_rix,
    calc_smog_index,
    calc_sol_grade,
    flesch_reading_easy_to_grade,
    flesch_reading_easy_to_level,
    grade_to_age,
    mu_to_level,
)

TEXT = (
    "Los tesauros son una clase especial de recursos lexicográficos que se caracterizan por"
    " los siguientes rasgos: la completitud de los significados del vocabulario de una lengua"
    " o de alguno de sus segmentos; la ordenación temática, o ideográfica, de los significados"
    " de las palabras. La diferencia entre los tesauros y las ontologías formales consiste en"
    " la salida hacia la esfera de los significados léxicos, en el establecimiento de"
    " relaciones no solo entre los significados y las palabras que los expresan, sino también"
    " entre los propios significados (el registro de diversas relaciones semánticas dentro del"
    " diccionario)."
)
QUOTE = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"


@pytest.fixture(scope="module")
def rs():
    return ReadabilityStats(TEXT)


@pytest.fixture(scope="module")
def quote():
    return ReadabilityStats(QUOTE)


def test_init_value_error():
    with pytest.raises(ValueError):
        ReadabilityStats("+ _")


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        ReadabilityStats(text)


def test_init_no_sents_error():
    with pytest.raises(ValueError, match="sentences"):
        ReadabilityStats("Un texto. Otro texto.", sents_extractor=SentsExtractor(min_len=1000))


def test_init_preset_error():
    with pytest.raises(ValueError):
        ReadabilityStats(TEXT, preset="unknown")


def test_init_basic_stats(rs):
    basic = BasicStats(TEXT)
    from_basic = ReadabilityStats(basic, preset="classic")
    assert from_basic.bs is basic
    assert from_basic.preset == "classic"
    assert ReadabilityStats(basic).get_stats() == rs.get_stats()


def test_init_doc(rs):
    doc = spacy.blank("es")(TEXT)
    assert ReadabilityStats(doc).get_stats() == rs.get_stats()


def test_default_preset(rs):
    assert rs.preset == "general"
    assert rs.coefficients == READABILITY_PRESETS["general"]


def test_coefficients_copy():
    rs = ReadabilityStats(TEXT)
    rs.coefficients["flesch_reading_easy"] = (1.02, 60.0, 206.84)
    assert rs.flesch_reading_easy == pytest.approx(22.942553191489367)
    assert READABILITY_PRESETS["general"]["flesch_reading_easy"] == (1.0, 62.3, 206.835)
    assert ReadabilityStats(TEXT).flesch_reading_easy == pytest.approx(18.66585106382979)


@pytest.mark.parametrize(
    ("preset", "flesch_reading_easy"),
    [("general", 18.66585106382979), ("classic", 22.942553191489367)],
)
def test_presets(preset, flesch_reading_easy):
    rs = ReadabilityStats(TEXT, preset=preset)
    assert rs.flesch_reading_easy == pytest.approx(flesch_reading_easy)
    assert rs.crawford_grade == pytest.approx(7.260021276595744)


class TestQuoteByHand:
    """The docstring example: 10 words, 1 sentence, 23 syllables, 60 letters, 5 words of
    three or more syllables and 5 words of seven or more letters, checked by hand"""

    def test_flesch_reading_easy(self, quote):
        assert quote.flesch_reading_easy == pytest.approx(206.835 - 62.3 * 2.3 - 10)
        assert ReadabilityStats(QUOTE, preset="classic").flesch_reading_easy == pytest.approx(
            206.84 - 60 * 2.3 - 1.02 * 10
        )

    def test_gutierrez_polini_index(self, quote):
        assert quote.gutierrez_polini_index == pytest.approx(95.2 - 9.7 * 6 - 0.35 * 10)

    def test_crawford_grade(self, quote):
        assert quote.crawford_grade == pytest.approx(-0.205 * 10 + 0.049 * 230 - 3.407)

    def test_mu_index(self, quote):
        # letters per word 3, 4, 6, 2, 8, 8, 8, 8, 1, 12: mean 6, population variance 10.6
        assert quote.mu_index == pytest.approx(10 / 9 * 6 / 10.6 * 100)

    def test_sol_grade(self, quote):
        smog = 1.043 * (5 * 30) ** 0.5 + 3.1291
        assert quote.sol_grade == pytest.approx(-2.51 + 0.74 * smog)

    def test_lix_rix(self, quote):
        assert quote.lix == 60.0
        assert quote.rix == 5.0

    def test_consensus_grade(self, quote):
        # Crawford 5.8 -> 6, SOL 9.3 -> 9, reading ease 53.5 -> 11: median 9
        assert quote.consensus_grade == 9.0

    def test_reading_time(self, quote):
        assert quote.reading_time == pytest.approx(10 / 278)

    def test_descriptions(self, quote):
        assert quote.describe_level() == "algo difícil"
        assert quote.describe_level(scale="szigriszt") == "normal"
        assert quote.describe_level("mu_index") == "adecuado"
        assert quote.describe_grade() == "ESO (12-16 years)"
        assert quote.describe_grade("crawford_grade") == "primary school, grades 4-6 (9-12 years)"


def test_flesch_reading_easy(rs):
    assert rs.flesch_reading_easy == pytest.approx(18.66585106382979)
    assert calc_flesch_reading_easy(23, 10, 1) == pytest.approx(53.545)
    assert calc_flesch_reading_easy(23, 10, 1, 1.02, 60, 206.84) == pytest.approx(58.64)


def test_gutierrez_polini_index(rs):
    assert rs.gutierrez_polini_index == pytest.approx(25.193617021276605)
    assert calc_gutierrez_polini_index(60, 10, 1) == pytest.approx(33.5)


def test_crawford_grade(rs):
    assert rs.crawford_grade == pytest.approx(7.260021276595744)
    assert calc_crawford_grade(23, 10, 1) == pytest.approx(5.813)
    assert calc_crawford_grade(150, 100, 5) == pytest.approx(-0.205 * 5 + 0.049 * 150 - 3.407)


def test_mu_index(rs):
    assert rs.mu_index == pytest.approx(41.984674748325894)
    # the example of the authors' manual: 18 words, mean 6.9444, variance 13.5844
    assert pytest.approx(54.13, abs=0.01) == 18 / 17 * 6.9444 / 13.5844 * 100
    assert calc_mu_index({3: 5, 5: 5}) == pytest.approx(10 / 9 * 4 / 1 * 100)
    assert calc_mu_index({0: 4, 3: 5, 5: 5}) == calc_mu_index({3: 5, 5: 5})
    assert isnan(calc_mu_index({3: 1}))
    assert isnan(calc_mu_index({3: 5}))
    assert isnan(calc_mu_index({}))


def test_sol_grade(rs):
    assert rs.sol_grade == pytest.approx(17.74101003761885)
    assert calc_smog_index(0, 1) == pytest.approx(3.1291)
    assert calc_smog_index(30, 30) == pytest.approx(1.043 * 30**0.5 + 3.1291)
    # Table 5 of Contreras et al. (1999): SMOG 15 in Spanish is grade 8.59, 25 is 15.99
    assert pytest.approx(8.59) == -2.51 + 0.74 * 15
    assert pytest.approx(15.99) == -2.51 + 0.74 * 25
    assert calc_sol_grade(5, 1) == pytest.approx(-2.51 + 0.74 * calc_smog_index(5, 1))


def test_lix(rs):
    assert rs.lix == pytest.approx(84.23404255319149)
    assert calc_lix(5, 10, 1) == 60.0


def test_rix(rs):
    assert rs.rix == pytest.approx(17.5)
    assert calc_rix(2, 1) == 2.0


def test_consensus_grade(rs):
    assert rs.consensus_grade == 13.0
    grades = [getattr(rs, stat) for stat in READABILITY_GRADE_STATS]
    assert rs.consensus_grade == calc_consensus_grade(grades, rs.flesch_reading_easy)


def test_calc_consensus_grade():
    assert calc_consensus_grade([5.813, 9.258], 53.545) == 9.0
    assert calc_consensus_grade([2.5, 2.5, 3.4]) == 3.0
    assert calc_consensus_grade([7.0]) == 7.0
    assert calc_consensus_grade([], 60) == 8.0
    assert calc_consensus_grade([8, 8, 9, 9], 60) == 8.0
    assert calc_consensus_grade([8.5]) == 9.0
    with pytest.raises(ValueError):
        calc_consensus_grade([])


@pytest.mark.parametrize(
    ("flesch_reading_easy", "grade"),
    [
        (120, 3),
        (80, 3),
        (79.9, 5),
        (65, 5),
        (60, 8),
        (55, 8),
        (54.9, 11),
        (40, 11),
        (39.9, 13),
        (-50, 13),
    ],
)
def test_flesch_reading_easy_to_grade(flesch_reading_easy, grade):
    assert flesch_reading_easy_to_grade(flesch_reading_easy) == grade


@pytest.mark.parametrize(
    ("value", "scale", "level"),
    [
        (95, "inflesz", "muy fácil"),
        (80, "inflesz", "muy fácil"),
        (79.9, "inflesz", "bastante fácil"),
        (65, "inflesz", "bastante fácil"),
        (60, "inflesz", "normal"),
        (55, "inflesz", "normal"),
        (54.9, "inflesz", "algo difícil"),
        (40, "inflesz", "algo difícil"),
        (39.9, "inflesz", "muy difícil"),
        (-10, "inflesz", "muy difícil"),
        (90, "szigriszt", "muy fácil"),
        (80, "szigriszt", "fácil"),
        (70, "szigriszt", "bastante fácil"),
        (60, "szigriszt", "normal"),
        (40, "szigriszt", "bastante difícil"),
        (20, "szigriszt", "árido"),
        (10, "szigriszt", "muy difícil"),
        (95, "fernandez_huerta", "muy fácil"),
        (85, "fernandez_huerta", "fácil"),
        (75, "fernandez_huerta", "bastante fácil"),
        (65, "fernandez_huerta", "normal"),
        (55, "fernandez_huerta", "bastante difícil"),
        (40, "fernandez_huerta", "difícil"),
        (29.9, "fernandez_huerta", "muy difícil"),
    ],
)
def test_flesch_reading_easy_to_level(value, scale, level):
    assert flesch_reading_easy_to_level(value, scale) == level


def test_flesch_reading_easy_to_level_error():
    with pytest.raises(ValueError):
        flesch_reading_easy_to_level(50, "unknown")


@pytest.mark.parametrize(
    ("value", "level"),
    [
        (100, "muy fácil"),
        (91, "muy fácil"),
        (90.9, "fácil"),
        (81, "fácil"),
        (75, "un poco fácil"),
        (65, "adecuado"),
        (55, "un poco difícil"),
        (40, "difícil"),
        (30, "muy difícil"),
        (0, "muy difícil"),
        (533.3, "muy fácil"),
        (float("nan"), ""),
    ],
)
def test_mu_to_level(value, level):
    assert mu_to_level(value) == level


@pytest.mark.parametrize(
    ("grade", "expected"),
    [
        (-3, "primary school, grades 1-3 (6-9 years)"),
        (0.4, "primary school, grades 1-3 (6-9 years)"),
        (3.5, "primary school, grades 4-6 (9-12 years)"),
        (6.49, "primary school, grades 4-6 (9-12 years)"),
        (8, "ESO (12-16 years)"),
        (10.4, "ESO (12-16 years)"),
        (10.5, "bachillerato (16-18 years)"),
        (12, "bachillerato (16-18 years)"),
        (14, "university (18-22 years)"),
        (16.4, "university (18-22 years)"),
        (16.5, "postgraduate (over 22 years)"),
        (40, "postgraduate (over 22 years)"),
    ],
)
def test_grade_to_age(grade, expected):
    assert grade_to_age(grade) == expected


def test_describe_grade(rs):
    assert rs.describe_grade() == grade_to_age(rs.consensus_grade)
    assert rs.describe_grade("sol_grade") == grade_to_age(rs.sol_grade)
    assert ReadabilityStats("Mi mamá me mima.").describe_grade() == (
        "primary school, grades 1-3 (6-9 years)"
    )
    with pytest.raises(ValueError):
        rs.describe_grade("lix")


def test_describe_level(rs):
    assert rs.describe_level() == "muy difícil"
    assert rs.describe_level(scale="szigriszt") == "árido"
    assert rs.describe_level(scale="fernandez_huerta") == "muy difícil"
    assert rs.describe_level("mu_index") == "difícil"
    with pytest.raises(ValueError):
        rs.describe_level("lix")
    with pytest.raises(ValueError):
        rs.describe_level(scale="unknown")


def test_reading_time(rs):
    assert rs.reading_time == pytest.approx(94 / 278)
    assert calc_reading_time(278, 139) == 2.0
    with pytest.raises(ValueError):
        calc_reading_time(100, 0)


def test_reading_time_by_speed(rs):
    assert rs.reading_time_by_speed(278) == rs.reading_time
    assert rs.reading_time_by_speed(94) == 1.0
    with pytest.raises(ValueError):
        rs.reading_time_by_speed(-1)


def test_reading_time_by_norm(rs):
    aloud, silent = rs.reading_time_by_norm("grade_4")
    assert (aloud, silent) == (pytest.approx(94 / 104), pytest.approx(94 / 125))
    assert rs.reading_time_by_norm("adult")[1] == rs.reading_time
    assert rs.reading_time_by_norm("grade_1")[0] < rs.reading_time_by_norm("grade_1")[1]
    assert list(READING_SPEED_NORMS) == [f"grade_{i}" for i in range(1, 12)] + ["adult"]
    with pytest.raises(ValueError):
        rs.reading_time_by_norm("grade_12")


def test_get_stats(rs):
    stats = rs.get_stats()
    assert isinstance(stats, dict)
    assert list(stats) == list(READABILITY_STATS_DESC)
    for key in READABILITY_STATS_DESC:
        assert stats[key] == getattr(rs, key)


def test_print_stats(capsys, rs):
    rs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(READABILITY_STATS_DESC) + 1
    assert "Legibilidad µ" in captured.out
