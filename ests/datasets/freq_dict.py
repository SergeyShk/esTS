import csv
from collections.abc import Iterator
from functools import cache
from itertools import islice
from pathlib import Path
from typing import Any, NamedTuple

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DatasetNotFoundError, ParameterError
from ..utils import lemmatize, to_path
from .dataset import Dataset, check_limit, fetch_archive

NAME = "freq_dict"
VERSION = 1
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
ARCHIVE_SHA256 = "f38c6a17b484f84eaa3d92fb06f6c8d571f1a2d720287368b8bc5c5cb7a5a9a7"
FILENAME = "freq_dict.tsv"
# Version of simplemma whose lemmas the dictionary is built with
SIMPLEMMA_VERSION = "2.0.0"
CORPUS_SIZE = 63_090_618_290
POS_TAGS = ("NOUN", "PROPN", "VERB", "ADJ", "ADV", "PRON", "DET", "ADP", "CONJ")
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


def lemma_key(word: str, proper: bool = False) -> str:
    """
    Key of a word in the frequency dictionary

    Description:
        The word goes to lower case and then to its lemma by lemmatize.
        simplemma tells the case apart and leaves an unknown capitalized word
        as it is, so a word at the start of a sentence would miss its lemma
        (Miró, Déjame - mirar, dejar); the lower case finds it. A proper noun
        keeps its form in lower case (París, not the verb parir), as the
        dictionary keeps the forms of the nouns written with a capital letter.
        The dictionary is built with this function, so a text is looked up by
        the keys the dictionary was built with; the lemmas are those of
        simplemma SIMPLEMMA_VERSION, another version gives other ones

    Arguments:
        word (str): Word form in any case
        proper (bool): The word is a proper noun

    Returns:
        str: Key of the dictionary

    Example:
        >>> from ests.datasets.freq_dict import lemma_key
        >>> lemma_key("Miró"), lemma_key("computadoras"), lemma_key("fue")
        ('mirar', 'computador', 'ser')
        >>> lemma_key("París"), lemma_key("París", proper=True)
        ('parir', 'parís')
    """
    form = word.lower()
    return form if proper else lemmatize(form).lower()


class FreqDict(Dataset):
    """
    Frequency dictionary of Spanish lemmas by Google Books Ngram

    Description:
        83,785 lemmas (109,178 rows of a lemma and a part of speech) of the
        Spanish books of Google Books Ngram of 1980-2019, 63 billion words, with
        the frequency per million words, the range (the number of years out of
        40 in which the lemma occurs), Juilland's D over the years and the
        number of books. The forms tagged by Google with a part of speech are
        lower-cased and lemmatized by simplemma 2.0.0, the lemmatizer of the
        library, so a word is looked up by its lemma_key (computadoras -
        computador);
        a noun form written with a capital letter in 90% of its occurrences is
        a proper noun (PROPN) as a whole, its lower-case occurrences included
        (the form dios; the NOUN row of dios comes from dioses), as the tagset
        of Google has none. The rows below
        0.1 ipm or found in fewer than 5 years are left out. The dictionary is
        derived from Google Books Ngram under CC BY 3.0 and is distributed
        under the same licence
        For a lookup the parts of speech of a lemma are merged: the frequencies
        are summed, the range, the dispersion and the number of books are the
        greatest ones. The parsed dictionary is cached by the path of the file
        and read once per process; the archive is verified against its SHA-256
        checksum

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
        Entry(lemma='gato', pos=('NOUN', 'ADJ'), ipm=29.08, range=40, dispersion=95, docs=232841)
        >>> fd.ipm("perro"), fd.ipm("computadora"), fd.ipm("computador")
        (62.57, 0.0, 20.07)

    Iterating over the dictionary:
        >>> for record in fd.get_records(pos="NOUN", limit=2):
        ...     print(record)
        {'lemma': 'año', 'pos': 'NOUN', 'ipm': 1639.27, 'range': 40, 'dispersion': 98, 'docs': 837102}
        {'lemma': 'parte', 'pos': 'NOUN', 'ipm': 1295.88, 'range': 40, 'dispersion': 99, 'docs': 852898}

    Arguments:
        data_dir (str|Path): Directory of the dictionary

    Attributes:
        entries (dict[str, Entry]): Entries by lemma, the parts of speech merged
        min_ipm (float): Minimum frequency in the dictionary

    Methods:
        check_data: Checking that the file of the dictionary is in place
        download: Downloading the dictionary from the network
        lookup: Getting the entry of a lemma
        ipm: Getting the frequency of a lemma
        get_texts: Getting the lemmas of the dictionary
        get_records: Getting the records of the dictionary
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

        Returns:
            bool: Result of the check

        Raises:
            DatasetNotFoundError: If the dictionary is not found
        """
        if not self._filepath.is_file():
            msg = (
                f"The dataset {NAME} is not found\n"
                "Download it with the commands:\n"
                ">>> fd = FreqDict()\n"
                ">>> fd.download()"
            )
            raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Downloading the dictionary from the network and extracting the file

        Description:
            The archive is verified against its SHA-256 checksum; a corrupted
            or replaced file is removed and downloaded again in the same call.
            If the archive is there but the file of the dictionary is missing,
            it is extracted again. The parsed dictionary is read anew

        Arguments:
            force (bool): Download the dictionary even if it is already downloaded

        Raises:
            DownloadError: If the archive cannot be downloaded or fails the checksum
        """
        missing = not self._filepath.is_file()
        fetch_archive(DOWNLOAD_URL, self._archive, ARCHIVE_SHA256, missing, force)
        self.check_data()
        load_entries.cache_clear()
        load_min_ipm.cache_clear()

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
            ParameterError: If the part of speech is unknown
            ParameterError: If the number of records is negative
        """
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
    def min_ipm(self) -> float:
        """
        Minimum frequency of an entry of the dictionary
        """
        self._ensure_data()
        return load_min_ipm(self._filepath)

    def _ensure_data(self) -> None:
        """
        Checking once that the file of the dictionary is in place

        Description:
            The first successful check is remembered, so that lookup and ipm do
            not touch the file system for every word
        """
        if not self._checked:
            self.check_data()
            self._checked = True

    def lookup(self, lemma: str) -> Entry | None:
        """
        Getting the entry of a lemma

        Arguments:
            lemma (str): Lemma in any case

        Returns:
            Entry|None: Entry of the dictionary, None if the lemma is not in it
        """
        return self.entries.get(lemma.lower())

    def ipm(self, lemma: str) -> float:
        """
        Getting the frequency of a lemma

        Arguments:
            lemma (str): Lemma in any case

        Returns:
            float: Occurrences per million words, 0 if the lemma is not in the dictionary
        """
        entry = self.lookup(lemma)
        return entry.ipm if entry else 0.0

    def __len__(self) -> int:
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
        greatest ones. The result is cached by the path of the file, so every
        FreqDict over one directory shares one parsed dictionary; the cache is
        cleared by a new download

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
        Computed once over the parsed dictionary and cached by the path of the
        file, as load_entries; it is the frequency of the words out of the
        dictionary in the surprisal

    Arguments:
        filepath (Path): Path to the file of the dictionary

    Returns:
        float: Minimum frequency
    """
    return min(entry.ipm for entry in load_entries(filepath).values())
