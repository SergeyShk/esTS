from math import isnan

import pytest
import spacy

from ests import MorphStats
from ests.constants import MORPHOLOGY_FEATURES, MORPHOLOGY_MARKERS_DESC, MORPHOLOGY_STATS_DESC
from ests.exceptions import SourceError, SourceTypeError, UnknownStatError
from ests.utils import get_nlp

TEXT = (
    "El gato duerme en la ventana mientras los niños juegan. "
    "Si tuviera tiempo, leería el libro que me recomendaste ayer, pero no lo tengo. "
    "Ella está cansada y él es alto, aunque hable rápidamente."
)


@pytest.fixture(scope="module")
def ms():
    return MorphStats(TEXT)


@pytest.fixture(scope="module")
def short():
    return MorphStats("Los niños juegan alegremente")


def test_words(short):
    assert short.words == ("Los", "niños", "juegan", "alegremente")


def test_lemmas(short):
    assert short.lemmas == ("el", "niño", "jugar", "alegremente")


def test_tags(short):
    assert short.tags == (
        "Definite=Def|Gender=Masc|Number=Plur|PronType=Art",
        "Gender=Masc|Number=Plur",
        "Mood=Ind|Number=Plur|Person=3|Tense=Pres|VerbForm=Fin",
        "_",
    )


def test_pos(short):
    assert short.pos == ("DET", "NOUN", "VERB", "ADV")


def test_polite():
    ms = MorphStats("Pase usted primero")
    assert "Form" in ms.polite


def test_features(short):
    assert short.number == ("Plur", "Plur", "Plur", None)
    assert short.person == (None, None, "3", None)
    assert short.definite == ("Def", None, None, None)
    assert short.gender == ("Masc", "Masc", None, None)
    assert short.mood == (None, None, "Ind", None)
    assert short.tense == (None, None, "Pres", None)
    assert short.verb_form == (None, None, "Fin", None)
    assert short.pron_type == ("Art", None, None, None)


@pytest.mark.parametrize("stat", MORPHOLOGY_FEATURES)
def test_feature_length(ms, stat):
    assert len(getattr(ms, stat)) == len(ms.words)


@pytest.mark.parametrize(
    ("text", "stat", "expected"),
    [
        ("No lo sé", "polarity", "Neg"),
        ("Es mi libro", "poss", "Yes"),
        ("Se lava las manos", "reflex", "Yes"),
        ("Compré dos libros", "num_type", "Card"),
        ("Es el mejor libro", "degree", "Cmp"),
        ("Es un libro buenísimo", "degree", "Abs"),
        ("Ella lo ve", "case", "Acc"),
        ("Ese libro es mío", "pron_type", "Dem"),
        ("Algunos libros son tuyos", "pron_type", "Ind"),
    ],
)
def test_feature_values(text, stat, expected):
    assert expected in getattr(MorphStats(text), stat)


def test_multiple_values():
    assert "Int,Rel" in MorphStats("No sé qué quieres").pron_type


def test_punctuations_and_symbols_dropped():
    ms = MorphStats("El 50 % de los libros, ¡vaya!")
    assert ms.words == ("El", "50", "de", "los", "libros", "vaya")


def test_doc_source(ms):
    assert MorphStats(get_nlp()(TEXT)).tags == ms.tags


def test_nlp_parameter(ms):
    assert MorphStats(TEXT, nlp=get_nlp()).tags == ms.tags


@pytest.mark.parametrize("source", [1, ["El", "gato"], None, spacy.blank("es")])
def test_source_type_error(source):
    with pytest.raises(SourceTypeError):
        MorphStats(source)


@pytest.mark.parametrize("source", ["", "   ", "¡¿...!"])
def test_source_without_words(source):
    with pytest.raises(SourceError, match="no words"):
        MorphStats(source)


def test_source_too_long():
    nlp = get_nlp()
    with pytest.raises(SourceError, match="longer than the limit"):
        MorphStats("hola " * (nlp.max_length // 4), nlp=nlp)


def test_source_without_annotation():
    with pytest.raises(SourceError, match="parts of speech"):
        MorphStats(spacy.blank("es")("Los niños juegan"))


def test_get_stats_all(ms):
    assert tuple(ms.get_stats()) == tuple(MORPHOLOGY_STATS_DESC)


def test_get_stats_selected(short):
    assert short.get_stats("pos", "number") == {
        "pos": {"DET": 1, "NOUN": 1, "VERB": 1, "ADV": 1},
        "number": {"Plur": 3, None: 1},
    }


def test_get_stats_filter_none(short):
    assert short.get_stats("number", filter_none=True) == {"number": {"Plur": 3}}


def test_get_stats_counts_words(ms):
    assert sum(ms.get_stats("pos")["pos"].values()) == len(ms.words)


def test_get_stats_unknown():
    with pytest.raises(UnknownStatError, match="lemma"):
        MorphStats("Los niños juegan").get_stats("lemma")


def test_explain_text(short):
    assert short.explain_text("pos", "mood") == (
        ("Los", {"pos": "DET", "mood": None}),
        ("niños", {"pos": "NOUN", "mood": None}),
        ("juegan", {"pos": "VERB", "mood": "Ind"}),
        ("alegremente", {"pos": "ADV", "mood": None}),
    )


def test_explain_text_filter_none(short):
    assert short.explain_text("pos", "mood", filter_none=True)[0] == ("Los", {"pos": "DET"})


def test_explain_text_all(ms):
    explained = ms.explain_text()
    assert len(explained) == len(ms.words)
    assert tuple(explained[0][1]) == tuple(MORPHOLOGY_STATS_DESC)


def test_explain_text_unknown(short):
    with pytest.raises(UnknownStatError, match="tags"):
        short.explain_text("tags")


def test_markers(ms):
    markers = ms.get_markers()
    assert tuple(markers) == tuple(MORPHOLOGY_MARKERS_DESC)
    assert markers["p_indicative"] == pytest.approx(6 / 9)
    assert markers["p_subjunctive"] == pytest.approx(2 / 9)
    assert markers["p_conditional"] == pytest.approx(1 / 9)
    assert markers["p_ser"] == pytest.approx(0.5)
    assert markers["p_mente_adverbs"] == pytest.approx(1 / 3)


def test_markers_moods_sum_to_one(ms):
    markers = ms.get_markers()
    assert sum(markers[marker] for marker in ("p_indicative", "p_subjunctive")) + sum(
        markers[marker] for marker in ("p_conditional", "p_imperative")
    ) == pytest.approx(1)


def test_markers_non_finite():
    markers = MorphStats("Quiero leer un libro escrito cantando").get_markers()
    assert markers["p_infinitive"] == pytest.approx(1 / 3)
    assert markers["p_gerund"] == pytest.approx(1 / 3)
    assert markers["p_indicative"] == pytest.approx(1)


def test_markers_adjectival_participle_ignored():
    ms = MorphStats("La casa blanca está pintada")
    assert "Part" in ms.verb_form
    assert ms.get_markers()["p_participle"] == 0


def test_markers_verbal_participle_counted():
    ms = MorphStats("He leído el libro")
    assert ms.get_markers()["p_participle"] == pytest.approx(0.5)


@pytest.mark.parametrize(
    ("text", "marker"),
    [
        ("La casa blanca", "p_indicative"),
        ("La casa blanca", "p_infinitive"),
        ("Los niños juegan", "p_ser"),
        ("Los niños juegan", "p_mente_adverbs"),
    ],
)
def test_markers_without_base(text, marker):
    assert isnan(MorphStats(text).get_markers()[marker])


@pytest.mark.parametrize(
    "text",
    [
        "El libro fue escrito por Cervantes y ha sido leído por todos",
        "Ella está cantando y él está comiendo",
    ],
)
def test_markers_auxiliaries_are_not_copulas(text):
    ms = MorphStats(text)
    assert "ser" in ms.lemmas or "estar" in ms.lemmas
    assert isnan(ms.get_markers()["p_ser"])


def test_markers_copulas():
    assert MorphStats("Ella es alta pero hoy está cansada").get_markers()["p_ser"] == 0.5


def test_markers_ser_without_parse():
    doc = get_nlp()("Ella es alta pero hoy está cansada", disable=["parser"])
    assert not doc.has_annotation("DEP")
    assert isnan(MorphStats(doc).get_markers()["p_ser"])


def test_print_stats(short, capsys):
    short.print_stats("pos")
    assert capsys.readouterr().out == (
        "-------------Part of speech-------------\n"
        "Determiner                    |    1     \n"
        "Noun                          |    1     \n"
        "Verb                          |    1     \n"
        "Adverb                        |    1     \n"
        "\n"
    )


def test_print_stats_filter_none(short, capsys):
    short.print_stats("number", filter_none=True)
    assert "Unknown" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("text", "stat", "expected"),
    [
        ("No sé qué quieres", "pron_type", "Interrogative or relative"),
        ("Usted lo ve", "case", "Accusative or nominative"),
    ],
)
def test_print_stats_combined_value(text, stat, expected, capsys):
    MorphStats(text).print_stats(stat, filter_none=True)
    assert expected in capsys.readouterr().out


def test_print_stats_unknown_value(short, capsys):
    ms = MorphStats("Los niños juegan")
    ms.number = ("Dual",) * len(ms.words)
    ms.print_stats("number")
    assert "Dual" in capsys.readouterr().out


def test_print_stats_all(ms, capsys):
    ms.print_stats()
    out = capsys.readouterr().out
    assert all(str(desc["name"]) in out for desc in MORPHOLOGY_STATS_DESC.values())


def test_print_stats_unknown(short):
    with pytest.raises(UnknownStatError):
        short.print_stats("tags")


def test_print_markers(short, capsys):
    short.print_markers()
    out = capsys.readouterr().out.splitlines()
    assert out[0].split("|") == ["                     Marker                    ", "   Value   "]
    assert out[2] == "Indicative among the finite forms              |   1.00    "
    assert out[-1] == "Adverbs in -mente among the adverbs            |   1.00    "
    assert out[-2] == "ser among the copulas ser and estar            |    nan    "
