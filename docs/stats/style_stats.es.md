# Métricas de estilo

``` {.python .signature}
StyleStats(source, words_extractor=None, stopwords=None, top_n=10, cliches=None, nlp=None, nausea_stopwords=None)
```

<!-- core: stats/style_stats.md:StyleStats 145407f -->
Las métricas de estilo de un texto: las métricas SEO de Advego y Text.ru y los marcadores del estilo burocrático. Los servicios no publican sus fórmulas, así que se toman las definiciones comunes. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy).

Las métricas SEO se cuentan sobre las palabras del extractor de palabras, en minúsculas por defecto, o sobre los tokens de un `Doc`; un extractor pasado explícitamente se aplica al texto de un `Doc`. Los marcadores se cuentan sobre las formas en minúsculas (`forms`), sea cual sea el extractor.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un extractor de otro tipo, una lista que no es una lista de cadenas;
- `SourceError` - una fuente sin palabras;
- `ParameterError` - un `top_n` que no es un entero de al menos uno.

La clase extiende el `StyleStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/style_stats/) con los ganchos del español, descritos en las tarjetas de las métricas: las palabras vacías, las locuciones prepositivas, las expresiones parentéticas y los clichés contra los que advierten las guías de lenguaje claro en español, que se encuentran con sus contracciones y las formas de sus verbos, y los sustantivos derivados de un verbo entre los sustantivos del modelo de spaCy. Las palabras de una cadena las extrae el [`WordsExtractor`](../extractors/words.md) del español y no se lematizan, así que las formas de una palabra cuentan como palabras distintas, como en Advego; para calcular por lemas, pase un `WordsExtractor` con `use_lexemes=True` y `lowercase=True`. La tabla de `print_stats` toma las descripciones de `ests.constants.STYLE_STATS_DESC`.

Los sustantivos deverbales necesitan las categorías gramaticales y los lemas: un `Doc` da su propia anotación, también cuando un extractor toma su texto, y una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline pasado en `nlp` la primera vez que se lee `verbal_nouns` o [`markers()`](#methods); las demás métricas de una cadena no necesitan modelo. Una cadena más larga que el `max_length` del pipeline se analiza en partes de oraciones enteras. Además de las excepciones anteriores, un pipeline que no es un `Language` de spaCy lanza `SourceTypeError` y una cadena con un carácter sin forma UTF-8 lanza `SourceError` desde el tokenizador del español; leer `verbal_nouns` o `markers()` lanza `SourceError` para un `Doc` sin las categorías gramaticales o los lemas y para una cadena con una oración más larga que el `max_length` del pipeline.

Los ejemplos de esta página toman un aviso escrito en estilo administrativo:

=== "Código"

    ``` python
    from ests import StyleStats

    official = (
        "En el marco del procedimiento de referencia, y a efectos de dar cumplimiento a lo "
        "dispuesto en la normativa vigente, se procedió a la revisión de la documentación "
        "presentada. No obstante, en virtud de la resolución de la comisión, se llevará a cabo "
        "la notificación de la misma a la mayor brevedad, en tiempo y forma."
    )
    ss = StyleStats(official)
    ss.print_stats()
    ```

=== "Resultado"

    ```
                      Metric                  |  Value
    -----------------------------------------------------
    Classic nausea                            |   2.83
    Academic nausea (%)                       |  17.86
    Water content (%)                         |  57.14
    Spam score (%)                            |  37.50
    Naturalness by Zipf's law (%)             |  53.57
    Verbal nouns (% of nouns)                 |  47.06
    Compound prepositions (per 100 words)     |   5.36
    Parenthetical expressions (per 100 words) |   1.79
    Officialese clichés (per 100 words)       |   8.93
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras; para un `Doc` se aplica a su texto |
| `stopwords` | `list[str]` / `set[str]` | `None` | Palabras de agua; `is_stopword` si no se dan |
| `top_n` | `int` | `10` | Número de las palabras más frecuentes de la náusea académica y de la naturalidad según la ley de Zipf (`NAUSEA_TOP_N`) |
| `cliches` | `list[str]` / `set[str]` | `None` | Clichés; `OFFICIALESE_CLICHES` si no se dan |
| `nlp` | `Language` | `None` | Pipeline de spaCy que analiza una cadena para los sustantivos deverbales; el modelo `es_core_news_sm` de `ests.utils.get_nlp` si no se da |
| `nausea_stopwords` | `list[str]` / `set[str]` | `None` | Palabras vacías que se dejan fuera de las palabras más frecuentes de la náusea académica; `is_stopword` si no se dan |

Un conjunto de palabras se toma en orden alfabético. `NAUSEA_TOP_N` es una constante de `anyts.constants`.

<!-- core: stats/style_stats.md:StyleStats-check_params 2d25321 -->
``` {.python .signature}
check_params(top_n, *, messages=MESSAGES)
```

Comprueba el número de las palabras más frecuentes: uno que no es un entero de al menos uno lanza `ParameterError`.

## Atributos

<!-- core: stats/style_stats.md:StyleStats-attributes 42b352a -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `words` | `tuple[str]` | Palabras de las métricas SEO |
| `forms` | `tuple[str]` | Formas en minúsculas, de los marcadores |

Las métricas son propiedades que se calculan en cada acceso.

El pipeline del parámetro `nlp` se guarda en el atributo `nlp`, `None` si no se da.

## Métricas

<!-- core: stats/style_stats.md:StyleStats-metrics 16cf262 -->
`get_stats` da todas las métricas. Una métrica se calcula con la función de su tarjeta sobre `words` o `forms` con los ganchos de la clase.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`classic_nausea`](#classic_nausea) | Repetición de la palabra más frecuente | 0 o más, crece con el texto | Más insistencia en una palabra |
| [`academic_nausea`](#academic_nausea) | Proporción de las palabras significativas más frecuentes | 0-100 % | Un vocabulario más estrecho |
| [`water`](#water) | Proporción de las palabras sin contenido | 0-100 % | Menos contenido por palabra |
| [`spam`](#spam) | Proporción de las palabras repetidas | 0-100 % | Más repetición |
| [`zipf_naturalness`](#zipf_naturalness) | Concordancia de las frecuencias más altas con la ley de Zipf | 0-100 %, `nan` sin rangos que comparar | Un texto más cercano a uno natural |
| [`verbal_nouns`](#verbal_nouns) | Proporción de los sustantivos deverbales entre los sustantivos | 0-100 %, `nan` sin sustantivos | Un estilo más nominal |
| [`compound_prepositions`](#phrase_density) | Locuciones prepositivas por cada 100 palabras | 0-100 | Más estilo burocrático |
| [`parentheticals`](#parentheticals) | Expresiones parentéticas por cada 100 palabras | 0-100 | Más incisos |
| [`cliches`](#phrase_density) | Clichés por cada 100 palabras | 0-100 | Más clichés |

Las funciones de las tarjetas se importan de `ests.style_stats`. Las tarjetas dan las normas de [Advego](https://advego.com/text/seo/), [Text.ru](https://text.ru/seo), pr-cy y megaindex; las normas de los servicios están pensadas para textos de varios cientos de palabras, y en textos cortos la náusea y el spam dicen poco. esTS no da escalas a las métricas, así que `describe` da `None`; los marcadores del estilo burocrático no tienen normas.

<div class="metric-card" markdown>

### Náusea clásica { #classic_nausea }

`classic_nausea` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

<!-- core: stats/style_stats.md:calc_classic_nausea 3829e0a -->
``` {.python .signature}
calc_classic_nausea(text)
```

Cuánto se insiste en una palabra: la raíz cuadrada de las apariciones $f_1$ de la palabra más frecuente. El valor no se corrige por la longitud del texto, así que crece con el texto; sin palabras es 0.

$$
\sqrt{f_1}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

La norma de Advego es como máximo 7, en la práctica 1-5.

</div>

<div class="metric-card" markdown>

### Náusea académica { #academic_nausea }

`academic_nausea` · `nausea_words()` · [Advego](https://advego.com/text/seo/)
{ .metric-meta }

``` {.python .signature}
calc_academic_nausea(text, top_n=10, stopwords=None)
```

La proporción de las apariciones de las `top_n` palabras significativas más frecuentes entre todas las palabras, en porcentaje. La fórmula exacta de Advego no se ha publicado. Con las palabras vacías, las diez primeras de casi cualquier texto serían `de`, `la`, `que`, `el`, y su náusea quedaría por encima de la norma. La norma de Advego es 5-15%, para textos de varios cientos de palabras: en un texto corto las diez primeras son una parte grande de las palabras, sea cual sea el estilo.

$$
100 \cdot \frac{\sum_{w \in \textrm{top}_n} f_w}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `top_n` | `int` | `10` | Número de las palabras más frecuentes (`NAUSEA_TOP_N`) |
| `stopwords` | `list[str]` / `set[str]` | `None` | Palabras vacías que se dejan fuera de las palabras más frecuentes; `is_stopword` si no se dan |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas, unas palabras vacías que no son una lista o un conjunto de cadenas;
- `ParameterError` - un `top_n` que no es un entero de al menos uno.

``` {.python .signature}
find_nausea_words(text, top_n=10, stopwords=None)
```

Las `top_n` palabras más frecuentes sin las palabras vacías, las que cuenta la náusea académica, con sus apariciones: de la más frecuente a la menos y las de igual frecuencia en el orden del texto. Una palabra vacía es una palabra de `stopwords`, sin distinguir mayúsculas, o, sin la lista, una palabra de `is_stopword`. Los parámetros y las excepciones son los de `calc_academic_nausea`.

``` {.python .signature}
is_stopword(word)
```

Si una palabra es una palabra vacía, sin distinguir mayúsculas: las 265 formas de `ests.constants.STOPWORDS` - las clases cerradas de la gramática: artículos y demás determinantes (`este`, `cada`, `mucho`), pronombres (`él`, `cuyo`, `nadie`), preposiciones, conjunciones e interjecciones, con los adverbios que señalan, relacionan o preguntan (`aquí`, `así`, `dónde`) y los que niegan, afirman o focalizan (`no`, `solo`, `también`) - y las expresiones parentéticas de una palabra de `PARENTHETICALS` (`finalmente`, `naturalmente`). Se incluyen las formas de la ortografía antigua (`á`, `ó`, `tí`). `StyleStats` la usa para la náusea académica sin `nausea_stopwords` y para el contenido de agua sin `stopwords`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `word` | `str` | - | Palabra |

Excepciones:

- `SourceTypeError` - una palabra que no es una cadena.

=== "Código"

    ``` python
    from ests.style_stats import find_nausea_words, is_stopword

    is_stopword("Aquel"), is_stopword("sin"), is_stopword("trigo")
    find_nausea_words(["gato", "y", "gato", "y", "perro"], top_n=1)
    ```

=== "Resultado"

    ```
    (True, True, False)
    {'gato': 2}
    ```

</div>

<div class="metric-card" markdown>

### Contenido de agua { #water }

`water` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

``` {.python .signature}
calc_water(text, stopwords=None)
```

La proporción de las palabras sin contenido, en porcentaje: las palabras de `stopwords`, sin distinguir mayúsculas, o, sin la lista, las palabras vacías de `is_stopword`. Las normas de Text.ru: hasta 15% natural, 15-30% excesivo, más de 30% alto.

$$
100 \cdot \frac{\textrm{Número de palabras de agua}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `stopwords` | `list[str]` / `set[str]` | `None` | Palabras de agua; `is_stopword` si no se dan |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas, unas palabras vacías que no son una lista o un conjunto de cadenas.

!!! warning "El contenido de agua del español"
    Las normas de Text.ru están pensadas para el ruso, que no tiene artículos; un texto en español tiene más agua solo por su gramática. Compare el contenido de agua de los textos entre sí, no con la norma.

</div>

<div class="metric-card" markdown>

### Índice de spam { #spam }

`spam` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

<!-- core: stats/style_stats.md:calc_spam 66512af -->
``` {.python .signature}
calc_spam(text)
```

La proporción de las palabras repetidas en porcentaje: cada aparición de una palabra después de la primera.

$$
100 \cdot \left(1 - \frac{\textrm{Número de lexemas}}{\textrm{Número de palabras}}\right)
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

Para calcularlo por lemas, extraiga las palabras lematizadas. Las normas de Text.ru: hasta 30% natural, 30-60% optimizado para SEO, más de 60% saturado.

</div>

<div class="metric-card" markdown>

### Naturalidad según la ley de Zipf { #zipf_naturalness }

`zipf_naturalness` · pr-cy, megaindex
{ .metric-meta }

<!-- core: stats/style_stats.md:calc_zipf_naturalness 811103a -->
``` {.python .signature}
calc_zipf_naturalness(text, top_n=10, *, messages=MESSAGES)
```

La concordancia de las frecuencias de las palabras más frecuentes con la distribución ideal $f_r = f_1 / r$, donde $r$ es el rango. El primer rango es ideal por construcción, y por encima de $f_1$ la frecuencia ideal baja de uno, así que los rangos van de 2 a $R = \min(\textrm{top\_n}, V, f_1)$. Los valores negativos se recortan a 0. Sin rangos que comparar - todas las palabras hápax, un solo lexema o `top_n` menor que 2 - el valor es `nan`.

$$
100 \cdot \left(1 - \frac{1}{R - 1} \sum_{r=2}^{R} \frac{|r \cdot f_r - f_1|}{f_1}\right)
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `top_n` | `int` | `10` | Número de las palabras más frecuentes (`NAUSEA_TOP_N`) |
| `messages` | `dict[str, str]` | `MESSAGES` | Mensajes de los errores por clave |

Un `top_n` que no es un entero de al menos uno lanza `ParameterError`.

La distribución ideal es la de la [ley de Zipf](https://es.wikipedia.org/wiki/Ley_de_Zipf); la norma de pr-cy y megaindex es al menos 50%.

</div>

<div class="metric-card" markdown>

### Sustantivos deverbales { #verbal_nouns }

`verbal_nouns`
{ .metric-meta }

``` {.python .signature}
calc_verbal_nouns(nouns)
```

La proporción de los sustantivos derivados de un verbo entre los lemas de los sustantivos, en porcentaje; `nan` sin sustantivos. Un sustantivo es deverbal por su sufijo - `-ción`, `-sión`, `-miento`, `-anza`, `-encia`, `-ancia`, `-aje`, `-dura`, `-azgo` (`revisión`, `nombramiento`, `aprendizaje`) - o es uno de los sustantivos cuya derivación no deja sufijo (`uso`, `pago`, `envío`), como en los predicados escindidos de [`SyntaxStats`](syntax_stats.md). La regla atrapa también sustantivos de otro origen con las mismas terminaciones (`ciencia`, `distancia`). La función recibe los lemas de los tokens etiquetados `NOUN`, no las palabras: un sustantivo y una forma verbal pueden escribirse igual (`uso`, `viaje`).

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `nouns` | `list[str]` | - | Lemas de los sustantivos |

Excepciones:

- `SourceTypeError` - unos sustantivos que no son una lista de cadenas.

``` {.python .signature}
noun_lemmas(doc)
```

Los lemas de los tokens de un `Doc` etiquetados `NOUN`. `StyleStats` toma así los sustantivos de un `Doc`, y los de una cadena, de su análisis con el pipeline de `nlp` o de `get_nlp`, que se ejecuta sin el analizador sintáctico ni las entidades nombradas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `doc` | `Doc` | - | Objeto Doc |

Excepciones:

- `SourceTypeError` - una fuente que no es un `Doc`;
- `SourceError` - un `Doc` sin las categorías gramaticales o los lemas.

=== "Código"

    ``` python
    from ests.style_stats import calc_verbal_nouns, noun_lemmas
    from ests.utils import get_nlp

    calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
    lemmas = noun_lemmas(get_nlp()("Se procedió a la revisión de los proyectos"))
    lemmas, calc_verbal_nouns(lemmas)
    ```

=== "Resultado"

    ```
    50.0
    (['revisión', 'proyecto'], 50.0)
    ```

</div>

<div class="metric-card" markdown>

### Locuciones prepositivas y clichés { #phrase_density }

`compound_prepositions` · `cliches`
{ .metric-meta }

``` {.python .signature}
calc_phrase_density(text, phrases)
```

Las apariciones de las expresiones de una lista por cada 100 palabras, con las contracciones y las formas de los verbos de `expand_phrases`. En cada posición se toma la expresión más larga, y las expresiones encontradas no se solapan. `StyleStats` cuenta así, sobre las formas (`forms`), las locuciones prepositivas de `COMPOUND_PREPOSITIONS` (`en el marco de`, `a efectos de`, `en virtud de`) y los clichés de `OFFICIALESE_CLICHES` (`dar cumplimiento`, `proceder a`, `a la mayor brevedad`) o del parámetro `cliches`.

$$
100 \cdot \frac{\textrm{Número de expresiones encontradas}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `phrases` | `list[str]` / `set[str]` | - | Expresiones, palabras separadas por espacios |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas, unas expresiones que no son una lista o un conjunto de cadenas.

``` {.python .signature}
expand_phrases(text, phrases)
```

Las expresiones escritas en las formas de un texto, cada una con la expresión de la lista que escribe. Una expresión que termina en `a` o `de` también recibe la contracción con el artículo (`a efectos del`, `conforme al`), y una expresión cuya primera palabra es un infinitivo recibe las formas del texto con ese lema (`proceder a` - `procedió a`, `ser de aplicación` - `es de aplicación`). El lema es el de simplemma, y un lema pronominal vale por su verbo (`llévese` - `llevar`); las formas que simplemma no lematiza - algunos participios (`ha dado`, `ha hecho`) y el imperativo `dese` - las da `IRREGULAR_VERB_FORMS`. Las palabras que siguen al verbo descartan la lectura como sustantivo (`el hecho`, `el puesto`). Cuando dos expresiones dan las mismas palabras, una expresión escrita así gana a las formas de otra (`a efectos del` sigue siendo ella misma junto a `a efectos de`), y después la primera expresión de una lista, o de un conjunto en orden alfabético.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `phrases` | `list[str]` / `set[str]` | - | Expresiones, palabras separadas por espacios |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas, unas expresiones que no son una lista o un conjunto de cadenas.

=== "Código"

    ``` python
    from ests.constants import COMPOUND_PREPOSITIONS
    from ests.style_stats import calc_phrase_density, expand_phrases

    expand_phrases(["se", "procedió", "al", "cierre"], ["proceder a"])
    words = "se procedió a la revisión en el marco del proyecto".split()
    calc_phrase_density(words, COMPOUND_PREPOSITIONS)
    ```

=== "Resultado"

    ```
    {'proceder a': 'proceder a',
     'proceder al': 'proceder a',
     'procedió a': 'proceder a',
     'procedió al': 'proceder a'}
    10.0
    ```

Las locuciones prepositivas (42) y los clichés (74) son los que señalan las guías de lenguaje claro en español y los manuales de estilo de las administraciones:

| Fuente | Autor | Año |
| :----- | :---- | :-- |
| [Libro de estilo de la Justicia](https://www.rae.es/libro-estilo-justicia/el-lenguaje-jur%C3%ADdico/caracteres-externos/car%C3%A1cter-arcaizante) | RAE, CGPJ | 2017 |
| [Diccionario panhispánico de dudas](https://www.rae.es/dpd/hoy), 2.ª ed. | RAE, ASALE | en línea |
| [Guía panhispánica de lenguaje claro y accesible](https://www.rae.es/sites/default/files/2025-10/Gu%C3%ADa%20panhisp%C3%A1nica%20de%20lenguaje%20claro%20y%20accesible.pdf) | RAE, ASALE | 2024 |
| [Claridad y derecho a comprender](https://www.mjusticia.gob.es/es/AreaTematica/DocumentacionPublicaciones/InstListDownload/Claridad_y_derecho_a_comprender_Comision_para_la_modernizacion_del_lenguaje_juridico.PDF) | Comisión de Modernización del Lenguaje Jurídico | 2011 |
| [Cómo escribir con claridad](https://publications.europa.eu/resource/cellar/725b7eb0-d92e-11e5-8fea-01aa75ed71a1.0007.03/DOC_1) | Comisión Europea | 2015 |
| [Manual del Lenguaje Administrativo](https://www.madrid.es/UnidadesDescentralizadas/Calidad/Publicaciones/Documentaciontecnica/ficherosdocte/ManualLA.pdf) | Ayuntamiento de Madrid | hacia 2008 |
| [Comunicación Clara. Guía práctica](https://www.madrid.es/UnidadesDescentralizadas/Calidad/LenguajeClaro/ComunicacionClara/Documentos/GuiaPracticaCClara.pdf) | Ayuntamiento de Madrid | 2017 |
| [Guía de Comunicación Clara](https://www.comunidad.madrid/transparencia/sites/default/files/ckeditor/guia_tramites_claros-comunidad_madrid-noviembre_2021.pdf) | Comunidad de Madrid | 2021 |
| [Manual de Lenguaje y Estilo Administrativo](https://www.carm.es/web/integra.servlets.Blob?ARCHIVO=0-2934_Manual+de+lenguaje+y+estilo+administrativo.pdf&TABLA=ARCHIVOS&CAMPOCLAVE=IDARCHIVO&VALORCLAVE=33424&CAMPOIMAGEN=ARCHIVO&IDTIPO=60) | Región de Murcia | 2008 |
| [Manual de Lenguaje Claro](https://www.economia.gob.mx/files/empleo/ManualLenguaje.pdf) | Secretaría de la Función Pública, México | 2007 |
| [Guía de lenguaje claro para servidores públicos](https://colaboracion.dnp.gov.co/CDT/Programa%20Nacional%20del%20Servicio%20al%20Ciudadano/GUIA%20DEL%20LENGUAJE%20CLARO.pdf) | Departamento Nacional de Planeación, Colombia | 2015 |
| [Guía de lenguaje claro](https://colombiacompra.gov.co/wp-content/uploads/2025/05/cce-rec-gi-01_guia_lenguaje_claro_v2_31-12-2024-1.pdf) | Colombia Compra Eficiente | 2024 |
| [Manual de lenguaje claro](https://gcba.github.io/programadelenguajeclaro/Manual%20de%20lenguaje%20claro%202024%20(Final).pdf) | Gobierno de la Ciudad de Buenos Aires | 2024 |
| [Guía para el uso del Lenguaje Claro](https://biblioteca.legislatura.gob.ar/archivos/lenguajeClaro.pdf) | Legislatura de la Ciudad de Buenos Aires | 2024 |
| [Manual de Estilo del Lenguaje para uso de la Administración Pública Provincial](https://www.salta.gob.ar/public/descargas/archivos/ocspdfs/ocs_manual_de_estilo_del_lenguaje_para_la_administracion_publica_provincial.pdf) | Provincia de Salta | hacia 2007 |

Quedan fuera las formas que las guías recomiendan (`sobre la base de`) o aceptan (`de acuerdo a`) y las expresiones con usos neutros frecuentes (`en este sentido`), salvo `proceder a` y `llevar a cabo`. Algunas locuciones prepositivas también tienen usos neutros (`a través de`, `en caso de`, `con respecto a`), así que la densidad de un texto neutro no es cero: compare los textos entre sí.

</div>

<div class="metric-card" markdown>

### Expresiones parentéticas { #parentheticals }

`parentheticals`
{ .metric-meta }

``` {.python .signature}
calc_parentheticals(text)
```

Las expresiones parentéticas de `PARENTHETICALS` (`sin embargo`, `es decir`, `por ejemplo`, `finalmente`) por cada 100 palabras: las expresiones de la lista con sus contracciones (`expand_phrases`) y, fuera de ellas, las expresiones de una palabra de la lista. La puntuación no se mira, así que la lista contiene las expresiones que van entre comas o en el borde de una oración en la mayoría de sus apariciones en el [corpus de literatura](../datasets/spanishliterature.md), con las series de orden (`en primer lugar`, `en segundo lugar`). Los adverbios de duda (`tal vez`, `quizá`), `sobre todo`, `sin duda` y `además` no están en la lista.

$$
100 \cdot \frac{\textrm{Número de expresiones parentéticas}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas.

``` {.python .signature}
find_parentheticals(text)
```

Los límites de las expresiones parentéticas de `calc_parentheticals` como cortes de la lista de palabras, en orden. El parámetro y las excepciones son los de `calc_parentheticals`.

``` {.python .signature}
is_parenthetical(word)
```

Si una palabra es una de las expresiones de una palabra de `PARENTHETICALS` (`finalmente`, `naturalmente`, `verbigracia`), sin distinguir mayúsculas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `word` | `str` | - | Palabra |

Excepciones:

- `SourceTypeError` - una palabra que no es una cadena.

=== "Código"

    ``` python
    from ests.style_stats import calc_parentheticals, find_parentheticals, is_parenthetical

    words = ["sin", "embargo", "el", "gato", "finalmente", "duerme"]
    find_parentheticals(words), calc_parentheticals(words)
    is_parenthetical("Finalmente")
    ```

=== "Resultado"

    ```
    ([(0, 2), (4, 5)], 33.33333333333333)
    True
    ```

</div>

<div class="metric-card" markdown>

### Densidad de palabras clave { #keyword_density }

`keyword_density(*keywords)` · [Text.ru](https://text.ru/seo)
{ .metric-meta }

<!-- core: stats/style_stats.md:calc_keyword_density 3092629 -->
``` {.python .signature}
calc_keyword_density(text, keywords, normalize=str.lower)
```

Las apariciones de cada palabra clave por cada 100 palabras. Una palabra clave de varias palabras separadas por espacios es una secuencia de palabras cuyas apariciones pueden solaparse. Las palabras y las palabras clave se comparan por sus formas normalizadas, y las palabras clave de un conjunto van en orden alfabético.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `keywords` | `list[str]` | - | Palabras o frases clave |
| `normalize` | `Callable[[str], str]` | `str.lower` | Forma normalizada de una palabra y de una palabra clave |

Para comparar por lemas, extraiga las palabras lematizadas y pase lemas.

=== "Código"

    ``` python
    from ests import StyleStats

    text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
    StyleStats(text).keyword_density("tres tristes", "trigo")
    ```

=== "Resultado"

    ```
    {'tres tristes': 16.666666666666668, 'trigo': 8.333333333333334}
    ```

</div>

Las funciones de las tarjetas del núcleo también comprueban sus palabras: unas palabras o palabras clave que no son una lista de cadenas y un `normalize` que no es invocable lanzan `SourceTypeError`.

## Métodos { #methods }

<!-- core: stats/style_stats.md:StyleStats-keyword_density 5d9b0bc -->
`keyword_density(*keywords)` da la densidad de las palabras y frases clave en porcentaje (`calc_keyword_density` con el `normalize` de la clase), y `nausea_words()`, las palabras significativas más frecuentes de la náusea académica con sus apariciones (`find_nausea_words`).

<!-- core: stats/style_stats.md:StyleStats-markers 18537e6 -->
`markers()` devuelve los marcadores del estilo burocrático encontrados por métrica - `verbal_nouns`, `compound_prepositions`, `parentheticals`, `cliches` - tal como los escriben las formas, en el orden del texto.

Una expresión se encuentra con sus contracciones y las formas de su verbo ([`expand_phrases`](#phrase_density)). Los sustantivos deverbales necesitan las categorías gramaticales y los lemas, como su métrica, así que una cadena se analiza con el modelo y un `Doc` sin ellos lanza `SourceError`.

=== "Código"

    ``` python
    ss.markers()
    ```

=== "Resultado"

    ```
    {'verbal_nouns': ('procedimiento',
                      'referencia',
                      'cumplimiento',
                      'revisión',
                      'documentación',
                      'resolución',
                      'comisión',
                      'notificación'),
     'compound_prepositions': ('en el marco del', 'a efectos de', 'en virtud de'),
     'parentheticals': ('no obstante',),
     'cliches': ('dar cumplimiento',
                 'procedió a',
                 'llevará a cabo',
                 'a la mayor brevedad',
                 'en tiempo y forma')}
    ```

El aviso de 56 palabras tiene tres locuciones prepositivas, cinco clichés y una expresión parentética, y casi la mitad de sus sustantivos son deverbales. El anafórico `de la misma`, que las guías también desaconsejan, no se cuenta.

Los demás métodos - `get_stats`, `to_dataframe`, `print_stats` y `describe` - son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; las métricas de estilo de esTS no tienen escalas, así que `describe` da `None` para las métricas de `get_stats`. El mismo aviso en lenguaje claro:

=== "Código"

    ``` python
    plain = (
        "Hemos revisado los documentos que nos envió, como pide la ley. La comisión ha "
        "decidido su caso y le avisaremos lo antes posible."
    )
    StyleStats(plain).get_stats()
    ss.describe("water"), ss.describe("cliches")
    ```

=== "Resultado"

    ```
    {'classic_nausea': 1.4142135623730951,
     'academic_nausea': 43.47826086956522,
     'water': 43.47826086956522,
     'spam': 4.3478260869565215,
     'zipf_naturalness': 100.0,
     'verbal_nouns': 25.0,
     'compound_prepositions': 0.0,
     'parentheticals': 0.0,
     'cliches': 0.0}
    (None, None)
    ```

La versión clara no tiene locuciones prepositivas, expresiones parentéticas ni clichés, y una cuarta parte de sus sustantivos son deverbales. La náusea académica no dice nada del estilo aquí: ninguno de los avisos repite una palabra significativa, así que son diez palabras sobre la longitud del texto, 10/56 y 10/23.
