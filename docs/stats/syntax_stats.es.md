# Estadísticas sintácticas

``` {.python .signature}
SyntaxStats(source, nlp=None)
```

Las estadísticas sintácticas de un texto por su árbol de dependencias ([Ivanov, Solnyshkina y Solovyev 2018](https://dialogue-conf.org/media/4302/ivanovvv.pdf)): las medidas del árbol y de las construcciones sintácticas. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy), y tiene que estar analizada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`, sin las entidades nombradas, y un `Doc` debe llevar las dependencias, que vienen de un `parser`, y los lemas, que vienen de un `lemmatizer`. Los signos de puntuación, los símbolos (`%`, `€`, `+`) y los espacios no son nodos del árbol, y las distancias se cuentan en posiciones de palabras.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un pipeline en `nlp` que no es un `Language` de spaCy;
- `SourceError` - una fuente sin palabras; un `Doc` sin las dependencias o los lemas (un `Doc` de `spacy.blank("es")`, de un pipeline sin analizador o con el `lemmatizer` excluido); una cadena más larga que el `max_length` del pipeline o con un carácter sin forma UTF-8;
- `DatasetNotFoundError` - una cadena sin `nlp` cuando el modelo no está instalado.

La clase extiende el `SyntaxStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats/) con la capa del español. Las relaciones y los rasgos son los de la anotación de [Universal Dependencies](https://universaldependencies.org/u/dep/) de los modelos `es_core_news_sm`, `es_core_news_md` y `es_core_news_lg`, y las estadísticas valen lo que vale el análisis sintáctico. Las cláusulas, la pasiva, las negaciones y los predicados escindidos siguen las reglas del español descritas en las tarjetas de las métricas, y esTS añade sus propias métricas de las cadenas de `de`, las cláusulas de gerundio y las oraciones con `se`. Las construcciones del estilo administrativo - la pasiva con `ser` y con `se`, las cláusulas de participio y de gerundio, las cadenas de `de`, los predicados escindidos - son las que advierten las guías de lenguaje claro en español. La tabla de `print_stats` toma las descripciones de `SYNTAX_STATS_DESC` de `ests.constants`.

El `max_length` del pipeline es de un millón de caracteres por defecto: divida un texto más largo en partes o suba `max_length` en un pipeline propio y páselo en `nlp`.

=== "Código"

    ``` python
    from ests import SyntaxStats

    text = (
        "La revisión de las cuentas del organismo fue realizada por el comité. "
        "Se llevó a cabo la reforma, aprobada en 1998, sin que nadie hiciera "
        "mención de los problemas."
    )
    ss = SyntaxStats(text)
    ss.print_stats()
    ```

=== "Resultado"

    ```
                        Statistic                     |  Value
    -------------------------------------------------------------
    Mean dependency distance                          |   2.26
    Standard deviation of the dependency distance     |   2.15
    Mean of the longest dependencies of the sentences |   9.00
    Share of adjacent dependencies                    |   0.48
    Depth of the dependency tree                      |   4.00
    Leaves per sentence                               |   8.00
    Subtrees per sentence                             |   6.50
    Mean of the nodes per leaf of the sentences       |   1.80
    Valency of the finite verbs                       |   4.00
    Coordination chains per sentence                  |   0.00
    Mean length of a coordination chain               |   nan
    Clauses per sentence                              |   1.50
    Mean length of a clause (words)                   |   9.67
    Subordinate clauses per sentence                  |   0.50
    Share of sentences with a subordinate clause      |   0.50
    Infinitive clauses under a verb per sentence      |   0.00
    Modifiers per noun phrase                         |   1.00
    Chains of de per sentence                         |   0.50
    Maximum length of a chain of de                   |    2
    Participial clauses per sentence                  |   0.50
    Mean length of a participial clause (words)       |   3.00
    Gerund clauses per sentence                       |   0.00
    Mean length of a gerund clause (words)            |   nan
    Share of passive forms among the verbs            |   0.67
    Share of agentless forms among the passive ones   |   0.50
    Passives with se per sentence                     |   0.50
    Impersonal sentences with se per sentence         |   0.00
    Infinitives per sentence                          |   0.00
    Words of negation per sentence                    |   0.50
    Split predicates per sentence                     |   1.00
    Ratio of nouns to verbs                           |   3.00
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos: un texto o un `Doc` con las dependencias y los lemas |
| `nlp` | `Language` | `None` | Pipeline de spaCy que analiza una cadena; si no se indica, el modelo `es_core_news_sm` de `ests.utils.get_nlp` |

## Atributos

<!-- core: stats/syntax_stats.md:SyntaxStats-attributes a0c3c7a -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `sents` | `tuple[tuple[Token]]` | Palabras de cada oración con palabras, sobre una copia del `Doc` sin su tensor ni sus datos de usuario |
| `n_sents`, `n_words` | `int` | Números de las oraciones con palabras y de las palabras |
| `n_leaves`, `n_subtrees` | `int` | Números de las palabras sin dependientes y con ellas |
| `n_coordination_chains` | `int` | Número de las cadenas de coordinación |
| `n_clauses`, `n_subordinate_clauses`, `n_complex_sents` | `int` | Números de las cláusulas, de las cláusulas subordinadas y de las oraciones con alguna |
| `n_infinitive_clauses` | `int` | Número de las cláusulas de infinitivo bajo un verbo |
| `n_nouns`, `n_verbs` | `int` | Números de los sustantivos (`NOUN`, `PROPN`) y de las formas verbales (`VERB`) |
| `n_participle_clauses` | `int` | Número de las cláusulas de participio |
| `n_passive`, `n_agentless_passive` | `int` | Números de las formas pasivas y de las que no tienen agente |
| `n_infinitives`, `n_negations` | `int` | Números de los infinitivos y de las palabras de negación |
| `n_split_predicates`, `split_predicates` | `int`, `tuple[str]` | Número de los predicados escindidos y los predicados, el verbo y el sustantivo |
| `c_children` | `dict[int, int]` | Número de las palabras por número de dependientes |
| `c_deps` | `dict[str, int]` | Número de las palabras por relación |

Los atributos de las construcciones de esTS son `n_de_chains`, `n_gerund_clauses`, `n_se_passives` y `n_impersonal_se` (`int`): los números de las cadenas de `de`, de las cláusulas de gerundio, de las pasivas con `se` y de las oraciones impersonales con `se`.

=== "Código"

    ``` python
    ss.n_clauses, ss.n_nouns, ss.n_verbs
    ss.n_de_chains, ss.n_se_passives, ss.split_predicates
    ss.c_children
    ss.c_deps
    ss.sents[0]
    ```

=== "Resultado"

    ```
    (3, 9, 3)
    (1, 1, ('llevó cabo', 'hiciera mención'))
    {0: 16, 1: 5, 2: 4, 3: 2, 4: 2}
    {'ROOT': 2,
     'advcl': 1,
     'amod': 1,
     'aux': 1,
     'case': 6,
     'compound': 1,
     'det': 5,
     'expl:pass': 1,
     'mark': 2,
     'nmod': 3,
     'nsubj': 3,
     'obj': 2,
     'obl': 1}
    (La, revisión, de, las, cuentas, del, organismo, fue, realizada, por, el, comité)
    ```

## Métricas

Cada métrica es un atributo del objeto, calculado al crearlo, y `get_stats` da las métricas de la tabla. Las medidas de una oración (la dependencia más larga, la profundidad, los nodos por hoja) se promedian sobre las oraciones; las construcciones se dan por oración.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`mean_dependency_distance`](#dependency_distances) | Distancia media entre una palabra y su núcleo | 1 o más, `nan` sin dependencias | Más difícil de procesar |
| [`std_dependency_distance`](#dependency_distances) | Desviación típica de la distancia de dependencia | 0 o más, `nan` sin dependencias | Distancias menos parejas |
| [`max_dependency_distance`](#dependency_distances) | Media de las dependencias más largas de las oraciones que tienen dependencias | 1 o más, `nan` sin dependencias | Dependencias más largas |
| [`p_adjacent_dependencies`](#dependency_distances) | Proporción de las dependencias de longitud 1 | 0-1, `nan` sin dependencias | Más enlaces entre vecinas |
| [`tree_depth`](#tree_depth) | Profundidad media del árbol de una oración | 0 o más | Más incrustación |
| [`leaves_per_sent`](#leaves) | Hojas por oración | 0 o más | Oraciones más largas o más planas |
| [`subtrees_per_sent`](#leaves) | Subárboles por oración | 0 o más | Más sintagmas en una oración |
| [`nodes_per_leaf`](#leaves) | Media por oración de las palabras por hoja | 1 o más, `nan` para una oración sin hojas | Ramas más largas |
| [`verb_valency`](#valency) | Número medio de dependientes de un verbo en forma personal | 0 o más, `nan` sin verbos en forma personal | Más dependientes de un verbo |
| [`coordination_chains_per_sent`](#coordination_chains) | Cadenas de coordinación por oración | 0 o más | Más coordinación |
| [`mean_coordination_chain_len`](#coordination_chains) | Longitud media de una cadena de coordinación en palabras | 2 o más, `nan` sin cadenas | Enumeraciones más largas |
| [`clauses_per_sent`](#clauses) | Cláusulas por oración | 0 o más | Más cláusulas en una oración |
| [`mean_clause_len`](#clauses) | Longitud media de una cláusula en palabras | 1 o más, `nan` sin cláusulas | Cláusulas más largas |
| [`subordinate_clauses_per_sent`](#subordinate_clauses) | Cláusulas subordinadas por oración | 0 o más | Más subordinación |
| [`p_complex_sents`](#subordinate_clauses) | Proporción de las oraciones con subordinada | 0-1 | Más oraciones complejas |
| [`infinitive_clauses_per_sent`](#infinitive_clauses) | Cláusulas de infinitivo bajo un verbo por oración | 0 o más | Más complementos de infinitivo |
| [`modifiers_per_noun`](#noun_modifiers) | Número medio de modificadores de un sustantivo | 0 o más, `nan` sin sustantivos | Sintagmas nominales más pesados |
| [`de_chains_per_sent`](#de_chains) | Cadenas de `de` por oración | 0 o más | Más cadenas |
| [`max_de_chain_len`](#de_chains) | Cadena de `de` más larga del texto | 0 sin cadenas, si no 2 o más | Una cadena más larga |
| [`participle_clauses_per_sent`](#participle_clauses) | Cláusulas de participio por oración | 0 o más | Más cláusulas de participio |
| [`mean_participle_clause_len`](#participle_clauses) | Longitud media de una cláusula de participio en palabras | 2 o más, `nan` sin cláusulas de participio | Cláusulas de participio más largas |
| [`gerund_clauses_per_sent`](#gerund_clauses) | Cláusulas de gerundio por oración | 0 o más | Más cláusulas de gerundio |
| [`mean_gerund_clause_len`](#gerund_clauses) | Longitud media de una cláusula de gerundio en palabras | 2 o más, `nan` sin cláusulas de gerundio | Cláusulas de gerundio más largas |
| [`p_passive`](#passive) | Proporción de las formas pasivas entre las formas verbales | 0-1, `nan` sin formas verbales | Más pasiva |
| [`p_agentless_passive`](#passive) | Proporción de las formas sin agente entre las pasivas | 0-1, `nan` sin formas pasivas | Más pasiva sin agente |
| [`se_passives_per_sent`](#se) | Pasivas con `se` por oración | 0 o más | Más pasivas con `se` |
| [`impersonal_se_per_sent`](#se) | Oraciones impersonales con `se` por oración | 0 o más | Más oraciones impersonales |
| [`infinitives_per_sent`](#constructions) | Infinitivos por oración | 0 o más | Más infinitivos |
| [`negations_per_sent`](#constructions) | Palabras de negación por oración | 0 o más | Más negación |
| [`split_predicates_per_sent`](#constructions) | Predicados escindidos por oración | 0 o más | Más predicados escindidos |
| [`noun_verb_ratio`](#noun_verb_ratio) | Razón entre los sustantivos y las formas verbales | 0 o más, `nan` sin formas verbales | Un estilo más nominal |

Las funciones de las tarjetas se importan de `ests.syntax_stats`; las de las medidas del árbol que esTS no reexporta están en la [página de anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats/).

<div class="metric-card" markdown>

### Distancia de dependencia { #dependency_distances }

`mean_dependency_distance` · `std_dependency_distance` · `max_dependency_distance` · `p_adjacent_dependencies`
{ .metric-meta }

La distancia de dependencia (Liu 2008) es la distancia entre una palabra y su núcleo en posiciones de palabras, sin la puntuación; el núcleo de una oración no tiene ninguna. `mean_dependency_distance` y `std_dependency_distance` son la media y la desviación típica de las distancias del texto, `max_dependency_distance` la media de la distancia más larga de cada oración que tiene alguna, y `p_adjacent_dependencies` la proporción de las distancias de 1. Las oraciones de una palabra no entran en ninguna de las métricas. Las distancias son las de `calc_dependency_distances` de `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Profundidad del árbol { #tree_depth }

`tree_depth`
{ .metric-meta }

La profundidad del árbol de dependencias de una oración es el camino más largo de su núcleo a una hoja, en relaciones entre palabras, 0 para una oración de una palabra; la métrica es su media sobre las oraciones. La profundidad es la de `calc_tree_depth` de `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Hojas y subárboles { #leaves }

`leaves_per_sent` · `subtrees_per_sent` · `nodes_per_leaf`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:SyntaxStats-leaves 0162a04 -->
Una hoja es una palabra sin dependientes (`count_children`), un subárbol una palabra con ellas. Los nodos por hoja son las palabras de una oración entre sus hojas, promediados sobre las $S$ oraciones.

$$
\frac{1}{S} \sum_{s=1}^{S} \frac{\textrm{Número de palabras de } s}{\textrm{Número de hojas de } s}
$$

La distribución de las palabras por número de dependientes es el atributo `c_children`.

</div>

<div class="metric-card" markdown>

### Valencia de los verbos en forma personal { #valency }

`verb_valency`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:calc_valency 4a77742 -->
``` {.python .signature}
calc_valency(token, join_hyphens=False)
```

La valencia de un token: el número de sus palabras dependientes, sin las relaciones `cc`, `conj`, `parataxis` y `punct` (`anyts.constants.VALENCY_IGNORED_DEPS`); con `join_hyphens=True` una dependiente con guion cuenta una vez, así que `came` en `Some-one came` tiene una dependiente y no dos.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

Un verbo en forma personal es una palabra etiquetada `VERB` con `VerbForm=Fin` (`is_finite_verb` de `anyts.utils`). Los modelos del español etiquetan el participio de un tiempo compuesto o de la pasiva con `ser` (`ha llegado`, `fue construida`) como el verbo y su auxiliar como `AUX`, así que esos predicados quedan fuera.

</div>

<div class="metric-card" markdown>

### Cadenas de coordinación { #coordination_chains }

`coordination_chains_per_sent` · `mean_coordination_chain_len`
{ .metric-meta }

Una cadena de coordinación es un grupo de palabras unidas por `conj`: `manzanas, peras y ciruelas` es una cadena de tres. Una coordinación anidada y una enumeración repartida entre varios núcleos también son una sola cadena; la longitud de una cadena es el número de sus palabras. Las cadenas son las de `calc_coordination_chains` de `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Cláusulas { #clauses }

`clauses_per_sent` · `mean_clause_len`
{ .metric-meta }

``` {.python .signature}
is_clause_head(token)
```

Comprueba si una palabra encabeza una cláusula: el núcleo de la oración o, según la forma de su predicado ([`predicate_form`](#verb-forms)), una palabra con `ccomp`, `advcl`, `acl` (incluida una oración de relativo), `csubj` o `parataxis` (`anyts.constants.CLAUSE_DEPS`). Un predicado en forma personal encabeza su cláusula (`dijo que había llegado`, `estaba cantando`, `los regalos que te van a dar`, `sé que os habéis posado`), también bajo `xcomp`, que los modelos dan a algunos complementos en forma personal; un predicado en forma de participio o de gerundio no encabeza una cláusula de esa clase - esos predicados se cuentan aparte (`llegando tarde`, `habiendo llegado tarde`) -, ni tampoco uno en forma de infinitivo bajo `acl` (`el deseo de irse`, `el miedo de ser robado`). Bajo `xcomp` un infinitivo encabeza una cláusula según `is_infinitive_clause`, y un adjetivo predicativo (`parece cansado`) no encabeza ninguna. Un inciso (`parataxis`) y un predicado coordinado (`conj` del núcleo de una cláusula) cuentan solo cuando pueden ser un predicado ([`is_predicate`](#is_predicate)), de modo que incisos como `por ejemplo` no son cláusulas; un infinitivo que los modelos cuelgan como `conj` o `csubj` del verbo de su perífrasis (`hay que salir`, `llega a convertirse`) forma un solo predicado con él (`is_infinitive_periphrasis`). Es el [`is_clause_head`](https://sergeyshk.github.io/anyTS/stats/syntax_stats/#clauses) del núcleo anyTS con las reglas españolas de `is_infinitive_periphrasis` y `predicate_form`.

``` {.python .signature}
is_infinitive_clause(token)
```

Comprueba si un infinitivo bajo `xcomp` encabeza una cláusula propia: un predicado en forma de infinitivo que completa a su núcleo (`quiere salir`, `le hizo reír`, `quiere ser médico`, `quiere ser elegido`, `cree haber ganado`), salvo que los dos formen un solo predicado (`is_infinitive_periphrasis`: `puede salir`, `parece dormir`) o que la palabra que completa no encabece ninguna cláusula (`is_clause_head`): un infinitivo en una construcción de gerundio o de participio pertenece a ella (`intentando salir`, `destinada a disculpar`).

``` {.python .signature}
is_infinitive_periphrasis(token)
```

Comprueba si un infinitivo forma un solo predicado con su núcleo: un infinitivo bajo `xcomp` de un verbo de `RAISING_VERBS`, `parecer` (`parece dormir`), o una perífrasis. En una perífrasis el núcleo es un verbo de `INFINITIVE_PERIPHRASES` (NGLE, cap. 28) y el infinitivo se une a él por uno de los nexos de ese verbo - un `mark`, `case` o `cc` antes del infinitivo, o la palabra justo anterior, con la grafía antigua `á` leída como `a`. Los verbos son `poder`, `soler` y `deber` sin nexo (`puede salir`, `suele salir`), `deber de`, `tener que`, `haber que`, `haber de`, `ir a`, `venir a`, `pasar a`, `volver a`, `tornar a`, `empezar a` y `por`, `comenzar a` y `por`, `principiar a`, `poner a`, `echar a`, `romper a`, `llegar a`, `alcanzar a`, `acabar de` y `por`, `terminar de` y `por`, `dejar de`, `cesar de`, `parar de`, `estar para` y `por`. El lema del núcleo es el del modelo, o el de `ests.utils.lemmatize` cuando el del modelo no es ninguno de esos verbos (puede leer un verbo que abre la oración como nombre propio: `Solía salir`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

La longitud media de una cláusula es el número de las palabras entre el número de las cláusulas.

</div>

<div class="metric-card" markdown>

### Cláusulas subordinadas { #subordinate_clauses }

`subordinate_clauses_per_sent` · `p_complex_sents`
{ .metric-meta }

``` {.python .signature}
is_subordinate_clause_head(token)
```

Comprueba si una palabra encabeza una cláusula subordinada: un núcleo de cláusula (`is_clause_head`) con `ccomp`, `advcl`, `acl` o `csubj` (`anyts.constants.SUBORDINATE_CLAUSE_DEPS`), o bajo `xcomp` con un predicado en forma personal, o un predicado coordinado de una cláusula subordinada, por la relación de la primera palabra de su cadena de conjuntos hacia arriba. Una cláusula de infinitivo bajo un verbo (`quiere salir`) se cuenta aparte, entre las [cláusulas de infinitivo](#infinitive_clauses).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

`p_complex_sents` es la proporción de las oraciones con al menos una cláusula subordinada.

=== "Código"

    ``` python
    from ests.syntax_stats import is_clause_head, is_subordinate_clause_head
    from ests.utils import get_nlp

    doc = get_nlp()("Él quiere salir, pero tiene que quedarse porque parece cansado.")
    [token.text for token in doc if is_clause_head(token)]
    [token.text for token in doc if is_subordinate_clause_head(token)]
    ```

=== "Resultado"

    ```
    ['quiere', 'salir', 'tiene', 'parece']
    ['parece']
    ```

</div>

<div class="metric-card" markdown>

### Cláusulas de infinitivo { #infinitive_clauses }

`infinitive_clauses_per_sent`
{ .metric-meta }

``` {.python .signature}
is_infinitive_clause_head(token)
```

Comprueba si una palabra encabeza una cláusula de infinitivo bajo un verbo: un núcleo de cláusula (`is_clause_head`) cuyo predicado es un infinitivo bajo `xcomp` (`quiere salir`, `le pidió salir`), o un conjunto de uno, sea cual sea su propia forma: decide la primera palabra de su cadena de conjuntos hacia arriba (`quiero salir y que vengas`). Estas cláusulas se cuentan entre las cláusulas, pero no entre las subordinadas: las gramáticas toman un complemento de infinitivo por parte de una oración simple, y las correlaciones publicadas de la subordinación se obtuvieron para las subordinadas en forma personal. Es el [`is_infinitive_clause_head`](https://sergeyshk.github.io/anyTS/stats/syntax_stats/#infinitive_clauses) del núcleo anyTS sobre `is_clause_head`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

=== "Código"

    ``` python
    from ests.syntax_stats import is_clause_head, is_infinitive_clause_head
    from ests.utils import get_nlp

    doc = get_nlp()("Quiere salir y volver, pero intentando salir se cayó.")
    [token.text for token in doc if is_clause_head(token)]
    [token.text for token in doc if is_infinitive_clause_head(token)]
    ```

=== "Resultado"

    ```
    ['Quiere', 'salir', 'volver', 'cayó']
    ['salir', 'volver']
    ```

</div>

<div class="metric-card" markdown>

### Modificadores de un sustantivo { #noun_modifiers }

`modifiers_per_noun`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:count_noun_modifiers 6775fc1 -->
``` {.python .signature}
count_noun_modifiers(token, join_hyphens=False)
```

Cuenta los modificadores de un sintagma nominal: las dependientes con las relaciones `amod`, `det`, `nmod`, `nummod`, `acl` y sus subtipos (`anyts.constants.NOUN_MODIFIER_DEPS`); `conj` y `appos` no son modificadores.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

Los sustantivos son las palabras etiquetadas `NOUN` o `PROPN`: `la nueva casa de mi padre` da a `casa` tres modificadores, `la`, `nueva` y `padre`.

</div>

<div class="metric-card" markdown>

### Cadenas de de { #de_chains }

`de_chains_per_sent` · `max_de_chain_len`
{ .metric-meta }

``` {.python .signature}
calc_de_chains(tokens)
```

Las longitudes de las cadenas de `de` en el orden de las palabras: las cadenas de [`calc_modifier_chains`](#calc_modifier_chains) cuyos modificadores son complementos con `de`; `el aumento de la eficiencia del uso de los recursos` es una cadena de longitud 3, y un complemento suelto (`el uso del agua`) no es una cadena.

``` {.python .signature}
is_de_modifier(token)
```

Comprueba si una palabra es un complemento introducido por `de`: una palabra con la relación `nmod` cuya preposición (`case`) es `de` o su contracción `del` (`DE_PREPOSITIONS`): `el uso del agua`, pero no `la vuelta al campo`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Secuencia de tokens (`calc_de_chains`) |
| `token` | `Token` | - | Token (`is_de_modifier`) |

`max_de_chain_len` es la cadena más larga del texto, 0 sin cadenas.

=== "Código"

    ``` python
    from ests.syntax_stats import calc_de_chains
    from ests.utils import get_nlp

    calc_de_chains(get_nlp()("El aumento de la eficiencia del uso de los recursos fue notable."))
    ```

=== "Resultado"

    ```
    [3]
    ```

</div>

<div class="metric-card" markdown>

### Cláusulas de participio { #participle_clauses }

`participle_clauses_per_sent` · `mean_participle_clause_len`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:SyntaxStats-participle_clauses 098c370 -->
Las cláusulas que encabezan las palabras del gancho `is_participle_clause`; la longitud de una cláusula es el número de las palabras del subárbol de su núcleo (`subtree_len`).

``` {.python .signature}
is_participle_clause(token)
```

Comprueba si una palabra encabeza una cláusula de participio: un participio ([`is_participle`](#verb-forms)) que no es el núcleo de la oración, no lleva auxiliar ni cópula ([`has_auxiliary`](#verb-forms)) y tiene al menos una dependiente ([`calc_valency`](#valency)). `la casa, construida por los obreros, se vendió` tiene una, mientras que `ha pintado` y `fue construida` son predicados. `SyntaxStats` cuenta las cláusulas de participio con la misma regla.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

=== "Código"

    ``` python
    from ests.syntax_stats import is_participle_clause, subtree_len
    from ests.utils import get_nlp

    doc = get_nlp()("La casa, construida por los obreros en 1900, fue vendida.")
    [(token.text, subtree_len(token)) for token in doc if is_participle_clause(token)]
    ```

=== "Resultado"

    ```
    [('construida', 6)]
    ```

</div>

<div class="metric-card" markdown>

### Cláusulas de gerundio { #gerund_clauses }

`gerund_clauses_per_sent` · `mean_gerund_clause_len`
{ .metric-meta }

``` {.python .signature}
is_gerund_clause(token)
```

Comprueba si una palabra encabeza una cláusula de gerundio: un predicado en forma de gerundio ([`predicate_form`](#verb-forms)), simple o compuesta (`llegando tarde`, `habiendo llegado tarde`, `siendo elegido presidente`), que no es el núcleo de la oración y tiene al menos una dependiente además de sus auxiliares y cópulas ([`calc_valency`](#valency)). Las perífrasis quedan fuera: una con un auxiliar en forma personal (`está cantando`) es un predicado en forma personal, y un gerundio que los modelos cuelgan como `xcomp` o `advcl` de un verbo de `GERUND_PERIPHRASIS_VERBS` - `quedar`, `llevar`, `seguir`, `venir`, `ir`, `andar`, `continuar`, `acabar` (`sigue trabajando`, `acabó reconociendo`) - no encabeza ninguna cláusula. La longitud de una cláusula es el número de las palabras del subárbol del gerundio (`subtree_len`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

=== "Código"

    ``` python
    from ests.syntax_stats import is_gerund_clause
    from ests.utils import get_nlp

    doc = get_nlp()("Llegando tarde, encontró la puerta cerrada y siguió trabajando.")
    [token.text for token in doc if is_gerund_clause(token)]
    ```

=== "Resultado"

    ```
    ['Llegando']
    ```

</div>

<div class="metric-card" markdown>

### Pasiva { #passive }

`p_passive` · `p_agentless_passive`
{ .metric-meta }

``` {.python .signature}
is_passive(token)
```

Comprueba si una palabra es una forma verbal pasiva: un verbo (`VERB`) que es un participio con el auxiliar `ser` (`PASSIVE_AUX`) como `aux` o `cop` - `la casa fue construida`, también cuando los modelos leen el auxiliar como cópula, `el proyecto es financiado` - o que lleva el `se` de la pasiva (`expl:pass`, `SE_PASSIVE_DEP`: `se construyó la casa`). Un participio que modifica a un sustantivo (`la casa construida por los obreros`) es en cambio una cláusula de participio.

``` {.python .signature}
is_agentless(token)
```

Comprueba si una forma pasiva no tiene agente: ninguna de sus dependientes es de `is_agent` - `la casa fue construida`, pero no `la casa fue construida por los obreros`. Una palabra que no es una forma pasiva (`is_passive`) da `False`.

``` {.python .signature}
is_agent(token)
```

Comprueba si una palabra es el agente de una pasiva: un complemento cuya preposición (`case`) es `por` (`AGENT_PREPOSITION`), sea cual sea su relación, porque los modelos no tienen `obl:agent`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

Las formas verbales de `p_passive` son las palabras etiquetadas `VERB`.

=== "Código"

    ``` python
    from ests.syntax_stats import is_agentless, is_passive
    from ests.utils import get_nlp

    doc = get_nlp()(
        "La casa fue construida por los obreros y el proyecto es financiado por el Estado. "
        "Se construyó la casa."
    )
    [(token.text, is_agentless(token)) for token in doc if is_passive(token)]
    ```

=== "Resultado"

    ```
    [('construida', False), ('financiado', False), ('construyó', True)]
    ```

</div>

<div class="metric-card" markdown>

### Oraciones con se { #se }

`se_passives_per_sent` · `impersonal_se_per_sent`
{ .metric-meta }

`se_passives_per_sent` cuenta el `se` de la pasiva (`expl:pass`, `SE_PASSIVE_DEP`: `se construyó la casa`) por oración, `impersonal_se_per_sent` el `se` de una oración impersonal (`expl:impers`, `SE_IMPERSONAL_DEP`: `se vive bien`, `aquí se trabaja mucho`), tal como los etiqueta el modelo. Un verbo con el `se` de la pasiva es también una forma pasiva de `p_passive`.

!!! warning "Aviso"
    `es_core_news_sm` distingue mal los tres `se` del español - rara vez marca un `se` impersonal y lee `se fue dando un portazo` como una pasiva -, así que lea `se_passives_per_sent` e `impersonal_se_per_sent` juntas y no por separado.

=== "Código"

    ``` python
    ss = SyntaxStats("Se construyó la casa en un año. Aquí se trabaja mucho.")
    ss.se_passives_per_sent, ss.impersonal_se_per_sent
    ```

=== "Resultado"

    ```
    (0.5, 0.5)
    ```

</div>

<div class="metric-card" markdown>

### Infinitivos, negaciones y predicados escindidos { #constructions }

`infinitives_per_sent` · `negations_per_sent` · `split_predicates_per_sent`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:SyntaxStats-constructions 4d8a10f -->
Los infinitivos (`is_infinitive` de `anyts.utils`), las palabras de negación del gancho `is_negation` y los predicados escindidos del gancho `find_split_predicates`, por oración.

``` {.python .signature}
is_negation(token)
```

Comprueba si una palabra es una palabra de negación: una palabra con `Polarity=Neg`, que los modelos dan solo a `no`, o una de `NEGATION_WORDS` en mayúsculas o minúsculas - `no`, `nunca`, `jamás`, `nada`, `nadie`, `ninguno` con sus formas, `tampoco`; una conjunción (`ni` de `ni... ni`) no lo es. Cuenta cada una de esas palabras, así que la concordancia negativa del español, donde una negación se escribe dos veces (`no vino nadie`), da dos. `SyntaxStats` cuenta las negaciones con la misma regla.

``` {.python .signature}
find_split_predicates(tokens)
```

``` {.python .signature}
is_light_verb(token)
```

``` {.python .signature}
is_split_predicate_noun(token, verb)
```

Los predicados escindidos, pares de un verbo y un sustantivo en el orden de las palabras, sustituyen un verbo por un verbo soporte y un sustantivo: `hacer una revisión` en lugar de `revisar`. Un verbo soporte (`is_light_verb`) es un `VERB` con un lema de `LIGHT_VERBS` - `hacer`, `dar`, `tomar`, `tener`, `poner`, `llevar`, `prestar`, `efectuar`, `realizar`, `proceder`, `proporcionar`, `ejercer`. Su parte nominal (`is_split_predicate_noun`) es un `NOUN` cuyo lema deriva de un verbo, según la regla de los [sustantivos deverbales](style_stats.md#verbal_nouns) (`revisión`, `decisión`, `uso`), o uno de los sustantivos de `SPLIT_PREDICATE_NOUNS` - `cabo`, `cargo`, `caso`, `comienzo`, `cuenta`, `efecto`, `fin`, `gala`, `hincapié`, `lugar`, `manifiesto`, `marcha`, `parte` - con un verbo `verb` de su expresión fija (`llevar a cabo`, `tomar parte`, `poner de manifiesto`, `tener lugar`), de modo que `poner en primer lugar la seguridad` no lo es. Un verbo toma como mucho una parte nominal, preferida por relación en el orden `compound`, `obj`, `nsubj` (solo con el `se` de la pasiva: `se tomó la decisión`), `iobj`, `nmod`, `obl`. Un complemento con preposición es la parte nominal solo en una expresión fija (`poner de manifiesto`) o con un verbo de `PREPOSITIONAL_LIGHT_VERBS`, `proceder` (`se procedió a la votación`); el agente de una pasiva nunca lo es. Los pares hallados están en el atributo `split_predicates`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Secuencia de tokens (`find_split_predicates`) |
| `verb` | `Token` | - | Verbo del que depende el sustantivo (`is_split_predicate_noun`) |

=== "Código"

    ``` python
    from ests.syntax_stats import find_split_predicates, is_negation
    from ests.utils import get_nlp

    doc = get_nlp()(
        "Se procedió a la votación y el comité tomó parte en la revisión. "
        "No vino nadie, ni Juan ni María."
    )
    find_split_predicates(doc)
    [token.text for token in doc if is_negation(token)]
    ```

=== "Resultado"

    ```
    [(procedió, votación), (tomó, parte)]
    ['No', 'nadie']
    ```

</div>

<div class="metric-card" markdown>

### Razón entre los sustantivos y los verbos { #noun_verb_ratio }

`noun_verb_ratio`
{ .metric-meta }

<!-- core: stats/syntax_stats.md:SyntaxStats-noun_verb_ratio e8f2957 -->
El número de los sustantivos `n_nouns` entre el número de las formas verbales `n_verbs`.

$$
\frac{\textrm{Número de sustantivos}}{\textrm{Número de formas verbales}}
$$

</div>

## Métodos

Los métodos `get_stats`, `to_dataframe`, `print_stats` y `describe` son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas sintácticas no tienen escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    ss = SyntaxStats(text)
    ss.get_stats()
    ss.describe("tree_depth"), ss.describe("de_chains_per_sent")
    ```

=== "Resultado"

    ```
    {'mean_dependency_distance': 2.259259259259259,
     'std_dependency_distance': 2.1532506449997975,
     'max_dependency_distance': 9.0,
     'p_adjacent_dependencies': 0.48148148148148145,
     'tree_depth': 4.0,
     'leaves_per_sent': 8.0,
     'subtrees_per_sent': 6.5,
     'nodes_per_leaf': 1.8015873015873014,
     'verb_valency': 4.0,
     'coordination_chains_per_sent': 0.0,
     'mean_coordination_chain_len': nan,
     'clauses_per_sent': 1.5,
     'mean_clause_len': 9.666666666666666,
     'subordinate_clauses_per_sent': 0.5,
     'p_complex_sents': 0.5,
     'infinitive_clauses_per_sent': 0.0,
     'modifiers_per_noun': 1.0,
     'de_chains_per_sent': 0.5,
     'max_de_chain_len': 2,
     'participle_clauses_per_sent': 0.5,
     'mean_participle_clause_len': 3.0,
     'gerund_clauses_per_sent': 0.0,
     'mean_gerund_clause_len': nan,
     'p_passive': 0.6666666666666666,
     'p_agentless_passive': 0.5,
     'se_passives_per_sent': 0.5,
     'impersonal_se_per_sent': 0.0,
     'infinitives_per_sent': 0.0,
     'negations_per_sent': 0.5,
     'split_predicates_per_sent': 1.0,
     'noun_verb_ratio': 3.0}
    (None, None)
    ```

Las funciones trabajan con tokens de spaCy: las funciones `calc_*` y `find_*` reciben una secuencia de tokens (`Doc`, `Span` o una lista), las funciones `is_*`, `has_*` y `count_*` un solo token; las palabras de una secuencia son los tokens de `is_word` de `anyts.utils`. Las funciones del árbol de dependencias vienen del núcleo, las de las construcciones del español son propias de esTS.

## Palabras de una secuencia { #get_words }

<!-- core: stats/syntax_stats.md:get_words fb9eece -->
``` {.python .signature}
get_words(tokens, join_hyphens=False)
```

Las palabras de una secuencia de tokens en su orden; con `join_hyphens=True` una palabra que el tokenizador dividió por sus guiones es una sola palabra, dada por la parte que lleva su relación, como con las dependientes de `get_children` (`governor` en `He is vice-governor`), o por su primera parte cuando la lleva un guion.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Secuencia de tokens |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

## Relación base { #base_dep }

<!-- core: stats/syntax_stats.md:base_dep 66fdc26 -->
``` {.python .signature}
base_dep(token)
```

La relación de un token sin su subtipo, que Universal Dependencies separa con dos puntos: `nsubj:pass` da `nsubj`, `expl:pass` da `expl`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

## Palabras dependientes { #get_children }

<!-- core: stats/syntax_stats.md:get_children 2fc8508 -->
``` {.python .signature}
get_children(token, join_hyphens=False)
```

Las palabras dependientes de un token, sin la puntuación ni los espacios; con `join_hyphens=True`, las dependientes de toda la palabra con guion a la que pertenece el token.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

<!-- core: stats/syntax_stats.md:subtree_len bfb372e -->
``` {.python .signature}
subtree_len(token, join_hyphens=False)
```

El número de palabras del subárbol de un token: el propio token y todas sus dependientes directas e indirectas; los argumentos son los de `get_children`.

## Formas verbales { #verb-forms }

``` {.python .signature}
predicate_form(token)
```

La forma verbal de un predicado por las formas (`VerbForm`) de sus auxiliares y cópulas (`aux`, `cop`): un auxiliar en forma personal hace el predicado personal (`había llegado`, `estaba cantando`); si no, decide el primer auxiliar (`de haber matado` es un infinitivo, `siendo elegido` un gerundio), y sin auxiliares la propia palabra. Un auxiliar en participio cuenta como forma personal: `sido` y `estado` siguen a una forma de `haber`, que los modelos pueden colgar de otra palabra (`hubieras sido albañil`). Un auxiliar que el modelo deja sin forma se lee por su terminación cuando es un verbo de `AUXILIARY_VERBS` (`habéis llegado`) - un infinitivo en `-r` y un gerundio en `-ndo`, con enclíticos detrás (`ENCLITICS`), una forma personal en otro caso - y se omite cuando no lo es (la grafía antigua `á`). Es el `predicate_form` del núcleo anyTS con la lectura española de un auxiliar sin forma. La forma es `'Fin'`, `'Inf'`, `'Ger'` o `'Part'`, una cadena vacía para una palabra sin forma verbal.

``` {.python .signature}
is_participle(token)
```

``` {.python .signature}
is_gerund(token)
```

``` {.python .signature}
has_auxiliary(token)
```

`is_participle` comprueba si un token es un participio (`VerbForm=Part`) sea cual sea su categoría, porque los modelos etiquetan como adjetivo un participio que modifica a un sustantivo (`la casa pintada`); `is_gerund`, si es un gerundio (`VerbForm=Ger`); `has_auxiliary`, si lleva un auxiliar o una cópula (`aux`, `cop`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |

=== "Código"

    ``` python
    from ests.syntax_stats import is_participle, predicate_form
    from ests.utils import get_nlp

    doc = get_nlp()(
        "Dijo que había llegado tarde. Lo acusan de haber matado al rey siendo elegido presidente."
    )
    [(token.text, predicate_form(token)) for token in doc if is_participle(token)]
    ```

=== "Resultado"

    ```
    [('llegado', 'Fin'), ('matado', 'Inf'), ('elegido', 'Ger')]
    ```

## Predicado de una cláusula { #is_predicate }

<!-- core: stats/syntax_stats.md:is_predicate b814232 -->
``` {.python .signature}
is_predicate(token, join_hyphens=False)
```

Comprueba si una palabra puede ser el predicado de su cláusula: un verbo (`VERB`, `AUX`), una palabra con sujeto propio (`nsubj`, `csubj` y sus subtipos, `anyts.constants.SUBJECT_DEPS`) o con cópula (`cop`), de modo que el predicado nominal de `he is tall` y de una lengua que omite el sujeto pasa y una palabra parentética no.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `token` | `Token` | - | Token |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

Un valor que no es un `Token` lanza `SourceTypeError`.

## Cadenas de modificadores { #calc_modifier_chains }

<!-- core: stats/syntax_stats.md:calc_modifier_chains f16f96d -->
``` {.python .signature}
calc_modifier_chains(tokens, is_modifier, join_hyphens=False)
```

Las longitudes de las cadenas de modificadores encajados, en el orden de las palabras. Una cadena son dos o más modificadores, cada uno colgado del anterior, como los complementos de `the increase of the efficiency of the use of resources` (longitud 3); la comprobación `is_modifier` de una lengua dice qué es un modificador (un complemento con preposición, un sustantivo en genitivo). Una cadena empieza en un modificador cuyo núcleo no lo es, y su longitud es el número de modificadores de su rama más larga. Los enlaces son los de `get_children`: la puntuación no es un enlace, y con `join_hyphens` una palabra con guion es un solo enlace.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Secuencia de tokens |
| `is_modifier` | `Callable[[Token], bool]` | - | Si una palabra es un modificador de la cadena |
| `join_hyphens` | `bool` | `False` | Tomar una palabra con guion por una sola palabra |

Una comprobación que no es invocable lanza `SourceTypeError`.
