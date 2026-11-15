from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from math import nan
from typing import TYPE_CHECKING, Any, ClassVar

import anyts.morph_stats
from anyts.document import get_tree
from anyts.morph_stats import MorphWord as MorphWord
from anyts.utils import has_words, safe_divide

from .constants import (
    COPULAS,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
    PASSIVE_AUX,
)
from .exceptions import SourceError
from .utils import _check_nlp, _parse_text, get_document

if TYPE_CHECKING:
    from anyseg import Document
    from anyts.document import TreeWord
    from spacy.language import Language
    from spacy.tokens import Doc

FINITE_MOODS = {
    "p_indicative": "Ind",
    "p_subjunctive": "Sub",
    "p_conditional": "Cnd",
    "p_imperative": "Imp",
}
VERB_FORMS = {"p_infinitive": "Inf", "p_gerund": "Ger", "p_participle": "Part"}
# Parts of speech of the verb forms: participles tagged ADJ (cansada) stay out
VERBAL_POS = ("VERB", "AUX")
# Dependencies of an auxiliary (aux, aux:pass) and of a copula
AUXILIARY_DEP = "aux"
COPULA_DEP = "cop"
# Components the statistics never read; the parser stays for the copulas
UNUSED_COMPONENTS = ["ner"]


def is_auxiliary(token: TreeWord) -> bool:
    """
    Checking whether a word of the tree is an auxiliary and not a copula

    Description:
        A token with the dependency aux or aux:pass, or ser with the dependency
        cop over a participle: the models tag the auxiliary of a present passive
        (el proyecto es financiado) as a copula

    Arguments:
        token (TreeWord): Word of the tree

    Returns:
        bool: Result of the check
    """
    deprel = token.deprel or ""
    if deprel.startswith(AUXILIARY_DEP):
        return True
    head = token.head
    if deprel != COPULA_DEP or token.lemma != PASSIVE_AUX or head is None:
        return False
    return head.upos == "VERB" and "Part" in head.feats.get("VerbForm", "").split(",")


class MorphStats(anyts.morph_stats.MorphStats):
    """
    Class for computing the morphological statistics of a text

    Description:
        Extends the MorphStats of the anyTS core with the Spanish layer: a
        string is parsed by the spaCy model, a Doc must carry the lemmas next
        to the parts of speech, and get_markers gives the markers of Spanish
        computed from the features. The statistics are the parts of speech
        and the features of MORPHOLOGY_FEATURES in the tags of Universal
        Dependencies (NOUN, VERB; Ind, Sub; Pres, Past); a feature with
        several values keeps the form of CoNLL-U (PronType=Int,Rel), and tags
        holds the whole annotation of every word. Punctuation marks and
        symbols are not words

    References:
        https://universaldependencies.org/u/feat/
        https://spacy.io/models/es

    Example:
        >>> from ests import MorphStats
        >>> text = "El gato duerme en la ventana mientras los niños juegan"
        >>> ms = MorphStats(text)
        >>> ms.get_stats("pos", filter_none=True)
        {'pos': {'DET': 3, 'NOUN': 3, 'VERB': 2, 'ADP': 1, 'SCONJ': 1}}
        >>> ms.tags[1]
        'Gender=Masc|Number=Sing'

    Arguments:
        source (str|Doc|Document): Data source (a string, a Doc or a Document)
        nlp (Language): Pipeline of spaCy that parses a string; without it
            the model of SPACY_MODEL is loaded

    Attributes:
        words (tuple[str]): Tuple of extracted words
        lemmas (tuple[str]): Tuple of lemmas of the words
        tags (tuple[str]): Tuple of feature strings in the CoNLL-U format
        pos (tuple[str|None]): Tuple of the parts of speech
        case (tuple[str|None]): Tuple of the values of case
        definite (tuple[str|None]): Tuple of the values of definiteness
        degree (tuple[str|None]): Tuple of the values of degree
        gender (tuple[str|None]): Tuple of the values of gender
        mood (tuple[str|None]): Tuple of the values of mood
        num_type (tuple[str|None]): Tuple of the values of the numeral type
        number (tuple[str|None]): Tuple of the values of number
        person (tuple[str|None]): Tuple of the values of person
        polarity (tuple[str|None]): Tuple of the values of polarity
        polite (tuple[str|None]): Tuple of the values of politeness
        poss (tuple[str|None]): Tuple of the values of the possessive
        pron_type (tuple[str|None]): Tuple of the values of the pronoun type
        reflex (tuple[str|None]): Tuple of the values of the reflexive
        tense (tuple[str|None]): Tuple of the values of tense
        verb_form (tuple[str|None]): Tuple of the values of the verb form

    Methods:
        analyze: Words of a source with their features, a string parsed
        describe: Reading of a statistic by its scale, None for every statistic
        get_stats: Getting the computed morphological statistics of the text
        to_dataframe: Getting the statistics as a table of one row
        get_markers: Getting the markers of Spanish computed from the features
        explain_text: Parsing the text by the morphological statistics
        print_stats: Printing the computed morphological statistics with descriptions
        print_markers: Printing the computed markers of Spanish with descriptions

    Raises:
        SourceTypeError: If the source is neither a string, a Doc nor a Document, or the
            pipeline is not a spaCy Language
        SourceError: If the source has no words, no annotation of the parts of
            speech or no lemmas, or is a string longer than the max_length of
            the pipeline
        DatasetNotFoundError: If a string is passed and the model is not installed
    """

    feature_names = MORPHOLOGY_FEATURES
    stats_desc: ClassVar[Mapping[str, str]] = {
        stat: str(desc["name"]) for stat, desc in MORPHOLOGY_STATS_DESC.items()
    }
    values_desc: ClassVar[Mapping[str, Mapping[str, str]]] = {
        stat: dict(desc["values"])  # type: ignore[call-overload]
        for stat, desc in MORPHOLOGY_STATS_DESC.items()
    }
    markers_desc = MORPHOLOGY_MARKERS_DESC

    def __init__(self, source: str | Doc | Document, nlp: Language | None = None):
        _check_nlp(nlp)
        self._nlp = nlp
        super().__init__(source)
        # analyze can be called again on the object; the markers read the words of the source
        self.lemmas, self._parsed, self._auxiliary = self._found

    def __getstate__(self) -> dict[str, Any]:
        """State for pickle and copy without the pipeline, which is no part of the statistics"""
        state = self.__dict__.copy()
        state["_nlp"] = None
        return state

    def parse(self, source: str | Doc | Document) -> Document:
        """
        Getting the document of a source

        Description:
            A string is parsed by nlp or get_nlp() without the named entities; a
            Doc or a Document goes to get_document

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            Document: Document of anySeg

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
            SourceError: If a string is longer than the max_length of the pipeline
            DatasetNotFoundError: If a string is passed and the model is not installed
        """
        if isinstance(source, str):
            return _parse_text(source, self._nlp, UNUSED_COMPONENTS)
        return get_document(source)

    def analyze(self, source: str | Doc | Document) -> list[MorphWord]:
        """
        Getting the words of a source with their features

        Description:
            The words of the core; the document must carry the lemmas too, which
            the markers read with the auxiliaries of the tree

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            list[MorphWord]: Words with their features

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
            SourceError: If a string is longer than the max_length of the pipeline, or the
                words have no parts of speech or no lemmas
            DatasetNotFoundError: If a string is passed and the model is not installed
        """
        document = self._document(source)
        # A source without words: the core raises no_words, whatever its annotation
        words = list(super().analyze(document))
        if not words:
            return []
        if not any(document.column("lemma")):
            raise SourceError(self.messages["no_lemmas"])
        found = [word for word in get_tree(document).words if has_words(word.form)]
        self._found = (
            tuple(word.lemma or "" for word in found),
            any(document.column("deprel")),
            tuple(is_auxiliary(word) for word in found),
        )
        return words

    def get_markers(self) -> dict[str, float]:
        """
        Getting the markers of Spanish computed from the features

        Description:
            Every marker is a share of its own base: the moods among the
            finite forms, the non-finite forms among the verb forms (VERB and
            AUX, so participles tagged ADJ stay out), ser among the copular
            uses of ser and estar (the auxiliaries of the passive and of the
            progressive left out, see is_auxiliary) and the adverbs in -mente
            among the adverbs
            A marker whose base is empty is nan, and so is p_ser for a Doc
            with no parse; a feature of several values (Mood=Ind,Sub) counts
            in the share of each

        Returns:
            dict[str, float]: Dictionary of the markers in the order of
                MORPHOLOGY_MARKERS_DESC

        Example:
            >>> from ests import MorphStats
            >>> ms = MorphStats("Si tuviera tiempo, leería el libro que quiero leer")
            >>> ms.get_markers()["p_subjunctive"]
            0.3333333333333333
        """
        verbs = [i for i, form in enumerate(self.verb_form) if form and self.pos[i] in VERBAL_POS]
        forms = Counter(value for i in verbs for value in _values(self.verb_form[i]))
        finite = [i for i in verbs if "Fin" in _values(self.verb_form[i])]
        moods = Counter(value for i in finite for value in _values(self.mood[i]))
        n_finite = len(finite)
        n_forms = len(verbs)
        copulas = Counter(
            lemma
            for lemma, pos, auxiliary in zip(self.lemmas, self.pos, self._auxiliary, strict=True)
            if pos in VERBAL_POS and lemma in COPULAS and not auxiliary
        )
        adverbs = [word for word, pos in zip(self.words, self.pos, strict=True) if pos == "ADV"]
        markers = {
            marker: safe_divide(moods[mood], n_finite, nan)
            for marker, mood in FINITE_MOODS.items()
        }
        markers.update(
            {marker: safe_divide(forms[form], n_forms, nan) for marker, form in VERB_FORMS.items()}
        )
        markers["p_ser"] = (
            safe_divide(copulas["ser"], sum(copulas.values()), nan) if self._parsed else nan
        )
        markers["p_mente_adverbs"] = safe_divide(
            sum(1 for adverb in adverbs if adverb.lower().endswith("mente")), len(adverbs), nan
        )
        return {marker: markers[marker] for marker in MORPHOLOGY_MARKERS_DESC}


def _values(value: str | None) -> list[str]:
    """Values of a feature of several values joined by commas, none without the feature"""
    return value.split(",") if value else []
