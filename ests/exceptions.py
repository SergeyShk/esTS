class EstsError(Exception):
    """
    Base exception of the library

    Description:
        Every exception of the library also inherits ValueError, TypeError,
        OSError or RuntimeError and can be caught by it
    """


class SourceTypeError(EstsError, TypeError):
    """
    Wrong type of the data source

    Description:
        The source is neither a string nor a Doc, a string or a Doc is passed
        for a list of words, the frequencies are not a Counter, the texts are
        not lists of words, the path is neither a string nor a Path, the
        tokenizer or the measure is not callable, the stopwords or the clichés
        are a string
    """


class SourceError(EstsError, ValueError):
    """
    Unusable data source

    Description:
        The source has no words, sentences, texts, collocations or windows of
        enough words, lacks an annotation a statistic needs (parts of speech,
        lemmas, parse), is a string longer than the max_length of the pipeline
        (for the verbal nouns, has a sentence longer than it), has too few
        texts for the distances or the principal components; the matrix of
        distances is not square or not finite, the keyword of a word tree has
        no context, or nothing is left after culling
    """


class ParameterError(EstsError, ValueError):
    """
    Invalid parameter

    Description:
        A threshold, window, segment size, number of items, bound of a
        frequency band or number of bootstrap samples is out of range, the
        sizes of the parts do not add up to the words, the keyword is empty;
        an unknown measure, variant, preset, scale, field, genre, part of
        speech or layer of the highlighting, a layer the source does not
        allow, or layers that are neither a list nor a string
    """


class UnknownStatError(ParameterError, KeyError):
    """Unknown name of a statistic"""

    # Without the quotes that KeyError.__str__ adds to the message
    __str__ = Exception.__str__


class DatasetNotFoundError(EstsError, OSError):
    """
    Dataset is not downloaded

    Description:
        The spaCy model is not installed or the dataset files are missing from
        the data directory; the message shows the command that brings them
    """


class DataFileError(EstsError, ValueError):
    """
    Dataset file cannot be read

    Description:
        The archive is not a ZIP or TAR archive, cannot be extracted, has no
        files or has paths outside its directory, or its target directory
        cannot be created; a line of a dataset file cannot be read
    """


class DownloadError(EstsError, RuntimeError):
    """
    Download failed

    Description:
        The file cannot be downloaded, its directory cannot be created, or it
        failed the checksum verification twice and was removed
    """
