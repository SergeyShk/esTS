from anyts.exceptions import (
    AnyTSError,
    DataFileError as DataFileError,
    DatasetNotFoundError as DatasetNotFoundError,
    DownloadError as DownloadError,
    ParameterError as ParameterError,
    SourceError as SourceError,
    SourceTypeError as SourceTypeError,
    UnknownStatError as UnknownStatError,
)

# The classes of the core itself, so that an error raised by its code is caught by them too
EstsError = AnyTSError
