# Árbol de palabras

!!! info ""
    **ests.visualizers.wordtree()**

## Descripción

La construcción de un [árbol de palabras](https://www.weblyzard.com/word-tree/) que muestra los contextos de una palabra clave en un texto: en cada lista de palabras - una oración, por ejemplo - se cuentan los N-gramas de hasta `max_n` palabras que empiezan o terminan en la palabra clave. A cada lado los tamaños se recorren en orden ascendente, y entre los N-gramas que continúan uno más corto ya conservado se conservan los `max_per_n` más frecuentes, alfabéticamente si empatan, así que cada nivel del árbol tiene a lo sumo `max_per_n` palabras y cada rama continúa una conservada. Los N-gramas conservados se unen en dos árboles, las palabras tras la palabra clave y ante ella, con el tamaño de la letra según la frecuencia; las palabras son solo las etiquetas de los nodos, así que dos puntos o un guion en una palabra no dan problemas.

!!! note "Nota"
    El árbol de palabras se describe en detalle en este [artículo](https://www.cg.tuwien.ac.at/courses/InfoVis/HallOfFame/2011/Gruppe05/Homepage/Paper/wordtree-paper-wattenberg.pdf).

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `texts` | list[list[str]] | `-` | Lista de listas de palabras |
| `keyword` | str | `-` | Palabra clave cuyos contextos se muestran |
| `max_n` | int | `5` | Mayor tamaño del contexto |
| `max_per_n` | int | `8` | Mayor número de ejemplos para cada tamaño del contexto |
| `**kwargs` | - | `-` | Parámetros de dibujo: `max_font_size` (por defecto `30`), `min_font_size` (`12`), `font_interp` - una función que interpola el tamaño de la letra a partir de la frecuencia |

La función devuelve un `Digraph` de graphviz.

## Ejemplo de uso

Las oraciones de *Marianela* de Galdós de [Project Gutenberg](https://www.gutenberg.org).

!!! example "Ejemplo"

    _Código_:

    ``` python
    from urllib.request import urlopen

    from ests import SentsExtractor, WordsExtractor
    from ests.visualizers import wordtree

    url = "https://www.gutenberg.org/cache/epub/17340/pg17340.txt"
    text = urlopen(url).read().decode("utf-8")
    text = text[text.index("\n", text.index("*** START OF")) : text.index("*** END OF")]

    we = WordsExtractor(lowercase=True)
    sentences = [we.extract(sentence) for sentence in SentsExtractor().extract(text)]
    graph = wordtree(sentences, "ojos", max_n=4)
    graph.render("wordtree", format="png")
    ```

    _Resultado_:

    ![ests](../img/wordtree.png){: .center }

!!! warning "Advertencia"
    Para dibujar el árbol hacen falta los ejecutables de [Graphviz](https://graphviz.org/download/).
