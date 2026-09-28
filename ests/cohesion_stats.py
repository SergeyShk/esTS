from collections import Counter
from collections.abc import Mapping, Sequence
from functools import cache
from math import nan
from pathlib import Path
from statistics import fmean
from types import MappingProxyType
from typing import NamedTuple

import anyts
from anyts.cohesion import calc_overlaps, calc_repetition, count_given
from anyts.utils import iter_doc_tokens, safe_divide
from spacy.language import Language
from spacy.tokens import Doc, Token

from .constants import (
    COHESION_STATS_DESC,
    CONNECTOR_BLOCKED_AFTER,
    CONNECTOR_BLOCKED_AFTER_POS,
    CONNECTOR_BLOCKED_BEFORE,
    CONNECTOR_CLASSES,
    CONNECTOR_POS,
    CONNECTOR_POS_EXTRA,
    CONNECTOR_TYPES,
    CONTENT_UD_POS,
)
from .exceptions import ParameterError, SourceError, SourceTypeError
from .extractors import SentsExtractor
from .utils import get_nlp

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


class Connector(NamedTuple):
    """
    Occurrence of a connector in a text

    Attributes:
        sent (int): Number of the sentence
        start (int): Position of the first word of the connector in the sentence
        end (int): Position after the last word of the connector
        text (str): Connector as the dictionary writes it
        cls (str): Class of the connector
        kind (str): Kind of the connector
    """

    sent: int
    start: int
    end: int
    text: str
    cls: str
    kind: str


class CohesionStats:
    """
    Class for computing the cohesion statistics of a text

    Description:
        Referential cohesion in the manner of Coh-Metrix: the overlap of nouns,
        of arguments (nouns and pronouns) and of content words between adjacent
        sentences and between all pairs of sentences, givenness (pronouns,
        demonstratives, lemmas already used) and temporal cohesion (repetition
        of the tense and of the mood of the verbs of adjacent sentences)
        Sentences are compared by lemmas; the features of a word are the ones
        of token_info. A Doc must carry the parts of speech (from a
        morphologizer, or a tagger with an attribute ruler) and the lemmas
        Connectors (porque, sin embargo, es decir) are found by find_connectors
        in the dictionary of load_connectors, in the classes of Martín
        Zorraquino and Portolés; a primary one is a conjunction, a conjunctive
        locution or an adverb, a secondary one a lexicalized phrase. Their
        density is given per 1000 words

    References:
        https://doi.org/10.1017/CBO9780511894664 (McNamara et al. 2014, Coh-Metrix)
        https://doi.org/10.3758/s13428-015-0651-7 (Crossley et al. 2016, TAACO)
        https://www.aclweb.org/anthology/W16-4105 (Quispesaravia et al. 2016, Coh-Metrix-Esp)

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
        temporal_cohesion (float): Mean of the repetition of the tense and of the mood
        connectors (float): Connectors per 1000 words
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
        get_stats: Getting the computed cohesion statistics of the text
        print_stats: Printing the computed cohesion statistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object, the extractor
            or the pipeline is of another type, or the connectors are not a dictionary
            of phrases and pairs of strings
        SourceError: If the source has no words, no annotation of the parts of
            speech or no lemmas, or is a string longer than the max_length of
            the pipeline
        ParameterError: If the dictionary of connectors has an unknown class or kind
        DatasetNotFoundError: If a string is passed and the model is not installed
    """

    def __init__(
        self,
        source: str | Doc,
        sents_extractor: SentsExtractor | None = None,
        connectors: Mapping[str, tuple[str, str]] | None = None,
        nlp: Language | None = None,
    ):
        if sents_extractor is not None and not isinstance(sents_extractor, anyts.SentsExtractor):
            raise SourceTypeError("The sentence extractor must be a SentsExtractor")
        if nlp is not None and not isinstance(nlp, Language):
            raise SourceTypeError("The pipeline must be a spaCy Language")
        index = _normalize_connectors() if connectors is None else _normalize(connectors)
        if isinstance(source, str):
            pipeline = nlp or get_nlp()
            if len(source) > pipeline.max_length:
                raise SourceError(
                    f"The text of {len(source)} characters is longer than the limit of the "
                    f"pipeline ({pipeline.max_length}): split it into parts or raise "
                    "max_length on a pipeline of your own and pass it in nlp"
                )
            source = pipeline(source, disable=UNUSED_COMPONENTS)
        elif not isinstance(source, Doc):
            raise SourceTypeError("The data source is set incorrectly")
        if sents_extractor is not None or not source.has_annotation("SENT_START"):
            sents = split_doc_sents(source, sents_extractor or SentsExtractor())
        else:
            sents = [list(iter_doc_tokens(sent)) for sent in source.sents]
        sents = [sent for sent in sents if sent]
        if not sents:
            raise SourceError("The data source has no words")
        if not source.has_annotation("POS"):
            raise SourceError(
                "The data source has no annotation of the parts of speech: "
                "parse the text with a model instead of a blank pipeline"
            )
        if not source.has_annotation("LEMMA"):
            raise SourceError(
                "The data source has no lemmas: parse the text with a pipeline that has "
                "a lemmatizer"
            )
        infos = [[token_info(token) for token in sent] for sent in sents]
        self.words = tuple(tuple(token.text for token in sent) for sent in sents)
        self.n_sents = len(self.words)
        self.n_words = sum(len(sent) for sent in self.words)

        self.lemmas = tuple(tuple(info.lemma for info in sent) for sent in infos)
        nouns = [frozenset(info.lemma for info in sent if info.noun) for sent in infos]
        arguments = [frozenset(info.lemma for info in sent if info.argument) for sent in infos]
        content = [[info.lemma for info in sent if info.content] for sent in infos]
        content_sets = [frozenset(sent) for sent in content]
        tenses = [[info.tense for info in sent if info.tense] for sent in infos]
        moods = [[info.mood for info in sent if info.mood] for sent in infos]

        self.n_nouns = sum(1 for sent in infos for info in sent if info.noun)
        self.n_pronouns = sum(1 for sent in infos for info in sent if info.pronoun)
        self.n_demonstratives = sum(1 for sent in infos for info in sent if info.demonstrative)
        self.n_content_words = sum(len(sent) for sent in content)
        self.n_given = count_given(content)

        noun_overlap = calc_overlaps(nouns, proportional=False)
        argument_overlap = calc_overlaps(arguments, proportional=False)
        content_overlap = calc_overlaps(content_sets)
        self.noun_overlap_adjacent = noun_overlap.adjacent
        self.noun_overlap_all = noun_overlap.all
        self.argument_overlap_adjacent = argument_overlap.adjacent
        self.argument_overlap_all = argument_overlap.all
        self.content_overlap_adjacent = content_overlap.adjacent
        self.content_overlap_all = content_overlap.all
        self.content_overlap_prop_adjacent = content_overlap.prop_adjacent
        self.content_overlap_prop_all = content_overlap.prop_all
        self.p_pronouns = self.n_pronouns / self.n_words
        self.pronoun_noun_ratio = safe_divide(self.n_pronouns, self.n_nouns, nan)
        self.p_demonstratives = self.n_demonstratives / self.n_words
        self.p_given = safe_divide(self.n_given, self.n_content_words, nan)
        self.tense_repetition = calc_repetition(tenses)
        self.mood_repetition = calc_repetition(moods)
        self.temporal_cohesion = fmean((self.tense_repetition, self.mood_repetition))

        pos = [[token.pos_ or None for token in sent] for sent in sents]
        self.connector_spans = tuple(
            connector
            for sent_index, (sent, sent_pos) in enumerate(zip(self.words, pos, strict=True))
            for connector in _find(sent, index, sent_index, sent_pos)
        )
        self.n_connectors = len(self.connector_spans)
        self.c_connectors = dict(
            sorted(Counter(connector.text for connector in self.connector_spans).items())
        )
        per_1000 = 1000 / self.n_words
        classes = Counter(connector.cls for connector in self.connector_spans)
        kinds = Counter(connector.kind for connector in self.connector_spans)
        self.connectors = self.n_connectors * per_1000
        self.connectors_causal = classes["causal"] * per_1000
        self.connectors_adversative = classes["adversative"] * per_1000
        self.connectors_concessive = classes["concessive"] * per_1000
        self.connectors_temporal = classes["temporal"] * per_1000
        self.connectors_additive = classes["additive"] * per_1000
        self.connectors_conditional = classes["conditional"] * per_1000
        self.connectors_reformulative = classes["reformulative"] * per_1000
        self.connectors_primary = kinds["primary"] * per_1000
        self.connectors_secondary = kinds["secondary"] * per_1000

    def get_stats(self) -> dict[str, float]:
        """
        Getting the computed cohesion statistics of the text

        Returns:
            dict[str, float]: Dictionary of the computed cohesion statistics
        """
        return {stat: getattr(self, stat) for stat in COHESION_STATS_DESC}

    def print_stats(self) -> None:
        """Printing the computed cohesion statistics with descriptions"""
        print(f"{'Statistic':^58}|{'Value':^10}")
        print("-" * 68)
        stats = self.get_stats()
        for stat, desc in COHESION_STATS_DESC.items():
            print(f"{desc:58}|{stats[stat]:^10.2f}")


@cache
def load_connectors() -> Mapping[str, tuple[str, str]]:
    """
    Loading the dictionary of the connectors

    Description:
        The file resources/connectors.tsv: 255 discourse markers, each with its
        class of CONNECTOR_CLASSES and its kind of CONNECTOR_TYPES

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


class ConnectorIndex(NamedTuple):
    """
    Index of the dictionary of the connectors, for the search

    Attributes:
        entries (dict[str, tuple[str, str, str]]): Connector, class and kind
            by normalized key
        by_first (dict[str, tuple[tuple[str, ...], ...]]): Patterns by their first
            word, from the longest to the shortest
    """

    entries: dict[str, tuple[str, str, str]]
    by_first: dict[str, tuple[tuple[str, ...], ...]]


def _normalize(connectors: Mapping[str, tuple[str, str]]) -> ConnectorIndex:
    """
    Building the index of the dictionary of the connectors

    Description:
        The key is the word forms in lower case separated by one space, plus a
        key with the periods and hyphens split off (p. ej.), as the tokenizer
        splits them; the patterns are grouped by their first word
    """
    entries: dict[str, tuple[str, str, str]] = {}
    patterns: dict[str, list[tuple[str, ...]]] = {}
    if not isinstance(connectors, Mapping):
        raise SourceTypeError(
            "The connectors must be a dictionary of a phrase and its class and kind"
        )
    for connector, value in connectors.items():
        if not (
            isinstance(connector, str)
            and isinstance(value, tuple | list)
            and len(value) == 2
            and all(isinstance(item, str) for item in value)
        ):
            raise SourceTypeError(
                f"A connector must be a phrase with a pair of its class and kind: {connector!r}"
            )
        cls, kind = value
        if cls not in CONNECTOR_CLASSES or kind not in CONNECTOR_TYPES:
            raise ParameterError(f"Unknown class or kind of a connector: {cls}, {kind}")
        key = " ".join(connector.lower().split())
        split = " ".join(key.replace("-", " ").replace(".", " ").split())
        for variant in {key, split}:
            if not variant:
                continue
            entries[variant] = (connector, cls, kind)
            pattern = tuple(variant.split())
            patterns.setdefault(pattern[0], []).append(pattern)
    by_first = {
        first: tuple(sorted(set(group), key=len, reverse=True))
        for first, group in patterns.items()
    }
    return ConnectorIndex(entries, by_first)


@cache
def _normalize_connectors() -> ConnectorIndex:
    return _normalize(load_connectors())


def _find(
    words: Sequence[str],
    index: ConnectorIndex,
    sent_index: int,
    pos: Sequence[str | None] | None = None,
) -> list[Connector]:
    normalized = [word.lower() for word in words]
    found = []
    position = 0
    while position < len(normalized):
        for pattern in index.by_first.get(normalized[position], ()):
            end = position + len(pattern)
            if tuple(normalized[position:end]) != pattern:
                continue
            text, cls, kind = index.entries[" ".join(pattern)]
            if _is_phrase(text, normalized, position, end, pos):
                continue
            if (
                len(pattern) == 1
                and pos is not None
                and not _is_connector_pos(pattern[0], pos, position)
            ):
                continue
            found.append(Connector(sent_index, position, end, text, cls, kind))
            position = end
            break
        else:
            position += 1
    return found


def _is_connector_pos(word: str, pos: Sequence[str | None], position: int) -> bool:
    if pos[position] is None:
        return True
    if position and pos[position - 1] == "DET":
        return False
    if pos[position] == "PROPN":
        return position == 0
    return pos[position] in CONNECTOR_POS or pos[position] in CONNECTOR_POS_EXTRA.get(
        word, frozenset()
    )


def _is_phrase(
    text: str,
    words: Sequence[str],
    position: int,
    end: int,
    pos: Sequence[str | None] | None,
) -> bool:
    """Whether the words of a marker are a phrase of their own here, antes de la reunión"""
    following = words[end] if end < len(words) else ""
    if following in CONNECTOR_BLOCKED_AFTER.get(text, frozenset()):
        return True
    if position and words[position - 1] in CONNECTOR_BLOCKED_BEFORE.get(text, frozenset()):
        return True
    if pos is None or end >= len(pos):
        return False
    return pos[end] in CONNECTOR_BLOCKED_AFTER_POS.get(text, frozenset())


def find_connectors(
    words: Sequence[str],
    connectors: Mapping[str, tuple[str, str]] | None = None,
    sent_index: int = 0,
    pos: Sequence[str | None] | None = None,
) -> list[Connector]:
    """
    Finding the connectors of a sentence

    Description:
        Connectors are matched by their word forms in lower case, the longest
        one at every position, without overlaps. A marker that heads a
        prepositional phrase (antes de la reunión, por encima de 80) is dropped
        With the parts of speech given, a one-word connector counts only with a
        part of speech of CONNECTOR_POS or of CONNECTOR_POS_EXTRA for that word,
        never after a determiner and, as a proper noun, only at the start of the
        sentence

    Arguments:
        words (list[str]): Words of the sentence
        connectors (dict[str, tuple[str, str]]): Dictionary of the connectors -
            class and kind by connector; without it the dictionary of resources is used
        sent_index (int): Number of the sentence, written into the occurrences
        pos (list[str]): Parts of speech of the words; without them the rules
            that read a tag are skipped

    Returns:
        list[Connector]: Occurrences of the connectors in the order of the words

    Raises:
        ParameterError: If the dictionary has an unknown class or kind

    Example:
        >>> from ests.cohesion_stats import find_connectors
        >>> find_connectors(["Sin", "embargo", "no", "vino"])
        [Connector(sent=0, start=0, end=2, text='sin embargo', cls='adversative', kind='secondary')]
    """
    index = _normalize_connectors() if connectors is None else _normalize(connectors)
    return _find(words, index, sent_index, pos)


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


def split_doc_sents(source: Doc, sents_extractor: SentsExtractor) -> list[list[Token]]:
    """
    Splitting the words of a Doc object with no sentence boundaries into sentences

    Description:
        A word belongs to the sentence of sents_extractor its token lies in;
        words outside the sentences found (dropped by the extractor) are left
        out, so with no sentence found there are no words

    Arguments:
        source (Doc): Doc object
        sents_extractor (SentsExtractor): Sentence extraction tool

    Returns:
        list[list[Token]]: Tokens of the words of every sentence
    """
    text = source.text
    spans = []
    cursor = 0
    for sent in sents_extractor.extract(text):
        start = text.find(sent, cursor)
        if start != -1:
            spans.append((start, start + len(sent)))
            cursor = start + len(sent)
    if not spans:
        return []
    sents: list[list[Token]] = [[] for _ in spans]
    index = 0
    for token in iter_doc_tokens(source):
        position = token.idx
        while index + 1 < len(spans) and spans[index + 1][0] <= position:
            index += 1
        if spans[index][0] <= position < spans[index][1]:
            sents[index].append(token)
    return sents
