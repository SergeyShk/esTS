"""
Checking the scansion of VerseStats on the metrical annotation checked by hand

The source is the Corpus of Spanish Golden-Age Sonnets of Navarro-Colorado
(https://github.com/bncolorado/CorpusSonetosSigloDeOro, commit 092a5fe of
2026-02-19; the annotation is CC BY-NC 4.0, the texts are of the Biblioteca Virtual
Miguel de Cervantes), cloned locally: the sonnets whose annotation is not the
automatic one. Every line has the pattern of its metrical syllables of + (stressed)
and - (unstressed), the convention of VerseStats.patterns; of a line with readings
(app) the lemma (lem) is read. The script counts the lines of the same number of
syllables, of the same pattern and of a stressed tenth syllable on both sides, and
the metrical syllables of the same stress in the lines of equal length; the lines
of another length are printed.

Usage:
    uv run python scripts/check_scansion.py CORPUS_DIR
"""

import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from ests import VerseStats

TEI = "{http://www.tei-c.org/ns/1.0}"


def line_text(element: ET.Element) -> str:
    """Text of a line without the variant readings (rdg) of its apparatus"""
    parts = [element.text or ""]
    for child in element:
        if child.tag != f"{TEI}rdg":
            parts.append(line_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def checked_sonnets(root: Path):
    """The stanzas of (line, pattern) of every sonnet whose annotation is checked by hand"""
    for path in sorted(root.rglob("*.xml")):
        tree = ET.parse(path)
        if any("automatically" in (p.text or "") for p in tree.iter(f"{TEI}p")):
            continue
        stanzas = [
            [(line_text(line).strip(), line.get("met")) for line in lg.iter(f"{TEI}l")]
            for lg in tree.iter(f"{TEI}lg")
        ]
        yield path, stanzas


def main(root: Path) -> None:
    counts: Counter[str] = Counter()
    for path, stanzas in checked_sonnets(root):
        text = "\n\n".join("\n".join(line for line, _ in stanza) for stanza in stanzas)
        gold = [(line, met) for stanza in stanzas for line, met in stanza]
        counts["sonnets"] += 1
        for (line, met), pattern in zip(gold, VerseStats(text).patterns, strict=True):
            counts["lines"] += 1
            counts["same_length"] += len(met) == len(pattern)
            counts["same_pattern"] += met == pattern
            if len(met) >= 10:
                counts["tenth"] += met[9] == "+"
                counts["same_tenth"] += met[9] == "+" and pattern[9:10] == "+"
            if len(met) == len(pattern):
                counts["syllables"] += len(met)
                counts["same_syllables"] += sum(a == b for a, b in zip(met, pattern, strict=True))
            else:
                print(f"{path.parent.name}: {line} | {met} | {pattern}")
    lines = counts["lines"]
    print(
        f"{counts['sonnets']} sonnets, {lines} lines: syllables {counts['same_length'] / lines:.2%}, "
        f"pattern {counts['same_pattern'] / lines:.2%}, "
        f"tenth {counts['same_tenth'] / counts['tenth']:.2%}, "
        "metrical syllables of the lines of equal length "
        f"{counts['same_syllables'] / counts['syllables']:.2%}"
    )


if __name__ == "__main__":
    main(Path(sys.argv[1]))
