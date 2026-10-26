# Cohesion statistics

``` {.python .signature}
CohesionStats(source, sents_extractor=None, connectors=None, nlp=None)
```

The cohesion statistics of a text in the manner of [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) and of its Spanish adaptation [Coh-Metrix-Esp](https://aclanthology.org/L16-1745/): the overlap of the sentences, the givenness, the temporal cohesion and the connectors of a dictionary. The sentences are compared by lemmas. The data source is a text or a `Doc` object of [spaCy](https://github.com/explosion/spaCy), and it has to be annotated: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, without the named entities, and a `Doc` must carry the parts of speech, which come from a `morphologizer` (or a `tagger` with an `attribute_ruler`), and the lemmas, which come from a `lemmatizer`.

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, an extractor of another type, a pipeline in `nlp` that is not a spaCy `Language`, connectors that are not a dictionary of phrases and pairs of strings;
- `SourceError` - a source without words; a `Doc` without the parts of speech or the lemmas (a `Doc` of `spacy.blank("es")`); a string longer than the `max_length` of the pipeline or with a character without a UTF-8 form;
- `ParameterError` - an unknown class or kind of a connector;
- `DatasetNotFoundError` - a string without `nlp` when the model is not installed.

The class extends the `CohesionStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/) core with the Spanish layer. A `Doc` without sentence boundaries - from a pipeline without a parser - is split into sentences by the Spanish [`SentsExtractor`](../extractors/sentences.md). The features of the words come from the [Universal Dependencies](https://universaldependencies.org/u/feat/) annotation, the temporal cohesion compares the tense and the mood of the verbs, and the connectors are found by [`SpanishConnectorMatcher`](#ConnectorMatcher) over the dictionary of [`load_connectors`](#connectors). The `print_stats` table takes the descriptions of `COHESION_STATS_DESC` of `ests.constants`.

The `max_length` of the pipeline is a million characters by default: split a longer text into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

The words are classified by the Universal Dependencies annotation:

| Notion | Universal Dependencies |
| :----- | :--------------------- |
| Nouns | `NOUN`, `PROPN` |
| Pronouns | `PRON` and the determiners that point at something: possessive (`Poss=Yes`), demonstrative or personal (`PronType=Dem`, `Prs`) - `mi libro` and `este libro` hold a pronoun, `el libro` and `cada libro` do not, and neither do the quantifiers and the indefinites (`cada`, `todos`, `ningún`, `otro`, `cualquier`) |
| Arguments | `NOUN`, `PROPN`, `PRON`, without the determiners that count as pronouns |
| Content words | `CONTENT_UD_POS` of `anyts.constants` (`NOUN`, `PROPN`, `ADJ`, `VERB`, `ADV`) without the demonstratives |
| Demonstratives | `PronType=Dem` |
| Tense and mood | features `Tense` and `Mood` |

=== "Code"

    ``` python
    from ests import CohesionStats

    text = (
        "El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve "
        "el problema. Es decir, la comisión aplazó la decisión. Por lo tanto, el "
        "problema sigue abierto."
    )
    cs = CohesionStats(text)
    cs.print_stats()
    ```

=== "Result"

    ```
                                 Statistic                             |  Value
    ------------------------------------------------------------------------------
    Noun overlap in adjacent sentences                                 |   0.33
    Noun overlap in all pairs of sentences                             |   0.50
    Argument overlap in adjacent sentences                             |   0.33
    Argument overlap in all pairs of sentences                         |   0.50
    Content word overlap in adjacent sentences                         |   0.33
    Content word overlap in all pairs of sentences                     |   0.50
    Share of shared content words in adjacent sentences                |   0.08
    Share of shared content words in all pairs of sentences            |   0.12
    Share of the nouns of a sentence repeated in the next two          |   0.60
    Share of the arguments of a sentence repeated in the next two      |   0.60
    Share of the content words of a sentence repeated in the next two  |   0.38
    Share of the nouns of a paragraph repeated in the next one         |   nan
    Share of the arguments of a paragraph repeated in the next one     |   nan
    Share of the content words of a paragraph repeated in the next one |   nan
    Share of pronouns                                                  |   0.03
    Ratio of pronouns to nouns                                         |   0.09
    Share of demonstratives                                            |   0.00
    Share of content words seen before                                 |   0.18
    Repetition of the tense in adjacent sentences                      |   0.00
    Repetition of the mood in adjacent sentences                       |   1.00
    Temporal cohesion                                                  |   0.50
    Connectors per 1000 words                                          |  103.45
    Connectors linking a sentence to the ones before per 1000 words    |  103.45
    Connectors linking the parts of a sentence per 1000 words          |   0.00
    Causal connectors per 1000 words                                   |  34.48
    Adversative connectors per 1000 words                              |  34.48
    Concessive connectors per 1000 words                               |   0.00
    Temporal connectors per 1000 words                                 |   0.00
    Additive connectors per 1000 words                                 |   0.00
    Conditional connectors per 1000 words                              |   0.00
    Reformulative connectors per 1000 words                            |  34.48
    Primary connectors per 1000 words                                  |   0.00
    Secondary connectors per 1000 words                                |  103.45
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source: a text or a `Doc` with the parts of speech and the lemmas |
| `sents_extractor` | `SentsExtractor` | `None` | Sentence extraction tool; given, it splits a text and a `Doc` by their text, whatever the sentence boundaries of the pipeline |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Class and kind by connector; the dictionary of `load_connectors` by default |
| `nlp` | `Language` | `None` | spaCy pipeline that parses a string; the model `es_core_news_sm` of `ests.utils.get_nlp` if not given |

## Attributes

--8<-- "stats/cohesion_stats.md:CohesionStats-attributes"

The extractor given is kept in the attribute `sents_extractor`, `None` without it.

=== "Code"

    ``` python
    cs.lemmas[1]
    cs.n_nouns, cs.n_pronouns, cs.n_content_words, cs.n_given
    cs.connector_spans
    cs.c_connectors
    ```

=== "Result"

    ```
    ('sin', 'embargo', 'el', 'informe', 'no', 'resolver', 'el', 'problema')
    (11, 1, 17, 3)
    (Connector(sent=1, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary'),
     Connector(sent=2, start=0, end=2, text='es decir', cls='reformulative', kind='secondary'),
     Connector(sent=3, start=0, end=3, text='por lo tanto', cls='causal', kind='secondary'))
    {'es decir': 1, 'por lo tanto': 1, 'sin embargo': 1}
    ```

## Metrics

Every metric is an attribute of the object, computed when it is created, and `get_stats` gives the metrics of the table; `aspect_repetition` is an attribute outside it.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| [`noun_overlap_adjacent`](#overlap) | Share of the adjacent pairs of sentences sharing a noun | 0-1, `nan` for one sentence | Neighbouring sentences tied tighter |
| [`noun_overlap_all`](#overlap) | Share of all the pairs of sentences sharing a noun | 0-1, `nan` for one sentence | The whole text tied tighter |
| [`argument_overlap_adjacent`](#overlap) | Share of the adjacent pairs sharing a noun or a pronoun | 0-1, `nan` for one sentence | Neighbouring sentences tied tighter |
| [`argument_overlap_all`](#overlap) | Share of all the pairs sharing a noun or a pronoun | 0-1, `nan` for one sentence | The whole text tied tighter |
| [`content_overlap_adjacent`](#overlap) | Share of the adjacent pairs sharing a content word | 0-1, `nan` for one sentence | Neighbouring sentences tied tighter |
| [`content_overlap_all`](#overlap) | Share of all the pairs sharing a content word | 0-1, `nan` for one sentence | The whole text tied tighter |
| [`content_overlap_prop_adjacent`](#proportional_overlap) | Mean share of the shared content words (Dice) in the adjacent pairs | 0-1, `nan` for one sentence | More words shared by neighbours |
| [`content_overlap_prop_all`](#proportional_overlap) | Mean share of the shared content words (Dice) in all the pairs | 0-1, `nan` for one sentence | More words shared across the text |
| [`noun_overlap_2_sent`](#forward_overlap) | Share of the nouns of a sentence repeated in one of the next two | 0-1, `nan` for fewer than three sentences | Nouns carried further |
| [`argument_overlap_2_sent`](#forward_overlap) | Share of the arguments of a sentence repeated in one of the next two | 0-1, `nan` for fewer than three sentences | Arguments carried further |
| [`content_overlap_2_sent`](#forward_overlap) | Share of the content words of a sentence repeated in one of the next two | 0-1, `nan` for fewer than three sentences | Content words carried further |
| [`noun_overlap_para`](#forward_overlap) | Share of the nouns of a paragraph repeated in the next one | 0-1, `nan` for one paragraph | Paragraphs tied tighter |
| [`argument_overlap_para`](#forward_overlap) | Share of the arguments of a paragraph repeated in the next one | 0-1, `nan` for one paragraph | Paragraphs tied tighter |
| [`content_overlap_para`](#forward_overlap) | Share of the content words of a paragraph repeated in the next one | 0-1, `nan` for one paragraph | Paragraphs tied tighter |
| [`p_pronouns`](#pronouns) | Share of the pronouns among the words | 0-1 | More reference by pronouns |
| [`pronoun_noun_ratio`](#pronouns) | Ratio of the pronouns to the nouns | 0 and above, `nan` without nouns | More pronouns per noun |
| [`p_demonstratives`](#pronouns) | Share of the demonstratives among the words | 0-1 | More pointing back |
| [`p_given`](#given) | Share of the content words whose lemma was used before in the text | 0-1, `nan` without content words | More given information |
| [`tense_repetition`](#temporal_cohesion) | Share of the adjacent pairs of sentences with the same dominant tense | 0-1, `nan` without two adjacent sentences with the feature | A steadier tense |
| [`mood_repetition`](#temporal_cohesion) | Share of the adjacent pairs with the same dominant mood | 0-1, `nan` without two adjacent sentences with the feature | A steadier mood |
| [`temporal_cohesion`](#temporal_cohesion) | Mean of the repetitions of the tense and of the mood | 0-1, `nan` when one of them is `nan` | A steadier time frame |
| [`connectors`](#connectors) | Connectors per 1000 words | 0-1000 | More explicit links |
| [`connectors_inter`](#connectors) | Connectors linking a sentence to the ones before per 1000 words | 0-1000 | More links between sentences |
| [`connectors_intra`](#connectors) | Connectors linking the parts of a sentence per 1000 words | 0-1000 | More links inside sentences |
| [`connectors_<class>`](#connectors) | Connectors of a class per 1000 words: `causal`, `adversative`, `concessive`, `temporal`, `additive`, `conditional`, `reformulative` | 0-1000 | More links of the class |
| [`connectors_primary`, `connectors_secondary`](#connectors) | Primary and secondary connectors per 1000 words | 0-1000 | More links of the kind |

The functions of the overlaps, the givenness and the repetitions (`calc_overlap`, `calc_proportional_overlap`, `calc_overlaps`, `dice`, `count_given`, `calc_repetition`, `dominant`) are those of `anyts.cohesion_stats`, which esTS does not re-export; they are on the [anyTS page](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/). `calc_forward_overlap` of the [overlaps with the next segments](#forward_overlap) is imported from `ests.cohesion_stats`.

<div class="metric-card" markdown>

### Binary overlap { #overlap }

`noun_overlap_adjacent` · `noun_overlap_all` · `argument_overlap_adjacent` · `argument_overlap_all` · `content_overlap_adjacent` · `content_overlap_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

The binary overlap of Coh-Metrix (CRFNO1, CRFAO1, CRFSO1 over the adjacent pairs, CRFNOa, CRFAOa, CRFSOa over all of them): the share of the pairs of sentences that share the lemma of at least one noun, argument or content word; `nan` for a text shorter than two sentences.

$$
\frac{\textrm{Number of pairs sharing a lemma}}{\textrm{Number of pairs}}
$$

</div>

<div class="metric-card" markdown>

### Proportional overlap { #proportional_overlap }

`content_overlap_prop_adjacent` · `content_overlap_prop_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

The proportional overlap of Coh-Metrix (CRFCWO1, CRFCWOa): the Dice coefficient of the sets of the lemmas of the content words $A$ and $B$ of two sentences, averaged over the adjacent pairs or over all of them, 0 for two sentences without content words; `nan` for a text shorter than two sentences.

$$
\frac{1}{\textrm{Number of pairs}} \sum_{(A, B)} \frac{2 \times |A \cap B|}{|A| + |B|}
$$

</div>

<div class="metric-card" markdown>

### Overlap with the next sentences and paragraphs { #forward_overlap }

`noun_overlap_2_sent` · `argument_overlap_2_sent` · `content_overlap_2_sent` · `noun_overlap_para` · `argument_overlap_para` · `content_overlap_para` · [TAACO](https://doi.org/10.3758/s13428-015-0651-7)
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-forward_overlap"

--8<-- "stats/cohesion_stats.md:calc_forward_overlap"

In esTS a string is parsed into a `Doc`, so both are split into paragraphs by the blank lines between their tokens.

=== "Code"

    ``` python
    from ests.cohesion_stats import calc_forward_overlap

    calc_forward_overlap([{"gato", "ventana"}, {"pájaro"}, {"gato"}], span=2)
    text = (
        "El gato estaba en la ventana. Miraba a los pájaros.\n\n"
        "Los pájaros se fueron y el gato se durmió. Mañana el gato volverá a la ventana."
    )
    paragraphs = CohesionStats(text)
    paragraphs.n_paragraphs, paragraphs.noun_overlap_para, paragraphs.content_overlap_para
    ```

=== "Result"

    ```
    0.5
    (2, 1.0, 0.6)
    ```

</div>

<div class="metric-card" markdown>

### Pronouns and demonstratives { #pronouns }

`p_pronouns` · `pronoun_noun_ratio` · `p_demonstratives`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-pronouns"

In esTS they are those of the table of the classes of words above, the features of [`token_info`](#token_info).

</div>

<div class="metric-card" markdown>

### Givenness { #given }

`p_given`
{ .metric-meta }

The share of the content words whose lemma was used before in the text, the current sentence included; the first occurrence of a lemma is new.

$$
\frac{\textrm{Number of given content words}}{\textrm{Number of content words}}
$$

</div>

<div class="metric-card" markdown>

### Temporal cohesion { #temporal_cohesion }

`tense_repetition` · `mood_repetition` · `temporal_cohesion` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

The repetition of the tense of Coh-Metrix (SMTEMP): every sentence gets the dominant value of the feature of its verbs - the most frequent one, the first of the equally frequent - and the metric is the share of the adjacent pairs of sentences with the same value; a pair where one of the sentences has no verb with the feature is skipped, and without a single such pair the value is `nan`.

$$
\frac{\textrm{Number of pairs with the same dominant value}}{\textrm{Number of pairs with the feature}}
$$

Spanish has no aspect in the Universal Dependencies annotation of the models, so esTS compares the mood next to the tense (`temporal_features` is `("tense", "mood")`): `temporal_cohesion` is the mean of `tense_repetition` and `mood_repetition`. The attribute `aspect_repetition` of the core is `nan` without the feature `Aspect`.

</div>

<div class="metric-card" markdown>

### Connectors { #connectors }

`connectors` · `connectors_inter` · `connectors_intra` · `connectors_<class>` · `connectors_primary` · `connectors_secondary`
{ .metric-meta }

--8<-- "stats/cohesion_stats.md:CohesionStats-connectors"

The subordinators of esTS are the one-word connectors tagged `SCONJ` or `ADP` (`cuando`, `aunque`, `si`) and the conjunctive and prepositional phrases of `CONNECTOR_SUBORDINATORS` (`ya que`, `a pesar de`, `siempre que`), but `porque` and `conque`, which open a sentence linking it to the one before (`CONNECTOR_PARCELLATION`: `¿Por qué? Porque...`). In `Ya que estás aquí, ayúdame` the connector is intra-sentential; in `No vino. Porque llovía.` and `Sin embargo, no.` it is inter-sentential. The anaphoric forms of the prepositional subordinators (`a pesar de esto`, `gracias a ello`) are entries of the dictionary of their own, which link a sentence to the one before.

``` {.python .signature}
load_connectors()
```

The connector dictionary of esTS: the file `ests/resources/connectors.tsv`, 273 discourse markers (*marcadores del discurso*) of Martín Zorraquino and Portolés (1999) and conjunctions of the NGLE, each with its class of `CONNECTOR_CLASSES` and its kind of `CONNECTOR_KINDS` of `anyts.constants`. The classes are the causal, adversative, temporal and additive connectives of Coh-Metrix with the concessive, conditional and reformulative ones added. The dictionary is read-only and shared by every caller, so a dictionary of your own goes through the `connectors` parameter.

| Class | Key | Examples |
| :---- | :-- | :------- |
| Causal | `causal` | porque, por lo tanto, así que |
| Adversative | `adversative` | pero, sin embargo, en cambio |
| Concessive | `concessive` | aunque, a pesar de, de todos modos |
| Temporal | `temporal` | cuando, a continuación, por último |
| Additive (ordinals included) | `additive` | y, además, por otra parte, en primer lugar |
| Conditional | `conditional` | si, a menos que, de lo contrario |
| Reformulative (operators of concretion included) | `reformulative` | es decir, en resumen, por ejemplo, en particular, sobre todo |

The primary connectors (`primary`) are conjunctions, conjunctive locutions and adverbs (porque, aunque, además), the secondary ones (`secondary`) lexicalized phrases (sin embargo, por lo tanto, es decir). `si` also opens indirect questions, exclamations and hypothetical comparisons - about a third of its occurrences in the corpus of literature - and is no connector after a verb that takes an indirect question, after an opening `¡` ([`is_connector_blocked`](#is_connector_blocked)), and after `como`, `cual`, `vaya` and `maldito` (`CONNECTOR_BLOCKED_BEFORE`: `como si fuera`, `vaya si lo sé`); the rules find about three quarters of these `si` and drop 25 % of the conditional connectors of the literature. `siempre que` is temporal with the indicative and conditional with the subjunctive and is counted in its class of the dictionary. The rules by which a word of the dictionary counts as a connector are those of the [matcher](#ConnectorMatcher).

=== "Code"

    ``` python
    from ests.cohesion_stats import load_connectors

    connectors = load_connectors()
    len(connectors), connectors["por lo tanto"]
    ```

=== "Result"

    ```
    (273, ('causal', 'secondary'))
    ```

!!! warning "Warning"
    The words of a marker are counted as words like any other: the noun `embargo` of `sin embargo` is a noun and a content word of its sentence, so a text that repeats a marker gains a little overlap from it.

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the cohesion statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    cs.get_stats()
    cs.describe("p_given")
    ```

=== "Result"

    ```
    {'noun_overlap_adjacent': 0.3333333333333333,
     'noun_overlap_all': 0.5,
     'argument_overlap_adjacent': 0.3333333333333333,
     'argument_overlap_all': 0.5,
     'content_overlap_adjacent': 0.3333333333333333,
     'content_overlap_all': 0.5,
     'content_overlap_prop_adjacent': 0.08333333333333333,
     'content_overlap_prop_all': 0.12037037037037035,
     'noun_overlap_2_sent': 0.6,
     'argument_overlap_2_sent': 0.6,
     'content_overlap_2_sent': 0.375,
     'noun_overlap_para': nan,
     'argument_overlap_para': nan,
     'content_overlap_para': nan,
     'p_pronouns': 0.034482758620689655,
     'pronoun_noun_ratio': 0.09090909090909091,
     'p_demonstratives': 0.0,
     'p_given': 0.17647058823529413,
     'tense_repetition': 0.0,
     'mood_repetition': 1.0,
     'temporal_cohesion': 0.5,
     'connectors': 103.44827586206898,
     'connectors_inter': 103.44827586206898,
     'connectors_intra': 0.0,
     'connectors_causal': 34.48275862068966,
     'connectors_adversative': 34.48275862068966,
     'connectors_concessive': 0.0,
     'connectors_temporal': 0.0,
     'connectors_additive': 0.0,
     'connectors_conditional': 0.0,
     'connectors_reformulative': 34.48275862068966,
     'connectors_primary': 0.0,
     'connectors_secondary': 103.44827586206898}
    None
    ```

## Connector matcher { #ConnectorMatcher }

``` {.python .signature}
SpanishConnectorMatcher(connectors)
```

--8<-- "stats/cohesion_stats.md:ConnectorMatcher"

`SpanishConnectorMatcher` is a subclass of the core `ConnectorMatcher` with the rules of Spanish; words and connectors are compared in lower case. A one-word connector takes a part of speech of `CONNECTOR_POS` - a conjunction, a particle, an adverb, an adposition, an interjection, a proper noun or `X` - or of `CONNECTOR_POS_EXTRA` for its form (`pues` and `verbigracia` as `NOUN`, `resumiendo`, `recapitulando` and `concluyendo` as `VERB`). It is no connector right after a determiner, so `el antes y el después` holds one connector, `y`, and not three; and as a proper noun it counts only at the start of a sentence, where the models read a marker so (`Primeramente`), so the surname in `Habló con Juan Luego ayer` is no connector. A marker that is part of another phrase is dropped: the words after it of `CONNECTOR_BLOCKED_AFTER` (`antes de la reunión`, `en cuanto a`, `a pesar de todo lo que`), the words before it of `CONNECTOR_BLOCKED_BEFORE` (`algo así como`, `como si fuera`) and the parts of speech of the word after it of `CONNECTOR_BLOCKED_AFTER_POS` (`sobre todo el texto`, `a pesar de todo el esfuerzo`) make it none, while `antes, firmó el acta` and `sobre todo cuando llueve` count their marker. A few markers depend on their place: `pues` opening a sentence opens a reply (`Pues bien`) and is no connector (`CONNECTOR_NOT_AT_START`), and `encima` counts inside a sentence only after `y`, `e`, `ni` or `pero` (`y encima llueve`, `CONNECTOR_ONLY_AFTER`). These lists are attributes of the matcher: `CONNECTOR_POS` is `pos_tags`, the others are named without `CONNECTOR_` in lower case (`CONNECTOR_BLOCKED_AFTER` is `blocked_after`); `not_after_pos` is the determiner `DET`, `start_only_pos` the proper noun `PROPN`, and `read_through_marks` is empty in esTS. A punctuation mark inside a conjunctive phrase ending in `que`, `como` or `si` (`CONNECTOR_SPLIT_BY_MARKS`) makes the conjunction a word of its own, so `No tire así, que se romperá` and `lo de siempre, que...` hold no connector; the consecutive phrases with `de modo`, `de manera`, `de forma` or `de suerte` (`de modo que`, `de tal manera que`) and `bien es verdad que` are left out, as old texts put a comma before their `que` (`de tal modo, que`).

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-find"

`CohesionStats` passes the positions of the punctuation marks of every sentence, so in `sin gracia alguna, y el amor` the comma cuts `y` off the determiner `alguna` and it counts, and `encima` after a comma counts too.

=== "Code"

    ``` python
    from ests.cohesion_stats import SpanishConnectorMatcher, load_connectors

    matcher = SpanishConnectorMatcher(load_connectors())
    words = ["Vivía", "sin", "gracia", "alguna", "y", "el", "amor", "llegó"]
    pos = ["VERB", "ADP", "NOUN", "DET", "CCONJ", "DET", "NOUN", "VERB"]
    matcher.find(words, pos=pos)
    matcher.find(words, pos=pos, breaks={4})
    ```

=== "Result"

    ```
    []
    [Connector(sent=0, start=4, end=5, text='y', cls='additive', kind='primary')]
    ```

--8<-- "stats/cohesion_stats.md:ConnectorMatcher-is_subordinator"

`subordinators` is `CONNECTOR_SUBORDINATORS` and `parcellation` is `CONNECTOR_PARCELLATION`.

=== "Code"

    ``` python
    matcher.is_subordinator(matcher.find(["Ya", "que", "estás", "aquí"])[0])
    matcher.is_subordinator(matcher.find(["Porque", "llovía"])[0], "SCONJ")
    ```

=== "Result"

    ```
    True
    False
    ```

## Connector search { #find_connectors }

``` {.python .signature}
find_connectors(words, connectors=None, sent_index=0, pos=None, breaks=None, blocked=None)
```

Searches a sentence for connectors with the `find` method of `SpanishConnectorMatcher` over the dictionary `connectors`, that of `load_connectors` by default; the other parameters and the errors are those of the matcher and of `find`. Without `breaks`, the positions of the words a punctuation mark stands before ([`find_marks`](https://sergeyshk.github.io/anyTS/utils/words/#find_marks) of a string), the words are read as adjacent; `blocked`, the positions of the words of [`is_connector_blocked`](#is_connector_blocked), drops the `si` that `CohesionStats` drops. With a dictionary of your own the function builds a matcher on every call, so over many sentences build `SpanishConnectorMatcher(connectors)` once and call its `find`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Class and kind by connector |

=== "Code"

    ``` python
    from ests.cohesion_stats import find_connectors

    find_connectors(["Sin", "embargo", "no", "vino"])
    find_connectors(["El", "antes", "y", "el", "después"], pos=["DET", "NOUN", "CCONJ", "DET", "NOUN"])
    find_connectors(["No", "tire", "así", "que", "se", "romperá"], breaks={3})
    find_connectors(["No", "sé", "si", "vendrá"], blocked={2})
    ```

=== "Result"

    ```
    [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]
    [Connector(sent=0, start=2, end=3, text='y', cls='additive', kind='primary')]
    []
    []
    ```

## Word features { #token_info }

``` {.python .signature}
token_info(token)
```

The features of a spaCy token for the cohesion statistics by its Universal Dependencies annotation, after the table of the classes of words: a `WordInfo` named tuple with `lemma` (the `lemma_` of the token in lower case), `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` and `mood` (the first value of `Tense` and of `Mood`, `None` without it). [`LexicalStats`](lexical_stats.md) takes its content words from it.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | spaCy token |

=== "Code"

    ``` python
    from ests.cohesion_stats import token_info
    from ests.utils import get_nlp

    doc = get_nlp()("Mi hermano miraba este libro.")
    token_info(doc[2])
    token_info(doc[3])
    ```

=== "Result"

    ```
    WordInfo(lemma='mirar', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='Imp', mood='Ind')
    WordInfo(lemma='este', noun=False, pronoun=True, demonstrative=True, argument=False, content=False, tense=None, mood=None)
    ```

## Blocked connectors { #is_connector_blocked }

``` {.python .signature}
is_connector_blocked(token)
```

Checks whether no connector starts at a token by the words before it in a `Doc`: a `si` that opens no condition. It is so after a verb of `CONNECTOR_QUESTION_VERBS` - `saber`, `ver`, `mirar`, `preguntar`, `dudar`, `ignorar`, `pensar`, `averiguar`, `probar`, `comprobar`, `observar`, `examinar`, `determinar`, `decidir`, `considerar`, `consultar`, `investigar`, `adivinar` - tagged `VERB` or `AUX`, by the lemma of the model or of `ests.utils.lemmatize` (`no sé si vendrá`, `a ver si llega`, `preguntó si tenía hambre`), and after an opening `¡` (`¡Si ya te lo dije!`). On a sample of the literature the rule of the verbs was right in all the cases checked, that of `¡` in about nine of ten. `CohesionStats` sets `connector_blocked` of the words of the core by it, and the [`connectors`](../visualizers/highlight.md) layer of the highlighting of a `Doc` drops the same `si`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | spaCy token |

=== "Code"

    ``` python
    from ests.cohesion_stats import is_connector_blocked
    from ests.utils import get_nlp

    doc = get_nlp()("No sé si vendrá. Si llueve, me quedo. ¡Si ya te lo dije!")
    [is_connector_blocked(token) for token in doc if token.lower_ == "si"]
    ```

=== "Result"

    ```
    [True, False, True]
    ```
