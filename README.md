<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/esTS/master/docs/img/ests.png" alt="esTS" width="340">
</p>

<h1 align="center">esTS</h1>

<p align="center">
  <i>¿Cómo esTáS, texto?</i>
</p>

<p align="center">
  <b>Spanish Texts Statistics</b> - a library for statistics extraction from texts in Spanish
</p>

<p align="center">
  <a href="https://sergeyshk.github.io/esTS/">Documentation</a> ·
  <a href="https://pypi.org/project/pyests/">PyPI</a> ·
  <a href="https://github.com/SergeyShk/esTS/blob/master/README.es.md">Español</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/pyests/"><img src="https://img.shields.io/pypi/v/pyests?logo=pypi&logoColor=FFE873" alt="Version"></a>
  <a href="https://pypi.org/project/pyests/"><img src="https://img.shields.io/pypi/pyversions/pyests.svg?logo=python&logoColor=FFE873" alt="Supported Python versions"></a>
  <a href="https://github.com/SergeyShk/esTS/actions/workflows/ci.yml"><img src="https://github.com/SergeyShk/esTS/actions/workflows/ci.yml/badge.svg" alt="Build"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/SergeyShk/esTS/blob/master/LICENSE.txt"><img src="https://img.shields.io/github/license/sergeyshk/esTS.svg" alt="License"></a>
</p>

---

**esTS** computes for Spanish texts what usually requires assembling several separate tools: basic statistics, readability, lexical diversity and morphology - by published formulas with the coefficients and the scales of their authors, and by the parts of speech and the features of Universal Dependencies.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy): sentences, words and character N-grams are extracted by rules, syllables and stress follow from the orthography, and only the morphological statistics need a trained model.

* **[Object extraction](https://sergeyshk.github.io/esTS/extractors/sentences/)** - configurable sentence, word and character N-gram tokenizers that know the inverted marks, the dialogue dash and the abbreviations of Spanish
* **[Syllables and stress](https://sergeyshk.github.io/esTS/syllables/)** - rule-based syllabification and the stressed syllable derived from the spelling, with no dictionary
* **[Basic statistics](https://sergeyshk.github.io/esTS/stats/basic_stats/)** - counts of sentences, words, letters, syllables and punctuation marks by type, with distributions and normalized shares
* **[Readability metrics](https://sergeyshk.github.io/esTS/stats/readability_stats/)** - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad µ, SOL, LIX and RIX, with a consensus grade, the school stages of Spain and reading time
* **[Lexical diversity metrics](https://sergeyshk.github.io/esTS/stats/diversity_stats/)** - TTR and its variations, MATTR, MSTTR, MTLD, HD-D, Simpson's and Yule's indices, entropy, Zipf's and Heaps' laws
* **[Morphological statistics](https://sergeyshk.github.io/esTS/stats/morph_stats/)** - parts of speech and fourteen grammatical features of Universal Dependencies, with the markers of Spanish: the moods, the non-finite forms, `ser` against `estar`, the adverbs in `-mente`

Syntax and cohesion come in the rest of 0.2, corpus measures and stylometry in 0.3, style, phonostatistics, metre and rhyme in 0.4.

## Installation

Requires Python 3.11 or newer.

```bash
pip install pyests
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pyests
```

The distribution on PyPI is `pyests`, the package it installs is `ests`. The basic statistics, the readability and the lexical diversity metrics need no spaCy model; the morphological statistics do, and so does parsing a text yourself to pass the `Doc` instead of a string:

```bash
python -m spacy download es_core_news_sm
```

## Quick start

```python
>>> from ests import BasicStats, DiversityStats, ReadabilityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

>>> BasicStats(text).get_stats()
{'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
 'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
 'n_sents': 1,
 'n_words': 10,
 'n_unique_words': 8,
 'n_long_words': 5,
 'n_complex_words': 5,
 'n_simple_words': 5,
 'n_monosyllable_words': 4,
 'n_polysyllable_words': 6,
 'n_chars': 71,
 'n_letters': 60,
 'n_spaces': 9,
 'n_syllables': 23,
 'n_punctuations': 2,
 'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0,
                    'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0,
                    'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0,
                    'parentheses': 0, 'other': 0}}

>>> ReadabilityStats(text).flesch_reading_easy
53.545000000000016

>>> DiversityStats(text).ttr
0.8
```

## Features

### Object extraction

The library allows creating your own tools for sentence, word and character N-gram extraction from a text, which can be further employed for counting statistics. The sentence splitter knows the inverted marks, the dash of a line of dialogue with the remark of the narrator, the abbreviations and the initials of Spanish; the word tokenizer keeps clitics, ordinals and numbers written the Spanish way together, and lemmas come from [simplemma](https://github.com/adbar/simplemma), which needs no model.

```python
>>> from ests import CharNgramsExtractor, SentsExtractor, WordsExtractor

>>> SentsExtractor().extract("—¿Vienes? —preguntó María. ¡Claro que sí!")
('—¿Vienes? —preguntó María.', '¡Claro que sí!')

>>> we = WordsExtractor(use_lexemes=True, stopwords=["de", "y"], filter_nums=True, ngram_range=(1, 2))
>>> we.extract("Hay 3 clases de mentiras y estadísticas")
('haber', 'clase', 'mentira', 'estadística', 'haber_clase', 'clase_mentira', 'mentira_estadística')

>>> CharNgramsExtractor(n=3, lowercase=True).extract("estadísticas")[:5]
('est', 'sta', 'tad', 'adí', 'dís')
```

More in the [documentation](https://sergeyshk.github.io/esTS/extractors/sentences/).

<details>
<summary><b>Syllables and stress</b></summary>

<br>

Spanish spelling encodes both the syllable boundaries and the stress, so the library needs no dictionary: diphthongs, hiatuses and triphthongs, the silent `u` of `qu` and `gu`, the vocalic `y`, the `h` inside a diphthong and the consonant clusters give the syllables; the written accent, or the ending of the word when there is none, gives the stressed syllable. Adverbs in `-mente` and hyphenated compounds carry two stresses.

```python
>>> from ests.syllables import stress_type, syllabify, word_stress, word_stresses

>>> syllabify("murciélago")
['mur', 'cié', 'la', 'go']

>>> syllabify("averiguáis")
['a', 've', 'ri', 'guáis']

>>> word_stress("construir"), stress_type("construir")
(1, 'aguda')

>>> word_stresses("fácilmente")
[0, 2]
```

More in the [documentation](https://sergeyshk.github.io/esTS/syllables/).

</details>

<details>
<summary><b>Basic statistics</b></summary>

<br>

The library allows extracting the following statistics from a text:

*   the number of sentences
*   the number of words
*   the number of unique words
*   the number of long words
*   the number of complex words
*   the number of simple words
*   the number of monosyllable words
*   the number of polysyllable words
*   the number of characters
*   the number of letters
*   the number of spaces
*   the number of syllables
*   the number of punctuation marks and their distribution by type
*   the distribution of words by the number of letters
*   the distribution of words by the number of syllables

A complex word has three or more syllables and a long word seven or more letters, as the Spanish readability formulas count them. Any statistic can be printed in a readable form:

```python
>>> from ests import BasicStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> BasicStats(text).print_stats()
     Statistic      |  Value
------------------------------
Sentences           |    1
Words               |    10
Unique words        |    8
Long words          |    5
Complex words       |    5
Simple words        |    5
Monosyllabic words  |    4
Polysyllabic words  |    6
Characters          |    71
Letters             |    60
Spaces              |    9
Syllables           |    23
Punctuation marks   |    2
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/basic_stats/).

</details>

<details>
<summary><b>Readability metrics</b></summary>

<br>

The library allows counting the following readability metrics:

*   Flesch reading ease with the coefficients of Szigriszt-Pazos or of Fernández Huerta
*   Gutiérrez de Polini comprehensibility formula
*   Crawford grade
*   Legibilidad µ
*   SOL grade, the SMOG index converted to Spanish
*   LIX readability measure
*   RIX readability measure

An interpretation layer works on top of the formulas: the band of a scale for the reading ease and for Legibilidad µ, a consensus grade as the median of the grade formulas, the school stage and the reader age of Spain, and reading time by the norms of Spanish-speaking readers.

The coefficients of the Flesch reading ease are selected by the `preset` argument: by default the *fórmula de perspicuidad* of Szigriszt-Pazos with the INFLESZ scale validated on texts for patients (`general`); the coefficients of Fernández Huerta with the bands of their author are available as `classic`.

```python
>>> from pprint import pprint
>>> from ests import ReadabilityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> rs = ReadabilityStats(text)

>>> pprint(rs.get_stats(), sort_dicts=False)
{'flesch_reading_easy': 53.545000000000016,
 'gutierrez_polini_index': 33.5,
 'crawford_grade': 5.812999999999999,
 'mu_index': 50.943396226415096,
 'sol_grade': 9.258359866374562,
 'lix': 60.0,
 'rix': 5.0,
 'consensus_grade': 9.0,
 'reading_time': 0.03597122302158273}

>>> rs.print_stats()
                   Metric                    |  Value
-------------------------------------------------------
Flesch reading ease (Szigriszt-Pazos)        |  53.55
Gutiérrez de Polini comprehensibility        |  33.50
Crawford grade                               |   5.81
Legibilidad µ                                |  50.94
SOL grade (SMOG for Spanish)                 |   9.26
LIX readability index                        |  60.00
RIX readability index                        |   5.00
Consensus grade                              |   9.00
Reading time (min)                           |   0.04

>>> rs.describe_level()
'algo difícil'

>>> rs.describe_grade()
'ESO (12-16 years)'
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/readability_stats/).

</details>

<details>
<summary><b>Lexical diversity metrics</b></summary>

<br>

The library allows counting 32 lexical diversity metrics, among them:

*   Type-Token Ratio and its variations: RTTR, CTTR, Herdan, Summer, Maas, Dugast
*   Moving Average Type-Token Ratio and Mean Segmental Type-Token Ratio
*   Measure of Textual Lexical Diversity and its moving-window variants MA-MTLD and MTLD-W
*   Hypergeometric Distribution D
*   Simpson's index, its reciprocal and the Gini-Simpson index
*   the hapax index (Honoré's R), the measures of Yule, Herdan, Sichel, Michéa, Brunet, Dugast and Baayen
*   Shannon entropy, evenness and perplexity
*   the slope of Zipf's law, the Zipf-Mandelbrot fit and the exponent of Heaps' law

Any metric can be computed over windows of equal length, which is the standard way to compare texts of different lengths: the mean over the windows comes with a confidence interval.

```python
>>> from ests import DiversityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> ds = DiversityStats(text)

>>> ds.ttr, ds.mtld, ds.yule_k
(0.8, 14.000000000000004, 600.0)

>>> ds.frequency_spectrum
{1: 7, 3: 1}

>>> DiversityStats("La legibilidad de un texto depende de la longitud de sus oraciones y de sus "
...                "palabras. Las fórmulas clásicas miden esas dos magnitudes y las combinan en "
...                "un solo número. Ninguna de ellas mide la comprensión: miden la superficie "
...                "del texto.").windowed("ttr", window_len=10)
WindowStats(mean=0.875, std=0.1258305739211792, lower=0.6747754774664074, upper=1.0752245225335926, n_windows=4)
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/diversity_stats/).

</details>

<details>
<summary><b>Morphological statistics</b></summary>

<br>

The library annotates a text with the parts of speech and the grammatical features of Universal Dependencies, as the Spanish models of spaCy give them, and counts them:

*   the part of speech and fourteen features: case, definiteness, degree, gender, mood, numeral type, number, person, polarity, possessive, pronoun type, reflexive, tense and verb form
*   the distribution of the words by the values of any feature, and the parse of the text word by word
*   the markers of Spanish: the moods among the finite forms, the non-finite forms, `ser` against `estar`, the adverbs in `-mente`

```python
>>> from ests import MorphStats

>>> ms = MorphStats("Si tuviera tiempo, leería el libro que me recomendaste ayer")

>>> ms.get_stats("mood", "tense", filter_none=True)
{'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1}, 'tense': {'Imp': 1, 'Pres': 1}}

>>> ms.tags[1]
'Mood=Sub|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin'

>>> ms.explain_text("pos", "mood", filter_none=True)[1]
('tuviera', {'pos': 'VERB', 'mood': 'Sub'})

>>> MorphStats("Ella es alta pero hoy está cansada y habla lentamente").get_markers()["p_ser"]
0.5
```

The statistics need a spaCy model: a text is parsed with `es_core_news_sm`, and any other pipeline can be passed in `nlp`.

More in the [documentation](https://sergeyshk.github.io/esTS/stats/morph_stats/).

</details>

## Development

The project uses [uv](https://docs.astral.sh/uv/) for dependency management and [ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS

make deps        # create the environment and install dependencies
make test        # run the tests and docstring examples (doctest)
make lint        # ruff + mypy
```

Run `make help` for the full list of commands.

The documentation is bilingual: English pages are `docs/*.md`, Spanish ones are `docs/*.es.md` next to them ([mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)); when editing a page, update both versions.

The installed version is `ests.__version__`. All exceptions inherit `ests.EstsError` and one of the built-in classes (`SourceError` and `ParameterError` - `ValueError`, `SourceTypeError` - `TypeError`, `UnknownStatError` - `KeyError`), so `except ValueError` keeps working. The library prints nothing on its own: its messages go to the `ests` logger (`logging.getLogger("ests")`) and are silent by default.

Before submitting changes, install the hooks that run the linters on commit and the tests on push:

```bash
uv run pre-commit install
```

## Contributing

Bug reports, ideas and pull requests are welcome - [issues](https://github.com/SergeyShk/esTS/issues) are open. The workflow, the checks to run before submitting a pull request and how to shape the changes are described in [CONTRIBUTING.md](https://github.com/SergeyShk/esTS/blob/master/CONTRIBUTING.md); the rules of conduct are in the [code of conduct](https://github.com/SergeyShk/esTS/blob/master/CODE_OF_CONDUCT.md).

<details>
<summary><b>Project structure</b></summary>

<br>

*   **docs** - project documentation
*   **ests**:
    *   basic_stats.py - basic text statistics
    *   constants.py - constants of the Spanish language and of the metrics
    *   diversity_stats.py - lexical diversity metrics
    *   exceptions.py - library exceptions
    *   extractors.py - tools for object extraction from a text
    *   morph_stats.py - morphological statistics
    *   readability_stats.py - readability metrics
    *   syllables.py - syllabification and stress
    *   utils.py - helper tools
*   **tests** - tests mirroring the package structure

</details>

## Authors

*   Sergey Shkarin (kouki.sergey@gmail.com)

## License

[MIT](https://github.com/SergeyShk/esTS/blob/master/LICENSE.txt)

## Citation

Please use the following BibTeX entry for citing **esTS** if you use it in your research or software. Citations are helpful for the continued development and maintenance of this library. The same metadata is in [CITATION.cff](https://github.com/SergeyShk/esTS/blob/master/CITATION.cff) - GitHub shows it under the "Cite this repository" button.

```bibtex
@software{esTS,
  author = {Sergey Shkarin},
  title = {{esTS, a library for statistics extraction from texts in Spanish}},
  year = 2026,
  url = {https://github.com/SergeyShk/esTS}
}
```
