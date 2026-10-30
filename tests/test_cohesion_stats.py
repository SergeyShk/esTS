import pickle
from math import isnan

import pytest
import spacy

from ests import CohesionStats, SentsExtractor
from ests.cohesion_stats import (
    Connector,
    find_connectors,
    is_connector_blocked,
    load_connectors,
    token_info,
)
from ests.constants import (
    COHESION_STATS_DESC,
    CONNECTOR_CLASSES,
    CONNECTOR_PARCELLATION,
    CONNECTOR_SPLIT_BY_MARKS,
    CONNECTOR_SUBORDINATORS,
    CONNECTOR_TYPES,
)
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
    # sin embargo opens its sentence and links it to the one before
    assert cs.connectors_inter == pytest.approx(1000 / cs.n_words)
    assert cs.connectors_intra == pytest.approx(1000 / cs.n_words)


def test_connectors_by_place():
    cs = CohesionStats("No vino. Porque llovía. Ya que estás aquí, ayúdame. Cuando llegue, avisa.")
    assert [c.text for c in cs.connector_spans] == ["porque", "ya que", "cuando"]
    # porque opens a sentence linking it to the one before; ya que and cuando, their clause
    assert cs.n_inter_connectors == 1
    assert cs.connectors_intra == pytest.approx(2000 / cs.n_words)


@pytest.mark.parametrize(
    ("words", "pos", "expected"),
    [
        (["Ya", "que", "estás", "aquí"], "ADV", True),
        (["A", "pesar", "de", "la", "lluvia"], "ADP", True),
        (["A", "pesar", "de", "todo"], "ADP", False),
        (["Cuando", "llegó"], "SCONJ", True),
        (["Porque", "llovía"], "SCONJ", False),
        (["Conque", "vayamos"], "SCONJ", False),
        (["Sin", "embargo", "no"], "ADP", False),
    ],
)
def test_subordinators(words, pos, expected):
    matcher = CohesionStats.connector_matcher()
    assert matcher.is_subordinator(matcher.find(words)[0], pos) is expected


@pytest.mark.parametrize(
    ("text", "found", "inter"),
    [
        ("Llovía. A pesar de todo, salimos.", ["a pesar de todo"], 1),
        ("Llovía. A pesar de todo el esfuerzo, salimos.", ["a pesar de"], 0),
        ("Llovía. A pesar de todo lo que hizo, salimos.", ["a pesar de"], 0),
        ("Llovía. Pese a todo ello, salimos.", ["pese a todo"], 1),
        ("Llovía. Gracias a ello, nos quedamos.", ["gracias a ello"], 1),
    ],
)
def test_anaphoric_forms_link_to_the_sentence_before(text, found, inter):
    cs = CohesionStats(text)
    assert [c.text for c in cs.connector_spans] == found
    assert cs.n_inter_connectors == inter


@pytest.mark.parametrize("determiner", ["el", "mi", "nuestro", "vuestras", "aquellos"])
def test_anaphoric_form_before_a_noun_phrase_of_a_string(determiner):
    found = find_connectors(["A", "pesar", "de", "todo", determiner, "esfuerzo"])
    assert [c.text for c in found] == ["a pesar de"]


def test_consecutive_connector_after_a_comma():
    # old texts put a comma before the que of a consecutive connector
    cs = CohesionStats("Se enfureció de tal modo, que gritó.")
    assert [c.text for c in cs.connector_spans] == ["de tal modo que"]


def test_lists_of_the_connectors_are_in_the_dictionary():
    connectors = load_connectors()
    lists = (CONNECTOR_SUBORDINATORS, CONNECTOR_PARCELLATION, CONNECTOR_SPLIT_BY_MARKS)
    assert all(text in connectors for texts in lists for text in texts)


def test_pronouns_exclude_articles():
    cs = CohesionStats("El libro es mío. Este libro me gusta. Yo lo leí.")
    assert cs.n_pronouns == 5
    assert cs.n_demonstratives == 1


def test_pronouns_exclude_quantifiers():
    cs = CohesionStats("Cada libro tiene su autor. Todos los libros son suyos. Este libro es mío.")
    assert cs.n_pronouns == 4
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
    assert [cell.strip() for cell in out[0].split("|")] == ["Statistic", "Value"]
    assert set(out[1]) == {"-"}
    assert len(out) == len(COHESION_STATS_DESC) + 2
    assert [cell.strip() for cell in out[2].split("|")] == [
        "Noun overlap in adjacent sentences",
        "0.50",
    ]


def test_rules_do_not_read_across_a_comma():
    # «y» after a determiner is no connector, but a comma between them breaks the rule
    cs = CohesionStats("Su padre tiene un hijo feo y sin gracia alguna, y el amor le ciega.")
    assert [(c.text, c.start) for c in cs.connector_spans] == [("y", 6), ("y", 10)]


def test_pipeline_is_not_pickled(nlp):
    cs = CohesionStats(TEXT, nlp=nlp)
    restored = pickle.loads(pickle.dumps(cs))
    assert "_nlp" not in vars(restored)
    assert repr(restored.get_stats()) == repr(cs.get_stats())


def test_doc_source(cs, nlp):
    assert CohesionStats(nlp(TEXT)).get_stats() == cs.get_stats()


def test_nlp_parameter(cs, nlp):
    assert CohesionStats(TEXT, nlp=nlp).get_stats() == cs.get_stats()


def test_sents_extractor_of_a_string():
    text = "El gato duerme. Los niños juegan."
    assert CohesionStats(text).n_sents == 2
    assert CohesionStats(text, sents_extractor=SentsExtractor(min_len=16)).n_sents == 1


def test_sents_extractor_of_a_parsed_doc(nlp):
    doc = nlp("El gato duerme. Los niños juegan.")
    assert CohesionStats(doc).n_sents == 2
    assert CohesionStats(doc, sents_extractor=SentsExtractor(min_len=16)).n_sents == 1


def test_doc_without_sentence_boundaries():
    tagged = spacy.load("es_core_news_sm", exclude=["parser"])
    doc = tagged("El gato duerme. Los niños juegan mucho.")
    assert not doc.has_annotation("SENT_START")
    cs = CohesionStats(doc)
    assert cs.words == (("El", "gato", "duerme"), ("Los", "niños", "juegan", "mucho"))


def test_doc_without_sentence_boundaries_and_extractor():
    tagged = spacy.load("es_core_news_sm", exclude=["parser"])
    doc = tagged("El gato duerme. Los niños juegan mucho.")
    cs = CohesionStats(doc, sents_extractor=SentsExtractor(min_len=16))
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
    with pytest.raises(SourceError, match="parts of speech: parse the text with a model"):
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
    assert len(connectors) == 273
    assert connectors["sin embargo"] == ("adversative", "secondary")
    assert all(cls in CONNECTOR_CLASSES for cls, _ in connectors.values())
    assert all(kind in CONNECTOR_TYPES for _, kind in connectors.values())


def test_load_connectors_cached():
    assert load_connectors() is load_connectors()


def test_load_connectors_is_read_only():
    with pytest.raises(TypeError):
        load_connectors()["ojalá"] = ("temporal", "primary")  # type: ignore[index]


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("Pues bien no vino", []),
        ("No vino pues estaba enfermo", ["pues"]),
        ("En cuanto a la casa", []),
        ("En cuanto llegó se fue", ["en cuanto"]),
        ("Y encima llueve", ["y", "encima"]),
        ("Encima llueve", ["encima"]),
        ("Está encima de la mesa", []),
        ("Pasó por encima", []),
        ("Es algo así como un perro", []),
        ("Así como los gatos", ["así como"]),
    ],
)
def test_find_connectors_in_context(text, found):
    """A marker that opens a reply or belongs to a phrase of its own is no connector"""
    assert [c.text for c in find_connectors(text.split())] == found


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
    pos = ["DET", "ADV", "CCONJ", "DET", "ADV"]
    assert [c.text for c in find_connectors(words, pos=pos)] == ["y"]
    assert [c.text for c in find_connectors(words)] == ["antes", "y", "después"]


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("El antes y el después no importan.", ["y"]),
        ("Habló con Juan Luego ayer.", []),
        ("Resumiendo, el texto es claro.", ["resumiendo"]),
        ("Primeramente, hay que leer.", ["primeramente"]),
    ],
)
def test_connector_spans_of_a_parsed_text(text, expected):
    assert [connector.text for connector in CohesionStats(text).connector_spans] == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Antes de la reunión firmó el acta.", []),
        ("Antes, firmó el acta.", ["antes"]),
        ("Por encima de 80 casos.", []),
        ("Encima, no vino.", ["encima"]),
        ("Al final de la línea hay un guion.", []),
        ("Al final, no vino.", ["al final"]),
        ("La métrica se calcula sobre todo el texto.", []),
        ("Sobre todo cuando el texto es largo.", ["sobre todo", "cuando"]),
        ("Luego de la reunión firmó.", []),
        ("Luego firmó el acta.", ["luego"]),
    ],
)
def test_connectors_inside_a_prepositional_phrase(text, expected):
    assert [connector.text for connector in CohesionStats(text).connector_spans] == expected


def test_find_connectors_blocked_without_pos():
    assert find_connectors(["antes", "de", "la", "reunión"]) == []
    assert [c.text for c in find_connectors(["por", "encima", "de", "todo"])] == []


def test_find_connectors_blocked_by_the_preceding_word():
    assert find_connectors(["por", "encima", "no", "vino"]) == []
    assert [c.text for c in find_connectors(["encima", "no", "vino"])] == ["encima"]


def test_find_connectors_of_a_word_without_pos():
    assert [c.text for c in find_connectors(["además"], pos=[None])] == ["además"]


def test_find_connectors_pos_extra():
    assert [c.text for c in find_connectors(["Resumiendo"], pos=["VERB"])] == ["resumiendo"]
    assert find_connectors(["Duerme"], pos=["VERB"]) == []


@pytest.mark.parametrize(
    "words",
    [["No", "tire", "así", "que", "se", "romperá"], ["Lo", "de", "siempre", "que", "derrocho"]],
)
def test_find_connectors_split_by_a_mark(words):
    # a mark before que makes it a word of its own
    assert find_connectors(words)
    assert find_connectors(words, breaks={3}) == []


@pytest.mark.parametrize(("breaks", "error"), [("x", SourceTypeError), ([1.5], ParameterError)])
def test_find_connectors_breaks_errors(breaks, error):
    with pytest.raises(error):
        find_connectors(["así", "que", "vino"], breaks=breaks)


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
    assert token_info(nlp("Mi libro")[0]).pronoun
    assert not token_info(nlp("El libro")[0]).pronoun


PARAGRAPHS = (
    "El gato duerme en la casa. El perro mira la calle. La casa es grande.\n\n"
    "El perro corre por la casa.\n\nEl gato salta."
)


def test_paragraphs(nlp):
    """A paragraph is a part between blank lines, of a string and of a Doc"""
    for source in (PARAGRAPHS, nlp(PARAGRAPHS)):
        cs = CohesionStats(source)
        assert cs.n_paragraphs == 3
        # gato, casa, perro, calle | perro, casa | gato (salta): 2 of 4 and 0 of 2 come again
        assert cs.noun_overlap_para == pytest.approx(1 / 3)
    assert CohesionStats(PARAGRAPHS.replace("\n\n", "\n")).n_paragraphs == 1


def test_overlaps_with_the_next_two_sentences():
    """The nouns of a sentence with two after it that one of them repeats"""
    cs = CohesionStats(PARAGRAPHS)
    # gato, casa | perro, calle | casa: casa, perro and casa of the five nouns
    assert cs.noun_overlap_2_sent == pytest.approx(0.6)
    assert cs.get_stats()["noun_overlap_2_sent"] == cs.noun_overlap_2_sent


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Si llueve, me quedo.", ["si"]),
        ("No sé si vendrá.", []),
        ("Voy a ver si puedo venir.", []),
        ("Me preguntó si tenía hambre.", []),
        ("¡Si ya te lo dije!", []),
        ("Lo miró como si fuera un fantasma.", []),
        ("Vaya si lo sé.", []),
        ("Si bien es cierto, no lo creo.", ["si bien"]),
        ("Te lo diré si me lo pides.", ["si"]),
        # The model leaves the verb without its lemma, simplemma gives it
        ("Ya verás si tengo razón.", []),
        ("Decidiremos si vamos.", []),
        # simplemma keeps the reflexive verb, the model gives its lemma with the pronoun
        ("Empezó a preguntarse si valía la pena.", []),
    ],
)
def test_si_without_a_condition(text, expected):
    """si of an indirect question, of an exclamation and of a comparison is no conditional"""
    assert [connector.text for connector in CohesionStats(text).connector_spans] == expected


def test_is_connector_blocked(nlp):
    doc = nlp("No sé si vendrá. Si llueve, me quedo. ¡Si ya te lo dije!")
    assert [is_connector_blocked(token) for token in doc if token.lower_ == "si"] == [
        True,
        False,
        True,
    ]
    assert not any(is_connector_blocked(token) for token in doc if token.lower_ != "si")
    # Without the parts of speech only the exclamation is known
    doc = spacy.blank("es")("No sé si vendrá. ¡Si ya te lo dije!")
    assert [is_connector_blocked(token) for token in doc if token.lower_ == "si"] == [False, True]


def test_find_connectors_blocked(nlp):
    """The positions of is_connector_blocked drop the si that CohesionStats drops"""
    words = [token for token in nlp("No sé si vendrá.") if not token.is_punct]
    texts, pos = [token.text for token in words], [token.pos_ for token in words]
    assert [c.text for c in find_connectors(texts, pos=pos)] == ["si"]
    blocked = {i for i, token in enumerate(words) if is_connector_blocked(token)}
    assert blocked == {2}
    assert find_connectors(texts, pos=pos, blocked=blocked) == []
    with pytest.raises(ParameterError):
        find_connectors(texts, blocked={4})


def test_paragraphs_of_a_doc_with_the_blank_lines_component():
    """The component of the blank lines before the parser keeps the paragraphs of the string"""
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_blank_lines", before="parser")
    cs = CohesionStats(pipeline(PARAGRAPHS))
    assert cs.n_paragraphs == 3
    assert cs.noun_overlap_para == CohesionStats(PARAGRAPHS).noun_overlap_para
