"""
Components of spaCy for the classes of statistics

Description:
    Every component puts an object of a class of statistics into doc._.<name>;
    spaCy does not serialize such objects, so Doc.to_bytes(), DocBin with
    store_user_data=True and nlp.pipe(n_process > 1) do not work with these
    components - leave the user data out when saving, or keep get_stats()
    on your own
    The factories carry the prefix of the library, because the registry of
    spaCy is one for the whole process: a plain basic or morph would collide
    with the component of any other library that registers the same name, and
    spaCy answers a second registration with an error. The name of the pipe,
    which is also the name of the extension, is free: add_pipe(name="basic")
    gives doc._.basic
"""

from spacy.language import Language
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from .diversity_stats import DiversityStats
from .diversity_stats import check_params as check_diversity_params
from .morph_stats import MorphStats
from .readability_stats import ReadabilityStats, check_preset
from .syntax_stats import SyntaxStats


@Language.factory("ests_basic")
class BasicStatsComponent:
    """
    Class for the component of the basic statistics of a text

    Examples:
    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_basic", name="basic", last=True)
        <ests.components.BasicStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato duerme")
        >>> doc._.basic.c_letters
        {2: 1, 4: 1, 6: 1}

    Arguments:
        name (str): Name of the component in the pipeline
    """

    def __init__(self, nlp: Language, name: str = "ests_basic"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        bs = BasicStats(doc)
        doc._.set(self.name, bs)
        return doc


@Language.factory("ests_readability")
class ReadabilityStatsComponent:
    """
    Class for the component of the readability metrics of a text

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_readability", name="readability", last=True)
        <ests.components.ReadabilityStatsComponent object at 0x...>

    Choosing the preset of the coefficients:
        >>> nlp.add_pipe(
        ...     "ests_readability",
        ...     name="readability_classic",
        ...     config={"preset": "classic"},
        ...     last=True,
        ... )
        <ests.components.ReadabilityStatsComponent object at 0x...>

    Reading the computed metrics:
        >>> doc = nlp("El gato duerme en la ventana")
        >>> round(doc._.readability.flesch_reading_easy, 2)
        97.0

    Arguments:
        name (str): Name of the component in the pipeline
        preset (str): Preset of the coefficients (general, classic)

    Raises:
        ParameterError: If the preset is unknown
    """

    def __init__(self, nlp: Language, name: str = "ests_readability", preset: str = "general"):
        check_preset(preset)
        self.name = name
        self.preset = preset
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed metrics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        rs = ReadabilityStats(doc, preset=self.preset)
        doc._.set(self.name, rs)
        return doc


@Language.factory("ests_diversity")
class DiversityStatsComponent:
    """
    Class for the component of the lexical diversity metrics of a text

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_diversity", name="diversity", last=True)
        <ests.components.DiversityStatsComponent object at 0x...>

    Setting the windows, the thresholds and the base of the logarithm:
        >>> nlp.add_pipe(
        ...     "ests_diversity",
        ...     name="diversity_ln",
        ...     config={"window_len": 100, "log_base": 2.718281828459045},
        ...     last=True,
        ... )
        <ests.components.DiversityStatsComponent object at 0x...>

    Reading the computed metrics:
        >>> doc = nlp("El gato duerme")
        >>> doc._.diversity.ttr
        1.0

    Arguments:
        name (str): Name of the component in the pipeline
        window_len (int): Window size for MATTR and segment size for MSTTR
        mtld_threshold (float): TTR threshold for MTLD, MA-MTLD and MTLD-W
        mtld_min_len (int): Minimum factor length for MTLD, MA-MTLD and MTLD-W
        hdd_sample_size (int): Sample size for HD-D
        log_base (float): Logarithm base for the Summer, Maas and Dugast metrics

    Raises:
        ParameterError: If a parameter is out of its range
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ests_diversity",
        window_len: int = MATTR_WINDOW_LEN,
        mtld_threshold: float = MTLD_TTR_THRESHOLD,
        mtld_min_len: int = MTLD_MIN_LEN,
        hdd_sample_size: int = HDD_SAMPLE_SIZE,
        log_base: float = DIVERSITY_LOG_BASE,
    ):
        check_diversity_params(window_len, mtld_threshold, mtld_min_len, hdd_sample_size, log_base)
        self.name = name
        self.window_len = window_len
        self.mtld_threshold = mtld_threshold
        self.mtld_min_len = mtld_min_len
        self.hdd_sample_size = hdd_sample_size
        self.log_base = log_base
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed metrics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        ds = DiversityStats(
            doc,
            window_len=self.window_len,
            mtld_threshold=self.mtld_threshold,
            mtld_min_len=self.mtld_min_len,
            hdd_sample_size=self.hdd_sample_size,
            log_base=self.log_base,
        )
        doc._.set(self.name, ds)
        return doc


@Language.factory("ests_morph")
class MorphStatsComponent:
    """
    Class for the component of the morphological statistics of a text

    Description:
        The parts of speech and the features are read from the annotation of
        the model, so the pipeline needs a tagger before the component

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_morph", name="morph", last=True)
        <ests.components.MorphStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato duerme")
        >>> doc._.morph.pos
        ('DET', 'NOUN', 'VERB')

    Arguments:
        name (str): Name of the component in the pipeline

    Raises:
        SourceError: If the pipeline gives no annotation of the parts of speech
    """

    def __init__(self, nlp: Language, name: str = "ests_morph"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        ms = MorphStats(doc)
        doc._.set(self.name, ms)
        return doc


@Language.factory("ests_syntax")
class SyntaxStatsComponent:
    """
    Class for the component of the syntactic statistics of a text

    Description:
        The statistics are computed on the dependency tree, so the pipeline
        needs a parser before the component

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_syntax", name="syntax", last=True)
        <ests.components.SyntaxStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato duerme en la ventana")
        >>> doc._.syntax.tree_depth
        2.0

    Arguments:
        name (str): Name of the component in the pipeline

    Raises:
        SourceError: If the pipeline gives no parse
    """

    def __init__(self, nlp: Language, name: str = "ests_syntax"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        ss = SyntaxStats(doc)
        doc._.set(self.name, ss)
        return doc


@Language.factory("ests_cohesion")
class CohesionStatsComponent:
    """
    Class for the component of the cohesion statistics of a text

    Description:
        The features are read from the annotation of the model, so the pipeline
        needs a tagger before the component

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_cohesion", name="cohesion", last=True)
        <ests.components.CohesionStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato duerme. El gato come.")
        >>> doc._.cohesion.noun_overlap_adjacent
        1.0

    Arguments:
        name (str): Name of the component in the pipeline

    Raises:
        SourceError: If the pipeline gives no annotation of the parts of speech
    """

    def __init__(self, nlp: Language, name: str = "ests_cohesion"):
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        cs = CohesionStats(doc)
        doc._.set(self.name, cs)
        return doc
