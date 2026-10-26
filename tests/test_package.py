import importlib
import importlib.metadata
import re
import shutil
import subprocess
import sys
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
    "ests.cohesion_stats": {
        "COHESION_STATS_DESC",
        "CONNECTOR_POS",
        "CohesionStats",
        "SentsExtractor",
    },
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
        "is_infinitive_clause_head",
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
    "ests.components": {
        "BasicStats",
        "BasicStatsComponent",
        "CohesionStats",
        "CohesionStatsComponent",
        "DiversityStatsComponent",
        "LexicalStats",
        "LexicalStatsComponent",
        "PhonStats",
        "PhonStatsComponent",
        "ReadabilityStats",
        "ReadabilityStatsComponent",
        "StyleStats",
        "StyleStatsComponent",
        "SyntaxStats",
        "SyntaxStatsComponent",
    },
    "ests.datasets.freq_dict": {"USER_AGENT"},
    "ests.datasets.spanish_literature": {"USER_AGENT"},
    "ests.datasets.spanish_sonnets": {"USER_AGENT"},
    "ests.visualizers": {"HighlightedText", "sentence_lengths", "sentence_lengths_plot"},
    "ests.visualizers.highlight": {
        "HighlightedText",
        "calc_alliteration_runs",
        "find_alliteration",
        "find_complex_words",
        "find_connector_highlights",
        "find_long_sents",
        "find_phrase_highlights",
        "find_split_predicate_highlights",
    },
    "ests.visualizers.sentences": {*EXTRACTORS, "sentence_lengths", "sentence_lengths_plot"},
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


# Names of the core the library has not moved onto the object of the core yet: MorphStats
# before the frame of the core
PENDING = {"ests.components": {"MorphStats", "MorphStatsComponent"}}


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


def _run(code: str) -> str:
    """Output of the code in a process of its own, where nothing is imported beforehand"""
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


@pytest.mark.parametrize(
    ("statement", "absent"),
    [
        ("import ests", ("spacy", "thinc", "scipy", "pandas", "matplotlib")),
        ("from ests.visualizers import highlight", ("spacy", "pandas", "matplotlib")),
        ("from ests.corpus import kwic", ("spacy", "pandas", "matplotlib")),
    ],
)
def test_imports_are_light(statement, absent):
    loaded = _run(f"import sys\n{statement}\nprint(' '.join(sorted(sys.modules)))").split()
    assert not set(absent) & set(loaded)


def test_only_components_import_spacy():
    """spaCy is loaded by the documents of the user and by the components, not by importing
    the modules of esTS"""
    code = (
        "import importlib, pkgutil, sys, ests\n"
        "names = [m.name for m in pkgutil.walk_packages(ests.__path__, 'ests.')]\n"
        "for name in names:\n"
        "    if name != 'ests.components':\n"
        "        importlib.import_module(name)\n"
        "print(len(names), 'spacy' in sys.modules, 'thinc' in sys.modules)"
    )
    n_modules, spacy, thinc = _run(code).split()
    assert int(n_modules) > 30
    assert (spacy, thinc) == ("False", "False")


def test_components_on_first_use():
    code = (
        "import sys, ests\n"
        "before = 'spacy' in sys.modules\n"
        "component = ests.StyleStatsComponent\n"
        "print(before, 'spacy' in sys.modules, component.__module__)"
    )
    assert _run(code) == "False True ests.components"


def test_factories_without_import():
    """The factories are found by the entry points spacy_factories, without import ests"""
    code = (
        "import spacy\n"
        "nlp = spacy.blank('es')\n"
        "nlp.add_pipe('ests_basic')\n"
        "print(nlp('el gato duerme')._.ests_basic.n_words)"
    )
    assert _run(code) == "3"


@pytest.mark.parametrize(
    "stub", ["sys.modules['spacy'] = None", "sys.modules['spacy'] = types.ModuleType('spacy')"]
)
def test_import_with_a_stub_of_spacy(stub):
    """A mark of spaCy as missing and a stub of spaCy (Pyodide) do not break the import"""
    code = (
        f"import sys, types\n{stub}\n"
        "import ests\n"
        "from ests.syllables import count_syllables\n"
        "print(count_syllables('gato'), 'ests.components' in sys.modules)"
    )
    assert _run(code) == "2 False"


def test_star_import_and_help_without_spacy():
    code = (
        "import pydoc, sys\n"
        "from ests import *\n"
        "import ests\n"
        "pydoc.render_doc(ests)\n"
        "print('BasicStats' in dir(), 'spacy' in sys.modules, 'ests.components' in sys.modules)"
    )
    assert _run(code) == "True False False"


def test_lazy_packages_export_their_names():
    for package in (ests, ests.corpus, ests.visualizers):
        assert set(package.__all__) <= set(dir(package))
        assert all(getattr(package, name) is not None for name in package.__all__)
    assert callable(ests.visualizers.highlight) and callable(ests.corpus.kwic)


def test_factories_with_spacy_loaded_before():
    """Entry points read before esTS was installed do not matter: with spaCy loaded, import
    ests registers the factories itself"""
    code = (
        "import catalogue\n"
        "catalogue.AVAILABLE_ENTRY_POINTS = {}\n"
        "import spacy, ests\n"
        "nlp = spacy.blank('es')\n"
        "nlp.add_pipe('ests_basic')\n"
        "print(nlp('el gato duerme')._.ests_basic.n_words)"
    )
    assert _run(code) == "3"


def test_doc_of_spacy_loaded_after():
    """A Doc is recognized when spaCy is loaded after import ests"""
    code = (
        "import sys, ests\n"
        "before = 'spacy' in sys.modules\n"
        "import spacy\n"
        "doc = spacy.blank('es')('El gato duerme. El perro come.')\n"
        "print(before, ests.BasicStats(doc).n_sents, len(ests.DiversityStats(doc).words),"
        " len(ests.StyleStats(doc).words))"
    )
    assert _run(code) == "False 2 6 6"


def test_pipeline_check_without_spacy():
    """A pipeline is checked without loading spaCy: there is no Language before it"""
    code = (
        "import sys, ests\n"
        "try:\n"
        "    ests.StyleStats('El gato duerme.', nlp='es_core_news_sm')\n"
        "except ests.SourceTypeError as error:\n"
        "    print(error, 'spacy' in sys.modules)"
    )
    assert _run(code) == "The pipeline must be a spaCy Language False"


STATS_CLASSES = [
    "BasicStats",
    "CohesionStats",
    "DiversityStats",
    "LexicalStats",
    "MorphStats",
    "PhonStats",
    "ReadabilityStats",
    "StyleStats",
    "SyntaxStats",
    "VerseStats",
]


@pytest.mark.parametrize("name", STATS_CLASSES)
def test_stats_interface(name):
    """Every class of statistics has the interface of the core: get_stats, describe..."""
    from anyts.stats import Stats

    stats_class = getattr(ests, name)
    assert issubclass(stats_class, Stats)
    assert stats_class.stats_desc


@pytest.mark.parametrize("name", STATS_CLASSES)
def test_stats_in_docstring(name):
    """Every statistic of get_stats is described in the Attributes of the docstring of its class"""
    stats_class = getattr(ests, name)
    attributes = re.search(r"Attributes:\n(.*?)\n\n", stats_class.__doc__, re.DOTALL)
    assert attributes is not None
    assert [key for key in stats_class.stats_desc if f" {key} (" not in attributes[1]] == []


@pytest.mark.parametrize("name", STATS_CLASSES)
def test_source_type_message(name):
    """A source of a wrong type names its type, a Span asks for its Doc"""
    import spacy

    with pytest.raises(ests.SourceTypeError, match=r"^The data source cannot be of type int$"):
        getattr(ests, name)(5)
    span = spacy.blank("es")("El gato duerme en la ventana.")[0:2]
    with pytest.raises(ests.SourceTypeError, match=r"^The data source cannot be a Span"):
        getattr(ests, name)(span)


def test_demo_computes_its_examples(monkeypatch, freq_dict):
    """The demo computes every example and a text of long runs of marks, gradio stubbed"""
    import importlib.util
    import time
    from unittest.mock import MagicMock

    import ests.datasets

    monkeypatch.setitem(sys.modules, "gradio", MagicMock())
    monkeypatch.setattr(ests.datasets, "FreqDict", lambda: freq_dict)
    spec = importlib.util.spec_from_file_location("ests_demo", ROOT / "demo" / "app.py")
    assert spec and spec.loader
    app = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(app)
    for text in app.EXAMPLES.values():
        result = app.compute(text, app.DEFAULT_LAYERS)
        assert result["summary"] and not result["lexical"].empty
    start = time.perf_counter()
    result = app.compute("Hola, " + "!?" * 5000 + " " + "_" * 5000 + " mundo.", [])
    assert time.perf_counter() - start < 10
    assert result["text"] == "Hola, " + "!?" * 5 + " " + "_" * 10 + " mundo."


@pytest.mark.parametrize(
    "name", ["CohesionStats", "LexicalStats", "MorphStats", "StyleStats", "SyntaxStats"]
)
def test_pickle_without_the_pipeline(name, freq_dict):
    """A copy of a class built with a pipeline keeps its statistics but not the pipeline"""
    import copy
    import pickle

    from ests.utils import get_nlp

    extra = {"freq_dict": freq_dict} if name == "LexicalStats" else {}
    stats = getattr(ests, name)(
        "La revisión del expediente fue realizada por el comité.", nlp=get_nlp(), **extra
    )
    data = pickle.dumps(stats)
    assert len(data) < 100_000
    for clone in (pickle.loads(data), copy.deepcopy(stats)):
        assert repr(clone.get_stats()) == repr(stats.get_stats())
        if name == "LexicalStats":
            assert clone.analyze("El perro ladra.") == stats.analyze("El perro ladra.")


def test_version_of_the_notebooks():
    """The notebooks and their pages ask for the minor version of the package"""
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    major, minor = project["version"].split(".")[:2]
    for notebook in sorted((ROOT / "examples").glob("*.ipynb")):
        text = notebook.read_text(encoding="utf-8")
        assert f"< ({major}, {minor}):" in text, notebook.name
        assert f"pyests>={major}.{minor}" in text, notebook.name
        assert f"esTS {major}.{minor} or newer" in text, notebook.name
    for page, phrase in (
        ("examples/README.md", "or newer"),
        ("docs/examples.md", "or newer"),
        ("docs/examples.es.md", "o posterior"),
    ):
        assert f"esTS {major}.{minor} {phrase}" in (ROOT / page).read_text(encoding="utf-8")
