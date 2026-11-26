from __future__ import annotations

import sys
from collections.abc import Callable, Mapping, Sequence
from typing import TYPE_CHECKING, ClassVar

import anyts.cli
from anyts.constants import CLI_TEXTS
from anyts.stats import Stats

from . import __version__
from .datasets.freq_dict import NAME as FREQ_DICT_NAME, FreqDict
from .report import STATS_CLASSES, Report
from .utils import _annotate_text
from .verse_stats import VerseStats

if TYPE_CHECKING:
    from anyseg import Document
    from anyts.datasets import Dataset


class Command(anyts.cli.Command):
    """
    The command ests: statistics of Spanish texts, an HTML report and the download of the
    frequency dictionary

    Description:
        ests stats prints the statistics of texts from files or the standard
        input as tables, JSON or CSV, by parts with --parts; ests report writes
        the HTML report of a text (Report); ests download downloads the
        frequency dictionary. A text is segmented by anySeg and analyzed by
        esMorph once for all the classes, without spaCy, so the syntax is not
        among them; without --stats the classes of the report are counted, the
        verse statistics (verse) only with --stats

    Methods:
        run: Running the command with arguments, those of the command line by default

    Example:
        >>> from ests.cli import Command
        >>> import pathlib, tempfile
        >>> path = pathlib.Path(tempfile.mkdtemp()) / "gato.txt"
        >>> _ = path.write_text("El gato duerme en la ventana.", encoding="utf-8")
        >>> Command().run(["stats", "-s", "basic", "-f", "json", str(path)])  # doctest: +ELLIPSIS
        {"...gato.txt": {"basic": {"c_letters_2": 3, ..., "n_words": 6, ...}}}
        0
    """

    prog = "ests"
    stats_classes: ClassVar[Mapping[str, type[Stats]]] = {**STATS_CLASSES, "verse": VerseStats}
    default_stats: ClassVar[Sequence[str] | None] = tuple(STATS_CLASSES)
    datasets: ClassVar[Mapping[str, Callable[[], Dataset]]] = {FREQ_DICT_NAME: FreqDict}
    texts: ClassVar[Mapping[str, str]] = {
        **CLI_TEXTS,
        "description": "Statistics of Spanish texts",
    }
    report_class = Report
    version = __version__

    def parse(self, text: str) -> Document:
        """The document of anySeg with the analyses of esMorph in the context of its sentences"""
        return _annotate_text(text)


def main() -> None:
    """Entry point of the command ests"""
    sys.exit(Command().run())
