# Excepciones y registro

!!! info ""
    **ests.exceptions**

## Excepciones

Todas las excepciones de la biblioteca heredan de la clase base `EstsError` y de una de las clases integradas de Python, así que pueden capturarse tanto por su nombre en esTS como por el tipo integrado habitual: el código existente con `except ValueError` sigue funcionando.

| Excepción | Clase integrada | Cuándo se lanza |
| :-------- | :-------------- | :-------------- |
| `EstsError` | `Exception` | Clase base, nunca se lanza directamente |
| `SourceTypeError` | `TypeError` | La fuente de datos no es una cadena ni un `Doc`, el contador de frecuencias no es un `Counter`, la lista de textos no es una lista de listas, la ruta no es una cadena ni un `Path`, el tokenizador no es invocable o devuelve un objeto no iterable |
| `SourceError` | `ValueError` | La fuente no tiene palabras, oraciones, textos ni colocaciones, carece de análisis de dependencias o no queda nada tras el filtrado |
| `ParameterError` | `ValueError` | Un umbral, ventana, tamaño de segmento o número de elementos fuera de rango; una medida, variante, preajuste, capa, nivel o categoría de conjunto de datos desconocidos |
| `UnknownStatError` | `ParameterError`, `KeyError` | Se pide por nombre una estadística desconocida |
| `DatasetNotFoundError` | `OSError` | El conjunto de datos no está descargado; el mensaje muestra el comando de descarga |
| `DataFileError` | `ValueError` | Un archivo del conjunto de datos está dañado, tiene un formato inesperado o no se puede decodificar |
| `DownloadError` | `RuntimeError` | El archivo no se pudo descargar o no superó la comprobación de la suma de verificación |

Las clases están disponibles desde `ests` y desde `ests.exceptions`.

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
