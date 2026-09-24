import pytest
from graphviz import Digraph

from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.visualizers import wordtree


@pytest.fixture(scope="module")
def texts():
    return [["la", "clase", "obrera"], ["toda", "clase", "de", "gente"]]


def test_wordtree_type_error():
    with pytest.raises(TypeError):
        wordtree(1, "prueba")
    with pytest.raises(SourceTypeError):
        wordtree("la clase obrera", "clase")
    with pytest.raises(SourceTypeError):
        wordtree([["la", "clase"], "la clase obrera"], "clase")


def test_wordtree_value_error(texts):
    with pytest.raises(ValueError):
        wordtree(texts, "prueba")
    with pytest.raises(SourceError):
        wordtree([], "prueba")
    with pytest.raises(ParameterError):
        wordtree(texts, "clase", max_n=1)
    with pytest.raises(ParameterError):
        wordtree(texts, "clase", max_per_n=0)


def test_wordtree_html_like_words():
    g = wordtree([["<script>", "gato", "duerme"], ["malo", "<script>", "come"]], "<script>")
    assert g.source.splitlines()[0] == 'digraph "<script>" {'
    assert '\tn0 [label="<script>"' in g.source
    assert "\t<script>" not in g.source


def test_wordtree(texts):
    g = wordtree(texts, "clase", max_n=2)
    assert isinstance(g, Digraph)
    assert len(g.body) == 11
    assert g.name == "clase"


def test_wordtree_identifiers():
    # A colon would be a port of graphviz and hyphens would join the paths of two branches
    g = wordtree([["son", "las", "10:30", "ya"]], "las", max_n=3)
    assert '\tn2 [label="10:30" fontsize=30]' in g.source
    assert "\tn0 -> n2" in g.source and "\tn2 -> n3" in g.source
    g = wordtree([["dijo", "franco-alemán", "no"], ["dijo", "franco", "alemán", "no"]], "dijo")
    assert g.source.count("[label=no ") == 2
    assert sum(line.endswith("-> n0\n") for line in g.body) == 0
    assert len([line for line in g.body if " -> " in line]) == 5


def test_wordtree_max_per_n():
    # clase de gente is frequent, clase de is not among the two most frequent bigrams:
    # the trigram does not show up without its bigram, and a level holds max_per_n nodes
    texts = (
        [["clase", "obrera"]] * 4
        + [["clase", "media"]] * 3
        + [["clase", "de", "gente"]] * 2
        + [["clase", "alta", "y", "baja"]]
    )
    g = wordtree(texts, "clase", max_n=3, max_per_n=2)
    labels = [line.split("label=")[1].split()[0] for line in g.body if "label=" in line]
    assert labels == ["clase", "obrera", "media"]
    g = wordtree(texts, "clase", max_n=4, max_per_n=4)
    labels = [line.split("label=")[1].split()[0] for line in g.body if "label=" in line]
    assert labels == ["clase", "obrera", "media", "de", "gente", "alta", "y", "baja"]
