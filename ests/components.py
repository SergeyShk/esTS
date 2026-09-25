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
    The factories are declared as entry points of spacy_factories, so a
    pipeline saved with these components loads with spacy.load() in a process
    that never imports this package
    A document with no words - an empty string, whitespace, punctuation alone -
    passes through every component untouched, its extension left at None, so
    that one such document in a corpus does not stop nlp.pipe. A pipeline that
    gives no annotation a component needs is another matter: that is an error
    of the pipeline, and it is raised
    Adding a component extends the tokenizer of its pipeline with the rules for
    the dashes of a dialogue (add_dash_rules), which the string API has, so the
    words of a component are the words of the rest of the library: sí--dijo is
    two words and a dash, not one word
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
    NAUSEA_TOP_N,
    PHON_WINDOW_LEN,
)
from .datasets.freq_dict import FreqDict
from .diversity_stats import DiversityStats
from .diversity_stats import check_params as check_diversity_params
from .exceptions import SourceError
from .lexical_stats import LexicalStats, is_number
from .morph_stats import MorphStats
from .phon_stats import PhonStats
from .phon_stats import check_params as check_phon_params
from .readability_stats import ReadabilityStats, check_preset
from .style_stats import StyleStats
from .style_stats import check_params as check_style_params
from .syntax_stats import SyntaxStats
from .utils import add_dash_rules, has_words, iter_doc_tokens
from .verse_stats import LETTER, VerseStats


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
        add_dash_rules(nlp)
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
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

    Taking the basic statistics from a component that already computed them,
    instead of computing them a second time:
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
        basic (str): Name of the extension of a component of basic statistics,
            whose object is used instead of computing them again

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
        add_dash_rules(nlp)
        self.name = name
        self.preset = preset
        self.basic = basic
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed metrics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        rs = ReadabilityStats(self.__source(doc), preset=self.preset)
        doc._.set(self.name, rs)
        return doc

    def __source(self, doc: Doc) -> Doc | BasicStats:
        """
        Source of the metrics: the basic statistics of another component or the document

        Arguments:
            doc (Doc): Doc object

        Returns:
            Doc|BasicStats: Source of the metrics

        Raises:
            SourceError: If the named extension holds no basic statistics
        """
        if self.basic is None:
            return doc
        stats = doc._.get(self.basic) if Doc.has_extension(self.basic) else None
        if not isinstance(stats, BasicStats):
            raise SourceError(
                f"The extension {self.basic} holds no basic statistics: add the component "
                f"ests_basic with the name {self.basic} before {self.name}"
            )
        return stats


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
        add_dash_rules(nlp)
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

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
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
        the model, so the pipeline needs a morphologizer (or a tagger with an
        attribute ruler) and a lemmatizer before the component

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
        add_dash_rules(nlp)
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        ms = MorphStats(doc)
        doc._.set(self.name, ms)
        return doc


@Language.factory("ests_syntax")
class SyntaxStatsComponent:
    """
    Class for the component of the syntactic statistics of a text

    Description:
        The statistics are computed on the dependency tree, so the pipeline
        needs a parser and a lemmatizer before the component

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
        add_dash_rules(nlp)
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        ss = SyntaxStats(doc)
        doc._.set(self.name, ss)
        return doc


@Language.factory("ests_cohesion")
class CohesionStatsComponent:
    """
    Class for the component of the cohesion statistics of a text

    Description:
        The features are read from the annotation of the model, so the pipeline
        needs a morphologizer (or a tagger with an attribute ruler) and a
        lemmatizer before the component

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
        add_dash_rules(nlp)
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        cs = CohesionStats(doc)
        doc._.set(self.name, cs)
        return doc


@Language.factory("ests_lexical")
class LexicalStatsComponent:
    """
    Class for the component of the lexical sophistication statistics of a text

    Description:
        The words are looked up by their parts of speech, so the pipeline needs
        a morphologizer (or a tagger with an attribute ruler) before the
        component. The frequency dictionary is created once for the component;
        the statistics by the dictionary need it downloaded

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
        add_dash_rules(nlp)
        self.name = name
        self.freq_dict = FreqDict(data_dir) if data_dir else FreqDict()
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words - numbers are no words here - is
            returned untouched, its extension left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not any(not is_number(token.text) for token in iter_doc_tokens(doc)):
            return doc
        ls = LexicalStats(doc, freq_dict=self.freq_dict)
        doc._.set(self.name, ls)
        return doc


@Language.factory("ests_style")
class StyleStatsComponent:
    """
    Class for the component of the style metrics of a text

    Description:
        The SEO metrics and the markers of the officialese style read the words
        of the document; the verbal nouns read its parts of speech and lemmas,
        so the pipeline needs a morphologizer and a lemmatizer before the
        component for them

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
        ParameterError: If the number of the most frequent words is below one
    """

    def __init__(
        self,
        nlp: Language,
        name: str = "ests_style",
        stopwords: list[str] | None = None,
        top_n: int = NAUSEA_TOP_N,
    ):
        check_style_params(top_n)
        add_dash_rules(nlp)
        self.name = name
        self.stopwords = stopwords
        self.top_n = top_n
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed metrics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        ss = StyleStats(doc, stopwords=self.stopwords, top_n=self.top_n)
        doc._.set(self.name, ss)
        return doc


@Language.factory("ests_phon")
class PhonStatsComponent:
    """
    Class for the component of the phonostatistics of a text

    Description:
        The statistics read the words of the document and their transcription,
        so the component needs no annotation of a model

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
        ParameterError: If the window is below 2
    """

    def __init__(self, nlp: Language, name: str = "ests_phon", window_len: int = PHON_WINDOW_LEN):
        check_phon_params(window_len)
        add_dash_rules(nlp)
        self.name = name
        self.window_len = window_len
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no words is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not has_words(doc):
            return doc
        ps = PhonStats(doc, window_len=self.window_len)
        doc._.set(self.name, ps)
        return doc


@Language.factory("ests_verse")
class VerseStatsComponent:
    """
    Class for the component of the verse statistics of a text

    Description:
        The statistics read the text of the document with its line breaks and
        blank lines, so the text of a poem goes to nlp as it is, the lines not
        joined; the component needs no annotation of a model. A text with
        letters but no Spanish syllables gives empty statistics, as VerseStats,
        and a document with no letter passes untouched

    Adding the component to a pipeline:
        >>> import ests
        >>> import spacy
        >>> nlp = spacy.load("es_core_news_sm")
        >>> nlp.add_pipe("ests_verse", name="verse", last=True)
        <ests.components.VerseStatsComponent object at 0x...>

    Reading the computed statistics:
        >>> doc = nlp("Cuando me paro a contemplar mi estado\\ny a ver los pasos por do me han traído")
        >>> doc._.verse.meter, doc._.verse.n_feet
        ('endecasílabo', 11)

    Arguments:
        name (str): Name of the component in the pipeline
    """

    def __init__(self, nlp: Language, name: str = "ests_verse"):
        add_dash_rules(nlp)
        self.name = name
        Doc.set_extension(self.name, default=None, force=True)

    def __call__(self, doc: Doc) -> Doc:
        """
        Adding the computed statistics to the component

        Description:
            A document with no letter is returned untouched, its extension
            left at None

        Arguments:
            doc (Doc): Doc object

        Returns:
            doc (Doc): Modified Doc object
        """
        if not LETTER.search(doc.text):
            return doc
        doc._.set(self.name, VerseStats(doc))
        return doc
