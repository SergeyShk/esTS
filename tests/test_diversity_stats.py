from math import e, isnan, log10

import pytest
import spacy
from anyts.constants import DIVERSITY_STATS_DESC

from ests import DiversityStats, WordsExtractor
from ests.diversity_stats import (
    WindowStats,
    calc_dugast_k,
    calc_mattr,
    calc_msttr,
    calc_mtld,
    calc_mttr,
)
from ests.exceptions import ParameterError, SourceError, SourceTypeError

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
RIDDLE_TEXT = (
    "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse,"
    " cuándo empezar labores"
)
# 15 words, 11 lexemes, frequency spectrum {1: 8, 2: 2, 3: 1}
riddle = (
    "pies", "no", "tengo", "ando", "boca", "no", "tengo", "hablo",
    "cuándo", "dormir", "cuándo", "levantarse", "cuándo", "empezar", "labores",
)  # fmt: skip


@pytest.fixture(scope="module")
def ds():
    return DiversityStats(TEXT)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"window_len": 0},
        {"mtld_threshold": 0},
        {"mtld_threshold": 1},
        {"mtld_min_len": -1},
        {"hdd_sample_size": 0},
        {"log_base": 1},
    ],
)
def test_init_params_error(kwargs):
    with pytest.raises(ParameterError):
        DiversityStats(TEXT, **kwargs)


def test_init_params():
    ds = DiversityStats(TEXT, window_len=20, mtld_threshold=0.9, mtld_min_len=5, log_base=e)
    assert ds.mattr == pytest.approx(calc_mattr(ds.words, 20))
    assert ds.msttr == pytest.approx(calc_msttr(ds.words, 20))
    assert ds.mtld == pytest.approx(calc_mtld(ds.words, 5, 0.9))
    assert ds.mttr == pytest.approx(calc_mttr(ds.words, e))
    assert ds.mttr != pytest.approx(calc_mttr(ds.words))
    assert ds.dugast_k == pytest.approx(calc_dugast_k(ds.words, e))


def test_init_value_error():
    with pytest.raises(SourceError):
        DiversityStats("+ _")


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(SourceTypeError):
        DiversityStats(text)


def test_init_doc_lowercase():
    doc = spacy.blank("es")(RIDDLE_TEXT)
    assert DiversityStats(doc).words == DiversityStats(RIDDLE_TEXT).words == riddle
    assert DiversityStats(doc).ttr == DiversityStats(RIDDLE_TEXT).ttr


def test_init_byte_order_mark():
    """The words of a string and of its Doc are the same with a byte order mark"""
    text = "\ufeff" + RIDDLE_TEXT
    assert DiversityStats(text).words == DiversityStats(spacy.blank("es")(text)).words == riddle


def test_init_extractor_lowercase():
    """Words are lower-cased whatever the extractor, so the metrics stay case-insensitive"""
    text = "Los tesauros son una clase especial. Los TESAUROS son Una clase."
    default = DiversityStats(text)
    custom = DiversityStats(text, WordsExtractor())
    assert custom.words == default.words
    assert custom.ttr == default.ttr == pytest.approx(6 / 11)


def test_init_doc_with_extractor():
    """A given extractor is applied to the text of a Doc instead of its tokens"""
    doc = spacy.blank("es")(RIDDLE_TEXT)
    extractor = WordsExtractor(stopwords=["no", "cuándo"])
    assert DiversityStats(doc, extractor).words == DiversityStats(RIDDLE_TEXT, extractor).words
    assert "no" not in DiversityStats(doc, extractor).words


def test_init_params_checked_first():
    with pytest.raises(ParameterError):
        DiversityStats("+ _", window_len=0)


def test_custom_words_extractor():
    extractor = WordsExtractor(lowercase=True, stopwords=["no", "cuándo"])
    ds = DiversityStats(RIDDLE_TEXT, words_extractor=extractor)
    assert ds.words == tuple(word for word in riddle if word not in ("no", "cuándo"))
    assert ds.ttr == pytest.approx(9 / 10)


def test_words(ds):
    assert len(ds.words) == 94
    assert len(set(ds.words)) == 55
    assert ds.frequency_spectrum == {1: 39, 2: 10, 3: 2, 5: 2, 9: 1, 10: 1}


def test_values(ds):
    assert ds.ttr == pytest.approx(55 / 94)
    assert ds.sttr == pytest.approx(log10(log10(55)) / log10(log10(94)))
    assert ds.mattr == pytest.approx(0.6471111111111114)
    assert ds.msttr == pytest.approx(0.66)
    assert ds.mtld == pytest.approx(35.123446561723284)
    assert ds.mamtld == pytest.approx(30.059322033898304)
    assert ds.mtldw == pytest.approx(37.712765957446805)
    assert ds.heaps_beta == pytest.approx(0.8180436061700801)


def test_single_word_nan():
    ds = DiversityStats("palabra")
    for stat in ("simpson_index", "inverse_simpson_index", "gini_simpson_index", "hapax_index"):
        assert isnan(getattr(ds, stat))


def test_windowed_riddle():
    ds = DiversityStats(RIDDLE_TEXT)
    stats = ds.windowed("ttr", window_len=5)
    assert stats == WindowStats(
        pytest.approx(0.9333333333333332),
        pytest.approx(0.11547005383792512),
        pytest.approx(0.6464898180167025),
        pytest.approx(1.220176848649964),
        3,
    )
    assert ds.windowed("ttr", window_len=5, step=2).n_windows == 6


def test_get_stats(ds):
    stats = ds.get_stats()
    assert list(stats) == list(DIVERSITY_STATS_DESC)
    for key in DIVERSITY_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ds, key), nan_ok=True)


def test_print_stats(capsys, ds):
    ds.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(DIVERSITY_STATS_DESC) + 1
    assert "Yule's characteristic K" in captured.out
