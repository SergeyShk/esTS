# Style metrics

``` {.python .signature}
StyleStats(source, words_extractor=None, stopwords=None, top_n=10, cliches=None, nlp=None, nausea_stopwords=None)
```

--8<-- "stats/style_stats.md:StyleStats"

The class extends the `StyleStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/style_stats/) core with the hooks of Spanish, given in the cards of the metrics: the stopwords, the compound prepositions, parenthetical expressions and clichés that the Spanish-language guides to plain language warn about, found with their contractions and the forms of their verbs, and the nouns derived from a verb among the nouns of the spaCy model. The words of a string are extracted by the Spanish [`WordsExtractor`](../extractors/words.md) and are not lemmatized, so the forms of one word count as different words, as in Advego; to compute by lemmas, pass a `WordsExtractor` with `use_lexemes=True` and `lowercase=True`. The `print_stats` table takes the descriptions of `ests.constants.STYLE_STATS_DESC`.

The verbal nouns need the parts of speech and the lemmas: a `Doc` gives its own annotation, also when an extractor takes its text, and a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp` the first time `verbal_nouns` or [`markers()`](#methods) is read - the other metrics of a string need no model. A string longer than the `max_length` of the pipeline is parsed in parts of whole sentences. Besides the errors above, a pipeline that is not a spaCy `Language` raises `SourceTypeError` and a string with a character without a UTF-8 form raises `SourceError` from the Spanish tokenizer; reading `verbal_nouns` or `markers()` raises `SourceError` for a `Doc` without the parts of speech or the lemmas and for a string with a sentence longer than the `max_length` of the pipeline.

The examples of this page take a notice written in the administrative style:

=== "Code"

    ``` python
    from ests import StyleStats

    official = (
        "En el marco del procedimiento de referencia, y a efectos de dar cumplimiento a lo "
        "dispuesto en la normativa vigente, se procedió a la revisión de la documentación "
        "presentada. No obstante, en virtud de la resolución de la comisión, se llevará a cabo "
        "la notificación de la misma a la mayor brevedad, en tiempo y forma."
    )
    ss = StyleStats(official)
    ss.print_stats()
    ```

=== "Result"

    ```
                      Metric                  |  Value
    -----------------------------------------------------
    Classic nausea                            |   2.83
    Academic nausea (%)                       |  17.86
    Water content (%)                         |  57.14
    Spam score (%)                            |  37.50
    Naturalness by Zipf's law (%)             |  53.57
    Verbal nouns (% of nouns)                 |  47.06
    Compound prepositions (per 100 words)     |   5.36
    Parenthetical expressions (per 100 words) |   1.79
    Officialese clichés (per 100 words)       |   8.93
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `words_extractor` | `WordsExtractor` | `None` | Word extraction tool; for a `Doc` it is applied to its text |
| `stopwords` | `list[str]` / `set[str]` | `None` | Words of water; `is_stopword` if not given |
| `top_n` | `int` | `10` | Number of the most frequent words of the academic nausea and the naturalness by Zipf's law (`NAUSEA_TOP_N`) |
| `cliches` | `list[str]` / `set[str]` | `None` | Clichés; `OFFICIALESE_CLICHES` if not given |
| `nlp` | `Language` | `None` | spaCy pipeline that parses a string for the verbal nouns; the model `es_core_news_sm` of `ests.utils.get_nlp` if not given |
| `nausea_stopwords` | `list[str]` / `set[str]` | `None` | Stopwords left out of the most frequent words of the academic nausea; `is_stopword` if not given |

A set of words is taken in sorted order. `NAUSEA_TOP_N` is a constant of `anyts.constants`.

--8<-- "stats/style_stats.md:StyleStats-check_params"

## Attributes

--8<-- "stats/style_stats.md:StyleStats-attributes"

The pipeline of the parameter `nlp` is kept in the attribute `nlp`, `None` if not given.

## Metrics

--8<-- "stats/style_stats.md:StyleStats-metrics"

The functions of the cards are imported from `ests.style_stats`. The cards give the norms of [Advego](https://advego.com/text/seo/), [Text.ru](https://text.ru/seo), pr-cy and megaindex; the norms of the services are meant for texts of several hundred words, and on short texts nausea and spam are uninformative. esTS gives the metrics no scales, so `describe` gives `None`; the markers of the officialese have no norms.

<div class="metric-card" markdown>

### Classic nausea { #classic_nausea }

`classic_nausea` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_classic_nausea"

The norm of Advego is at most 7, 1-5 in practice.

</div>

<div class="metric-card" markdown>

### Academic nausea { #academic_nausea }

`academic_nausea` · `nausea_words()` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

``` {.python .signature}
calc_academic_nausea(text, top_n=10, stopwords=None)
```

The share of the occurrences of the `top_n` most frequent significant words among all the words, in percent. The exact formula of Advego is not published. With the stopwords the top ten of almost any text would be `de`, `la`, `que`, `el`, and its nausea above the norm. The norm of Advego is 5-15%, for texts of several hundred words: in a short text the top ten is a large share of the words whatever the style.

$$
100 \cdot \frac{\sum_{w \in \textrm{top}_n} f_w}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `top_n` | `int` | `10` | Number of the most frequent words (`NAUSEA_TOP_N`) |
| `stopwords` | `list[str]` / `set[str]` | `None` | Stopwords left out of the most frequent words; `is_stopword` if not given |

Raises:

- `SourceTypeError` - words that are not a list of strings, stopwords that are not a list or a set of strings;
- `ParameterError` - a `top_n` that is not an integer of at least one.

``` {.python .signature}
find_nausea_words(text, top_n=10, stopwords=None)
```

The `top_n` most frequent words without the stopwords, those the academic nausea counts, with their occurrences: the most frequent first, words of equal frequency in the order of the text. A stopword is a word of `stopwords`, in any case, or, without the list, a word of `is_stopword`. The parameters and the errors are those of `calc_academic_nausea`.

``` {.python .signature}
is_stopword(word)
```

Whether a word is a stopword, in any case: the 265 forms of `ests.constants.STOPWORDS` - the closed classes of the grammar: articles and the other determiners (`este`, `cada`, `mucho`), pronouns (`él`, `cuyo`, `nadie`), prepositions, conjunctions and interjections, with the adverbs that point, relate or ask (`aquí`, `así`, `dónde`) and the ones that negate, affirm or focus (`no`, `solo`, `también`) - and the one-word parenthetical expressions of `PARENTHETICALS` (`finalmente`, `naturalmente`). The forms of the old orthography are included (`á`, `ó`, `tí`). `StyleStats` takes it for the academic nausea without `nausea_stopwords` and for the water content without `stopwords`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

Raises:

- `SourceTypeError` - a word that is not a string.

=== "Code"

    ``` python
    from ests.style_stats import find_nausea_words, is_stopword

    is_stopword("Aquel"), is_stopword("sin"), is_stopword("trigo")
    find_nausea_words(["gato", "y", "gato", "y", "perro"], top_n=1)
    ```

=== "Result"

    ```
    (True, True, False)
    {'gato': 2}
    ```

</div>

<div class="metric-card" markdown>

### Water content { #water }

`water` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

``` {.python .signature}
calc_water(text, stopwords=None)
```

The share of the words without content, in percent: the words of `stopwords`, in any case, or, without the list, the stopwords of `is_stopword`. The norms of Text.ru: up to 15% natural, 15-30% excessive, above 30% high.

$$
100 \cdot \frac{\textrm{Number of water words}}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `stopwords` | `list[str]` / `set[str]` | `None` | Words of water; `is_stopword` if not given |

Raises:

- `SourceTypeError` - words that are not a list of strings, stopwords that are not a list or a set of strings.

!!! warning "The water content of Spanish"
    The norms of Text.ru are set for Russian, which has no articles; a Spanish text has more water by its grammar alone. Compare the water content of texts with each other, not with the norm.

</div>

<div class="metric-card" markdown>

### Spam score { #spam }

`spam` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_spam"

To compute it by lemmas, extract the words with lemmatization. The norms of Text.ru: up to 30% natural, 30-60% SEO-optimized, above 60% spammed.

</div>

<div class="metric-card" markdown>

### Naturalness by Zipf's law { #zipf_naturalness }

`zipf_naturalness` · pr-cy, megaindex
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_zipf_naturalness"

The ideal distribution is that of [Zipf's law](https://en.wikipedia.org/wiki/Zipf%27s_law); the norm of pr-cy and megaindex is at least 50%.

</div>

<div class="metric-card" markdown>

### Verbal nouns { #verbal_nouns }

`verbal_nouns`
{ .metric-meta }

``` {.python .signature}
calc_verbal_nouns(nouns)
```

The share of the nouns derived from a verb among the lemmas of the nouns, in percent; `nan` without nouns. A noun is derived from a verb by its suffix - `-ción`, `-sión`, `-miento`, `-anza`, `-encia`, `-ancia`, `-aje`, `-dura`, `-azgo` (`revisión`, `nombramiento`, `aprendizaje`) - or is one of the nouns whose derivation leaves no suffix behind (`uso`, `pago`, `envío`), as in the split predicates of [`SyntaxStats`](syntax_stats.md). The rule also catches the nouns of other origins with the same endings (`ciencia`, `distancia`). The function takes the lemmas of the tokens tagged `NOUN`, not the words: a noun and a verb form may be spelt alike (`uso`, `viaje`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `nouns` | `list[str]` | - | Lemmas of the nouns |

Raises:

- `SourceTypeError` - nouns that are not a list of strings.

``` {.python .signature}
noun_lemmas(doc)
```

The lemmas of the tokens of a `Doc` tagged `NOUN`. `StyleStats` takes the nouns of a `Doc` the same way, and those of a string from its parse by the pipeline of `nlp` or `get_nlp`, run without the parser and the named entities.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `doc` | `Doc` | - | Doc object |

Raises:

- `SourceTypeError` - a source that is not a `Doc`;
- `SourceError` - a `Doc` without the parts of speech or the lemmas.

=== "Code"

    ``` python
    from ests.style_stats import calc_verbal_nouns, noun_lemmas
    from ests.utils import get_nlp

    calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
    lemmas = noun_lemmas(get_nlp()("Se procedió a la revisión de los proyectos"))
    lemmas, calc_verbal_nouns(lemmas)
    ```

=== "Result"

    ```
    50.0
    (['revisión', 'proyecto'], 50.0)
    ```

</div>

<div class="metric-card" markdown>

### Compound prepositions and clichés { #phrase_density }

`compound_prepositions` · `cliches`
{ .metric-meta }

``` {.python .signature}
calc_phrase_density(text, phrases)
```

The occurrences of the phrases of a list per 100 words, with the contractions and the forms of the verbs of `expand_phrases`. At every position the longest phrase is taken, and the phrases found do not overlap. `StyleStats` counts this way, over the word forms (`forms`), the compound prepositions of `COMPOUND_PREPOSITIONS` (`en el marco de`, `a efectos de`, `en virtud de`) and the clichés of `OFFICIALESE_CLICHES` (`dar cumplimiento`, `proceder a`, `a la mayor brevedad`) or of the parameter `cliches`.

$$
100 \cdot \frac{\textrm{Number of phrases found}}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `phrases` | `list[str]` / `set[str]` | - | Phrases, words separated by spaces |

Raises:

- `SourceTypeError` - words that are not a list of strings, phrases that are not a list or a set of strings.

``` {.python .signature}
expand_phrases(text, phrases)
```

The phrases spelled out in the forms of a text, each with the phrase of the list it spells out. A phrase ending in `a` or `de` also takes the contraction with the article (`a efectos del`, `conforme al`), and a phrase whose first word is an infinitive takes the forms of the text with that lemma (`proceder a` - `procedió a`, `ser de aplicación` - `es de aplicación`). The lemma is the one of simplemma, and a pronominal lemma counts for its verb (`llévese` - `llevar`); the forms simplemma does not lemmatize - some participles (`ha dado`, `ha hecho`) and the imperative `dese` - are given by `IRREGULAR_VERB_FORMS`. The words after the verb rule out the readings as a noun (`el hecho`, `el puesto`). When two phrases spell out the same words, a phrase written so wins over the forms of another (`a efectos del` stays itself next to `a efectos de`), and then the first phrase of a list, or of a set in sorted order.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |
| `phrases` | `list[str]` / `set[str]` | - | Phrases, words separated by spaces |

Raises:

- `SourceTypeError` - words that are not a list of strings, phrases that are not a list or a set of strings.

=== "Code"

    ``` python
    from ests.constants import COMPOUND_PREPOSITIONS
    from ests.style_stats import calc_phrase_density, expand_phrases

    expand_phrases(["se", "procedió", "al", "cierre"], ["proceder a"])
    words = "se procedió a la revisión en el marco del proyecto".split()
    calc_phrase_density(words, COMPOUND_PREPOSITIONS)
    ```

=== "Result"

    ```
    {'proceder a': 'proceder a',
     'proceder al': 'proceder a',
     'procedió a': 'proceder a',
     'procedió al': 'proceder a'}
    10.0
    ```

The compound prepositions (42) and the clichés (74) are the ones the Spanish-language guides to plain language and style manuals of the administrations flag:

| Source | Author | Year |
| :----- | :----- | :--- |
| [Libro de estilo de la Justicia](https://www.rae.es/libro-estilo-justicia/el-lenguaje-jur%C3%ADdico/caracteres-externos/car%C3%A1cter-arcaizante) | RAE, CGPJ | 2017 |
| [Diccionario panhispánico de dudas](https://www.rae.es/dpd/hoy), 2nd ed. | RAE, ASALE | online |
| [Guía panhispánica de lenguaje claro y accesible](https://www.rae.es/sites/default/files/2025-10/Gu%C3%ADa%20panhisp%C3%A1nica%20de%20lenguaje%20claro%20y%20accesible.pdf) | RAE, ASALE | 2024 |
| [Claridad y derecho a comprender](https://www.mjusticia.gob.es/es/AreaTematica/DocumentacionPublicaciones/InstListDownload/Claridad_y_derecho_a_comprender_Comision_para_la_modernizacion_del_lenguaje_juridico.PDF) | Comisión de Modernización del Lenguaje Jurídico | 2011 |
| [Cómo escribir con claridad](https://publications.europa.eu/resource/cellar/725b7eb0-d92e-11e5-8fea-01aa75ed71a1.0007.03/DOC_1) | European Commission | 2015 |
| [Manual del Lenguaje Administrativo](https://www.madrid.es/UnidadesDescentralizadas/Calidad/Publicaciones/Documentaciontecnica/ficherosdocte/ManualLA.pdf) | Ayuntamiento de Madrid | about 2008 |
| [Comunicación Clara. Guía práctica](https://www.madrid.es/UnidadesDescentralizadas/Calidad/LenguajeClaro/ComunicacionClara/Documentos/GuiaPracticaCClara.pdf) | Ayuntamiento de Madrid | 2017 |
| [Guía de Comunicación Clara](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) | Comunidad de Madrid | 2021 |
| [Manual de Lenguaje y Estilo Administrativo](https://www.carm.es/web/integra.servlets.Blob?ARCHIVO=0-2934_Manual+de+lenguaje+y+estilo+administrativo.pdf&TABLA=ARCHIVOS&CAMPOCLAVE=IDARCHIVO&VALORCLAVE=33424&CAMPOIMAGEN=ARCHIVO&IDTIPO=60) | Región de Murcia | 2008 |
| [Manual de Lenguaje Claro](https://www.economia.gob.mx/files/empleo/ManualLenguaje.pdf) | Secretaría de la Función Pública, Mexico | 2007 |
| [Guía de lenguaje claro para servidores públicos](https://colaboracion.dnp.gov.co/CDT/Programa%20Nacional%20del%20Servicio%20al%20Ciudadano/GUIA%20DEL%20LENGUAJE%20CLARO.pdf) | Departamento Nacional de Planeación, Colombia | 2015 |
| [Guía de lenguaje claro](https://colombiacompra.gov.co/wp-content/uploads/2025/05/cce-rec-gi-01_guia_lenguaje_claro_v2_31-12-2024-1.pdf) | Colombia Compra Eficiente | 2024 |
| [Manual de lenguaje claro](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf) | Gobierno de la Ciudad de Buenos Aires | 2024 |
| [Guía para el uso del Lenguaje Claro](https://biblioteca.legislatura.gob.ar/archivos/lenguajeClaro.pdf) | Legislatura de la Ciudad de Buenos Aires | 2024 |
| [Manual de Estilo del Lenguaje para uso de la Administración Pública Provincial](https://www.salta.gob.ar/public/descargas/archivos/ocspdfs/ocs_manual_de_estilo_del_lenguaje_para_la_administracion_publica_provincial.pdf) | Provincia de Salta | about 2007 |

Left out are the forms the guides recommend (`sobre la base de`) or accept (`de acuerdo a`) and the phrases with frequent neutral uses (`en este sentido`), but for `proceder a` and `llevar a cabo`. A few compound prepositions have neutral uses too (`a través de`, `en caso de`, `con respecto a`), so the density of a neutral text is not zero: compare texts with each other.

</div>

<div class="metric-card" markdown>

### Parenthetical expressions { #parentheticals }

`parentheticals`
{ .metric-meta }

``` {.python .signature}
calc_parentheticals(text)
```

The parenthetical expressions of `PARENTHETICALS` (`sin embargo`, `es decir`, `por ejemplo`, `finalmente`) per 100 words: the phrases of the list with their contractions (`expand_phrases`) and, outside them, the one-word expressions of the list. The punctuation is not looked at, so the list holds the expressions set off by commas or standing at the edge of a sentence in most of their occurrences in the [corpus of literature](../datasets/spanishliterature.md), with the series of order (`en primer lugar`, `en segundo lugar`). The adverbs of doubt (`tal vez`, `quizá`), `sobre todo`, `sin duda` and `además` are not in the list.

$$
100 \cdot \frac{\textrm{Number of parenthetical expressions}}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | List of words |

Raises:

- `SourceTypeError` - words that are not a list of strings.

``` {.python .signature}
find_parentheticals(text)
```

The bounds of the parenthetical expressions of `calc_parentheticals` as slices of the list of words, in order. The parameter and the errors are those of `calc_parentheticals`.

``` {.python .signature}
is_parenthetical(word)
```

Whether a word is one of the one-word expressions of `PARENTHETICALS` (`finalmente`, `naturalmente`, `verbigracia`), in any case.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Word |

Raises:

- `SourceTypeError` - a word that is not a string.

=== "Code"

    ``` python
    from ests.style_stats import calc_parentheticals, find_parentheticals, is_parenthetical

    words = ["sin", "embargo", "el", "gato", "finalmente", "duerme"]
    find_parentheticals(words), calc_parentheticals(words)
    is_parenthetical("Finalmente")
    ```

=== "Result"

    ```
    ([(0, 2), (4, 5)], 33.33333333333333)
    True
    ```

</div>

<div class="metric-card" markdown>

### Keyword density { #keyword_density }

`keyword_density(*keywords)` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

--8<-- "stats/style_stats.md:calc_keyword_density"

To compare by lemmas, extract the words with lemmatization and pass lemmas.

=== "Code"

    ``` python
    from ests import StyleStats

    text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
    StyleStats(text).keyword_density("tres tristes", "trigo")
    ```

=== "Result"

    ```
    {'tres tristes': 16.666666666666668, 'trigo': 8.333333333333334}
    ```

</div>

The functions of the core cards check their words too: words and keywords that are not a list of strings, and a `normalize` that cannot be called, raise `SourceTypeError`.

## Methods { #methods }

--8<-- "stats/style_stats.md:StyleStats-keyword_density"

--8<-- "stats/style_stats.md:StyleStats-markers"

A phrase is found with its contractions and the forms of its verb ([`expand_phrases`](#phrase_density)). The verbal nouns need the parts of speech and the lemmas, as their metric does, so a string is parsed by the model and a `Doc` without them raises `SourceError`.

=== "Code"

    ``` python
    ss.markers()
    ```

=== "Result"

    ```
    {'verbal_nouns': ('procedimiento',
                      'referencia',
                      'cumplimiento',
                      'revisión',
                      'documentación',
                      'resolución',
                      'comisión',
                      'notificación'),
     'compound_prepositions': ('en el marco del', 'a efectos de', 'en virtud de'),
     'parentheticals': ('no obstante',),
     'cliches': ('dar cumplimiento',
                 'procedió a',
                 'llevará a cabo',
                 'a la mayor brevedad',
                 'en tiempo y forma')}
    ```

The notice of 56 words has three compound prepositions, five clichés and one parenthetical expression, and almost half of its nouns are derived from a verb. The anaphoric `de la misma`, which the guides also advise against, is not counted.

The other methods - `get_stats`, `to_dataframe`, `print_stats` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the style metrics of esTS have no scales, so `describe` gives `None` for the metrics of `get_stats`. The same notice in plain language:

=== "Code"

    ``` python
    plain = (
        "Hemos revisado los documentos que nos envió, como pide la ley. La comisión ha "
        "decidido su caso y le avisaremos lo antes posible."
    )
    StyleStats(plain).get_stats()
    ss.describe("water"), ss.describe("cliches")
    ```

=== "Result"

    ```
    {'classic_nausea': 1.4142135623730951,
     'academic_nausea': 43.47826086956522,
     'water': 43.47826086956522,
     'spam': 4.3478260869565215,
     'zipf_naturalness': 100.0,
     'verbal_nouns': 25.0,
     'compound_prepositions': 0.0,
     'parentheticals': 0.0,
     'cliches': 0.0}
    (None, None)
    ```

The plain version has no compound prepositions, parenthetical expressions or clichés, and a quarter of its nouns are derived from a verb. The academic nausea says nothing of the style here: neither notice repeats a significant word, so it is ten words over the length of the text, 10/56 and 10/23.
