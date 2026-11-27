import csv
import re
from collections.abc import Iterator
from functools import cache
from itertools import islice
from numbers import Real
from pathlib import Path
from typing import Any, NamedTuple

from anyts.datasets import Dataset, check_limit, fetch_archive, other_versions, to_path
from anyts.utils import check_word

from ..constants import DEFAULT_DATA_DIR, USER_AGENT
from ..exceptions import DatasetNotFoundError, ParameterError, SourceTypeError
from ..utils import _verb_lemmas, lemmatize

NAME = "freq_dict"
VERSION = 3
META = {
    "url": "https://storage.googleapis.com/books/ngrams/books/datasetsv3.html",
    "description": "Frequency dictionary of Spanish lemmas by Google Books Ngram",
    "author": "Shkarin S.S.",
    "license": "CC BY 3.0",
    "citation": (
        "Google Books Ngram Viewer, version 20200217, Spanish 1-grams "
        "(Michel J.-B. et al. Quantitative analysis of culture using millions "
        "of digitized books. Science 331 (6014), 2011)"
    ),
}
ARCHIVE = f"{NAME}_v{VERSION}.tar.xz"
DOWNLOAD_URL = f"https://github.com/SergeyShk/esTS/raw/master/ests/datasets/data/{ARCHIVE}"
ARCHIVE_SHA256 = "0756e3b8fdcb6726abf0378ddbaec05b8f22a2688ac30a96c29cc41b188851cb"
FILENAME = "freq_dict.tsv"
CORPUS_SIZE = 63_090_618_290
POS_TAGS = ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "CONJ")
# Forms the dictionary and CORPUS_SIZE count: no numbers, no forms with a hyphen or a dot
WORD_PATTERN = re.compile(r"[a-záéíóúüñ]+")
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("dicts")


class Entry(NamedTuple):
    """
    Entry of the frequency dictionary

    Attributes:
        lemma (str): Lemma in lower case
        pos (tuple[str, ...]): Parts of speech of the lemma (NOUN, PROPN, VERB, ADJ, ADV...)
        ipm (float): Occurrences per million words, summed over the parts of speech
        range (int): Number of years out of 40 (1980-2019) in which the lemma occurs
        dispersion (int): Juilland's D over the years, from 0 to 100
        docs (int): Number of books with the most widespread form of the lemma
    """

    lemma: str
    pos: tuple[str, ...]
    ipm: float
    range: int
    dispersion: int
    docs: int


def lemma_key(word: str, proper: bool = False, pos: str = "") -> str:
    """
    Key of a word in the frequency dictionary

    Description:
        The word goes to lower case and then to its lemma by lemmatize with the
        part of speech, so a capitalized word at the start of a sentence finds
        its lemma; a proper noun keeps its form in lower case. A verb and an
        auxiliary take the first analysis of either (fue - ser), as Google
        Books tags both as verbs. The dictionary is built with this function and
        the parts of speech of Google Books

    Arguments:
        word (str): Word form in any case
        proper (bool): The word is a proper noun
        pos (str): Part of speech of UD; without it the first analysis of esMorph

    Returns:
        str: Key of the dictionary

    Raises:
        SourceTypeError: If the word is not a string

    Example:
        >>> from ests.datasets.freq_dict import lemma_key
        >>> lemma_key("Miró"), lemma_key("computadoras"), lemma_key("fue")
        ('mirar', 'computadora', 'ser')
        >>> lemma_key("vino"), lemma_key("vino", pos="VERB")
        ('vino', 'venir')
        >>> lemma_key("Tomás"), lemma_key("Tomás", proper=True)
        ('tomar', 'tomás')
    """
    check_word(word)
    form = word.lower()
    if proper:
        return form
    if pos in ("VERB", "AUX") and (verbs := _verb_lemmas(form)):
        return verbs[0].lower()
    return lemmatize(form, pos).lower()


class FreqDict(Dataset):
    """
    Frequency dictionary of Spanish lemmas by Google Books Ngram

    Description:
        86,091 lemmas (106,909 rows of a lemma and a part of speech) of the
        Spanish books of Google Books Ngram of 1980-2019, 63 billion words, with
        the frequency per million words, the range (the number of years out of
        40 in which the lemma occurs), Juilland's D over the years and the
        number of books. The forms are lower-cased and lemmatized by esMorph
        with their part of speech, so a word is looked up by its lemma_key; a
        noun form written
        with a capital letter in 90% of its occurrences is a proper noun
        (PROPN), as Google tags none. The rows below 0.1 ipm or found in fewer
        than 5 years are left out. The dictionary is derived from Google Books
        Ngram under CC BY 3.0 and is distributed under the same licence
        For a lookup the parts of speech of a lemma are merged: the frequencies
        are summed, the range, the dispersion and the number of books are the
        greatest ones

    References:
        https://storage.googleapis.com/books/ngrams/books/datasetsv3.html
        https://doi.org/10.1126/science.1199644

    Example:
    Downloading and the information about the dictionary:
        >>> from ests.datasets import FreqDict
        >>> fd = FreqDict()
        >>> fd.download()  # doctest: +SKIP
        >>> fd.info["license"]
        'CC BY 3.0'

    Looking up a lemma:
        >>> fd.lookup("gato")
        Entry(lemma='gato', pos=('NOUN', 'ADJ'), ipm=25.37, range=40, dispersion=95, docs=232841)
        >>> fd.ipm("perro"), fd.ipm("computadora"), fd.ipm("computador")
        (58.41, 15.35, 4.72)

    Iterating over the dictionary:
        >>> for record in fd.get_records(pos="NOUN", limit=2):
        ...     print(record)
        {'lemma': 'año', 'pos': 'NOUN', 'ipm': 1639.31, 'range': 40, 'dispersion': 98, 'docs': 837102}
        {'lemma': 'parte', 'pos': 'NOUN', 'ipm': 1295.88, 'range': 40, 'dispersion': 99, 'docs': 852898}

    Arguments:
        data_dir (str|Path): Directory of the dictionary

    Attributes:
        entries (dict[str, Entry]): Entries by lemma, the parts of speech merged
        min_ipm (float): Minimum frequency in the dictionary
        word_ipm (dict[str, float]): Frequencies by the key a word form reaches
            without a part of speech - the reference of keyness

    Methods:
        check_data: Checking that the file of the dictionary is in place
        download: Downloading the dictionary from the network
        lookup: Getting the entry of a lemma
        ipm: Getting the frequency of a lemma
        get_texts: Getting the lemmas of the dictionary
        get_records: Getting the records of the dictionary

    Raises:
        SourceTypeError: If the directory of the data is not a string or a Path
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self._archive = self.data_dir.joinpath(ARCHIVE)
        self._filepath = self.data_dir.joinpath(f"{NAME}_v{VERSION}", FILENAME)
        self._checked = False

    @property
    def filepath(self) -> str | None:
        """
        Path to the file of the dictionary
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    def check_data(self) -> bool:
        """
        Checking that the file of the dictionary is in place

        Description:
            A dictionary of another version in the directory is not read: the
            message names it and asks to download the version of the library

        Returns:
            bool: Result of the check

        Raises:
            DatasetNotFoundError: If the dictionary is not found
        """
        if not self._filepath.is_file():
            other = other_versions(self.data_dir, NAME, VERSION, FILENAME)
            found = (
                f"The directory has {', '.join(other)}, but this version of esTS reads "
                f"{NAME}_v{VERSION}\n"
                if other
                else ""
            )
            msg = (
                f"The dataset {NAME} is not found\n{found}"
                f"Download it with the command ests download {NAME} or in Python:\n"
                ">>> fd = FreqDict()\n"
                ">>> fd.download()"
            )
            raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Downloading the dictionary from the network and extracting the file

        Description:
            The archive is verified against its SHA-256 checksum and downloaded
            again once if it fails; a missing file is extracted again from the
            archive

        Arguments:
            force (bool): Download the dictionary even if it is already downloaded

        Raises:
            DownloadError: If the archive cannot be downloaded or fails the checksum
        """
        missing = not self._filepath.is_file()
        fetch_archive(DOWNLOAD_URL, self._archive, ARCHIVE_SHA256, missing, force, USER_AGENT)
        self.check_data()
        load_entries.cache_clear()
        load_min_ipm.cache_clear()
        load_word_ipm.cache_clear()

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterating over the dictionary

        Description:
            A row for every lemma and part of speech, by frequency

        Returns:
            iterator[dict[str, object]]: Records of the dictionary
        """
        self.check_data()
        with self._filepath.open(encoding="utf-8", newline="") as file:
            reader = csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
            next(reader)
            for lemma, pos, ipm, range_, dispersion, docs in reader:
                yield {
                    "lemma": lemma,
                    "pos": pos,
                    "ipm": float(ipm),
                    "range": int(range_),
                    "dispersion": int(dispersion),
                    "docs": int(docs),
                }

    def get_records(
        self,
        pos: str | None = None,
        min_ipm: float | None = None,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Getting the records of the dictionary

        Arguments:
            pos (str): Part of speech from POS_TAGS (NOUN, PROPN, VERB, ADJ, ADV and others)
            min_ipm (float): Minimum frequency
            limit (int): Number of records

        Returns:
            iterator[dict[str, object]]: Records of the dictionary

        Raises:
            ParameterError: If the part of speech is unknown or the minimum frequency is
                not a number
            ParameterError: If the number of records is not an integer or is negative
        """
        if pos is not None and not isinstance(pos, str):
            raise ParameterError(f"The part of speech must be a string, not {type(pos).__name__}")
        threshold: object = min_ipm
        if threshold is not None and (
            isinstance(threshold, bool) or not isinstance(threshold, Real)
        ):
            raise ParameterError(
                f"The minimum frequency must be a number, not {type(min_ipm).__name__}"
            )
        if pos is not None and pos not in POS_TAGS:
            raise ParameterError(f"Unknown part of speech {pos}, expected one of {POS_TAGS}")
        check_limit(limit)
        records = (
            record
            for record in self
            if (pos is None or record["pos"] == pos)
            and (min_ipm is None or record["ipm"] >= min_ipm)
        )
        yield from islice(records, limit)

    def get_texts(
        self,
        pos: str | None = None,
        min_ipm: float | None = None,
        limit: int | None = None,
    ) -> Iterator[str]:
        """
        Getting the lemmas of the dictionary

        Arguments:
            pos (str): Part of speech from POS_TAGS (NOUN, PROPN, VERB, ADJ, ADV and others)
            min_ipm (float): Minimum frequency
            limit (int): Number of lemmas

        Returns:
            iterator[str]: Lemmas
        """
        for record in self.get_records(pos, min_ipm, limit):
            yield record["lemma"]

    @property
    def entries(self) -> dict[str, Entry]:
        """
        Entries of the dictionary by lemma, the parts of speech of a lemma merged
        """
        self._ensure_data()
        return load_entries(self._filepath)

    @property
    def word_ipm(self) -> dict[str, float]:
        """
        Frequencies of the dictionary by the key a word form reaches without a part of speech
        """
        self._ensure_data()
        return load_word_ipm(self._filepath)

    @property
    def min_ipm(self) -> float:
        """
        Minimum frequency of an entry of the dictionary
        """
        self._ensure_data()
        return load_min_ipm(self._filepath)

    def _ensure_data(self) -> None:
        """
        Checking once that the file of the dictionary is in place
        """
        if not self._checked:
            self.check_data()
            self._checked = True

    def lookup(self, lemma: str) -> Entry | None:
        """
        Getting the entry of a lemma

        Description:
            The lemma is the key lemma_key gives, not a word form: a word of a
            text is looked up by lookup(lemma_key(word)); the same holds for ipm
            and in

        Arguments:
            lemma (str): Lemma in any case

        Returns:
            Entry|None: Entry of the dictionary, None if the lemma is not in it

        Raises:
            SourceTypeError: If the lemma is not a string

        Example:
            >>> from ests.datasets import FreqDict
            >>> from ests.datasets.freq_dict import lemma_key
            >>> fd = FreqDict()
            >>> fd.lookup("usted"), fd.ipm(lemma_key("usted"))
            (None, 1463.67)
        """
        if not isinstance(lemma, str):
            raise SourceTypeError(f"The lemma must be a string, not {type(lemma).__name__}")
        return self.entries.get(lemma.lower())

    def ipm(self, lemma: str) -> float:
        """
        Getting the frequency of a lemma

        Arguments:
            lemma (str): Lemma in any case, the key lemma_key gives

        Returns:
            float: Occurrences per million words, 0 if the lemma is not in the dictionary

        Raises:
            SourceTypeError: If the lemma is not a string
        """
        entry = self.lookup(lemma)
        return entry.ipm if entry else 0.0

    def __len__(self) -> int:
        """
        Number of the lemmas of the dictionary

        Description:
            The lemmas with their parts of speech merged, fewer than the rows of
            the iteration
        """
        return len(self.entries)

    def __contains__(self, lemma: object) -> bool:
        return isinstance(lemma, str) and lemma.lower() in self.entries


@cache
def load_entries(filepath: Path) -> dict[str, Entry]:
    """
    Parsing the file of the dictionary into entries by lemma

    Description:
        The rows of the parts of speech of a lemma are merged: the frequencies
        are summed, the range, the dispersion and the number of books are the
        greatest ones

    Arguments:
        filepath (Path): Path to the file of the dictionary

    Returns:
        dict[str, Entry]: Entries by lemma
    """
    entries: dict[str, Entry] = {}
    with filepath.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(reader)
        for lemma, pos, ipm, range_, dispersion, docs in reader:
            entry = entries.get(lemma)
            if entry is None:
                entries[lemma] = Entry(
                    lemma, (pos,), float(ipm), int(range_), int(dispersion), int(docs)
                )
            else:
                entries[lemma] = Entry(
                    lemma,
                    (*entry.pos, pos),
                    round(entry.ipm + float(ipm), 2),
                    max(entry.range, int(range_)),
                    max(entry.dispersion, int(dispersion)),
                    max(entry.docs, int(docs)),
                )
    return entries


@cache
def load_min_ipm(filepath: Path) -> float:
    """
    Minimum frequency of an entry of the dictionary

    Description:
        The frequency of the words out of the dictionary in the surprisal and
        in keyness

    Arguments:
        filepath (Path): Path to the file of the dictionary

    Returns:
        float: Minimum frequency
    """
    return min(entry.ipm for entry in load_entries(filepath).values())


@cache
def load_word_ipm(filepath: Path) -> dict[str, float]:
    """
    Frequencies of the dictionary by the key that a word form reaches without a part of speech

    Description:
        The rows of the proper nouns go to lemma_key of their forms (Roma -
        romo), as a word of a text without annotation does, and every key is
        summed over the parts of speech

    Arguments:
        filepath (Path): Path to the file of the dictionary

    Returns:
        dict[str, float]: Occurrences per million words by key
    """
    ipm: dict[str, float] = {}
    with filepath.open(encoding="utf-8", newline="") as file:
        reader = csv.reader(file, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(reader)
        for lemma, pos, value, *_ in reader:
            key = lemma_key(lemma) if pos == "PROPN" else lemma
            ipm[key] = ipm.get(key, 0.0) + float(value)
    return ipm
