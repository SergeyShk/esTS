# Statistic functions

## Frequency by the dictionary { #frequency }

The attributes `coverage`, `mean_ipm`, `mean_ipm_content`, `mean_log_ipm`, `mean_log_ipm_content`, `mean_range` and `mean_dispersion` of `LexicalStats` are computed from the entries of the [`FreqDict`](../datasets/freqdict.md) for the words of the text (`entries`), looked up by [`lemma_key`](../datasets/freqdict.md#lemma_key): the means are taken over the words found in the dictionary, over all of them or over the content words alone. The mean frequency in ipm is sensitive to the function words (`el` - 97,000 ipm, `de` - 71,000), so to compare texts the log frequency or the mean over the content words suits better.

## Surprisal and perplexity { #calc_surprisal }

!!! info ""
    **ests.lexical_stats.calc_surprisal()**

Computing the mean surprisal of the words by the unigram model of the frequency dictionary. A word out of the dictionary gets the minimum frequency of the dictionary (0.1 ipm), so the surprisal is defined for every word; the more rare words a text has, the higher it is. The perplexity of the text `perplexity` is $2^{H}$.

Formula:

$$
H = -\frac{1}{N} \sum_{i=1}^{N} \log_2 \frac{\mathrm{ipm}(w_i)}{10^6}
$$

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemmas` | list[str] | `-` | Keys of the words (`lemma_key`) |
| `freq_dict` | FreqDict | `-` | Frequency dictionary |

## Frequency bands { #get_rank }

!!! info ""
    **ests.lexical_stats.get_rank()**, **ests.lexical_stats.load_top_lemmas()**

Getting the rank of a lemma by the embedded list of the 10,000 most frequent lemmas of the [frequency dictionary](../datasets/freqdict.md) (the file `ests/resources/google_books_top10000.txt`, derived from Google Books Ngram under CC BY 3.0), `None` for a lemma out of the list. The parts of speech of a lemma are summed and the proper nouns are left out; so are the letters other than the Spanish words (`a`, `e`, `o`, `u`, `y`, `á`, `é`, `ó`) - the letters of enumerations and initials - and the lemmas of two letters and the Roman numerals that simplemma does not know (`pp`, `vs`, `xix`). The abbreviations of the references (`cit`, `vol`) and the English words of the bibliographies (`the`, `of`) stay, as frequent tokens of the books. `LexicalStats` derives from the ranks the shares of the words of the top 1000, 2000, 5000 and 10000 (`FREQUENCY_BANDS`) and beyond the top 10000 - a profile of frequency bands in the manner of the Lexical Frequency Profile; the method `band_coverage` gives the shares for any bounds and over the distinct lemmas. The bands take the lower-case form of a proper noun, as the list alone cannot tell `París` from `parir`: a proper noun whose form is a common lemma gets its rank (`Unión` 798, `Gobierno` 106, `Guerra` 240), while the names and the inflected parts of names (`Madrid`, `Estados`, `Naciones`) fall beyond the top 10000, so a text full of names has a greater share there. A bound out of 1 and 10000 raises `ParameterError`: beyond the list every share would be the one of the top 10000.

Parameters:

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `lemma` | str | `-` | Lemma - the key of `lemma_key` |

!!! example "Example"

    ``` python
    from ests.lexical_stats import get_rank

    get_rank("el"), get_rank("gato"), get_rank("felinólogo")
    # (1, 2851, None)
    ```

## Lexical density { #lexical_density }

The attribute `lexical_density` of `LexicalStats` is the share of the content words among all the words: a content word is one of `CONTENT_UD_POS` (nouns, proper nouns, adjectives, verbs, adverbs) and no demonstrative, as in [`CohesionStats`](cohesion_stats.md); the auxiliaries (`es`, `ha`) are no content words.
