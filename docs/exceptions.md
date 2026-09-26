# Exceptions and logging

!!! info ""
    **ests.exceptions**

## Exceptions

All library exceptions inherit the base class `EstsError` and a built-in Python class, so they can be caught by either, and `except ValueError` keeps working.

| Exception | Built-in class | When raised |
| :-------- | :------------- | :---------- |
| `EstsError` | `Exception` | Base class, never raised itself |
| `SourceTypeError` | `TypeError` | The source is not a string or a `Doc`; a string or a `Doc` is passed where a list of words is expected; the texts of a visualizer are not lists of words; the frequencies of `zipf` are not a `Counter`; the measure of `fingerprinting` or the tokenizer is not callable, or the tokenizer returns a non-iterable; a path is not a string or a `Path`; the stopwords or the clichés (style metrics, highlighting) are a string, not a list |
| `SourceError` | `ValueError` | The source has no words, sentences, texts or collocations, lacks the annotation a statistic needs (parts of speech, lemmas, dependency parse), is a string longer than the `max_length` of the pipeline (for the verbal nouns, has a sentence longer than it), or nothing is left after culling; Delta or the principal components get fewer than three texts; a matrix of distances is not square or has an infinite distance; the pipeline of `function_words_profile` does not tag parts of speech; no text of a comparison has a window of enough words; the keyword of `wordtree` is not found or has no word next to it |
| `ParameterError` | `ValueError` | Out of range: a threshold, window, segment size, number of items, logarithm base, confidence level, number of bootstrap samples or bound of a frequency band (1-10,000); a negative limit of records; parts of `dispersion` that do not add up to the words; an empty keyword of `kwic`. Unknown: a preset, scale, metric name, measure, variant, keyword field, genre or part of speech. Highlighting: an unknown layer or one the source does not allow (syntactic layers and verbal nouns on a string or on a `Doc` without the parse or the lemmas), layers that are neither a list nor a string, an alliteration threshold outside (0, 1], a number of words of a long sentence or of syllables of a complex word below 1 |
| `UnknownStatError` | `ParameterError`, `KeyError` | An unknown statistic is requested by name, as in `DiversityStats.windowed` |
| `DatasetNotFoundError` | `OSError` | The spaCy model is not installed or a dataset is not downloaded; the message gives the command that fixes it |
| `DataFileError` | `ValueError` | The archive of a dataset is not ZIP or TAR, cannot be extracted, is empty or has paths outside its directory, or its target directory cannot be created; a line of a dataset file cannot be read |
| `DownloadError` | `RuntimeError` | The file could not be downloaded or its directory created, or it failed the checksum twice |

The classes are available from `ests` and from `ests.exceptions`.

!!! note "Note"
    `DatasetNotFoundError` is the first error a new user usually meets: `MorphStats("El gato duerme")` without the model `es_core_news_sm` raises it with the download command. `SpanishLiterature().get_texts()` before `download()` and the statistics of `LexicalStats` by the frequency dictionary raise it too.

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
