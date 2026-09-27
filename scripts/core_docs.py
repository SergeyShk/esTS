"""
Fetching the documentation of anyTS into docs/core

The English pages include the named sections of the pages of anyTS, and the test of
the documentation checks the Spanish translations against them. The pages are taken
from the tag of the version of anyTS in uv.lock, so the site describes the very core
the library depends on; the version is kept in docs/core/VERSION, and the pages are
fetched again only when it changes. docs/core is not in git and not in the site.

Usage:
    uv run python scripts/core_docs.py [ANYTS_DIR]

With ANYTS_DIR the pages are copied from a local clone of anyTS as they are, to see
unreleased changes of the core in the documentation.
"""

import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "core"
REPOSITORY = "https://github.com/SergeyShk/anyTS"


def locked_version() -> str:
    """Version of anyTS in uv.lock"""
    lock = tomllib.loads((ROOT / "uv.lock").read_text(encoding="utf-8"))
    return next(package["version"] for package in lock["package"] if package["name"] == "anyts")


def copy_pages(source: Path, version: str) -> None:
    """Replacing docs/core with the pages of a clone of anyTS"""
    shutil.rmtree(TARGET, ignore_errors=True)
    shutil.copytree(source / "docs", TARGET)
    (TARGET / "VERSION").write_text(version + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) > 1:
        copy_pages(Path(sys.argv[1]), "local")
        print(f"docs/core: anyTS from {sys.argv[1]}")
        return
    version = locked_version()
    marker = TARGET / "VERSION"
    if marker.is_file() and marker.read_text(encoding="utf-8").strip() == version:
        return
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as clone:
        clone_command = ["git", "-c", "advice.detachedHead=false", "clone", "--quiet"]
        subprocess.run(
            [*clone_command, "--depth", "1", "--branch", version, REPOSITORY, clone],
            check=True,
        )
        copy_pages(Path(clone), version)
    print(f"docs/core: anyTS {version}")


if __name__ == "__main__":
    main()
