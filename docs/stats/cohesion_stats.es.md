# Estadísticas de cohesión

``` {.python .signature}
CohesionStats(source, sents_extractor=None, connectors=None, nlp=None)
```

Las estadísticas de cohesión de un texto a la manera de [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664) y de su adaptación española [Coh-Metrix-Esp](https://aclanthology.org/L16-1745/): la repetición entre las oraciones, la información dada, la cohesión temporal y los conectores de un diccionario. Las oraciones se comparan por lemas. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy), y tiene que estar anotada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`, sin las entidades nombradas, y un `Doc` debe llevar las categorías gramaticales, que vienen de un `morphologizer` (o de un `tagger` con un `attribute_ruler`), y los lemas, que vienen de un `lemmatizer`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un extractor de otra clase, un pipeline en `nlp` que no es un `Language` de spaCy, unos conectores que no son un diccionario de locuciones y pares de cadenas;
- `SourceError` - una fuente sin palabras; un `Doc` sin las categorías gramaticales o los lemas (un `Doc` de `spacy.blank("es")`); una cadena más larga que el `max_length` del pipeline o con un carácter sin forma UTF-8;
- `ParameterError` - una clase o un tipo de conector desconocidos;
- `DatasetNotFoundError` - una cadena sin `nlp` cuando el modelo no está instalado.

La clase extiende el `CohesionStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/) con la capa del español. Un `Doc` sin límites de oración - de un pipeline sin analizador - se divide en oraciones con el [`SentsExtractor`](../extractors/sentences.md) del español. Los rasgos de las palabras vienen de la anotación de [Universal Dependencies](https://universaldependencies.org/u/feat/), la cohesión temporal compara el tiempo y el modo de los verbos, y los conectores los halla [`SpanishConnectorMatcher`](#ConnectorMatcher) en el diccionario de [`load_connectors`](#connectors). La tabla de `print_stats` toma las descripciones de `COHESION_STATS_DESC` de `ests.constants`.

El `max_length` del pipeline es de un millón de caracteres por defecto: divida un texto más largo en partes o suba `max_length` en un pipeline propio y páselo en `nlp`.

Las palabras se clasifican por la anotación de Universal Dependencies:

| Noción | Universal Dependencies |
| :----- | :--------------------- |
| Sustantivos | `NOUN`, `PROPN` |
| Pronombres | `PRON` y los determinantes que señalan algo: posesivos (`Poss=Yes`), demostrativos o personales (`PronType=Dem`, `Prs`) - `mi libro` y `este libro` llevan un pronombre, `el libro` y `cada libro` no, ni tampoco los cuantificadores y los indefinidos (`cada`, `todos`, `ningún`, `otro`, `cualquier`) |
| Argumentos | `NOUN`, `PROPN`, `PRON`, sin los determinantes que cuentan como pronombres |
| Palabras con contenido | `CONTENT_UD_POS` de `anyts.constants` (`NOUN`, `PROPN`, `ADJ`, `VERB`, `ADV`) sin los demostrativos |
| Demostrativos | `PronType=Dem` |
| Tiempo y modo | rasgos `Tense` y `Mood` |

=== "Código"

    ``` python
    from ests import CohesionStats

    text = (
        "El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve "
        "el problema. Es decir, la comisión aplazó la decisión. Por lo tanto, el "
        "problema sigue abierto."
    )
    cs = CohesionStats(text)
    cs.print_stats()
    ```

=== "Resultado"

    ```
                                 Statistic                             |  Value
    ------------------------------------------------------------------------------
    Noun overlap in adjacent sentences                                 |   0.33
    Noun overlap in all pairs of sentences                             |   0.50
    Argument overlap in adjacent sentences                             |   0.33
    Argument overlap in all pairs of sentences                         |   0.50
    Content word overlap in adjacent sentences                         |   0.33
    Content word overlap in all pairs of sentences                     |   0.50
    Share of shared content words in adjacent sentences                |   0.08
    Share of shared content words in all pairs of sentences            |   0.12
    Share of the nouns of a sentence repeated in the next two          |   0.60
    Share of the arguments of a sentence repeated in the next two      |   0.60
    Share of the content words of a sentence repeated in the next two  |   0.38
    Share of the nouns of a paragraph repeated in the next one         |   nan
    Share of the arguments of a paragraph repeated in the next one     |   nan
    Share of the content words of a paragraph repeated in the next one |   nan
    Share of pronouns                                                  |   0.03
    Ratio of pronouns to nouns                                         |   0.09
    Share of demonstratives                                            |   0.00
    Share of content words seen before                                 |   0.18
    Repetition of the tense in adjacent sentences                      |   0.00
    Repetition of the mood in adjacent sentences                       |   1.00
    Temporal cohesion                                                  |   0.50
    Connectors per 1000 words                                          |  103.45
    Connectors linking a sentence to the ones before per 1000 words    |  103.45
    Connectors linking the parts of a sentence per 1000 words          |   0.00
    Causal connectors per 1000 words                                   |  34.48
    Adversative connectors per 1000 words                              |  34.48
    Concessive connectors per 1000 words                               |   0.00
    Temporal connectors per 1000 words                                 |   0.00
    Additive connectors per 1000 words                                 |   0.00
    Conditional connectors per 1000 words                              |   0.00
    Reformulative connectors per 1000 words                            |  34.48
    Primary connectors per 1000 words                                  |   0.00
    Secondary connectors per 1000 words                                |  103.45
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos: un texto o un `Doc` con las categorías gramaticales y los lemas |
| `sents_extractor` | `SentsExtractor` | `None` | Herramienta de extracción de oraciones; si se indica, divide un texto y un `Doc` por su texto, sean cuales sean los límites de oración del pipeline |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Clase y tipo por conector; el diccionario de `load_connectors` por defecto |
| `nlp` | `Language` | `None` | Pipeline de spaCy que analiza una cadena; si no se indica, el modelo `es_core_news_sm` de `ests.utils.get_nlp` |

## Atributos

<!-- core: stats/cohesion_stats.md:CohesionStats-attributes b48ff23 -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `words`, `lemmas` | `tuple[tuple[str]]` | Palabras y lemas de cada oración con palabras |
| `n_sents`, `n_words` | `int` | Números de las oraciones con palabras y de las palabras |
| `n_paragraphs` | `int` | Número de los párrafos, las partes del texto entre líneas en blanco que tienen palabras |
| `n_nouns`, `n_pronouns`, `n_demonstratives`, `n_content_words` | `int` | Números de las palabras por clase |
| `n_given` | `int` | Número de las palabras con contenido cuyo lema ya apareció antes |
| `n_connectors`, `connector_spans`, `c_connectors` | `int`, `tuple[Connector]`, `dict[str, int]` | Número de los conectores, sus apariciones y su número por conector |
| `n_inter_connectors` | `int` | Número de los conectores interoracionales |

El extractor indicado se guarda en el atributo `sents_extractor`, `None` sin él.

=== "Código"

    ``` python
    cs.lemmas[1]
    cs.n_nouns, cs.n_pronouns, cs.n_content_words, cs.n_given
    cs.connector_spans
    cs.c_connectors
    ```

=== "Resultado"

    ```
    ('sin', 'embargo', 'el', 'informe', 'no', 'resolver', 'el', 'problema')
    (11, 1, 17, 3)
    (Connector(sent=1, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary'),
     Connector(sent=2, start=0, end=2, text='es decir', cls='reformulative', kind='secondary'),
     Connector(sent=3, start=0, end=3, text='por lo tanto', cls='causal', kind='secondary'))
    {'es decir': 1, 'por lo tanto': 1, 'sin embargo': 1}
    ```

## Métricas

Cada métrica es un atributo del objeto, calculado al crearlo, y `get_stats` da las métricas de la tabla; `aspect_repetition` es un atributo fuera de él.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`noun_overlap_adjacent`](#overlap) | Proporción de los pares de oraciones contiguas que comparten un sustantivo | 0-1, `nan` con una sola oración | Oraciones vecinas más unidas |
| [`noun_overlap_all`](#overlap) | Proporción de todos los pares de oraciones que comparten un sustantivo | 0-1, `nan` con una sola oración | Todo el texto más unido |
| [`argument_overlap_adjacent`](#overlap) | Proporción de los pares contiguos que comparten un sustantivo o un pronombre | 0-1, `nan` con una sola oración | Oraciones vecinas más unidas |
| [`argument_overlap_all`](#overlap) | Proporción de todos los pares que comparten un sustantivo o un pronombre | 0-1, `nan` con una sola oración | Todo el texto más unido |
| [`content_overlap_adjacent`](#overlap) | Proporción de los pares contiguos que comparten una palabra con contenido | 0-1, `nan` con una sola oración | Oraciones vecinas más unidas |
| [`content_overlap_all`](#overlap) | Proporción de todos los pares que comparten una palabra con contenido | 0-1, `nan` con una sola oración | Todo el texto más unido |
| [`content_overlap_prop_adjacent`](#proportional_overlap) | Proporción media de las palabras con contenido compartidas (Dice) en los pares contiguos | 0-1, `nan` con una sola oración | Más palabras compartidas por las vecinas |
| [`content_overlap_prop_all`](#proportional_overlap) | Proporción media de las palabras con contenido compartidas (Dice) en todos los pares | 0-1, `nan` con una sola oración | Más palabras compartidas en todo el texto |
| [`noun_overlap_2_sent`](#forward_overlap) | Proporción de los sustantivos de una oración repetidos en una de las dos siguientes | 0-1, `nan` con menos de tres oraciones | Sustantivos que llegan más lejos |
| [`argument_overlap_2_sent`](#forward_overlap) | Proporción de los argumentos de una oración repetidos en una de las dos siguientes | 0-1, `nan` con menos de tres oraciones | Argumentos que llegan más lejos |
| [`content_overlap_2_sent`](#forward_overlap) | Proporción de las palabras con contenido de una oración repetidas en una de las dos siguientes | 0-1, `nan` con menos de tres oraciones | Palabras con contenido que llegan más lejos |
| [`noun_overlap_para`](#forward_overlap) | Proporción de los sustantivos de un párrafo repetidos en el siguiente | 0-1, `nan` con un solo párrafo | Párrafos más unidos |
| [`argument_overlap_para`](#forward_overlap) | Proporción de los argumentos de un párrafo repetidos en el siguiente | 0-1, `nan` con un solo párrafo | Párrafos más unidos |
| [`content_overlap_para`](#forward_overlap) | Proporción de las palabras con contenido de un párrafo repetidas en el siguiente | 0-1, `nan` con un solo párrafo | Párrafos más unidos |
| [`p_pronouns`](#pronouns) | Proporción de los pronombres entre las palabras | 0-1 | Más referencia por pronombres |
| [`pronoun_noun_ratio`](#pronouns) | Razón entre los pronombres y los sustantivos | 0 o más, `nan` sin sustantivos | Más pronombres por sustantivo |
| [`p_demonstratives`](#pronouns) | Proporción de los demostrativos entre las palabras | 0-1 | Más referencia hacia atrás |
| [`p_given`](#given) | Proporción de las palabras con contenido cuyo lema ya apareció antes en el texto | 0-1, `nan` sin palabras con contenido | Más información dada |
| [`tense_repetition`](#temporal_cohesion) | Proporción de los pares de oraciones contiguas con el mismo tiempo dominante | 0-1, `nan` sin dos oraciones contiguas con el rasgo | Un tiempo más estable |
| [`mood_repetition`](#temporal_cohesion) | Proporción de los pares contiguos con el mismo modo dominante | 0-1, `nan` sin dos oraciones contiguas con el rasgo | Un modo más estable |
| [`temporal_cohesion`](#temporal_cohesion) | Media de las repeticiones del tiempo y del modo | 0-1, `nan` cuando una de ellas es `nan` | Un marco temporal más estable |
| [`connectors`](#connectors) | Conectores por 1000 palabras | 0-1000 | Más enlaces explícitos |
| [`connectors_inter`](#connectors) | Conectores que unen una oración con las anteriores por 1000 palabras | 0-1000 | Más enlaces entre oraciones |
| [`connectors_intra`](#connectors) | Conectores que unen las partes de una oración por 1000 palabras | 0-1000 | Más enlaces dentro de las oraciones |
| [`connectors_<class>`](#connectors) | Conectores de una clase por 1000 palabras: `causal`, `adversative`, `concessive`, `temporal`, `additive`, `conditional`, `reformulative` | 0-1000 | Más enlaces de la clase |
| [`connectors_primary`, `connectors_secondary`](#connectors) | Conectores primarios y secundarios por 1000 palabras | 0-1000 | Más enlaces del tipo |

Las funciones de la repetición, de la información dada y de las repeticiones del rasgo (`calc_overlap`, `calc_proportional_overlap`, `calc_overlaps`, `dice`, `count_given`, `calc_repetition`, `dominant`) son las de `anyts.cohesion_stats`, que esTS no reexporta; están en la [página de anyTS](https://sergeyshk.github.io/anyTS/stats/cohesion_stats/). `calc_forward_overlap` de la [repetición con los segmentos siguientes](#forward_overlap) se importa de `ests.cohesion_stats`.

<div class="metric-card" markdown>

### Repetición binaria { #overlap }

`noun_overlap_adjacent` · `noun_overlap_all` · `argument_overlap_adjacent` · `argument_overlap_all` · `content_overlap_adjacent` · `content_overlap_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

La repetición binaria de Coh-Metrix (CRFNO1, CRFAO1, CRFSO1 sobre los pares contiguos, CRFNOa, CRFAOa, CRFSOa sobre todos): la proporción de los pares de oraciones que comparten el lema de al menos un sustantivo, un argumento o una palabra con contenido; `nan` para un texto de menos de dos oraciones.

$$
\frac{\textrm{Número de pares que comparten un lema}}{\textrm{Número de pares}}
$$

</div>

<div class="metric-card" markdown>

### Repetición proporcional { #proportional_overlap }

`content_overlap_prop_adjacent` · `content_overlap_prop_all` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

La repetición proporcional de Coh-Metrix (CRFCWO1, CRFCWOa): el coeficiente de Dice de los conjuntos de los lemas de las palabras con contenido $A$ y $B$ de dos oraciones, promediado sobre los pares contiguos o sobre todos, 0 para dos oraciones sin palabras con contenido; `nan` para un texto de menos de dos oraciones.

$$
\frac{1}{\textrm{Número de pares}} \sum_{(A, B)} \frac{2 \times |A \cap B|}{|A| + |B|}
$$

</div>

<div class="metric-card" markdown>

### Repetición con las oraciones y los párrafos siguientes { #forward_overlap }

`noun_overlap_2_sent` · `argument_overlap_2_sent` · `content_overlap_2_sent` · `noun_overlap_para` · `argument_overlap_para` · `content_overlap_para` · [TAACO](https://doi.org/10.3758/s13428-015-0651-7)
{ .metric-meta }

<!-- core: stats/cohesion_stats.md:CohesionStats-forward_overlap 34e902e -->
La repetición contigua de TAACO, por los lemas de los sustantivos, de los argumentos y de las palabras con contenido: la proporción de los lemas distintos de una oración repetidos en una de las dos oraciones siguientes (`adjacent_overlap_2_*_sent`), y de un párrafo repetidos en el párrafo siguiente (`adjacent_overlap_*_para`), sobre todas las oraciones o párrafos que los tienen (`calc_forward_overlap`). A diferencia de la repetición binaria, un par de segmentos cuenta por la proporción de los lemas que comparten. Un párrafo es una parte del texto entre líneas en blanco que tiene palabras; una palabra que lleva `paragraph_start` abre uno, también dentro de una oración, como cuando un parser une un título a la oración siguiente. TAACO toma cada línea por un párrafo: un texto con un párrafo en cada línea y sin líneas en blanco es aquí un solo párrafo, y sus `*_para` son `nan`.

<!-- core: stats/cohesion_stats.md:calc_forward_overlap 7389f78 -->
``` {.python .signature}
calc_forward_overlap(sets, span=1)
```

La proporción de los elementos de un segmento repetidos en los siguientes: los elementos distintos de cada segmento seguido de `span` segmentos que están en alguno de ellos, entre los elementos distintos de esos segmentos; `nan` con no más segmentos que `span` o con segmentos sin elementos.

$$
\frac{\sum_{i=1}^{n-k} |A_i \cap (A_{i+1} \cup \dots \cup A_{i+k})|}{\sum_{i=1}^{n-k} |A_i|}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `sets` | `list[set[str]]` | - | Elementos de cada segmento |
| `span` | `int` | `1` | Número $k$ de los segmentos siguientes con los que se compara un segmento |

Unos segmentos que son una cadena, un `Doc`, un iterador o un segmento que no es una lista de cadenas lanzan `SourceTypeError`, y un alcance que no es un entero mayor que 0, `ParameterError`.

En esTS una cadena se analiza en un `Doc`, así que ambos se dividen en párrafos por las líneas en blanco entre sus tokens.

=== "Código"

    ``` python
    from ests.cohesion_stats import calc_forward_overlap

    calc_forward_overlap([{"gato", "ventana"}, {"pájaro"}, {"gato"}], span=2)
    text = (
        "El gato estaba en la ventana. Miraba a los pájaros.\n\n"
        "Los pájaros se fueron y el gato se durmió. Mañana el gato volverá a la ventana."
    )
    paragraphs = CohesionStats(text)
    paragraphs.n_paragraphs, paragraphs.noun_overlap_para, paragraphs.content_overlap_para
    ```

=== "Resultado"

    ```
    0.5
    (2, 1.0, 0.6)
    ```

</div>

<div class="metric-card" markdown>

### Pronombres y demostrativos { #pronouns }

`p_pronouns` · `pronoun_noun_ratio` · `p_demonstratives`
{ .metric-meta }

<!-- core: stats/cohesion_stats.md:CohesionStats-pronouns 6f16dbf -->
Los pronombres, los sustantivos y los demostrativos son las palabras que `analyze` marca así, con los rasgos de `word_info` por defecto.

$$
\frac{\textrm{Número de pronombres}}{\textrm{Número de palabras}}, \quad \frac{\textrm{Número de pronombres}}{\textrm{Número de sustantivos}}, \quad \frac{\textrm{Número de demostrativos}}{\textrm{Número de palabras}}
$$

En esTS son los de la tabla de las clases de palabras de arriba, los rasgos de [`token_info`](#token_info).

</div>

<div class="metric-card" markdown>

### Información dada { #given }

`p_given`
{ .metric-meta }

La proporción de las palabras con contenido cuyo lema ya apareció antes en el texto, incluida la oración actual; la primera aparición de un lema es nueva.

$$
\frac{\textrm{Número de palabras con contenido dadas}}{\textrm{Número de palabras con contenido}}
$$

</div>

<div class="metric-card" markdown>

### Cohesión temporal { #temporal_cohesion }

`tense_repetition` · `mood_repetition` · `temporal_cohesion` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

La repetición del tiempo de Coh-Metrix (SMTEMP): cada oración recibe el valor dominante del rasgo de sus verbos - el más frecuente, el primero de los igual de frecuentes -, y la métrica es la proporción de los pares de oraciones contiguas con el mismo valor; un par en el que una de las oraciones no tiene ningún verbo con el rasgo se omite, y sin un solo par así el valor es `nan`.

$$
\frac{\textrm{Número de pares con el mismo valor dominante}}{\textrm{Número de pares con el rasgo}}
$$

El español no tiene aspecto en la anotación de Universal Dependencies de los modelos, así que esTS compara el modo junto al tiempo (`temporal_features` es `("tense", "mood")`): `temporal_cohesion` es la media de `tense_repetition` y `mood_repetition`. El atributo `aspect_repetition` del núcleo es `nan` sin el rasgo `Aspect`.

</div>

<div class="metric-card" markdown>

### Conectores { #connectors }

`connectors` · `connectors_inter` · `connectors_intra` · `connectors_<class>` · `connectors_primary` · `connectors_secondary`
{ .metric-meta }

<!-- core: stats/cohesion_stats.md:CohesionStats-connectors 0332772 -->
Las apariciones de los conectores halladas en cada oración por el buscador de `connector_matcher_class`, por 1000 palabras. Un conector interoracional une una oración con las anteriores: abre una oración, salvo que el buscador lo tome por un subordinante (`is_subordinator`), cuya cláusula o sintagma pertenece a la misma oración; los demás son intraoracionales. Cada clase y cada tipo del buscador dan una densidad: `connectors_causal`, `connectors_adversative`, `connectors_concessive`, `connectors_temporal`, `connectors_additive`, `connectors_conditional`, `connectors_reformulative`, `connectors_primary` y `connectors_secondary` por defecto.

$$
1000 \cdot \frac{\textrm{Número de conectores}}{\textrm{Número de palabras}}
$$

Los subordinantes de esTS son los conectores de una palabra etiquetados `SCONJ` o `ADP` (`cuando`, `aunque`, `si`) y las locuciones conjuntivas y preposicionales de `CONNECTOR_SUBORDINATORS` (`ya que`, `a pesar de`, `siempre que`), salvo `porque` y `conque`, que abren una oración uniéndola a la anterior (`CONNECTOR_PARCELLATION`: `¿Por qué? Porque...`). En `Ya que estás aquí, ayúdame` el conector es intraoracional; en `No vino. Porque llovía.` y en `Sin embargo, no.` es interoracional. Las formas anafóricas de los subordinantes preposicionales (`a pesar de esto`, `gracias a ello`) son entradas propias del diccionario, que unen una oración con la anterior.

``` {.python .signature}
load_connectors()
```

El diccionario de conectores de esTS: el fichero `ests/resources/connectors.tsv`, 273 marcadores del discurso de Martín Zorraquino y Portolés (1999) y conjunciones de la NGLE, cada uno con su clase de `CONNECTOR_CLASSES` y su tipo de `CONNECTOR_KINDS` de `anyts.constants`. Las clases son los conectores causales, adversativos, temporales y aditivos de Coh-Metrix, con los concesivos, condicionales y reformulativos añadidos. El diccionario es de solo lectura y compartido por todos, así que un diccionario propio se pasa por el parámetro `connectors`.

| Clase | Clave | Ejemplos |
| :---- | :---- | :------- |
| Causal | `causal` | porque, por lo tanto, así que |
| Adversativa | `adversative` | pero, sin embargo, en cambio |
| Concesiva | `concessive` | aunque, a pesar de, de todos modos |
| Temporal | `temporal` | cuando, a continuación, por último |
| Aditiva (con los ordinales) | `additive` | y, además, por otra parte, en primer lugar |
| Condicional | `conditional` | si, a menos que, de lo contrario |
| Reformulativa (con los operadores de concreción) | `reformulative` | es decir, en resumen, por ejemplo, en particular, sobre todo |

Los conectores primarios (`primary`) son conjunciones, locuciones conjuntivas y adverbios (porque, aunque, además), los secundarios (`secondary`), locuciones lexicalizadas (sin embargo, por lo tanto, es decir). `si` abre también interrogativas indirectas, exclamaciones y comparaciones hipotéticas - cerca de un tercio de sus apariciones en el corpus de literatura - y no es conector tras un verbo que rige una interrogativa indirecta, tras un `¡` de apertura ([`is_connector_blocked`](#is_connector_blocked)) ni tras `como`, `cual`, `vaya` y `maldito` (`CONNECTOR_BLOCKED_BEFORE`: `como si fuera`, `vaya si lo sé`); las reglas hallan cerca de tres cuartas partes de estos `si` y descartan el 25 % de los conectores condicionales de la literatura. `siempre que` es temporal con indicativo y condicional con subjuntivo y se cuenta en su clase del diccionario. Las reglas por las que una palabra del diccionario cuenta como conector son las del [buscador](#ConnectorMatcher).

=== "Código"

    ``` python
    from ests.cohesion_stats import load_connectors

    connectors = load_connectors()
    len(connectors), connectors["por lo tanto"]
    ```

=== "Resultado"

    ```
    (273, ('causal', 'secondary'))
    ```

!!! warning "Aviso"
    Las palabras de un marcador se cuentan como cualquier otra: el sustantivo `embargo` de `sin embargo` es un sustantivo y una palabra con contenido de su oración, así que un texto que repite un marcador gana algo de repetición por ello.

</div>

## Métodos

Los métodos `get_stats`, `to_dataframe`, `print_stats` y `describe` son los de la [interfaz de las estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas de cohesión no tienen escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    cs.get_stats()
    cs.describe("p_given")
    ```

=== "Resultado"

    ```
    {'noun_overlap_adjacent': 0.3333333333333333,
     'noun_overlap_all': 0.5,
     'argument_overlap_adjacent': 0.3333333333333333,
     'argument_overlap_all': 0.5,
     'content_overlap_adjacent': 0.3333333333333333,
     'content_overlap_all': 0.5,
     'content_overlap_prop_adjacent': 0.08333333333333333,
     'content_overlap_prop_all': 0.12037037037037035,
     'noun_overlap_2_sent': 0.6,
     'argument_overlap_2_sent': 0.6,
     'content_overlap_2_sent': 0.375,
     'noun_overlap_para': nan,
     'argument_overlap_para': nan,
     'content_overlap_para': nan,
     'p_pronouns': 0.034482758620689655,
     'pronoun_noun_ratio': 0.09090909090909091,
     'p_demonstratives': 0.0,
     'p_given': 0.17647058823529413,
     'tense_repetition': 0.0,
     'mood_repetition': 1.0,
     'temporal_cohesion': 0.5,
     'connectors': 103.44827586206898,
     'connectors_inter': 103.44827586206898,
     'connectors_intra': 0.0,
     'connectors_causal': 34.48275862068966,
     'connectors_adversative': 34.48275862068966,
     'connectors_concessive': 0.0,
     'connectors_temporal': 0.0,
     'connectors_additive': 0.0,
     'connectors_conditional': 0.0,
     'connectors_reformulative': 34.48275862068966,
     'connectors_primary': 0.0,
     'connectors_secondary': 103.44827586206898}
    None
    ```

## Buscador de conectores { #ConnectorMatcher }

``` {.python .signature}
SpanishConnectorMatcher(connectors)
```

<!-- core: stats/cohesion_stats.md:ConnectorMatcher 4bd17e8 -->
La búsqueda de los conectores (marcadores del discurso: *porque*, *sin embargo*, *por otra parte*) de un diccionario en las oraciones de un texto. El diccionario da la clase de cada conector - causal, adversativa, concesiva, temporal, aditiva, condicional o reformulativa (`CONNECTOR_CLASSES`) - y su tipo, primario o secundario (`CONNECTOR_KINDS`). Un conector se reconoce por las formas normalizadas de sus palabras, el más largo en cada posición, sin solapamientos; un punto o un guion dentro de un conector puede quedar separado por el tokenizador (*e.g.* como `e`, `g`). Una aparición es un `Connector`: el número de la oración `sent`, las posiciones `start` y `end` de sus palabras, el conector `text` tal como lo escribe el diccionario, su clase `cls` y su tipo `kind`.

Excepciones:

- `SourceTypeError` - un diccionario que no es una correspondencia de una locución a un par de cadenas;
- `ParameterError` - una clase o un tipo desconocidos.

`SpanishConnectorMatcher` es una subclase del `ConnectorMatcher` del núcleo con las reglas del español; las palabras y los conectores se comparan en minúscula. Un conector de una palabra lleva una categoría de `CONNECTOR_POS` - conjunción, partícula, adverbio, adposición, interjección, nombre propio o `X` - o de `CONNECTOR_POS_EXTRA` para su forma (`pues` y `verbigracia` como `NOUN`, `resumiendo`, `recapitulando` y `concluyendo` como `VERB`). No es conector justo tras un determinante, así que `el antes y el después` lleva un conector, `y`, y no tres; y como nombre propio cuenta solo al principio de la oración, donde los modelos leen así un marcador (`Primeramente`), de modo que el apellido de `Habló con Juan Luego ayer` no es conector. Un marcador que forma parte de otra locución se descarta: las palabras que lo siguen de `CONNECTOR_BLOCKED_AFTER` (`antes de la reunión`, `en cuanto a`, `a pesar de todo lo que`), las que lo preceden de `CONNECTOR_BLOCKED_BEFORE` (`algo así como`, `como si fuera`) y las categorías de la palabra siguiente de `CONNECTOR_BLOCKED_AFTER_POS` (`sobre todo el texto`, `a pesar de todo el esfuerzo`) lo anulan, mientras que `antes, firmó el acta` y `sobre todo cuando llueve` cuentan su marcador. Algunos marcadores dependen de su lugar: `pues` al principio de la oración abre una réplica (`Pues bien`) y no es conector (`CONNECTOR_NOT_AT_START`), y `encima` cuenta dentro de la oración solo tras `y`, `e`, `ni` o `pero` (`y encima llueve`, `CONNECTOR_ONLY_AFTER`). Estas listas son atributos del buscador: `CONNECTOR_POS` es `pos_tags`, las demás se llaman sin `CONNECTOR_` en minúscula (`CONNECTOR_BLOCKED_AFTER` es `blocked_after`); `not_after_pos` es el determinante `DET`, `start_only_pos` el nombre propio `PROPN`, y `read_through_marks` está vacío en esTS. Un signo de puntuación dentro de una locución conjuntiva que acaba en `que`, `como` o `si` (`CONNECTOR_SPLIT_BY_MARKS`) hace de la conjunción una palabra aparte, así que `No tire así, que se romperá` y `lo de siempre, que...` no tienen conector; las locuciones consecutivas con `de modo`, `de manera`, `de forma` o `de suerte` (`de modo que`, `de tal manera que`) y `bien es verdad que` quedan fuera, porque los textos antiguos ponen una coma antes de su `que` (`de tal modo, que`).

<!-- core: stats/cohesion_stats.md:ConnectorMatcher-find 8e0022c -->
`find(words, sent_index, pos, breaks, blocked)` devuelve las apariciones de los conectores en una oración en el orden de sus palabras. Las palabras son las de una oración sin puntuación, la primera su inicio. Con las categorías gramaticales, un conector de una palabra cuenta solo con una de `pos_tags` o de `pos_extra` para su forma, nunca tras una de `not_after_pos`, y con una de `start_only_pos` solo al principio de la oración; una palabra sin categoría (`None`) pasa. Sin las categorías gramaticales se omiten las reglas que las leen. Las posiciones de los signos de puntuación `breaks` separan un conector de sus vecinas: una regla no lee una palabra a través de un signo, así que en *so, the end* la palabra tras la coma ni bloquea el conector ni le deja contar, salvo que el conector sea uno de `read_through_marks`, y un signo entre las palabras de un conector de `split_by_marks` lo anula; sin ellas las palabras se leen como contiguas. Ningún conector empieza en una palabra de `blocked`, que una lengua descarta por algo más que las palabras y sus categorías gramaticales, como su análisis sintáctico.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `words` | `list[str]` | - | Palabras de la oración |
| `sent_index` | `int` | `0` | Número de la oración, escrito en las apariciones |
| `pos` | `list[str]` | `None` | Categorías gramaticales de las palabras |
| `breaks` | `set[int]` | `None` | Posiciones de las palabras precedidas por un signo de puntuación |
| `blocked` | `set[int]` | `None` | Posiciones de las palabras en las que no empieza ningún conector |

Unas palabras que no son una lista de cadenas, unas categorías gramaticales que no son una lista de cadenas y `None` (las etiquetas `token.pos_` de spaCy, no los números `token.pos`) y unas posiciones que no son una colección lanzan `SourceTypeError`; un número de oración o una posición que no es un entero, una posición de un signo que no es la de una palabra después de la primera, una posición bloqueada que no es la de una palabra y unas categorías gramaticales que no son tantas como las palabras, `ParameterError`.

`CohesionStats` pasa las posiciones de los signos de puntuación de cada oración, así que en `sin gracia alguna, y el amor` la coma separa `y` del determinante `alguna` y cuenta, y `encima` tras una coma también cuenta.

=== "Código"

    ``` python
    from ests.cohesion_stats import SpanishConnectorMatcher, load_connectors

    matcher = SpanishConnectorMatcher(load_connectors())
    words = ["Vivía", "sin", "gracia", "alguna", "y", "el", "amor", "llegó"]
    pos = ["VERB", "ADP", "NOUN", "DET", "CCONJ", "DET", "NOUN", "VERB"]
    matcher.find(words, pos=pos)
    matcher.find(words, pos=pos, breaks={4})
    ```

=== "Resultado"

    ```
    []
    [Connector(sent=0, start=4, end=5, text='y', cls='additive', kind='primary')]
    ```

<!-- core: stats/cohesion_stats.md:ConnectorMatcher-is_subordinator 6913020 -->
`is_subordinator(connector, pos=None)` comprueba si una aparición de un conector une su cláusula o su sintagma a su propia oración: un conector de `subordinators`, o un conector de una palabra cuya categoría `pos` es `SCONJ` o `ADP`, pero ninguno de `parcellation`. La cláusula de una conjunción subordinante y el sintagma de una preposición pertenecen a la oración del conector esté donde esté, así que un subordinante que abre una oración (*when he came, ...*, *despite the rain, ...*) no la une con las anteriores. Un conector que no es un `Connector` lanza `SourceTypeError`.

`subordinators` es `CONNECTOR_SUBORDINATORS` y `parcellation` es `CONNECTOR_PARCELLATION`.

=== "Código"

    ``` python
    matcher.is_subordinator(matcher.find(["Ya", "que", "estás", "aquí"])[0])
    matcher.is_subordinator(matcher.find(["Porque", "llovía"])[0], "SCONJ")
    ```

=== "Resultado"

    ```
    True
    False
    ```

## Búsqueda de conectores { #find_connectors }

``` {.python .signature}
find_connectors(words, connectors=None, sent_index=0, pos=None, breaks=None)
```

Busca los conectores de una oración con el método `find` de `SpanishConnectorMatcher` en el diccionario `connectors`, el de `load_connectors` por defecto; los demás parámetros y las excepciones son los del buscador y de `find`. Sin `breaks`, las posiciones de las palabras ante las que hay un signo de puntuación ([`find_marks`](https://sergeyshk.github.io/anyTS/utils/words/#find_marks) de una cadena), las palabras se leen como contiguas. Con un diccionario propio la función construye un buscador en cada llamada, así que para muchas oraciones construya `SpanishConnectorMatcher(connectors)` una vez y llame a su `find`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `connectors` | `dict[str, tuple[str, str]]` | `None` | Clase y tipo por conector |

=== "Código"

    ``` python
    from ests.cohesion_stats import find_connectors

    find_connectors(["Sin", "embargo", "no", "vino"])
    find_connectors(["El", "antes", "y", "el", "después"], pos=["DET", "NOUN", "CCONJ", "DET", "NOUN"])
    find_connectors(["No", "tire", "así", "que", "se", "romperá"], breaks={3})
    ```

=== "Resultado"

    ```
    [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]
    [Connector(sent=0, start=2, end=3, text='y', cls='additive', kind='primary')]
    []
    ```

## Rasgos de las palabras { #token_info }

``` {.python .signature}
token_info(token)
```

Los rasgos de un token de spaCy para las estadísticas de cohesión según su anotación de Universal Dependencies, por la tabla de las clases de palabras: una tupla con nombre `WordInfo` con `lemma` (el `lemma_` del token en minúscula), `noun`, `pronoun`, `demonstrative`, `argument`, `content`, `tense` y `mood` (el primer valor de `Tense` y de `Mood`, `None` sin él). [`LexicalStats`](lexical_stats.md) toma de ella sus palabras con contenido.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token de spaCy |

=== "Código"

    ``` python
    from ests.cohesion_stats import token_info
    from ests.utils import get_nlp

    doc = get_nlp()("Mi hermano miraba este libro.")
    token_info(doc[2])
    token_info(doc[3])
    ```

=== "Resultado"

    ```
    WordInfo(lemma='mirar', noun=False, pronoun=False, demonstrative=False, argument=False, content=True, tense='Imp', mood='Ind')
    WordInfo(lemma='este', noun=False, pronoun=True, demonstrative=True, argument=False, content=False, tense=None, mood=None)
    ```

## Conectores bloqueados { #is_connector_blocked }

``` {.python .signature}
is_connector_blocked(token)
```

Comprueba si ningún conector empieza en un token por las palabras que lo preceden en un `Doc`: un `si` que no abre ninguna condición. Es así tras un verbo de `CONNECTOR_QUESTION_VERBS` - `saber`, `ver`, `mirar`, `preguntar`, `dudar`, `ignorar`, `pensar`, `averiguar`, `probar`, `comprobar`, `observar`, `examinar`, `determinar`, `decidir`, `considerar`, `consultar`, `investigar`, `adivinar` - etiquetado `VERB` o `AUX`, por el lema del modelo o de `ests.utils.lemmatize` (`no sé si vendrá`, `a ver si llega`, `preguntó si tenía hambre`), y tras un `¡` de apertura (`¡Si ya te lo dije!`). En una muestra de la literatura la regla de los verbos acertó en todos los casos revisados, la de `¡` en unos nueve de cada diez. `CohesionStats` fija con ella el `connector_blocked` de las palabras del núcleo, y la capa [`connectors`](../visualizers/highlight.md) del resaltado de un `Doc` descarta los mismos `si`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token de spaCy |

=== "Código"

    ``` python
    from ests.cohesion_stats import is_connector_blocked
    from ests.utils import get_nlp

    doc = get_nlp()("No sé si vendrá. Si llueve, me quedo. ¡Si ya te lo dije!")
    [is_connector_blocked(token) for token in doc if token.lower_ == "si"]
    ```

=== "Resultado"

    ```
    [True, False, True]
    ```
