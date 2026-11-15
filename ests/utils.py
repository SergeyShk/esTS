from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import simplemma
from anyseg import Segmenter
from anyts.constants import MESSAGES
from anyts.utils import (
    count_words_by_spans as count_words_by_spans,
    find_phrases as find_phrases,
    is_language,
    is_punctuation,
)

from .constants import SPACY_MODEL, VERBAL_NOUN_LEMMAS, VERBAL_NOUN_SUFFIXES
from .exceptions import DatasetNotFoundError, SourceError, SourceTypeError

if TYPE_CHECKING:
    from spacy.language import Language

# The segmenter of Spanish into tokens and sentences
SEGMENTER = Segmenter("es")
ANYSEG_TOKENIZER = "anyseg.Tokenizer.v1"
# A name of an installed model, as opposed to a path
PACKAGE_NAME = re.compile(r"[\w.-]+")


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


def load_pipeline(
    model: str = SPACY_MODEL, exclude: str | Iterable[str] = (), **kwargs: Any
) -> Language:
    """
    Loading the recommended spaCy pipeline

    Description:
        A spaCy model with the tokenizer anyseg.Tokenizer.v1 and the component
        anyseg_sentencizer first, so that the tokens and the sentences of a Doc are
        those of a string (iter_tokens, iter_text_sents); the tags, the lemmas, the
        parser and the other components are the model's. A contraction (del, al) is
        one token, its words are in token._.anyseg_words. A tokenizer of anySeg
        that config or a saved pipeline has is kept with its lists of
        abbreviations and tokens, so a saved pipeline loads as it is

    Arguments:
        model (str): Name or path of a spaCy model: es_core_news_sm, es_core_news_md,
            es_core_news_lg
        exclude (str|list[str]): Components of the model not to load, e.g. ner
        **kwargs: The other parameters of spacy.load; another tokenizer of config
            is replaced by that of anySeg

    Returns:
        Language: Pipeline

    Raises:
        DatasetNotFoundError: If the model is not installed or the pipeline of a path
            cannot be loaded

    Example:
        >>> from ests import load_pipeline
        >>> nlp = load_pipeline(exclude="ner")
        >>> nlp.pipe_names
        ['anyseg_sentencizer', 'tok2vec', 'morphologizer', 'parser', 'attribute_ruler', 'lemmatizer']
        >>> doc = nlp("--Dámelo --dijo el Sr. García.\\n\\nVino del pueblo")
        >>> [token.text for token in doc if not token.is_space]
        ['--', 'Dámelo', '--', 'dijo', 'el', 'Sr.', 'García', '.', 'Vino', 'del', 'pueblo']
        >>> [sent.text.strip() for sent in doc.sents]
        ['--Dámelo --dijo el Sr. García.', 'Vino del pueblo']
    """
    import spacy

    excluded = [exclude] if isinstance(exclude, str) else list(exclude)
    config = dict(kwargs.pop("config", {}))
    nlp_config = dict(config.get("nlp", {}))
    nlp_config["tokenizer"] = _tokenizer_config(model, nlp_config.get("tokenizer"))
    config["nlp"] = nlp_config
    try:
        nlp = spacy.load(model, exclude=excluded, config=config, **kwargs)
    except OSError as error:
        if Path(model).exists() or not PACKAGE_NAME.fullmatch(str(model)):
            raise DatasetNotFoundError(
                f"The spaCy pipeline {model} cannot be loaded: {error}"
            ) from error
        raise DatasetNotFoundError(
            f"The spaCy model {model} is not installed: python -m spacy download {model}"
        ) from error
    if "anyseg_sentencizer" not in nlp.component_names:
        nlp.add_pipe("anyseg_sentencizer", first=True)
    return nlp


def _tokenizer_config(model: str, given: object) -> dict[str, Any]:
    """
    The [nlp.tokenizer] block of load_pipeline: the tokenizer of anySeg that config or
    the config.cfg of a saved or installed pipeline gives, with its lists, or a new one
    """
    if isinstance(given, dict) and given.get("@tokenizers") == ANYSEG_TOKENIZER:
        return given
    saved = _saved_config(model)
    if saved is not None and saved.is_file():
        import spacy

        nlp = spacy.util.load_config(saved).get("nlp", {})
        tokenizer = dict(nlp.get("tokenizer", {}))
        if tokenizer.get("@tokenizers") == ANYSEG_TOKENIZER:
            return tokenizer
    return {"@tokenizers": ANYSEG_TOKENIZER}


def _saved_config(model: str) -> Path | None:
    """The config.cfg of a pipeline: in its directory or in the data of its package"""
    import spacy

    if Path(model).is_dir():
        return Path(model) / "config.cfg"
    if not spacy.util.is_package(str(model)):
        return None
    package = spacy.util.get_package_path(str(model))
    meta = spacy.util.get_model_meta(package)
    return package / f"{meta['lang']}_{meta['name']}-{meta['version']}" / "config.cfg"


@lru_cache(maxsize=4)
def _load_nlp(model: str) -> Language:
    """The pipeline of load_pipeline, once per model"""
    return load_pipeline(model)


def get_nlp(model: str = SPACY_MODEL) -> Language:
    """
    Loading the pipeline of load_pipeline, once per process and model

    Arguments:
        model (str): Name or path of the model

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
