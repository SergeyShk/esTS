"""Statistics by the parts of a document (by_parts of the core)"""

import pytest
import spacy
from anyts.document import document_part

import ests
from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.style_stats import _doc_nouns
from ests.utils import _annotate_text, get_nlp

# A sentence of the verse runs over its lines
VERSE = (
    "Con diez cañones por banda,\nviento en popa, a toda vela,\nno corta el mar, sino vuela\n"
    "un velero bergantín."
)
PROSE = "Bebimos vino de Rioja. Luego vino a casa y vino otra vez.\nEl pájaro canta en el jardín."
TEXT = VERSE + "\n\n" + PROSE
SIZES = {"sentences": 4, "lines": 3, "paragraphs": 2}
# Counts the parts share without a rest: unique words and the spaces between parts do not
ADDITIVE = {
    ests.BasicStats: lambda stats: [
        key
        for key in stats.get_stats(flat=True)
        if key not in {"n_chars", "n_spaces", "n_unique_words"} and key.startswith(("n_", "c_"))
    ],
    ests.MorphStats: lambda stats: [
        key
        for stat, value in stats.get_stats().items()
        if isinstance(value, dict)
        for key in stats.get_stats(flat=True)
        if key.startswith(f"{stat}_")
    ],
    ests.VerseStats: lambda stats: ["n_lines", "n_stanzas"],
}
CLASSES = [
    ests.BasicStats,
    ests.ReadabilityStats,
    ests.UnadaptedReadabilityStats,
    ests.MorphStats,
    ests.LexicalStats,
    ests.StyleStats,
    ests.SyntaxStats,
    ests.CohesionStats,
    ests.PhonStats,
    ests.VerseStats,
]


@pytest.fixture(scope="module")
def sources():
    return {"str": TEXT, "Document": _annotate_text(TEXT), "Doc": get_nlp()(TEXT)}


@pytest.fixture(scope="module")
def params(freq_dict):
    """The frequency dictionary of the tests for LexicalStats"""
    return {ests.LexicalStats: {"freq_dict": freq_dict}}


@pytest.mark.parametrize("cls", list(ADDITIVE), ids=lambda cls: cls.__name__)
@pytest.mark.parametrize("kind", ["str", "Document", "Doc"])
def test_parts_add_up(cls, kind, sources):
    """The counts of the parts add up to the counts of the whole text"""
    source = sources[kind]
    flat = cls(source).get_stats(flat=True)
    for parts in cls.part_kinds:
        table = cls.by_parts(source, parts)
        for key in ADDITIVE[cls](cls(source)):
            total = int(table[key].fillna(0).sum()) if key in table else 0
            assert total == flat[key], (parts, key)


@pytest.mark.parametrize("cls", CLASSES, ids=lambda cls: cls.__name__)
def test_by_parts(cls, sources, params):
    """A row of the table for every part of every kind of a string, a Document and a Doc"""
    for kind, source in sources.items():
        if cls is ests.SyntaxStats and kind == "Document":
            continue
        for parts in cls.part_kinds:
            table = cls.by_parts(source, parts, **params.get(cls, {}))
            assert len(table) == SIZES[parts], (kind, parts)
            assert table.index.name == parts[:-1]
    paragraphs = cls.by_parts(TEXT, "paragraphs", **params.get(cls, {}))
    assert list(paragraphs["start"]) == [0, len(VERSE) + 2]


def test_style_parts_analyzed_as_whole():
    """The nouns of the parts of a string are those of the whole text analyzed by esMorph"""
    document = ests.StyleStats.parts_document(TEXT)
    whole = _doc_nouns(_annotate_text(TEXT))
    found = []
    for sentence in document.sentences:
        found += _doc_nouns(document_part(document, sentence.start, sentence.end))
    assert found == whole


@pytest.mark.parametrize("cls", [ests.SyntaxStats, ests.CohesionStats], ids=lambda c: c.__name__)
def test_by_parts_with_a_pipeline(cls):
    """The parts of a string are parsed by the pipeline passed in nlp: a blank one has no
    annotation"""
    assert cls.by_parts(TEXT, "paragraphs", nlp=get_nlp()).equals(cls.by_parts(TEXT, "paragraphs"))
    with pytest.raises(SourceError):
        cls.by_parts(TEXT, "paragraphs", nlp=spacy.blank("es"))
    with pytest.raises(SourceTypeError):
        cls.by_parts(TEXT, "paragraphs", nlp="es_core_news_sm")


def test_by_parts_kinds():
    """VerseStats counts the stanzas only, DiversityStats no parts"""
    with pytest.raises(ParameterError, match="must be one of"):
        ests.VerseStats.by_parts(TEXT, "sentences")
    with pytest.raises(ParameterError, match="counts a whole text"):
        ests.DiversityStats.by_parts(TEXT)
