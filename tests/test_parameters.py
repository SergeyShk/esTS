"""The functions of the library check their counts and lists of words as the core does"""

import matplotlib
import numpy as np
import pytest

from ests import (
    BasicStats,
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    StyleStats,
    SyntaxStats,
    WordsExtractor,
)
from ests.basic_stats import punctuation_profile
from ests.corpus import compare_corpora, corpus_features, function_words_profile, kwic
from ests.corpus.compare import sentence_rhythm, split_windows, text_features
from ests.datasets import SpanishLiterature
from ests.exceptions import ParameterError, SourceTypeError
from ests.lexical_stats import calc_surprisal
from ests.phon_stats import (
    calc_alliteration,
    calc_assonance,
    calc_consonant_clusters,
    calc_cv_entropy,
    calc_hiatus,
)
from ests.readability_stats import flesch_reading_easy_to_grade
from ests.style_stats import (
    calc_academic_nausea,
    calc_classic_nausea,
    calc_keyword_density,
    calc_parentheticals,
    calc_phrase_density,
    calc_spam,
    calc_verbal_nouns,
    calc_water,
    calc_zipf_naturalness,
    expand_phrases,
)
from ests.utils import find_phrases
from ests.visualizers import (
    highlight,
    sentence_lengths_plot,
)

matplotlib.use("Agg")

TEXT = "El gato duerme en la ventana. El perro come en el suelo y el gato lo mira."
WORDS = ["el", "gato", "duerme", "en", "la", "ventana", "el", "perro"]

INTEGERS = {
    "StyleStats(top_n)": lambda: StyleStats(TEXT, top_n=1.5),
    "calc_academic_nausea(top_n)": lambda: calc_academic_nausea(WORDS, top_n=2.0),
    "calc_zipf_naturalness(top_n)": lambda: calc_zipf_naturalness(WORDS, top_n=True),
    "PhonStats(window_len)": lambda: PhonStats(TEXT, window_len=2.5),
    "calc_alliteration(window_len)": lambda: calc_alliteration(WORDS, window_len=3.0),
    "calc_assonance(window_len)": lambda: calc_assonance(WORDS, window_len=True),
    "BasicStats(complex_syl_factor)": lambda: BasicStats(TEXT, complex_syl_factor=3.0),
    "BasicStats(long_word_letter_factor)": lambda: BasicStats(TEXT, long_word_letter_factor=0),
    "count_words_by_syllables": lambda: BasicStats(TEXT).count_words_by_syllables(2.5),
    "count_words_by_letters": lambda: BasicStats(TEXT).count_words_by_letters(True),
    "kwic(window)": lambda: kwic(TEXT, "gato", window=1.5),
    "split_windows(window)": lambda: split_windows(TEXT, 1.5),
    "split_windows(window=True)": lambda: split_windows(TEXT, True),
    "split_windows(min_words)": lambda: split_windows(TEXT, 10, min_words=2.0),
    "corpus_features(window)": lambda: corpus_features([TEXT], window=2.5),
    "compare_corpora(n_bootstrap)": lambda: compare_corpora([TEXT], [TEXT], n_bootstrap=1.5),
    "sentence_lengths_plot(window)": lambda: sentence_lengths_plot(TEXT, window=2.5),
    "highlight(long_sent_word_factor)": lambda: highlight(TEXT, long_sent_word_factor=2.5),
    "highlight(complex_syl_factor)": lambda: highlight(TEXT, complex_syl_factor=True),
    "punctuation_profile(n_words)": lambda: punctuation_profile(TEXT, n_words=2.5),
    "punctuation_profile(negative n_words)": lambda: punctuation_profile(TEXT, n_words=-1),
    "SpanishLiterature(year_from)": lambda: SpanishLiterature._get_filters(
        None, None, None, 1850.5, None, None, None
    ),
    "ReadabilityStats(preset)": lambda: ReadabilityStats(TEXT, preset=["general"]),
    "flesch_reading_easy_to_grade(preset)": lambda: flesch_reading_easy_to_grade(60, ["general"]),
    "SpanishLiterature(author)": lambda: SpanishLiterature._get_filters(
        None, 5, None, None, None, None, None
    ),
}

NOT_STRINGS = [1, 2]
WORD_LISTS = {
    "function_words_profile": lambda: function_words_profile(NOT_STRINGS),
    "calc_classic_nausea": lambda: calc_classic_nausea(NOT_STRINGS),
    "calc_academic_nausea": lambda: calc_academic_nausea(NOT_STRINGS),
    "calc_water": lambda: calc_water(NOT_STRINGS),
    "calc_water(stopwords)": lambda: calc_water(WORDS, stopwords=NOT_STRINGS),
    "calc_spam(iterator)": lambda: calc_spam(iter(WORDS)),
    "calc_zipf_naturalness": lambda: calc_zipf_naturalness(NOT_STRINGS),
    "calc_keyword_density(keywords)": lambda: calc_keyword_density(WORDS, NOT_STRINGS),
    "calc_verbal_nouns": lambda: calc_verbal_nouns(NOT_STRINGS),
    "expand_phrases": lambda: expand_phrases(NOT_STRINGS, []),
    "calc_phrase_density(phrases)": lambda: calc_phrase_density(WORDS, "sin embargo"),
    "calc_parentheticals": lambda: calc_parentheticals(NOT_STRINGS),
    "calc_consonant_clusters": lambda: calc_consonant_clusters(NOT_STRINGS),
    "calc_hiatus": lambda: calc_hiatus(NOT_STRINGS),
    "calc_cv_entropy": lambda: calc_cv_entropy(NOT_STRINGS),
    "calc_alliteration": lambda: calc_alliteration(NOT_STRINGS),
    "calc_assonance": lambda: calc_assonance("gato"),
    "calc_surprisal": lambda: calc_surprisal(NOT_STRINGS, None),
    "find_phrases": lambda: find_phrases(NOT_STRINGS, []),
    "StyleStats(stopwords)": lambda: StyleStats(TEXT, stopwords=NOT_STRINGS),
    "StyleStats(cliches)": lambda: StyleStats(TEXT, cliches="por medio de"),
    "corpus_features": lambda: corpus_features(NOT_STRINGS),
    "compare_corpora": lambda: compare_corpora([TEXT], NOT_STRINGS),
    "highlight(stopwords)": lambda: highlight(TEXT, stopwords=NOT_STRINGS),
    "BasicStats(sents_extractor)": lambda: BasicStats(TEXT, sents_extractor="x"),
    "BasicStats(words_extractor)": lambda: BasicStats(TEXT, words_extractor=WordsExtractor),
    "DiversityStats(words_extractor)": lambda: DiversityStats(TEXT, words_extractor="x"),
    "PhonStats(words_extractor)": lambda: PhonStats(TEXT, words_extractor="x"),
    "StyleStats(nlp)": lambda: StyleStats(TEXT, nlp="es_core_news_sm"),
    "StyleStats(words_extractor)": lambda: StyleStats(TEXT, words_extractor="x"),
    "CohesionStats(nlp)": lambda: CohesionStats(TEXT, nlp="x"),
    "LexicalStats(nlp)": lambda: LexicalStats(TEXT, nlp="x"),
    "CohesionStats(sents_extractor)": lambda: CohesionStats(TEXT, sents_extractor="x"),
    "CohesionStats(connectors)": lambda: CohesionStats(TEXT, connectors=["porque"]),
    "CohesionStats(connector)": lambda: CohesionStats(TEXT, connectors={"porque": "causal"}),
    "MorphStats(nlp)": lambda: MorphStats(TEXT, nlp="es_core_news_sm"),
    "SyntaxStats(nlp)": lambda: SyntaxStats(TEXT, nlp="es_core_news_sm"),
    "LexicalStats(freq_dict)": lambda: LexicalStats(TEXT, freq_dict="x"),
    "calc_surprisal(freq_dict)": lambda: calc_surprisal(WORDS, "x"),
    "text_features": lambda: text_features(None),
    "text_features(nlp)": lambda: text_features(TEXT, nlp="x"),
    "function_words_profile(nlp)": lambda: function_words_profile(WORDS, nlp="x"),
    "split_windows": lambda: split_windows(WORDS),
    "sentence_rhythm": lambda: sentence_rhythm("texto"),
    "sentence_rhythm(elements)": lambda: sentence_rhythm(["4", "8"]),
    "kwic(keyword)": lambda: kwic(TEXT, 5),
}


@pytest.mark.parametrize("call", INTEGERS.values(), ids=INTEGERS)
def test_integers(call):
    with pytest.raises(ParameterError):
        call()


@pytest.mark.parametrize("call", WORD_LISTS.values(), ids=WORD_LISTS)
def test_word_lists(call):
    with pytest.raises(SourceTypeError):
        call()


def test_compare_corpora_checks_before_the_features():
    calls = []

    def features(text):
        calls.append(text)
        return {"chars": float(len(text))}

    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, n_bootstrap=1.5)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], window=2.5, features=features)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, seed=-1)
    with pytest.raises(ParameterError):
        compare_corpora([TEXT], [TEXT], features=features, labels=("diff", "B"))
    with pytest.raises(SourceTypeError):
        compare_corpora([TEXT], NOT_STRINGS, features=features)
    assert calls == []


def test_frequency_dictionary(freq_dict):
    with pytest.raises(SourceTypeError):
        freq_dict.lookup(5)
    with pytest.raises(SourceTypeError):
        freq_dict.ipm(None)
    with pytest.raises(ParameterError):
        next(freq_dict.get_records(min_ipm="1"))
    # A threshold from an array or a column is a number too
    assert next(freq_dict.get_records(min_ipm=np.int64(100)))
    assert next(freq_dict.get_records(min_ipm=np.float32(100)))
    with pytest.raises(ParameterError):
        next(freq_dict.get_records(pos=["NOUN"]))


def test_cohesion_checks_the_connectors_before_parsing():
    # A string over the limit of the pipeline fails only when it comes to parsing
    with pytest.raises(SourceTypeError):
        CohesionStats("a " * 1_000_000, connectors=["porque"])
