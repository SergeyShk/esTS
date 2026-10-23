from __future__ import annotations

import re
from collections.abc import Iterator
from functools import lru_cache
from typing import TYPE_CHECKING

import simplemma
from anyts.extractors import iter_part_sents
from anyts.utils import (
    add_tokenizer_rules,
    count_words_by_spans as count_words_by_spans,
    find_phrases as find_phrases,
    is_language,
    iter_doc_words,
)

from .constants import (
    ABBREVIATIONS,
    DASHES,
    SENTENCE_OPENERS,
    SPACY_MODEL,
    TOKENIZER_ABBREVIATIONS,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import DatasetNotFoundError, SourceError, SourceTypeError

if TYPE_CHECKING:
    from spacy.language import Language
    from spacy.tokenizer import Tokenizer

# End of a sentence: terminal marks, optionally closing quotes or brackets and a dash
# that closes a line of dialogue (¡Traidores!--), before whitespace, the end of the text
# or a dash glued to them that opens a line of dialogue (baja.--Tiene) - a raya or a run
# of hyphens before the next word or opening mark within the line, not a digit and not
# the punctuation after a closing dash, or a single hyphen before an opening mark
# (cuatro.-¿Cinco?), since one before a word numbers an article (Artículo 1.- Objeto)
SENTENCE_END = re.compile(
    r"(?<![.!?…])(?P<marks>[.!?…]++)(?P<closers>[»”’\"')\]]*)"
    rf"(?P<dash>(?:--+|[—–―][{DASHES}]*)(?=\s|$))?"
    rf"(?=\s|$|(?:--+|[—–―][{DASHES}]*)[ \t]*+[^\s\d.,;:!?…{DASHES}]|-[¿¡«“])"
)
NON_SPACE = re.compile(r"\S")
NON_DASH = re.compile(rf"[^\s{DASHES}]")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
# A period inside an abbreviation written without spaces (a.C., p.ej., EE.UU.)
INNER_PERIOD = re.compile(r"\.(?=\w)")
# Marker of a list (1. 2.1. b. IV.) that opens a sentence or a line, at the end of the window
LIST_MARKER = re.compile(r"(?:^|\n)[ \t]*(?:\d+(?:\.\d+)*|[a-z]|[IVXLC]+)\.\Z")
OPENING_CHARS = "(«“\"'["
# Characters looked back from a period for an abbreviation or an initial
LOOKBACK = 64
# Byte order mark glued to the start of a text read with utf-8 instead of utf-8-sig
BYTE_ORDER_MARK = "\ufeff"
# Components of spaCy that set the sentences of a Doc
SENTENCE_SETTERS = ("parser", "senter", "sentencizer")


def _opens_remark(text: str, position: int) -> bool:
    """
    Whether the dash before the position opens the remark of the narrator

    Description:
        A remark of the narrator opens in lower case ("-Sí -dijo él"),
        a new line of dialogue in upper case

    Arguments:
        text (str): Text string
        position (int): Position right after the dash

    Returns:
        bool: Result of the check
    """
    following = NON_DASH.search(text, position)
    return following is not None and following.group().islower()


def _ends_sentence(text: str, start: int, match: re.Match[str]) -> bool:
    """
    Checking whether the terminal marks found in a text end a sentence

    Description:
        The rules of sentenize; the next non-space character must be an
        upper-case letter, a digit or one of SENTENCE_OPENERS. Opening quotes
        and brackets are stripped from the tokens before the abbreviation
        check, so "(EE. UU. Es grande)" stays together

    Arguments:
        text (str): Text string
        start (int): Position where the current sentence starts
        match (Match): Match of SENTENCE_END in the text

    Returns:
        bool: Result of the check
    """
    following = NON_SPACE.search(text, match.end())
    if following is None:
        return True
    first = following.group()
    if not (first.isupper() or first.isdigit() or first in SENTENCE_OPENERS):
        return False
    if first in DASHES and _opens_remark(text, following.end()):
        return False
    if match.group("marks") != "." or match.group("closers"):
        return True
    window_start = max(start, match.end("marks") - LOOKBACK)
    window = text[window_start : match.end("marks")]
    if LIST_MARKER.search(window):
        return False
    tokens = [stripped for token in window.split() if (stripped := token.lstrip(OPENING_CHARS))]
    last = tokens[-1].lower()
    return not (
        INITIAL.fullmatch(tokens[-1])
        or last in ABBREVIATIONS
        or INNER_PERIOD.sub(". ", last) in ABBREVIATIONS
        or " ".join(tokens[-2:]).lower() in ABBREVIATIONS
    )


def sentenize(text: str) -> Iterator[str]:
    """
    Splitting a text into sentences by rules

    Description:
        A sentence ends with a period, an exclamation or question mark or
        an ellipsis, possibly followed by closing quotes or brackets, when
        the next word starts with an upper-case letter, a digit, an inverted
        mark, an opening quote or bracket or a dash, also a dash glued to
        the mark (baja.--Tiene), while a glued dash before whitespace closes
        a line of dialogue and stays with its sentence; a blank line ends one
        too. A dash before a lower-case word opens a remark of the narrator
        and keeps the sentence going. A single period after an abbreviation
        (Sr., p. ej., EE. UU., also without spaces: p.ej.), a capital initial
        or a list marker opening a sentence or a line (1. 2.1. IV.) does not
        end a sentence, nor does a single line break. Sentences are stripped
        of surrounding whitespace

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of sentences

    Raises:
        SourceTypeError: If the text is not a string
    """
    return (sent for _, _, sent in iter_text_sents(text))


def iter_text_sents(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Splitting a text into sentences with positions

    Description:
        The sentences of sentenize with their positions in the string; the parts
        of the text between blank lines are split one by one (iter_part_sents of
        the core)

    Arguments:
        text (str): Text string

    Returns:
        iterator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each sentence

    Raises:
        SourceTypeError: If the text is not a string

    Example:
        >>> from ests.utils import iter_text_sents
        >>> list(iter_text_sents("Hola.  ¿Qué tal?"))
        [(0, 5, 'Hola.'), (7, 16, '¿Qué tal?')]
    """
    return iter_part_sents(_iter_sents, text)


def _iter_sents(text: str) -> Iterator[tuple[int, int, str]]:
    """Sentences of a part of a text without blank lines, with their positions"""
    start = 0
    for match in SENTENCE_END.finditer(text):
        if not _ends_sentence(text, start, match):
            continue
        yield from _stripped_span(text, start, match.end())
        start = match.end()
    yield from _stripped_span(text, start, len(text))


def _stripped_span(text: str, start: int, stop: int) -> Iterator[tuple[int, int, str]]:
    """The span of the text between the positions without surrounding whitespace, if any is left"""
    chunk = text[start:stop]
    sent = chunk.strip()
    if sent:
        begin = start + len(chunk) - len(chunk.lstrip())
        yield begin, begin + len(sent), sent


@lru_cache(maxsize=1)
def get_tokenizer() -> Tokenizer:
    """
    Getting the rule-based tokenizer of the spaCy Spanish language class

    Description:
        The tokenizer of a blank "es" pipeline, with the rules of add_dash_rules

    Returns:
        Tokenizer: spaCy tokenizer
    """
    import spacy

    nlp = spacy.blank("es")
    add_dash_rules(nlp)
    return nlp.tokenizer


def add_dash_rules(nlp: Language) -> None:
    """
    Adding the rules for the dashes of a dialogue to the tokenizer of a pipeline

    Description:
        The rules of TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES and TOKENIZER_INFIXES
        split the dashes glued to the words off (--No, -dijo, reírse—me,
        dijo:—¡Mis) and leave a hyphen between letters (franco-alemán) or before
        a digit (-5) alone; a byte order mark glued to the start of a text is
        split off as well, so the marks after it are split as usual. The
        abbreviations of TOKENIZER_ABBREVIATIONS become single tokens in lower
        case, capitalized and in upper case (sr., Sr., SR.), when the tokenizer
        keeps one of their forms whole; get_tokenizer and get_nlp
        have the rules already. The add_tokenizer_rules of the core: a rule the
        tokenizer has is not added twice, and a tokenizer that is not the
        Tokenizer of spaCy, or whose rules are not regular expressions, is left
        as it is

    Arguments:
        nlp (Language): Pipeline whose tokenizer gets the rules

    Example:
        >>> import spacy
        >>> from ests.utils import add_dash_rules
        >>> nlp = spacy.blank("es")
        >>> [token.text for token in nlp("--No --dijo él.")]
        ['--No', '--dijo', 'él', '.']
        >>> add_dash_rules(nlp)
        >>> [token.text for token in nlp("--No --dijo él.")]
        ['--', 'No', '--', 'dijo', 'él', '.']
    """
    add_tokenizer_rules(
        nlp,
        prefixes=(BYTE_ORDER_MARK, *TOKENIZER_PREFIXES),
        suffixes=TOKENIZER_SUFFIXES,
        infixes=TOKENIZER_INFIXES,
        abbreviations=TOKENIZER_ABBREVIATIONS,
    )


def _check_nlp(nlp: object) -> None:
    """A pipeline that is not a spaCy Language (is_language)"""
    if nlp is not None and not is_language(nlp):
        raise SourceTypeError("The pipeline must be a spaCy Language")


def _check_encoding(text: str) -> None:
    """A text the tokenizer of spaCy cannot read: a lone surrogate has no UTF-8 form"""
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as error:
        raise SourceError(
            f"The text has a character without a UTF-8 form at {error.start}: "
            "read the file again with its encoding"
        ) from None


def tokenize(text: str) -> Iterator[str]:
    """
    Splitting a text into tokens with the spaCy Spanish tokenizer

    Description:
        Whitespace tokens are dropped; punctuation marks (¿, ¡), numbers
        (1.500,50, 3.º, 1990-1995), abbreviations (Sr., EE. UU.) and words
        with enclitic pronouns (dámelo) are single tokens; the dashes of
        a dialogue are split off by add_dash_rules; a byte order mark glued to
        the start of a token is dropped

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of tokens

    Raises:
        SourceError: If the text has a character without a UTF-8 form
    """
    _check_encoding(text)
    return (
        word
        for token in get_tokenizer()(text)
        if not token.is_space and (word := token.text.lstrip(BYTE_ORDER_MARK))
    )


@lru_cache(maxsize=131072)
def lemmatize(word: str) -> str:
    """
    Lemmatizing a word form with simplemma, with caching

    Description:
        A known form is mapped to its lower-case lemma (Tienes - tener,
        cantándole - cantar), an unknown form is returned unchanged (Madrid,
        dámelo)

    Arguments:
        word (str): Word form

    Returns:
        str: Lemma
    """
    return simplemma.lemmatize(word, lang="es") if word != "" else word


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Extracting words with positions from a string

    Description:
        The tokens of get_tokenizer without punctuation marks and symbols,
        as in WordsExtractor

    Arguments:
        text (str): Text string

    Returns:
        iterator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each word

    Raises:
        SourceError: If the text has a character without a UTF-8 form

    Example:
        >>> from ests.utils import iter_text_words
        >>> list(iter_text_words("¡Hola, mundo!"))
        [(1, 5, 'Hola'), (7, 12, 'mundo')]
    """
    _check_encoding(text)
    return iter_doc_words(get_tokenizer()(text))


@lru_cache(maxsize=4)
def _load_nlp(model: str) -> Language:
    """Loading a pipeline by the name of its model, once per name, with the dash rules"""
    import spacy

    from . import components  # noqa: F401  # registers ests_blank_lines

    try:
        nlp = spacy.load(model)
    except OSError as error:
        raise DatasetNotFoundError(
            f"The spaCy model {model} is not installed: python -m spacy download {model}"
        ) from error
    add_dash_rules(nlp)
    setters = [name for name in nlp.pipe_names if name in SENTENCE_SETTERS]
    if setters and "ests_blank_lines" not in nlp.component_names:
        nlp.add_pipe("ests_blank_lines", before=setters[0])
    return nlp


def get_nlp(model: str = SPACY_MODEL) -> Language:
    """
    Loading a spaCy pipeline, once per process

    Description:
        The tokenizer of the pipeline gets the rules of add_dash_rules, and the
        component ests_blank_lines goes before the parser, senter or sentencizer,
        so a blank line ends a sentence of a Doc as of a string

    Arguments:
        model (str): Name of the model

    Returns:
        Language: Loaded pipeline

    Raises:
        DatasetNotFoundError: If the model is not installed

    Example:
        >>> from ests.utils import get_nlp
        >>> get_nlp() is get_nlp("es_core_news_sm")
        True
    """
    return _load_nlp(model)


def is_verbal_noun(lemma: str) -> bool:
    """
    Checking whether a lemma is a noun derived from a verb, by its suffix

    Description:
        A suffix of VERBAL_NOUN_SUFFIXES (-ción, -miento, -aje...) or a lemma
        of VERBAL_NOUN_LEMMAS, the nouns derived without a suffix (uso, pago);
        nouns of other origins with the same endings match too (ciencia)

    Arguments:
        lemma (str): Lemma of a noun

    Returns:
        bool: Result of the check

    Example:
        >>> from ests.utils import is_verbal_noun
        >>> is_verbal_noun("revisión"), is_verbal_noun("uso"), is_verbal_noun("casa")
        (True, True, False)
    """
    lemma = lemma.lower()
    return lemma.endswith(VERBAL_NOUN_SUFFIXES) or lemma in VERBAL_NOUN_LEMMAS
