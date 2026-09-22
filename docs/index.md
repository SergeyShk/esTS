# Spanish Texts Statistics (esTS)

**esTS** will compute for Spanish text what usually requires assembling several separate tools: basic counts, readability formulas, lexical diversity and sophistication, morphological, syntactic and cohesion statistics, style markers, phonostatistics, metre and rhyme, corpus measures and stylometry - by published formulas adapted to Spanish, with deterministic results and no neural networks inside.

It is the Spanish sibling of [ruTS](https://github.com/SergeyShk/ruTS), the Russian text statistics library, and follows its structure and naming: every statistic is available as a class with `get_stats()` and as a [spaCy](https://github.com/explosion/spaCy) pipeline component.

!!! warning "Status"
    The project is at the scaffolding stage: the repository, tooling, CI and documentation skeleton are in place, the modules are not written yet. The first release (0.1) is planned to cover text extraction, syllabification and stress, basic statistics, readability with presets and lexical diversity.

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
