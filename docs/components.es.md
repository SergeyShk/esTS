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

    nlp = ests.load_pipeline()
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

Las fábricas llevan el prefijo de la biblioteca: `ests_basic`, `ests_readability`, `ests_unadapted_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style`, `ests_phon`, `ests_verse`. Están declaradas como puntos de entrada de `spacy_factories`, así que un pipeline guardado con estos componentes (`nlp.to_disk(path)`, `spacy package`) se carga con `spacy.load(path)` sin importar la biblioteca. `import ests` no carga los componentes mientras spaCy no está cargado - los hallan los puntos de entrada, y `ests.StyleStatsComponent` los carga al usarlo por primera vez; desde las fuentes sin el paquete instalado, `import ests.components` va antes de `add_pipe`.

<!-- core: components.md:StatsComponent-names 737f20b -->
El nombre del paso del pipeline es el nombre de la extensión: `nlp.add_pipe(factory, name="basic")` pone las estadísticas en `doc._.basic`. Sin `name` ambos toman el nombre de la fábrica. La extensión sigue al paso cuando el pipeline lo renombra (`nlp.rename_pipe`), y una extensión eliminada con `Doc.remove_extension` mientras el componente vive se registra de nuevo con su siguiente documento. Un nombre ocupado por una extensión de otro paquete lanza `ParameterError` en lugar de reemplazarla: en `add_pipe`, o con el primer documento después de `rename_pipe`, que renombra el paso antes de que el componente conozca su nombre. Un componente tomado de otro pipeline (`add_pipe(name, source=other)`) es el mismo objeto en ambos, así que con un nombre nuevo escribe también en esa extensión del otro pipeline; un componente independiente sale de la fábrica, `add_pipe(factory, name=...)`. El mismo componente puede añadirse dos veces con nombres distintos, con parámetros distintos. Un documento sin palabras - una cadena vacía, espacios, pura puntuación - pasa por un componente sin cambios, con su extensión en `None`. Un documento sin una anotación que las estadísticas necesitan, como el análisis de `SyntaxStats` en un pipeline sin parser, lanza `SourceError` en el componente, así que la llamada del pipeline falla.

En `ests_lexical` también pasa intacto un documento solo de números, y en `ests_verse` un documento sin letras.

<!-- core: components.md:StatsComponent-serialization b114bf2 -->
!!! warning "Serialización"
    Un componente guarda un objeto de estadísticas en `doc._.<name>`, y spaCy no sabe serializarlo: `Doc.to_bytes()`, `DocBin(store_user_data=True)` y `nlp.pipe(..., n_process>1)` fallan con estos componentes en el pipeline. Para guardar un documento, guarde `doc._.<name>.get_stats()` por separado y vacíe la extensión (`doc._.<name> = None`) antes de `doc.to_bytes()`: dejar fuera todos los datos de usuario (`exclude=["user_data"]`) pierde también las palabras de los tokens multipalabra de anySeg (`token._.anyseg_words`), y un documento cuyas palabras llevan columnas propias, como uno de `anyseg.spacy.to_doc`, se lee de vuelta con otras palabras. Para el multiproceso, calcule las estadísticas en el proceso principal después de `nlp.pipe`, sin los componentes.

Un componente lee el `Doc` de su pipeline tal cual y no toca su tokenizador: las palabras y las oraciones de la API de cadenas vienen con el pipeline de [`load_pipeline`](#load_pipeline), donde `sí--dijo` son dos palabras y una raya, y una línea en blanco cierra la oración.

## Componentes de las clases de estadísticas { #class-components }

| Componente | Fábrica | Clase de estadísticas | Parámetros |
| :--------- | :------ | :-------------------- | :--------- |
| [`BasicStatsComponent`](#BasicStatsComponent) | `ests_basic` | [`BasicStats`](stats/basic_stats.md) | - |
| [`ReadabilityStatsComponent`](#ReadabilityStatsComponent) | `ests_readability` | [`ReadabilityStats`](stats/readability_stats.md) | `preset`, `basic` |
| [`UnadaptedReadabilityStatsComponent`](#UnadaptedReadabilityStatsComponent) | `ests_unadapted_readability` | [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md) | `basic` |
| [`DiversityStatsComponent`](#DiversityStatsComponent) | `ests_diversity` | [`DiversityStats`](stats/diversity_stats.md) | `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` |
| [`MorphStatsComponent`](#MorphStatsComponent) | `ests_morph` | [`MorphStats`](stats/morph_stats.md) | - |
| [`SyntaxStatsComponent`](#SyntaxStatsComponent) | `ests_syntax` | [`SyntaxStats`](stats/syntax_stats.md) | - |
| [`CohesionStatsComponent`](#CohesionStatsComponent) | `ests_cohesion` | [`CohesionStats`](stats/cohesion_stats.md) | `blank_lines` |
| [`LexicalStatsComponent`](#LexicalStatsComponent) | `ests_lexical` | [`LexicalStats`](stats/lexical_stats.md) | `data_dir` |
| [`StyleStatsComponent`](#StyleStatsComponent) | `ests_style` | [`StyleStats`](stats/style_stats.md) | `stopwords`, `top_n`, `nausea_stopwords`, `cliches` |
| [`PhonStatsComponent`](#PhonStatsComponent) | `ests_phon` | [`PhonStats`](stats/phon_stats.md) | `window_len` |
| [`VerseStatsComponent`](#VerseStatsComponent) | `ests_verse` | [`VerseStats`](stats/verse_stats.md) | `seseo` |

Las estadísticas básicas, de legibilidad, de diversidad, fonéticas y del verso y las fórmulas de otros idiomas no necesitan ninguna anotación de un modelo. En el pipeline de [`load_pipeline`](#load_pipeline) las categorías gramaticales, los rasgos y los lemas vienen del componente `esmorph` de [esMorph](https://github.com/SergeyShk/esMorph) y el análisis del `parser` del modelo; en el pipeline del propio `es_core_news_sm` vienen del `morphologizer` (o de un `tagger` con un `attribute_ruler`; un `tagger` solo no las da) y del `lemmatizer`. Un componente al que le falta la anotación, también con componentes `excluded`, lanza `SourceError` cuando el documento pasa por él; `ests_lexical` solo necesita las categorías gramaticales, y `ests_style` lanza el error cuando se lee `verbal_nouns` o `markers()`.

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

<!-- core: components.md:ReadabilityStatsComponent 58263af -->
`ReadabilityStatsComponent` pone en la extensión las métricas de legibilidad, calculadas sobre el documento o, con `basic`, sobre las estadísticas básicas que otro componente puso en él. Una biblioteca fija `basic_factory`, la fábrica de su componente de las estadísticas básicas, que el error nombra cuando esa extensión no las tiene.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `preset` | `str` | `None` | Preajuste de los coeficientes, uno de los preajustes de la clase; el de la clase por defecto si es `None` |
| `basic` | `str` | `None` | Extensión de un componente de las estadísticas básicas que se reutilizan en lugar de calcularlas otra vez |

Con `preset` en `None` la configuración de un pipeline guardado no lleva preajuste, y el pipeline toma el de la clase por defecto al cargarse; una biblioteca que quiere su valor por defecto escrito en la configuración lo da en la firma de su subclase.

Excepciones:

- `ParameterError` - una `stats_class` que no es concreta, un preajuste que no es una cadena o no es de la clase, una extensión no nombrada por una cadena o nombrada por una vacía;
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

### Fórmulas de otros idiomas { #UnadaptedReadabilityStatsComponent }

``` {.python .signature}
UnadaptedReadabilityStatsComponent(nlp, name, basic=None)
```

<!-- core: components.md:UnadaptedReadabilityStatsComponent b7871a2 -->
`UnadaptedReadabilityStatsComponent` pone en la extensión las fórmulas de legibilidad de otros idiomas, calculadas sobre el documento o, con `basic`, sobre las estadísticas básicas que otro componente puso en él. Una biblioteca fija `basic_factory`, como para `ReadabilityStatsComponent`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `basic` | `str` | `None` | Extensión de un componente de las estadísticas básicas que se reutilizan en lugar de calcularlas otra vez |

Excepciones:

- `ParameterError` - una `stats_class` que no es concreta, una extensión no nombrada por una cadena o nombrada por una vacía;
- `SourceTypeError` - una clase sin `basic_stats_class` y sin `basic`;
- `SourceError` - un documento cuya extensión `basic` no tiene estadísticas básicas de la clase.

Las fórmulas son las de [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md), con sus propios coeficientes y sin calibración para el español. Como en `ReadabilityStatsComponent`, los errores de `stats_class` y `SourceTypeError` no se dan en esTS, y el mensaje de `SourceError` nombra el componente `ests_basic` que hay que añadir antes que este.

=== "Código"

    ``` python
    nlp.add_pipe("ests_unadapted_readability", name="unadapted", config={"basic": "basic"})
    doc = nlp(
        "El gato estaba en la ventana y miraba a los pájaros que volaban "
        "sobre los tejados de las casas."
    )
    doc._.unadapted.gulpease, doc._.unadapted.forcast
    doc._.unadapted.bs is doc._.basic
    ```

=== "Resultado"

    ```
    (64.78947368421052, 12.105263157894736)
    True
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

<!-- core: components.md:MorphStatsComponent 5d99bc4 -->
`MorphStatsComponent` pone las estadísticas morfológicas en la extensión; por defecto necesitan las categorías gramaticales antes de él.

En esTS el pipeline necesita además los lemas antes del componente, de `esmorph` o de un `lemmatizer`; la fábrica requiere `token.pos` y `token.lemma`, así que `nlp.analyze_pipes()` señala un pipeline sin alguno de ellos.

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

En esTS necesitan también los lemas antes de él, de `esmorph` o de un `lemmatizer`; la fábrica requiere `token.dep`, `token.head`, `token.pos` y `token.lemma`, así que `nlp.analyze_pipes()` señala un pipeline sin alguno de ellos.

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
CohesionStatsComponent(nlp, name, blank_lines=False)
```

<!-- core: components.md:CohesionStatsComponent 47c308b -->
`CohesionStatsComponent` pone las estadísticas de cohesión en la extensión; por defecto necesitan las categorías gramaticales y los lemas antes de él. Con `blank_lines` los párrafos empiezan solo tras las líneas en blanco, como en `CohesionStats`, para un texto con líneas cortadas dentro de sus párrafos.

Excepciones:

- `ParameterError` - un `blank_lines` que no es un `bool`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `blank_lines` | `bool` | `False` | Empezar los párrafos solo tras las líneas en blanco, para un texto con líneas cortadas dentro de sus párrafos; por defecto, tras cada salto de línea |

En el pipeline de `load_pipeline` las categorías gramaticales y los lemas vienen de `esmorph`, en el de `es_core_news_sm`, del `morphologizer` y del `lemmatizer`; la fábrica requiere `token.pos` y `token.lemma`, así que `nlp.analyze_pipes()` señala un pipeline sin alguno de ellos, y un documento sin ellos lanza `SourceError`. Los textos de [`SpanishLiterature`](datasets/spanishliterature.md) tienen las líneas cortadas dentro de sus párrafos y necesitan `blank_lines`.

=== "Código"

    ``` python
    nlp.add_pipe("ests_cohesion", name="cohesion")
    nlp.add_pipe("ests_cohesion", name="paragraphs", config={"blank_lines": True})
    doc = nlp("El informe fue aprobado. Sin embargo, el informe\nno resuelve el problema.")
    (
        doc._.cohesion.noun_overlap_adjacent,
        round(doc._.cohesion.connectors, 2),
        doc._.cohesion.n_paragraphs,
        doc._.paragraphs.n_paragraphs,
    )
    ```

=== "Resultado"

    ```
    (1.0, 83.33, 2, 1)
    ```

### Estadísticas de complejidad léxica { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

<!-- core: components.md:LexicalStatsComponent 5077aef -->
`LexicalStatsComponent` pone en la extensión las estadísticas de complejidad léxica, con el diccionario de frecuencias de su atributo `freq_dict`: `None` por defecto, para el diccionario de la clase, y fijado por una biblioteca antes del constructor del núcleo; una clase sin diccionario propio y sin `freq_dict` lanza `ParameterError` al crearse el componente. Un documento recibe las estadísticas cuando tiene un token con una letra o una cifra (`has_words`) que no es un número del método `is_number`, `anyts.utils.is_number` por defecto; una biblioteca da los números que su clase deja fuera, así que un documento solo de números pasa intacto.

En esTS `freq_dict` es el [diccionario de frecuencias](datasets/freqdict.md) `FreqDict` del directorio `data_dir`, e `is_number` toma los números del `NUMBER_PATTERN` del español (`2020`, `1.500,50`, `3.º`). El pipeline necesita las categorías gramaticales antes del componente, de `esmorph` o de un `morphologizer`, y la fábrica requiere `token.pos`; los lemas del modelo no se usan. Las bandas de frecuencia y la densidad léxica se calculan sin el diccionario, las estadísticas por el diccionario lo necesitan descargado.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `data_dir` | `str` | `None` | Directorio del diccionario de frecuencias; el de por defecto si no se indica |

Excepciones:

- `SourceError` - un documento sin las categorías gramaticales;
- `DatasetNotFoundError` - las estadísticas por el diccionario y `get_stats()` cuando el diccionario no está descargado;
- `ParameterError` - un `data_dir` que no es una cadena.

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

<!-- core: components.md:StyleStatsComponent 957821f -->
`StyleStatsComponent` pone las métricas de estilo en la extensión.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `stopwords` | `list[str]` | `None` | Palabras vacías del contenido de agua; las de la clase si es `None` |
| `top_n` | `int` | `10` | Número de las palabras más frecuentes de la náusea académica y de la naturalidad según la ley de Zipf (`NAUSEA_TOP_N`) |
| `nausea_stopwords` | `list[str]` | `None` | Palabras que se dejan fuera de las palabras más frecuentes de la náusea académica; las de la clase si es `None` |
| `cliches` | `list[str]` | `None` | Clichés; los de la clase (`cliches_list`) si es `None` |

Excepciones:

- `ParameterError` - palabras vacías, palabras vacías de la náusea o clichés que no son una lista de cadenas, un `top_n` que no es un entero de al menos uno.

Sin las listas, el contenido de agua toma las palabras vacías de `STOPWORDS` y las expresiones parentéticas de una palabra, la náusea académica deja fuera las palabras de `is_stopword`, y los clichés vienen de `OFFICIALESE_CLICHES`; `NAUSEA_TOP_N` es una constante de `anyts.constants`. Los sustantivos deverbales necesitan las categorías gramaticales y los lemas antes del componente, de `esmorph` o de un `morphologizer` y un `lemmatizer`, y sin ellos leer `verbal_nouns`, `markers()` o `get_stats()` lanza `SourceError`; las demás métricas solo leen las palabras.

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

- `ParameterError` - un `seseo` que no es un booleano.

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

## Pipeline recomendado { #load_pipeline }

``` {.python .signature}
load_pipeline(model='es_core_news_sm', exclude=(), **kwargs)
```

Un modelo de spaCy con el tokenizador `anyseg.Tokenizer.v1` y el componente `anyseg_sentencizer` en primer lugar, ambos de [anySeg](https://github.com/SergeyShk/anySeg): los tokens y las oraciones de un `Doc` son los que los [extractores](extractors/sentences.md) dan a su texto, así que las estadísticas de un `Doc` y de la cadena cuentan las mismas palabras y oraciones. Tras `anyseg_sentencizer` va el componente `esmorph` de [esMorph](https://github.com/SergeyShk/esMorph), en lugar del `morphologizer` y del `lemmatizer` del modelo: las categorías gramaticales, los rasgos y los lemas de un `Doc` son los de una cadena, elegidos en el contexto de la oración, mientras que el analizador sintáctico, cuyos árboles no dependen de las categorías gramaticales, y los demás componentes son los del modelo. Una contracción (`del`, `al`) o un verbo con clíticos (`dámelo`) es un token con el análisis de su primera palabra (`de`, `dar`), con sus palabras en `token._.anyseg_words`; una cadena las cuenta como palabras aparte, así que las estadísticas morfológicas y léxicas de un `Doc` y de su cadena difieren, ya que una cadena lee cada clítico como un pronombre y el artículo de `del` y `al` como un determinante aparte: en fragmentos de prosa la diferencia mediana es del 20-30 % para `Case=Acc`, `Case=Dat` y `Reflex`, del 12 % para los pronombres, del 9 % para los determinantes y la perplejidad y del 5 % para la frecuencia media. `text_features` lee la morfología de un `Doc`. Un pipeline guardado se carga con `spacy.load(path)`, ya que las fábricas de anySeg y de esMorph son puntos de entrada. `ests.utils.get_nlp`, que analiza las cadenas de las estadísticas sintácticas y de cohesión y de `text_features`, lo carga una vez por proceso y modelo.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `model` | `str` | `'es_core_news_sm'` | Nombre o ruta de un modelo de spaCy: `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg` |
| `exclude` | `str` / `list[str]` | `()` | Componentes del modelo que no se cargan, por ejemplo `ner` |
| `**kwargs` | | | Los demás parámetros de `spacy.load`; el tokenizador de `config` se sustituye por el de anySeg |

Excepciones:

- `DatasetNotFoundError` - un modelo que no está instalado, o una ruta sin pipeline.

Un pipeline propio, como `spacy.load("es_core_news_sm")`, conserva el tokenizador de spaCy: allí `sí--dijo` es un solo token, y el analizador pega un párrafo sin signo final a la oración siguiente por encima de una línea en blanco, así que las estadísticas de su `Doc` difieren de las de la cadena.

=== "Código"

    ``` python
    import ests

    nlp = ests.load_pipeline()
    doc = nlp("Novedades\n\nImportación rápida. Menos errores\n\n--Sí --dijo él. Vino del pueblo.")
    [sent.text.strip() for sent in doc.sents]
    [(token.text, token._.anyseg_words) for token in doc if token.text == "del"]
    ```

=== "Resultado"

    ```
    ['Novedades', 'Importación rápida.', 'Menos errores', '--Sí --dijo él.', 'Vino del pueblo.']
    [('del', [{'form': 'de'}, {'form': 'el'}])]
    ```

## Todo en un pipeline { #pipeline }

Los once componentes pueden compartir un pipeline.

=== "Código"

    ``` python
    import ests

    nlp = ests.load_pipeline()
    factories = (
        "basic",
        "readability",
        "unadapted_readability",
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
        round(doc._.unadapted_readability.gulpease, 2),
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
    (12, 102.19, 99.83, 0.833, ('DET', 'NOUN'), 2.0, 0.0, 0.583, 50.0, 0.457, 1)
    ```
