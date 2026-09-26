# Spanish sonnets

!!! info ""
    **ests.datasets.SpanishSonnets**

## Description

A collection of Spanish sonnets from the [Diachronic Spanish Sonnet Corpus](https://github.com/pruizf/disco) (DISCO 5.0): 4,259 sonnets by 1,167 authors from Spain, Latin America and the Philippines, from the 15th century to the early 20th, 60,209 lines. Every line has its metrical pattern and the label of its rhyme, so the collection suits the study of meter and rhyme and the checking of a scansion against the annotation of the corpus.

The sonnets fall into four periods: `15th-17th` (1,088 sonnets), `18th` (321), `19th` (2,845, an anthology of Spain and Latin America) and `20th` (5, by the Filipino poet Cecilio Apóstol); 295 sonnets are by women, and the authors were born in 22 countries, most of them in Spain (2,388 sonnets) and Cuba (719).

Only the sonnets in the public domain are kept, 4,259 of 4,523: those by the authors who died before 1946, by the authors of the 15th-18th centuries whose death is unknown and by the authors of the 19th-century anthology born before 1866 or with no dates; most of the Filipino poets are left out. An author of the anthology with no dates is left out too when the dates of [VIAF](https://viaf.org) that DISCO matched with high confidence give a death in 1946 or later or a birth in 1866 or later with no death; VIAF only drops an author and never replaces the dates of the source. The metadata of DISCO is corrected by the biographical line of the source: the years of life where DISCO took a later year of it for the death or missed a birth or a death given alone (Echegaray died in 1916, not in 1904), the country of birth where the line names one (Gertrudis Gómez de Avellaneda was born in Cuba, not in Haiti). The Filipino poets have the name before the surname, as the rest; the speakers of the dialogues (`[Car]`, `[POETA]`) and the calls of the footnotes are removed from the lines, as they are absent from their metrical patterns.

The archive (1 MB, a JSON Lines file) is kept in the repository of the library and downloaded once into the data directory; it is built by `scripts/build_spanish_sonnets.py` from DISCO at a fixed commit.

!!! quote "Licence and attribution"
    DISCO is distributed under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/), and so is this dataset; the archive carries a `README.txt` with the source and the changes. Cite the source as: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., Calvo Tello J. Diachronic Spanish Sonnet Corpus (DISCO), version 5.0. Madrid: UNED, 2017-2023; and the article: Ruiz Fabo P., Bermúdez Sabel H., Martínez Cantón C., González-Blanco E. The Diachronic Spanish Sonnet Corpus: TEI and linked open data encoding, data distribution, and metrical findings. Digital Scholarship in the Humanities 36 (Supplement 1), 2021, i68-i80, [doi:10.1093/llc/fqaa035](https://doi.org/10.1093/llc/fqaa035).

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str/Path | `DEFAULT_DATA_DIR.joinpath("texts")` | Path to the dataset directory; the data directory is described in [Installation](../installation.md#datasets) |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `periods` | tuple[str] | Tuple of periods: `15th-17th`, `18th`, `19th`, `20th` |
| `authors` | Counter | Number of sonnets by author, read from the file |
| `name` | str | Name of the dataset, `spanish_sonnets` |
| `meta` | dict[str, str] | Reference information: the source, the description, the authors, the licence and the citation |
| `info` | dict[str, str] | The name and the reference information in one dictionary |
| `data_dir` | Path | Absolute path to the dataset directory |
| `filepath` | str | Path to the file of the dataset, `None` before the download |

The dataset iterates over its records as `get_records()` without filters: `for record in ss` goes over the sonnets one at a time.

## Methods

### check_data

Checks that the file of the dataset is in place and returns `True`; a dataset that is not downloaded raises `DatasetNotFoundError`. The other methods check it themselves.

### download

Downloads the archive, verifies its SHA-256 checksum and extracts the file. A corrupted archive is downloaded again, a missing file is extracted again; a repeated call downloads nothing.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `False` | Download the dataset even if it is already downloaded |

!!! example "Example"

    ``` python
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()
    ss.download()
    ss.info["license"], ss.authors.most_common(2)
    # ('CC BY 4.0', [('Rubén Darío', 140), ('José Santos Chocano', 130)])
    ```

### get_texts

Extracts the texts (without headers) from the dataset: the lines of a sonnet, the stanzas separated by a blank line.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `period` | str | `None` | Period: `15th-17th`, `18th`, `19th` or `20th` |
| `author` | str | `None` | Author: a substring of the name, regardless of case and accents |
| `country` | str | `None` | Country of birth: a substring of the name in Spanish, regardless of case and accents |
| `gender` | str | `None` | Gender of the author: `F` or `M` |
| `min_len` | int | `None` | Minimum text length (in characters) |
| `max_len` | int | `None` | Maximum text length (in characters) |
| `limit` | int | `None` | Number of texts |

The filters are combined; `author="dario"` finds Rubén Darío, `country="mexico"` finds `México`. An unknown period or gender, a length below one, a minimum length above the maximum one and a negative limit raise `ParameterError`.

!!! example "Example"

    ``` python
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()
    for text in ss.get_texts(author="avellaneda", gender="F", limit=1):
        print(text.split("\n\n")[0])
    # No encuentro paz, ni me permiten guerra;
    # de fuego devorado, sufro el frío;
    # abrazo un mundo, y quédome vacío;
    # me lanzo al cielo, y préndeme la tierra.
    ```

### get_records

Extracts the records (with headers) from the dataset. Record fields: `id` - the identifier of the sonnet in DISCO, `period` - period, `author` - author, `title` - title, `country` - the country of birth of the author in Spanish (empty when unknown), `gender` - `F` or `M`, `birth` and `death` - the years of life (`None` when unknown), `text` - text, `meter` - the metrical pattern of every line, `rhyme` - the label of the rhyme of every line. In a metrical pattern `+` is a stressed syllable and `-` an unstressed one, so its length is the number of metrical syllables: 11 for an endecasílabo, 14 for an alejandrino. Equal labels of the rhyme mark the lines that rhyme together, `-` a line that rhymes with no other. The records go by period in the order of `periods`, within a period by the identifier of DISCO sorted numerically (`1035e_269` before `1035e_1360`), which keeps the sonnets of an author together in the order of their source.

The parameters are the same as for `get_texts`.

!!! example "Example"

    ``` python
    from collections import Counter
    from ests.datasets import SpanishSonnets

    ss = SpanishSonnets()

    # The first lines of a sonnet with their rhyme and meter
    record = next(ss.get_records(author="rubén darío"))
    lines = record["text"].replace("\n\n", "\n").split("\n")
    for line, pattern, label in list(zip(lines, record["meter"], record["rhyme"]))[:4]:
        print(f"{label} {pattern:<14} {line}")
    # A -+---+---+-    En medio del abismo de la duda
    # B +----+-+-+-    lleno de oscuridad, de sombra vana
    # B +--+---+-+-    hay una estrella que reflejos mana
    # A -+-+---+-+-    sublime, sí, mas silenciosa, muda.

    # The share of endecasílabos and alejandrinos by period
    for period in ss.periods:
        lengths = Counter(
            len(pattern) for record in ss.get_records(period=period) for pattern in record["meter"]
        )
        total = sum(lengths.values())
        print(period, f"{lengths[11] / total:.2f}", f"{lengths[14] / total:.2f}")
    # 15th-17th 0.98 0.00
    # 18th 0.99 0.00
    # 19th 0.86 0.09
    # 20th 0.60 0.40
    ```

!!! warning "The annotation is automatic"
    The metrical patterns and the labels of the rhyme are the automatic annotation of DISCO (the scansion by ADSO, by Jumper for the modernist and the Filipino sonnets, the rhyme by RhymeTagger): a reference to compare a scansion with, not a gold standard, as a pattern may miss a synalepha or a stress that a reader would make. Some sonnets have no labels of the rhyme, and the long sequences have none after the letter `N`: such a label is an empty string.

!!! note "Sonnets, sequences and titles"
    4,211 records are sonnets of 14 lines; the rest are sonnets with an estrambote, a few incomplete or irregular ones (Darío's "El soneto de trece versos") and sequences of sonnets that DISCO keeps in one file, up to 98 lines. The sonnets of a sequence kept in separate files have the title `Part of: ` and the title of the sequence. The titles and the spelling are those of the sources of DISCO, some titles in capitals.
