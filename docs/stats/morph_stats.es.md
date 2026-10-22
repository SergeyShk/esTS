# Estadísticas morfológicas

``` {.python .signature}
MorphStats(source, nlp=None)
```

Las estadísticas morfológicas de un texto: la categoría gramatical y los rasgos morfológicos de cada palabra en los términos de [Universal Dependencies](https://universaldependencies.org/u/feat/), sus distribuciones y los marcadores del español calculados a partir de ellos. La fuente de datos es un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy); las estadísticas se calculan al crear el objeto.

Un texto se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`; un `Doc` debe llevar las categorías gramaticales, que vienen de un `morphologizer` (o de un `tagger` con un `attribute_ruler`), y los lemas, que vienen de un `lemmatizer`. Las palabras se toman de los tokens y los signos de puntuación y los símbolos se descartan. Un texto más largo que el `max_length` del pipeline - un millón de caracteres por defecto - hay que dividirlo en partes o subir `max_length` en un pipeline propio indicado en `nlp`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un pipeline que no es un `Language` de spaCy;
- `SourceError` - una fuente sin palabras, un `Doc` sin las categorías gramaticales o sin los lemas (un `Doc` de `spacy.blank("es")` o de un pipeline con el `lemmatizer` excluido), una cadena más larga que el `max_length` del pipeline o con un carácter sin forma UTF-8;
- `DatasetNotFoundError` - una cadena sin `nlp` cuando el modelo `es_core_news_sm` no está instalado.

=== "Código"

    ``` python
    from ests import MorphStats

    text = "Si tuviera tiempo, leería el libro que me recomendaste ayer"
    ms = MorphStats(text)
    ms.print_stats("pos", "mood")
    ```

=== "Resultado"

    ```
    -------------Part of speech-------------
    Verb                          |    3
    Noun                          |    2
    Pronoun                       |    2
    Subordinating conjunction     |    1
    Determiner                    |    1
    Adverb                        |    1

    ------------------Mood------------------
    Unknown                       |    7
    Subjunctive                   |    1
    Conditional                   |    1
    Indicative                    |    1
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `nlp` | `Language` | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Atributos

| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `words` | `tuple[str]` | Palabras |
| `lemmas` | `tuple[str]` | Lemas de las palabras |
| `tags` | `tuple[str]` | Rasgos morfológicos de las palabras como cadenas en formato CoNLL-U (`Gender=Masc|Number=Sing`, `_` sin rasgos) |

=== "Código"

    ``` python
    ms.lemmas[:4]
    ms.tags[1]
    ```

=== "Resultado"

    ```
    ('si', 'tener', 'tiempo', 'leer')
    'Mood=Sub|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin'
    ```

## Estadísticas

Cada estadística es un atributo del objeto, una tupla de los valores de un rasgo por palabra (`None` para una palabra a la que el modelo no da ningún valor del rasgo), y `get_stats` devuelve las distribuciones de sus valores. Los valores se leen de `token.pos_` y `token.morph` del análisis, es decir, por el contexto. Las estadísticas son la categoría gramatical y los quince rasgos de `MORPHOLOGY_FEATURES`; el valor `Unknown` de las tablas impresas significa que el modelo no dio a la palabra ningún valor del rasgo. Los demás rasgos que anotan los modelos (`AdvType`, `Foreign`, `NumForm`, `Number[psor]`, `PrepCase`, `Typo`, `PunctSide`, `PunctType`) no se cuentan, pero quedan en `tags`.

| Estadística | Rasgo | Valores |
| :---------- | :---- | :------ |
| `pos` | Categoría gramatical | `NOUN`, `PROPN`, `ADJ`, `ADV`, `VERB`, `AUX`, `PRON`, `DET`, `NUM`, `ADP`, `CCONJ`, `SCONJ`, `PART`, `INTJ`, `SYM`, `X` |
| `case` | Caso | `Nom`, `Acc`, `Dat`, `Com` |
| `definite` | Definitud | `Def`, `Ind` |
| `degree` | Grado | `Cmp`, `Sup`, `Abs` |
| `gender` | Género | `Masc`, `Fem` |
| `mood` | Modo | `Ind`, `Sub`, `Imp`, `Cnd` |
| `num_type` | Tipo de numeral | `Card`, `Ord`, `Frac` |
| `number` | Número | `Sing`, `Plur` |
| `person` | Persona | `1`, `2`, `3` |
| `polarity` | Polaridad | `Neg` |
| `polite` | Cortesía | `Form` |
| `poss` | Posesivo | `Yes` |
| `pron_type` | Tipo de pronombre | `Art`, `Prs`, `Dem`, `Ind`, `Int`, `Rel`, `Neg`, `Tot`, `Exc` |
| `reflex` | Reflexivo | `Yes` |
| `tense` | Tiempo verbal | `Pres`, `Past`, `Imp`, `Fut` |
| `verb_form` | Forma verbal | `Fin`, `Inf`, `Part`, `Ger` |

Un rasgo con varios valores conserva la forma de CoNLL-U: `qué`, `quién`, `cuál` tienen `pron_type` igual a `Int,Rel`, y `usted` tiene `case` igual a `Acc,Nom`. `print_stats` nombra los valores según `MORPHOLOGY_STATS_DESC` de `ests.constants`, y un valor así, con los nombres de sus partes: «Interrogative or relative», «Accusative or nominative».

!!! warning "Aviso"
    Las estadísticas valen lo que vale la anotación del modelo. `es_core_news_sm` analiza mal los verbos con pronombres enclíticos (`dámelo`, `cuéntamelo` salen como sustantivos con lemas inventados) y etiqueta los imperativos de `tú` como indicativo (`Abre la ventana` recibe `Mood=Ind`), de modo que `p_imperative` se queda corto y `p_indicative` absorbe las órdenes: en el diálogo del corpus de literatura encuentra alrededor de un imperativo de cada diez. `es_core_news_lg` apenas mejora (15 %); el modelo de transformadores `es_dep_news_trf` indicado en `nlp` encuentra el 87 %, y en el teatro `p_imperative` sube del 1,6 % al 7,5 %, a costa de cerca de 1 GB con PyTorch y cinco veces más tiempo en una CPU, y necesita antes unir los saltos de línea simples de un texto con líneas cortadas.

<div class="metric-card" markdown>

### Marcadores del español { #markers }

`get_markers()` · `print_markers()`
{ .metric-meta }

Las proporciones de las formas que marcan el registro de un texto español, cada una sobre su propia base (`MORPHOLOGY_MARKERS_DESC`), de modo que los marcadores de textos de distinta longitud pueden compararse directamente; un marcador cuya base está vacía - un texto sin verbos, sin cópula, sin adverbios - es `nan`. El subjuntivo marca la hipótesis y la subordinación, `estar` un estado frente a la propiedad de `ser`, y los adverbios en `-mente` un registro formal y escrito.

| Marcador | Proporción | Base |
| :------- | :--------- | :--- |
| `p_indicative`, `p_subjunctive`, `p_conditional`, `p_imperative` | del modo indicativo, subjuntivo, condicional e imperativo | formas personales |
| `p_infinitive`, `p_gerund`, `p_participle` | de los infinitivos, gerundios y participios | formas verbales |
| `p_ser` | de `ser` | cópulas `ser` y `estar` |
| `p_mente_adverbs` | de los adverbios en `-mente` | adverbios |

Los cuatro primeros marcadores comparten la base de las formas personales y suman uno salvo que el modelo deje alguna forma personal sin modo. Los tres siguientes comparten la base de todas las formas verbales de verbos y auxiliares: un participio que el modelo anota como adjetivo (`la casa pintada`) queda fuera de la base, los de los tiempos compuestos y la pasiva (`he leído`, `fue escrito`) quedan dentro.

La base de `p_ser` son solo los usos copulativos, leídos del análisis sintáctico: los auxiliares de la pasiva y de la perífrasis progresiva (`fue escrito`, `es financiado`, `está cantando`) quedan fuera, mientras que `es alta`, `está cansada` y `lo importante es que vengas` cuentan. Para un `Doc` sin análisis sintáctico el marcador es `nan`.

=== "Código"

    ``` python
    ms.get_markers()
    ```

=== "Resultado"

    ```
    {'p_indicative': 0.3333333333333333,
     'p_subjunctive': 0.3333333333333333,
     'p_conditional': 0.3333333333333333,
     'p_imperative': 0.0,
     'p_infinitive': 0.0,
     'p_gerund': 0.0,
     'p_participle': 0.0,
     'p_ser': nan,
     'p_mente_adverbs': 0.0}
    ```

</div>

## Métodos

`get_stats(*args, filter_none=False)` devuelve las distribuciones de los valores de las estadísticas como un diccionario de recuentos para cada una. Las estadísticas se eligen por sus nombres separados por comas, todas sin nombres, y `filter_none=True` descarta las palabras sin el rasgo (`None`). Un nombre que no es una estadística lanza `UnknownStatError`, aquí y en `print_stats` y `explain_text`.

`print_stats(*args, filter_none=False)` muestra las distribuciones de las estadísticas elegidas como tablas, primero los valores frecuentes (el ejemplo del principio de la página), y `explain_text(*args, filter_none=False)` devuelve las palabras del texto en orden con los valores de las estadísticas elegidas.

=== "Código"

    ``` python
    ms.get_stats("pos", "mood", "tense", filter_none=True)
    ms.explain_text("pos", "mood", "tense", filter_none=True)
    ```

=== "Resultado"

    ```
    {'pos': {'SCONJ': 1, 'VERB': 3, 'NOUN': 2, 'DET': 1, 'PRON': 2, 'ADV': 1},
     'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1},
     'tense': {'Imp': 1, 'Pres': 1}}
    (('Si', {'pos': 'SCONJ'}),
     ('tuviera', {'pos': 'VERB', 'mood': 'Sub', 'tense': 'Imp'}),
     ('tiempo', {'pos': 'NOUN'}),
     ('leería', {'pos': 'VERB', 'mood': 'Cnd'}),
     ('el', {'pos': 'DET'}),
     ('libro', {'pos': 'NOUN'}),
     ('que', {'pos': 'PRON'}),
     ('me', {'pos': 'PRON'}),
     ('recomendaste', {'pos': 'VERB', 'mood': 'Ind', 'tense': 'Pres'}),
     ('ayer', {'pos': 'ADV'}))
    ```

`get_markers()` devuelve los [marcadores del español](#markers) como un diccionario, y `print_markers()` los muestra como una tabla.

=== "Código"

    ``` python
    ms.print_markers()
    ```

=== "Resultado"

    ```
                         Marker                    |   Value
    -----------------------------------------------------------
    Indicative among the finite forms              |   0.33
    Subjunctive among the finite forms             |   0.33
    Conditional among the finite forms             |   0.33
    Imperative among the finite forms              |   0.00
    Infinitive among the verb forms                |   0.00
    Gerund among the verb forms                    |   0.00
    Participle among the verb forms                |   0.00
    ser among the copulas ser and estar            |    nan
    Adverbs in -mente among the adverbs            |   0.00
    ```
