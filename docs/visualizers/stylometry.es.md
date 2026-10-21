# Gráficos estilométricos

!!! info ""
    **ests.visualizers.dendrogram_plot()**, **ests.visualizers.pca_plot()**, **ests.visualizers.mds_plot()**, **ests.visualizers.mendenhall_plot()**

## Descripción

Gráficos para la [estilometría](../corpus/stylometry.md): un dendrograma y el escalamiento multidimensional de la matriz de distancias de [`delta`](../corpus/stylometry.md#delta), las componentes principales de las frecuencias de las palabras más frecuentes y las curvas de Mendenhall de varios textos. Las funciones reciben los ejes `ax` y devuelven `Axes`.

Las funciones son las del núcleo [anyTS](https://sergeyshk.github.io/anyTS/visualizers/stylometry/); las frecuencias de las componentes principales salen de [`frequency_table`](../corpus/stylometry.md#delta) y las curvas de [`mendenhall_curve`](../corpus/stylometry.md#mendenhall). Las etiquetas por defecto son las inglesas de `VISUALIZER_LABELS` en `anyts.constants`; `labels` sustituye cualquiera de ellas.

## Dendrograma { #dendrogram_plot }

<!-- core: visualizers/stylometry.md:dendrogram_plot e3f6319 -->
``` {.python .signature}
dendrogram_plot(distances, method='ward', ax=None, labels=None)
```

Agrupamiento jerárquico con `scipy.cluster.hierarchy` sobre la matriz de distancias entre textos, por defecto con el método de Ward, como en [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf); las hojas se etiquetan con el índice de la matriz. Las columnas se toman en el orden de las filas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `distances` | `DataFrame` | - | Matriz simétrica de distancias con los nombres de los textos en las filas y en las columnas, en cualquier orden |
| `method` | `str` | `'ward'` | Método de `scipy.cluster.hierarchy.linkage` para unir los grupos: `single`, `complete`, `average`, `weighted`, `centroid`, `median` o `ward` |
| `ax` | `Axes` | `None` | Ejes para el gráfico |
| `labels` | `dict[str, str]` | `None` | Etiquetas sobre las de por defecto: `title`, `xlabel` |

Textos distintos en las columnas y en las filas, menos de dos textos, una distancia infinita o negativa, la asimetría o una distancia en la diagonal lanzan `SourceError` antes de crear una figura. Unas distancias que no son un `DataFrame` de números lanzan `SourceTypeError`; un `method` desconocido, unas etiquetas que `merge_labels` rechaza y un `ax` que no es un `Axes` de matplotlib lanzan `ParameterError`.

## Componentes principales { #pca_plot }

<!-- core: visualizers/stylometry.md:pca_plot b21b905 -->
``` {.python .signature}
pca_plot(corpus, n_mfw=100, culling=0.0, ax=None, labels=None)
```

Análisis de componentes principales de las puntuaciones z de las frecuencias relativas de las unidades más frecuentes (`frequency_table`, `z_scores`): los textos en el plano de las dos primeras componentes con sus nombres, y la proporción de la varianza explicada en las etiquetas de los ejes.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `corpus` | `dict[str, list[str]]` | - | Unidades de los textos por los nombres de los textos |
| `n_mfw` | `int` | `100` | Número de las unidades más frecuentes; `None` - todas |
| `culling` | `float` | `0.0` | Menor proporción de textos en la que aparece una unidad |
| `ax` | `Axes` | `None` | Ejes para el gráfico |
| `labels` | `dict[str, str]` | `None` | Etiquetas sobre las de por defecto: `title`, `xlabel` y `ylabel` (cadenas de formato con la proporción explicada `share`) |

El corpus, `n_mfw` y `culling` lanzan los errores de `frequency_table`, y menos de tres textos lanzan `SourceError`; unas etiquetas que `merge_labels` rechaza y un `ax` que no es un `Axes` de matplotlib lanzan `ParameterError`.

## Escalamiento multidimensional { #mds_plot }

<!-- core: visualizers/stylometry.md:mds_plot fee8015 -->
``` {.python .signature}
mds_plot(distances, ax=None, labels=None)
```

Escalamiento multidimensional clásico (Torgerson 1952) de cualquier matriz de distancias: los dos vectores propios principales de las distancias al cuadrado con doble centrado, así que las distancias entre los puntos aproximan las de la matriz. Las columnas se toman en el orden de las filas.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `distances` | `DataFrame` | - | Matriz simétrica de distancias con los nombres de los textos en las filas y en las columnas, en cualquier orden |
| `ax` | `Axes` | `None` | Ejes para el gráfico |
| `labels` | `dict[str, str]` | `None` | Etiquetas sobre las de por defecto: `title`, `xlabel`, `ylabel` |

Textos distintos en las columnas y en las filas, menos de dos textos, una distancia infinita o negativa, la asimetría o una distancia en la diagonal lanzan `SourceError` antes de crear una figura. Unas distancias que no son un `DataFrame` de números lanzan `SourceTypeError`; unas etiquetas que `merge_labels` rechaza y un `ax` que no es un `Axes` de matplotlib lanzan `ParameterError`.

## Curvas de Mendenhall { #mendenhall_plot }

<!-- core: visualizers/stylometry.md:mendenhall_plot 921690d -->
``` {.python .signature}
mendenhall_plot(corpus, ax=None, labels=None)
```

Las proporciones de las palabras por longitud en caracteres (`mendenhall_curve`) de cada texto en un mismo gráfico; una longitud que ninguna palabra tiene se dibuja en cero.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `corpus` | `dict[str, list[str]]` | - | Palabras de los textos por los nombres de los textos |
| `ax` | `Axes` | `None` | Ejes para el gráfico |
| `labels` | `dict[str, str]` | `None` | Etiquetas sobre las de por defecto: `title`, `xlabel`, `ylabel` |

Un corpus que no es un mapeo de listas de cadenas lanza `SourceTypeError`, la falta de textos o un texto sin palabras `SourceError`; unas etiquetas que `merge_labels` rechaza y un `ax` que no es un `Axes` de matplotlib lanzan `ParameterError`.

## Ejemplo de uso

Seis novelas del [corpus de literatura](../datasets/spanishliterature.md), tres de Galdós y tres de Unamuno.

!!! example "Ejemplo"

    _Código_:

    ``` python
    import matplotlib.pyplot as plt

    from ests import WordsExtractor
    from ests.corpus import delta
    from ests.datasets import SpanishLiterature
    from ests.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot

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
    corpus = {title: we.extract(novels[title]) for title in titles}
    distances = delta(corpus, n_mfw=100, variant="cosine")

    # Dendrograma y componentes principales en una figura
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    dendrogram_plot(distances, ax=left)
    pca_plot(corpus, n_mfw=100, ax=right)

    # Escalamiento multidimensional y curvas de Mendenhall
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    mds_plot(distances, ax=left)
    mendenhall_plot(
        {title: corpus[title] for title in ("Marianela", "Niebla", "La tía Tula")}, ax=right
    )
    ```

    _Resultado_:

    ![ests](../img/stylometry.png){: .center }

    ![ests](../img/mds_mendenhall.png){: .center }

La Delta coseno sobre las 100 palabras más frecuentes separa a los autores: el dendrograma une las novelas de cada autor antes de unir los dos grupos, y la primera componente principal pone a Galdós a un lado y a Unamuno al otro. Las curvas de Mendenhall apenas difieren: la longitud de las palabras es un rasgo débil por sí sola.
