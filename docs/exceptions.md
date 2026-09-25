# Exceptions and logging

!!! info ""
    **ests.exceptions**

## Exceptions

All library exceptions inherit the base class `EstsError` and one of the built-in Python classes, so they can be caught both by their esTS name and by the familiar built-in type - existing code with `except ValueError` keeps working.

| Exception | Built-in class | When raised |
| :-------- | :------------- | :---------- |
| `EstsError` | `Exception` | Base class, never raised itself |
| `SourceTypeError` | `TypeError` | The data source is neither a string nor a `Doc`, a string or a `Doc` is passed where a list of words is expected, the texts of a visualizer are not a list of lists of words, the frequencies of `zipf` are not a `Counter`, the measure of `fingerprinting` or the tokenizer is not callable, the tokenizer returns a non-iterable object, a path is neither a string nor a `Path` |
| `SourceError` | `ValueError` | The source has no words, no sentences, no texts or no collocations, lacks the annotation a statistic needs (the parts of speech, the lemmas, the dependency parse), is a string longer than the `max_length` of the pipeline, or no unit is left after culling; Delta and the principal components get fewer than three texts, a matrix of distances is not square or has an infinite distance, the pipeline of `function_words_profile` does not tag the parts of speech, no text of a comparison has a window of enough words, the keyword of `wordtree` is not found or has no word next to it |
| `ParameterError` | `ValueError` | A threshold, window, segment size, number of items, logarithm base, confidence level, number of bootstrap samples or bound of a frequency band (1-10,000) is out of range, a limit of records is negative, the sizes of the parts of `dispersion` do not add up to the words, the keyword of `kwic` is empty; an unknown preset, scale, metric name, measure, variant, field of a keyword, genre or part of speech |
| `UnknownStatError` | `ParameterError`, `KeyError` | An unknown statistic is requested by name, as in `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | The model of spaCy is not installed or a dataset is not downloaded; the message shows the command that brings what is missing |
| `DataFileError` | `ValueError` | The archive of a dataset is not a ZIP or TAR archive, cannot be extracted, has no files or has paths outside its directory, or the directory to extract it into cannot be created; a line of the file of a dataset cannot be read |
| `DownloadError` | `RuntimeError` | The file could not be downloaded, its directory could not be created, or it failed the checksum verification twice |

The classes are available from `ests` and from `ests.exceptions`.

!!! note "Note"
    `DatasetNotFoundError` is what a statistic of Universal Dependencies raises when the model `es_core_news_sm` is not installed, which is the first thing a new reader meets: `MorphStats("El gato duerme")` without the model says how to download it. The datasets raise it too while they are not downloaded (`SpanishLiterature().get_texts()` before `download()`), and so do the statistics of `LexicalStats` by the frequency dictionary; `DownloadError` comes from a download that failed or an archive that failed its SHA-256 checksum twice, `DataFileError` from an archive that cannot be extracted.

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
