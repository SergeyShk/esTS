import random
from math import isnan

import pytest
import spacy

from ests import CohesionStats, SentsExtractor
from ests.cohesion_stats import (
    Connector,
    _count_sharing_pairs,
    _sum_dice,
    calc_overlap,
    calc_overlaps,
    calc_proportional_overlap,
    calc_repetition,
    count_given,
    dice,
    dominant,
    find_connectors,
    load_connectors,
    split_doc_sents,
    token_info,
)
from ests.constants import COHESION_STATS_DESC, CONNECTOR_CLASSES, CONNECTOR_TYPES
from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp

TEXT = (
    "El gato estaba en la ventana. Miraba a los pájaros. "
    "Sin embargo, los pájaros se fueron y el gato se durmió."
)


@pytest.fixture(scope="module")
def nlp():
    return get_nlp()


@pytest.fixture(scope="module")
def cs():
    return CohesionStats(TEXT)


def test_words_and_lemmas(cs):
    assert cs.words[1] == ("Miraba", "a", "los", "pájaros")
    assert cs.lemmas[1] == ("mirar", "a", "el", "pájaro")


def test_counts(cs):
    assert cs.n_sents == 3
    assert cs.n_words == sum(len(sent) for sent in cs.words)
    assert cs.n_nouns == 6
    assert cs.n_content_words == 10


def test_get_stats(cs):
    assert tuple(cs.get_stats()) == tuple(COHESION_STATS_DESC)


def test_overlaps(cs):
    assert cs.noun_overlap_adjacent == 0.5
    assert cs.noun_overlap_all == pytest.approx(2 / 3)
    assert cs.argument_overlap_adjacent == 0.5
    assert cs.content_overlap_adjacent == 0.5


def test_temporal_cohesion(cs):
    assert cs.tense_repetition == 0.5
    assert cs.mood_repetition == 1
    assert cs.temporal_cohesion == 0.75


def test_connectors(cs):
    assert cs.connector_spans == (
        Connector(sent=2, start=0, end=2, text="sin embargo", cls="adversative", kind="secondary"),
        Connector(sent=2, start=6, end=7, text="y", cls="additive", kind="primary"),
    )
    assert cs.c_connectors == {"sin embargo": 1, "y": 1}
    assert cs.n_connectors == 2
    assert cs.connectors == pytest.approx(2000 / cs.n_words)
    assert cs.connectors_adversative == pytest.approx(1000 / cs.n_words)
    assert cs.connectors_primary == pytest.approx(1000 / cs.n_words)
    assert cs.connectors_secondary == pytest.approx(1000 / cs.n_words)


def test_pronouns_exclude_articles():
    cs = CohesionStats("El libro es mío. Este libro me gusta. Yo lo leí.")
    assert cs.n_pronouns == 5
    assert cs.n_demonstratives == 1
    assert cs.p_demonstratives == pytest.approx(1 / cs.n_words)


def test_noun_inside_a_connector_counts(cs):
    assert "embargo" in cs.lemmas[2]
    assert "embargo" in {lemma for sent in cs.lemmas for lemma in sent}


def test_given():
    cs = CohesionStats("El gato duerme en la casa. El gato come en la casa. La ventana es blanca.")
    assert cs.n_given == 2
    assert cs.p_given == pytest.approx(2 / cs.n_content_words)


def test_print_stats(cs, capsys):
    cs.print_stats()
    out = capsys.readouterr().out.splitlines()
    assert out[0].split("|")[1] == "  Value   "
    assert out[1] == "-" * 68
    assert len(out) == len(COHESION_STATS_DESC) + 2
    assert out[2] == f"{'Noun overlap in adjacent sentences':58}|{0.5:^10.2f}"


def test_doc_source(cs, nlp):
    assert CohesionStats(nlp(TEXT)).get_stats() == cs.get_stats()


def test_nlp_parameter(cs, nlp):
    assert CohesionStats(TEXT, nlp=nlp).get_stats() == cs.get_stats()


def test_doc_without_sentence_boundaries():
    tagged = spacy.load("es_core_news_sm", exclude=["parser"])
    doc = tagged("El gato duerme. Los niños juegan mucho.")
    assert not doc.has_annotation("SENT_START")
    cs = CohesionStats(doc)
    assert cs.words == (("El", "gato", "duerme"), ("Los", "niños", "juegan", "mucho"))


def test_doc_without_sentence_boundaries_and_extractor():
    tagged = spacy.load("es_core_news_sm", exclude=["parser"])
    doc = tagged("El gato duerme. Los niños juegan mucho.")
    cs = CohesionStats(doc, sents_extractor=SentsExtractor(min_len=20))
    assert cs.n_sents == 1


@pytest.mark.parametrize("source", [1, ["El", "gato"], None, spacy.blank("es")])
def test_source_type_error(source):
    with pytest.raises(SourceTypeError):
        CohesionStats(source)


@pytest.mark.parametrize("source", ["", "   ", "¡¿...!"])
def test_source_without_words(source):
    with pytest.raises(SourceError, match="no words"):
        CohesionStats(source)


def test_source_without_annotation():
    with pytest.raises(SourceError, match="parts of speech"):
        CohesionStats(spacy.blank("es")("El gato duerme"))


def test_source_too_long(nlp):
    with pytest.raises(SourceError, match="longer than the limit"):
        CohesionStats("hola " * (nlp.max_length // 4), nlp=nlp)


def test_single_sentence():
    cs = CohesionStats("El gato duerme en la ventana")
    assert cs.n_sents == 1
    assert isnan(cs.noun_overlap_adjacent)
    assert isnan(cs.noun_overlap_all)
    assert isnan(cs.content_overlap_prop_adjacent)
    assert isnan(cs.tense_repetition)
    assert isnan(cs.temporal_cohesion)


def test_text_without_nouns():
    cs = CohesionStats("Duerme mucho. Trabaja bien.")
    assert cs.n_nouns == 0
    assert isnan(cs.pronoun_noun_ratio)


def test_custom_connectors():
    cs = CohesionStats(TEXT, connectors={"sin embargo": ("causal", "primary")})
    assert cs.c_connectors == {"sin embargo": 1}
    assert cs.connectors_causal == pytest.approx(1000 / cs.n_words)
    assert cs.connectors_additive == 0


@pytest.mark.parametrize(
    "connectors",
    [{"y": ("unknown", "primary")}, {"y": ("additive", "unknown")}],
)
def test_unknown_connector_class(connectors):
    with pytest.raises(ParameterError, match="Unknown class or kind"):
        CohesionStats(TEXT, connectors=connectors)


def test_load_connectors():
    connectors = load_connectors()
    assert len(connectors) == 255
    assert connectors["sin embargo"] == ("adversative", "secondary")
    assert all(cls in CONNECTOR_CLASSES for cls, _ in connectors.values())
    assert all(kind in CONNECTOR_TYPES for _, kind in connectors.values())


def test_load_connectors_cached():
    assert load_connectors() is load_connectors()


def test_find_connectors_longest_match():
    assert [c.text for c in find_connectors(["Sin", "embargo", "no", "vino"])] == ["sin embargo"]


def test_find_connectors_do_not_overlap():
    found = find_connectors(["por", "lo", "tanto", "y", "además"])
    assert [(c.start, c.end, c.text) for c in found] == [
        (0, 3, "por lo tanto"),
        (3, 4, "y"),
        (4, 5, "además"),
    ]


def test_find_connectors_period_variant():
    assert [c.text for c in find_connectors(["p", "ej", "el", "agua"])] == ["p. ej."]


def test_find_connectors_pos_filter():
    words = ["El", "antes", "y", "el", "después"]
    pos = ["DET", "NOUN", "CCONJ", "DET", "NOUN"]
    assert [c.text for c in find_connectors(words, pos=pos)] == ["y"]
    assert [c.text for c in find_connectors(words)] == ["antes", "y", "después"]


def test_find_connectors_pos_extra():
    assert [c.text for c in find_connectors(["Resumiendo"], pos=["VERB"])] == ["resumiendo"]
    assert find_connectors(["Duerme"], pos=["VERB"]) == []


def test_find_connectors_sent_index():
    found = find_connectors(["además"], sent_index=3)
    assert found[0].sent == 3


def test_find_connectors_of_a_punctuation_connector():
    assert find_connectors(["y", "así"], connectors={".": ("additive", "primary")}) == []


def test_find_connectors_custom():
    found = find_connectors(["bueno"], connectors={"bueno": ("additive", "primary")})
    assert found[0] == Connector(0, 0, 1, "bueno", "additive", "primary")


def test_token_info(nlp):
    tokens = {token.text: token for token in nlp("Este libro me gusta mucho")}
    assert token_info(tokens["libro"]).noun
    assert token_info(tokens["Este"]).demonstrative
    assert token_info(tokens["me"]).pronoun
    assert token_info(tokens["gusta"]).tense == "Pres"
    assert token_info(tokens["gusta"]).mood == "Ind"
    assert not token_info(tokens["Este"]).content


def test_split_doc_sents(nlp):
    doc = nlp("El gato duerme. Los niños juegan.")
    sents = split_doc_sents(doc, SentsExtractor())
    assert [[token.text for token in sent] for sent in sents] == [
        ["El", "gato", "duerme"],
        ["Los", "niños", "juegan"],
    ]


def test_split_doc_sents_of_a_sentence_outside_the_text(nlp):
    doc = nlp("El gato duerme. Los niños juegan.")
    extractor = SentsExtractor(tokenizer=lambda text: ["El perro corre.", "Los niños juegan."])
    sents = split_doc_sents(doc, extractor)
    assert [[token.text for token in sent] for sent in sents] == [["Los", "niños", "juegan"]]


def test_split_doc_sents_without_sentences(nlp):
    assert split_doc_sents(nlp("El gato duerme"), SentsExtractor(min_len=50)) == []


@pytest.mark.parametrize(
    ("sets", "adjacent", "expected"),
    [
        ([{"a"}, {"a"}, {"b"}], True, 0.5),
        ([{"a"}, {"a"}, {"b"}], False, 1 / 3),
        ([{"a"}], True, None),
        ([{"a", "b"}, {"b", "c"}], True, 1.0),
    ],
)
def test_calc_overlap(sets, adjacent, expected):
    value = calc_overlap(sets, adjacent)
    assert isnan(value) if expected is None else value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("sets", "adjacent", "expected"),
    [
        ([{"a", "b"}, {"b", "c"}], True, 0.5),
        ([{"a"}, {"a"}, {"b"}], False, 1 / 3),
        ([{"a"}], False, None),
        ([set(), set()], True, 0.0),
    ],
)
def test_calc_proportional_overlap(sets, adjacent, expected):
    value = calc_proportional_overlap(sets, adjacent)
    assert isnan(value) if expected is None else value == pytest.approx(expected)


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ({"a", "b"}, {"b", "c"}, 0.5),
        ({"a"}, {"a"}, 1.0),
        ({"a"}, {"b"}, 0.0),
        (set(), set(), 0.0),
    ],
)
def test_dice(first, second, expected):
    assert dice(frozenset(first), frozenset(second)) == pytest.approx(expected)


def test_calc_overlaps_matches_the_direct_computation():
    random.seed(17)
    sets = [{str(random.randrange(12)) for _ in range(random.randrange(5))} for _ in range(40)]
    overlap = calc_overlaps(sets)
    assert overlap.adjacent == pytest.approx(calc_overlap(sets))
    assert overlap.all == pytest.approx(calc_overlap(sets, adjacent=False))
    assert overlap.prop_adjacent == pytest.approx(calc_proportional_overlap(sets))
    assert overlap.prop_all == pytest.approx(calc_proportional_overlap(sets, adjacent=False))


def test_calc_overlaps_of_a_single_sentence():
    assert all(isnan(value) for value in calc_overlaps([{"a"}]))


def test_count_sharing_pairs_in_blocks():
    sets = [frozenset({"a"}), frozenset({"a"}), frozenset({"b"}), frozenset({"a", "b"})]
    assert _count_sharing_pairs(sets) == _count_sharing_pairs(sets, block_size=2) == 4


def test_sum_dice_without_shared_elements():
    assert _sum_dice([frozenset({"a"}), frozenset({"b"}), frozenset()]) == 0


def test_count_given():
    assert count_given([["a", "b"], ["b", "c"], ["a"]]) == 2


def test_count_given_inside_a_sentence():
    assert count_given([["a", "a", "a"]]) == 2


@pytest.mark.parametrize(
    ("values", "expected"),
    [(["a", "b", "a"], "a"), (["a", "b"], "a"), ([], None)],
)
def test_dominant(values, expected):
    assert dominant(values) == expected


@pytest.mark.parametrize(
    ("sents", "expected"),
    [
        ([["Pres"], ["Pres"], ["Past"]], 0.5),
        ([["Pres"], [], ["Pres"]], None),
        ([["Pres", "Past", "Past"], ["Past"]], 1.0),
        ([[], []], None),
    ],
)
def test_calc_repetition(sents, expected):
    value = calc_repetition(sents)
    assert isnan(value) if expected is None else value == pytest.approx(expected)
