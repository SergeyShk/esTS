import hashlib
import io
import re
import shutil
import tarfile
from collections import Counter
from pathlib import Path

import pytest

from ests.datasets import SpanishLiterature
from ests.datasets import dataset as dataset_module
from ests.datasets import spanish_literature as module
from ests.exceptions import DatasetNotFoundError, DownloadError, ParameterError

BUNDLED_ARCHIVE = Path(__file__).parents[2] / "ests" / "datasets" / "data" / module.ARCHIVE
ROOT = f"{module.NAME}_v{module.VERSION}"
HEADER = "file\tgenre\tauthor\ttitle\tyear_from\tyear_to\tcountry\tgutenberg"
WORKS = [
    ("prose/galdos/1.txt", "prose", "Benito Pérez Galdós", "Uno", 1880, 1881, "España", "1"),
    ("poems/dario/2.txt", "poems", "Rubén Darío", "Dos", 1896, 1896, "Nicaragua", "2"),
    ("drama/lope/3.txt", "drama", "Lope de Vega", "Tres", 1619, 1619, "España", "3"),
    (
        "publicism/rodo/4.txt",
        "publicism",
        "José Enrique Rodó",
        "Cuatro",
        1900,
        1900,
        "Uruguay",
        "4",
    ),
]


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_data")
    shutil.copy(BUNDLED_ARCHIVE, path / module.ARCHIVE)
    dataset = SpanishLiterature(data_dir=path)
    # The archive is in the repository next to the code, the network is not needed
    dataset.download()
    return dataset


@pytest.fixture(scope="module")
def records(dataset):
    return list(dataset)


def _archive() -> bytes:
    """Small archive with the layout of the dataset"""
    files = {f"{ROOT}/metadata.tsv": "\n".join([HEADER] + ["\t".join(map(str, w)) for w in WORKS])}
    for work in WORKS:
        files[f"{ROOT}/{work[0]}"] = f"Texto de «{work[3]}».\n"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:xz") as tar:
        for name, content in files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


@pytest.fixture
def small(tmp_path, monkeypatch):
    """Dataset over the small archive, with the network replaced by a copy of the archive"""
    archive = _archive()
    monkeypatch.setattr(module, "ARCHIVE_SHA256", hashlib.sha256(archive).hexdigest())
    calls = []

    def fake_download(url, filename, dirpath, force=False):
        calls.append(force)
        path = Path(dirpath) / filename
        if path.is_file() and not force:
            return ""
        path.write_bytes(archive)
        return str(path)

    monkeypatch.setattr(dataset_module, "download_file", fake_download)
    return SpanishLiterature(data_dir=tmp_path), archive, calls


def test_info():
    dataset = SpanishLiterature(data_dir="/tmp")
    assert repr(dataset) == "Dataset('spanish_literature')"
    assert dataset.info["name"] == "spanish_literature"
    assert dataset.info["license"] == "Public domain"
    assert dataset.genres == ("prose", "poems", "drama", "publicism")
    assert dataset.authors["galdos"] == "Benito Pérez Galdós"


def test_not_downloaded(tmp_path):
    dataset = SpanishLiterature(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(
        DatasetNotFoundError, match=r"^The dataset spanish_literature is not found"
    ):
        dataset.check_data()
    with pytest.raises(OSError):
        list(dataset.get_texts())


@pytest.mark.network
def test_download(tmp_path):
    dataset = SpanishLiterature(data_dir=tmp_path)
    dataset.download()
    assert dataset.filepath == str(tmp_path / module.ARCHIVE)
    assert sum(1 for _ in dataset.get_records(genre="poems")) == 10


def test_download_extracts_existing_archive(small):
    dataset, _, calls = small
    dataset.download()
    assert calls == [False]
    assert dataset.check_data()
    assert dataset.filepath == str(dataset._filepath)
    assert [record["title"] for record in dataset] == ["Uno", "Dos", "Tres", "Cuatro"]


def test_download_keeps_extracted_files(small):
    dataset, _, calls = small
    dataset.download()
    marker = dataset._dirpath / "prose" / "galdos" / "1.txt"
    marker.write_text("Texto cambiado.", encoding="utf-8")
    dataset.download()
    assert calls == [False, False]
    assert marker.read_text(encoding="utf-8") == "Texto cambiado."


def test_download_force(small):
    dataset, _, calls = small
    dataset.download()
    dataset.download(force=True)
    assert calls == [False, True]


def test_download_restores_missing_files(small):
    dataset, _, _ = small
    dataset.download()
    stray = dataset._dirpath / "prose" / "stray.txt"
    stray.write_text("sobra", encoding="utf-8")
    (dataset._dirpath / "metadata.tsv").unlink()
    dataset.download()
    assert dataset.check_data()
    assert not stray.exists()


def test_download_restores_missing_text(small):
    dataset, _, calls = small
    dataset.download()
    text = dataset._dirpath / "publicism" / "rodo" / "4.txt"
    text.unlink()
    with pytest.raises(DatasetNotFoundError):
        dataset.check_data()
    with pytest.raises(DatasetNotFoundError):
        list(dataset.get_texts(genre="publicism"))
    dataset.download()
    assert calls == [False, False]
    assert text.read_text(encoding="utf-8") == "Texto de «Cuatro».\n"


def test_download_interrupted_extraction(small, monkeypatch):
    dataset, _, _ = small
    dataset.download()
    kept = dataset._dirpath / "prose" / "galdos" / "1.txt"
    kept.write_text("Texto anterior.", encoding="utf-8")
    (dataset._dirpath / "metadata.tsv").unlink()

    def broken_extract(archive_file, extract_dir=None):
        # The first members are written, then the extraction stops
        folder = Path(extract_dir) / ROOT / "drama"
        folder.mkdir(parents=True)
        (folder / "3.txt").write_text("Texto", encoding="utf-8")
        raise KeyboardInterrupt

    extract = dataset_module.extract_archive
    monkeypatch.setattr(dataset_module, "extract_archive", broken_extract)
    with pytest.raises(KeyboardInterrupt):
        dataset.download()
    # The earlier directory stays as it was and the partial one is gone
    assert kept.read_text(encoding="utf-8") == "Texto anterior."
    assert not (dataset.data_dir / f"{ROOT}.part").exists()
    monkeypatch.setattr(dataset_module, "extract_archive", extract)
    dataset.download()
    assert dataset.check_data()
    assert kept.read_text(encoding="utf-8") == "Texto de «Uno».\n"


def test_download_replaces_broken_archive(small):
    dataset, archive, calls = small
    dataset._filepath.write_bytes(b"\x00" * 40)
    dataset.download()
    assert calls == [False, True]
    assert dataset._filepath.read_bytes() == archive
    assert dataset.check_data()


def test_download_checksum_error(small, monkeypatch):
    dataset, _, calls = small
    monkeypatch.setattr(module, "ARCHIVE_SHA256", "0" * 64)
    with pytest.raises(DownloadError, match="checksum"):
        dataset.download()
    assert calls == [False, True]
    assert dataset.filepath is None


def test_bundled_archive_checksum():
    with BUNDLED_ARCHIVE.open("rb") as file:
        assert hashlib.file_digest(file, "sha256").hexdigest() == module.ARCHIVE_SHA256


def test_records(records):
    assert len(records) == 150
    assert Counter(record["genre"] for record in records) == {
        "prose": 107,
        "publicism": 17,
        "drama": 16,
        "poems": 10,
    }
    assert {record["author"] for record in records} == set(module.AUTHORS.values())
    assert sorted(records[0]) == [
        "author",
        "country",
        "file",
        "genre",
        "text",
        "title",
        "year_from",
        "year_to",
    ]
    for record in records:
        assert record["file"].is_file()
        assert record["file"].parent.name in module.AUTHORS
        assert 1600 <= record["year_from"] <= record["year_to"] <= 1930
        assert record["text"] and record["text"] == record["text"].strip()


def test_records_order(records):
    genres = [record["genre"] for record in records]
    assert genres == sorted(genres, key=module.GENRES.index)
    prose = [(r["file"].parent.name, r["year_from"]) for r in records if r["genre"] == "prose"]
    assert prose == sorted(prose)


def test_texts_are_clean(records):
    for record in records:
        text = record["text"]
        # The licence and the trademark go, Gutenberg the printer stays
        assert not re.search(r"project gutenberg|gutenberg\.org|gutenberg-tm", text, re.I)
        # Braces and angle brackets are left in the schemes drawn by the authors
        assert not set("_=~#<") & set(text), record["title"]


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({"genre": "poems"}, 10),
        ({"author": "galdos"}, 21),
        ({"author": "PÉREZ GALDÓS"}, 21),
        ({"author": "darío"}, 8),
        ({"genre": "poems", "author": "dario"}, 5),
        ({"country": "argentina"}, 10),
        ({"country": "Mexico"}, 3),
        ({"year_to": 1700}, 9),
        ({"year_from": 1920}, 8),
        ({"year_from": 1880, "year_to": 1884, "author": "galdos"}, 4),
        ({"author": "Tolstói"}, 0),
    ],
)
def test_filters(dataset, filters, expected):
    assert sum(1 for _ in dataset.get_records(**filters)) == expected


def test_gutenberg_the_printer(dataset):
    text = next(dataset.get_texts(author="larra", genre="publicism"))
    assert "¡Maldito Gutenberg! ¿Qué genio maléfico te inspiró tu diabólica\ninvención?" in text


def test_filters_before_reading(dataset, monkeypatch):
    read = []
    read_text = Path.read_text

    def counting(path, *args, **kwargs):
        read.append(path.name)
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", counting)
    assert [record["title"] for record in dataset.get_records(author="lope")] == [
        "Fuenteovejuna",
        "El castigo sin venganza",
    ]
    assert read == ["60198.txt", "78160.txt"]
    read.clear()
    assert sum(1 for _ in dataset.get_texts(genre="drama", min_len=140_000)) == 3
    assert len(read) == 16


def test_subscripts(dataset):
    text = next(dataset.get_texts(author="unamuno", genre="prose"))
    assert "H2O, y el salero con su ClNa" in text


def test_length_filters(dataset):
    short = list(dataset.get_texts(max_len=100_000))
    assert short and all(len(text) <= 100_000 for text in short)
    long = list(dataset.get_texts(min_len=2_000_000))
    assert len(long) == 2
    assert all(len(text) >= 2_000_000 for text in long)


@pytest.mark.parametrize("limit", [0, 1, 3])
def test_limit(dataset, limit):
    assert sum(1 for _ in dataset.get_texts(limit=limit)) == limit
    assert sum(1 for _ in dataset.get_records(genre="drama", limit=limit)) == limit


@pytest.mark.parametrize(
    "bad_filter",
    [
        {"genre": "novel"},
        {"year_from": 1900, "year_to": 1800},
        {"min_len": 0},
        {"max_len": -1},
        {"min_len": 10, "max_len": 5},
        {"limit": -1},
    ],
)
def test_bad_filters(dataset, bad_filter):
    with pytest.raises(ParameterError):
        list(dataset.get_texts(**bad_filter))
    with pytest.raises(ValueError):
        list(dataset.get_records(**bad_filter))
