# Funciones de las estadísticas

## Transcripción { #transcribe }

!!! info ""
    **ests.phon_stats.transcribe()**

Transcribe una palabra en sus sonidos. La palabra se divide en sílabas ([`syllabify`](../syllables.md)) y cada sílaba se lee por las reglas de la ortografía española; los caracteres que no son letras del español (cifras, guiones) se omiten, y los resultados se guardan en caché por forma.

| Grafía | Sonido | Ejemplo |
| :----- | :----: | :------ |
| `a`, `á`; `e`, `é`; `i`, `í`; `o`, `ó`; `u`, `ú`, `ü` | a, e, i, o, u | `canción` - k a n θ i o n |
| `h` | ninguno; `hi` ante vocal al principio de una sílaba es ʝ | `ahora` - a o r a, `hielo` - ʝ e l o |
| `ch` | tʃ | `hechizo` - e tʃ i θ o |
| `c` ante `e`, `i`; `z` | θ | `cena` - θ e n a |
| `c` en los demás casos, `qu` ante `e`, `i`, `k` | k | `queso` - k e s o |
| `g` ante `e`, `i`; `j` | x | `gente` - x e n t e |
| `g` en los demás casos, `gu` ante `e`, `i` | g | `guerra` - g e r a |
| `ll`; `y` ante vocal | ʝ | `calle` - k a ʝ e |
| `y` al final de una sílaba | i | `hoy` - o i |
| `r`, `rr` | r | `perro` - p e r o |
| `ñ` | ɲ | `niño` - n i ɲ o |
| `v` | b | `vaca` - b a k a |
| `x`; `x` al principio de una palabra | k s; s | `examen` - e k s a m e n, `xilófono` - s i l o f o n o |
| `w` | u | `whisky` - u i s k i |

La pronunciación es la del estándar de España, con yeísmo y distinción. Una regla lee la grafía de una palabra, no su historia: la `x` de `México` es k s, como en `examen`.

!!! example "Ejemplo"

    ``` python
    from ests.phon_stats import transcribe

    transcribe("hechizo"), transcribe("guerrilla"), transcribe("examen")
    # (('e', 'tʃ', 'i', 'θ', 'o'), ('g', 'e', 'r', 'i', 'ʝ', 'a'),
    #  ('e', 'k', 's', 'a', 'm', 'e', 'n'))
    ```

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `word` | str | `-` | Palabra |

## Patrón CV { #cv_pattern }

!!! info ""
    **ests.phon_stats.cv_pattern()**

El patrón CV de una palabra o de una sílaba: las vocales se escriben V y las consonantes C, sobre los sonidos de la transcripción - `queso` es CVCV, `hora` VCV, `examen` VCCVCVC.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `sounds` | tuple[str] | `-` | Sonidos de una palabra o de una sílaba |

## Sílaba abierta { #is_open_syllable }

!!! info ""
    **ests.phon_stats.is_open_syllable()**

Comprueba si una sílaba es abierta: una sílaba abierta termina en un sonido vocálico - `ca`, `que`, `hoy` (la `y` final es la vocal i); `car` y `pan` son cerradas.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `syllable` | tuple[str] | `-` | Sonidos de la sílaba |

## Grupos consonánticos { #calc_consonant_clusters }

!!! info ""
    **ests.phon_stats.calc_consonant_clusters()**

La distribución de los grupos consonánticos por longitud. Un grupo es una secuencia de sonidos consonánticos dentro de una palabra, a través de las sílabas: `instrumento` tiene los grupos n s t r (4), m (1) y n t (2). Los grupos de longitud 1 son las consonantes sueltas entre vocales o en los bordes de una palabra. Los dígrafos son un sonido (`calle`, `perro`, `chico`), y la `x` son dos (`extra` - k s t r).

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Hiatos { #calc_hiatus }

!!! info ""
    **ests.phon_stats.calc_hiatus()**

El número de hiatos: dos vocales seguidas en dos sílabas de una palabra, tal como las divide [`syllabify`](../syllables.md) - `po-e-ta`, `dí-a`, `le-er`, `a-é-re-o` (dos). Una `h` muda entre las vocales no rompe el hiato (`bú-ho`, `a-ho-ra`), y las vocales de un diptongo son una sílaba y no forman hiato (`cie-lo`, `ciu-dad`).

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Entropía de los patrones CV { #calc_cv_entropy }

!!! info ""
    **ests.phon_stats.calc_cv_entropy()**

La entropía de Shannon de la distribución de las palabras por patrón CV en bits: cuanto más alta, más variada la forma fónica de las palabras del texto. Las palabras sin sonidos (números) se omiten; `nan` para un texto sin ellas.

$$
H = -\sum_{k} p_k \log_2 p_k
$$

donde $p_k$ es la proporción de las palabras con el patrón CV $k$.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Dureza { #hardness }

La razón de las obstruyentes sordas a las vocales y las sonantes: un texto de p, t, k, s y θ suena más duro que un texto de vocales y de m, n, l, r.

$$
\frac{n_{voiceless}}{n_{vowels} + n_{sonorants}}
$$

## Índice de aliteración { #calc_alliteration }

!!! info ""
    **ests.phon_stats.calc_alliteration()**

La razón del número observado de ventanas de `window_len` palabras vecinas en las que un sonido consonántico aparece en dos palabras o más al número esperado si las consonantes se repartieran al azar entre las palabras, sumado sobre las consonantes. El número esperado sale de las frecuencias de las consonantes del propio texto, así que el índice dice si las repeticiones se agrupan en palabras vecinas, no cuán frecuente es un sonido: cerca de 1 - las repeticiones son aleatorias, bastante por encima de 1 - aliteración. Las consonantes son los sonidos de la transcripción, así que `casa` y `queso` repiten k, y `cena` y `casa` no; `nan` para un texto más corto que la ventana.

$$
\frac{\sum_c O_c}{\sum_c (W - w + 1) \left(1 - (1 - p_c)^w - w p_c (1 - p_c)^{w - 1}\right)}
$$

donde $O_c$ es el número de ventanas con la consonante $c$ en dos palabras o más, $W$ el número de palabras, $w$ la ventana y $p_c$ la proporción de las palabras con la consonante $c$.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `window_len` | int | `3` | Ventana en palabras |

## Índice de asonancia { #calc_assonance }

!!! info ""
    **ests.phon_stats.calc_assonance()**

La misma razón sobre las vocales: el número observado de ventanas de `window_len` palabras vecinas en las que una vocal aparece en dos palabras o más frente al número esperado por las frecuencias de las vocales del texto. Cuentan todas las vocales, tónicas o no; `nan` para un texto más corto que la ventana.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `window_len` | int | `3` | Ventana en palabras |
