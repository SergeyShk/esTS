# Style metrics

!!! info ""
    **ests.style_stats.StyleStats**

## Description

A module for computing the style metrics of a text: the SEO indicators of the [Advego](https://advego.com/text/seo/) and [Text.ru](https://text.ru/seo) services - nausea, water content, spam score, naturalness of the distribution of words by Zipf's law and keyword density - and the lexical markers of the officialese style that the Spanish guides to plain language warn about: the nouns derived from a verb, the compound prepositions of the administrative style, the parenthetical expressions and the clichés. The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The exact formulas of the services are not published, so the commonly accepted definitions are implemented; they are described in the [functions](style_stats_funcs.md) section. By default words are extracted in lower case without lemmatization, so the forms of one word count as different words, as in Advego. To compute by lemmas, pass a [`WordsExtractor`](../extractors/words.md) object with `use_lexemes=True` and `lowercase=True`.

The markers of the officialese style are counted over the unfiltered word forms (`forms`) whatever the extractor passed, by the lists `COMPOUND_PREPOSITIONS`, `PARENTHETICALS` and `OFFICIALESE_CLICHES` of `ests.constants`. A phrase ending in `a` or `de` also matches the contraction with the article (`a efectos del`, `conforme al`), and a phrase that starts with an infinitive stands for every form of the verb: `proceder a` finds `se procedió a`, `dar cumplimiento` finds `dio cumplimiento`. The verbal nouns need the parts of speech and the lemmas: a `Doc` gives its own annotation, and a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp` the first time `verbal_nouns` is read - the other metrics of a string need no model.

!!! note "Note"
    The metrics are computed by accessing the corresponding attribute or by calling the `get_stats` method of the `StyleStats` object. The norms of the services are meant for texts of several hundred words; on short texts nausea and spam are uninformative.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `words_extractor` | WordsExtractor | `None` | Word extraction tool |
| `stopwords` | list[str] | `None` | Stopwords for the water content; if not given, `STOPWORDS` and the one-word parenthetical expressions are used |
| `top_n` | int | `10` | Number of the most frequent words for the academic nausea and the naturalness by Zipf's law |
| `cliches` | list[str] | `None` | List of clichés; if not given, `OFFICIALESE_CLICHES` is used |
| `nlp` | Language | `None` | Pipeline of spaCy that parses a string for the verbal nouns; without it the model `es_core_news_sm` is loaded |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of the extracted words |
| `forms` | tuple[str] | Tuple of the unfiltered word forms in lower case; the markers of the officialese style are counted over them |
| `classic_nausea` | float | Classic nausea |
| `academic_nausea` | float | Academic nausea in percent |
| `water` | float | Water content in percent |
| `spam` | float | Spam score in percent |
| `zipf_naturalness` | float | Naturalness by Zipf's law in percent |
| `verbal_nouns` | float | Share of the verbal nouns among the nouns in percent |
| `compound_prepositions` | float | Compound prepositions per 100 words |
| `parentheticals` | float | Parenthetical expressions per 100 words |
| `cliches` | float | Clichés per 100 words |

Norms of the services:

| Metric | Norm |
| :----: | :--: |
| Classic nausea | at most 7, in practice 1-5 (Advego) |
| Academic nausea | 5-15% (Advego) |
| Water content | up to 15% - natural, 15-30% - excessive, above 30% - high (Text.ru) |
| Spam score | up to 30% - natural, 30-60% - SEO-optimized text, above 60% - spammed (Text.ru) |
| Naturalness by Zipf's law | at least 50% (pr-cy, megaindex) |

!!! warning "The water content of Spanish"
    The norms of Text.ru are set for Russian, which has no articles. A Spanish text has more water by its grammar alone: the 150 texts of the [corpus of literature](../datasets/spanishliterature.md) have 42-54% of it, the prose 49% by the median. Compare the water content of texts with each other, not with the norm.

## Methods

### keyword_density

Returns the density of keywords and phrases - the frequency of each per 100 words of the text. A phrase of several words separated by spaces is looked for as a sequence of words, in any case.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `keywords` | tuple[str] | `-` | Keywords or phrases |

!!! example "Example"

    ``` python
    from ests import StyleStats

    text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
    StyleStats(text).keyword_density("tres tristes", "trigo")
    # {'tres tristes': 16.666666666666668, 'trigo': 8.333333333333334}
    ```

### get_stats

Returns a dictionary with the computed style metrics.

### print_stats

Prints a table with the computed style metrics.

## Usage example

The same notice written in the administrative style and in plain language.

!!! example "Example"

    _Code_:

    ``` python
    from ests import StyleStats

    official = (
        "En el marco del procedimiento de referencia, y a efectos de dar cumplimiento a lo "
        "dispuesto en la normativa vigente, se procedió a la revisión de la documentación "
        "presentada. No obstante, en virtud de la resolución de la comisión, se llevará a cabo "
        "la notificación de la misma a la mayor brevedad, en tiempo y forma."
    )
    plain = (
        "Hemos revisado los documentos que nos envió, como pide la ley. La comisión ha "
        "decidido su caso y le avisaremos lo antes posible."
    )

    StyleStats(official).print_stats()
    StyleStats(plain).get_stats()
    ```

    _Result_:

    ``` bash
                          Metric                      |  Value
    ------------------------------------------------------------
    Classic nausea                                    |   2.83
    Academic nausea (%)                               |  55.36
    Water content (%)                                 |  57.14
    Spam score (%)                                    |  37.50
    Naturalness by Zipf's law (%)                     |  53.57
    Verbal nouns (% of nouns)                         |  47.06
    Compound prepositions (per 100 words)             |   5.36
    Parenthetical expressions (per 100 words)         |   1.79
    Officialese clichés (per 100 words)               |   8.93

    {'classic_nausea': 1.4142135623730951,
     'academic_nausea': 47.82608695652174,
     'water': 43.47826086956522,
     'spam': 4.3478260869565215,
     'zipf_naturalness': 100.0,
     'verbal_nouns': 25.0,
     'compound_prepositions': 0.0,
     'parentheticals': 0.0,
     'cliches': 0.0}
    ```

The notice of 56 words has three compound prepositions (`en el marco del`, `a efectos de`, `en virtud de`), five clichés (`dar cumplimiento`, `se procedió a`, `se llevará a cabo`, `a la mayor brevedad`, `en tiempo y forma`) and one parenthetical expression, and almost half of its nouns are derived from a verb (`revisión`, `notificación`, `resolución`); the plain version of 23 words has none of the markers. The anaphoric `de la misma`, which the guides also advise against, is not counted: telling it from `el mismo día` needs the syntax.
