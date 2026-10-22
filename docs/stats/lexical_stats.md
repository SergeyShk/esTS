# Lexical sophistication statistics

``` {.python .signature}
LexicalStats(source, freq_dict=None, nlp=None)
```

--8<-- "stats/lexical_stats.md:LexicalStats"

In esTS a source that is neither a string nor a `Doc` and a pipeline in `nlp` that is not a spaCy `Language` raise `SourceTypeError` too; a source without the parts of speech, a string longer than the `max_length` of the pipeline and a string with a character without a UTF-8 form `SourceError`; and the metrics by the dictionary without the dictionary downloaded `DatasetNotFoundError`.

Unlike the [lexical diversity metrics](diversity_stats.md), which compare the words of a text with each other, here the words are compared with the frequencies of the language ([TAALES](https://doi.org/10.3758/s13428-017-0924-4)). The data source is a text or a `Doc` object of the [spaCy](https://github.com/explosion/spaCy) library.

The class extends the `LexicalStats` of the [anyTS](https://sergeyshk.github.io/anyTS/stats/lexical_stats/) core with the Spanish layer: the dictionary is the Google Books Ngram [`FreqDict`](../datasets/freqdict.md) (`freq_dict_class`), and the ranks of the lemmas and the size of the list (`rank`, `top_size`) come from the embedded list of its 10,000 most frequent lemmas ([`get_rank`](#bands)). Whether a word is a proper noun, and whether it is a content word, comes from the annotation, so the source has to be annotated: a string is parsed with [`es_core_news_sm`](../installation.md#model) or with the pipeline passed in `nlp`, without the parser, the lemmatizer and the named entities, and a `Doc` must carry the parts of speech (a `morphologizer`, or a `tagger` with an `attribute_ruler`). Numbers (`2020`, `5,5`, `3.º`) are not words. The lemmas come from [`lemma_key`](../datasets/freqdict.md#lemma_key), the simplemma lemma in lower case, not from the model; a proper noun keeps its lower-case form. A content word is defined as in [`CohesionStats`](cohesion_stats.md): one of `CONTENT_UD_POS` (nouns, proper nouns, adjectives, verbs, adverbs) and no demonstrative. The `print_stats` table has the descriptions of `LEXICAL_STATS_DESC` of `ests.constants`, with the range in years out of 40.

The `max_length` of the pipeline is a million characters by default: split a longer text into parts, or raise `max_length` on a pipeline of your own and pass it in `nlp`.

=== "Code"

    ``` python
    from ests import LexicalStats
    from ests.datasets import FreqDict

    FreqDict().download()
    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.print_stats()
    ```

=== "Result"

    ```
                        Statistic                    |  Value
    ------------------------------------------------------------
    Share of words found in the frequency dictionary |   1.00
    Mean frequency (ipm)                             | 34283.75
    Mean frequency of content words (ipm)            |  956.33
    Mean log frequency (lg ipm)                      |   3.56
    Mean log frequency of content words              |   2.19
    Mean range (years out of 40)                     |  40.00
    Mean dispersion (D)                              |  97.64
    Mean surprisal (bits)                            |   8.11
    Unigram perplexity                               |  275.44
    Share of words in the top 1000                   |   0.73
    Share of words in the top 2000                   |   0.82
    Share of words in the top 5000                   |   1.00
    Share of words in the top 10000                  |   1.00
    Share of words beyond the top 10000              |   0.00
    Lexical density                                  |   0.45
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Data source |
| `freq_dict` | `FreqDict` | `None` | Frequency dictionary; `FreqDict()` from the default directory by default |
| `nlp` | `Language` | `None` | Pipeline of spaCy that parses a string; without it the model `es_core_news_sm` is loaded |

## Attributes

--8<-- "stats/lexical_stats.md:LexicalStats-attributes"

In esTS the dictionary is a `FreqDict`, and its entries are the named tuples [`Entry`](../datasets/freqdict.md). The keys of the words in the dictionary (`keys`, `dictionary_keys`) are their lemmas, and a proper noun is looked up by its form when the dictionary has it (`París` as `parís`, not the verb `parir`) and by its lemma otherwise (`Estados` of *Estados Unidos* as `estado`, a sentence-initial `Miró` tagged `PROPN` as `mirar`). A word is looked up without the period of an abbreviation (`Sr.` as `sr`, `pág.` as `página`); an initial (`D.`, `J.`) keeps it and is out of the dictionary.

=== "Code"

    ``` python
    ls = LexicalStats("Miró desde París hacia los Estados Unidos")
    ls.lemmas
    ls.keys
    ```

=== "Result"

    ```
    ('miró', 'desde', 'parís', 'hacia', 'el', 'estados', 'unidos')
    ('mirar', 'desde', 'parís', 'hacia', 'el', 'estado', 'unidos')
    ```

## Metrics

--8<-- "stats/lexical_stats.md:LexicalStats-metrics"

The metrics rely on two resources; always read the means by the dictionary next to `coverage`.

| Resource | Metrics | Availability |
| :------- | :------ | :----------- |
| [`FreqDict`](../datasets/freqdict.md) - 83,785 lemmas of Google Books Ngram (1980-2019) with ipm, range and dispersion | `coverage`, `mean_ipm*`, `mean_log_ipm*`, `mean_range`, `mean_dispersion`, `surprisal`, `perplexity` | downloaded once with `FreqDict().download()` |
| The embedded list of the 10,000 most frequent lemmas of the same dictionary (`ests/resources/google_books_top10000.txt`, CC BY 3.0) | `p_top1000`, `p_top2000`, `p_top5000`, `p_top10000`, `p_beyond_top10000`, `band_coverage` | always |

<div class="metric-card" markdown>

### Dictionary frequency { #frequency }

`coverage` · `mean_ipm` · `mean_ipm_content` · `mean_log_ipm` · `mean_log_ipm_content` · `mean_range` · `mean_dispersion` · [Google Books Ngram](https://storage.googleapis.com/books/ngrams/books/datasetsv3.html)
{ .metric-meta }

The metrics are computed from the `FreqDict` entries for the keys of the words (`keys`, `entries`): the means are taken over the words found in the dictionary, over all of them or only over the content words. The range is the number of years out of 40 (1980-2019) in which the lemma occurs in the books, and the dispersion is Juilland's D over the years, from 0 to 100. The mean frequency in ipm is sensitive to function words (`el` - 98,000 ipm, `de` - 71,000), so for comparing texts the log frequency or the mean over the content words is more convenient.

Rare words lower the coverage and the log frequency and raise the surprisal and the share beyond the top 10000:

=== "Code"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El felinólogo examinaba al minino con parsimonia")
    ls.coverage, ls.mean_log_ipm, ls.surprisal, ls.p_beyond_top10000
    ```

=== "Result"

    ```
    (0.8571428571428571, 2.3529196195453976, 13.70650419215419, 0.4285714285714286)
    ```

</div>

<div class="metric-card" markdown>

### Surprisal and perplexity { #surprisal }

`surprisal` · `perplexity`
{ .metric-meta }

--8<-- "stats/lexical_stats.md:calc_surprisal"

In esTS the dictionary is a `FreqDict` with the lowest frequency of 0.1 ipm: a dictionary of another class raises `SourceTypeError`.

=== "Code"

    ``` python
    from ests.datasets import FreqDict
    from ests.lexical_stats import calc_surprisal

    calc_surprisal(["gato", "estar", "felinólogo"], FreqDict())
    ```

=== "Result"

    ```
    15.392368319318606
    ```

</div>

<div class="metric-card" markdown>

### Frequency bands { #bands }

`p_top1000` · `p_top2000` · `p_top5000` · `p_top10000` · `p_beyond_top10000` · `band_coverage(bands, unique)`
{ .metric-meta }

--8<-- "stats/lexical_stats.md:LexicalStats-bands"

This builds a frequency band profile in the manner of the Lexical Frequency Profile. The bands take the lower-case form of a proper noun: a proper noun whose form is a common lemma gets its rank (`Gobierno` 106), while the names and their inflected parts (`Madrid`, `Estados`) fall beyond the top 10000, so a text full of names has a greater share there.

``` {.python .signature}
get_rank(lemma)
```

The rank of a lemma by the embedded list, `None` for a lemma outside the list; the lemma may be in any case.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `lemma` | `str` | - | Lemma - the key of `lemma_key` |

``` {.python .signature}
load_top_lemmas()
```

The whole list from the file `ests/resources/google_books_top10000.txt`, derived from Google Books Ngram under CC BY 3.0: the rank of every lemma, starting from 1. The list holds the 10,000 most frequent lemmas of the [frequency dictionary](../datasets/freqdict.md) by decreasing frequency, the parts of speech of a lemma summed; it leaves out the proper nouns, the single letters other than the Spanish words `a`, `e`, `o`, `u`, `y`, `á`, `é`, `ó`, and the two-letter lemmas and Roman numerals that simplemma does not know (`pp`, `xix`), while the abbreviations of the references (`cit`) and the English words of the bibliographies (`the`) stay.

=== "Code"

    ``` python
    from ests.lexical_stats import get_rank, load_top_lemmas

    get_rank("el"), get_rank("gato"), get_rank("felinólogo")
    len(load_top_lemmas())
    ```

=== "Result"

    ```
    (1, 2851, None)
    10000
    ```

</div>

<div class="metric-card" markdown>

### Lexical density { #lexical_density }

`lexical_density`
{ .metric-meta }

The share of the content words among all the words; a content word is one of `CONTENT_UD_POS` (nouns, proper nouns, adjectives, verbs, adverbs) and no demonstrative, as in [`CohesionStats`](cohesion_stats.md), so the auxiliaries (`es`, `ha`) are not content words.

$$
\frac{\textrm{Number of content words}}{\textrm{Number of words}}
$$

</div>

## Methods

--8<-- "stats/lexical_stats.md:LexicalStats-band_coverage"

=== "Code"

    ``` python
    from ests import LexicalStats

    ls = LexicalStats("El gato estaba en la ventana y miraba a los pájaros")
    ls.band_coverage(unique=True)
    ls.band_coverage(bands=(100, 500))
    ```

=== "Result"

    ```
    {1000: 0.6666666666666666, 2000: 0.7777777777777778, 5000: 1.0, 10000: 1.0}
    {100: 0.6363636363636364, 500: 0.7272727272727273}
    ```

The other methods - `get_stats`, `to_dataframe`, `print_stats` and `describe` - are those of the [statistics interface](https://sergeyshk.github.io/anyTS/stats/stats/) of the anyTS core; the lexical sophistication statistics have no scales, so `describe` gives `None` for the statistics of `get_stats`.

=== "Code"

    ``` python
    ls.get_stats()
    ```

=== "Result"

    ```
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
