# Installation

## Requirements

*   `python` 3.11 or newer
*   `spaCy` 3.7 or newer
*   `numpy`, `scipy`, `pandas`, `simplemma` 2
*   `matplotlib` and `graphviz` for the [visualizers](visualizers/zipf.md)

The dependencies are installed with the package. `graphviz` is the Python interface; the [word tree](visualizers/word_tree.md) and the [network of collocations](visualizers/corpus.md#collocation_network) are rendered by the executables of [Graphviz](https://graphviz.org/download/), installed apart (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`).

## From PyPI

The distribution on PyPI is `pyests`, the package it installs is `ests`:

``` bash
pip install pyests
```

## From the repository

``` bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS
uv sync --all-groups
```

## The spaCy model { #model }

Basic statistics, readability, lexical diversity and phonostatistics need no trained model: sentences, words and character N-grams are extracted by rules and by the tokenizer of the blank Spanish pipeline, syllables and stress by the orthography. The [morphological](stats/morph_stats.md), the [syntactic](stats/syntax_stats.md), the [cohesion](stats/cohesion_stats.md) and the [lexical sophistication statistics](stats/lexical_stats.md) of a string need one - the syntactic ones need a pipeline with a parser - and so do the verbal nouns of the [style metrics](stats/style_stats.md), the profile of the function words ([`function_words_profile`](corpus/stylometry.md)), the features of a text and the [comparison of corpora](corpus/compare.md), and building a `Doc` yourself to pass it to the statistics instead of a string; the test suite needs it too, where it comes with the `test` dependency group:

``` bash
python -m spacy download es_core_news_sm
```

## Datasets { #datasets }

The [corpus of literature](datasets/spanishliterature.md), the [sonnets](datasets/spanishsonnets.md) and the [frequency dictionary](datasets/freqdict.md) are downloaded once by their `download()` method; the statistics of [`LexicalStats`](stats/lexical_stats.md) by the dictionary and [`keyness`](corpus/keyness.md) against it need `FreqDict().download()`. The archives go to the directory `ests_data` next to the installed package (`ests.constants.DEFAULT_DATA_DIR`), `dicts` for the dictionary and `texts` for the corpus and the sonnets. Where that directory cannot be written - a system Python, a shared environment - pass another one in `data_dir` (`FreqDict(data_dir="...")`) or set the environment variable `ESTS_DATA_DIR` before the package is imported:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
