# Syntactic statistics

!!! info ""
    **ests.syntax_stats.SyntaxStats**

## Description

A module for computing the syntactic statistics of a text on the dependency tree of [Universal Dependencies](https://universaldependencies.org/u/dep/). The data source can be either a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library, but it has to be parsed: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, and a `Doc` must carry the dependencies, so a `Doc` of `spacy.blank("es")` or of a pipeline without a parser is not a valid source.

Punctuation marks and whitespace are not nodes of the tree: the words are, and the distances are counted in positions of words. The measures of a sentence - the longest dependency, the depth of the tree, the number of leaves and of subtrees, the nodes per leaf - are averaged over the sentences, the constructions are given per sentence, and the passive and the modifiers are shares of the verbs and of the nouns.

A text longer than the `max_length` of the pipeline - a million characters by default - raises `SourceError`: split it into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

!!! note "Note"
    The statistics are computed when the `SyntaxStats` object is initialized.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `nlp` | Language | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Measures of complexity { #complexity }

The measures of the tree follow the work of Ivanov, Solnyshkina and Solovyev on the syntactic complexity of a text: the dependency distance of Liu (2008) - the distance between a word and its head in positions of words - the depth of the tree, the leaves and the subtrees, the valency of the finite verbs, the coordination chains, the clauses and the modifiers of a noun.

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `mean_dependency_distance` | float | Mean dependency distance |
| `std_dependency_distance` | float | Standard deviation of the dependency distance |
| `max_dependency_distance` | float | Maximum dependency distance in a sentence, over the sentences that have dependencies |
| `p_adjacent_dependencies` | float | Share of adjacent dependencies - of length 1 |
| `tree_depth` | float | Depth of the dependency tree |
| `leaves_per_sent` | float | Leaves per sentence |
| `subtrees_per_sent` | float | Subtrees per sentence |
| `nodes_per_leaf` | float | Ratio of the number of words to the number of leaves |
| `verb_valency` | float | Mean number of dependents of a finite verb |
| `coordination_chains_per_sent` | float | Coordination chains per sentence |
| `mean_coordination_chain_len` | float | Mean length of a coordination chain |
| `clauses_per_sent` | float | Clauses per sentence |
| `mean_clause_len` | float | Mean length of a clause in words |
| `subordinate_clauses_per_sent` | float | Subordinate clauses per sentence |
| `p_complex_sents` | float | Share of sentences with at least one subordinate clause |
| `modifiers_per_noun` | float | Mean number of modifiers of a noun |
| `noun_verb_ratio` | float | Ratio of the number of nouns to the number of verb forms |

A clause is headed by the head of a sentence or by a word with the relation `ccomp`, `advcl`, `acl` or `csubj`; the Spanish models use no subtypes, so a relative clause carries the plain `acl`. The participles and the gerunds head no clause of that kind - they are counted apart - and neither does an infinitive under `acl` (`el deseo de irse`). A parenthetical (`parataxis`) and a coordinated predicate (`conj` of the head of a clause) count only when they are a verb or carry a subject of their own.

## Constructions of the administrative style { #constructions }

The constructions are the ones the Spanish guides to clear language (*lenguaje claro*) warn about: the passive, the participial and the gerund clauses, the chains of `de`, the split predicates.

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `de_chains_per_sent` | float | Chains of `de` per sentence |
| `max_de_chain_len` | int | Maximum length of a chain of `de` |
| `participle_clauses_per_sent` | float | Participial clauses per sentence |
| `mean_participle_clause_len` | float | Mean length of a participial clause in words |
| `gerund_clauses_per_sent` | float | Gerund clauses per sentence |
| `mean_gerund_clause_len` | float | Mean length of a gerund clause in words |
| `p_passive` | float | Share of passive forms among the verb forms |
| `p_agentless_passive` | float | Share of forms with no agent among the passive ones |
| `se_passives_per_sent` | float | Passives with `se` per sentence |
| `impersonal_se_per_sent` | float | Impersonal sentences with `se` per sentence |
| `infinitives_per_sent` | float | Infinitives per sentence |
| `negations_per_sent` | float | Words of negation per sentence |
| `split_predicates_per_sent` | float | Split predicates per sentence |

*   A **chain of `de`** is two or more nested complements introduced by `de` or its contraction `del`: `el aumento de la eficiencia del uso de los recursos` is a chain of length 3. A single complement (`el uso del agua`) is not a chain.
*   A **participial clause** is a participle with at least one dependent that is not the predicate of its clause: `la casa, construida por los obreros, se vendió` has one, `el autor ha escrito el libro` has none, because the participle of a compound tense carries an auxiliary. A **gerund clause** is the same for a gerund, the periphrasis `está cantando` left out.
*   The **passive** is a participle with the auxiliary `ser` (`la casa fue construida`) or a verb with the `se` of the passive (`se construyó la casa`). The Spanish models give the auxiliary of the passive the plain relation `aux` and its subject the plain `nsubj`, so it is the lemma of the auxiliary that tells `fue construida` from `ha construido`. A passive is **agentless** when no complement of it is introduced by `por`.
*   A **split predicate** is a light verb (`hacer`, `dar`, `tomar`, `tener`, `poner`, `llevar`, `prestar`, `efectuar`, `realizar`, `proceder`, `proporcionar`, `ejercer`) with a nominal part derived from a verb (`revisión`, `decisión`, `uso`) or one of the fixed ones (`cabo`, `cuenta`, `manifiesto`, `parte`): `hacer una revisión` instead of `revisar`, `llevar a cabo la reforma` instead of `reformar`. The pairs found are in the attribute `split_predicates`.
*   A **word of negation** carries `Polarity=Neg`, which the models give to `no` alone, or is one of `nunca`, `jamás`, `nada`, `nadie`, `ninguno` and `tampoco`; the conjunction `ni` of `ni... ni` is not one. Every such word counts, so the negative concord of Spanish, where one negation is written twice (`no vino nadie`), gives two.

!!! warning "Warning"
    The statistics are as good as the parse. `es_core_news_sm` tells the three `se` of Spanish apart poorly: on the Spanish pages of this site it marks 60 as the `se` of a passive, 51 as the one of a pronominal verb and only 2 as impersonal, and it reads `se fue dando un portazo` as a passive. Read `se_passives_per_sent` and `impersonal_se_per_sent` together rather than apart. The agent of a passive is another weak spot - the models have no relation `obl:agent` and annotate `por los obreros` as an object as readily as an oblique - which is why the agent is looked for by its preposition and not by its relation.

## Counts { #counts }

Besides the statistics the object keeps the counts they are built from, which are useful on their own.

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `n_sents` | int | Number of sentences containing words |
| `n_words` | int | Number of words |
| `n_leaves` | int | Number of leaves - words with no dependent word |
| `n_subtrees` | int | Number of subtrees - words with dependent words |
| `n_coordination_chains` | int | Number of coordination chains |
| `n_clauses` | int | Number of clauses |
| `n_subordinate_clauses` | int | Number of subordinate clauses |
| `n_complex_sents` | int | Number of sentences with a subordinate clause |
| `n_nouns` | int | Number of nouns |
| `n_de_chains` | int | Number of chains of `de` |
| `n_participle_clauses` | int | Number of participial clauses |
| `n_gerund_clauses` | int | Number of gerund clauses |
| `n_verbs` | int | Number of verb forms |
| `n_passive` | int | Number of passive verb forms |
| `n_agentless_passive` | int | Number of passive forms with no agent |
| `n_se_passives` | int | Number of passives with `se` |
| `n_impersonal_se` | int | Number of impersonal sentences with `se` |
| `n_infinitives` | int | Number of infinitives |
| `n_negations` | int | Number of words of negation |
| `n_split_predicates` | int | Number of split predicates |
| `split_predicates` | tuple[str] | Tuple of the split predicates (verb and noun) |
| `c_children` | dict[int, int] | Distribution of words by number of dependent words |
| `c_deps` | dict[str, int] | Distribution of words by syntactic relation |

## Methods

### get_stats

Returns a dictionary with the computed syntactic statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the library
    from ests import SyntaxStats

    # Prepare the data
    text = (
        "La revisión de las cuentas del organismo fue realizada por el comité. "
        "Se llevó a cabo la reforma, aprobada en 1998, sin que nadie hiciera "
        "mención de los problemas."
    )

    # Compute the statistics
    ss = SyntaxStats(text)
    ss.get_stats()
    ```

    _Result_:

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

    The split predicates of the text are in an attribute of their own:

    ``` python
    ss.split_predicates
    # ('llevó cabo', 'hiciera mención')
    ```

### print_stats

Prints a table with the computed syntactic statistics.

To illustrate the method, we reuse the code from the previous example:

!!! example "Example"

    _Code_:

    ``` python
    ...

    # Print the table of computed statistics
    ss.print_stats()
    ```

    _Result_:

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
