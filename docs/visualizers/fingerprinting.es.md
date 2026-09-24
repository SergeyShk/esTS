# Huella literaria

!!! info ""
    **ests.visualizers.fingerprinting()**

## Descripción

Visualización de la huella literaria (literature fingerprinting).

!!! note "Nota"
    La huella literaria se describe en detalle en este [artículo](https://www.uni-konstanz.de/mmsp/pubsys/publishedFiles/KeOe07.pdf).

Cada texto se corta en segmentos de `segment_len` palabras con un paso deslizante de una décima parte del segmento, y para cada segmento se calcula una medida de diversidad léxica. Un texto es un bloque de cuadrados en el orden de sus segmentos, fila a fila, de 8 filas de alto, o una sola columna cuando tiene a lo sumo 8 segmentos; un bloque más ancho que una fila del área de dibujo se parte en filas de esa anchura. Los bloques se colocan de izquierda a derecha y pasan a la fila siguiente dentro de un área de `2 · x_size` de ancho, que crece hacia abajo desde `2 · y_size` cuando necesitan más altura, así que nada queda cortado. El color de un cuadrado es el valor de la medida en la escala de la barra de colores, de su menor a su mayor valor finito en todos los textos; el mapa por defecto es secuencial, ya que el punto medio de una medida no significa nada. Los segmentos en los que la medida no está definida (`nan` en segmentos demasiado cortos para ella) y las celdas vacías de un bloque son de un gris claro, distinto de cualquier valor, incluido el cero.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `texts` | list[list[str]] | `-` | Lista de listas de palabras |
| `segment_len` | int | `10` | Tamaño de un segmento |
| `metric` | Callable | `None` | Función de una medida de [diversidad léxica](../stats/diversity_stats.md); `calc_ttr` por defecto |
| `x_size` | int | `800` | Mitad de la anchura del área de dibujo |
| `y_size` | int | `600` | Mitad de la altura del área de dibujo, que crece cuando los bloques necesitan más |
| `cmap` | str | `'viridis'` | Mapa de colores |
| `ax` | Axes | `None` | Ejes de matplotlib para el gráfico; si no se dan, se crea una figura de 15×10 |

La función devuelve los `Axes` con la visualización, con una relación de aspecto igual para que los cuadrados sigan siendo cuadrados; la figura es `ax.figure`.

## Ejemplo de uso

Las cinco primeras ventanas de 1000 palabras de seis novelas del [corpus de literatura](../datasets/spanishliterature.md), tres de Galdós y tres de Unamuno, según el índice de Simpson.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import WordsExtractor
    from ests.corpus import split_windows
    from ests.datasets import SpanishLiterature
    from ests.diversity_stats import calc_simpson_index
    from ests.visualizers import fingerprinting

    sl = SpanishLiterature()
    sl.download()
    titles = (
        "Marianela",
        "Misericordia",
        "Torquemada en la hoguera",
        "Niebla",
        "Abel Sánchez",
        "La tía Tula",
    )
    novels = {
        record["title"]: record["text"]
        for author in ("galdos", "unamuno")
        for record in sl.get_records(author=author)
        if record["title"] in titles
    }

    we = WordsExtractor(lowercase=True)
    texts = [
        we.extract(window) for title in titles for window in split_windows(novels[title], 1000)[:5]
    ]
    fingerprinting(texts, segment_len=100, metric=calc_simpson_index, x_size=1000, y_size=330)
    ```

    _Resultado_:

    ![ests](../img/fingerprinting.png){: .center }

Los quince primeros bloques son de Galdós, los quince últimos de Unamuno. El índice de Simpson - la probabilidad de que dos palabras tomadas al azar sean la misma - es más bajo en Galdós (una mediana de 0.0109 frente a 0.0127 sobre los segmentos), así que sus bloques son más oscuros y los de Unamuno, que repite más sus palabras, más verdes.
