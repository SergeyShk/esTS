# Installation

## Requirements

*   `python` 3.11 or newer
*   `spaCy` 3.7 or newer
*   `numpy`, `scipy`, `pandas`, `simplemma` 2
*   `matplotlib` and `graphviz` for the [visualizers](visualizers/zipf.md)

The dependencies are installed with the package. The [word tree](visualizers/word_tree.md) and the [network of collocations](visualizers/corpus.md#collocation_network) are rendered by the executables of [Graphviz](https://graphviz.org/download/), installed separately (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`).

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

Basic statistics, readability, lexical diversity, the style metrics except the verbal nouns, phonostatistics and verse statistics need no trained model. The [morphological](stats/morph_stats.md), the [syntactic](stats/syntax_stats.md) (with a parser), the [cohesion](stats/cohesion_stats.md) and the [lexical sophistication statistics](stats/lexical_stats.md) of a string need one, and so do the verbal nouns of the [style metrics](stats/style_stats.md), [`function_words_profile`](corpus/stylometry.md), the features of a text, the [comparison of corpora](corpus/compare.md) and building a `Doc` yourself. The test suite needs it too; the `test` dependency group installs it:

``` bash
python -m spacy download es_core_news_sm
```

## Datasets { #datasets }

The [corpus of literature](datasets/spanishliterature.md), the [sonnets](datasets/spanishsonnets.md) and the [frequency dictionary](datasets/freqdict.md) are downloaded once by their `download()` method; the statistics of [`LexicalStats`](stats/lexical_stats.md) by the dictionary and [`keyness`](corpus/keyness.md) against it need `FreqDict().download()`. The archives go to the directory `ests_data` next to the installed package (`ests.constants.DEFAULT_DATA_DIR`), `dicts` for the dictionary and `texts` for the corpus and the sonnets. Where that directory cannot be written, pass another one in `data_dir` (`FreqDict(data_dir="...")`) or set the environment variable `ESTS_DATA_DIR` before the package is imported:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
