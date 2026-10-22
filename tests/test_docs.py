"""
Every English documentation page has a Spanish twin with the same headings, anchors and links

The English pages include the sections of the pages of anyTS (--8<-- "page:section"),
fetched into docs/core by scripts/core_docs.py; the Spanish twin carries the translation
of each with the mark <!-- core: page:section digest -->, the first seven characters of
the SHA-1 of the section it was translated from, so a changed section fails the test
until its translation is brought up to date
"""

import hashlib
import importlib
import inspect
import pkgutil
import re
from pathlib import Path

import anyts
import anyts.constants
import pytest

import ests
import ests.constants

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


# A signature block: ``` {.python .signature} with one call on one line
SIGNATURE = re.compile(r"^``` \{\.python \.signature\}\n(\w+)\((.*)\)\n```$", re.MULTILINE)
MODULES = [
    importlib.import_module(info.name)
    for info in pkgutil.walk_packages(ests.__path__, "ests.")
    if not info.name.endswith("__main__")
]
CORE_MODULES = [
    importlib.import_module(info.name)
    for info in pkgutil.walk_packages(anyts.__path__, "anyts.")
]
CONSTANTS = [ests.constants, anyts.constants, *MODULES, *CORE_MODULES]
# Pages whose name is not that of their module
PAGE_MODULES = {
    "extractors": "ests.extractors",
    "datasets/freqdict": "ests.datasets.freq_dict",
    "datasets/spanishliterature": "ests.datasets.spanish_literature",
    "datasets/spanishsonnets": "ests.datasets.spanish_sonnets",
}


def default_text(value: object) -> str:
    """A default as a signature block writes it: a literal, a name or a constant"""
    if value is None or isinstance(value, bool | int | float | str | tuple):
        return repr(value)
    if callable(value) and hasattr(value, "__qualname__"):
        return value.__qualname__
    for module in CONSTANTS:
        for name, constant in vars(module).items():
            if name.isupper() and constant is value:
                return name
    return repr(value)


def signature_text(target: object) -> str:
    """The parameters of a callable as a signature block writes them"""
    parts = []
    keyword_only = False
    for param in inspect.signature(target).parameters.values():
        if param.kind is param.KEYWORD_ONLY and not keyword_only:
            parts.append("*")
            keyword_only = True
        if param.kind is param.VAR_POSITIONAL:
            parts.append(f"*{param.name}")
            keyword_only = True
        elif param.kind is param.VAR_KEYWORD:
            parts.append(f"**{param.name}")
        elif param.default is param.empty:
            parts.append(param.name)
        else:
            parts.append(f"{param.name}={default_text(param.default)}")
    return ", ".join(parts)


def page_target(page: Path, name: str) -> object:
    """The callable of a page: from the module of the page or the only one of the name in esTS"""
    key = page.relative_to(DOCS).with_suffix("").as_posix().removesuffix(".es")
    module_name = PAGE_MODULES.get(key) or PAGE_MODULES.get(key.split("/")[0])
    if module_name is None:
        module_name = "ests." + key.removeprefix("stats/").removesuffix("_funcs").replace("/", ".")
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        module = None
    if module is not None and name in vars(module):
        return vars(module)[name]
    targets = {id(vars(m)[name]): vars(m)[name] for m in MODULES if name in vars(m)}
    return next(iter(targets.values())) if len(targets) == 1 else None


def test_signatures_match_the_code():
    found = 0
    for page in sorted(path for path in DOCS.rglob("*.md") if not path.is_relative_to(CORE)):
        text = INCLUDE.sub(
            lambda match: core_section(match["ref"]), page.read_text(encoding="utf-8")
        )
        for name, written in SIGNATURE.findall(text):
            target = page_target(page, name)
            where = page.relative_to(DOCS)
            assert target is not None, f"{where}: no {name} in esTS"
            assert written == signature_text(target), (
                f"{where}: {name}({written}) differs from the code"
            )
            found += 1
    assert found
