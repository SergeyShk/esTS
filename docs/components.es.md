# Componentes

<!-- core: components.md:StatsComponent e3962ed -->
La base de los componentes de [spaCy](https://github.com/explosion/spaCy) que ponen las estadísticas de un texto en una extensión de `Doc`: un componente registra la extensión al añadirse a un pipeline y, para cada documento, calcula las estadísticas y las pone en `doc._.<name>`. La escritura de componentes en general se describe en la [documentación de spaCy](https://spacy.io/usage/processing-pipelines#custom-components).

Los componentes de esTS son subclases del `StatsComponent` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/components/), una por cada clase de estadísticas.

!!! note "Nota"
    Los ejemplos de abajo usan el modelo `es_core_news_sm`, que se instala aparte: `python -m spacy download es_core_news_sm` (véase [instalación](installation.md)).

## Nombres { #names }

Las fábricas llevan el prefijo de la biblioteca: `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style`, `ests_phon`, `ests_verse`. Están declaradas como entry points de `spacy_factories`, así que un pipeline guardado con estos componentes (`nlp.to_disk(path)`, `spacy package`) se carga con `spacy.load(path)` sin importar la biblioteca.

``` python
nlp.add_pipe("ests_basic", name="basic", last=True)
doc = nlp("El gato duerme")
doc._.basic.n_words
```

<!-- core: components.md:StatsComponent-names 9314eeb -->
El nombre del paso del pipeline es el nombre de la extensión: `nlp.add_pipe(factory, name="basic")` pone las estadísticas en `doc._.basic`. Sin `name` el paso y la extensión conservan el nombre de la fábrica. La extensión sigue al paso cuando el pipeline lo renombra (`nlp.rename_pipe`), y un nombre ocupado por una extensión de otro paquete lanza `ParameterError` en lugar de reemplazarla. Un componente tomado de otro pipeline (`add_pipe(name, source=other)`) es el mismo objeto en ambos, así que con un nombre nuevo escribe también en esa extensión del otro pipeline; un componente propio sale de la fábrica, `add_pipe(factory, name=...)`. El mismo componente puede añadirse dos veces con nombres distintos, con parámetros distintos. Un documento sin palabras - una cadena vacía, espacios, pura puntuación - pasa por un componente sin cambios, con su extensión en `None`.

<!-- core: components.md:StatsComponent-serialization d6d5068 -->
!!! warning "Serialización"
    Un componente guarda un objeto de estadísticas en `doc._.<name>`, y spaCy no sabe serializarlo: `Doc.to_bytes()`, `DocBin(store_user_data=True)` y `nlp.pipe(..., n_process>1)` fallan con estos componentes en el pipeline. Para guardar un documento, deje fuera los datos de usuario (`doc.to_bytes(exclude=["user_data"])`) o guarde `doc._.<name>.get_stats()` por su cuenta; para el multiproceso, calcule las estadísticas en el proceso principal después de `nlp.pipe`, sin los componentes.

Añadir un componente amplía el tokenizador de su pipeline con las reglas de las rayas de un diálogo pegadas a las palabras ([`add_dash_rules`](extractors/words.md)), como en la API de cadenas: `sí--dijo` son dos palabras y una raya. Un tokenizador que no es el `Tokenizer` de spaCy se queda como está.

## Qué necesita cada componente { #requirements }

| Componente | Fábrica | Estadísticas | Necesita |
| :--------: | :-----: | :----------: | :------: |
| `BasicStatsComponent` | `ests_basic` | [BasicStats](stats/basic_stats.md) | nada |
| `ReadabilityStatsComponent` | `ests_readability` | [ReadabilityStats](stats/readability_stats.md) | nada |
| `DiversityStatsComponent` | `ests_diversity` | [DiversityStats](stats/diversity_stats.md) | nada |
| `MorphStatsComponent` | `ests_morph` | [MorphStats](stats/morph_stats.md) | categorías gramaticales y lemas |
| `SyntaxStatsComponent` | `ests_syntax` | [SyntaxStats](stats/syntax_stats.md) | análisis sintáctico y lemas |
| `CohesionStatsComponent` | `ests_cohesion` | [CohesionStats](stats/cohesion_stats.md) | categorías gramaticales y lemas |
| `LexicalStatsComponent` | `ests_lexical` | [LexicalStats](stats/lexical_stats.md) | categorías gramaticales; las estadísticas por el diccionario de frecuencias lo necesitan descargado |
| `StyleStatsComponent` | `ests_style` | [StyleStats](stats/style_stats.md) | categorías gramaticales y lemas para los sustantivos deverbales |
| `PhonStatsComponent` | `ests_phon` | [PhonStats](stats/phon_stats.md) | nada |
| `VerseStatsComponent` | `ests_verse` | [VerseStats](stats/verse_stats.md) | nada; los saltos de línea del texto |

En el pipeline de `es_core_news_sm` las categorías gramaticales vienen del `morphologizer` (o de un `tagger` con un `attribute_ruler`; un `tagger` solo no las da), el análisis del `parser` y los lemas del `lemmatizer`. Un componente al que le falta la anotación, también con componentes `excluded`, lanza `SourceError` cuando el documento pasa por él.

## BasicStatsComponent

!!! info ""
    **ests.components.BasicStatsComponent**

El componente de las estadísticas básicas de un texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_basic"` | Nombre del componente en el pipeline |

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar las bibliotecas
    import ests
    import spacy

    # Cargar el modelo de spaCy
    nlp = spacy.load("es_core_news_sm")

    # Añadir el componente
    nlp.add_pipe("ests_basic", name="basic", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.basic.n_words, doc._.basic.c_letters
    ```

    _Resultado_:

    ``` bash
    (12, {2: 5, 3: 1, 4: 1, 5: 1, 6: 3, 7: 1})
    ```

## ReadabilityStatsComponent

!!! info ""
    **ests.components.ReadabilityStatsComponent**

El componente de las métricas de legibilidad de un texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_readability"` | Nombre del componente en el pipeline |
| `preset` | str | `"general"` | Preajuste de los coeficientes (`general`, `classic`) |
| `basic` | str | `None` | Nombre de la extensión de un componente de estadísticas básicas, cuyo objeto se usa en lugar de calcularlas otra vez |

Un preajuste desconocido lanza `ParameterError` al añadir el componente.

Las métricas de legibilidad se calculan sobre las estadísticas básicas, así que un pipeline con los dos componentes las calcula dos veces salvo que `basic` nombre la extensión del primero: `nlp.add_pipe("ests_readability", config={"basic": "basic"})` después de un componente llamado `basic`. Un nombre que no lleva estadísticas básicas, o un componente que corre después de este, lanza `SourceError`.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente con los coeficientes clásicos
    nlp.add_pipe(
        "ests_readability",
        name="readability_classic",
        config={"preset": "classic"},
        last=True,
    )

    # Leer las métricas calculadas
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.readability_classic.flesch_reading_easy, 2)
    ```

    _Resultado_:

    ``` bash
    105.72
    ```

## DiversityStatsComponent

!!! info ""
    **ests.components.DiversityStatsComponent**

El componente de las métricas de diversidad léxica de un texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_diversity"` | Nombre del componente en el pipeline |
| `window_len` | int | `50` | Tamaño de la ventana de MATTR y del segmento de MSTTR |
| `mtld_threshold` | float | `0.72` | Umbral de TTR para MTLD, MA-MTLD y MTLD-W |
| `mtld_min_len` | int | `10` | Longitud mínima del factor para MTLD, MA-MTLD y MTLD-W |
| `hdd_sample_size` | int | `42` | Tamaño de la muestra de HD-D |
| `log_base` | float | `10` | Base del logaritmo de las métricas de Summer, Maas y Dugast |

Un parámetro fuera de su rango lanza `ParameterError` al añadir el componente.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente con logaritmo natural y ventana de 100 palabras
    nlp.add_pipe(
        "ests_diversity",
        name="diversity_ln",
        config={"window_len": 100, "log_base": 2.718281828459045},
        last=True,
    )

    # Leer las métricas calculadas
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.diversity_ln.ttr, 3)
    ```

    _Resultado_:

    ``` bash
    0.833
    ```

## MorphStatsComponent

!!! info ""
    **ests.components.MorphStatsComponent**

El componente de las estadísticas morfológicas de un texto. El pipeline necesita un `morphologizer` y un `lemmatizer` antes del componente.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_morph"` | Nombre del componente en el pipeline |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_morph", name="morph", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.morph.pos[:4]
    ```

    _Resultado_:

    ``` bash
    ('DET', 'NOUN', 'VERB', 'ADP')
    ```

## SyntaxStatsComponent

!!! info ""
    **ests.components.SyntaxStatsComponent**

El componente de las estadísticas sintácticas de un texto. El pipeline necesita un `parser` y un `lemmatizer` antes del componente.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_syntax"` | Nombre del componente en el pipeline |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_syntax", name="syntax", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.syntax.tree_depth, doc._.syntax.mean_dependency_distance
    ```

    _Resultado_:

    ``` bash
    (2.0, 1.6)
    ```

## CohesionStatsComponent

!!! info ""
    **ests.components.CohesionStatsComponent**

El componente de las estadísticas de cohesión de un texto. El pipeline necesita un `morphologizer` y un `lemmatizer` antes del componente.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_cohesion"` | Nombre del componente en el pipeline |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_cohesion", name="cohesion", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("El informe fue aprobado. Sin embargo, el informe no resuelve el problema.")
    doc._.cohesion.noun_overlap_adjacent, round(doc._.cohesion.connectors, 2)
    ```

    _Resultado_:

    ``` bash
    (1.0, 83.33)
    ```

## LexicalStatsComponent

!!! info ""
    **ests.components.LexicalStatsComponent**

El componente de las estadísticas de complejidad léxica de un texto. El pipeline necesita un `morphologizer` antes del componente; los lemas del modelo no se usan. Las bandas de frecuencia y la densidad léxica se calculan sin el [diccionario de frecuencias](datasets/freqdict.md), las estadísticas por el diccionario lo necesitan descargado. Aquí los números no son palabras, así que un documento solo de números también pasa intacto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_lexical"` | Nombre del componente en el pipeline |
| `data_dir` | str | `None` | Directorio del diccionario de frecuencias; el de por defecto si no se indica |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_lexical", name="lexical", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("El felinólogo examinaba al minino con parsimonia.")
    round(doc._.lexical.coverage, 3), round(doc._.lexical.p_top1000, 3)
    ```

    _Resultado_:

    ``` bash
    (0.857, 0.429)
    ```

## StyleStatsComponent

!!! info ""
    **ests.components.StyleStatsComponent**

El componente de las métricas de estilo de un texto. Los sustantivos deverbales necesitan un `morphologizer` y un `lemmatizer` antes del componente; las demás métricas solo leen las palabras.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_style"` | Nombre del componente en el pipeline |
| `stopwords` | list[str] | `None` | Palabras vacías para el contenido de agua; `STOPWORDS` y las expresiones parentéticas de una palabra si no se indican |
| `top_n` | int | `10` | Número de las palabras más frecuentes para la náusea académica y la naturalidad según Zipf |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_style", name="style", last=True)

    # Leer las métricas calculadas
    doc = nlp("Se procedió a la revisión del expediente a la mayor brevedad.")
    round(doc._.style.cliches, 2), round(doc._.style.verbal_nouns, 2)
    ```

    _Resultado_:

    ``` bash
    (18.18, 33.33)
    ```

## PhonStatsComponent

!!! info ""
    **ests.components.PhonStatsComponent**

El componente de la fonoestadística de un texto. No necesita ninguna anotación de un modelo.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_phon"` | Nombre del componente en el pipeline |
| `window_len` | int | `3` | Ventana en palabras para la aliteración y la asonancia |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_phon", name="phon", last=True)

    # Leer las estadísticas calculadas
    doc = nlp("Tres tristes tigres tragaban trigo en un trigal")
    round(doc._.phon.hardness, 3), doc._.phon.c_clusters
    ```

    _Resultado_:

    ``` bash
    (0.458, {1: 12, 2: 7})
    ```

## VerseStatsComponent

!!! info ""
    **ests.components.VerseStatsComponent**

El componente de las estadísticas del verso de un texto. Las estadísticas leen los saltos de línea y las líneas en blanco del documento, así que pase el texto de un poema a `nlp` sin unir los versos; el componente no necesita ninguna anotación de un modelo. Un documento sin letras pasa intacto, y un texto con letras pero sin sílabas españolas da estadísticas vacías.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `nlp` | Language | `-` | Objeto Language |
| `name` | str | `"ests_verse"` | Nombre del componente en el pipeline |
| `seseo` | bool | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Añadir el componente
    nlp.add_pipe("ests_verse", name="verse", last=True)

    # Leer las estadísticas calculadas del comienzo del Romance del prisionero
    doc = nlp(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    doc._.verse.meter, doc._.verse.c_clausulas
    ```

    _Resultado_:

    ``` bash
    ('octosílabo', {'aguda': 2, 'llana': 2})
    ```

## Todo en un pipeline { #pipeline }

Los diez componentes pueden compartir un pipeline.

!!! example "Ejemplo"

    _Código_:

    ``` python
    import ests
    import spacy

    nlp = spacy.load("es_core_news_sm")
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
        nlp.add_pipe(f"ests_{factory}", name=factory, last=True)

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

    _Resultado_:

    ``` bash
    (12, 102.19, 0.833, ('DET', 'NOUN'), 2.0, 0.0, 0.667, 50.0, 0.457, 1)
    ```
