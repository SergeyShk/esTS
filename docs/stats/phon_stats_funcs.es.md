# Funciones de las estadísticas

## Transcripción { #transcribe }

!!! info ""
    **ests.phon_stats.transcribe()**

Transcribe una palabra en sus sonidos. La palabra se divide en sílabas ([`syllabify`](../syllables.md)) y cada sílaba se lee por las reglas de la ortografía española; los caracteres que no son letras del español (cifras, guiones) se omiten.

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

El patrón CV de una palabra o de una sílaba: las vocales se escriben V y las consonantes C, sobre los sonidos de la transcripción - `queso` es CVCV, `hora` VCV, `examen` VCCVCVC. Una sílaba se lee como una palabra por sí sola, así que su `x` inicial es s, como al comienzo de una palabra: `xi` es CV, mientras que la sílaba `xi` de `México` cuenta como CCV en `PhonStats`.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `word` | str | `-` | Palabra o sílaba |

## Sílaba abierta { #is_open_syllable }

!!! info ""
    **ests.phon_stats.is_open_syllable()**

Comprueba si una sílaba es abierta: una sílaba abierta termina en un sonido vocálico - `ca`, `que`, `hoy` (la `y` final es la vocal i); `car` y `pan` son cerradas. La sílaba se lee como una palabra por sí sola.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `syllable` | str | `-` | Sílaba |

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

El índice es `calc_repetition_index` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/phonetics/) sobre los sonidos consonánticos de las palabras:

<!-- core: stats/phonetics.md:calc_repetition_index 4e25d01 -->
El índice de repetición: el número de ventanas de `window_len` palabras vecinas donde un rasgo - una letra o un sonido, según elija una biblioteca - aparece en dos palabras o más, sumado sobre los rasgos, dividido por el número esperado si las palabras estuvieran en orden aleatorio. Una ventana de palabras barajadas es una muestra de ellas sin reposición, así que, para un rasgo presente en \(K\) de las \(N\) palabras del texto, una ventana de \(w\) palabras lo contiene en dos palabras o más con la probabilidad hipergeométrica

$$
P = 1 - \frac{\binom{N-K}{w} + K \binom{N-K}{w-1}}{\binom{N}{w}}
$$

y el número esperado es la suma de estas probabilidades sobre los rasgos multiplicada por las \(N - w + 1\) ventanas. La esperanza sale del propio texto, así que el índice dice si las repeticiones se agrupan en palabras vecinas, no cuán frecuente es un rasgo: vale 1 de media sobre los órdenes de las palabras y queda bastante por encima de 1 cuando las repeticiones se acercan más que al azar. Una palabra cuenta un rasgo una vez, lo contenga las veces que lo contenga; `nan` para un texto más corto que la ventana y para un texto en el que ningún rasgo aparezca en dos palabras.

Los rasgos son los sonidos consonánticos de la transcripción, así que `casa` y `queso` repiten k, y `cena` y `casa` no.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `window_len` | int | `3` | Ventana en palabras |

## Índice de asonancia { #calc_assonance }

!!! info ""
    **ests.phon_stats.calc_assonance()**

El índice de `calc_alliteration` sobre las vocales: el número observado de ventanas de `window_len` palabras vecinas en las que una vocal aparece en dos palabras o más frente al número esperado con las palabras en orden aleatorio. Cuentan todas las vocales, tónicas o no; `nan` para un texto más corto que la ventana o sin una vocal que compartan dos palabras.

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `window_len` | int | `3` | Ventana en palabras |
