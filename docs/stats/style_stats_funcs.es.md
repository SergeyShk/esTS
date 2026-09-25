# Funciones de las métricas

## Náusea clásica { #calc_classic_nausea }

!!! info ""
    **ests.style_stats.calc_classic_nausea()**

La náusea clásica de [Advego](https://advego.com/text/seo/): la raíz cuadrada del número de apariciones de la palabra más frecuente. Mide la insistencia en una palabra sin tener en cuenta la longitud del texto, así que crece con el texto. La norma de Advego es como máximo 7, en la práctica 1-5.

Fórmula:

$$
\sqrt{\max_k n_k}
$$

donde $n_k$ es el número de apariciones de la palabra $k$.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Náusea académica { #calc_academic_nausea }

!!! info ""
    **ests.style_stats.calc_academic_nausea()**

La náusea académica de [Advego](https://advego.com/text/seo/): la proporción de las apariciones de las palabras más frecuentes del texto en porcentaje. La fórmula exacta de Advego no se ha publicado: la frecuencia sumada de las `top_n` palabras más frecuentes se divide entre el número de palabras. La norma de Advego es 5-15%.

Fórmula:

$$
100\times\frac{\sum_{k \in \textrm{top}_n} n_k}{N}
$$

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `top_n` | int | `10` | Número de las palabras más frecuentes |

## Contenido de agua { #calc_water }

!!! info ""
    **ests.style_stats.calc_water()**

El contenido de agua de [Text.ru](https://text.ru/seo): la proporción de las palabras sin contenido en porcentaje, es decir, las palabras vacías de [`is_stopword`](#is_stopword) o de la lista pasada, sin distinguir mayúsculas. Las normas de Text.ru - hasta 15% natural, 15-30% excesivo, más de 30% alto - están pensadas para el ruso, que no tiene artículos; un texto en español tiene más agua solo por su gramática, un 42-54% en los textos del corpus de literatura.

Fórmula:

$$
100\times\frac{\textrm{Número de palabras vacías}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `stopwords` | list[str] | `None` | Lista de palabras vacías; si no se da, se usa `is_stopword` |

## Palabra vacía { #is_stopword }

!!! info ""
    **ests.style_stats.is_stopword()**

Comprueba si una palabra es una palabra vacía, sin distinguir mayúsculas. Las palabras vacías son las 265 formas de `ests.constants.STOPWORDS` - las clases cerradas de la gramática: artículos y demás determinantes (`este`, `cada`, `mucho`), pronombres (`él`, `cuyo`, `nadie`), preposiciones, conjunciones e interjecciones, con los adverbios que señalan, relacionan o preguntan (`aquí`, `así`, `dónde`) y los que niegan, afirman o focalizan (`no`, `solo`, `también`) - y las expresiones parentéticas de una palabra de `PARENTHETICALS` (`finalmente`, `naturalmente`). Se conservan las formas de la ortografía antigua (`á`, `ó`, `tí`), tal como las escriben los textos de dominio público. No se usan las palabras vacías de spaCy para el español: esa lista está hecha para noticias y contiene palabras con contenido (`acuerdo`, `dijo`, `verdad`, `grande`).

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `word` | str | `-` | Palabra |

## Índice de spam { #calc_spam }

!!! info ""
    **ests.style_stats.calc_spam()**

El índice de spam de [Text.ru](https://text.ru/seo): la proporción de las palabras repetidas del texto en porcentaje; cada aparición de una palabra salvo la primera es una repetición, así que el índice es $100 \times (1 - TTR)$. Para calcularlo por lemas, extraiga las palabras lematizadas. Las normas de Text.ru: hasta 30% natural, 30-60% optimizado para SEO, más de 60% saturado.

Fórmula:

$$
100\times\frac{N - V}{N}
$$

donde $N$ es el número de palabras y $V$ el número de palabras distintas.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Naturalidad según la ley de Zipf { #calc_zipf_naturalness }

!!! info ""
    **ests.style_stats.calc_zipf_naturalness()**

La concordancia de las frecuencias de las palabras más frecuentes con la distribución ideal $f_r = f_1 / r$ de la [ley de Zipf](https://es.wikipedia.org/wiki/Ley_de_Zipf), donde $f_1$ es la frecuencia de la palabra más frecuente y $r$ el rango de una palabra (pr-cy, megaindex). Es 100 por uno menos la desviación relativa media de las frecuencias respecto de las ideales en los rangos de 2 a $R = \min(top\_n, V, f_1)$: el rango 1 coincide con el ideal por construcción, y por encima del rango $f_1$ la frecuencia ideal es menor que uno y la desviación de los hápax crece sin límite. Los valores negativos se recortan a 0; la norma de los servicios es al menos 50%. Es `nan` cuando no hay rangos que comparar: todas las palabras son hápax, el texto tiene un solo tipo de palabra o `top_n` es menor que 2.

Fórmula:

$$
\max\left(0,\ 100\times\left(1 - \frac{1}{R-1}\sum_{r=2}^{R}\frac{|f_r - f_1/r|}{f_1/r}\right)\right)
$$

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `top_n` | int | `10` | Número de las palabras más frecuentes |

## Densidad de palabras clave { #calc_keyword_density }

!!! info ""
    **ests.style_stats.calc_keyword_density()**

La frecuencia de cada palabra clave por cada 100 palabras del texto ([Text.ru](https://text.ru/seo)). Una palabra clave de varias palabras separadas por espacios se busca como una secuencia de palabras, y sus apariciones pueden solaparse. Las palabras se comparan sin distinguir mayúsculas; para comparar por lemas, extraiga las palabras lematizadas y pase lemas.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `keywords` | list[str] | `-` | Palabras o frases clave |

## Sustantivos deverbales { #calc_verbal_nouns }

!!! info ""
    **ests.style_stats.calc_verbal_nouns()**

La proporción de los sustantivos derivados de un verbo entre los lemas de los sustantivos de un texto en porcentaje, `nan` para un texto sin sustantivos. Un sustantivo es deverbal por su sufijo - `-ción`, `-sión`, `-miento`, `-anza`, `-encia`, `-ancia`, `-aje`, `-dura`, `-azgo` (`revisión`, `nombramiento`, `aprendizaje`) - o es uno de los sustantivos cuya derivación no deja sufijo (`uso`, `pago`, `envío`), como en los predicados escindidos de [`SyntaxStats`](syntax_stats.md). La regla atrapa también sustantivos de otro origen con las mismas terminaciones (`ciencia`, `distancia`), como cualquier regla de sufijos. En español un sustantivo solo se distingue de una forma verbal por la anotación (`uso`, `viaje`, `dura`), así que la función recibe los lemas de los tokens etiquetados `NOUN`, no las palabras.

!!! example "Ejemplo"

    ``` python
    from ests.style_stats import calc_verbal_nouns

    calc_verbal_nouns(["revisión", "proyecto", "nombramiento", "casa"])
    # 50.0
    ```

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `nouns` | list[str] | `-` | Lemas de los sustantivos |

## Densidad de expresiones { #calc_phrase_density }

!!! info ""
    **ests.style_stats.calc_phrase_density()**, **ests.style_stats.expand_phrases()**

El número de apariciones de las expresiones de una lista por cada 100 palabras: las locuciones prepositivas (`COMPOUND_PREPOSITIONS`), las expresiones parentéticas (`PARENTHETICALS`) y los clichés (`OFFICIALESE_CLICHES`). En cada posición se toma la expresión más larga, y las expresiones encontradas no se solapan. `expand_phrases` escribe las expresiones en las formas del texto: una expresión que termina en `a` o `de` también recibe la contracción con el artículo (`a efectos del`, `conforme al`), y una expresión cuya primera palabra es un infinitivo recibe las formas del texto con ese lema (`proceder a` - `procedió a`, `ser de aplicación` - `es de aplicación`). El lema es el de simplemma, y un lema pronominal vale por su verbo (`llévese`, `llevarse` - `llevarse` - `llevar`); las formas que simplemma deja como están - los participios irregulares del perfecto (`ha dado`, `ha hecho`, `ha puesto`) y el imperativo `dese` - las da `IRREGULAR_VERB_FORMS`. Las palabras que siguen al verbo descartan la lectura como sustantivo (`el hecho`, `el puesto`).

Las locuciones prepositivas (42) y los clichés (74) son los que señalan las guías españolas de lenguaje claro y los manuales de estilo de las administraciones:

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

Quedan fuera las formas que las propias guías recomiendan (`sobre la base de`, `con base en`) o aceptan (`de acuerdo a`, `de cara a`), y las expresiones con usos neutros frecuentes (`tomar una decisión`, `en este sentido`), salvo `proceder a` y `llevar a cabo`, que señalan las guías de tres administraciones o más. Algunas locuciones prepositivas también tienen usos neutros (`a través de`, `en caso de`, `con respecto a`), así que la densidad de un texto neutro no es cero: compare los textos entre sí.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `phrases` | list[str] | `-` | Expresiones, palabras separadas por espacios |

## Expresiones parentéticas { #calc_parentheticals }

!!! info ""
    **ests.style_stats.calc_parentheticals()**, **ests.style_stats.is_parenthetical()**

Las expresiones parentéticas de `PARENTHETICALS` (`sin embargo`, `es decir`, `por ejemplo`, `finalmente`) por cada 100 palabras; `is_parenthetical` comprueba una palabra con las expresiones de una palabra de la lista. La puntuación no se mira, así que la lista contiene las expresiones que van aparte en la mayoría de sus apariciones: las 55 que van entre comas o en el borde de una oración en al menos el 55% de sus apariciones en el [corpus de literatura](../datasets/spanishliterature.md), con las series de orden que abre la primera de ellas (`en primer lugar`, `en segundo lugar`). Quedan fuera los adverbios de duda, que el español rara vez aísla (`tal vez` 8%, `quizá` 10%), y también `sobre todo` (32%), `sin duda` (28%) y `además` (53%), que llevan un complemento o se unen a la oración sin comas.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
