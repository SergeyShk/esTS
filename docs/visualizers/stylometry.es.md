# Gráficos estilométricos

!!! info ""
    **ests.visualizers.dendrogram_plot()**, **ests.visualizers.pca_plot()**, **ests.visualizers.mds_plot()**, **ests.visualizers.mendenhall_plot()**

## Descripción

Gráficos para la [estilometría](../corpus/stylometry.md): un dendrograma y el escalamiento multidimensional de la matriz de distancias de [`delta`](../corpus/stylometry.md#delta), las componentes principales de las frecuencias de las palabras más frecuentes y las curvas de Mendenhall de varios textos, el conjunto que usa stylo para ver cómo se agrupan los textos por autor. Las funciones reciben los ejes `ax` y devuelven `Axes`.

## Dendrograma { #dendrogram_plot }

Agrupamiento jerárquico con `scipy.cluster.hierarchy` sobre la matriz de distancias entre textos; el método de Ward por defecto, como en stylo y en [Evert et al. (2015)](https://aclanthology.org/W15-0709.pdf); las etiquetas de las hojas son los nombres de los textos del índice de la matriz.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `distances` | DataFrame | `-` | Matriz simétrica de distancias con los nombres de los textos |
| `method` | str | `ward` | Método de `scipy.cluster.hierarchy.linkage` para unir los grupos |
| `ax` | Axes | `None` | Ejes para el gráfico |

## Componentes principales { #pca_plot }

Análisis de componentes principales de las puntuaciones z de las frecuencias relativas de las unidades más frecuentes ([`frequency_table`](../corpus/stylometry.md#delta), `z_scores`) mediante la descomposición en valores singulares, como `pca.visualization` de stylo: los textos en el plano de las dos primeras componentes con sus nombres, y la proporción de la varianza explicada en las etiquetas de los ejes.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Unidades de los textos por los nombres de los textos |
| `n_mfw` | int | `100` | Número de las unidades más frecuentes; `None` - todas |
| `culling` | float | `0.0` | Menor proporción de textos en la que aparece una unidad |
| `ax` | Axes | `None` | Ejes para el gráfico |

## Escalamiento multidimensional { #mds_plot }

Escalamiento multidimensional clásico (Torgerson 1952) de cualquier matriz de distancias: el doble centrado de la matriz de distancias al cuadrado y los dos vectores propios principales; las distancias entre los puntos aproximan las distancias de la matriz.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `distances` | DataFrame | `-` | Matriz simétrica de distancias con los nombres de los textos |
| `ax` | Axes | `None` | Ejes para el gráfico |

## Curvas de Mendenhall { #mendenhall_plot }

Las proporciones de las palabras por longitud en caracteres ([`mendenhall_curve`](../corpus/stylometry.md#mendenhall)) de cada texto en un mismo gráfico, una comparación de los perfiles de los autores.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `corpus` | dict[str, list[str]] | `-` | Palabras de los textos por los nombres de los textos |
| `ax` | Axes | `None` | Ejes para el gráfico |

## Ejemplo de uso

Seis novelas de [Project Gutenberg](https://www.gutenberg.org), tres de Galdós y tres de Unamuno.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from urllib.request import urlopen

    import matplotlib.pyplot as plt

    from ests import WordsExtractor
    from ests.corpus import delta
    from ests.visualizers import dendrogram_plot, mds_plot, mendenhall_plot, pca_plot


    def gutenberg(number):
        url = f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
        text = urlopen(url).read().decode("utf-8")
        start = text.index("\n", text.index("*** START OF"))
        return text[start : text.index("*** END OF")]


    novels = {
        "Marianela": 17340,
        "Misericordia": 21831,
        "Torquemada": 15206,
        "Niebla": 49836,
        "Abel Sánchez": 44512,
        "La tía Tula": 44358,
    }
    we = WordsExtractor(lowercase=True)
    corpus = {name: we.extract(gutenberg(number)) for name, number in novels.items()}
    distances = delta(corpus, n_mfw=100, variant="cosine")

    # Dendrograma y componentes principales en una figura
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5))
    dendrogram_plot(distances, ax=left)
    pca_plot(corpus, n_mfw=100, ax=right)

    # Escalamiento multidimensional y curvas de Mendenhall
    fig, (left, right) = plt.subplots(1, 2, figsize=(13, 5), layout="constrained")
    mds_plot(distances, ax=left)
    mendenhall_plot({name: corpus[name] for name in ("Marianela", "Niebla", "La tía Tula")}, ax=right)
    ```

    _Resultado_:

    ![ests](../img/stylometry.png){: .center }

    ![ests](../img/mds_mendenhall.png){: .center }

La Delta coseno sobre las 100 palabras más frecuentes separa a los autores: el dendrograma une las novelas de cada autor antes de unir los dos grupos, y la primera componente principal, el 47.8% de la varianza, pone a Galdós a un lado y a Unamuno al otro. Las curvas de Mendenhall apenas difieren: la longitud de las palabras es un rasgo débil por sí sola.
