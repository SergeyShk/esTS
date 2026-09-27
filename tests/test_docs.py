"""
Every English documentation page has a Spanish twin with the same headings, anchors and links

The English pages include the sections of the pages of anyTS (--8<-- "page:section"),
fetched into docs/core by scripts/core_docs.py; the Spanish twin carries the translation
of each with the mark <!-- core: page:section digest -->, the first seven characters of
the SHA-1 of the section it was translated from, so a changed section fails the test
until its translation is brought up to date
"""

import hashlib
import re
from pathlib import Path

import pytest

DOCS = Path(__file__).parent.parent / "docs"
CORE = DOCS / "core"
PAGES = sorted(
    path
    for path in DOCS.rglob("*.md")
    if not path.name.endswith(".es.md") and not path.is_relative_to(CORE)
)
INCLUDE = re.compile(r'^--8<-- "(?P<ref>[\w/.-]+\.md:[\w-]+)"$', re.MULTILINE)
MARK = re.compile(
    r"^<!-- core: (?P<ref>[\w/.-]+\.md:[\w-]+) (?P<digest>[0-9a-f]{7}) -->$", re.MULTILINE
)
SECTION = re.compile(
    r"^<!-- --8<-- \[start:(?P<name>[\w-]+)\] -->\n(?P<body>.*?)^<!-- --8<-- \[end:(?P=name)\] -->$",
    re.MULTILINE | re.DOTALL,
)


def anchors(text: str) -> set[str]:
    return set(re.findall(r"\{ #([\w-]+) \}", text))


def links(text: str) -> set[str]:
    return set(re.findall(r"\]\(([^)#\s]+\.md)", text))


def core_section(ref: str) -> str:
    page, name = ref.split(":")
    assert (CORE / page).is_file(), (
        f"missing {CORE / page}: run uv run python scripts/core_docs.py"
    )
    sections = {
        match["name"]: match["body"]
        for match in SECTION.finditer((CORE / page).read_text(encoding="utf-8"))
    }
    assert name in sections, f"no section {name} in the page {page} of anyTS"
    return sections[name]


def digest(ref: str) -> str:
    return hashlib.sha1(core_section(ref).encode()).hexdigest()[:7]


@pytest.mark.parametrize("page", PAGES, ids=[str(page.relative_to(DOCS)) for page in PAGES])
def test_spanish_page(page):
    spanish = page.with_name(page.name[:-3] + ".es.md")
    assert spanish.is_file(), f"missing Spanish version {spanish.relative_to(DOCS)}"
    english_text = page.read_text(encoding="utf-8")
    spanish_text = spanish.read_text(encoding="utf-8")
    english_text = INCLUDE.sub(lambda match: core_section(match["ref"]), english_text)
    assert anchors(spanish_text) == anchors(english_text)
    assert links(spanish_text) == links(english_text)
    assert english_text.count("\n## ") == spanish_text.count("\n## ")


@pytest.mark.parametrize("page", PAGES, ids=[str(page.relative_to(DOCS)) for page in PAGES])
def test_core_translations(page):
    spanish = page.with_name(page.name[:-3] + ".es.md")
    included = INCLUDE.findall(page.read_text(encoding="utf-8"))
    marks = [
        (match["ref"], match["digest"])
        for match in MARK.finditer(spanish.read_text(encoding="utf-8"))
    ]
    assert [ref for ref, _ in marks] == included, "the Spanish page translates other sections"
    for ref, translated in marks:
        assert translated == digest(ref), (
            f"{ref}: translated from {translated}, the core is {digest(ref)}"
        )
