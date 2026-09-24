import csv
from collections.abc import Iterator
from itertools import islice
from pathlib import Path
from typing import Any

from ..constants import DEFAULT_DATA_DIR
from ..exceptions import DatasetNotFoundError, ParameterError
from ..utils import to_path
from .dataset import Dataset, Filters, check_limit, fetch_archive, length_filters, substring_filter

NAME = "spanish_literature"
VERSION = 1
META = {
    "url": "https://www.gutenberg.org",
    "description": "Spanish-language literature in the public domain",
    "author": "Shkarin S.S.",
    "license": "Public domain",
}
ARCHIVE = f"{NAME}_v{VERSION}.tar.xz"
DOWNLOAD_URL = f"https://github.com/SergeyShk/esTS/raw/master/ests/datasets/data/{ARCHIVE}"
ARCHIVE_SHA256 = "a11d5e3f54f6b9808e13f5312253f6d2315810f3f710d8231d46083fb96f0e9c"
GENRES = ("prose", "poems", "drama", "publicism")
AUTHORS = {
    "alarcon": "Pedro Antonio de Alarcón",
    "arniches": "Carlos Arniches",
    "blasco_ibanez": "Vicente Blasco Ibáñez",
    "cervantes": "Miguel de Cervantes",
    "clarin": "Leopoldo Alas «Clarín»",
    "dario": "Rubén Darío",
    "dicenta": "Joaquín Dicenta",
    "galdos": "Benito Pérez Galdós",
    "hernandez": "José Hernández",
    "ingenieros": "José Ingenieros",
    "larra": "Mariano José de Larra",
    "lope": "Lope de Vega",
    "lugones": "Leopoldo Lugones",
    "machado": "Antonio Machado",
    "marti": "José Martí",
    "moratin": "Leandro Fernández de Moratín",
    "palacio_valdes": "Armando Palacio Valdés",
    "palma": "Ricardo Palma",
    "pardo_bazan": "Emilia Pardo Bazán",
    "payro": "Roberto J. Payró",
    "pereda": "José María de Pereda",
    "quevedo": "Francisco de Quevedo",
    "quiroga": "Horacio Quiroga",
    "ramon_y_cajal": "Santiago Ramón y Cajal",
    "rizal": "José Rizal",
    "rodo": "José Enrique Rodó",
    "rosalia_de_castro": "Rosalía de Castro",
    "ruiz_de_alarcon": "Juan Ruiz de Alarcón",
    "sarmiento": "Domingo Faustino Sarmiento",
    "unamuno": "Miguel de Unamuno",
    "valera": "Juan Valera",
    "valle_inclan": "Ramón del Valle-Inclán",
    "zorrilla": "José Zorrilla",
}
METADATA = "metadata.tsv"
DEFAULT_DATASET_DIR = DEFAULT_DATA_DIR.joinpath("texts")


class SpanishLiterature(Dataset):
    """
    Collection of Spanish-language literature in the public domain

    Description:
        150 works by 33 authors from Spain, Latin America and the Philippines,
        from the Golden Age to the 1920s, in four genres: prose, poems, drama
        and publicism. The texts are transcriptions of Project Gutenberg
        without its licence and trademark, cut to the text of the author:
        without the title pages, the notes of the transcribers, the tables of
        contents, the introductions and notes of the editors and the
        footnotes. Every work is in the public domain both in Spain (the
        author died before 1946) and in the United States (published before
        1931). Works in several volumes are joined in one text. The years are
        those of the first publication. The archive is downloaded from the
        repository of the library and verified against its SHA-256 checksum

    References:
        https://www.gutenberg.org

    Example:
    Information about the dataset:
        >>> from pprint import pprint
        >>> from ests.datasets import SpanishLiterature
        >>> sl = SpanishLiterature()
        >>> pprint(sl.info)
        {'author': 'Shkarin S.S.',
         'description': 'Spanish-language literature in the public domain',
         'license': 'Public domain',
         'name': 'spanish_literature',
         'url': 'https://www.gutenberg.org'}

    Iterating over the dataset:
        >>> record = next(sl.get_records(genre="drama", author="lope"))
        >>> sorted(record)
        ['author', 'country', 'file', 'genre', 'text', 'title', 'year_from', 'year_to']
        >>> record["title"], record["year_from"], record["country"], record["file"].name
        ('Fuenteovejuna', 1619, 'España', '60198.txt')
        >>> for record in sl.get_records(author="galdos", year_from=1880, year_to=1884):
        ...     print(record["title"], record["year_from"], len(record["text"]))
        La desheredada 1881 820454
        El amigo Manso 1882 521156
        La de Bringas 1884 413730
        Tormento 1884 477286

    Arguments:
        data_dir (str|Path): Directory of the dataset

    Attributes:
        genres (tuple[str]): Genres
        authors (dict[str, str]): Names of the authors by the names of their folders

    Methods:
        check_data: Checking that the directories and files of the dataset are in place
        download: Downloading the dataset from the network
        get_texts: Getting the texts (without the headers) of the dataset
        get_records: Getting the records (with the headers) of the dataset
    """

    def __init__(self, data_dir: str | Path = DEFAULT_DATASET_DIR) -> None:
        super().__init__(NAME, meta=META)
        self.data_dir = to_path(data_dir).resolve()
        self.genres = GENRES
        self.authors = AUTHORS
        self._filepath = self.data_dir.joinpath(ARCHIVE)
        self._dirpath = self.data_dir.joinpath(f"{NAME}_v{VERSION}")

    @property
    def filepath(self) -> str | None:
        """
        Path to the archive of the dataset
        """
        if self._filepath.is_file():
            return str(self._filepath)
        return None

    def _rows(self) -> list[dict[str, str]]:
        """Rows of the list of works"""
        with self._dirpath.joinpath(METADATA).open(encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file, delimiter="\t", quoting=csv.QUOTE_NONE))

    def _missing(self) -> bool:
        """Whether the list of works or the file of a work is missing"""
        if not self._dirpath.joinpath(METADATA).is_file():
            return True
        return any(not self._dirpath.joinpath(row["file"]).is_file() for row in self._rows())

    def check_data(self) -> bool:
        """
        Checking that the list of works and the file of every work are in place

        Returns:
            bool: Result of the check

        Raises:
            DatasetNotFoundError: If the dataset is not found
        """
        if self._missing():
            msg = (
                f"The dataset {NAME} is not found\n"
                "Download it with the commands:\n"
                ">>> sl = SpanishLiterature()\n"
                ">>> sl.download()"
            )
            raise DatasetNotFoundError(msg)
        return True

    def download(self, force: bool = False) -> None:
        """
        Downloading the dataset from the network and extracting the files

        Description:
            The archive is verified against its SHA-256 checksum; a corrupted
            or replaced file (after a broken download, for example) is removed
            and downloaded again in the same call. If the archive is there but
            the list of works or the file of a work is missing (after an
            interrupted extraction, for example), it is extracted again

        Arguments:
            force (bool): Download the dataset even if it is already downloaded

        Raises:
            DownloadError: If the archive cannot be downloaded or fails the checksum
        """
        fetch_archive(DOWNLOAD_URL, self._filepath, ARCHIVE_SHA256, self._missing(), force)
        self.check_data()

    def get_texts(
        self,
        genre: str | None = None,
        author: str | None = None,
        country: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Iterator[str]:
        """
        Getting the texts (without the headers) of the dataset

        Arguments:
            genre (str): Genre from GENRES - prose, poems, drama or publicism
            author (str): Author (a substring of the name, regardless of case and accents)
            country (str): Country (a substring of the name, regardless of case and accents)
            year_from (int): Earliest year of the first publication
            year_to (int): Latest year of the first publication
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)
            limit (int): Number of texts

        Returns:
            iterator[str]: Texts
        """
        fields, lengths = self._get_filters(
            genre, author, country, year_from, year_to, min_len, max_len
        )
        check_limit(limit)
        for record in islice(self._filtered_iter(fields, lengths), limit):
            yield record["text"]

    def get_records(
        self,
        genre: str | None = None,
        author: str | None = None,
        country: str | None = None,
        year_from: int | None = None,
        year_to: int | None = None,
        min_len: int | None = None,
        max_len: int | None = None,
        limit: int | None = None,
    ) -> Iterator[dict[str, Any]]:
        """
        Getting the records (with the headers) of the dataset

        Arguments:
            genre (str): Genre from GENRES - prose, poems, drama or publicism
            author (str): Author (a substring of the name, regardless of case and accents)
            country (str): Country (a substring of the name, regardless of case and accents)
            year_from (int): Earliest year of the first publication
            year_to (int): Latest year of the first publication
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)
            limit (int): Number of records

        Returns:
            iterator[dict[str, object]]: Records
        """
        fields, lengths = self._get_filters(
            genre, author, country, year_from, year_to, min_len, max_len
        )
        check_limit(limit)
        yield from islice(self._filtered_iter(fields, lengths), limit)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterating over the dataset

        Description:
            The works in the order of the list of works: the genres in the
            order of GENRES, within a genre the authors by the names of their
            folders and their works by year; the texts are read one at a time

        Returns:
            iterator[dict[str, object]]: Records
        """
        yield from self._filtered_iter([], [])

    def _filtered_iter(self, fields: Filters, lengths: Filters) -> Iterator[dict[str, Any]]:
        """
        Records that pass every filter

        Description:
            The filters on the fields of the list of works go before the text
            is read, so a work that fails them is not opened; the filters on
            the length go after

        Arguments:
            fields (Filters): Predicates on the fields of a record
            lengths (Filters): Predicates on the length of the text

        Returns:
            iterator[dict[str, object]]: Records
        """
        self.check_data()
        for row in self._rows():
            filepath = self._dirpath.joinpath(row["file"])
            record = {
                "genre": row["genre"],
                "author": row["author"],
                "title": row["title"],
                "year_from": int(row["year_from"]),
                "year_to": int(row["year_to"]),
                "country": row["country"],
                "text": "",
                "file": filepath,
            }
            if not all(filter_(record) for filter_ in fields):
                continue
            record["text"] = filepath.read_text(encoding="utf-8").strip()
            if all(filter_(record) for filter_ in lengths):
                yield record

    @staticmethod
    def _get_filters(
        genre: str | None,
        author: str | None,
        country: str | None,
        year_from: int | None,
        year_to: int | None,
        min_len: int | None,
        max_len: int | None,
    ) -> tuple[Filters, Filters]:
        """
        Filters of the records: on the fields of the list of works and on the length of the text

        Arguments:
            genre (str): Genre from GENRES
            author (str): Author (a substring of the name, regardless of case and accents)
            country (str): Country (a substring of the name, regardless of case and accents)
            year_from (int): Earliest year of the first publication
            year_to (int): Latest year of the first publication
            min_len (int): Minimum length of the text (in characters)
            max_len (int): Maximum length of the text (in characters)

        Returns:
            tuple[Filters, Filters]: Predicates on the fields and on the length of the text

        Raises:
            ParameterError: If the genre is unknown
            ParameterError: If the earliest year is greater than the latest one
            ParameterError: If a length of the text is not greater than 0
            ParameterError: If the minimum length is greater than the maximum one
        """
        filters: Filters = []
        if genre is not None:
            if genre not in GENRES:
                raise ParameterError(f"Unknown genre {genre}, expected one of {GENRES}")
            filters.append(lambda record: record["genre"] == genre)
        if author is not None:
            filters.append(substring_filter("author", author))
        if country is not None:
            filters.append(substring_filter("country", country))
        if year_from is not None and year_to is not None and year_from > year_to:
            raise ParameterError("The earliest year is greater than the latest one")
        if year_from is not None:
            filters.append(lambda record: record["year_from"] >= year_from)
        if year_to is not None:
            filters.append(lambda record: record["year_to"] <= year_to)
        return filters, length_filters(min_len, max_len)
