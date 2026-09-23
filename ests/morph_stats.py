from collections import Counter, OrderedDict
from math import nan
from typing import Any

from spacy.language import Language
from spacy.tokens import Doc, Token

from .constants import (
    COPULAS,
    MORPHOLOGY_FEATURES,
    MORPHOLOGY_MARKERS_DESC,
    MORPHOLOGY_STATS_DESC,
)
from .exceptions import SourceError, SourceTypeError, UnknownStatError
from .utils import get_nlp, iter_doc_tokens, safe_divide

FINITE_MOODS = {
    "p_indicative": "Ind",
    "p_subjunctive": "Sub",
    "p_conditional": "Cnd",
    "p_imperative": "Imp",
}
VERB_FORMS = {"p_infinitive": "Inf", "p_gerund": "Ger", "p_participle": "Part"}
# Parts of speech whose forms make the verbal system: the participles that the
# model annotates as adjectives (cansada, escrita) stay out of the markers
VERBAL_POS = ("VERB", "AUX")
# Dependency of an auxiliary: aux for the progressive (está cantando) and the
# compound tenses (ha sido leído), aux:pass for the passive (fue escrito). In the
# present the models often give the auxiliary of a passive the dependency of a
# copula instead (el proyecto es financiado), which its head gives away
AUXILIARY_DEP = "aux"
COPULA_DEP = "cop"
# Components a parse of the text does not need: the entities are never read, and
# the parse is, for the dependency of the copulas
UNUSED_COMPONENTS = ["ner"]


def is_auxiliary(token: Token) -> bool:
    """
    Checking whether a token is an auxiliary and not a copula

    Description:
        An auxiliary carries a dependency of aux - aux for the compound tenses
        and the progressive, aux:pass for the passive - or, in the present of
        a passive, the dependency of a copula over a participle: el proyecto es
        financiado has the same es as ella es alta, and only its head tells
        them apart

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if token.dep_.startswith(AUXILIARY_DEP):
        return True
    if token.dep_ != COPULA_DEP:
        return False
    return token.head.pos_ == "VERB" and "Part" in token.head.morph.get("VerbForm", [])


class MorphStats:
    """
    Class for computing the morphological statistics of a text

    Description:
        Parts of speech and grammatical features are given in the terms of
        Universal Dependencies, as the Spanish models of spaCy annotate them:
        pos - NOUN, VERB, ADJ, PRON, DET and the others, mood - Ind, Sub,
        Imp, Cnd, tense - Pres, Past, Imp, Fut, and likewise case, definite,
        degree, gender, num_type, number, person, polarity, polite, poss,
        pron_type, reflex and verb_form: the fifteen features of
        MORPHOLOGY_FEATURES, chosen among the ones the models annotate.
        A feature with several values keeps the form of CoNLL-U,
        PronType=Int,Rel, and the whole annotation of a word, the features
        left uncounted included, stays in tags
        A string is parsed with the model es_core_news_sm, or with the
        pipeline given in nlp, without the entity recognizer, which nothing
        here reads; a Doc is taken as it is and must carry the parts of speech,
        which come from a morphologizer or from a tagger with an attribute
        ruler, and the lemmas, which come from a lemmatizer. Punctuation marks
        and symbols are not words and are left out
        On top of the features the class computes the markers of Spanish:
        the moods of the finite forms, the non-finite forms, the choice
        between the copulas ser and estar and the adverbs in -mente

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
        source (str|Doc): Data source (a string or a Doc object)
        nlp (Language): Pipeline of spaCy that parses a string; without it
            the model of SPACY_MODEL is loaded

    Attributes:
        words (tuple[str]): Tuple of extracted words
        lemmas (tuple[str]): Tuple of lemmas of the words
        tags (tuple[str]): Tuple of feature strings in the CoNLL-U format
        pos (tuple[str]): Tuple of the parts of speech
        case (tuple[str]): Tuple of the values of case
        definite (tuple[str]): Tuple of the values of definiteness
        degree (tuple[str]): Tuple of the values of degree
        gender (tuple[str]): Tuple of the values of gender
        mood (tuple[str]): Tuple of the values of mood
        num_type (tuple[str]): Tuple of the values of the numeral type
        number (tuple[str]): Tuple of the values of number
        person (tuple[str]): Tuple of the values of person
        polarity (tuple[str]): Tuple of the values of polarity
        polite (tuple[str]): Tuple of the values of politeness
        poss (tuple[str]): Tuple of the values of the possessive
        pron_type (tuple[str]): Tuple of the values of the pronoun type
        reflex (tuple[str]): Tuple of the values of the reflexive
        tense (tuple[str]): Tuple of the values of tense
        verb_form (tuple[str]): Tuple of the values of the verb form

    Methods:
        get_stats: Getting the computed morphological statistics of the text
        get_markers: Getting the markers of Spanish computed from the features
        explain_text: Parsing the text by the morphological statistics
        print_stats: Printing the computed morphological statistics with descriptions
        print_markers: Printing the computed markers of Spanish with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object
        SourceError: If the source has no words, no annotation of the parts of
            speech or no lemmas, or is a string longer than the max_length of
            the pipeline
        DatasetNotFoundError: If a string is passed and the model is not installed
    """

    def __init__(self, source: str | Doc, nlp: Language | None = None):
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
        tokens = list(iter_doc_tokens(source))
        if not tokens:
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

        self.words = tuple(token.text for token in tokens)
        self.lemmas = tuple(token.lemma_ for token in tokens)
        self.tags = tuple(str(token.morph) or "_" for token in tokens)
        self.pos = tuple(token.pos_ or None for token in tokens)
        features = [token.morph.to_dict() for token in tokens]
        self.case = self.__feature(features, "case")
        self.definite = self.__feature(features, "definite")
        self.degree = self.__feature(features, "degree")
        self.gender = self.__feature(features, "gender")
        self.mood = self.__feature(features, "mood")
        self.num_type = self.__feature(features, "num_type")
        self.number = self.__feature(features, "number")
        self.person = self.__feature(features, "person")
        self.polarity = self.__feature(features, "polarity")
        self.polite = self.__feature(features, "polite")
        self.poss = self.__feature(features, "poss")
        self.pron_type = self.__feature(features, "pron_type")
        self.reflex = self.__feature(features, "reflex")
        self.tense = self.__feature(features, "tense")
        self.verb_form = self.__feature(features, "verb_form")
        self.__parsed = source.has_annotation("DEP")
        self.__auxiliary = tuple(is_auxiliary(token) for token in tokens)

    @staticmethod
    def __feature(features: list[dict[str, str]], stat: str) -> tuple[str | None, ...]:
        """Values of one feature for every word, None where the model gives none"""
        name = MORPHOLOGY_FEATURES[stat]
        return tuple(word.get(name) for word in features)

    def get_stats(self, *args: str, filter_none: bool = False) -> dict[str, dict[str, int]]:
        """
        Getting the computed morphological statistics of the text

        Arguments:
            args (tuple[str]): Names of the selected statistics
            filter_none (bool): Filter out the empty values

        Returns:
            dict[str, dict[str, int]]: Dictionary of the computed morphological statistics

        Raises:
            UnknownStatError: If a statistic is unknown

        Example:
            >>> from ests import MorphStats
            >>> ms = MorphStats("Los niños juegan")
            >>> ms.get_stats("number", filter_none=True)
            {'number': {'Plur': 3}}
        """
        args = self.__check_stat(args)
        stats: dict[str, dict[str, int]] = {}
        for arg in args:
            counts = dict(Counter(getattr(self, arg)))
            stats[arg] = {k: v for k, v in counts.items() if k} if filter_none else counts
        return stats

    def get_markers(self) -> dict[str, float]:
        """
        Getting the markers of Spanish computed from the features

        Description:
            Every marker is a share of its own base: the moods among the
            finite forms, the non-finite forms among all the verb forms,
            ser among the two copulas and the adverbs in -mente among the
            adverbs. Verb forms are counted on verbs and auxiliaries, so
            that the participles that the model annotates as adjectives
            (cansada, escrita) stay out of the base; the moods sum to one
            wherever the model leaves no finite form without a mood
            The base of p_ser is the copular uses of ser and estar, read
            from the dependency of the token and from what it depends on: the
            auxiliaries of the passive (fue escrito, es financiado) and of the
            progressive (está cantando) are not a choice between the two
            copulas. For a Doc with no parse the marker is nan
            A marker whose base is empty is nan

        Returns:
            dict[str, float]: Dictionary of the markers in the order of
                MORPHOLOGY_MARKERS_DESC

        Example:
            >>> from ests import MorphStats
            >>> ms = MorphStats("Si tuviera tiempo, leería el libro que quiero leer")
            >>> ms.get_markers()["p_subjunctive"]
            0.3333333333333333
        """
        verbs = [
            (self.mood[i], form)
            for i, form in enumerate(self.verb_form)
            if form and self.pos[i] in VERBAL_POS
        ]
        moods = Counter(mood for mood, form in verbs if form == "Fin")
        forms = Counter(form for _, form in verbs)
        n_finite = forms["Fin"]
        n_forms = sum(forms.values())
        copulas = Counter(
            lemma
            for lemma, pos, auxiliary in zip(self.lemmas, self.pos, self.__auxiliary, strict=True)
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
            safe_divide(copulas["ser"], sum(copulas.values()), nan) if self.__parsed else nan
        )
        markers["p_mente_adverbs"] = safe_divide(
            sum(1 for adverb in adverbs if adverb.lower().endswith("mente")), len(adverbs), nan
        )
        return {marker: markers[marker] for marker in MORPHOLOGY_MARKERS_DESC}

    def print_markers(self) -> None:
        """
        Printing the computed markers of Spanish with descriptions

        Example:
            >>> from ests import MorphStats
            >>> MorphStats("Los niños juegan alegremente").print_markers()
                                 Marker                     |   Value
            -----------------------------------------------------------
            Indicative among the finite forms              |  1.00
            Subjunctive among the finite forms             |  0.00
            Conditional among the finite forms             |  0.00
            Imperative among the finite forms              |  0.00
            Infinitive among the verb forms                |  0.00
            Gerund among the verb forms                    |  0.00
            Participle among the verb forms                |  0.00
            ser among the copulas ser and estar            |  nan
            Adverbs in -mente among the adverbs            |  1.00
        """
        markers = self.get_markers()
        print(f"{'Marker'.center(47)}|{'Value'.center(11)}")
        print("-" * 59)
        for marker, desc in MORPHOLOGY_MARKERS_DESC.items():
            print(f"{desc:47}|{markers[marker]:^11.2f}")

    def explain_text(
        self, *args: str, filter_none: bool = False
    ) -> tuple[tuple[str, dict[str, str | None]], ...]:
        """
        Parsing the text by the morphological statistics

        Arguments:
            args (tuple[str]): Names of the selected statistics
            filter_none (bool): Filter out the empty values

        Returns:
            tuple[tuple[str, dict[str, str]]]: Tuple of the words of the text
                with their morphological statistics

        Raises:
            UnknownStatError: If a statistic is unknown

        Example:
            >>> from ests import MorphStats
            >>> ms = MorphStats("Los niños juegan")
            >>> ms.explain_text("pos", "number", filter_none=True)[2]
            ('juegan', {'pos': 'VERB', 'number': 'Plur'})
        """
        args = self.__check_stat(args)
        values = tuple(zip(*(getattr(self, arg) for arg in args), strict=True))
        explains = tuple(
            {
                stat: value
                for stat, value in zip(args, word_values, strict=True)
                if value or not filter_none
            }
            for word_values in values
        )
        return tuple(zip(self.words, explains, strict=True))

    def print_stats(self, *args: str, filter_none: bool = False) -> None:
        """
        Printing the computed morphological statistics with descriptions

        Arguments:
            args (tuple[str]): Names of the selected statistics
            filter_none (bool): Filter out the empty values

        Raises:
            UnknownStatError: If a statistic is unknown

        Example:
            >>> from ests import MorphStats
            >>> MorphStats("Los niños juegan alegremente").print_stats("number")
            -----------------Number-----------------
            Plural                        |    3
            Unknown                       |    1
        """
        args = self.__check_stat(args)
        for stat, values in self.get_stats(*args).items():
            desc: Any = MORPHOLOGY_STATS_DESC[stat]
            print(f"{desc['name'].center(40, '-')}")
            for value, number in OrderedDict(
                sorted(values.items(), key=lambda item: item[1], reverse=True)
            ).items():
                if filter_none and not value:
                    continue
                print(f"{self.__describe(desc['values'], value):30}|{number!s:^10}")
            print()

    @staticmethod
    def __describe(values: dict[str, str], value: str | None) -> str:
        """
        Description of a value of a statistic

        Description:
            A value of several values, which the models write in the form of
            CoNLL-U (Case=Acc,Nom of usted, PronType=Int,Rel of qué), is
            described by the descriptions of its parts joined with or; a value
            with no description at all is printed as the model gives it

        Arguments:
            values (dict[str, str]): Descriptions of the values of the statistic
            value (str|None): Value of the statistic

        Returns:
            str: Description of the value
        """
        if not value:
            return "Unknown"
        if value in values:
            return values[value]
        if "," in value:
            parts = [values.get(part, part) for part in value.split(",")]
            return " or ".join([parts[0]] + [part.lower() for part in parts[1:]])
        return value

    @staticmethod
    def __check_stat(args: tuple[str, ...]) -> tuple[str, ...]:
        """
        Checking the names of the selected statistics

        Arguments:
            args (tuple[str]): Names of the selected statistics

        Returns:
            tuple[str]: The names, or all of them when none is given

        Raises:
            UnknownStatError: If a statistic is missing from MORPHOLOGY_STATS_DESC
        """
        if not args:
            return tuple(MORPHOLOGY_STATS_DESC)
        for arg in args:
            if arg not in MORPHOLOGY_STATS_DESC:
                raise UnknownStatError(
                    f"{arg} is missing from the morphological statistics, "
                    f"available: {', '.join(MORPHOLOGY_STATS_DESC)}"
                )
        return args
