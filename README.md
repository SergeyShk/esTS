# Spanish Texts Statistics (esTS)

[![Build](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml/badge.svg)](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Versión en español: [README.es.md](https://github.com/SergeyShk/esTS/blob/master/README.es.md)

**esTS** computes for Spanish text what usually requires assembling several separate tools: basic counts, readability formulas, lexical diversity and, in the releases to come, morphological, syntactic and cohesion statistics, style markers, phonostatistics, metre and rhyme, corpus measures and stylometry - by published formulas adapted to Spanish, with deterministic results and no neural networks inside.

It is the Spanish sibling of [ruTS](https://github.com/SergeyShk/ruTS), the Russian text statistics library, and follows its structure and naming: every statistic is a class with `get_stats()`. Components for a [spaCy](https://github.com/explosion/spaCy) pipeline come with the morphology and syntax of 0.2.

> **Status:** 0.1 is the first release. It covers text extraction, syllables and stress, basic statistics, readability and lexical diversity; morphology, syntax and cohesion on Universal Dependencies follow in 0.2.

## What it computes

Release 0.1:

* **Extraction** - sentences with Spanish punctuation (`¿ ¡`, dialogue dashes, abbreviations), words with clitics, lemmas via `simplemma`, character N-grams
* **Syllables and stress** - rule-based syllabification and stress derived from orthography, no dictionary needed
* **Basic statistics** - sentences, words, letters, syllables and punctuation by type, with distributions and normalized shares
* **Readability** - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, LIX and RIX, with presets, school stages and reading time
* **Lexical diversity** - TTR and its variants, MATTR, MSTTR, MTLD, HD-D, Yule, Herdan, Brunet, entropy, Zipf and Heaps fits, windowed computation

Planned:

* **Morphology, syntax and cohesion** (0.2) - on Universal Dependencies features and relations from spaCy `es_core_news_*` models, with pipeline components
* **Corpus measures and stylometry** (0.3) - keywords, collocations, dispersion, KWIC, Burrows's Delta, Zeta, corpus comparison
* **Style and sound** (0.4) - SEO-style metrics, plain language (lenguaje claro) markers, phonostatistics, syllabic metre and rhyme

## Installation

``` bash
pip install ests
```

Python 3.11 or newer. The statistics of 0.1 need no trained spaCy model; a model is needed only to pass a parsed `Doc` instead of a string.

## Quick start

``` python
from ests import BasicStats, ReadabilityStats

text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
BasicStats(text).n_syllables
# 23
ReadabilityStats(text).describe_level()
# 'algo difícil'
```

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependencies and [ruff](https://docs.astral.sh/ruff/) for linting and formatting. Python 3.11 or newer is required.

```bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS

make deps                   # create the environment and install all dependencies
uv run pre-commit install   # hooks: linters on commit, tests on push
make lint                   # ruff check, ruff format --check, mypy
make test                   # pytest with doctests
make docs-build             # mkdocs build --strict
```

The full list of commands is in `make help`. Contribution guidelines are in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE.txt)
