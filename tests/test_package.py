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
}
# Names of the core the library defines for Spanish: subclasses with the hooks, a wrapper
# taking the frequency dictionary and the pattern of Spanish numbers
SPANISH = {
    "CharNgramsExtractor",
    "DiversityStats",
    "NUMBER_PATTERN",
    "SentsExtractor",
    "WordsExtractor",
    "keyness",
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
    for name, value in vars(core_module).items():
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
