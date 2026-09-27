import importlib
import importlib.metadata
import re
import shutil
import subprocess
import zipfile
from pathlib import Path

import anyts
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
# Names that moved to the core, by the module of the library and the module of the core
MOVED = {
    ("exceptions", "exceptions"): [
        "DataFileError",
        "DatasetNotFoundError",
        "DownloadError",
        "ParameterError",
        "SourceError",
        "SourceTypeError",
        "UnknownStatError",
    ],
    ("utils", "utils"): [
        "check_sequence",
        "count_letters",
        "has_words",
        "is_punctuation",
        "iter_doc_tokens",
        "iter_doc_words",
        "safe_divide",
    ],
    ("extractors", "extractors"): ["Extractor", "Tokenizer"],
    ("diversity_stats", "diversity_stats"): [
        "Calculator",
        "HeapsFit",
        "WindowStats",
        "ZipfMandelbrot",
        "calc_alpha2",
        "calc_baayen_p",
        "calc_brunet_w",
        "calc_cttr",
        "calc_dttr",
        "calc_dugast_k",
        "calc_entropy",
        "calc_evenness",
        "calc_frequency_spectrum",
        "calc_gini_simpson_index",
        "calc_hapax_index",
        "calc_hapax_ratio",
        "calc_hdd",
        "calc_heaps_beta",
        "calc_herdan_vm",
        "calc_honore_r",
        "calc_httr",
        "calc_inverse_simpson_index",
        "calc_mamtld",
        "calc_mattr",
        "calc_michea_m",
        "calc_msttr",
        "calc_mtld",
        "calc_mtldw",
        "calc_mttr",
        "calc_perplexity",
        "calc_rttr",
        "calc_sichel_s",
        "calc_simpson_index",
        "calc_sttr",
        "calc_ttr",
        "calc_windowed",
        "calc_yule_i",
        "calc_yule_k",
        "calc_zipf_alpha",
        "check_params",
        "fit_heaps",
        "fit_zipf_mandelbrot",
        "vocabulary_growth",
    ],
    ("cohesion_stats", "cohesion"): [
        "Overlap",
        "calc_overlap",
        "calc_overlaps",
        "calc_proportional_overlap",
        "calc_repetition",
        "count_given",
        "dice",
        "dominant",
    ],
    ("syntax_stats", "syntax"): [
        "base_dep",
        "calc_coordination_chains",
        "calc_dependency_distances",
        "calc_tree_depth",
        "calc_valency",
        "count_children",
        "get_children",
        "get_words",
        "has_feature",
        "is_root",
        "is_word",
        "subtree_len",
    ],
    ("corpus.collocations", "corpus.collocations"): [
        "MEASURES",
        "Collocation",
        "calc_dice",
        "calc_log_likelihood",
        "calc_logdice",
        "calc_mi",
        "calc_mi3",
        "calc_min_sensitivity",
        "calc_npmi",
        "calc_t_score",
        "collocations",
    ],
    ("corpus.dispersion", "corpus.dispersion"): [
        "Dispersion",
        "calc_carroll_d2",
        "calc_dp",
        "calc_dp_norm",
        "calc_juilland_d",
        "calc_kl_divergence",
        "calc_rosengren_s",
        "dispersion",
    ],
    ("corpus.keyness", "corpus.keyness"): [
        "MEASURES",
        "ZERO_ADJUSTMENT",
        "FrequencyReference",
        "Keyword",
        "calc_bic",
        "calc_chi2",
        "calc_diff",
        "calc_ell",
        "calc_log_likelihood",
        "calc_log_ratio",
        "calc_odds_ratio",
        "calc_p_value",
    ],
    ("corpus.stylometry", "corpus.stylometry"): [
        "ZERO_SEGMENTS",
        "ZetaScore",
        "delta",
        "delta_profiles",
        "frequency_table",
        "kilgarriff_chi2",
        "mendenhall_curve",
        "mendenhall_distance",
        "z_scores",
        "zeta",
    ],
    ("corpus.compare", "corpus.compare"): [
        "COMPARISON_COLUMNS",
        "Values",
        "bootstrap_median_diff",
        "calc_cliff_delta",
        "calc_cohen_d",
        "compare_features",
        "compare_values",
        "holm_correction",
    ],
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


@pytest.mark.parametrize(("modules", "names"), MOVED.items(), ids=[m for m, _ in MOVED])
def test_moved_names(modules, names):
    """The names moved to the core are still there, as the objects of the core"""
    library, core = (
        importlib.import_module(f"{package}.{name}")
        for package, name in zip(("ests", "anyts"), modules, strict=True)
    )
    for name in names:
        assert getattr(library, name) is getattr(core, name), name


def test_base_exception():
    assert ests.EstsError is anyts.AnyTSError


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
