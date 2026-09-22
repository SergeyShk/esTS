import logging
from importlib.metadata import version

import pytest

import ests
from ests import EstsError, SentsExtractor, WordsExtractor
from ests.exceptions import (
    DataFileError,
    DatasetNotFoundError,
    DownloadError,
    ParameterError,
    SourceError,
    SourceTypeError,
    UnknownStatError,
)


@pytest.mark.parametrize(
    "exception, builtin",
    [
        (SourceTypeError, TypeError),
        (SourceError, ValueError),
        (ParameterError, ValueError),
        (UnknownStatError, KeyError),
        (DatasetNotFoundError, OSError),
        (DataFileError, ValueError),
        (DownloadError, RuntimeError),
    ],
)
def test_hierarchy(exception, builtin):
    assert issubclass(exception, EstsError)
    assert issubclass(exception, builtin)
    assert getattr(ests, exception.__name__) is exception
    assert exception.__name__ in ests.__all__


def test_raised_classes():
    with pytest.raises(SourceTypeError):
        SentsExtractor(tokenizer=42).extract("El gato duerme.")  # type: ignore
    with pytest.raises(ParameterError):
        WordsExtractor(ngram_range=(0, 1))
    with pytest.raises(ParameterError):
        WordsExtractor().get_most_common(0)


def test_unknown_stat_error_message():
    assert str(UnknownStatError("unknown")) == "unknown"
    assert str(KeyError("unknown")) == "'unknown'"


def test_builtin_compatibility():
    with pytest.raises(ValueError):
        WordsExtractor(min_len=3, max_len=2)
    with pytest.raises(TypeError):
        WordsExtractor(tokenizer=42).extract("El gato duerme.")  # type: ignore
    with pytest.raises(EstsError):
        SentsExtractor(min_len=3, max_len=2)


def test_logging():
    assert any(isinstance(h, logging.NullHandler) for h in logging.getLogger("ests").handlers)


def test_version():
    assert ests.__version__ == version("ests")
    assert "__version__" in ests.__all__
