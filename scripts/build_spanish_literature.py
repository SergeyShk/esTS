"""
Building the archive of the SpanishLiterature dataset from Project Gutenberg

The works are in the public domain both in Spain (the author died more than
80 years ago) and in the United States (published before 1931). Every book is
downloaded once into a cache and cut between the start and end markers of
Project Gutenberg; every line that mentions Project Gutenberg and the credits of
the transcription go: without the licence and the trademark the text is in the
public domain and can be redistributed. Every volume is then cut to the text of
the author by the markers of BOUNDS - without the title pages, the notes of the
transcribers, the tables of contents, the advertisements and the introductions
and notes of the editors - and cleared of the markup of the transcription: the
images, the footnotes, the italics and the bold, the numbers of stanzas. Works
in several volumes are joined in order.

Usage:
    uv run python scripts/build_spanish_literature.py CACHE_DIR OUTPUT_DIR

The archive is written deterministically (sorted names, zero times and owners),
so a rebuild from the same cache gives the same SHA-256. A published archive is
never replaced: a new build raises VERSION in the module of the dataset, goes to
ests/datasets/data under the new name, and its checksum goes to ARCHIVE_SHA256.
"""

import io
import re
import sys
import tarfile
import time
import urllib.request
from hashlib import sha256
from pathlib import Path

from ests.datasets.spanish_literature import AUTHORS, GENRES, NAME, VERSION

ROOT = f"{NAME}_v{VERSION}"
URL = "https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
DELAY = 2.0

# Gutenberg numbers (volumes in order), genre, author key, title, first and last year
# of the first publication, country
WORKS = [
    # Spain, Golden Age and the eighteenth century
    ((2000,), "prose", "cervantes", "Don Quijote de la Mancha", 1605, 1615, "España"),
    ((61202,), "prose", "cervantes", "Novelas ejemplares", 1613, 1613, "España"),
    ((57955,), "drama", "cervantes", "Entremeses", 1615, 1615, "España"),
    ((32315,), "prose", "quevedo", "Historia de la vida del Buscón", 1626, 1626, "España"),
    ((60198,), "drama", "lope", "Fuenteovejuna", 1619, 1619, "España"),
    ((78160,), "drama", "lope", "El castigo sin venganza", 1634, 1634, "España"),
    ((57590,), "drama", "ruiz_de_alarcon", "La verdad sospechosa", 1634, 1634, "México"),
    ((77445,), "drama", "ruiz_de_alarcon", "Las paredes oyen", 1628, 1628, "México"),
    ((18580,), "drama", "ruiz_de_alarcon", "Los favores del mundo", 1628, 1628, "México"),
    ((50027,), "drama", "moratin", "El sí de las niñas", 1806, 1806, "España"),
    # Spain, Romanticism
    ((31541,), "publicism", "larra", "Fígaro. Artículos selectos", 1832, 1837, "España"),
    (
        (53587, 53588, 53589, 53590),
        "prose",
        "larra",
        "El doncel de don Enrique el Doliente",
        1834,
        1834,
        "España",
    ),
    ((76073,), "drama", "zorrilla", "Traidor, inconfeso y mártir", 1849, 1849, "España"),
    ((55480, 58275), "poems", "zorrilla", "Granada. Poema oriental", 1852, 1852, "España"),
    ((53294,), "publicism", "zorrilla", "Recuerdos del tiempo viejo I", 1880, 1880, "España"),
    ((70984,), "poems", "rosalia_de_castro", "En las orillas del Sar", 1884, 1884, "España"),
    # Spain, realism and naturalism
    ((67248,), "prose", "alarcon", "El clavo", 1853, 1853, "España"),
    ((59154,), "prose", "alarcon", "El niño de la bola", 1880, 1880, "España"),
    ((26314,), "publicism", "alarcon", "Viajes por España", 1883, 1883, "España"),
    ((17223,), "prose", "valera", "Pepita Jiménez", 1874, 1874, "España"),
    ((52093, 53436), "prose", "valera", "Las ilusiones del doctor Faustino", 1875, 1875, "España"),
    ((13210,), "prose", "valera", "El comendador Mendoza", 1877, 1877, "España"),
    ((17338,), "prose", "valera", "Doña Luz", 1879, 1879, "España"),
    ((16484,), "prose", "valera", "Juanita la Larga", 1895, 1895, "España"),
    ((17317,), "prose", "valera", "Genio y figura", 1897, 1897, "España"),
    ((62984,), "publicism", "valera", "Cartas americanas", 1889, 1889, "España"),
    ((12627,), "prose", "pereda", "Escenas montañesas", 1864, 1864, "España"),
    ((14995,), "prose", "pereda", "Los hombres de pro", 1872, 1872, "España"),
    ((63922,), "prose", "pereda", "De tal palo, tal astilla", 1880, 1880, "España"),
    ((53429,), "prose", "pereda", "El sabor de la tierruca", 1882, 1882, "España"),
    ((74981,), "prose", "pereda", "Pedro Sánchez", 1883, 1883, "España"),
    ((49388,), "prose", "pereda", "Sotileza", 1885, 1885, "España"),
    ((55058,), "prose", "pereda", "La puchera", 1889, 1889, "España"),
    ((24127,), "prose", "pereda", "Peñas arriba", 1895, 1895, "España"),
    ((11070,), "prose", "galdos", "La Fontana de Oro", 1870, 1870, "España"),
    ((16961,), "prose", "galdos", "Trafalgar", 1873, 1873, "España"),
    ((14311,), "prose", "galdos", "Bailén", 1873, 1873, "España"),
    ((21906,), "prose", "galdos", "Cádiz", 1874, 1874, "España"),
    ((49433,), "prose", "galdos", "Zaragoza", 1874, 1874, "España"),
    ((48946,), "prose", "galdos", "Gloria", 1876, 1877, "España"),
    ((17340,), "prose", "galdos", "Marianela", 1878, 1878, "España"),
    ((48093,), "prose", "galdos", "La familia de León Roch", 1878, 1879, "España"),
    ((25956,), "prose", "galdos", "La desheredada", 1881, 1881, "España"),
    ((55563,), "prose", "galdos", "El amigo Manso", 1882, 1882, "España"),
    ((31465,), "prose", "galdos", "Tormento", 1884, 1884, "España"),
    ((31464,), "prose", "galdos", "La de Bringas", 1884, 1884, "España"),
    ((17013,), "prose", "galdos", "Fortunata y Jacinta", 1887, 1887, "España"),
    ((52392,), "prose", "galdos", "Miau", 1888, 1888, "España"),
    ((15206,), "prose", "galdos", "Torquemada en la hoguera", 1889, 1889, "España"),
    ((54521,), "prose", "galdos", "La incógnita", 1889, 1889, "España"),
    ((54423,), "prose", "galdos", "Realidad", 1889, 1889, "España"),
    ((54861,), "prose", "galdos", "Torquemada en la cruz", 1893, 1893, "España"),
    ((55139,), "prose", "galdos", "Torquemada en el purgatorio", 1894, 1894, "España"),
    ((55915,), "prose", "galdos", "Torquemada y San Pedro", 1895, 1895, "España"),
    ((21831,), "prose", "galdos", "Misericordia", 1897, 1897, "España"),
    ((17406,), "prose", "pardo_bazan", "Un viaje de novios", 1881, 1881, "España"),
    ((17491,), "prose", "pardo_bazan", "La Tribuna", 1883, 1883, "España"),
    ((71469,), "prose", "pardo_bazan", "El cisne de Vilamorta", 1885, 1885, "España"),
    ((18005,), "prose", "pardo_bazan", "Los pazos de Ulloa", 1886, 1886, "España"),
    ((58059,), "prose", "pardo_bazan", "La madre naturaleza", 1887, 1887, "España"),
    ((52597,), "prose", "pardo_bazan", "Insolación y Morriña", 1889, 1889, "España"),
    ((60137,), "prose", "pardo_bazan", "Una cristiana", 1890, 1890, "España"),
    ((65632,), "prose", "pardo_bazan", "La prueba", 1890, 1890, "España"),
    ((68452,), "prose", "pardo_bazan", "La piedra angular", 1891, 1891, "España"),
    ((55514,), "prose", "pardo_bazan", "Cuentos de amor", 1898, 1898, "España"),
    ((49756,), "prose", "pardo_bazan", "La quimera", 1905, 1905, "España"),
    ((51450,), "prose", "pardo_bazan", "La sirena negra", 1908, 1908, "España"),
    ((56044,), "prose", "pardo_bazan", "Dulce dueño", 1911, 1911, "España"),
    ((17073,), "prose", "clarin", "La Regenta", 1884, 1885, "España"),
    ((17341,), "prose", "clarin", "Su único hijo", 1890, 1890, "España"),
    ((62361,), "prose", "clarin", "El Señor y lo demás, son cuentos", 1893, 1893, "España"),
    ((36940,), "prose", "palacio_valdes", "El señorito Octavio", 1881, 1881, "España"),
    ((32364,), "prose", "palacio_valdes", "Marta y María", 1883, 1883, "España"),
    ((25777,), "prose", "palacio_valdes", "El idilio de un enfermo", 1884, 1884, "España"),
    ((29831,), "prose", "palacio_valdes", "Riverita", 1886, 1886, "España"),
    ((40810,), "prose", "palacio_valdes", "Maximina", 1887, 1887, "España"),
    ((24601,), "prose", "palacio_valdes", "El cuarto poder", 1888, 1888, "España"),
    ((31013,), "prose", "palacio_valdes", "La hermana San Sulpicio", 1889, 1889, "España"),
    ((11529,), "prose", "palacio_valdes", "La espuma", 1890, 1890, "España"),
    ((31637,), "prose", "palacio_valdes", "La fe", 1892, 1892, "España"),
    ((30425,), "prose", "palacio_valdes", "El maestrante", 1893, 1893, "España"),
    ((42727,), "prose", "palacio_valdes", "La alegría del capitán Ribot", 1899, 1899, "España"),
    ((36573,), "prose", "palacio_valdes", "La aldea perdida", 1903, 1903, "España"),
    ((26655,), "prose", "palacio_valdes", "Tristán o el pesimismo", 1906, 1906, "España"),
    ((16413,), "prose", "blasco_ibanez", "Arroz y tartana", 1894, 1894, "España"),
    ((41746,), "prose", "blasco_ibanez", "Flor de mayo", 1895, 1895, "España"),
    ((14944,), "prose", "blasco_ibanez", "La barraca", 1898, 1898, "España"),
    ((30122,), "prose", "blasco_ibanez", "Entre naranjos", 1900, 1900, "España"),
    ((16670,), "prose", "blasco_ibanez", "La catedral", 1903, 1903, "España"),
    ((24466,), "prose", "blasco_ibanez", "El intruso", 1904, 1904, "España"),
    ((28927,), "prose", "blasco_ibanez", "La bodega", 1905, 1905, "España"),
    ((33474,), "prose", "blasco_ibanez", "La horda", 1905, 1905, "España"),
    ((43030,), "prose", "blasco_ibanez", "La maja desnuda", 1906, 1906, "España"),
    ((26983,), "prose", "blasco_ibanez", "Sangre y arena", 1908, 1908, "España"),
    ((21651,), "prose", "blasco_ibanez", "Los muertos mandan", 1909, 1909, "España"),
    ((25640,), "prose", "blasco_ibanez", "Los argonautas", 1914, 1914, "España"),
    (
        (24536,),
        "prose",
        "blasco_ibanez",
        "Los cuatro jinetes del Apocalipsis",
        1916,
        1916,
        "España",
    ),
    ((23236,), "prose", "blasco_ibanez", "Mare nostrum", 1918, 1918, "España"),
    ((37139,), "prose", "blasco_ibanez", "Los enemigos de la mujer", 1919, 1919, "España"),
    ((40182,), "publicism", "blasco_ibanez", "Oriente", 1907, 1907, "España"),
    ((59629,), "drama", "dicenta", "Juan José", 1895, 1895, "España"),
    (
        (66373,),
        "publicism",
        "ramon_y_cajal",
        "Reglas y consejos sobre investigación científica",
        1897,
        1897,
        "España",
    ),
    ((58331, 60675), "publicism", "ramon_y_cajal", "Recuerdos de mi vida", 1901, 1917, "España"),
    # Spain, the turn of the century
    ((49149,), "prose", "unamuno", "Amor y pedagogía", 1902, 1902, "España"),
    ((77759,), "prose", "unamuno", "El espejo de la muerte", 1913, 1913, "España"),
    ((49836,), "prose", "unamuno", "Niebla", 1914, 1914, "España"),
    ((44512,), "prose", "unamuno", "Abel Sánchez", 1917, 1917, "España"),
    ((55916,), "prose", "unamuno", "Tres novelas ejemplares y un prólogo", 1920, 1920, "España"),
    ((44358,), "prose", "unamuno", "La tía Tula", 1921, 1921, "España"),
    ((75472,), "publicism", "unamuno", "Vida de Don Quijote y Sancho", 1905, 1905, "España"),
    ((59852,), "publicism", "unamuno", "Del sentimiento trágico de la vida", 1913, 1913, "España"),
    ((78052,), "publicism", "unamuno", "Andanzas y visiones españolas", 1922, 1922, "España"),
    (
        (46182,),
        "prose",
        "valle_inclan",
        "Sonata de otoño. Sonata de invierno",
        1902,
        1905,
        "España",
    ),
    ((42424,), "prose", "valle_inclan", "Sonata de estío", 1903, 1903, "España"),
    ((42440,), "prose", "valle_inclan", "Sonata de primavera", 1904, 1904, "España"),
    ((55448,), "prose", "valle_inclan", "La media noche", 1917, 1917, "España"),
    ((68154,), "prose", "valle_inclan", "Tirano Banderas", 1926, 1926, "España"),
    ((58049,), "drama", "valle_inclan", "El marqués de Bradomín", 1907, 1907, "España"),
    ((10506,), "drama", "valle_inclan", "Romance de lobos", 1908, 1908, "España"),
    ((69951,), "drama", "valle_inclan", "Divinas palabras", 1920, 1920, "España"),
    ((68745,), "drama", "valle_inclan", "Luces de bohemia", 1920, 1924, "España"),
    ((53947,), "drama", "arniches", "La señorita de Trevélez", 1916, 1916, "España"),
    ((67638,), "drama", "arniches", "Los caciques", 1920, 1920, "España"),
    ((67895,), "drama", "arniches", "Es mi hombre", 1921, 1921, "España"),
    ((68525,), "poems", "machado", "Poesías completas", 1917, 1917, "España"),
    # Latin America and the Philippines
    ((14765,), "poems", "hernandez", "El gaucho Martín Fierro", 1872, 1872, "Argentina"),
    ((15066,), "poems", "hernandez", "La vuelta de Martín Fierro", 1879, 1879, "Argentina"),
    ((33267,), "publicism", "sarmiento", "Facundo", 1845, 1845, "Argentina"),
    ((21282,), "prose", "palma", "Tradiciones peruanas", 1872, 1910, "Perú"),
    ((18166,), "prose", "marti", "Amistad funesta", 1885, 1885, "Cuba"),
    ((19898,), "prose", "marti", "La Edad de Oro", 1889, 1889, "Cuba"),
    ((47584,), "prose", "rizal", "Noli me tángere", 1887, 1887, "Filipinas"),
    ((30903,), "prose", "rizal", "El filibusterismo", 1891, 1891, "Filipinas"),
    ((52894,), "prose", "dario", "Azul...", 1888, 1888, "Nicaragua"),
    ((47650,), "poems", "dario", "Prosas profanas", 1896, 1896, "Nicaragua"),
    ((50341,), "poems", "dario", "Cantos de vida y esperanza", 1905, 1905, "Nicaragua"),
    ((51711,), "poems", "dario", "El canto errante", 1907, 1907, "Nicaragua"),
    ((51569,), "poems", "dario", "Poema del otoño y otros poemas", 1910, 1910, "Nicaragua"),
    ((51458,), "poems", "dario", "Canto a la Argentina y otros poemas", 1914, 1914, "Nicaragua"),
    ((50365,), "publicism", "dario", "Los raros", 1896, 1896, "Nicaragua"),
    ((54934,), "publicism", "dario", "España contemporánea", 1901, 1901, "Nicaragua"),
    ((22899,), "publicism", "rodo", "Ariel", 1900, 1900, "Uruguay"),
    ((13507,), "prose", "quiroga", "Cuentos de amor de locura y de muerte", 1917, 1917, "Uruguay"),
    ((65689,), "prose", "lugones", "Las fuerzas extrañas", 1906, 1906, "Argentina"),
    ((56451,), "publicism", "lugones", "El payador", 1916, 1916, "Argentina"),
    ((62952,), "prose", "payro", "El casamiento de Laucha", 1906, 1906, "Argentina"),
    ((62785,), "prose", "payro", "Pago Chico", 1908, 1908, "Argentina"),
    (
        (60634,),
        "prose",
        "payro",
        "Divertidas aventuras del nieto de Juan Moreira",
        1910,
        1910,
        "Argentina",
    ),
    (
        (64188,),
        "publicism",
        "ingenieros",
        "La simulación en la lucha por la vida",
        1903,
        1903,
        "Argentina",
    ),
    ((64974,), "publicism", "ingenieros", "El hombre mediocre", 1913, 1913, "Argentina"),
]

# Where the text of the author begins and ends in every volume: the line with the first
# marker is the first line kept, the line with the last marker the last one; the blocks
# between the pairs of markers of cuts are removed. A marker is a substring of the only
# line that has it, or a substring with the number of the line among those that have it
Marker = str | tuple[str, int]
BOUNDS: dict[int, tuple[Marker | None, Marker | None, list[tuple[Marker, Marker]]]] = {
    2000: ("AL DUQUE DE BÉJAR,", None, [(("TASA", 2), "Pedro de Contreras.")]),
    61202: ("Á D. PEDRO FERNÁNDEZ DE CASTRO", "Y con esto se fueron.", [("ÍNDICE.", "373")]),
    57955: (
        "DEL JUEZ DE LOS DIVORCIOS",
        ("FIN DE ESTE ENTREMES.", 9),
        [(("ENTREMES", 15), ("FIN DE ESTE ENTREMES.", 7))],
    ),
    32315: ("Libro Primero: Capítulo I: En que cuenta", "de vida y costumbres.", []),
    60198: ("COMEDIA FAMOSA", "FIN", []),
    78160: ("SEÑOR DUQUE DE", None, []),
    57590: ("PERSONAS.", None, []),
    77445: ("PERSONAS.", None, []),
    18580: (
        "PERSONAS:",
        "dan fin, y piden perdón.",
        [('"Tormento" pone el texto original', 'mujer."')],
    ),
    50027: ("PERSONAS.", "FIN.", [("Imp. de EL PORVENIR", "Imp. de EL PORVENIR")]),
    31541: ("MI NOMBRE Y MIS PROPÓSITOS", None, []),
    53587: ("CAPITULO I.", "FIN DEL TOMO PRIMERO.", []),
    53588: ("CAPITULO IX.", "FIN DEL TOMO SEGUNDO.", []),
    53589: ("CAPITULO XXII.", "FIN DEL TOMO TERCERO.", []),
    53590: ("CAPITULO XXXII.", "AQUI YACE MACÍAS EL ENAMORADO.", []),
    76073: ("REPARTO", None, []),
    55480: (
        "Bruselas, 21 de Febrero de 1852.",
        "FIN DE LOS VERSOS CONTENIDOS EN EL TOMO PRIMERO.",
        [],
    ),
    58275: ("INVOCACIÓN", "Fin de los versos contenidos en el tomo segundo.", []),
    53294: ("Este libro no necesitaba prólogo", "se olvida de los ángeles en Barcelona.", []),
    70984: ("Aunque no alcancen gloria,", "La luz del faro que le guíe al puerto.", []),
    67248: (
        "Felipe encendió un cigarro y habló",
        "de melancolía que oscurece a ratos la frente de mi amigo.",
        [],
    ),
    59154: ("EN LO ALTO DE LA SIERRA.", "FIN.", []),
    26314: ("AL SEÑOR D. MARIANO VÁZQUEZ,", "costumbre de veranear en tierra extranjera.", []),
    17223: ("El señor deán de la catedral de..., muerto", None, []),
    52093: ("A MI QUERIDO AMIGO", "FIN DEL TOMO I", []),
    53436: (("XV.", 1), "indulgencia del público ilustrado y desapasionado.", []),
    13210: ("Á LA EXCMA. SEÑORA", "Madrid, 1876.", []),
    17338: ("A la señora condesa de Gomar", None, []),
    16484: ("Cierto amigo mío, diputado novel", None, []),
    17317: ("Medio de fonte leporum", None, []),
    62984: ("AL EXCMO. SEÑOR", "tanto por ciento que cobran en Madrid los autores", []),
    12627: ("ADVERTENCIA", "que me le ha dictado.", []),
    14995: ("ADVERTENCIA", "1872.", []),
    63922: ("AL PÍO LECTOR", "Diciembre de 1879.", []),
    53429: ("EL ESCENARIO", "POLANCO, octubre de 1881.", []),
    74981: ("Entonces no era mi pueblo la mitad", "POLANCO, octubre 1883.", []),
    49388: ("MIS CONTEMPORÁNEOS DE SANTANDER", "SANTANDER, noviembre 1884.", []),
    55058: ("EN LA ARCILLOSA", "POLANCO, agosto-octubre 1888.", []),
    24127: ("Dedicatoria", None, []),
    11070: ("Los hechos históricos ó novelescos", None, [("ÍNDICE", "XLIII.--Conclusión")]),
    16961: ("Se me permitirá que antes de referir", "Madrid, enero-febrero 1873.", []),
    14311: ("Me hacen ustedes reír con su sencilla", "Octubre-noviembre de 1878.", []),
    21906: ("En una mañana del mes de Febrero de 1810", None, []),
    49433: ("Me parece que fué al anochecer del 18", "FIN DE ZARAGOZA", []),
    48946: (
        "Allá lejos, sobre verde colina",
        "FIN DE LA NOVELA",
        [("FIN DE LA PRIMERA PARTE", ("1890", 2))],
    ),
    17340: ("Perdido", None, []),
    48093: (
        "Ugoibea, 30 de Agosto",
        "FIN DE LA NOVELA",
        [("FIN DEL TOMO PRIMERO", "SEGUNDA PARTE (CONTINUACIÓN)")],
    ),
    25956: ("Saliendo a relucir aquí, sin saber", None, []),
    55563: ("Y por si algún desconfiado", "FIN DE LA NOVELA", []),
    31465: ("Esquina de las Descalzas", None, []),
    31464: ("Era aquello... ¿cómo lo diré yo?", None, []),
    17013: ("Parte primera", "FIN DE LA NOVELA", []),
    52392: ("Á las cuatro de la tarde, la chiquillería", None, []),
    15206: ("Voy á contar cómo fue al quemadero", "FIN DE LA NOVELA", []),
    54521: ("Á D. EQUIS X, EN ORBAJOSA", None, []),
    54423: ("DRAMATIS PERSON", None, []),
    54861: ("PRIMERA PARTE", "FIN DE TORQUEMADA EN LA CRUZ", []),
    55139: ("PRIMERA PARTE", None, []),
    55915: ("PRIMERA PARTE", None, []),
    21831: ("Dos caras, como algunas personas", None, []),
    17406: ("En Septiembre del pasado año 1880", "Marzo, 1881", []),
    17491: ("Prólogo", "¡Viva la República federal!", []),
    71469: ("PRÓLOGO", ("LA CORUÑA, Septiembre de 1884.", 2), []),
    18005: ("Por más que el jinete trataba de sofrenarlo", None, []),
    58059: (
        "Las nubes, amontonadas y de un gris",
        "FIN DEL TOMO SEGUNDO",
        [("FIN DEL TOMO PRIMERO", ("Establecimiento tipográfico-editorial de Daniel Cortezo", 2))],
    ),
    52597: ("A José Lázaro Galdiano", None, []),
    60137: ("Verán ustedes las asignaturas", "FIN", []),
    65632: ("No sé si he dicho en la primera parte", None, []),
    68452: ("ita ut serviamus in novitate spiritus", None, []),
    55514: ("PREFACIO", "temblar una lágrima", []),
    49756: ("Había prescindido en mis novelas", "FIN", []),
    51450: ("En la esquina de la Red de San Luis", None, []),
    56044: ("Escuchad.", "voluntad...", []),
    17073: ("La heroica ciudad dormía la siesta", None, [("FIN DE LA PRIMERA PARTE", "TOMO II")]),
    17341: ("Emma Valcárcel fue una hija única mimada", None, []),
    62361: ("No tenía más consuelo temporal la viuda", None, []),
    36940: ("Despierta el héroe.", "FIN", []),
    32364: ("No está fundado el libro, que hoy tengo el honor", None, []),
    25777: ("DEDICATORIA", "FIN", []),
    29831: (
        "La primera noticia que Miguel tuvo",
        "servido.",
        [("FIN DEL TOMO I", ("TOMO II", 2))],
    ),
    40810: ("LLEGÓ á Pasajes Miguel", "respondió el secretario llevándose el pañuelo", []),
    24601: ("CAPITULO PRIMERO", "resistir tanto dolor y rodó por el suelo", []),
    31013: ("A las aguas de Marmolejo.", None, []),
    11529: ("#Presentación de la farándula", "FIN", []),
    31637: ("No cabía en la iglesia una persona más", None, []),
    30425: ("La casa del maestrante.", None, []),
    42727: ("En Málaga no los guisan mal", "FIN", []),
    36573: ("Et in Arcadia ego.", "FIN", []),
    26655: ("EL DUEÑO DE LA FINCA", "me abracé a él y... ya lo ves, me he salvado.", []),
    16413: ("A las tres de la tarde entró doña Manuela", None, []),
    41746: ("Al amanecer cesó la lluvia.", "Valencia, 1895", []),
    14944: ("AL LECTOR", "Valencia.--Octubre-Diciembre 1898.", []),
    30122: ("Los amigos te esperan en el casino", "Playa de la Malvarrosa (Valencia)", []),
    16670: ("Comenzaba a amanecer cuando Gabriel Luna", None, []),
    24466: ("Comenzaba á clarear el día cuando despertó", "Abril-Junio de 1904.", []),
    28927: (
        "Apresuradamente, como en los tiempos que llegaba tarde",
        "Madrid, Diciembre 1904-Febrero 1905.",
        [],
    ),
    33474: ("A las tres de la madrugada comenzaron a llegar", None, []),
    43030: ("PRIMERA PARTE", "Madrid, Febrero-Abril 1906.", []),
    26983: ("Como en todos los días de corrida", "Madrid.--Enero-Marzo 1908.", []),
    21651: ("Al lector", None, []),
    25640: ("Al sentir un roce en el cuello", None, []),
    24536: ("Debían encontrarse á las cinco de la tarde", None, []),
    23236: ("EL CAPITÁN ULISES FERRAGUT", None, []),
    37139: ("AL LECTOR", "Monte-Carlo.--Enero-Julio 1919.", []),
    40182: ("Este libro--algunos de cuyos", "Agosto-Noviembre 1907.", []),
    59629: (
        "PERSONAJES",
        "FIN DEL DRAMA",
        [("Esta obra es propiedad de su autor", "Queda hecho el depósito que marca la ley")],
    ),
    66373: (
        "PRÓLOGO DE LA SEGUNDA EDICIÓN",
        None,
        [("ÍNDICE", "del método de injertación cultural")],
    ),
    58331: (("ADVERTENCIA AL LECTOR", 1), "FIN DEL TOMO PRIMERO", []),
    60675: (("DOS PALABRAS AL LECTOR", 1), "inteligencia?...", []),
    49149: ("Al Lector,", "considerable monumento de sabiduría", []),
    77759: (("EL ESPEJO DE LA MUERTE", 2), None, []),
    49836: (("PRÓLOGO", 2), "Y luego dirán que no matan las penas", []),
    44512: (("ABEL SÁNCHEZ", 3), "rendía su último cansado respiro", []),
    55916: (("PRÓLOGO", 3), "FIN", []),
    44358: ("PROLOGO", None, []),
    75472: ("PRÓLOGO A ESTA SEGUNDA EDICIÓN", None, []),
    59852: ("EL HOMBRE DE CARNE Y HUESO", "Águia", []),
    78052: (
        "Quiero aquí, a modo de dedicatoria",
        None,
        [("ÍNDICE", "Junto a la vieja Colegiata")],
    ),
    46182: (
        "Amor Adorado, estoy muriéndome",
        "mí, acaso para siempre.",
        [(("ACABÓSE DE IMPRIMIR ESTE LIBRO", 1), "MEMORIAS DEL MARQUES DE BRANDOMIN")],
    ),
    42424: (("MEMORIAS", 3), "de la carne.", []),
    42440: ("DEDICATORIA", "¡FUÉ SATANÁS!", [(("SONETO", 1), "MI SANGRE SE DERRAMA POR LA CAZA")]),
    55448: ("BREVE NOTICIA", "y terrible.", []),
    68154: (("PRÓLOGO", 2), "fueron las ciudades agraciadas", []),
    58049: ("Estos diálogos tuvieron hace", "ASÍ TERMINA LA JORNADA TERCERA", []),
    10506: ("DRAMATIS PERSONAE", "Y metidos en un pleito para veinte años", []),
    69951: (
        ("DRAMATIS PERSONÆ", 1),
        "DIVINAS PALABRAS_",
        [(("OPERA OMNIA", 2), ("VOL. XVII", 2))],
    ),
    68745: (("DRAMATIS PERSONÆ", 1), ("¡Cráneo previlegiado!", 2), []),
    53947: ("A Emilio Thuillier con un efusivo", "FIN DE LA OBRA", []),
    67638: ("REPARTO", None, []),
    67895: ("A Alicante", "FIN DE LA OBRA", []),
    68525: ("(1899-1917)", "vagando por el jardín", []),
    14765: ("Carta del Autor a don José Zoilo Miguens", None, []),
    15066: ("Cuatro palabras de conversación con los lectores", None, []),
    33267: (
        "ASPECTO FÍSICO DE LA REPÚBLICA ARGENTINA, Y CARACTERES",
        "Yungay, 7 de abril de 1851.",
        [("Hemos dividido este", "R. R.")],
    ),
    21282: ("LOS DUENDES DEL CUZCO", None, []),
    18166: ("Una frondosa magnolia", None, []),
    19898: ("Para los niños es este periódico", None, []),
    47584: (
        "Qué, ¿no podría César presentarse",
        "FIN",
        [("BARCELONA", "(De La Correspondencia, de Puerto Rico).")],
    ),
    30903: ("Facilmente se puede suponer que un", None, [("GENT,", "1891.")]),
    52894: ("EL REY BURGUÉS", "que saludan triunfantes la Libertad", []),
    47650: (
        "voces insinuantes, buena y",
        "Y el cuello del gran cisne blanco que me interroga",
        [],
    ),
    50341: ("NICARAGUA", "ni de dónde venimos", []),
    51711: ("A LOS NUEVOS POETAS DE LAS ESPAÑAS", "con el rojo pendón de los reyes del mar", []),
    51569: ("DEDICATORIA", "las boleras mallorquinas.", []),
    51458: ("¡Argentina! ¡Argentina!", "porque no me resuelvo a deciros adiós", []),
    50365: ("PROLOGO", None, [("ÍNDICE", "Gabriel D’Anunnzio")]),
    54934: ("A EMILIO", None, [("ÍNDICE", "Certámenes y Exposiciones")]),
    22899: ("Aquella tarde, el viejo y venerado maestro", None, []),
    13507: ("UNA ESTACION DE AMOR", None, []),
    65689: ("No éramos sino tres amigos", None, []),
    56451: ("PRÓLOGO", "la viña de oro de las estrellas.", []),
    62952: ("INTRODUCCIÓN", None, []),
    62785: ("Al Dr. Genaro Sisto", None, [("ÍNDICE", "XXIII Epílogo")]),
    60634: ("Nací á la política, al amor y al éxito", None, []),
    64188: (("Advertencia de la 11.ª edición", 1), None, [("ÍNDICE", "CONCLUSIONES SINTÉTICAS")]),
    64974: (("LA MORAL DE LOS IDEALISTAS", 2), "de los pensadores.", []),
}

START = re.compile(r"^\*\*\* ?START OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.MULTILINE)
END = re.compile(r"^\*\*\* ?END OF (?:THE|THIS) PROJECT GUTENBERG.*$", re.MULTILINE)
# Lines of the licence and the trademark: every line of the boilerplate between the
# markers has one of them, while Gutenberg the printer stays in the texts (Larra, Galdós)
LICENCE = re.compile(r"project gutenberg|gutenberg\.org|gutenberg-tm", re.IGNORECASE)
CREDITS = re.compile(
    r"produced by|prepared by|proofread|pgdp|transcriber|transcriptor|internet archive|"
    r"hathitrust|images (?:generously|of the)|this (?:file|e-?book) was",
    re.IGNORECASE,
)
# Markup of the transcriptions: images (a caption left open ends with its paragraph),
# drop caps given as images, footnotes and their marks, HTML tags, italics, bold, headings
# and stage directions (also over several lines of a paragraph), superscripts and
# subscripts, asterisms,
# frames of tables, the brackets of verse blocks, alignment labels, numbers of stanzas and
# the headings of the removed notes
IMAGE = re.compile(
    r"\[(?:Ilustración|Illustration|imagen)\b(?:[^\]\n]|\n(?![ \t]*\n))*(?:\]|(?=\n[ \t]*\n|\Z))"
    r"|\[(?:PDF|\*\*[^\]\n]*)\]",
    re.IGNORECASE,
)
DROP_CAP = re.compile(r"\[imagen: ([A-ZÁÉÍÓÚÑ])\](?=[a-záéíóúñ])")
FOOTNOTE = re.compile(
    r"\s*(?:\[(?:\d{1,3}\]|\*\]|[A-Z]\]|Footnote \d+:|Nota [A-Z\d])|#Nota a pie de página:#)"
)
NOTE_MARK = re.compile(r"\[(?:\d{1,3}|\*|[A-Z])\]")
TAGS = re.compile(r"</?(?:i|b|sc|small)/?>")


def _delimited(mark: str) -> re.Pattern[str]:
    """Text between a pair of marks within a paragraph"""
    span = rf"(?:[^{mark}\n]|\n(?![ \t]*\n))+?"
    return re.compile(
        rf"(?<![\w{mark}]){mark}(?=[^\s{mark}])({span})(?<=[^\s{mark}]){mark}(?![\w{mark}])"
    )


DELIMITED = [_delimited(mark) for mark in "_=#~"]
SUPERSCRIPT = re.compile(r"\^\{([^}\n]*)\}|\^(?=\w)")
SUBSCRIPT = re.compile(r"(?<=[A-Za-z])_\{(\d{1,2})\}")
LINES = re.compile(
    r"^[ \t]*(?:(?:[*·][ \t]*){3,}|\+[-=+]+\+|/\*(?:\[\d+\])?|\*/|RIGHT|\d{1,4}\.?|NOTAS?:?|Notas?:?)[ \t]*$",
    re.MULTILINE,
)


def fetch(number: int, cache: Path) -> str:
    """Text of a book of Project Gutenberg, downloaded once into the cache"""
    path = cache / f"pg{number}.txt"
    if not path.is_file():
        request = urllib.request.Request(URL.format(number=number), headers={"User-Agent": "esTS"})
        with urllib.request.urlopen(request, timeout=60) as response:
            path.write_bytes(response.read())
        time.sleep(DELAY)
    return path.read_text(encoding="utf-8-sig")


def extract(raw: str) -> str:
    """Text of a book between the markers, without the lines of Project Gutenberg and credits"""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    start, end = START.search(text), END.search(text)
    if not start or not end:
        raise ValueError("The markers of Project Gutenberg are not found")
    text = text[start.end() : end.start()]
    lines = [line.rstrip() for line in text.split("\n") if not LICENCE.search(line)]
    paragraphs = re.split(r"\n\s*\n", "\n".join(lines).strip())
    while paragraphs and CREDITS.search(paragraphs[0]):
        paragraphs.pop(0)
    return "\n\n".join(paragraphs) + "\n"


def _line(lines: list[str], marker: Marker, number: int) -> int:
    """Index of the line with the marker: the only one, or the given one of those with it"""
    substring, occurrence = marker if isinstance(marker, tuple) else (marker, 0)
    found = [index for index, line in enumerate(lines) if substring in line]
    if occurrence:
        if len(found) < occurrence:
            raise ValueError(f"{number}: {substring!r} is found in {len(found)} lines only")
        return found[occurrence - 1]
    if len(found) != 1:
        raise ValueError(f"{number}: {substring!r} is found in {len(found)} lines instead of one")
    return found[0]


def cut(text: str, number: int) -> str:
    """Text of the author: from the first to the last marked line, without the cut blocks"""
    first, last, cuts = BOUNDS.get(number, (None, None, []))
    lines = text.split("\n")
    drop = [False] * len(lines)
    for start, end in cuts:
        for index in range(_line(lines, start, number), _line(lines, end, number) + 1):
            drop[index] = True
    begin = _line(lines, first, number) if first else 0
    stop = _line(lines, last, number) + 1 if last else len(lines)
    return "\n".join(
        line for index, line in enumerate(lines[begin:stop], begin) if not drop[index]
    )


def _balance(paragraph: str) -> str:
    """Paragraph without a bracket whose pair was cut off with the markup"""
    if "[" not in paragraph:
        return paragraph.replace("]", "")
    if "]" not in paragraph:
        return paragraph.replace("[", "")
    return paragraph


def tidy(text: str) -> str:
    """Text without the markup of the transcription, footnotes and stray blank lines"""
    text = DROP_CAP.sub(r"\1", text)
    text = IMAGE.sub("", text)
    paragraphs = re.split(r"\n[ \t]*\n", text)
    text = "\n\n".join(_balance(p) for p in paragraphs if not FOOTNOTE.match(p))
    text = NOTE_MARK.sub("", text)
    text = TAGS.sub("", text)
    text = SUBSCRIPT.sub(r"\1", text)
    for pattern in DELIMITED:
        text = pattern.sub(r"\1", text)
    text = SUPERSCRIPT.sub(r"\1", text)
    text = LINES.sub("", text)
    for mark in "_=~":
        text = text.replace(mark, "")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def clean(raw: str, number: int) -> str:
    """Text of the author from a book of Project Gutenberg"""
    return tidy(cut(extract(raw), number))


def main(cache: Path, output: Path) -> None:
    cache.mkdir(parents=True, exist_ok=True)
    files: dict[str, bytes] = {}
    rows = []
    for numbers, genre, key, title, year_from, year_to, country in WORKS:
        text = (
            "\n\n".join(clean(fetch(number, cache), number).strip() for number in numbers) + "\n"
        )
        name = f"{genre}/{key}/{numbers[0]}.txt"
        files[f"{ROOT}/{name}"] = text.encode("utf-8")
        gutenberg = "+".join(str(number) for number in numbers)
        order = (GENRES.index(genre), key, year_from, numbers[0])
        rows.append(
            (
                order,
                f"{name}\t{genre}\t{AUTHORS[key]}\t{title}\t{year_from}\t{year_to}\t{country}\t{gutenberg}",
            )
        )
    header = "file\tgenre\tauthor\ttitle\tyear_from\tyear_to\tcountry\tgutenberg"
    lines = [header] + [row for _, row in sorted(rows)]
    files[f"{ROOT}/metadata.tsv"] = ("\n".join(lines) + "\n").encode("utf-8")
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{ROOT}.tar.xz"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:xz", format=tarfile.PAX_FORMAT) as tar:
        for member in sorted(files):
            data = files[member]
            info = tarfile.TarInfo(member)
            info.size, info.mtime, info.mode = len(data), 0, 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    archive.write_bytes(buffer.getvalue())
    size = sum(len(data) for data in files.values())
    print(
        f"{archive}: {len(WORKS)} works, {size / 1e6:.1f} MB of text, {archive.stat().st_size / 1e6:.1f} MB"
    )
    print("sha256", sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
