from math import isnan

import pytest
import spacy
from spacy.tokens import Doc

from ests import SyntaxStats
from ests.constants import SYNTAX_STATS_DESC
from ests.exceptions import SourceError, SourceTypeError
from ests.syntax_stats import (
    base_dep,
    calc_coordination_chains,
    calc_de_chains,
    calc_dependency_distances,
    calc_tree_depth,
    calc_valency,
    count_children,
    count_noun_modifiers,
    find_split_predicates,
    get_words,
    has_auxiliary,
    has_feature,
    is_agent,
    is_agentless,
    is_clause_head,
    is_de_modifier,
    is_finite_verb,
    is_gerund,
    is_gerund_clause,
    is_infinitive,
    is_light_verb,
    is_negation,
    is_participle,
    is_participle_clause,
    is_passive,
    is_predicate,
    is_root,
    is_split_predicate_noun,
    is_subordinate_clause_head,
    is_word,
    subtree_len,
)
from ests.utils import get_nlp

TEXT = (
    "La casa, construida por los obreros en 1900, fue vendida. "
    "Dijo que no vendría y se fue dando un portazo."
)


@pytest.fixture(scope="module")
def nlp():
    return get_nlp()


@pytest.fixture(scope="module")
def ss():
    return SyntaxStats(TEXT)


def words(nlp, text):
    return get_words(nlp(text, disable=["ner"]))


def test_counts(ss):
    assert (ss.n_sents, ss.n_words) == (2, 20)
    assert ss.n_leaves + ss.n_subtrees == ss.n_words
    assert sum(ss.c_deps.values()) == ss.n_words
    assert sum(ss.c_children.values()) == ss.n_words


def test_get_stats(ss):
    assert tuple(ss.get_stats()) == tuple(SYNTAX_STATS_DESC)


def test_get_stats_values(ss):
    stats = ss.get_stats()
    assert stats["mean_dependency_distance"] == pytest.approx(2.3333333, rel=1e-6)
    assert stats["tree_depth"] == 4
    assert stats["clauses_per_sent"] == 1.5
    assert stats["p_complex_sents"] == 0.5
    assert stats["noun_verb_ratio"] == 1


def test_print_stats(ss, capsys):
    ss.print_stats()
    out = capsys.readouterr().out.splitlines()
    assert out[0].split("|") == [
        "                    Statistic                     ",
        "  Value   ",
    ]
    assert out[1] == "-" * 60
    assert len(out) == len(SYNTAX_STATS_DESC) + 2
    assert out[2] == f"{'Mean dependency distance':50}|{2.33:^10.2f}"


def test_doc_source(ss, nlp):
    assert SyntaxStats(nlp(TEXT)).get_stats() == ss.get_stats()


def test_nlp_parameter(ss, nlp):
    assert SyntaxStats(TEXT, nlp=nlp).get_stats() == ss.get_stats()


@pytest.mark.parametrize("source", [1, ["La", "casa"], None, spacy.blank("es")])
def test_source_type_error(source):
    with pytest.raises(SourceTypeError):
        SyntaxStats(source)


def test_source_without_parse():
    with pytest.raises(SourceError, match="no parse"):
        SyntaxStats(spacy.blank("es")("La casa es blanca"))


@pytest.mark.parametrize("source", ["", "   ", "¡¿...!"])
def test_source_without_words(source):
    with pytest.raises(SourceError, match="no words"):
        SyntaxStats(source)


def test_source_too_long(nlp):
    with pytest.raises(SourceError, match="longer than the limit"):
        SyntaxStats("hola " * (nlp.max_length // 4), nlp=nlp)


def test_is_word(nlp):
    doc = nlp("La casa, blanca")
    assert [token.text for token in doc if is_word(token)] == ["La", "casa", "blanca"]


def test_is_root(nlp):
    assert [token.text for token in nlp("La casa es blanca") if is_root(token)] == ["blanca"]


def test_base_dep(nlp):
    assert next(base_dep(token) for token in words(nlp, "Se construyó la casa")) == "expl"


def test_count_children_and_subtree(nlp):
    tokens = words(nlp, "La casa blanca es bonita")
    casa = tokens[1]
    assert count_children(casa) == 2
    assert subtree_len(casa) == 3


def test_dependency_distances(nlp):
    assert calc_dependency_distances(words(nlp, "La casa es blanca")) == [1, 2, 1]


def test_dependency_distances_empty(nlp):
    assert calc_dependency_distances(words(nlp, "Hola")) == []


def test_tree_depth(nlp):
    assert calc_tree_depth(words(nlp, "La casa blanca es muy bonita")) == 2
    assert calc_tree_depth(words(nlp, "Hola")) == 0


def test_has_feature(nlp):
    token = words(nlp, "Los niños juegan")[2]
    assert has_feature(token, "VerbForm", "Fin")
    assert not has_feature(token, "VerbForm", "Inf")


@pytest.mark.parametrize(
    ("text", "check", "expected"),
    [
        ("Los niños juegan", is_finite_verb, "juegan"),
        ("Quiero leer el libro", is_infinitive, "leer"),
        ("Está cantando una canción", is_gerund, "cantando"),
        ("Ha leído el libro", is_participle, "leído"),
        ("Nunca lo vi", is_negation, "Nunca"),
        ("Ningún libro es perfecto", is_negation, "Ningún"),
    ],
)
def test_word_checks(nlp, text, check, expected):
    assert [token.text for token in words(nlp, text) if check(token)] == [expected]


def test_negative_concord(nlp):
    assert [token.text for token in words(nlp, "No vino nadie") if is_negation(token)] == [
        "No",
        "nadie",
    ]


def test_negation_conjunction(nlp):
    assert [token.text for token in words(nlp, "Ni tú ni yo") if is_negation(token)] == []


def test_valency(nlp):
    tokens = words(nlp, "El director hizo una revisión y firmó")
    assert calc_valency(tokens[2]) == 2


def test_coordination_chains(nlp):
    assert calc_coordination_chains(words(nlp, "Compré libros, cuadernos y lápices")) == [3]


def test_coordination_chains_none(nlp):
    assert calc_coordination_chains(words(nlp, "Compré un libro")) == []


def test_clause_heads(nlp):
    tokens = words(nlp, "Dijo que vendría y se fue")
    assert [token.text for token in tokens if is_clause_head(token)] == ["Dijo", "vendría", "fue"]


def test_subordinate_clause_heads(nlp):
    tokens = words(nlp, "Dijo que vendría cuando terminara")
    assert [token.text for token in tokens if is_subordinate_clause_head(token)] == [
        "vendría",
        "terminara",
    ]


def test_is_predicate(nlp):
    tokens = words(nlp, "Ella es alta")
    assert is_predicate(tokens[2])
    assert not is_predicate(tokens[0])


def test_noun_modifiers(nlp):
    tokens = words(nlp, "La casa blanca del pueblo es bonita")
    assert count_noun_modifiers(tokens[1]) == 3


def test_de_modifier(nlp):
    tokens = words(nlp, "El uso del agua y la vuelta al campo")
    assert [token.text for token in tokens if is_de_modifier(token)] == ["agua"]


def test_de_chains(nlp):
    tokens = words(nlp, "El aumento de la eficiencia del uso de los recursos es notable")
    assert calc_de_chains(tokens) == [3]


def test_de_chains_single(nlp):
    assert calc_de_chains(words(nlp, "El uso del agua es libre")) == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("La casa fue construida por los obreros", ["construida"]),
        ("La casa fue vendida", ["vendida"]),
        ("El libro ha sido leído por todos", ["leído"]),
        ("El autor ha escrito el libro", []),
        ("Se construyó la casa", ["construyó"]),
        ("El proyecto es financiado por la Unión Europea", ["financiado"]),
        ("La casa está construida", []),
        ("Los niños juegan", []),
    ],
)
def test_passive(nlp, text, expected):
    assert [token.text for token in words(nlp, text) if is_passive(token)] == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("La casa fue construida por los obreros", False),
        ("La casa fue vendida", True),
        ("El libro ha sido leído por todos", False),
    ],
)
def test_agentless(nlp, text, expected):
    passive = next(token for token in words(nlp, text) if is_passive(token))
    assert is_agentless(passive) is expected


def test_agentless_of_an_active_form(nlp):
    assert is_agentless(words(nlp, "Los niños juegan")[2])


def test_agent(nlp):
    tokens = words(nlp, "La casa fue construida por los obreros")
    assert [token.text for token in tokens if is_agent(token)] == ["obreros"]


def test_has_auxiliary(nlp):
    tokens = words(nlp, "La casa fue construida")
    assert has_auxiliary(tokens[-1])
    assert not has_auxiliary(tokens[1])


def test_participle_clause(nlp):
    tokens = words(nlp, "La casa, construida por los obreros, se vendió")
    assert [token.text for token in tokens if is_participle_clause(token)] == ["construida"]


def test_participle_of_a_compound_tense_is_not_a_clause(nlp):
    tokens = words(nlp, "El autor ha escrito el libro")
    assert [token.text for token in tokens if is_participle_clause(token)] == []


def test_gerund_clause(nlp):
    tokens = words(nlp, "Hablando en voz alta, entró en la sala")
    assert [token.text for token in tokens if is_gerund_clause(token)] == ["Hablando"]


@pytest.mark.parametrize(
    "text",
    [
        "Está cantando una canción",
        "Sigue trabajando en el proyecto",
        "Continúa creciendo la demanda",
        "Lleva años estudiando el problema",
        "Acabó reconociendo el error",
    ],
)
def test_gerund_of_a_periphrasis_is_not_a_clause(nlp, text):
    assert [token.text for token in words(nlp, text) if is_gerund_clause(token)] == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("El director hizo una revisión de las cuentas", ["hizo revisión"]),
        ("Tomó una decisión", ["Tomó decisión"]),
        ("Se llevó a cabo la reforma", ["llevó cabo"]),
        ("El comité puso de manifiesto el problema", ["puso manifiesto"]),
        ("El director firmó el documento", []),
        ("Hizo una casa", []),
        ("Dio comienzo a la sesión", ["Dio comienzo"]),
        ("Se realizó una revisión de las cuentas", ["realizó revisión"]),
        ("Tomó parte en la reunión", ["Tomó parte"]),
        ("Se hizo por decisión del comité", []),
        ("Hizo el trabajo con dedicación", []),
        ("La decisión tomó forma", []),
        ("El tribunal dio traslado a las partes", []),
        ("La empresa puso en primer lugar la seguridad", []),
        ("El secretario dio lectura al acuerdo", ["dio lectura"]),
        ("Se procedió a la notificación de la resolución", ["procedió notificación"]),
        ("Llevó el asunto a la comisión", []),
        ("La reunión tuvo lugar en Madrid", ["tuvo lugar"]),
        ("El director llevó el proyecto al comienzo de su carrera", []),
        ("El tren llevó a los viajeros al comienzo de la ruta", []),
    ],
)
def test_split_predicates(nlp, text, expected):
    found = find_split_predicates(words(nlp, text))
    assert [f"{verb.text} {noun.text}" for verb, noun in found] == expected


def test_split_predicate_prefers_the_fixed_part(nlp):
    found = find_split_predicates(words(nlp, "Dio comienzo a la sesión"))
    assert [noun.text for _, noun in found] == ["comienzo"]


def test_clause_head_of_a_punctuation_mark(nlp):
    assert not is_clause_head(nlp("La casa es blanca.")[-1])


@pytest.mark.parametrize(
    ("pos", "expected"),
    [("VERB", True), ("ADV", False)],
)
def test_clause_head_of_a_parenthetical(nlp, pos, expected):
    doc = Doc(
        nlp.vocab,
        words=["El", "libro", "es", "bueno", "claro"],
        heads=[1, 3, 3, 3, 3],
        deps=["det", "nsubj", "cop", "ROOT", "parataxis"],
        pos=["DET", "NOUN", "AUX", "ADJ", pos],
    )
    assert is_clause_head(doc[4]) is expected


def test_split_predicate_of_an_unlisted_relation(nlp):
    doc = Doc(
        nlp.vocab,
        words=["Hizo", "el", "trabajo", "revisión"],
        heads=[0, 2, 0, 0],
        deps=["ROOT", "det", "obj", "appos"],
        pos=["VERB", "DET", "NOUN", "NOUN"],
        lemmas=["hacer", "el", "trabajo", "revisión"],
    )
    assert find_split_predicates(get_words(doc)) == []


def test_light_verb(nlp):
    tokens = words(nlp, "El director hizo una revisión")
    assert [token.text for token in tokens if is_light_verb(token)] == ["hizo"]


def test_split_predicate_noun(nlp):
    verb, noun = words(nlp, "Hizo una revisión")[0], words(nlp, "Hizo una revisión")[2]
    assert is_split_predicate_noun(noun, verb)


@pytest.mark.parametrize(
    ("noun_text", "verb_text", "expected"),
    [
        ("cabo", "llevó", True),
        ("cabo", "dio", False),
        ("parte", "tomó", True),
        ("parte", "dio", False),
    ],
)
def test_split_predicate_noun_of_a_fixed_expression(nlp, noun_text, verb_text, expected):
    noun = next(
        token for token in words(nlp, f"Se llevó a {noun_text} el plan") if token.text == noun_text
    )
    verb = next(
        token for token in words(nlp, f"El juez {verb_text} el plan") if token.text == verb_text
    )
    assert is_split_predicate_noun(noun, verb) is expected


def test_split_predicates_attribute():
    ss = SyntaxStats("El director hizo una revisión y tomó una decisión")
    assert ss.split_predicates == ("hizo revisión", "tomó decisión")
    assert ss.n_split_predicates == 2
    assert ss.split_predicates_per_sent == 2


def test_se_constructions():
    ss = SyntaxStats("Se construyó la casa. Aquí se trabaja mucho.")
    assert ss.n_se_passives == 1
    assert ss.n_impersonal_se == 1
    assert ss.se_passives_per_sent == 0.5


def test_single_word_sentence():
    ss = SyntaxStats("Hola")
    assert ss.n_sents == 1
    assert ss.tree_depth == 0
    assert isnan(ss.mean_dependency_distance)
    assert isnan(ss.std_dependency_distance)
    assert isnan(ss.max_dependency_distance)
    assert isnan(ss.p_adjacent_dependencies)


def test_text_without_verbs():
    ss = SyntaxStats("La casa blanca del pueblo")
    assert ss.n_verbs == 0
    assert isnan(ss.p_passive)
    assert isnan(ss.noun_verb_ratio)
    assert isnan(ss.verb_valency)


def test_empty_bases():
    ss = SyntaxStats("La casa blanca")
    assert isnan(ss.mean_coordination_chain_len)
    assert isnan(ss.mean_participle_clause_len)
    assert isnan(ss.mean_gerund_clause_len)
    assert isnan(ss.p_agentless_passive)
    assert ss.max_de_chain_len == 0
