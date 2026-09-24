import pytest
import spacy

from ests.corpus import Concordance, format_kwic, kwic, print_kwic
from ests.exceptions import ParameterError, SourceTypeError
from ests.utils import get_nlp

text = (
    "El gato estaba en la ventana. Al gato lo llamaban Tom, y los gatos querían la ventana. "
    "Porque el gato dormía."
)


def test_kwic():
    assert kwic(text, "gato", window=2) == [
        Concordance(3, 7, "El", "gato", "estaba en"),
        Concordance(33, 37, "ventana. Al", "gato", "lo llamaban"),
        Concordance(97, 101, "Porque el", "gato", "dormía"),
    ]


def test_kwic_without_context():
    assert kwic(text, "gato", window=0) == [
        Concordance(3, 7, "", "gato", ""),
        Concordance(33, 37, "", "gato", ""),
        Concordance(97, 101, "", "gato", ""),
    ]


def test_kwic_by_case():
    assert [line.keyword for line in kwic("Gato y gato", "gato")] == ["Gato", "gato"]
    assert [line.keyword for line in kwic("Gato y gato", "gato", ignore_case=False)] == ["gato"]


def test_kwic_by_lemma():
    assert [line.keyword for line in kwic(text, "gato", by_lemma=True)] == [
        "gato",
        "gato",
        "gatos",
        "gato",
    ]
    assert kwic(text, "gatos", by_lemma=True) == kwic(text, "gato", by_lemma=True)


def test_kwic_of_a_phrase():
    expected = [Concordance(67, 85, "gatos", "querían la ventana", ". Porque")]
    assert kwic(text, "querían la ventana", window=1) == expected
    assert kwic(text, "querer la ventana", window=1, by_lemma=True) == expected


def test_kwic_of_an_absent_word():
    assert kwic(text, "perro") == []


def test_kwic_does_not_overlap():
    assert kwic("gato gato gato", "gato gato") == [Concordance(0, 9, "", "gato gato", "gato")]


def test_kwic_collapses_whitespace():
    assert kwic("El gato:\n\n  «duerme» tranquilo", "duerme", window=1) == [
        Concordance(13, 19, "gato: «", "duerme", "» tranquilo")
    ]
    assert kwic("gato\n\tduerme en la cama", "gato duerme", window=1) == [
        Concordance(0, 12, "", "gato duerme", "en")
    ]


def test_kwic_of_a_blank_doc():
    assert kwic(spacy.blank("es")(text), "gato", window=2) == kwic(text, "gato", window=2)


def test_kwic_of_a_doc_with_lemmas():
    doc = get_nlp()("Mi amigo vino con una botella de vino.")
    assert [(line.start, line.keyword) for line in kwic(doc, "venir", by_lemma=True)] == [
        (9, "vino")
    ]
    assert [line.start for line in kwic(doc, "vino", by_lemma=True)] == [9, 33]
    assert kwic(doc.text, "venir", by_lemma=True) == []


@pytest.mark.parametrize(
    ("keyword", "expected"),
    [
        ("venir", ["vendrían", "vinieron"]),
        ("vendrían", ["vendrían", "vinieron"]),
        ("poner", ["pusiste"]),
    ],
)
def test_kwic_of_a_doc_finds_what_the_model_misreads(keyword, expected):
    text = "Ellas dijeron que vendrían mañana, pero no vinieron. ¿Dónde pusiste las llaves?"
    doc = get_nlp()(text)
    assert [line.keyword for line in kwic(doc, keyword, by_lemma=True)] == expected
    assert {line.keyword for line in kwic(text, keyword, by_lemma=True)} <= set(expected)


def test_kwic_of_a_doc_finds_every_word_by_its_own_form():
    text = "Ellas dijeron que vendrían mañana, pero no vinieron. ¿Dónde pusiste las llaves?"
    doc = get_nlp()(text)
    for word in ("dijeron", "vendrían", "vinieron", "pusiste", "llaves"):
        assert word in [line.keyword for line in kwic(doc, word, by_lemma=True)]


@pytest.mark.parametrize(
    ("text", "keyword", "expected"),
    [
        ("Viajó a EE. UU. en mayo.", "EE. UU.", "EE. UU."),
        ("¿Dónde está?", "¿Dónde", "Dónde"),
        ("Pagó 20 € por él.", "20 €", "20"),
    ],
)
def test_kwic_splits_the_keyword_like_the_text(text, keyword, expected):
    assert [line.keyword for line in kwic(text, keyword)] == [expected]
    assert [line.keyword for line in kwic(get_nlp()(text), keyword)] == [expected]


def test_kwic_of_a_wrong_source():
    with pytest.raises(SourceTypeError):
        kwic(["gato"], "gato")


@pytest.mark.parametrize(("keyword", "window"), [("  ", 5), ("¿?", 5), ("gato", -1)])
def test_kwic_errors(keyword, window):
    with pytest.raises(ParameterError):
        kwic(text, keyword, window=window)


def test_format_kwic():
    lines = kwic(text, "gato", window=2, by_lemma=True)
    assert format_kwic(lines, width=10).split("\n") == [
        "        El  gato   estaba en",
        "entana. Al  gato   lo llamaba",
        "     y los  gatos  querían la",
        " Porque el  gato   dormía",
    ]
    assert format_kwic([]) == ""
    assert format_kwic(kwic("gato\nduerme", "gato duerme"), width=1).split("\n") == [
        "   gato duerme  "
    ]


@pytest.mark.parametrize("width", [0, -1])
def test_format_kwic_errors(width):
    with pytest.raises(ParameterError):
        format_kwic(kwic(text, "gato"), width=width)


def test_print_kwic(capsys):
    lines = kwic(text, "gato", window=2)
    print_kwic(lines, width=10)
    assert capsys.readouterr().out == format_kwic(lines, width=10) + "\n"
