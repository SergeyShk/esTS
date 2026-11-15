# Morphological statistics

``` {.python .signature}
MorphStats(source)
```

--8<-- "stats/morph_stats.md:MorphStats"

The class extends the `MorphStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/morph_stats/) core with the Spanish layer and the [markers of Spanish](#markers); the statistics are computed when the object is created. In esTS the data source is a text, a `Doc` or a `Document`: a text gets the analyses of [esMorph](https://github.com/SergeyShk/esMorph) in the context of its sentences, without spaCy, and a `Doc` must carry the parts of speech and the lemmas: the pipeline of [`load_pipeline`](../components.md#load_pipeline) gives it the same analyses of esMorph, a pipeline of one's own those of a `morphologizer` (or a `tagger` with an `attribute_ruler`) and a `lemmatizer`. The words are those of the document with a letter or a digit: in a text the words of a contraction and of a verb with clitics are words of their own (`del` - `de` + `el`, `dámelo` - `da` + `me` + `lo`), while a `Doc` keeps the token whole with the analysis of its first word. The `print_stats` and `print_markers` tables take the descriptions of `MORPHOLOGY_STATS_DESC` and `MORPHOLOGY_MARKERS_DESC` of `ests.constants`.

Besides, in esTS a source that is neither a string, a `Doc` nor a `Document` raises `SourceTypeError`, and a `Doc` without the lemmas (of a pipeline of one's own without a `lemmatizer`) raises `SourceError`.

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
| `source` | `str` / `Doc` / `Document` | - | Data source |

## Attributes

--8<-- "stats/morph_stats.md:MorphStats-attributes"

In esTS the statistics are `case`, ..., `verb_form` of the [table below](#statistics); `animacy`, `aspect` and `voice` of the core are not among them. esTS also has the attribute `lemmas` (`tuple[str]`) - the lemmas of the words, of esMorph for a text and of the pipeline for a `Doc`.

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

## Statistics { #statistics }

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

A feature with several values keeps the form of CoNLL-U: `usted` has `case` equal to `Acc,Nom`, and in a `Doc` of `es_core_news_sm` `qué`, `quién`, `cuál` have `pron_type` equal to `Int,Rel`. `print_stats` names the values by `MORPHOLOGY_STATS_DESC` of `ests.constants`, and such a value by the names of its parts joined with a slash - "Interrogative / Relative", "Accusative / Nominative".

!!! warning "Warning"
    The statistics are as good as the annotation. esMorph analyzes a verb with clitics as the verb (`dámelo` - the imperative of `dar`), but, like the models, reads the imperative of `tú` that has the form of the indicative (`Abre la ventana`) as indicative: on the test set of AnCora (UD 2.18) it finds 29% of the imperatives, against 11% of `es_core_news_sm`. In a `Doc` of a pipeline of one's own, `es_core_news_sm` mis-analyses verbs with enclitic pronouns (`dámelo`, `cuéntamelo` come out as nouns with invented lemmas) and tags the imperatives of `tú` as indicative (`Abre la ventana` gets `Mood=Ind`), so `p_imperative` under-reports and `p_indicative` absorbs the orders: in the dialogue of the corpus of literature it finds about one imperative in ten. `es_core_news_lg` does little better (15%); the transformer model `es_dep_news_trf`, which builds the `Doc`, finds 87% of them, and in drama `p_imperative` rises from 1.6% to 7.5% - at the cost of about 1 GB with PyTorch and five times the time on a CPU, and it needs the single line breaks of a hard-wrapped text joined first.

<div class="metric-card" markdown>

### Markers of Spanish { #markers }

`get_markers()` · `print_markers()`
{ .metric-meta }

The shares of the forms that mark the register of a Spanish text, each of its own base (`MORPHOLOGY_MARKERS_DESC`), so the markers of texts of different lengths can be compared directly; a marker whose base is empty - a text without verbs, without a copula, without adverbs - is `nan`. The subjunctive marks hypothesis and subordination, `estar` a state against the property of `ser`, and the adverbs in `-mente` a formal, written register.

| Marker | Share | Base |
| :----- | :---- | :--- |
| `p_indicative`, `p_subjunctive`, `p_conditional`, `p_imperative` | of the indicative, subjunctive, conditional and imperative mood | finite forms |
| `p_infinitive`, `p_gerund`, `p_participle` | of infinitives, gerunds and participles | verb forms |
| `p_enclitics`, `p_proclitics` | of the forms with enclitic pronouns and of those after proclitic ones | verb forms |
| `p_ser` | of `ser` | copulas `ser` and `estar` |
| `p_mente_adverbs` | of the adverbs in `-mente` | adverbs |

The first four markers share the base of the finite forms and sum to one unless the model leaves a finite form without a mood or gives it several (`Mood=Ind,Sub`, which counts in the share of each; `es_core_news_sm` gives none). The next three share the base of all the verb forms of verbs and auxiliaries: a participle that the model annotates as an adjective (`la casa pintada`) is out of the base, the ones of the compound tenses and the passive (`he leído`, `fue escrito`) are in.

The clitic pronouns (`ENCLITICS`) go after the infinitive, the gerund and the imperative (`dámelo`, `escribirle`, `diciéndole`) and before the other forms (`se lo dijo`, `me ha visto`), and the old literary language puts them after a finite form too (`pasábanse`, `díjole`), so `p_enclitics` measures that register and the orders of a dialogue. A form has enclitics when its token is, by the first analysis of esMorph as a verb, a verb with pronouns after it (`ests.morph_stats.has_enclitics`); the imperfect subjunctive in `-se` (`hablase`) is one word. A form comes after proclitics when the word before it is a clitic pronoun of a token of its own (`ests.morph_stats.has_proclitics`), so in a compound tense the pronouns count for the auxiliary (`se ha ido`). In the corpus of literature the medians of `p_enclitics` are 8.7% of the verb forms in prose, 8.0% in drama, 7.7% in journalism and 3.9% in verse, those of `p_proclitics` 18%, 19%, 14% and 12%.

The base of `p_ser` is the copular uses alone, read from the morphology: `ser` before a participle and `estar` before a gerund, with adverbs and pronouns between them, are the auxiliaries of the passive and of the progressive (`fue escrito`, `es financiado`, `está cantando`) and are left out, while `es alta`, `está cansada` and `lo importante es que vengas` count. The rule needs no parse, so a text and a `Doc` without a parser have the marker too; a participle that the tagger reads as an adjective (`fue muy bien recibido`) leaves its `ser` a copula.

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
     'p_enclitics': 0.0,
     'p_proclitics': 0.3333333333333333,
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
     'tense': {'Imp': 1, 'Past': 1}}
    (('Si', {'pos': 'SCONJ'}),
     ('tuviera', {'pos': 'VERB', 'mood': 'Sub', 'tense': 'Imp'}),
     ('tiempo', {'pos': 'NOUN'}),
     ('leería', {'pos': 'VERB', 'mood': 'Cnd'}),
     ('el', {'pos': 'DET'}),
     ('libro', {'pos': 'NOUN'}),
     ('que', {'pos': 'PRON'}),
     ('me', {'pos': 'PRON'}),
     ('recomendaste', {'pos': 'VERB', 'mood': 'Ind', 'tense': 'Past'}),
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
                       Marker                   |  Value
    -------------------------------------------------------
    Indicative among the finite forms           |   0.33
    Subjunctive among the finite forms          |   0.33
    Conditional among the finite forms          |   0.33
    Imperative among the finite forms           |   0.00
    Infinitive among the verb forms             |   0.00
    Gerund among the verb forms                 |   0.00
    Participle among the verb forms             |   0.00
    Forms with enclitics among the verb forms   |   0.00
    Forms after proclitics among the verb forms |   0.33
    ser among the copulas ser and estar         |   nan
    Adverbs in -mente among the adverbs         |   0.00
    ```

--8<-- "stats/morph_stats.md:MorphWord"

In esTS `MorphWord` is imported from `ests.morph_stats` too.
