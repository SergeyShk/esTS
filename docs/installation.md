# Installation

The library is not published yet. Until the first release it can be installed from the repository.

## Requirements

*   `python` 3.11 or newer
*   `spaCy` 3.7 or newer with the `es_core_news_sm` model for morphology and syntax
*   `numpy`, `pandas`, `scipy`, `matplotlib`

## From the repository

``` bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS
uv sync --all-groups
```

The spaCy model is installed together with the `test` dependency group; for a separate environment:

``` bash
python -m spacy download es_core_news_sm
```

## From PyPI

After the first release:

``` bash
pip install ests
```
