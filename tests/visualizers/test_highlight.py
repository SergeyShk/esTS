import pytest
import spacy

from ests import StyleStats
from ests.constants import (
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_GROUPS,
    HIGHLIGHT_LAYERS_DESC,
    HIGHLIGHT_SYNTAX_LAYERS,
    HIGHLIGHT_TAGGED_LAYERS,
)
from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp
from ests.visualizers import Highlight, HighlightedText, highlight
from ests.visualizers.highlight import (
    CSS,
    Sent,
    Word,
    calc_alliteration_runs,
    find_alliteration,
    find_complex_words,
    find_connector_highlights,
    find_long_sents,
    get_stem_sounds,
    get_text_sents,
    get_text_words,
    group_words_by_sents,
    plural,
    split_segments,
)

text = (
    "El informe elaborado por la comisión fue aprobado ayer. "
    "Se revisaron los expedientes, siendo necesario hacer una revisión del aumento de la "
    "eficiencia del uso de los recursos. "
    "Sin embargo, a efectos del cobro se procedió al cierre a la mayor brevedad."
)
gerund = (
    "Los técnicos revisaron el informe durante la mañana, analizando con cuidado los datos "
    "del proyecto."
)
long_sent = (
    " ".join(
        ["La comisión revisó los documentos del expediente y los informes de los técnicos"] * 3
    )
    + "."
)
TEXT_LAYERS = [
    layer
    for layer in HIGHLIGHT_LAYERS_DESC
    if layer not in HIGHLIGHT_SYNTAX_LAYERS | HIGHLIGHT_TAGGED_LAYERS
]


@pytest.fixture(scope="module")
def nlp():
    return get_nlp()


@pytest.fixture(scope="module")
def doc(nlp):
    return nlp(text)


@pytest.fixture(scope="module")
def ht():
    return highlight(text, layers="all")


def spans(ht, layer):
    return [ht.text[h.start : h.end] for h in ht.highlights if h.layer == layer]


def test_init_value_error():
    with pytest.raises(SourceError):
        highlight("¿? ...")
    for threshold in (0, 1.5, "0.1"):
        with pytest.raises(ParameterError, match="alliteration"):
            highlight(text, alliteration_threshold=threshold)
    with pytest.raises(ParameterError):
        highlight(text, long_sent_word_factor=0)
    with pytest.raises(ParameterError):
        highlight(text, complex_syl_factor=0)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(SourceTypeError):
        highlight(source)


def test_init_string_lists():
    with pytest.raises(SourceTypeError):
        highlight(text, stopwords="el la")
    with pytest.raises(SourceTypeError):
        highlight(text, cliches="a la mayor brevedad")


def test_layers_generator():
    ht = highlight(text, layers=(layer for layer in ["cliches", "long_sents"]))
    assert ht.layers == ("long_sents", "cliches")


def test_highlight_returns_highlighted_text(ht):
    assert isinstance(ht, HighlightedText)
    assert repr(ht) == f"HighlightedText(counts={ht.counts})"


def test_layers_default_str():
    assert highlight(text).layers == ("long_sents", "complex_words", "cliches")


def test_layers_default_doc(doc):
    assert highlight(doc).layers == HIGHLIGHT_DEFAULT_LAYERS


def test_layers_default_blank_doc():
    # a blank pipeline gives no parse; its sentences come from the rules of SentsExtractor
    ht = highlight(spacy.blank("es")(text))
    assert ht.layers == ("long_sents", "complex_words", "cliches")


def test_layer_groups():
    layers = [layer for group in HIGHLIGHT_LAYER_GROUPS.values() for layer in group]
    assert sorted(layers) == sorted(HIGHLIGHT_LAYERS_DESC)
    assert frozenset(HIGHLIGHT_LAYER_GROUPS["Syntax"]) == HIGHLIGHT_SYNTAX_LAYERS


def test_layers_selection(doc):
    assert highlight(doc, layers="cliches").layers == ("cliches",)
    assert highlight(doc, layers="all").layers == tuple(HIGHLIGHT_LAYERS_DESC)
    assert highlight(text, layers="all").layers == tuple(TEXT_LAYERS)


def test_layers_unknown():
    with pytest.raises(ParameterError, match="Unknown layer"):
        highlight(text, layers=["cliches", "rhymes"])
    with pytest.raises(ParameterError, match="list of names"):
        highlight(text, layers=5)


@pytest.mark.parametrize(
    ("layer", "requirement"),
    [
        ("passive", "a dependency parse"),
        ("de_chains", "a dependency parse"),
        ("verbal_nouns", "the parts of speech and the lemmas"),
    ],
)
def test_layers_unavailable(layer, requirement):
    with pytest.raises(ParameterError, match=requirement):
        highlight(text, layers=layer)


def test_doc_without_the_sentence_boundaries(nlp):
    doc = nlp(long_sent + " " + text, disable=["parser"])
    assert not doc.has_annotation("SENT_START")
    for layer in ("long_sents", "connectors"):
        assert spans(highlight(doc, layers=layer), layer) == spans(
            highlight(doc.text, layers=layer), layer
        )
    assert highlight(doc, layers="long_sents").counts == {"long_sents": 1}


@pytest.mark.parametrize("layer", sorted(HIGHLIGHT_SYNTAX_LAYERS))
def test_syntax_layers_without_the_lemmas(nlp, layer):
    # the syntactic layers read the lemmas: ser of the passive, the light verbs
    doc = nlp(text, disable=["lemmatizer"])
    with pytest.raises(ParameterError, match="parse and the lemmas"):
        highlight(doc, layers=layer)
    assert highlight(doc).layers == ("long_sents", "complex_words", "cliches")


def test_counts(ht):
    assert list(ht.counts) == list(ht.layers)
    assert ht.counts["cliches"] == 2
    assert ht.counts["compound_prepositions"] == 1
    assert ht.counts["parentheticals"] == 1


def test_counts_all_layers(doc):
    counts = highlight(doc, layers="all").counts
    assert counts["passive"] == 2
    assert counts["participle_clauses"] == 1
    assert counts["de_chains"] == 1
    assert counts["split_predicates"] == 1
    assert counts["verbal_nouns"] == 4


def test_highlights_sorted(ht):
    positions = [(h.start, -h.end) for h in ht.highlights]
    assert positions == sorted(positions)


def test_get_text_words():
    words = get_text_words("¿Hola, mundo?")
    assert words == [Word(1, 5, "Hola"), Word(7, 12, "mundo")]


def test_get_text_sents():
    sample = "Hola, mundo. ¿Qué tal estás?"
    sents = get_text_sents(sample, get_text_words(sample))
    assert sents == [Sent(0, 12, 2), Sent(13, 28, 3)]


def test_get_text_sents_without_words():
    assert get_text_sents("Hola.", []) == [Sent(0, 5, 0)]


def test_group_words_by_sents():
    words = [Word(0, 4, "Hola"), Word(6, 11, "mundo"), Word(13, 16, "Qué"), Word(30, 33, "fin")]
    sents = [Sent(0, 12, 2), Sent(13, 28, 1)]
    assert group_words_by_sents(words, sents) == [words[:2], [words[2]]]


def test_doc_sents_whitespace_start(nlp):
    doc = nlp("\n\nHola, mundo. ¿Qué tal estás?")
    ht = highlight(doc, layers="long_sents", long_sent_word_factor=2)
    assert spans(ht, "long_sents") == ["Hola, mundo.", "¿Qué tal estás?"]


def test_plural():
    assert plural(1, "word") == "1 word"
    assert plural(3, "word") == "3 words"


def test_long_sents():
    ht = highlight(long_sent, layers="long_sents")
    assert ht.highlights == (
        Highlight(0, len(long_sent), "long_sents", "long sentence, 39 words"),
    )
    assert highlight(long_sent, layers="long_sents", long_sent_word_factor=40).counts == {
        "long_sents": 0
    }


def test_find_long_sents():
    sents = [Sent(0, 10, 3), Sent(11, 20, 5)]
    assert find_long_sents(sents, 5) == [Highlight(11, 20, "long_sents", "long sentence, 5 words")]


def test_complex_words(ht):
    # from 4 syllables by default: at 3 half the content words would be complex
    assert "expedientes" in spans(ht, "complex_words")
    assert "comisión" not in spans(ht, "complex_words")
    three = highlight(text, layers="complex_words", complex_syl_factor=3)
    assert "comisión" in spans(three, "complex_words")
    assert "hacer" not in spans(three, "complex_words")


def test_find_complex_words():
    words = [Word(0, 3, "sol"), Word(4, 12, "carretera")]
    assert find_complex_words(words, 3) == [
        Highlight(4, 12, "complex_words", "complex word, 4 syllables")
    ]
    assert find_complex_words(words, 5) == []


def test_stopwords(ht):
    found = {word.lower() for word in spans(ht, "stopwords")}
    assert {"el", "la", "del", "se"} <= found
    assert "informe" not in found


def test_stopwords_list():
    ht = highlight(text, layers="stopwords", stopwords=["INFORME", "cobro"])
    assert spans(ht, "stopwords") == ["informe", "cobro"]


def test_rare_words():
    ht = highlight(
        "El felinólogo examinaba al minino con parsimonia 2020 y x-23.", layers="rare_words"
    )
    assert spans(ht, "rare_words") == ["felinólogo", "minino", "parsimonia"]
    assert ht.highlights[0].note == "rare word: beyond the top 10000"


def test_rare_words_proper_nouns(nlp):
    # a proper noun of a tagged Doc keeps its form, parís, beyond the top 10000; a string
    # without the parts of speech takes the lemma parir, as LexicalStats would
    doc = nlp("Viajó a París en tren.")
    assert "París" in spans(highlight(doc, layers="rare_words"), "rare_words")
    assert "París" not in spans(highlight(doc.text, layers="rare_words"), "rare_words")


def test_verbal_nouns(doc):
    ht = highlight(doc, layers="verbal_nouns")
    assert spans(ht, "verbal_nouns") == ["comisión", "revisión", "eficiencia", "uso"]
    lemmas = [token.lemma_ for token in doc if token.pos_ == "NOUN"]
    assert StyleStats(doc).verbal_nouns == pytest.approx(100 * 4 / len(lemmas))


def test_verbal_nouns_without_the_lemmas(nlp):
    with pytest.raises(ParameterError, match="lemmas"):
        highlight(nlp(text, disable=["lemmatizer"]), layers="verbal_nouns")


def test_compound_prepositions(ht):
    assert spans(ht, "compound_prepositions") == ["a efectos del"]
    (fragment,) = [h for h in ht.highlights if h.layer == "compound_prepositions"]
    assert fragment.note == "compound preposition: «a efectos de»"


def test_cliches(ht):
    assert spans(ht, "cliches") == ["procedió al", "a la mayor brevedad"]
    notes = [h.note for h in ht.highlights if h.layer == "cliches"]
    assert notes == ["cliché: «proceder a»", "cliché: «a la mayor brevedad»"]
    custom = highlight(text, layers="cliches", cliches=["el informe", "hacer una revisión"])
    assert spans(custom, "cliches") == ["El informe", "hacer una revisión"]


def test_parentheticals(ht):
    assert spans(ht, "parentheticals") == ["Sin embargo"]


def test_connectors(ht):
    notes = [h.note for h in ht.highlights if h.layer == "connectors"]
    assert "connector «sin embargo»: adversative, secondary" in notes


def test_connectors_pos():
    # a one-word connector counts with its part of speech only, pues as a verb is no connector
    words = [Word(0, 4, "Pues"), Word(5, 7, "no"), Word(8, 12, "vino")]
    sents = [Sent(0, 13, 3)]
    assert len(find_connector_highlights(words, sents)) == 1
    tagged = [
        word._replace(pos=pos) for word, pos in zip(words, ["VERB", "ADV", "VERB"], strict=True)
    ]
    assert find_connector_highlights(tagged, sents) == []


def test_passive(doc):
    ht = highlight(doc, layers="passive")
    assert spans(ht, "passive") == ["fue aprobado", "Se revisaron"]
    assert [h.note for h in ht.highlights] == ["passive with ser, no agent", "passive with se"]


def test_passive_with_an_agent(nlp):
    ht = highlight(nlp("La casa fue construida por los obreros."), layers="passive")
    assert [h.note for h in ht.highlights] == ["passive with ser"]


def test_participle_clauses(doc):
    ht = highlight(doc, layers="participle_clauses")
    assert spans(ht, "participle_clauses") == ["elaborado por la comisión"]
    assert ht.highlights[0].note == "participial clause, 4 words"


def test_gerund_clauses(nlp):
    ht = highlight(nlp(gerund), layers="gerund_clauses")
    assert spans(ht, "gerund_clauses") == ["analizando con cuidado los datos del proyecto"]


def test_de_chains(doc):
    ht = highlight(doc, layers="de_chains")
    assert spans(ht, "de_chains") == [
        "revisión del aumento de la eficiencia del uso de los recursos"
    ]
    assert ht.highlights[0].note == "chain of 4 complements with de"


def test_de_chains_single_complement(nlp):
    ht = highlight(nlp("El uso del agua."), layers="de_chains")
    assert ht.counts == {"de_chains": 0}


def test_split_predicates(doc):
    ht = highlight(doc, layers="split_predicates")
    assert spans(ht, "split_predicates") == ["hacer una revisión"]
    assert ht.highlights[0].note == "split predicate: hacer revisión"


def test_doc_long_sents(nlp):
    ht = highlight(nlp(long_sent), layers="long_sents")
    assert ht.counts == {"long_sents": 1}


def test_doc_text_layers(doc):
    # the layers that read the words give the same fragments for a Doc and a string
    for layer in ("complex_words", "compound_prepositions", "cliches", "parentheticals"):
        assert spans(highlight(doc, layers=layer), layer) == spans(
            highlight(text, layers=layer), layer
        )


def test_alliteration():
    ht = highlight("Boga y boga en el lago. Deje la abeja.", layers="alliteration")
    assert spans(ht, "alliteration") == ["Boga y boga en el lago", "Deje la abeja"]
    assert [h.note for h in ht.highlights] == [
        "alliteration on /g/ (g, gu)",
        "alliteration on /x/ (j, g)",
    ]
    # Machado: en and la neither break nor continue the run, nieve holds b in its v
    machado = (
        "El cierzo corre por el campo yerto alborotando en blancos torbellinos "
        "la nieve silenciosa."
    )
    ht = highlight(machado, layers="alliteration")
    assert spans(ht, "alliteration") == ["alborotando en blancos torbellinos la nieve"]
    # a sound written with its own letter has no spellings in the note
    ht = highlight(
        "Ala aleve del leve abanico.", layers="alliteration", alliteration_threshold=0.01
    )
    assert "alliteration on /l/" in [h.note for h in ht.highlights]


def test_alliteration_within_sentences():
    # the repetition is looked for inside a sentence, not across the period
    sample = "Boga. Boga."
    ht = highlight(sample, layers="alliteration", alliteration_threshold=0.5)
    assert ht.counts == {"alliteration": 0}
    # without the sentences, b and g repeat across the period
    assert len(find_alliteration(get_text_words(sample), 0.5)) == 2


def test_alliteration_threshold():
    sample = "La luz del sol llena la sala."
    strict = highlight(sample, layers="alliteration").counts["alliteration"]
    loose = highlight(sample, layers="alliteration", alliteration_threshold=0.5)
    assert loose.counts["alliteration"] > strict


def test_calc_alliteration_runs():
    # de is too short to break the run, the sounds count and not the letters: casa, queso and
    # fresco repeat k, 0.148 · 0.148 · 0.214 = 0.0047
    assert calc_alliteration_runs(["casa", "de", "queso", "fresco"], 0.01) == [(0, 4, "k")]
    assert calc_alliteration_runs(["casa", "de", "queso", "fresco"]) == []
    # two words are 0.022 for k and 0.08 for s: several sounds of one run
    assert calc_alliteration_runs(["casa", "queso"], 0.01) == []
    assert calc_alliteration_runs(["casa", "queso"], 0.5) == [(0, 2, "k"), (0, 2, "s")]


def test_calc_alliteration_runs_skips_the_stopwords():
    # que neither breaks nor continues a run of k: the model of chance does not fit it
    assert calc_alliteration_runs(["que", "hacía", "y", "de", "que", "aquel"]) == []
    words = ["casa", "que", "con", "queso", "fresco"]
    assert calc_alliteration_runs(words, 0.01) == [(0, 5, "k")]


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("cantaban", "k a n t a"),
        ("casas", "k a s a"),
        # the transcriptions are compared, so the letters at the cut keep their sound
        ("hacía", "a θ"),
        ("cogió", "k o x"),
        ("aquella", "a k e"),
        ("seguía", "s e g i"),
        # a suppletive form keeps the whole word
        ("fue", "f u e"),
        ("quiero", "k i e r o"),
    ],
)
def test_get_stem_sounds(word, expected):
    assert get_stem_sounds(word) == tuple(expected.split())


def test_split_segments():
    highlights = [Highlight(0, 4, "a"), Highlight(2, 6, "b")]
    segments = [
        (start, end, [h.layer for h in active])
        for start, end, active in split_segments(8, highlights)
    ]
    assert segments == [(0, 2, ["a"]), (2, 4, ["a", "b"]), (4, 6, ["b"]), (6, 8, [])]


def test_split_segments_empty():
    assert list(split_segments(3, [])) == [(0, 3, [])]


def test_to_html(ht):
    markup = ht.to_html()
    assert markup.startswith('<div class="ests-highlight"><style>')
    assert '<div class="ests-highlight-legend">' in markup
    assert 'title="cliché: «a la mayor brevedad»"' in markup
    assert ht._repr_html_() == markup


def test_to_html_without_legend_and_css(ht):
    markup = ht.to_html(legend=False, css=False)
    assert "<style>" not in markup
    assert "ests-highlight-legend" not in markup


def test_to_html_escaping():
    markup = highlight("El <gato> & el perro\nduermen.", layers="stopwords").to_html()
    assert "&lt;gato&gt; &amp;" in markup
    assert "&#10;" in markup


def test_css_paints_the_stopwords_first():
    # the densest layer comes first, so that every other background covers it
    backgrounds = [
        line.split()[0].removeprefix(".ests-hl-")
        for line in CSS.splitlines()
        if line.startswith(".ests-hl-") and "background" in line
    ]
    assert backgrounds[:2] == ["long_sents", "stopwords"]
    ht = highlight(text, layers=["stopwords", "compound_prepositions"])
    markup = ht.to_html(legend=False, css=False)
    assert '<span class="ests-hl ests-hl-compound_prepositions ests-hl-stopwords"' in markup


def test_to_html_title():
    ht = highlight('Él dijo "sí".', layers="cliches", cliches=["dijo"])
    assert 'title="cliché: «dijo»"' in ht.to_html()


def test_to_html_nested_classes(doc):
    markup = highlight(doc, layers=["complex_words", "verbal_nouns"]).to_html(legend=False)
    assert 'class="ests-hl ests-hl-complex_words ests-hl-verbal_nouns"' in markup
