# Spanish sonnets

!!! info ""
    **ests.datasets.SpanishSonnets**

## Description

A collection of Spanish sonnets from the [Diachronic Spanish Sonnet Corpus](https://github.com/pruizf/disco) (DISCO 5.0): 4,259 sonnets by 1,167 authors from Spain, Latin America and the Philippines, from the 15th century to the early 20th, 60,209 lines. Every line has its metrical pattern and the label of its rhyme, so the collection suits the study of meter and rhyme and the checking of a scansion against the annotation of the corpus.

| Period | Key | Sonnets | Authors | The most represented authors |
| :----- | :-- | :-----: | :-----: | :--------------------------- |
| 15th-17th centuries | `15th-17th` | 1,088 | 475 | Juan de Arguijo (72), Marqués de Santillana (42), Juan de Jauregui (23), Luis Martín de la Plaza (22) |
| 18th century | `18th` | 321 | 42 | Juan Nicasio Gallego (50), Juan Bautista Arriaza (28), Vicente García de la Huerta (25), Juan Meléndez Valdés (25) |
| 19th century | `19th` | 2,845 | 650 | Rubén Darío (140), José Santos Chocano (130), Clemente Althaus (52), Julio Flores Roa (52) |
| 20th century | `20th` | 5 | 1 | Cecilio Apóstol (5) |

295 sonnets are by women. By the country of birth: Spain (2,388), Cuba (719), Peru (204), Mexico (191), Nicaragua (141), Colombia (100), Argentina (93), Uruguay (76), Venezuela (68) and 13 more countries; the country of 38 sonnets is unknown. The 19th-century part of DISCO is an anthology of Spain and Latin America, the 20th-century one gathers the Filipino poets in Spanish.

Only the sonnets in the public domain are kept, 4,259 of 4,523: the ones by the authors who died before 1946, by the authors of the 15th-18th centuries whose death is unknown and by the authors of the 19th-century anthology born before 1866 or with no dates. The sonnets by the authors who died in 1946 or later are left out, most of the Filipino poets among them. An author of the anthology with no dates in the source is left out too when the dates of [VIAF](https://viaf.org) that DISCO matched with high confidence give a death in 1946 or later or a birth in 1866 or later with no death (Luis Rodríguez Embil, 1879-1954, marked only as of the 19th century): VIAF only drops an author and never replaces the dates of the source, as some of its matches are other people. The years of life are read from the biographical line of the source where DISCO took a later year of it for the death (Echegaray died in 1916, not in 1904, the year of his Nobel prize) or missed a birth or a death given alone (`1585 - Siglo XVII`, `18¿? - 1892`); the years after a century in that line are of other people or events and are not taken. The country of birth is read from that line too where it names one (Gertrudis Gómez de Avellaneda was born in Puerto Príncipe, Cuba, not in Haiti). The Filipino poets, written in DISCO with the surname first, have the name first as the rest; the speakers of the dialogues (`[Car]`, `[POETA]`) and the calls of the footnotes are left out of the lines, as they are out of their metrical patterns.

The archive (1 MB) is kept in the repository of the library, is downloaded once into the data directory, verified against its SHA-256 checksum and extracted; the sonnets are read one at a time from a JSON Lines file. It is built by `scripts/build_spanish_sonnets.py` from DISCO at a fixed commit.

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

Downloads the archive with checksum verification and extracts the file. A corrupted or replaced archive is removed and downloaded again in the same call; if the archive is there but the file is missing, it is extracted again. A repeated call downloads nothing.

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

Extracts the records (with headers) from the dataset. Record fields: `id` - the identifier of the sonnet in DISCO, `period` - period, `author` - author, `title` - title, `country` - the country of birth of the author in Spanish (empty when unknown), `gender` - `F` or `M`, `birth` and `death` - the years of life (`None` when unknown), `text` - text, `meter` - the metrical pattern of every line, `rhyme` - the label of the rhyme of every line. In a metrical pattern `+` is a stressed syllable and `-` an unstressed one, so its length is the number of metrical syllables: 11 for an endecasílabo, 14 for an alejandrino. Equal labels of the rhyme mark the lines that rhyme together, `-` a line that rhymes with no other. The records go by period in the order of `periods`, within a period by the identifier of DISCO, which keeps the sonnets of an author together.

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
    The metrical patterns and the labels of the rhyme are the automatic annotation of DISCO, not a manual one: the scansion by ADSO (accuracy 0.91) and, for the modernist and the Filipino sonnets, by Jumper (0.95); the rhyme by RhymeTagger. They are a reference to compare a scansion with, not a gold standard: a pattern may miss a synalepha or a stress that a reader would make. 20 sonnets have no labels of the rhyme, and the long sequences have none after the letter `N`: such a label is an empty string.

!!! note "Sonnets, sequences and titles"
    4,211 records are sonnets of 14 lines. The rest are sonnets with an estrambote (17 lines and so on), a few incomplete ones or ones with an irregular form (Darío's "El soneto de trece versos"), and sequences of sonnets that DISCO keeps in one file, up to 98 lines. The sonnets of a sequence in separate files have the title `Part of: ` and the title of the sequence (397 records). The titles and the spelling are those of the sources of DISCO, some titles in capitals.
