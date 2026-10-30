from math import isnan

import anyts.basic_stats
import pytest
import spacy
from anyts.constants import UNADAPTED_READABILITY_STATS_DESC

from ests import BasicStats, ReadabilityStats, UnadaptedReadabilityStats
from ests.exceptions import SourceError, SourceTypeError
from ests.unadapted_readability_stats import (
    calc_fucks,
    calc_gulpease,
    calc_strain_index,
    calc_wheeler_smith,
)

text = (
    "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse,"
    " cuándo empezar labores"
)


@pytest.fixture(scope="module")
def urs():
    return UnadaptedReadabilityStats(text)


def test_spanish_syllables(urs):
    """The formulas read the Spanish syllables and letters of the BasicStats of esTS"""
    bs = urs.bs
    assert isinstance(bs, BasicStats)
    assert urs.fucks == calc_fucks(bs.n_syllables, bs.n_sents)
    assert urs.strain_index == calc_strain_index(bs.n_syllables, bs.n_sents)
    assert urs.wheeler_smith == calc_wheeler_smith(bs.n_polysyllable_words, bs.n_sents)
    assert urs.gulpease == calc_gulpease(bs.n_letters, bs.n_words, bs.n_sents)
    # The syllables of count_syllables: pies is one, a diphthong
    assert bs.n_syllables == 31


def test_sources(urs):
    """A string, a Doc and ready basic statistics give the same formulas"""
    stats = urs.get_stats()
    assert list(stats) == list(UNADAPTED_READABILITY_STATS_DESC)
    assert UnadaptedReadabilityStats(BasicStats(text)).get_stats() == stats
    assert UnadaptedReadabilityStats(spacy.blank("es")(text)).get_stats() == stats


def test_no_scales_and_no_grade(urs):
    """No calibration for Spanish: no reading and no part of the consensus grade"""
    assert all(urs.describe(stat) is None for stat in UNADAPTED_READABILITY_STATS_DESC)
    assert not set(UNADAPTED_READABILITY_STATS_DESC) & set(ReadabilityStats.grade_stats)


def test_print_stats(urs, capsys):
    urs.print_stats()
    out = capsys.readouterr().out
    assert all(desc in out for desc in UNADAPTED_READABILITY_STATS_DESC.values())


def test_errors():
    with pytest.raises(SourceTypeError, match=r"^The data source cannot be of type int$"):
        UnadaptedReadabilityStats(5)
    with pytest.raises(SourceError, match=r"^The data source has no words$"):
        UnadaptedReadabilityStats("?!")

    class Basic(anyts.basic_stats.BasicStats):
        def count_syllables(self, word):
            return 1

    # The basic statistics of the core, without the Spanish syllables
    with pytest.raises(SourceTypeError, match="BasicStats"):
        UnadaptedReadabilityStats(Basic(text))
    assert not isnan(UnadaptedReadabilityStats("Gato.").forcast)
