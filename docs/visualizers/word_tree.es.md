# Árbol de palabras

!!! info ""
    **ests.visualizers.wordtree()**

## Descripción

<!-- core: visualizers/word_tree.md:wordtree c07e802 -->
``` {.python .signature}
wordtree(texts, keyword, max_n=5, max_per_n=8, **kwargs)
```

La construcción de un [árbol de palabras](https://www.weblyzard.com/word-tree/) de los contextos de una palabra clave: en cada lista de palabras, como una oración, se cuentan los N-gramas de hasta `max_n` palabras que empiezan o terminan en la palabra clave. Cada nivel conserva los `max_per_n` N-gramas más frecuentes que continúan uno más corto ya conservado, alfabéticamente si empatan; se unen en dos árboles, tras la palabra clave y ante ella, con el tamaño de la letra según la frecuencia ([Wattenberg y Viégas 2008](https://www.cg.tuwien.ac.at/courses/InfoVis/HallOfFame/2011/Gruppe05/Homepage/Paper/wordtree-paper-wattenberg.pdf)). Para dibujarlo hacen falta los ejecutables de [Graphviz](https://graphviz.org/download/).

La función es la del núcleo [anyTS](https://sergeyshk.github.io/anyTS/visualizers/word_tree/).

## Parámetros

<!-- core: visualizers/word_tree.md:wordtree-parameters 7409f71 -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `texts` | `list[list[str]]` | - | Lista de listas de palabras |
| `keyword` | `str` | - | Palabra clave cuyos contextos se muestran |
| `max_n` | `int` | `5` | Mayor tamaño del contexto |
| `max_per_n` | `int` | `8` | Mayor número de ejemplos para cada tamaño del contexto |
| `**kwargs` | - | - | Parámetros de dibujo: `max_font_size` (por defecto `30`), `min_font_size` (`12`), `font_interp` - una función de la frecuencia relativa de un nodo (su frecuencia entre la mayor, en (0, 1]) que da la parte del intervalo de `min_font_size` a `max_font_size`, de 0 a 1; la raíz cúbica por defecto |

La función devuelve un `Digraph` de graphviz. Unos textos que no son una lista de listas de cadenas y una palabra clave que no es una cadena lanzan `SourceTypeError`; la falta de textos, o una palabra clave sin ninguna palabra a su lado en ninguno de ellos, `SourceError`; un `max_n` que no es un entero de al menos 2 y un `max_per_n` que no es un entero de al menos uno, `ParameterError`.

## Ejemplo de uso

Las oraciones de *Marianela* de Galdós del [corpus de literatura](../datasets/spanishliterature.md).

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import SentsExtractor, WordsExtractor
    from ests.datasets import SpanishLiterature
    from ests.visualizers import wordtree

    sl = SpanishLiterature()
    sl.download()
    text = next(
        record["text"] for record in sl.get_records(author="galdos") if record["title"] == "Marianela"
    )

    we = WordsExtractor(lowercase=True)
    sentences = [we.extract(sentence) for sentence in SentsExtractor().extract(text)]
    graph = wordtree(sentences, "ojos", max_n=4)
    graph.render("wordtree", format="png")
    ```

    _Resultado_:

    ![ests](../img/wordtree.png){: .center }
