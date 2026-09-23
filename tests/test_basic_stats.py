from math import isnan

import pytest
import spacy

from ests import BasicStats
from ests.basic_stats import count_punctuations, punctuation_profile
from ests.constants import BASIC_STATS_DESC, PUNCTUATION_TYPES
from ests.utils import get_nlp

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


@pytest.fixture(scope="module")
def bs():
    return BasicStats(TEXT, normalize=True)


@pytest.fixture(scope="module")
def nlp():
    return spacy.load("es_core_news_sm")


@pytest.mark.parametrize("source", ["Hola. ¿? Adiós.", "Hola.\n...\nAdiós."])
def test_sentences_without_words_are_not_counted(source):
    assert BasicStats(source).n_sents == 2


def test_sentences_without_words_are_not_counted_in_a_doc():
    doc = get_nlp()("Hola. ¿? Adiós.")
    assert BasicStats(doc).n_sents == 2


def test_init_value_error():
    with pytest.raises(ValueError):
        BasicStats("+ _")


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        BasicStats(text)


def test_c_letters(bs):
    assert bs.c_letters == {
        1: 4,
        2: 21,
        3: 21,
        4: 2,
        5: 5,
        6: 6,
        7: 3,
        8: 12,
        9: 1,
        10: 7,
        11: 4,
        12: 6,
        14: 1,
        15: 1,
    }


def test_c_syllables(bs):
    assert bs.c_syllables == {1: 44, 2: 14, 3: 17, 4: 8, 5: 8, 6: 3}


def test_n_chars(bs):
    assert bs.n_chars == 622


def test_n_complex_words(bs):
    assert bs.n_complex_words == 36


def test_n_letters(bs):
    assert bs.n_letters == 519


def test_n_long_words(bs):
    assert bs.n_long_words == 35


def test_n_monosyllable_words(bs):
    assert bs.n_monosyllable_words == 44


def test_n_polysyllable_words(bs):
    assert bs.n_polysyllable_words == 50


def test_n_sents(bs):
    assert bs.n_sents == 2


def test_n_simple_words(bs):
    assert bs.n_simple_words == 58


def test_n_spaces(bs):
    assert bs.n_spaces == 93


def test_n_syllables(bs):
    assert bs.n_syllables == 213


def test_n_unique_words(bs):
    assert bs.n_unique_words == 55


def test_n_words(bs):
    assert bs.n_words == 94


def test_n_punctuations(bs):
    assert bs.n_punctuations == 10


def test_c_punctuations(bs):
    assert bs.c_punctuations == {
        "comma": 4,
        "period": 2,
        "question": 0,
        "exclamation": 0,
        "ellipsis": 0,
        "colon": 1,
        "semicolon": 1,
        "dash": 0,
        "hyphen": 0,
        "angle_quotes": 0,
        "straight_quotes": 0,
        "parentheses": 2,
        "other": 0,
    }
    assert sum(bs.c_punctuations.values()) == bs.n_punctuations
    assert list(bs.c_punctuations) == list(PUNCTUATION_TYPES)


def test_count_punctuations():
    text = (
        "El gato — «fiera»... El perro, claro, - amigo; y “alguien” (el que vive) – ¡no!"
        ' ¿Así? "Sí". ‘Ya’ 5…'
    )
    assert count_punctuations(text) == {
        "comma": 2,
        "period": 1,
        "question": 2,
        "exclamation": 2,
        "ellipsis": 2,
        "colon": 0,
        "semicolon": 1,
        "dash": 3,
        "hyphen": 0,
        "angle_quotes": 2,
        "straight_quotes": 6,
        "parentheses": 2,
        "other": 0,
    }
    assert count_punctuations("Hola.... Adiós....... Sí") == {
        **dict.fromkeys(PUNCTUATION_TYPES, 0),
        "ellipsis": 2,
    }
    assert count_punctuations("") == dict.fromkeys(PUNCTUATION_TYPES, 0)


def test_count_punctuations_inverted_marks():
    counts = count_punctuations("¿Quién?.. ¡Nadie!.. Se fueron... ¿Sí?.")
    assert (counts["question"], counts["exclamation"], counts["ellipsis"], counts["period"]) == (
        4,
        2,
        3,
        1,
    )
    assert count_punctuations("¿¡Qué!?")["question"] == 2
    assert count_punctuations("¿¡Qué!?")["exclamation"] == 2


def test_count_punctuations_other_marks():
    """Every mark that is_punctuation removes from the words lands in a type"""
    counts = count_punctuations("Dijo ‹así› y «así» § 5 € 20° ‰ † „así“")
    assert (counts["angle_quotes"], counts["straight_quotes"], counts["other"]) == (2, 1, 8)
    for char in "‹›§€°‰†„":
        assert count_punctuations(f"a {char} b")["other"] == 1
    assert count_punctuations("Dijo: ‘Ya está’")["straight_quotes"] == 2


def test_count_punctuations_spaced_hyphen_as_dash():
    text = "- Se fueron, - dijo él.\n- Sí-sí, - contestó alguien - y todo.\n-"
    counts = count_punctuations(text)
    assert (counts["dash"], counts["hyphen"]) == (6, 1)
    counts = count_punctuations("Qué joven soy - y no conozco el miedo.")
    assert (counts["dash"], counts["hyphen"]) == (1, 0)
    assert count_punctuations("teórico-práctico")["hyphen"] == 1
    assert count_punctuations("casa -\nmuseo")["dash"] == 1


@pytest.mark.parametrize(
    ("text", "dashes", "hyphens"),
    [
        ("-Hola -dijo Juan.", 2, 0),
        ("-¿Vienes? -preguntó ella.", 2, 0),
        ("Sí -dijo- claro.", 2, 0),
        ("—Hola —dijo Juan—.", 3, 0),
        ("-5 grados y -3", 0, 2),
        ("1990-1995", 0, 1),
        ("teórico-práctico", 0, 1),
        ("Madrid - Barcelona 2-1", 1, 1),
        ("pala-\nbra", 0, 1),
        ("un texto jus-\ntificado con dos pala-\nbras", 0, 2),
        ("todo -\nnada", 1, 0),
        ("fin-", 1, 0),
    ],
)
def test_count_punctuations_attached_raya(text, dashes, hyphens):
    counts = count_punctuations(text)
    assert (counts["dash"], counts["hyphen"]) == (dashes, hyphens)


def test_punctuation_profile():
    profile = punctuation_profile("¿Qué haces? ¡Ven aquí! Vale, voy")
    assert profile["comma"] == pytest.approx(1 / 6 * 1000)
    assert profile["question"] == pytest.approx(2 / 6 * 1000)
    assert profile["exclamation"] == pytest.approx(2 / 6 * 1000)
    assert profile["period"] == 0
    assert profile["inverted_share"] == 0.5
    assert punctuation_profile("Que haces? Ven aqui! Vale, voy")["inverted_share"] == 0
    assert punctuation_profile("¡Ven! Vale?")["inverted_share"] == pytest.approx(1 / 3)
    assert punctuation_profile("Hola, hola", n_words=4)["comma"] == 250
    assert isnan(punctuation_profile("Hola, hola")["inverted_share"])
    assert all(isnan(value) for value in punctuation_profile("...").values())


def test_punctuation_profile_docs_example():
    text = "El gato — «fiera»... El perro, claro, - amigo; y alguien (el que vive) — ¡no!"
    counts = {kind: count for kind, count in count_punctuations(text).items() if count}
    assert counts == {
        "comma": 2,
        "exclamation": 2,
        "ellipsis": 1,
        "semicolon": 1,
        "dash": 3,
        "angle_quotes": 2,
        "parentheses": 2,
    }
    profile = punctuation_profile(text)
    assert round(profile["dash"], 1) == 230.8
    assert profile["inverted_share"] == 0.5


def test_p_unique_words(bs):
    assert bs.p_unique_words == pytest.approx(55 / 94)


def test_p_long_words(bs):
    assert bs.p_long_words == pytest.approx(35 / 94)


def test_p_complex_words(bs):
    assert bs.p_complex_words == pytest.approx(36 / 94)


def test_p_simple_words(bs):
    assert bs.p_simple_words == pytest.approx(58 / 94)


def test_p_monosyllable_words(bs):
    assert bs.p_monosyllable_words == pytest.approx(44 / 94)


def test_p_polysyllable_words(bs):
    assert bs.p_polysyllable_words == pytest.approx(50 / 94)


def test_p_letters(bs):
    assert bs.p_letters == pytest.approx(519 / 622)


def test_p_spaces(bs):
    assert bs.p_spaces == pytest.approx(93 / 622)


def test_p_punctuations(bs):
    assert bs.p_punctuations == pytest.approx(10 / 622)


def test_no_normalized_stats_by_default():
    assert not hasattr(BasicStats(TEXT), "p_unique_words")


def test_count_words_by_syllables(bs):
    assert bs.count_words_by_syllables(3) == bs.n_complex_words
    assert bs.count_words_by_syllables(4) == 19


def test_count_words_by_letters(bs):
    assert bs.count_words_by_letters(7) == bs.n_long_words
    assert bs.count_words_by_letters(8) == 32


def test_custom_factors():
    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
    bs = BasicStats(text, complex_syl_factor=4, long_word_letter_factor=9)
    assert bs.n_complex_words == 1
    assert bs.n_simple_words == 9
    assert bs.n_long_words == 1


def test_multichar_punctuation():
    bs = BasicStats("¡¡¡Hurra!!! ¿¡Hurra!? Hurra... Palabra – palabra… y §1")
    assert bs.n_words == 7
    assert bs.n_punctuations == 14 == sum(bs.c_punctuations.values())
    assert bs.c_punctuations["exclamation"] == 8
    assert bs.c_punctuations["other"] == 1
    assert BasicStats(text := "¡¡¡Hurra!!! ¿¡Hurra!? Hurra...", normalize=True).p_punctuations == (
        11 / BasicStats(text).n_chars
    )


def test_letters_only():
    bs = BasicStats("teórico-práctico abcdefg 1234567 gato")
    assert bs.c_letters == {0: 1, 4: 1, 7: 1, 15: 1}
    assert bs.n_letters == 26
    assert bs.n_long_words == 2
    assert bs.count_words_by_letters(7) == 2
    assert BasicStats("El gato duerme.\r\nEl perro come.").n_chars == (
        BasicStats("El gato duerme.\nEl perro come.").n_chars
    )


def test_custom_extractors():
    import re

    from ests import SentsExtractor, WordsExtractor

    bs = BasicStats(
        "uno, dos; tres, cuatro",
        sents_extractor=SentsExtractor(tokenizer=re.compile(r"; ")),
        words_extractor=WordsExtractor(tokenizer=re.compile(r"[,; ]+")),
    )
    assert bs.n_sents == 2
    assert bs.n_words == 4


def test_doc_without_sentence_boundaries(bs):
    doc = spacy.blank("es")(TEXT)
    assert not doc.has_annotation("SENT_START")
    doc_stats = BasicStats(doc, normalize=True)
    assert doc_stats.get_stats() == bs.get_stats()


def test_doc_with_sentence_boundaries(bs, nlp):
    doc_stats = BasicStats(nlp(TEXT), normalize=True)
    assert doc_stats.n_sents == 2
    assert doc_stats.get_stats() == bs.get_stats()


def test_doc_words(nlp):
    doc = nlp("El 3.º costó 1.500,50 €; EE. UU. teórico-práctico 10%.")
    doc_stats = BasicStats(doc)
    assert doc_stats.n_words == 7
    # the ordinal indicator of 3.º is a letter for str.isalpha, EE. UU. has four
    assert doc_stats.c_letters == {0: 2, 1: 1, 2: 1, 4: 1, 5: 1, 15: 1}
    # marks are counted in the text, so the periods of 3.º, 1.500,50 and EE. UU. count
    assert doc_stats.n_punctuations == 10
    assert {kind: count for kind, count in doc_stats.c_punctuations.items() if count} == {
        "comma": 1,
        "period": 5,
        "semicolon": 1,
        "hyphen": 1,
        "other": 2,
    }


def test_doc_with_extractors(nlp):
    """An extractor passed explicitly is used for a Doc too, on its text"""
    from ests import SentsExtractor, WordsExtractor

    doc = nlp("Los tesauros son una clase. Los TESAUROS son una clase.")
    words_extractor = WordsExtractor(stopwords=["los", "una"], lowercase=True)
    stats = BasicStats(doc, words_extractor=words_extractor)
    assert stats.n_words == BasicStats(doc.text, words_extractor=words_extractor).n_words == 6
    sents_extractor = SentsExtractor(min_len=1000)
    assert BasicStats(doc, words_extractor=words_extractor, sents_extractor=sents_extractor)
    assert BasicStats(doc, sents_extractor=SentsExtractor()).n_sents == 2


def test_doc_without_words():
    with pytest.raises(ValueError):
        BasicStats(spacy.blank("es")("... !"))


def test_get_stats(bs):
    stats = bs.get_stats()
    assert isinstance(stats, dict)
    for key in BASIC_STATS_DESC:
        assert stats[key] == getattr(bs, key)
    stats["n_words"] = -1
    stats["c_letters"][1] = -1
    assert bs.n_words > 0 and bs.c_letters[1] == 4


def test_print_stats(capsys, bs, monkeypatch):
    calls = []
    original = BasicStats.get_stats

    def counting(self):
        calls.append(1)
        return original(self)

    monkeypatch.setattr(BasicStats, "get_stats", counting)
    bs.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == 14
    assert "Sentences" in captured.out
    assert len(calls) == 1
