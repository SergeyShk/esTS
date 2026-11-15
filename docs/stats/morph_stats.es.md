# Estadísticas morfológicas

``` {.python .signature}
MorphStats(source)
```

<!-- core: stats/morph_stats.md:MorphStats e18b976 -->
Las estadísticas morfológicas de un texto: la categoría gramatical y los rasgos de [Universal Dependencies](https://universaldependencies.org/u/feat/) de cada palabra, contados por valor o dados palabra por palabra. La fuente de datos es un texto, un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy) o un `Document` de [anySeg](https://github.com/SergeyShk/anySeg); las palabras son las palabras de Universal Dependencies de su [documento](https://sergeyshk.github.io/anyTS/document/) con una letra o una cifra (el español `del` da `de` y `el`), y sus categorías gramaticales y sus rasgos son sus columnas `upos` y `feats`. Una biblioteca de un idioma anota una cadena en su `parse`, o lee los rasgos en su propio `analyze`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena, ni un `Doc`, ni un `Document`, un `parse` que no devuelve un `Document`, un `analyze` que no da objetos `MorphWord`;
- `SourceError` - palabras sin categorías gramaticales, una fuente sin palabras.

La clase extiende el `MorphStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/morph_stats/) con la capa del español y los [marcadores del español](#markers); las estadísticas se calculan al crear el objeto. En esTS la fuente de datos es un texto, un `Doc` o un `Document`: un texto recibe los análisis de [esMorph](https://github.com/SergeyShk/esMorph) en el contexto de sus oraciones, sin spaCy, y un `Doc` debe llevar las categorías gramaticales, que vienen de un `morphologizer` (o de un `tagger` con un `attribute_ruler`), y los lemas, que vienen de un `lemmatizer`. Las palabras son las del documento con una letra o una cifra: en un texto las palabras de una contracción y de un verbo con clíticos son palabras aparte (`del` - `de` + `el`, `dámelo` - `da` + `me` + `lo`), mientras que un `Doc` conserva entero el token del modelo. Las tablas de `print_stats` y `print_markers` toman las descripciones de `MORPHOLOGY_STATS_DESC` y `MORPHOLOGY_MARKERS_DESC` de `ests.constants`.

Además, en esTS una fuente que no es ni una cadena, ni un `Doc` ni un `Document` lanza `SourceTypeError`, y un `Doc` sin los lemas (de un pipeline con el `lemmatizer` excluido) lanza `SourceError`.

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
| `source` | `str` / `Doc` / `Document` | - | Fuente de datos |

## Atributos

<!-- core: stats/morph_stats.md:MorphStats-attributes 0edcb8a -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `words` | `tuple[str]` | Palabras del texto |
| `tags` | `tuple[str]` | Rasgos de cada palabra en el formato CoNLL-U (`Case=Nom|Number=Plur`), `_` para una palabra sin ellos |
| `pos` | `tuple[str / None]` | Categoría gramatical de cada palabra |
| `animacy`, `aspect`, ..., `voice` | `tuple[str / None]` | Valor de una estadística para cada palabra, `None` para una palabra sin el rasgo |

En esTS las estadísticas son `case`, ..., `verb_form` de la [tabla de abajo](#statistics); `animacy`, `aspect` y `voice` del núcleo no están entre ellas. esTS tiene además el atributo `lemmas` (`tuple[str]`): los lemas de las palabras, de esMorph para un texto y del pipeline para un `Doc`.

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

## Estadísticas { #statistics }

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

Un rasgo con varios valores conserva la forma de CoNLL-U: `usted` tiene `case` igual a `Acc,Nom`, y en un `Doc` de `es_core_news_sm` `qué`, `quién`, `cuál` tienen `pron_type` igual a `Int,Rel`. `print_stats` nombra los valores según `MORPHOLOGY_STATS_DESC` de `ests.constants`, y un valor así, con los nombres de sus partes unidos por una barra: «Interrogative / Relative», «Accusative / Nominative».

!!! warning "Aviso"
    Las estadísticas valen lo que vale la anotación. esMorph analiza un verbo con clíticos como el verbo (`dámelo` - el imperativo de `dar`), pero, como los modelos, lee como indicativo el imperativo de `tú` que tiene la forma del indicativo (`Abre la ventana`). En un `Doc`, `es_core_news_sm` analiza mal los verbos con pronombres enclíticos (`dámelo`, `cuéntamelo` salen como sustantivos con lemas inventados) y etiqueta los imperativos de `tú` como indicativo (`Abre la ventana` recibe `Mood=Ind`), de modo que `p_imperative` se queda corto y `p_indicative` absorbe las órdenes: en el diálogo del corpus de literatura encuentra alrededor de un imperativo de cada diez. `es_core_news_lg` apenas mejora (15 %); el modelo de transformadores `es_dep_news_trf`, que construye el `Doc`, encuentra el 87 %, y en el teatro `p_imperative` sube del 1,6 % al 7,5 %, a costa de cerca de 1 GB con PyTorch y cinco veces más tiempo en una CPU, y necesita antes unir los saltos de línea simples de un texto con líneas cortadas.

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

Los cuatro primeros marcadores comparten la base de las formas personales y suman uno salvo que el modelo deje alguna forma personal sin modo o le dé varios (`Mood=Ind,Sub`, que cuenta en la proporción de cada uno; `es_core_news_sm` no los da). Los tres siguientes comparten la base de todas las formas verbales de verbos y auxiliares: un participio que el modelo anota como adjetivo (`la casa pintada`) queda fuera de la base, los de los tiempos compuestos y la pasiva (`he leído`, `fue escrito`) quedan dentro.

La base de `p_ser` son solo los usos copulativos, leídos de la morfología: `ser` ante un participio y `estar` ante un gerundio, con adverbios y pronombres entre ellos, son los auxiliares de la pasiva y de la perífrasis progresiva (`fue escrito`, `es financiado`, `está cantando`) y quedan fuera, mientras que `es alta`, `está cansada` y `lo importante es que vengas` cuentan. La regla no necesita análisis sintáctico, así que un texto y un `Doc` sin analizador también tienen el marcador; un participio que el etiquetador lee como adjetivo (`fue muy bien recibido`) deja su `ser` como cópula.

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

<!-- core: stats/morph_stats.md:MorphStats-get_stats 748058e -->
`get_stats(*stats, filter_none=False, flat=False)` da el número de las palabras por valor de cada estadística elegida, todas por defecto, en el orden de las primeras apariciones; `None` cuenta las palabras sin el rasgo, y `filter_none` las deja fuera. Con `flat` las claves son `statistic_value` (la estadística y el valor), como `pos_NOUN`, sin las palabras que carecen del rasgo, como en `to_dataframe`. Una estadística desconocida lanza `UnknownStatError`, y un `filter_none` o un `flat` que no es un `bool`, `ParameterError`.

<!-- core: stats/morph_stats.md:MorphStats-explain_text 037565e -->
`explain_text(*stats, filter_none=False)` da cada palabra con los valores de las estadísticas elegidas; `filter_none` deja fuera los que le faltan a una palabra. Una estadística desconocida lanza `UnknownStatError`.

<!-- core: stats/morph_stats.md:MorphStats-print_stats a935578 -->
`print_stats(*stats, filter_none=False)` muestra una tabla para cada estadística elegida: las descripciones de sus valores desde el más frecuente, con el número de las palabras. Un valor de varios une las descripciones de sus partes con una barra. Una estadística desconocida lanza `UnknownStatError`.

El ejemplo del principio de la página muestra dos de las tablas. `to_dataframe` y `describe` son los de la [interfaz de las estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las estadísticas morfológicas no tienen escalas, así que `describe` da `None`.

=== "Código"

    ``` python
    ms.get_stats("pos", "mood", "tense", filter_none=True)
    ms.explain_text("pos", "mood", "tense", filter_none=True)
    ```

=== "Resultado"

    ```
    {'pos': {'SCONJ': 1, 'VERB': 3, 'NOUN': 2, 'DET': 1, 'PRON': 2, 'ADV': 1},
     'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1},
     'tense': {'Imp': 1, 'Past': 1}}
    (('Si', {'pos': 'SCONJ'}),
     ('tuviera', {'pos': 'VERB', 'mood': 'Sub', 'tense': 'Imp'}),
     ('tiempo', {'pos': 'NOUN'}),
     ('leería', {'pos': 'VERB', 'mood': 'Cnd'}),
     ('el', {'pos': 'DET'}),
     ('libro', {'pos': 'NOUN'}),
     ('que', {'pos': 'PRON'}),
     ('me', {'pos': 'PRON'}),
     ('recomendaste', {'pos': 'VERB', 'mood': 'Ind', 'tense': 'Past'}),
     ('ayer', {'pos': 'ADV'}))
    ```

<!-- core: stats/morph_stats.md:MorphStats-markers a7e33d7 -->
`get_markers()` da los marcadores de un idioma calculados a partir de los rasgos - proporciones de formas gramaticales, cada una de su propia base - por los nombres de `markers_desc`, y `print_markers()` los muestra con sus descripciones. Los calcula una biblioteca; por defecto no hay ninguno.

En esTS los marcadores son los [marcadores del español](#markers).

=== "Código"

    ``` python
    ms.print_markers()
    ```

=== "Resultado"

    ```
                   Marker               |  Value
    -----------------------------------------------
    Indicative among the finite forms   |   0.33
    Subjunctive among the finite forms  |   0.33
    Conditional among the finite forms  |   0.33
    Imperative among the finite forms   |   0.00
    Infinitive among the verb forms     |   0.00
    Gerund among the verb forms         |   0.00
    Participle among the verb forms     |   0.00
    ser among the copulas ser and estar |   nan
    Adverbs in -mente among the adverbs |   0.00
    ```

<!-- core: stats/morph_stats.md:MorphWord 7a841ee -->
`MorphWord` es una palabra de `analyze`: su texto `word`, su categoría gramatical `pos` (`None` cuando no se conoce) y sus rasgos `features` - los valores de los rasgos de Universal Dependencies por sus nombres (`{"Case": "Nom"}`), un valor de varios unidos por comas.

En esTS `MorphWord` se importa también de `ests.morph_stats`.
