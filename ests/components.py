"""
Components of spaCy for the classes of statistics

Description:
    Every component puts an object of a class of statistics into doc._.<name>,
    the name of the pipe: add_pipe("ests_basic", name="basic") gives doc._.basic
    spaCy does not serialize these objects, so Doc.to_bytes(), DocBin with
    store_user_data=True and nlp.pipe(n_process > 1) fail - leave the user data
    out when saving, or keep get_stats() on your own
    The factories are entry points of spacy_factories, so a saved pipeline loads
    with spacy.load() without importing the package
    A document with no words passes untouched, its extension left at None; a
    pipeline without an annotation a component needs raises SourceError, and
    a name taken by an extension of another package raises ParameterError
    Adding a component extends the tokenizer of its pipeline with add_dash_rules
"""

from anyts.components import StatsComponent
from anyts.constants import (
    DIVERSITY_LOG_BASE,
    HDD_SAMPLE_SIZE,
    MATTR_WINDOW_LEN,
    MTLD_MIN_LEN,
    MTLD_TTR_THRESHOLD,
)
from anyts.utils import check_words, iter_doc_tokens
from spacy.language import Language
from spacy.tokens import Doc

from .basic_stats import BasicStats
from .cohesion_stats import CohesionStats
from .constants import NAUSEA_TOP_N, PHON_WINDOW_LEN
from .datasets.freq_dict import FreqDict
from .diversity_stats import DiversityStats, check_params as check_diversity_params
from .lexical_stats import LexicalStats, is_number
from .morph_stats import MorphStats
from .phon_stats import PhonStats, check_params as check_phon_params
from .readability_stats import ReadabilityStats, check_preset
from .style_stats import StyleStats, check_params as check_style_params
from .syntax_stats import SyntaxStats
from .utils import add_dash_rules
from .verse_stats import LETTER, VerseStats


class _Component(StatsComponent):
    """Component of esTS: extends the tokenizer of its pipeline with add_dash_rules"""

    def prepare(self, nlp: Language) -> None:
        add_dash_rules(nlp)


@Language.factory("ests_basic")
class BasicStatsComponent(_Component):
    """
    Class for the component of the basic statistics of a text

    Description:
        Puts a BasicStats object into doc._.<name>

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
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> BasicStats:
        return BasicStats(doc)


@Language.factory("ests_readability")
class ReadabilityStatsComponent(_Component):
    """
    Class for the component of the readability metrics of a text

    Description:
        Puts a ReadabilityStats object into doc._.<name>

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

    Reusing the basic statistics of another component:
        >>> _ = nlp.add_pipe("ests_basic", name="basic", before="readability")
        >>> nlp.add_pipe(
        ...     "ests_readability",
        ...     name="readability_reuse",
        ...     config={"basic": "basic"},
        ...     last=True,
        ... )
        <ests.components.ReadabilityStatsComponent object at 0x...>

    Arguments:
        name (str): Name of the component in the pipeline
        preset (str): Preset of the coefficients (general, classic)
        basic (str): Extension of a component of basic statistics to reuse
            instead of computing them again

    Raises:
        ParameterError: If the preset is unknown
        SourceError: If the named extension holds no basic statistics
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ests_readability",
        preset: str = "general",
        basic: str | None = None,
    ):
        check_preset(preset)
        self.preset = preset
        self.basic = basic
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> ReadabilityStats:
        source: Doc | BasicStats = doc
        if self.basic is not None:
            source = self.from_extension(doc, self.basic, BasicStats, "ests_basic")
        return ReadabilityStats(source, preset=self.preset)


@Language.factory("ests_diversity")
class DiversityStatsComponent(_Component):
    """
    Class for the component of the lexical diversity metrics of a text

    Description:
        Puts a DiversityStats object into doc._.<name>

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
        ParameterError: If a parameter is not an integer where one is expected or is out
            of its range
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
        self.window_len = window_len
        self.mtld_threshold = mtld_threshold
        self.mtld_min_len = mtld_min_len
        self.hdd_sample_size = hdd_sample_size
        self.log_base = log_base
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> DiversityStats:
        return DiversityStats(
            doc,
            window_len=self.window_len,
            mtld_threshold=self.mtld_threshold,
            mtld_min_len=self.mtld_min_len,
            hdd_sample_size=self.hdd_sample_size,
            log_base=self.log_base,
        )


@Language.factory("ests_morph")
class MorphStatsComponent(_Component):
    """
    Class for the component of the morphological statistics of a text

    Description:
        Puts a MorphStats object into doc._.<name>; needs a morphologizer (or
        a tagger with an attribute ruler) and a lemmatizer before it

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
        SourceError: If the pipeline gives no parts of speech or no lemmas
    """

    def __init__(self, nlp: Language, name: str = "ests_morph"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> MorphStats:
        return MorphStats(doc)


@Language.factory("ests_syntax")
class SyntaxStatsComponent(_Component):
    """
    Class for the component of the syntactic statistics of a text

    Description:
        Puts a SyntaxStats object into doc._.<name>; needs a parser and
        a lemmatizer before it

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
        SourceError: If the pipeline gives no parse or no lemmas
    """

    def __init__(self, nlp: Language, name: str = "ests_syntax"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> SyntaxStats:
        return SyntaxStats(doc)


@Language.factory("ests_cohesion")
class CohesionStatsComponent(_Component):
    """
    Class for the component of the cohesion statistics of a text

    Description:
        Puts a CohesionStats object into doc._.<name>; needs a morphologizer (or
        a tagger with an attribute ruler) and a lemmatizer before it

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
        SourceError: If the pipeline gives no parts of speech or no lemmas
    """

    def __init__(self, nlp: Language, name: str = "ests_cohesion"):
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> CohesionStats:
        return CohesionStats(doc)


@Language.factory("ests_lexical")
class LexicalStatsComponent(_Component):
    """
    Class for the component of the lexical sophistication statistics of a text

    Description:
        Puts a LexicalStats object into doc._.<name>; needs a morphologizer (or
        a tagger with an attribute ruler) before it, and the statistics by the
        frequency dictionary need it downloaded

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_lexical", name="lexical", last=True)
        <ests.components.LexicalStatsComponent object at 0x...>

    The dictionary from another directory:
        >>> nlp.add_pipe(
        ...     "ests_lexical", name="lexical_dicts", config={"data_dir": "/path/to/dicts"}, last=True
        ... )
        <ests.components.LexicalStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato estaba en la ventana y miraba a los pájaros")
        >>> round(doc._.lexical.p_top1000, 3)
        0.727

    Arguments:
        name (str): Name of the component in the pipeline
        data_dir (str): Directory of the frequency dictionary; the default one if not given

    Raises:
        SourceError: If the pipeline gives no parts of speech
    """

    def __init__(self, nlp: Language, name: str = "ests_lexical", data_dir: str | None = None):
        self.freq_dict = FreqDict(data_dir) if data_dir else FreqDict()
        super().__init__(nlp, name)

    def accepts(self, doc: Doc) -> bool:
        """A document gets the statistics when it has a word other than a number"""
        return any(not is_number(token.text) for token in iter_doc_tokens(doc))

    def compute(self, doc: Doc) -> LexicalStats:
        return LexicalStats(doc, freq_dict=self.freq_dict)


@Language.factory("ests_style")
class StyleStatsComponent(_Component):
    """
    Class for the component of the style metrics of a text

    Description:
        Puts a StyleStats object into doc._.<name>; the verbal nouns need
        a morphologizer and a lemmatizer before it

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_style", name="style", last=True)
        <ests.components.StyleStatsComponent object at 0x...>

    Setting the stopwords and the number of the most frequent words:
        >>> nlp.add_pipe(
        ...     "ests_style",
        ...     name="style_short",
        ...     config={"stopwords": ["el", "la", "de"], "top_n": 5},
        ...     last=True,
        ... )
        <ests.components.StyleStatsComponent object at 0x...>

    Reading the computed metrics:
        >>> doc = nlp("El gato duerme en la ventana")
        >>> round(doc._.style.water, 2)
        50.0

    Arguments:
        name (str): Name of the component in the pipeline
        stopwords (list[str]): Stopwords for the water content; STOPWORDS and
            the one-word parenthetical expressions if not set
        top_n (int): Number of the most frequent words for the academic nausea
            and the naturalness by Zipf's law

    Raises:
        SourceTypeError: If the stopwords are not a list of strings
        ParameterError: If the number of the most frequent words is not an integer or is
            below one
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ests_style",
        stopwords: list[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
    ):
        check_style_params(top_n)
        if stopwords is not None:
            check_words(stopwords, "stopwords")
        self.stopwords = stopwords
        self.top_n = top_n
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> StyleStats:
        return StyleStats(doc, stopwords=self.stopwords, top_n=self.top_n)


@Language.factory("ests_phon")
class PhonStatsComponent(_Component):
    """
    Class for the component of the phonostatistics of a text

    Description:
        Puts a PhonStats object into doc._.<name>; needs no annotation of a model

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_phon", name="phon", last=True)
        <ests.components.PhonStatsComponent object at 0x...>

    Setting the window of the alliteration and the assonance:
        >>> nlp.add_pipe("ests_phon", name="phon_windowed", config={"window_len": 5}, last=True)
        <ests.components.PhonStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("El gato duerme en la ventana")
        >>> round(doc._.phon.p_vowels, 3)
        0.478

    Arguments:
        name (str): Name of the component in the pipeline
        window_len (int): Window in words for the alliteration and the assonance

    Raises:
        ParameterError: If the window is not an integer or is below 2
    """

    def __init__(self, nlp: Language, name: str = "ests_phon", window_len: int = PHON_WINDOW_LEN):
        check_phon_params(window_len)
        self.window_len = window_len
        super().__init__(nlp, name)

    def compute(self, doc: Doc) -> PhonStats:
        return PhonStats(doc, window_len=self.window_len)


@Language.factory("ests_verse")
class VerseStatsComponent(_Component):
    """
    Class for the component of the verse statistics of a text

    Description:
        Puts a VerseStats object into doc._.<name>; reads the text with its line
        breaks, so a poem goes to nlp with its lines not joined. Needs no
        annotation of a model; a document with no letter passes untouched

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_verse", name="verse", last=True)
        <ests.components.VerseStatsComponent object at 0x...>

    Reading the rhyme with seseo:
        >>> nlp.add_pipe("ests_verse", name="verse_seseo", config={"seseo": True}, last=True)
        <ests.components.VerseStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("Cuando me paro a contemplar mi estado\\ny a ver los pasos por do me han traído")
        >>> doc._.verse.meter, doc._.verse.n_feet
        ('endecasílabo', 11)

    Arguments:
        name (str): Name of the component in the pipeline
        seseo (bool): Pronounce c and z before e and i as s in the rhyme
    """

    def __init__(self, nlp: Language, name: str = "ests_verse", seseo: bool = False):
        self.seseo = seseo
        super().__init__(nlp, name)

    def accepts(self, doc: Doc) -> bool:
        """A document gets the statistics when it has a letter"""
        return LETTER.search(doc.text) is not None

    def compute(self, doc: Doc) -> VerseStats:
        return VerseStats(doc, seseo=self.seseo)
