# Exceptions and logging

!!! info ""
    **ests.exceptions**

## Exceptions

All library exceptions inherit the base class `EstsError` and one of the built-in Python classes, so they can be caught both by their esTS name and by the familiar built-in type - existing code with `except ValueError` keeps working.

| Exception | Built-in class | When raised |
| :-------- | :------------- | :---------- |
| `EstsError` | `Exception` | Base class, never raised itself |
| `SourceTypeError` | `TypeError` | The data source is neither a string nor a `Doc`, a string or a `Doc` is passed where a list of words is expected, the tokenizer is not callable or returns a non-iterable object |
| `SourceError` | `ValueError` | The source has no words, no sentences or no texts, lacks the annotation a statistic needs (the parts of speech, the lemmas, the dependency parse), is a string longer than the `max_length` of the pipeline, or no unit is left after culling |
| `ParameterError` | `ValueError` | A threshold, window, segment size, number of items, logarithm base or confidence level is out of range; an unknown preset, scale, metric name, measure or variant |
| `UnknownStatError` | `ParameterError`, `KeyError` | An unknown statistic is requested by name, as in `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | The model of spaCy is not installed or a dataset is not downloaded; the message shows the command that brings what is missing |
| `DataFileError` | `ValueError` | A dataset file is corrupted, has an unexpected format or cannot be decoded |
| `DownloadError` | `RuntimeError` | The file could not be downloaded or failed the checksum verification |

The classes are available from `ests` and from `ests.exceptions`.

!!! note "Note"
    `DatasetNotFoundError` is what a statistic of Universal Dependencies raises when the model `es_core_news_sm` is not installed, which is the first thing a new reader meets: `MorphStats("El gato duerme")` without the model says how to download it. The datasets raise it too while they are not downloaded (`SpanishLiterature().get_texts()` before `download()`); `DownloadError` comes from a download that failed or an archive that failed its SHA-256 checksum twice, `DataFileError` from an archive that cannot be extracted.

!!! example "Example"

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

## Logging

The library prints nothing on its own: its messages go to the `ests` logger, which has a `NullHandler` by default, so they are silent. To see them, configure logging in your application:

!!! example "Example"

    ``` python
    import logging

    logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")
    ```

Methods that print by design, such as the `print_stats()` methods of the statistics classes, write to standard output; logging does not affect them.
