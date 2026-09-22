# Spanish Texts Statistics (esTS)
#
# Copyright (C) 2026
# Author: Sergey Shkarin <kouki.sergey@gmail.com>
# URL: <https://github.com/SergeyShk/esTS>

import logging
from importlib.metadata import PackageNotFoundError, version

logging.getLogger(__name__).addHandler(logging.NullHandler())

try:
    __version__ = version("ests")
except PackageNotFoundError:
    __version__ = "0.0.0"
__description__ = (
    "A library for extracting statistics from texts in Spanish. Requires Python 3.11+"
)
__author__ = "Sergey Shkarin"
__author_email__ = "kouki.sergey@gmail.com"

__all__ = ["__version__"]
