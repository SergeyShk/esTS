from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping, Sequence
from functools import cache
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, NamedTuple

import anyts.cohesion_stats
from anyts.cohesion_stats import Connector as Connector, ConnectorMatcher
from anyts.constants import CONTENT_UD_POS

from .constants import (
    COHESION_STATS_DESC,
    CONNECTOR_BLOCKED_AFTER,
    CONNECTOR_BLOCKED_AFTER_POS,
    CONNECTOR_BLOCKED_BEFORE,
    CONNECTOR_NOT_AT_START,
    CONNECTOR_ONLY_AFTER,
    CONNECTOR_PARCELLATION,
    CONNECTOR_POS,
    CONNECTOR_POS_EXTRA,
    CONNECTOR_SPLIT_BY_MARKS,
    CONNECTOR_SUBORDINATORS,
)
from .exceptions import SourceError
from .extractors import SentsExtractor
from .utils import _check_encoding, _check_nlp, get_nlp

if TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokens import Doc, Token

CONNECTORS_FILE = Path(__file__).parent / "resources" / "connectors.tsv"
# Components the statistics never read
UNUSED_COMPONENTS = ["ner"]


class WordInfo(NamedTuple):
    """
    Features of a word used by the cohesion statistics

    Attributes:
        lemma (str): Lemma of the word
        noun (bool): Whether the word is a noun
        pronoun (bool): Whether the word is a pronoun
        demonstrative (bool): Whether the word is a demonstrative
        argument (bool): Whether the word is an argument - a noun or a pronoun
        content (bool): Whether the word is a content word
        tense (str): Tense of a verb form
        mood (str): Mood of a verb form
    """

    lemma: str
    noun: bool
    pronoun: bool
    demonstrative: bool
    argument: bool
    content: bool
    tense: str | None
    mood: str | None


class SpanishConnectorMatcher(ConnectorMatcher):
    """
    Matcher of the Spanish connectors in the words of a sentence

    Description:
        Extends the ConnectorMatcher of the anyTS core with the rules of
        Spanish: a one-word connector counts with a part of speech of
        CONNECTOR_POS or of CONNECTOR_POS_EXTRA for that word, never after a
        determiner and, as a proper noun, only at the start of the sentence; a
        marker that heads a prepositional phrase (antes de la reunión, por
        encima de 80) is dropped (CONNECTOR_BLOCKED_AFTER, CONNECTOR_BLOCKED_BEFORE,
        CONNECTOR_BLOCKED_AFTER_POS), and so are one of CONNECTOR_NOT_AT_START
        opening the sentence (Pues bien) and one of CONNECTOR_ONLY_AFTER inside
        the sentence after another word than those listed (encima). A rule
        reads no word across a punctuation mark when find gets the positions
        of the marks, and a mark inside a connector of CONNECTOR_SPLIT_BY_MARKS
        splits it (así, que). A connector opening a sentence links it to the
        ones before unless it is a subordinator: one of CONNECTOR_SUBORDINATORS
        (ya que, a pesar de) or a one-word one tagged SCONJ or ADP, but for
        those of CONNECTOR_PARCELLATION (Porque...)

    Example:
        >>> from ests.cohesion_stats import SpanishConnectorMatcher, load_connectors
        >>> SpanishConnectorMatcher(load_connectors()).find(["Sin", "embargo", "no", "vino"])
        [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]

    Raises:
        SourceTypeError: If the connectors are not a dictionary of a phrase and a pair of
            strings
        ParameterError: If a class or a kind of the dictionary is unknown
    """

    pos_tags = CONNECTOR_POS
    pos_extra = CONNECTOR_POS_EXTRA
    not_after_pos = frozenset({"DET"})
    start_only_pos = frozenset({"PROPN"})
    blocked_after = CONNECTOR_BLOCKED_AFTER
    blocked_before = CONNECTOR_BLOCKED_BEFORE
    blocked_after_pos = CONNECTOR_BLOCKED_AFTER_POS
    not_at_start = CONNECTOR_NOT_AT_START
    only_after = CONNECTOR_ONLY_AFTER
    split_by_marks = CONNECTOR_SPLIT_BY_MARKS
    subordinators = CONNECTOR_SUBORDINATORS
    parcellation = CONNECTOR_PARCELLATION


class CohesionStats(anyts.cohesion_stats.CohesionStats):
    """
    Class for computing the cohesion statistics of a text

    Description:
        Extends the CohesionStats of the anyTS core with the Spanish layer: a
        string is parsed by the spaCy model, the sentences of a Doc without
        boundaries come from the Spanish SentsExtractor, the temporal cohesion
        is the repetition of the tense and of the mood, and the connectors
        (porque, sin embargo, es decir) are found in the dictionary of
        load_connectors by SpanishConnectorMatcher. A Doc must carry the parts
        of speech (from a morphologizer, or a tagger with an attribute ruler)
        and the lemmas

    References:
        https://doi.org/10.1017/CBO9780511894664 (McNamara et al. 2014, Coh-Metrix)
        https://doi.org/10.3758/s13428-015-0651-7 (Crossley et al. 2016, TAACO)
        https://aclanthology.org/L16-1745/ (Quispesaravia et al. 2016, Coh-Metrix-Esp)

    Example:
        >>> from ests import CohesionStats
        >>> text = ("El gato estaba en la ventana. Miraba a los pájaros. "
        ...         "Sin embargo, los pájaros se fueron y el gato se durmió.")
        >>> cs = CohesionStats(text)
        >>> cs.noun_overlap_adjacent
        0.5
        >>> cs.lemmas[1]
        ('mirar', 'a', 'el', 'pájaro')
        >>> cs.connector_spans
        (Connector(sent=2, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary'),
         Connector(sent=2, start=6, end=7, text='y', cls='additive', kind='primary'))

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        sents_extractor (SentsExtractor): Sentence extraction tool; an extractor
            given here is used whatever the source, and without one a Doc with no
            sentence boundaries is split by the rules of the default extractor
        connectors (dict[str, tuple[str, str]]): Dictionary of the connectors - class
            and kind by connector; without it the dictionary of resources is used
        nlp (Language): Pipeline of spaCy that parses a string; without it
            the model of SPACY_MODEL is loaded

    Attributes:
        sents_extractor (SentsExtractor|None): Sentence extraction tool given
        words (tuple[tuple[str, ...], ...]): Tuple of the words of every sentence
        lemmas (tuple[tuple[str, ...], ...]): Tuple of the lemmas of every sentence
        n_sents (int): Number of sentences containing words
        n_words (int): Number of words
        n_nouns (int): Number of nouns
        n_pronouns (int): Number of pronouns
        n_demonstratives (int): Number of demonstratives
        n_content_words (int): Number of content words
        n_given (int): Number of content words whose lemma was used before
        n_connectors (int): Number of connectors
        n_inter_connectors (int): Number of connectors that open a sentence and link it to
            the ones before, outside get_stats
        connector_spans (tuple[Connector]): Tuple of the occurrences of the connectors
        c_connectors (dict[str, int]): Distribution of the occurrences by connector
        noun_overlap_adjacent (float): Share of adjacent pairs of sentences sharing a noun
        noun_overlap_all (float): Share of all pairs of sentences sharing a noun
        argument_overlap_adjacent (float): Share of adjacent pairs sharing a noun or a pronoun
        argument_overlap_all (float): Share of all pairs sharing a noun or a pronoun
        content_overlap_adjacent (float): Share of adjacent pairs sharing a content word
        content_overlap_all (float): Share of all pairs sharing a content word
        content_overlap_prop_adjacent (float): Mean share of shared content words
            in adjacent pairs of sentences
        content_overlap_prop_all (float): Mean share of shared content words
            in all pairs of sentences
        p_pronouns (float): Share of pronouns among the words
        pronoun_noun_ratio (float): Ratio of the number of pronouns to the number of nouns
        p_demonstratives (float): Share of demonstratives among the words
        p_given (float): Share of content words whose lemma was used before in the text
        tense_repetition (float): Share of adjacent pairs of sentences with the same
            dominant tense
        mood_repetition (float): Share of adjacent pairs of sentences with the same
            dominant mood
        aspect_repetition (float): Share of adjacent pairs of sentences with the same
            dominant aspect, outside get_stats
        temporal_cohesion (float): Mean of the repetition of the tense and of the mood
        connectors (float): Connectors per 1000 words
        connectors_inter (float): Connectors linking a sentence to the ones before per
            1000 words: those opening a sentence, unless a subordinator
        connectors_intra (float): Connectors linking the parts of a sentence per 1000
            words
        connectors_causal (float): Causal connectors per 1000 words
        connectors_adversative (float): Adversative connectors per 1000 words
        connectors_concessive (float): Concessive connectors per 1000 words
        connectors_temporal (float): Temporal connectors per 1000 words
        connectors_additive (float): Additive connectors per 1000 words
        connectors_conditional (float): Conditional connectors per 1000 words
        connectors_reformulative (float): Reformulative connectors per 1000 words
        connectors_primary (float): Primary connectors per 1000 words
        connectors_secondary (float): Secondary connectors per 1000 words

    Methods:
        describe: Reading of a statistic by its scale, None for every statistic
        get_stats: Getting the computed cohesion statistics of the text
        to_dataframe: Getting the statistics as a table of one row
        print_stats: Printing the computed cohesion statistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object, the extractor
            or the pipeline is of another type, or the connectors are not a dictionary
            of phrases and pairs of strings
        SourceError: If the source has no words, no annotation of the parts of
            speech or no lemmas, or is a string longer than the max_length of
            the pipeline or with a character without a UTF-8 form
        ParameterError: If the dictionary of connectors has an unknown class or kind
        DatasetNotFoundError: If a string is passed and the model is not installed
    """

    sents_extractor_class = SentsExtractor
    connector_matcher_class = SpanishConnectorMatcher
    temporal_features = ("tense", "mood")
    stats_desc = COHESION_STATS_DESC

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: anyts.SentsExtractor | None = None,
        connectors: Mapping[str, tuple[str, str]] | None = None,
        nlp: Language | None = None,
    ):
        _check_nlp(nlp)
        self._nlp = nlp
        super().__init__(source, sents_extractor, connectors)  # type: ignore[arg-type]  # analyze takes a string too

    def __getstate__(self) -> dict[str, Any]:
        """State for pickle and copy without the pipeline, which is no part of the statistics"""
        state = self.__dict__.copy()
        state.pop("_nlp", None)
        return state

    @classmethod
    def load_connectors(cls) -> Mapping[str, tuple[str, str]]:
        """Dictionary of the Spanish connectors (load_connectors)"""
        return load_connectors()

    def analyze(self, source: str | Doc) -> Iterable[Sequence[anyts.cohesion_stats.CohesionWord]]:
        """
        Getting the words of the sentences of a source with their features

        Description:
            A string is parsed by nlp or get_nlp() without the named entities;
            the words of the Doc then come with the features of the core

        Arguments:
            source (str|Doc): Data source

        Returns:
            iterable[list[CohesionWord]]: Words of every sentence

        Raises:
            SourceTypeError: If the source is neither a string nor a Doc object
            SourceError: If a string is longer than the max_length of the pipeline or
                has a character without a UTF-8 form, or the Doc has no parts of speech
                or no lemmas
            DatasetNotFoundError: If a string is passed and the model is not installed
        """
        if isinstance(source, str):
            pipeline = getattr(self, "_nlp", None) or get_nlp()
            if len(source) > pipeline.max_length:
                raise SourceError(
                    f"The text of {len(source)} characters is longer than the limit of the "
                    f"pipeline ({pipeline.max_length}): split it into parts or raise "
                    "max_length on a pipeline of your own and pass it in nlp"
                )
            _check_encoding(source)
            source = pipeline(source, disable=UNUSED_COMPONENTS)
        return super().analyze(source)


@cache
def load_connectors() -> Mapping[str, tuple[str, str]]:
    """
    Loading the dictionary of the connectors

    Description:
        The file resources/connectors.tsv: 273 discourse markers, each with its
        class of CONNECTOR_CLASSES and its kind of CONNECTOR_KINDS of anyts.constants

    Returns:
        Mapping[str, tuple[str, str]]: Class and kind by connector, read-only
            and shared by every caller
    """
    connectors: dict[str, tuple[str, str]] = {}
    with CONNECTORS_FILE.open(encoding="utf-8") as file:
        next(file)
        for line in file:
            connector, cls, kind = line.rstrip("\n").split("\t")
            connectors[connector] = (cls, kind)
    return MappingProxyType(connectors)


def find_connectors(
    words: Sequence[str],
    connectors: Mapping[str, tuple[str, str]] | None = None,
    sent_index: int = 0,
    pos: Sequence[str | None] | None = None,
    breaks: Collection[int] | None = None,
) -> list[Connector]:
    """
    Finding the connectors of a sentence

    Description:
        The find of SpanishConnectorMatcher: connectors are matched by their
        word forms in lower case, the longest one at every position, without
        overlaps. The words are those of one sentence without punctuation, the
        first one its start; with the parts of speech given, the rules that
        read a tag apply too, and with the positions of the marks a rule reads
        no word across a mark. With a dictionary of its own the function builds
        a matcher on every call: over many sentences, build a
        SpanishConnectorMatcher once and call its find

    Arguments:
        words (list[str]): Words of the sentence
        connectors (dict[str, tuple[str, str]]): Dictionary of the connectors -
            class and kind by connector; without it the dictionary of resources is used
        sent_index (int): Number of the sentence, written into the occurrences
        pos (list[str]): Parts of speech of the words; without them the rules
            that read a tag are skipped
        breaks (set[int]): Positions of the words a punctuation mark stands
            before (find_marks); without them the rules read through the marks

    Returns:
        list[Connector]: Occurrences of the connectors in the order of the words

    Raises:
        SourceTypeError: If the words are not a list of strings, the parts of speech are
            not a list of strings and None, the positions of the marks are not a
            collection, or the connectors are not a dictionary of phrases and pairs of
            strings
        ParameterError: If the dictionary has an unknown class or kind, the number of
            the sentence or a position of a mark is not an integer, or the parts of
            speech are not as many as the words

    Example:
        >>> from ests.cohesion_stats import find_connectors
        >>> find_connectors(["Sin", "embargo", "no", "vino"])
        [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]
    """
    matcher = (
        CohesionStats.connector_matcher()
        if connectors is None
        else SpanishConnectorMatcher(connectors)
    )
    return matcher.find(words, sent_index, pos, breaks)


def token_info(token: Token) -> WordInfo:
    """
    Getting the features of a token by the annotation of Universal Dependencies

    Description:
        A noun is NOUN or PROPN; a pronoun is PRON or a possessive,
        demonstrative or personal determiner (mi libro, este libro, but not el
        libro or cada libro); a demonstrative carries PronType=Dem; an argument
        is NOUN, PROPN or PRON; a content word is one of CONTENT_UD_POS and no
        demonstrative

    Arguments:
        token (Token): Token

    Returns:
        WordInfo: Features of the word
    """
    pron_type = token.morph.get("PronType", [])
    tense = token.morph.get("Tense", [])
    mood = token.morph.get("Mood", [])
    demonstrative = "Dem" in pron_type
    return WordInfo(
        lemma=token.lemma_.lower(),
        noun=token.pos_ in ("NOUN", "PROPN"),
        pronoun=token.pos_ == "PRON" or _is_pronominal_det(token, pron_type),
        demonstrative=demonstrative,
        argument=token.pos_ in ("NOUN", "PROPN", "PRON"),
        content=not demonstrative and token.pos_ in CONTENT_UD_POS,
        tense=tense[0] if tense else None,
        mood=mood[0] if mood else None,
    )


def _is_pronominal_det(token: Token, pron_type: list[str]) -> bool:
    """Whether a determiner points at something: mi libro, su libro, este libro"""
    if token.pos_ != "DET":
        return False
    if "Yes" in token.morph.get("Poss", []):
        return True
    return bool({"Dem", "Prs"} & set(pron_type))
