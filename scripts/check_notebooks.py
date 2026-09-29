"""
Comparing the text outputs of the notebooks of examples/ with the committed ones

The notebooks keep their outputs, and their prose quotes them; after a run with
`pytest --nbmake --overwrite examples` the script compares the text of every output
(the streams of a cell joined, the plain text and the HTML of the results, object
addresses left out) with the version of the file at HEAD and fails when a number
has moved, so that the prose is read again. Images are not compared: their bytes
depend on the platform.

Usage:
    uv run python scripts/check_notebooks.py [NOTEBOOK ...]
"""

import difflib
import re
import subprocess
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = re.compile(r" at 0x[0-9a-f]+")
TEXTS = ("text/plain", "text/html")


def outputs(notebook: nbformat.NotebookNode) -> list[list[str]]:
    """Text of the outputs of every code cell"""
    cells = []
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        texts, streams = [], {}
        for output in cell.get("outputs", []):
            if output.output_type == "stream":
                streams[output.name] = streams.get(output.name, "") + output.text
            elif output.output_type == "error":
                texts.append(f"{output.ename}: {output.evalue}")
            else:
                data = output.get("data", {})
                texts.extend(ADDRESS.sub("", data[kind]) for kind in TEXTS if kind in data)
        cells.append([*(f"{name}: {text}" for name, text in sorted(streams.items())), *texts])
    return cells


def main() -> int:
    paths = [Path(arg) for arg in sys.argv[1:]] or sorted((ROOT / "examples").glob("*.ipynb"))
    failed = 0
    for path in paths:
        relative = path.resolve().relative_to(ROOT).as_posix()
        committed = subprocess.run(
            ["git", "show", f"HEAD:{relative}"], cwd=ROOT, capture_output=True, text=True
        )
        if committed.returncode:
            print(f"{relative}: not committed")
            continue
        old = outputs(nbformat.reads(committed.stdout, as_version=4))
        new = outputs(nbformat.read(path, as_version=4))
        changed = [index for index, (a, b) in enumerate(zip(old, new, strict=False)) if a != b]
        if len(old) != len(new) or changed:
            failed += 1
            print(f"{relative}: the outputs of code cells {changed} changed")
            for index in changed:
                diff = difflib.unified_diff(
                    "\n".join(old[index]).splitlines(),
                    "\n".join(new[index]).splitlines(),
                    f"cell {index}, committed",
                    f"cell {index}, now",
                    lineterm="",
                )
                print("\n".join(diff))
        else:
            print(f"{relative}: the same outputs")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
