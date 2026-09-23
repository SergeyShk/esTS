# Installation

## Requirements

*   `python` 3.11 or newer
*   `spaCy` 3.7 or newer
*   `numpy`, `scipy`, `simplemma`

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

Basic statistics, readability and lexical diversity need no trained model: sentences, words and character N-grams are extracted by rules and by the tokenizer of the blank Spanish pipeline, syllables and stress by the orthography. The [morphological statistics](stats/morph_stats.md) need one, and so does building a `Doc` yourself to pass it to the statistics instead of a string; the test suite needs it too, where it comes with the `test` dependency group:

``` bash
python -m spacy download es_core_news_sm
```
