import importlib
import importlib.metadata
import re
import shutil
import subprocess
import tomllib
import zipfile
from pathlib import Path
from types import ModuleType

import pytest
from spacy.language import Language

import ests

ROOT = Path(__file__).parents[1]
SUBPACKAGES = ("corpus", "datasets", "visualizers")
FACTORIES = {
    "ests_basic",
    "ests_readability",
    "ests_diversity",
    "ests_morph",
    "ests_syntax",
    "ests_cohesion",
    "ests_lexical",
    "ests_style",
    "ests_phon",
    "ests_verse",
}
# The component of the core registered under the prefix of the library
CORE_COMPONENTS = {"ests_blank_lines"}
RESOURCES = {"connectors.tsv", "google_books_top10000.txt"}
# Modules of the library and the modules of the core they build on
CORE_MODULES = {
    "ests": "anyts",
    "ests.exceptions": "anyts.exceptions",
    "ests.utils": "anyts.utils",
    "ests.extractors": "anyts.extractors",
    "ests.diversity_stats": "anyts.diversity_stats",
    "ests.cohesion_stats": "anyts.cohesion_stats",
    "ests.syntax_stats": "anyts.syntax_stats",
    "ests.style_stats": "anyts.style_stats",
    "ests.lexical_stats": "anyts.lexical_stats",
    "ests.phon_stats": "anyts.phon_stats",
    "ests.corpus": "anyts.corpus",
    "ests.corpus.collocations": "anyts.corpus.collocations",
    "ests.corpus.dispersion": "anyts.corpus.dispersion",
    "ests.corpus.keyness": "anyts.corpus.keyness",
    "ests.corpus.stylometry": "anyts.corpus.stylometry",
    "ests.corpus.compare": "anyts.corpus.compare",
    "ests.corpus.kwic": "anyts.corpus.kwic",
    "ests.basic_stats": "anyts.basic_stats",
    "ests.readability_stats": "anyts.readability_stats",
    "ests.components": "anyts.components",
    "ests.datasets.freq_dict": "anyts.datasets",
    "ests.datasets.spanish_literature": "anyts.datasets",
    "ests.datasets.spanish_sonnets": "anyts.datasets",
    "ests.visualizers": "anyts.visualizers",
    "ests.visualizers.corpus": "anyts.visualizers.corpus",
    "ests.visualizers.fingerprinting": "anyts.visualizers.fingerprinting",
    "ests.visualizers.highlight": "anyts.visualizers.highlight",
    "ests.visualizers.sentences": "anyts.visualizers.sentences",
    "ests.visualizers.stylometry": "anyts.visualizers.stylometry",
    "ests.visualizers.vocabulary": "anyts.visualizers.vocabulary",
    "ests.visualizers.word_tree": "anyts.visualizers.word_tree",
    "ests.visualizers.zipf": "anyts.visualizers.zipf",
}
# Names of the core a module of the library defines for itself: subclasses with the
# Spanish hooks, wrappers with the Spanish defaults, the pattern of Spanish numbers, the
# Spanish marks, the tables of the Spanish readability and the User-Agent of the downloads
EXTRACTORS = {"SentsExtractor", "WordsExtractor"}
READABILITY = {
    "GRADE_AGE_LEVELS",
    "POSTGRADUATE_LEVEL",
    "READABILITY_GRADE_STATS",
    "READABILITY_PRESETS",
    "READABILITY_STATS_DESC",
    "READING_EASE_GRADES",
    "READING_SPEED_NORMS",
    "READING_SPEED_WPM",
    "ReadabilityStats",
    "calc_consensus_grade",
    "calc_flesch_reading_easy",
    "calc_reading_time",
    "flesch_reading_easy_to_grade",
    "grade_to_age",
}
SPANISH = {
    "ests": {*EXTRACTORS, "CharNgramsExtractor", "DiversityStats"},
    "ests.extractors": {*EXTRACTORS, "CharNgramsExtractor", "NUMBER_PATTERN"},
    "ests.diversity_stats": {"DiversityStats"},
    "ests.cohesion_stats": {"SentsExtractor"},
    "ests.style_stats": {
        "STYLE_STATS_DESC",
        "StyleStats",
        "WordsExtractor",
        "calc_academic_nausea",
        "calc_parentheticals",
        "calc_phrase_density",
        "calc_water",
        "find_nausea_words",
        "find_parentheticals",
    },
    "ests.lexical_stats": {"LEXICAL_STATS_DESC", "LexicalStats", "calc_surprisal"},
    "ests.phon_stats": {"PhonStats", "WordsExtractor", "cv_pattern"},
    "ests.syntax_stats": {
        "SYNTAX_STATS_DESC",
        "SyntaxStats",
        "is_agentless",
        "is_clause_head",
        "is_infinitive_clause",
        "is_passive",
        "is_subordinate_clause_head",
        "predicate_form",
    },
    "ests.corpus": {"keyness", "kwic", "split_windows"},
    "ests.corpus.keyness": {"keyness"},
    "ests.corpus.compare": {"OPENING_MARKS", "SYMMETRIC_MARKS", "split_windows"},
    "ests.corpus.kwic": {"kwic"},
    "ests.basic_stats": {*EXTRACTORS, "BasicStats"},
    "ests.readability_stats": {*EXTRACTORS, *READABILITY, "BasicStats"},
    "ests.components": {"BasicStats", "ReadabilityStats"},
    "ests.datasets.freq_dict": {"USER_AGENT"},
    "ests.datasets.spanish_literature": {"USER_AGENT"},
    "ests.datasets.spanish_sonnets": {"USER_AGENT"},
    "ests.visualizers": {"HighlightedText", "sentence_lengths", "sentence_lengths_plot"},
    "ests.visualizers.highlight": {"HighlightedText"},
    "ests.visualizers.sentences": {*EXTRACTORS, "sentence_lengths", "sentence_lengths_plot"},
}
# Copies of the mechanics of the core until the classes move onto the frames of anyTS 0.3:
# every PR of 0.8 removes its own
PENDING = {
    "ests.cohesion_stats": {
        "COHESION_STATS_DESC",
        "CONNECTOR_CLASSES",
        "CONNECTOR_POS",
        "CONTENT_UD_POS",
        "CohesionStats",
        "Connector",
    },
    "ests.components": {
        "BasicStatsComponent",
        "CohesionStats",
        "CohesionStatsComponent",
        "DiversityStatsComponent",
        "LexicalStats",
        "LexicalStatsComponent",
        "PhonStats",
        "PhonStatsComponent",
        "ReadabilityStatsComponent",
        "StyleStats",
        "StyleStatsComponent",
        "SyntaxStats",
        "SyntaxStatsComponent",
        "check_phon_params",
        "check_style_params",
    },
    "ests.visualizers.highlight": {
        "ALLITERATION_THRESHOLD",
        "calc_alliteration_runs",
        "find_alliteration",
        "find_complex_words",
        "find_connector_highlights",
        "find_long_sents",
        "find_phrase_highlights",
        "find_split_predicate_highlights",
    },
}


def test_version():
    assert re.fullmatch(r"\d+\.\d+\.\d+(\.dev\d+)?", ests.__version__)
    assert ests.__version__ != "0.0.0"


def test_metadata():
    assert "Spanish" in ests.__description__
    assert "__version__" in ests.__all__
    assert ests.__all__ == sorted(ests.__all__)


def test_version_fallback(monkeypatch):
    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    try:
        assert importlib.reload(ests).__version__ == "0.0.0"
    finally:
        monkeypatch.undo()
        importlib.reload(ests)
    assert ests.__version__ != "0.0.0"


@pytest.mark.parametrize("name", SUBPACKAGES)
def test_subpackage_exports(name):
    module = importlib.import_module(f"ests.{name}")
    assert module.__all__ == sorted(module.__all__)
    assert all(hasattr(module, attr) for attr in module.__all__)


@pytest.mark.parametrize(("library", "core"), CORE_MODULES.items())
def test_core_names(library, core):
    """A name of the core in the library is the object of the core, not a copy of it"""
    library_module, core_module = importlib.import_module(library), importlib.import_module(core)
    # dir, not vars: a lazy package of the core imports its names on first use
    for name in dir(core_module):
        value = getattr(core_module, name)
        if (
            name.startswith("_")
            or isinstance(value, ModuleType)
            or not hasattr(library_module, name)
            or name in PENDING.get(library, ())
        ):
            continue
        own = getattr(library_module, name)
        if name in SPANISH.get(library, ()):
            assert own is not value, name
            assert not isinstance(value, type) or issubclass(own, value), name
        else:
            assert own is value, name


def test_package_data():
    package = Path(ests.__file__).parent
    assert (package / "py.typed").is_file()
    assert all((package / "resources" / name).is_file() for name in RESOURCES)


def test_entry_points():
    points = {
        point.name: point for point in importlib.metadata.entry_points(group="spacy_factories")
    }
    assert set(points) >= FACTORIES | CORE_COMPONENTS
    for name in FACTORIES:
        assert points[name].load().__module__ == "ests.components"
        assert Language.has_factory(name)
    for name in CORE_COMPONENTS:
        assert points[name].load().__module__ == "anyts.components"
        assert Language.has_factory(name)


@pytest.mark.skipif(shutil.which("uv") is None, reason="the wheel is built by uv")
def test_wheel_contents(tmp_path):
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path), str(ROOT)],
        capture_output=True,
        check=True,
    )
    (wheel,) = tmp_path.glob("*.whl")
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        (points,) = (name for name in names if name.endswith(".dist-info/entry_points.txt"))
        declared = re.findall(
            r"^(ests_\w+) = ests\.components:", archive.read(points).decode(), re.MULTILINE
        )
    assert "ests/py.typed" in names
    assert {f"ests/resources/{name}" for name in RESOURCES} <= names
    # The archives of the datasets are downloaded, not installed
    assert not any(name.startswith("ests/datasets/data/") for name in names)
    assert set(declared) == FACTORIES | CORE_COMPONENTS


@pytest.mark.parametrize("page", ["installation.md", "installation.es.md"])
def test_installation_bounds(page):
    """The installation page states the lower bounds of anyTS and spaCy of the package"""
    requirements = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    bounds = {
        match[1]: match[2]
        for requirement in requirements["project"]["dependencies"]
        if (match := re.match(r"(anyts|spacy)>=([\d.]+)", requirement))
    }
    text = (ROOT / "docs" / page).read_text(encoding="utf-8")
    assert f"`spaCy` {bounds['spacy']} " in text
    assert f"(https://sergeyshk.github.io/anyTS/) {bounds['anyts']} " in text
