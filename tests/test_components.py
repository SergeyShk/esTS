import subprocess
import sys

import pytest
import spacy
from spacy.language import Language

from ests import (
    BasicStats,
    BasicStatsComponent,
    CohesionStats,
    CohesionStatsComponent,
    DiversityStats,
    DiversityStatsComponent,
    MorphStats,
    MorphStatsComponent,
    ReadabilityStats,
    ReadabilityStatsComponent,
    SyntaxStats,
    SyntaxStatsComponent,
)
from ests.exceptions import ParameterError, SourceError

COMPONENTS = (
    ("ests_basic", BasicStatsComponent, BasicStats),
    ("ests_readability", ReadabilityStatsComponent, ReadabilityStats),
    ("ests_diversity", DiversityStatsComponent, DiversityStats),
    ("ests_morph", MorphStatsComponent, MorphStats),
    ("ests_syntax", SyntaxStatsComponent, SyntaxStats),
    ("ests_cohesion", CohesionStatsComponent, CohesionStats),
)
TEXT = "El gato duerme en la ventana. Los niños juegan en el parque."


@pytest.fixture(scope="module")
def nlp():
    return spacy.load("es_core_news_sm")


@pytest.mark.parametrize(("factory", "component", "stats"), COMPONENTS)
def test_factory_is_registered(factory, component, stats):
    assert Language.has_factory(factory)


@pytest.mark.parametrize(("factory", "component", "stats"), COMPONENTS)
def test_component_computes_the_statistics(nlp, factory, component, stats):
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe(factory, name="stats", last=True)
    doc = pipeline(TEXT)
    assert isinstance(doc._.stats, stats)
    assert doc._.stats.get_stats() == stats(nlp(TEXT)).get_stats()


@pytest.mark.parametrize(("factory", "component", "stats"), COMPONENTS)
def test_component_type(factory, component, stats):
    pipeline = spacy.load("es_core_news_sm")
    assert isinstance(pipeline.add_pipe(factory, name="stats", last=True), component)


def test_default_name_is_the_factory():
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_basic", last=True)
    assert pipeline("El gato duerme")._.ests_basic.n_words == 3


def test_several_components_in_one_pipeline():
    pipeline = spacy.load("es_core_news_sm")
    for factory in ("ests_basic", "ests_morph", "ests_syntax"):
        pipeline.add_pipe(factory, name=factory.removeprefix("ests_"), last=True)
    doc = pipeline(TEXT)
    assert doc._.basic.n_sents == 2
    assert doc._.morph.pos[0] == "DET"
    assert doc._.syntax.n_sents == 2


def test_the_same_component_twice_with_its_own_name():
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_readability", name="readability", last=True)
    pipeline.add_pipe(
        "ests_readability", name="readability_classic", config={"preset": "classic"}, last=True
    )
    doc = pipeline(TEXT)
    assert doc._.readability.preset == "general"
    assert doc._.readability_classic.preset == "classic"
    assert doc._.readability.flesch_reading_easy != doc._.readability_classic.flesch_reading_easy


def test_readability_preset(nlp):
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_readability", name="stats", config={"preset": "classic"}, last=True)
    doc = pipeline(TEXT)
    assert doc._.stats.get_stats() == ReadabilityStats(nlp(TEXT), preset="classic").get_stats()


def test_readability_unknown_preset():
    pipeline = spacy.load("es_core_news_sm")
    with pytest.raises(ParameterError, match="Unknown coefficient preset"):
        pipeline.add_pipe("ests_readability", name="stats", config={"preset": "fiction"})


def test_diversity_parameters(nlp):
    pipeline = spacy.load("es_core_news_sm")
    config = {"window_len": 10, "mtld_threshold": 0.66, "mtld_min_len": 5, "hdd_sample_size": 12}
    pipeline.add_pipe("ests_diversity", name="stats", config=config, last=True)
    doc = pipeline(TEXT)
    assert doc._.stats.get_stats() == DiversityStats(nlp(TEXT), **config).get_stats()


@pytest.mark.parametrize(
    "config",
    [{"window_len": 0}, {"mtld_threshold": 1.5}, {"mtld_min_len": -1}, {"hdd_sample_size": 0}],
)
def test_diversity_wrong_parameters(config):
    pipeline = spacy.load("es_core_news_sm")
    with pytest.raises(ParameterError):
        pipeline.add_pipe("ests_diversity", name="stats", config=config)


@pytest.mark.parametrize("factory", ["ests_morph", "ests_syntax", "ests_cohesion"])
def test_component_without_the_annotation(factory):
    pipeline = spacy.blank("es")
    pipeline.add_pipe(factory, name="stats", last=True)
    with pytest.raises(SourceError):
        pipeline("El gato duerme")


def test_readability_reuses_the_basic_statistics(nlp):
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_basic", name="basic", last=True)
    pipeline.add_pipe("ests_readability", name="stats", config={"basic": "basic"}, last=True)
    doc = pipeline(TEXT)
    assert doc._.stats.get_stats() == ReadabilityStats(nlp(TEXT)).get_stats()
    assert doc._.stats.get_stats() == ReadabilityStats(doc._.basic).get_stats()


def test_readability_reuse_of_a_missing_component():
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_readability", name="stats", config={"basic": "basic"}, last=True)
    with pytest.raises(SourceError, match="holds no basic statistics"):
        pipeline(TEXT)


def test_readability_reuse_of_a_component_that_runs_later():
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_readability", name="stats", config={"basic": "basic"}, last=True)
    pipeline.add_pipe("ests_basic", name="basic", last=True)
    with pytest.raises(SourceError, match="holds no basic statistics"):
        pipeline(TEXT)


@pytest.mark.parametrize("factory", ["ests_morph", "ests_syntax", "ests_cohesion"])
def test_component_without_the_lemmas(factory):
    pipeline = spacy.load("es_core_news_sm", exclude=["lemmatizer"])
    pipeline.add_pipe(factory, name="stats", last=True)
    with pytest.raises(SourceError, match="no lemmas"):
        pipeline(TEXT)


def test_pipeline_is_loaded_without_importing_the_package(tmp_path):
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_basic", name="basic", last=True)
    pipeline.to_disk(tmp_path)
    code = (
        "import spacy;"
        f"nlp = spacy.load({str(tmp_path)!r});"
        "print(nlp('El gato duerme en la ventana')._.basic.n_words)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True
    )
    assert result.stdout.strip() == "6"


def test_extension_is_set_by_the_name():
    pipeline = spacy.load("es_core_news_sm")
    pipeline.add_pipe("ests_basic", name="basic_stats", last=True)
    doc = pipeline("El gato duerme")
    assert doc._.basic_stats is not None
    assert doc.has_extension("basic_stats")
