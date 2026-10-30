# Resaltado del texto

``` {.python .signature}
HighlightedText(source, layers=None, long_sent_word_factor=30, complex_syl_factor=4, stopwords=None, cliches=None, alliteration_threshold=0.001)
```

<!-- core: visualizers/highlight.md:HighlightedText f056ba1 -->
Resaltado de un texto por capas, a la manera de los correctores de estilo: cada capa marca los fragmentos de un texto que cuenta una estadística - las oraciones largas, las palabras complejas, la pasiva. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy). El resultado se muestra en Jupyter como HTML con estilos y una leyenda; `to_html` devuelve el marcado, y `highlights` guarda los fragmentos para una representación propia. Los fragmentos de capas distintas pueden solaparse.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`;
- `SourceError` - una fuente sin palabras;
- `ParameterError` - unas capas que no son un nombre ni una lista de nombres, una capa desconocida o una que necesita una anotación que le falta a la fuente.

``` {.python .signature}
highlight(source, layers=None, long_sent_word_factor=30, complex_syl_factor=4, stopwords=None, cliches=None, alliteration_threshold=0.001)
```

La función `highlight` devuelve un objeto `HighlightedText` de esTS con las capas de las estadísticas de la biblioteca:

| Grupo | Capa | Qué marca | Estadística |
| :---- | :--- | :-------- | :---------- |
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
| | `anaphoric_mismo` | El `el mismo` anafórico con su artículo (`se archivó el mismo`, `la duración del mismo`) | - |
| Estilo | `stopwords` | Palabras vacías de `STOPWORDS` o del parámetro `stopwords`, el agua del texto | [StyleStats](../stats/style_stats.md) |
| | `parentheticals` | Expresiones parentéticas | [StyleStats](../stats/style_stats.md) |
| | `connectors` | Marcadores del discurso, con la clase y el tipo en la nota | [CohesionStats](../stats/cohesion_stats.md) |
| Fónica | `alliteration` | Repeticiones de un sonido consonántico en palabras vecinas, poco probables por las frecuencias de los sonidos del español; la nota da el sonido y las letras que lo escriben | [PhonStats](../stats/phon_stats.md) |

Los grupos se definen en `ests.constants.HIGHLIGHT_LAYER_GROUPS`. Las capas del grupo «Sintaxis» necesitan un `Doc` con análisis de dependencias y lemas (los modelos `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg`), como [SyntaxStats](../stats/syntax_stats.md); `verbal_nouns` necesita un `Doc` con las categorías gramaticales y los lemas, y `anaphoric_mismo`, uno con el análisis de dependencias, las categorías gramaticales y los lemas. Por defecto se activan las capas de `HIGHLIGHT_DEFAULT_LAYERS` que la fuente permite - oraciones largas, palabras complejas, pasiva, cadenas de `de`, predicados escindidos, clichés; `layers="all"` activa todas las permitidas. Las capas se solapan (una locución prepositiva está hecha de palabras vacías), así que elija las que necesite.

Una oración es larga a partir de 30 palabras, el límite de las guías de lenguaje claro en español (la [Comunidad de Madrid](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) y el [Gobierno de la Ciudad de Buenos Aires](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf)), y una palabra es compleja a partir de cuatro sílabas; `complex_syl_factor=3`, el límite de `BasicStats`, muestra las palabras de `n_complex_words`.

!!! note "Aliteración"
    Una aliteración se busca dentro de una oración como una secuencia de dos palabras vecinas o más con el mismo sonido consonántico en su raíz. Los sonidos son los de la [transcripción](../stats/phon_stats.md#transcribe), así que `casa` y `queso` repiten k; la raíz es el comienzo común de las transcripciones de la forma y de su lema (`cantaban` - k a n t a), lo que deja fuera las terminaciones que se repiten por la concordancia (`las casas blancas`). La probabilidad de una secuencia con un reparto independiente de los sonidos es el producto sobre sus palabras de la probabilidad de encontrar la consonante entre los sonidos de la raíz, $1 - (1 - f)^n$, donde $f$ es la frecuencia del sonido en el [corpus de literatura](../datasets/spanishliterature.md) y $n$ el número de sonidos de la raíz; una secuencia se resalta cuando la probabilidad queda por debajo de `alliteration_threshold`. La repetición de un sonido raro se nota en dos o tres palabras (`deje la abeja`), mientras que la `s` de `los suspiros se escapan` es demasiado frecuente para contar en dos palabras. Las palabras de menos de tres letras (`de`, `la`, `el`), las palabras vacías (`que`, `los`, `con`) y las palabras sin vocales no cortan ni continúan una secuencia. El índice de aliteración de [PhonStats](../stats/phon_stats.md) mide cómo se agrupan las repeticiones en todo el texto; el resaltado muestra dónde están.

La clase extiende el `HighlightedText` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/visualizers/highlight/) con los ganchos del español de `ests.constants`: las capas con sus nombres en la leyenda son `HIGHLIGHT_LAYERS_DESC`, las capas activadas por defecto `HIGHLIGHT_DEFAULT_LAYERS`, las anotaciones de un `Doc` que necesita una capa `HIGHLIGHT_LAYER_ANNOTATIONS` y los estilos de las capas `HIGHLIGHT_LAYER_STYLES`; el prefijo de las clases CSS es `ests`. Las palabras de una cadena son las de [`WordsExtractor`](../extractors/words.md), sin la puntuación, y sus oraciones las de [`SentsExtractor`](../extractors/sentences.md); un `Doc` sin los límites de las oraciones (un pipeline vacío, un pipeline sin analizador) también se divide en oraciones con las reglas de `SentsExtractor`. Una cadena con un carácter sin forma UTF-8 lanza `SourceError` desde el tokenizador del español. Los fragmentos de cada capa los encuentran las [funciones de búsqueda de esTS](#finders).

=== "Código"

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
    ht = highlight(nlp(text))
    ht.counts
    ht.highlights[:2]
    highlight(nlp(text), layers="all").counts
    ```

=== "Resultado"

    ```
    {'long_sents': 1,
     'complex_words': 16,
     'passive': 2,
     'de_chains': 3,
     'split_predicates': 2,
     'cliches': 1}
    (Highlight(start=13, end=22, layer='complex_words', note='complex word, 5 syllables'),
     Highlight(start=42, end=54, layer='passive', note='passive with ser'))
    {'long_sents': 1,
     'complex_words': 16,
     'rare_words': 0,
     'passive': 2,
     'participle_clauses': 2,
     'gerund_clauses': 1,
     'de_chains': 3,
     'split_predicates': 2,
     'verbal_nouns': 9,
     'compound_prepositions': 1,
     'cliches': 1,
     'anaphoric_mismo': 0,
     'stopwords': 48,
     'parentheticals': 0,
     'connectors': 3,
     'alliteration': 0}
    ```

En Jupyter el objeto `ht` se muestra así (pase el cursor sobre un fragmento para ver su nota):

<div class="ests-highlight"><style>.ests-highlight { line-height: 1.7; }
.ests-highlight-legend { display: flex; flex-wrap: wrap; gap: 0.4em 1.2em; margin-bottom: 0.8em; font-size: 0.9em; }
.ests-highlight-legend .ests-hl { padding: 0 0.3em; }
.ests-highlight-count { opacity: 0.6; margin-left: 0.3em; }
.ests-highlight-text { white-space: pre-wrap; }
.ests-highlight .ests-hl.ests-hl-long_sents, .ests-highlight .ests-hl.ests-hl-stopwords, .ests-highlight .ests-hl.ests-hl-complex_words, .ests-highlight .ests-hl.ests-hl-rare_words, .ests-highlight .ests-hl.ests-hl-passive, .ests-highlight .ests-hl.ests-hl-verbal_nouns, .ests-highlight .ests-hl.ests-hl-compound_prepositions, .ests-highlight .ests-hl.ests-hl-cliches, .ests-highlight .ests-hl.ests-hl-parentheticals { color: #1f2328; border-radius: 2px; }
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

=== "Código"

    ``` python
    from ests.visualizers import highlight

    # Antonio Machado, Poesías completas (el corpus de literatura)
    poem = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(poem, layers="alliteration").highlights
    text = "Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad."
    highlight(text, layers=["compound_prepositions", "cliches"]).highlights
    ```

=== "Resultado"

    ```
    (Highlight(start=35, end=78, layer='alliteration', note='alliteration on /b/ (b, v)'),)
    (Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»'),
     Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»'),
     Highlight(start=62, end=81, layer='cliches', note='cliché: «a la mayor brevedad»'))
    ```

## Parámetros

<!-- core: visualizers/highlight.md:HighlightedText-parameters da96774 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos (una cadena o un objeto Doc) |
| `layers` | `list[str]` / `str` | `None` | Capas del resaltado; si no se dan, las capas por defecto que la fuente permite; `"all"` - todas las permitidas |

Los parámetros de las capas de esTS:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `long_sent_word_factor` | `int` | `30` | Número mínimo de palabras de una oración larga |
| `complex_syl_factor` | `int` | `4` | Número mínimo de sílabas de una palabra compleja |
| `stopwords` | `list[str]` / `set[str]` | `None` | Lista o conjunto de palabras vacías; si no se da, `STOPWORDS` y las expresiones parentéticas de una palabra |
| `cliches` | `list[str]` / `set[str]` | `None` | Lista o conjunto de clichés; si no se da, `OFFICIALESE_CLICHES` |
| `alliteration_threshold` | `float` | `0.001` | Probabilidad de una repetición de una consonante con un reparto independiente de los sonidos, por debajo de la cual la repetición es aliteración |

Un número de palabras o de sílabas que no es un entero de al menos uno o un umbral fuera de (0, 1] lanza `ParameterError`, unas palabras vacías o unos clichés que no son una lista o un conjunto de cadenas `SourceTypeError`.

## Atributos

<!-- core: visualizers/highlight.md:HighlightedText-attributes 78a8c2b -->
| Atributo | Tipo | Descripción |
| :-------- | :--- | :---------- |
| `text` | `str` | Texto de la fuente de datos |
| `layers` | `tuple[str]` | Capas activadas, en el orden de dibujo |
| `highlights` | `tuple[Highlight]` | Fragmentos resaltados, ordenados por su inicio y luego por su final descendente |
| `counts` | `dict[str, int]` | Número de fragmentos de cada capa |

<!-- core: visualizers/highlight.md:Highlight cfcf714 -->
``` {.python .signature}
Highlight(start, end, layer, note='')
```

Un fragmento del resaltado: un objeto inmutable con los parámetros como campos.

| Campo | Tipo | Por defecto | Descripción |
| :---- | :--- | :------ | :---------- |
| `start` | `int` | - | Posición del primer carácter del fragmento en el texto |
| `end` | `int` | - | Posición siguiente al último carácter del fragmento |
| `layer` | `str` | - | Capa del resaltado |
| `note` | `str` | `''` | Explicación del fragmento para la ventana emergente |

Las notas de esTS están en inglés: dan el número de palabras de la oración o de la construcción, de sílabas de la palabra, la longitud de la cadena, la expresión de la lista, la clase y el tipo del conector, el sonido de la aliteración y sus letras.

## Métodos

<!-- core: visualizers/highlight.md:HighlightedText-to_html 1693b8b -->
`to_html(legend=True, css=True)` devuelve el marcado HTML del texto resaltado: un `div` de la clase `<prefix>-highlight` con la leyenda, sus recuentos y el texto, donde un segmento resaltado es un `span` de las clases `<prefix>-hl` y `<prefix>-hl-<layer>` con las notas en su `title`; `<prefix>` es `css_prefix`. Los fragmentos solapados de capas distintas dan segmentos con varias clases, en el orden de dibujo. Los saltos de línea (`\n`, `\r\n`, `\r`) se convierten en referencias de caracteres, una por salto, así que el marcado puede ir en Markdown.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `legend` | `bool` | `True` | Añadir la leyenda con los recuentos de los fragmentos |
| `css` | `bool` | `True` | Añadir los estilos de las capas |

<!-- core: visualizers/highlight.md:HighlightedText-css 42034ba -->
El método de clase `css()` devuelve los estilos que añade `to_html`: el contenedor, la leyenda y el texto con las clases de `css_prefix`, las declaraciones de `layer_styles` de cada capa y un color oscuro del texto en las capas con fondo.

=== "Código"

    ``` python
    from ests.visualizers import highlight

    poem = "El cierzo corre por el campo yerto alborotando en blancos torbellinos la nieve silenciosa."
    highlight(poem, layers="alliteration").to_html(legend=False, css=False)
    ```

=== "Resultado"

    ```
    '<div class="ests-highlight"><div class="ests-highlight-text">El cierzo corre por el campo yerto <span class="ests-hl ests-hl-alliteration" title="alliteration on /b/ (b, v)">alborotando en blancos torbellinos la nieve</span> silenciosa.</div></div>'
    ```

## Auxiliares de las capas

Las palabras y las oraciones que toman las funciones de búsqueda de las capas; los auxiliares están en `ests.visualizers.highlight`.

<!-- core: visualizers/highlight.md:Word b88a554 -->
``` {.python .signature}
Word(start, end, text, pos=None, lemma=None)
```

Una palabra con su posición en el texto y, cuando se conocen, su categoría gramatical y su lema.

<!-- core: visualizers/highlight.md:Sent 2381bd5 -->
``` {.python .signature}
Sent(start, end, n_words)
```

Una oración con su posición y su número de palabras.

<!-- core: visualizers/highlight.md:group_words_by_sents 5d947e5 -->
``` {.python .signature}
group_words_by_sents(words, sents)
```

Las palabras de cada oración; las palabras fuera de las oraciones se omiten.

## Búsqueda de las capas { #finders }

Los fragmentos de cada capa los encuentra una función de `ests.visualizers.highlight` que devuelve una lista de `Highlight`: a partir de las palabras y las oraciones del texto, o del `Doc` para las capas sintácticas (`SYNTAX_FINDERS` las da por capa). Todas salvo la pasiva, las construcciones de participio y de gerundio, las cadenas de `de` y el `el mismo` anafórico son las [funciones de búsqueda del núcleo](https://sergeyshk.github.io/anyTS/visualizers/highlight/#finders) con los ganchos del español.

### Oraciones largas y palabras complejas { #long-sents }

``` {.python .signature}
find_long_sents(sents, long_sent_word_factor)
```

La capa `long_sents`: las oraciones de `long_sent_word_factor` palabras o más, con su número de palabras en la nota.

``` {.python .signature}
find_complex_words(words, complex_syl_factor)
```

La capa `complex_words`: las palabras de `complex_syl_factor` sílabas o más según [`count_syllables`](../syllables.md#count_syllables), con su número de sílabas en la nota.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `sents` | `list[Sent]` | - | Oraciones con sus posiciones y sus números de palabras |
| `long_sent_word_factor` | `int` | - | Número mínimo de palabras de una oración larga |
| `words` | `list[Word]` | - | Palabras con sus posiciones |
| `complex_syl_factor` | `int` | - | Número mínimo de sílabas de una palabra compleja |

Excepciones:

- `ParameterError` - un número de palabras o de sílabas que no es un entero de al menos uno.

=== "Código"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Sent, Word, find_complex_words, find_long_sents

    text = "El felinólogo examinó al gato. Lo devolvieron."
    words = [Word(*word) for word in iter_text_words(text)]
    find_long_sents([Sent(0, 30, 5), Sent(31, 46, 2)], 5)
    find_complex_words(words, 4)
    ```

=== "Resultado"

    ```
    [Highlight(start=0, end=30, layer='long_sents', note='long sentence, 5 words')]
    [Highlight(start=3, end=13, layer='complex_words', note='complex word, 5 syllables'),
     Highlight(start=14, end=21, layer='complex_words', note='complex word, 4 syllables'),
     Highlight(start=34, end=45, layer='complex_words', note='complex word, 4 syllables')]
    ```

### Palabras sueltas { #single-words }

``` {.python .signature}
find_rare_words(words)
```

La capa `rare_words`: las palabras cuya clave ([`lemma_key`](../datasets/freqdict.md#lemma_key)) queda fuera de los 10 000 lemas más frecuentes ([`get_rank`](../stats/lexical_stats.md#bands)), como las cuenta `p_beyond_top10000` de `LexicalStats`; una palabra etiquetada `PROPN` conserva su forma. Solo se miran las palabras de dos letras españolas o más que no son palabras vacías.

``` {.python .signature}
find_stopwords(words, stopwords=None)
```

La capa `stopwords`: las palabras de `stopwords` sin distinguir mayúsculas y minúsculas o, sin la lista, las palabras vacías de [`is_stopword`](../stats/style_stats.md#academic_nausea).

``` {.python .signature}
find_verbal_nouns(words)
```

La capa `verbal_nouns`: las palabras etiquetadas `NOUN` cuyo lema deriva de un verbo, como en los [sustantivos deverbales](../stats/style_stats.md#verbal_nouns) de `StyleStats`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Palabras con sus posiciones; con sus categorías gramaticales y sus lemas para `find_verbal_nouns` |
| `stopwords` | `list[str]` / `set[str]` | `None` | Lista o conjunto de palabras vacías; `is_stopword` si no se da |

Excepciones:

- `SourceTypeError` - unas palabras vacías que no son una lista o un conjunto de cadenas.

=== "Código"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Word, find_rare_words, find_stopwords

    text = "El felinólogo examinó minuciosamente al gato."
    words = [Word(*word) for word in iter_text_words(text)]
    find_rare_words(words)
    find_stopwords(words)
    ```

=== "Resultado"

    ```
    [Highlight(start=3, end=13, layer='rare_words', note='rare word: beyond the top 10000'),
     Highlight(start=22, end=36, layer='rare_words', note='rare word: beyond the top 10000')]
    [Highlight(start=0, end=2, layer='stopwords', note='stopword'),
     Highlight(start=37, end=39, layer='stopwords', note='stopword')]
    ```

### Expresiones { #phrases }

``` {.python .signature}
find_phrase_highlights(words, phrases, layer, label)
```

Los fragmentos de las expresiones de una lista, buscadas con sus contracciones y las formas de sus verbos ([`expand_phrases`](../stats/style_stats.md#phrase_density)); la nota da la etiqueta y la expresión de la lista (`cliché: «proceder a»`).

``` {.python .signature}
find_compound_prepositions(words)
```

La capa `compound_prepositions`: las expresiones de `COMPOUND_PREPOSITIONS`.

``` {.python .signature}
find_cliches(words, cliches=None)
```

La capa `cliches`: las expresiones de `cliches`, de `OFFICIALESE_CLICHES` si no se da.

``` {.python .signature}
find_parentheticals(words)
```

La capa `parentheticals`: las expresiones de `PARENTHETICALS`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Palabras con sus posiciones |
| `phrases` | `list[str]` / `set[str]` | - | Expresiones, palabras separadas por espacios |
| `layer` | `str` | - | Capa del resaltado |
| `label` | `str` | - | Etiqueta del fragmento en la nota |
| `cliches` | `list[str]` / `set[str]` | `None` | Lista o conjunto de clichés |

Excepciones:

- `SourceTypeError` - unas expresiones o unos clichés que no son una lista o un conjunto de cadenas.

=== "Código"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Word, find_cliches, find_compound_prepositions

    text = "Se procedió a la revisión del expediente en el marco del plan."
    words = [Word(*word) for word in iter_text_words(text)]
    find_cliches(words)
    find_compound_prepositions(words)
    ```

=== "Resultado"

    ```
    [Highlight(start=3, end=13, layer='cliches', note='cliché: «proceder a»')]
    [Highlight(start=41, end=56, layer='compound_prepositions', note='compound preposition: «en el marco de»')]
    ```

### Conectores { #connectors }

``` {.python .signature}
find_connector_highlights(words, sents, text=None, doc=None)
```

La capa `connectors`: los conectores de [`CohesionStats`](../stats/cohesion_stats.md#connectors) dentro de cada oración, encontrados por su buscador [`SpanishConnectorMatcher`](../stats/cohesion_stats.md#ConnectorMatcher), un conector de una palabra comprobado por su categoría gramatical cuando las palabras la tienen; la nota da el conector, su clase y su tipo. Con el texto, las reglas del buscador no leen ninguna palabra a través de un signo de puntuación entre dos palabras, así que `así, que` no es conector; con el `Doc`, ningún conector empieza en un `si` que no abre ninguna condición, como en `CohesionStats` ([`is_connector_blocked`](../stats/cohesion_stats.md#is_connector_blocked): `no sé si vendrá`). `HighlightedText` pasa el texto de su fuente y su `Doc`; en una cadena, que no analiza, solo las reglas del buscador descartan un `si` (`como si fuera`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `words` | `list[Word]` | - | Palabras con sus posiciones y sus categorías gramaticales |
| `sents` | `list[Sent]` | - | Oraciones con sus posiciones |
| `text` | `str` | `None` | Texto de las palabras, para los signos de puntuación entre ellas |
| `doc` | `Doc` | `None` | `Doc` de las palabras, para las reglas por sus tokens |

Excepciones:

- `SourceTypeError` - un texto que no es una cadena.

=== "Código"

    ``` python
    from ests.utils import iter_text_words
    from ests.visualizers.highlight import Sent, Word, find_connector_highlights

    text = "Sin embargo, el plan no se aprobó."
    words = [Word(*word) for word in iter_text_words(text)]
    find_connector_highlights(words, [Sent(0, len(text), len(words))], text)
    ```

=== "Resultado"

    ```
    [Highlight(start=0, end=11, layer='connectors', note='connector «sin embargo»: adversative, secondary')]
    ```

### Aliteración { #alliteration }

``` {.python .signature}
get_stem_sounds(word)
```

Los sonidos de la raíz de una forma: el comienzo común de las [transcripciones](../stats/phon_stats.md#transcribe) de la forma y de su lema (`cantaban` - k a n t a, `cogió` - k o x). Cuando es más corto que dos sonidos, como en las formas supletivas (`fue` - `ser`), la raíz es la forma entera.

``` {.python .signature}
calc_alliteration_runs(text, threshold=0.001)
```

Las secuencias de [`calc_alliteration_runs`](https://sergeyshk.github.io/anyTS/visualizers/highlight/#calc_alliteration_runs) del núcleo sobre las raíces de `get_stem_sounds` y los sonidos consonánticos de `ALLITERATION_FREQUENCIES`, con sus frecuencias de `SOUND_FREQUENCIES`; las palabras de menos de tres letras, las palabras vacías y las palabras sin vocales no cortan ni continúan una secuencia. Una secuencia es una terna del índice de su primera palabra, el índice siguiente a su última palabra y su sonido.

``` {.python .signature}
find_alliteration(words, threshold=0.001, sents=None)
```

La capa `alliteration`: las secuencias de `calc_alliteration_runs` dentro de cada oración, en todo el texto sin las oraciones; la nota da el sonido y las letras que lo escriben (`alliteration on /b/ (b, v)`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `word` | `str` | - | Forma de la palabra en minúsculas |
| `text` | `list[str]` | - | Lista de palabras |
| `threshold` | `float` | `0.001` | Umbral de la probabilidad (`ALLITERATION_THRESHOLD` de `anyts.constants`) |
| `words` | `list[Word]` | - | Palabras con sus posiciones |
| `sents` | `list[Sent]` | `None` | Oraciones con sus posiciones |

Excepciones:

- `SourceTypeError` - una palabra que no es una cadena, unas palabras de `calc_alliteration_runs` que no son una lista de cadenas;
- `ParameterError` - un umbral fuera de (0, 1].

=== "Código"

    ``` python
    from ests.visualizers.highlight import calc_alliteration_runs, get_stem_sounds

    get_stem_sounds("cantaban"), get_stem_sounds("fue")
    calc_alliteration_runs(["deje", "la", "abeja"])
    calc_alliteration_runs(["los", "suspiros", "se", "escapan"])
    ```

=== "Resultado"

    ```
    (('k', 'a', 'n', 't', 'a'), ('f', 'u', 'e'))
    [(0, 3, 'x')]
    []
    ```

### Capas sintácticas { #syntax-layers }

``` {.python .signature}
find_passive(doc)
```

La capa `passive`: cada forma pasiva de [`is_passive`](../stats/syntax_stats.md#passive) con su auxiliar `ser` (`fue construida`) o su `se` (`se construyó`); la nota distingue la pasiva con `se` de la pasiva con `ser` y marca una pasiva con `ser` sin agente (`is_agentless`).

``` {.python .signature}
find_participle_clauses(doc)
```

La capa `participle_clauses`: el subárbol de cada núcleo de una [construcción de participio](../stats/syntax_stats.md#participle_clauses), con su número de palabras en la nota.

``` {.python .signature}
find_gerund_clauses(doc)
```

La capa `gerund_clauses`: el subárbol de cada núcleo de una [construcción de gerundio](../stats/syntax_stats.md#gerund_clauses), con su número de palabras en la nota.

``` {.python .signature}
find_de_chains(doc)
```

La capa `de_chains`: las [cadenas de `de`](../stats/syntax_stats.md#de_chains) de dos complementos o más, un fragmento del núcleo al último complemento (`el aumento de la eficiencia del uso de los recursos`), con la longitud de la cadena en la nota.

``` {.python .signature}
find_split_predicate_highlights(doc)
```

La capa `split_predicates`: los pares de un verbo de apoyo y un sustantivo de [`find_split_predicates`](../stats/syntax_stats.md#constructions), un fragmento de la primera palabra del par a la última (`hacer una revisión`), con sus lemas en la nota.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `doc` | `Doc` | - | Objeto Doc con análisis de dependencias y lemas |

=== "Código"

    ``` python
    from ests.utils import get_nlp
    from ests.visualizers.highlight import (
        find_de_chains,
        find_gerund_clauses,
        find_participle_clauses,
        find_passive,
        find_split_predicate_highlights,
    )

    doc = get_nlp()(
        "El informe, redactado por el comité, fue aprobado tras hacer una revisión, "
        "siguiendo las normas del uso de los recursos."
    )
    find_passive(doc)
    find_participle_clauses(doc)
    find_gerund_clauses(doc)
    find_de_chains(doc)
    find_split_predicate_highlights(doc)
    ```

=== "Resultado"

    ```
    [Highlight(start=37, end=49, layer='passive', note='passive with ser, no agent')]
    [Highlight(start=12, end=35, layer='participle_clauses', note='participial clause, 4 words')]
    [Highlight(start=75, end=119, layer='gerund_clauses', note='gerund clause, 8 words')]
    [Highlight(start=89, end=119, layer='de_chains', note='chain of 2 complements with de')]
    [Highlight(start=55, end=73, layer='split_predicates', note='split predicate: hacer revisión')]
    ```

### El mismo anafórico { #anaphoric-mismo }

``` {.python .signature}
is_anaphoric_mismo(token)
```

Comprueba si una palabra es un `el mismo` anafórico: una forma de `mismo` que encabeza un sintagma nominal propio con su artículo (`el`, `la`, `los`, `las`, `del`, `al`) y sin otro dependiente que una cláusula tras una coma, como argumento de un verbo o de un sustantivo (`se archivó el mismo`, `la duración del mismo`, `contra la misma, que pone fin a la vía administrativa, cabe recurso`). El [Diccionario panhispánico de dudas](https://www.rae.es/dpd/mismo) tiene por innecesario este uso del estilo administrativo y periodístico y propone en su lugar un demostrativo, un posesivo o un pronombre personal (`su duración`, `dentro de ella`). La identidad no es anáfora: `el mismo día`, `es el mismo`, `lo mismo`, `él mismo`, una forma tras `ser`, `estar`, `parecer`, `permanecer` o `resultar`, por el lema del modelo o de simplemma (`no parecía la misma`, `siempre serás el mismo`), justo ante `que` (`el mismo que el año pasado`, mientras que `del mismo, que...` es anafórico) y ante una conjunción y un adjetivo o un determinante que no es un artículo ni un posesivo, que comparten su sustantivo (`de la misma o superior categoría`, `a la misma u otra sede`). Los modelos cuelgan algunas formas anafóricas de su artículo (`en la misma hay oficinas`): esa forma cuenta cuando no la sigue en su oración un sustantivo, un adjetivo, un numeral o un pronombre; un adjetivo en singular sin género cuyo lema de simplemma es un infinitivo es un verbo mal leído por el modelo (`contra la misma cabe recurso`). Un token de un `Doc` sin análisis no lo es. Los espacios y los signos de puntuación no son dependientes de la forma, así que un salto de línea tras ella no cambia nada.

``` {.python .signature}
find_anaphoric_mismo(doc)
```

La capa `anaphoric_mismo`: cada forma de `is_anaphoric_mismo` con su artículo (`la misma`, `del mismo`), las dos palabras en la nota.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `doc` | `Doc` | - | Objeto Doc con análisis de dependencias, categorías gramaticales y lemas |

=== "Código"

    ``` python
    from ests.utils import get_nlp
    from ests.visualizers.highlight import find_anaphoric_mismo, is_anaphoric_mismo

    doc = get_nlp()("Se recibió la solicitud el mismo día, y se procedió al estudio de la misma.")
    [token.text for token in doc if is_anaphoric_mismo(token)]
    find_anaphoric_mismo(doc)
    ```

=== "Resultado"

    ```
    ['misma']
    [Highlight(start=66, end=74, layer='anaphoric_mismo', note='anaphoric la misma')]
    ```
