# Spanish Texts Statistics (esTS)

**esTS** will compute for Spanish text what usually requires assembling several separate tools: basic counts, readability formulas, lexical diversity and sophistication, morphological, syntactic and cohesion statistics, style markers, phonostatistics, metre and rhyme, corpus measures and stylometry - by published formulas adapted to Spanish, with deterministic results and no neural networks inside.

It is the Spanish sibling of [ruTS](https://github.com/SergeyShk/ruTS), the Russian text statistics library, and follows its structure and naming: every statistic is available as a class with `get_stats()` and as a [spaCy](https://github.com/explosion/spaCy) pipeline component.

!!! warning "Status"
    The modules of the first release (0.1) are written: extraction of sentences, words and character N-grams, syllabification and stress, basic statistics, readability with presets and lexical diversity. The release itself is pending a QA pass and publication on PyPI.

## Planned scope

*   **Extraction** - sentences and words with Spanish punctuation (`¿ ¡`), clitics, lemmas via spaCy or `simplemma`.
*   **Syllables and stress** - rule-based syllabification (diphthongs, hiatus, consonant clusters) and stress derived from orthography.
*   **Readability** - Fernández Huerta, Szigriszt-Pazos with the INFLESZ scale, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, with presets.
*   **Lexical diversity** - TTR and its variants, MTLD, HD-D, Yule, Herdan, Brunet, entropy, Zipf and Heaps fits, windowed computation.
*   **Morphology, syntax and cohesion** - on Universal Dependencies features and relations from spaCy `es_core_news_*` models; Coh-Metrix style cohesion with a Spanish list of discourse markers.
*   **Corpus measures and stylometry** - keywords, collocations, dispersion, KWIC, Burrows's Delta, Zeta, corpus comparison.
*   **Style and sound** - SEO-style metrics, plain language (lenguaje claro) markers, phonostatistics, syllabic metre and rhyme (consonante and asonante).

## Links

*   Repository: [github.com/SergeyShk/esTS](https://github.com/SergeyShk/esTS)
*   The Russian sibling: [github.com/SergeyShk/ruTS](https://github.com/SergeyShk/ruTS)
