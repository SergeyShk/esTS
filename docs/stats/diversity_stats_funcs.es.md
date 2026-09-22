# Funciones de las métricas

## Type-Token Ratio (TTR)

!!! info ""
    **ests.diversity_stats.calc_ttr()**

Cálculo del Type-Token Ratio (TTR).

La forma más simple y más criticada de calcular la diversidad léxica, que ignora el efecto de la longitud del texto.

Fórmula:

$$
\frac{\textrm{Número de lexemas}}{\textrm{Número de palabras}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Root Type-Token Ratio (RTTR)

!!! info ""
    **ests.diversity_stats.calc_rttr()**

Cálculo del Root Type-Token Ratio (RTTR).

Una modificación del TTR (Guiraud, 1960).

Fórmula:

$$
\frac{\textrm{Número de lexemas}}{\sqrt{\textrm{(Número de palabras)}}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Corrected Type-Token Ratio (CTTR)

!!! info ""
    **ests.diversity_stats.calc_cttr()**

Cálculo del Corrected Type-Token Ratio (CTTR).

Una modificación del TTR (Carroll, 1964).

Fórmula:

$$
\frac{\textrm{Número de lexemas}}{\sqrt{2\times\textrm{(Número de palabras)}}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Herdan Type-Token Ratio (HTTR)

!!! info ""
    **ests.diversity_stats.calc_httr()**

Cálculo del Herdan Type-Token Ratio (HTTR).

Una modificación logarítmica del TTR (Herdan, 1960).

Fórmula:

$$
\frac{\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Summer Type-Token Ratio (STTR)

!!! info ""
    **ests.diversity_stats.calc_sttr()**

Cálculo del Summer Type-Token Ratio (STTR).

Una modificación logarítmica del TTR (Summer, 1966).

!!! note "Nota"
    El valor depende de la base del logaritmo: 10 por defecto, como en koRpus y lexical-diversity; LexicalRichness, textcomplexity y zipfR usan el logaritmo natural. Véanse las [convenciones](diversity_stats.md#conventions).

Fórmula:

$$
\frac{\log_{10} {\log_{10} {\textrm{(Número de lexemas)}}}}{\log_{10} {\log_{10} {{\textrm{(Número de palabras)}}}}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `base` | float | `10` | Base del logaritmo |

## Maas Type-Token Ratio (MTTR)

!!! info ""
    **ests.diversity_stats.calc_mttr()**

Cálculo del Maas Type-Token Ratio (MTTR).

Una modificación logarítmica del TTR (Maas, 1972). La métrica más estable respecto a la longitud del texto.

!!! note "Nota"
    El valor depende de la base del logaritmo: 10 por defecto, como en koRpus y lexical-diversity; LexicalRichness, textcomplexity y zipfR usan el logaritmo natural. Véanse las [convenciones](diversity_stats.md#conventions).

Fórmula:

$$
\frac{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}{\log_{10} {{\textrm{(Número de palabras)}}}^2}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `base` | float | `10` | Base del logaritmo |

## Dugast Type-Token Ratio (DTTR)

!!! info ""
    **ests.diversity_stats.calc_dttr()**

Cálculo del Dugast Type-Token Ratio (DTTR).

Una modificación logarítmica del TTR (Dugast, 1978).

!!! note "Nota"
    El valor depende de la base del logaritmo: 10 por defecto, como en koRpus y lexical-diversity; LexicalRichness, textcomplexity y zipfR usan el logaritmo natural. Véanse las [convenciones](diversity_stats.md#conventions).

Fórmula:

$$
\frac{\log_{10} {{\textrm{(Número de palabras)}}}^2}{\log_{10} {\textrm{(Número de palabras)}}-\log_{10} {\textrm{(Número de lexemas)}}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `base` | float | `10` | Base del logaritmo |

## Moving Average Type-Token Ratio (MATTR)

!!! info ""
    **ests.diversity_stats.calc_mattr()**

Cálculo del Moving Average Type-Token Ratio (MATTR).

Una modificación del TTR con media móvil (Covington & McFall, 2010). Independiente de la longitud del texto.

Algoritmo:

1. Deslizar una ventana de tamaño fijo por el texto
2. Calcular el TTR de cada ventana
3. Promediar los valores

!!! note "Nota"
    La ventana por defecto es de 50 palabras, como en lexical-diversity, TAALED y textacy; quanteda y koRpus usan 100. En los textos más cortos que la ventana se devuelve el TTR de todo el texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `window_len` | int | `50` | Tamaño de la ventana |

## Mean Segmental Type-Token Ratio (MSTTR)

!!! info ""
    **ests.diversity_stats.calc_msttr()**

Cálculo del Mean Segmental Type-Token Ratio (MSTTR).

Una modificación del TTR por segmentación (Johnson, 1944). Independiente de la longitud del texto.

Algoritmo:

1. Dividir el texto en segmentos de tamaño fijo
2. Calcular el TTR de cada segmento
3. Promediar los valores

!!! note "Nota"
    El segmento por defecto es de 50 palabras, como en lexical-diversity, TAALED y textacy; quanteda y koRpus usan 100. En los textos más cortos que el segmento se devuelve el TTR de todo el texto; un último segmento incompleto se descarta.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `segment_len` | int | `50` | Tamaño del segmento |

## Measure of Textual Lexical Diversity (MTLD)

!!! info ""
    **ests.diversity_stats.calc_mtld()**

Cálculo de la Measure of Textual Lexical Diversity (MTLD).

Una modificación del MSTTR (McCarthy, 2005). Independiente de la longitud del texto.

Algoritmo:

1. El texto se divide en factores: tramos en los que el TTR baja hasta el umbral 0.72 inclusive (`TTR <= 0.72`; lexical-diversity y TAALED usan una comparación estricta, véanse las [convenciones](diversity_stats.md#conventions))
2. Un factor incompleto al final del texto cuenta parcialmente, en proporción a lo que su TTR se acercó al umbral
3. El número de palabras se divide por el número de factores

La versión refinada del algoritmo hace dos pasadas por el texto, hacia delante y hacia atrás, y promedia los valores (McCarthy & Jarvis, 2010).

!!! note "Nota"
    La longitud mínima del factor procede de lexical-diversity de Kyle y no es estándar: koRpus la aplica solo a MA-MTLD, LexicalRichness y textcomplexity no la aplican. El umbral 0.72 varía entre 0.66 y 0.75 en la bibliografía. Si ningún factor se completa y el TTR nunca baja de 1, se devuelve infinito.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `min_len` | int | `10` | Longitud mínima del factor |
| `threshold` | float | `0.72` | Umbral de TTR para completar un factor |

## Moving Average Measure of Textual Lexical Diversity (MA-MTLD)

!!! info ""
    **ests.diversity_stats.calc_mamtld()**

Cálculo de la Moving Average Measure of Textual Lexical Diversity (MA-MTLD).

Una modificación de MTLD con ventana móvil (MTLD-MA de koRpus): un factor empieza en cada posición del texto, el valor es la longitud media de los factores completados en dos pasadas, hacia delante y hacia atrás. Los factores no completados al final del texto se ignoran.

!!! warning "Aviso"
    Si ningún factor se completa, la función devuelve `nan`. La métrica es inestable en textos cortos.

Los factores de todos los inicios se calculan a partir de la matriz de apariciones anteriores de cada palabra en bloques de inicios con numpy, en lugar de reconstruir conjuntos de lexemas (`_mtld_factor_lengths`): el número de lexemas de un tramo es el número de posiciones cuya aparición anterior está antes del inicio del tramo. El tiempo es lineal en la longitud del texto; los valores coinciden con la enumeración directa.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `min_len` | int | `10` | Longitud mínima del factor |
| `threshold` | float | `0.72` | Umbral de TTR para completar un factor |

## MTLD con ventana móvil y texto envuelto (MTLD-W)

!!! info ""
    **ests.diversity_stats.calc_mtldw()**

Cálculo de MTLD-W (`mtld_ma_wrap` de lexical-diversity, TAALED).

Una modificación de MA-MTLD: un factor empieza en cada posición del texto, y los factores no completados al final del texto continúan desde su principio, así que todas las posiciones tienen el mismo peso. Un factor no puede ser más largo que el texto.

!!! warning "Aviso"
    Si el TTR no baja hasta el umbral ni siquiera en todo el texto, la función devuelve `nan`. La métrica es inestable en textos de menos de 100 palabras.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `min_len` | int | `10` | Longitud mínima del factor |
| `threshold` | float | `0.72` | Umbral de TTR para completar un factor |

## Hypergeometric Distribution D (HD-D)

!!! info ""
    **ests.diversity_stats.calc_hdd()**

Cálculo de la Hypergeometric Distribution D (HD-D).

La implementación más fiable del algoritmo VocD (McCarthy & Jarvis, 2010).

Algoritmo:

1. Muestreo aleatorio de segmentos de 32 a 50 palabras del texto
2. Cálculo del TTR de cada segmento
3. Promedio de los valores

!!! warning "Aviso"
    En los textos de menos de 50 palabras y más cortos que el tamaño de la muestra la métrica no está definida; la función devuelve `nan`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `sample_size` | int | `42` | Longitud del segmento, de 35 a 50 en la bibliografía |

## Índice de Simpson (D)

!!! info ""
    **ests.diversity_stats.calc_simpson_index()**

Cálculo del [índice de Simpson](https://en.wikipedia.org/wiki/Diversity_index#Simpson_index).

El índice se usa ampliamente en biología para describir la probabilidad de que dos individuos extraídos al azar de una comunidad indefinidamente grande pertenezcan a especies distintas. Con ciertos supuestos describe también la diversidad léxica de un texto.

Se calcula en la forma clásica sin reemplazo, como en quanteda, LexicalRichness y zipfR. Cuanto menor es el valor, más rico es el vocabulario.

!!! warning "Aviso"
    En los textos de menos de dos palabras el índice no está definido; la función devuelve `nan`. Lo mismo vale para el índice de Simpson inverso y el índice de Gini-Simpson.

Fórmula:

$$
\frac{\sum n\times(n-1)}{\textrm{(Número de palabras)}\times(\textrm{Número de palabras}-1)}
$$

donde $n$ es el número de apariciones de un lexema en el texto.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Índice de Simpson inverso (1/D) { #inverse_simpson_index }

!!! info ""
    **ests.diversity_stats.calc_inverse_simpson_index()**

Cálculo del [índice de Simpson inverso](https://en.wikipedia.org/wiki/Diversity_index#Inverse_Simpson_index), el número de Hill de orden dos.

Cuanto mayor es el valor, más rico es el vocabulario.

Fórmula:

$$
\frac{1}{D}
$$

!!! warning "Aviso"
    Si todas las palabras del texto son únicas, el índice de Simpson es 0 y el índice inverso es infinito.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Índice de Gini-Simpson (1-D)

!!! info ""
    **ests.diversity_stats.calc_gini_simpson_index()**

Cálculo del [índice de Gini-Simpson](https://en.wikipedia.org/wiki/Diversity_index#Gini–Simpson_index).

La probabilidad de que dos palabras del texto elegidas al azar sean distintas. Cuanto mayor es el valor, más rico es el vocabulario.

Fórmula:

$$
1-D
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Índice de hápax (R de Honoré)

!!! info ""
    **ests.diversity_stats.calc_hapax_index()**, alias **ests.diversity_stats.calc_honore_r()**

Cálculo del [índice de hápax](https://en.wikipedia.org/wiki/Hapax_legomenon).

!!! quote "Definición"

    Un hápax (del griego ἅπαξ λεγόμενον, «dicho una sola vez») es una palabra que aparece una sola vez en un corpus de textos. Por ejemplo, *baciyelmo*, la bacía-yelmo de Sancho Panza, es un hápax de Cervantes (aparece en un solo capítulo del *Quijote*). El término es popular en los estudios bíblicos, donde se han encontrado varios cientos de palabras así.

Los hápax de un autor se usan a menudo para atribuirle otra obra en la que aparecen esas palabras.

La métrica coincide con la medida de Honoré (1979). Se usa el logaritmo natural, como en zipfR y textcomplexity.

Fórmula:

$$
100\times\frac{\ln {\textrm{(Número de palabras)}}}{1-\frac{\textrm{Número de hápax}}{\textrm{Número de lexemas}}}
$$

!!! warning "Aviso"
    Si todas las palabras del texto son hápax, el índice es infinito. En los textos de menos de dos palabras el índice no está definido; la función devuelve `nan`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Espectro de frecuencias { #frequency_spectrum }

!!! info ""
    **ests.diversity_stats.calc_frequency_spectrum()**

Cálculo del espectro de frecuencias: el número de lexemas $V_i$ que aparecen exactamente $i$ veces en el texto. La base de las medidas de Yule, Herdan, Sichel, Michéa, Baayen y de los modelos LNRE de zipfR. Todas las medidas siguientes se calculan a partir del espectro de frecuencias en tiempo lineal; las fórmulas están contrastadas con Tweedie y Baayen (1998), zipfR, quanteda, koRpus, LexicalRichness y textcomplexity.

Notación: $N$ es el número de palabras, $V$ el número de lexemas, $V_i$ el número de lexemas con frecuencia $i$, $V_1$ los hápax, $V_2$ los dis legomena, $p_k$ la frecuencia relativa de un lexema.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Característica de Yule (K de Yule)

!!! info ""
    **ests.diversity_stats.calc_yule_k()**

Cálculo de la característica de Yule (Yule, 1944). Una de las pocas medidas teóricamente independientes de la longitud del texto (Tweedie & Baayen, 1998); en la práctica converge a medida que el texto crece. Cuanto menor es el valor, más rico es el vocabulario. Proporcional al índice de Simpson: $K \approx 10^4 \cdot D$. Un marcador estilométrico presente en todas las bibliotecas comparables.

Fórmula:

$$
K = 10^4\times\frac{\sum_i i^2 V_i - N}{N^2}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Característica inversa de Yule (I de Yule)

!!! info ""
    **ests.diversity_stats.calc_yule_i()**

Cálculo de la característica inversa de Yule. Cuanto mayor es el valor, más rico es el vocabulario; si todas las palabras del texto son únicas, el valor es infinito.

Fórmula:

$$
I = \frac{V^2}{\sum_i i^2 V_i - V}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Vm de Herdan

!!! info ""
    **ests.diversity_stats.calc_herdan_vm()**

Cálculo de la medida de Herdan (Herdan, 1955). Teóricamente independiente de la longitud del texto; cuanto menor es el valor, más rico es el vocabulario.

Fórmula:

$$
V_m = \sqrt{\sum_i V_i \left(\frac{i}{N}\right)^2 - \frac{1}{V}}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## S de Sichel

!!! info ""
    **ests.diversity_stats.calc_sichel_s()**

Cálculo de la medida de Sichel (Sichel, 1975): la proporción de dis legomena, lexemas con frecuencia 2, entre todos los lexemas. Estable en textos de distinta longitud.

Fórmula:

$$
S = \frac{V_2}{V}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## M de Michéa

!!! info ""
    **ests.diversity_stats.calc_michea_m()**

Cálculo de la medida de Michéa (Michéa, 1969): el recíproco de la medida de Sichel. Si el texto no tiene dis legomena, el valor es infinito.

Fórmula:

$$
M = \frac{V}{V_2}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## W de Brunet

!!! info ""
    **ests.diversity_stats.calc_brunet_w()**

Cálculo de la medida de Brunet (Brunet, 1978). Los valores de los textos suelen estar entre 10 y 20; cuanto menor es el valor, más rico es el vocabulario.

Fórmula:

$$
W = N^{V^{-a}}, \quad a = 0.172
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `a` | float | `0.172` | Exponente |

## k de Dugast

!!! info ""
    **ests.diversity_stats.calc_dugast_k()**

Cálculo de la medida de Dugast (Dugast, 1979). No confundir con la U de Dugast, la métrica [DTTR](#dugast-type-token-ratio-dttr).

!!! note "Nota"
    El valor depende de la base del logaritmo: 10 por defecto, como en las métricas de Summer, Maas y U de Dugast; textcomplexity usa el logaritmo natural. La medida no está definida cuando $\log N \le 1$, es decir, en los textos no más largos que la base del logaritmo; en ese caso la función devuelve `nan`.

Fórmula:

$$
k = \frac{\log V}{\log \log N}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `base` | float | `10` | Base del logaritmo |

## P de Baayen

!!! info ""
    **ests.diversity_stats.calc_baayen_p()**

Cálculo de la medida de Baayen (Baayen, 1991): la proporción de hápax entre todas las palabras del texto. Es la pendiente de la curva de crecimiento del vocabulario al final del texto: la probabilidad de que la siguiente palabra sea nueva (Evert, 2004).

Fórmula:

$$
P = \frac{V_1}{N}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Proporción de hápax { #hapax_ratio }

!!! info ""
    **ests.diversity_stats.calc_hapax_ratio()**

Cálculo de la proporción de hápax entre todos los lexemas del texto.

Fórmula:

$$
\frac{V_1}{V}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## El exponente α₂ { #alpha2 }

!!! info ""
    **ests.diversity_stats.calc_alpha2()**

Cálculo del exponente $\alpha_2$: una estimación del parámetro de Zipf-Mandelbrot a partir de la parte baja del espectro de frecuencias (Evert, 2004). Si el texto no tiene hápax, la función devuelve `nan`.

Fórmula:

$$
\alpha_2 = 1 - \frac{2 V_2}{V_1}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Entropía de Shannon { #entropy }

!!! info ""
    **ests.diversity_stats.calc_entropy()**

Cálculo de la [entropía de Shannon](https://en.wikipedia.org/wiki/Diversity_index#Shannon_index) de la distribución de lexemas en bits. Cuanto mayor es el valor, más rico es el vocabulario. El número de Hill de orden uno es $2^H$ ([perplejidad](#perplexity)), el de orden cero $V$, el de orden dos el [índice de Simpson inverso](#inverse_simpson_index).

Fórmula:

$$
H = -\sum_k p_k \log_2 p_k
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Equitatividad { #evenness }

!!! info ""
    **ests.diversity_stats.calc_evenness()**

Cálculo de la equitatividad (equitatividad de Pielou): el cociente entre la entropía de Shannon y su máximo para el número de lexemas dado. Va de 0 a 1; en los textos de un solo lexema no está definida, la función devuelve `nan`.

Fórmula:

$$
\frac{H}{\log_2 V}
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Perplejidad { #perplexity }

!!! info ""
    **ests.diversity_stats.calc_perplexity()**

Cálculo de la perplejidad: el número de Hill de orden uno, el número efectivo de lexemas del texto.

Fórmula:

$$
2^H
$$

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Pendiente de la ley de Zipf { #zipf_alpha }

!!! info ""
    **ests.diversity_stats.calc_zipf_alpha()**

Cálculo del exponente $\alpha$ de la [ley de Zipf](https://en.wikipedia.org/wiki/Zipf's_law) $f(r) \propto r^{-\alpha}$, donde $r$ es el rango de frecuencia de un lexema. Se estima por regresión lineal del logaritmo de la frecuencia sobre el logaritmo del rango. En los textos naturales $\alpha$ está cerca de 1.

!!! note "Nota"
    La estimación por mínimos cuadrados sobre los rangos está sesgada; para una estimación precisa se usa la máxima verosimilitud (por ejemplo, la biblioteca powerlaw). En los textos de un solo lexema la función devuelve `nan`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Ajuste de Zipf-Mandelbrot { #fit_zipf_mandelbrot }

!!! info ""
    **ests.diversity_stats.fit_zipf_mandelbrot()**, **ests.diversity_stats.ZipfMandelbrot**

Ajuste de la [ley de Zipf-Mandelbrot](https://en.wikipedia.org/wiki/Zipf–Mandelbrot_law) $f(r) = C / (r + q)^s$ a la distribución rango-frecuencia. Con $q = 0$ la ley se reduce a la ley de Zipf con exponente $s$; el desplazamiento $q$ describe el aplanamiento de la curva en las palabras más frecuentes que la ley de Zipf no recoge. Los parámetros se ajustan por mínimos cuadrados en coordenadas logarítmicas (`scipy.optimize.curve_fit`) con la aproximación inicial $C = f(1)$, $q = 1$, $s = 1$ y las restricciones $q \ge 0$, $s \ge 0$. Devuelve una tupla con nombre `ZipfMandelbrot` con los campos `c`, `q`, `s` y `r2`, el coeficiente de determinación del ajuste en coordenadas logarítmicas.

!!! note "Nota"
    En los textos de menos de tres lexemas, con frecuencias idénticas de todos los lexemas y cuando el ajuste diverge, todos los campos son `nan`. En textos cortos los parámetros son inestables: la ley describe la distribución de frecuencias de corpus grandes.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

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

Cálculo del exponente $\beta$ de la [ley de Heaps](https://en.wikipedia.org/wiki/Heaps'_law) $V(N) = K \cdot N^{\beta}$, que describe el crecimiento del vocabulario con la longitud del texto. Se estima por regresión lineal del logaritmo del tamaño del vocabulario sobre el logaritmo de la longitud del texto a lo largo de la curva de crecimiento del vocabulario (`vocabulary_growth`: el tamaño del vocabulario tras cada palabra). En corpus de millones de palabras $\beta$ está entre 0.4 y 0.6; la regresión sobre toda la curva de crecimiento de un solo texto da más (0.6-0.9), porque al principio de un texto casi cada palabra es nueva, así que los valores solo son comparables entre textos de longitud parecida. `fit_heaps` devuelve una tupla con nombre `HeapsFit` con los dos parámetros `k`, `beta` y el coeficiente de determinación `r2`.

!!! note "Nota"
    El valor depende del orden de las palabras y necesita varios cientos de palabras o más. En los textos de menos de dos palabras la función devuelve `nan`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |

## Cálculo por ventanas { #calc_windowed }

!!! info ""
    **ests.diversity_stats.calc_windowed()**

Cálculo por ventanas de cualquier métrica: su valor en ventanas consecutivas del texto de igual longitud, la media, la desviación típica muestral y el intervalo de confianza de la media por la distribución de Student. Es la forma estándar de comparar textos de distinta longitud (`bootstrap` de textcomplexity, las curvas características de koRpus); el STTR de Kubát y Milička es un TTR por ventanas de 1000 palabras con un intervalo de confianza del 95 %. En los textos más cortos que la ventana la métrica se calcula sobre todo el texto como una sola ventana; las ventanas con un valor no definido (`nan`) se ignoran. Si la métrica es infinita en al menos una ventana (por ejemplo, el índice de Simpson inverso en una ventana de palabras únicas), la media es infinita y la desviación típica y el intervalo de confianza no están definidos. Devuelve una tupla con nombre `WindowStats` con los campos `mean`, `std`, `lower`, `upper` y `n_windows`.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `text` | list[str] | `-` | Lista de palabras |
| `func` | callable | `-` | Función que calcula la métrica a partir de una lista de palabras |
| `window_len` | int | `100` | Tamaño de la ventana |
| `step` | int | `None` | Paso de la ventana, por defecto igual a su tamaño |
| `confidence` | float | `0.95` | Nivel de confianza |
