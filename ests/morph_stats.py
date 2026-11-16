from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from functools import lru_cache
from math import nan
from typing import TYPE_CHECKING, ClassVar

import anyts.morph_stats
from anyts.document import get_tree
from anyts.morph_stats import MorphWord as MorphWord
from anyts.utils import has_words, safe_divide

from .constants import (
    COPULA_AUXILIARY_FORMS,
    COPULAS,
    ENCLITICS,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
)
from .exceptions import SourceError
from .utils import SEGMENTER, _annotate_text, get_document, get_morph_analyzer

if TYPE_CHECKING:
    from anyseg import Document
    from anyts.document import TreeWord
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
# Parts of speech between an auxiliary and its verb form (fue ayer aprobada, está siempre
# cantando)
AUXILIARY_GAP_POS = ("ADV", "PRON", "PART")


def is_auxiliary(token: TreeWord) -> bool:
    """
    Checking whether a word of the tree is an auxiliary and not a copula

    Description:
        A copula before the verb form of COPULA_AUXILIARY_FORMS in the same
        sentence: ser before a participle (fue escrito, el proyecto es
        financiado - the passive) and estar before a gerund (está cantando -
        the progressive), with adverbs and pronouns between them (fue ayer
        aprobada, está siempre cantando); both words are a VERB or an AUX. The
        rule reads the parts of speech and the features alone and needs no
        parse; a participle the tagger reads as an adjective (fue muy bien
        recibido) leaves its ser a copula

    Arguments:
        token (TreeWord): Word of the tree

    Returns:
        bool: Result of the check

    Example:
        >>> from anyts.document import get_tree
        >>> from ests.morph_stats import is_auxiliary
        >>> from ests.utils import get_document, get_morph_analyzer
        >>> document = get_document("La casa fue construida. Está cansada.")
        >>> get_morph_analyzer().annotate(document)
        >>> tree = get_tree(document)
        >>> [word.form for word in tree.words if is_auxiliary(word)]
        ['fue']
    """
    form = COPULA_AUXILIARY_FORMS.get(token.lemma or "")
    if form is None or token.upos not in VERBAL_POS:
        return False
    words = token.tree.words
    for index in range(token.index + 1, len(words)):
        word = words[index]
        if word.sentence != token.sentence:
            return False
        if word.upos not in AUXILIARY_GAP_POS:
            return word.upos in VERBAL_POS and form in word.feats.get("VerbForm", "").split(",")
    return False


def has_enclitics(token: TreeWord) -> bool:
    """
    Checking whether a verb form of the tree carries enclitic pronouns

    Description:
        A VERB or an AUX whose token the segmenter anySeg splits into the verb
        and its pronouns (dale - da + le, dámelo - da + me + lo, buscarla) or
        whose first analysis as a verb in esMorph has pronouns after it
        (pasábanse, díjole); the forms in -se of the subjunctive are one word
        (hablase). The rule reads the text of the token, so a string and a Doc
        give the same

    Arguments:
        token (TreeWord): Word of the tree

    Returns:
        bool: Result of the check

    Example:
        >>> from anyts.document import get_tree
        >>> from ests.morph_stats import has_enclitics
        >>> from ests.utils import get_document, get_morph_analyzer
        >>> document = get_document("Dámelo, que quiero leerlo si hablase de ti.")
        >>> get_morph_analyzer().annotate(document)
        >>> [word.form for word in get_tree(document).words if has_enclitics(word)]
        ['Da', 'leer']
    """
    if token.upos not in VERBAL_POS:
        return False
    return _verb_with_pronouns(token.tree.text[token.start : token.end].lower())


@lru_cache(maxsize=65536)
def _verb_with_pronouns(text: str) -> bool:
    """Whether anySeg splits a token into words or its first analysis as a verb in esMorph has
    more than one word"""
    if len(SEGMENTER.segment(text).tokens[0].words) > 1:
        return True
    analyses = get_morph_analyzer().analyze(text)
    return next((len(a.words) > 1 for a in analyses if a.pos in VERBAL_POS), False)


def has_proclitics(token: TreeWord) -> bool:
    """
    Checking whether a verb form of the tree comes after proclitic pronouns

    Description:
        A VERB or an AUX right after a pronoun of ENCLITICS that is a token of
        its own, in the same sentence; the pronouns may be a chain (se lo
        dijo), and the enclitic of the verb before is none (hallándose
        expresado). In a compound tense the pronouns go before the auxiliary
        (se ha ido)

    Arguments:
        token (TreeWord): Word of the tree

    Returns:
        bool: Result of the check

    Example:
        >>> from anyts.document import get_tree
        >>> from ests.morph_stats import has_proclitics
        >>> from ests.utils import get_document, get_morph_analyzer
        >>> document = get_document("No se lo dijo, pero lo sabía y se ha ido.")
        >>> get_morph_analyzer().annotate(document)
        >>> [word.form for word in get_tree(document).words if has_proclitics(word)]
        ['dijo', 'sabía', 'ha']
    """
    if token.upos not in VERBAL_POS or not token.index:
        return False
    previous = token.tree.words[token.index - 1]
    return (
        previous.sentence == token.sentence
        and previous.upos == "PRON"
        and previous.form.lower() in ENCLITICS
        and token.tree.text[previous.start : previous.end].lower() == previous.form.lower()
    )


class MorphStats(anyts.morph_stats.MorphStats):
    """
    Class for computing the morphological statistics of a text

    Description:
        Extends the MorphStats of the anyTS core with the Spanish layer: a
        string gets the analyses of esMorph in the context of its sentences,
        with the words of a contraction and of a verb with clitics apart (del -
        de + el, dámelo - da + me + lo); a Doc must carry the lemmas next to the
        parts of speech; get_markers gives the markers of Spanish computed from
        the features. The statistics are the parts of speech
        and the features of MORPHOLOGY_FEATURES in the tags of Universal
        Dependencies (NOUN, VERB; Ind, Sub; Pres, Past); a feature with
        several values keeps the form of CoNLL-U (Case=Acc,Nom of usted), and tags
        holds the whole annotation of every word. Punctuation marks and
        symbols are not words

    References:
        https://universaldependencies.org/u/feat/
        https://github.com/SergeyShk/esMorph

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
        SourceTypeError: If the source is neither a string, a Doc nor a Document
        SourceError: If the source has no words, no annotation of the parts of
            speech or no lemmas
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

    def __init__(self, source: str | Doc | Document):
        super().__init__(source)
        # analyze can be called again on the object; the markers read the words of the source
        self.lemmas, self._auxiliary, self._enclitics, self._proclitics = self._found

    def parse(self, source: str | Doc | Document) -> Document:
        """
        Getting the document of a source

        Description:
            A string is segmented by anySeg and analyzed by esMorph in the
            context of its sentences; a Doc or a Document goes to get_document

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            Document: Document of anySeg

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
        """
        if isinstance(source, str):
            return _annotate_text(source)
        return get_document(source)

    def analyze(self, source: str | Doc | Document) -> list[MorphWord]:
        """
        Getting the words of a source with their features

        Description:
            The words of the core; the document must carry the lemmas too, which
            the markers read with the auxiliaries (is_auxiliary)

        Arguments:
            source (str|Doc|Document): Data source

        Returns:
            list[MorphWord]: Words with their features

        Raises:
            SourceTypeError: If the source is neither a string, a Doc nor a Document
            SourceError: If the words have no parts of speech or no lemmas
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
            tuple(is_auxiliary(word) for word in found),
            tuple(has_enclitics(word) for word in found),
            tuple(has_proclitics(word) for word in found),
        )
        return words

    def get_markers(self) -> dict[str, float]:
        """
        Getting the markers of Spanish computed from the features

        Description:
            Every marker is a share of its own base: the moods among the
            finite forms, the non-finite forms and the forms with enclitics or
            after proclitics (has_enclitics, has_proclitics) among the verb
            forms (VERB and AUX, so participles tagged ADJ stay out), ser among
            the copular
            uses of ser and estar (the auxiliaries of the passive and of the
            progressive left out, see is_auxiliary) and the adverbs in -mente
            among the adverbs
            A marker whose base is empty is nan; a feature of several values
            (Mood=Ind,Sub) counts in the share of each

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
        markers["p_enclitics"] = safe_divide(sum(self._enclitics[i] for i in verbs), n_forms, nan)
        markers["p_proclitics"] = safe_divide(
            sum(self._proclitics[i] for i in verbs), n_forms, nan
        )
        markers["p_ser"] = safe_divide(copulas["ser"], sum(copulas.values()), nan)
        markers["p_mente_adverbs"] = safe_divide(
            sum(1 for adverb in adverbs if adverb.lower().endswith("mente")), len(adverbs), nan
        )
        return {marker: markers[marker] for marker in MORPHOLOGY_MARKERS_DESC}


def _values(value: str | None) -> list[str]:
    """Values of a feature of several values joined by commas, none without the feature"""
    return value.split(",") if value else []
