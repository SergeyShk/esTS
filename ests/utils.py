import hashlib
import logging
import os
import re
import shutil
import tarfile
import urllib.parse
import urllib.request
import zipfile
from collections.abc import Iterable, Iterator, Sequence
from functools import lru_cache
from pathlib import Path, PurePosixPath

import simplemma
import spacy
from anyts.utils import (
    check_sequence as check_sequence,
    check_words,
    count_letters as count_letters,
    has_words as has_words,
    is_punctuation as is_punctuation,
    iter_doc_tokens as iter_doc_tokens,
    iter_doc_words as iter_doc_words,
    safe_divide as safe_divide,
)
from spacy.language import Language
from spacy.tokenizer import Tokenizer

from .constants import (
    ABBREVIATIONS,
    DASHES,
    DEFAULT_DATA_DIR,
    SENTENCE_OPENERS,
    SPACY_MODEL,
    TOKENIZER_INFIXES,
    TOKENIZER_PREFIXES,
    TOKENIZER_SUFFIXES,
    VERBAL_NOUN_LEMMAS,
    VERBAL_NOUN_SUFFIXES,
)
from .exceptions import DataFileError, DatasetNotFoundError, DownloadError, SourceTypeError

logger = logging.getLogger(__name__)

# End of a sentence: terminal marks, optionally closing quotes or brackets,
# before whitespace or the end of the text; or a blank line
SENTENCE_END = re.compile(
    r"(?P<marks>[.!?…]+)(?P<closers>[»”’\"')\]]*)(?=\s|$)|(?P<break>\n[ \t\r\f\v]*\n)"
)
NON_SPACE = re.compile(r"\S")
INITIAL = re.compile(r"[A-ZÁÉÍÓÚÜÑ]\.")
# Marker of a list (1. 2.1. b. IV.) that opens a sentence or a line, at the end of the window
LIST_MARKER = re.compile(r"(?:^|\n)[ \t]*(?:\d+(?:\.\d+)*|[a-z]|[IVXLC]+)\.\Z")
OPENING_CHARS = "(«“\"'["
# Characters looked back from a period for an abbreviation or an initial
LOOKBACK = 64


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
    following = NON_SPACE.search(text, position)
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
        mark, an opening quote or bracket or a dash; a blank line ends one
        too. A dash before a lower-case word opens a remark of the narrator
        and keeps the sentence going. A single period after an abbreviation
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
        a digit (-5) alone; get_tokenizer and get_nlp have them already.
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
    prefixes = _extend_rules(tokenizer.prefix_search, [f"^{rule}" for rule in TOKENIZER_PREFIXES])
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
        a dialogue are split off by add_dash_rules

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
        A known form is mapped to its lower-case lemma (Tienes - tener,
        cantándole - cantar), an unknown form is returned unchanged (Madrid,
        dámelo)

    Arguments:
        word (str): Word form

    Returns:
        str: Lemma
    """
    return simplemma.lemmatize(word, lang="es")


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


def to_path(path: str | Path) -> Path:
    """
    Converting the string form of a path into a Path

    Arguments:
        path (str|Path): Path as a string or a Path

    Returns:
        Path: Path object

    Raises:
        SourceTypeError: If the value is neither a string nor a Path
    """
    if isinstance(path, str):
        return Path(path)
    if isinstance(path, Path):
        return path
    raise SourceTypeError("The path must be a string or a Path")


# Seconds a download waits for the server to answer
DOWNLOAD_TIMEOUT = 60

# Whether tarfile has the data filter (Python 3.11.4+)
TAR_DATA_FILTER = hasattr(tarfile, "data_filter")


def download_file(
    url: str,
    filename: str | None = None,
    dirpath: str | Path = DEFAULT_DATA_DIR,
    force: bool = False,
) -> str:
    """
    Downloading a file from the network

    Description:
        A broken download leaves no partial file; the server is waited for
        DOWNLOAD_TIMEOUT seconds at most

    Arguments:
        url (str): Address of the file
        filename (str): Name of the downloaded file; the last part of the address by default
        dirpath (str|Path): Directory for the downloaded file
        force (bool): Download the file even if it is already there

    Returns:
        str: Path to the downloaded file; an empty string if it was already there

    Raises:
        DownloadError: If the directory cannot be created or the file cannot be downloaded
    """
    dirpath = to_path(dirpath)
    try:
        dirpath.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise DownloadError(f"Cannot create the directory {dirpath}") from e
    if not filename:
        filename = Path(urllib.parse.urlparse(urllib.parse.unquote_plus(url)).path).name
    filepath = dirpath.resolve() / filename
    if filepath.is_file() and not force:
        logger.info("The file %s is already downloaded", filepath)
        return ""
    partial = filepath.with_name(filepath.name + ".part")
    try:
        logger.info("Downloading the file %s", url)
        request = urllib.request.Request(url, headers={"User-Agent": "esTS"})
        with (
            urllib.request.urlopen(request, timeout=DOWNLOAD_TIMEOUT) as response,
            partial.open("wb") as out_file,
        ):
            shutil.copyfileobj(response, out_file)
        partial.replace(filepath)
    except Exception as e:
        partial.unlink(missing_ok=True)
        raise DownloadError(f"Cannot download the file {url}") from e
    logger.info("The file is downloaded: %s", filepath)
    return str(filepath)


def _is_outside(member: str) -> bool:
    """Whether the path of an archive member leads outside the directory of extraction"""
    parts = PurePosixPath(member.replace("\\", "/")).parts
    return bool(parts) and (parts[0] in ("/", "..") or ".." in parts)


def extract_archive(archive_file: str | Path, extract_dir: str | Path | None = None) -> str:
    """
    Extracting the files of a ZIP or TAR archive

    Description:
        Paths and links leading outside the directory are refused. A root
        directory that differs from the name of the archive without its
        extensions is renamed to it, replacing an earlier extraction

    Arguments:
        archive_file (str|Path): Path to the archive
        extract_dir (str|Path): Directory for the extracted files; the directory of the archive by default

    Returns:
        str: Path to the directory with the extracted files

    Raises:
        DataFileError: If the file is not a ZIP or TAR archive, the archive is
            corrupted, empty, has paths outside the directory or links, or the
            directory cannot be created
    """
    archive_path = to_path(archive_file).resolve()
    extract_path = to_path(extract_dir) if extract_dir else archive_path.parent
    try:
        extract_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise DataFileError(f"Cannot create the directory {extract_path}") from e
    is_zip = zipfile.is_zipfile(archive_path)
    is_tar = tarfile.is_tarfile(archive_path)
    if not is_zip and not is_tar:
        raise DataFileError(f"The file {archive_path} is not a ZIP or TAR archive")
    logger.info("Extracting the archive %s", archive_path)
    try:
        if is_zip:
            with zipfile.ZipFile(archive_path, mode="r") as zip_file:
                members = zip_file.namelist()
                if any(_is_outside(member) for member in members):
                    raise DataFileError(
                        f"The archive {archive_path} has paths outside the directory"
                    )
                zip_file.extractall(extract_path)
        else:
            with tarfile.open(archive_path, mode="r") as tar_file:
                if TAR_DATA_FILTER:
                    tar_file.extractall(extract_path, filter="data")
                else:
                    for member in tar_file:
                        if _is_outside(member.name) or not (member.isfile() or member.isdir()):
                            raise DataFileError(
                                f"The archive {archive_path} has paths outside the directory "
                                "or links"
                            )
                        tar_file.extract(member, extract_path)
                # After the extraction, so that the stream is read once
                members = tar_file.getnames()
    except (OSError, zipfile.BadZipFile, tarfile.TarError) as e:
        raise DataFileError(f"Cannot extract the archive {archive_path}") from e
    if not members:
        raise DataFileError(f"The archive {archive_path} has no files")
    src_basename = os.path.commonpath(members)
    if src_basename and not (extract_path / src_basename).is_dir():
        src_basename = str(Path(src_basename).parent)
    if not src_basename or src_basename == ".":
        return str(extract_path)
    # spanish_literature_v1.tar.xz -> spanish_literature_v1
    dest_basename = archive_path.name
    while (stem := Path(dest_basename).stem) != dest_basename:
        dest_basename = stem
    if src_basename != dest_basename:
        destination = extract_path / dest_basename
        if destination.is_dir():
            shutil.rmtree(destination)
        return str(shutil.move(extract_path / src_basename, destination))
    return str(extract_path / src_basename)


def sha256(path: Path) -> str:
    """
    Computing the SHA-256 checksum of a file

    Arguments:
        path (Path): Path to the file

    Returns:
        str: Hexadecimal checksum; an empty string for a missing file
    """
    if not path.is_file():
        return ""
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()
