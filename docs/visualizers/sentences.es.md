# Longitudes de las oraciones

!!! info ""
    **ests.visualizers.sentence_lengths_plot()**, **ests.visualizers.sentence_lengths()**

## Descripción

La curva de las longitudes de las oraciones, el ritmo de un texto: la longitud de cada oración en palabras en orden, la media móvil sobre una ventana de `window` oraciones y un recuadro con el histograma de las longitudes. Oraciones cortas y largas que se alternan son un signo editorial de un texto vivo; una curva plana, de uno monótono. `sentence_lengths` extrae las longitudes: las oraciones de una cadena salen de [`SentsExtractor`](../extractors/sentences.md) con las mismas reglas - los signos de apertura, las rayas de un diálogo, las abreviaturas - y una palabra pertenece a la oración en la que empieza; las oraciones de un `Doc` salen de sus límites (sin ellos, de su texto); las longitudes ya hechas - cualquier secuencia de enteros, incluidos un array de numpy y una Series - se usan tal cual; las oraciones sin palabras se omiten. La función recibe los ejes `ax` y devuelve `Axes`.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc/Iterable[int] | `-` | Texto, objeto Doc o longitudes de las oraciones (una lista, un array de numpy, una Series) |
| `window` | int | `10` | Ventana de la media móvil en oraciones |
| `inset` | bool | `True` | Mostrar el recuadro con el histograma |
| `ax` | Axes | `None` | Ejes para el gráfico |

## Ejemplo de uso

La segunda ventana de 2000 palabras de *Niebla* de Unamuno del [corpus de literatura](../datasets/spanishliterature.md); una ventana se corta por palabras, así que empieza con el final de una oración.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests.corpus import split_windows
    from ests.datasets import SpanishLiterature
    from ests.visualizers import sentence_lengths, sentence_lengths_plot

    sl = SpanishLiterature()
    sl.download()
    text = next(
        record["text"] for record in sl.get_records(author="unamuno") if record["title"] == "Niebla"
    )
    chapter = split_windows(text, 2000)[1]

    sentence_lengths(chapter)[:5]
    # [2, 26, 30, 41, 41]

    sentence_lengths_plot(chapter, window=10)
    ```

    _Resultado_:

    ![ests](../img/sentences.png){: .center }
