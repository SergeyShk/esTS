# Componentes

``` {.python .signature}
StatsComponent(nlp, name)
```

<!-- core: components.md:StatsComponent d49cea9 -->
La base de los componentes de [spaCy](https://github.com/explosion/spaCy) que ponen las estadísticas de un texto en una extensión de `Doc`: un componente registra la extensión al añadirse a un pipeline y pone las estadísticas de cada documento en `doc._.<name>`. La escritura de componentes en general se describe en la [documentación de spaCy](https://spacy.io/usage/processing-pipelines#custom-components).

Los componentes de esTS son subclases del `StatsComponent` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/components/), una por cada clase de estadísticas.

!!! note "Nota"
    Los ejemplos de abajo usan el modelo `es_core_news_sm`, que se instala aparte: `python -m spacy download es_core_news_sm` (véase [instalación](installation.md)).

=== "Código"

    ``` python
    import ests
    import spacy

    nlp = spacy.load("es_core_news_sm")
    nlp.add_pipe("ests_basic", name="basic")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.basic.n_words, doc._.basic.c_letters
    nlp("?!")._.basic is None
    ```

=== "Resultado"

    ```
    (12, {2: 5, 3: 1, 4: 1, 5: 1, 6: 3, 7: 1})
    True
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `nlp` | `Language` | - | Pipeline al que se añade el componente |
| `name` | `str` | - | Nombre del componente en el pipeline y de la extensión |

spaCy fija ambos en `nlp.add_pipe(factory, name=...)`; los demás parámetros de un componente se pasan en el diccionario `config` de la misma llamada.

## Nombres { #names }

Las fábricas llevan el prefijo de la biblioteca: `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style`, `ests_phon`, `ests_verse`, y el componente de los límites de oración [`ests_blank_lines`](#blank_lines). Están declaradas como entry points de `spacy_factories`, así que un pipeline guardado con estos componentes (`nlp.to_disk(path)`, `spacy package`) se carga con `spacy.load(path)` sin importar la biblioteca. `import ests` no carga los componentes mientras spaCy no está cargado - los hallan los puntos de entrada, y `ests.StyleStatsComponent` los carga al usarlo por primera vez; desde las fuentes sin el paquete instalado, `import ests.components` va antes de `add_pipe`.

<!-- core: components.md:StatsComponent-names 33ebb87 -->
El nombre del paso del pipeline es el nombre de la extensión: `nlp.add_pipe(factory, name="basic")` pone las estadísticas en `doc._.basic`. Sin `name` ambos toman el nombre de la fábrica. La extensión sigue al paso cuando el pipeline lo renombra (`nlp.rename_pipe`). Un nombre ocupado por una extensión de otro paquete lanza `ParameterError` en lugar de reemplazarla: en `add_pipe`, o con el primer documento después de `rename_pipe`, que renombra el paso antes de que el componente conozca su nombre. Un componente tomado de otro pipeline (`add_pipe(name, source=other)`) es el mismo objeto en ambos, así que con un nombre nuevo escribe también en esa extensión del otro pipeline; un componente independiente sale de la fábrica, `add_pipe(factory, name=...)`. El mismo componente puede añadirse dos veces con nombres distintos, con parámetros distintos. Un documento sin palabras - una cadena vacía, espacios, pura puntuación - pasa por un componente sin cambios, con su extensión en `None`.

En `ests_lexical` también pasa intacto un documento solo de números, y en `ests_verse` un documento sin letras.

<!-- core: components.md:StatsComponent-serialization a238412 -->
!!! warning "Serialización"
    Un componente guarda un objeto de estadísticas en `doc._.<name>`, y spaCy no sabe serializarlo: `Doc.to_bytes()`, `DocBin(store_user_data=True)` y `nlp.pipe(..., n_process>1)` fallan con estos componentes en el pipeline. Para guardar un documento, deje fuera los datos de usuario (`doc.to_bytes(exclude=["user_data"])`) o guarde `doc._.<name>.get_stats()` por separado; para el multiproceso, calcule las estadísticas en el proceso principal después de `nlp.pipe`, sin los componentes.

Añadir un componente amplía el tokenizador de su pipeline con las reglas de las rayas de un diálogo pegadas a las palabras y de las abreviaturas en cualquier caja ([`add_dash_rules`](extractors/words.md)), como en la API de cadenas: `sí--dijo` son dos palabras y una raya, `SR.` una palabra. Un tokenizador que no es el `Tokenizer` de spaCy se queda como está.

## Componentes de las clases de estadísticas { #class-components }

| Componente | Fábrica | Clase de estadísticas | Parámetros |
| :--------- | :------ | :-------------------- | :--------- |
| [`BasicStatsComponent`](#BasicStatsComponent) | `ests_basic` | [`BasicStats`](stats/basic_stats.md) | - |
| [`ReadabilityStatsComponent`](#ReadabilityStatsComponent) | `ests_readability` | [`ReadabilityStats`](stats/readability_stats.md) | `preset`, `basic` |
| [`DiversityStatsComponent`](#DiversityStatsComponent) | `ests_diversity` | [`DiversityStats`](stats/diversity_stats.md) | `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` |
| [`MorphStatsComponent`](#MorphStatsComponent) | `ests_morph` | [`MorphStats`](stats/morph_stats.md) | - |
| [`SyntaxStatsComponent`](#SyntaxStatsComponent) | `ests_syntax` | [`SyntaxStats`](stats/syntax_stats.md) | - |
| [`CohesionStatsComponent`](#CohesionStatsComponent) | `ests_cohesion` | [`CohesionStats`](stats/cohesion_stats.md) | - |
| [`LexicalStatsComponent`](#LexicalStatsComponent) | `ests_lexical` | [`LexicalStats`](stats/lexical_stats.md) | `data_dir` |
| [`StyleStatsComponent`](#StyleStatsComponent) | `ests_style` | [`StyleStats`](stats/style_stats.md) | `stopwords`, `top_n`, `nausea_stopwords`, `cliches` |
| [`PhonStatsComponent`](#PhonStatsComponent) | `ests_phon` | [`PhonStats`](stats/phon_stats.md) | `window_len` |
| [`VerseStatsComponent`](#VerseStatsComponent) | `ests_verse` | [`VerseStats`](stats/verse_stats.md) | `seseo` |

Las estadísticas básicas, de legibilidad, de diversidad, fonéticas y del verso no necesitan ninguna anotación de un modelo. En el pipeline de `es_core_news_sm` las categorías gramaticales vienen del `morphologizer` (o de un `tagger` con un `attribute_ruler`; un `tagger` solo no las da), el análisis del `parser` y los lemas del `lemmatizer`. Un componente al que le falta la anotación, también con componentes `excluded`, lanza `SourceError` cuando el documento pasa por él; `ests_lexical` solo necesita las categorías gramaticales, y `ests_style` lanza el error cuando se lee `verbal_nouns` o `markers()`.

### Estadísticas básicas { #BasicStatsComponent }

``` {.python .signature}
BasicStatsComponent(nlp, name)
```

<!-- core: components.md:BasicStatsComponent 7b037d9 -->
`BasicStatsComponent` pone las estadísticas básicas de un documento en su extensión.

### Métricas de legibilidad { #ReadabilityStatsComponent }

``` {.python .signature}
ReadabilityStatsComponent(nlp, name, preset=None, basic=None)
```

<!-- core: components.md:ReadabilityStatsComponent 78d49ec -->
`ReadabilityStatsComponent` pone en la extensión las métricas de legibilidad, calculadas sobre el documento o, con `basic`, sobre las estadísticas básicas que otro componente puso en él. Una biblioteca fija `basic_factory`, la fábrica de su componente de las estadísticas básicas, que el error nombra cuando esa extensión no las tiene.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `preset` | `str` | `None` | Preajuste de los coeficientes, uno de los preajustes de la clase; el de la clase por defecto si es `None` |
| `basic` | `str` | `None` | Extensión de un componente de las estadísticas básicas que se reutilizan en lugar de calcularlas otra vez |

Con `preset` en `None` la configuración de un pipeline guardado no lleva preajuste, y el pipeline toma el de la clase por defecto al cargarse; una biblioteca que quiere su valor por defecto escrito en la configuración lo da en la firma de su subclase.

Excepciones:

- `ParameterError` - una `stats_class` que no es concreta, un preajuste que no es una cadena o no es de la clase, una extensión no nombrada por una cadena;
- `SourceTypeError` - una clase sin `basic_stats_class` y sin `basic`;
- `SourceError` - un documento cuya extensión `basic` no tiene estadísticas básicas de la clase.

Los [preajustes](stats/readability_stats.md#presets) de esTS son `general` y `classic`, el de la clase `general`. En esTS la clase de estadísticas y su `basic_stats_class` están fijadas, así que los errores de `stats_class` y `SourceTypeError` no se dan. El componente nombrado por `basic` va antes que este en el pipeline; el mensaje de `SourceError` nombra el componente `ests_basic` (`basic_factory`) que hay que añadir allí.

=== "Código"

    ``` python
    nlp.add_pipe("ests_readability", name="readability")
    config = {"preset": "classic", "basic": "basic"}
    nlp.add_pipe("ests_readability", name="readability_classic", config=config)
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.readability.flesch_reading_easy, 2)
    round(doc._.readability_classic.flesch_reading_easy, 2)
    ```

=== "Resultado"

    ```
    102.19
    105.72
    ```

### Métricas de diversidad léxica { #DiversityStatsComponent }

``` {.python .signature}
DiversityStatsComponent(nlp, name, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

<!-- core: components.md:DiversityStatsComponent a13bd76 -->
`DiversityStatsComponent` pone en la extensión las métricas de diversidad léxica, mediante una clase de la biblioteca que lee un `Doc`. Sus parámetros son los de `DiversityStats`, con los mismos valores por defecto.

Excepciones:

- `ParameterError` - un parámetro erróneo (`check_params` de la diversidad).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `window_len` | `int` | `50` | Tamaño de la ventana de MATTR y del segmento de MSTTR |
| `mtld_threshold` | `float` | `0.72` | Umbral de TTR para MTLD, MA-MTLD y MTLD-W |
| `mtld_min_len` | `int` | `10` | Longitud mínima del factor para MTLD, MA-MTLD y MTLD-W |
| `hdd_sample_size` | `int` | `42` | Tamaño de la muestra de HD-D |
| `log_base` | `float` | `10` | Base del logaritmo de las métricas de Summer, Maas y Dugast |

=== "Código"

    ``` python
    config = {"window_len": 100, "log_base": 2.718281828459045}
    nlp.add_pipe("ests_diversity", name="diversity", config=config)
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.diversity.ttr, 3), round(doc._.diversity.sttr, 3)
    ```

=== "Resultado"

    ```
    (0.833, 0.916)
    ```

### Estadísticas morfológicas { #MorphStatsComponent }

``` {.python .signature}
MorphStatsComponent(nlp, name)
```

`MorphStatsComponent` pone las estadísticas morfológicas en la extensión. El pipeline necesita un `morphologizer` y un `lemmatizer` antes del componente.

Excepciones:

- `SourceError` - un documento sin las categorías gramaticales o sin los lemas.

=== "Código"

    ``` python
    nlp.add_pipe("ests_morph", name="morph")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.morph.pos[:4]
    ```

=== "Resultado"

    ```
    ('DET', 'NOUN', 'VERB', 'ADP')
    ```

### Estadísticas sintácticas { #SyntaxStatsComponent }

``` {.python .signature}
SyntaxStatsComponent(nlp, name)
```

<!-- core: components.md:SyntaxStatsComponent f99599b -->
`SyntaxStatsComponent` pone las estadísticas sintácticas en la extensión; necesitan un parser y las categorías gramaticales antes de él.

En esTS necesitan también un `lemmatizer` antes de él; la fábrica requiere `token.dep`, `token.head`, `token.pos` y `token.lemma`, así que `nlp.analyze_pipes()` señala un pipeline sin alguno de ellos.

Excepciones:

- `SourceError` - un documento sin análisis de dependencias, sin las categorías gramaticales o sin los lemas.

=== "Código"

    ``` python
    nlp.add_pipe("ests_syntax", name="syntax")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.syntax.tree_depth, doc._.syntax.mean_dependency_distance
    ```

=== "Resultado"

    ```
    (2.0, 1.6)
    ```

### Estadísticas de cohesión { #CohesionStatsComponent }

``` {.python .signature}
CohesionStatsComponent(nlp, name)
```

<!-- core: components.md:CohesionStatsComponent 51ecae4 -->
`CohesionStatsComponent` pone las estadísticas de cohesión en la extensión; por defecto necesitan las categorías gramaticales y los lemas antes de él.

En el pipeline de `es_core_news_sm` vienen del `morphologizer` y del `lemmatizer`.

Excepciones:

- `SourceError` - un documento sin las categorías gramaticales o sin los lemas.

=== "Código"

    ``` python
    nlp.add_pipe("ests_cohesion", name="cohesion")
    doc = nlp("El informe fue aprobado. Sin embargo, el informe no resuelve el problema.")
    doc._.cohesion.noun_overlap_adjacent, round(doc._.cohesion.connectors, 2)
    ```

=== "Resultado"

    ```
    (1.0, 83.33)
    ```

### Estadísticas de complejidad léxica { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

<!-- core: components.md:LexicalStatsComponent 7d94500 -->
`LexicalStatsComponent` pone en la extensión las estadísticas de complejidad léxica, con el diccionario de frecuencias de su atributo `freq_dict`: `None` por defecto, para el diccionario de la clase, y fijado por una biblioteca en el constructor de su componente. Un documento recibe las estadísticas cuando tiene una palabra de `iter_doc_words` (con `join_hyphens`) que no es un número del método `is_number`, `anyts.utils.is_number` por defecto; una biblioteca da los números que su clase deja fuera, así que un documento solo de números pasa intacto.

En esTS `freq_dict` es el [diccionario de frecuencias](datasets/freqdict.md) `FreqDict` del directorio `data_dir`, e `is_number` toma los números del `NUMBER_PATTERN` del español (`2020`, `1.500,50`, `3.º`). El pipeline necesita un `morphologizer` antes del componente; los lemas del modelo no se usan. Las bandas de frecuencia y la densidad léxica se calculan sin el diccionario, las estadísticas por el diccionario lo necesitan descargado.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `data_dir` | `str` | `None` | Directorio del diccionario de frecuencias; el de por defecto si no se indica |

Excepciones:

- `SourceError` - un documento sin las categorías gramaticales;
- `DatasetNotFoundError` - las estadísticas por el diccionario y `get_stats()` cuando el diccionario no está descargado;
- `ConfigValidationError` de spaCy - un `data_dir` que no es una cadena, en `add_pipe`.

=== "Código"

    ``` python
    nlp.add_pipe("ests_lexical", name="lexical")
    doc = nlp("El felinólogo examinaba al minino con parsimonia.")
    round(doc._.lexical.coverage, 3), round(doc._.lexical.p_top1000, 3)
    nlp("2020 1.500,50 3.º")._.lexical is None
    ```

=== "Resultado"

    ```
    (0.857, 0.429)
    True
    ```

### Métricas de estilo { #StyleStatsComponent }

``` {.python .signature}
StyleStatsComponent(nlp, name, stopwords=None, top_n=10, nausea_stopwords=None, cliches=None)
```

<!-- core: components.md:StyleStatsComponent 0abace1 -->
`StyleStatsComponent` pone las métricas de estilo en la extensión.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `stopwords` | `list[str]` | `None` | Palabras vacías del contenido de agua; las de la clase si es `None` |
| `top_n` | `int` | `10` | Número de las palabras más frecuentes de la náusea académica y de la naturalidad según la ley de Zipf (`NAUSEA_TOP_N`) |
| `nausea_stopwords` | `list[str]` | `None` | Palabras que se dejan fuera de las palabras más frecuentes de la náusea académica; las de la clase si es `None` |
| `cliches` | `list[str]` | `None` | Clichés; los de la clase (`cliches_list`) si es `None` |

Excepciones:

- `SourceTypeError` - palabras vacías, palabras vacías de la náusea o clichés que no son una lista de cadenas;
- `ParameterError` - un `top_n` que no es un entero de al menos uno.

Sin las listas, el contenido de agua toma las palabras vacías de `STOPWORDS` y las expresiones parentéticas de una palabra, la náusea académica deja fuera las palabras de `is_stopword`, y los clichés vienen de `OFFICIALESE_CLICHES`; `NAUSEA_TOP_N` es una constante de `anyts.constants`. Los sustantivos deverbales necesitan un `morphologizer` y un `lemmatizer` antes del componente, y sin ellos leer `verbal_nouns`, `markers()` o `get_stats()` lanza `SourceError`; las demás métricas solo leen las palabras.

=== "Código"

    ``` python
    nlp.add_pipe("ests_style", name="style")
    doc = nlp("Se procedió a la revisión del expediente a la mayor brevedad.")
    round(doc._.style.cliches, 2), round(doc._.style.verbal_nouns, 2)
    nlp.add_pipe("ests_style", name="style_cliches", config={"cliches": ["se procedió a"]})
    doc = nlp("Se procedió a la revisión del expediente a la mayor brevedad.")
    round(doc._.style_cliches.cliches, 2)
    ```

=== "Resultado"

    ```
    (18.18, 33.33)
    9.09
    ```

### Fonoestadística { #PhonStatsComponent }

``` {.python .signature}
PhonStatsComponent(nlp, name, window_len=3)
```

<!-- core: components.md:PhonStatsComponent 0e52eb9 -->
`PhonStatsComponent` pone las estadísticas fonéticas en la extensión; `window_len` (`PHON_WINDOW_LEN` por defecto) es la ventana en palabras de la aliteración y la asonancia.

Excepciones:

- `ParameterError` - un `window_len` que no es un entero de al menos 2.

=== "Código"

    ``` python
    nlp.add_pipe("ests_phon", name="phon", config={"window_len": 5})
    doc = nlp("Tres tristes tigres tragaban trigo en un trigal")
    round(doc._.phon.hardness, 3), round(doc._.phon.alliteration, 3)
    ```

=== "Resultado"

    ```
    (0.458, 0.975)
    ```

### Estadísticas del verso { #VerseStatsComponent }

``` {.python .signature}
VerseStatsComponent(nlp, name, seseo=False)
```

`VerseStatsComponent` pone las estadísticas del verso en la extensión. Las estadísticas leen los saltos de línea y las líneas en blanco del documento, así que pase el texto de un poema a `nlp` sin unir los versos; el componente no necesita ninguna anotación de un modelo. Un documento sin letras pasa intacto, y un texto con letras pero sin sílabas españolas da estadísticas vacías.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `seseo` | `bool` | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima |

Excepciones:

- `ConfigValidationError` de spaCy - un `seseo` que no es un booleano, en `add_pipe`.

=== "Código"

    ``` python
    nlp.add_pipe("ests_verse", name="verse")
    doc = nlp(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    doc._.verse.meter, doc._.verse.c_clausulas
    ```

=== "Resultado"

    ```
    ('octosílabo', {'aguda': 2, 'llana': 2})
    ```

## Oraciones tras líneas en blanco { #blank_lines }

<!-- core: components.md:start_sents_after_blank_lines b811493 -->
``` {.python .signature}
start_sents_after_blank_lines(doc)
```

Un componente que inicia una oración en el primer token tras una línea en blanco - un salto de línea, espacios opcionales y otro salto de línea -, para que un título, un elemento de una lista o un párrafo sin signo final sean una oración propia, como en el extractor de oraciones. Va antes del parser, `senter` o `sentencizer`, que conserva sus inicios y coloca los demás. Los espacios ante tal inicio se quedan con la oración anterior, y los signos que abren un párrafo (una raya de diálogo, `¡`, `«`) se quedan con su primera palabra. Por sí solo, el componente no divide las oraciones dentro de un párrafo y fija límites parciales (`has_sents`), así que las estadísticas toman las oraciones de tal documento de su texto. Un documento ya analizado, como uno que vuelve a pasar por el pipeline, pasa intacto, porque spaCy conserva sus oraciones. Una biblioteca del idioma registra el componente con su prefijo, `Language.component("<prefix>_blank_lines", func=start_sents_after_blank_lines)`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `doc` | `Doc` | - | Objeto Doc |

En esTS el componente está registrado como `ests_blank_lines`. Sin él, el modelo `es_core_news_sm` pega un párrafo sin signo final a la oración siguiente, y las estadísticas de un `Doc` difieren de las de la misma cadena. El pipeline de `ests.utils.get_nlp`, que analiza las cadenas de las estadísticas morfológicas, sintácticas, de cohesión y léxicas, lo tiene antes del parser.

=== "Código"

    ``` python
    nlp = spacy.load("es_core_news_sm")
    nlp.add_pipe("ests_blank_lines", before="parser")
    doc = nlp("Novedades\n\nImportación rápida. Menos errores")
    [sent.text.strip() for sent in doc.sents]
    ```

=== "Resultado"

    ```
    ['Novedades', 'Importación rápida.', 'Menos errores']
    ```

## Todo en un pipeline { #pipeline }

Los diez componentes pueden compartir un pipeline.

=== "Código"

    ``` python
    import ests
    import spacy

    nlp = spacy.load("es_core_news_sm")
    nlp.add_pipe("ests_blank_lines", before="parser")
    factories = (
        "basic",
        "readability",
        "diversity",
        "morph",
        "syntax",
        "cohesion",
        "lexical",
        "style",
        "phon",
        "verse",
    )
    for factory in factories:
        nlp.add_pipe(f"ests_{factory}", name=factory)

    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    (
        doc._.basic.n_words,
        round(doc._.readability.flesch_reading_easy, 2),
        round(doc._.diversity.ttr, 3),
        doc._.morph.pos[:2],
        doc._.syntax.tree_depth,
        doc._.cohesion.p_given,
        round(doc._.lexical.p_top1000, 3),
        round(doc._.style.water, 2),
        round(doc._.phon.p_vowels, 3),
        doc._.verse.n_lines,
    )
    ```

=== "Resultado"

    ```
    (12, 102.19, 0.833, ('DET', 'NOUN'), 2.0, 0.0, 0.667, 50.0, 0.457, 1)
    ```
