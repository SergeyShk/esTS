from math import isclose, log2, sqrt

import numpy as np
import pandas as pd
import pytest
import spacy
from scipy.spatial.distance import jensenshannon

from ests import CharNgramsExtractor, WordsExtractor
from ests.constants import DELTA_VARIANTS, FUNCTION_UD_POS
from ests.corpus import (
    ZetaScore,
    delta,
    delta_profiles,
    frequency_table,
    function_words_profile,
    kilgarriff_chi2,
    mendenhall_curve,
    mendenhall_distance,
    stylometry,
    z_scores,
    zeta,
)
from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp, tokenize

texts = {
    "A": (
        "El gato estaba en la ventana y miraba los pájaros. "
        "Los pájaros se fueron y el gato durmió en la ventana."
    ),
    "B": "El perro estaba en el suelo y dormía. Después el perro comió y otra vez dormía en el suelo.",
    "C": "Mañana el gato volverá a la ventana y mirará los pájaros, pero el perro dormirá.",
}
extractor = WordsExtractor(lowercase=True)
corpus = {name: extractor.extract(text) for name, text in texts.items()}


def test_frequency_table():
    table = frequency_table(corpus, n_mfw=5)
    assert list(table.index) == ["A", "B", "C"]
    assert list(table.columns) == ["el", "y", "en", "perro", "gato"]
    assert table.loc["B", "el"] == pytest.approx(4 / 19)
    assert table.loc["A", "perro"] == 0
    assert frequency_table(corpus, n_mfw=None).shape == (3, 26)
    assert list(frequency_table(corpus, n_mfw=None, culling=1.0).columns) == ["el", "y"]
    assert list(frequency_table(corpus, n_mfw=None, culling=0.5).columns)[:5] == [
        "el",
        "y",
        "en",
        "perro",
        "gato",
    ]
    assert frequency_table({"A": ["a"]}, n_mfw=None).loc["A", "a"] == 1


def test_z_scores():
    table = frequency_table(corpus, n_mfw=5)
    scores = z_scores(table)
    column = table["el"]
    assert scores["el"].tolist() == pytest.approx(
        ((column - column.mean()) / column.std(ddof=1)).tolist()
    )
    assert scores.std(ddof=1).tolist() == pytest.approx([1.0] * 5)
    constant = z_scores(frequency_table({"A": ["a", "b"], "B": ["a", "c"]}, n_mfw=None))
    assert constant["a"].tolist() == [0.0, 0.0]
    assert constant["b"].tolist() == pytest.approx([sqrt(2) / 2, -sqrt(2) / 2])


def test_constant_column_with_float_noise():
    # 0.1 in three texts: the rounding of the mean leaves a deviation of noise and not zero
    reference = {
        "A": ["el", "gato", "come", "pan", "y", "duerme", "mucho", "en", "casa", "hoy"],
        "B": ["el", "perro", "ladra", "fuerte", "y", "corre", "poco", "por", "aquí", "ya"],
        "C": ["el", "niño", "lee", "libros", "o", "juega", "solo", "en", "su", "cuarto"],
    }
    table = frequency_table(reference, n_mfw=3)
    assert list(table.columns) == ["el", "en", "y"]
    assert z_scores(table)["el"].tolist() == [0.0, 0.0, 0.0]
    varying = table[["en", "y"]]
    expected = (varying - varying.mean()) / varying.std(ddof=1)
    a, b = expected.loc["A"], expected.loc["B"]
    assert delta(reference, n_mfw=3, variant="cosine").loc["A", "B"] == pytest.approx(
        1 - (a * b).sum() / sqrt((a**2).sum() * (b**2).sum())
    )
    # The tested text has el at 0.2: the constant column is zeroed for it as well
    distances = delta_profiles(reference, {"?": ["el", *reference["A"][1:-1], "el"]}, n_mfw=3)
    tested = (pd.Series({"en": 0.1, "y": 0.1}) - varying.mean()) / varying.std(ddof=1)
    assert distances.loc["?"].tolist() == pytest.approx(
        [(tested - expected.loc[name]).abs().sum() / 3 for name in reference]
    )


def test_delta():
    scores = z_scores(frequency_table(corpus, n_mfw=5))
    difference = (scores.loc["A"] - scores.loc["B"]).abs()
    distances = delta(corpus, n_mfw=5)
    assert list(distances.index) == list(distances.columns) == ["A", "B", "C"]
    assert np.allclose(distances, distances.T)
    assert np.diag(distances).tolist() == [0.0, 0.0, 0.0]
    assert distances.loc["A", "B"] == pytest.approx(difference.sum() / 5)
    assert delta(corpus, n_mfw=5, variant="quadratic").loc["A", "B"] == pytest.approx(
        sqrt((difference**2).sum()) / 5
    )
    weights = [(5 - rank + 2) / 5 for rank in range(1, 6)]
    assert delta(corpus, n_mfw=5, variant="eder").loc["A", "B"] == pytest.approx(
        (difference * weights).sum()
    )
    a, b = scores.loc["A"], scores.loc["B"]
    assert delta(corpus, n_mfw=5, variant="cosine").loc["A", "B"] == pytest.approx(
        1 - (a * b).sum() / sqrt((a**2).sum() * (b**2).sum())
    )
    assert distances.loc["A", "C"] < distances.loc["A", "B"]
    assert set(DELTA_VARIANTS) == {"burrows", "quadratic", "eder", "cosine"}


def test_delta_identical_texts():
    same = {"A": corpus["A"], "B": corpus["A"], "C": corpus["B"]}
    distances = delta(same, n_mfw=5, variant="cosine")
    assert abs(distances.loc["A", "B"]) < 1e-12
    assert distances.loc["A", "C"] > 0
    assert abs(delta(same, n_mfw=5).loc["A", "B"]) < 1e-12


def test_delta_char_ngrams():
    ngrams = CharNgramsExtractor(n=2, lowercase=True)
    distances = delta({name: ngrams.extract(text) for name, text in texts.items()}, n_mfw=20)
    assert distances.shape == (3, 3)
    assert distances.loc["A", "C"] < distances.loc["A", "B"]


def test_delta_profiles():
    samples = {
        "A2": corpus["A"],
        "D": extractor.extract("El perro dormía en el suelo y el gato miraba la ventana."),
    }
    distances = delta_profiles(corpus, samples, n_mfw=5)
    assert list(distances.index) == ["A2", "D"]
    assert list(distances.columns) == ["A", "B", "C"]
    # A reference text under test: the same z-scores, the distances of delta
    for variant in DELTA_VARIANTS:
        expected = delta(corpus, n_mfw=5, variant=variant).loc["A"]
        row = delta_profiles(corpus, samples, n_mfw=5, variant=variant).loc["A2"]
        assert np.allclose(row.to_numpy(), expected.to_numpy())
    # The units and the scaling come from the references: the neighbours do not matter
    alone = delta_profiles(corpus, {"D": samples["D"]}, n_mfw=5)
    assert np.allclose(alone.loc["D"].to_numpy(), distances.loc["D"].to_numpy())
    # Words of a tested text outside the list of the references only change its length
    extra = delta_profiles(corpus, {"D": (*samples["D"], "elefante", "elefante")}, n_mfw=5)
    assert not np.allclose(extra.loc["D"].to_numpy(), distances.loc["D"].to_numpy())
    with pytest.raises(ParameterError):
        delta_profiles(corpus, samples, variant="manhattan")
    with pytest.raises(SourceError):
        delta_profiles({"A": corpus["A"], "B": corpus["B"]}, samples)
    with pytest.raises(SourceError):
        delta_profiles(corpus, {})
    with pytest.raises(SourceError):
        delta_profiles(corpus, {"D": []})
    with pytest.raises(SourceTypeError):
        delta_profiles(corpus, {"D": "el gato dormía"})
    # Statistics of a separate set: two references are allowed, scaled by statistics
    two = {"A": corpus["A"], "B": corpus["B"]}
    scaled = delta_profiles(two, samples, n_mfw=5, statistics=corpus)
    assert list(scaled.columns) == ["A", "B"]
    assert np.allclose(scaled.loc["A2"].to_numpy(), distances.loc["A2", ["A", "B"]].to_numpy())
    with pytest.raises(SourceError):
        delta_profiles(two, samples, n_mfw=5)


def test_delta_errors():
    with pytest.raises(ParameterError):
        delta(corpus, variant="manhattan")
    with pytest.raises(SourceError):
        delta({"A": corpus["A"], "B": corpus["B"]})
    with pytest.raises(ParameterError):
        delta(corpus, n_mfw=0)
    with pytest.raises(ParameterError):
        frequency_table(corpus, n_mfw=-1)
    with pytest.raises(SourceError):
        frequency_table({})
    with pytest.raises(SourceError):
        frequency_table({"A": corpus["A"], "B": []})
    with pytest.raises(ParameterError):
        frequency_table(corpus, culling=2)
    with pytest.raises(SourceError):
        delta({"A": ["a"], "B": ["b"], "C": ["c"]}, culling=1.0)
    with pytest.raises(SourceTypeError):
        frequency_table({"A": texts["A"]})
    with pytest.raises(SourceTypeError):
        frequency_table({"A": get_nlp()(texts["A"])})


def test_zeta():
    # 21 and 19 words give four segments each
    scores = zeta(corpus["A"], corpus["B"], segment_size=5)
    assert scores[0] == ZetaScore("gato", 0.5, 0.0, 0.5, log2(0.5 / (0.5 / 4)))
    assert [score.word for score in scores[:4]] == ["gato", "la", "pájaros", "ventana"]
    el = next(score for score in scores if score.word == "el")
    assert el == ZetaScore("el", 0.5, 0.75, -0.25, pytest.approx(log2(0.5 / 0.75)))
    assert scores[-1] == ZetaScore("suelo", 0.0, 0.5, -0.5, log2((0.5 / 4) / 0.5))
    assert zeta(corpus["A"], corpus["B"], segment_size=5, top_n=2) == scores[:2]
    assert zeta(corpus["A"], corpus["B"], segment_size=100)[0].zeta == 1.0
    # Four segments of A with gato in two, three of C with it in one
    several = zeta([corpus["A"], corpus["C"]], [corpus["B"]], segment_size=5)
    assert next(score for score in several if score.word == "gato").dp_target == 3 / 7
    assert zeta([corpus["A"], []], corpus["B"], segment_size=5) == scores
    assert zeta(["a"] * 2500, ["b"] * 100, segment_size=1000)[0].dp_target == 1.0
    scores = zeta(["a"] * 2500 + ["b"], ["b"] * 100, segment_size=1000)
    assert next(score for score in scores if score.word == "b").dp_target == pytest.approx(1 / 3)


def test_zeta_errors():
    with pytest.raises(ParameterError):
        zeta(corpus["A"], corpus["B"], segment_size=0)
    with pytest.raises(SourceError):
        zeta([], corpus["B"])
    with pytest.raises(SourceError):
        zeta(corpus["A"], [[]])
    with pytest.raises(ParameterError):
        zeta(corpus["A"], corpus["B"], top_n=0)
    with pytest.raises(SourceTypeError):
        zeta(texts["A"], corpus["B"])
    # A text among lists of words, a Doc among the texts
    with pytest.raises(SourceTypeError):
        zeta(["gato", ["perro"]], corpus["B"])
    with pytest.raises(SourceTypeError):
        zeta([get_nlp()(texts["A"])], corpus["B"])


def test_kilgarriff_chi2():
    words_a = ["a"] * 6 + ["b"] * 3 + ["c"]
    words_b = ["a"] * 2 + ["b"] * 5 + ["d"] * 3
    expected = 0.0
    for count_a, count_b in ((6, 2), (3, 5)):
        joint = count_a + count_b
        expected += (count_a - joint / 2) ** 2 / (joint / 2) * 2
    assert kilgarriff_chi2(words_a, words_b, n_mfw=2) == pytest.approx(expected)
    assert kilgarriff_chi2(words_a, words_a) == 0
    assert kilgarriff_chi2(words_a, words_b) > kilgarriff_chi2(words_a, words_b, n_mfw=2)
    with pytest.raises(SourceError):
        kilgarriff_chi2([], words_b)
    with pytest.raises(ParameterError):
        kilgarriff_chi2(words_a, words_b, n_mfw=0)
    with pytest.raises(SourceTypeError):
        kilgarriff_chi2(texts["A"], words_b)


def test_mendenhall():
    curve = mendenhall_curve(corpus["A"])
    assert list(curve) == [1, 2, 3, 4, 6, 7]
    assert curve[2] == pytest.approx(7 / 21)
    assert isclose(sum(curve.values()), 1.0)
    curve_b = mendenhall_curve(corpus["B"])
    lengths = sorted(set(curve) | set(curve_b))
    assert mendenhall_distance(corpus["A"], corpus["B"]) == pytest.approx(
        jensenshannon(
            [curve.get(length, 0) for length in lengths],
            [curve_b.get(length, 0) for length in lengths],
            base=2,
        )
    )
    assert mendenhall_distance(corpus["A"], corpus["A"]) == 0
    assert mendenhall_distance(["a"], ["bb"]) == pytest.approx(1.0)
    with pytest.raises(SourceError):
        mendenhall_curve([])
    with pytest.raises(SourceTypeError):
        mendenhall_curve(texts["A"])


def test_function_words_profile():
    profile = function_words_profile(corpus["A"])
    assert list(profile) == list(FUNCTION_UD_POS)
    assert profile["ADP"] == pytest.approx(2 / 21)
    assert profile["CCONJ"] == pytest.approx(2 / 21)
    assert profile["PRON"] == pytest.approx(1 / 21)
    assert profile["DET"] == pytest.approx(6 / 21)
    assert profile["SCONJ"] == 0
    # Punctuation helps the tagging and is not counted; no is an adverb
    words = ["Él", "no", "sabía", ",", "que", "ella", "estaba", "aquí"]
    profile = function_words_profile(words)
    assert profile["PRON"] == pytest.approx(2 / 7)
    assert profile["SCONJ"] == pytest.approx(1 / 7)
    assert profile["PART"] == 0
    assert function_words_profile(["el", " ", "gato", ""]) == function_words_profile(
        ["el", "gato"]
    )
    # A Doc without parts of speech is tagged as a list of its words
    assert function_words_profile(spacy.blank("es")(" ".join(words))) == profile
    untagged = get_nlp()(texts["A"], disable=["morphologizer"])
    assert not untagged.has_annotation("POS")
    assert function_words_profile(untagged) == function_words_profile(get_nlp()(texts["A"]))
    assert function_words_profile(words, nlp=get_nlp()) == profile


def test_function_words_profile_chunks(monkeypatch):
    # Chunks with a margin of context give the tags of one sequence, chunks without it do not
    words = list(tokenize(" ".join(texts.values())))
    whole = function_words_profile(words)
    monkeypatch.setattr(stylometry, "CHUNK_SIZE", 4)
    assert function_words_profile(words) == whole
    monkeypatch.setattr(stylometry, "CHUNK_MARGIN", 0)
    assert function_words_profile(words) != whole


def test_function_words_profile_tagged():
    doc = get_nlp()("Él dijo que el gato dormía, pero ¡ay!, nadie lo vio.")
    profile = function_words_profile(doc)
    assert profile["PRON"] == pytest.approx(3 / 11)
    assert profile["SCONJ"] == pytest.approx(1 / 11)
    assert profile["CCONJ"] == pytest.approx(1 / 11)
    assert profile["INTJ"] == pytest.approx(1 / 11)
    assert profile["ADP"] == 0


def test_function_words_profile_errors():
    with pytest.raises(SourceError):
        function_words_profile([",", "-"])
    with pytest.raises(SourceError):
        function_words_profile([])
    with pytest.raises(SourceError):
        function_words_profile(spacy.blank("es")("¿?"))
    with pytest.raises(SourceTypeError):
        function_words_profile(texts["A"])
    with pytest.raises(SourceError, match="parts of speech"):
        function_words_profile(corpus["A"], nlp=spacy.blank("es"))
