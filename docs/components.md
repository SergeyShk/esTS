# Components

A set of components for [spaCy](https://github.com/explosion/spaCy) pipelines. Each one is a class with two methods: `__init__`, which registers an extension of `Doc` at initialization, and `__call__`, which takes a `Doc` object and returns it with the statistics attached. With them a text is annotated and measured in one pass, and the statistics travel with the document.

!!! note "Note"
    Writing components of your own is described in the corresponding section of the [documentation of spaCy](https://spacy.io/usage/processing-pipelines#custom-components). The examples below use the model `es_core_news_sm`, which is installed apart: `python -m spacy download es_core_news_sm` (see [installation](installation.md)).

## Names { #names }

The factories carry the prefix of the library - `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion` - because the registry of spaCy is one for the whole process: a plain `basic` would collide with the component of any other library registering that name, and spaCy answers a second registration with `ValueError [E004]`.

The name of the pipe is free and is what the extension is called, so the short form is one argument away:

``` python
nlp.add_pipe("ests_basic", name="basic", last=True)
doc = nlp("El gato duerme")
doc._.basic.n_words
```

Without `name` the pipe and the extension keep the name of the factory (`doc._.ests_basic`). The same component can be added twice under different names, which is how two presets or two sets of parameters live in one pipeline.

!!! warning "Serialization"
    A component keeps an object of statistics in `doc._.<name>`, and spaCy cannot serialize it: `Doc.to_bytes()`, `DocBin(store_user_data=True)` and `nlp.pipe(..., n_process>1)` fail with these components in the pipeline. To save a document, leave the user data out (`doc.to_bytes(exclude=["user_data"])`) or keep `doc._.<name>.get_stats()` on your own; for multiprocessing compute the statistics in the main process after `nlp.pipe`, without the components.

## What each component needs { #requirements }

| Component | Factory | Statistics | Needs |
| :-------: | :-----: | :--------: | :---: |
| `BasicStatsComponent` | `ests_basic` | [BasicStats](stats/basic_stats.md) | nothing |
| `ReadabilityStatsComponent` | `ests_readability` | [ReadabilityStats](stats/readability_stats.md) | nothing |
| `DiversityStatsComponent` | `ests_diversity` | [DiversityStats](stats/diversity_stats.md) | nothing |
| `MorphStatsComponent` | `ests_morph` | [MorphStats](stats/morph_stats.md) | a tagger before it |
| `SyntaxStatsComponent` | `ests_syntax` | [SyntaxStats](stats/syntax_stats.md) | a parser before it |
| `CohesionStatsComponent` | `ests_cohesion` | [CohesionStats](stats/cohesion_stats.md) | a tagger before it |

A component whose annotation is missing - one of the last three in a pipeline of `spacy.blank("es")` - raises `SourceError` when the document goes through it.

## BasicStatsComponent

!!! info ""
    **ests.components.BasicStatsComponent**

The component of the basic statistics of a text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_basic"` | Name of the component in the pipeline |

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    import ests
    import spacy

    # Load the model of spaCy
    nlp = spacy.load("es_core_news_sm")

    # Add the component
    nlp.add_pipe("ests_basic", name="basic", last=True)

    # Read the computed statistics
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.basic.n_words, doc._.basic.c_letters
    ```

    _Result_:

    ``` bash
    (12, {2: 5, 3: 1, 4: 1, 5: 1, 6: 3, 7: 1})
    ```

## ReadabilityStatsComponent

!!! info ""
    **ests.components.ReadabilityStatsComponent**

The component of the readability metrics of a text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_readability"` | Name of the component in the pipeline |
| `preset` | str | `"general"` | Preset of the coefficients (`general`, `classic`) |

An unknown preset raises `ParameterError` when the component is added, not when a document goes through it.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Add the component with the classic coefficients
    nlp.add_pipe(
        "ests_readability",
        name="readability_classic",
        config={"preset": "classic"},
        last=True,
    )

    # Read the computed metrics
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.readability_classic.flesch_reading_easy, 2)
    ```

    _Result_:

    ``` bash
    105.72
    ```

## DiversityStatsComponent

!!! info ""
    **ests.components.DiversityStatsComponent**

The component of the lexical diversity metrics of a text.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_diversity"` | Name of the component in the pipeline |
| `window_len` | int | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | float | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | int | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | int | `42` | Sample size for HD-D |
| `log_base` | float | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

A parameter out of its range raises `ParameterError` when the component is added.

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Add the component with a natural logarithm and a window of 100 words
    nlp.add_pipe(
        "ests_diversity",
        name="diversity_ln",
        config={"window_len": 100, "log_base": 2.718281828459045},
        last=True,
    )

    # Read the computed metrics
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.diversity_ln.ttr, 3)
    ```

    _Result_:

    ``` bash
    0.833
    ```

## MorphStatsComponent

!!! info ""
    **ests.components.MorphStatsComponent**

The component of the morphological statistics of a text. The parts of speech and the features are read from the annotation of the model, so the pipeline needs a tagger before the component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_morph"` | Name of the component in the pipeline |

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Add the component
    nlp.add_pipe("ests_morph", name="morph", last=True)

    # Read the computed statistics
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.morph.pos[:4]
    ```

    _Result_:

    ``` bash
    ('DET', 'NOUN', 'VERB', 'ADP')
    ```

## SyntaxStatsComponent

!!! info ""
    **ests.components.SyntaxStatsComponent**

The component of the syntactic statistics of a text. The statistics are computed on the dependency tree, so the pipeline needs a parser before the component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_syntax"` | Name of the component in the pipeline |

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Add the component
    nlp.add_pipe("ests_syntax", name="syntax", last=True)

    # Read the computed statistics
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.syntax.tree_depth, doc._.syntax.mean_dependency_distance
    ```

    _Result_:

    ``` bash
    (2.0, 1.6)
    ```

## CohesionStatsComponent

!!! info ""
    **ests.components.CohesionStatsComponent**

The component of the cohesion statistics of a text. The features are read from the annotation of the model, so the pipeline needs a tagger before the component.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `nlp` | Language | `-` | Language object |
| `name` | str | `"ests_cohesion"` | Name of the component in the pipeline |

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Add the component
    nlp.add_pipe("ests_cohesion", name="cohesion", last=True)

    # Read the computed statistics
    doc = nlp("El informe fue aprobado. Sin embargo, el informe no resuelve el problema.")
    doc._.cohesion.noun_overlap_adjacent, round(doc._.cohesion.connectors, 2)
    ```

    _Result_:

    ``` bash
    (1.0, 83.33)
    ```

## Everything in one pipeline { #pipeline }

The six components can live side by side, and then one pass over a document gives every statistic of the library that a `Doc` can carry.

!!! example "Example"

    _Code_:

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

    _Result_:

    ``` bash
    (12, 102.19, 0.833, ('DET', 'NOUN'), 2.0, 0.0)
    ```
