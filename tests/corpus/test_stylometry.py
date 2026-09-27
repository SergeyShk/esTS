import numpy as np
import pandas as pd
import pytest
import spacy

from ests import WordsExtractor
from ests.constants import FUNCTION_UD_POS
from ests.corpus import function_words_profile, stylometry
from ests.exceptions import SourceError, SourceTypeError
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


@pytest.mark.parametrize("container", [np.array, pd.Series])
def test_arrays_of_words(container):
    text = ["el", "gato", "y", "el", "perro", "duerme", "en", "la", "casa"]
    assert function_words_profile(container(text)) == function_words_profile(text)
