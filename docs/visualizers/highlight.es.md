# Resaltado del texto

!!! info ""
    **ests.visualizers.highlight()**

## Descripción

Resaltado de los fragmentos del texto que cuentan las estadísticas de la biblioteca, a la manera de los correctores de estilo: oraciones largas, palabras complejas y raras, la pasiva con `ser` y con `se`, construcciones de participio y de gerundio, cadenas de `de`, predicados escindidos, sustantivos deverbales, locuciones prepositivas, clichés, palabras vacías, expresiones parentéticas, conectores y aliteraciones. Una imagen dice de qué están hechos los valores de las métricas mejor que una tabla de números. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

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
| Fónica | `alliteration` | Repeticiones de un sonido consonántico en palabras vecinas, poco probables por las frecuencias de los sonidos del español; la nota da el sonido y las letras que lo escriben | [PhonStats](../stats/phon_stats.md) |

Los grupos se definen en `ests.constants.HIGHLIGHT_LAYER_GROUPS`. Las capas del grupo «Sintaxis» se leen del árbol de dependencias y de los lemas (el auxiliar `ser`, los verbos de apoyo) y necesitan un `Doc` con análisis y lematizador (los modelos `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg`), como [SyntaxStats](../stats/syntax_stats.md); `verbal_nouns` necesita un `Doc` con las categorías gramaticales y los lemas, como los sustantivos deverbales de `StyleStats`. Un `Doc` sin los límites de las oraciones (un pipeline vacío, un pipeline sin analizador) se divide con las reglas de [SentsExtractor](../extractors/sentences.md), como lo divide `BasicStats`. Por defecto se activan las capas de `HIGHLIGHT_DEFAULT_LAYERS` que la fuente permite - oraciones largas, palabras complejas, pasiva, cadenas de `de`, predicados escindidos, clichés; `layers="all"` activa todas las permitidas. Quince capas a la vez se solapan (una locución prepositiva está hecha de palabras vacías, un conector puede ser una expresión parentética), así que elija las que necesite.

Una oración es larga a partir de 30 palabras: ahí ponen el límite las guías españolas de lenguaje claro (la [Comunidad de Madrid](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) y el [Gobierno de la Ciudad de Buenos Aires](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf)), y una palabra es compleja a partir de cuatro sílabas. Con tres, el límite de las fórmulas de legibilidad y de `BasicStats`, la capa marca la mitad de las palabras con contenido de cualquier texto en español (`abuela`, `pequeña`, `camino`), y un relato sencillo parece casi tan pesado como un aviso oficial; `complex_syl_factor=3` muestra las palabras de `n_complex_words`. Los dos límites son parámetros.

!!! note "Nota"
    Una aliteración se busca dentro de una oración como una secuencia de dos palabras vecinas o más con el mismo sonido consonántico en su raíz. Los sonidos son los de la [transcripción](../stats/phon_stats_funcs.md#transcribe), así que `casa` y `queso` repiten k; la raíz es el comienzo común de las transcripciones de la forma y de su lema (`cantaban` - k a n t a, `hacía` - a θ), ya que las terminaciones concuerdan con las palabras vecinas y repiten sus consonantes por la gramática, no por el sonido (`las casas blancas`). La probabilidad de una secuencia con un reparto independiente de los sonidos es el producto sobre sus palabras de la probabilidad de encontrar la consonante entre los sonidos de la raíz, $1 - (1 - f)^n$, donde $f$ es la frecuencia del sonido en el [corpus de literatura](../datasets/spanishliterature.md) y $n$ el número de sonidos de la raíz; una secuencia se resalta cuando la probabilidad queda por debajo de `alliteration_threshold`. En cada posición se comprueban unas veinte consonantes, así que el umbral es estricto: con 0.001 se resalta el 3,4% de las palabras de la prosa del corpus, con 0.002 el 5,8%, con 0.01 el 16%. La repetición de un sonido raro se nota en dos o tres palabras (`deje la abeja`), mientras que la `s` de `los suspiros se escapan` es demasiado frecuente para contar en dos palabras. Las palabras de menos de tres letras (`de`, `la`, `el`) y las palabras vacías (`que`, `los`, `con`, `como`) no cortan ni continúan una secuencia: el modelo del azar no sirve para las palabras funcionales - `que` y `qué`, el 3,8% de las palabras de la prosa, tienen una k con mucha más probabilidad que dos sonidos tomados al azar - y con ellas las repeticiones de la k de `que` y de la l de `los` y `del` llenaban la capa. El índice de aliteración de [PhonStats](../stats/phon_stats.md) mide cómo se agrupan las repeticiones en todo el texto; el resaltado muestra dónde están.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `layers` | list[str]/str | `None` | Capas del resaltado; si no se dan, las capas de `HIGHLIGHT_DEFAULT_LAYERS` que la fuente permite; `"all"` - todas las permitidas |
| `long_sent_word_factor` | int | `30` | Número mínimo de palabras de una oración larga |
| `complex_syl_factor` | int | `4` | Número mínimo de sílabas de una palabra compleja |
| `stopwords` | list[str] | `None` | Lista de palabras vacías; si no se da, `STOPWORDS` y las expresiones parentéticas de una palabra |
| `cliches` | list[str] | `None` | Lista de clichés; si no se da, `OFFICIALESE_CLICHES` |
| `alliteration_threshold` | float | `0.001` | Probabilidad de una repetición de una consonante con un reparto independiente de los sonidos, por debajo de la cual la repetición es aliteración |

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
    # {'long_sents': 1, 'complex_words': 16, 'passive': 2, 'de_chains': 3,
    #  'split_predicates': 2, 'cliches': 1}

    ht.highlights[:2]
    # (Highlight(start=13, end=22, layer='complex_words', note='complex word, 5 syllables'),
    #  Highlight(start=42, end=54, layer='passive', note='passive with ser'))

    # Todas las capas
    highlight(nlp(text), layers="all").counts
    # {'long_sents': 1, 'complex_words': 16, 'rare_words': 0, 'passive': 2,
    #  'participle_clauses': 2, 'gerund_clauses': 1, 'de_chains': 3, 'split_predicates': 2,
    #  'verbal_nouns': 9, 'compound_prepositions': 1, 'cliches': 1, 'stopwords': 48,
    #  'parentheticals': 0, 'connectors': 3, 'alliteration': 0}

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

Una cadena sin modelo de spaCy permite todas las capas salvo las sintácticas y `verbal_nouns`: por defecto, oraciones largas, palabras complejas y clichés, y la aliteración a petición.

!!! example "Ejemplo"

    ``` python
    from ests.visualizers import highlight

    # Antonio Machado, Poesías completas (el corpus de literatura)
    text = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(text, layers="alliteration").highlights
    # (Highlight(start=35, end=78, layer='alliteration', note='alliteration on /b/ (b, v)'),)
    ```

!!! example "Ejemplo"

    ``` python
    from ests.visualizers import highlight

    text = "Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad."
    highlight(text, layers=["compound_prepositions", "cliches"]).highlights
    # (Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»'),
    #  Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»'),
    #  Highlight(start=62, end=81, layer='cliches', note='cliché: «a la mayor brevedad»'))
    ```
