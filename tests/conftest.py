import shutil
from pathlib import Path

import pytest

from ests.datasets import FreqDict
from ests.datasets import freq_dict as freq_dict_module

FREQ_DICT_ARCHIVE = (
    Path(__file__).parents[1] / "ests" / "datasets" / "data" / freq_dict_module.ARCHIVE
)


@pytest.fixture(scope="session")
def freq_dict(tmp_path_factory):
    """Frequency dictionary extracted from the archive in the repository, without the network"""
    path = tmp_path_factory.mktemp("ests_dicts")
    shutil.copy(FREQ_DICT_ARCHIVE, path / freq_dict_module.ARCHIVE)
    dictionary = FreqDict(data_dir=path)
    dictionary.download()
    return dictionary
