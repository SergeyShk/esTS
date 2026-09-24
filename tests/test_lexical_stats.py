from math import isnan, log2, log10

import pytest
import spacy

from ests import LexicalStats
from ests.constants import FREQUENCY_BANDS, LEXICAL_STATS_DESC
from ests.datasets import FreqDict
from ests.exceptions import DatasetNotFoundError, SourceError, SourceTypeError
from ests.lexical_stats import calc_surprisal, get_rank, is_number, load_top_lemmas
from ests.utils import get_nlp

TEXT = "El gato estaba en la ventana y miraba a los pájaros"
LEMMAS = ("el", "gato", "estar", "en", "el", "ventana", "y", "mirar", "a", "el", "pájaro")
CONTENT = ("gato", "estar", "ventana", "mirar", "pájaro")


@pytest.fixture(scope="module")
def ls(freq_dict):
    return LexicalStats(TEXT, freq_dict=freq_dict)


def test_words_and_lemmas(ls):
    assert ls.words == tuple(TEXT.split())
    assert ls.lemmas == LEMMAS
    assert ls.n_words == 11
    assert ls.n_content_words == 5
    assert ls.lexical_density == pytest.approx(5 / 11)
    assert ls.ranks == tuple(get_rank(lemma) for lemma in LEMMAS)
    assert ls.ranks[:2] == (1, 2851)


def test_frequency(ls, freq_dict):
    entries = [freq_dict.lookup(lemma) for lemma in LEMMAS]
    content = [freq_dict.lookup(lemma) for lemma in CONTENT]
    assert ls.entries == tuple(entries)
    assert ls.n_found == 11
    assert ls.coverage == 1.0
    assert ls.mean_ipm == pytest.approx(sum(e.ipm for e in entries) / 11)
    assert ls.mean_ipm_content == pytest.approx(sum(e.ipm for e in content) / 5)
    assert ls.mean_log_ipm == pytest.approx(sum(log10(e.ipm) for e in entries) / 11)
    assert ls.mean_log_ipm_content == pytest.approx(sum(log10(e.ipm) for e in content) / 5)
    assert ls.mean_range == 40.0
    assert ls.mean_dispersion == pytest.approx(sum(e.dispersion for e in entries) / 11)


def test_surprisal(ls, freq_dict):
    expected = sum(-log2(freq_dict.ipm(lemma) / 1_000_000) for lemma in LEMMAS) / 11
    assert ls.surprisal == pytest.approx(expected)
    assert ls.perplexity == pytest.approx(2**expected)
    assert calc_surprisal(["gato"], freq_dict) == pytest.approx(-log2(29.08 / 1_000_000))
    floor = freq_dict.min_ipm
    assert calc_surprisal(["gatx"], freq_dict) == pytest.approx(-log2(floor / 1_000_000))
    assert isnan(calc_surprisal([], freq_dict))


def test_rare_words(freq_dict):
    ls = LexicalStats("El felinólogo examinaba al minino con gatófila parsimonia", freq_dict)
    assert ls.coverage < 1
    assert ls.entries[ls.words.index("gatófila")] is None
    assert ls.p_beyond_top10000 > 0
    common = LexicalStats(TEXT, freq_dict)
    assert ls.surprisal > common.surprisal
    assert ls.mean_log_ipm_content < common.mean_log_ipm_content


def test_proper_nouns(freq_dict):
    ls = LexicalStats("París es la capital de Francia y Ana vive allí", freq_dict)
    assert ls.lemmas[0] == "parís"
    assert ls.entries[0].pos == ("PROPN",)
    assert ls.lemmas[5] == "francia"
    assert ls.n_content_words == 6


def test_numbers_are_no_words(freq_dict):
    ls = LexicalStats("En 2020 hubo 3 gatos y 1,5 perros", freq_dict)
    assert ls.words == ("En", "hubo", "gatos", "y", "perros")
    assert ls.coverage == 1.0
    with pytest.raises(SourceError):
        LexicalStats("2020, 3.º, 1,5", freq_dict)


@pytest.mark.parametrize(
    ("word", "expected"), [("2020", True), ("1,5", True), ("3.º", True), ("gato", False)]
)
def test_is_number(word, expected):
    assert is_number(word) is expected


def test_doc_source(ls, freq_dict):
    doc = get_nlp()(TEXT)
    assert LexicalStats(doc, freq_dict).get_stats() == ls.get_stats()


def test_nlp_is_used(freq_dict):
    pipeline = spacy.load("es_core_news_sm")
    pipeline.max_length = 5
    with pytest.raises(SourceError, match="longer than the limit"):
        LexicalStats(TEXT, freq_dict, nlp=pipeline)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_type_error(source, freq_dict):
    with pytest.raises(SourceTypeError):
        LexicalStats(source, freq_dict)


@pytest.mark.parametrize("source", ["", "   ", "¿?", "+ _"])
def test_no_words(source, freq_dict):
    with pytest.raises(SourceError):
        LexicalStats(source, freq_dict)


def test_doc_without_parts_of_speech(freq_dict):
    with pytest.raises(SourceError, match="parts of speech"):
        LexicalStats(spacy.blank("es")(TEXT), freq_dict)


def test_without_the_dictionary(tmp_path):
    ls = LexicalStats(TEXT, FreqDict(data_dir=tmp_path))
    assert ls.p_top1000 == pytest.approx(8 / 11)
    assert ls.lexical_density == pytest.approx(5 / 11)
    with pytest.raises(DatasetNotFoundError):
        _ = ls.coverage
    with pytest.raises(DatasetNotFoundError):
        ls.get_stats()


def test_default_dictionary(monkeypatch, freq_dict):
    monkeypatch.setattr("ests.lexical_stats.FreqDict", lambda: freq_dict)
    assert LexicalStats(TEXT).freq_dict is freq_dict


def test_bands(ls):
    ranks = [get_rank(lemma) for lemma in LEMMAS]
    for band in FREQUENCY_BANDS:
        expected = sum(1 for rank in ranks if rank and rank <= band) / 11
        assert getattr(ls, f"p_top{band}") == pytest.approx(expected)
    assert ls.p_beyond_top10000 == pytest.approx(1 - ls.p_top10000)
    assert ls.band_coverage(bands=(1, 2851)) == {
        1: 3 / 11,
        2851: sum(rank <= 2851 for rank in ranks) / 11,
    }
    unique = ls.band_coverage(unique=True)
    assert unique[1000] == pytest.approx(6 / 9)


def test_top_lemmas():
    ranks = load_top_lemmas()
    assert len(ranks) == 10_000
    assert list(ranks)[:5] == ["el", "de", "y", "en", "que"]
    assert get_rank("El") == 1
    for lemma in ("madrid", "pp", "xix", "b"):
        assert get_rank(lemma) is None
    for lemma in ("a", "y", "ya"):
        assert get_rank(lemma) is not None


def test_get_stats(ls):
    stats = ls.get_stats()
    assert list(stats) == list(LEXICAL_STATS_DESC)
    assert stats["coverage"] == 1.0


def test_print_stats(ls, capsys):
    ls.print_stats()
    lines = capsys.readouterr().out.splitlines()
    assert "Statistic" in lines[0]
    assert len(lines) == len(LEXICAL_STATS_DESC) + 2
    assert lines[2].startswith("Share of words found in the frequency dictionary")
    assert lines[2].rstrip().endswith("|   1.00")
