from collections import Counter
from math import inf, isnan, log

import numpy as np
import pytest

from ests.constants import G2_CRITICAL_VALUES, KEYNESS_MEASURES
from ests.corpus import Keyword, keyness
from ests.corpus.keyness import (
    MEASURES,
    calc_bic,
    calc_chi2,
    calc_diff,
    calc_ell,
    calc_log_likelihood,
    calc_log_ratio,
    calc_odds_ratio,
    calc_p_value,
)
from ests.datasets import FreqDict
from ests.datasets.freq_dict import CORPUS_SIZE
from ests.exceptions import DatasetNotFoundError, ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp

target = ["gato", "estaba", "en", "ventana", "y", "miraba", "en", "pájaros", "gato", "dormía"]
reference = ["perro", "yacía", "en", "suelo", "y", "descansaba", "perro", "comía"]


def test_measures():
    assert set(MEASURES) == set(KEYNESS_MEASURES)
    assert calc_log_likelihood(10, 5, 1000, 2000) == pytest.approx(
        2 * (10 * log(2) + 5 * log(0.5))
    )
    assert calc_log_likelihood(5, 10, 2000, 1000) == pytest.approx(
        -calc_log_likelihood(10, 5, 1000, 2000)
    )
    assert calc_log_likelihood(0, 0, 1000, 2000) == 0
    assert calc_log_likelihood(10, 0, 1000, 2000) == pytest.approx(2 * 10 * log(3))
    assert calc_chi2(10, 5, 1000, 2000) == pytest.approx(6.105527638190955)
    assert calc_chi2(5, 10, 2000, 1000) == pytest.approx(-6.105527638190955)
    assert calc_chi2(1, 2, 1000, 2000) == 0
    assert calc_chi2(0, 0, 1000, 2000) == 0
    assert calc_diff(10, 5, 1000, 2000) == pytest.approx(300)
    assert calc_diff(10, 0, 1000, 2000) == pytest.approx((0.01 - 0.00025) / 0.00025 * 100)
    assert calc_log_ratio(10, 5, 1000, 2000) == 2
    assert calc_log_ratio(0, 5, 1000, 2000) == pytest.approx(-2.321928094887362)
    assert calc_bic(10, 5, 1000, 2000) == pytest.approx(
        calc_log_likelihood(10, 5, 1000, 2000) - log(3000)
    )
    assert calc_bic(5, 10, 2000, 1000) == pytest.approx(-calc_bic(10, 5, 1000, 2000))


def test_effect_sizes():
    assert calc_ell(10, 5, 1000, 2000) == pytest.approx(
        calc_log_likelihood(10, 5, 1000, 2000) / (3000 * log(5))
    )
    assert isnan(calc_ell(1, 0, 1000, 2000))
    assert isnan(calc_ell(5, 0, 1000, 2000))
    assert not isnan(calc_ell(9, 0, 1000, 2000))
    assert isnan(calc_ell(4, 0, 4, 2))
    assert 0 < calc_ell(30, 5, 60, 60) < 1
    assert calc_odds_ratio(10, 5, 1000, 2000) == pytest.approx((10 / 990) / (5 / 1995))
    assert calc_odds_ratio(10, 10, 10, 20) == inf
    assert calc_odds_ratio(10, 20, 20, 20) == 0
    assert isnan(calc_odds_ratio(20, 20, 20, 20))


def test_p_value():
    assert calc_p_value(3.84) == pytest.approx(0.05, abs=0.001)
    for p, critical in G2_CRITICAL_VALUES.items():
        assert calc_p_value(critical) == pytest.approx(p, rel=0.01)
        assert calc_p_value(-critical) == pytest.approx(p, rel=0.01)
    assert list(calc_p_value(np.array([3.84, -6.63]))) == [
        pytest.approx(0.05, abs=0.001),
        pytest.approx(0.01, abs=0.001),
    ]


def test_keyness():
    keywords = keyness(target, reference)
    assert [keyword.word for keyword in keywords] == [
        "gato",
        "dormía",
        "estaba",
        "miraba",
        "pájaros",
        "ventana",
        "en",
    ]
    g2 = calc_log_likelihood(2, 0, 10, 8)
    assert keywords[0] == Keyword(
        "gato", 2, 0, 200000.0, 0.0, g2, calc_p_value(g2), calc_log_ratio(2, 0, 10, 8), g2
    )
    assert keywords[-1].freq_reference == 1
    assert keywords[-1].ipm_reference == 125000.0
    assert all(keyword.g2 > 0 for keyword in keywords)
    assert [keyword.p_value for keyword in keywords] == [
        pytest.approx(calc_p_value(keyword.g2)) for keyword in keywords
    ]


def test_keyness_options():
    keywords = keyness(target, reference)
    assert keyness(Counter(target), Counter(reference)) == keywords
    assert keyness(target, reference, top_n=2) == keywords[:2]
    assert [keyword.word for keyword in keyness(target, reference, min_freq=2)] == ["gato", "en"]


def test_keyness_negative():
    keywords = keyness(target, reference, positive=False)
    assert [keyword.word for keyword in keywords] == [
        "perro",
        "comía",
        "descansaba",
        "suelo",
        "yacía",
        "y",
    ]
    assert all(keyword.g2 < 0 and keyword.score < 0 for keyword in keywords)
    assert keywords[-1].freq_target == 1
    assert keywords[-1].log_ratio == pytest.approx(-0.32192809488736235)


def test_keyness_against_frequencies_of_a_dictionary():
    frequencies = {"gato": 40.0, "en": 20000.0, "pájaros": 8.0, "y": 25000.0}
    keywords = keyness(target, frequencies)
    gato = next(keyword for keyword in keywords if keyword.word == "gato")
    size = sum(frequencies.values())
    assert gato.freq_reference == 40.0
    assert gato.ipm_reference == pytest.approx(40 / size * 1e6)
    assert gato.g2 == pytest.approx(calc_log_likelihood(2, 40, 10, size))


def test_keyness_against_the_frequency_dictionary(freq_dict):
    words = ["Gatos", "gato", "gatos", "el", "felinólogo", "ventana"]
    keywords = keyness(words, freq_dict)
    gato = next(keyword for keyword in keywords if keyword.word == "gato")
    reference = freq_dict.ipm("gato") * CORPUS_SIZE / 1e6
    assert gato.freq_target == 3
    assert gato.freq_reference == pytest.approx(reference)
    assert gato.ipm_reference == pytest.approx(freq_dict.ipm("gato"))
    assert gato.g2 == pytest.approx(calc_log_likelihood(3, reference, 6, CORPUS_SIZE))
    # A word out of the dictionary gets the least frequency of the dictionary
    felinologo = next(keyword for keyword in keywords if keyword.word == "felinólogo")
    assert felinologo.freq_reference == pytest.approx(freq_dict.min_ipm * CORPUS_SIZE / 1e6)
    assert [keyword.g2 for keyword in keywords] == sorted((k.g2 for k in keywords), reverse=True)


def test_keyness_against_the_frequency_dictionary_by_frequencies(freq_dict):
    by_words = keyness(["gatos", "gatos", "gato", "ventana"], freq_dict)
    by_counts = keyness({"gatos": 2, "gato": 1, "ventana": 1}, freq_dict)
    assert by_counts == by_words
    assert {keyword.word for keyword in by_words} == {"gato", "ventana"}


def test_keyness_against_the_frequency_dictionary_negative(freq_dict):
    keywords = keyness(["gato"] * 5, freq_dict, positive=False, top_n=3)
    assert [keyword.word for keyword in keywords] == ["el", "de", "y"]
    assert all(keyword.g2 < 0 for keyword in keywords)


def test_keyness_against_the_frequency_dictionary_proper_nouns(freq_dict):
    # The row of Roma goes to romo, the key the word Roma reaches with no part of speech
    rows = {(r["lemma"], r["pos"]): r["ipm"] for r in freq_dict}
    romo = (
        sum(ipm for (lemma, pos), ipm in rows.items() if lemma == "romo") + rows["roma", "PROPN"]
    )
    assert freq_dict.word_ipm["romo"] == pytest.approx(romo)
    assert "roma" not in freq_dict.word_ipm
    words = ["Roma"] * 80 + ["el", "de", "la"] * 100
    keyword = keyness(words, freq_dict, top_n=1)[0]
    assert keyword.word == "romo"
    assert keyword.freq_reference == pytest.approx(romo * CORPUS_SIZE / 1e6)
    negative = keyness(words, freq_dict, positive=False)
    assert all(k.word not in ("roma", "romo") for k in negative)


def test_keyness_against_the_frequency_dictionary_alphabet(freq_dict):
    words = ["Gato", "2020", "1.º", "ciudad-real", "etc.", "o[t]ras"]
    keywords = keyness(words, freq_dict)
    assert [keyword.word for keyword in keywords] == ["gato"]
    # The words left out do not count in the size of the target either
    assert keywords[0].ipm_target == 1e6


def test_keyness_against_the_frequency_dictionary_large_target(freq_dict):
    # Beyond 10 million words a hapax out of the dictionary has less than 0.1 ipm,
    # while the least frequency of the dictionary is only an upper bound for it
    target = {"gato": 100_000_000, "felinólogo": 1}
    negative = keyness(target, freq_dict, positive=False)
    assert "felinólogo" not in {keyword.word for keyword in negative}
    assert "el" in {keyword.word for keyword in negative}
    positive = keyness({"gato": 10, "felinólogo": 1}, freq_dict)
    assert "felinólogo" in {keyword.word for keyword in positive}


def test_keyness_without_the_dictionary(tmp_path):
    with pytest.raises(DatasetNotFoundError):
        keyness(["gato"], FreqDict(data_dir=tmp_path))


@pytest.mark.parametrize("measure", list(KEYNESS_MEASURES))
def test_keyness_measures(measure):
    keywords = keyness(target, reference, measure=measure)
    gato = next(keyword for keyword in keywords if keyword.word == "gato")
    assert gato.score == MEASURES[measure](2, 0, 10, 8) or isnan(gato.score)
    if measure != "ell":
        assert keywords[0].word == "gato"


def test_keyness_of_small_corpora_by_the_effect_size():
    keywords = keyness(target, reference, measure="ell")
    assert all(isnan(keyword.score) for keyword in keywords)
    assert [keyword.word for keyword in keywords[:2]] == ["en", "gato"]
    found = keyness(["a"] * 30 + ["b"] * 30, ["a"] * 5 + ["b"] * 55, measure="ell")
    assert found[0].score == pytest.approx(calc_ell(30, 5, 60, 60))


def test_keyness_by_the_odds_ratio():
    assert keyness(target, reference, measure="odds_ratio")[0].word == "gato"
    assert keyness(["a", "b"], ["a"], positive=False, measure="odds_ratio")[0].score == 0


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        ({"measure": "mi"}, ParameterError),
        ({"top_n": 0}, ParameterError),
        ({"top_n": -1}, ParameterError),
    ],
)
def test_keyness_errors(kwargs, error):
    with pytest.raises(error):
        keyness(target, reference, **kwargs)


@pytest.mark.parametrize(("first", "second"), [([], reference), (target, {})])
def test_keyness_of_an_empty_corpus(first, second):
    with pytest.raises(SourceError):
        keyness(first, second)


def test_keyness_of_a_string():
    with pytest.raises(SourceTypeError):
        keyness("el gato duerme", reference)


@pytest.mark.parametrize("span", [False, True])
def test_refuses_a_doc(span):
    doc = get_nlp()("El gato duerme y el gato come.")
    source = doc[0:3] if span else doc
    with pytest.raises(SourceTypeError, match="WordsExtractor"):
        keyness(source, reference)
