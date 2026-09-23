# Estadísticas sintácticas

!!! info ""
    **ests.syntax_stats.SyntaxStats**

## Descripción

Módulo para calcular las estadísticas sintácticas de un texto sobre el árbol de dependencias de [Universal Dependencies](https://universaldependencies.org/u/dep/). La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy), pero tiene que estar analizada: una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`, y un `Doc` debe llevar las dependencias, de modo que un `Doc` de `spacy.blank("es")` o de un pipeline sin analizador no es una fuente válida.

Los signos de puntuación y los espacios no son nodos del árbol: lo son las palabras, y las distancias se cuentan en posiciones de palabras. Las medidas de una oración - la dependencia más larga, la profundidad del árbol, el número de hojas y de subárboles, los nodos por hoja - se promedian sobre las oraciones, las construcciones se dan por oración, y la pasiva y los modificadores son proporciones sobre los verbos y sobre los sustantivos.

Un texto más largo que el `max_length` del pipeline - un millón de caracteres por defecto - levanta `SourceError`: divídalo en partes o suba `max_length` en un pipeline propio y páselo en `nlp`.

!!! note "Nota"
    Las estadísticas se calculan al inicializar el objeto `SyntaxStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (cadena u objeto Doc) |
| `nlp` | Language | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Medidas de complejidad { #complexity }

Las medidas del árbol siguen el trabajo de Ivanov, Solnyshkina y Solovyev sobre la complejidad sintáctica de un texto: la distancia de dependencia de Liu (2008) - la distancia entre una palabra y su núcleo en posiciones de palabras -, la profundidad del árbol, las hojas y los subárboles, la valencia de los verbos personales, las cadenas de coordinación, las cláusulas y los modificadores del sustantivo.

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `mean_dependency_distance` | float | Distancia media de dependencia |
| `std_dependency_distance` | float | Desviación típica de la distancia de dependencia |
| `max_dependency_distance` | float | Distancia máxima de dependencia en una oración, sobre las oraciones que tienen dependencias |
| `p_adjacent_dependencies` | float | Proporción de dependencias contiguas, de longitud 1 |
| `tree_depth` | float | Profundidad del árbol de dependencias |
| `leaves_per_sent` | float | Hojas por oración |
| `subtrees_per_sent` | float | Subárboles por oración |
| `nodes_per_leaf` | float | Razón entre el número de palabras y el de hojas |
| `verb_valency` | float | Número medio de dependientes de un verbo personal |
| `coordination_chains_per_sent` | float | Cadenas de coordinación por oración |
| `mean_coordination_chain_len` | float | Longitud media de una cadena de coordinación |
| `clauses_per_sent` | float | Cláusulas por oración |
| `mean_clause_len` | float | Longitud media de una cláusula en palabras |
| `subordinate_clauses_per_sent` | float | Cláusulas subordinadas por oración |
| `p_complex_sents` | float | Proporción de oraciones con al menos una subordinada |
| `modifiers_per_noun` | float | Número medio de modificadores de un sustantivo |
| `noun_verb_ratio` | float | Razón entre el número de sustantivos y el de formas verbales |

Una cláusula la encabeza el núcleo de una oración o una palabra con la relación `ccomp`, `advcl`, `acl` o `csubj`; los modelos españoles no usan subtipos, así que una oración de relativo lleva el `acl` sin más. Los participios y los gerundios no encabezan una cláusula de esa clase - se cuentan aparte -, ni tampoco un infinitivo bajo `acl` (`el deseo de irse`). Un inciso (`parataxis`) y un predicado coordinado (`conj` del núcleo de una cláusula) cuentan solo cuando son un verbo o llevan sujeto propio.

## Construcciones del estilo administrativo { #constructions }

Las construcciones son las que advierten las guías españolas de lenguaje claro: la pasiva, las cláusulas de participio y de gerundio, las cadenas de `de`, los predicados escindidos.

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `de_chains_per_sent` | float | Cadenas de `de` por oración |
| `max_de_chain_len` | int | Longitud máxima de una cadena de `de` |
| `participle_clauses_per_sent` | float | Cláusulas de participio por oración |
| `mean_participle_clause_len` | float | Longitud media de una cláusula de participio en palabras |
| `gerund_clauses_per_sent` | float | Cláusulas de gerundio por oración |
| `mean_gerund_clause_len` | float | Longitud media de una cláusula de gerundio en palabras |
| `p_passive` | float | Proporción de formas pasivas entre las formas verbales |
| `p_agentless_passive` | float | Proporción de formas sin agente entre las pasivas |
| `se_passives_per_sent` | float | Pasivas con `se` por oración |
| `impersonal_se_per_sent` | float | Oraciones impersonales con `se` por oración |
| `infinitives_per_sent` | float | Infinitivos por oración |
| `negations_per_sent` | float | Palabras de negación por oración |
| `split_predicates_per_sent` | float | Predicados escindidos por oración |

*   Una **cadena de `de`** son dos o más complementos encajados introducidos por `de` o su contracción `del`: `el aumento de la eficiencia del uso de los recursos` es una cadena de longitud 3. Un complemento suelto (`el uso del agua`) no es una cadena.
*   Una **cláusula de participio** es un participio con al menos un dependiente que no es el predicado de su cláusula: `la casa, construida por los obreros, se vendió` tiene una, `el autor ha escrito el libro` ninguna, porque el participio de un tiempo compuesto lleva auxiliar. Una **cláusula de gerundio** es lo mismo para un gerundio, dejando fuera la perífrasis `está cantando`.
*   La **pasiva** es un participio con el auxiliar `ser` (`la casa fue construida`) o un verbo con el `se` de la pasiva (`se construyó la casa`). Los modelos españoles dan al auxiliar de la pasiva la relación `aux` sin más y a su sujeto el `nsubj` sin más, así que es el lema del auxiliar lo que distingue `fue construida` de `ha construido`. Una pasiva es **sin agente** cuando ningún complemento suyo va introducido por `por`.
*   Un **predicado escindido** es un verbo soporte (`hacer`, `dar`, `tomar`, `tener`, `poner`, `llevar`, `prestar`, `efectuar`, `realizar`, `proceder`, `proporcionar`, `ejercer`) con una parte nominal derivada de un verbo (`revisión`, `decisión`, `uso`) o una de las fijas (`cabo`, `cuenta`, `manifiesto`, `parte`): `hacer una revisión` en lugar de `revisar`, `llevar a cabo la reforma` en lugar de `reformar`. Los pares hallados están en el atributo `split_predicates`.
*   Una **palabra de negación** lleva `Polarity=Neg`, que los modelos dan solo a `no`, o es una de `nunca`, `jamás`, `nada`, `nadie`, `ninguno` y `tampoco`; la conjunción `ni` de `ni... ni` no lo es. Cuenta cada una de esas palabras, así que la concordancia negativa del español, donde una negación se escribe dos veces (`no vino nadie`), da dos.

!!! warning "Advertencia"
    Las estadísticas valen lo que vale el análisis sintáctico. `es_core_news_sm` distingue mal los tres `se` del español: en las páginas españolas de este sitio marca 60 como `se` de pasiva, 51 como de verbo pronominal y solo 2 como impersonal, y lee `se fue dando un portazo` como una pasiva. Lea `se_passives_per_sent` e `impersonal_se_per_sent` juntas y no por separado. El agente de la pasiva es otro punto débil - los modelos no tienen la relación `obl:agent` y anotan `por los obreros` tanto como objeto como como oblicuo -, y por eso el agente se busca por su preposición y no por su relación.

## Recuentos { #counts }

Además de las estadísticas, el objeto guarda los recuentos con los que están hechas, útiles por sí mismos.

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `n_sents` | int | Número de oraciones con palabras |
| `n_words` | int | Número de palabras |
| `n_leaves` | int | Número de hojas, palabras sin ninguna dependiente |
| `n_subtrees` | int | Número de subárboles, palabras con dependientes |
| `n_coordination_chains` | int | Número de cadenas de coordinación |
| `n_clauses` | int | Número de cláusulas |
| `n_subordinate_clauses` | int | Número de cláusulas subordinadas |
| `n_complex_sents` | int | Número de oraciones con subordinada |
| `n_nouns` | int | Número de sustantivos |
| `n_de_chains` | int | Número de cadenas de `de` |
| `n_participle_clauses` | int | Número de cláusulas de participio |
| `n_gerund_clauses` | int | Número de cláusulas de gerundio |
| `n_verbs` | int | Número de formas verbales |
| `n_passive` | int | Número de formas verbales pasivas |
| `n_agentless_passive` | int | Número de formas pasivas sin agente |
| `n_se_passives` | int | Número de pasivas con `se` |
| `n_impersonal_se` | int | Número de oraciones impersonales con `se` |
| `n_infinitives` | int | Número de infinitivos |
| `n_negations` | int | Número de palabras de negación |
| `n_split_predicates` | int | Número de predicados escindidos |
| `split_predicates` | tuple[str] | Tupla de los predicados escindidos (verbo y sustantivo) |
| `c_children` | dict[int, int] | Distribución de las palabras por número de dependientes |
| `c_deps` | dict[str, int] | Distribución de las palabras por relación sintáctica |

## Métodos

### get_stats

Devuelve un diccionario con las estadísticas sintácticas calculadas.

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import SyntaxStats

    # Preparar los datos
    text = (
        "La revisión de las cuentas del organismo fue realizada por el comité. "
        "Se llevó a cabo la reforma, aprobada en 1998, sin que nadie hiciera "
        "mención de los problemas."
    )

    # Calcular las estadísticas
    ss = SyntaxStats(text)
    ss.get_stats()
    ```

    _Resultado_:

    ``` bash
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
    ```

    Los predicados escindidos del texto están en un atributo propio:

    ``` python
    ss.split_predicates
    # ('llevó cabo', 'hiciera mención')
    ```

### print_stats

Muestra una tabla con las estadísticas sintácticas calculadas.

Para ilustrar el método reutilizamos el código del ejemplo anterior:

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de las estadísticas calculadas
    ss.print_stats()
    ```

    _Resultado_:

    ``` bash
                        Statistic                     |  Value
    ------------------------------------------------------------
    Mean dependency distance                          |   2.26
    Standard deviation of the dependency distance     |   2.15
    Maximum dependency distance                       |   9.00
    Share of adjacent dependencies                    |   0.48
    Depth of the dependency tree                      |   4.00
    Leaves per sentence                               |   8.00
    Subtrees per sentence                             |   6.50
    Nodes per leaf                                    |   1.80
    Valency of the finite verbs                       |   4.00
    Coordination chains per sentence                  |   0.00
    Mean length of a coordination chain               |   nan
    Clauses per sentence                              |   1.50
    Mean length of a clause (words)                   |   9.67
    Subordinate clauses per sentence                  |   0.50
    Share of sentences with a subordinate clause      |   0.50
    Modifiers per noun phrase                         |   1.00
    Chains of de per sentence                         |   0.50
    Maximum length of a chain of de                   |   2.00
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
