# Syntactic statistics

``` {.python .signature}
SyntaxStats(source, nlp=None)
```

The syntactic statistics of a text by its dependency tree ([Ivanov, Solnyshkina and Solovyev 2018](https://dialogue-conf.org/media/4302/ivanovvv.pdf)): the measures of the tree and of the syntactic constructions. The data source is a text or a `Doc` object of [spaCy](https://github.com/explosion/spaCy), and it has to be parsed: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, without the named entities, and a `Doc` must carry the dependencies, which come from a `parser`, the parts of speech, which come from a `morphologizer` (or a `tagger` with an `attribute_ruler`), and the lemmas, which come from a `lemmatizer`. Punctuation marks, symbols (`%`, `€`, `+`) and whitespace are no nodes of the tree, and the distances are counted in positions of words.

Raises:

- `SourceTypeError` - a source that is neither a string nor a `Doc`, a pipeline in `nlp` that is not a spaCy `Language`;
- `SourceError` - a source without words; a `Doc` without the dependencies, the parts of speech or the lemmas (a `Doc` of `spacy.blank("es")`, of a pipeline without a parser or with the `morphologizer` or the `lemmatizer` excluded); a string longer than the `max_length` of the pipeline or with a character without a UTF-8 form;
- `DatasetNotFoundError` - a string without `nlp` when the model is not installed.

The class extends the `SyntaxStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/syntax_stats/) core with the Spanish layer. The relations and features are those of the [Universal Dependencies](https://universaldependencies.org/u/dep/) annotation of the `es_core_news_sm`, `es_core_news_md` and `es_core_news_lg` models, and the statistics are as good as the parse. The clauses, the passive, the negations and the split predicates follow the rules of Spanish given in the cards of the metrics, and esTS adds its own metrics of the chains of `de`, the gerund clauses and the sentences with `se`. The constructions of the administrative style - the passive with `ser` and with `se`, the participial and gerund clauses, the chains of `de`, the split predicates - are the ones the Spanish-language guides to plain language (*lenguaje claro*) warn about. The `print_stats` table takes the descriptions of `SYNTAX_STATS_DESC` of `ests.constants`.

The `max_length` of the pipeline is a million characters by default: split a longer text into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

=== "Code"

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

=== "Result"

    ```
                             Statistic                         |  Value
    ----------------------------------------------------------------------
    Mean dependency distance                                   |   2.26
    Standard deviation of the dependency distance              |   2.15
    Mean of the longest dependencies of the sentences          |   9.00
    Share of adjacent dependencies                             |   0.48
    Depth of the dependency tree                               |   4.00
    Leaves per sentence                                        |   8.00
    Subtrees per sentence                                      |   6.50
    Mean of the nodes per leaf of the sentences                |   1.80
    Mean number of words before the root of a sentence         |   4.50
    Valency of the finite verbs                                |   4.00
    Coordination chains per sentence                           |   0.00
    Mean length of a coordination chain                        |   nan
    Clauses per sentence                                       |   1.50
    Mean length of a clause (words)                            |   9.67
    Subordinate clauses per sentence                           |   0.50
    Share of sentences with a subordinate clause               |   0.50
    Infinitive clauses per sentence                            |   0.00
    T-units per sentence                                       |   1.00
    Mean length of a T-unit (words)                            |  14.50
    Clauses per T-unit                                         |   1.50
    Share of T-units with a subordinate clause                 |   0.50
    Verb phrases per T-unit                                    |   1.50
    Coordinate phrases per clause                              |   0.00
    Complex nominals per clause                                |   1.33
    Modifiers per noun phrase                                  |   1.00
    Prepositional chains per sentence                          |   0.50
    Maximum length of a prepositional chain                    |    2
    Chains of de per sentence                                  |   0.50
    Maximum length of a chain of de                            |    2
    Participial clauses per sentence                           |   0.50
    Mean length of a participial clause (words)                |   3.00
    Gerund clauses per sentence                                |   0.00
    Mean length of a gerund clause (words)                     |   nan
    Share of passive forms among the verbs                     |   0.67
    Share of agentless forms among the passive ones            |   0.50
    Passives with se per sentence                              |   0.50
    Impersonal sentences with se per sentence                  |   0.00
    Infinitives per sentence                                   |   0.00
    Words of negation per sentence                             |   0.50
    Split predicates per sentence                              |   1.00
    Share of nominal subjects before their head                |   0.50
    Share of nominal objects before their head                 |   0.00
    Edit distance of the parts of speech of adjacent sentences |   0.47
    Syntactic similarity of adjacent sentences                 |   0.45
    Ratio of nouns to verbs                                    |   3.00
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source: a text or a `Doc` with the dependencies and the lemmas |
| `nlp` | `Language` | `None` | spaCy pipeline that parses a string; the model `es_core_news_sm` of `ests.utils.get_nlp` if not given |

## Attributes

--8<-- "stats/syntax_stats.md:SyntaxStats-attributes"

The attributes of the constructions of esTS are `n_de_chains`, `n_gerund_clauses`, `n_se_passives` and `n_impersonal_se` (`int`): the numbers of the chains of `de`, of the gerund clauses, of the passives with `se` and of the impersonal sentences with `se`.

=== "Code"

    ``` python
    ss.n_clauses, ss.n_nouns, ss.n_verbs
    ss.n_de_chains, ss.n_se_passives, ss.split_predicates
    ss.c_children
    ss.c_deps
    ss.sents[0]
    ```

=== "Result"

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

## Metrics

Every metric is an attribute of the object, computed when it is created, and `get_stats` gives the metrics of the table. The measures of a sentence (the longest dependency, the depth, the nodes per leaf) are averaged over the sentences; the constructions are given per sentence.

| Metric | Measures | Range | Higher means |
| :----- | :------- | :---- | :----------- |
| [`mean_dependency_distance`](#dependency_distances) | Mean distance between a word and its head | 1 and above, `nan` without dependencies | Harder to process |
| [`std_dependency_distance`](#dependency_distances) | Standard deviation of the dependency distance | 0 and above, `nan` without dependencies | Less even distances |
| [`max_dependency_distance`](#dependency_distances) | Mean of the longest dependencies of the sentences that have dependencies | 1 and above, `nan` without dependencies | Longer longest dependencies |
| [`p_adjacent_dependencies`](#dependency_distances) | Share of the dependencies of length 1 | 0-1, `nan` without dependencies | More links between neighbours |
| [`tree_depth`](#tree_depth) | Mean depth of the tree of a sentence | 0 and above | Deeper embedding |
| [`leaves_per_sent`](#leaves) | Leaves per sentence | 0 and above | Longer or flatter sentences |
| [`subtrees_per_sent`](#leaves) | Subtrees per sentence | 0 and above | More phrases in a sentence |
| [`nodes_per_leaf`](#leaves) | Mean over the sentences of the words per leaf | 1 and above, `nan` for a sentence without leaves | Longer branches |
| [`words_before_root`](#words_before_root) | Mean number of the words before the root of a sentence | 0 and above, `nan` without a root among the words | A later main predicate |
| [`verb_valency`](#valency) | Mean number of the dependents of a finite verb | 0 and above, `nan` without finite verbs | More dependents of a verb |
| [`coordination_chains_per_sent`](#coordination_chains) | Coordination chains per sentence | 0 and above | More coordination |
| [`mean_coordination_chain_len`](#coordination_chains) | Mean length of a coordination chain in words | 2 and above, `nan` without chains | Longer enumerations |
| [`clauses_per_sent`](#clauses) | Clauses per sentence | 0 and above | More clauses in a sentence |
| [`mean_clause_len`](#clauses) | Mean length of a clause in words | 1 and above, `nan` without clauses | Longer clauses |
| [`subordinate_clauses_per_sent`](#subordinate_clauses) | Subordinate clauses per sentence | 0 and above | More subordination |
| [`p_complex_sents`](#subordinate_clauses) | Share of the sentences with a subordinate clause | 0-1 | More complex sentences |
| [`infinitive_clauses_per_sent`](#infinitive_clauses) | Infinitive clauses per sentence | 0 and above | More infinitive clauses |
| [`t_units_per_sent`](#l2sca) | T-units per sentence (T/S) | 0 and above | More main clauses in a sentence |
| [`mean_t_unit_len`](#l2sca) | Mean length of a T-unit in words (MLT) | 1 and above, `nan` without T-units | Longer T-units |
| [`clauses_per_t_unit`](#l2sca) | Clauses per T-unit (C/T) | 1 and above, `nan` without T-units | More subordination |
| [`p_complex_t_units`](#l2sca) | Share of the T-units with a subordinate clause (CT/T) | 0-1, `nan` without T-units | More complex T-units |
| [`verb_phrases_per_t_unit`](#l2sca) | Verb phrases per T-unit (VP/T) | 0 and above, `nan` without T-units | More verb phrases |
| [`coordinate_phrases_per_clause`](#l2sca) | Coordinate phrases per clause (CP/C) | 0 and above, `nan` without clauses | More phrasal coordination |
| [`complex_nominals_per_clause`](#l2sca) | Complex nominals per clause (CN/C) | 0 and above, `nan` without clauses | Denser noun phrases |
| [`modifiers_per_noun`](#noun_modifiers) | Mean number of the modifiers of a noun | 0 and above, `nan` without nouns | Heavier noun phrases |
| [`prep_chains_per_sent`](#prep_chains) | Chains of nested complements with a preposition per sentence | 0 and above | More nested complements |
| [`max_prep_chain_len`](#prep_chains) | Length of the longest prepositional chain | 0, or 2 and above | Longer chains |
| [`de_chains_per_sent`](#de_chains) | Chains of `de` per sentence | 0 and above | More chains |
| [`max_de_chain_len`](#de_chains) | Longest chain of `de` of the text | 0 without chains, otherwise 2 and above | A longer chain |
| [`participle_clauses_per_sent`](#participle_clauses) | Participial clauses per sentence | 0 and above | More participial clauses |
| [`mean_participle_clause_len`](#participle_clauses) | Mean length of a participial clause in words | 2 and above, `nan` without participial clauses | Longer participial clauses |
| [`gerund_clauses_per_sent`](#gerund_clauses) | Gerund clauses per sentence | 0 and above | More gerund clauses |
| [`mean_gerund_clause_len`](#gerund_clauses) | Mean length of a gerund clause in words | 2 and above, `nan` without gerund clauses | Longer gerund clauses |
| [`p_passive`](#passive) | Share of the passive forms among the verb forms | 0-1, `nan` without verb forms | More passive |
| [`p_agentless_passive`](#passive) | Share of the forms with no agent among the passive ones | 0-1, `nan` without passive forms | More passive without an agent |
| [`se_passives_per_sent`](#se) | Passives with `se` per sentence | 0 and above | More passives with `se` |
| [`impersonal_se_per_sent`](#se) | Impersonal sentences with `se` per sentence | 0 and above | More impersonal sentences |
| [`infinitives_per_sent`](#constructions) | Infinitives per sentence | 0 and above | More infinitives |
| [`negations_per_sent`](#constructions) | Words of negation per sentence | 0 and above | More negation |
| [`split_predicates_per_sent`](#constructions) | Split predicates per sentence | 0 and above | More split predicates |
| [`p_preverbal_subjects`](#word_order) | Share of the nominal subjects before their head | 0-1, `nan` without nominal subjects | Fewer inverted subjects |
| [`p_preverbal_objects`](#word_order) | Share of the nominal direct objects before their head | 0-1, `nan` without nominal objects | More fronted objects |
| [`pos_edit_distance`](#similarity) | Mean edit distance of the parts of speech of adjacent sentences over the longer one | 0-1, `nan` for one sentence | Less alike sentences |
| [`syntax_similarity`](#similarity) | Mean similarity of the dependency triples of adjacent sentences | 0-1, `nan` for one sentence | More alike sentences |
| [`noun_verb_ratio`](#noun_verb_ratio) | Ratio of the nouns to the verb forms | 0 and above, `nan` without verb forms | A more nominal style |

The functions of the cards are imported from `ests.syntax_stats`; those of the measures of the tree that esTS does not re-export are on the [anyTS page](https://sergeyshk.github.io/anyTS/stats/syntax_stats/).

<div class="metric-card" markdown>

### Dependency distance { #dependency_distances }

`mean_dependency_distance` · `std_dependency_distance` · `max_dependency_distance` · `p_adjacent_dependencies`
{ .metric-meta }

The dependency distance (Liu 2008) is the distance between a word and its head in positions of words, punctuation left out; the head of a sentence has none. `mean_dependency_distance` and `std_dependency_distance` are the mean and the standard deviation of the distances of the text, `max_dependency_distance` the mean of the longest distance of every sentence that has one, and `p_adjacent_dependencies` the share of the distances of 1. One-word sentences enter none of the metrics. The distances are those of `calc_dependency_distances` of `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Tree depth { #tree_depth }

`tree_depth`
{ .metric-meta }

The depth of the dependency tree of a sentence is the longest path from its head to a leaf, in relations between words, 0 for a sentence of one word; the metric is its mean over the sentences. The depth is that of `calc_tree_depth` of `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Leaves and subtrees { #leaves }

`leaves_per_sent` · `subtrees_per_sent` · `nodes_per_leaf`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-leaves"

The distribution of the words by number of dependents is the attribute `c_children`.

</div>

<div class="metric-card" markdown>

### Words before the root { #words_before_root }

`words_before_root` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-words_before_root"

</div>

<div class="metric-card" markdown>

### Valency of the finite verbs { #valency }

`verb_valency`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:calc_valency"

A finite verb is a word tagged `VERB` with `VerbForm=Fin` (`is_finite_verb` of `anyts.utils`). The Spanish models tag the participle of a compound tense or of the passive with `ser` (`ha llegado`, `fue construida`) as the verb and its auxiliary as `AUX`, so such predicates are left out.

</div>

<div class="metric-card" markdown>

### Coordination chains { #coordination_chains }

`coordination_chains_per_sent` · `mean_coordination_chain_len`
{ .metric-meta }

A coordination chain is a group of words linked by `conj`: `manzanas, peras y ciruelas` is one chain of three. A nested coordination and an enumeration split between several heads are one chain too; the length of a chain is the number of its words. The chains are those of `calc_coordination_chains` of `anyts.syntax_stats`.

</div>

<div class="metric-card" markdown>

### Clauses { #clauses }

`clauses_per_sent` · `mean_clause_len`
{ .metric-meta }

``` {.python .signature}
is_clause_head(token)
```

Checks whether a word heads a clause: the head of the sentence or, by the form of its predicate ([`predicate_form`](#verb-forms)), a word with `ccomp`, `advcl`, `acl` (a relative clause included), `csubj` or `parataxis` (`anyts.constants.CLAUSE_DEPS`). A finite predicate heads its clause (`dijo que había llegado`, `estaba cantando`, `los regalos que te van a dar`, `sé que os habéis posado`), also under `xcomp`, which the models give to some finite complements; a predicate in the form of a participle or a gerund heads no clause of that kind - such predicates are counted apart (`llegando tarde`, `habiendo llegado tarde`) - and neither does one in the form of an infinitive under `acl` (`el deseo de irse`, `el miedo de ser robado`). Under `xcomp` an infinitive heads a clause by `is_infinitive_clause`, and a predicative adjective (`parece cansado`) heads none. A parenthetical (`parataxis`) and a coordinated predicate (`conj` of the head of a clause) count only when they can be a predicate ([`is_predicate`](#is_predicate)), so that parentheticals such as `por ejemplo` are no clauses; an infinitive the models attach as `conj` or `csubj` to the verb of its periphrasis (`hay que salir`, `llega a convertirse`) makes one predicate with it (`is_infinitive_periphrasis`). It is the [`is_clause_head`](https://sergeyshk.github.io/anyTS/stats/syntax_stats/#clauses) of the anyTS core with the Spanish rules of `is_infinitive_periphrasis` and `predicate_form`.

``` {.python .signature}
is_infinitive_clause(token)
```

Checks whether an infinitive under `xcomp` heads a clause of its own: a predicate in the form of an infinitive that completes its head (`quiere salir`, `le hizo reír`, `quiere ser médico`, `quiere ser elegido`, `cree haber ganado`), unless the two make one predicate (`is_infinitive_periphrasis`: `puede salir`, `parece dormir`) or the word it completes heads no clause (`is_clause_head`): an infinitive in a gerund or participial phrase belongs to that phrase (`intentando salir`, `destinada a disculpar`).

``` {.python .signature}
is_infinitive_periphrasis(token)
```

Checks whether an infinitive makes one predicate with its head: an infinitive under `xcomp` of a verb of `RAISING_VERBS`, `parecer` (`parece dormir`), or a periphrasis. In a periphrasis the head is a verb of `INFINITIVE_PERIPHRASES` (NGLE, ch. 28) and the infinitive is linked to it by one of the words of that verb - a `mark`, `case` or `cc` before the infinitive, or the word right before it, the old spelling `á` read as `a`. The verbs are `poder`, `soler` and `deber` with no word (`puede salir`, `suele salir`), `deber de`, `tener que`, `haber que`, `haber de`, `ir a`, `venir a`, `pasar a`, `volver a`, `tornar a`, `empezar a` and `por`, `comenzar a` and `por`, `principiar a`, `poner a`, `echar a`, `romper a`, `llegar a`, `alcanzar a`, `acabar de` and `por`, `terminar de` and `por`, `dejar de`, `cesar de`, `parar de`, `estar para` and `por`. The lemma of the head is that of the model, or of `ests.utils.lemmatize` when the model gives none of these verbs (it can read a verb opening a sentence as a proper noun: `Solía salir`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

The mean length of a clause is the number of the words over the number of the clauses.

</div>

<div class="metric-card" markdown>

### Subordinate clauses { #subordinate_clauses }

`subordinate_clauses_per_sent` · `p_complex_sents`
{ .metric-meta }

``` {.python .signature}
is_subordinate_clause_head(token)
```

Checks whether a word heads a subordinate clause: a clause head (`is_clause_head`) whose predicate is no infinitive, with `ccomp`, `advcl`, `acl` or `csubj` (`anyts.constants.SUBORDINATE_CLAUSE_DEPS`) or under `xcomp`, or a coordinated predicate of a subordinate clause, by the relation of the first word up its chain of conjuncts. A clause under `conj` or `parataxis` with a subordinating conjunction (`is_subordinating_mark`) is subordinate too, with its conjuncts that have a subject of their own: the models attach a clause after `y`, `pero` or `sino` as a conjunct of the clause before it (`sino porque le había cobrado afición`, `quiero salir y que vengas`). An infinitive clause (`quiere salir`, `salió para ayudar`) is counted apart, among the [infinitive clauses](#infinitive_clauses).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

`p_complex_sents` is the share of the sentences with at least one subordinate clause.

``` {.python .signature}
is_subordinating_mark(token)
```

Checks whether a word with the relation `mark` is a subordinating conjunction: one of `SUBORDINATING_MARKS` with the words of its fixed expression (`que`, `si`, `como`, `cuando`, `porque`, `aunque`, `ya que`, `puesto que`), but not `que` after `sino`, which coordinates (`no lo dijo, sino que lo calló`). The models parse `para que`, `sin que` and `hasta que` with a mark `que` of their own. Prepositions are left out: `a` and `de` before an infinitive mostly make a periphrasis (`iba a preparar`, `ha de vivir`). It is the hook `is_subordinating_mark` of the `SyntaxStats` of the anyTS core.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    from ests.syntax_stats import is_clause_head, is_subordinate_clause_head
    from ests.utils import get_nlp

    nlp = get_nlp()
    doc = nlp("Él quiere salir, pero tiene que quedarse porque parece cansado.")
    [token.text for token in doc if is_clause_head(token)]
    [token.text for token in doc if is_subordinate_clause_head(token)]
    doc = nlp("Se sentaba a sus pies, no por servicio, sino porque le había cobrado afición.")
    [token.text for token in doc if is_subordinate_clause_head(token)]
    ```

=== "Result"

    ```
    ['quiere', 'salir', 'tiene', 'parece']
    ['parece']
    ['cobrado']
    ```

</div>

<div class="metric-card" markdown>

### Infinitive clauses { #infinitive_clauses }

`infinitive_clauses_per_sent`
{ .metric-meta }

``` {.python .signature}
is_infinitive_clause_head(token)
```

Checks whether a word heads an infinitive clause: a clause head (`is_clause_head`) whose own predicate is an infinitive under `xcomp`, `ccomp`, `advcl` or `csubj` (`quiere salir`, `le pidió salir`, `salió para ayudar`, `es difícil decirlo`), an infinitive under `conj` or `parataxis` with a subordinating conjunction, or an infinitive conjunct of one; a finite conjunct of an infinitive (`quiero salir y que vengas`) is none. These clauses count among the clauses, but not among the subordinate ones: grammars take an infinitive complement for a part of a simple sentence, and the published correlations of the subordination were obtained for finite subordinate clauses. It is the [`is_infinitive_clause_head`](https://sergeyshk.github.io/anyTS/stats/syntax_stats/#infinitive_clauses) of the anyTS core over `is_clause_head`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    from ests.syntax_stats import is_clause_head, is_infinitive_clause_head
    from ests.utils import get_nlp

    doc = get_nlp()("Quiere salir y volver, pero intentando salir se cayó.")
    [token.text for token in doc if is_clause_head(token)]
    [token.text for token in doc if is_infinitive_clause_head(token)]
    ```

=== "Result"

    ```
    ['Quiere', 'salir', 'volver', 'cayó']
    ['salir', 'volver']
    ```

</div>

<div class="metric-card" markdown>

### Production units of L2SCA { #l2sca }

`t_units_per_sent` · `mean_t_unit_len` · `clauses_per_t_unit` · `p_complex_t_units` · `verb_phrases_per_t_unit` · `coordinate_phrases_per_clause` · `complex_nominals_per_clause` · [Lu 2010](https://doi.org/10.1075/ijcl.15.4.02lu)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-l2sca"

The clauses and the subordinate clauses are those of the Spanish rules of the cards above, and a periphrasis is one verb phrase (`puede venir`). The models attach the infinitive of some periphrases as a conjunct of their verb (`tiene que venir`): it stays inside the verb phrase of the verb, but the pair counts as a coordinate phrase too.

</div>

<div class="metric-card" markdown>

### Modifiers of a noun { #noun_modifiers }

`modifiers_per_noun`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:count_noun_modifiers"

The nouns are the words tagged `NOUN` or `PROPN`: `la nueva casa de mi padre` gives `casa` three modifiers, `la`, `nueva` and `padre`.

</div>

<div class="metric-card" markdown>

### Prepositional chains { #prep_chains }

`prep_chains_per_sent` · `max_prep_chain_len` · [Profiling-UD](https://aclanthology.org/2020.lrec-1.883/)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-prep_chains"

The chains of `de` of esTS ([`de_chains_per_sent`](#de_chains)) are counted apart: their links are complements of `de` alone (`la revisión de las cuentas del organismo`), the marker of the nominal style of Spanish, and those of a prepositional chain complements with any preposition (`sobre la mesa en la sala`).

</div>

<div class="metric-card" markdown>

### Chains of de { #de_chains }

`de_chains_per_sent` · `max_de_chain_len`
{ .metric-meta }

``` {.python .signature}
calc_de_chains(tokens)
```

The lengths of the chains of `de` in the order of the words: the chains of [`calc_modifier_chains`](#calc_modifier_chains) whose modifiers are complements with `de`; `el aumento de la eficiencia del uso de los recursos` is a chain of length 3, and a single complement (`el uso del agua`) is no chain.

``` {.python .signature}
is_de_modifier(token)
```

Checks whether a word is a complement introduced by `de`: a word with the relation `nmod` whose preposition (`case`) is `de` or its contraction `del` (`DE_PREPOSITIONS`): `el uso del agua`, but not `la vuelta al campo`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Sequence of tokens (`calc_de_chains`) |
| `token` | `Token` | - | Token (`is_de_modifier`) |

`max_de_chain_len` is the longest chain of the text, 0 without chains.

=== "Code"

    ``` python
    from ests.syntax_stats import calc_de_chains
    from ests.utils import get_nlp

    calc_de_chains(get_nlp()("El aumento de la eficiencia del uso de los recursos fue notable."))
    ```

=== "Result"

    ```
    [3]
    ```

</div>

<div class="metric-card" markdown>

### Participial clauses { #participle_clauses }

`participle_clauses_per_sent` · `mean_participle_clause_len`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-participle_clauses"

``` {.python .signature}
is_participle_clause(token)
```

Checks whether a word heads a participial clause: a participle ([`is_participle`](#verb-forms)) that is not the head of the sentence, carries no auxiliary or copula ([`has_auxiliary`](#verb-forms)) and has at least one dependent ([`calc_valency`](#valency)). `la casa, construida por los obreros, se vendió` has one, while `ha pintado` and `fue construida` are predicates. `SyntaxStats` counts the participial clauses by the same rule.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    from ests.syntax_stats import is_participle_clause, subtree_len
    from ests.utils import get_nlp

    doc = get_nlp()("La casa, construida por los obreros en 1900, fue vendida.")
    [(token.text, subtree_len(token)) for token in doc if is_participle_clause(token)]
    ```

=== "Result"

    ```
    [('construida', 6)]
    ```

</div>

<div class="metric-card" markdown>

### Gerund clauses { #gerund_clauses }

`gerund_clauses_per_sent` · `mean_gerund_clause_len`
{ .metric-meta }

``` {.python .signature}
is_gerund_clause(token)
```

Checks whether a word heads a gerund clause: a predicate in the form of a gerund ([`predicate_form`](#verb-forms)), simple or compound (`llegando tarde`, `habiendo llegado tarde`, `siendo elegido presidente`), that is not the head of the sentence and has at least one dependent besides its auxiliaries and copulas ([`calc_valency`](#valency)). The periphrases are left out: one with a finite auxiliary (`está cantando`) is a finite predicate, and a gerund the models attach as `xcomp` or `advcl` to a verb of `GERUND_PERIPHRASIS_VERBS` - `quedar`, `llevar`, `seguir`, `venir`, `ir`, `andar`, `continuar`, `acabar` (`sigue trabajando`, `acabó reconociendo`) - heads no clause. The length of a clause is the number of the words in the subtree of the gerund (`subtree_len`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    from ests.syntax_stats import is_gerund_clause
    from ests.utils import get_nlp

    doc = get_nlp()("Llegando tarde, encontró la puerta cerrada y siguió trabajando.")
    [token.text for token in doc if is_gerund_clause(token)]
    ```

=== "Result"

    ```
    ['Llegando']
    ```

</div>

<div class="metric-card" markdown>

### Passive { #passive }

`p_passive` · `p_agentless_passive`
{ .metric-meta }

``` {.python .signature}
is_passive(token)
```

Checks whether a word is a passive verb form: a verb (`VERB`) that is a participle with the auxiliary `ser` (`PASSIVE_AUX`) as `aux` or `cop` - `la casa fue construida`, also when the models read the auxiliary as a copula, `el proyecto es financiado` - or that carries the `se` of the passive (`expl:pass`, `SE_PASSIVE_DEP`: `se construyó la casa`). A participle that modifies a noun (`la casa construida por los obreros`) is a participial clause instead.

``` {.python .signature}
is_agentless(token)
```

Checks whether a passive form has no agent: none of its dependents is one of `is_agent` - `la casa fue construida`, but not `la casa fue construida por los obreros`. A word that is no passive form (`is_passive`) gives `False`.

``` {.python .signature}
is_agent(token)
```

Checks whether a word is the agent of a passive: a complement whose preposition (`case`) is `por` (`AGENT_PREPOSITION`), whatever its relation, since the models have no `obl:agent`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

The verb forms of `p_passive` are the words tagged `VERB`.

=== "Code"

    ``` python
    from ests.syntax_stats import is_agentless, is_passive
    from ests.utils import get_nlp

    doc = get_nlp()(
        "La casa fue construida por los obreros y el proyecto es financiado por el Estado. "
        "Se construyó la casa."
    )
    [(token.text, is_agentless(token)) for token in doc if is_passive(token)]
    ```

=== "Result"

    ```
    [('construida', False), ('financiado', False), ('construyó', True)]
    ```

</div>

<div class="metric-card" markdown>

### Sentences with se { #se }

`se_passives_per_sent` · `impersonal_se_per_sent`
{ .metric-meta }

`se_passives_per_sent` counts the `se` of the passive (`expl:pass`, `SE_PASSIVE_DEP`: `se construyó la casa`) per sentence, `impersonal_se_per_sent` the `se` of an impersonal sentence (`expl:impers`, `SE_IMPERSONAL_DEP`: `se vive bien`, `aquí se trabaja mucho`), as the model labels them. A verb with the `se` of the passive is a passive form of `p_passive` too.

!!! warning "Warning"
    `es_core_news_sm` tells the three `se` of Spanish apart poorly - it rarely marks an impersonal `se` and reads `se fue dando un portazo` as a passive - so read `se_passives_per_sent` and `impersonal_se_per_sent` together rather than apart.

=== "Code"

    ``` python
    ss = SyntaxStats("Se construyó la casa en un año. Aquí se trabaja mucho.")
    ss.se_passives_per_sent, ss.impersonal_se_per_sent
    ```

=== "Result"

    ```
    (0.5, 0.5)
    ```

</div>

<div class="metric-card" markdown>

### Infinitives, negations and split predicates { #constructions }

`infinitives_per_sent` · `negations_per_sent` · `split_predicates_per_sent`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-constructions"

``` {.python .signature}
is_negation(token)
```

Checks whether a word is a word of negation: a word with `Polarity=Neg`, which the models give to `no` alone, or one of `NEGATION_WORDS` in any case - `no`, `nunca`, `jamás`, `nada`, `nadie`, `ninguno` with its forms, `tampoco`; a conjunction (`ni` of `ni... ni`) is none. Every such word counts, so the negative concord of Spanish, where one negation is written twice (`no vino nadie`), gives two. `SyntaxStats` counts the negations by the same rule.

``` {.python .signature}
find_split_predicates(tokens)
```

``` {.python .signature}
is_light_verb(token)
```

``` {.python .signature}
is_split_predicate_noun(token, verb)
```

The split predicates, pairs of a verb and a noun in the order of the words, replace a verb with a light verb and a noun: `hacer una revisión` instead of `revisar`. A light verb (`is_light_verb`) is a `VERB` with a lemma of `LIGHT_VERBS` - `hacer`, `dar`, `tomar`, `tener`, `poner`, `llevar`, `prestar`, `efectuar`, `realizar`, `proceder`, `proporcionar`, `ejercer`. Its nominal part (`is_split_predicate_noun`) is a `NOUN` whose lemma is derived from a verb, by the rule of the [verbal nouns](style_stats.md#verbal_nouns) (`revisión`, `decisión`, `uso`), or one of the nouns of `SPLIT_PREDICATE_NOUNS` - `cabo`, `cargo`, `caso`, `comienzo`, `cuenta`, `efecto`, `fin`, `gala`, `hincapié`, `lugar`, `manifiesto`, `marcha`, `parte` - with a verb `verb` of its fixed expression (`llevar a cabo`, `tomar parte`, `poner de manifiesto`, `tener lugar`), so `poner en primer lugar la seguridad` is none. A verb takes one nominal part at most, preferred by relation in the order `compound`, `obj`, `nsubj` (only with the `se` of the passive: `se tomó la decisión`), `iobj`, `nmod`, `obl`. A complement with a preposition is the nominal part only in a fixed expression (`poner de manifiesto`) or with a verb of `PREPOSITIONAL_LIGHT_VERBS`, `proceder` (`se procedió a la votación`); the agent of a passive never is. The pairs found are in the attribute `split_predicates`.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |
| `tokens` | `Doc` / `Span` / `list[Token]` | - | Sequence of tokens (`find_split_predicates`) |
| `verb` | `Token` | - | Verb the noun depends on (`is_split_predicate_noun`) |

=== "Code"

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

=== "Result"

    ```
    [(procedió, votación), (tomó, parte)]
    ['No', 'nadie']
    ```

</div>

<div class="metric-card" markdown>

### Order of the subjects and the objects { #word_order }

`p_preverbal_subjects` · `p_preverbal_objects` · [Profiling-UD](https://aclanthology.org/2020.lrec-1.883/)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-word_order"

Spanish puts the subject after the verb more often than English does (`llegó el tren`, `me gusta el café`). A fronted object comes back as a clitic (`el libro lo compré ayer`), and the models take the noun for an indirect object, so the share of the nominal objects before their head stays near 0.

</div>

<div class="metric-card" markdown>

### Similarity of adjacent sentences { #similarity }

`pos_edit_distance` · `syntax_similarity` · [Coh-Metrix](https://doi.org/10.1017/CBO9780511894664)
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-similarity"

</div>

<div class="metric-card" markdown>

### Ratio of the nouns to the verbs { #noun_verb_ratio }

`noun_verb_ratio`
{ .metric-meta }

--8<-- "stats/syntax_stats.md:SyntaxStats-noun_verb_ratio"

</div>

## Methods

The methods `get_stats`, `to_dataframe`, `print_stats` and `describe` are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the syntactic statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    ss = SyntaxStats(text)
    ss.get_stats()
    ss.describe("tree_depth"), ss.describe("de_chains_per_sent")
    ```

=== "Result"

    ```
    {'mean_dependency_distance': 2.259259259259259,
     'std_dependency_distance': 2.1532506449997975,
     'max_dependency_distance': 9.0,
     'p_adjacent_dependencies': 0.48148148148148145,
     'tree_depth': 4.0,
     'leaves_per_sent': 8.0,
     'subtrees_per_sent': 6.5,
     'nodes_per_leaf': 1.8015873015873014,
     'words_before_root': 4.5,
     'verb_valency': 4.0,
     'coordination_chains_per_sent': 0.0,
     'mean_coordination_chain_len': nan,
     'clauses_per_sent': 1.5,
     'mean_clause_len': 9.666666666666666,
     'subordinate_clauses_per_sent': 0.5,
     'p_complex_sents': 0.5,
     'infinitive_clauses_per_sent': 0.0,
     't_units_per_sent': 1.0,
     'mean_t_unit_len': 14.5,
     'clauses_per_t_unit': 1.5,
     'p_complex_t_units': 0.5,
     'verb_phrases_per_t_unit': 1.5,
     'coordinate_phrases_per_clause': 0.0,
     'complex_nominals_per_clause': 1.3333333333333333,
     'modifiers_per_noun': 1.0,
     'prep_chains_per_sent': 0.5,
     'max_prep_chain_len': 2,
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
     'p_preverbal_subjects': 0.5,
     'p_preverbal_objects': 0.0,
     'pos_edit_distance': 0.47058823529411764,
     'syntax_similarity': 0.45,
     'noun_verb_ratio': 3.0}
    (None, None)
    ```

The functions work with spaCy tokens: the `calc_*` and `find_*` functions and `dependency_triples` take a sequence of tokens (`Doc`, `Span` or a list), the `is_*`, `has_*` and `count_*` functions a single token, and `calc_edit_distance` and `calc_multiset_similarity` lists of the items of sentences; the words of a sequence are the tokens of `is_word` of `anyts.utils`. The functions of the dependency tree come from the core, those of the Spanish constructions are esTS's own.

## Words of a sequence { #get_words }

--8<-- "stats/syntax_stats.md:get_words"

## Base relation { #base_dep }

--8<-- "stats/syntax_stats.md:base_dep"

## Dependent words { #get_children }

--8<-- "stats/syntax_stats.md:get_children"

--8<-- "stats/syntax_stats.md:subtree_len"

## Verb forms { #verb-forms }

``` {.python .signature}
predicate_form(token)
```

The verb form of a predicate by the forms (`VerbForm`) of its auxiliaries and copulas (`aux`, `cop`): a finite auxiliary makes the predicate finite (`había llegado`, `estaba cantando`); otherwise the first auxiliary decides (`de haber matado` is an infinitive, `siendo elegido` a gerund), and without auxiliaries the word itself. A participle auxiliary counts as finite: `sido` and `estado` follow a form of `haber`, which the models may attach to another word (`hubieras sido albañil`). An auxiliary the model leaves without a form is read by its ending when it is a verb of `AUXILIARY_VERBS` (`habéis llegado`) - an infinitive in `-r` and a gerund in `-ndo`, enclitics after them (`ENCLITICS`), a finite form otherwise - and skipped when it is not (the old spelling `á`). It is the `predicate_form` of the anyTS core with the Spanish reading of an auxiliary without a form. The form is `'Fin'`, `'Inf'`, `'Ger'` or `'Part'`, an empty string for a word with no verb form.

``` {.python .signature}
is_participle(token)
```

``` {.python .signature}
is_gerund(token)
```

``` {.python .signature}
has_auxiliary(token)
```

`is_participle` checks whether a token is a participle (`VerbForm=Part`) whatever its part of speech, since the models tag a participle that modifies a noun as an adjective (`la casa pintada`); `is_gerund` whether it is a gerund (`VerbForm=Ger`); `has_auxiliary` whether it carries an auxiliary or a copula (`aux`, `cop`).

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `token` | `Token` | - | Token |

=== "Code"

    ``` python
    from ests.syntax_stats import is_participle, predicate_form
    from ests.utils import get_nlp

    doc = get_nlp()(
        "Dijo que había llegado tarde. Lo acusan de haber matado al rey siendo elegido presidente."
    )
    [(token.text, predicate_form(token)) for token in doc if is_participle(token)]
    ```

=== "Result"

    ```
    [('llegado', 'Fin'), ('matado', 'Inf'), ('elegido', 'Ger')]
    ```

## Predicate of a clause { #is_predicate }

--8<-- "stats/syntax_stats.md:is_predicate"

## Chains of modifiers { #calc_modifier_chains }

--8<-- "stats/syntax_stats.md:calc_modifier_chains"

## Complements with a preposition { #is_prep_complement }

--8<-- "stats/syntax_stats.md:is_prep_complement"

## Dependency triples { #dependency_triples }

--8<-- "stats/syntax_stats.md:dependency_triples"

## Edit distance and multiset similarity { #calc_edit_distance }

--8<-- "stats/syntax_stats.md:calc_edit_distance"

--8<-- "stats/syntax_stats.md:calc_multiset_similarity"
