# Fonoestadística

``` {.python .signature}
PhonStats(source, words_extractor=None, window_len=3)
```

<!-- core: stats/phon_stats.md:PhonStats 408ded2 -->
Las estadísticas fonéticas de un texto: sus sonidos por clase, sus grupos, secuencias y repeticiones, y sus sílabas. Un sonido es por defecto una letra de una palabra, o un sonido de su transcripción cuando una biblioteca la da. La fuente de datos es un texto o un objeto `Doc` de [spaCy](https://github.com/explosion/spaCy); las palabras se toman en minúsculas, y un extractor pasado explícitamente se aplica al texto de un `Doc`.

Excepciones:

- `SourceTypeError` - una fuente que no es ni una cadena ni un `Doc`, un extractor de otro tipo;
- `SourceError` - una fuente sin palabras;
- `ParameterError` - una ventana que no es un entero de al menos 2.

Además de las excepciones anteriores, una cadena con un carácter sin forma UTF-8 lanza `SourceError` desde el tokenizador del español.

La clase extiende el `PhonStats` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/stats/phon_stats/) con los sonidos del español. Los sonidos son los de la transcripción de las palabras ([`transcribe`](#transcribe)), no sus letras: `ch`, `ll`, `rr` y `qu` son un sonido, la `h` y la `u` de `que` y `gui` ninguno, y la `x` dos. La pronunciación es la del estándar de España: yeísmo (`ll` e `y` son un solo sonido) y distinción (`c` ante `e` e `i` y `z` son θ, distinta de `s`). Las clases de los sonidos son las constantes de `ests.constants` de la tabla siguiente. Las sílabas son las de [`syllabify`](../syllables.md#syllabify), por las reglas ortográficas, y un hiato son dos vocales en dos sílabas vecinas de una palabra (`po-e-ta`, `dí-a`, `bú-ho`). Las palabras de una cadena las extrae el [`WordsExtractor`](../extractors/words.md) español; sin extractor, las palabras de un `Doc` salen de sus tokens. No hace falta ningún modelo entrenado. La tabla de `print_stats` lleva las descripciones inglesas del núcleo, `anyts.constants.PHON_STATS_DESC`.

| Clase | Sonidos | Constante |
| :---- | :------ | :-------- |
| Vocales | a, e, i, o, u | `VOWEL_SOUNDS` |
| Sonantes | m, n, ɲ (`ñ`), l, r (la vibrante simple y la múltiple son un sonido) | `SONORANT_SOUNDS` |
| Obstruyentes sonoras | b (`b`, `v`), d, g, ʝ (`y`, `ll`) | `VOICED_SOUNDS` |
| Obstruyentes sordas | p, t, k (`c`, `qu`, `k`), f, θ (`c`, `z`), s, x (`j`, `g`), tʃ (`ch`) | `VOICELESS_SOUNDS` |

=== "Código"

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
    ps = PhonStats(sonatina)
    ps.print_stats()
    ```

=== "Resultado"

    ```
                     Statistic                 |  Value
    ------------------------------------------------------
    Share of vowels                            |   0.46
    Share of sonorant consonants               |   0.19
    Share of voiced obstruents                 |   0.10
    Share of voiceless obstruents              |   0.25
    Ratio of consonants to vowels              |   1.19
    Share of clusters of 3 consonants or more  |   0.01
    Hiatuses per word                          |   0.00
    Entropy of the CV patterns of words (bits) |   3.55
    Hardness                                   |   0.39
    Alliteration index                         |   0.87
    Assonance index                            |   0.87
    Share of open syllables                    |   0.74
    Mean length of a syllable (sounds)         |   2.19
    ```

## Parámetros

<!-- core: stats/phon_stats.md:PhonStats-parameters b90ae7b -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `source` | `str` / `Doc` | - | Fuente de datos |
| `words_extractor` | `WordsExtractor` | `None` | Herramienta de extracción de palabras; se usa también con un `Doc`, sobre su texto |
| `window_len` | `int` | `3` | Ventana en palabras de la aliteración y la asonancia (`PHON_WINDOW_LEN`) |

`PHON_WINDOW_LEN` es una constante de `anyts.constants`.

<!-- core: stats/phon_stats.md:PhonStats-check_params d87e0c6 -->
``` {.python .signature}
check_params(window_len, *, messages=MESSAGES)
```

Comprueba la ventana de la aliteración y la asonancia: una que no es un entero de al menos 2 lanza `ParameterError`.

## Atributos

<!-- core: stats/phon_stats.md:PhonStats-attributes a595894 -->
| Atributo | Tipo | Descripción |
| :------- | :--- | :---------- |
| `words` | `tuple[str]` | Palabras en minúsculas |
| `window_len` | `int` | Ventana de la aliteración y la asonancia |
| `syllables`, `sounds` | `tuple` | Sílabas (`syllabify`) y sonidos (`transcribe`) de cada palabra |
| `n_vowels`, `n_sonorants`, `n_voiced`, `n_voiceless`, `n_consonants` | `int` | Números de los sonidos por clase |
| `c_clusters` | `dict[int, int]` | Número de los grupos consonánticos por longitud (`consonant_clusters`) |
| `c_syllable_patterns` | `dict[str, int]` | Número de las sílabas por patrón CV |

=== "Código"

    ``` python
    ps.syllables[:4]
    ps.sounds[:2]
    ps.c_clusters
    ps.c_syllable_patterns
    ```

=== "Resultado"

    ```
    (('la',), ('prin', 'ce', 'sa'), ('es', 'tá'), ('tris', 'te'))
    (('l', 'a'), ('p', 'r', 'i', 'n', 'θ', 'e', 's', 'a'))
    {1: 66, 2: 21, 3: 1}
    {'CCV': 4, 'CCVC': 5, 'CV': 60, 'CVC': 9, 'V': 5, 'VC': 10}
    ```

## Transcripción { #transcribe }

``` {.python .signature}
transcribe(word)
```

Transcribe una palabra en sus sonidos, los que cuenta `PhonStats`. La palabra se divide en sílabas ([`syllabify`](../syllables.md#syllabify)) y cada sílaba se lee por las reglas de la ortografía española; los caracteres que no son letras del español (cifras, guiones) se omiten.

| Grafía | Sonido | Ejemplo |
| :----- | :----- | :------ |
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

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `word` | `str` | - | Palabra |

Excepciones:

- `SourceTypeError` - una palabra que no es una cadena.

=== "Código"

    ``` python
    from ests.phon_stats import transcribe

    transcribe("hechizo")
    transcribe("guerrilla")
    transcribe("examen")
    ```

=== "Resultado"

    ```
    ('e', 'tʃ', 'i', 'θ', 'o')
    ('g', 'e', 'r', 'i', 'ʝ', 'a')
    ('e', 'k', 's', 'a', 'm', 'e', 'n')
    ```

## Métricas

<!-- core: stats/phon_stats.md:PhonStats-metrics 83c97d6 -->
Cada métrica es un atributo del objeto, calculado al crearlo, y `get_stats` las da todas.

| Métrica | Qué mide | Rango | Un valor mayor indica |
| :------ | :------- | :---- | :-------------------- |
| [`p_vowels`](#sound_shares) | Proporción de las vocales entre los sonidos de las clases | 0-1, `nan` sin sonidos | Un texto más vocálico |
| [`p_sonorants`](#sound_shares) | Proporción de las sonantes entre los sonidos de las clases | 0-1, `nan` sin sonidos | Un texto más sonoro |
| [`p_voiced`](#sound_shares) | Proporción de las obstruyentes sonoras entre los sonidos de las clases | 0-1, `nan` sin sonidos | Más obstruyentes sonoras |
| [`p_voiceless`](#sound_shares) | Proporción de las obstruyentes sordas entre los sonidos de las clases | 0-1, `nan` sin sonidos | Más obstruyentes sordas |
| [`consonant_vowel_ratio`](#consonant_vowel_ratio) | Razón de las consonantes a las vocales | 0 o más, `nan` sin vocales | Consonantes más densas |
| [`p_heavy_clusters`](#consonant_clusters) | Proporción de los grupos de tres consonantes o más | 0-1, `nan` sin grupos | Grupos más pesados |
| [`p_hiatus`](#hiatus) | Hiatos de `word_hiatus` por palabra | 0 o más, `nan` sin sonidos | Más vocales seguidas |
| [`cv_entropy`](#cv_entropy) | Entropía de Shannon de los patrones CV de las palabras, en bits | 0 o más, `nan` sin sonidos | Formas de las palabras más variadas |
| [`hardness`](#hardness) | Obstruyentes sordas frente a las vocales y las sonantes | 0 o más, `nan` sin vocales ni sonantes | Un sonido más duro |
| [`alliteration`](#repetition_index) | Índice de repetición de las consonantes en ventanas de `window_len` palabras | 0 o más, `nan` para un texto más corto que la ventana o sin ninguna consonante que compartan dos palabras | Consonantes repetidas más cerca |
| [`assonance`](#repetition_index) | Índice de repetición de las vocales en ventanas de `window_len` palabras | 0 o más, `nan` para un texto más corto que la ventana o sin ninguna vocal que compartan dos palabras | Vocales repetidas más cerca |
| [`p_open_syllables`](#syllables) | Proporción de las sílabas que terminan en vocal | 0-1, `nan` sin sílabas | Más sílabas abiertas |
| [`mean_syllable_len`](#syllables) | Longitud media de una sílaba en sonidos | 1 o más, `nan` sin sílabas | Sílabas más largas |

Las funciones de las tarjetas se importan de `ests.phon_stats`; reciben las palabras como cadenas y cuentan sobre los sonidos de su transcripción.

<div class="metric-card" markdown>

### Proporciones de las clases de sonidos { #sound_shares }

`p_vowels` · `p_sonorants` · `p_voiced` · `p_voiceless`
{ .metric-meta }

<!-- core: stats/phon_stats.md:PhonStats-sound_shares 4a3e68b -->
La proporción de los sonidos de cada clase - las vocales, las sonantes y las obstruyentes sonoras y sordas - entre los sonidos de todas ellas; un sonido de `skipped` o de ninguna clase (una cifra, una letra de otra escritura) no cuenta en ninguna.

$$
\frac{\textrm{Número de sonidos de la clase}}{\textrm{Número de vocales y consonantes}}
$$

</div>

<div class="metric-card" markdown>

### Razón de las consonantes a las vocales { #consonant_vowel_ratio }

`consonant_vowel_ratio`
{ .metric-meta }

<!-- core: stats/phon_stats.md:PhonStats-consonant_vowel_ratio 7e4ca83 -->
El número de las consonantes `n_consonants` frente al número de las vocales `n_vowels`.

$$
\frac{\textrm{Número de consonantes}}{\textrm{Número de vocales}}
$$

</div>

<div class="metric-card" markdown>

### Grupos consonánticos { #consonant_clusters }

`p_heavy_clusters` · `c_clusters`
{ .metric-meta }

``` {.python .signature}
calc_consonant_clusters(text)
```

La distribución de los grupos consonánticos de las palabras por longitud, el atributo `c_clusters`. Un grupo es una secuencia de sonidos consonánticos dentro de una palabra, a través de las sílabas, incluida una consonante suelta entre vocales o en el borde de una palabra: `instrumento` tiene los grupos n s t r (4), m (1) y n t (2). Los dígrafos son un sonido (`calle`, `perro`, `chico`), y la `x` son dos (`extra` - k s t r). `p_heavy_clusters` es la proporción de los grupos pesados:

$$
\frac{\textrm{Número de grupos de 3 consonantes o más}}{\textrm{Número de grupos}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas.

=== "Código"

    ``` python
    from ests.phon_stats import calc_consonant_clusters

    calc_consonant_clusters(["instrumento", "calle"])
    ```

=== "Resultado"

    ```
    {1: 3, 2: 1, 4: 1}
    ```

</div>

<div class="metric-card" markdown>

### Hiatos { #hiatus }

`p_hiatus`
{ .metric-meta }

``` {.python .signature}
calc_hiatus(text)
```

El número de hiatos: dos vocales seguidas en dos sílabas de una palabra, tal como las divide [`syllabify`](../syllables.md#syllabify) - `po-e-ta`, `dí-a`, `le-er`, `a-é-re-o` (dos). Una `h` muda entre las vocales no rompe el hiato (`bú-ho`, `a-ho-ra`), y las vocales de un diptongo son una sílaba y no forman hiato (`cie-lo`, `ciu-dad`). `p_hiatus` es el número de hiatos del texto por palabra.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas.

=== "Código"

    ``` python
    from ests.phon_stats import calc_hiatus

    calc_hiatus(["poeta", "búho", "cielo", "aéreo"])
    ```

=== "Resultado"

    ```
    4
    ```

</div>

<div class="metric-card" markdown>

### Entropía de los patrones CV { #cv_entropy }

`cv_entropy`
{ .metric-meta }

<!-- core: stats/phon_stats.md:PhonStats-cv_entropy 8ca17ec -->
La entropía de Shannon de los patrones CV de las palabras (`cv_pattern`), en bits, donde $P(p)$ es la proporción de las palabras con el patrón $p$ entre las palabras que tienen uno.

$$
-\sum_{p} P(p) \log_2 P(p)
$$

``` {.python .signature}
calc_cv_entropy(text)
```

La entropía de los patrones CV de una lista de palabras: cuanto más alta, más variada la forma fónica de las palabras del texto. Las palabras sin sonidos (números) se omiten; `nan` para un texto sin otras palabras.

``` {.python .signature}
cv_pattern(word)
```

El patrón CV de una palabra o de una sílaba: las vocales se escriben V y las consonantes C, sobre los sonidos de la transcripción - `queso` es CVCV, `hora` VCV, `examen` VCCVCVC. Una sílaba se lee como una palabra por sí sola, así que su `x` inicial es s, como al comienzo de una palabra: `xi` es CV, mientras que la sílaba `xi` de `México` cuenta como CCV en `PhonStats`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras (`calc_cv_entropy`) |
| `word` | `str` | - | Palabra o sílaba (`cv_pattern`) |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas (`calc_cv_entropy`), una palabra que no es una cadena (`cv_pattern`).

=== "Código"

    ``` python
    from ests.phon_stats import calc_cv_entropy, cv_pattern

    cv_pattern("queso"), cv_pattern("examen")
    calc_cv_entropy(["poeta", "búho", "cielo", "aéreo"])
    ```

=== "Resultado"

    ```
    ('CVCV', 'VCCVCVC')
    1.5
    ```

</div>

<div class="metric-card" markdown>

### Dureza { #hardness }

`hardness`
{ .metric-meta }

<!-- core: stats/phon_stats.md:PhonStats-hardness 7602f72 -->
El número de las obstruyentes sordas frente al número de las vocales y las sonantes.

$$
\frac{\textrm{Número de obstruyentes sordas}}{\textrm{Número de vocales} + \textrm{Número de sonantes}}
$$

Un texto de p, t, k, s y θ suena más duro que un texto de vocales y de m, n, l, r.

</div>

<div class="metric-card" markdown>

### Aliteración y asonancia { #repetition_index }

`alliteration` · `assonance`
{ .metric-meta }

``` {.python .signature}
calc_alliteration(text, window_len=3)
```

``` {.python .signature}
calc_assonance(text, window_len=3)
```

Los índices de aliteración y de asonancia de una lista de palabras: el índice de repetición `calc_repetition_index` de `anyts.phon_stats` sobre los sonidos consonánticos y sobre los vocálicos de la transcripción de las palabras. Cuentan los sonidos, no las letras: `casa` y `queso` repiten k, `cena` y `casa` no; cuentan todas las vocales, tónicas o no.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `window_len` | `int` | `3` | Ventana en palabras (`PHON_WINDOW_LEN`) |

Excepciones:

- `SourceTypeError` - unas palabras que no son una lista de cadenas;
- `ParameterError` - una ventana que no es un entero de al menos 2.

<!-- core: stats/phon_stats.md:calc_repetition_index ea6ed82 -->
``` {.python .signature}
calc_repetition_index(words, window_len, features=None)
```

El índice de repetición: el número de ventanas de `window_len` palabras vecinas donde un rasgo (una letra o un sonido) aparece en dos palabras o más, sumado sobre los rasgos, dividido por el número esperado si las palabras estuvieran en orden aleatorio. Una ventana de palabras barajadas es una muestra sin reposición, así que, para un rasgo presente en \(K\) de las \(N\) palabras, una ventana de \(w\) palabras lo contiene en dos palabras o más con la probabilidad hipergeométrica

$$
P = 1 - \frac{\binom{N-K}{w} + K \binom{N-K}{w-1}}{\binom{N}{w}}
$$

y el número esperado es la suma de estas probabilidades sobre los rasgos multiplicada por las \(N - w + 1\) ventanas. Como la esperanza sale del propio texto, el índice muestra si las repeticiones se agrupan en palabras vecinas, no cuán frecuente es un rasgo: vale 1 de media sobre los órdenes de las palabras y queda bastante por encima de 1 cuando las repeticiones se acercan más que al azar. Una palabra cuenta un rasgo una vez; el índice es `nan` para un texto más corto que la ventana o sin ningún rasgo que compartan dos palabras.

<!-- core: stats/phon_stats.md:calc_repetition_index-parameters 9e9f02b -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `words` | `list[str]` / `list[list[str]]` | - | Rasgos de cada palabra: una cadena de sus letras o una colección de sus sonidos |
| `window_len` | `int` | - | Ventana en palabras, al menos 2 |
| `features` | `Collection[str]` | `None` | Rasgos que se cuentan, todos por defecto |

Unas palabras que no son una lista de cadenas o de colecciones de cadenas y unos rasgos que no son una colección de cadenas lanzan `SourceTypeError`, y un `window_len` que no es un entero de al menos 2, `ParameterError`.

Con las palabras en orden aleatorio los índices valen 1 de media: los 150 libros del [corpus de literatura](../datasets/spanishliterature.md) con sus palabras barajadas dan de 0,98 a 1,02. En los libros tal como están escritos el índice de aliteración queda algo por debajo de 1 tanto en verso como en prosa, de 0,90 a 0,99 con una mediana de 0,95, y el de asonancia cerca de 1, de 0,99 a 1,01: en un libro entero las palabras vecinas comparten una consonante algo menos a menudo que al azar. Los 4259 [sonetos](../datasets/spanishsonnets.md) dan medianas de 0,92 y 0,98, con gran dispersión en textos tan cortos (de 0,59 a 1,30 la aliteración). Las repeticiones de un poema son locales, y los lugares donde se agrupan los muestra la capa `alliteration` del [resaltado](../visualizers/highlight.md).

=== "Código"

    ``` python
    from ests.phon_stats import calc_alliteration, calc_assonance

    # Garcilaso de la Vega, Égloga III
    words = "en el silencio sólo se escuchaba un susurro de abejas que sonaba".split()
    calc_alliteration(words), calc_assonance(words)
    ```

=== "Resultado"

    ```
    (1.0232558139534884, 1.115942028985507)
    ```

</div>

<div class="metric-card" markdown>

### Sílabas { #syllables }

`p_open_syllables` · `mean_syllable_len`
{ .metric-meta }

<!-- core: stats/phon_stats.md:PhonStats-syllables eb2f919 -->
Las sílabas son los sonidos de cada sílaba de una palabra según `syllable_sounds`; una sílaba sin ningún sonido de las clases (un número) no es una sílaba, tampoco en `c_syllable_patterns`. Una sílaba abierta termina en vocal según su patrón CV (`cv_pattern`), y la longitud de una sílaba es la longitud de ese patrón: los sonidos de las clases, sin `skipped` ni los signos fuera de ellas.

Los sonidos de una sílaba son su transcripción, y la primera sílaba de una palabra se lee como el comienzo de la palabra: la `xi` de `xilófono` es s i, la `xi` de `México`, k s i.

``` {.python .signature}
is_open_syllable(syllable)
```

Comprueba si una sílaba es abierta: una sílaba abierta termina en un sonido vocálico - `ca`, `que`, `hoy` (la `y` final es la vocal i); `car` y `pan` son cerradas. La sílaba se lee como una palabra por sí sola.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :---------- | :---------- |
| `syllable` | `str` | - | Sílaba |

Excepciones:

- `SourceTypeError` - una sílaba que no es una cadena.

=== "Código"

    ``` python
    from ests.phon_stats import is_open_syllable

    is_open_syllable("hoy"), is_open_syllable("car")
    ```

=== "Resultado"

    ```
    (True, False)
    ```

</div>

## Métodos

Los métodos `get_stats`, `to_dataframe`, `print_stats` y `describe` son los de la [interfaz de estadísticas](https://sergeyshk.github.io/anyTS/stats/stats/) del núcleo anyTS; la fonoestadística no tiene escalas, así que `describe` da `None` para las estadísticas de `get_stats`.

=== "Código"

    ``` python
    from ests import PhonStats

    PhonStats("Tres tristes tigres tragaban trigo en un trigal").get_stats()
    ```

=== "Resultado"

    ```
    {'p_vowels': 0.35,
     'p_sonorants': 0.25,
     'p_voiced': 0.125,
     'p_voiceless': 0.275,
     'consonant_vowel_ratio': 1.8571428571428572,
     'p_heavy_clusters': 0.0,
     'p_hiatus': 0.0,
     'cv_entropy': 2.75,
     'hardness': 0.4583333333333333,
     'alliteration': 0.9333333333333333,
     'assonance': 0.7526881720430108,
     'p_open_syllables': 0.42857142857142855,
     'mean_syllable_len': 2.857142857142857}
    ```
