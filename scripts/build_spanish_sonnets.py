"""
Building the archive of the SpanishSonnets dataset from the Diachronic Spanish Sonnet Corpus

DISCO 5.0 (https://github.com/pruizf/disco, CC BY 4.0) is downloaded at a pinned
commit and verified against its SHA-256 checksum. Every sonnet of the TEI files
of one sonnet per file gives a record: the identifier, the period of the
subcorpus, the author, the title, the country and the gender of the author, the
years of life, the lines with the stanzas separated by a blank line, and the
metrical pattern and the label of the rhyme of every line, as DISCO annotated
them.

The years of life are read from the biographical line of the source (raw in
author_metadata.tsv: "Maracaibo (Venezuela). 1819 - Madrid. 1860 ..."), where
DISCO sometimes took a later year of the line for the death (the Obras
Completas of Baralt published in 1960, the Nobel prize of Echegaray in 1904)
and missed a birth or a death given alone ("1585 - Siglo XVII", "18¿? - 1892");
the years after a century are of other people or events ("Siglos XVI-XVII Poeta
nombrado por Juan de Castellanos, 1522-1607"). Without a match the years of the
table are taken, unless they are one year for both (the year of a work of Luis
de Rivera). The country of birth is the one named in the place of birth of the
line, where it names one: DISCO took Haiti for "Puerto Príncipe. (Cuba)" of
Gómez de Avellaneda and Spain for three places of America. The names of the
Filipino poets, written with the surname first ("Rizal, José"), are written
with the name first, as the rest. The speakers of the dialogues
(<name>[Car]</name>) and the calls of the footnotes at the end of a line
("diestra.7") are left out of the lines: the metrical patterns of DISCO count
neither. Only the sonnets in the public domain are kept: of the authors who died
before 1946, of the authors of the 15th-18th centuries with no known death, of
the authors of the 19th-century anthology born before 1866 with no known death
and of the ones with no dates, unless the dates of VIAF that DISCO matched with
high confidence give a death in 1946 or later or a birth in 1866 or later with
no death (Luis Rodríguez Embil, 1879-1954, "Cuba. Siglo XIX").

Usage:
    uv run python scripts/build_spanish_sonnets.py CACHE_DIR OUTPUT_DIR

The archive is written deterministically (sorted names, zero times and owners),
so a rebuild from the same source gives the same SHA-256. A published archive is
never replaced: a new build raises VERSION in the module of the dataset.
"""

import csv
import io
import json
import re
import sys
import tarfile
import urllib.request
import xml.etree.ElementTree as ET
from hashlib import sha256
from pathlib import Path

from ests.datasets.spanish_sonnets import FILENAME, NAME, PERIODS, VERSION

ROOT = f"{NAME}_v{VERSION}"
COMMIT = "b626fefad22b2c8a0ecec8903cb6a465ebadb541"
URL = f"https://codeload.github.com/pruizf/disco/tar.gz/{COMMIT}"
SOURCE_SHA256 = "6afaa3a9fe0b7a9a7aca84cac464c1481a1a7316af05971e01221f040b57aae5"
TEI = "{http://www.tei-c.org/ns/1.0}"
# Period of the subcorpus by the letter at the end of the identifier of an author
PERIOD_LETTERS = {"g": "15th-17th", "e": "18th", "n": "19th", "t": "20th"}
# "1819 - Madrid. 1860": the first two years of the biographical line joined by a dash
LIFE = re.compile(r"(\d{4})\??\s*(?:o \d{4}\s*)?-\s*[^\d]{0,80}?(\d{4})")
# "1585 - Siglo XVII": a birth, the death unknown
BIRTH = re.compile(r"(\d{4})\??\s*-\s*$")
# "18¿? - 1892", "Sevilla - Madrid,1651": a death, the birth unknown
DEATH = re.compile(r"-\s*[^\d]{0,80}?(\d{4})")
# The years after a century in the line are of other people or events: "Siglos XVI-XVII
# Poeta nombrado por Juan de Castellanos, 1522-1607", "1585 - Siglo XVII Caballero en 1613"
CENTURY = re.compile(r"[Ss]iglo")
YEAR = re.compile(r"\d{4}")
# The call of a footnote left at the end of a line: "potente diestra.7"
NOTE_CALL = re.compile(r"(?<=[.,;:!?])\d+$")
# The public domain in Spain: 80 years after the death of the author
PUBLIC_DOMAIN_DEATH = 1946
# The latest birth of an author of the 19th-century anthology with no known death
PUBLIC_DOMAIN_BIRTH = 1866
README = """\
Spanish sonnets of the Diachronic Spanish Sonnet Corpus (DISCO)

Source: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., Calvo Tello J.
Diachronic Spanish Sonnet Corpus (DISCO), version 5.0. Madrid: UNED, 2017-2023.
https://github.com/pruizf/disco (commit {commit}).
Article: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., González-Blanco E.
The Diachronic Spanish Sonnet Corpus: TEI and linked open data encoding, data
distribution, and metrical findings. Digital Scholarship in the Humanities 36
(Supplement 1), 2021, i68-i80. https://doi.org/10.1093/llc/fqaa035

Licence: DISCO is distributed under the Creative Commons Attribution 4.0
International License (https://creativecommons.org/licenses/by/4.0/), and so
is this dataset.

Changes: the TEI files of one sonnet per file are converted to JSON Lines, one
sonnet per line, with the fields id, period, author, title, country, gender,
birth, death, text, meter and rhyme. The metrical patterns (ADSO, Jumper) and
the rhyme labels (RhymeTagger) are the automatic annotation of DISCO. The years
of life are read from the biographical line of the source where DISCO took a
later year of it for the death or missed a birth or a death given alone, and
without the years after a century, which are of other people or events; one
year of a work given for both years of life is left out. The country of birth
is the one named in the place of birth of that line, where it names one (Cuba
and not Haiti for Gómez de Avellaneda). The names of the authors written with
the surname first ("Rizal, José") are written with the name first, as the rest.
The speakers of the dialogues ([Car], [POETA]) and the calls of the footnotes
at the end of a line are left out of the lines, as out of their metrical
patterns. Only the sonnets in the public domain are kept: {kept} of {total}; the
{dropped} left out are the ones of the authors who died in 1946 or later, of the
20th-century authors with no known death, of the 19th-century authors born in
1866 or later with no known death and of the 19th-century authors with no dates
whom the dates of VIAF matched by DISCO with high confidence put after 1946.
"""


def fetch(cache: Path) -> Path:
    """Archive of DISCO at the pinned commit, downloaded once and verified"""
    cache.mkdir(parents=True, exist_ok=True)
    path = cache / f"disco-{COMMIT}.tar.gz"
    if not path.is_file():
        with urllib.request.urlopen(URL, timeout=120) as response:
            path.write_bytes(response.read())
    if sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        path.unlink()
        raise SystemExit(f"{URL} failed the checksum, run the script again")
    return path


def _year(value: str) -> int | None:
    return int(value) if YEAR.fullmatch(value.strip()) else None


def life(row: dict[str, str]) -> tuple[int | None, int | None]:
    """Years of birth and of death of an author, the biographical line first"""
    line = CENTURY.split(row["raw"][:120], maxsplit=1)[0]
    if match := LIFE.search(line):
        return int(match.group(1)), int(match.group(2))
    if match := BIRTH.search(line):
        return int(match.group(1)), None
    if match := DEATH.search(line):
        return None, int(match.group(1))
    birth, death = _year(row["birth"]), _year(row["death"])
    # One year of the line for both is the year of a work ("España. 1612 De Sagradas
    # Poesías (1612)"), not the years of life
    if birth is not None and death is not None and birth >= death:
        return None, None
    return birth, death


def country(row: dict[str, str], countries: set[str]) -> str:
    """Country of birth, the one named in the place of birth of the biographical line first"""
    place = re.split(r"\d{4}|[Ss]iglo", row["raw"], maxsplit=1)[0]
    named = [name for name in countries if re.search(rf"\b{name}\b", place)]
    return named[0] if len(named) == 1 else row["country-birth"]


def is_late_by_viaf(row: dict[str, str]) -> bool:
    """Whether the dates of VIAF matched with high confidence put an author out of the public domain"""
    if row["vf_validation"] != "high":
        return False
    birth, death = _year(row["vf_bi"]), _year(row["vf_de"])
    if death is not None:
        return death >= PUBLIC_DOMAIN_DEATH
    return birth is not None and birth >= PUBLIC_DOMAIN_BIRTH


def is_public_domain(period: str, birth: int | None, death: int | None, late: bool) -> bool:
    """Whether the sonnets of an author are in the public domain"""
    if death is not None:
        return death < PUBLIC_DOMAIN_DEATH
    if period in ("15th-17th", "18th"):
        return True
    if period == "19th":
        # With no dates in the line VIAF can only drop an author: its matches are not always
        # right (the musicologist José Antonio Calcaño, 1900-1978, for the poet of 1821-1891;
        # a birth in 1928 for Guillermo Rances, born in 1854 by the line)
        return not late if birth is None else birth < PUBLIC_DOMAIN_BIRTH
    return False


def _text(element: ET.Element) -> str:
    return " ".join("".join(element.itertext()).split())


def _line(element: ET.Element) -> str:
    """Text of a line without the speakers of a dialogue ([Car], [POETA]) and the footnote calls"""
    parts = [element.text or ""]
    for child in element:
        if child.tag != f"{TEI}name":
            parts.append("".join(child.itertext()))
        parts.append(child.tail or "")
    return NOTE_CALL.sub("", " ".join("".join(parts).split()))


def sonnet(root: ET.Element) -> tuple[str, str, list[str], list[str]]:
    """Title, text, metrical patterns and rhyme labels of a TEI sonnet"""
    body = root.find(f".//{TEI}body")
    if body is None:
        raise ValueError("The TEI file has no body")
    head = body.find(f".//{TEI}head")
    title = _text(head) if head is not None else ""
    if not title:
        heading = root.find(f".//{TEI}titleStmt/{TEI}title")
        title = _text(heading) if heading is not None else ""
    stanzas, meter, rhyme = [], [], []
    for stanza in body.iter(f"{TEI}lg"):
        lines = stanza.findall(f"{TEI}l")
        if not lines:
            continue
        stanzas.append("\n".join(_line(line) for line in lines))
        meter += [line.get("met", "") for line in lines]
        rhyme += [line.get("rhyme", "") for line in lines]
    return title, "\n\n".join(stanzas), meter, rhyme


def main(cache: Path, output: Path) -> None:
    source = fetch(cache)
    records = []
    total = 0
    with tarfile.open(source, mode="r:gz") as tar:
        members = {member.name.split("/", 1)[1]: member for member in tar if "/" in member.name}

        def read(name: str) -> bytes:
            file = tar.extractfile(members[name])
            if file is None:
                raise ValueError(f"{name} is not a file")
            return file.read()

        authors = {
            row["aid"]: row
            for row in csv.DictReader(
                io.StringIO(read("author_metadata.tsv").decode("utf-8")), delimiter="\t"
            )
        }
        countries = {row["country-birth"] for row in authors.values()} - {""}
        for name in sorted(members):
            match = re.fullmatch(r"tei/([^/]+)/per-sonnet/disco([\w-]+?)\.xml", name)
            if not match:
                continue
            total += 1
            identifier = match.group(2)
            author_id = identifier.split("_")[0]
            period = PERIOD_LETTERS[author_id[-1]]
            if match.group(1) != period:
                raise ValueError(f"{name} is not in the folder of its period")
            row = authors[author_id]
            birth, death = life(row)
            if not is_public_domain(period, birth, death, is_late_by_viaf(row)):
                continue
            root = ET.fromstring(read(name))
            title, text, meter, rhyme = sonnet(root)
            source_name = root.find(f".//{TEI}persName[@type='source']")
            author = _text(source_name) if source_name is not None else row["author"]
            # The Filipino poets are written "Rizal, José": the name goes first as for the rest
            surname, _, first_name = author.partition(", ")
            author = f"{first_name} {surname}" if first_name else author
            records.append(
                (
                    (PERIODS.index(period), identifier),
                    {
                        "id": identifier,
                        "period": period,
                        "author": author,
                        "title": title,
                        "country": country(row, countries),
                        "gender": row["gender"],
                        "birth": birth,
                        "death": death,
                        "text": text,
                        "meter": meter,
                        "rhyme": rhyme,
                    },
                )
            )
    lines = [
        json.dumps(record, ensure_ascii=False)
        for _, record in sorted(records, key=lambda item: item[0])
    ]
    files = {
        f"{ROOT}/{FILENAME}": ("\n".join(lines) + "\n").encode("utf-8"),
        f"{ROOT}/README.txt": README.format(
            commit=COMMIT, kept=len(records), total=total, dropped=total - len(records)
        ).encode("utf-8"),
    }
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{ROOT}.tar.xz"
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:xz", format=tarfile.PAX_FORMAT) as tar:
        for member in sorted(files):
            data = files[member]
            info = tarfile.TarInfo(member)
            info.size, info.mtime, info.mode = len(data), 0, 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    archive.write_bytes(buffer.getvalue())
    print(f"{archive}: {len(records)} of {total} sonnets, {archive.stat().st_size / 1e6:.2f} MB")
    print("sha256", sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
