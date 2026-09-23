# Morphological statistics

!!! info ""
    **ests.morph_stats.MorphStats**

## Description

A module for computing the morphological statistics of a text. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

Parts of speech and grammatical features are given in the terms of [Universal Dependencies](https://universaldependencies.org/u/feat/), as the Spanish models of spaCy annotate them. A text is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`; a `Doc` is taken as it is and must carry the annotation of the parts of speech, so a `Doc` of `spacy.blank("es")` is not a valid source. Words are taken from the tokens, punctuation marks and symbols are dropped.

!!! note "Note"
    The statistics are computed when the `MorphStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `nlp` | Language | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of extracted words |
| `lemmas` | tuple[str] | Tuple of lemmas of the words |
| `tags` | tuple[str] | Tuple of feature strings in the CoNLL-U format |
| `pos` | tuple[str] | Tuple of the parts of speech |
| `case` | tuple[str] | Tuple of the values of case |
| `definite` | tuple[str] | Tuple of the values of definiteness |
| `degree` | tuple[str] | Tuple of the values of degree |
| `gender` | tuple[str] | Tuple of the values of gender |
| `mood` | tuple[str] | Tuple of the values of mood |
| `num_type` | tuple[str] | Tuple of the values of the numeral type |
| `number` | tuple[str] | Tuple of the values of number |
| `person` | tuple[str] | Tuple of the values of person |
| `polarity` | tuple[str] | Tuple of the values of polarity |
| `poss` | tuple[str] | Tuple of the values of the possessive |
| `pron_type` | tuple[str] | Tuple of the values of the pronoun type |
| `reflex` | tuple[str] | Tuple of the values of the reflexive |
| `tense` | tuple[str] | Tuple of the values of tense |
| `verb_form` | tuple[str] | Tuple of the values of the verb form |

Every attribute has the length of `words`, and a word that the model gives the feature no value for holds `None`. The names of the attributes are the names of the statistics accepted by the methods; `tags` and `lemmas` are not statistics.

!!! note "Note"
    A feature with several values keeps the form of CoNLL-U: the interrogative and relative `qué`, `quién`, `cuál`, which the models do not disambiguate, has `pron_type` equal to `Int,Rel`.

## Features { #features }

The Spanish models annotate the features of the table below; the value `Unknown` in the printed tables and `None` in the attributes mean that the model gave the word no value of the feature.

| Statistic | Feature | Values |
| :-------: | :-----: | :----: |
| `pos` | Part of speech | NOUN, PROPN, ADJ, ADV, VERB, AUX, PRON, DET, NUM, ADP, CCONJ, SCONJ, PART, INTJ, SYM, X |
| `case` | Case | Nom, Acc, Dat, Com |
| `definite` | Definiteness | Def, Ind |
| `degree` | Degree | Cmp, Sup, Abs |
| `gender` | Gender | Masc, Fem |
| `mood` | Mood | Ind, Sub, Imp, Cnd |
| `num_type` | Numeral type | Card, Ord, Frac |
| `number` | Number | Sing, Plur |
| `person` | Person | 1, 2, 3 |
| `polarity` | Polarity | Neg |
| `poss` | Possessive | Yes |
| `pron_type` | Pronoun type | Art, Prs, Dem, Ind, Int,Rel, Neg, Tot, Exc |
| `reflex` | Reflexive | Yes |
| `tense` | Tense | Pres, Past, Imp, Fut |
| `verb_form` | Verb form | Fin, Inf, Part, Ger |

!!! warning "Warning"
    The statistics are as good as the annotation of the model. `es_core_news_sm` mis-analyses verbs with enclitic pronouns: `dámelo`, `decírselo`, `vámonos`, `cuéntamelo` come out as nouns or proper nouns and get invented lemmas (`dámelir`, `siéntatir`). The imperative suffers most of all: the models carry the value `Mood=Imp` in their label set, but in practice they tag the imperatives of `tú` as indicative - `Habla más despacio` and `Abre la ventana` get `Mood=Ind` - so `p_imperative` under-reports and `p_indicative` absorbs the orders.

    Passing a bigger model in `nlp` does not fix that. Measured on the same examples, `es_core_news_md` leaves the enclitic lemmas and the moods exactly where `es_core_news_sm` leaves them, and agrees with it on every part of speech and every feature of modern prose. What it brings is the rare and the old vocabulary - in the opening of the *Quijote* it reads `rocín`, `salpicón`, `lentejas` and `carnero` as nouns, where the small model sees verbs and adjectives - for 54 MB against 16 MB and at the same speed.

## Methods

### get_stats

Returns a dictionary with the computed morphological statistics: for every statistic, how many words carry each of its values.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Names of the selected statistics, by default all of them |
| `filter_none` | bool | `False` | Filter out the empty values |

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import MorphStats

    # Prepare the data
    text = "Si tuviera tiempo, leería el libro que me recomendaste ayer"

    # Compute the statistics
    ms = MorphStats(text)
    ms.get_stats("pos", "mood", "tense", filter_none=True)
    ```

    _Result_:

    ``` bash
    {'pos': {'SCONJ': 1, 'VERB': 3, 'NOUN': 2, 'DET': 1, 'PRON': 2, 'ADV': 1},
    'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1},
    'tense': {'Imp': 1, 'Pres': 1}}
    ```

### get_markers

Returns a dictionary with the markers of Spanish computed from the features. Every marker is a share of its own base, so the markers of texts of different lengths can be compared directly:

| Marker | Description |
| :----: | :---------: |
| `p_indicative` | Indicative among the finite forms |
| `p_subjunctive` | Subjunctive among the finite forms |
| `p_conditional` | Conditional among the finite forms |
| `p_imperative` | Imperative among the finite forms |
| `p_infinitive` | Infinitive among the verb forms |
| `p_gerund` | Gerund among the verb forms |
| `p_participle` | Participle among the verb forms |
| `p_ser` | `ser` among the copulas `ser` and `estar` |
| `p_mente_adverbs` | Adverbs in `-mente` among the adverbs |

The first four markers share the base of the finite forms and sum to one; the next three share the base of all the verb forms. Verb forms are counted on verbs and auxiliaries, so that the participles that the model annotates as adjectives (`la casa pintada`) stay out of the base, while the ones of the compound tenses and the passive (`he leído`, `fue escrito`) stay in. A marker whose base is empty - a text without verbs, without a copula, without adverbs - is `nan`.

!!! note "Note"
    The subjunctive, the choice between `ser` and `estar` and the adverbs in `-mente` are the traits of Spanish that the readability formulas do not see: the subjunctive marks hypothesis and subordination, `estar` a state against the property of `ser`, and the adverbs in `-mente` a formal, written register.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Compute the markers
    ms.get_markers()
    ```

    _Result_:

    ``` bash
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

### explain_text

Returns a tuple of the words of the text with the values of the selected statistics.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Names of the selected statistics, by default all of them |
| `filter_none` | bool | `False` | Filter out the empty values |

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Parse the text
    ms.explain_text("pos", "mood", "tense", filter_none=True)
    ```

    _Result_:

    ``` bash
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

### print_stats

Prints a table of the values of every selected statistic, from the most frequent to the least frequent.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `args` | tuple[str] | `-` | Names of the selected statistics, by default all of them |
| `filter_none` | bool | `False` | Filter out the empty values |

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ms.print_stats("pos", "mood")
    ```

    _Result_:

    ``` bash
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

### print_markers

Prints a table with the computed markers of Spanish.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed markers
    ms.print_markers()
    ```

    _Result_:

    ``` bash
                         Marker                    |   Value
    -----------------------------------------------------------
    Indicative among the finite forms              |   0.33
    Subjunctive among the finite forms             |   0.33
    Conditional among the finite forms             |   0.33
    Imperative among the finite forms              |   0.00
    Infinitive among the verb forms                |   0.00
    Gerund among the verb forms                    |   0.00
    Participle among the verb forms                |   0.00
    ser among the copulas ser and estar            |    nan
    Adverbs in -mente among the adverbs            |   0.00
    ```
