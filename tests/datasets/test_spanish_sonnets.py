import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

import pytest

from ests.datasets import SpanishSonnets
from ests.datasets import spanish_sonnets as module
from ests.exceptions import DataFileError, DatasetNotFoundError, ParameterError

BUNDLED_ARCHIVE = Path(__file__).parents[2] / "ests" / "datasets" / "data" / module.ARCHIVE
ROOT = f"{module.NAME}_v{module.VERSION}"


@pytest.fixture(scope="module")
def dataset(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_data")
    shutil.copy(BUNDLED_ARCHIVE, path / module.ARCHIVE)
    dataset = SpanishSonnets(data_dir=path)
    # The archive is in the repository next to the code, the network is not needed
    dataset.download()
    return dataset


@pytest.fixture(scope="module")
def records(dataset):
    return list(dataset)


def test_info():
    dataset = SpanishSonnets(data_dir="/tmp")
    assert repr(dataset) == "Dataset('spanish_sonnets')"
    assert dataset.info["name"] == "spanish_sonnets"
    assert dataset.info["license"] == "CC BY 4.0"
    assert "Diachronic Spanish Sonnet Corpus" in dataset.info["citation"]
    assert dataset.periods == ("15th-17th", "18th", "19th", "20th")


def test_not_downloaded(tmp_path):
    dataset = SpanishSonnets(data_dir=tmp_path)
    assert dataset.filepath is None
    with pytest.raises(DatasetNotFoundError, match=r"^The dataset spanish_sonnets is not found"):
        dataset.check_data()
    with pytest.raises(DatasetNotFoundError):
        list(dataset.get_texts())
    with pytest.raises(DatasetNotFoundError):
        dataset.authors  # noqa: B018


def test_bundled_archive_checksum():
    with BUNDLED_ARCHIVE.open("rb") as file:
        assert hashlib.file_digest(file, "sha256").hexdigest() == module.ARCHIVE_SHA256


@pytest.mark.network
def test_download(tmp_path):
    dataset = SpanishSonnets(data_dir=tmp_path)
    dataset.download()
    assert dataset.filepath == str(tmp_path / ROOT / module.FILENAME)
    assert sum(1 for _ in dataset.get_records(period="18th")) == 321


def test_download_extracts_again(tmp_path):
    shutil.copy(BUNDLED_ARCHIVE, tmp_path / module.ARCHIVE)
    dataset = SpanishSonnets(data_dir=tmp_path)
    dataset.download()
    assert dataset.filepath == str(tmp_path / ROOT / module.FILENAME)
    Path(dataset.filepath).unlink()
    assert dataset.filepath is None
    dataset.download()
    assert dataset.check_data()
    readme = (tmp_path / ROOT / "README.txt").read_text(encoding="utf-8")
    assert "Creative Commons Attribution 4.0" in readme
    assert "4259 of 4523" in readme


def test_records(records):
    assert len(records) == 4259
    assert Counter(record["period"] for record in records) == {
        "19th": 2845,
        "15th-17th": 1088,
        "18th": 321,
        "20th": 5,
    }
    assert Counter(record["gender"] for record in records) == {"M": 3964, "F": 295}
    assert sorted(records[0]) == [
        "author",
        "birth",
        "country",
        "death",
        "gender",
        "id",
        "meter",
        "period",
        "rhyme",
        "text",
        "title",
    ]
    for record in records:
        lines = record["text"].replace("\n\n", "\n").split("\n")
        assert record["text"] == record["text"].strip() and all(lines)
        # No speakers of the dialogues ([Car]) and no calls of the footnotes (diestra.7)
        assert not re.search(r"[\[\]\d]", record["text"])
        assert record["title"]
        assert isinstance(record["meter"], tuple) and isinstance(record["rhyme"], tuple)
        assert len(record["meter"]) == len(record["rhyme"]) == len(lines)
        assert all(re.fullmatch(r"[+-]+", pattern) for pattern in record["meter"])
        assert all(re.fullmatch(r"[A-N-]?", label) for label in record["rhyme"])
        # Only the sonnets in the public domain
        assert record["death"] is None or record["death"] < 1946
        if record["birth"] is not None and record["death"] is not None:
            assert record["birth"] < record["death"]


def test_records_order(records):
    keys = [(module.PERIODS.index(record["period"]), record["id"]) for record in records]
    assert keys == sorted(keys)
    assert records[0]["id"] == "001g_0001"
    assert records[0]["author"] == "Joseph Aragonés"
    assert records[0]["text"].split("\n")[0] == "Valencia insigne, patria venturosa,"
    assert records[-1]["id"] == "001t_0005"


def test_dialogue(records):
    dialogue = next(record for record in records if record["id"] == "235g_0492-1")
    first = dialogue["text"].split("\n")[0]
    assert first == "Imágenes confusas del deseo"
    assert dialogue["meter"][0] == "-+---+---+-"


def test_sonnets(records):
    # A sonnet of 14 lines, a sonnet with an estrambote or a sequence in one record
    lengths = Counter(len(record["meter"]) for record in records)
    assert lengths[14] == 4211
    assert lengths[17] == 13
    assert max(lengths) == 98
    assert sum(record["title"].startswith("Part of: ") for record in records) == 397


def test_rhyme_labels(records):
    labels = Counter(label for record in records for label in record["rhyme"])
    assert labels["-"] == 546
    assert labels[""] == 434
    assert sum(not any(record["rhyme"]) for record in records) == 20
    first = records[0]
    assert "".join(first["rhyme"]) == "ABBAABBACDECDE"
    assert first["meter"][0] == "-+-+-+---+-"


@pytest.mark.parametrize(
    ("author", "years"),
    [
        # The death that DISCO took from a later year of the biographical line
        ("José Echegaray", (1832, 1916)),
        # The year of a work that DISCO gave for both years of life
        ("Luis de Rivera", (None, None)),
        # "Siglos XVI-XVII Poeta nombrado por Juan de Castellanos, 1522-1607": the years
        # after a century are of other people
        ("Juan Ciberio de Vera", (None, None)),
        ("Jerónimo Gálvez", (None, None)),
        ("Petri Verdugo", (None, None)),
        # "1585 - Siglo XVII Caballero en 1613": a birth, the death unknown
        ("Diego Jiménez de Enciso", (1585, None)),
        # "18¿? - 1892", "Sevilla - Madrid,1651": a death, the birth unknown
        ("Antonio Alcalde Valladares", (None, 1892)),
        ("José García de Salcedo Coronel", (None, 1651)),
        # The years of the line, not the ones of VIAF (the musicologist of 1900-1978)
        ("José Antonio Calcaño", (1821, 1891)),
    ],
)
def test_years_of_life(records, author, years):
    record = next(record for record in records if record["author"] == author)
    assert (record["birth"], record["death"]) == years


def test_authors(dataset, records):
    authors = dataset.authors
    assert len(authors) == 1167
    assert authors.most_common(2) == [("Rubén Darío", 140), ("José Santos Chocano", 130)]
    # The Filipino poets have the name first, as the rest
    assert authors["José Rizal"] == 2
    assert not any(", " in author for author in authors)
    # With no dates in the line, the ones of VIAF put out of the public domain
    # (Luis Rodríguez Embil, 1879-1954; Manuel de Montoliu, 1877-1961)
    assert authors["Luis Rodríguez Embil"] == authors["Manuel de Montoliu"] == 0
    # The country named in the place of birth, "Puerto Príncipe. (Cuba)", not Haiti
    avellaneda = next(r for r in records if r["author"] == "Gertrudis Gómez de Avellaneda")
    assert avellaneda["country"] == "Cuba"


@pytest.mark.parametrize(
    ("filters", "expected"),
    [
        ({"period": "18th"}, 321),
        ({"period": "20th"}, 5),
        ({"author": "dario"}, 142),
        ({"author": "RUBÉN DARÍO"}, 140),
        ({"country": "mexico"}, 191),
        ({"country": "México"}, 191),
        ({"country": "filipinas"}, 26),
        ({"country": "cuba"}, 719),
        ({"gender": "F"}, 295),
        ({"period": "15th-17th", "gender": "F"}, 54),
        ({"author": "avellaneda", "gender": "F"}, 14),
        ({"author": "garcilaso"}, 0),
    ],
)
def test_filters(dataset, filters, expected):
    assert sum(1 for _ in dataset.get_records(**filters)) == expected


def test_length_filters(dataset):
    short = list(dataset.get_texts(max_len=400))
    assert len(short) == 15
    assert all(len(text) <= 400 for text in short)
    long = list(dataset.get_texts(min_len=2000))
    assert len(long) == 4
    assert all(len(text) >= 2000 for text in long)


@pytest.mark.parametrize("limit", [0, 1, 3])
def test_limit(dataset, limit):
    assert sum(1 for _ in dataset.get_texts(limit=limit)) == limit
    assert sum(1 for _ in dataset.get_records(period="18th", limit=limit)) == limit


@pytest.mark.parametrize(
    "bad_filter",
    [
        {"period": "21st"},
        {"gender": "X"},
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


def test_broken_line(tmp_path):
    dataset = SpanishSonnets(data_dir=tmp_path)
    folder = tmp_path / ROOT
    folder.mkdir()
    record = {"id": "1", "meter": ["-+"], "rhyme": ["A"]}
    folder.joinpath(module.FILENAME).write_text(
        json.dumps(record) + "\n{broken\n", encoding="utf-8"
    )
    records = iter(dataset)
    assert next(records)["meter"] == ("-+",)
    with pytest.raises(DataFileError, match=r"^Line 2 of .+ cannot be read"):
        next(records)
