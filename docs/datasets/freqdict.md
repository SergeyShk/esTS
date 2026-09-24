# Frequency dictionary

!!! info ""
    **ests.datasets.FreqDict**

## Description

A frequency dictionary of Spanish lemmas built from the Spanish books of [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html) (version 20200217): 83,785 lemmas (109,178 rows of a lemma and a part of speech) of the books of 1980-2019, 63 billion words. Every row has the frequency per million words (ipm), the range (the number of years out of 40 in which the lemma occurs), Juilland's D over the years (0-100) and the number of books with the most widespread form of the lemma. The parts of speech are those of Google, with the names of Universal Dependencies: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP`, `CONJ` (coordinating and subordinating together).

The dictionary is built by `scripts/build_freq_dict.py` from the 1-grams (3.2 GB): only the forms tagged with a part of speech and made of letters are counted (numbers, punctuation and the tag `X` go); the forms go to their keys by [`lemma_key`](#lemma_key) - lower case, then the lemma by simplemma 2.0.0, the lemmatizer of the library. Google has no tag for proper nouns, so a noun form written with a capital letter in 90% of its occurrences is `PROPN` and keeps its form. The decision is taken for the whole form, the lower-case occurrences included: the form `dios` is capitalized in 92% of its occurrences, so all of it, `dios` in lower case too, is `PROPN` (405.9 ipm), while the `NOUN` row of `dios` (37.3 ipm) comes mostly from the plural `dioses`, capitalized in 6% of its occurrences. The rows below 0.1 ipm or found in fewer than 5 years (the misreadings of one batch of scanned books) are left out. The dispersion is computed on the relative frequency of every year, so that the years of different size weigh the same; the number of books is a lower bound, as a book with several forms of the lemma is counted once.

For a lookup the parts of speech of a lemma are merged: the frequencies are summed, the range, the dispersion and the number of books are the greatest ones. The lemma is looked up in lower case. The parsed dictionary is cached by the path of the file and read once per process, so a `FreqDict()` for every text is cheap. The dictionary is the source of the frequencies of [`LexicalStats`](../stats/lexical_stats.md), and its 10,000 most frequent lemmas are the embedded list of the frequency bands. The dictionary size is `CORPUS_SIZE`, 63,090,618,290 words.

The archive (0.9 MB) is kept in the repository of the library, downloaded once into the data directory, verified against its SHA-256 checksum and extracted.

!!! quote "Licence and attribution"
    The dictionary is derived from Google Books Ngram, which is licensed under the [Creative Commons Attribution 3.0 Unported License](https://creativecommons.org/licenses/by/3.0/), and is distributed under the same licence; the archive carries a `README.txt` with the source and the changes. Cite the source as: Michel J.-B. et al. Quantitative analysis of culture using millions of digitized books. Science 331 (6014), 2011.

## Key of a word { #lemma_key }

`ests.datasets.freq_dict.lemma_key(word, proper=False)` - the key by which a word is looked up in the dictionary, and by which the dictionary is built: the word goes to lower case and then to its lemma by `lemmatize`. simplemma tells the case apart and leaves an unknown capitalized word as it is, so a word at the start of a sentence would miss its lemma (`Miró`, `Déjame`); the lower case finds it (`mirar`, `dejar`). A proper noun keeps its form in lower case (`proper=True`): `París` is `parís`, not the verb `parir`.

The lemmas depend on the version of simplemma: the dictionary is built with 2.0.0 (the constant `SIMPLEMMA_VERSION`), and the library requires simplemma 2.0 or newer; with 1.x about 4% of the words of a text would get other lemmas (`fue` - `ir` instead of `ser`, `usted` left as it is).

!!! example "Example"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    lemma_key("Miró"), lemma_key("computadoras"), lemma_key("fue")
    # ('mirar', 'computador', 'ser')
    lemma_key("París"), lemma_key("París", proper=True)
    # ('parir', 'parís')
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `data_dir` | str/Path | `DEFAULT_DATA_DIR.joinpath("dicts")` | Path to the dictionary directory |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `entries` | dict[str, Entry] | Entries by lemma, the parts of speech merged |
| `min_ipm` | float | Minimum frequency in the dictionary (0.1) |
| `word_ipm` | dict[str, float] | Frequencies by the key a word form reaches without a part of speech: the rows of the proper nouns go to `lemma_key` of their forms (`roma` to `romo`); the reference of [`keyness`](../corpus/keyness.md) |

An `Entry` is a named tuple with the fields `lemma`, `pos` (tuple of parts of speech), `ipm`, `range`, `dispersion`, `docs`.

## Methods

### download

Downloads the archive with checksum verification and extracts the file. A corrupted or replaced archive is removed and downloaded again in the same call; if the archive is there but the file of the dictionary is missing, it is extracted again, and the parsed dictionary is read anew.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `force` | bool | `False` | Download the dictionary even if it is already downloaded |

!!! example "Example"

    ``` python
    from ests.datasets import FreqDict

    fd = FreqDict()
    fd.download()
    fd.info["license"]
    # 'CC BY 3.0'
    ```

### lookup

Returns the entry of a lemma in any case, `None` for a lemma out of the dictionary. A word form is looked up by its key: `computadoras` by `lemma_key("computadoras")`, which is `computador`, not by `computadora`.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemma` | str | `-` | Lemma |

!!! example "Example"

    ``` python
    fd.lookup("Gato")
    # Entry(lemma='gato', pos=('NOUN', 'ADJ'), ipm=29.08, range=40, dispersion=95, docs=232841)
    fd.lookup("dios")
    # Entry(lemma='dios', pos=('PROPN', 'NOUN', 'ADJ'), ipm=444.42, range=40, dispersion=98, docs=566129)
    ```

### ipm

Returns the frequency of a lemma per million words, 0 for a lemma out of the dictionary.

!!! example "Example"

    ``` python
    from ests.datasets.freq_dict import lemma_key

    fd.ipm("computadora"), fd.ipm(lemma_key("computadoras"))
    # (0.0, 20.07)
    "gato" in fd, len(fd)
    # (True, 83785)
    ```

### get_records

Returns the records of the dictionary - a row for every lemma and part of speech, by frequency - filtered by the part of speech and the minimum frequency. An unknown part of speech and a negative limit raise `ParameterError`.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `pos` | str | `None` | Part of speech: `NOUN`, `PROPN`, `VERB`, `ADJ`, `ADV`, `PRON`, `DET`, `ADP` or `CONJ` |
| `min_ipm` | float | `None` | Minimum frequency |
| `limit` | int | `None` | Number of records |

!!! example "Example"

    ``` python
    for record in fd.get_records(pos="PROPN", limit=3):
        print(record)
    # {'lemma': 'méxico', 'pos': 'PROPN', 'ipm': 546.31, 'range': 40, 'dispersion': 94, 'docs': 535343}
    # {'lemma': 'san', 'pos': 'PROPN', 'ipm': 411.07, 'range': 40, 'dispersion': 94, 'docs': 645513}
    # {'lemma': 'dios', 'pos': 'PROPN', 'ipm': 405.93, 'range': 40, 'dispersion': 95, 'docs': 566129}
    ```

### get_texts

Returns the lemmas of the dictionary with the same parameters as `get_records`.

!!! example "Example"

    ``` python
    list(fd.get_texts(pos="ADV", limit=5))
    # ['no', 'más', 'mucho', 'ya', 'también']
    ```

!!! warning "The register of the books"
    The dictionary describes the written language of books, a good part of them scholarly, and keeps what the books have: the abbreviations of the references are frequent words (`pp` 259.6 ipm, `cit` 110.5, `vol` 53.6), and so are the English words of the bibliographies (`the` 320.3, `of` 262.4) and the old spellings of the reprints (`fué` 26.7). The texts are recognized from scans and tagged automatically, so misreadings and tagging errors remain, mostly among the rare lemmas; the lemmatizer knows no context, so a form shared by two lemmas goes to one of them (`como` is only `como`, never `comer`), and a form it does not know stays as it is (`darle`, `verlo`).
