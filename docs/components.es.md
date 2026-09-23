# Componentes

Conjunto de componentes para los pipelines de [spaCy](https://github.com/explosion/spaCy). Cada uno es una clase con dos métodos: `__init__`, que registra una extensión de `Doc` al inicializarse, y `__call__`, que toma un objeto `Doc` y lo devuelve con las estadísticas puestas. Con ellos un texto se anota y se mide en una sola pasada, y las estadísticas viajan con el documento.

!!! note "Nota"
    La escritura de componentes propios se describe en la sección correspondiente de la [documentación de spaCy](https://spacy.io/usage/processing-pipelines#custom-components). Los ejemplos de abajo usan el modelo `es_core_news_sm`, que se instala aparte: `python -m spacy download es_core_news_sm` (véase [instalación](installation.md)).

## Nombres { #names }

Las fábricas llevan el prefijo de la biblioteca - `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion` - porque el registro de spaCy es uno para todo el proceso: un `basic` a secas chocaría con el componente de cualquier otra biblioteca que registre ese nombre, y spaCy responde a un segundo registro con `ValueError [E004]`.

Están declaradas como entry points de `spacy_factories`, así que un pipeline guardado con estos componentes - `nlp.to_disk(path)`, `spacy package`, una configuración de entrenamiento - se carga con `spacy.load(path)` en un proceso que nunca importa la biblioteca.

El nombre del paso del pipeline es libre y es como se llama la extensión, así que la forma corta está a un argumento de distancia:

``` python
nlp.add_pipe("ests_basic", name="basic", last=True)
doc = nlp("El gato duerme")
doc._.basic.n_words
```

Sin `name` el paso y la extensión conservan el nombre de la fábrica (`doc._.ests_basic`). El mismo componente puede añadirse dos veces con nombres distintos, que es como dos presets o dos juegos de parámetros conviven en un pipeline.

!!! warning "Serialización"
    Un componente guarda un objeto de estadísticas en `doc._.<name>`, y spaCy no sabe serializarlo: `Doc.to_bytes()`, `DocBin(store_user_data=True)` y `nlp.pipe(..., n_process>1)` fallan con estos componentes en el pipeline. Para guardar un documento, deje fuera los datos de usuario (`doc.to_bytes(exclude=["user_data"])`) o guarde `doc._.<name>.get_stats()` por su cuenta; para el multiproceso, calcule las estadísticas en el proceso principal después de `nlp.pipe`, sin los componentes.

## Qué necesita cada componente { #requirements }

| Componente | Fábrica | Estadísticas | Necesita |
| :--------: | :-----: | :----------: | :------: |
| `BasicStatsComponent` | `ests_basic` | [BasicStats](stats/basic_stats.md) | nada |
| `ReadabilityStatsComponent` | `ests_readability` | [ReadabilityStats](stats/readability_stats.md) | nada |
| `DiversityStatsComponent` | `ests_diversity` | [DiversityStats](stats/diversity_stats.md) | nada |
| `MorphStatsComponent` | `ests_morph` | [MorphStats](stats/morph_stats.md) | categorías gramaticales y lemas |
| `SyntaxStatsComponent` | `ests_syntax` | [SyntaxStats](stats/syntax_stats.md) | análisis sintáctico y lemas |
| `CohesionStatsComponent` | `ests_cohesion` | [CohesionStats](stats/cohesion_stats.md) | categorías gramaticales y lemas |

En el pipeline de `es_core_news_sm` las categorías gramaticales vienen del `morphologizer` (un `tagger` solo da la etiqueta del corpus y no la categoría de Universal Dependencies; con un `attribute_ruler` sí la da), el análisis del `parser` y los lemas del `lemmatizer`. Un componente al que le falta la anotación levanta `SourceError` cuando el documento pasa por él, también con componentes `excluded`: sin el `lemmatizer` todos los lemas son cadenas vacías, y eso haría que todos los sustantivos de un texto se repitieran entre sí.

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
| `preset` | str | `"general"` | Preset de los coeficientes (`general`, `classic`) |
| `basic` | str | `None` | Nombre de la extensión de un componente de estadísticas básicas, cuyo objeto se usa en lugar de calcularlas otra vez |

Un preset desconocido levanta `ParameterError` al añadir el componente, no al pasar un documento por él.

Las métricas de legibilidad se calculan sobre las estadísticas básicas, así que un pipeline con los dos componentes las calcula dos veces salvo que `basic` nombre la extensión del primero: `nlp.add_pipe("ests_readability", config={"basic": "basic"})` después de un componente llamado `basic`. En las páginas españolas de este sitio eso lleva un documento de 0,025 s a 0,015 s, y el ahorro crece con cada preset añadido. Un nombre que no lleva estadísticas básicas, o un componente que corre después de este, levanta `SourceError`.

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

Un parámetro fuera de su rango levanta `ParameterError` al añadir el componente.

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

El componente de las estadísticas morfológicas de un texto. Las categorías gramaticales y los rasgos se leen de la anotación del modelo, así que el pipeline necesita un etiquetador antes del componente.

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

El componente de las estadísticas sintácticas de un texto. Las estadísticas se calculan sobre el árbol de dependencias, así que el pipeline necesita un analizador antes del componente.

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

El componente de las estadísticas de cohesión de un texto. Los rasgos se leen de la anotación del modelo, así que el pipeline necesita un etiquetador antes del componente.

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

## Todo en un pipeline { #pipeline }

Los seis componentes pueden convivir, y entonces una sola pasada sobre un documento da todas las estadísticas de la biblioteca que un `Doc` puede llevar.

!!! example "Ejemplo"

    _Código_:

    ``` python
    import ests
    import spacy

    nlp = spacy.load("es_core_news_sm")
    for factory in ("basic", "readability", "diversity", "morph", "syntax", "cohesion"):
        nlp.add_pipe(f"ests_{factory}", name=factory, last=True)

    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    (
        doc._.basic.n_words,
        round(doc._.readability.flesch_reading_easy, 2),
        round(doc._.diversity.ttr, 3),
        doc._.morph.pos[:2],
        doc._.syntax.tree_depth,
        doc._.cohesion.p_given,
    )
    ```

    _Resultado_:

    ``` bash
    (12, 102.19, 0.833, ('DET', 'NOUN'), 2.0, 0.0)
    ```
