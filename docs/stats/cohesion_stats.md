# Cohesion statistics

!!! info ""
    **ests.cohesion_stats.CohesionStats**

## Description

A module for computing the cohesion statistics of a text in the manner of [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and of its Spanish adaptation [Coh-Metrix-Esp](https://aclanthology.org/W16-4105/): the overlap of nouns, of arguments and of content words between sentences, givenness, temporal cohesion and the density of the discourse markers.

Sentences are compared by lemmas, and the features come from the annotation of [Universal Dependencies](https://universaldependencies.org/u/feat/), so the source has to be tagged: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, and a `Doc` must carry the parts of speech. Without sentence boundaries - a pipeline with a tagger but no parser - the sentences are taken from the text by [`SentsExtractor`](../extractors/sentences.md).

A text longer than the `max_length` of the pipeline - a million characters by default - raises `SourceError`: split it into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

!!! note "Note"
    The statistics are computed when the `CohesionStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `sents_extractor` | SentsExtractor | `None` | Sentence extraction tool, used for a Doc with no sentence boundaries |
| `connectors` | dict[str, tuple[str, str]] | `None` | Dictionary of the connectors - class and kind by connector; without it the dictionary of the library is used |
| `nlp` | Language | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Referential cohesion { #reference }

The overlap of Coh-Metrix: a pair of sentences is cohesive when they share the lemma of a noun (CRFNO), of an argument - a noun or a pronoun - (CRFAO) or of a content word (CRFSO). The binary measures give the share of such pairs among the adjacent sentences and among all the pairs of the text; the proportional ones (CRFCWO) give the mean Dice coefficient of the sets of lemmas, `2·|A ∩ B| / (|A| + |B|)`.

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `noun_overlap_adjacent` | float | Share of adjacent pairs of sentences sharing a noun |
| `noun_overlap_all` | float | Share of all pairs of sentences sharing a noun |
| `argument_overlap_adjacent` | float | Share of adjacent pairs sharing a noun or a pronoun |
| `argument_overlap_all` | float | Share of all pairs sharing a noun or a pronoun |
| `content_overlap_adjacent` | float | Share of adjacent pairs sharing a content word |
| `content_overlap_all` | float | Share of all pairs sharing a content word |
| `content_overlap_prop_adjacent` | float | Mean share of shared content words in adjacent pairs |
| `content_overlap_prop_all` | float | Mean share of shared content words in all pairs |
| `p_pronouns` | float | Share of pronouns among the words |
| `pronoun_noun_ratio` | float | Ratio of the number of pronouns to the number of nouns |
| `p_demonstratives` | float | Share of demonstratives among the words |
| `p_given` | float | Share of content words whose lemma was used before in the text |
| `tense_repetition` | float | Share of adjacent pairs with the same dominant tense |
| `mood_repetition` | float | Share of adjacent pairs with the same dominant mood |
| `temporal_cohesion` | float | Mean of the repetition of the tense and of the mood |

A noun is `NOUN` or `PROPN`, an argument is a noun or a `PRON`, and a content word is a `NOUN`, `PROPN`, `ADJ`, `VERB` or `ADV`. A pronoun is a `PRON` or a determiner that is not an article, so `el libro` holds none while `mi libro` and `este libro` do; a demonstrative carries `PronType=Dem`.

Temporal cohesion follows SMTEMP of Coh-Metrix: for every sentence the dominant value of the feature of its verbs is taken, and a pair of adjacent sentences counts as cohesive when the values are equal. Spanish has no aspect in Universal Dependencies, so the mood takes its place next to the tense - the shift from the indicative to the subjunctive is what breaks the temporal frame of a Spanish text. Pairs where one of the sentences has no verb with the feature are skipped, and a text shorter than two sentences leaves every measure of this section `nan`.

## Connectors { #connectors }

The discourse markers (*marcadores del discurso*) of the classification of Martín Zorraquino and Portolés, 255 of them in `ests/resources/connectors.tsv`, in seven classes and two kinds: primary - conjunctions, conjunctive locutions and adverbs (`porque`, `aunque`, `además`) - and secondary, the lexicalized phrases (`sin embargo`, `por lo tanto`, `es decir`). The density is given per 1000 words.

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `connectors` | float | Connectors per 1000 words |
| `connectors_causal` | float | Causal connectors (`porque`, `por lo tanto`, `así que`) |
| `connectors_adversative` | float | Adversative connectors (`pero`, `sin embargo`, `en cambio`) |
| `connectors_concessive` | float | Concessive connectors (`aunque`, `a pesar de`, `de todos modos`) |
| `connectors_temporal` | float | Temporal connectors (`cuando`, `a continuación`, `por último`) |
| `connectors_additive` | float | Additive connectors (`y`, `además`, `por otra parte`) |
| `connectors_conditional` | float | Conditional connectors (`si`, `a menos que`, `de lo contrario`) |
| `connectors_reformulative` | float | Reformulative connectors (`es decir`, `en resumen`, `por ejemplo`) |
| `connectors_primary` | float | Primary connectors per 1000 words |
| `connectors_secondary` | float | Secondary connectors per 1000 words |

The connectors are looked for by their word forms in lower case: at every position the longest one is taken, so `sin embargo` does not fall apart into `sin`, and the ones found do not overlap. A one-word connector counts only with a part of speech of `CONNECTOR_POS` - a conjunction, a particle, an adverb, an adposition, an interjection - so `el antes y el después` holds one connector, `y`, and not three. The occurrences are in the attribute `connector_spans` and their distribution in `c_connectors`.

Your own dictionary can be passed in `connectors`: a mapping from the connector to its class of `CONNECTOR_CLASSES` and its kind of `CONNECTOR_TYPES`, an unknown one raising `ParameterError`.

!!! warning "Warning"
    A Spanish marker is most often a phrase built of ordinary words, and those words are counted as words like any other: the noun `embargo` of `sin embargo` and the noun `ejemplo` of `por ejemplo` are nouns and content words of their sentence, and a text that repeats a marker gains a little overlap from it. Measured on the Spanish pages of this site the difference is below 0.002 for every overlap, but on a text built of markers it would be larger.

## Counts { #counts }

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[tuple[str, ...], ...] | Tuple of the words of every sentence |
| `lemmas` | tuple[tuple[str, ...], ...] | Tuple of the lemmas of every sentence |
| `n_sents` | int | Number of sentences containing words |
| `n_words` | int | Number of words |
| `n_nouns` | int | Number of nouns |
| `n_pronouns` | int | Number of pronouns |
| `n_demonstratives` | int | Number of demonstratives |
| `n_content_words` | int | Number of content words |
| `n_given` | int | Number of content words whose lemma was used before |
| `n_connectors` | int | Number of connectors |
| `connector_spans` | tuple[Connector] | Tuple of the occurrences of the connectors |
| `c_connectors` | dict[str, int] | Distribution of the occurrences by connector |

## Methods

### get_stats

Returns a dictionary with the computed cohesion statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import CohesionStats

    # Prepare the data
    text = (
        "El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve "
        "el problema. Es decir, la comisión aplazó la decisión. Por lo tanto, el "
        "problema sigue abierto."
    )

    # Compute the statistics
    cs = CohesionStats(text)
    cs.get_stats()
    ```

    _Result_:

    ``` bash
    {'noun_overlap_adjacent': 0.3333333333333333,
    'noun_overlap_all': 0.5,
    'argument_overlap_adjacent': 0.3333333333333333,
    'argument_overlap_all': 0.5,
    'content_overlap_adjacent': 0.3333333333333333,
    'content_overlap_all': 0.5,
    'content_overlap_prop_adjacent': 0.08333333333333333,
    'content_overlap_prop_all': 0.12037037037037039,
    'p_pronouns': 0.034482758620689655,
    'pronoun_noun_ratio': 0.09090909090909091,
    'p_demonstratives': 0.0,
    'p_given': 0.17647058823529413,
    'tense_repetition': 0.0,
    'mood_repetition': 1.0,
    'temporal_cohesion': 0.5,
    'connectors': 103.44827586206898,
    'connectors_causal': 34.48275862068966,
    'connectors_adversative': 34.48275862068966,
    'connectors_concessive': 0.0,
    'connectors_temporal': 0.0,
    'connectors_additive': 0.0,
    'connectors_conditional': 0.0,
    'connectors_reformulative': 34.48275862068966,
    'connectors_primary': 0.0,
    'connectors_secondary': 103.44827586206898}
    ```

    The occurrences of the connectors are in an attribute of their own:

    ``` python
    cs.connector_spans
    # (Connector(sent=1, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary'),
    #  Connector(sent=2, start=0, end=2, text='es decir', cls='reformulative', kind='secondary'),
    #  Connector(sent=3, start=0, end=3, text='por lo tanto', cls='causal', kind='secondary'))
    ```

### print_stats

Prints a table with the computed cohesion statistics.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    cs.print_stats()
    ```

    _Result_:

    ``` bash
                            Statistic                         |  Value
    --------------------------------------------------------------------
    Noun overlap in adjacent sentences                        |   0.33
    Noun overlap in all pairs of sentences                    |   0.50
    Argument overlap in adjacent sentences                    |   0.33
    Argument overlap in all pairs of sentences                |   0.50
    Content word overlap in adjacent sentences                |   0.33
    Content word overlap in all pairs of sentences            |   0.50
    Share of shared content words in adjacent sentences       |   0.08
    Share of shared content words in all pairs of sentences   |   0.12
    Share of pronouns                                         |   0.03
    Ratio of pronouns to nouns                                |   0.09
    Share of demonstratives                                   |   0.00
    Share of content words seen before                        |   0.18
    Repetition of the tense in adjacent sentences             |   0.00
    Repetition of the mood in adjacent sentences              |   1.00
    Temporal cohesion                                         |   0.50
    Connectors per 1000 words                                 |  103.45
    Causal connectors per 1000 words                          |  34.48
    Adversative connectors per 1000 words                     |  34.48
    Concessive connectors per 1000 words                      |   0.00
    Temporal connectors per 1000 words                        |   0.00
    Additive connectors per 1000 words                        |   0.00
    Conditional connectors per 1000 words                     |   0.00
    Reformulative connectors per 1000 words                   |  34.48
    Primary connectors per 1000 words                         |   0.00
    Secondary connectors per 1000 words                       |  103.45
    ```

## Connector search { #find_connectors }

!!! info ""
    **ests.cohesion_stats.find_connectors()**, **ests.cohesion_stats.load_connectors()**

`find_connectors(words, connectors=None, sent_index=0, pos=None)` finds the connectors of a single sentence and returns their occurrences, and `load_connectors()` returns the dictionary of the library, the class and the kind by connector.

!!! example "Example"

    ``` python
    from ests.cohesion_stats import find_connectors, load_connectors

    find_connectors(["Sin", "embargo", "no", "vino"])
    # [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]

    find_connectors(["El", "antes", "y", "el", "después"], pos=["DET", "NOUN", "CCONJ", "DET", "NOUN"])
    # [Connector(sent=0, start=2, end=3, text='y', cls='additive', kind='primary')]

    load_connectors()["por lo tanto"]
    # ('causal', 'secondary')
    ```
