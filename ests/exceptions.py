class EstsError(Exception):
    """
    Base exception of the library

    Description:
        Every esTS exception inherits it together with one of the built-in
        classes, so it can be caught both by its own name and by the familiar
        ValueError, TypeError, OSError or RuntimeError
    """


class SourceTypeError(EstsError, TypeError):
    """
    Wrong type of the data source

    Description:
        Something other than a string or a Doc was passed, the frequency
        counter is not a Counter, the list of texts is not a list of word
        lists, the path is neither a string nor a Path, the tokenizer
        is not callable
    """


class SourceError(EstsError, ValueError):
    """
    Unusable data source

    Description:
        The source has no words, sentences, texts or collocations, lacks
        the needed annotation (a dependency parse) or nothing is left
        after culling
    """


class ParameterError(EstsError, ValueError):
    """
    Invalid parameter

    Description:
        A threshold, window, segment size or number of items is out of range;
        an unknown measure, variant, preset, layer, stage or dataset category
    """


class UnknownStatError(ParameterError, KeyError):
    """
    Unknown name of a statistic

    Description:
        The message goes without the quotes that KeyError.__str__ adds
    """

    __str__ = Exception.__str__


class DatasetNotFoundError(EstsError, OSError):
    """
    Dataset is not downloaded

    Description:
        The dataset files are missing from the data directory; the message
        shows the download command
    """


class DataFileError(EstsError, ValueError):
    """
    Dataset file cannot be read

    Description:
        The file is corrupted, has an unexpected format or cannot be decoded
        in any of the supported encodings
    """


class DownloadError(EstsError, RuntimeError):
    """
    Download failed

    Description:
        The file could not be downloaded or failed the checksum verification
        and was removed
    """
