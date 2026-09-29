import importlib
import importlib.metadata
import re
import shutil
import subprocess
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
RESOURCES = {"connectors.tsv", "google_books_top10000.txt"}
# Modules of the library and the modules of the core they build on
CORE_MODULES = {
    "ests": "anyts",
    "ests.exceptions": "anyts.exceptions",
    "ests.utils": "anyts.utils",
    "ests.extractors": "anyts.extractors",
    "ests.diversity_stats": "anyts.diversity_stats",
    "ests.cohesion_stats": "anyts.cohesion",
    "ests.syntax_stats": "anyts.syntax",
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
# Names of the core the library defines for itself: subclasses with the Spanish hooks,
# wrappers with the Spanish defaults, the pattern of Spanish numbers, the tables of the
# Spanish readability and the User-Agent of the downloads
SPANISH = {
    "BasicStats",
    "CharNgramsExtractor",
    "DiversityStats",
    "GRADE_AGE_LEVELS",
    "HighlightedText",
    "NUMBER_PATTERN",
    "POSTGRADUATE_LEVEL",
    "READABILITY_GRADE_STATS",
    "READABILITY_PRESETS",
    "READABILITY_STATS_DESC",
    "READING_EASE_GRADES",
    "READING_SPEED_NORMS",
    "READING_SPEED_WPM",
    "ReadabilityStats",
    "SentsExtractor",
    "USER_AGENT",
    "WordsExtractor",
    "calc_consensus_grade",
    "calc_flesch_reading_easy",
    "calc_reading_time",
    "flesch_reading_easy_to_grade",
    "grade_to_age",
    "keyness",
    "kwic",
    "sentence_lengths",
    "sentence_lengths_plot",
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
        ):
            continue
        own = getattr(library_module, name)
        if name in SPANISH:
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
    assert set(points) >= FACTORIES
    for name in FACTORIES:
        assert points[name].load().__module__ == "ests.components"
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
    assert set(declared) == FACTORIES
