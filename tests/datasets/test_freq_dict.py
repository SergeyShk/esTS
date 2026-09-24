import hashlib
import shutil
from collections import Counter
from pathlib import Path

import pytest

from ests.datasets import FreqDict
from ests.datasets import freq_dict as module
from ests.datasets.freq_dict import Entry, lemma_key, load_entries
from ests.exceptions import DatasetNotFoundError, ParameterError

BUNDLED_ARCHIVE = Path(__file__).parents[2] / "ests" / "datasets" / "data" / module.ARCHIVE


@pytest.fixture(scope="module")
def dictionary(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_dicts")
    shutil.copy(BUNDLED_ARCHIVE, path / module.ARCHIVE)
    dictionary = FreqDict(data_dir=path)
    # The archive is in the repository next to the code, the network is not needed
    dictionary.download()
    return dictionary


@pytest.fixture(scope="module")
def records(dictionary):
    return list(dictionary)


def test_info():
    dictionary = FreqDict(data_dir="/tmp")
    assert repr(dictionary) == "Dataset('freq_dict')"
    assert dictionary.info["license"] == "CC BY 3.0"
    assert "Google Books Ngram" in dictionary.info["citation"]


def test_not_downloaded(tmp_path):
    dictionary = FreqDict(data_dir=tmp_path)
    assert dictionary.filepath is None
    with pytest.raises(DatasetNotFoundError, match=r"^The dataset freq_dict is not found"):
        dictionary.check_data()
    with pytest.raises(DatasetNotFoundError):
        dictionary.lookup("gato")
    with pytest.raises(DatasetNotFoundError):
        list(dictionary.get_records())


def test_bundled_archive_checksum():
    with BUNDLED_ARCHIVE.open("rb") as file:
        assert hashlib.file_digest(file, "sha256").hexdigest() == module.ARCHIVE_SHA256


def test_download_extracts_again(tmp_path):
    shutil.copy(BUNDLED_ARCHIVE, tmp_path / module.ARCHIVE)
    dictionary = FreqDict(data_dir=tmp_path)
    dictionary.download()
    assert dictionary.filepath == str(
        tmp_path / f"{module.NAME}_v{module.VERSION}" / "freq_dict.tsv"
    )
    assert dictionary.ipm("gato") == 29.08
    Path(dictionary.filepath).unlink()
    dictionary.download()
    # A new download reads the dictionary anew
    assert load_entries.cache_info().currsize == 0
    assert dictionary.ipm("gato") == 29.08
    readme = Path(dictionary.filepath).with_name("README.txt").read_text(encoding="utf-8")
    assert "Creative Commons Attribution 3.0" in readme


def test_lookup(dictionary):
    entry = dictionary.lookup("gato")
    assert entry == Entry("gato", ("NOUN", "ADJ"), 29.08, 40, 95, 232841)
    assert dictionary.lookup("Gato") == entry
    assert dictionary.lookup("gatx") is None
    assert dictionary.lookup("madrid").pos == ("PROPN",)
    assert dictionary.ipm("perro") == 62.57
    assert dictionary.ipm("computadora") == 0.0
    assert dictionary.ipm("computador") == 20.07
    assert "Gato" in dictionary
    assert "gatx" not in dictionary
    assert 5 not in dictionary


def test_entries(dictionary, records):
    assert len(dictionary) == 83785
    assert dictionary.min_ipm == 0.1
    rows = [record for record in records if record["lemma"] == "ser"]
    entry = dictionary.lookup("ser")
    assert entry.pos == tuple(record["pos"] for record in rows)
    assert entry.ipm == round(sum(record["ipm"] for record in rows), 2)
    assert entry.docs == max(record["docs"] for record in rows)


def test_records(records):
    assert len(records) == 109178
    assert records[0] == {
        "lemma": "el",
        "pos": "DET",
        "ipm": 96989.39,
        "range": 40,
        "dispersion": 99,
        "docs": 905361,
    }
    ipms = [record["ipm"] for record in records]
    assert ipms == sorted(ipms, reverse=True)
    assert set(Counter(record["pos"] for record in records)) == set(module.POS_TAGS)
    for record in records:
        assert record["lemma"] == record["lemma"].lower()
        assert record["ipm"] >= 0.1
        assert 5 <= record["range"] <= 40
        assert 0 <= record["dispersion"] <= 100
        assert record["docs"] > 0


def test_get_records(dictionary):
    assert [record["lemma"] for record in dictionary.get_records(pos="NOUN", limit=3)] == [
        "año",
        "parte",
        "vez",
    ]
    verbs = list(dictionary.get_records(pos="VERB", min_ipm=2000))
    assert [record["lemma"] for record in verbs][:3] == ["ser", "haber", "estar"]
    assert all(record["ipm"] >= 2000 for record in verbs)
    assert list(dictionary.get_texts(pos="ADJ", limit=3)) == ["primero", "nuevo", "social"]
    assert list(dictionary.get_texts(limit=0)) == []


@pytest.mark.parametrize("bad_filter", [{"pos": "PART"}, {"pos": "noun"}, {"limit": -1}])
def test_bad_filters(dictionary, bad_filter):
    with pytest.raises(ParameterError):
        list(dictionary.get_records(**bad_filter))


@pytest.mark.parametrize(
    ("word", "key"),
    [
        ("usted", "tú"),
        ("fue", "ser"),
        ("Esta", "este"),
        ("sé", "saber"),
        ("Miró", "mirar"),
        ("Déjame", "dejar"),
        ("computadoras", "computador"),
    ],
)
def test_lemma_key(dictionary, word, key):
    # These lemmas differ between the versions of simplemma: when the lock moves
    # to a version that changes them, the dictionary has to be built anew
    assert lemma_key(word) == key
    assert key in dictionary


def test_lemma_key_proper(dictionary):
    assert lemma_key("París") == "parir"
    assert lemma_key("París", proper=True) == "parís"
    assert dictionary.lookup(lemma_key("París", proper=True)).pos == ("PROPN",)
