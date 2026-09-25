# Sonetos en español

!!! info ""
    **ests.datasets.SpanishSonnets**

## Descripción

Una colección de sonetos en español del [Diachronic Spanish Sonnet Corpus](https://github.com/pruizf/disco) (DISCO 5.0): 4259 sonetos de 1167 autores de España, Hispanoamérica y Filipinas, del siglo XV a principios del XX, 60 209 versos. Cada verso lleva su patrón métrico y la etiqueta de su rima, así que la colección sirve para estudiar la métrica y la rima y para contrastar una escansión con la anotación del corpus.

| Periodo | Clave | Sonetos | Autores | Los autores más representados |
| :------ | :---- | :-----: | :-----: | :---------------------------- |
| Siglos XV-XVII | `15th-17th` | 1088 | 475 | Juan de Arguijo (72), Marqués de Santillana (42), Juan de Jauregui (23), Luis Martín de la Plaza (22) |
| Siglo XVIII | `18th` | 321 | 42 | Juan Nicasio Gallego (50), Juan Bautista Arriaza (28), Vicente García de la Huerta (25), Juan Meléndez Valdés (25) |
| Siglo XIX | `19th` | 2845 | 650 | Rubén Darío (140), José Santos Chocano (130), Clemente Althaus (52), Julio Flores Roa (52) |
| Siglo XX | `20th` | 5 | 1 | Cecilio Apóstol (5) |

295 sonetos son de mujeres. Por el país de nacimiento: España (2388), Cuba (719), Perú (204), México (191), Nicaragua (141), Colombia (100), Argentina (93), Uruguay (76), Venezuela (68) y 13 países más; el país de 38 sonetos es desconocido. La parte del siglo XIX de DISCO es una antología de España e Hispanoamérica, la del siglo XX reúne a los poetas filipinos en español.

Solo se guardan los sonetos de dominio público, 4259 de 4523: los de los autores que murieron antes de 1946, los de los autores de los siglos XV-XVIII cuya muerte se desconoce y los de los autores de la antología del siglo XIX nacidos antes de 1866 o sin fechas. Los sonetos de los autores que murieron en 1946 o después se quedan fuera, entre ellos los de la mayoría de los poetas filipinos. Un autor de la antología sin fechas en la fuente también se queda fuera cuando las fechas de [VIAF](https://viaf.org) que DISCO asoció con confianza alta dan una muerte en 1946 o después o un nacimiento en 1866 o después sin muerte (Luis Rodríguez Embil, 1879-1954, marcado solo como del siglo XIX): VIAF solo deja fuera a un autor y nunca sustituye las fechas de la fuente, ya que algunas de sus asociaciones son otras personas. Los años de vida se leen de la línea biográfica de la fuente donde DISCO tomó de ella un año posterior por el de la muerte (Echegaray murió en 1916, no en 1904, el año de su premio Nobel) o no vio un nacimiento o una muerte dados solos (`1585 - Siglo XVII`, `18¿? - 1892`); los años que siguen a un siglo en esa línea son de otras personas o sucesos y no se toman. El país de nacimiento también se lee de esa línea donde la nombra (Gertrudis Gómez de Avellaneda nació en Puerto Príncipe, Cuba, no en Haití). Los poetas filipinos, escritos en DISCO con el apellido primero, llevan el nombre primero como los demás; los interlocutores de los diálogos (`[Car]`, `[POETA]`) y las llamadas de las notas se quitan de los versos, como están fuera de sus patrones métricos.

El archivo (1 MB) se guarda en el repositorio de la biblioteca, se descarga una vez en el directorio de datos, se verifica con su suma de comprobación SHA-256 y se extrae; los sonetos se leen de uno en uno de un fichero JSON Lines. Lo construye `scripts/build_spanish_sonnets.py` a partir de DISCO en un commit fijo.

!!! quote "Licencia y atribución"
    DISCO se publica con la [licencia Creative Commons Reconocimiento 4.0 Internacional](https://creativecommons.org/licenses/by/4.0/), y este conjunto de datos también; el archivo lleva un `README.txt` con la fuente y los cambios. Cite la fuente así: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., Calvo Tello J. Diachronic Spanish Sonnet Corpus (DISCO), version 5.0. Madrid: UNED, 2017-2023; y el artículo: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., González-Blanco E. The Diachronic Spanish Sonnet Corpus: TEI and linked open data encoding, data distribution, and metrical findings. Digital Scholarship in the Humanities 36 (Supplement 1), 2021, i68-i80, [doi:10.1093/llc/fqaa035](https://doi.org/10.1093/llc/fqaa035).

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `data_dir` | str/Path | `DEFAULT_DATA_DIR.joinpath("texts")` | Ruta al directorio del conjunto de datos; el directorio de datos se describe en [Instalación](../installation.md#datasets) |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `periods` | tuple[str] | Tupla de periodos: `15th-17th`, `18th`, `19th`, `20th` |
| `authors` | Counter | Número de sonetos por autor, leído del fichero |
| `name` | str | Nombre del conjunto de datos, `spanish_sonnets` |
| `meta` | dict[str, str] | Información de referencia: la fuente, la descripción, los autores, la licencia y la cita |
| `info` | dict[str, str] | El nombre y la información de referencia en un diccionario |
| `data_dir` | Path | Ruta absoluta al directorio del conjunto de datos |
| `filepath` | str | Ruta al fichero del conjunto de datos, `None` antes de la descarga |

El conjunto de datos se recorre por sus registros como `get_records()` sin filtros: `for record in ss` pasa por los sonetos de uno en uno.

## Métodos

### check_data

Comprueba que el fichero del conjunto de datos está en su sitio y devuelve `True`; un conjunto sin descargar levanta `DatasetNotFoundError`. Los demás métodos lo comprueban por sí mismos.

### download

Descarga el archivo con verificación de la suma de comprobación y extrae el fichero. Un archivo dañado o sustituido se borra y se descarga de nuevo en la misma llamada; si el archivo está pero falta el fichero, se extrae otra vez. Una llamada repetida no descarga nada.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `force` | bool | `False` | Descargar el conjunto de datos aunque ya esté descargado |

!!! example "Ejemplo"

    ``` python
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()
    ss.download()
    ss.info["license"], ss.authors.most_common(2)
    # ('CC BY 4.0', [('Rubén Darío', 140), ('José Santos Chocano', 130)])
    ```

### get_texts

Extrae los textos (sin encabezados) del conjunto de datos: los versos de un soneto, las estrofas separadas por una línea en blanco.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `period` | str | `None` | Periodo: `15th-17th`, `18th`, `19th` o `20th` |
| `author` | str | `None` | Autor: una subcadena del nombre, sin distinguir mayúsculas ni tildes |
| `country` | str | `None` | País de nacimiento: una subcadena del nombre en español, sin distinguir mayúsculas ni tildes |
| `gender` | str | `None` | Género del autor: `F` o `M` |
| `min_len` | int | `None` | Longitud mínima del texto (en caracteres) |
| `max_len` | int | `None` | Longitud máxima del texto (en caracteres) |
| `limit` | int | `None` | Número de textos |

Los filtros se combinan; `author="dario"` encuentra a Rubén Darío, `country="mexico"` encuentra `México`. Un periodo o un género desconocidos, una longitud menor que uno, una longitud mínima mayor que la máxima y un límite negativo levantan `ParameterError`.

!!! example "Ejemplo"

    ``` python
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()
    for text in ss.get_texts(author="avellaneda", gender="F", limit=1):
        print(text.split("\n\n")[0])
    # No encuentro paz, ni me permiten guerra;
    # de fuego devorado, sufro el frío;
    # abrazo un mundo, y quédome vacío;
    # me lanzo al cielo, y préndeme la tierra.
    ```

### get_records

Extrae los registros (con encabezados) del conjunto de datos. Campos del registro: `id` - el identificador del soneto en DISCO, `period` - periodo, `author` - autor, `title` - título, `country` - el país de nacimiento del autor en español (vacío si se desconoce), `gender` - `F` o `M`, `birth` y `death` - los años de vida (`None` si se desconocen), `text` - texto, `meter` - el patrón métrico de cada verso, `rhyme` - la etiqueta de la rima de cada verso. En un patrón métrico `+` es una sílaba tónica y `-` una átona, así que su longitud es el número de sílabas métricas: 11 para un endecasílabo, 14 para un alejandrino. Las etiquetas iguales marcan los versos que riman entre sí, `-` un verso que no rima con ningún otro. Los registros van por periodo en el orden de `periods`, dentro de un periodo por el identificador de DISCO con sus números comparados como números (`1035e_269` antes de `1035e_1360`), que mantiene juntos los sonetos de un autor en el orden de su fuente.

Los parámetros son los mismos que los de `get_texts`.

!!! example "Ejemplo"

    ``` python
    from collections import Counter
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()

    # Los primeros versos de un soneto con su rima y su métrica
    record = next(ss.get_records(author="rubén darío"))
    lines = record["text"].replace("\n\n", "\n").split("\n")
    for line, pattern, label in list(zip(lines, record["meter"], record["rhyme"]))[:4]:
        print(f"{label} {pattern:<14} {line}")
    # A -+---+---+-    En medio del abismo de la duda
    # B +----+-+-+-    lleno de oscuridad, de sombra vana
    # B +--+---+-+-    hay una estrella que reflejos mana
    # A -+-+---+-+-    sublime, sí, mas silenciosa, muda.

    # La proporción de endecasílabos y alejandrinos por periodo
    for period in ss.periods:
        lengths = Counter(
            len(pattern) for record in ss.get_records(period=period) for pattern in record["meter"]
        )
        total = sum(lengths.values())
        print(period, f"{lengths[11] / total:.2f}", f"{lengths[14] / total:.2f}")
    # 15th-17th 0.98 0.00
    # 18th 0.99 0.00
    # 19th 0.86 0.09
    # 20th 0.60 0.40
    ```

!!! warning "La anotación es automática"
    Los patrones métricos y las etiquetas de la rima son la anotación automática de DISCO, no una manual: la escansión de ADSO (precisión 0,91) y, para los sonetos modernistas y filipinos, de Jumper (0,95); la rima de RhymeTagger. Son una referencia con la que comparar una escansión, no un patrón de oro: un patrón puede perder una sinalefa o un acento que haría un lector. 20 sonetos no tienen etiquetas de la rima, y las secuencias largas no las tienen después de la letra `N`: esa etiqueta es una cadena vacía.

!!! note "Sonetos, secuencias y títulos"
    4211 registros son sonetos de 14 versos. Los demás son sonetos con estrambote (17 versos, etc.), unos pocos incompletos o de forma irregular («El soneto de trece versos» de Darío) y secuencias de sonetos que DISCO guarda en un solo fichero, de hasta 98 versos. Los sonetos de una secuencia en ficheros separados tienen el título `Part of: ` y el título de la secuencia (397 registros). Los títulos y la ortografía son los de las fuentes de DISCO, algunos títulos en mayúsculas.
