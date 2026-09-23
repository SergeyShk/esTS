# Estadísticas de cohesión

!!! info ""
    **ests.cohesion_stats.CohesionStats**

## Descripción

Módulo para calcular las estadísticas de cohesión de un texto a la manera de [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) y de su adaptación española [Coh-Metrix-Esp](https://aclanthology.org/W16-4105/): la repetición de sustantivos, de argumentos y de palabras con contenido entre oraciones, la información dada, la cohesión temporal y la densidad de los marcadores del discurso.

Las oraciones se comparan por lemas, y los rasgos vienen de la anotación de [Universal Dependencies](https://universaldependencies.org/u/feat/), así que la fuente tiene que estar etiquetada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`, y un `Doc` debe llevar las categorías gramaticales. Sin límites de oración - un pipeline con etiquetador pero sin analizador - las oraciones se toman del texto con [`SentsExtractor`](../extractors/sentences.md).

Un texto más largo que el `max_length` del pipeline - un millón de caracteres por defecto - levanta `SourceError`: divídalo en partes o suba `max_length` en un pipeline propio y páselo en `nlp`.

!!! note "Nota"
    Las estadísticas se calculan al inicializar el objeto `CohesionStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (cadena u objeto Doc) |
| `sents_extractor` | SentsExtractor | `None` | Herramienta de extracción de oraciones, usada con un Doc sin límites de oración |
| `connectors` | dict[str, tuple[str, str]] | `None` | Diccionario de conectores: clase y tipo por conector; sin él se usa el diccionario de la biblioteca |
| `nlp` | Language | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Cohesión referencial { #reference }

La repetición de Coh-Metrix: un par de oraciones es cohesivo cuando comparten el lema de un sustantivo (CRFNO), de un argumento - sustantivo o pronombre - (CRFAO) o de una palabra con contenido (CRFSO). Las medidas binarias dan la proporción de esos pares entre las oraciones contiguas y entre todos los pares del texto; las proporcionales (CRFCWO) dan el coeficiente de Dice medio de los conjuntos de lemas, `2·|A ∩ B| / (|A| + |B|)`.

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `noun_overlap_adjacent` | float | Proporción de pares contiguos que comparten un sustantivo |
| `noun_overlap_all` | float | Proporción de todos los pares que comparten un sustantivo |
| `argument_overlap_adjacent` | float | Proporción de pares contiguos que comparten un sustantivo o un pronombre |
| `argument_overlap_all` | float | Proporción de todos los pares que comparten un sustantivo o un pronombre |
| `content_overlap_adjacent` | float | Proporción de pares contiguos que comparten una palabra con contenido |
| `content_overlap_all` | float | Proporción de todos los pares que comparten una palabra con contenido |
| `content_overlap_prop_adjacent` | float | Proporción media de palabras con contenido compartidas en pares contiguos |
| `content_overlap_prop_all` | float | Proporción media de palabras con contenido compartidas en todos los pares |
| `p_pronouns` | float | Proporción de pronombres entre las palabras |
| `pronoun_noun_ratio` | float | Razón entre el número de pronombres y el de sustantivos |
| `p_demonstratives` | float | Proporción de demostrativos entre las palabras |
| `p_given` | float | Proporción de palabras con contenido cuyo lema ya apareció antes en el texto |
| `tense_repetition` | float | Proporción de pares contiguos con el mismo tiempo dominante |
| `mood_repetition` | float | Proporción de pares contiguos con el mismo modo dominante |
| `temporal_cohesion` | float | Media de la repetición del tiempo y del modo |

Un sustantivo es `NOUN` o `PROPN` y una palabra con contenido es un `NOUN`, `PROPN`, `ADJ`, `VERB` o `ADV`. Un pronombre es un `PRON` o un determinante que señala algo - un posesivo (`Poss=Yes`) o uno demostrativo o personal (`PronType=Dem`, `Prs`) -, de modo que `mi libro` y `este libro` llevan un pronombre y `el libro` y `cada libro` no: los cuantificadores y los indefinidos (`cada`, `todos`, `ningún`, `otro`, `cualquier`) no señalan nada e inflarían alrededor de un quinto una medida de densidad anafórica. Un demostrativo lleva `PronType=Dem`.

Un argumento es un `NOUN`, `PROPN` o `PRON`, dejando fuera los determinantes aunque cuenten como pronombres: la repetición de argumentos de Coh-Metrix se hace con sustantivos y pronombres propiamente dichos, y el lema de `este` en dos oraciones no remite a la misma cosa.

La cohesión temporal sigue el SMTEMP de Coh-Metrix: de cada oración se toma el valor dominante del rasgo de sus verbos, y un par de oraciones contiguas cuenta como cohesivo cuando los valores coinciden. El español no tiene aspecto en Universal Dependencies, así que el modo ocupa su lugar junto al tiempo: el paso del indicativo al subjuntivo es lo que rompe el marco temporal de un texto español. Los pares en los que una de las oraciones no tiene ningún verbo con el rasgo se omiten, y un texto de menos de dos oraciones deja en `nan` todas las medidas de esta sección.

## Conectores { #connectors }

Los marcadores del discurso de la clasificación de Martín Zorraquino y Portolés, 255 en `ests/resources/connectors.tsv`, en siete clases y dos tipos: primarios - conjunciones, locuciones conjuntivas y adverbios (`porque`, `aunque`, `además`) - y secundarios, las locuciones lexicalizadas (`sin embargo`, `por lo tanto`, `es decir`). La densidad se da por 1000 palabras.

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `connectors` | float | Conectores por 1000 palabras |
| `connectors_causal` | float | Conectores causales (`porque`, `por lo tanto`, `así que`) |
| `connectors_adversative` | float | Conectores adversativos (`pero`, `sin embargo`, `en cambio`) |
| `connectors_concessive` | float | Conectores concesivos (`aunque`, `a pesar de`, `de todos modos`) |
| `connectors_temporal` | float | Conectores temporales (`cuando`, `a continuación`, `por último`) |
| `connectors_additive` | float | Conectores aditivos (`y`, `además`, `por otra parte`) |
| `connectors_conditional` | float | Conectores condicionales (`si`, `a menos que`, `de lo contrario`) |
| `connectors_reformulative` | float | Conectores reformulativos (`es decir`, `en resumen`, `por ejemplo`) |
| `connectors_primary` | float | Conectores primarios por 1000 palabras |
| `connectors_secondary` | float | Conectores secundarios por 1000 palabras |

Los conectores se buscan por sus formas en minúscula: en cada posición se toma el más largo, de modo que `sin embargo` no se rompe en `sin`, y los hallados no se solapan. Las apariciones están en el atributo `connector_spans` y su distribución en `c_connectors`.

Dos reglas dejan fuera los usos corrientes de esas palabras. Un conector de una palabra cuenta solo con una categoría de `CONNECTOR_POS` - conjunción, partícula, adverbio, adposición, interjección - y nunca tras un determinante, así que `el antes y el después` lleva un conector, `y`, y no tres; un nombre propio cuenta solo al principio de la oración, donde los modelos leen así un marcador (`Primeramente`, `Concluyendo`), de modo que el apellido de `Ana, Luego y Mas firmaron` no es conector. Y un marcador que además encabeza un sintagma preposicional se descarta ahí: `antes de la reunión`, `después del informe`, `por encima de 80`, `al final de la línea`, `al principio de la oración`, `luego de la sesión` y `sobre todo el texto` no cuentan nada, mientras que `antes, firmó el acta`, `encima, no vino`, `al final, no vino` y `sobre todo cuando llueve` cuentan su marcador.

En `connectors` puede pasarse un diccionario propio: del conector a su clase de `CONNECTOR_CLASSES` y su tipo de `CONNECTOR_TYPES`, y uno desconocido levanta `ParameterError`.

!!! warning "Advertencia"
    Un marcador español suele ser una locución hecha de palabras corrientes, y esas palabras se cuentan como cualquier otra: el sustantivo `embargo` de `sin embargo` y el sustantivo `ejemplo` de `por ejemplo` son sustantivos y palabras con contenido de su oración, y un texto que repite un marcador gana algo de repetición por ello. Medido sobre las páginas españolas de este sitio, la diferencia es inferior a 0,002 en todas las repeticiones, pero en un texto hecho de marcadores sería mayor.

## Recuentos { #counts }

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[tuple[str, ...], ...] | Tupla de las palabras de cada oración |
| `lemmas` | tuple[tuple[str, ...], ...] | Tupla de los lemas de cada oración |
| `n_sents` | int | Número de oraciones con palabras |
| `n_words` | int | Número de palabras |
| `n_nouns` | int | Número de sustantivos |
| `n_pronouns` | int | Número de pronombres |
| `n_demonstratives` | int | Número de demostrativos |
| `n_content_words` | int | Número de palabras con contenido |
| `n_given` | int | Número de palabras con contenido cuyo lema ya apareció antes |
| `n_connectors` | int | Número de conectores |
| `connector_spans` | tuple[Connector] | Tupla de las apariciones de los conectores |
| `c_connectors` | dict[str, int] | Distribución de las apariciones por conector |

## Métodos

### get_stats

Devuelve un diccionario con las estadísticas de cohesión calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import CohesionStats

    # Preparar los datos
    text = (
        "El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve "
        "el problema. Es decir, la comisión aplazó la decisión. Por lo tanto, el "
        "problema sigue abierto."
    )

    # Calcular las estadísticas
    cs = CohesionStats(text)
    cs.get_stats()
    ```

    _Resultado_:

    ``` bash
    {'noun_overlap_adjacent': 0.3333333333333333,
    'noun_overlap_all': 0.5,
    'argument_overlap_adjacent': 0.3333333333333333,
    'argument_overlap_all': 0.5,
    'content_overlap_adjacent': 0.3333333333333333,
    'content_overlap_all': 0.5,
    'content_overlap_prop_adjacent': 0.08333333333333333,
    'content_overlap_prop_all': 0.12037037037037039,
    'p_pronouns': 0.034482758620689655,
    'pronoun_noun_ratio': 0.09090909090909091,
    'p_demonstratives': 0.0,
    'p_given': 0.17647058823529413,
    'tense_repetition': 0.0,
    'mood_repetition': 1.0,
    'temporal_cohesion': 0.5,
    'connectors': 103.44827586206898,
    'connectors_causal': 34.48275862068966,
    'connectors_adversative': 34.48275862068966,
    'connectors_concessive': 0.0,
    'connectors_temporal': 0.0,
    'connectors_additive': 0.0,
    'connectors_conditional': 0.0,
    'connectors_reformulative': 34.48275862068966,
    'connectors_primary': 0.0,
    'connectors_secondary': 103.44827586206898}
    ```

    Las apariciones de los conectores están en un atributo propio:

    ``` python
    cs.connector_spans
    # (Connector(sent=1, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary'),
    #  Connector(sent=2, start=0, end=2, text='es decir', cls='reformulative', kind='secondary'),
    #  Connector(sent=3, start=0, end=3, text='por lo tanto', cls='causal', kind='secondary'))
    ```

### print_stats

Muestra una tabla con las estadísticas de cohesión calculadas.

Para ilustrar el método reutilizamos el código del ejemplo anterior:

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de las estadísticas calculadas
    cs.print_stats()
    ```

    _Resultado_:

    ``` bash
                            Statistic                         |  Value
    --------------------------------------------------------------------
    Noun overlap in adjacent sentences                        |   0.33
    Noun overlap in all pairs of sentences                    |   0.50
    Argument overlap in adjacent sentences                    |   0.33
    Argument overlap in all pairs of sentences                |   0.50
    Content word overlap in adjacent sentences                |   0.33
    Content word overlap in all pairs of sentences            |   0.50
    Share of shared content words in adjacent sentences       |   0.08
    Share of shared content words in all pairs of sentences   |   0.12
    Share of pronouns                                         |   0.03
    Ratio of pronouns to nouns                                |   0.09
    Share of demonstratives                                   |   0.00
    Share of content words seen before                        |   0.18
    Repetition of the tense in adjacent sentences             |   0.00
    Repetition of the mood in adjacent sentences              |   1.00
    Temporal cohesion                                         |   0.50
    Connectors per 1000 words                                 |  103.45
    Causal connectors per 1000 words                          |  34.48
    Adversative connectors per 1000 words                     |  34.48
    Concessive connectors per 1000 words                      |   0.00
    Temporal connectors per 1000 words                        |   0.00
    Additive connectors per 1000 words                        |   0.00
    Conditional connectors per 1000 words                     |   0.00
    Reformulative connectors per 1000 words                   |  34.48
    Primary connectors per 1000 words                         |   0.00
    Secondary connectors per 1000 words                       |  103.45
    ```

## Búsqueda de conectores { #find_connectors }

!!! info ""
    **ests.cohesion_stats.find_connectors()**, **ests.cohesion_stats.load_connectors()**

`find_connectors(words, connectors=None, sent_index=0, pos=None)` halla los conectores de una sola oración y devuelve sus apariciones, y `load_connectors()` devuelve el diccionario de la biblioteca, la clase y el tipo por conector; el diccionario está en caché y es de solo lectura, así que un cambio se hace por el parámetro `connectors` y no sobre el objeto devuelto.

!!! example "Ejemplo"

    ``` python
    from ests.cohesion_stats import find_connectors, load_connectors

    find_connectors(["Sin", "embargo", "no", "vino"])
    # [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]

    find_connectors(["El", "antes", "y", "el", "después"], pos=["DET", "NOUN", "CCONJ", "DET", "NOUN"])
    # [Connector(sent=0, start=2, end=3, text='y', cls='additive', kind='primary')]

    load_connectors()["por lo tanto"]
    # ('causal', 'secondary')
    ```
