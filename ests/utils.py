from __future__ import annotations

from collections.abc import Iterable, Iterator
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import esmorph
from anyseg import Segmenter
from anyts.constants import MESSAGES
from anyts.document import to_document
from anyts.utils import (
    count_words_by_spans as count_words_by_spans,
    find_phrases as find_phrases,
    is_language,
    is_punctuation,
)

from .constants import SPACY_MODEL, VERBAL_NOUN_LEMMAS, VERBAL_NOUN_SUFFIXES
from .exceptions import DatasetNotFoundError, SourceError, SourceTypeError

if TYPE_CHECKING:
    from anyseg import Document
    from spacy.language import Language
    from spacy.tokens import Doc

# The segmenter of Spanish into tokens and sentences
SEGMENTER = Segmenter("es")
# Components of a model that the component esmorph replaces in load_pipeline
MORPH_COMPONENTS = ("morphologizer", "lemmatizer")


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


def get_document(source: str | Doc | Document) -> Document:
    """
    Getting the document of a data source in the model of anySeg

    Description:
        A string is segmented by anySeg (the tokens of iter_tokens, the sentences
        of iter_text_sents); a Doc keeps its tokens, columns and sentences, and a
        Doc without sentences gets those of iter_text_sents (to_document of the
        core); a Document is returned as it is

    Arguments:
        source (str|Doc|Document): Data source

    Returns:
        Document: Document of anySeg

    Raises:
        SourceTypeError: If the source is neither a string, a Doc nor a Document

    Example:
        >>> from ests.utils import get_document
        >>> document = get_document("Vino del pueblo. ¿Y tú?")
        >>> [token.text for token in document.tokens]
        ['Vino', 'del', 'pueblo', '.', '¿', 'Y', 'tú', '?']
        >>> [word.form for word in document.tokens[1].words]
        ['de', 'el']
    """
    if isinstance(source, str):
        return SEGMENTER.segment(source)
    return to_document(source, sentenize=iter_text_sents)


def _annotate_text(text: str) -> Document:
    """The document of a string (get_document) with the lemmas, the parts of speech and the
    features of esMorph in the context of its sentences"""
    document = SEGMENTER.segment(text)
    get_morph_analyzer().annotate(document)
    return document


def _parse_text(text: str, nlp: Language | None, disable: Iterable[str]) -> Document:
    """
    The document of a string parsed by a pipeline, nlp or get_nlp(), without the
    components of disable; a string longer than the max_length of the pipeline raises
    SourceError
    """
    pipeline = nlp or get_nlp()
    if len(text) > pipeline.max_length:
        raise SourceError(
            f"The text of {len(text)} characters is longer than the limit of the "
            f"pipeline ({pipeline.max_length}): split it into parts or raise "
            "max_length on a pipeline of your own and pass it in nlp"
        )
    return get_document(pipeline(text, disable=list(disable)))


def _check_text(text: object) -> None:
    """A text that is not a string"""
    if not isinstance(text, str):
        raise SourceTypeError(MESSAGES["text_type"].format(type=type(text).__name__))


def _check_nlp(nlp: object) -> None:
    """A pipeline that is not a spaCy Language (is_language)"""
    if nlp is not None and not is_language(nlp):
        raise SourceTypeError("The pipeline must be a spaCy Language")


@lru_cache(maxsize=1)
def get_morph_analyzer() -> esmorph.Analyzer:
    """
    Getting the morphological analyzer esMorph

    Returns:
        Analyzer: Morphological analyzer
    """
    return esmorph.Analyzer()


@lru_cache(maxsize=131072)
def lemmatize(word: str, pos: str = "") -> str:
    """
    Lemmatizing a word form with esMorph given its part of speech of Universal Dependencies

    Description:
        The lemma of the first analysis with the part of speech (vino: NOUN -
        vino, VERB - venir), and without the part of speech or such an analysis
        the lemma of the first analysis (Tienes - tener, cantándole - cantar,
        del - de); a word without analyses is its own lemma

    Arguments:
        word (str): Word form
        pos (str): Part of speech of UD

    Returns:
        str: Lemma

    Example:
        >>> from ests.utils import lemmatize
        >>> lemmatize("vino"), lemmatize("vino", "VERB")
        ('vino', 'venir')
    """
    analyses = get_morph_analyzer().analyze(word)
    if not analyses:
        return word
    return next((analysis for analysis in analyses if analysis.pos == pos), analyses[0]).lemma


@lru_cache(maxsize=131072)
def _verb_lemmas(word: str) -> tuple[str, ...]:
    """Lemmas of the analyses of a word form as a verb or an auxiliary (VERB, AUX) of esMorph,
    in their order: fue - ser, ir"""
    analyses = get_morph_analyzer().analyze(word)
    return tuple(dict.fromkeys(a.lemma for a in analyses if a.pos in ("VERB", "AUX")))


def load_pipeline(
    model: str = SPACY_MODEL, exclude: str | Iterable[str] = (), **kwargs: Any
) -> Language:
    """
    Loading the recommended spaCy pipeline

    Description:
        A spaCy model with the tokenizer anyseg.Tokenizer.v1 and the component
        anyseg_sentencizer first, so that the tokens and the sentences of a Doc are
        those of a string (iter_tokens, iter_text_sents), and the component esmorph
        of esMorph after it in place of the morphologizer and the lemmatizer of the
        model, so that the parts of speech, the features and the lemmas are those
        of a string too; the parser and the other components are the model's. A
        contraction (del, al) is one token with the analysis of its first word, its
        words are in token._.anyseg_words. A saved pipeline loads with spacy.load,
        as the factories of anySeg and esMorph are entry points

    Arguments:
        model (str): Name or path of a spaCy model: es_core_news_sm, es_core_news_md,
            es_core_news_lg
        exclude (str|list[str]): Components of the model not to load, e.g. ner
        **kwargs: The other parameters of spacy.load; the tokenizer of config is
            replaced by that of anySeg

    Returns:
        Language: Pipeline

    Raises:
        DatasetNotFoundError: If the model is not installed or there is no pipeline at the path

    Example:
        >>> from ests import load_pipeline
        >>> nlp = load_pipeline(exclude="ner")
        >>> nlp.pipe_names
        ['anyseg_sentencizer', 'esmorph', 'tok2vec', 'parser', 'attribute_ruler']
        >>> doc = nlp("--Dámelo --dijo el Sr. García.\\n\\nVino del pueblo")
        >>> [token.text for token in doc if not token.is_space]
        ['--', 'Dámelo', '--', 'dijo', 'el', 'Sr.', 'García', '.', 'Vino', 'del', 'pueblo']
        >>> [sent.text.strip() for sent in doc.sents]
        ['--Dámelo --dijo el Sr. García.', 'Vino del pueblo']
    """
    import spacy

    excluded = [exclude] if isinstance(exclude, str) else list(exclude)
    config = dict(kwargs.pop("config", {}))
    config["nlp"] = {**config.get("nlp", {}), "tokenizer": {"@tokenizers": "anyseg.Tokenizer.v1"}}
    try:
        nlp = spacy.load(model, exclude=[*excluded, *MORPH_COMPONENTS], config=config, **kwargs)
    except OSError as error:
        # A path names a saved pipeline, which no download gives
        if Path(model).exists() or any(sep in str(model) for sep in ("/", "\\")):
            raise DatasetNotFoundError(f"No spaCy pipeline at {model}: {error}") from error
        raise DatasetNotFoundError(
            f"The spaCy model {model} is not installed: python -m spacy download {model}"
        ) from error
    if "anyseg_sentencizer" not in nlp.component_names:
        nlp.add_pipe("anyseg_sentencizer", first=True)
    if "esmorph" not in nlp.component_names:
        nlp.add_pipe("esmorph", after="anyseg_sentencizer")
    return nlp


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
