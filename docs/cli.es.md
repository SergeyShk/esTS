# Línea de comandos

El comando `ests` calcula las estadísticas de textos sin código de Python: las imprime como tabla, JSON o CSV, del texto entero o de sus partes, escribe un informe HTML y descarga el diccionario de frecuencias. Se instala con la biblioteca; `python -m ests` es lo mismo.

``` bash
ests download
ests stats texto.txt
ests stats -f json capitulo1.txt capitulo2.txt
ests stats -s basic,readability -p sentences -f csv -o oraciones.csv texto.txt
cat texto.txt | ests stats -f json
ests report texto.txt -t "Mi texto" -o informe.html
```

## Comando { #Command }

<!-- core: cli.md:Command 84cbecf -->
``` {.python .signature}
Command()
```

La línea de comandos de las estadísticas de una biblioteca de un idioma. Su comando `stats` lee textos de ficheros, o de la entrada estándar sin ellos o para `-`, analiza cada texto una vez (`parse`) e imprime las estadísticas de las clases de `stats_classes`:

| Opción | Por defecto | Descripción |
| :----- | :---------- | :---------- |
| `files` | la entrada estándar | Ficheros de texto |
| `-s`, `--stats` | las clases de `default_stats` | Clases de estadísticas, por nombre y separadas por comas; con `-p`, por defecto las de `default_stats` que cuentan esas partes |
| `-p`, `--parts` | - | `sentences`, `lines` o `paragraphs`: una fila por parte ([`by_parts`](https://sergeyshk.github.io/anyTS/stats/stats/#by_parts)); una clase de `-s` que no cuenta esas partes es un error |
| `-f`, `--format` | `table` | `table` - la tabla de `print_stats` de cada clase, o de las partes; `json` - las estadísticas planas de cada clase por texto, `get_stats(flat=True)`, o los registros de las partes, con `nan` y los infinitos como `null`; `csv` - una fila por texto, o por parte de un texto, con una columna `<clase>.<estadística>` para cada estadística y 0 para un recuento de una distribución que falta en un texto ([`stats_dataframe`](https://sergeyshk.github.io/anyTS/stats/stats/#stats_dataframe)) |
| `-o`, `--output` | la salida estándar | Fichero de la salida, que solo un resultado reemplaza; la salida estándar para `-` |
| `-e`, `--encoding` | `utf-8-sig` | Codificación de los ficheros: por defecto UTF-8, sin la marca de orden de bytes; la salida va en UTF-8 |

La entrada estándar se lee como un fichero, igual sus saltos de línea y su marca de orden de bytes, y una tabla se imprime a medida que se cuenta cada texto.

Su comando `download`, en una biblioteca con `datasets`, descarga los conjuntos de datos que necesitan sus clases, los nombrados o todos, otra vez con `--force`, y nombra cada uno en la salida estándar.

Su comando `report` escribe el [informe HTML](https://sergeyshk.github.io/anyTS/report/) de un texto, de un fichero o de la entrada estándar, en `-o` o en la salida estándar, con las clases de `-s` y el título de `-t`, `--title`; sus estadísticas, también las de su tabla de oraciones, se cuentan como en `stats`, y una clase que no puede contar el texto queda fuera de él.

`run(argv=None)` ejecuta el comando con los argumentos, por defecto los de la línea de comandos, y devuelve el código de salida: 0; 1 cuando un fichero no puede leerse o escribirse, una clase no puede contar un texto o un conjunto de datos no puede descargarse, cuyo error va a la salida de errores mientras los demás se cuentan, y cuando el lector de la salida se detiene, como `head`, sin mensaje; 2 para argumentos erróneos, entre ellos una codificación desconocida, con la ayuda de `argparse`, y sin comando, con la ayuda del comando; 130 al interrumpirlo. `-V`, `--version` imprime las versiones de la biblioteca y del núcleo.

Lanza `ParameterError` cuando una subclase se define con textos que `check_messages` rechaza frente a `CLI_TEXTS`, o con un `default_stats` que nombra una clase que no está en `stats_classes`.

En esTS anySeg divide el texto y esMorph lo analiza en el contexto de sus oraciones una vez para todas las clases, sin spaCy, y las clases de `-s` son:

| Nombre | Clase |
| :----- | :---- |
| `basic` | [`BasicStats`](stats/basic_stats.md) |
| `readability` | [`ReadabilityStats`](stats/readability_stats.md) |
| `unadapted_readability` | [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md) |
| `diversity` | [`DiversityStats`](stats/diversity_stats.md) |
| `morph` | [`MorphStats`](stats/morph_stats.md) |
| `lexical` | [`LexicalStats`](stats/lexical_stats.md) |
| `style` | [`StyleStats`](stats/style_stats.md) |
| `phon` | [`PhonStats`](stats/phon_stats.md) |
| `cohesion` | [`CohesionStats`](stats/cohesion_stats.md) |
| `verse` | [`VerseStats`](stats/verse_stats.md), solo por su nombre en `-s` |

El comando no tiene estadísticas sintácticas, porque no analiza dependencias, y `cohesion` lee los análisis de esMorph sin análisis sintáctico: el [`si` que no abre ninguna condición](stats/cohesion_stats.md#is_connector_blocked) se reconoce tras un `¡` de apertura y tras un verbo que toma una interrogativa indirecta, con un clítico unido al verbo (`indíquelo si es necesario`) como el único complemento que ve. `ests download` descarga el [diccionario de frecuencias](datasets/freqdict.md) `freq_dict` para `lexical`; sin él la clase no se cuenta, y su error nombra este comando.

## Informe { #Report }

<!-- core: report.md:Report a4ff058 -->
``` {.python .signature}
Report(source, title=None, stats_classes=None, *, skip_errors=False)
```

El informe HTML de las estadísticas de un texto. El texto se analiza una vez (`parse`), cada clase lo cuenta a él y a sus oraciones con `compute`, y sus secciones siguen `sections`, cada una un método `section_<nombre>` que da un fragmento de HTML:

| Sección | Contenido |
| :------ | :-------- |
| `statistics` | Una tabla por clase de `stats_classes` bajo su título (`titles`): la descripción de cada estadística de `stats_desc`, como `print_stats`, su valor - un número real con dos decimales, uno menor que 0,1 con dos cifras significativas, una distribución como sus pares desde el más frecuente, con los valores descritos por `value_desc`, un valor indefinido como el texto `undefined` - y su lectura (`describe`); las clases que `skip_errors` dejó fuera se nombran arriba |
| `sentences` | El texto de cada oración con palabras, numerada como en el gráfico de sus longitudes, con las estadísticas de `sentence_columns` ([`by_parts`](https://sergeyshk.github.io/anyTS/stats/stats/#by_parts)); ninguna sin ellas. Un texto de más de `max_sentences` oraciones así tiene las de los valores más altos de la primera estadística, en su orden |
| `highlight` | El texto resaltado por `highlight_class` con sus capas por defecto, sus estilos en la cabecera de la página; nada sin ella |
| `plots` | Los gráficos de `plots` en SVG con sus pies: las longitudes de las oraciones (`sentence_lengths_plot`) por defecto, sin una marca en cada oración para un texto de más de 300; ninguno para un texto sin oraciones |

La página es la misma para el mismo texto, y ningún texto de la fuente o de las estadísticas se convierte en marcado.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` / `Document` | - | Fuente de datos |
| `title` | `str` | `None` | Título del informe; por defecto el texto `title` |
| `stats_classes` | `dict[str, type[Stats]]` | `None` | Clases de estadísticas por nombre; por defecto las de la clase |
| `skip_errors` | `bool` | `False` | Dejar fuera una clase que no puede contar la fuente, con su error en `errors`, en lugar de lanzarlo |

El objeto guarda `document`, `title`, las estadísticas de cada clase por nombre, `stats`, y los errores de las clases dejadas fuera, `errors`. `to_html()` devuelve la página, y `save(path)` la escribe en un fichero en UTF-8, la codificación que la página declara. Una fuente que una clase no puede contar lanza el error de la clase, salvo con `skip_errors`; un `skip_errors` que no es un `bool` y unos `stats_classes` que no son un diccionario de clases de estadísticas lanzan `ParameterError`.

En esTS `Report` está en `ests.report`: sus clases son `STATS_CLASSES` del mismo módulo, las clases del comando salvo `verse`; una cadena se analiza como en el comando; las columnas de las oraciones son los caracteres, las palabras, las sílabas, la facilidad de lectura de Flesch y el contenido de agua; el resaltado es [`HighlightedText`](visualizers/highlight.md) con sus capas por defecto. Los textos del informe están en inglés, como los de `print_stats`, y las lecturas conservan los nombres de las bandas de sus escalas (`bastante fácil`).

=== "Código"

    ``` python
    from ests.report import Report

    report = Report(
        "El gato duerme en la ventana. El perro ladra en el patio.",
        title="Dos oraciones",
        skip_errors=True,
    )
    report.save("informe.html")
    report.stats["basic"].n_words, len(report.document.sentences)
    ```

=== "Resultado"

    ```
    (12, 2)
    ```
