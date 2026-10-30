# Morphological statistics

``` {.python .signature}
MorphStats(source, nlp=None)
```

--8<-- "stats/morph_stats.md:MorphStats"

The class extends the `MorphStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/morph_stats/) core with the Spanish layer and the [markers of Spanish](#markers); the statistics are computed when the object is created. In esTS the data source is a text or a `Doc`: a text is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, and a `Doc` must carry the parts of speech, which come from a `morphologizer` (or a `tagger` with an `attribute_ruler`), and the lemmas, which come from a `lemmatizer`. Words are taken from the tokens, punctuation marks and symbols are dropped. A text longer than the `max_length` of the pipeline - a million characters by default - has to be split into parts, or `max_length` raised on a pipeline of your own passed in `nlp`. The `print_stats` and `print_markers` tables take the descriptions of `MORPHOLOGY_STATS_DESC` and `MORPHOLOGY_MARKERS_DESC` of `ests.constants`.

Besides, a pipeline in `nlp` that is not a spaCy `Language` raises `SourceTypeError`; a `Doc` without the lemmas (of a pipeline with the `lemmatizer` excluded), a string longer than the `max_length` of the pipeline or with a character that has no UTF-8 form raise `SourceError`; a string without `nlp` when the model `es_core_news_sm` is not installed raises `DatasetNotFoundError`.

=== "Code"

    ``` python
    from ests import MorphStats

    text = "Si tuviera tiempo, leería el libro que me recomendaste ayer"
    ms = MorphStats(text)
    ms.print_stats("pos", "mood")
    ```

=== "Result"

    ```
    -------------Part of speech-------------
    Verb                          |    3
    Noun                          |    2
    Pronoun                       |    2
    Subordinating conjunction     |    1
    Determiner                    |    1
    Adverb                        |    1

    ------------------Mood------------------
    Unknown                       |    7
    Subjunctive                   |    1
    Conditional                   |    1
    Indicative                    |    1
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `nlp` | `Language` | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Attributes

--8<-- "stats/morph_stats.md:MorphStats-attributes"

esTS also has the attribute `lemmas` (`tuple[str]`) - the lemmas of the words that the model gives.

=== "Code"

    ``` python
    ms.lemmas[:4]
    ms.tags[1]
    ```

=== "Result"

    ```
    ('si', 'tener', 'tiempo', 'leer')
    'Mood=Sub|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin'
    ```

## Statistics

Every statistic is an attribute of the object, a tuple of the values of a feature by word (`None` for a word the model gives no value of the feature), and `get_stats` gives the distributions of their values. The values are read from `token.pos_` and `token.morph` of the parse, that is, by context. The statistics are the part of speech and the fifteen features of `MORPHOLOGY_FEATURES`; the value `Unknown` in the printed tables means that the model gave the word no value of the feature. The other features the models annotate (`AdvType`, `Foreign`, `NumForm`, `Number[psor]`, `PrepCase`, `Typo`, `PunctSide`, `PunctType`) are not counted but stay in `tags`.

| Statistic | Feature | Values |
| :-------- | :------ | :----- |
| `pos` | Part of speech | `NOUN`, `PROPN`, `ADJ`, `ADV`, `VERB`, `AUX`, `PRON`, `DET`, `NUM`, `ADP`, `CCONJ`, `SCONJ`, `PART`, `INTJ`, `SYM`, `X` |
| `case` | Case | `Nom`, `Acc`, `Dat`, `Com` |
| `definite` | Definiteness | `Def`, `Ind` |
| `degree` | Degree | `Cmp`, `Sup`, `Abs` |
| `gender` | Gender | `Masc`, `Fem` |
| `mood` | Mood | `Ind`, `Sub`, `Imp`, `Cnd` |
| `num_type` | Numeral type | `Card`, `Ord`, `Frac` |
| `number` | Number | `Sing`, `Plur` |
| `person` | Person | `1`, `2`, `3` |
| `polarity` | Polarity | `Neg` |
| `polite` | Politeness | `Form` |
| `poss` | Possessive | `Yes` |
| `pron_type` | Pronoun type | `Art`, `Prs`, `Dem`, `Ind`, `Int`, `Rel`, `Neg`, `Tot`, `Exc` |
| `reflex` | Reflexive | `Yes` |
| `tense` | Tense | `Pres`, `Past`, `Imp`, `Fut` |
| `verb_form` | Verb form | `Fin`, `Inf`, `Part`, `Ger` |

A feature with several values keeps the form of CoNLL-U: `qué`, `quién`, `cuál` have `pron_type` equal to `Int,Rel`, and `usted` has `case` equal to `Acc,Nom`. `print_stats` names the values by `MORPHOLOGY_STATS_DESC` of `ests.constants`, and such a value by the names of its parts joined with a slash - "Interrogative / Relative", "Accusative / Nominative".

!!! warning "Warning"
    The statistics are as good as the annotation of the model. `es_core_news_sm` mis-analyses verbs with enclitic pronouns (`dámelo`, `cuéntamelo` come out as nouns with invented lemmas) and tags the imperatives of `tú` as indicative (`Abre la ventana` gets `Mood=Ind`), so `p_imperative` under-reports and `p_indicative` absorbs the orders: in the dialogue of the corpus of literature it finds about one imperative in ten. `es_core_news_lg` does little better (15%); the transformer model `es_dep_news_trf` passed in `nlp` finds 87% of them, and in drama `p_imperative` rises from 1.6% to 7.5% - at the cost of about 1 GB with PyTorch and five times the time on a CPU, and it needs the single line breaks of a hard-wrapped text joined first.

<div class="metric-card" markdown>

### Markers of Spanish { #markers }

`get_markers()` · `print_markers()`
{ .metric-meta }

The shares of the forms that mark the register of a Spanish text, each of its own base (`MORPHOLOGY_MARKERS_DESC`), so the markers of texts of different lengths can be compared directly; a marker whose base is empty - a text without verbs, without a copula, without adverbs - is `nan`. The subjunctive marks hypothesis and subordination, `estar` a state against the property of `ser`, and the adverbs in `-mente` a formal, written register.

| Marker | Share | Base |
| :----- | :---- | :--- |
| `p_indicative`, `p_subjunctive`, `p_conditional`, `p_imperative` | of the indicative, subjunctive, conditional and imperative mood | finite forms |
| `p_infinitive`, `p_gerund`, `p_participle` | of infinitives, gerunds and participles | verb forms |
| `p_ser` | of `ser` | copulas `ser` and `estar` |
| `p_mente_adverbs` | of the adverbs in `-mente` | adverbs |

The first four markers share the base of the finite forms and sum to one unless the model leaves a finite form without a mood. The next three share the base of all the verb forms of verbs and auxiliaries: a participle that the model annotates as an adjective (`la casa pintada`) is out of the base, the ones of the compound tenses and the passive (`he leído`, `fue escrito`) are in.

The base of `p_ser` is the copular uses alone, read from the parse: the auxiliaries of the passive and of the progressive (`fue escrito`, `es financiado`, `está cantando`) are left out, while `es alta`, `está cansada` and `lo importante es que vengas` count. For a `Doc` without a parse the marker is `nan`.

=== "Code"

    ``` python
    ms.get_markers()
    ```

=== "Result"

    ```
    {'p_indicative': 0.3333333333333333,
     'p_subjunctive': 0.3333333333333333,
     'p_conditional': 0.3333333333333333,
     'p_imperative': 0.0,
     'p_infinitive': 0.0,
     'p_gerund': 0.0,
     'p_participle': 0.0,
     'p_ser': nan,
     'p_mente_adverbs': 0.0}
    ```

</div>

## Methods

--8<-- "stats/morph_stats.md:MorphStats-get_stats"

--8<-- "stats/morph_stats.md:MorphStats-explain_text"

--8<-- "stats/morph_stats.md:MorphStats-print_stats"

The example at the top of the page prints two of the tables. `to_dataframe` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the morphological statistics have no scales, so `describe` gives `None`.

=== "Code"

    ``` python
    ms.get_stats("pos", "mood", "tense", filter_none=True)
    ms.explain_text("pos", "mood", "tense", filter_none=True)
    ```

=== "Result"

    ```
    {'pos': {'SCONJ': 1, 'VERB': 3, 'NOUN': 2, 'DET': 1, 'PRON': 2, 'ADV': 1},
     'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1},
     'tense': {'Imp': 1, 'Pres': 1}}
    (('Si', {'pos': 'SCONJ'}),
     ('tuviera', {'pos': 'VERB', 'mood': 'Sub', 'tense': 'Imp'}),
     ('tiempo', {'pos': 'NOUN'}),
     ('leería', {'pos': 'VERB', 'mood': 'Cnd'}),
     ('el', {'pos': 'DET'}),
     ('libro', {'pos': 'NOUN'}),
     ('que', {'pos': 'PRON'}),
     ('me', {'pos': 'PRON'}),
     ('recomendaste', {'pos': 'VERB', 'mood': 'Ind', 'tense': 'Pres'}),
     ('ayer', {'pos': 'ADV'}))
    ```

--8<-- "stats/morph_stats.md:MorphStats-markers"

In esTS the markers are the [markers of Spanish](#markers).

=== "Code"

    ``` python
    ms.print_markers()
    ```

=== "Result"

    ```
                   Marker               |  Value
    -----------------------------------------------
    Indicative among the finite forms   |   0.33
    Subjunctive among the finite forms  |   0.33
    Conditional among the finite forms  |   0.33
    Imperative among the finite forms   |   0.00
    Infinitive among the verb forms     |   0.00
    Gerund among the verb forms         |   0.00
    Participle among the verb forms     |   0.00
    ser among the copulas ser and estar |   nan
    Adverbs in -mente among the adverbs |   0.00
    ```

--8<-- "stats/morph_stats.md:MorphWord"

In esTS `MorphWord` is imported from `ests.morph_stats` too.
