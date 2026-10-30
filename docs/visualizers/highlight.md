# Text highlighting

``` {.python .signature}
HighlightedText(source, layers=None, long_sent_word_factor=30, complex_syl_factor=4, stopwords=None, cliches=None, alliteration_threshold=0.001)
```

--8<-- "visualizers/highlight.md:HighlightedText"

``` {.python .signature}
highlight(source, layers=None, long_sent_word_factor=30, complex_syl_factor=4, stopwords=None, cliches=None, alliteration_threshold=0.001)
```

The function `highlight` returns a `HighlightedText` object of esTS with the layers of the statistics of the library:

| Group | Layer | What it marks | Statistic |
| :---- | :---- | :------------ | :-------- |
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
| | `anaphoric_mismo` | The anaphoric `el mismo` with its article (`se archivó el mismo`, `la duración del mismo`) | - |
| Style | `stopwords` | Stopwords of `STOPWORDS` or of the parameter `stopwords`, the water of the text | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Parenthetical expressions | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Discourse markers, the class and the kind in the note | [CohesionStats](../stats/cohesion_stats.md) |
| Phonics | `alliteration` | Repetitions of a consonant sound in neighbouring words, unlikely by the frequencies of the Spanish sounds; the note gives the sound and the letters that write it | [PhonStats](../stats/phon_stats.md) |

The groups are defined in `ests.constants.HIGHLIGHT_LAYER_GROUPS`. The layers of the group "Syntax" need a `Doc` with a dependency parse and the lemmas (the models `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg`), as [SyntaxStats](../stats/syntax_stats.md) does; `verbal_nouns` needs a `Doc` with the parts of speech and the lemmas, and `anaphoric_mismo` one with the dependency parse, the parts of speech and the lemmas. The layers of `HIGHLIGHT_DEFAULT_LAYERS` the source allows are on by default - long sentences, complex words, passive, chains of `de`, split predicates, clichés; `layers="all"` turns on every layer allowed. The layers overlap (a compound preposition is made of stopwords), so pick the ones you need.

A sentence is long from 30 words, the bound of the Spanish-language guides to plain language (the [Comunidad de Madrid](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) and the [Gobierno de la Ciudad de Buenos Aires](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf)), and a word is complex from four syllables; `complex_syl_factor=3`, the bound of `BasicStats`, shows the words of `n_complex_words`.

!!! note "Alliteration"
    An alliteration is looked for inside a sentence as a run of two neighbouring words or more with the same consonant sound in their stems. The sounds are the ones of the [transcription](../stats/phon_stats.md#transcribe), so `casa` and `queso` repeat k; the stem is the common start of the transcriptions of the word form and of its lemma (`cantaban` - k a n t a), which leaves out the endings that repeat by agreement (`las casas blancas`). The probability of a run under an independent spread of the sounds is the product over its words of the probability to meet the consonant among the sounds of the stem, $1 - (1 - f)^n$, where $f$ is the frequency of the sound in the [corpus of literature](../datasets/spanishliterature.md) and $n$ the number of the sounds of the stem; a run is highlighted when the probability is below `alliteration_threshold`. A repetition of a rare sound shows in two or three words (`deje la abeja`), while the `s` of `los suspiros se escapan` is too frequent to count in two words. Words shorter than three letters (`de`, `la`, `el`), stopwords (`que`, `los`, `con`) and words without vowels neither break nor continue a run. The alliteration index of [PhonStats](../stats/phon_stats.md) measures how the repetitions cluster over the whole text; the highlighting shows where they are.

The class extends the `HighlightedText` of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/highlight/) core with the hooks of Spanish from `ests.constants`: the layers with their names in the legend are `HIGHLIGHT_LAYERS_DESC`, the layers on by default `HIGHLIGHT_DEFAULT_LAYERS`, the annotations of a `Doc` a layer needs `HIGHLIGHT_LAYER_ANNOTATIONS` and the styles of the layers `HIGHLIGHT_LAYER_STYLES`; the prefix of the CSS classes is `ests`. The words of a string are those of [`WordsExtractor`](../extractors/words.md), without the punctuation, and its sentences those of [`SentsExtractor`](../extractors/sentences.md); a `Doc` without the sentence boundaries (a blank pipeline, a pipeline without the parser) is split into sentences by the rules of `SentsExtractor` too. A string with a character without a UTF-8 form raises `SourceError` from the Spanish tokenizer. The fragments of every layer are found by the [finders of esTS](#finders).

=== "Code"

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
    ht = highlight(nlp(text))
    ht.counts
    ht.highlights[:2]
    highlight(nlp(text), layers="all").counts
    ```

=== "Result"

    ```
    {'long_sents': 1,
     'complex_words': 16,
     'passive': 2,
     'de_chains': 3,
     'split_predicates': 2,
     'cliches': 1}
    (Highlight(start=13, end=22, layer='complex_words', note='complex word, 5 syllables'),
     Highlight(start=42, end=54, layer='passive', note='passive with ser'))
    {'long_sents': 1,
     'complex_words': 16,
     'rare_words': 0,
     'passive': 2,
     'participle_clauses': 2,
     'gerund_clauses': 1,
     'de_chains': 3,
     'split_predicates': 2,
     'verbal_nouns': 9,
     'compound_prepositions': 1,
     'cliches': 1,
     'anaphoric_mismo': 0,
     'stopwords': 48,
     'parentheticals': 0,
     'connectors': 3,
     'alliteration': 0}
    ```

In Jupyter the object `ht` displays like this (hover over a fragment to see its note):

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

=== "Code"

    ``` python
    from ests.visualizers import highlight

    # Antonio Machado, Poesías completas (the corpus of literature)
    poem = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(poem, layers="alliteration").highlights
    text = "Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad."
    highlight(text, layers=["compound_prepositions", "cliches"]).highlights
    ```

=== "Result"

    ```
    (Highlight(start=35, end=78, layer='alliteration', note='alliteration on /b/ (b, v)'),)
    (Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»'),
     Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»'),
     Highlight(start=62, end=81, layer='cliches', note='cliché: «a la mayor brevedad»'))
    ```

## Parameters

--8<-- "visualizers/highlight.md:HighlightedText-parameters"

The parameters of the layers of esTS:

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `long_sent_word_factor` | `int` | `30` | Minimum number of words of a long sentence |
| `complex_syl_factor` | `int` | `4` | Minimum number of syllables of a complex word |
| `stopwords` | `list[str]` / `set[str]` | `None` | List or set of stopwords; if not given, `STOPWORDS` and the one-word parenthetical expressions |
| `cliches` | `list[str]` / `set[str]` | `None` | List or set of clichés; if not given, `OFFICIALESE_CLICHES` |
| `alliteration_threshold` | `float` | `0.001` | Probability of a repetition of a consonant under an independent spread of the sounds, below which the repetition is alliteration |

A number of words or syllables that is not an integer of at least one or a threshold outside (0, 1] raises `ParameterError`, stopwords or clichés that are not a list or a set of strings `SourceTypeError`.

## Attributes

--8<-- "visualizers/highlight.md:HighlightedText-attributes"

--8<-- "visualizers/highlight.md:Highlight"

The notes of esTS are in English: they give the number of words of the sentence or of the clause, of syllables of the word, the length of the chain, the phrase of the list, the class and the kind of the connector, the sound of the alliteration and its letters.

## Methods

--8<-- "visualizers/highlight.md:HighlightedText-to_html"

--8<-- "visualizers/highlight.md:HighlightedText-css"

=== "Code"

    ``` python
    from ests.visualizers import highlight

    poem = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(poem, layers="alliteration").to_html(legend=False, css=False)
    ```

=== "Result"

    ```
    '<div class="ests-highlight"><div class="ests-highlight-text">El cierzo corre por el campo yerto <span class="ests-hl ests-hl-alliteration" title="alliteration on /b/ (b, v)">alborotando en blancos torbellinos la nieve</span> silenciosa.</div></div>'
    ```

## Helpers of the layers

The words and the sentences the finders of the layers take; the helpers are in `ests.visualizers.highlight`.

--8<-- "visualizers/highlight.md:Word"

--8<-- "visualizers/highlight.md:Sent"

--8<-- "visualizers/highlight.md:group_words_by_sents"

## Finders of the layers { #finders }

The fragments of every layer are found by a function of `ests.visualizers.highlight` that returns a list of `Highlight`: from the words and the sentences of the text, or from the `Doc` for the syntactic layers (`SYNTAX_FINDERS` gives them by layer). All but the passive, the participial and gerund clauses, the chains of `de` and the anaphoric `el mismo` are the [finders of the core](https://sergeyshk.github.io/anyTS/visualizers/highlight/#finders) with the hooks of Spanish.

### Long sentences and complex words { #long-sents }

``` {.python .signature}
find_long_sents(sents, long_sent_word_factor)
```

The layer `long_sents`: the sentences of `long_sent_word_factor` words or more, the note with their number of words.

``` {.python .signature}
find_complex_words(words, complex_syl_factor)
```

The layer `complex_words`: the words of `complex_syl_factor` syllables or more by [`count_syllables`](../syllables.md#count_syllables), the note with their number of syllables.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `sents` | `list[Sent]` | - | Sentences with their positions and numbers of words |
| `long_sent_word_factor` | `int` | - | Minimum number of words of a long sentence |
| `words` | `list[Word]` | - | Words with their positions |
| `complex_syl_factor` | `int` | - | Minimum number of syllables of a complex word |

Raises:

- `ParameterError` - a number of words or syllables that is not an integer of at least one.

=== "Code"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Sent, Word, find_complex_words, find_long_sents

    text = "El felinólogo examinó al gato. Lo devolvieron."
    words = [Word(*word) for word in iter_text_words(text)]
    find_long_sents([Sent(0, 30, 5), Sent(31, 46, 2)], 5)
    find_complex_words(words, 4)
    ```

=== "Result"

    ```
    [Highlight(start=0, end=30, layer='long_sents', note='long sentence, 5 words')]
    [Highlight(start=3, end=13, layer='complex_words', note='complex word, 5 syllables'),
     Highlight(start=14, end=21, layer='complex_words', note='complex word, 4 syllables'),
     Highlight(start=34, end=45, layer='complex_words', note='complex word, 4 syllables')]
    ```

### Single words { #single-words }

``` {.python .signature}
find_rare_words(words)
```

The layer `rare_words`: the words whose key ([`lemma_key`](../datasets/freqdict.md#lemma_key)) is beyond the 10,000 most frequent lemmas ([`get_rank`](../stats/lexical_stats.md#bands)), as `p_beyond_top10000` of `LexicalStats` counts them; a word tagged `PROPN` keeps its form. Only the words of two Spanish letters or more that are not stopwords are looked at.

``` {.python .signature}
find_stopwords(words, stopwords=None)
```

The layer `stopwords`: the words of `stopwords` in any case or, without the list, the stopwords of [`is_stopword`](../stats/style_stats.md#academic_nausea).

``` {.python .signature}
find_verbal_nouns(words)
```

The layer `verbal_nouns`: the words tagged `NOUN` whose lemma is derived from a verb, as for the [verbal nouns](../stats/style_stats.md#verbal_nouns) of `StyleStats`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Words with their positions; with their parts of speech and lemmas for `find_verbal_nouns` |
| `stopwords` | `list[str]` / `set[str]` | `None` | List or set of stopwords; `is_stopword` if not given |

Raises:

- `SourceTypeError` - stopwords that are not a list or a set of strings.

=== "Code"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Word, find_rare_words, find_stopwords

    text = "El felinólogo examinó minuciosamente al gato."
    words = [Word(*word) for word in iter_text_words(text)]
    find_rare_words(words)
    find_stopwords(words)
    ```

=== "Result"

    ```
    [Highlight(start=3, end=13, layer='rare_words', note='rare word: beyond the top 10000'),
     Highlight(start=22, end=36, layer='rare_words', note='rare word: beyond the top 10000')]
    [Highlight(start=0, end=2, layer='stopwords', note='stopword'),
     Highlight(start=37, end=39, layer='stopwords', note='stopword')]
    ```

### Phrases { #phrases }

``` {.python .signature}
find_phrase_highlights(words, phrases, layer, label)
```

The fragments of the phrases of a list, matched with their contractions and the forms of their verbs ([`expand_phrases`](../stats/style_stats.md#phrase_density)); the note gives the label and the phrase of the list (`cliché: «proceder a»`).

``` {.python .signature}
find_compound_prepositions(words)
```

The layer `compound_prepositions`: the phrases of `COMPOUND_PREPOSITIONS`.

``` {.python .signature}
find_cliches(words, cliches=None)
```

The layer `cliches`: the phrases of `cliches`, of `OFFICIALESE_CLICHES` if not given.

``` {.python .signature}
find_parentheticals(words)
```

The layer `parentheticals`: the phrases of `PARENTHETICALS`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Words with their positions |
| `phrases` | `list[str]` / `set[str]` | - | Phrases, words separated by spaces |
| `layer` | `str` | - | Layer of the highlighting |
| `label` | `str` | - | Label of the fragment in the note |
| `cliches` | `list[str]` / `set[str]` | `None` | List or set of clichés |

Raises:

- `SourceTypeError` - phrases or clichés that are not a list or a set of strings.

=== "Code"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Word, find_cliches, find_compound_prepositions

    text = "Se procedió a la revisión del expediente en el marco del plan."
    words = [Word(*word) for word in iter_text_words(text)]
    find_cliches(words)
    find_compound_prepositions(words)
    ```

=== "Result"

    ```
    [Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»')]
    [Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»')]
    ```

### Connectors { #connectors }

``` {.python .signature}
find_connector_highlights(words, sents, text=None, doc=None)
```

The layer `connectors`: the connectors of [`CohesionStats`](../stats/cohesion_stats.md#connectors) inside every sentence, found by its matcher [`SpanishConnectorMatcher`](../stats/cohesion_stats.md#ConnectorMatcher), a one-word connector checked by its part of speech when the words have it; the note gives the connector, its class and its kind. With the text, the rules of the matcher read no word across a punctuation mark between two words, so `así, que` is no connector; with the `Doc`, no connector starts at a `si` that opens no condition, as in `CohesionStats` ([`is_connector_blocked`](../stats/cohesion_stats.md#is_connector_blocked): `no sé si vendrá`). `HighlightedText` passes the text of its source and its `Doc`; in a string, which it does not parse, only the rules of the matcher drop a `si` (`como si fuera`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Words with their positions and parts of speech |
| `sents` | `list[Sent]` | - | Sentences with their positions |
| `text` | `str` | `None` | Text of the words, for the punctuation marks between them |
| `doc` | `Doc` | `None` | `Doc` of the words, for the rules by its tokens |

Raises:

- `SourceTypeError` - a text that is not a string.

=== "Code"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Sent, Word, find_connector_highlights

    text = "Sin embargo, el plan no se aprobó."
    words = [Word(*word) for word in iter_text_words(text)]
    find_connector_highlights(words, [Sent(0, len(text), len(words))], text)
    ```

=== "Result"

    ```
    [Highlight(start=0, end=11, layer='connectors', note='connector «sin embargo»: adversative, secondary')]
    ```

### Alliteration { #alliteration }

``` {.python .signature}
get_stem_sounds(word)
```

The sounds of the stem of a word form: the common start of the [transcriptions](../stats/phon_stats.md#transcribe) of the form and of its lemma (`cantaban` - k a n t a, `cogió` - k o x). When it is shorter than two sounds, as for the suppletive forms (`fue` - `ser`), the stem is the whole form.

``` {.python .signature}
calc_alliteration_runs(text, threshold=0.001)
```

The runs of [`calc_alliteration_runs`](https://sergeyshk.github.io/anyTS/visualizers/highlight/#calc_alliteration_runs) of the core over the stems of `get_stem_sounds` and the consonant sounds of `ALLITERATION_FREQUENCIES`, their frequencies in `SOUND_FREQUENCIES`; the words shorter than three letters, the stopwords and the words without vowels neither break nor continue a run. A run is a triple of the index of its first word, the index after its last word and its sound.

``` {.python .signature}
find_alliteration(words, threshold=0.001, sents=None)
```

The layer `alliteration`: the runs of `calc_alliteration_runs` inside every sentence, in the whole text without the sentences; the note gives the sound and the letters that write it (`alliteration on /b/ (b, v)`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word form in lower case |
| `text` | `list[str]` | - | List of words |
| `threshold` | `float` | `0.001` | Probability threshold (`ALLITERATION_THRESHOLD` of `anyts.constants`) |
| `words` | `list[Word]` | - | Words with their positions |
| `sents` | `list[Sent]` | `None` | Sentences with their positions |

Raises:

- `SourceTypeError` - a word that is not a string, words of `calc_alliteration_runs` that are not a list of strings;
- `ParameterError` - a threshold outside (0, 1].

=== "Code"

    ``` python
    from ests.visualizers.highlight import calc_alliteration_runs, get_stem_sounds

    get_stem_sounds("cantaban"), get_stem_sounds("fue")
    calc_alliteration_runs(["deje", "la", "abeja"])
    calc_alliteration_runs(["los", "suspiros", "se", "escapan"])
    ```

=== "Result"

    ```
    (('k', 'a', 'n', 't', 'a'), ('f', 'u', 'e'))
    [(0, 3, 'x')]
    []
    ```

### Syntactic layers { #syntax-layers }

``` {.python .signature}
find_passive(doc)
```

The layer `passive`: every passive form of [`is_passive`](../stats/syntax_stats.md#passive) with its auxiliary `ser` (`fue construida`) or its `se` (`se construyó`); the note tells the passive with `se` from the one with `ser` and marks a passive with `ser` without an agent (`is_agentless`).

``` {.python .signature}
find_participle_clauses(doc)
```

The layer `participle_clauses`: the subtree of every head of a [participial clause](../stats/syntax_stats.md#participle_clauses), the note with its number of words.

``` {.python .signature}
find_gerund_clauses(doc)
```

The layer `gerund_clauses`: the subtree of every head of a [gerund clause](../stats/syntax_stats.md#gerund_clauses), the note with its number of words.

``` {.python .signature}
find_de_chains(doc)
```

The layer `de_chains`: the [chains of `de`](../stats/syntax_stats.md#de_chains) of two complements or more, a fragment from the head to the last complement (`el aumento de la eficiencia del uso de los recursos`), the note with the length of the chain.

``` {.python .signature}
find_split_predicate_highlights(doc)
```

The layer `split_predicates`: the pairs of a light verb and a noun of [`find_split_predicates`](../stats/syntax_stats.md#constructions), a fragment from the first word of the pair to the last (`hacer una revisión`), the note with their lemmas.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `doc` | `Doc` | - | Doc object with a dependency parse and the lemmas |

=== "Code"

    ``` python
    from ests.utils import get_nlp
    from ests.visualizers.highlight import (
        find_de_chains,
        find_gerund_clauses,
        find_participle_clauses,
        find_passive,
        find_split_predicate_highlights,
    )

    doc = get_nlp()(
        "El informe, redactado por el comité, fue aprobado tras hacer una revisión, "
        "siguiendo las normas del uso de los recursos."
    )
    find_passive(doc)
    find_participle_clauses(doc)
    find_gerund_clauses(doc)
    find_de_chains(doc)
    find_split_predicate_highlights(doc)
    ```

=== "Result"

    ```
    [Highlight(start=37, end=49, layer='passive', note='passive with ser, no agent')]
    [Highlight(start=12, end=35, layer='participle_clauses', note='participial clause, 4 words')]
    [Highlight(start=75, end=119, layer='gerund_clauses', note='gerund clause, 8 words')]
    [Highlight(start=89, end=119, layer='de_chains', note='chain of 2 complements with de')]
    [Highlight(start=55, end=73, layer='split_predicates', note='split predicate: hacer revisión')]
    ```

### Anaphoric el mismo { #anaphoric-mismo }

``` {.python .signature}
is_anaphoric_mismo(token)
```

Checks whether a word is an anaphoric `el mismo`: a form of `mismo` that heads a noun phrase of its own with its article (`el`, `la`, `los`, `las`, `del`, `al`) and no other dependent, as an argument of a verb or a noun (`se archivó el mismo`, `la duración del mismo`, `dentro de la misma`). The [Diccionario panhispánico de dudas](https://www.rae.es/dpd/mismo) takes this use of the administrative and the journalistic style for unnecessary and suggests a demonstrative, a possessive or a personal pronoun instead (`su duración`, `dentro de ella`). The identity is no anaphora: `el mismo día`, `es el mismo`, `lo mismo`, `él mismo`, a form after `ser`, `estar`, `parecer`, `permanecer` or `resultar` (`no parecía la misma`, `la situación permanece la misma`), right before `que` (`el mismo que el año pasado`, while `del mismo, que...` is anaphoric) and before a conjunction and an adjective or a determiner other than an article or a possessive, which share its noun (`de la misma o superior categoría`, `a la misma u otra sede`). The models attach some anaphoric forms to their article (`en la misma hay oficinas`): such a form counts when no noun, adjective, numeral or pronoun follows it in its sentence. Whitespace and punctuation are no dependents of the form, so a line break after it changes nothing.

``` {.python .signature}
find_anaphoric_mismo(doc)
```

The layer `anaphoric_mismo`: every form of `is_anaphoric_mismo` with its article (`la misma`, `del mismo`), the two words in the note.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |
| `doc` | `Doc` | - | Doc object with a dependency parse, the parts of speech and the lemmas |

=== "Code"

    ``` python
    from ests.utils import get_nlp
    from ests.visualizers.highlight import find_anaphoric_mismo, is_anaphoric_mismo

    doc = get_nlp()("Se recibió la solicitud el mismo día, y se procedió al estudio de la misma.")
    [token.text for token in doc if is_anaphoric_mismo(token)]
    find_anaphoric_mismo(doc)
    ```

=== "Result"

    ```
    ['misma']
    [Highlight(start=66, end=74, layer='anaphoric_mismo', note='anaphoric la misma')]
    ```
