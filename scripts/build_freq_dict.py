"""
Building the frequency dictionary of Spanish lemmas from Google Books Ngram

The source is the Spanish corpus of Google Books Ngram, version 20200217, 1-grams
(three files, 3.2 GB), licensed under CC BY 3.0. Only the forms tagged with a part
of speech are counted (the untagged lines repeat their sums), only the years
FIRST_YEAR-LAST_YEAR, and only the forms of letters: numbers, punctuation and the
tag X go. The forms go to their keys by lemma_key, the function by which the library
looks a word up: lower case, then the lemma by simplemma.

For every lemma and part of speech the dictionary gives:
    ipm - occurrences per million words of the period (the words are all the
        counted forms);
    range - the number of years of the period in which the lemma occurs;
    dispersion - Juilland's D over the years, times 100 (the relative frequency
        of every year, so that the unequal years weigh the same);
    docs - the number of books with the most widespread form of the lemma (a
        lower bound: a book with several forms is not counted twice).
A noun form that is written with a capital letter in at least PROPER_SHARE of its
occurrences is a proper noun (PROPN) as a whole, the lower-case occurrences
included, since the case variants are merged in the first pass: the tagset of
Google has no such tag.

Usage:
    uv run python scripts/build_freq_dict.py NGRAMS_DIR OUTPUT_DIR

NGRAMS_DIR holds the files 1-0000N-of-00003.gz of
http://storage.googleapis.com/books/ngrams/books/20200217/spa/; the counts of the
forms are cached there in forms.tsv.gz after the first pass. The archive of the
dictionary and the list of the most frequent lemmas go to OUTPUT_DIR; the list goes on to
ests/resources, where LexicalStats reads it.
"""

import gzip
import io
import re
import sys
import tarfile
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

import numpy as np
import simplemma

from ests.datasets.freq_dict import (
    FILENAME,
    NAME,
    SIMPLEMMA_VERSION,
    VERSION,
    WORD_PATTERN,
    lemma_key,
)

FIRST_YEAR, LAST_YEAR = 1980, 2019
N_YEARS = LAST_YEAR - FIRST_YEAR + 1
FILES = [f"1-0000{number}-of-00003.gz" for number in range(3)]
FORMS = "forms.tsv.gz"
# Tags of the words (the Spanish corpus has no PRT); NUM, X and the punctuation . go
TAGS = {
    "NOUN": "NOUN",
    "VERB": "VERB",
    "ADJ": "ADJ",
    "ADV": "ADV",
    "PRON": "PRON",
    "DET": "DET",
    "ADP": "ADP",
    "CONJ": "CONJ",
}
# A form below this count in the period is not kept: it adds less than 0.002 ipm
MIN_FORM_COUNT = 100
PROPER_SHARE = 0.9
# Rows below this frequency or found in fewer years (the spikes of the recognition of a
# single batch of books) are left out
MIN_IPM = 0.1
MIN_RANGE = 5
ROOT = f"{NAME}_v{VERSION}"
TOP_FILE = "google_books_top10000.txt"
TOP_SIZE = 10_000
SPANISH_LETTERS = frozenset("aeouyáéó")
ROMAN = re.compile(r"m{0,3}(?:c[md]|d?c{0,3})(?:x[cl]|l?x{0,3})(?:i[xv]|v?i{0,3})")
README = """Frequency dictionary of Spanish lemmas

Derived from the Spanish corpus of Google Books Ngram, version 20200217, 1-grams
(https://storage.googleapis.com/books/ngrams/books/datasetsv3.html), licensed under
the Creative Commons Attribution 3.0 Unported License
(https://creativecommons.org/licenses/by/3.0/).

Changes: the forms tagged with a part of speech of the years 1980-2019 were
lower-cased, lemmatized by simplemma {simplemma} and summed by lemma and part of
speech; nouns written with a capital letter in 90% of their occurrences are proper
nouns (PROPN) and keep their forms.
{size} words; {rows} rows with at least 0.1 occurrences per million words found in
at least 5 of the 40 years.

Columns: lemma, pos, ipm (occurrences per million words), range (years with the
lemma), dispersion (Juilland's D over the years, times 100), docs (books with the
most widespread form of the lemma).
"""


def count_file(path: Path) -> tuple[dict[tuple[str, str], list[int]], np.ndarray]:
    """
    Counts of the forms of one file

    Returns:
        forms: (form, tag) - [count, books, capitals, count of every year...]
        totals: number of words in every year
    """
    forms: dict[tuple[str, str], list[int]] = {}
    totals = np.zeros(N_YEARS, dtype=np.int64)
    with gzip.open(path, "rt", encoding="utf-8") as file:
        for line in file:
            ngram, _, rest = line.partition("\t")
            word, sep, tag = ngram.rpartition("_")
            if not sep or tag not in TAGS:
                continue
            form = word.lower()
            if not WORD_PATTERN.fullmatch(form):
                continue
            years = [0] * N_YEARS
            books = 0
            # The years go in order, so the period is read from the end
            for field in reversed(rest.rstrip("\n").split("\t")):
                year, match, volumes = field.split(",")
                index = int(year) - FIRST_YEAR
                if index < 0:
                    break
                if index < N_YEARS:
                    years[index] = int(match)
                    books += int(volumes)
            count = sum(years)
            if not count:
                continue
            totals += years
            if count < MIN_FORM_COUNT:
                continue
            key = (form, TAGS[tag])
            capitals = count if word[0].isupper() else 0
            stored = forms.get(key)
            if stored is None:
                forms[key] = [count, books, capitals, *years]
            else:
                stored[0] += count
                stored[1] = max(stored[1], books)
                stored[2] += capitals
                for index, value in enumerate(years, 3):
                    stored[index] += value
    return forms, totals


def count_forms(ngrams: Path) -> Path:
    """Counts of the forms of all the files, cached in FORMS"""
    cache = ngrams / FORMS
    if cache.is_file():
        return cache
    forms: dict[tuple[str, str], list[int]] = {}
    totals = np.zeros(N_YEARS, dtype=np.int64)
    with ProcessPoolExecutor(len(FILES)) as pool:
        for part, part_totals in pool.map(count_file, [ngrams / name for name in FILES]):
            totals += part_totals
            for key, values in part.items():
                stored = forms.get(key)
                if stored is None:
                    forms[key] = values
                else:
                    stored[0] += values[0]
                    stored[1] = max(stored[1], values[1])
                    for index in range(2, len(values)):
                        stored[index] += values[index]
    with gzip.open(cache, "wt", encoding="utf-8") as file:
        file.write("\t".join(["#total", "", *map(str, totals)]) + "\n")
        for (form, tag), values in sorted(forms.items()):
            file.write("\t".join([form, tag, *map(str, values)]) + "\n")
    return cache


def aggregate(cache: Path) -> tuple[np.ndarray, dict[tuple[str, str], list]]:
    """
    Counts by lemma and part of speech

    Returns:
        totals: number of words in every year
        lemmas: (lemma, tag) - [count, books, count of every year]
    """
    lemmas: dict[tuple[str, str], list] = {}
    with gzip.open(cache, "rt", encoding="utf-8") as file:
        totals = np.array(file.readline().rstrip("\n").split("\t")[2:], dtype=np.int64)
        for line in file:
            form, tag, count, books, capitals, *years = line.rstrip("\n").split("\t")
            # A proper noun keeps its form: simplemma would read Morales as moral
            proper = tag == "NOUN" and int(capitals) >= PROPER_SHARE * int(count)
            key = (lemma_key(form, proper), "PROPN" if proper else tag)
            counts = np.array(years, dtype=np.int64)
            stored = lemmas.get(key)
            if stored is None:
                lemmas[key] = [int(count), int(books), counts]
            else:
                stored[0] += int(count)
                stored[1] = max(stored[1], int(books))
                stored[2] = stored[2] + counts
    return totals, lemmas


def juilland(counts: np.ndarray, totals: np.ndarray) -> float:
    """Juilland's D over the years by the relative frequencies, from 0 to 1"""
    shares = counts / totals
    return max(0.0, 1 - shares.std() / shares.mean() / (len(shares) - 1) ** 0.5)


def build_rows(totals: np.ndarray, lemmas: dict[tuple[str, str], list]) -> list[tuple]:
    """Rows of the dictionary above MIN_IPM and MIN_RANGE, by frequency"""
    size = totals.sum()
    rows = []
    for (lemma, tag), (count, books, counts) in lemmas.items():
        ipm = count / size * 1_000_000
        years = int((counts > 0).sum())
        if ipm < MIN_IPM or years < MIN_RANGE:
            continue
        dispersion = round(100 * juilland(counts, totals))
        rows.append((lemma, tag, round(ipm, 2), years, dispersion, books))
    rows.sort(key=lambda row: (-row[2], row[0], row[1]))
    return rows


def is_vocabulary(lemma: str) -> bool:
    """
    Whether a lemma belongs to the list of the most frequent lemmas

    Description:
        A letter is a word only if it is one in Spanish (a, e, o, u, y and the
        accented á, é, ó of the older spelling), the others are the letters of
        enumerations and initials. A lemma of two letters and a Roman numeral go
        unless simplemma knows them as words (su, ya, mi, vi): the others are
        abbreviations (pp, ss, vs) and numbers of volumes and centuries (ii, xix)
    """
    if len(lemma) == 1:
        return lemma in SPANISH_LETTERS
    if len(lemma) == 2 or ROMAN.fullmatch(lemma):
        return simplemma.is_known(lemma, lang="es")
    return True


def top_lemmas(rows: list[tuple], size: int) -> list[str]:
    """The most frequent lemmas of the vocabulary, the parts of speech summed, no proper nouns"""
    ipm: dict[str, float] = defaultdict(float)
    for lemma, tag, value, *_ in rows:
        if tag != "PROPN" and is_vocabulary(lemma):
            ipm[lemma] += value
    return sorted(ipm, key=lambda lemma: (-ipm[lemma], lemma))[:size]


def main(ngrams: Path, output: Path) -> None:
    installed = version("simplemma")
    if installed != SIMPLEMMA_VERSION:
        raise SystemExit(
            f"simplemma {installed} is installed, the dictionary needs {SIMPLEMMA_VERSION}"
        )
    totals, lemmas = aggregate(count_forms(ngrams))
    rows = build_rows(totals, lemmas)
    header = "lemma\tpos\tipm\trange\tdispersion\tdocs"
    table = "\n".join([header, *("\t".join(map(str, row)) for row in rows)]) + "\n"
    files = {
        f"{ROOT}/{FILENAME}": table.encode("utf-8"),
        f"{ROOT}/README.txt": README.format(
            size=totals.sum(), rows=len(rows), simplemma=SIMPLEMMA_VERSION
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
    top = output / TOP_FILE
    top.write_text("\n".join(top_lemmas(rows, TOP_SIZE)) + "\n", encoding="utf-8")
    print(
        f"{archive}: {len(rows)} rows, {totals.sum()} words, {archive.stat().st_size / 1e6:.1f} MB"
    )
    print("sha256", sha256(archive.read_bytes()).hexdigest())
    print(top)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
