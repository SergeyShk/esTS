# Fonoestadística

!!! info ""
    **ests.phon_stats.PhonStats**

## Descripción

Módulo para calcular la fonoestadística de un texto: las proporciones de las clases de sonidos, los grupos consonánticos, los hiatos, la variedad de la forma fónica de las palabras, las sílabas abiertas y los índices de aliteración y de asonancia, que dicen si las repeticiones de un sonido se agrupan en palabras vecinas. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy); no hace falta ningún modelo entrenado.

Las estadísticas se cuentan sobre los sonidos de la transcripción de las palabras ([`transcribe`](phon_stats_funcs.md#transcribe)), no sobre las letras: el español escribe algunos sonidos con dos letras (`ch`, `ll`, `rr`, `qu`), algunas letras sin sonido (`h`, la `u` de `que` y `gui`) y una letra para dos sonidos (`x`), así que un recuento de letras haría de `calle` un grupo de dos consonantes y de `queso` una palabra de tres vocales. La ortografía del español es lo bastante regular como para leerse por reglas, sin diccionario. La pronunciación es la del estándar de España: yeísmo (`ll` e `y` son un solo sonido) y distinción (`c` ante `e` e `i` y `z` son θ, distinta de `s`).

| Clase | Sonidos |
| :---- | :------ |
| Vocales | a, e, i, o, u |
| Sonantes | m, n, ɲ (`ñ`), l, r (la vibrante simple y la múltiple son un sonido) |
| Obstruyentes sonoras | b (`b`, `v`), d, g, ʝ (`y`, `ll`) |
| Obstruyentes sordas | p, t, k (`c`, `qu`, `k`), f, θ (`c`, `z`), s, x (`j`, `g`), tʃ (`ch`) |

Las sílabas son las de [`syllabify`](../syllables.md), por las reglas ortográficas, y un hiato son dos vocales en dos sílabas vecinas de una palabra (`po-e-ta`, `dí-a`, `bú-ho`).

!!! note "Nota"
    Las estadísticas se calculan al crear el objeto `PhonStats`. Las estadísticas y las funciones que las calculan se describen en la [sección](phon_stats_funcs.md) correspondiente.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `words_extractor` | WordsExtractor | `None` | Herramienta de extracción de palabras |
| `window_len` | int | `3` | Ventana en palabras para la aliteración y la asonancia |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[str] | Tupla de las palabras extraídas en minúsculas |
| `syllables` | tuple[tuple[str]] | Tupla de las sílabas de cada palabra |
| `sounds` | tuple[tuple[str]] | Tupla de los sonidos de cada palabra |
| `n_vowels` | int | Número de vocales |
| `n_consonants` | int | Número de consonantes |
| `n_sonorants` | int | Número de consonantes sonantes |
| `n_voiced` | int | Número de obstruyentes sonoras |
| `n_voiceless` | int | Número de obstruyentes sordas |
| `c_clusters` | dict[int, int] | Distribución de los grupos consonánticos por longitud |
| `c_syllable_patterns` | dict[str, int] | Distribución de las sílabas por patrón CV |
| `p_vowels` | float | Proporción de vocales entre los sonidos |
| `p_sonorants` | float | Proporción de consonantes sonantes entre los sonidos |
| `p_voiced` | float | Proporción de obstruyentes sonoras entre los sonidos |
| `p_voiceless` | float | Proporción de obstruyentes sordas entre los sonidos |
| `consonant_vowel_ratio` | float | Razón de consonantes a vocales |
| `p_heavy_clusters` | float | Proporción de los grupos de 3 consonantes o más |
| `p_hiatus` | float | Hiatos por palabra |
| `cv_entropy` | float | Entropía de los patrones CV de las palabras en bits |
| `hardness` | float | Razón de las obstruyentes sordas a las vocales y las sonantes |
| `alliteration` | float | Índice de aliteración |
| `assonance` | float | Índice de asonancia |
| `p_open_syllables` | float | Proporción de sílabas abiertas |
| `mean_syllable_len` | float | Longitud media de una sílaba en sonidos |

## Métodos

### get_stats

Devuelve un diccionario con la fonoestadística calculada.

!!! example "Ejemplo"

    ``` python
    from ests import PhonStats

    ps = PhonStats("Tres tristes tigres tragaban trigo en un trigal")
    ps.get_stats()
    # {'p_vowels': 0.35,
    #  'p_sonorants': 0.25,
    #  'p_voiced': 0.125,
    #  'p_voiceless': 0.275,
    #  'consonant_vowel_ratio': 1.8571428571428572,
    #  'p_heavy_clusters': 0.0,
    #  'p_hiatus': 0.0,
    #  'cv_entropy': 2.75,
    #  'hardness': 0.4583333333333333,
    #  'alliteration': 0.9175627240143369,
    #  'assonance': 0.6708595387840671,
    #  'p_open_syllables': 0.42857142857142855,
    #  'mean_syllable_len': 2.857142857142857}

    ps.syllables[:3], ps.sounds[:2]
    # ((('tres',), ('tris', 'tes'), ('ti', 'gres')),
    #  (('t', 'r', 'e', 's'), ('t', 'r', 'i', 's', 't', 'e', 's')))
    ```

### print_stats

Muestra una tabla con la fonoestadística calculada.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import PhonStats

    # La primera estrofa de Sonatina de Rubén Darío (Prosas profanas, 1896)
    sonatina = (
        "La princesa está triste... ¿qué tendrá la princesa?\n"
        "Los suspiros se escapan de su boca de fresa,\n"
        "que ha perdido la risa, que ha perdido el color.\n"
        "La princesa está pálida en su silla de oro,\n"
        "está mudo el teclado de su clave sonoro;\n"
        "y en un vaso olvidada se desmaya una flor."
    )
    PhonStats(sonatina).print_stats()
    ```

    _Resultado_:

    ``` bash
                      Statistic                   |  Value
    --------------------------------------------------------
    Share of vowels                               |   0.46
    Share of sonorant consonants                  |   0.19
    Share of voiced obstruents                    |   0.10
    Share of voiceless obstruents                 |   0.25
    Ratio of consonants to vowels                 |   1.19
    Share of clusters of 3 consonants or more     |   0.01
    Hiatuses per word                             |   0.00
    Entropy of the CV patterns of words (bits)    |   3.55
    Hardness                                      |   0.39
    Alliteration index                            |   0.83
    Assonance index                               |   0.86
    Share of open syllables                       |   0.74
    Mean length of a syllable (sounds)            |   2.19
    ```

Los índices de aliteración y de asonancia comparan las repeticiones con las que se esperan de las frecuencias de los sonidos del propio texto, así que dicen si un texto agrupa sus repeticiones en palabras vecinas. Sobre un libro entero se acercan a 1 tanto en verso como en prosa (0,95-0,98 para *Prosas profanas*, los poemas de Machado, *En las orillas del Sar*, *Marianela* y *Niebla* del [corpus de literatura](../datasets/spanishliterature.md)): las repeticiones de un poema son locales, y los lugares donde se agrupan los muestra la capa `alliteration` del [resaltado](../visualizers/highlight.md).
