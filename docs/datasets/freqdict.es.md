# Diccionario de frecuencias

!!! info ""
    **ests.datasets.FreqDict**

## Descripción

Un diccionario de frecuencias de lemas del español construido a partir de los libros en español de [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html) (versión 20200217): 83 785 lemas (109 178 filas de un lema y una categoría gramatical) de los libros de 1980-2019, 63 000 millones de palabras. Cada fila tiene la frecuencia por millón de palabras (ipm), el rango (el número de años, de 40, en que aparece el lema), la D de Juilland por años (0-100) y el número de libros con la forma más extendida del lema. Las categorías gramaticales son las de Google, con los nombres de Universal Dependencies: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP`, `CONJ` (coordinantes y subordinantes juntas).

El diccionario lo construye `scripts/build_freq_dict.py` a partir de los 1-gramas (3,2 GB): se cuentan solo las formas etiquetadas con una categoría gramatical y hechas de letras (se quitan los números, la puntuación y la etiqueta `X`); las formas pasan a sus claves por [`lemma_key`](#lemma_key): minúsculas y luego el lema por simplemma 2.0.0, el lematizador de la biblioteca. Google no tiene etiqueta para los nombres propios, así que una forma de sustantivo escrita con mayúscula en el 90 % de sus apariciones es `PROPN` y conserva su forma. La decisión se toma para la forma entera, con las apariciones en minúsculas: la forma `dios` va con mayúscula en el 92 % de sus apariciones, así que toda ella, también `dios` en minúsculas, es `PROPN` (405,9 ipm), mientras que la fila `NOUN` de `dios` (37,3 ipm) viene sobre todo del plural `dioses`, con mayúscula en el 6 % de sus apariciones. Se dejan fuera las filas por debajo de 0,1 ipm o presentes en menos de 5 años (las malas lecturas de un solo lote de libros escaneados). La dispersión se calcula sobre la frecuencia relativa de cada año, para que los años de distinto tamaño pesen igual; el número de libros es una cota inferior, ya que un libro con varias formas del lema se cuenta una vez.

Para buscar un lema se unen sus categorías gramaticales: las frecuencias se suman, el rango, la dispersión y el número de libros son los mayores. El lema se busca en minúsculas. El diccionario analizado se guarda en caché por la ruta del fichero y se lee una vez por proceso, así que un `FreqDict()` para cada texto es barato. El diccionario es la fuente de las frecuencias de [`LexicalStats`](../stats/lexical_stats.md), y sus 10 000 lemas más frecuentes son la lista integrada de las bandas de frecuencia. El tamaño del diccionario es `CORPUS_SIZE`, 63 090 618 290 palabras.

El archivo (0,9 MB) se guarda en el repositorio de la biblioteca, se descarga una vez en el directorio de datos, se verifica con su suma de comprobación SHA-256 y se extrae.

!!! quote "Licencia y atribución"
    El diccionario deriva de Google Books Ngram, que se publica con la [licencia Creative Commons Reconocimiento 3.0 No adaptada](https://creativecommons.org/licenses/by/3.0/), y se distribuye con la misma licencia; el archivo lleva un `README.txt` con la fuente y los cambios. Cite la fuente así: Michel J.-B. et al. Quantitative analysis of culture using millions of digitized books. Science 331 (6014), 2011.

## Clave de una palabra { #lemma_key }

`ests.datasets.freq_dict.lemma_key(word, proper=False)` - la clave por la que se busca una palabra en el diccionario y con la que se construye el diccionario: la palabra pasa a minúsculas y luego a su lema por `lemmatize`. simplemma distingue mayúsculas y minúsculas y deja tal cual una palabra desconocida con mayúscula, así que una palabra al principio de una oración perdería su lema (`Miró`, `Déjame`); en minúsculas lo encuentra (`mirar`, `dejar`). Un nombre propio conserva su forma en minúsculas (`proper=True`): `París` es `parís`, no el verbo `parir`.

Los lemas dependen de la versión de simplemma: el diccionario se construye con la 2.0.0 (la constante `SIMPLEMMA_VERSION`), y la biblioteca requiere simplemma 2.0 o posterior; con la 1.x cerca del 4 % de las palabras de un texto tendrían otros lemas (`fue` - `ir` en lugar de `ser`, `usted` sin cambios).

!!! example "Ejemplo"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    lemma_key("Miró"), lemma_key("computadoras"), lemma_key("fue")
    # ('mirar', 'computador', 'ser')
    lemma_key("París"), lemma_key("París", proper=True)
    # ('parir', 'parís')
    ```

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `data_dir` | str/Path | `DEFAULT_DATA_DIR.joinpath("dicts")` | Ruta al directorio del diccionario |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `entries` | dict[str, Entry] | Entradas por lema, con las categorías gramaticales unidas |
| `min_ipm` | float | Frecuencia mínima del diccionario (0,1) |
| `word_ipm` | dict[str, float] | Frecuencias por la clave a la que llega una forma sin categoría gramatical: las filas de los nombres propios van a `lemma_key` de sus formas (`roma` a `romo`); la referencia de [`keyness`](../corpus/keyness.md) |

Un `Entry` es una tupla con nombre con los campos `lemma`, `pos` (tupla de categorías gramaticales), `ipm`, `range`, `dispersion`, `docs`.

## Métodos

### download

Descarga el archivo con verificación de la suma de comprobación y extrae el fichero. Un archivo dañado o sustituido se borra y se descarga de nuevo en la misma llamada; si el archivo está pero falta el fichero del diccionario, se extrae otra vez, y el diccionario analizado se vuelve a leer.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `force` | bool | `False` | Descargar el diccionario aunque ya esté descargado |

!!! example "Ejemplo"

    ``` python
    from ests.datasets import FreqDict

    fd = FreqDict()
    fd.download()
    fd.info["license"]
    # 'CC BY 3.0'
    ```

### lookup

Devuelve la entrada de un lema en cualquier combinación de mayúsculas y minúsculas, `None` para un lema que no está en el diccionario. Una forma se busca por su clave: `computadoras` por `lemma_key("computadoras")`, que es `computador`, no por `computadora`.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `lemma` | str | `-` | Lema |

!!! example "Ejemplo"

    ``` python
    fd.lookup("Gato")
    # Entry(lemma='gato', pos=('NOUN', 'ADJ'), ipm=29.08, range=40, dispersion=95, docs=232841)
    fd.lookup("dios")
    # Entry(lemma='dios', pos=('PROPN', 'NOUN', 'ADJ'), ipm=444.42, range=40, dispersion=98, docs=566129)
    ```

### ipm

Devuelve la frecuencia de un lema por millón de palabras, 0 para un lema que no está en el diccionario.

!!! example "Ejemplo"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    fd.ipm("computadora"), fd.ipm(lemma_key("computadoras"))
    # (0.0, 20.07)
    "gato" in fd, len(fd)
    # (True, 83785)
    ```

### get_records

Devuelve los registros del diccionario - una fila por lema y categoría gramatical, por frecuencia - filtrados por la categoría gramatical y la frecuencia mínima. Una categoría desconocida y un límite negativo levantan `ParameterError`.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `pos` | str | `None` | Categoría gramatical: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP` o `CONJ` |
| `min_ipm` | float | `None` | Frecuencia mínima |
| `limit` | int | `None` | Número de registros |

!!! example "Ejemplo"

    ``` python
    for record in fd.get_records(pos="PROPN", limit=3):
        print(record)
    # {'lemma': 'méxico', 'pos': 'PROPN', 'ipm': 546.31, 'range': 40, 'dispersion': 94, 'docs': 535343}
    # {'lemma': 'san', 'pos': 'PROPN', 'ipm': 411.07, 'range': 40, 'dispersion': 94, 'docs': 645513}
    # {'lemma': 'dios', 'pos': 'PROPN', 'ipm': 405.93, 'range': 40, 'dispersion': 95, 'docs': 566129}
    ```

### get_texts

Devuelve los lemas del diccionario con los mismos parámetros que `get_records`.

!!! example "Ejemplo"

    ``` python
    list(fd.get_texts(pos="ADV", limit=5))
    # ['no', 'más', 'mucho', 'ya', 'también']
    ```

!!! warning "El registro de los libros"
    El diccionario describe la lengua escrita de los libros, buena parte de ellos académicos, y conserva lo que tienen los libros: las abreviaturas de las referencias son palabras frecuentes (`pp` 259,6 ipm, `cit` 110,5, `vol` 53,6), igual que las palabras inglesas de las bibliografías (`the` 320,3, `of` 262,4) y las grafías antiguas de las reediciones (`fué` 26,7). Los textos se reconocen a partir de escaneos y se etiquetan automáticamente, así que quedan malas lecturas y errores de etiquetado, sobre todo entre los lemas raros; el lematizador no ve el contexto, así que una forma compartida por dos lemas va a uno de ellos (`como` es siempre `como`, nunca `comer`), y una forma que no conoce se queda como está (`darle`, `verlo`).
