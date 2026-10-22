import re
from collections.abc import Collection, Iterable, Sequence
from math import nan
from statistics import fmean

import anyts.syntax_stats
from anyts.constants import AUXILIARY_DEPS, CLAUSE_DEPS, SUBORDINATE_CLAUSE_DEPS
from anyts.syntax_stats import (
    base_dep,
    calc_modifier_chains,
    calc_valency,
    count_noun_modifiers as count_noun_modifiers,
    get_children,
    get_words,
    is_predicate as is_predicate,
    is_root,
    subtree_len,
)
from anyts.utils import has_feature, is_word
from spacy.language import Language
from spacy.tokens import Doc, Token

from .constants import (
    AGENT_PREPOSITION,
    AUXILIARY_VERBS,
    DE_PREPOSITIONS,
    ENCLITICS,
    GERUND_PERIPHRASIS_VERBS,
    INFINITIVE_PERIPHRASES,
    LIGHT_VERBS,
    NEGATION_WORDS,
    PASSIVE_AUX,
    PREPOSITIONAL_LIGHT_VERBS,
    RAISING_VERBS,
    SE_IMPERSONAL_DEP,
    SE_PASSIVE_DEP,
    SPLIT_PREDICATE_NOUNS,
    SYNTAX_STATS_DESC,
)
from .exceptions import SourceError, SourceTypeError
from .utils import _check_encoding, get_nlp, is_verbal_noun, lemmatize

# Dependencies of the nominal part of a split predicate, in the order of preference
SPLIT_PREDICATE_DEPS = ("compound", "obj", "nsubj", "iobj", "nmod", "obl")
# Relations by which the models attach the gerund of a periphrasis to its verb
PERIPHRASIS_DEPS = ("xcomp", "advcl")
# The endings of the infinitive and the gerund, enclitics after them
NONFINITE_ENDINGS = (
    ("Inf", re.compile(rf"r(?:{'|'.join(ENCLITICS)})*$")),
    ("Ger", re.compile(rf"ndo(?:{'|'.join(ENCLITICS)})*$")),
)
# Relations of the word that links an infinitive to the verb of its periphrasis
LINKING_DEPS = ("mark", "case", "cc")
LINKING_WORDS = frozenset(
    word for words in INFINITIVE_PERIPHRASES.values() for word in words if word
)
# Components the statistics never read
UNUSED_COMPONENTS = ["ner"]


class SyntaxStats(anyts.syntax_stats.SyntaxStats):
    """
    Class for computing the syntactic statistics of a text

    Description:
        Extends the SyntaxStats of the anyTS core with the constructions of the
        Spanish administrative style: the clauses (is_clause_head), the passive
        with ser and with se, the gerund clauses, the chains of de, the words
        of negation of NEGATION_WORDS and the split predicates. A string is
        parsed by the spaCy model; a Doc must carry the dependencies and the
        lemmas

    References:
        https://universaldependencies.org/u/dep/
        https://dialogue-conf.org/media/4302/ivanovvv.pdf

    Example:
        >>> from ests import SyntaxStats
        >>> text = ("La casa, construida por los obreros en 1900, fue vendida. "
        ...         "Dijo que no vendría y se fue dando un portazo.")
        >>> ss = SyntaxStats(text)
        >>> ss.n_sents, ss.n_words
        (2, 20)
        >>> round(ss.mean_dependency_distance, 2)
        2.33
        >>> ss.c_deps["nsubj"]
        2

    Arguments:
        source (str|Doc): Data source (a string or a Doc object)
        nlp (Language): Pipeline of spaCy that parses a string; without it
            the model of SPACY_MODEL is loaded

    Attributes:
        sents (tuple[tuple[Token]]): Words of every sentence with words
        n_sents (int): Number of sentences containing words
        n_words (int): Number of words
        n_leaves (int): Number of leaves - words with no dependent word
        n_subtrees (int): Number of subtrees - words with dependent words
        n_coordination_chains (int): Number of coordination chains
        n_clauses (int): Number of clauses
        n_subordinate_clauses (int): Number of subordinate clauses
        n_complex_sents (int): Number of sentences with a subordinate clause
        n_infinitive_clauses (int): Number of infinitive clauses under a verb
        n_nouns (int): Number of nouns
        n_de_chains (int): Number of chains of de
        n_participle_clauses (int): Number of participial clauses
        n_gerund_clauses (int): Number of gerund clauses
        n_verbs (int): Number of verb forms
        n_passive (int): Number of passive verb forms
        n_agentless_passive (int): Number of passive forms with no agent
        n_se_passives (int): Number of passives with se
        n_impersonal_se (int): Number of impersonal sentences with se
        n_infinitives (int): Number of infinitives
        n_negations (int): Number of words of negation
        n_split_predicates (int): Number of split predicates
        split_predicates (tuple[str]): Tuple of the split predicates (verb and noun)
        c_children (dict[int, int]): Distribution of words by number of dependent words
        c_deps (dict[str, int]): Distribution of words by syntactic relation
        mean_dependency_distance (float): Mean dependency distance
        std_dependency_distance (float): Standard deviation of the dependency distance
        max_dependency_distance (float): Mean of the longest dependencies of the
            sentences, over the sentences that have dependencies
        p_adjacent_dependencies (float): Share of adjacent dependencies - of length 1
        tree_depth (float): Depth of the dependency tree
        leaves_per_sent (float): Leaves per sentence
        subtrees_per_sent (float): Subtrees per sentence
        nodes_per_leaf (float): Mean over the sentences of the words per leaf
        verb_valency (float): Mean number of dependents of a finite verb
        coordination_chains_per_sent (float): Coordination chains per sentence
        mean_coordination_chain_len (float): Mean length of a coordination chain
        clauses_per_sent (float): Clauses per sentence
        mean_clause_len (float): Mean length of a clause in words
        subordinate_clauses_per_sent (float): Subordinate clauses per sentence
        p_complex_sents (float): Share of sentences with at least one subordinate clause
        infinitive_clauses_per_sent (float): Infinitive clauses under a verb per sentence
        modifiers_per_noun (float): Mean number of modifiers of a noun
        de_chains_per_sent (float): Chains of de per sentence
        max_de_chain_len (int): Maximum length of a chain of de
        participle_clauses_per_sent (float): Participial clauses per sentence
        mean_participle_clause_len (float): Mean length of a participial clause in words
        gerund_clauses_per_sent (float): Gerund clauses per sentence
        mean_gerund_clause_len (float): Mean length of a gerund clause in words
        p_passive (float): Share of passive forms among the verb forms
        p_agentless_passive (float): Share of forms with no agent among the passive ones
        se_passives_per_sent (float): Passives with se per sentence
        impersonal_se_per_sent (float): Impersonal sentences with se per sentence
        infinitives_per_sent (float): Infinitives per sentence
        negations_per_sent (float): Words of negation per sentence
        split_predicates_per_sent (float): Split predicates per sentence
        noun_verb_ratio (float): Ratio of the number of nouns to the number of verb forms

    Methods:
        describe: Reading of a statistic by its scale, None for every statistic
        get_stats: Getting the computed syntactic statistics of the text
        to_dataframe: Getting the statistics as a table of one row
        print_stats: Printing the computed syntactic statistics with descriptions

    Raises:
        SourceTypeError: If the source is neither a string nor a Doc object, or the
            pipeline is not a spaCy Language
        SourceError: If the source has no words, no parse or no lemmas, or is
            a string longer than the max_length of the pipeline or with a character
            without a UTF-8 form
        DatasetNotFoundError: If a string is passed and the model is not installed
    """

    requires_lemmas = True
    negation_words = NEGATION_WORDS
    stats_desc = SYNTAX_STATS_DESC

    def __init__(self, source: str | Doc, nlp: Language | None = None):
        if nlp is not None and not isinstance(nlp, Language):
            raise SourceTypeError("The pipeline must be a spaCy Language")
        # The pipeline only parses the source: kept, it would go into a pickle of the object
        self._nlp = nlp
        try:
            super().__init__(source)  # type: ignore[arg-type]  # parse takes a string too
        finally:
            del self._nlp
        words = [token for sent in self.sents for token in sent]
        de_chains = [length for sent in self.sents for length in calc_de_chains(sent)]
        self.n_de_chains = len(de_chains)
        gerund_clauses = [subtree_len(token) for token in words if is_gerund_clause(token)]
        self.n_gerund_clauses = len(gerund_clauses)
        self.n_se_passives = sum(1 for token in words if token.dep_ == SE_PASSIVE_DEP)
        self.n_impersonal_se = sum(1 for token in words if token.dep_ == SE_IMPERSONAL_DEP)
        self.de_chains_per_sent = self.n_de_chains / self.n_sents
        self.max_de_chain_len = max(de_chains, default=0)
        self.gerund_clauses_per_sent = self.n_gerund_clauses / self.n_sents
        self.mean_gerund_clause_len = fmean(gerund_clauses) if gerund_clauses else nan
        self.se_passives_per_sent = self.n_se_passives / self.n_sents
        self.impersonal_se_per_sent = self.n_impersonal_se / self.n_sents

    def parse(self, source: str | Doc) -> Doc:
        """
        Getting the Doc of a source

        Description:
            A string is parsed by nlp or get_nlp() without the named entities;
            a Doc is taken as it is

        Arguments:
            source (str|Doc): Data source

        Returns:
            Doc: Doc with a dependency parse

        Raises:
            SourceTypeError: If the source is neither a string nor a Doc object
            SourceError: If a string is longer than the max_length of the pipeline or
                has a character without a UTF-8 form
            DatasetNotFoundError: If a string is passed and the model is not installed
        """
        if isinstance(source, str):
            pipeline = self._nlp or get_nlp()
            if len(source) > pipeline.max_length:
                raise SourceError(
                    f"The text of {len(source)} characters is longer than the limit of the "
                    f"pipeline ({pipeline.max_length}): split it into parts or raise "
                    "max_length on a pipeline of your own and pass it in nlp"
                )
            _check_encoding(source)
            return pipeline(source, disable=UNUSED_COMPONENTS)
        return super().parse(source)

    def is_clause_head(self, token: Token) -> bool:
        """Head of a clause by the Spanish rules (is_clause_head)"""
        return is_clause_head(token)

    def is_subordinate_clause_head(self, token: Token) -> bool:
        """Head of a subordinate clause by the Spanish rules (is_subordinate_clause_head)"""
        return is_subordinate_clause_head(token)

    def is_passive(self, token: Token) -> bool:
        """Passive with ser or with se (is_passive)"""
        return is_passive(token)

    def is_agentless(self, token: Token) -> bool:
        """Passive form with no complement of por (is_agentless)"""
        return is_agentless(token)

    def find_split_predicates(self, words: Sequence[Token]) -> list[tuple[Token, Token]]:
        """Split predicates of a light verb and a verbal noun (find_split_predicates)"""
        return find_split_predicates(words)


def is_participle(token: Token) -> bool:
    """
    Checking whether a token is a participle

    Description:
        A word with VerbForm=Part, whatever its part of speech: the models tag
        a participle that modifies a noun (la casa pintada) as an adjective

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return has_feature(token, "VerbForm", "Part")


def is_gerund(token: Token) -> bool:
    """
    Checking whether a token is a gerund

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return has_feature(token, "VerbForm", "Ger")


def is_negation(token: Token) -> bool:
    """
    Checking whether a token is a word of negation

    Description:
        A word with Polarity=Neg or one of NEGATION_WORDS; the conjunction ni
        is not. Every such word counts, so no vino nadie gives two

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if token.pos_ in ("CCONJ", "SCONJ"):
        return False
    return has_feature(token, "Polarity", "Neg") or token.text.lower() in NEGATION_WORDS


def is_clause_head(token: Token) -> bool:
    """
    Checking whether a token heads a clause

    Description:
        The head of the sentence or a word with the relation ccomp, advcl, acl
        or csubj, and under xcomp an infinitive (is_infinitive_clause: quiere
        salir) or a finite predicate, which the models give to some finite
        complements. The form of a predicate (predicate_form) decides:
        a participle or a gerund is counted apart (llegando tarde, habiendo
        llegado tarde), an infinitive under acl is no clause (el deseo de
        irse, el miedo de ser robado), and había llegado and estaba cantando
        are finite. A parataxis or a conj of the head of a clause counts only
        as a predicate (is_predicate), so that parentheticals such as por
        ejemplo are no clauses, and an infinitive the models attach as conj
        to a verb of INFINITIVE_PERIPHRASES makes a periphrasis with it
        (tiene que salir, va a salir)

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if not is_word(token):
        return False
    if is_root(token):
        return True
    form = predicate_form(token)
    if form in ("Ger", "Part"):
        return False
    if token.dep_ == "xcomp":
        return form == "Fin" or is_infinitive_clause(token)
    if token.dep_ not in CLAUSE_DEPS:
        return (
            token.dep_ == "conj"
            and not (form == "Inf" and is_infinitive_periphrasis(token))
            and is_clause_head(token.head)
            and is_predicate(token)
        )
    if token.dep_ == "parataxis":
        return is_predicate(token)
    return not (token.dep_ == "acl" and form == "Inf")


def is_subordinate_clause_head(token: Token) -> bool:
    """
    Checking whether a token heads a subordinate clause

    Description:
        The head of a clause with the relation ccomp, advcl, acl, csubj or
        xcomp, and a coordinated predicate of a subordinate clause

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return is_clause_head(token) and _is_subordinate(token)


def _is_subordinate(token: Token) -> bool:
    """Whether a clause head heads a subordinate clause, up its chain of conjuncts"""
    while not is_root(token):
        if token.dep_ in SUBORDINATE_CLAUSE_DEPS or token.dep_ == "xcomp":
            return True
        if token.dep_ != "conj" or not is_clause_head(token.head):
            return False
        token = token.head
    return False


def is_infinitive_clause(token: Token) -> bool:
    """
    Checking whether an infinitive under xcomp heads a clause of its own

    Description:
        A predicate in the form of an infinitive (predicate_form) that
        completes its head (quiere salir, le hizo reír, quiere ser médico,
        quiere ser elegido, cree haber ganado), unless the two
        make a periphrasis (is_infinitive_periphrasis: puede salir, vuelve a
        salir) or the head is a verb of RAISING_VERBS (parece dormir);
        a predicative adjective (parece cansado) is no clause

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return (
        predicate_form(token) == "Inf"
        and not is_infinitive_periphrasis(token)
        and _head_verb(token, RAISING_VERBS) not in RAISING_VERBS
    )


def is_infinitive_periphrasis(token: Token) -> bool:
    """
    Checking whether an infinitive makes a periphrasis with its head

    Description:
        The head is a verb of INFINITIVE_PERIPHRASES and the infinitive is
        linked to it by one of the words of that verb: a mark, case or cc
        before the infinitive or the word right before it, the old spelling
        á read as a; the verbs taking no word (puede salir) need none

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    allowed = INFINITIVE_PERIPHRASES.get(_head_verb(token, INFINITIVE_PERIPHRASES))
    if allowed is None:
        return False
    links: set[str | None] = {
        _linking_word(child)
        for child in token.children
        if child.i < token.i and base_dep(child) in LINKING_DEPS
    }
    # The models parse the old spelling á as a dependent of the head
    if token.i - 1 > token.head.i:
        previous = _linking_word(token.doc[token.i - 1])
        if previous in LINKING_WORDS:
            links.add(previous)
    return bool(allowed & (links or {None}))


def _head_verb(token: Token, verbs: Collection[str]) -> str:
    """
    Lemma of the head of a token looked up among some verbs

    Description:
        The first word of the lemma of the model (it can give hacer él); when
        it is none of the verbs, the lemma of lemmatize, since the model can
        read a verb opening a sentence as a proper noun (Solía salir) or
        invent a lemma for an old form (debiérar)
    """
    words = token.head.lemma_.lower().split()
    lemma = words[0] if words else ""
    return lemma if lemma in verbs else lemmatize(token.head.text.lower())


def _linking_word(token: Token) -> str:
    """Text of a word that may link an infinitive, the old spelling á read as a"""
    return token.text.lower().replace("á", "a")


def is_de_modifier(token: Token) -> bool:
    """
    Checking whether a token is a complement introduced by de

    Description:
        A word with the relation nmod whose preposition is de or its contraction
        del: el uso del agua, but not la vuelta al campo

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if base_dep(token) != "nmod":
        return False
    return any(
        child.dep_ == "case" and child.text.lower() in DE_PREPOSITIONS for child in token.children
    )


def calc_de_chains(tokens: Iterable[Token]) -> list[int]:
    """
    Computing the lengths of the chains of de

    Description:
        A chain is two or more nested complements with de: el aumento de la
        eficiencia del uso de los recursos (length 3); the length is the number
        of complements in the longest branch

    Arguments:
        tokens (Doc|Span|list[Token]): Sequence of tokens

    Returns:
        list[int]: Lengths of the chains in the order of the words
    """
    return calc_modifier_chains(tokens, is_de_modifier)


def is_participle_clause(token: Token) -> bool:
    """
    Checking whether a token heads a participial clause

    Description:
        A participle with a valency above 0 (calc_valency) and no auxiliary:
        ha pintado and fue construida are predicates, not clauses

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if not is_participle(token) or is_root(token) or has_auxiliary(token):
        return False
    return calc_valency(token) > 0


def is_gerund_clause(token: Token) -> bool:
    """
    Checking whether a token heads a gerund clause

    Description:
        A predicate in the form of a gerund (predicate_form: llegando tarde,
        habiendo llegado tarde) with a valency above 0, its auxiliaries left
        out (calc_valency), outside a periphrasis: está cantando is finite,
        and a gerund under a verb of GERUND_PERIPHRASIS_VERBS (sigue
        trabajando) is none

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if predicate_form(token) != "Ger" or is_root(token):
        return False
    if token.dep_ in PERIPHRASIS_DEPS and token.head.lemma_.lower() in GERUND_PERIPHRASIS_VERBS:
        return False
    return _valency(token) > 0


def _valency(token: Token) -> int:
    """Valency of a predicate without its auxiliaries and copulas"""
    return calc_valency(token) - sum(
        1 for child in token.children if base_dep(child) in AUXILIARY_DEPS
    )


def predicate_form(token: Token) -> str:
    """
    Getting the verb form of a predicate

    Description:
        The form of the auxiliaries and copulas of a word: Fin when one of them
        is finite or the first one is a participle, else the form of the first
        one (había llegado is finite, de haber matado an infinitive, siendo
        elegido a gerund), and without them the form of the word itself. An auxiliary the
        model leaves without a form is read by its ending when it is a verb of
        AUXILIARY_VERBS (habéis llegado) and skipped otherwise (the old
        spelling á). A participle auxiliary counts as finite: sido and estado
        follow a form of haber, which the models may attach to another word
        (hubieras sido albañil). The predicate_form of the core with the
        Spanish reading of an auxiliary without a form

    Arguments:
        token (Token): Token

    Returns:
        str: Fin, Inf, Ger or Part, an empty string for a word with no verb form
    """
    return anyts.syntax_stats.predicate_form(token, _auxiliary_form)


def _auxiliary_form(token: Token) -> str:
    """Verb form of an auxiliary the model leaves without one, by its ending"""
    word = token.text.lower()
    if lemmatize(word) not in AUXILIARY_VERBS:
        return ""
    return next((form for form, ending in NONFINITE_ENDINGS if ending.search(word)), "Fin")


def has_auxiliary(token: Token) -> bool:
    """
    Checking whether a token carries an auxiliary or a copula

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return any(base_dep(child) in AUXILIARY_DEPS for child in token.children)


def is_passive(token: Token) -> bool:
    """
    Checking whether a token is a passive verb form

    Description:
        A verb that is a participle with the auxiliary ser, as aux or cop (la
        casa fue construida, el proyecto es financiado), or carries the se of
        the passive (se construyó la casa). A participle that modifies a noun
        (la casa construida por los obreros) is a participial clause instead

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if token.pos_ != "VERB":
        return False
    if any(child.dep_ == SE_PASSIVE_DEP for child in token.children):
        return True
    if not is_participle(token):
        return False
    return any(
        base_dep(child) in AUXILIARY_DEPS and child.lemma_ == PASSIVE_AUX
        for child in token.children
    )


def is_agentless(token: Token) -> bool:
    """
    Checking whether a token is a passive form with no agent

    Description:
        A passive form with no complement introduced by por: la casa fue
        construida, but not la casa fue construida por los obreros

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    if not is_passive(token):
        return False
    return not any(is_agent(child) for child in get_children(token))


def is_agent(token: Token) -> bool:
    """
    Checking whether a token is the agent of a passive

    Description:
        A complement whose preposition is por, whatever its relation: the
        models have no obl:agent

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return any(
        child.dep_ == "case" and child.text.lower() == AGENT_PREPOSITION
        for child in token.children
    )


def is_light_verb(token: Token) -> bool:
    """
    Checking whether a token is a light verb

    Description:
        A verb with a lemma of LIGHT_VERBS (hacer, dar, tomar, realizar...)

    Arguments:
        token (Token): Token

    Returns:
        bool: Result of the check
    """
    return token.pos_ == "VERB" and token.lemma_.lower() in LIGHT_VERBS


def is_split_predicate_noun(token: Token, verb: Token) -> bool:
    """
    Checking whether a token can be the nominal part of a split predicate

    Description:
        A noun with a lemma derived from a verb (is_verbal_noun: revisión, uso),
        or a noun of SPLIT_PREDICATE_NOUNS with the verb of its fixed expression
        (cabo with llevar, parte with tomar)

    Arguments:
        token (Token): Token
        verb (Token): Verb the token depends on

    Returns:
        bool: Result of the check
    """
    if token.pos_ != "NOUN":
        return False
    lemma = token.lemma_.lower()
    if is_verbal_noun(lemma):
        return True
    return verb.lemma_.lower() in SPLIT_PREDICATE_NOUNS.get(lemma, ())


def find_split_predicates(tokens: Iterable[Token]) -> list[tuple[Token, Token]]:
    """
    Finding the split predicates

    Description:
        A light verb (is_light_verb) with a nominal part of its own
        (is_split_predicate_noun): hacer una revisión, llevar a cabo la reforma,
        se procedió a la votación
        A verb takes one nominal part at most, preferred by relation in the
        order compound, obj, nsubj (only with the se of the passive), iobj,
        nmod, obl. A complement with a preposition is left out unless the pair
        is a fixed expression of SPLIT_PREDICATE_NOUNS or the verb is one of
        PREPOSITIONAL_LIGHT_VERBS; the agent of a passive is always left out

    Arguments:
        tokens (Doc|Span|list[Token]): Sequence of tokens

    Returns:
        list[tuple[Token, Token]]: Pairs of verb and noun in the order of the words
    """
    pairs = []
    for token in get_words(tokens):
        if not is_light_verb(token):
            continue
        candidates = [
            child
            for child in get_children(token)
            if is_split_predicate_noun(child, token) and _is_nominal_part(child, token)
        ]
        if candidates:
            pairs.append((token, min(candidates, key=_nominal_part_rank)))
    return pairs


def _is_nominal_part(child: Token, verb: Token) -> bool:
    dep = base_dep(child)
    if dep not in SPLIT_PREDICATE_DEPS:
        return False
    if dep == "nsubj":
        return any(grandchild.dep_ == SE_PASSIVE_DEP for grandchild in verb.children)
    if is_agent(child):
        return False
    if (
        verb.lemma_.lower() in SPLIT_PREDICATE_NOUNS.get(child.lemma_.lower(), ())
        or verb.lemma_.lower() in PREPOSITIONAL_LIGHT_VERBS
    ):
        return True
    return not any(grandchild.dep_ == "case" for grandchild in child.children)


def _nominal_part_rank(child: Token) -> int:
    return SPLIT_PREDICATE_DEPS.index(base_dep(child))
