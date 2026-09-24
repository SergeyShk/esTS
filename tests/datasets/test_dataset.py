import pytest

from ests.datasets.dataset import Dataset, check_limit, length_filters, substring_filter
from ests.exceptions import ParameterError


class IncompleteDataset(Dataset):
    def __init__(self, name, meta):
        super().__init__(name, meta)


class MinimalDataset(Dataset):
    def __init__(self, name, meta=None):
        super().__init__(name, meta)

    def __iter__(self):
        return super().__iter__()

    def check_data(self):
        return super().check_data()

    def get_texts(self, *args):
        return super().get_texts()

    def get_records(self, *args):
        return super().get_records()

    def download(self, force=False):
        return super().download()


@pytest.fixture(scope="module")
def dataset():
    return MinimalDataset("test", {"a": "1", "b": "2"})


def test_repr(dataset):
    assert repr(dataset) == "Dataset('test')"


def test_info(dataset):
    assert dataset.info == {"name": "test", "a": "1", "b": "2"}
    assert list(dataset.info) == ["name", "a", "b"]
    assert MinimalDataset("empty").info == {"name": "empty"}


def test_abstract():
    with pytest.raises(TypeError):
        IncompleteDataset("", {})


@pytest.mark.parametrize(
    "name", ["__iter__", "check_data", "get_texts", "get_records", "download"]
)
def test_methods(dataset, name):
    with pytest.raises(NotImplementedError):
        getattr(dataset, name)()


def test_check_limit():
    check_limit(None)
    check_limit(0)
    with pytest.raises(ParameterError):
        check_limit(-1)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("galdos", True), ("GALDÓS", True), ("Pérez", True), ("perez galdos", True), ("Galdó", True)],
)
def test_substring_filter(value, expected):
    assert substring_filter("author", value)({"author": "Benito Pérez Galdós"}) is expected


def test_substring_filter_miss():
    predicate = substring_filter("country", "españa")
    assert predicate({"country": "España"})
    assert not predicate({"country": "Argentina"})
    # Characters of regular expressions are plain characters
    assert not substring_filter("title", ".")({"title": "Azul"})
    assert substring_filter("title", ".")({"title": "Azul..."})


def test_length_filters():
    records = [{"text": "a" * size} for size in (1, 5, 10)]
    filters = length_filters(2, 9)
    assert [len(r["text"]) for r in records if all(f(r) for f in filters)] == [5]
    assert length_filters(None, None) == []


@pytest.mark.parametrize(("min_len", "max_len"), [(0, None), (None, 0), (-1, None), (10, 5)])
def test_length_filters_errors(min_len, max_len):
    with pytest.raises(ParameterError):
        length_filters(min_len, max_len)
