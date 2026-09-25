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
  <a href="https://doi.org/10.5281/zenodo.22924655"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.22924655.svg" alt="DOI"></a>
</p>

---

**esTS** computes for Spanish texts what usually requires assembling several separate tools: basic statistics, readability, lexical diversity, lexical sophistication, style, phonostatistics, morphology, syntax and cohesion - by published formulas with the coefficients and the scales of their authors, and by the parts of speech and the features of Universal Dependencies.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy): sentences, words and character N-grams are extracted by rules, syllables and stress follow from the orthography, and only the morphological, the syntactic, the cohesion and the lexical sophistication statistics, the verbal nouns of the style metrics, the profile of the function words and the comparison of corpora need a trained model.

* **[Object extraction](https://sergeyshk.github.io/esTS/extractors/sentences/)** - configurable sentence, word and character N-gram tokenizers that know the inverted marks, the dialogue dash and the abbreviations of Spanish
* **[Syllables and stress](https://sergeyshk.github.io/esTS/syllables/)** - rule-based syllabification and the stressed syllable derived from the spelling, with no dictionary
* **[Basic statistics](https://sergeyshk.github.io/esTS/stats/basic_stats/)** - counts of sentences, words, letters, syllables and punctuation marks by type, with distributions and normalized shares
* **[Readability metrics](https://sergeyshk.github.io/esTS/stats/readability_stats/)** - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad µ, SOL, LIX and RIX, with a consensus grade, the school stages of Spain and reading time
* **[Lexical diversity metrics](https://sergeyshk.github.io/esTS/stats/diversity_stats/)** - TTR and its variations, MATTR, MSTTR, MTLD, HD-D, Simpson's and Yule's indices, entropy, Zipf's and Heaps' laws
* **[Morphological statistics](https://sergeyshk.github.io/esTS/stats/morph_stats/)** - parts of speech and fifteen grammatical features of Universal Dependencies, with the markers of Spanish: the moods, the non-finite forms, `ser` against `estar`, the adverbs in `-mente`
* **[Corpus measures](https://sergeyshk.github.io/esTS/corpus/keyness/)** - keywords against a reference corpus, collocations, the dispersion of a word over the parts of a text, a KWIC concordance and the stylometry of authorship: Burrows's Delta with its variants, Zeta, the Mendenhall curve, the profile of the function words; the comparison of two corpora by 132 features of a text with effect sizes
* **[Visualizers](https://sergeyshk.github.io/esTS/visualizers/zipf/)** - Zipf's law, literature fingerprinting, a word tree, lexical dispersion and keywords, a network of collocations, a dendrogram, PCA and MDS by Delta, vocabulary growth, sentence lengths, and the highlighting of a text by the fragments the statistics count: long sentences, passives, chains of de, clichés
* **[Datasets](https://sergeyshk.github.io/esTS/datasets/spanishliterature/)** - Spanish-language literature in the public domain: 150 works by 33 authors from Spain, Latin America and the Philippines in prose, poems, drama and publicism, with the genre, the years and the country; 4,259 sonnets of the 15th-20th centuries with the metrical pattern and the rhyme of every line; a frequency dictionary of 83,785 lemmas by Google Books Ngram with ipm, range and dispersion
* **[spaCy components](https://sergeyshk.github.io/esTS/components/)** - every statistics class as a component of a pipeline, the statistics attached to the `Doc` in one pass
* **[Cohesion statistics](https://sergeyshk.github.io/esTS/stats/cohesion_stats/)** - the overlap of nouns, arguments and content words between sentences, givenness and temporal cohesion in the manner of Coh-Metrix, with the density of 255 Spanish discourse markers
* **[Lexical sophistication statistics](https://sergeyshk.github.io/esTS/stats/lexical_stats/)** - how rare the words of a text are in the language: the frequency, range and dispersion of the lemmas by a dictionary of Google Books Ngram, the frequency bands top-1000 to 10000, surprisal, perplexity and lexical density
* **[Style metrics](https://sergeyshk.github.io/esTS/stats/style_stats/)** - the SEO indicators of Advego and Text.ru (nausea, water content, spam score, naturalness by Zipf's law, keyword density) and the markers of the officialese style by the Spanish guides to plain language: verbal nouns, compound prepositions, parenthetical expressions and clichés
* **[Phonostatistics](https://sergeyshk.github.io/esTS/stats/phon_stats/)** - the shares of the classes of sounds, consonant clusters, hiatuses, open syllables, hardness and the indices of alliteration and assonance, over the sounds of a rule-based transcription
* **[Syntactic statistics](https://sergeyshk.github.io/esTS/stats/syntax_stats/)** - the dependency tree by distances, depth, clauses and coordination, with the constructions of the administrative style: the passive with `ser` and with `se`, the participial and the gerund clauses, the chains of `de`, the split predicates

Metre and rhyme come in 0.4.

## Installation

Requires Python 3.11 or newer.

```bash
pip install pyests
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add pyests
```

The distribution on PyPI is `pyests`, the package it installs is `ests`. The basic statistics, the readability, the lexical diversity metrics and the phonostatistics need no spaCy model; the morphological, the syntactic, the cohesion and the lexical sophistication statistics of a string do, and so do the verbal nouns of the style metrics, the profile of the function words, the features of a text and the comparison of corpora, and parsing a text yourself to pass the `Doc` instead of a string:

```bash
python -m spacy download es_core_news_sm
```

The statistics by the frequency dictionary need it downloaded once with `FreqDict().download()`. The datasets go to the directory `ests_data` next to the installed package; another one is passed in `data_dir` or set in the environment variable `ESTS_DATA_DIR` before the package is imported.

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

*   the part of speech and fifteen features: case, definiteness, degree, gender, mood, numeral type, number, person, polarity, politeness, possessive, pronoun type, reflexive, tense and verb form
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

<details>
<summary><b>Syntactic statistics</b></summary>

<br>

The library measures the dependency tree of Universal Dependencies and the constructions that the Spanish guides to clear language warn about:

*   the complexity of the tree: dependency distances, depth, leaves and subtrees, valency of the finite verbs, coordination chains, clauses and subordinate clauses, modifiers per noun
*   the constructions: the passive with `ser` and with `se`, the participial and the gerund clauses, the chains of `de`, the split predicates, the impersonal `se`, the words of negation, the ratio of nouns to verbs

```python
>>> from ests import SyntaxStats

>>> text = ("La revisión de las cuentas fue realizada por el comité. "
...         "Se llevó a cabo la reforma sin que nadie hiciera mención de los problemas.")
>>> ss = SyntaxStats(text)

>>> ss.n_sents, ss.n_words
(2, 24)

>>> ss.p_passive, ss.noun_verb_ratio
(0.6666666666666666, 2.3333333333333335)

>>> ss.split_predicates
('llevó cabo', 'hiciera mención')

>>> round(ss.mean_dependency_distance, 2)
2.05
```

The statistics need a parse: a text is parsed with `es_core_news_sm`, and any other pipeline can be passed in `nlp`.

More in the [documentation](https://sergeyshk.github.io/esTS/stats/syntax_stats/).

</details>

<details>
<summary><b>Cohesion statistics</b></summary>

<br>

The library measures referential cohesion in the manner of Coh-Metrix and of its Spanish adaptation Coh-Metrix-Esp:

*   the overlap of nouns, of arguments and of content words between adjacent sentences and between all pairs of sentences, binary and proportional
*   givenness: pronouns, demonstratives and the content words whose lemma was already used
*   temporal cohesion: the repetition of the tense and of the mood of the verbs of adjacent sentences
*   the density of 255 Spanish discourse markers by class - causal, adversative, concessive, temporal, additive, conditional, reformulative - and by kind

```python
>>> from ests import CohesionStats

>>> text = ("El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve el problema. "
...         "Por lo tanto, la comisión aplazó la decisión.")
>>> cs = CohesionStats(text)

>>> cs.n_sents, cs.n_words
(3, 23)

>>> cs.noun_overlap_adjacent, round(cs.p_given, 3)
(0.5, 0.167)

>>> cs.c_connectors
{'por lo tanto': 1, 'sin embargo': 1}

>>> round(cs.connectors, 2), round(cs.connectors_causal, 2)
(86.96, 43.48)
```

The statistics need the annotation: a text is parsed with `es_core_news_sm`, and any other pipeline can be passed in `nlp`.

More in the [documentation](https://sergeyshk.github.io/esTS/stats/cohesion_stats/).

</details>

<details>
<summary><b>Lexical sophistication statistics</b></summary>

<br>

How rare the words of a text are in the language, in the manner of TAALES: the mean frequency, range and dispersion of the lemmas by the frequency dictionary of Google Books Ngram, the shares of the words of the frequency bands top-1000, 2000, 5000 and 10000, the surprisal and the perplexity by the unigram model of the dictionary, the lexical density. The bands and the density work out of the box; the statistics by the dictionary need it downloaded once.

```python
>>> from ests import LexicalStats
>>> from ests.datasets import FreqDict

>>> FreqDict().download()
>>> ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
>>> ls.coverage, ls.p_top1000, round(ls.surprisal, 2)
(0.8571428571428571, 0.42857142857142855, 13.71)
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/lexical_stats/).

</details>

<details>
<summary><b>Style metrics</b></summary>

<br>

The SEO indicators of Advego and Text.ru - nausea, water content, spam score, naturalness by Zipf's law, keyword density - and the markers of the officialese style that the Spanish guides to plain language warn about: the nouns derived from a verb, the compound prepositions of the administrative style, the parenthetical expressions and the clichés, whose verbs are found in their forms (`se procedió a`, `ha dado cumplimiento`).

```python
>>> from ests import StyleStats

>>> ss = StyleStats("Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad.")
>>> ss.compound_prepositions, ss.cliches, ss.verbal_nouns
(6.25, 12.5, 20.0)
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/style_stats/).

</details>

<details>
<summary><b>Phonostatistics</b></summary>

<br>

The shares of the classes of sounds, the consonant clusters, the hiatuses, the open syllables, the hardness and the indices of alliteration and assonance, counted over the sounds of a rule-based transcription rather than over the letters: `h` and the `u` of `que` are silent, `ll`, `ch` and `rr` are one sound, `x` is two.

```python
>>> from ests import PhonStats

>>> ps = PhonStats("Los suspiros se escapan de su boca de fresa")
>>> round(ps.p_voiceless, 3), round(ps.hardness, 3), ps.sounds[-1]
(0.371, 0.684, ('f', 'r', 'e', 's', 'a'))
```

More in the [documentation](https://sergeyshk.github.io/esTS/stats/phon_stats/).

</details>

<details>
<summary><b>spaCy components</b></summary>

<br>

Every statistics class is also a component of a pipeline, so a text is annotated and measured in one pass and the statistics travel with the `Doc`:

```python
>>> import ests
>>> import spacy

>>> nlp = spacy.load("es_core_news_sm")
>>> for factory in ("basic", "morph", "syntax"):
...     _ = nlp.add_pipe(f"ests_{factory}", name=factory, last=True)

>>> nlp.pipe_names[-3:]
['basic', 'morph', 'syntax']

>>> doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
>>> doc._.basic.n_words, doc._.morph.pos[:2], doc._.syntax.tree_depth
(12, ('DET', 'NOUN'), 2.0)
```

The factories are `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style` and `ests_phon`; the name of the pipe is free and is what the extension is called.

More in the [documentation](https://sergeyshk.github.io/esTS/components/).

</details>

<details>
<summary><b>Corpus measures</b></summary>

<br>

The library compares corpora and describes the use of a word, with the measures of corpus linguistics:

*   keywords of a target corpus against a reference one or against the frequency dictionary of Google Books Ngram: the log-likelihood with its p-value, Log Ratio, chi-square, %DIFF, BIC, ELL and the odds ratio
*   collocations by logDice, MI, MI³, t-score, Dice, log-likelihood, NPMI and minimum sensitivity, checked against NLTK
*   the dispersion of a word over the parts of a text: DP of Gries, normalized DP, Juilland's D, Carroll's D2, Rosengren's S and the Kullback-Leibler divergence
*   a KWIC concordance by word form or by lemma
*   stylometry: the distances between texts by Burrows's Delta and its variants, with the attribution of a text to reference authors, the markers of preferred and avoided words by Zeta, Kilgarriff's chi-square, the Mendenhall curve and the profile of the function words
*   the comparison of two corpora by 132 features of a text over windows of about the same size: Cliff's delta, Cohen's d and the AUC of every feature, the Mann-Whitney test with Holm's correction and a bootstrap interval of the difference of the medians that resamples whole texts

```python
>>> from ests import WordsExtractor
>>> from ests.corpus import collocations, keyness, kwic, zeta

>>> we = WordsExtractor(use_lexemes=True, lowercase=True)
>>> target = we.extract("El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
...                     "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros.")
>>> reference = we.extract("El perro estaba en el suelo y dormía. Después el perro comió y volvió a dormir. "
...                        "Mañana el perro saldrá a pasear.")

>>> [(k.word, round(k.g2, 2)) for k in keyness(target, reference, top_n=2)]
[('gato', 2.8), ('pájaro', 2.8)]

>>> [(c.left, c.right, round(c.score, 1)) for c in collocations(target, window=2, top_n=2)]
[('en', 'ventana', 13.0), ('estar', 'en', 12.7)]

>>> [line.keyword for line in kwic("Los gatos juegan y el gato duerme.", "gato", by_lemma=True)]
['gatos', 'gato']

>>> scores = zeta(target, reference, segment_size=10)
>>> [z.word for z in scores[:2]], [z.word for z in scores[-2:]]
(['gato', 'ventana'], ['dormir', 'perro'])
```

Words are compared as they are, so case, lemmas and stop words are chosen at the extraction.

More in the [documentation](https://sergeyshk.github.io/esTS/corpus/keyness/).

</details>

<details>
<summary><b>Datasets</b></summary>

<br>

*   [spanish_literature](https://sergeyshk.github.io/esTS/datasets/spanishliterature/) - Spanish-language literature in the public domain: 150 works by 33 authors from Spain, Latin America and the Philippines, from Cervantes to the 1920s, in prose, poems, drama and publicism; 65 million characters
*   [spanish_sonnets](https://sergeyshk.github.io/esTS/datasets/spanishsonnets/) - Spanish sonnets of the Diachronic Spanish Sonnet Corpus (DISCO) in the public domain: 4,259 sonnets by 1,167 authors of the 15th-20th centuries, every line with its metrical pattern and the label of its rhyme, the automatic annotation of DISCO (CC BY 4.0)
*   [freq_dict](https://sergeyshk.github.io/esTS/datasets/freqdict/) - a frequency dictionary of 83,785 Spanish lemmas from the books of Google Books Ngram of 1980-2019 (63 billion words): ipm, range and Juilland's D over the years, the number of books and the part of speech (CC BY 3.0)

The texts are cut to the text of the author, without title pages, notes of the transcribers and the editors, tables of contents and footnotes, and come with the genre, the author, the title, the years of the first publication and the country; the records can be filtered by any of them and by the length of the text.

```python
>>> from ests.datasets import SpanishLiterature

>>> sl = SpanishLiterature()
>>> sl.download()
>>> for record in sl.get_records(author="galdos", year_from=1880, year_to=1884):
...     print(record["title"], record["year_from"], len(record["text"]))
La desheredada 1881 820454
El amigo Manso 1882 521156
La de Bringas 1884 413730
Tormento 1884 477286
```

The archive (19 MB) is downloaded once by `download()` into the data directory and verified against its SHA-256 checksum; before the download `get_texts()` and `get_records()` raise `DatasetNotFoundError` with a hint.

More in the [documentation](https://sergeyshk.github.io/esTS/datasets/spanishliterature/).

</details>

<details>
<summary><b>Visualizers</b></summary>

<br>

*   [Zipf's law](https://sergeyshk.github.io/esTS/visualizers/zipf/) with the theoretical curve and the Zipf-Mandelbrot fit
*   [Literature fingerprinting](https://sergeyshk.github.io/esTS/visualizers/fingerprinting/) (Literature Fingerprinting)
*   [Word tree](https://sergeyshk.github.io/esTS/visualizers/word_tree/) (Word Tree)
*   [Corpus plots](https://sergeyshk.github.io/esTS/visualizers/corpus/): lexical dispersion, a chart of keywords, a network of collocations
*   [Stylometric plots](https://sergeyshk.github.io/esTS/visualizers/stylometry/): a dendrogram, the principal components and the multidimensional scaling by Delta, the Mendenhall curves
*   [Vocabulary growth and frequency spectrum](https://sergeyshk.github.io/esTS/visualizers/vocabulary/), [sentence lengths](https://sergeyshk.github.io/esTS/visualizers/sentences/) with a moving average

The matplotlib plots take the axes `ax` and return `Axes`, so they can be laid out on one figure; the network of collocations and the word tree are graphs of graphviz, whose executables render them. Cosine Delta separates three novels by Galdós from three by Unamuno:

```python
import matplotlib.pyplot as plt
from ests import WordsExtractor
from ests.corpus import delta
from ests.datasets import SpanishLiterature
from ests.visualizers import dendrogram_plot, pca_plot

# six novels by Galdós and Unamuno from the corpus of literature
titles = (
    "Marianela",
    "Misericordia",
    "Torquemada en la hoguera",
    "Niebla",
    "Abel Sánchez",
    "La tía Tula",
)
sl = SpanishLiterature()
sl.download()
novels = {
    record["title"]: record["text"]
    for author in ("galdos", "unamuno")
    for record in sl.get_records(author=author)
    if record["title"] in titles
}
we = WordsExtractor(lowercase=True)
corpus = {title: we.extract(novels[title]) for title in titles}
distances = delta(corpus, n_mfw=100, variant="cosine")

fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
dendrogram_plot(distances, ax=left)
pca_plot(corpus, n_mfw=100, ax=right)
```

<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/esTS/master/docs/img/stylometry.png" alt="Stylometric plots" width="760">
</p>

More in the [documentation](https://sergeyshk.github.io/esTS/visualizers/zipf/).

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

The installed version is `ests.__version__`. All exceptions inherit `ests.EstsError` and one of the built-in classes (`SourceError`, `ParameterError` and `DataFileError` - `ValueError`, `SourceTypeError` - `TypeError`, `UnknownStatError` - `KeyError`, `DatasetNotFoundError` - `OSError`, `DownloadError` - `RuntimeError`), so `except ValueError` keeps working. The library prints nothing on its own: its messages go to the `ests` logger (`logging.getLogger("ests")`) and are silent by default.

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
    *   cohesion_stats.py - cohesion statistics
    *   lexical_stats.py - lexical sophistication statistics
    *   components.py - components of a spaCy pipeline
    *   corpus - measures of corpus linguistics: keywords, collocations, dispersion, concordance, stylometry, comparison of corpora
    *   datasets - datasets: Spanish-language literature, the frequency dictionary
    *   constants.py - constants of the Spanish language and of the metrics
    *   diversity_stats.py - lexical diversity metrics
    *   exceptions.py - library exceptions
    *   extractors.py - tools for object extraction from a text
    *   morph_stats.py - morphological statistics
    *   readability_stats.py - readability metrics
    *   style_stats.py - style metrics
    *   phon_stats.py - phonostatistics
    *   syntax_stats.py - syntactic statistics
    *   syllables.py - syllabification and stress
    *   utils.py - helper tools
    *   visualizers - plots: Zipf's law, fingerprinting, word tree, corpus and stylometric plots, vocabulary growth, sentence lengths, text highlighting
*   **scripts** - scripts that build the archives of the datasets
*   **tests** - tests mirroring the package structure

</details>

## Authors

*   Sergey Shkarin (kouki.sergey@gmail.com)

## License

[MIT](https://github.com/SergeyShk/esTS/blob/master/LICENSE.txt)

## Citation

Please use the following BibTeX entry for citing **esTS** if you use it in your research or software. Citations are helpful for the continued development and maintenance of this library. The same metadata is in [CITATION.cff](https://github.com/SergeyShk/esTS/blob/master/CITATION.cff) - GitHub shows it under the "Cite this repository" button. The Concept DOI [10.5281/zenodo.22924655](https://doi.org/10.5281/zenodo.22924655) on Zenodo points at every version of the library; the DOI of a single version is on the page of its release.

```bibtex
@software{esTS,
  author = {Sergey Shkarin},
  title = {{esTS, a library for statistics extraction from texts in Spanish}},
  year = 2026,
  doi = {10.5281/zenodo.22924655},
  url = {https://github.com/SergeyShk/esTS}
}
```
