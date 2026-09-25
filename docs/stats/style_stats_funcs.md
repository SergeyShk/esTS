# Metric functions

## Classic nausea { #calc_classic_nausea }

!!! info ""
    **ests.style_stats.calc_classic_nausea()**

The classic nausea of [Advego](https://advego.com/text/seo/) - the square root of the number of occurrences of the most frequent word. It measures how insistent one word is regardless of the length of the text, so it grows with the text. The norm of Advego is at most 7, 1-5 in practice.

Formula:

$$
\sqrt{\max_k n_k}
$$

where $n_k$ is the number of occurrences of the word $k$.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Academic nausea { #calc_academic_nausea }

!!! info ""
    **ests.style_stats.calc_academic_nausea()**

The academic nausea of [Advego](https://advego.com/text/seo/) - the share of the occurrences of the most frequent words of the text in percent. The exact formula of Advego is not published: the summed frequency of the `top_n` most frequent words is divided by the number of words. The norm of Advego is 5-15%.

Formula:

$$
100\times\frac{\sum_{k \in \textrm{top}_n} n_k}{N}
$$

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |

## Water content { #calc_water }

!!! info ""
    **ests.style_stats.calc_water()**

The water content of [Text.ru](https://text.ru/seo) - the share of the words that carry no content in percent: the stopwords of [`is_stopword`](#is_stopword) or of the list passed, in any case. The norms of Text.ru - up to 15% natural, 15-30% excessive, above 30% high - are set for Russian, which has no articles; a Spanish text has more water by its grammar alone, 42-54% in the texts of the corpus of literature.

Formula:

$$
100\times\frac{\textrm{Number of stopwords}}{\textrm{Number of words}}
$$

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `stopwords` | list[str] | `None` | List of stopwords; if not given, `is_stopword` is used |

## Stopword { #is_stopword }

!!! info ""
    **ests.style_stats.is_stopword()**

Checks whether a word is a stopword, in any case. The stopwords are the 265 forms of `ests.constants.STOPWORDS` - the closed classes of the grammar: articles and the other determiners (`este`, `cada`, `mucho`), pronouns (`él`, `cuyo`, `nadie`), prepositions, conjunctions and interjections, with the adverbs that point, relate or ask (`aquí`, `así`, `dónde`) and the ones that negate, affirm or focus (`no`, `solo`, `también`) - and the one-word parenthetical expressions of `PARENTHETICALS` (`finalmente`, `naturalmente`). The forms of the old orthography are kept (`á`, `ó`, `tí`), as the texts of the public domain write them. The stopwords of spaCy for Spanish are not used: that list is made for news and holds content words (`acuerdo`, `dijo`, `verdad`, `grande`).

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `word` | str | `-` | Word |

## Spam score { #calc_spam }

!!! info ""
    **ests.style_stats.calc_spam()**

The spam score of [Text.ru](https://text.ru/seo) - the share of the repeated words of the text in percent: every occurrence of a word but the first is a repetition, so the spam score is $100 \times (1 - TTR)$. To compute it by lemmas, extract the words with lemmatization. The norms of Text.ru: up to 30% natural, 30-60% SEO-optimized, above 60% spammed.

Formula:

$$
100\times\frac{N - V}{N}
$$

where $N$ is the number of words and $V$ the number of distinct words.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |

## Naturalness by Zipf's law { #calc_zipf_naturalness }

!!! info ""
    **ests.style_stats.calc_zipf_naturalness()**

How well the frequencies of the most frequent words agree with the ideal distribution $f_r = f_1 / r$ of [Zipf's law](https://en.wikipedia.org/wiki/Zipf%27s_law), where $f_1$ is the frequency of the most frequent word and $r$ is the rank of a word (pr-cy, megaindex). It is 100 times one minus the mean relative deviation of the frequencies from the ideal ones over the ranks from 2 to $R = \min(top\_n, V, f_1)$: rank 1 matches the ideal by construction, and above the rank $f_1$ the ideal frequency is below one and the deviation of the hapaxes grows without a bound. Negative values are clipped to 0; the norm of the services is at least 50%. It is `nan` when there are no ranks to compare: every word is a hapax, the text has one word type or `top_n` is below 2.

Formula:

$$
\max\left(0,\ 100\times\left(1 - \frac{1}{R-1}\sum_{r=2}^{R}\frac{|f_r - f_1/r|}{f_1/r}\right)\right)
$$

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `top_n` | int | `10` | Number of the most frequent words |

## Keyword density { #calc_keyword_density }

!!! info ""
    **ests.style_stats.calc_keyword_density()**

The frequency of every keyword per 100 words of the text ([Text.ru](https://text.ru/seo)). A keyword of several words separated by spaces is looked for as a sequence of words, and its occurrences may overlap. The words are compared in any case; to compare by lemmas, extract the words with lemmatization and pass lemmas.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `keywords` | list[str] | `-` | Keywords or phrases |

## Verbal nouns { #calc_verbal_nouns }

!!! info ""
    **ests.style_stats.calc_verbal_nouns()**

The share of the nouns derived from a verb among the lemmas of the nouns of a text in percent, `nan` for a text without nouns. A noun is derived from a verb by its suffix - `-ción`, `-sión`, `-miento`, `-anza`, `-encia`, `-ancia`, `-aje`, `-dura`, `-azgo` (`revisión`, `nombramiento`, `aprendizaje`) - or is one of the nouns whose derivation leaves no suffix behind (`uso`, `pago`, `envío`), as in the split predicates of [`SyntaxStats`](syntax_stats.md). The rule catches the nouns of other origins with the same endings (`ciencia`, `distancia`), as any suffix rule does. Spanish tells a noun from a verb form by the annotation only (`uso`, `viaje`, `dura`), so the function takes the lemmas of the tokens tagged `NOUN`, not the words.

!!! example "Example"

    ``` python
    from ests.style_stats import calc_verbal_nouns

    calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
    # 50.0
    ```

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nouns` | list[str] | `-` | Lemmas of the nouns |

## Phrase density { #calc_phrase_density }

!!! info ""
    **ests.style_stats.calc_phrase_density()**, **ests.style_stats.expand_phrases()**

The number of occurrences of the phrases of a list per 100 words - the compound prepositions (`COMPOUND_PREPOSITIONS`), the parenthetical expressions (`PARENTHETICALS`) and the clichés (`OFFICIALESE_CLICHES`). At every position the longest phrase is taken, and the phrases found do not overlap. `expand_phrases` spells the phrases out in the forms of the text: a phrase ending in `a` or `de` also takes the contraction with the article (`a efectos del`, `conforme al`), and a phrase whose first word is an infinitive takes the forms of the text with that lemma (`proceder a` - `procedió a`, `ser de aplicación` - `es de aplicación`). The lemma is the one of simplemma, and a pronominal lemma counts for its verb (`llévese`, `llevarse` - `llevarse` - `llevar`); the forms simplemma leaves as they are - the irregular participles of the perfect (`ha dado`, `ha hecho`, `ha puesto`) and the imperative `dese` - are given by `IRREGULAR_VERB_FORMS`. The words after the verb rule out the readings as a noun (`el hecho`, `el puesto`).

The compound prepositions (42) and the clichés (74) are the ones the Spanish guides to plain language and style manuals of the administrations flag:

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

Left out are the forms the guides themselves recommend (`sobre la base de`, `con base en`) or accept (`de acuerdo a`, `de cara a`), and the phrases with frequent neutral uses (`tomar una decisión`, `en este sentido`), but for `proceder a` and `llevar a cabo`, which the guides of three administrations and more flag. A few compound prepositions have neutral uses too (`a través de`, `en caso de`, `con respecto a`), so the density of a neutral text is not zero: compare texts with each other.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
| `phrases` | list[str] | `-` | Phrases, words separated by spaces |

## Parenthetical expressions { #calc_parentheticals }

!!! info ""
    **ests.style_stats.calc_parentheticals()**, **ests.style_stats.is_parenthetical()**

The parenthetical expressions of `PARENTHETICALS` (`sin embargo`, `es decir`, `por ejemplo`, `finalmente`) per 100 words; `is_parenthetical` checks a word against the one-word expressions of the list. The punctuation is not looked at, so the list holds the expressions that stand apart in most of their occurrences: the 55 set off by commas or standing at the edge of a sentence in at least 55% of their occurrences in the [corpus of literature](../datasets/spanishliterature.md), with the series of order the first of them opens (`en primer lugar`, `en segundo lugar`). The adverbs of doubt stay out, as Spanish rarely sets them off (`tal vez` 8%, `quizá` 10%), and so do `sobre todo` (32%), `sin duda` (28%) and `además` (53%), which take a complement or join a sentence without commas.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `text` | list[str] | `-` | List of words |
