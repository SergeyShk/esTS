# Spanish Texts Statistics (esTS)

[![Build](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml/badge.svg)](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Versión en español: [README.es.md](README.es.md)

**esTS** will compute for Spanish text what usually requires assembling several separate tools: basic counts, readability formulas, lexical diversity and sophistication, morphological, syntactic and cohesion statistics, style markers, phonostatistics, metre and rhyme, corpus measures and stylometry - by published formulas adapted to Spanish, with deterministic results and no neural networks inside.

It is the Spanish sibling of [ruTS](https://github.com/SergeyShk/ruTS), the Russian text statistics library, and follows its structure and naming: every statistic is available as a class with `get_stats()` and as a [spaCy](https://github.com/explosion/spaCy) pipeline component.

> **Status:** in development towards 0.1. The repository, tooling, CI and documentation are in place, and the first module is written: extraction of sentences, words and character N-grams. The first release (0.1) will also cover syllabification and stress, basic statistics, readability with presets and lexical diversity.

## Planned scope

* **Extraction** - sentences and words with Spanish punctuation (`¿ ¡`), clitics, lemmas via spaCy or `simplemma`
* **Syllables and stress** - rule-based syllabification and stress derived from orthography, no dictionary needed
* **Readability** - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, with presets
* **Lexical diversity** - TTR and its variants, MTLD, HD-D, Yule, Herdan, Brunet, entropy, Zipf and Heaps fits, windowed computation
* **Morphology, syntax and cohesion** - on Universal Dependencies features and relations from spaCy `es_core_news_*` models
* **Corpus measures and stylometry** - keywords, collocations, dispersion, KWIC, Burrows's Delta, Zeta, corpus comparison
* **Style and sound** - SEO-style metrics, plain language (lenguaje claro) markers, phonostatistics, syllabic metre and rhyme

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
