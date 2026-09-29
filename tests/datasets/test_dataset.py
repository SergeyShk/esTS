import os
import subprocess
import sys

import anyts.datasets
import pytest

from ests.datasets import FreqDict, SpanishLiterature, SpanishSonnets
from ests.exceptions import DownloadError


def test_data_directory_of_the_environment(tmp_path):
    code = (
        "from ests.datasets import FreqDict, SpanishLiterature;"
        "print(FreqDict().data_dir);"
        "print(SpanishLiterature().data_dir)"
    )
    environment = {**os.environ, "ESTS_DATA_DIR": str(tmp_path)}
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=True, env=environment
    )
    assert result.stdout.splitlines() == [
        str((tmp_path / "dicts").resolve()),
        str((tmp_path / "texts").resolve()),
    ]


@pytest.mark.parametrize("dataset", [FreqDict, SpanishLiterature, SpanishSonnets])
def test_download_as_ests(dataset, tmp_path, monkeypatch):
    agents = []

    def urlopen(request, timeout=None):
        agents.append(request.get_header("User-agent"))
        raise OSError("offline")

    monkeypatch.setattr(anyts.datasets.urllib.request, "urlopen", urlopen)
    with pytest.raises(DownloadError):
        dataset(tmp_path).download(force=True)
    assert agents == ["esTS"]
