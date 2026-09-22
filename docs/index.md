# Spanish Texts Statistics (esTS)

**esTS** computes for Spanish text what usually requires assembling several separate tools: basic counts, readability formulas, lexical diversity and, in the releases to come, morphological, syntactic and cohesion statistics, style markers, phonostatistics, metre and rhyme, corpus measures and stylometry - by published formulas adapted to Spanish, with deterministic results and no neural networks inside.

It is the Spanish sibling of [ruTS](https://github.com/SergeyShk/ruTS), the Russian text statistics library, and follows its structure and naming: every statistic is a class with `get_stats()`. Components for a [spaCy](https://github.com/explosion/spaCy) pipeline come with the morphology and syntax of 0.2.

!!! note "Status"
    0.1 is the first release. It covers text extraction, syllables and stress, basic statistics, readability and lexical diversity; morphology, syntax and cohesion on Universal Dependencies follow in 0.2.

## What it computes

Release 0.1:

*   [**Extraction**](extractors/sentences.md) - sentences with Spanish punctuation (`¿ ¡`, dialogue dashes, abbreviations), words with clitics, lemmas via `simplemma`, character N-grams.
*   [**Syllables and stress**](syllables.md) - rule-based syllabification (diphthongs, hiatus, consonant clusters) and stress derived from orthography.
*   [**Basic statistics**](stats/basic_stats.md) - sentences, words, letters, syllables and punctuation by type, with distributions and normalized shares.
*   [**Readability**](stats/readability_stats.md) - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, LIX and RIX, with presets, school stages and reading time.
*   [**Lexical diversity**](stats/diversity_stats.md) - TTR and its variants, MATTR, MSTTR, MTLD, HD-D, Yule, Herdan, Brunet, entropy, Zipf and Heaps fits, windowed computation.

Planned:

*   **Morphology, syntax and cohesion** (0.2) - on Universal Dependencies features and relations from spaCy `es_core_news_*` models; Coh-Metrix style cohesion with a Spanish list of discourse markers; pipeline components.
*   **Corpus measures and stylometry** (0.3) - keywords, collocations, dispersion, KWIC, Burrows's Delta, Zeta, corpus comparison.
*   **Style and sound** (0.4) - SEO-style metrics, plain language (lenguaje claro) markers, phonostatistics, syllabic metre and rhyme (consonante and asonante).

## Links

*   Repository: [github.com/SergeyShk/esTS](https://github.com/SergeyShk/esTS)
*   The Russian sibling: [github.com/SergeyShk/ruTS](https://github.com/SergeyShk/ruTS)
