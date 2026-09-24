import re
import unicodedata
from collections.abc import Iterator, Sequence
from functools import lru_cache

import simplemma
import spacy
from spacy.language import Language
from spacy.tokenizer import Tokenizer
from spacy.tokens import Doc, Span, Token
from spacy.util import compile_infix_regex, compile_prefix_regex, compile_suffix_regex

from .constants import (
    ABBREVIATIONS,
    DASHES,
    PUNCTUATIONS,
    SENTENCE_OPENERS,
    SPACY_MODEL,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import DatasetNotFoundError, SourceTypeError

# End of a sentence: terminal marks, optionally closing quotes or brackets,
# before whitespace or the end of the text; or a blank line
SENTENCE_END = re.compile(
    r"(?P<marks>[.!?…]+)(?P<closers>[»”’\"')\]]*)(?=\s|$)|(?P<break>\n[ \t\r\f\v]*\n)"
)
NON_SPACE = re.compile(r"\S")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
# Marker of a numbered or lettered list (1. 2.1. b. IV.) that opens a sentence
# or a line, at the end of the examined window
LIST_MARKER = re.compile(r"(?:^|\n)[ \t]*(?:\d+(?:\.\d+)*|[a-z]|[IVXLC]+)\.\Z")
OPENING_CHARS = "(«“\"'["
# Characters looked back from a period for an abbreviation: enough for the two
# tokens that are checked, so that the scan stays linear in the text length.
# A token cut by the window is at least 61 characters long and matches
# neither an abbreviation nor an initial
LOOKBACK = 64


def is_punctuation(token: str) -> bool:
    """
    Checking whether a token consists only of punctuation marks and symbols

    Description:
        Marks are the characters of PUNCTUATIONS and the Unicode characters
        of the categories P (punctuation) and S (symbols), so multi-character
        tokens like "?!", "!..", "--", "…", "«", "€" are filtered as well

    Arguments:
        token (str): Token

    Returns:
        bool: Result of the check
    """
    return all(char in PUNCTUATIONS or unicodedata.category(char)[0] in "PS" for char in token)


def _opens_remark(text: str, position: int) -> bool:
    """
    Whether the dash before the position opens the remark of the narrator

    Description:
        In a dialogue the narrator's remark follows the dash in lower case
        and belongs to the sentence of the line ("-Si -dijo el"), while
        a new line of dialogue opens with an upper-case word

    Arguments:
        text (str): Text string
        position (int): Position right after the dash

    Returns:
        bool: Result of the check
    """
    following = NON_SPACE.search(text, position)
    return following is not None and following.group().islower()


def _ends_sentence(text: str, start: int, match: re.Match[str]) -> bool:
    """
    Checking whether the terminal marks found in a text end a sentence

    Description:
        The next non-space character must open a sentence: an upper-case
        letter, a digit or one of SENTENCE_OPENERS; a lower-case continuation
        after an ellipsis or an exclamation mark keeps the sentence going.
        A dash followed by a lower-case word opens the remark of the narrator
        of a dialogue rather than a sentence ("-¿Vienes? -preguntó ella").
        A single period does not end a sentence after an abbreviation from
        ABBREVIATIONS, after a capital initial or after a list marker that
        opens the sentence or a line. Opening quotes and brackets are
        stripped from the tokens before the check, so "(EE. UU. Es grande)"
        stays together. Only the last LOOKBACK characters before the period
        are examined

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
        mark, an opening quote or bracket or a dash; a blank line ends
        a sentence too. A dash followed by a lower-case word opens the remark
        of the narrator of a dialogue and keeps the sentence going.
        Abbreviations (Sr., Dra., p. ej., EE. UU., a. m.),
        capital initials and list markers at the start of a sentence or
        a line (1. 2.1. IV.) do not end a sentence. A single line break
        does not split a sentence, so hard-wrapped texts are handled.
        The text is scanned once, the sentences are yielded as they are
        found, stripped of surrounding whitespace

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
        The sentences of sentenize, by the same rules, with the positions of
        their stripped text in the string

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
        The tokenizer of a blank "es" pipeline does not need a trained
        model; it is created once per process, with the rules of
        add_dash_rules for the dashes of a dialogue

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
        spaCy splits a long dash off only at the start and at the end of
        a token and a hyphen not at all, so the dashes of a dialogue glued
        to the words stay inside them: --No, -dijo, reírse—me decía and
        dijo:—¡Mis are single tokens, and the words are not words. The rules
        of TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES and TOKENIZER_INFIXES split
        them off and leave a hyphen between letters (franco-alemán) or before
        a digit (-5) alone. The blank pipeline of get_tokenizer and the models
        of get_nlp get them; a pipeline of one's own gets them from this
        function, so that its words are the words of the rest of the library.
        A tokenizer that is not the Tokenizer of spaCy is left as it is

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
    defaults = nlp.Defaults
    tokenizer = nlp.tokenizer
    if not isinstance(tokenizer, Tokenizer):
        return
    tokenizer.prefix_search = compile_prefix_regex(
        (*(defaults.prefixes or ()), *TOKENIZER_PREFIXES)
    ).search
    tokenizer.suffix_search = compile_suffix_regex(
        (*(defaults.suffixes or ()), *TOKENIZER_SUFFIXES)
    ).search
    tokenizer.infix_finditer = compile_infix_regex(
        (*(defaults.infixes or ()), *TOKENIZER_INFIXES)
    ).finditer


def tokenize(text: str) -> Iterator[str]:
    """
    Splitting a text into tokens with the spaCy Spanish tokenizer

    Description:
        Whitespace tokens are dropped; punctuation marks, including "¿"
        and "¡", numbers like "1.500,50", "3.º", "1990-1995" and
        abbreviations like "Sr.", "EE. UU." are single tokens; words
        with enclitic pronouns (dámelo) are not split; the dashes of a
        dialogue glued to the words (--No, -dijo, reírse—me) are split off
        by the rules of add_dash_rules

    Arguments:
        text (str): Text string

    Returns:
        iterator[str]: Iterator of tokens
    """
    return (token.text for token in get_tokenizer()(text) if not token.is_space)


@lru_cache(maxsize=131072)
def lemmatize(word: str) -> str:
    """
    Lemmatizing a word form with simplemma, with caching

    Description:
        simplemma works from a dictionary without a trained model: a known
        form is mapped to its lower-case lemma (Tienes - tener, NIÑOS -
        niño), an unknown form is returned unchanged (Madrid, dámelo).
        Verbs with enclitic pronouns are handled when the form is in the
        dictionary (cantándole - cantar). The results are cached by form:
        a text has far fewer distinct forms than tokens

    Arguments:
        word (str): Word form

    Returns:
        str: Lemma
    """
    return simplemma.lemmatize(word, lang="es")


def iter_doc_tokens(source: Doc | Span) -> Iterator[Token]:
    """
    Extracting the tokens of the words from a Doc or Span object

    Description:
        Whitespace tokens are skipped, punctuation marks and symbols are
        dropped by the same is_punctuation check as for a string (%, €, §
        and other symbols of the category S are not words, although spaCy
        does not treat them as punctuation). The Spanish tokenizer keeps
        hyphenated words (teórico-práctico) and abbreviations (EE. UU.)
        as single tokens, so a word is always one token

    Arguments:
        source (Doc|Span): Doc or Span object

    Returns:
        generator[Token]: Token of each word
    """
    for token in source:
        if not token.is_space and not is_punctuation(token.text):
            yield token


def iter_doc_words(source: Doc | Span) -> Iterator[tuple[int, int, str]]:
    """
    Extracting words with positions from a Doc or Span object

    Description:
        The words of iter_doc_tokens with the positions of their tokens

    Arguments:
        source (Doc|Span): Doc or Span object

    Returns:
        generator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each word
    """
    for token in iter_doc_tokens(source):
        yield token.idx, token.idx + len(token), token.text


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Extracting words with positions from a string

    Description:
        The string is split by the tokenizer of the blank Spanish pipeline
        (get_tokenizer), and punctuation marks and symbols are dropped, as in
        WordsExtractor

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
        The statistics on Universal Dependencies need a trained model.
        The default one is es_core_news_sm; a pipeline loaded by the caller
        can be passed to those statistics instead. The tokenizer of a loaded
        model gets the rules of add_dash_rules, so that its words are the
        words of get_tokenizer. The default is resolved before the cache, so
        that get_nlp() and get_nlp(SPACY_MODEL) are the same pipeline and not
        two copies of it

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


def has_words(source: str | Doc | Span) -> bool:
    """
    Checking whether a text holds a word

    Description:
        A text of punctuation alone (¿?, ..., a line of dots between two
        paragraphs) and an empty one hold no word: the statistics have nothing
        to count in them, the formulas of readability would divide by them, and
        a component of a pipeline meets them in any corpus

    Arguments:
        source (str|Doc|Span): Text, Doc or Span object

    Returns:
        bool: Result of the check

    Example:
        >>> from ests.utils import has_words
        >>> has_words("El gato duerme"), has_words("¿?"), has_words("")
        (True, False, False)
    """
    text = source if isinstance(source, str) else source.text
    return any(not char.isspace() and not is_punctuation(char) for char in text)


def check_sequence(value: object, what: str = "words") -> None:
    """
    Checking that an argument is a sequence of strings and not a text

    Description:
        A string satisfies Sequence[str] formally but is iterated character by
        character, and a Doc or a Span of spaCy is iterated token by token,
        where every token compares only with itself, so every one of them would
        be a word of its own with a frequency of one; the functions that expect
        a list of words or of texts refuse both explicitly

    Arguments:
        value (object): Value to check
        what (str): What is expected, for the message of the error

    Raises:
        SourceTypeError: If a string, a Doc or a Span is passed

    Example:
        >>> from ests.utils import check_sequence
        >>> check_sequence(["el", "gato"])
        >>> check_sequence("el gato")
        Traceback (most recent call last):
        ...
        ests.exceptions.SourceTypeError: A list of words is expected, not a string
    """
    if isinstance(value, str):
        raise SourceTypeError(f"A list of {what} is expected, not a string")
    if isinstance(value, Doc | Span):
        raise SourceTypeError(
            f"A list of {what} is expected, not a {type(value).__name__}: "
            "extract the words with WordsExtractor"
        )


def is_verbal_noun(lemma: str) -> bool:
    """
    Checking whether a lemma is a noun derived from a verb, by its suffix

    Description:
        The suffixes of VERBAL_NOUN_SUFFIXES - -ción, -sión, -miento, -anza,
        -encia, -ancia, -aje, -dura, -azgo (revisión, nombramiento, aprendizaje)
        - or a lemma of VERBAL_NOUN_LEMMAS, the nouns whose derivation leaves no
        suffix behind (uso, pago, comienzo, envío). The rule catches nouns of
        other origins with the same endings (ciencia, distancia), as any suffix
        rule does

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


def count_letters(word: str) -> int:
    """
    Counting the letters of a string

    Description:
        Letters of any alphabet (str.isalpha), without digits, hyphens
        and marks; the ordinal indicators º and ª are letters for
        str.isalpha, so 3.º is a one-letter word

    Arguments:
        word (str): Word form

    Returns:
        int: Number of letters
    """
    return sum(map(str.isalpha, word))


def safe_divide(num: float | int, den: float | int, default: float | int = 0) -> float:
    """
    Dividing two numbers safely

    Arguments:
        num (float|int): Numerator
        den (float|int): Denominator
        default (float|int): Value returned for a zero denominator

    Returns:
        float: Result of the division
    """
    if not den:
        return default
    return num / den
