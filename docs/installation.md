# Installation

## Requirements

*   `python` 3.11 or newer
*   `spaCy` 3.8.17 or newer within 3
*   [`anyts`](https://sergeyshk.github.io/anyTS/) 0.6.5 or newer within 0.6, the language-independent core: the extractors, the basic statistics and the common readability formulas, the lexical diversity metrics, the corpus measures, the plots and the machinery of the highlighting come from it with the hooks of Spanish: the tokens and sentences of anySeg, the lemmas of esMorph, the syllables of esTS
*   [`anyseg`](https://github.com/SergeyShk/anySeg) 0.4 or newer within 0.4, the segmenter into tokens and sentences
*   [`esmorph`](https://github.com/SergeyShk/esMorph) 0.4 or newer within 0.4, the morphological analyzer: the lemmas, the parts of speech and the features of a text; its dictionary, built from the English and the Spanish Wiktionary with the context model of the UD treebanks AnCora and GSD, is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
*   `numpy`, `scipy`, `pandas`
*   `matplotlib` and `graphviz` for the [visualizers](visualizers/zipf.md)

The dependencies are installed with the package. anySeg and esMorph are written in Rust and come as wheels for Linux, macOS and Windows on x86-64 and arm64; elsewhere pip builds them from the source, which needs [Rust](https://rustup.rs/). `import ests` loads neither spaCy nor matplotlib nor pandas, and the statistics of a string leave spaCy out, the morphology and the lexicon included: it comes with the first statistics that read the parse of its model - the syntax and the cohesion -, and the plots and the corpus functions on first use.

!!! warning "Graphviz"
    The `graphviz` package among the dependencies is only a wrapper: rendering the [word tree](visualizers/word_tree.md) and the [network of collocations](visualizers/corpus.md#collocation_network) requires the executables of [Graphviz](https://graphviz.org/download/), installed separately (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`), otherwise `render()` and displaying the graph in Jupyter fail with `ExecutableNotFound`. Nothing else needs them. The network of collocations uses the layout engine `neato`, which newer Ubuntu ships apart (`apt install libgvplugin-neato-layout8`).

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

Basic statistics, readability, lexical diversity, the [morphological](stats/morph_stats.md) and the [lexical sophistication statistics](stats/lexical_stats.md), the style metrics, phonostatistics and verse statistics of a string need no trained model: the morphology comes from esMorph. The [syntactic](stats/syntax_stats.md) (with a parser) and the [cohesion statistics](stats/cohesion_stats.md) of a string need one, and so do the features of a text, the [comparison of corpora](corpus/compare.md) and building a `Doc` yourself, best with [`ests.load_pipeline()`](components.md#load_pipeline), which gives a `Doc` the tokens and the sentences of its string. The test suite needs it too; the `test` dependency group installs it:

``` bash
python -m spacy download es_core_news_sm
```

## Datasets { #datasets }

The [corpus of literature](datasets/spanishliterature.md), the [sonnets](datasets/spanishsonnets.md) and the [frequency dictionary](datasets/freqdict.md) are downloaded once by their `download()` method; the statistics of [`LexicalStats`](stats/lexical_stats.md) by the dictionary and [`keyness`](corpus/keyness.md) against it need `FreqDict().download()` or the command [`ests download`](cli.md). The archives go to the directory `ests_data` next to the installed package (`ests.constants.DEFAULT_DATA_DIR`), `dicts` for the dictionary and `texts` for the corpus and the sonnets. Where that directory cannot be written, pass another one in `data_dir` (`FreqDict(data_dir="...")`) or set the environment variable `ESTS_DATA_DIR` before the package is imported:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
