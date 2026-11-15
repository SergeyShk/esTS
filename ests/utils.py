from __future__ import annotations

from collections.abc import Iterator
from functools import lru_cache
from typing import TYPE_CHECKING

import simplemma
from anyseg import Segmenter
from anyts.constants import MESSAGES
from anyts.utils import (
    add_tokenizer_rules,
    count_words_by_spans as count_words_by_spans,
    find_phrases as find_phrases,
    is_language,
    is_punctuation,
)

from .constants import (
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

# Byte order mark glued to the start of a text read with utf-8 instead of utf-8-sig
BYTE_ORDER_MARK = "\ufeff"
# Components of spaCy that set the sentences of a Doc
SENTENCE_SETTERS = ("parser", "senter", "sentencizer")
# The segmenter of Spanish into tokens and sentences
SEGMENTER = Segmenter("es")


def iter_tokens(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Tokenizing a string with the segmenter anySeg

    Description:
        Tokens follow the conventions of UD for Spanish (AnCora): the dashes of
        a dialogue glued to the words are tokens of their own (--No --dijo él),
        punctuation marks (¿, ¡), numbers (1.500,50, 3.º, 1990-1995) and
        abbreviations (Sr., p.ej.) are single tokens, as are contractions (del,
        al) and words with enclitic pronouns (dámelo); an abbreviation written
        with spaces is a token for each part (EE., UU.), and the period of one
        that ends a sentence is a token of its own. A byte order mark is no
        token, a lone surrogate is a token of its own

    Arguments:
        text (str): Text string

    Returns:
        iterator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each token

    Raises:
        SourceTypeError: If the text is not a string

    Example:
        >>> from ests.utils import iter_tokens
        >>> [token for *_, token in iter_tokens("--Dámelo --dijo el Sr. García.")]
        ['--', 'Dámelo', '--', 'dijo', 'el', 'Sr.', 'García', '.']
    """
    _check_text(text)
    return ((span.start, span.end, span.text) for span in SEGMENTER.tokenize(text))


def iter_text_words(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Extracting words with positions from a string

    Description:
        The tokens of iter_tokens without punctuation marks and symbols,
        as in WordsExtractor

    Arguments:
        text (str): Text string

    Returns:
        iterator[tuple[int, int, str]]: Position of the first character,
            position after the last character and text of each word

    Raises:
        SourceTypeError: If the text is not a string

    Example:
        >>> from ests.utils import iter_text_words
        >>> list(iter_text_words("¡Hola, mundo!"))
        [(1, 5, 'Hola'), (7, 12, 'mundo')]
    """
    return (token for token in iter_tokens(text) if not is_punctuation(token[2]))


def iter_text_sents(text: str) -> Iterator[tuple[int, int, str]]:
    """
    Splitting a string into sentences of the segmenter anySeg, with positions

    Description:
        A sentence ends with a period, an exclamation or question mark or an
        ellipsis before a word in upper case, a digit, an inverted mark, an opening
        quote or bracket or a dash of a dialogue; a dash before a word in lower case
        opens a remark of the narrator and keeps the sentence going. A period after
        an abbreviation (Sr., p. ej.) or an initial does not end a sentence, unless
        the abbreviation may close one (etc., p. m., EE. UU.) and a word in upper
        case follows. A blank line ends a sentence, as does a line without a final
        mark before a line in upper case, a dash or a list marker (a heading, an
        item of a list); a line break before a word in lower case does not.
        Sentences are stripped of the surrounding whitespace

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
        >>> [sent for *_, sent in iter_text_sents("--Sí --dijo él--. Vámonos.")]
        ['--Sí --dijo él--.', 'Vámonos.']
    """
    _check_text(text)
    return ((span.start, span.end, span.text) for span in SEGMENTER.sentenize(text))


def _check_text(text: object) -> None:
    """A text that is not a string"""
    if not isinstance(text, str):
        raise SourceTypeError(MESSAGES["text_type"].format(type=type(text).__name__))


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
        keeps one of their forms whole; get_nlp has the rules already. The
        add_tokenizer_rules of the core: a rule the tokenizer has is not added
        twice, and a tokenizer that is not the Tokenizer of spaCy, or whose rules
        are not regular expressions, is left as it is

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


@lru_cache(maxsize=131072)
def lemmatize(word: str) -> str:
    """
    Lemmatizing a word form with simplemma, with caching

    Description:
        A known form is mapped to its lower-case lemma (Tienes - tener,
        cantándole - cantar), an unknown form is returned unchanged (Madrid,
        dámelo), as is a word with a lone surrogate, which has no UTF-8 form

    Arguments:
        word (str): Word form

    Returns:
        str: Lemma
    """
    try:
        word.encode("utf-8")
    except UnicodeEncodeError:
        return word
    return simplemma.lemmatize(word, lang="es") if word != "" else word


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
