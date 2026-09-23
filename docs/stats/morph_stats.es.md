# Estadísticas morfológicas

!!! info ""
    **ests.morph_stats.MorphStats**

## Descripción

Módulo para calcular las estadísticas morfológicas de un texto. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

Las categorías gramaticales y los rasgos morfológicos se dan en los términos de [Universal Dependencies](https://universaldependencies.org/u/feat/), tal como los anotan los modelos españoles de spaCy. Un texto se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline indicado en `nlp`, sin el reconocedor de entidades, que aquí no se lee; un `Doc` se toma tal cual y debe llevar las categorías gramaticales, que vienen de un `morphologizer` (o de un `tagger` con un `attribute_ruler`), y los lemas, que vienen de un `lemmatizer`: un `Doc` de `spacy.blank("es")` o de un pipeline con el `lemmatizer` excluido no es una fuente válida y levanta `SourceError`. Las palabras se toman de los tokens y los signos de puntuación y los símbolos se descartan.

Un texto más largo que el `max_length` del pipeline - un millón de caracteres por defecto, una novela larga - levanta `SourceError` en lugar de llegar a spaCy: divídalo en partes o suba `max_length` en un pipeline propio y páselo en `nlp`.

!!! note "Nota"
    Las estadísticas se calculan al inicializar el objeto `MorphStats`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (cadena u objeto Doc) |
| `nlp` | Language | `None` | Pipeline de spaCy que analiza una cadena; sin él se carga el modelo `es_core_news_sm` |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[str] | Tupla de las palabras extraídas |
| `lemmas` | tuple[str] | Tupla de los lemas de las palabras |
| `tags` | tuple[str] | Tupla de las cadenas de rasgos en formato CoNLL-U |
| `pos` | tuple[str] | Tupla de las categorías gramaticales |
| `case` | tuple[str] | Tupla de los valores del caso |
| `definite` | tuple[str] | Tupla de los valores de la definitud |
| `degree` | tuple[str] | Tupla de los valores del grado |
| `gender` | tuple[str] | Tupla de los valores del género |
| `mood` | tuple[str] | Tupla de los valores del modo |
| `num_type` | tuple[str] | Tupla de los valores del tipo de numeral |
| `number` | tuple[str] | Tupla de los valores del número |
| `person` | tuple[str] | Tupla de los valores de la persona |
| `polarity` | tuple[str] | Tupla de los valores de la polaridad |
| `polite` | tuple[str] | Tupla de los valores de la cortesía |
| `poss` | tuple[str] | Tupla de los valores del posesivo |
| `pron_type` | tuple[str] | Tupla de los valores del tipo de pronombre |
| `reflex` | tuple[str] | Tupla de los valores del reflexivo |
| `tense` | tuple[str] | Tupla de los valores del tiempo verbal |
| `verb_form` | tuple[str] | Tupla de los valores de la forma verbal |

Cada atributo tiene la longitud de `words`, y una palabra a la que el modelo no da ningún valor del rasgo lleva `None`. Los nombres de los atributos son los nombres de las estadísticas que aceptan los métodos; `tags` y `lemmas` no son estadísticas.

!!! note "Nota"
    Un rasgo con varios valores conserva la forma de CoNLL-U: el interrogativo y relativo `qué`, `quién`, `cuál`, que los modelos no desambiguan, tiene `pron_type` igual a `Int,Rel`, y `usted` tiene `case` igual a `Acc,Nom`. `print_stats` describe un valor así con las descripciones de sus partes: «Interrogative or relative», «Accusative or nominative».

## Rasgos { #features }

Las estadísticas cuentan los quince rasgos de la tabla siguiente; el valor `Unknown` de las tablas impresas y `None` de los atributos significan que el modelo no dio a la palabra ningún valor del rasgo.

Son un subconjunto: los modelos españoles anotan 23 rasgos, y los que quedan fuera son marginales (`AdvType`, `Foreign`, `NumForm`, `Number[psor]`, `PrepCase`, `Typo`) o viven en la puntuación (`PunctSide`, `PunctType`), que este módulo no trata como palabras. Todo lo que el modelo anota queda en `tags`, se cuente o no.

| Estadística | Rasgo | Valores |
| :---------: | :---: | :-----: |
| `pos` | Categoría gramatical | NOUN, PROPN, ADJ, ADV, VERB, AUX, PRON, DET, NUM, ADP, CCONJ, SCONJ, PART, INTJ, SYM, X |
| `case` | Caso | Nom, Acc, Dat, Com |
| `definite` | Definitud | Def, Ind |
| `degree` | Grado | Cmp, Sup, Abs |
| `gender` | Género | Masc, Fem |
| `mood` | Modo | Ind, Sub, Imp, Cnd |
| `num_type` | Tipo de numeral | Card, Ord, Frac |
| `number` | Número | Sing, Plur |
| `person` | Persona | 1, 2, 3 |
| `polarity` | Polaridad | Neg |
| `polite` | Cortesía | Form |
| `poss` | Posesivo | Yes |
| `pron_type` | Tipo de pronombre | Art, Prs, Dem, Ind, Int, Rel, Neg, Tot, Exc |
| `reflex` | Reflexivo | Yes |
| `tense` | Tiempo verbal | Pres, Past, Imp, Fut |
| `verb_form` | Forma verbal | Fin, Inf, Part, Ger |

!!! warning "Advertencia"
    Las estadísticas valen lo que vale la anotación del modelo. `es_core_news_sm` analiza mal los verbos con pronombres enclíticos: `dámelo`, `decírselo`, `vámonos`, `cuéntamelo` salen como sustantivos o nombres propios y reciben lemas inventados (`dámelir`, `siéntatir`). El imperativo es el que más lo sufre: los modelos llevan el valor `Mood=Imp` en su juego de etiquetas - 21 de las 433 del morfologizador -, pero en la práctica etiquetan los imperativos de `tú` como indicativo, y `Habla más despacio`, `Abre la ventana` y `Ven aquí` reciben todos `Mood=Ind`. Sobre 24 oraciones imperativas de `tú`, `vosotros` y `usted`, con enclíticos y sin ellos, `es_core_news_sm` encontró el imperativo dos veces, `es_core_news_md` tres y `es_core_news_lg` cuatro, de modo que `p_imperative` se queda corto y `p_indicative` absorbe las órdenes.

    Indicar un modelo mayor en `nlp` no lo cambia. Medidos frente a `es_core_news_sm`, tanto `es_core_news_md` (54 MB) como `es_core_news_lg` (631 MB) coinciden con él en todas las categorías gramaticales de la prosa moderna y corren a la misma velocidad: los vectores que añaden pesan en memoria, no en el etiquetador. Lo que aportan es el vocabulario raro y antiguo: en el comienzo del *Quijote* leen `rocín`, `salpicón`, `lentejas` y `carnero` como sustantivos, donde el modelo pequeño ve verbos y adjetivos. Con los enclíticos cambian una mejora por un empeoramiento: `Dime` pasa a ser verbo mientras `Cantándole` deja de ser gerundio.

## Métodos

### get_stats

Devuelve un diccionario con las estadísticas morfológicas calculadas: para cada estadística, cuántas palabras llevan cada uno de sus valores.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `args` | tuple[str] | `-` | Nombres de las estadísticas seleccionadas, por defecto todas |
| `filter_none` | bool | `False` | Filtrar los valores vacíos |

!!! example "Ejemplo"

    _Código_:

    ``` python
    # Importar la biblioteca
    from ests import MorphStats

    # Preparar los datos
    text = "Si tuviera tiempo, leería el libro que me recomendaste ayer"

    # Calcular las estadísticas
    ms = MorphStats(text)
    ms.get_stats("pos", "mood", "tense", filter_none=True)
    ```

    _Resultado_:

    ``` bash
    {'pos': {'SCONJ': 1, 'VERB': 3, 'NOUN': 2, 'DET': 1, 'PRON': 2, 'ADV': 1},
    'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1},
    'tense': {'Imp': 1, 'Pres': 1}}
    ```

### get_markers

Devuelve un diccionario con los marcadores del español calculados a partir de los rasgos. Cada marcador es una proporción sobre su propia base, de modo que los marcadores de textos de distinta longitud pueden compararse directamente:

| Marcador | Descripción |
| :------: | :---------: |
| `p_indicative` | Indicativo entre las formas personales |
| `p_subjunctive` | Subjuntivo entre las formas personales |
| `p_conditional` | Condicional entre las formas personales |
| `p_imperative` | Imperativo entre las formas personales |
| `p_infinitive` | Infinitivo entre las formas verbales |
| `p_gerund` | Gerundio entre las formas verbales |
| `p_participle` | Participio entre las formas verbales |
| `p_ser` | `ser` entre las cópulas `ser` y `estar` |
| `p_mente_adverbs` | Adverbios en `-mente` entre los adverbios |

Los cuatro primeros marcadores comparten la base de las formas personales y suman uno siempre que el modelo no deje ninguna forma personal sin modo: cinco de sus 433 etiquetas llevan `VerbForm=Fin` y ningún `Mood`, y cada forma así falta en las cuatro proporciones. Los tres siguientes comparten la base de todas las formas verbales, contadas sobre verbos y auxiliares, de modo que los participios que el modelo anota como adjetivos (`la casa pintada`) quedan fuera de la base, mientras que los de los tiempos compuestos y la pasiva (`he leído`, `fue escrito`) quedan dentro.

La base de `p_ser` son solo los usos copulativos, leídos de la dependencia del token: `fue escrito` y `está cantando` son los auxiliares de la pasiva y de la perífrasis progresiva, no una elección entre las dos cópulas, mientras que `es alta`, `está cansada` y `lo importante es que vengas` sí lo son. El análisis sintáctico es lo que los distingue, así que para un `Doc` que no lo lleva el marcador es `nan`.

Un marcador cuya base está vacía - un texto sin verbos, sin cópula, sin adverbios - es `nan`.

!!! note "Nota"
    El subjuntivo, la elección entre `ser` y `estar` y los adverbios en `-mente` son los rasgos del español que las fórmulas de legibilidad no ven: el subjuntivo marca la hipótesis y la subordinación, `estar` un estado frente a la propiedad de `ser`, y los adverbios en `-mente` un registro formal y escrito.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Calcular los marcadores
    ms.get_markers()
    ```

    _Resultado_:

    ``` bash
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

### explain_text

Devuelve una tupla de las palabras del texto con los valores de las estadísticas seleccionadas.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `args` | tuple[str] | `-` | Nombres de las estadísticas seleccionadas, por defecto todas |
| `filter_none` | bool | `False` | Filtrar los valores vacíos |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Analizar el texto
    ms.explain_text("pos", "mood", "tense", filter_none=True)
    ```

    _Resultado_:

    ``` bash
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

### print_stats

Muestra una tabla de los valores de cada estadística seleccionada, del más frecuente al menos frecuente.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `args` | tuple[str] | `-` | Nombres de las estadísticas seleccionadas, por defecto todas |
| `filter_none` | bool | `False` | Filtrar los valores vacíos |

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de las estadísticas calculadas
    ms.print_stats("pos", "mood")
    ```

    _Resultado_:

    ``` bash
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

### print_markers

Muestra una tabla con los marcadores del español calculados.

!!! example "Ejemplo"

    _Código_:

    ``` python
    ...

    # Mostrar la tabla de los marcadores calculados
    ms.print_markers()
    ```

    _Resultado_:

    ``` bash
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
