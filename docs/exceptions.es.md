# Excepciones y registro

!!! info ""
    **ests.exceptions**

## Excepciones

Todas las excepciones de la biblioteca heredan de la clase base `EstsError` y de una clase integrada de Python, así que pueden capturarse por cualquiera de las dos, y `except ValueError` sigue funcionando.

| Excepción | Clase integrada | Cuándo se lanza |
| :-------- | :-------------- | :-------------- |
| `EstsError` | `Exception` | Clase base, nunca se lanza directamente |
| `SourceTypeError` | `TypeError` | La fuente no es una cadena ni un `Doc`; el texto de un extractor no es una cadena; se pasa una cadena, un `Doc`, un iterador o un objeto no iterable donde se espera una lista de palabras, o la lista contiene algo que no son cadenas, como tokens de spaCy; los textos de una visualización no son listas de palabras; las frecuencias de `zipf` no son un `Counter`; la medida de `fingerprinting` o el tokenizador no son invocables, o el tokenizador devuelve un objeto no iterable o algo que no son cadenas; una ruta no es una cadena ni un `Path`; las palabras vacías o los clichés (métricas de estilo, resaltado) son una cadena y no una lista; una palabra de las sílabas, de la transcripción o de las palabras vacías no es una cadena; las palabras clave de `keyness_plot`, las colocaciones de `collocation_network` o las concordancias de `format_kwic` no son una lista; las características de `compare_corpora` no son una función |
| `SourceError` | `ValueError` | La fuente no tiene palabras, oraciones, textos ni colocaciones, le falta la anotación que una estadística necesita (categorías gramaticales, lemas, análisis de dependencias), es una cadena más larga que el `max_length` del pipeline (para los sustantivos deverbales, tiene una oración más larga que él) o no queda nada tras el filtrado; Delta o las componentes principales reciben menos de tres textos; una matriz de distancias no es cuadrada o tiene una distancia infinita; el pipeline de `function_words_profile` no etiqueta las categorías gramaticales; ningún texto de una comparación tiene una ventana de palabras suficientes; la palabra clave de `wordtree` no se encuentra o no tiene ninguna palabra al lado |
| `ParameterError` | `ValueError` | No es un entero: una longitud, ventana, paso, número de elementos u otro recuento, aunque sea un float sin decimales. Fuera de rango: un umbral, ventana, tamaño de segmento, número de elementos, base del logaritmo, nivel de confianza, número de muestras bootstrap o límite de una banda de frecuencia (1-10 000); un límite de registros o un límite de longitud de un extractor negativo; partes de `dispersion` que no suman las palabras; una palabra clave de `kwic` vacía. Desconocidos: un preajuste, escala, nombre de métrica, medida, variante, campo de una palabra clave, género o categoría gramatical. Resaltado: una capa desconocida o que la fuente no admite (las capas sintácticas y los sustantivos deverbales en una cadena o en un `Doc` sin el análisis o sin los lemas), capas que no son una lista ni una cadena, un umbral de la aliteración fuera de (0, 1], un número de palabras de una oración larga o de sílabas de una palabra compleja menor que 1. Gráficos: los ejes no son unos `Axes` de matplotlib. Una facilidad de lectura indefinida (`nan`) convertida en un grado; categorías gramaticales de `find_connectors` que no son tantas como las palabras |
| `UnknownStatError` | `ParameterError`, `KeyError` | Se pide por nombre una estadística desconocida, como en `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | El modelo de spaCy no está instalado o un conjunto de datos no está descargado; el mensaje da el comando que lo resuelve |
| `DataFileError` | `ValueError` | El archivo de un conjunto de datos no es ZIP ni TAR, no se puede extraer, está vacío o tiene rutas fuera de su directorio, o su directorio de destino no se puede crear; una línea de un fichero de un conjunto de datos no se puede leer |
| `DownloadError` | `RuntimeError` | El archivo no se pudo descargar o no se pudo crear su directorio, o no superó dos veces la suma de verificación |

Las clases están disponibles desde `ests` y desde `ests.exceptions`. Son las clases del núcleo [anyTS](https://sergeyshk.github.io/anyTS/exceptions/) con los mismos nombres, y `EstsError` es su `AnyTSError`: alias, no subclases, así que `except EstsError` captura también los errores que lanza el código del núcleo, y una traza muestra `anyts.exceptions.SourceTypeError`.

!!! note "Nota"
    `DatasetNotFoundError` suele ser el primer error con el que se topa un usuario nuevo: `MorphStats("El gato duerme")` sin el modelo `es_core_news_sm` la lanza con el comando de descarga. También la lanzan `SpanishLiterature().get_texts()` antes de `download()` y las estadísticas de `LexicalStats` según el diccionario de frecuencias.

!!! example "Ejemplo"

    ``` python
    from ests import EstsError, ParameterError, WordsExtractor

    try:
        WordsExtractor(ngram_range=(2, 1))
    except ParameterError as e:
        print(e)
    # The lower N-gram bound is greater than the upper

    try:
        WordsExtractor(tokenizer=42).extract("El gato duerme.")
    except EstsError as e:
        print(type(e).__name__)
    # SourceTypeError
    ```

## Registro

La biblioteca no imprime nada por su cuenta: sus mensajes van al logger `ests`, que por defecto tiene un `NullHandler`, así que quedan en silencio. Para verlos, configure el registro en su aplicación:

!!! example "Ejemplo"

    ``` python
    import logging

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    ```

Los métodos que imprimen a propósito, como los métodos `print_stats()` de las clases de estadísticas, escriben en la salida estándar; el registro no les afecta.
