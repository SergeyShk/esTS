# Spanish Texts Statistics (esTS)

![esTS](img/ests.svg)

*¿Cómo esTáS, texto?*

**esTS** computes statistics of Spanish texts: basic statistics, readability, lexical diversity, lexical sophistication, style, phonostatistics, morphology, syntax and cohesion - by published formulas with the coefficients and the scales of their authors, and by the parts of speech, the features and the dependencies of Universal Dependencies.

The library works both with raw strings and with `Doc` objects of [spaCy](https://github.com/explosion/spaCy); most statistics need no trained model ([Installation](installation.md#model)).

Try it without installing in the [demo on Hugging Face Spaces](https://huggingface.co/spaces/SergeyShk/esTS): paste a text and get its readability, the metrics, the plots and the highlighting of its fragments.

## Features

<div class="grid cards" markdown>

-   :material-scissors-cutting:{ .lg .middle } __Extraction__

    ---

    Tokenizers of [sentences](extractors/sentences.md), [words](extractors/words.md) and [character N-grams](extractors/char_ngrams.md) that know the inverted marks, the dialogue dash and the abbreviations of Spanish

    [:octicons-arrow-right-24: Extraction](extractors/sentences.md)

-   :material-format-letter-case:{ .lg .middle } __Syllables and stress__

    ---

    Division of a word into syllables and its stress by the orthographic rules, with no dictionary

    [:octicons-arrow-right-24: Syllables and stress](syllables.md)

-   :material-counter:{ .lg .middle } __Basic statistics__

    ---

    Numbers of sentences, words, letters, syllables and punctuation marks by type and their distributions

    [:octicons-arrow-right-24: Basic statistics](stats/basic_stats.md)

-   :material-book-open-variant:{ .lg .middle } __Readability__

    ---

    Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad µ, SOL, LIX and RIX with a consensus grade, the school stages of Spain and reading time

    [:octicons-arrow-right-24: Readability metrics](stats/readability_stats.md)

-   :material-chart-bell-curve:{ .lg .middle } __Lexical diversity__

    ---

    Type-Token Ratio and its variations, MATTR, MSTTR, Measure of Textual Lexical Diversity, HD-D, the indices of Simpson and Yule, entropy, the laws of Zipf and Heaps, over the whole text or over windows with confidence intervals

    [:octicons-arrow-right-24: Lexical diversity metrics](stats/diversity_stats.md)

-   :material-alphabetical-variant:{ .lg .middle } __Morphology__

    ---

    Parts of speech and fifteen grammatical features of Universal Dependencies with the markers of Spanish: the moods, the non-finite forms, the copulas `ser` and `estar`, the adverbs in `-mente`

    [:octicons-arrow-right-24: Morphological statistics](stats/morph_stats.md)

-   :material-file-tree:{ .lg .middle } __Syntax__

    ---

    Statistics of the dependency tree (dependency distances, depth, clauses, coordination) with the constructions of the administrative style: the passive with `ser` and with `se`, the participial and the gerund clauses, the chains of `de`, the split predicates

    [:octicons-arrow-right-24: Syntactic statistics](stats/syntax_stats.md)

-   :material-link-variant:{ .lg .middle } __Cohesion__

    ---

    Overlap of nouns, arguments and content words between sentences in the manner of Coh-Metrix, givenness, temporal cohesion and the density of 250 Spanish discourse markers by class

    [:octicons-arrow-right-24: Cohesion statistics](stats/cohesion_stats.md)

-   :material-school:{ .lg .middle } __Lexical sophistication__

    ---

    How rare the words of a text are, in the manner of TAALES: frequency, range, dispersion and surprisal by a [frequency dictionary](datasets/freqdict.md) of Google Books Ngram, the frequency bands top-1000 to 10000, lexical density

    [:octicons-arrow-right-24: Lexical sophistication statistics](stats/lexical_stats.md)

-   :material-feather:{ .lg .middle } __Style__

    ---

    SEO indicators of Advego and Text.ru (nausea, water content, spam score, naturalness by Zipf's law, keyword density) and the markers of the officialese by the Spanish-language guides to plain language: verbal nouns, compound prepositions, parenthetical expressions and clichés

    [:octicons-arrow-right-24: Style metrics](stats/style_stats.md)

-   :material-waveform:{ .lg .middle } __Phonetics__

    ---

    Shares of the classes of sounds of a rule-based transcription, consonant clusters, hiatuses, open syllables, hardness and the indices of alliteration and assonance

    [:octicons-arrow-right-24: Phonostatistics](stats/phon_stats.md)

-   :material-music-note:{ .lg .middle } __Verse__

    ---

    Metrical syllables and the meter of a poem, the stress profile and the types of the endecasílabo, the rhyme in full and by assonance with its scheme, the strophes and the form of a poem

    [:octicons-arrow-right-24: Verse statistics](stats/verse_stats.md)

-   :material-bookshelf:{ .lg .middle } __Corpus measures__

    ---

    [Keywords](corpus/keyness.md) against a reference corpus or the frequency dictionary, [collocations](corpus/collocations.md), the [dispersion](corpus/dispersion.md) of a word over the parts of a text, a [KWIC concordance](corpus/kwic.md), authorship by [stylometry](corpus/stylometry.md) (Burrows's Delta, Zeta, the Mendenhall curve, the function words) and the [comparison of corpora](corpus/compare.md) over 132 features of a text

    [:octicons-arrow-right-24: Corpus measures](corpus/keyness.md)

-   :material-database:{ .lg .middle } __Datasets__

    ---

    A [corpus of Spanish-language literature](datasets/spanishliterature.md) in the public domain (150 works by 33 authors in four genres), a [collection of sonnets](datasets/spanishsonnets.md) of the 15th-20th centuries with the metrical pattern and the rhyme of every line and a [frequency dictionary](datasets/freqdict.md) of 83,785 lemmas by Google Books Ngram

    [:octicons-arrow-right-24: Datasets](datasets/spanishliterature.md)

-   :material-chart-scatter-plot:{ .lg .middle } __Visualization__

    ---

    [Zipf's law](visualizers/zipf.md), [literature fingerprinting](visualizers/fingerprinting.md), [word tree](visualizers/word_tree.md), [corpus](visualizers/corpus.md) and [stylometric](visualizers/stylometry.md) plots, [vocabulary growth and frequency spectrum](visualizers/vocabulary.md), [sentence lengths](visualizers/sentences.md) and the [highlighting of a text](visualizers/highlight.md) by the fragments the statistics count

    [:octicons-arrow-right-24: Visualizers](visualizers/zipf.md)

-   :material-pipe:{ .lg .middle } __Components__

    ---

    Components of a spaCy pipeline, so that a text is annotated and measured in one pass and the statistics travel with the `Doc`

    [:octicons-arrow-right-24: spaCy components](components.md)

-   :material-alert-circle-outline:{ .lg .middle } __Exceptions__

    ---

    Errors of one hierarchy whose classes are also built-in Python exceptions

    [:octicons-arrow-right-24: Exceptions and logging](exceptions.md)

</div>

## Installation

Requires Python 3.11 or newer.

``` bash
pip install pyests
```

The distribution on PyPI is `pyests`, the package it installs is `ests`. The dependencies, the spaCy model and the datasets are on the [Installation](installation.md) page.

## Quick start

=== "Code"

    ``` python
    from ests import BasicStats, DiversityStats, ReadabilityStats

    text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

    BasicStats(text).get_stats()
    ReadabilityStats(text).flesch_reading_easy
    DiversityStats(text).ttr
    ```

=== "Result"

    ```
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
     'c_punctuations': {'comma': 1,
                        'period': 0,
                        'question': 0,
                        'exclamation': 0,
                        'ellipsis': 0,
                        'colon': 1,
                        'semicolon': 0,
                        'dash': 0,
                        'hyphen': 0,
                        'angle_quotes': 0,
                        'straight_quotes': 0,
                        'parentheses': 0,
                        'other': 0}}
    53.545000000000016
    0.8
    ```

Any statistic can be printed in a readable form:

=== "Code"

    ``` python
    BasicStats(text).print_stats()
    ```

=== "Result"

    ```
         Statistic     |  Value
    ------------------------------
    Sentences          |    1
    Words              |    10
    Unique words       |    8
    Long words         |    5
    Complex words      |    5
    Simple words       |    5
    Monosyllabic words |    4
    Polysyllabic words |    6
    Characters         |    71
    Letters            |    60
    Spaces             |    9
    Syllables          |    23
    Punctuation marks  |    2
    ```

A walkthrough of one short story with every tool of the library is in the notebook [examples/01_text_walkthrough.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb), which opens in [Colab](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb); the notebooks on prose authors, sonnets and corpus measures are on the [examples](examples.md) page.

??? note "Project structure"

    *   **demo** - the demo on Hugging Face Spaces (Gradio)
    *   **docs** - project documentation
    *   **ests**:
        *   basic_stats.py - basic text statistics
        *   cohesion_stats.py - cohesion statistics
        *   components.py - spaCy components
        *   constants.py - constants of the Spanish language and of the metrics
        *   diversity_stats.py - lexical diversity metrics
        *   exceptions.py - library exceptions
        *   extractors.py - extractors of sentences, words and character N-grams with the Spanish tokenizers
        *   lexical_stats.py - lexical sophistication statistics
        *   morph_stats.py - morphological statistics
        *   phon_stats.py - phonostatistics
        *   readability_stats.py - readability metrics
        *   style_stats.py - style metrics
        *   syllables.py - syllabification and stress
        *   syntax_stats.py - syntactic statistics
        *   utils.py - helper tools
        *   verse_stats.py - verse statistics
        *   **corpus** - corpus measures:
            *   collocations.py - collocations and association measures
            *   compare.py - comparison of corpora by the features of a text
            *   dispersion.py - word dispersion over the parts of a text
            *   keyness.py - keywords against a reference corpus or the frequency dictionary
            *   kwic.py - KWIC concordance
            *   stylometry.py - Burrows's Delta, Zeta, the function words and other stylometry measures
        *   **datasets** - datasets:
            *   freq_dict.py - the frequency dictionary by Google Books Ngram
            *   spanish_literature.py - the corpus of Spanish-language literature
            *   spanish_sonnets.py - the sonnets of the 15th-20th centuries
        *   **resources** - embedded lexical resources (the discourse markers, the 10,000 most frequent lemmas)
        *   **visualizers** - plots:
            *   corpus.py - lexical dispersion, keyness chart, collocation network
            *   fingerprinting.py - literature fingerprinting
            *   highlight.py - text highlighting
            *   sentences.py - sentence lengths
            *   stylometry.py - dendrogram, principal components, scaling, Mendenhall curves
            *   vocabulary.py - vocabulary growth and frequency spectrum
            *   word_tree.py - word tree
            *   zipf.py - Zipf's law
    *   **examples** - notebooks with examples
    *   **scripts** - scripts that build the archives of the datasets, fetch the anyTS pages of the documentation and check the outputs of the notebooks
    *   **tests** - tests mirroring the package structure
