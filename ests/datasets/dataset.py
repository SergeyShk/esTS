import shutil
import unicodedata
from abc import ABCMeta, abstractmethod
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from ..exceptions import DownloadError, ParameterError
from ..utils import download_file, extract_archive, sha256

Filter = Callable[[dict[str, Any]], bool]
Filters = list[Filter]


class Dataset(metaclass=ABCMeta):
    """
    Abstract dataset

    Arguments:
        name (str): Name of the dataset
        meta (dict): Reference information about the dataset

    Methods:
        check_data: Checking that the directories and files of the dataset are in place
        get_texts: Getting the texts (without the headers) of the dataset
        get_records: Getting the records (with the headers) of the dataset
        download: Downloading the dataset from the network
    """

    __test__ = False

    @abstractmethod
    def __init__(self, name: str, meta: dict[str, str] | None = None) -> None:
        self.name = name
        self.meta = meta or {}

    def __repr__(self) -> str:
        return f"Dataset('{self.name}')"

    @property
    def info(self) -> dict[str, str]:
        """
        Name of the dataset and its reference information
        """
        return {"name": self.name, **self.meta}

    @abstractmethod
    def __iter__(self) -> Iterator[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def check_data(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_texts(self, *args: Any) -> Iterator[str]:
        raise NotImplementedError

    @abstractmethod
    def get_records(self, *args: Any) -> Iterator[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def download(self, force: bool = False) -> None:
        raise NotImplementedError


def fetch_archive(
    url: str, filepath: Path, checksum: str, missing: bool, force: bool = False
) -> None:
    """
    Downloading the archive of a dataset, verifying it and extracting the files

    Description:
        The archive is verified and extracted when it is downloaded now or the
        extracted files are missing. A file that fails the SHA-256 checksum
        (corrupted, cut short, replaced) is removed and downloaded again in the
        same call. The files are extracted into a temporary directory next to
        the archive, which takes the place of the earlier directory of the
        dataset only once the extraction is complete: no stale file stays, and
        an interrupted extraction never leaves a half of the dataset under its
        name

    Arguments:
        url (str): Address of the archive
        filepath (Path): Path to the archive; the files are extracted into its directory
        checksum (str): SHA-256 checksum of the archive
        missing (bool): Whether the extracted files are missing
        force (bool): Download the archive even if it is already there

    Raises:
        DownloadError: If the archive cannot be downloaded or fails the checksum twice
        DataFileError: If the verified archive cannot be extracted
    """
    downloaded = download_file(
        url=url, filename=filepath.name, dirpath=filepath.parent, force=force
    )
    if not downloaded and not missing:
        return
    if sha256(filepath) != checksum:
        filepath.unlink(missing_ok=True)
        download_file(url=url, filename=filepath.name, dirpath=filepath.parent, force=True)
        if sha256(filepath) != checksum:
            filepath.unlink(missing_ok=True)
            raise DownloadError(
                f"The file {filepath} failed the checksum verification and was removed, "
                "download it again"
            )
    stem = filepath.name
    while (shorter := Path(stem).stem) != stem:
        stem = shorter
    target = filepath.parent / stem
    partial = filepath.parent / (stem + ".part")
    shutil.rmtree(partial, ignore_errors=True)
    try:
        extracted = Path(extract_archive(filepath, partial))
        shutil.rmtree(target, ignore_errors=True)
        extracted.rename(target)
    finally:
        shutil.rmtree(partial, ignore_errors=True)


def check_limit(limit: int | None) -> None:
    """
    Checking the number of records

    Arguments:
        limit (int): Number of records

    Raises:
        ParameterError: If the number of records is negative
    """
    if limit is not None and limit < 0:
        raise ParameterError(f"The number of records must not be negative - {limit}")


def _fold(value: str) -> str:
    """String in lower case without diacritics: «Galdós» and «galdos» are the same"""
    decomposed = unicodedata.normalize("NFD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def substring_filter(field: str, value: str) -> Filter:
    """
    Filter of the records by a substring of a field, regardless of case and accents

    Arguments:
        field (str): Name of the field of a record
        value (str): Substring to look for

    Returns:
        Filter: Predicate on a record
    """
    needle = _fold(value)
    return lambda record: needle in _fold(record[field])


def length_filters(min_len: int | None, max_len: int | None) -> Filters:
    """
    Filters of the records by the length of the text

    Arguments:
        min_len (int): Minimum length of the text (in characters)
        max_len (int): Maximum length of the text (in characters)

    Returns:
        Filters: List of predicates on a record

    Raises:
        ParameterError: If the minimum length is not greater than 0
        ParameterError: If the maximum length is not greater than 0
        ParameterError: If the minimum length is greater than the maximum one
    """
    filters: Filters = []
    if min_len is not None:
        if min_len < 1:
            raise ParameterError("The minimum length of the text must be greater than 0")
        filters.append(lambda record: len(record["text"]) >= min_len)
    if max_len is not None:
        if max_len < 1:
            raise ParameterError("The maximum length of the text must be greater than 0")
        filters.append(lambda record: len(record["text"]) <= max_len)
    if min_len is not None and max_len is not None and min_len > max_len:
        raise ParameterError("The minimum length of the text is greater than the maximum one")
    return filters
