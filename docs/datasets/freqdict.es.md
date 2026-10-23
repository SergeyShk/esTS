# Diccionario de frecuencias

``` {.python .signature}
FreqDict(data_dir=DEFAULT_DATASET_DIR)
```

Un diccionario de frecuencias de lemas del español construido a partir de los libros en español de [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html) (versión 20200217): 83 785 lemas (109 178 filas de un lema y una categoría gramatical) de los libros de 1980-2019, 63 000 millones de palabras. Cada fila tiene la frecuencia por millón de palabras (ipm), el rango (el número de años, de 40, en que aparece el lema), la D de Juilland por años (0-100) y el número de libros con la forma más extendida del lema. Las categorías gramaticales son las de Google, con los nombres de Universal Dependencies: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP`, `CONJ` (coordinantes y subordinantes juntas).

El diccionario lo construye `scripts/build_freq_dict.py` a partir de los 1-gramas: se cuentan solo las formas etiquetadas con una categoría gramatical y hechas de letras (se quitan los números, la puntuación y la etiqueta `X`), y cada forma pasa a su clave por [`lemma_key`](#lemma_key). Google no tiene etiqueta para los nombres propios, así que una forma de sustantivo escrita con mayúscula en al menos el 90 % de sus apariciones es `PROPN` y conserva su forma. La decisión se toma para la forma entera: `dios`, con mayúscula en el 92 % de sus apariciones, es `PROPN` también en minúsculas, mientras que su fila `NOUN` viene sobre todo del plural `dioses`. Se dejan fuera las filas por debajo de 0,1 ipm o presentes en menos de 5 años. La dispersión se calcula sobre la frecuencia relativa de cada año; el número de libros es una cota inferior, ya que un libro con varias formas del lema se cuenta una vez.

Para buscar un lema se unen sus categorías gramaticales: las frecuencias se suman, el rango, la dispersión y el número de libros son los mayores. El diccionario se lee una vez por proceso, así que un `FreqDict()` para cada texto es barato. Es la fuente de las frecuencias de [`LexicalStats`](../stats/lexical_stats.md), y la lista integrada de las [bandas de frecuencia](../stats/lexical_stats.md#bands) tiene sus 10 000 lemas más frecuentes, sin los nombres propios y algunos lemas que no son palabras. El tamaño del diccionario es `CORPUS_SIZE`, 63 090 618 290 palabras.

El archivo (0,9 MB) se guarda en el repositorio de la biblioteca y se descarga una vez en el directorio de datos.

!!! quote "Licencia y atribución"
    El diccionario deriva de Google Books Ngram, que se publica con la [licencia Creative Commons Reconocimiento 3.0 No adaptada](https://creativecommons.org/licenses/by/3.0/), y se distribuye con la misma licencia; el archivo lleva un `README.txt` con la fuente y los cambios. Cite la fuente así: Michel J.-B. et al. Quantitative analysis of culture using millions of digitized books. Science 331 (6014), 2011.

Excepciones:

- `SourceTypeError` - un `data_dir` que no es ni una cadena ni un `Path`.

=== "Código"

    ``` python
    from ests.datasets import FreqDict

    fd = FreqDict()
    fd.download()
    fd.info["license"]
    ```

=== "Resultado"

    ```
    'CC BY 3.0'
    ```

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `data_dir` | `str` / `Path` | `DEFAULT_DATASET_DIR` | Ruta al directorio del diccionario; por defecto `dicts` en `DEFAULT_DATA_DIR`, el directorio de datos se describe en [Instalación](../installation.md#datasets) |

## Atributos

| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `name` | `str` | Nombre del conjunto de datos, `freq_dict` |
| `meta` | `dict[str, str]` | Información de referencia: la fuente, la descripción, el autor, la licencia y la cita |
| `info` | `dict[str, str]` | El nombre y la información de referencia en un diccionario |
| `data_dir` | `Path` | Ruta absoluta al directorio del diccionario |
| `filepath` | `str` | Ruta al fichero del diccionario, `None` antes de la descarga |
| `entries` | `dict[str, Entry]` | Entradas por lema, con las categorías gramaticales unidas |
| `min_ipm` | `float` | Frecuencia mínima del diccionario (0,1) |
| `word_ipm` | `dict[str, float]` | Frecuencias por la clave a la que llega una forma sin categoría gramatical: las filas de los nombres propios van a `lemma_key` de sus formas (`roma` a `romo`); la referencia de [`keyness`](../corpus/keyness.md) |

``` {.python .signature}
Entry(lemma, pos, ipm, range, dispersion, docs)
```

Una entrada del diccionario: una tupla con nombre.

| Campo | Tipo | Descripción |
| :---- | :--- | :---------- |
| `lemma` | `str` | Lema en minúsculas |
| `pos` | `tuple[str, ...]` | Categorías gramaticales del lema |
| `ipm` | `float` | Frecuencia por millón de palabras, sumada sobre las categorías gramaticales |
| `range` | `int` | Número de años, de 40 (1980-2019), en que aparece el lema |
| `dispersion` | `int` | D de Juilland por años, de 0 a 100 |
| `docs` | `int` | Número de libros con la forma más extendida del lema |

El diccionario se recorre por sus registros como `get_records()` sin filtros: `for record in fd` pasa por las 109 178 filas de un lema y una categoría gramatical, mientras que `len(fd)` cuenta los 83 785 lemas con sus categorías unidas, tal como los ven `lookup` e `in`.

## Métodos

`download(force=False)` descarga el archivo, verifica su suma de comprobación SHA-256 y extrae el fichero. Un archivo dañado se descarga de nuevo, un fichero que falta se extrae otra vez; después de la llamada el diccionario se vuelve a leer.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `force` | `bool` | `False` | Descargar el diccionario aunque ya esté descargado |

Un archivo que no se puede descargar o que no pasa la suma de comprobación dos veces lanza `DownloadError`, y un archivo que no se puede extraer, `DataFileError`.

`check_data()` comprueba que el fichero del diccionario está en su sitio y devuelve `True`; un diccionario sin descargar lanza `DatasetNotFoundError` con las órdenes para descargarlo. Los demás métodos y los atributos de las entradas y las frecuencias lo comprueban por sí mismos.

`lookup(lemma)` devuelve la entrada de un lema en cualquier combinación de mayúsculas y minúsculas, `None` para un lema que no está en el diccionario; `ipm(lemma)` devuelve la frecuencia de un lema por millón de palabras, 0 para un lema que no está en el diccionario. El argumento es una clave del diccionario, no una forma: una forma se busca por su clave, `computadoras` por `lemma_key("computadoras")` (`computador`), no por `computadora`; el lema de `usted` en simplemma es `tú`, así que `fd.lookup("usted")` es `None`. Lo mismo vale para `in`; [`LexicalStats`](../stats/lexical_stats.md) y [`keyness`](../corpus/keyness.md) pasan a las claves por sí mismos.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `lemma` | `str` | - | Lema |

Un lema que no es una cadena lanza `SourceTypeError`.

=== "Código"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    fd.lookup("Gato")
    fd.lookup("dios")
    fd.lookup("usted"), fd.ipm(lemma_key("usted"))
    fd.ipm("computadora"), fd.ipm(lemma_key("computadoras"))
    "gato" in fd, len(fd), sum(1 for _ in fd)
    ```

=== "Resultado"

    ```
    Entry(lemma='gato', pos=('NOUN', 'ADJ'), ipm=29.08, range=40, dispersion=95, docs=232841)
    Entry(lemma='dios', pos=('PROPN', 'NOUN', 'ADJ'), ipm=444.42, range=40, dispersion=98, docs=566129)
    (None, 1396.74)
    (0.0, 20.07)
    (True, 83785, 109178)
    ```

`get_records(pos=None, min_ipm=None, limit=None)` devuelve los registros del diccionario - una fila por lema y categoría gramatical, por frecuencia - filtrados por la categoría gramatical y la frecuencia mínima; `get_texts` con los mismos parámetros devuelve los lemas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `pos` | `str` | `None` | Categoría gramatical: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP` o `CONJ` |
| `min_ipm` | `float` | `None` | Frecuencia mínima |
| `limit` | `int` | `None` | Número de registros |

Una categoría desconocida, una frecuencia mínima que no es un número y un `limit` que no es un entero no negativo lanzan `ParameterError`.

=== "Código"

    ``` python
    for record in fd.get_records(pos="PROPN", limit=3):
        print(record)
    list(fd.get_texts(pos="ADV", limit=5))
    ```

=== "Resultado"

    ```
    {'lemma': 'méxico', 'pos': 'PROPN', 'ipm': 546.31, 'range': 40, 'dispersion': 94, 'docs': 535343}
    {'lemma': 'san', 'pos': 'PROPN', 'ipm': 411.07, 'range': 40, 'dispersion': 94, 'docs': 645513}
    {'lemma': 'dios', 'pos': 'PROPN', 'ipm': 405.93, 'range': 40, 'dispersion': 95, 'docs': 566129}
    ['no', 'más', 'mucho', 'ya', 'también']
    ```

!!! warning "El registro de los libros"
    El diccionario describe la lengua escrita de los libros, buena parte de ellos académicos, y conserva lo que tienen los libros: las abreviaturas de las referencias son palabras frecuentes (`pp`, `cit`, `vol`), igual que las palabras inglesas de las bibliografías (`the`, `of`) y las grafías antiguas de las reediciones (`fué`). Los textos se reconocen a partir de escaneos y se etiquetan automáticamente, así que quedan malas lecturas y errores de etiquetado, sobre todo entre los lemas raros; el lematizador no ve el contexto, así que una forma compartida por dos lemas va a uno de ellos (`como` es siempre `como`, nunca `comer`), y una forma que no conoce se queda como está (`darle`, `verlo`).

## Clave de una palabra { #lemma_key }

``` {.python .signature}
lemma_key(word, proper=False)
```

La clave por la que se busca una palabra en el diccionario y con la que se construye el diccionario (`ests.datasets.freq_dict.lemma_key`): la palabra pasa a minúsculas, para que una palabra al principio de una oración encuentre su lema (`Miró` - `mirar`), y luego a su lema por `lemmatize`. Un nombre propio conserva su forma en minúsculas (`proper=True`): `París` es `parís`, no el verbo `parir`.

Los lemas dependen de la versión de simplemma: el diccionario se construye con la 2.0.0 (la constante `SIMPLEMMA_VERSION`), y un `FreqDict` avisa una vez por proceso cuando está instalada otra versión, ya que entonces algunas palabras pueden no encontrarse en el diccionario.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `word` | `str` | - | Forma de la palabra en cualquier combinación de mayúsculas y minúsculas |
| `proper` | `bool` | `False` | La palabra es un nombre propio |

=== "Código"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    lemma_key("Miró"), lemma_key("computadoras"), lemma_key("fue")
    lemma_key("París"), lemma_key("París", proper=True)
    ```

=== "Resultado"

    ```
    ('mirar', 'computador', 'ser')
    ('parir', 'parís')
    ```
