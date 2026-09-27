import pytest

from ests.corpus import Keyword, keyness
from ests.corpus.keyness import (
    calc_log_likelihood,
    calc_log_ratio,
    calc_p_value,
)
from ests.datasets import FreqDict
from ests.datasets.freq_dict import CORPUS_SIZE
from ests.exceptions import DatasetNotFoundError, ParameterError

target = ["gato", "estaba", "en", "ventana", "y", "miraba", "en", "pájaros", "gato", "dormía"]
reference = ["perro", "yacía", "en", "suelo", "y", "descansaba", "perro", "comía"]


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
    assert {type(keyword.freq_reference) for keyword in keywords} == {float}
    assert keywords[-1].ipm_reference == 125000.0
    assert all(keyword.g2 > 0 for keyword in keywords)
    assert [keyword.p_value for keyword in keywords] == [
        pytest.approx(calc_p_value(keyword.g2)) for keyword in keywords
    ]


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
    # The least frequency of the dictionary is only an upper bound for a hapax out of it
    target = {"gato": 100_000_000, "felinólogo": 1}
    negative = keyness(target, freq_dict, positive=False)
    assert "felinólogo" not in {keyword.word for keyword in negative}
    assert "el" in {keyword.word for keyword in negative}
    positive = keyness({"gato": 10, "felinólogo": 1}, freq_dict)
    assert "felinólogo" in {keyword.word for keyword in positive}


def test_keyness_without_the_dictionary(tmp_path):
    with pytest.raises(DatasetNotFoundError):
        keyness(["gato"], FreqDict(data_dir=tmp_path))


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
