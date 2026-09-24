# Literatura en español

!!! info ""
    **ests.datasets.SpanishLiterature**

## Descripción

Una colección de literatura en español de dominio público: 150 obras de 33 autores de España, Hispanoamérica y Filipinas, de Cervantes a los años veinte, 65 millones de caracteres (unos 11 millones de palabras) en cuatro géneros:

| Género | Clave | Autores | Obras |
| :----- | :---- | :------ | :---: |
| Prosa | `prose` | Pérez Galdós (21), Blasco Ibáñez (15), Palacio Valdés (13), Pardo Bazán (13), Pereda (8), Unamuno (6), Valera (6), Valle-Inclán (5), Clarín (3), Payró (3), Alarcón (2), Cervantes (2), Martí (2), Rizal (2), Darío, Larra, Lugones, Palma, Quevedo, Quiroga | 107 |
| Poesía | `poems` | Darío (5), Hernández (2), Machado, Rosalía de Castro, Zorrilla | 10 |
| Teatro | `drama` | Valle-Inclán (4), Arniches (3), Ruiz de Alarcón (3), Lope de Vega (2), Cervantes, Dicenta, Moratín, Zorrilla | 16 |
| Ensayo | `publicism` | Unamuno (3), Darío (2), Ingenieros (2), Ramón y Cajal (2), Alarcón, Blasco Ibáñez, Larra, Lugones, Rodó, Sarmiento, Valera, Zorrilla | 17 |

Por país: España (122), Argentina (10), Nicaragua (8), México (3), Cuba (2), Uruguay (2), Filipinas (2), Perú (1); el país es el del autor, así que Juan Ruiz de Alarcón, nacido en México, cuenta para México. Todas las obras son de dominio público tanto en España, donde el autor murió antes de 1946, como en los Estados Unidos, donde se publicaron antes de 1931. La colección sirve para la atribución de autoría y para comparar géneros, épocas y el español de España y de América.

Los textos son las transcripciones del [Proyecto Gutenberg](https://www.gutenberg.org), recortadas al texto del autor: se quitan las portadas, las notas de los transcriptores, las listas de otras obras y los anuncios, los índices, las introducciones, los prólogos y las notas de los editores, las fe de erratas y las notas al pie, así como el marcado de las transcripciones (los guiones bajos de la cursiva, las imágenes, los números de las estrofas). Los prólogos, las dedicatorias y las notas de los propios autores se quedan. Las obras en varios tomos se unen en un solo texto. Los años son los de la primera publicación (`1605`-`1615` para las dos partes del Quijote); los archivos de la colección llevan los números de los libros del Proyecto Gutenberg.

El archivo (19 MB) se guarda en el repositorio de la biblioteca, se descarga una vez en el directorio de datos, se verifica con su suma de comprobación SHA-256 y se extrae; los textos se leen de uno en uno.

??? info "Las 150 obras"

    | Autor | Obra | Género | Años | País |
    | :---- | :--- | :----: | :--: | :--- |
    | Pedro Antonio de Alarcón | El clavo | `prose` | 1853 | España |
    | Pedro Antonio de Alarcón | El niño de la bola | `prose` | 1880 | España |
    | Vicente Blasco Ibáñez | Arroz y tartana | `prose` | 1894 | España |
    | Vicente Blasco Ibáñez | Flor de mayo | `prose` | 1895 | España |
    | Vicente Blasco Ibáñez | La barraca | `prose` | 1898 | España |
    | Vicente Blasco Ibáñez | Entre naranjos | `prose` | 1900 | España |
    | Vicente Blasco Ibáñez | La catedral | `prose` | 1903 | España |
    | Vicente Blasco Ibáñez | El intruso | `prose` | 1904 | España |
    | Vicente Blasco Ibáñez | La bodega | `prose` | 1905 | España |
    | Vicente Blasco Ibáñez | La horda | `prose` | 1905 | España |
    | Vicente Blasco Ibáñez | La maja desnuda | `prose` | 1906 | España |
    | Vicente Blasco Ibáñez | Sangre y arena | `prose` | 1908 | España |
    | Vicente Blasco Ibáñez | Los muertos mandan | `prose` | 1909 | España |
    | Vicente Blasco Ibáñez | Los argonautas | `prose` | 1914 | España |
    | Vicente Blasco Ibáñez | Los cuatro jinetes del Apocalipsis | `prose` | 1916 | España |
    | Vicente Blasco Ibáñez | Mare nostrum | `prose` | 1918 | España |
    | Vicente Blasco Ibáñez | Los enemigos de la mujer | `prose` | 1919 | España |
    | Miguel de Cervantes | Don Quijote de la Mancha | `prose` | 1605-1615 | España |
    | Miguel de Cervantes | Novelas ejemplares | `prose` | 1613 | España |
    | Leopoldo Alas «Clarín» | La Regenta | `prose` | 1884-1885 | España |
    | Leopoldo Alas «Clarín» | Su único hijo | `prose` | 1890 | España |
    | Leopoldo Alas «Clarín» | El Señor y lo demás, son cuentos | `prose` | 1893 | España |
    | Rubén Darío | Azul... | `prose` | 1888 | Nicaragua |
    | Benito Pérez Galdós | La Fontana de Oro | `prose` | 1870 | España |
    | Benito Pérez Galdós | Bailén | `prose` | 1873 | España |
    | Benito Pérez Galdós | Trafalgar | `prose` | 1873 | España |
    | Benito Pérez Galdós | Cádiz | `prose` | 1874 | España |
    | Benito Pérez Galdós | Zaragoza | `prose` | 1874 | España |
    | Benito Pérez Galdós | Gloria | `prose` | 1876-1877 | España |
    | Benito Pérez Galdós | Marianela | `prose` | 1878 | España |
    | Benito Pérez Galdós | La familia de León Roch | `prose` | 1878-1879 | España |
    | Benito Pérez Galdós | La desheredada | `prose` | 1881 | España |
    | Benito Pérez Galdós | El amigo Manso | `prose` | 1882 | España |
    | Benito Pérez Galdós | La de Bringas | `prose` | 1884 | España |
    | Benito Pérez Galdós | Tormento | `prose` | 1884 | España |
    | Benito Pérez Galdós | Fortunata y Jacinta | `prose` | 1887 | España |
    | Benito Pérez Galdós | Miau | `prose` | 1888 | España |
    | Benito Pérez Galdós | Torquemada en la hoguera | `prose` | 1889 | España |
    | Benito Pérez Galdós | Realidad | `prose` | 1889 | España |
    | Benito Pérez Galdós | La incógnita | `prose` | 1889 | España |
    | Benito Pérez Galdós | Torquemada en la cruz | `prose` | 1893 | España |
    | Benito Pérez Galdós | Torquemada en el purgatorio | `prose` | 1894 | España |
    | Benito Pérez Galdós | Torquemada y San Pedro | `prose` | 1895 | España |
    | Benito Pérez Galdós | Misericordia | `prose` | 1897 | España |
    | Mariano José de Larra | El doncel de don Enrique el Doliente | `prose` | 1834 | España |
    | Leopoldo Lugones | Las fuerzas extrañas | `prose` | 1906 | Argentina |
    | José Martí | Amistad funesta | `prose` | 1885 | Cuba |
    | José Martí | La Edad de Oro | `prose` | 1889 | Cuba |
    | Armando Palacio Valdés | El señorito Octavio | `prose` | 1881 | España |
    | Armando Palacio Valdés | Marta y María | `prose` | 1883 | España |
    | Armando Palacio Valdés | El idilio de un enfermo | `prose` | 1884 | España |
    | Armando Palacio Valdés | Riverita | `prose` | 1886 | España |
    | Armando Palacio Valdés | Maximina | `prose` | 1887 | España |
    | Armando Palacio Valdés | El cuarto poder | `prose` | 1888 | España |
    | Armando Palacio Valdés | La hermana San Sulpicio | `prose` | 1889 | España |
    | Armando Palacio Valdés | La espuma | `prose` | 1890 | España |
    | Armando Palacio Valdés | La fe | `prose` | 1892 | España |
    | Armando Palacio Valdés | El maestrante | `prose` | 1893 | España |
    | Armando Palacio Valdés | La alegría del capitán Ribot | `prose` | 1899 | España |
    | Armando Palacio Valdés | La aldea perdida | `prose` | 1903 | España |
    | Armando Palacio Valdés | Tristán o el pesimismo | `prose` | 1906 | España |
    | Ricardo Palma | Tradiciones peruanas | `prose` | 1872-1910 | Perú |
    | Emilia Pardo Bazán | Un viaje de novios | `prose` | 1881 | España |
    | Emilia Pardo Bazán | La Tribuna | `prose` | 1883 | España |
    | Emilia Pardo Bazán | El cisne de Vilamorta | `prose` | 1885 | España |
    | Emilia Pardo Bazán | Los pazos de Ulloa | `prose` | 1886 | España |
    | Emilia Pardo Bazán | La madre naturaleza | `prose` | 1887 | España |
    | Emilia Pardo Bazán | Insolación y Morriña | `prose` | 1889 | España |
    | Emilia Pardo Bazán | Una cristiana | `prose` | 1890 | España |
    | Emilia Pardo Bazán | La prueba | `prose` | 1890 | España |
    | Emilia Pardo Bazán | La piedra angular | `prose` | 1891 | España |
    | Emilia Pardo Bazán | Cuentos de amor | `prose` | 1898 | España |
    | Emilia Pardo Bazán | La quimera | `prose` | 1905 | España |
    | Emilia Pardo Bazán | La sirena negra | `prose` | 1908 | España |
    | Emilia Pardo Bazán | Dulce dueño | `prose` | 1911 | España |
    | Roberto J. Payró | El casamiento de Laucha | `prose` | 1906 | Argentina |
    | Roberto J. Payró | Pago Chico | `prose` | 1908 | Argentina |
    | Roberto J. Payró | Divertidas aventuras del nieto de Juan Moreira | `prose` | 1910 | Argentina |
    | José María de Pereda | Escenas montañesas | `prose` | 1864 | España |
    | José María de Pereda | Los hombres de pro | `prose` | 1872 | España |
    | José María de Pereda | De tal palo, tal astilla | `prose` | 1880 | España |
    | José María de Pereda | El sabor de la tierruca | `prose` | 1882 | España |
    | José María de Pereda | Pedro Sánchez | `prose` | 1883 | España |
    | José María de Pereda | Sotileza | `prose` | 1885 | España |
    | José María de Pereda | La puchera | `prose` | 1889 | España |
    | José María de Pereda | Peñas arriba | `prose` | 1895 | España |
    | Francisco de Quevedo | Historia de la vida del Buscón | `prose` | 1626 | España |
    | Horacio Quiroga | Cuentos de amor de locura y de muerte | `prose` | 1917 | Uruguay |
    | José Rizal | Noli me tángere | `prose` | 1887 | Filipinas |
    | José Rizal | El filibusterismo | `prose` | 1891 | Filipinas |
    | Miguel de Unamuno | Amor y pedagogía | `prose` | 1902 | España |
    | Miguel de Unamuno | El espejo de la muerte | `prose` | 1913 | España |
    | Miguel de Unamuno | Niebla | `prose` | 1914 | España |
    | Miguel de Unamuno | Abel Sánchez | `prose` | 1917 | España |
    | Miguel de Unamuno | Tres novelas ejemplares y un prólogo | `prose` | 1920 | España |
    | Miguel de Unamuno | La tía Tula | `prose` | 1921 | España |
    | Juan Valera | Pepita Jiménez | `prose` | 1874 | España |
    | Juan Valera | Las ilusiones del doctor Faustino | `prose` | 1875 | España |
    | Juan Valera | El comendador Mendoza | `prose` | 1877 | España |
    | Juan Valera | Doña Luz | `prose` | 1879 | España |
    | Juan Valera | Juanita la Larga | `prose` | 1895 | España |
    | Juan Valera | Genio y figura | `prose` | 1897 | España |
    | Ramón del Valle-Inclán | Sonata de otoño. Sonata de invierno | `prose` | 1902-1905 | España |
    | Ramón del Valle-Inclán | Sonata de estío | `prose` | 1903 | España |
    | Ramón del Valle-Inclán | Sonata de primavera | `prose` | 1904 | España |
    | Ramón del Valle-Inclán | La media noche | `prose` | 1917 | España |
    | Ramón del Valle-Inclán | Tirano Banderas | `prose` | 1926 | España |
    | Rubén Darío | Prosas profanas | `poems` | 1896 | Nicaragua |
    | Rubén Darío | Cantos de vida y esperanza | `poems` | 1905 | Nicaragua |
    | Rubén Darío | El canto errante | `poems` | 1907 | Nicaragua |
    | Rubén Darío | Poema del otoño y otros poemas | `poems` | 1910 | Nicaragua |
    | Rubén Darío | Canto a la Argentina y otros poemas | `poems` | 1914 | Nicaragua |
    | José Hernández | El gaucho Martín Fierro | `poems` | 1872 | Argentina |
    | José Hernández | La vuelta de Martín Fierro | `poems` | 1879 | Argentina |
    | Antonio Machado | Poesías completas | `poems` | 1917 | España |
    | Rosalía de Castro | En las orillas del Sar | `poems` | 1884 | España |
    | José Zorrilla | Granada. Poema oriental | `poems` | 1852 | España |
    | Carlos Arniches | La señorita de Trevélez | `drama` | 1916 | España |
    | Carlos Arniches | Los caciques | `drama` | 1920 | España |
    | Carlos Arniches | Es mi hombre | `drama` | 1921 | España |
    | Miguel de Cervantes | Entremeses | `drama` | 1615 | España |
    | Joaquín Dicenta | Juan José | `drama` | 1895 | España |
    | Lope de Vega | Fuenteovejuna | `drama` | 1619 | España |
    | Lope de Vega | El castigo sin venganza | `drama` | 1634 | España |
    | Leandro Fernández de Moratín | El sí de las niñas | `drama` | 1806 | España |
    | Juan Ruiz de Alarcón | Los favores del mundo | `drama` | 1628 | México |
    | Juan Ruiz de Alarcón | Las paredes oyen | `drama` | 1628 | México |
    | Juan Ruiz de Alarcón | La verdad sospechosa | `drama` | 1634 | México |
    | Ramón del Valle-Inclán | El marqués de Bradomín | `drama` | 1907 | España |
    | Ramón del Valle-Inclán | Romance de lobos | `drama` | 1908 | España |
    | Ramón del Valle-Inclán | Luces de bohemia | `drama` | 1920-1924 | España |
    | Ramón del Valle-Inclán | Divinas palabras | `drama` | 1920 | España |
    | José Zorrilla | Traidor, inconfeso y mártir | `drama` | 1849 | España |
    | Pedro Antonio de Alarcón | Viajes por España | `publicism` | 1883 | España |
    | Vicente Blasco Ibáñez | Oriente | `publicism` | 1907 | España |
    | Rubén Darío | Los raros | `publicism` | 1896 | Nicaragua |
    | Rubén Darío | España contemporánea | `publicism` | 1901 | Nicaragua |
    | José Ingenieros | La simulación en la lucha por la vida | `publicism` | 1903 | Argentina |
    | José Ingenieros | El hombre mediocre | `publicism` | 1913 | Argentina |
    | Mariano José de Larra | Fígaro. Artículos selectos | `publicism` | 1832-1837 | España |
    | Leopoldo Lugones | El payador | `publicism` | 1916 | Argentina |
    | Santiago Ramón y Cajal | Reglas y consejos sobre investigación científica | `publicism` | 1897 | España |
    | Santiago Ramón y Cajal | Recuerdos de mi vida | `publicism` | 1901-1917 | España |
    | José Enrique Rodó | Ariel | `publicism` | 1900 | Uruguay |
    | Domingo Faustino Sarmiento | Facundo | `publicism` | 1845 | Argentina |
    | Miguel de Unamuno | Vida de Don Quijote y Sancho | `publicism` | 1905 | España |
    | Miguel de Unamuno | Del sentimiento trágico de la vida | `publicism` | 1913 | España |
    | Miguel de Unamuno | Andanzas y visiones españolas | `publicism` | 1922 | España |
    | Juan Valera | Cartas americanas | `publicism` | 1889 | España |
    | José Zorrilla | Recuerdos del tiempo viejo I | `publicism` | 1880 | España |

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `data_dir` | str/Path | `DEFAULT_DATA_DIR.joinpath("texts")` | Ruta al directorio del conjunto de datos |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `genres` | tuple[str] | Tupla de géneros: `prose`, `poems`, `drama`, `publicism` |
| `authors` | dict[str, str] | Nombres de los autores por los nombres de sus carpetas |

## Métodos

### download

Descarga el archivo con verificación de la suma de comprobación y extrae los ficheros. Un archivo dañado o sustituido se borra y se descarga de nuevo en la misma llamada; si el archivo está pero faltan ficheros, se extrae otra vez. Una llamada repetida no descarga nada.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `force` | bool | `False` | Descargar el conjunto de datos aunque ya esté descargado |

!!! example "Ejemplo"

    ``` python
    from ests.datasets import SpanishLiterature

    sl = SpanishLiterature()
    sl.download()
    sl.info
    # {'name': 'spanish_literature',
    #  'url': 'https://www.gutenberg.org',
    #  'description': 'Spanish-language literature in the public domain',
    #  'author': 'Shkarin S.S.',
    #  'license': 'Public domain'}
    ```

### get_texts

Extrae los textos (sin encabezados) del conjunto de datos.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `genre` | str | `None` | Género: `prose`, `poems`, `drama` o `publicism` |
| `author` | str | `None` | Autor: una subcadena del nombre, sin distinguir mayúsculas ni tildes |
| `country` | str | `None` | País: una subcadena del nombre en español, sin distinguir mayúsculas ni tildes |
| `year_from` | int | `None` | Primer año de la primera publicación |
| `year_to` | int | `None` | Último año de la primera publicación |
| `min_len` | int | `None` | Longitud mínima del texto (en caracteres) |
| `max_len` | int | `None` | Longitud máxima del texto (en caracteres) |
| `limit` | int | `None` | Número de textos |

Los filtros se combinan; `author="galdos"` encuentra a Benito Pérez Galdós, `country="mexico"` encuentra `México`. Un género desconocido, un primer año posterior al último, una longitud menor que uno, una longitud mínima mayor que la máxima y un límite negativo levantan `ParameterError`.

!!! example "Ejemplo"

    ``` python
    from ests.datasets import SpanishLiterature

    sl = SpanishLiterature()
    for text in sl.get_texts(genre="poems", author="Rosalía", limit=1):
        print(text[:107])
    # Aunque no alcancen gloria,
    #     Pensé escribiendo libro tan pequeño,
    #     Son fáciles y breves mis canciones,
    ```

### get_records

Extrae los registros (con encabezados) del conjunto de datos. Campos del registro: `genre` - género, `author` - autor, `title` - título, `year_from` y `year_to` - los años de la primera publicación, `country` - el país del autor en español, `text` - texto, `file` - ruta al fichero. Los registros van por género en el orden de `genres`, dentro de un género por la carpeta del autor y por año.

Los parámetros son los mismos que los de `get_texts`.

!!! example "Ejemplo"

    ``` python
    from ests.datasets import SpanishLiterature

    sl = SpanishLiterature()

    # El teatro del siglo XX
    for record in sl.get_records(genre="drama", year_from=1900):
        print(record["title"], record["year_from"], record["author"])
    # La señorita de Trevélez 1916 Carlos Arniches
    # Los caciques 1920 Carlos Arniches
    # Es mi hombre 1921 Carlos Arniches
    # El marqués de Bradomín 1907 Ramón del Valle-Inclán
    # Romance de lobos 1908 Ramón del Valle-Inclán
    # Luces de bohemia 1920 Ramón del Valle-Inclán
    # Divinas palabras 1920 Ramón del Valle-Inclán
    ```

!!! warning "La ortografía sigue a la edición"
    Los textos conservan la ortografía de las ediciones transcritas. 62 de ellos tienen las tildes de su época (`á` como preposición, `fué`, `dió`), 87 tienen las modernas: las ediciones impresas después de las reformas de la Academia y una docena de textos que los transcriptores del Proyecto Gutenberg modernizaron según las normas de 2010 (entre ellos El castigo sin venganza, Las paredes oyen, Tirano Banderas, Luces de bohemia, Los caciques y Es mi hombre). Tres novelas vienen de ediciones de 1978-1982 con ortografía moderna (Arroz y tartana, La catedral, Juanita la Larga). Galdós tiene 12 textos del primer tipo y 9 del segundo. Como `á` y `a` son palabras distintas para una lista de frecuencias, la estilometría sobre las palabras más frecuentes puede separar los textos por su edición y no por su autor: quite la tilde de los monosílabos (`á`, `é`, `ó`, `ú`, `fué`, `dió`, `vió`) antes de una comparación así. A Abel Sánchez le faltan la mayoría de los `¿` y `¡` de apertura, como a su edición.

!!! note "Ediciones y contenido"
    Varias obras siguen ediciones revisadas por sus autores: la Opera Omnia de Valle-Inclán (1913-1924), las obras completas de Pereda, Palacio Valdés y Blasco Ibáñez, la sexta edición de Reglas y consejos sobre investigación científica (1923), muy ampliada respecto al discurso de 1897; los años siguen siendo los de la primera publicación. Algunos registros son selecciones o tomos sueltos: Tradiciones peruanas (27 tradiciones), Recuerdos del tiempo viejo I (el primero de tres tomos), El payador (el primer y único tomo publicado); los Entremeses son los ocho de la colección de 1615, sin los tres de atribución dudosa. Las Novelas ejemplares van sin La tía fingida. Dos registros contienen dos obras cada uno, como dicen sus títulos: Insolación y Morriña y Sonata de otoño. Sonata de invierno. En algunas comedias del Siglo de Oro quedan los corchetes de los editores alrededor de las acotaciones y de los nombres que añadieron.
