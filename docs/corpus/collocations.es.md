# Colocaciones

!!! info ""
    **ests.corpus.collocations()**, **ests.corpus.Collocation**

## Descripción

Extracción de colocaciones: pares de palabras que aparecen juntas más a menudo de lo que daría la independencia - expresiones fijas (`punto de vista`, `llevar a cabo`), terminología, la combinatoria de una palabra. Las medidas de asociación son las de [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) y de [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html), y las pruebas las contrastan con NLTK.

Los pares de palabras son ordenados, como en NLTK: la palabra de la derecha aparece a no más de `window` palabras después de la de la izquierda, y cada par de posiciones se cuenta una vez; `window=1` da bigramas. Dentro de la medida la frecuencia del par se divide por el tamaño de la ventana (Church y Hanks 1990, como en NLTK), para que la frecuencia esperada no dependa de la ventana y Dice y la sensibilidad mínima no superen uno; el campo `freq_pair` guarda la frecuencia sin dividir. Con `window > 1` la escala de las medidas de Dice se desplaza por ello: un par siempre contiguo recibe un logDice de $14 - \log_2 window$ - 13 con una ventana de 2, 11.68 con 5 - y no 14, como le dan los bigramas y Sketch Engine, que calcula logDice sobre la coocurrencia sin dividir; el máximo de 14 solo lo alcanza un par que aparece a todas las distancias dentro de la ventana. El parámetro `node` conserva los pares con la palabra dada a la izquierda o a la derecha: la combinatoria de una palabra.

Las palabras se comparan tal cual: la caja, la lematización y las palabras vacías corresponden a [`WordsExtractor`](../extractors/words.md); los lemas convienen a las expresiones fijas, las formas a las construcciones gramaticales.

## Medidas

Para un par de palabras de frecuencias $f_a$ y $f_b$, una frecuencia del par $f_{ab}$ y un número de palabras $N$:

| Medida | Clave | Fórmula | Descripción |
| :----- | :---- | :------ | :---------- |
| Información mutua | `mi` | $\log_2 \frac{f_{ab} N}{f_a f_b}$ | Church y Hanks (1990); sobrevalora los pares raros |
| MI³ | `mi3` | $\log_2 \frac{f_{ab}^3 N}{f_a f_b}$ | Oakes (1998); favorece los pares frecuentes |
| t-score | `t_score` | $\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}$ | Church et al. (1991); favorece los pares frecuentes |
| Coeficiente de Dice | `dice` | $\frac{2 f_{ab}}{f_a + f_b}$ | no depende del tamaño del texto |
| logDice | `logdice` | $14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}$ | [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/); no depende del tamaño del texto, como máximo 14 (con ventana $14 - \log_2 window$), por debajo de cero - un vínculo débil; la medida por defecto, como en Sketch Engine |
| Razón de verosimilitud | `log_likelihood` | $G^2 = 2 \sum O \ln \frac{O}{E}$ | Dunning (1993); sobre la tabla de contingencia 2×2, `nan` si una de las palabras ocupa todo el texto |
| NPMI | `npmi` | $\frac{MI}{-\log_2 (f_{ab} / N)}$ | Bouma (2009); de −1 a 1, uno significa que las palabras solo aparecen juntas |
| Sensibilidad mínima | `min_sensitivity` | $\min(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b})$ | Pedersen (1998); de 0 a 1 |

Las medidas están disponibles como las funciones `calc_mi`, `calc_mi3`, `calc_t_score`, `calc_dice`, `calc_logdice`, `calc_log_likelihood`, `calc_npmi`, `calc_min_sensitivity` con los argumentos `(freq_a, freq_b, freq_ab, n)` del módulo `ests.corpus.collocations` (`from ests.corpus.collocations import calc_logdice`); sus nombres y descripciones están en `ests.constants.COLLOCATION_MEASURES`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `words` | list[str] | `-` | Palabras del texto en orden |
| `window` | int | `5` | Mayor distancia entre las palabras de un par |
| `measure` | str | `logdice` | Medida de `COLLOCATION_MEASURES` |
| `min_freq` | int | `2` | Frecuencia mínima de un par |
| `node` | str | `None` | Palabra cuya combinatoria se busca; `None` - todos los pares |
| `top_n` | int | `None` | Número de colocaciones; `None` - todas |

## Resultado

Una lista de tuplas con nombre `Collocation` por orden descendente de la medida y de la frecuencia del par (los empates, alfabéticamente); `pd.DataFrame(found)` da una tabla.

| Campo | Tipo | Descripción |
| :---: | :--: | :---------- |
| `left` | str | Palabra de la izquierda |
| `right` | str | Palabra de la derecha, dentro de la ventana tras la de la izquierda |
| `freq_left` | int | Frecuencia de la palabra de la izquierda |
| `freq_right` | int | Frecuencia de la palabra de la derecha |
| `freq_pair` | int | Frecuencia de la coocurrencia |
| `score` | float | Valor de la medida elegida |

## Ejemplo

!!! example "Ejemplo"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )

    collocations(words, window=2, top_n=1)
    # [Collocation(left='en', right='ventana', freq_left=3, freq_right=3, freq_pair=3, score=13.0)]

    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="gato", min_freq=1, measure="mi")[:2]
    ]
    # [('gato', 'volver', 3.62), ('gato', 'estar', 2.62)]
    ```
