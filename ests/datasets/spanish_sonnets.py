import json
from collections import Counter
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DataFileError, DatasetNotFoundError, ParameterError
from ..utils import to_path
from .dataset import Dataset, Filters, check_limit, fetch_archive, length_filters, substring_filter

NAME = "spanish_sonnets"
VERSION = 1
META = {
    "url": "https://github.com/pruizf/disco",
    "description": "Diachronic Spanish Sonnet Corpus (DISCO), the sonnets in the public domain",
    "author": "Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., Calvo Tello J.",
    "license": "CC BY 4.0",
    "citation": (
        "Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., Calvo Tello J. Diachronic "
        "Spanish Sonnet Corpus (DISCO), version 5.0. Madrid: UNED, 2017-2023. "
        "https://github.com/pruizf/disco"
    ),
}
ARCHIVE = f"{NAME}_v{VERSION}.tar.xz"
DOWNLOAD_URL = f"https://github.com/SergeyShk/esTS/raw/master/ests/datasets/data/{ARCHIVE}"
ARCHIVE_SHA256 = "f2f6d2443c37891d5c4a1372d83a589505f5cbbe531e5f081f7aa3fb94e30af7"
FILENAME = "sonnets.jsonl"
# Periods of the subcorpora of DISCO, in the order of the records
PERIODS = ("15th-17th", "18th", "19th", "20th")
GENDERS = ("F", "M")
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class SpanishSonnets(Dataset):
    """
    Collection of Spanish sonnets of the Diachronic Spanish Sonnet Corpus (DISCO)

    Description:
        The sonnets of DISCO 5.0 in the public domain: the ones of the authors
        who died before 1946, of the authors of the 15th-18th centuries whose
        death is unknown and of the authors of the 19th-century anthology born
        before 1866 or with no dates; the sonnets of the authors who died in
        1946 or later, most of the Filipino poets of the 20th century, are left
        out. The years of life are read from the biographical line of the source
        where DISCO took a later year of it for the death (Echegaray, 1916 and
        not 1904), and so is the country of birth where the line names it
        (Gómez de Avellaneda, Cuba and not Haiti). Every line of a sonnet carries its metrical pattern (+ for a
        stressed syllable, - for an unstressed one) and the label of its rhyme,
        both annotated automatically by DISCO: the scansion by ADSO (accuracy
        0.91) and by Jumper for the modernist and the Filipino sonnets (0.95),
        the rhyme by RhymeTagger, which labels a line that rhymes with no other
        with -. 20 sonnets have no labels of the rhyme, and the long sequences
        none after the letter N: such a label is empty. A record is one sonnet
        of 14 lines, a sonnet with an estrambote or a sequence of sonnets that
        DISCO keeps in one file; the sonnets of a sequence in separate files
        have the title "Part of: " and the title of the sequence. The speakers
        of the dialogues ([Car], [POETA]) and the calls of the footnotes are
        left out of the lines, as out of their metrical patterns. DISCO is
        distributed under CC BY 4.0, and so is this dataset; the archive is
        downloaded from the repository of the library and verified against its
        SHA-256 checksum

    References:
        https://github.com/pruizf/disco
        https://doi.org/10.1093/llc/fqaa035

    Example:
    Information about the dataset:
        >>> from ests.datasets import SpanishSonnets
        >>> ss = SpanishSonnets()
        >>> ss.info["license"]
        'CC BY 4.0'
        >>> ss.authors.most_common(2)
        [('Rubén Darío', 140), ('José Santos Chocano', 130)]

    Iterating over the dataset:
        >>> record = next(ss.get_records(author="rubén darío"))
        >>> sorted(record)
        ['author', 'birth', 'country', 'death', 'gender', 'id', 'meter', 'period', 'rhyme', 'text', 'title']
        >>> record["title"], record["period"], record["country"], record["death"]
        ('LA FE', '19th', 'Nicaragua', 1916)
        >>> print(record["text"].split("\\n")[0])
        En medio del abismo de la duda
        >>> record["meter"][0], "".join(record["rhyme"])
        ('-+---+---+-', 'ABBAABBACDCDEE')
        >>> sum(1 for _ in ss.get_texts(period="18th"))
        321

    Arguments:
        data_dir (str|Path): Directory of the dataset

    Attributes:
        periods (tuple[str]): Periods of the subcorpora
        authors (Counter): Number of sonnets by author

    Methods:
        check_data: Checking that the file of the dataset is in place
        download: Downloading the dataset from the network
        get_texts: Getting the texts (without the headers) of the dataset
        get_records: Getting the records (with the headers) of the dataset
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.periods = PERIODS
        self._archive = self.data_dir.joinpath(ARCHIVE)
        self._filepath = self.data_dir.joinpath(f"{NAME}_v{VERSION}", FILENAME)

    @property
    def filepath(self) -> str | None:
        """
        Path to the file of the dataset
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    @property
    def authors(self) -> Counter[str]:
        """
        Number of sonnets by author
        """
        return Counter(record["author"] for record in self)

    def check_data(self) -> bool:
        """
        Checking that the file of the dataset is in place

        Returns:
            bool: Result of the check

        Raises:
            DatasetNotFoundError: If the dataset is not found
        """
        if not self._filepath.is_file():
            msg = (
                f"The dataset {NAME} is not found\n"
                "Download it with the commands:\n"
                ">>> ss = SpanishSonnets()\n"
                ">>> ss.download()"
            )
            raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Downloading the dataset from the network and extracting the file

        Description:
            The archive is verified against its SHA-256 checksum; a corrupted
            or replaced file is removed and downloaded again in the same call.
            If the archive is there but the file of the dataset is missing, it
            is extracted again

        Arguments:
            force (bool): Download the dataset even if it is already downloaded

        Raises:
            DownloadError: If the archive cannot be downloaded or fails the checksum
        """
        missing = not self._filepath.is_file()
        fetch_archive(DOWNLOAD_URL, self._archive, ARCHIVE_SHA256, missing, force)
        self.check_data()

    def get_texts(
        self,
        period: str | None = None,
        author: str | None = None,
        country: str | None = None,
        gender: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Iterator[str]:
        """
        Getting the texts (without the headers) of the dataset

        Arguments:
            period (str): Period from PERIODS
            author (str): Author (a substring of the name, regardless of case and accents)
            country (str): Country of birth (a substring of the name in Spanish,
                regardless of case and accents)
            gender (str): Gender of the author, F or M
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)
            limit (int): Number of texts

        Returns:
            iterator[str]: Texts of the sonnets
        """
        for record in self.get_records(period, author, country, gender, min_len, max_len, limit):
            yield record["text"]

    def get_records(
        self,
        period: str | None = None,
        author: str | None = None,
        country: str | None = None,
        gender: str | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Getting the records (with the headers) of the dataset

        Description:
            The fields of a record: id - the identifier of the sonnet in DISCO,
            period, author, title, country of birth (empty when unknown) and
            gender of the author, birth and death - the years of life (None
            when unknown), text - the lines, the stanzas separated by a blank
            line, meter - the metrical pattern of every line, rhyme - the label
            of the rhyme of every line

        Arguments:
            period (str): Period from PERIODS
            author (str): Author (a substring of the name, regardless of case and accents)
            country (str): Country of birth (a substring of the name in Spanish,
                regardless of case and accents)
            gender (str): Gender of the author, F or M
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)
            limit (int): Number of records

        Returns:
            iterator[dict[str, object]]: Records

        Raises:
            ParameterError: If the period or the gender is unknown
            ParameterError: If a length is not greater than 0 or the minimum is
                greater than the maximum
            ParameterError: If the number of records is negative
        """
        filters = self._get_filters(period, author, country, gender, min_len, max_len)
        check_limit(limit)
        records = (record for record in self if all(filter_(record) for filter_ in filters))
        yield from islice(records, limit)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterating over the dataset

        Description:
            The sonnets in the order of PERIODS, within a period by the
            identifier of DISCO, which keeps the authors and the order of their
            source; the file is read one line at a time

        Returns:
            iterator[dict[str, object]]: Records

        Raises:
            DataFileError: If a line of the file cannot be read
        """
        self.check_data()
        with self._filepath.open(encoding="utf-8") as file:
            for number, line in enumerate(file, start=1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    raise DataFileError(f"Line {number} of {self._filepath} cannot be read") from e
                record["meter"] = tuple(record["meter"])
                record["rhyme"] = tuple(record["rhyme"])
                yield record

    @staticmethod
    def _get_filters(
        period: str | None,
        author: str | None,
        country: str | None,
        gender: str | None,
        min_len: int | None,
        max_len: int | None,
    ) -> Filters:
        """
        Filters of the records

        Arguments:
            period (str): Period from PERIODS
            author (str): Author (a substring of the name)
            country (str): Country of birth (a substring of the name)
            gender (str): Gender of the author, F or M
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)

        Returns:
            Filters: Predicates on the records

        Raises:
            ParameterError: If the period or the gender is unknown
        """
        filters: Filters = []
        if period is not None:
            if period not in PERIODS:
                raise ParameterError(f"Unknown period {period}, expected one of {PERIODS}")
            filters.append(lambda record: record["period"] == period)
        if gender is not None:
            if gender not in GENDERS:
                raise ParameterError(f"Unknown gender {gender}, expected one of {GENDERS}")
            filters.append(lambda record: record["gender"] == gender)
        if author is not None:
            filters.append(substring_filter("author", author))
        if country is not None:
            filters.append(substring_filter("country", country))
        filters.extend(length_filters(min_len, max_len))
        return filters
