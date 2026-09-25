from math import isnan

import pytest
import spacy

from ests import StyleStats, WordsExtractor
from ests.constants import (
    COMPOUND_PREPOSITIONS,
    OFFICIALESE_CLICHES,
    PARENTHETICALS,
    STOPWORDS,
    STYLE_STATS_DESC,
)
from ests.exceptions import SourceError
from ests.style_stats import (
    calc_academic_nausea,
    calc_classic_nausea,
    calc_keyword_density,
    calc_parentheticals,
    calc_phrase_density,
    calc_spam,
    calc_verbal_nouns,
    calc_water,
    calc_zipf_naturalness,
    expand_phrases,
    is_parenthetical,
    is_stopword,
)
from ests.utils import get_nlp

text = (
    "La revisión de los expedientes se hizo durante el mes de marzo. Sin embargo, el "
    "nombramiento de la comisión no llegó hasta abril, es decir, después de la votación. "
    "Por ejemplo, el uso de los datos exigió una nueva revisión."
)
# 12 words, 9 word types, the frequency spectrum {1: 6, 2: 3}
riddle = (
    "tres", "tristes", "tigres", "tragaban", "trigo", "en", "un", "trigal",
    "en", "tres", "tristes", "trastos",
)  # fmt: skip
riddle_text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
# 33 words: the prepositions a efectos del, en el marco de, conforme al; the clichés se
# procedió a, a la mayor brevedad, dio cumplimiento; the parenthetical no obstante
officialese = (
    "A efectos del cobro, se procedió a la revisión del expediente en el marco de la ley. "
    "No obstante, conforme al reglamento, la comisión dio cumplimiento a la resolución "
    "a la mayor brevedad."
)


@pytest.fixture(scope="module")
def nlp():
    return get_nlp()


@pytest.fixture(scope="module")
def ss():
    return StyleStats(text)


def test_init_value_error():
    with pytest.raises(SourceError):
        StyleStats("¿? ...")
    with pytest.raises(ValueError):
        StyleStats(text, top_n=0)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        StyleStats(source)


def test_init_doc(nlp):
    assert StyleStats(riddle_text).words == riddle
    doc = spacy.blank("es")(riddle_text)
    assert StyleStats(doc).words == riddle
    stats = StyleStats(nlp(text)).get_stats()
    assert stats == StyleStats(text).get_stats()


def test_init_lexemes():
    ss = StyleStats(text, words_extractor=WordsExtractor(use_lexemes=True, lowercase=True))
    assert ss.forms == StyleStats(text).forms
    assert ss.spam > StyleStats(text).spam


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("y", True),
        ("no", True),
        ("de", True),
        ("Él", True),
        ("aquel", True),
        ("cuyo", True),
        ("aquí", True),
        ("dónde", True),
        ("á", True),
        ("ay", True),
        ("finalmente", True),
        ("gato", False),
        ("rápidamente", False),
        ("leer", False),
        ("100", False),
    ],
)
def test_is_stopword(word, expected):
    assert is_stopword(word) is expected


def test_stopwords_are_lower_case():
    assert all(word == word.lower() for word in STOPWORDS)


def test_classic_nausea(ss):
    assert calc_classic_nausea(riddle) == pytest.approx(2**0.5)
    assert ss.classic_nausea == pytest.approx(ss.words.count("de") ** 0.5)
    assert calc_classic_nausea([]) == 0.0


def test_academic_nausea():
    assert calc_academic_nausea(riddle, 1) == pytest.approx(100 * 2 / 12)
    assert calc_academic_nausea(riddle, 3) == pytest.approx(100 * 6 / 12)
    assert calc_academic_nausea(riddle, 100) == 100.0
    assert StyleStats(riddle_text, top_n=3).academic_nausea == pytest.approx(100 * 6 / 12)


def test_water(ss):
    # stopwords: en x2, un
    assert calc_water(riddle) == pytest.approx(100 * 3 / 12)
    assert calc_water(riddle, stopwords=["en", "tres"]) == pytest.approx(100 * 4 / 12)
    assert calc_water(riddle, stopwords=["EN"]) == pytest.approx(100 * 2 / 12)
    assert calc_water(riddle, stopwords=[]) == 0.0
    assert StyleStats(riddle_text, stopwords=["tres"]).water == pytest.approx(100 * 2 / 12)
    n_stopwords = sum(1 for word in ss.words if is_stopword(word))
    assert ss.water == pytest.approx(100 * n_stopwords / len(ss.words))


def test_spam(ss):
    assert calc_spam(riddle) == pytest.approx(100 * 3 / 12)
    assert calc_spam(["a", "b", "c"]) == 0.0
    assert calc_spam(["a", "a", "a"]) == pytest.approx(200 / 3)
    assert ss.spam == pytest.approx(100 * (1 - len(set(ss.words)) / len(ss.words)))


def test_zipf_naturalness():
    # rank 2 has the frequency 2 against the ideal 1: the deviation is 1
    assert calc_zipf_naturalness(riddle) == 0.0
    assert calc_zipf_naturalness(["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3) == 100.0
    assert calc_zipf_naturalness(["a"] * 6 + ["b"] * 6 + ["c"] * 6 + ["d"] * 6) == 0.0
    # frequencies 3 and 1 on the ranks 2 and 3 against the ideal 2 and 4/3: deviations 1/2 and 1/4
    assert calc_zipf_naturalness(["a"] * 4 + ["b"] * 3 + ["c"]) == pytest.approx(
        100 * (1 - (1 / 2 + 1 / 4) / 2)
    )
    # no ranks to compare: hapaxes alone, one word type, top_n below 2
    assert isnan(calc_zipf_naturalness(["a", "b", "c"]))
    assert isnan(calc_zipf_naturalness(["a", "a", "a"]))
    assert isnan(calc_zipf_naturalness(riddle, top_n=1))
    assert isnan(calc_zipf_naturalness([]))
    assert isnan(StyleStats(riddle_text, top_n=1).zipf_naturalness)


def test_keyword_density():
    assert calc_keyword_density(riddle, ["tres", "tres tristes", "TRIGO en", "perro", ""]) == {
        "tres": pytest.approx(100 * 2 / 12),
        "tres tristes": pytest.approx(100 * 2 / 12),
        "TRIGO en": pytest.approx(100 / 12),
        "perro": 0.0,
        "": 0.0,
    }
    # occurrences of a phrase may overlap
    assert calc_keyword_density(["a", "a", "a"], ["a a"]) == {"a a": pytest.approx(200 / 3)}
    assert StyleStats(riddle_text).keyword_density("trigo") == {"trigo": pytest.approx(100 / 12)}


def test_verbal_nouns(ss, nlp):
    assert calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"]) == 50.0
    assert calc_verbal_nouns(["uso", "viaje", "Aprendizaje"]) == 100.0
    assert isnan(calc_verbal_nouns([]))
    # revisión x2, nombramiento, comisión, votación, uso among the 15 nouns of the model
    nouns = [token.lemma_ for token in nlp(text) if token.pos_ == "NOUN"]
    assert len(nouns) == 15
    assert ss.verbal_nouns == pytest.approx(100 * 6 / 15)
    assert StyleStats(nlp(text)).verbal_nouns == ss.verbal_nouns
    assert StyleStats(text, nlp=nlp).verbal_nouns == ss.verbal_nouns


def test_verbal_nouns_without_the_annotation(nlp):
    ss = StyleStats(spacy.blank("es")(text))
    assert ss.water == StyleStats(text).water
    with pytest.raises(SourceError, match="parts of speech"):
        _ = ss.verbal_nouns
    # the parts of speech without the lemmas give every noun an empty lemma
    ss = StyleStats(nlp(text, disable=["lemmatizer"]))
    assert ss.spam == StyleStats(text).spam
    with pytest.raises(SourceError, match="no lemmas"):
        _ = ss.verbal_nouns
    pipeline = spacy.load("es_core_news_sm", exclude=["lemmatizer"])
    with pytest.raises(SourceError, match="no lemmas"):
        _ = StyleStats(text, nlp=pipeline).verbal_nouns


def test_verbal_nouns_of_a_long_text():
    pipeline = spacy.blank("es")
    pipeline.max_length = 20
    ss = StyleStats(text, nlp=pipeline)
    assert ss.spam == StyleStats(text).spam
    with pytest.raises(SourceError, match="longer than the limit"):
        _ = ss.verbal_nouns


def test_parentheticals(ss):
    words = ["sin", "embargo", "finalmente", "el", "gato", "es", "decir", "duerme"]
    assert calc_parentheticals(words) == pytest.approx(100 * 3 / 8)
    # sin embargo, es decir, por ejemplo
    assert ss.parentheticals == pytest.approx(100 * 3 / len(ss.forms))
    assert is_parenthetical("Finalmente")
    assert not is_parenthetical("embargo")


def test_officialese():
    ss = StyleStats(officialese)
    assert len(ss.forms) == 33
    assert ss.compound_prepositions == pytest.approx(100 * 3 / 33)
    assert ss.cliches == pytest.approx(100 * 3 / 33)
    assert ss.parentheticals == pytest.approx(100 / 33)


@pytest.mark.parametrize("phrases", [COMPOUND_PREPOSITIONS, OFFICIALESE_CLICHES, PARENTHETICALS])
def test_lists_are_sorted_and_lower_case(phrases):
    assert list(phrases) == sorted(phrases)
    assert all(phrase == phrase.lower() for phrase in phrases)
    assert len(set(phrases)) == len(phrases)


def test_expand_phrases():
    assert sorted(expand_phrases(["x"], ["a efectos de", "conforme a", "sírvase", ""])) == [
        "a efectos de",
        "a efectos del",
        "conforme a",
        "conforme al",
        "sírvase",
    ]
    # an infinitive at the start takes the forms of the text with its lemma
    words = ["dio", "cumplimiento", "y", "dar", "curso", "se", "llevará", "a", "cabo"]
    assert sorted(expand_phrases(words, ["dar cumplimiento", "llevar a cabo"])) == [
        "dar cumplimiento",
        "dio cumplimiento",
        "llevar a cabo",
        "llevará a cabo",
    ]
    assert calc_phrase_density(words, OFFICIALESE_CLICHES) == pytest.approx(100 * 3 / 9)
    # a word that is no infinitive stays as it is
    assert expand_phrases(["cabe"], ["cabe destacar"]) == ["cabe destacar"]


@pytest.mark.parametrize(
    "phrase",
    [
        # the irregular participles of the perfect and the imperative with se
        "ha dado cumplimiento",
        "se ha hecho entrega",
        "ha puesto de manifiesto",
        "han resultado beneficiarios",
        "dese traslado a las partes",
        "dénse por notificados",
        # the pronominal lemmas of simplemma: llevarse, ponerse
        "llévese a cabo",
        "deberá llevarse a cabo",
        "poniéndose de manifiesto",
    ],
)
def test_expand_phrases_of_the_forms_simplemma_misses(phrase):
    words = phrase.split()
    cliches = ["dar cumplimiento", "hacer entrega", "poner de manifiesto", "dar traslado"]
    cliches += ["resultar beneficiarios", "dar por notificados", "llevar a cabo"]
    assert calc_phrase_density(words, cliches) == pytest.approx(100 / len(words))


def test_expand_phrases_leaves_the_nouns():
    words = ["el", "hecho", "de", "que", "el", "puesto", "de", "trabajo"]
    assert calc_phrase_density(words, OFFICIALESE_CLICHES) == 0.0


def test_phrase_density():
    words = ["en", "el", "marco", "de", "la", "ley", "en", "el", "marco"]
    assert calc_phrase_density(words, ["en el marco de", "en el"]) == pytest.approx(100 * 2 / 9)
    assert calc_phrase_density(words, []) == 0.0


def test_custom_cliches():
    ss = StyleStats(riddle_text, cliches=["tres tristes", "trigal en"])
    assert ss.cliches == pytest.approx(100 * 3 / 12)


def test_get_stats(ss):
    stats = ss.get_stats()
    assert list(stats) == list(STYLE_STATS_DESC)
    assert all(isinstance(value, float) for value in stats.values())


def test_print_stats(ss, capsys):
    ss.print_stats()
    output = capsys.readouterr().out
    assert all(desc in output for desc in STYLE_STATS_DESC.values())
