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
        Something other than a string or a Doc was passed, a string or a Doc
        where a list of words is expected, the frequency counter is not a
        Counter, the list of texts is not a list of word lists, the path is
        neither a string nor a Path, the tokenizer or the measure is not
        callable
    """


class SourceError(EstsError, ValueError):
    """
    Unusable data source

    Description:
        The source has no words, sentences, texts, collocations or windows of
        enough words, lacks the annotation a statistic needs (the parts of
        speech, the lemmas, the dependency parse), is a string longer than the
        max_length of the pipeline, has too few texts for the distances or the
        principal components, the matrix of distances is not square or not
        finite, the keyword of a word tree has no context, or nothing is left
        after culling
    """


class ParameterError(EstsError, ValueError):
    """
    Invalid parameter

    Description:
        A threshold, window, segment size, number of items, bound of a
        frequency band or number of bootstrap samples is out of range, the
        sizes of the parts do not add up to the words, the keyword is empty;
        an unknown measure, variant, preset, scale, field, genre or part of
        speech
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
        The model of spaCy is not installed or the dataset files are missing
        from the data directory; the message shows the command that brings
        what is missing
    """


class DataFileError(EstsError, ValueError):
    """
    Dataset file cannot be read

    Description:
        The archive is not a ZIP or TAR archive, cannot be extracted, has no
        files or has paths outside its directory, or the directory to extract
        it into cannot be created
    """


class DownloadError(EstsError, RuntimeError):
    """
    Download failed

    Description:
        The file could not be downloaded, its directory could not be
        created, or it failed the checksum verification twice and was removed
    """
