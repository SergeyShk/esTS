import re

import ests


def test_version():
    assert re.fullmatch(r"\d+\.\d+\.\d+(\.dev\d+)?", ests.__version__)
    assert ests.__version__ != "0.0.0"


def test_metadata():
    assert "Spanish" in ests.__description__
    assert "__version__" in ests.__all__
    assert ests.__all__ == sorted(ests.__all__)


def test_version_fallback(monkeypatch):
    import importlib
    import importlib.metadata

    def missing(name):
        raise importlib.metadata.PackageNotFoundError(name)

    monkeypatch.setattr(importlib.metadata, "version", missing)
    try:
        assert importlib.reload(ests).__version__ == "0.0.0"
    finally:
        monkeypatch.undo()
        importlib.reload(ests)
    assert ests.__version__ != "0.0.0"
