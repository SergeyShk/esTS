# Lexical sophistication statistics

!!! info ""
    **ests.lexical_stats.LexicalStats**

## Description

A module for computing the lexical sophistication statistics of a text in the manner of [TAALES](https://doi.org/10.3758/s13428-017-0924-4) - how rare the words of the text are in the language: the mean frequency, range and dispersion of the lemmas by the [frequency dictionary](../datasets/freqdict.md) of Google Books Ngram, the shares of the words of the frequency bands top-1000, 2000, 5000 and 10000 by the embedded list of the most frequent lemmas, the surprisal and the perplexity by the unigram model of the dictionary, the lexical density. Unlike the [lexical diversity metrics](diversity_stats.md), which compare the words of the text with each other, here the words are compared with the frequencies of the language.

A word is looked up by [`lemma_key`](../datasets/freqdict.md#lemma_key), the key the dictionary is built with: the lemma of simplemma of the word in lower case, and the lower-case form for a proper noun, so `París` is found as `parís` and not as the verb `parir`. Whether a word is a proper noun, and whether it is a content word, comes from the annotation, so the source has to be annotated: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, and a `Doc` must carry the parts of speech (a `morphologizer`, or a `tagger` with an `attribute_ruler`); a source without them raises `SourceError`. The lemmas of the model are not used. The tagger has the last word on the proper nouns: a capitalized verb at the start of a sentence tagged `PROPN` is looked up by its form. A content word is defined as in [`CohesionStats`](cohesion_stats.md): one of `CONTENT_UD_POS` (nouns, proper nouns, adjectives, verbs, adverbs) and no demonstrative. Numbers (`2020`, `5,5`, `3.º`) are no words: the dictionary and the list do not have them, and they would look like the rarest words of the text.

A text longer than the `max_length` of the pipeline - a million characters by default - raises `SourceError`: split it into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

Resources:

| Resource | Statistics | Availability |
| :------- | :--------- | :----------- |
| [`FreqDict`](../datasets/freqdict.md) - 83,785 lemmas of Google Books Ngram (1980-2019) with ipm, range and dispersion | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | downloaded once with `FreqDict().download()`; without the dictionary reading these statistics and `get_stats` raises `DatasetNotFoundError` |
| The embedded list of the 10,000 most frequent lemmas of the same dictionary (`ests/resources/google_books_top10000.txt`, CC BY 3.0) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | always |

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Data source (a string or a Doc object) |
| `freq_dict` | FreqDict | `None` | Frequency dictionary; if not given, `FreqDict()` from the default directory is used |
| `nlp` | Language | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Attributes

| Attribute | Type | Description |
| :-------: | :--: | :---------: |
| `words` | tuple[str] | Tuple of the words |
| `lemmas` | tuple[str] | Tuple of the keys of the words in the dictionary (`lemma_key`) |
| `ranks` | tuple[int/None] | Tuple of the ranks of the lemmas by the embedded list, `None` beyond the top 10000 |
| `entries` | tuple[Entry/None] | Tuple of the entries of the dictionary for every word, `None` for a word out of it |
| `n_words` | int | Number of words |
| `n_content_words` | int | Number of content words |
| `n_found` | int | Number of words found in the dictionary |
| `coverage` | float | Share of words found in the dictionary |
| `mean_ipm` | float | Mean frequency of the words found |
| `mean_ipm_content` | float | Mean frequency of the content words found |
| `mean_log_ipm` | float | Mean decimal logarithm of the frequency of the words found |
| `mean_log_ipm_content` | float | The same over the content words |
| `mean_range` | float | Mean range of the words found - years out of 40 |
| `mean_dispersion` | float | Mean dispersion D of the words found |
| `surprisal` | float | Mean surprisal of the words by the unigram model of the dictionary, in bits |
| `perplexity` | float | Unigram perplexity |
| `p_top1000` | float | Share of words with a lemma of the top 1000 |
| `p_top2000` | float | Share of words with a lemma of the top 2000 |
| `p_top5000` | float | Share of words with a lemma of the top 5000 |
| `p_top10000` | float | Share of words with a lemma of the top 10000 |
| `p_beyond_top10000` | float | Share of words with a lemma beyond the top 10000 |
| `lexical_density` | float | Share of content words |

The means by the dictionary are computed over the words found only, `nan` without them; read them next to `coverage`. The mean frequency in ipm is dominated by the function words (`el` - 97,000 ipm, `de` - 71,000), so to compare texts the log frequency or the mean over the content words suits better. The range is the number of years out of 40 in which the lemma occurs in the books, not the number of parts of a corpus out of 100.

!!! note "Note"
    Every statistic can be computed apart by calling its function. The statistics and the functions that compute them are described in the corresponding [section](lexical_stats_funcs.md).

## Methods

### band_coverage

Returns the shares of the words with a lemma of the top N for every bound N.

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `bands` | list[int] | `(1000, 2000, 5000, 10000)` | Bounds of the bands - the sizes of the top lists |
| `unique` | bool | `False` | Count the distinct lemmas instead of the words |

!!! example "Example"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.band_coverage(unique=True)
    # {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}
    ls.band_coverage(bands=(100, 500))
    # {100: 0.6363636363636364, 500: 0.7272727272727273}
    ```

### get_stats

Returns a dictionary with the computed lexical sophistication statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Import the libraries
    from ests import LexicalStats
    from ests.datasets import FreqDict

    # Download the dictionary (once)
    FreqDict().download()

    # Compute the statistics
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.get_stats()
    ```

    _Result_:

    ``` bash
    {'coverage': 1.0,
     'mean_ipm': 34283.74818181818,
     'mean_ipm_content': 956.3320000000001,
     'mean_log_ipm': 3.559971676175293,
     'mean_log_ipm_content': 2.1916598821626314,
     'mean_range': 40.0,
     'mean_dispersion': 97.63636363636364,
     'surprisal': 8.105598641234213,
     'perplexity': 275.4408334528846,
     'p_top1000': 0.7272727272727273,
     'p_top2000': 0.8181818181818182,
     'p_top5000': 1.0,
     'p_top10000': 1.0,
     'p_beyond_top10000': 0.0,
     'lexical_density': 0.45454545454545453}
    ```

Rare words raise the surprisal and lower the coverage and the bands:

!!! example "Example"

    ``` python
    ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
    ls.coverage, ls.p_top1000, ls.p_beyond_top10000, ls.surprisal
    # (0.8571428571428571, 0.42857142857142855, 0.4285714285714286, 13.70650419215419)
    ```

### print_stats

Prints a table with the computed lexical sophistication statistics.

!!! example "Example"

    _Code_:

    ``` python
    # Create the object of the statistics
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")

    # Print the table of the computed statistics
    ls.print_stats()
    ```

    _Result_:

    ``` bash
                            Statistic                         |  Value
    --------------------------------------------------------------------
    Share of words found in the frequency dictionary          |   1.00
    Mean frequency (ipm)                                      | 34283.75
    Mean frequency of content words (ipm)                     |  956.33
    Mean log frequency (lg ipm)                               |   3.56
    Mean log frequency of content words                       |   2.19
    Mean range (years out of 40)                              |  40.00
    Mean dispersion (D)                                       |  97.64
    Mean surprisal (bits)                                     |   8.11
    Unigram perplexity                                        |  275.44
    Share of words in the top 1000                            |   0.73
    Share of words in the top 2000                            |   0.82
    Share of words in the top 5000                            |   1.00
    Share of words in the top 10000                           |   1.00
    Share of words beyond the top 10000                       |   0.00
    Lexical density                                           |   0.45
    ```
