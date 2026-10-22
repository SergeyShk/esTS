# Funciones de las métricas

## Type-Token Ratio (TTR)

!!! info ""
    **ests.diversity_stats.calc_ttr()**

<!-- core: stats/diversity_stats.md:calc_ttr 4982ca2 -->
``` {.python .signature}
calc_ttr(text)
```

La medida más simple de la diversidad léxica; no está corregida por la longitud del texto.

$$
\frac{\textrm{Número de lexemas}}{\textrm{Número de palabras}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Root Type-Token Ratio (RTTR)

!!! info ""
    **ests.diversity_stats.calc_rttr()**

<!-- core: stats/diversity_stats.md:calc_rttr 565f2bc -->
``` {.python .signature}
calc_rttr(text)
```

Una modificación del TTR (Guiraud, 1960).

$$
\frac{\textrm{Número de lexemas}}{\sqrt{\textrm{(Número de palabras)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Corrected Type-Token Ratio (CTTR)

!!! info ""
    **ests.diversity_stats.calc_cttr()**

<!-- core: stats/diversity_stats.md:calc_cttr 06c97ca -->
``` {.python .signature}
calc_cttr(text)
```

Una modificación del TTR (Carroll, 1964).

$$
\frac{\textrm{Número de lexemas}}{\sqrt{2\times\textrm{(Número de palabras)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Herdan Type-Token Ratio (HTTR)

!!! info ""
    **ests.diversity_stats.calc_httr()**

<!-- core: stats/diversity_stats.md:calc_httr 42487d4 -->
``` {.python .signature}
calc_httr(text)
```

Una modificación logarítmica del TTR (Herdan, 1960).

$$
\frac{\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Summer Type-Token Ratio (STTR)

!!! info ""
    **ests.diversity_stats.calc_sttr()**

<!-- core: stats/diversity_stats.md:calc_sttr 1847a8d -->
``` {.python .signature}
calc_sttr(text, base=10)
```

Una modificación logarítmica del TTR (Summer, 1966). El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)). Es `nan` en un texto de un solo lexema, donde el numerador no está definido, y en un texto no más largo que la base ($\log \log N \le 0$), incluidas las ventanas así de cortas de `calc_windowed`.

$$
\frac{\log_{10} {\log_{10} {\textrm{(Número de lexemas)}}}}{\log_{10} {\log_{10} {{\textrm{(Número de palabras)}}}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

## Maas Type-Token Ratio (MTTR)

!!! info ""
    **ests.diversity_stats.calc_mttr()**

<!-- core: stats/diversity_stats.md:calc_mttr 4d5f1b1 -->
``` {.python .signature}
calc_mttr(text, base=10)
```

Una modificación logarítmica del TTR (Maas, 1972). El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)).

$$
\frac{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}^2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

## Dugast Type-Token Ratio (DTTR)

!!! info ""
    **ests.diversity_stats.calc_dttr()**

<!-- core: stats/diversity_stats.md:calc_dttr 654db67 -->
``` {.python .signature}
calc_dttr(text, base=10)
```

Una modificación logarítmica del TTR (Dugast, 1978), el recíproco de la métrica de Maas. El valor depende de la base del logaritmo (véanse las [convenciones](#conventions)). Un texto sin palabras repetidas tiene un valor infinito.

$$
\frac{\log_{10} {{\textrm{(Número de palabras)}}}^2}{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

## Moving Average Type-Token Ratio (MATTR)

!!! info ""
    **ests.diversity_stats.calc_mattr()**

<!-- core: stats/diversity_stats.md:calc_mattr e57be40 -->
``` {.python .signature}
calc_mattr(text, window_len=50)
```

Una modificación del TTR con media móvil (Covington & McFall, 2010), independiente de la longitud del texto: una ventana de tamaño fijo se desliza por el texto y se promedia el TTR de cada ventana. En los textos más cortos que la ventana se devuelve el TTR de todo el texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `window_len` | `int` | `50` | Tamaño de la ventana (`MATTR_WINDOW_LEN`) |

Un `window_len` que no es un entero de al menos uno lanza `ParameterError`.

## Mean Segmental Type-Token Ratio (MSTTR)

!!! info ""
    **ests.diversity_stats.calc_msttr()**

<!-- core: stats/diversity_stats.md:calc_msttr 21799ac -->
``` {.python .signature}
calc_msttr(text, segment_len=50)
```

Una modificación del TTR por segmentación (Johnson, 1944), independiente de la longitud del texto: el texto se divide en segmentos de tamaño fijo y se promedia el TTR de cada segmento; un último segmento incompleto se descarta. En los textos más cortos que el segmento se devuelve el TTR de todo el texto.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `segment_len` | `int` | `50` | Tamaño del segmento (`MATTR_WINDOW_LEN`) |

Un `segment_len` que no es un entero de al menos uno lanza `ParameterError`.

## Measure of Textual Lexical Diversity (MTLD)

!!! info ""
    **ests.diversity_stats.calc_mtld()**

<!-- core: stats/diversity_stats.md:calc_mtld 427e11b -->
``` {.python .signature}
calc_mtld(text, min_len=10, threshold=0.72)
```

Una modificación del MSTTR (McCarthy, 2005), independiente de la longitud del texto: el número de palabras dividido por el número de factores, los tramos en los que el TTR baja hasta el umbral (`TTR <= threshold`, véanse las [convenciones](#conventions)). Un último factor incompleto cuenta en proporción a lo que su TTR se acercó al umbral. El valor es la media de una pasada hacia delante y otra hacia atrás (McCarthy & Jarvis, 2010). La longitud mínima del factor no es estándar (lexical-diversity de Kyle), y un `min_len` de 0 la desactiva. Si ningún factor se completa y el TTR nunca baja de 1, el valor es infinito.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

## Moving Average Measure of Textual Lexical Diversity (MA-MTLD)

!!! info ""
    **ests.diversity_stats.calc_mamtld()**

<!-- core: stats/diversity_stats.md:calc_mamtld c845458 -->
``` {.python .signature}
calc_mamtld(text, min_len=10, threshold=0.72)
```

Una modificación de MTLD con ventana móvil según el MTLD-MA de koRpus: un factor empieza en cada posición del texto, y el valor es la longitud media de los factores completados en una pasada hacia delante y otra hacia atrás. koRpus hace solo la pasada hacia delante, cierra un factor con un TTR estrictamente menor que el umbral y descarta los factores más cortos que la longitud mínima en lugar de extenderlos. Si ningún factor se completa, el valor es `nan`. La métrica es inestable en textos cortos.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

## MTLD con ventana móvil y vuelta al inicio del texto (MTLD-W)

!!! info ""
    **ests.diversity_stats.calc_mtldw()**

<!-- core: stats/diversity_stats.md:calc_mtldw 6e0e9fe -->
``` {.python .signature}
calc_mtldw(text, min_len=10, threshold=0.72)
```

Una modificación de MA-MTLD según `mtld_ma_wrap` de lexical-diversity y TAALED: los factores no completados al final del texto continúan desde su principio, así que todas las posiciones tienen el mismo peso. Un factor no puede ser más largo que el texto. Si ningún factor se completa, porque el texto es más corto que `min_len` o porque el TTR no baja hasta el umbral desde ningún inicio, el valor es `nan`. La métrica es inestable en textos de menos de 100 palabras.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `min_len` | `int` | `10` | Longitud mínima del factor (`MTLD_MIN_LEN`) |
| `threshold` | `float` | `0.72` | Umbral de TTR para completar un factor (`MTLD_TTR_THRESHOLD`) |

Un `min_len` que no es un entero no negativo y un `threshold` que no es un número en (0, 1) lanzan `ParameterError`.

## Hypergeometric Distribution D (HD-D)

!!! info ""
    **ests.diversity_stats.calc_hdd()**

<!-- core: stats/diversity_stats.md:calc_hdd 44ad1ca -->
``` {.python .signature}
calc_hdd(text, sample_size=42)
```

Una alternativa a vocd-D (McCarthy & Jarvis, 2010): el TTR esperado exacto de una muestra aleatoria de `sample_size` palabras, sin extraer muestras. La distribución hipergeométrica da la probabilidad de que la muestra contenga cada lexema al menos una vez; HD-D es la suma de estas probabilidades dividida por el tamaño de la muestra. En los textos de menos de 50 palabras o más cortos que el tamaño de la muestra la métrica no está definida, y el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `sample_size` | `int` | `42` | Tamaño de la muestra en palabras (`HDD_SAMPLE_SIZE`) |

Un `sample_size` que no es un entero de al menos uno lanza `ParameterError`.

## Índice de Simpson (D)

!!! info ""
    **ests.diversity_stats.calc_simpson_index()**

<!-- core: stats/diversity_stats.md:calc_simpson_index 5c0c871 -->
``` {.python .signature}
calc_simpson_index(text)
```

La probabilidad de que dos palabras extraídas del texto al azar sin reemplazo sean el mismo lexema; $n$ es el número de apariciones de un lexema en el texto. En los textos de menos de dos palabras el índice no está definido, y el valor es `nan`; lo mismo vale para el índice de Simpson inverso y el índice de Gini-Simpson.

$$
\frac{\sum n\times(n-1)}{\textrm{(Número de palabras)}\times(\textrm{Número de palabras}-1)}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Índice de Simpson inverso (1/D) { #inverse_simpson_index }

!!! info ""
    **ests.diversity_stats.calc_inverse_simpson_index()**

<!-- core: stats/diversity_stats.md:calc_inverse_simpson_index 370880d -->
``` {.python .signature}
calc_inverse_simpson_index(text)
```

Una estimación del número de Hill de orden dos ($1/\sum_k p_k^2$) a partir de pares extraídos sin reposición. Si todas las palabras del texto son únicas, el índice de Simpson es 0 y el índice inverso es infinito.

$$
\frac{1}{D}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Índice de Gini-Simpson (1-D)

!!! info ""
    **ests.diversity_stats.calc_gini_simpson_index()**

<!-- core: stats/diversity_stats.md:calc_gini_simpson_index 00e1184 -->
``` {.python .signature}
calc_gini_simpson_index(text)
```

La probabilidad de que dos palabras del texto elegidas al azar sean distintas.

$$
1-D
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Índice de hápax (R de Honoré)

!!! info ""
    **ests.diversity_stats.calc_hapax_index()**, alias **ests.diversity_stats.calc_honore_r()**

<!-- core: stats/diversity_stats.md:calc_hapax_index debfb9b -->
``` {.python .signature}
calc_hapax_index(text)
```

Un hápax (del griego ἅπαξ λεγόμενον, «dicho una sola vez») es una palabra que aparece una sola vez en un corpus: *baciyelmo*, la palabra con que Sancho Panza llama a la bacía que don Quijote toma por yelmo, es un hápax de Cervantes (capítulo 44 de la primera parte del *Quijote*). El índice coincide con la medida de Honoré (1979), con el logaritmo natural. Si todas las palabras del texto son hápax, el índice es infinito; en los textos de menos de dos palabras no está definido, y el valor es `nan`. `calc_honore_r` es la misma función.

$$
100\times\frac{\ln {\textrm{(Número de palabras)}}}{1-\frac{\textrm{Número de hápax}}{\textrm{Número de lexemas}}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Espectro de frecuencias { #frequency_spectrum }

!!! info ""
    **ests.diversity_stats.calc_frequency_spectrum()**

<!-- core: stats/diversity_stats.md:calc_frequency_spectrum 5ca9622 -->
``` {.python .signature}
calc_frequency_spectrum(text)
```

El número de lexemas $V_i$ que aparecen exactamente $i$ veces en el texto, como un diccionario por la frecuencia $i$ en orden ascendente. A partir de él se calculan el índice de hápax, la K y la I de Yule, la Vm de Herdan, la S de Sichel, la M de Michéa, la P de Baayen, la proporción de hápax y el exponente α₂, con las fórmulas de Tweedie y Baayen (1998).

Notación: $N$ es el número de palabras, $V$ el número de lexemas, $V_i$ el número de lexemas con frecuencia $i$, $V_1$ los hápax, $V_2$ los dis legomena, $p_k$ la frecuencia relativa de un lexema.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Característica de Yule (K de Yule)

!!! info ""
    **ests.diversity_stats.calc_yule_k()**

<!-- core: stats/diversity_stats.md:calc_yule_k baaaa5a -->
``` {.python .signature}
calc_yule_k(text)
```

La característica de Yule (Yule, 1944), una de las pocas medidas teóricamente independientes de la longitud del texto (Tweedie & Baayen, 1998); en la práctica converge a medida que el texto crece. Es proporcional al índice de Simpson: $K \approx 10^4 \cdot D$. En los textos de menos de dos palabras el valor es `nan`.

$$
K = 10^4\times\frac{\sum_i i^2 V_i - N}{N^2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Característica inversa de Yule (I de Yule)

!!! info ""
    **ests.diversity_stats.calc_yule_i()**

<!-- core: stats/diversity_stats.md:calc_yule_i e6ed7d8 -->
``` {.python .signature}
calc_yule_i(text)
```

La característica inversa de Yule. Si todas las palabras del texto son únicas, el valor es infinito; en los textos de menos de dos palabras es `nan`.

$$
I = \frac{V^2}{\sum_i i^2 V_i - V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Vm de Herdan

!!! info ""
    **ests.diversity_stats.calc_herdan_vm()**

<!-- core: stats/diversity_stats.md:calc_herdan_vm a9088dd -->
``` {.python .signature}
calc_herdan_vm(text)
```

La medida de Herdan (Herdan, 1955), teóricamente independiente de la longitud del texto. En los textos de menos de dos palabras el valor es `nan`.

$$
V_m = \sqrt{\sum_i V_i \left(\frac{i}{N}\right)^2 - \frac{1}{V}}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## S de Sichel

!!! info ""
    **ests.diversity_stats.calc_sichel_s()**

<!-- core: stats/diversity_stats.md:calc_sichel_s 5485001 -->
``` {.python .signature}
calc_sichel_s(text)
```

La medida de Sichel (Sichel, 1975): la proporción de dis legomena, lexemas con frecuencia 2, entre todos los lexemas. Estable en textos de distinta longitud.

$$
S = \frac{V_2}{V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## M de Michéa

!!! info ""
    **ests.diversity_stats.calc_michea_m()**

<!-- core: stats/diversity_stats.md:calc_michea_m 8e3f6f5 -->
``` {.python .signature}
calc_michea_m(text)
```

La medida de Michéa (Michéa, 1969): el recíproco de la medida de Sichel. Si el texto no tiene dis legomena, el valor es infinito.

$$
M = \frac{V}{V_2}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## W de Brunet

!!! info ""
    **ests.diversity_stats.calc_brunet_w()**

<!-- core: stats/diversity_stats.md:calc_brunet_w 2ac7def -->
``` {.python .signature}
calc_brunet_w(text, a=0.172)
```

La medida de Brunet (Brunet, 1978). Los valores de los textos suelen estar entre 10 y 20.

$$
W = N^{V^{-a}}, \quad a = 0.172
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `a` | `float` | `0.172` | Exponente (`BRUNET_W_EXPONENT`) |

Un `a` que no es un número finito lanza `ParameterError`.

## k de Dugast

!!! info ""
    **ests.diversity_stats.calc_dugast_k()**

<!-- core: stats/diversity_stats.md:calc_dugast_k a8d476b -->
``` {.python .signature}
calc_dugast_k(text, base=10)
```

La medida de Dugast (Dugast, 1979), que no debe confundirse con la U de Dugast, la métrica [DTTR](#dttr). El valor depende de la base del logaritmo. En los textos no más largos que la base ($\log N \le 1$) la medida no está definida, y el valor es `nan`.

$$
k = \frac{\log V}{\log \log N}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `base` | `float` | `10` | Base del logaritmo (`DIVERSITY_LOG_BASE`) |

Una `base` que no es un número finito mayor que 1 lanza `ParameterError`.

## P de Baayen

!!! info ""
    **ests.diversity_stats.calc_baayen_p()**

<!-- core: stats/diversity_stats.md:calc_baayen_p 3754bfb -->
``` {.python .signature}
calc_baayen_p(text)
```

La medida de Baayen (Baayen, 1991): la proporción de hápax entre todas las palabras del texto. Es la pendiente de la curva de crecimiento del vocabulario al final del texto: la probabilidad de que la siguiente palabra sea nueva (Evert, 2004).

$$
P = \frac{V_1}{N}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Proporción de hápax { #hapax_ratio }

!!! info ""
    **ests.diversity_stats.calc_hapax_ratio()**

<!-- core: stats/diversity_stats.md:calc_hapax_ratio d3c3e24 -->
``` {.python .signature}
calc_hapax_ratio(text)
```

La proporción de hápax entre todos los lexemas del texto.

$$
\frac{V_1}{V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## El exponente α₂ { #alpha2 }

!!! info ""
    **ests.diversity_stats.calc_alpha2()**

<!-- core: stats/diversity_stats.md:calc_alpha2 69486ad -->
``` {.python .signature}
calc_alpha2(text)
```

Una estimación del parámetro de Zipf-Mandelbrot a partir de la parte baja del espectro de frecuencias (Evert, 2004). Si el texto no tiene hápax, el valor es `nan`.

$$
\alpha_2 = 1 - \frac{2 V_2}{V_1}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Entropía de Shannon { #entropy }

!!! info ""
    **ests.diversity_stats.calc_entropy()**

<!-- core: stats/diversity_stats.md:calc_entropy 507c0b8 -->
``` {.python .signature}
calc_entropy(text)
```

La entropía de la distribución de lexemas en bits. El número de Hill de orden uno es $2^H$ ([perplejidad](#perplexity)), y el de orden cero, $V$; el [índice de Simpson inverso](#inverse_simpson_index) estima el de orden dos.

$$
H = -\sum_k p_k \log_2 p_k
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Equitatividad { #evenness }

!!! info ""
    **ests.diversity_stats.calc_evenness()**

<!-- core: stats/diversity_stats.md:calc_evenness d6817c3 -->
``` {.python .signature}
calc_evenness(text)
```

La equitatividad de Pielou: el cociente entre la entropía de Shannon y su máximo para el número de lexemas dado. En los textos de un solo lexema no está definida, y el valor es `nan`.

$$
\frac{H}{\log_2 V}
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Perplejidad { #perplexity }

!!! info ""
    **ests.diversity_stats.calc_perplexity()**

<!-- core: stats/diversity_stats.md:calc_perplexity b5c954f -->
``` {.python .signature}
calc_perplexity(text)
```

El número de Hill de orden uno, el número efectivo de lexemas del texto.

$$
2^H
$$

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Pendiente de la ley de Zipf { #zipf_alpha }

!!! info ""
    **ests.diversity_stats.calc_zipf_alpha()**

<!-- core: stats/diversity_stats.md:calc_zipf_alpha a63837a -->
``` {.python .signature}
calc_zipf_alpha(text)
```

El exponente $\alpha$ de la ley de Zipf $f(r) \propto r^{-\alpha}$, donde $r$ es el rango de frecuencia de un lexema, estimado por regresión lineal del logaritmo de la frecuencia sobre el logaritmo del rango. En los textos naturales $\alpha$ está cerca de 1. La estimación por mínimos cuadrados sobre los rangos está sesgada; la máxima verosimilitud es más precisa. En los textos de un solo lexema el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

## Ajuste de Zipf-Mandelbrot { #fit_zipf_mandelbrot }

!!! info ""
    **ests.diversity_stats.fit_zipf_mandelbrot()**, **ests.diversity_stats.ZipfMandelbrot**

<!-- core: stats/diversity_stats.md:fit_zipf_mandelbrot 41b2359 -->
``` {.python .signature}
fit_zipf_mandelbrot(text)
```

Ajusta la ley de Zipf-Mandelbrot $f(r) = C / (r + q)^s$ a la distribución rango-frecuencia. Con $q = 0$ es la ley de Zipf con exponente $s$; el desplazamiento $q$ recoge el aplanamiento de la curva en las palabras más frecuentes. El ajuste se hace por mínimos cuadrados en coordenadas logarítmicas con $q \ge 0$, $s \ge 0$; los lexemas de frecuencia cero de un contador se dejan fuera. El resultado es una tupla con nombre `ZipfMandelbrot` con los campos `c`, `q`, `s` y `r2`, el coeficiente de determinación del ajuste en coordenadas logarítmicas. Todos los campos son `nan` en los textos de menos de tres lexemas, con frecuencias idénticas de todos los lexemas o cuando el ajuste diverge. En textos cortos los parámetros son inestables: la ley describe corpus grandes.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` / `Counter` | - | Lista de palabras o un contador de sus frecuencias |

Un contador cuyas palabras no son cadenas o cuyas frecuencias no son números lanza `SourceTypeError`, y una frecuencia negativa, `nan` o infinita, `SourceError` (`check_counts`).

!!! example "Ejemplo"

    ``` python
    from ests.diversity_stats import fit_zipf_mandelbrot

    # las frecuencias 12, 6, 4, 3 siguen exactamente la ley f = 12 / r
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    fit = fit_zipf_mandelbrot(words)
    round(fit.c, 3), round(fit.q, 3), round(fit.s, 3), round(fit.r2, 3)
    # (12.001, 0.0, 1.0, 1.0)
    ```

## Exponente de la ley de Heaps { #heaps_beta }

!!! info ""
    **ests.diversity_stats.calc_heaps_beta()**, **ests.diversity_stats.fit_heaps()**, **ests.diversity_stats.vocabulary_growth()**

<!-- core: stats/diversity_stats.md:calc_heaps_beta 6aaa64a -->
``` {.python .signature}
calc_heaps_beta(text)
```

El exponente $\beta$ de la ley de Heaps $V(N) = K \cdot N^{\beta}$ del crecimiento del vocabulario con la longitud del texto, estimado por regresión lineal del logaritmo del tamaño del vocabulario sobre el logaritmo de la longitud del texto a lo largo de la curva de crecimiento. En corpus de millones de palabras $\beta$ está entre 0.4 y 0.6, en un solo texto entre 0.6 y 0.9, así que los valores solo son comparables entre textos de longitud parecida. El valor depende del orden de las palabras y necesita varios cientos de palabras o más. En los textos de menos de dos palabras el valor es `nan`.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |

<!-- core: stats/diversity_stats.md:vocabulary_growth d1f1d6d -->
``` {.python .signature}
vocabulary_growth(text)
```

La curva de crecimiento del vocabulario de una lista de palabras: el tamaño del vocabulario tras cada palabra del texto.

<!-- core: stats/diversity_stats.md:fit_heaps eefb450 -->
``` {.python .signature}
fit_heaps(text)
```

Ajusta la ley de Heaps sobre la curva de crecimiento del vocabulario de una lista de palabras, como hace `calc_heaps_beta`, y devuelve una tupla con nombre `HeapsFit` con los parámetros `k`, `beta` y el coeficiente de determinación `r2`, todos `nan` en los textos de menos de dos palabras; `r2` es `nan` también en un texto de un solo lexema.

## Cálculo por ventanas { #calc_windowed }

!!! info ""
    **ests.diversity_stats.calc_windowed()**

<!-- core: stats/diversity_stats.md:calc_windowed 40fa4f2 -->
Los valores de una métrica en ventanas consecutivas de igual longitud dan su media, su desviación típica muestral y el intervalo de confianza de la media por la distribución de Student. Es la forma estándar de comparar textos de distinta longitud; el TTR estandarizado de Kubát y Milička (no el STTR de Summer) es un TTR por ventanas de 1000 palabras con un intervalo del 95 %. Un texto más corto que la ventana es una sola ventana; las ventanas con valor `nan` se ignoran. Con menos de dos ventanas de valor definido la desviación y el intervalo son `nan`, y sin ninguna también la media. Una métrica infinita en alguna ventana (por ejemplo, el índice de Simpson inverso en una ventana de palabras únicas) hace la media infinita y la desviación y el intervalo `nan`. El resultado es una tupla con nombre `WindowStats` con los campos `mean`, `std`, `lower`, `upper` y `n_windows`, el número de ventanas de valor definido.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `text` | `list[str]` | - | Lista de palabras |
| `func` | `Callable` | - | Función que calcula la métrica a partir de una lista de palabras |
| `window_len` | `int` | `100` | Tamaño de la ventana |
| `step` | `int` | `None` | Paso de la ventana; por defecto, el tamaño de la ventana, así que las ventanas no se solapan |
| `confidence` | `float` | `0.95` | Nivel de confianza |
| `messages` | `dict[str, str]` | `MESSAGES` | Mensajes de los errores por clave |

Un `func` que no es invocable lanza `SourceTypeError`; un `window_len` o un `step` que no es un entero de al menos uno y un `confidence` que no es un número en (0, 1) lanzan `ParameterError`.
