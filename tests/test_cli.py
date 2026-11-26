"""The command ests and the HTML report"""

import json
import re
import runpy
import sys
from importlib.metadata import entry_points

import pytest

from ests.cli import Command
from ests.datasets import FreqDict
from ests.report import STATS_CLASSES
from ests.utils import _annotate_text

TEXT = (
    "El gato duerme en la ventana. El perro ladra en el patio.\n\n"
    "Un pájaro canta en el jardín. ¡No, no canta!"
)


@pytest.fixture
def dictionary(freq_dict, monkeypatch):
    """The dictionary of the tests, which FreqDict() of the classes of the command reads"""
    monkeypatch.setattr(FreqDict.__init__, "__defaults__", (freq_dict.data_dir,))


@pytest.fixture
def text_file(tmp_path):
    path = tmp_path / "texto.txt"
    path.write_text(TEXT, encoding="utf-8")
    return str(path)


def finite(stats):
    return {
        key: None if isinstance(value, float) and value != value else value
        for key, value in stats.items()
    }


def test_json_is_the_flat_statistics(capsys, text_file, dictionary):
    """JSON is get_stats(flat=True) of every default class on the document of the text, nan null"""
    assert Command().run(["stats", "-f", "json", text_file]) == 0
    found = json.loads(capsys.readouterr().out)[text_file]
    assert list(found) == list(STATS_CLASSES)
    for name, cls in STATS_CLASSES.items():
        assert found[name] == finite(cls(_annotate_text(TEXT)).get_stats(flat=True)), name


def test_default_classes(capsys):
    """Without --stats the classes of the report are counted: the verse ones only by name"""
    command = Command()
    assert command.run(["stats", "--help"]) == 0
    help_text = " ".join(capsys.readouterr().out.split())
    assert f"{', '.join(STATS_CLASSES)} by default" in help_text
    assert list(command.stats_classes) == [*STATS_CLASSES, "verse"]
    assert command.run(["stats", "-p", "sentences", "-s", "verse"]) == 2
    assert "verse counts no sentences" in capsys.readouterr().err


def test_parts(capsys, text_file, dictionary):
    """Parts without --stats: the default classes that count them; verse by name"""
    assert Command().run(["stats", "-p", "sentences", "-f", "json", text_file]) == 0
    found = json.loads(capsys.readouterr().out)[text_file]
    assert list(found) == [name for name in STATS_CLASSES if name not in {"diversity", "cohesion"}]
    assert [record["n_words"] for record in found["basic"]] == [6, 6, 6, 3]
    argv = ["stats", "-p", "paragraphs", "-f", "json", "-s", "verse", text_file]
    assert Command().run(argv) == 0
    stanzas = json.loads(capsys.readouterr().out)[text_file]["verse"]
    assert [record["n_lines"] for record in stanzas] == [1, 1]


def test_report(tmp_path, text_file, dictionary):
    """The report opens without the network: no scripts, no external resources"""
    output = tmp_path / "informe.html"
    assert Command().run(["report", "-t", "Ejemplo", "-o", str(output), text_file]) == 0
    page = output.read_text(encoding="utf-8")
    assert page.startswith('<!DOCTYPE html>\n<html lang="en">')
    assert not re.search(r"<script|<link|<img|(src|href)=\"(https?:)?//", page)
    for heading in ("Basic statistics", "Sentences", "Highlighted text", "Plots"):
        assert f">{heading}<" in page
    assert "Water content (%)" in page


def test_report_of_verse(capsys, text_file, dictionary):
    """The verse statistics are in the report only by name, with their heading"""
    assert Command().run(["report", "-s", "basic", text_file]) == 0
    assert ">Verse statistics<" not in capsys.readouterr().out
    assert Command().run(["report", "-s", "basic,verse", text_file]) == 0
    assert ">Verse statistics<" in capsys.readouterr().out


def test_missing_dictionary(capsys, text_file, tmp_path, monkeypatch):
    """A class without the downloaded dictionary is left out with the command that downloads it"""
    monkeypatch.setattr(FreqDict.__init__, "__defaults__", (tmp_path,))
    assert Command().run(["stats", "-s", "basic,lexical", "-f", "json", text_file]) == 1
    out, err = capsys.readouterr()
    assert list(json.loads(out)[text_file]) == ["basic"]
    assert "lexical: The dataset freq_dict is not found" in err
    assert "ests download freq_dict" in err


def test_datasets():
    command = Command()
    assert list(command.datasets) == ["freq_dict"]
    assert command.run(["download", "freq"]) == 2


def test_version_and_file_errors(capsys, tmp_path):
    """--version names the versions of esTS and of the core"""
    assert Command().run(["--version"]) == 0
    assert re.fullmatch(r"ests \S+ \(anyTS \S+\)\n", capsys.readouterr().out)
    missing = str(tmp_path / "no.txt")
    assert Command().run(["stats", missing, str(tmp_path)]) == 1
    assert capsys.readouterr().err.splitlines() == [
        f"ests: {missing}: no such file or directory",
        f"ests: {tmp_path}: is a directory",
    ]


def test_entry_points(capsys, monkeypatch):
    """The command ests is an entry point of the package and python -m ests"""
    (script,) = entry_points(group="console_scripts", name="ests")
    assert script.value == "ests.cli:main"
    monkeypatch.setattr(sys, "argv", ["ests", "--help"])
    with pytest.raises(SystemExit) as exit_info:
        runpy.run_module("ests", run_name="__main__")
    assert exit_info.value.code == 0
    assert "Statistics of Spanish texts" in capsys.readouterr().out
