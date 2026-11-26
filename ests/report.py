from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, ClassVar

import anyts.report
from anyts.stats import Stats

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .diversity_stats import DiversityStats
from .lexical_stats import LexicalStats
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .readability_stats import ReadabilityStats
from .style_stats import StyleStats
from .unadapted_readability_stats import UnadaptedReadabilityStats
from .utils import _annotate_text, get_document
from .visualizers.highlight import HighlightedText

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.tokens import Doc

STATS_CLASSES: Mapping[str, type[Stats]] = {
    "basic": BasicStats,
    "readability": ReadabilityStats,
    "unadapted_readability": UnadaptedReadabilityStats,
    "diversity": DiversityStats,
    "morph": MorphStats,
    "lexical": LexicalStats,
    "style": StyleStats,
    "phon": PhonStats,
    "cohesion": CohesionStats,
}
STATS_TITLES: Mapping[str, str] = {
    "basic": "Basic statistics",
    "readability": "Readability metrics",
    "unadapted_readability": "Formulas of other languages",
    "diversity": "Lexical diversity metrics",
    "morph": "Morphological statistics",
    "lexical": "Lexical sophistication statistics",
    "style": "Style metrics",
    "phon": "Phonostatistics",
    "cohesion": "Cohesion statistics",
    "verse": "Verse statistics",
}


class Report(anyts.report.Report):
    """
    HTML report of the statistics of a Spanish text

    Description:
        One HTML file without external resources: the statistics of every
        class with their descriptions and readings by the scales (describe),
        the statistics of every sentence, the highlighted text and the plots.
        A string is segmented by anySeg and analyzed by esMorph in the context
        of its sentences once, and every class counts its document; the
        cohesion reads that document without a dependency parse, and the verse
        statistics are counted only when stats_classes names them

    Arguments:
        source (str|Doc|Document): Data source
        title (str): Title of the report; "Text statistics" by default
        stats_classes (dict[str, type[Stats]]): Classes of statistics by name;
            STATS_CLASSES by default
        skip_errors (bool): Leave out a class that cannot count the source, with its
            error in errors, instead of raising it

    Attributes:
        document (Document): Document of the source
        title (str): Title of the report
        stats (dict[str, Stats]): Statistics of every class by name
        errors (dict[str, EstsError]): Errors of the classes left out with skip_errors

    Methods:
        to_html: Getting the report as one HTML page
        save: Writing the report to a file in UTF-8

    Raises:
        ParameterError: If skip_errors is not a bool or stats_classes is not a mapping of
            classes of statistics
        SourceTypeError, SourceError: As the classes of statistics, without skip_errors

    Example:
        >>> from ests.report import Report
        >>> text = "El gato duerme en la ventana. El perro ladra en el patio."
        >>> report = Report(text, title="Dos oraciones", skip_errors=True)
        >>> page = report.to_html()
        >>> page.startswith("<!DOCTYPE html>"), report.stats["basic"].n_words
        (True, 12)
    """

    stats_classes: ClassVar[Mapping[str, type[Stats]]] = STATS_CLASSES
    titles: ClassVar[Mapping[str, str]] = STATS_TITLES
    # The first column picks the hard sentences: characters are closer than words to how
    # readers rate them
    sentence_columns: ClassVar[Sequence[tuple[str, str]]] = (
        ("basic", "n_chars"),
        ("basic", "n_words"),
        ("basic", "n_syllables"),
        ("readability", "flesch_reading_easy"),
        ("style", "water"),
    )
    highlight_class = HighlightedText

    def parse(self, source: str | Doc | Document) -> Document:
        """The document of anySeg (ests.utils.get_document), a string with the analyses of
        esMorph in the context of its sentences"""
        if isinstance(source, str):
            return _annotate_text(source)
        return get_document(source)
