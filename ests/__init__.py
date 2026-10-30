# Spanish Texts Statistics (esTS)
#
# Copyright (C) 2026
# Author: Sergey Shkarin <kouki.sergey@gmail.com>
# URL: <https://github.com/SergeyShk/esTS>

import logging
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING

from anyts.utils import make_lazy

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
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
from .lexical_stats import LexicalStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .syntax_stats import SyntaxStats
from .unadapted_readability_stats import UnadaptedReadabilityStats
from .verse_stats import VerseStats

if TYPE_CHECKING:
    from .components import (
        BasicStatsComponent as BasicStatsComponent,
        CohesionStatsComponent as CohesionStatsComponent,
        DiversityStatsComponent as DiversityStatsComponent,
        LexicalStatsComponent as LexicalStatsComponent,
        MorphStatsComponent as MorphStatsComponent,
        PhonStatsComponent as PhonStatsComponent,
        ReadabilityStatsComponent as ReadabilityStatsComponent,
        StyleStatsComponent as StyleStatsComponent,
        SyntaxStatsComponent as SyntaxStatsComponent,
        UnadaptedReadabilityStatsComponent as UnadaptedReadabilityStatsComponent,
        VerseStatsComponent as VerseStatsComponent,
    )

logging.getLogger(__name__).addHandler(logging.NullHandler())

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
    "CohesionStats",
    "DataFileError",
    "DatasetNotFoundError",
    "DiversityStats",
    "DownloadError",
    "EstsError",
    "LexicalStats",
    "MorphStats",
    "ParameterError",
    "PhonStats",
    "ReadabilityStats",
    "SentsExtractor",
    "SourceError",
    "SourceTypeError",
    "StyleStats",
    "SyntaxStats",
    "UnadaptedReadabilityStats",
    "UnknownStatError",
    "VerseStats",
    "WordsExtractor",
    "__version__",
]

# The components register the factories of spaCy and import it: the module is loaded on first
# use, or at once when spaCy is loaded already, as it may have read the entry points before
# esTS was installed. The components are out of __all__, so import * and help() load no spaCy;
# a stub of spaCy is no spaCy
if sys.modules.get("spacy.language") is not None:
    from . import components as components

make_lazy(
    __name__,
    dict.fromkeys(
        (
            "BasicStatsComponent",
            "CohesionStatsComponent",
            "DiversityStatsComponent",
            "LexicalStatsComponent",
            "MorphStatsComponent",
            "PhonStatsComponent",
            "ReadabilityStatsComponent",
            "StyleStatsComponent",
            "SyntaxStatsComponent",
            "UnadaptedReadabilityStatsComponent",
            "VerseStatsComponent",
        ),
        "components",
    ),
)
