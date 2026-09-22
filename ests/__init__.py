# Spanish Texts Statistics (esTS)
#
# Copyright (C) 2026
# Author: Sergey Shkarin <kouki.sergey@gmail.com>
# URL: <https://github.com/SergeyShk/esTS>

import logging
from importlib.metadata import PackageNotFoundError, version

from .basic_stats import BasicStats
from .diversity_stats import DiversityStats
from .exceptions import (
    DataFileError,
    DatasetNotFoundError,
    DownloadError,
    EstsError,
    ParameterError,
    SourceError,
    SourceTypeError,
    UnknownStatError,
)
from .extractors import CharNgramsExtractor, SentsExtractor, WordsExtractor
from .readability_stats import ReadabilityStats

logging.getLogger(__name__).addHandler(logging.NullHandler())

# Metadata

# The distribution is pyests, the package it installs is ests
try:
    __version__ = version("pyests")
except PackageNotFoundError:
    __version__ = "0.0.0"
__description__ = (
    "A library for extracting statistics from texts in Spanish. Requires Python 3.11+"
)
__author__ = "Sergey Shkarin"
__author_email__ = "kouki.sergey@gmail.com"

__all__ = [
    "BasicStats",
    "CharNgramsExtractor",
    "DataFileError",
    "DatasetNotFoundError",
    "DiversityStats",
    "DownloadError",
    "EstsError",
    "ParameterError",
    "ReadabilityStats",
    "SentsExtractor",
    "SourceError",
    "SourceTypeError",
    "UnknownStatError",
    "WordsExtractor",
    "__version__",
]
