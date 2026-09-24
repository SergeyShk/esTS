# Excepciones y registro

!!! info ""
    **ests.exceptions**

## Excepciones

Todas las excepciones de la biblioteca heredan de la clase base `EstsError` y de una de las clases integradas de Python, así que pueden capturarse tanto por su nombre en esTS como por el tipo integrado habitual: el código existente con `except ValueError` sigue funcionando.

| Excepción | Clase integrada | Cuándo se lanza |
| :-------- | :-------------- | :-------------- |
| `EstsError` | `Exception` | Clase base, nunca se lanza directamente |
| `SourceTypeError` | `TypeError` | La fuente de datos no es una cadena ni un `Doc`, se pasa una cadena o un `Doc` donde se espera una lista de palabras, el tokenizador no es invocable o devuelve un objeto no iterable |
| `SourceError` | `ValueError` | La fuente no tiene palabras, oraciones ni textos, le falta la anotación que una estadística necesita (las categorías gramaticales, los lemas, el análisis de dependencias), es una cadena más larga que el `max_length` del pipeline o no queda ninguna unidad tras el filtrado |
| `ParameterError` | `ValueError` | Un umbral, ventana, tamaño de segmento, número de elementos, base del logaritmo o nivel de confianza fuera de rango; un preajuste, escala, nombre de métrica, medida o variante desconocidos |
| `UnknownStatError` | `ParameterError`, `KeyError` | Se pide por nombre una estadística desconocida, como en `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | El modelo de spaCy no está instalado o un conjunto de datos no está descargado; el mensaje muestra el comando que trae lo que falta |
| `DataFileError` | `ValueError` | Un archivo del conjunto de datos está dañado, tiene un formato inesperado o no se puede decodificar |
| `DownloadError` | `RuntimeError` | El archivo no se pudo descargar o no superó la comprobación de la suma de verificación |

Las clases están disponibles desde `ests` y desde `ests.exceptions`.

!!! note "Nota"
    `DatasetNotFoundError` es lo que levanta una estadística de Universal Dependencies cuando el modelo `es_core_news_sm` no está instalado, que es lo primero con lo que se topa un lector nuevo: `MorphStats("El gato duerme")` sin el modelo dice cómo descargarlo. `DataFileError` y `DownloadError` quedan reservadas para los cargadores de conjuntos de datos de las próximas versiones; todavía nada las lanza.

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
