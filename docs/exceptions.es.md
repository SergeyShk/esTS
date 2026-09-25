# Excepciones y registro

!!! info ""
    **ests.exceptions**

## Excepciones

Todas las excepciones de la biblioteca heredan de la clase base `EstsError` y de una de las clases integradas de Python, así que pueden capturarse tanto por su nombre en esTS como por el tipo integrado habitual: el código existente con `except ValueError` sigue funcionando.

| Excepción | Clase integrada | Cuándo se lanza |
| :-------- | :-------------- | :-------------- |
| `EstsError` | `Exception` | Clase base, nunca se lanza directamente |
| `SourceTypeError` | `TypeError` | La fuente de datos no es una cadena ni un `Doc`, se pasa una cadena o un `Doc` donde se espera una lista de palabras, los textos de una visualización no son una lista de listas de palabras, las frecuencias de `zipf` no son un `Counter`, la medida de `fingerprinting` o el tokenizador no son invocables, el tokenizador devuelve un objeto no iterable, una ruta no es una cadena ni un `Path` |
| `SourceError` | `ValueError` | La fuente no tiene palabras, oraciones, textos ni colocaciones, le falta la anotación que una estadística necesita (las categorías gramaticales, los lemas, el análisis de dependencias), es una cadena más larga que el `max_length` del pipeline o no queda ninguna unidad tras el filtrado; Delta y las componentes principales reciben menos de tres textos, una matriz de distancias no es cuadrada o tiene una distancia infinita, el pipeline de `function_words_profile` no etiqueta las categorías gramaticales, ningún texto de una comparación tiene una ventana de palabras suficientes, la palabra clave de `wordtree` no se encuentra o no tiene ninguna palabra al lado |
| `ParameterError` | `ValueError` | Un umbral, ventana, tamaño de segmento, número de elementos, base del logaritmo, nivel de confianza, número de muestras bootstrap o límite de una banda de frecuencia (1-10 000) fuera de rango, un límite de registros negativo, los tamaños de las partes de `dispersion` que no suman las palabras, la palabra clave de `kwic` vacía; un preajuste, escala, nombre de métrica, medida, variante, campo de una palabra clave, género o categoría gramatical desconocidos |
| `UnknownStatError` | `ParameterError`, `KeyError` | Se pide por nombre una estadística desconocida, como en `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | El modelo de spaCy no está instalado o un conjunto de datos no está descargado; el mensaje muestra el comando que trae lo que falta |
| `DataFileError` | `ValueError` | El archivo de un conjunto de datos no es un archivo ZIP ni TAR, no se puede extraer, no tiene ficheros o tiene rutas fuera de su directorio, o el directorio donde extraerlo no se puede crear; una línea del fichero de un conjunto de datos no se puede leer |
| `DownloadError` | `RuntimeError` | El archivo no se pudo descargar, su directorio no se pudo crear o no superó dos veces la comprobación de la suma de verificación |

Las clases están disponibles desde `ests` y desde `ests.exceptions`.

!!! note "Nota"
    `DatasetNotFoundError` es lo que levanta una estadística de Universal Dependencies cuando el modelo `es_core_news_sm` no está instalado, que es lo primero con lo que se topa un lector nuevo: `MorphStats("El gato duerme")` sin el modelo dice cómo descargarlo. También la levantan los conjuntos de datos mientras no se han descargado (`SpanishLiterature().get_texts()` antes de `download()`), y las estadísticas de `LexicalStats` según el diccionario de frecuencias; `DownloadError` viene de una descarga fallida o de un archivo que no supera dos veces su suma de comprobación SHA-256, `DataFileError` de un archivo que no se puede extraer.

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
