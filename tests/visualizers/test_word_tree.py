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
    assert '"<script>" [label="<script>"' in g.source
    assert "\t<script>" not in g.source


def test_wordtree(texts):
    g = wordtree(texts, "clase", max_n=2)
    assert isinstance(g, Digraph)
    assert len(g.body) == 11
    assert g.name == "clase"
