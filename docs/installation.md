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

The statistics of release 0.1 need no trained model: sentences, words and character N-grams are extracted by rules and by the tokenizer of the blank Spanish pipeline, syllables and stress by the orthography. A model is needed only to build a `Doc` yourself and pass it to the statistics instead of a string, and to run the test suite, where it comes with the `test` dependency group:

``` bash
python -m spacy download es_core_news_sm
```
