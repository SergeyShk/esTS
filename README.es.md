<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/esTS/master/docs/img/ests.png" alt="esTS" width="340">
</p>

<h1 align="center">esTS</h1>

<p align="center">
  <i>¿Cómo esTáS, texto?</i>
</p>

<p align="center">
  <b>Spanish Texts Statistics</b> - biblioteca para extraer estadísticas de textos en español
</p>

<p align="center">
  <a href="https://sergeyshk.github.io/esTS/es/">Documentación</a> ·
  <a href="https://pypi.org/project/pyests/">PyPI</a> ·
  <a href="https://github.com/SergeyShk/esTS/blob/master/README.md">English</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/pyests/"><img src="https://img.shields.io/pypi/v/pyests?logo=pypi&logoColor=FFE873" alt="Version"></a>
  <a href="https://pypi.org/project/pyests/"><img src="https://img.shields.io/pypi/pyversions/pyests.svg?logo=python&logoColor=FFE873" alt="Supported Python versions"></a>
  <a href="https://github.com/SergeyShk/esTS/actions/workflows/ci.yml"><img src="https://github.com/SergeyShk/esTS/actions/workflows/ci.yml/badge.svg" alt="Build"></a>
  <a href="https://github.com/astral-sh/ruff"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json" alt="Ruff"></a>
  <a href="https://github.com/SergeyShk/esTS/blob/master/LICENSE.txt"><img src="https://img.shields.io/github/license/sergeyshk/esTS.svg" alt="License"></a>
  <a href="https://doi.org/10.5281/zenodo.22924655"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.22924655.svg" alt="DOI"></a>
</p>

---

**esTS** calcula para textos en español lo que normalmente exige juntar varias herramientas sueltas: estadísticas básicas, legibilidad, diversidad léxica, complejidad léxica, estilo, fonoestadística, morfología, sintaxis y cohesión, con fórmulas publicadas y con los coeficientes y las escalas de sus autores, y con las categorías y los rasgos de Universal Dependencies.

La biblioteca trabaja tanto con cadenas como con objetos `Doc` de [spaCy](https://github.com/explosion/spaCy): las oraciones, las palabras y los N-gramas de caracteres se extraen por reglas, las sílabas y el acento se deducen de la ortografía, y solo las estadísticas morfológicas, las sintácticas, las de cohesión y las de complejidad léxica, los sustantivos deverbales de las métricas de estilo, el perfil de las palabras funcionales y la comparación de corpus necesitan un modelo entrenado.

* **[Extracción de objetos](https://sergeyshk.github.io/esTS/es/extractors/sentences/)** - tokenizadores configurables de oraciones, palabras y N-gramas de caracteres que conocen los signos de apertura, la raya de diálogo y las abreviaturas del español
* **[Sílabas y acento](https://sergeyshk.github.io/esTS/es/syllables/)** - silabificación por reglas y sílaba tónica deducida de la escritura, sin diccionario
* **[Estadísticas básicas](https://sergeyshk.github.io/esTS/es/stats/basic_stats/)** - recuentos de oraciones, palabras, letras, sílabas y signos de puntuación por tipo, con distribuciones y proporciones normalizadas
* **[Métricas de legibilidad](https://sergeyshk.github.io/esTS/es/stats/readability_stats/)** - Fernández Huerta, Szigriszt-Pazos con la escala INFLESZ, Gutiérrez de Polini, Crawford, Legibilidad µ, SOL, LIX y RIX, con grado de consenso, etapas escolares de España y tiempo de lectura
* **[Métricas de diversidad léxica](https://sergeyshk.github.io/esTS/es/stats/diversity_stats/)** - TTR y sus variantes, MATTR, MSTTR, MTLD, HD-D, índices de Simpson y de Yule, entropía, leyes de Zipf y de Heaps
* **[Estadísticas morfológicas](https://sergeyshk.github.io/esTS/es/stats/morph_stats/)** - categorías gramaticales y quince rasgos morfológicos de Universal Dependencies, con los marcadores del español: los modos, las formas no personales, `ser` frente a `estar`, los adverbios en `-mente`
* **[Medidas de corpus](https://sergeyshk.github.io/esTS/es/corpus/keyness/)** - palabras clave frente a un corpus de referencia, colocaciones, la dispersión de una palabra por las partes de un texto, una concordancia KWIC y la estilometría de autoría: la Delta de Burrows con sus variantes, Zeta, la curva de Mendenhall, el perfil de las palabras funcionales; la comparación de dos corpus por 132 rasgos de un texto con tamaños del efecto
* **[Visualizaciones](https://sergeyshk.github.io/esTS/es/visualizers/zipf/)** - ley de Zipf, huella literaria, árbol de palabras, dispersión léxica y palabras clave, red de colocaciones, dendrograma, PCA y MDS por la Delta, crecimiento del vocabulario, longitudes de las oraciones y el resaltado del texto por los fragmentos que cuentan las estadísticas: oraciones largas, pasivas, cadenas de de, clichés
* **[Conjuntos de datos](https://sergeyshk.github.io/esTS/es/datasets/spanishliterature/)** - literatura en español de dominio público: 150 obras de 33 autores de España, Hispanoamérica y Filipinas en prosa, poesía, teatro y ensayo, con el género, los años y el país; 4259 sonetos de los siglos XV-XX con el patrón métrico y la rima de cada verso; un diccionario de frecuencias de 83 785 lemas según Google Books Ngram con ipm, rango y dispersión
* **[Componentes de spaCy](https://sergeyshk.github.io/esTS/es/components/)** - cada clase de estadísticas como componente de un pipeline, con las estadísticas puestas en el `Doc` en una sola pasada
* **[Estadísticas de cohesión](https://sergeyshk.github.io/esTS/es/stats/cohesion_stats/)** - la repetición de sustantivos, argumentos y palabras con contenido entre oraciones, la información dada y la cohesión temporal a la manera de Coh-Metrix, con la densidad de 255 marcadores del discurso españoles
* **[Estadísticas de complejidad léxica](https://sergeyshk.github.io/esTS/es/stats/lexical_stats/)** - cuán raras son las palabras de un texto en la lengua: la frecuencia, el rango y la dispersión de los lemas según un diccionario de Google Books Ngram, las bandas de frecuencia del top-1000 al 10000, la sorpresa, la perplejidad y la densidad léxica
* **[Métricas de estilo](https://sergeyshk.github.io/esTS/es/stats/style_stats/)** - los indicadores SEO de Advego y Text.ru (náusea, contenido de agua, índice de spam, naturalidad según Zipf, densidad de palabras clave) y los marcadores del estilo burocrático según las guías españolas de lenguaje claro: sustantivos deverbales, locuciones prepositivas, expresiones parentéticas y clichés
* **[Fonoestadística](https://sergeyshk.github.io/esTS/es/stats/phon_stats/)** - proporciones de las clases de sonidos, grupos consonánticos, hiatos, sílabas abiertas, dureza e índices de aliteración y de asonancia, sobre los sonidos de una transcripción por reglas
* **[Estadísticas del verso](https://sergeyshk.github.io/esTS/es/stats/verse_stats/)** - la escansión del verso español por su metro silábico: las sílabas métricas con la sinalefa y la ley del acento final, el metro de un poema y los hemistiquios del alejandrino, el perfil acentual y los tipos del endecasílabo
* **[Estadísticas sintácticas](https://sergeyshk.github.io/esTS/es/stats/syntax_stats/)** - el árbol de dependencias por distancias, profundidad, cláusulas y coordinación, con las construcciones del estilo administrativo: la pasiva con `ser` y con `se`, las cláusulas de participio y de gerundio, las cadenas de `de`, los predicados escindidos

La rima llega en la 0.4.

## Instalación

Se requiere Python 3.11 o superior.

```bash
pip install pyests
```

O con [uv](https://docs.astral.sh/uv/):

```bash
uv add pyests
```

El distribuible en PyPI se llama `pyests` y el paquete que instala es `ests`. Las estadísticas básicas, la legibilidad, la diversidad léxica y la fonoestadística no necesitan ningún modelo de spaCy; las estadísticas morfológicas, las sintácticas, las de cohesión y las de complejidad léxica de una cadena sí, igual que los sustantivos deverbales de las métricas de estilo, el perfil de las palabras funcionales, los rasgos de un texto y la comparación de corpus, y analizar un texto por su cuenta para pasar el `Doc` en lugar de una cadena:

```bash
python -m spacy download es_core_news_sm
```

Las estadísticas según el diccionario de frecuencias lo necesitan descargado una vez con `FreqDict().download()`. Los conjuntos de datos van al directorio `ests_data` junto al paquete instalado; otro se pasa en `data_dir` o se define en la variable de entorno `ESTS_DATA_DIR` antes de importar el paquete.

## Primeros pasos

```python
>>> from ests import BasicStats, DiversityStats, ReadabilityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"

>>> BasicStats(text).get_stats()
{'c_letters': {1: 1, 2: 1, 3: 1, 4: 1, 6: 1, 8: 4, 12: 1},
 'c_syllables': {1: 4, 2: 1, 3: 4, 5: 1},
 'n_sents': 1,
 'n_words': 10,
 'n_unique_words': 8,
 'n_long_words': 5,
 'n_complex_words': 5,
 'n_simple_words': 5,
 'n_monosyllable_words': 4,
 'n_polysyllable_words': 6,
 'n_chars': 71,
 'n_letters': 60,
 'n_spaces': 9,
 'n_syllables': 23,
 'n_punctuations': 2,
 'c_punctuations': {'comma': 1, 'period': 0, 'question': 0, 'exclamation': 0,
                    'ellipsis': 0, 'colon': 1, 'semicolon': 0, 'dash': 0,
                    'hyphen': 0, 'angle_quotes': 0, 'straight_quotes': 0,
                    'parentheses': 0, 'other': 0}}

>>> ReadabilityStats(text).flesch_reading_easy
53.545000000000016

>>> DiversityStats(text).ttr
0.8
```

## Funcionalidad

### Extracción de objetos

La biblioteca permite construir herramientas propias de extracción de oraciones, palabras y N-gramas de caracteres, que luego sirven para calcular las estadísticas. El segmentador de oraciones conoce los signos de apertura, la raya de una línea de diálogo con la remarca del narrador, y las abreviaturas e iniciales del español; el tokenizador de palabras mantiene enteros los clíticos, los ordinales y los números escritos a la española, y los lemas vienen de [simplemma](https://github.com/adbar/simplemma), que no necesita modelo.

```python
>>> from ests import CharNgramsExtractor, SentsExtractor, WordsExtractor

>>> SentsExtractor().extract("—¿Vienes? —preguntó María. ¡Claro que sí!")
('—¿Vienes? —preguntó María.', '¡Claro que sí!')

>>> we = WordsExtractor(use_lexemes=True, stopwords=["de", "y"], filter_nums=True, ngram_range=(1, 2))
>>> we.extract("Hay 3 clases de mentiras y estadísticas")
('haber', 'clase', 'mentira', 'estadística', 'haber_clase', 'clase_mentira', 'mentira_estadística')

>>> CharNgramsExtractor(n=3, lowercase=True).extract("estadísticas")[:5]
('est', 'sta', 'tad', 'adí', 'dís')
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/extractors/sentences/).

<details>
<summary><b>Sílabas y acento</b></summary>

<br>

La ortografía española codifica tanto los límites silábicos como el acento, así que la biblioteca no necesita diccionario: los diptongos, los hiatos y los triptongos, la `u` muda de `qu` y `gu`, la `y` vocálica, la `h` dentro de un diptongo y los grupos consonánticos dan las sílabas; la tilde, o la terminación de la palabra cuando no la hay, da la sílaba tónica. Los adverbios en `-mente` y los compuestos con guion llevan dos acentos.

```python
>>> from ests.syllables import stress_type, syllabify, word_stress, word_stresses

>>> syllabify("murciélago")
['mur', 'cié', 'la', 'go']

>>> syllabify("averiguáis")
['a', 've', 'ri', 'guáis']

>>> word_stress("construir"), stress_type("construir")
(1, 'aguda')

>>> word_stresses("fácilmente")
[0, 2]
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/syllables/).

</details>

<details>
<summary><b>Estadísticas básicas</b></summary>

<br>

La biblioteca permite extraer de un texto las siguientes estadísticas:

*   el número de oraciones
*   el número de palabras
*   el número de palabras únicas
*   el número de palabras largas
*   el número de palabras complejas
*   el número de palabras simples
*   el número de palabras monosílabas
*   el número de palabras polisílabas
*   el número de caracteres
*   el número de letras
*   el número de espacios
*   el número de sílabas
*   el número de signos de puntuación y su distribución por tipo
*   la distribución de las palabras por número de letras
*   la distribución de las palabras por número de sílabas

Una palabra compleja tiene tres o más sílabas y una palabra larga siete o más letras, como las cuentan las fórmulas españolas de legibilidad. Cualquier estadística puede mostrarse en forma legible:

```python
>>> from ests import BasicStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> BasicStats(text).print_stats()
     Statistic      |  Value
------------------------------
Sentences           |    1
Words               |    10
Unique words        |    8
Long words          |    5
Complex words       |    5
Simple words        |    5
Monosyllabic words  |    4
Polysyllabic words  |    6
Characters          |    71
Letters             |    60
Spaces              |    9
Syllables           |    23
Punctuation marks   |    2
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/basic_stats/).

</details>

<details>
<summary><b>Métricas de legibilidad</b></summary>

<br>

La biblioteca permite calcular las siguientes métricas de legibilidad:

*   facilidad de lectura de Flesch con los coeficientes de Szigriszt-Pazos o de Fernández Huerta
*   fórmula de comprensibilidad de Gutiérrez de Polini
*   grado de Crawford
*   Legibilidad µ
*   grado SOL, el índice SMOG convertido al español
*   índice de legibilidad LIX
*   índice de legibilidad RIX

Sobre las fórmulas trabaja una capa de interpretación: el nivel de una escala para la facilidad de lectura y para la Legibilidad µ, un grado de consenso como mediana de las fórmulas de grado, la etapa escolar y la edad del lector en España, y el tiempo de lectura según las normas de los lectores hispanohablantes.

Los coeficientes de la facilidad de lectura se eligen con el argumento `preset`: por defecto la *fórmula de perspicuidad* de Szigriszt-Pazos con la escala INFLESZ validada con textos para pacientes (`general`); los coeficientes de Fernández Huerta con los niveles de su autor están disponibles como `classic`.

```python
>>> from pprint import pprint
>>> from ests import ReadabilityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> rs = ReadabilityStats(text)

>>> pprint(rs.get_stats(), sort_dicts=False)
{'flesch_reading_easy': 53.545000000000016,
 'gutierrez_polini_index': 33.5,
 'crawford_grade': 5.812999999999999,
 'mu_index': 50.943396226415096,
 'sol_grade': 9.258359866374562,
 'lix': 60.0,
 'rix': 5.0,
 'consensus_grade': 9.0,
 'reading_time': 0.03597122302158273}

>>> rs.print_stats()
                   Metric                    |  Value
-------------------------------------------------------
Flesch reading ease (Szigriszt-Pazos)        |  53.55
Gutiérrez de Polini comprehensibility        |  33.50
Crawford grade                               |   5.81
Legibilidad µ                                |  50.94
SOL grade (SMOG for Spanish)                 |   9.26
LIX readability index                        |  60.00
RIX readability index                        |   5.00
Consensus grade                              |   9.00
Reading time (min)                           |   0.04

>>> rs.describe_level()
'algo difícil'

>>> rs.describe_grade()
'ESO (12-16 years)'
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/readability_stats/).

</details>

<details>
<summary><b>Métricas de diversidad léxica</b></summary>

<br>

La biblioteca permite calcular 32 métricas de diversidad léxica, entre ellas:

*   Type-Token Ratio y sus variantes: RTTR, CTTR, Herdan, Summer, Maas, Dugast
*   Moving Average Type-Token Ratio y Mean Segmental Type-Token Ratio
*   Measure of Textual Lexical Diversity y sus variantes de ventana móvil MA-MTLD y MTLD-W
*   Hypergeometric Distribution D
*   índice de Simpson, su recíproco y el índice de Gini-Simpson
*   el índice de hápax (R de Honoré) y las medidas de Yule, Herdan, Sichel, Michéa, Brunet, Dugast y Baayen
*   entropía de Shannon, equitatividad y perplejidad
*   la pendiente de la ley de Zipf, el ajuste de Zipf-Mandelbrot y el exponente de la ley de Heaps

Cualquier métrica puede calcularse por ventanas de igual longitud, la forma estándar de comparar textos de distinta extensión: la media entre ventanas viene con su intervalo de confianza.

```python
>>> from ests import DiversityStats

>>> text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
>>> ds = DiversityStats(text)

>>> ds.ttr, ds.mtld, ds.yule_k
(0.8, 14.000000000000004, 600.0)

>>> ds.frequency_spectrum
{1: 7, 3: 1}

>>> DiversityStats("La legibilidad de un texto depende de la longitud de sus oraciones y de sus "
...                "palabras. Las fórmulas clásicas miden esas dos magnitudes y las combinan en "
...                "un solo número. Ninguna de ellas mide la comprensión: miden la superficie "
...                "del texto.").windowed("ttr", window_len=10)
WindowStats(mean=0.875, std=0.1258305739211792, lower=0.6747754774664074, upper=1.0752245225335926, n_windows=4)
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/diversity_stats/).

</details>

<details>
<summary><b>Estadísticas morfológicas</b></summary>

<br>

La biblioteca anota el texto con las categorías gramaticales y los rasgos morfológicos de Universal Dependencies, tal como los dan los modelos españoles de spaCy, y los cuenta:

*   la categoría gramatical y quince rasgos: caso, definitud, grado, género, modo, tipo de numeral, número, persona, polaridad, cortesía, posesivo, tipo de pronombre, reflexivo, tiempo verbal y forma verbal
*   la distribución de las palabras por los valores de cualquier rasgo y el análisis del texto palabra por palabra
*   los marcadores del español: los modos entre las formas personales, las formas no personales, `ser` frente a `estar`, los adverbios en `-mente`

```python
>>> from ests import MorphStats

>>> ms = MorphStats("Si tuviera tiempo, leería el libro que me recomendaste ayer")

>>> ms.get_stats("mood", "tense", filter_none=True)
{'mood': {'Sub': 1, 'Cnd': 1, 'Ind': 1}, 'tense': {'Imp': 1, 'Pres': 1}}

>>> ms.tags[1]
'Mood=Sub|Number=Sing|Person=3|Tense=Imp|VerbForm=Fin'

>>> ms.explain_text("pos", "mood", filter_none=True)[1]
('tuviera', {'pos': 'VERB', 'mood': 'Sub'})

>>> MorphStats("Ella es alta pero hoy está cansada y habla lentamente").get_markers()["p_ser"]
0.5
```

Las estadísticas necesitan un modelo de spaCy: el texto se analiza con `es_core_news_sm`, y en `nlp` puede indicarse cualquier otro pipeline.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/morph_stats/).

</details>

<details>
<summary><b>Estadísticas sintácticas</b></summary>

<br>

La biblioteca mide el árbol de dependencias de Universal Dependencies y las construcciones que advierten las guías españolas de lenguaje claro:

*   la complejidad del árbol: distancias de dependencia, profundidad, hojas y subárboles, valencia de los verbos personales, cadenas de coordinación, cláusulas y subordinadas, modificadores por sustantivo
*   las construcciones: la pasiva con `ser` y con `se`, las cláusulas de participio y de gerundio, las cadenas de `de`, los predicados escindidos, el `se` impersonal, las palabras de negación, la razón entre sustantivos y verbos

```python
>>> from ests import SyntaxStats

>>> text = ("La revisión de las cuentas fue realizada por el comité. "
...         "Se llevó a cabo la reforma sin que nadie hiciera mención de los problemas.")
>>> ss = SyntaxStats(text)

>>> ss.n_sents, ss.n_words
(2, 24)

>>> ss.p_passive, ss.noun_verb_ratio
(0.6666666666666666, 2.3333333333333335)

>>> ss.split_predicates
('llevó cabo', 'hiciera mención')

>>> round(ss.mean_dependency_distance, 2)
2.05
```

Las estadísticas necesitan el análisis sintáctico: el texto se analiza con `es_core_news_sm`, y en `nlp` puede indicarse cualquier otro pipeline.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/syntax_stats/).

</details>

<details>
<summary><b>Estadísticas de cohesión</b></summary>

<br>

La biblioteca mide la cohesión referencial a la manera de Coh-Metrix y de su adaptación española Coh-Metrix-Esp:

*   la repetición de sustantivos, de argumentos y de palabras con contenido entre oraciones contiguas y entre todos los pares de oraciones, binaria y proporcional
*   la información dada: pronombres, demostrativos y palabras con contenido cuyo lema ya se había usado
*   la cohesión temporal: la repetición del tiempo y del modo de los verbos de oraciones contiguas
*   la densidad de 255 marcadores del discurso españoles por clase - causales, adversativos, concesivos, temporales, aditivos, condicionales, reformulativos - y por tipo

```python
>>> from ests import CohesionStats

>>> text = ("El informe fue aprobado por la comisión. Sin embargo, el informe no resuelve el problema. "
...         "Por lo tanto, la comisión aplazó la decisión.")
>>> cs = CohesionStats(text)

>>> cs.n_sents, cs.n_words
(3, 23)

>>> cs.noun_overlap_adjacent, round(cs.p_given, 3)
(0.5, 0.167)

>>> cs.c_connectors
{'por lo tanto': 1, 'sin embargo': 1}

>>> round(cs.connectors, 2), round(cs.connectors_causal, 2)
(86.96, 43.48)
```

Las estadísticas necesitan la anotación: el texto se analiza con `es_core_news_sm`, y en `nlp` puede indicarse cualquier otro pipeline.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/cohesion_stats/).

</details>

<details>
<summary><b>Estadísticas de complejidad léxica</b></summary>

<br>

Cuán raras son las palabras de un texto en la lengua, a la manera de TAALES: la frecuencia media, el rango y la dispersión de los lemas según el diccionario de frecuencias de Google Books Ngram, las proporciones de palabras de las bandas de frecuencia top-1000, 2000, 5000 y 10000, la sorpresa y la perplejidad según el modelo de unigramas del diccionario, la densidad léxica. Las bandas y la densidad funcionan sin más; las estadísticas según el diccionario lo necesitan descargado una vez.

```python
>>> from ests import LexicalStats
>>> from ests.datasets import FreqDict

>>> FreqDict().download()
>>> ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
>>> ls.coverage, ls.p_top1000, round(ls.surprisal, 2)
(0.8571428571428571, 0.42857142857142855, 13.71)
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/lexical_stats/).

</details>

<details>
<summary><b>Métricas de estilo</b></summary>

<br>

Los indicadores SEO de Advego y Text.ru - náusea, contenido de agua, índice de spam, naturalidad según la ley de Zipf, densidad de palabras clave - y los marcadores del estilo burocrático contra los que advierten las guías españolas de lenguaje claro: los sustantivos deverbales, las locuciones prepositivas del estilo administrativo, las expresiones parentéticas y los clichés, cuyos verbos se encuentran en sus formas (`se procedió a`, `ha dado cumplimiento`).

```python
>>> from ests import StyleStats

>>> ss = StyleStats("Se procedió a la revisión del expediente en el marco del plan a la mayor brevedad.")
>>> ss.compound_prepositions, ss.cliches, ss.verbal_nouns
(6.25, 12.5, 20.0)
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/style_stats/).

</details>

<details>
<summary><b>Fonoestadística</b></summary>

<br>

Las proporciones de las clases de sonidos, los grupos consonánticos, los hiatos, las sílabas abiertas, la dureza y los índices de aliteración y de asonancia, contados sobre los sonidos de una transcripción por reglas y no sobre las letras: la `h` y la `u` de `que` son mudas, `ll`, `ch` y `rr` son un sonido, la `x` son dos.

```python
>>> from ests import PhonStats

>>> ps = PhonStats("Los suspiros se escapan de su boca de fresa")
>>> round(ps.p_voiceless, 3), round(ps.hardness, 3), ps.sounds[-1]
(0.371, 0.684, ('f', 'r', 'e', 's', 'a'))
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/phon_stats/).

</details>

<details>
<summary><b>Estadísticas del verso</b></summary>

<br>

La escansión del verso español por su metro silábico: las sílabas métricas de un verso con la sinalefa y la ley del acento final, un verso ajustado al metro de su poema por un hiato, una diéresis o una sinéresis, el alejandrino leído por hemistiquios; el metro, el perfil acentual, los tipos del endecasílabo y las terminaciones de los versos. No hacen falta ni modelo ni diccionario.

```python
>>> from ests import VerseStats

>>> text = """Cuando me paro a contemplar mi estado
... y a ver los pasos por do me han traído,
... hallo, según por do anduve perdido,
... que a mayor mal pudiera haber llegado."""
>>> vs = VerseStats(text)
>>> vs.meter, vs.patterns[0], vs.c_rhythms
('endecasílabo', '---+---+-+-', {'4-8-10': 2, '4-7-10': 1, '3-6-10': 1})
>>> vs.syllables[0]
('cuan', 'do', 'me', 'pa', 'ro‿a', 'con', 'tem', 'plar', 'mi‿es', 'ta', 'do')
```

Más en la [documentación](https://sergeyshk.github.io/esTS/es/stats/verse_stats/).

</details>

<details>
<summary><b>Componentes de spaCy</b></summary>

<br>

Cada clase de estadísticas es también un componente de un pipeline, de modo que el texto se anota y se mide en una sola pasada y las estadísticas viajan con el `Doc`:

```python
>>> import ests
>>> import spacy

>>> nlp = spacy.load("es_core_news_sm")
>>> for factory in ("basic", "morph", "syntax"):
...     _ = nlp.add_pipe(f"ests_{factory}", name=factory, last=True)

>>> nlp.pipe_names[-3:]
['basic', 'morph', 'syntax']

>>> doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
>>> doc._.basic.n_words, doc._.morph.pos[:2], doc._.syntax.tree_depth
(12, ('DET', 'NOUN'), 2.0)
```

Las fábricas son `ests_basic`, `ests_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style` y `ests_phon`; el nombre del paso del pipeline es libre y es como se llama la extensión.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/components/).

</details>

<details>
<summary><b>Medidas de corpus</b></summary>

<br>

La biblioteca compara corpus y describe el uso de una palabra con las medidas de la lingüística de corpus:

*   palabras clave de un corpus objetivo frente a uno de referencia o frente al diccionario de frecuencias de Google Books Ngram: la razón de verosimilitud con su valor p, Log Ratio, ji cuadrado, %DIFF, BIC, ELL y la razón de momios
*   colocaciones por logDice, MI, MI³, t-score, Dice, razón de verosimilitud, NPMI y sensibilidad mínima, contrastadas con NLTK
*   la dispersión de una palabra por las partes de un texto: la DP de Gries, la DP normalizada, la D de Juilland, la D2 de Carroll, la S de Rosengren y la divergencia de Kullback-Leibler
*   una concordancia KWIC por forma o por lema
*   estilometría: las distancias entre textos por la Delta de Burrows y sus variantes, con la atribución de un texto a autores de referencia, los marcadores de palabras preferidas y evitadas por Zeta, el ji cuadrado de Kilgarriff, la curva de Mendenhall y el perfil de las palabras funcionales
*   la comparación de dos corpus por 132 rasgos de un texto en ventanas de un tamaño parecido: la delta de Cliff, la d de Cohen y el AUC de cada rasgo, la prueba de Mann-Whitney con la corrección de Holm y un intervalo bootstrap de la diferencia de las medianas que remuestrea textos enteros

```python
>>> from ests import WordsExtractor
>>> from ests.corpus import collocations, keyness, kwic, zeta

>>> we = WordsExtractor(use_lexemes=True, lowercase=True)
>>> target = we.extract("El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
...                     "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros.")
>>> reference = we.extract("El perro estaba en el suelo y dormía. Después el perro comió y volvió a dormir. "
...                        "Mañana el perro saldrá a pasear.")

>>> [(k.word, round(k.g2, 2)) for k in keyness(target, reference, top_n=2)]
[('gato', 2.8), ('pájaro', 2.8)]

>>> [(c.left, c.right, round(c.score, 1)) for c in collocations(target, window=2, top_n=2)]
[('en', 'ventana', 13.0), ('estar', 'en', 12.7)]

>>> [line.keyword for line in kwic("Los gatos juegan y el gato duerme.", "gato", by_lemma=True)]
['gatos', 'gato']

>>> scores = zeta(target, reference, segment_size=10)
>>> [z.word for z in scores[:2]], [z.word for z in scores[-2:]]
(['gato', 'ventana'], ['dormir', 'perro'])
```

Las palabras se comparan tal cual, así que la caja, los lemas y las palabras vacías se eligen en la extracción.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/corpus/keyness/).

</details>

<details>
<summary><b>Conjuntos de datos</b></summary>

<br>

*   [spanish_literature](https://sergeyshk.github.io/esTS/es/datasets/spanishliterature/) - literatura en español de dominio público: 150 obras de 33 autores de España, Hispanoamérica y Filipinas, de Cervantes a los años veinte, en prosa, poesía, teatro y ensayo; 65 millones de caracteres
*   [spanish_sonnets](https://sergeyshk.github.io/esTS/es/datasets/spanishsonnets/) - sonetos en español del Diachronic Spanish Sonnet Corpus (DISCO) de dominio público: 4259 sonetos de 1167 autores de los siglos XV-XX, cada verso con su patrón métrico y la etiqueta de su rima, la anotación automática de DISCO (CC BY 4.0)
*   [freq_dict](https://sergeyshk.github.io/esTS/es/datasets/freqdict/) - un diccionario de frecuencias de 83 785 lemas del español a partir de los libros de Google Books Ngram de 1980-2019 (63 000 millones de palabras): ipm, rango y D de Juilland por años, número de libros y categoría gramatical (CC BY 3.0)

Los textos se recortan al texto del autor, sin portadas, notas de los transcriptores y de los editores, índices ni notas al pie, y llevan el género, el autor, el título, los años de la primera publicación y el país; los registros se pueden filtrar por cualquiera de ellos y por la longitud del texto.

```python
>>> from ests.datasets import SpanishLiterature

>>> sl = SpanishLiterature()
>>> sl.download()
>>> for record in sl.get_records(author="galdos", year_from=1880, year_to=1884):
...     print(record["title"], record["year_from"], len(record["text"]))
La desheredada 1881 820454
El amigo Manso 1882 521156
La de Bringas 1884 413730
Tormento 1884 477286
```

El archivo (19 MB) se descarga una vez con `download()` en el directorio de datos y se verifica con su suma de comprobación SHA-256; antes de la descarga `get_texts()` y `get_records()` levantan `DatasetNotFoundError` con una indicación.

Más en la [documentación](https://sergeyshk.github.io/esTS/es/datasets/spanishliterature/).

</details>

<details>
<summary><b>Visualizaciones</b></summary>

<br>

*   [Ley de Zipf](https://sergeyshk.github.io/esTS/es/visualizers/zipf/) con la curva teórica y el ajuste de Zipf-Mandelbrot
*   [Huella literaria](https://sergeyshk.github.io/esTS/es/visualizers/fingerprinting/) (Literature Fingerprinting)
*   [Árbol de palabras](https://sergeyshk.github.io/esTS/es/visualizers/word_tree/) (Word Tree)
*   [Gráficos de corpus](https://sergeyshk.github.io/esTS/es/visualizers/corpus/): dispersión léxica, un diagrama de palabras clave, una red de colocaciones
*   [Gráficos estilométricos](https://sergeyshk.github.io/esTS/es/visualizers/stylometry/): un dendrograma, las componentes principales y el escalamiento multidimensional por la Delta, las curvas de Mendenhall
*   [Crecimiento del vocabulario y espectro de frecuencias](https://sergeyshk.github.io/esTS/es/visualizers/vocabulary/), [longitudes de las oraciones](https://sergeyshk.github.io/esTS/es/visualizers/sentences/) con una media móvil

Los gráficos de matplotlib reciben los ejes `ax` y devuelven `Axes`, así que se pueden disponer en una misma figura; la red de colocaciones y el árbol de palabras son grafos de graphviz, cuyos ejecutables los dibujan. La Delta coseno separa tres novelas de Galdós de tres de Unamuno:

```python
import matplotlib.pyplot as plt
from ests import WordsExtractor
from ests.corpus import delta
from ests.datasets import SpanishLiterature
from ests.visualizers import dendrogram_plot, pca_plot

# seis novelas de Galdós y de Unamuno del corpus de literatura
titles = (
    "Marianela",
    "Misericordia",
    "Torquemada en la hoguera",
    "Niebla",
    "Abel Sánchez",
    "La tía Tula",
)
sl = SpanishLiterature()
sl.download()
novels = {
    record["title"]: record["text"]
    for author in ("galdos", "unamuno")
    for record in sl.get_records(author=author)
    if record["title"] in titles
}
we = WordsExtractor(lowercase=True)
corpus = {title: we.extract(novels[title]) for title in titles}
distances = delta(corpus, n_mfw=100, variant="cosine")

fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
dendrogram_plot(distances, ax=left)
pca_plot(corpus, n_mfw=100, ax=right)
```

<p align="center">
  <img src="https://raw.githubusercontent.com/SergeyShk/esTS/master/docs/img/stylometry.png" alt="Gráficos estilométricos" width="760">
</p>

Más en la [documentación](https://sergeyshk.github.io/esTS/es/visualizers/zipf/).

</details>

## Desarrollo

El proyecto usa [uv](https://docs.astral.sh/uv/) para gestionar las dependencias y [ruff](https://docs.astral.sh/ruff/) para el análisis y el formato del código.

```bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS

make deps        # crear el entorno e instalar las dependencias
make test        # ejecutar las pruebas y los ejemplos de los docstrings (doctest)
make lint        # ruff + mypy
```

Ejecute `make help` para ver la lista completa de comandos.

La documentación es bilingüe: las páginas en inglés son `docs/*.md` y las españolas `docs/*.es.md` junto a ellas ([mkdocs-static-i18n](https://github.com/ultrabug/mkdocs-static-i18n)); al editar una página, actualice las dos versiones.

La versión instalada está en `ests.__version__`. Todas las excepciones heredan de `ests.EstsError` y de una de las clases integradas (`SourceError`, `ParameterError` y `DataFileError` de `ValueError`, `SourceTypeError` de `TypeError`, `UnknownStatError` de `KeyError`, `DatasetNotFoundError` de `OSError`, `DownloadError` de `RuntimeError`), así que `except ValueError` sigue funcionando. La biblioteca no imprime nada por su cuenta: sus mensajes van al logger `ests` (`logging.getLogger("ests")`) y están en silencio por defecto.

Antes de enviar cambios, instale los hooks que ejecutan los linters al hacer commit y las pruebas al hacer push:

```bash
uv run pre-commit install
```

## Contribuir

Los informes de errores, las ideas y los pull requests son bienvenidos: las [issues](https://github.com/SergeyShk/esTS/issues) están abiertas. El flujo de trabajo, las comprobaciones previas a un pull request y la forma de presentar los cambios están descritos en [CONTRIBUTING.md](https://github.com/SergeyShk/esTS/blob/master/CONTRIBUTING.md); las normas de convivencia, en el [código de conducta](https://github.com/SergeyShk/esTS/blob/master/CODE_OF_CONDUCT.md).

<details>
<summary><b>Estructura del proyecto</b></summary>

<br>

*   **docs** - documentación del proyecto
*   **ests**:
    *   basic_stats.py - estadísticas básicas del texto
    *   cohesion_stats.py - estadísticas de cohesión
    *   lexical_stats.py - estadísticas de complejidad léxica
    *   components.py - componentes de un pipeline de spaCy
    *   corpus - medidas de la lingüística de corpus: palabras clave, colocaciones, dispersión, concordancia, estilometría, comparación de corpus
    *   datasets - conjuntos de datos: literatura en español, diccionario de frecuencias
    *   constants.py - constantes de la lengua española y de las métricas
    *   diversity_stats.py - métricas de diversidad léxica
    *   exceptions.py - excepciones de la biblioteca
    *   extractors.py - herramientas de extracción de objetos del texto
    *   morph_stats.py - estadísticas morfológicas
    *   readability_stats.py - métricas de legibilidad
    *   style_stats.py - métricas de estilo
    *   phon_stats.py - fonoestadística
    *   syntax_stats.py - estadísticas sintácticas
    *   verse_stats.py - estadísticas del verso
    *   syllables.py - silabificación y acento
    *   utils.py - herramientas auxiliares
    *   visualizers - gráficos: ley de Zipf, huella literaria, árbol de palabras, gráficos de corpus y estilométricos, crecimiento del vocabulario, longitudes de las oraciones, resaltado del texto
*   **scripts** - scripts que construyen los archivos de los conjuntos de datos
*   **tests** - pruebas que reproducen la estructura del paquete

</details>

## Autores

*   Sergey Shkarin (kouki.sergey@gmail.com)

## Licencia

[MIT](https://github.com/SergeyShk/esTS/blob/master/LICENSE.txt)

## Cómo citar

Si usa **esTS** en su investigación o en su software, cítelo con la siguiente entrada BibTeX. Las citas ayudan al desarrollo y al mantenimiento continuos de la biblioteca. Los mismos metadatos están en [CITATION.cff](https://github.com/SergeyShk/esTS/blob/master/CITATION.cff): GitHub los muestra bajo el botón «Cite this repository». El Concept DOI [10.5281/zenodo.22924655](https://doi.org/10.5281/zenodo.22924655) en Zenodo apunta a todas las versiones de la biblioteca; el DOI de una versión concreta está en la página de su publicación.

```bibtex
@software{esTS,
  author = {Sergey Shkarin},
  title = {{esTS, a library for statistics extraction from texts in Spanish}},
  year = 2026,
  doi = {10.5281/zenodo.22924655},
  url = {https://github.com/SergeyShk/esTS}
}
```
