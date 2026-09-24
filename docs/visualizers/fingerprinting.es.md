# Huella literaria

!!! info ""
    **ests.visualizers.fingerprinting()**

## Descripción

Visualización de la huella literaria (literature fingerprinting).

!!! note "Nota"
    La huella literaria se describe en detalle en este [artículo](https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf).

Cada texto se corta en segmentos de `segment_len` palabras con un paso deslizante de una décima parte del segmento, y para cada segmento se calcula una medida de diversidad léxica; un texto es un bloque de cuadrados, 8 por columna, coloreados por el valor de la medida respecto al mayor de todos los textos. Los segmentos en los que la medida no está definida (`nan` en segmentos demasiado cortos para ella) y las celdas vacías de un bloque se dibujan en negro.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `texts` | list[list[str]] | `-` | Lista de listas de palabras |
| `segment_len` | int | `10` | Tamaño de un segmento |
| `metric` | Callable | `None` | Función de una medida de [diversidad léxica](../stats/diversity_stats.md); `calc_ttr` por defecto |
| `x_size` | int | `800` | Anchura del área de dibujo |
| `y_size` | int | `600` | Altura del área de dibujo |
| `cmap` | str | `'PuOr'` | Mapa de colores |
| `ax` | Axes | `None` | Ejes de matplotlib para el gráfico; si no se dan, se crea una figura de 15×10 |

La función devuelve los `Axes` con la visualización; la figura es `ax.figure`.

## Ejemplo de uso

Las cinco primeras ventanas de 1000 palabras de seis novelas de [Project Gutenberg](https://www.gutenberg.org), tres de Galdós y tres de Unamuno, según el índice de Simpson.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from urllib.request import urlopen

    from ests import WordsExtractor
    from ests.corpus import split_windows
    from ests.diversity_stats import calc_simpson_index
    from ests.visualizers import fingerprinting


    def gutenberg(number):
        url = f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
        text = urlopen(url).read().decode("utf-8")
        start = text.index("\n", text.index("*** START OF"))
        return text[start : text.index("*** END OF")]


    we = WordsExtractor(lowercase=True)
    texts = [
        we.extract(window)
        for number in (17340, 21831, 15206, 49836, 44512, 44358)
        for window in split_windows(gutenberg(number), 1000)[:5]
    ]
    fingerprinting(texts, segment_len=100, metric=calc_simpson_index, x_size=1000, y_size=330)
    ```

    _Resultado_:

    ![ests](../img/fingerprinting.png){: .center }

Los quince primeros bloques son de Galdós, los quince últimos de Unamuno. El índice de Simpson - la probabilidad de que dos palabras tomadas al azar sean la misma - es más bajo en Galdós (una mediana de 0.0107 frente a 0.0117 sobre los segmentos), así que sus bloques son de un naranja más oscuro y los de Unamuno, que repite más sus palabras, más claros.
