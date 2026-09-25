# Resaltado del texto

!!! info ""
    **ests.visualizers.highlight()**

## Descripción

Resaltado de los fragmentos del texto que cuentan las estadísticas de la biblioteca, a la manera de los correctores de estilo: oraciones largas, palabras complejas y raras, la pasiva con `ser` y con `se`, construcciones de participio y de gerundio, cadenas de `de`, predicados escindidos, sustantivos deverbales, locuciones prepositivas, clichés, palabras vacías, expresiones parentéticas y conectores. Una imagen dice de qué están hechos los valores de las métricas mejor que una tabla de números. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

La función devuelve un objeto `HighlightedText`, que Jupyter muestra como HTML con estilos y una leyenda; el método `to_html` devuelve el mismo marcado para la documentación y las aplicaciones web. Los fragmentos se guardan en el atributo `highlights` y quedan disponibles para una representación propia.

Capas del resaltado:

| Grupo | Capa | Qué marca | Estadística |
| :---- | :--: | :-------: | :---------: |
| Legibilidad | `long_sents` | Oraciones de `long_sent_word_factor` palabras o más | [BasicStats](../stats/basic_stats.md) |
| | `complex_words` | Palabras de `complex_syl_factor` sílabas o más | [BasicStats](../stats/basic_stats.md) |
| | `rare_words` | Palabras con un lema fuera del top 10000 incorporado; no se resaltan los números, las palabras con guion o con cifras ni las palabras vacías | [LexicalStats](../stats/lexical_stats.md) |
| Sintaxis | `passive` | Formas verbales pasivas con su auxiliar `ser` o su `se`; la nota distingue las dos y marca la pasiva con `ser` sin agente | [SyntaxStats](../stats/syntax_stats.md) |
| | `participle_clauses` | Construcciones de participio | [SyntaxStats](../stats/syntax_stats.md) |
| | `gerund_clauses` | Construcciones de gerundio | [SyntaxStats](../stats/syntax_stats.md) |
| | `de_chains` | Cadenas de complementos con `de` con su núcleo | [SyntaxStats](../stats/syntax_stats.md) |
| | `split_predicates` | Predicados escindidos del verbo al sustantivo | [SyntaxStats](../stats/syntax_stats.md) |
| Estilo burocrático | `verbal_nouns` | Sustantivos deverbales | [StyleStats](../stats/style_stats.md) |
| | `compound_prepositions` | Locuciones prepositivas de `COMPOUND_PREPOSITIONS` | [StyleStats](../stats/style_stats.md) |
| | `cliches` | Clichés de `OFFICIALESE_CLICHES` o del parámetro `cliches` | [StyleStats](../stats/style_stats.md) |
| Estilo | `stopwords` | Palabras vacías de `STOPWORDS` o de la lista pasada, el agua del texto | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Expresiones parentéticas | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Marcadores del discurso, con la clase y el tipo en la nota | [CohesionStats](../stats/cohesion_stats.md) |

Los grupos se definen en `ests.constants.HIGHLIGHT_LAYER_GROUPS`. Las capas del grupo «Sintaxis» se leen del árbol de dependencias y necesitan un `Doc` con análisis (los modelos `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg`); `verbal_nouns` necesita un `Doc` con las categorías gramaticales y los lemas, como los sustantivos deverbales de `StyleStats`; `long_sents` de un `Doc` necesita los límites de las oraciones. Por defecto se activan las capas de `HIGHLIGHT_DEFAULT_LAYERS` que la fuente permite - oraciones largas, palabras complejas, pasiva, cadenas de `de`, predicados escindidos, clichés; `layers="all"` activa todas las permitidas. Catorce capas a la vez se solapan (una locución prepositiva está hecha de palabras vacías, un conector puede ser una expresión parentética), así que elija las que necesite.

Una oración es larga a partir de 30 palabras: ahí ponen el límite las guías españolas de lenguaje claro (la [Comunidad de Madrid](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) y el [Gobierno de la Ciudad de Buenos Aires](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf)), y una palabra es compleja a partir de tres sílabas, como la cuentan las fórmulas españolas de legibilidad; los dos son parámetros.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `layers` | list[str]/str | `None` | Capas del resaltado; si no se dan, las capas de `HIGHLIGHT_DEFAULT_LAYERS` que la fuente permite; `"all"` - todas las permitidas |
| `long_sent_word_factor` | int | `30` | Número mínimo de palabras de una oración larga |
| `complex_syl_factor` | int | `3` | Número mínimo de sílabas de una palabra compleja |
| `stopwords` | list[str] | `None` | Lista de palabras vacías; si no se da, `STOPWORDS` y las expresiones parentéticas de una palabra |
| `cliches` | list[str] | `None` | Lista de clichés; si no se da, `OFFICIALESE_CLICHES` |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `text` | str | Texto de la fuente de datos |
| `layers` | tuple[str] | Capas activadas, en el orden de dibujo |
| `highlights` | tuple[Highlight] | Fragmentos resaltados en el orden del texto |
| `counts` | dict[str, int] | Número de fragmentos de cada capa |

Un fragmento `Highlight` es un objeto inmutable con los campos `start` y `end` (posiciones en el texto), `layer` (la capa) y `note` (la explicación de la ventana emergente: el número de palabras de la oración, de sílabas de la palabra, la longitud de la cadena, la expresión de la lista).

## Métodos

### to_html

Devuelve el marcado HTML del texto resaltado: un `div` de la clase `ests-highlight` con la leyenda y sus recuentos y el texto, donde los segmentos resaltados van dentro de un `span` de las clases `ests-hl` y `ests-hl-<capa>`, y las notas van al atributo `title`. Los fragmentos solapados de capas distintas dan segmentos con varias clases. Los saltos de línea se guardan como referencias de caracteres, así que el marcado puede insertarse en Markdown.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `legend` | bool | `True` | Añadir la leyenda con los recuentos de los fragmentos |
| `css` | bool | `True` | Añadir los estilos de las capas |

## Ejemplo de uso

!!! example "Ejemplo"

    _Código_:

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

    # Resaltar el texto con las capas por defecto
    ht = highlight(nlp(text))
    ht.counts
    # {'long_sents': 1, 'complex_words': 34, 'passive': 2, 'de_chains': 3,
    #  'split_predicates': 2, 'cliches': 1}

    ht.highlights[:2]
    # (Highlight(start=3, end=11, layer='complex_words', note='complex word, 3 syllables'),
    #  Highlight(start=13, end=22, layer='complex_words', note='complex word, 5 syllables'))

    # Todas las capas
    highlight(nlp(text), layers="all").counts
    # {'long_sents': 1, 'complex_words': 34, 'rare_words': 0, 'passive': 2,
    #  'participle_clauses': 2, 'gerund_clauses': 1, 'de_chains': 3, 'split_predicates': 2,
    #  'verbal_nouns': 9, 'compound_prepositions': 1, 'cliches': 1, 'stopwords': 48,
    #  'parentheticals': 0, 'connectors': 3}

    # Mostrar en Jupyter o guardar el marcado
    ht
    html = ht.to_html()
    ```

_Resultado_ (pase el cursor sobre un fragmento para ver su nota):

<div class="ests-highlight"><style>.ests-highlight { line-height: 1.7; }
.ests-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ests-highlight-legend .ests-hl { padding: 0 0.3em; }
.ests-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ests-highlight-text { white-space: pre-wrap; }
.ests-highlight .ests-hl.ests-hl-long_sents, .ests-highlight .ests-hl.ests-hl-complex_words, .ests-highlight .ests-hl.ests-hl-rare_words, .ests-highlight .ests-hl.ests-hl-stopwords, .ests-highlight .ests-hl.ests-hl-passive, .ests-highlight .ests-hl.ests-hl-verbal_nouns, .ests-highlight .ests-hl.ests-hl-compound_prepositions, .ests-highlight .ests-hl.ests-hl-cliches, .ests-highlight .ests-hl.ests-hl-parentheticals { color: #1f2328; border-radius: 2px; }
.ests-hl-long_sents { background: #fef9c3; }
.ests-hl-complex_words { background: #fed7aa; }
.ests-hl-rare_words { background: #e5e7eb; }
.ests-hl-passive { background: #fecaca; }
.ests-hl-verbal_nouns { background: #e9d5ff; }
.ests-hl-compound_prepositions { background: #a7f3d0; }
.ests-hl-cliches { background: #fbcfe8; }
.ests-hl-stopwords { background: #bae6fd; }
.ests-hl-parentheticals { background: #d9f99d; }
.ests-hl-participle_clauses { border-bottom: 2px solid #7c3aed; }
.ests-hl-gerund_clauses { border-bottom: 2px solid #0d9488; }
.ests-hl-de_chains { border-bottom: 2px solid #b45309; }
.ests-hl-split_predicates { border-bottom: 2px solid #dc2626; }
.ests-hl-connectors { border-bottom: 2px dashed #2563eb; }
</style><div class="ests-highlight-legend"><span><span class="ests-hl ests-hl-long_sents">Long sentences</span><span class="ests-highlight-count">1</span></span><span><span class="ests-hl ests-hl-complex_words">Complex words</span><span class="ests-highlight-count">34</span></span><span><span class="ests-hl ests-hl-passive">Passive</span><span class="ests-highlight-count">2</span></span><span><span class="ests-hl ests-hl-de_chains">Chains of de</span><span class="ests-highlight-count">3</span></span><span><span class="ests-hl ests-hl-split_predicates">Split predicates</span><span class="ests-highlight-count">2</span></span><span><span class="ests-hl ests-hl-cliches">Clichés</span><span class="ests-highlight-count">1</span></span></div><div class="ests-highlight-text">El <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">proyecto</span>, <span class="ests-hl ests-hl-complex_words" title="complex word, 5 syllables">elaborado</span> <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">durante</span> el <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">verano</span>, <span class="ests-hl ests-hl-passive" title="passive with ser">fue </span><span class="ests-hl ests-hl-complex_words ests-hl-passive" title="complex word, 4 syllables; passive with ser">aprobado</span> por el <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">consejo</span> sin <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">debate</span>. El <span class="ests-hl ests-hl-complex_words ests-hl-de_chains" title="complex word, 3 syllables; chain of 3 complements with de">aumento</span><span class="ests-hl ests-hl-de_chains" title="chain of 3 complements with de"> de la </span><span class="ests-hl ests-hl-complex_words ests-hl-de_chains" title="complex word, 4 syllables; chain of 3 complements with de">eficiencia</span><span class="ests-hl ests-hl-de_chains" title="chain of 3 complements with de"> del uso de los </span><span class="ests-hl ests-hl-complex_words ests-hl-de_chains" title="complex word, 3 syllables; chain of 3 complements with de">recursos</span> <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">públicos</span> <span class="ests-hl ests-hl-passive" title="passive with se">se </span><span class="ests-hl ests-hl-complex_words ests-hl-passive" title="complex word, 4 syllables; passive with se">analizó</span>, <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">siguiendo</span> las normas del <span class="ests-hl ests-hl-complex_words" title="complex word, 4 syllables">reglamento</span>. <span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">Los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 5 syllables">representantes</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> de los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">ministerios</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">regionales</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> no </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">consiguieron</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> </span><span class="ests-hl ests-hl-long_sents ests-hl-split_predicates" title="long sentence, 40 words; split predicate: hacer revisión">hacer una </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains ests-hl-split_predicates" title="long sentence, 40 words; complex word, 3 syllables; chain of 2 complements with de; split predicate: hacer revisión">revisión</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 3 syllables; chain of 2 complements with de">conjunta</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> de las </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 3 syllables; chain of 2 complements with de">cuestiones</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> de </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 4 syllables; chain of 2 complements with de">financiación</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> y de </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 3 syllables">reparto</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> de </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 7 syllables">responsabilidades</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> entre los </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">organismos</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">, puesto que cada uno de ellos </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words" title="long sentence, 40 words; complex word, 4 syllables">defendía</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words"> su propia </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 5 syllables; chain of 2 complements with de">interpretación</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> de las </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 5 syllables; chain of 2 complements with de">disposiciones</span><span class="ests-hl ests-hl-long_sents ests-hl-de_chains" title="long sentence, 40 words; chain of 2 complements with de"> del </span><span class="ests-hl ests-hl-long_sents ests-hl-complex_words ests-hl-de_chains" title="long sentence, 40 words; complex word, 3 syllables; chain of 2 complements with de">acuerdo</span><span class="ests-hl ests-hl-long_sents" title="long sentence, 40 words">.</span> En el marco de la reunión se <span class="ests-hl ests-hl-complex_words ests-hl-split_predicates ests-hl-cliches" title="complex word, 3 syllables; split predicate: proceder votación; cliché: «proceder a»">procedió</span><span class="ests-hl ests-hl-split_predicates ests-hl-cliches" title="split predicate: proceder votación; cliché: «proceder a»"> a</span><span class="ests-hl ests-hl-split_predicates" title="split predicate: proceder votación"> la </span><span class="ests-hl ests-hl-complex_words ests-hl-split_predicates" title="complex word, 3 syllables; split predicate: proceder votación">votación</span>, y la <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">decisión</span> quedó <span class="ests-hl ests-hl-complex_words" title="complex word, 4 syllables">aplazada</span> hasta la <span class="ests-hl ests-hl-complex_words" title="complex word, 3 syllables">próxima</span> sesión.</div></div>

Una cadena sin modelo de spaCy permite todas las capas salvo las sintácticas y `verbal_nouns`: por defecto, oraciones largas, palabras complejas y clichés.

!!! example "Ejemplo"

    ``` python
    from ests.visualizers import highlight

    text = "Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad."
    highlight(text, layers=["compound_prepositions", "cliches"]).highlights
    # (Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»'),
    #  Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»'),
    #  Highlight(start=62, end=81, layer='cliches', note='cliché: «a la mayor brevedad»'))
    ```
