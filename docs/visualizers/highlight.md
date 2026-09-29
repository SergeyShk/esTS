# Text highlighting

!!! info ""
    **ests.visualizers.highlight()**, **ests.visualizers.HighlightedText**, **ests.visualizers.Highlight**

## Description

--8<-- "visualizers/highlight.md:HighlightedText"

The function `highlight` returns a `HighlightedText` object of esTS, which extends the `HighlightedText` of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/highlight/) core with the layers of the library, their search and their parameters, and the prefix `ests` of the CSS classes.

Layers of the highlighting:

| Group | Layer | What it marks | Statistic |
| :---- | :---: | :-----------: | :-------: |
| Readability | `long_sents` | Sentences of `long_sent_word_factor` words or more | [BasicStats](../stats/basic_stats.md) |
| | `complex_words` | Words of `complex_syl_factor` syllables or more | [BasicStats](../stats/basic_stats.md) |
| | `rare_words` | Words with a lemma beyond the embedded top 10000; numbers, words with a hyphen or a digit and stopwords are not highlighted | [LexicalStats](../stats/lexical_stats.md) |
| Syntax | `passive` | Passive verb forms with their auxiliary `ser` or their `se`; the note tells the two apart and marks the passive with `ser` without an agent | [SyntaxStats](../stats/syntax_stats.md) |
| | `participle_clauses` | Participial clauses | [SyntaxStats](../stats/syntax_stats.md) |
| | `gerund_clauses` | Gerund clauses | [SyntaxStats](../stats/syntax_stats.md) |
| | `de_chains` | Chains of complements with `de` with their head | [SyntaxStats](../stats/syntax_stats.md) |
| | `split_predicates` | Split predicates from the verb to the noun | [SyntaxStats](../stats/syntax_stats.md) |
| Officialese | `verbal_nouns` | Nouns derived from a verb | [StyleStats](../stats/style_stats.md) |
| | `compound_prepositions` | Compound prepositions of `COMPOUND_PREPOSITIONS` | [StyleStats](../stats/style_stats.md) |
| | `cliches` | Clichés of `OFFICIALESE_CLICHES` or of the parameter `cliches` | [StyleStats](../stats/style_stats.md) |
| Style | `stopwords` | Stopwords of `STOPWORDS` or of the parameter `stopwords`, the water of the text | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Parenthetical expressions | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Discourse markers, the class and the kind in the note | [CohesionStats](../stats/cohesion_stats.md) |
| Phonics | `alliteration` | Repetitions of a consonant sound in neighbouring words, unlikely by the frequencies of the Spanish sounds; the note gives the sound and the letters that write it | [PhonStats](../stats/phon_stats.md) |

The groups are defined in `ests.constants.HIGHLIGHT_LAYER_GROUPS`, the annotations of a `Doc` a layer needs in `HIGHLIGHT_LAYER_ANNOTATIONS` and the styles of the layers in `HIGHLIGHT_LAYER_STYLES`. The layers of the group "Syntax" need a `Doc` with a parse and a lemmatizer (the models `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg`), as [SyntaxStats](../stats/syntax_stats.md) does; `verbal_nouns` needs a `Doc` with the parts of speech and the lemmas. A `Doc` without the sentence boundaries (a blank pipeline, a pipeline without the parser) is split by the rules of [SentsExtractor](../extractors/sentences.md). The layers of `HIGHLIGHT_DEFAULT_LAYERS` the source allows are on by default - long sentences, complex words, passive, chains of `de`, split predicates, clichés; `layers="all"` turns on every layer allowed. The layers overlap (a compound preposition is made of stopwords), so pick the ones you need.

A sentence is long from 30 words, the bound of the Spanish-language guides to plain language (the [Comunidad de Madrid](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) and the [Gobierno de la Ciudad de Buenos Aires](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf)), and a word is complex from four syllables; `complex_syl_factor=3`, the bound of `BasicStats`, shows the words of `n_complex_words`.

!!! note "Note"
    An alliteration is looked for inside a sentence as a run of two neighbouring words or more with the same consonant sound in their stems. The sounds are the ones of the [transcription](../stats/phon_stats_funcs.md#transcribe), so `casa` and `queso` repeat k; the stem is the common start of the transcriptions of the word form and of its lemma (`cantaban` - k a n t a), which leaves out the endings that repeat by agreement (`las casas blancas`). The probability of a run under an independent spread of the sounds is the product over its words of the probability to meet the consonant among the sounds of the stem, $1 - (1 - f)^n$, where $f$ is the frequency of the sound in the [corpus of literature](../datasets/spanishliterature.md) and $n$ the number of the sounds of the stem; a run is highlighted when the probability is below `alliteration_threshold`. A repetition of a rare sound shows in two or three words (`deje la abeja`), while the `s` of `los suspiros se escapan` is too frequent to count in two words. Words shorter than three letters (`de`, `la`, `el`) and stopwords (`que`, `los`, `con`) neither break nor continue a run. The alliteration index of [PhonStats](../stats/phon_stats.md) measures how the repetitions cluster over the whole text; the highlighting shows where they are.

## Parameters

--8<-- "visualizers/highlight.md:HighlightedText-parameters"

The parameters of the layers of esTS:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `long_sent_word_factor` | int | `30` | Minimum number of words of a long sentence |
| `complex_syl_factor` | int | `4` | Minimum number of syllables of a complex word |
| `stopwords` | list[str]/set[str] | `None` | List or set of stopwords; if not given, `STOPWORDS` and the one-word parenthetical expressions |
| `cliches` | list[str]/set[str] | `None` | List or set of clichés; if not given, `OFFICIALESE_CLICHES` |
| `alliteration_threshold` | float | `0.001` | Probability of a repetition of a consonant under an independent spread of the sounds, below which the repetition is alliteration |

A threshold that is not an integer of at least one or a probability outside (0, 1] raises `ParameterError`, stopwords or clichés that are not strings `SourceTypeError`.

## Attributes

--8<-- "visualizers/highlight.md:HighlightedText-attributes"

--8<-- "visualizers/highlight.md:Highlight"

The note of a fragment gives the number of words of the sentence, of syllables of the word, the length of the chain or the phrase of the list.

## Methods

### to_html

--8<-- "visualizers/highlight.md:HighlightedText-to_html"

### css

--8<-- "visualizers/highlight.md:HighlightedText-css"

## Usage example

!!! example "Example"

    _Code_:

    ``` python
    import spacy
    from ests.visualizers import highlight

    nlp = spacy.load("es_core_news_sm")
    text = (
        "El proyecto, elaborado durante el verano, fue aprobado por el consejo sin debate. "
        "El aumento de la eficiencia del uso de los recursos públicos se analizó, siguiendo "
        "las normas del reglamento. "
        "Los representantes de los ministerios regionales no consiguieron hacer una revisión "
        "conjunta de las cuestiones de financiación y de reparto de responsabilidades entre los "
        "organismos, puesto que cada uno de ellos defendía su propia interpretación de las "
        "disposiciones del acuerdo. "
        "En el marco de la reunión se procedió a la votación, y la decisión quedó aplazada "
        "hasta la próxima sesión."
    )

    # Highlight the text with the default layers
    ht = highlight(nlp(text))
    ht.counts
    # {'long_sents': 1, 'complex_words': 16, 'passive': 2, 'de_chains': 3,
    #  'split_predicates': 2, 'cliches': 1}

    ht.highlights[:2]
    # (Highlight(start=13, end=22, layer='complex_words', note='complex word, 5 syllables'),
    #  Highlight(start=42, end=54, layer='passive', note='passive with ser'))

    # Every layer
    highlight(nlp(text), layers="all").counts
    # {'long_sents': 1, 'complex_words': 16, 'rare_words': 0, 'passive': 2,
    #  'participle_clauses': 2, 'gerund_clauses': 1, 'de_chains': 3, 'split_predicates': 2,
    #  'verbal_nouns': 9, 'compound_prepositions': 1, 'cliches': 1, 'stopwords': 48,
    #  'parentheticals': 0, 'connectors': 3, 'alliteration': 0}

    # Show in Jupyter or save the markup
    ht
    html = ht.to_html()
    ```

_Result_ (hover over a fragment to see its note):

<div class="ests-highlight"><style>.ests-highlight { line-height: 1.7; }
.ests-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ests-highlight-legend .ests-hl { padding: 0 0.3em; }
.ests-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ests-highlight-text { white-space: pre-wrap; }
.ests-highlight .ests-hl.ests-hl-long_sents, .ests-highlight .ests-hl.ests-hl-stopwords, .ests-highlight .ests-hl.ests-hl-complex_words, .ests-highlight .ests-hl.ests-hl-rare_words, .ests-highlight .ests-hl.ests-hl-passive, .ests-highlight .ests-hl.ests-hl-verbal_nouns, .ests-highlight .ests-hl.ests-hl-compound_prepositions, .ests-highlight .ests-hl.ests-hl-cliches, .ests-highlight .ests-hl.ests-hl-parentheticals { color: #1f2328; border-radius: 2px; }
.ests-hl-long_sents { background: #fef9c3; }
.ests-hl-stopwords { background: #bae6fd; }
.ests-hl-complex_words { background: #fed7aa; }
.ests-hl-rare_words { background: #e5e7eb; }
.ests-hl-passive { background: #fecaca; }
.ests-hl-verbal_nouns { background: #e9d5ff; }
.ests-hl-compound_prepositions { background: #a7f3d0; }
.ests-hl-cliches { background: #fbcfe8; }
.ests-hl-parentheticals { background: #d9f99d; }
.ests-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ests-hl-gerund_clauses { border-bottom: 2px solid #0d9488; }
.ests-hl-de_chains { border-bottom: 2px solid #b45309; }
.ests-hl-split_predicates { border-bottom: 2px solid #dc2626; }
.ests-hl-connectors { border-bottom: 2px dashed #2563eb; }
.ests-hl-alliteration { text-decoration-line: underline; text-decoration-style: dotted; text-decoration-color: #db2777; text-decoration-thickness: 2px; text-underline-offset: 3px; }
</style><div class="ests-highlight-legend"><span><span class="ests-hl ests-hl-long_sents">Long sentences</span><span class="ests-highlight-count">1</span></span><span><span class="ests-hl ests-hl-complex_words">Complex words</span><span class="ests-highlight-count">16</span></span><span><span class="ests-hl ests-hl-passive">Passive</span><span class="ests-highlight-count">2</span></span><span><span class="ests-hl ests-hl-de_chains">Chains of de</span><span class="ests-highlight-count">3</span></span><span><span class="ests-hl ests-hl-split_predicates">Split predicates</span><span class="ests-highlight-count">2</span></span><span><span class="ests-hl ests-hl-cliches">Clichés</span><span class="ests-highlight-count">1</span></span></div><div class="ests-highlight-text">El proyecto, <span class="ests-hl ests-hl-complex_words" title="complex word, 5 syllables">elaborado</span> durante el verano, <span class="ests-hl ests-hl-passive" title="passive with ser">fue </span><span class="ests-hl ests-hl-complex_words ests-hl-passive" title="complex word, 4 syllables; passive with ser">aprobado</span> por el consejo sin debate. El <span class="ests-hl ests-hl-de_chains" title="chain of 3 complements with de">aumento de la </span><span class="ests-hl ests-hl-complex_words ests-hl-de_chains" title="complex word, 4 syllables; chain of 3 complements with de">eficiencia</span><span class="ests-hl ests-hl-de_chains" title="chain of 3 complements with de"> del uso de los recursos</span> públicos <span class="ests-hl ests-hl-passive" title="passive with se">se </span><span class="ests-hl ests-hl-complex_words ests-hl-passive" title="complex word, 4 syllables; passive with se">analizó</span>, siguiendo las normas del <span class="ests-hl ests-hl-complex_words" title="complex word, 4 syllables">reglamento</span>. <span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">Los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 5 syllables">representantes</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> de los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">ministerios</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">regionales</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> no </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">consiguieron</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> </span><span class="ests-hl ests-hl-long_sents ests-hl-split_predicates" title="long sentence, 40 words; split predicate: hacer revisión">hacer una </span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains ests-hl-split_predicates" title="long sentence, 40 words; chain of 2 complements with de; split predicate: hacer revisión">revisión</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> conjunta de las cuestiones de </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 4 syllables; chain of 2 complements with de">financiación</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> y de reparto de </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 7 syllables">responsabilidades</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> entre los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">organismos</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">, puesto que cada uno de ellos </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">defendía</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> su propia </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 5 syllables; chain of 2 complements with de">interpretación</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> de las </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 5 syllables; chain of 2 complements with de">disposiciones</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> del acuerdo</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">.</span> En el marco de la reunión se <span class="ests-hl ests-hl-split_predicates ests-hl-cliches" title="split predicate: proceder votación; cliché: «proceder a»">procedió a</span><span class="ests-hl ests-hl-split_predicates" title="split predicate: proceder votación"> la votación</span>, y la decisión quedó <span class="ests-hl ests-hl-complex_words" title="complex word, 4 syllables">aplazada</span> hasta la próxima sesión.</div></div>

A string without a model of spaCy allows every layer but the syntactic ones and `verbal_nouns`: long sentences, complex words and clichés by default, and the alliteration on request.

!!! example "Example"

    ``` python
    from ests.visualizers import highlight

    # Antonio Machado, Poesías completas (the corpus of literature)
    text = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(text, layers="alliteration").highlights
    # (Highlight(start=35, end=78, layer='alliteration', note='alliteration on /b/ (b, v)'),)
    ```

!!! example "Example"

    ``` python
    from ests.visualizers import highlight

    text = "Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad."
    highlight(text, layers=["compound_prepositions", "cliches"]).highlights
    # (Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»'),
    #  Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»'),
    #  Highlight(start=62, end=81, layer='cliches', note='cliché: «a la mayor brevedad»'))
    ```
