import re
from collections.abc import Iterable, Iterator, Sequence
from functools import lru_cache

import simplemma
import spacy
from anyts.utils import check_words, iter_doc_words
from spacy.language import Language
from spacy.tokenizer import Tokenizer

from .constants import (
    ABBREVIATIONS,
    DASHES,
    SENTENCE_OPENERS,
    SPACY_MODEL,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import DatasetNotFoundError

# End of a sentence: terminal marks, optionally closing quotes or brackets and a dash
# that closes a line of dialogue at the end of a line (¡Traidores!--), before whitespace,
# the end of the text or a dash glued to them that opens a line of dialogue (baja.--Tiene)
# - a raya or a run of hyphens before the next word or opening mark within the line, not
# a digit and not the punctuation after a closing dash, or a single hyphen before an
# opening mark (cuatro.-¿Cinco?), since one before a word numbers an article (Artículo
# 1.- Objeto); or a blank line
SENTENCE_END = re.compile(
    r"(?P<marks>[.!?…]+)(?P<closers>[»”’\"')\]]*)"
    rf"(?P<dash>(?:--+|[—–―][{DASHES}]*)(?=[ \t]*+(?:\n|$)))?"
    rf"(?=\s|$|(?:--+|[—–―][{DASHES}]*)[ \t]*+[^\s\d.,;:!?…{DASHES}]|-[¿¡«“])"
    r"|(?P<break>\n[ \t\r\f\v]*\n)"
)
NON_SPACE = re.compile(r"\S")
NON_DASH = re.compile(rf"[^\s{DASHES}]")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
# Marker of a list (1. 2.1. b. IV.) that opens a sentence or a line, at the end of the window
LIST_MARKER = re.compile(r"(?:^|\n)[ \t]*(?:\d+(?:\.\d+)*|[a-z]|[IVXLC]+)\.\Z")
OPENING_CHARS = "(«“\"'["
# Characters looked back from a period for an abbreviation or an initial
LOOKBACK = 64
# Byte order mark glued to the start of a text read with utf-8 instead of utf-8-sig
BYTE_ORDER_MARK = "\ufeff"


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
    if match.group("marks") != "." or match.group("closers") or match.group("dash"):
        return True
    window_start = max(start, match.end() - LOOKBACK)
    window = text[window_start : match.end()]
    if LIST_MARKER.search(window):
        return False
    tokens = [stripped for token in window.split() if (stripped := token.lstrip(OPENING_CHARS))]
    last = tokens[-1]
    return not (
        INITIAL.fullmatch(last)
        or last.lower() in ABBREVIATIONS
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
        the mark (baja.--Tiene), while a glued dash at the end of a line
        stays with its sentence; a blank line ends one too. A dash before
        a lower-case word opens a remark of the narrator and keeps the
        sentence going. A single period after an abbreviation
        (Sr., p. ej., EE. UU.), a capital initial or a list marker opening
        a sentence or a line (1. 2.1. IV.) does not end a sentence, nor does
        a single line break. Sentences are stripped of surrounding whitespace

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of sentences
    """
    return (sent for _, _, sent in iter_text_sents(text))


def iter_text_sents(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Splitting a text into sentences with positions

    Description:
        The sentences of sentenize with their positions in the string

    Arguments:
        text (str): Text string

    Returns:
        iterator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each sentence

    Example:
        >>> from ests.utils import iter_text_sents
        >>> list(iter_text_sents("Hola.  ¿Qué tal?"))
        [(0, 5, 'Hola.'), (7, 16, '¿Qué tal?')]
    """
    start = 0
    for match in SENTENCE_END.finditer(text):
        if match.group("break") is None and not _ends_sentence(text, start, match):
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
        split off as well, so the marks after it are split as usual;
        get_tokenizer and get_nlp have them already.
        A rule the tokenizer has is not added twice; a tokenizer that is not
        the Tokenizer of spaCy, or whose rules are not regular expressions,
        is left as it is

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
    tokenizer = nlp.tokenizer
    if not isinstance(tokenizer, Tokenizer):
        return
    prefixes = _extend_rules(
        tokenizer.prefix_search, [f"^{rule}" for rule in (BYTE_ORDER_MARK, *TOKENIZER_PREFIXES)]
    )
    suffixes = _extend_rules(tokenizer.suffix_search, [f"{rule}$" for rule in TOKENIZER_SUFFIXES])
    infixes = _extend_rules(tokenizer.infix_finditer, list(TOKENIZER_INFIXES))
    if prefixes is not None:
        tokenizer.prefix_search = prefixes.search
    if suffixes is not None:
        tokenizer.suffix_search = suffixes.search
    if infixes is not None:
        tokenizer.infix_finditer = infixes.finditer


def _extend_rules(method: object, rules: list[str]) -> re.Pattern[str] | None:
    """
    Regular expression of a tokenizer extended with the rules it does not have yet

    Description:
        The expression is read from a bound method of the tokenizer
        (prefix_search, suffix_search, infix_finditer); no method gives the
        rules alone, a method not bound to a regular expression gives None
    """
    if method is None:
        return re.compile("|".join(rules))
    pattern = getattr(getattr(method, "__self__", None), "pattern", None)
    if not isinstance(pattern, str):
        return None
    missing = [rule for rule in rules if rule not in pattern]
    return re.compile("|".join([pattern, *missing]))


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
    """
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

    Example:
        >>> from ests.utils import iter_text_words
        >>> list(iter_text_words("¡Hola, mundo!"))
        [(1, 5, 'Hola'), (7, 12, 'mundo')]
    """
    return iter_doc_words(get_tokenizer()(text))


def count_words_by_spans(starts: Sequence[int], spans: Sequence[tuple[int, int]]) -> list[int]:
    """
    Counting the words in every span of a text by the positions of the words and the spans

    Arguments:
        starts (list[int]): Positions of the first characters of the words in order
        spans (list[tuple[int, int]]): Spans in order - the start and the position
            after the end

    Returns:
        list[int]: Number of words in every span; spans without words are skipped

    Example:
        >>> from ests.utils import count_words_by_spans, iter_text_sents, iter_text_words
        >>> text = "El gato duerme. ¿Y el perro? Come."
        >>> starts = [start for start, _, _ in iter_text_words(text)]
        >>> count_words_by_spans(starts, [(start, stop) for start, stop, _ in iter_text_sents(text)])
        [3, 3, 1]
    """
    lengths = []
    index = 0
    for start, stop in spans:
        count = 0
        while index < len(starts) and starts[index] < stop:
            count += starts[index] >= start
            index += 1
        lengths.append(count)
    return [length for length in lengths if length]


@lru_cache(maxsize=4)
def _load_nlp(model: str) -> Language:
    """Loading a pipeline by the name of its model, once per name, with the dash rules"""
    try:
        nlp = spacy.load(model)
    except OSError as error:
        raise DatasetNotFoundError(
            f"The spaCy model {model} is not installed: python -m spacy download {model}"
        ) from error
    add_dash_rules(nlp)
    return nlp


def get_nlp(model: str = SPACY_MODEL) -> Language:
    """
    Loading a spaCy pipeline, once per process

    Description:
        The tokenizer of the pipeline gets the rules of add_dash_rules

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


def find_phrases(words: Sequence[str], phrases: Iterable[str]) -> list[tuple[int, int]]:
    """
    Finding phrases in a sequence of words

    Description:
        The words and the phrases are compared in lower case; at every position
        the longest phrase is taken, and the phrases found do not overlap

    Arguments:
        words (list[str]): Words of the text
        phrases (list[str]): Phrases, words separated by spaces

    Returns:
        list[tuple[int, int]]: Bounds of the phrases found as slices of words;
            empty phrases are skipped

    Raises:
        SourceTypeError: If the words are not a list of strings

    Example:
        >>> from ests.utils import find_phrases
        >>> find_phrases(["Sin", "embargo", "no", "llegó"], ["sin embargo", "sin"])
        [(0, 2)]
    """
    check_words(words)
    patterns = sorted(
        {pattern for phrase in phrases if (pattern := tuple(phrase.lower().split()))},
        key=len,
        reverse=True,
    )
    by_first: dict[str, list[tuple[str, ...]]] = {}
    for pattern in patterns:
        by_first.setdefault(pattern[0], []).append(pattern)
    lowered = [word.lower() for word in words]
    spans = []
    position = 0
    while position < len(lowered):
        for pattern in by_first.get(lowered[position], ()):
            end = position + len(pattern)
            if tuple(lowered[position:end]) == pattern:
                spans.append((position, end))
                position = end
                break
        else:
            position += 1
    return spans
