# Keywords

!!! info ""
    **ests.corpus.keyness()**, **ests.corpus.Keyword**

## Description

Keyword extraction (keyness) for a target corpus against a reference one: the words that occur significantly more often in the target corpus than in the reference. A standard tool of corpus linguistics for comparing genres, authors, translations and periods ([AntConc](https://www.laurenceanthony.net/software/antconc/), [Sketch Engine](https://www.sketchengine.eu/), quanteda `textstat_keyness`).

For every word two values are computed that [Gabrielatos and Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) and [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recommend reading together: the log-likelihood $G^2$ with its p-value (the significance of the difference - whether there is one) and Log Ratio (the size of the effect - how large it is). The chosen measure `score` is computed as well and used for the sorting. The measures of significance ($G^2$, chi-square, BIC, ELL) are signed: negative when the word is more frequent in the reference; the measures of effect (%DIFF, Log Ratio, odds ratio) are directional by construction.

The reference may be a list of words or a mapping of frequencies, with the size of the reference taken as the sum of the counts, or the [frequency dictionary](../datasets/freqdict.md) `FreqDict` of Google Books Ngram. With the dictionary the words of the target corpus go to its keys by [`lemma_key`](../datasets/freqdict.md#lemma_key) - a word form to its lemma, a lemma stays as it is - so the keywords are lemmas, and the frequency of a lemma in the reference is its ipm times the size of the corpus of the dictionary (`CORPUS_SIZE`, 63 billion words of the books of 1980-2019); a word out of the dictionary has a zero frequency there. Without the parts of speech a proper noun goes to its lemma as well (`París` - `parir`), while an unknown name stays as it is (`Madrid` - `madrid`). The dictionary describes the register of the books, so the negative keywords of a text are the words of scholarly prose (`de`, `social`, `país`).

Words are compared as they are: case, lemmatization and stop words belong to [`WordsExtractor`](../extractors/words.md).

## Measures

For a word of frequency $a$ in a target corpus of size $c$ and of frequency $b$ in a reference corpus of size $d$, $N = c + d$:

| Measure | Key | Formula | Description |
| :------ | :-- | :------ | :---------- |
| Log-likelihood | `log_likelihood` | $G^2 = 2\,(a \ln \frac{a}{E_1} + b \ln \frac{b}{E_2})$, $E_1 = \frac{c\,(a+b)}{N}$, $E_2 = \frac{d\,(a+b)}{N}$ | [Rayson and Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html); critical values `G2_CRITICAL_VALUES`: 3.84 for p < 0.05, 6.63 for p < 0.01, 10.83 for p < 0.001, 15.13 for p < 0.0001 |
| Chi-square | `chi2` | $\chi^2 = \frac{N\,\max(\lvert a(d-b) - b(c-a) \rvert - N/2,\ 0)^2}{(a+b)(N-a-b)\,c\,d}$ | with Yates's correction over the 2×2 contingency table; when the correction exceeds the difference, the statistic is zero |
| %DIFF | `diff` | $\frac{NF_a - NF_b}{NF_b} \cdot 100$ | [Gabrielatos and Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf); $NF$ - frequency per million words |
| Log Ratio | `log_ratio` | $\log_2 \frac{NF_a}{NF_b}$ | [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/); one means the word is twice as frequent in the target corpus |
| BIC | `bic` | $\operatorname{sign}(G^2) \cdot (\lvert G^2 \rvert - \ln N)$ | Wilson (2013); in absolute value above 2 - positive evidence of a difference, above 6 - strong, above 10 - very strong; a negative value with $\lvert G^2 \rvert < \ln N$ means no evidence, not the opposite direction |
| ELL | `ell` | $\frac{G^2}{N \ln \min(E_1, E_2)}$ | Johnson, Culpeper and Rayson (2007); size of the effect of $G^2$ from 0 to 1, `nan` when the least expected frequency is below $e$ - then $\ln \min(E_1, E_2) < 1$ and the measure exceeds one |
| Odds ratio | `odds_ratio` | $\frac{a / (c - a)}{b / (d - b)}$ | one means equal odds; `inf` if the word fills the whole target corpus, 0 - the whole reference |

A zero frequency in one of the corpora is replaced with 0.5 for %DIFF, Log Ratio and the odds ratio (Hardie 2014). The p-value of $G^2$ comes from the chi-square distribution with one degree of freedom (`calc_p_value`). The measures are available as the functions `calc_log_likelihood`, `calc_chi2`, `calc_diff`, `calc_log_ratio`, `calc_bic`, `calc_ell`, `calc_odds_ratio` with the arguments `(a, b, c, d)` of the module `ests.corpus.keyness` (`from ests.corpus.keyness import calc_log_likelihood`); their names and descriptions are in `ests.constants.KEYNESS_MEASURES`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `target` | list[str]/dict[str, int] | `-` | Words of the target corpus or their frequencies |
| `reference` | list[str]/dict[str, float]/FreqDict | `-` | Words of the reference corpus, their frequencies or the frequency dictionary |
| `measure` | str | `log_likelihood` | Measure of `KEYNESS_MEASURES` for `score` and the sorting |
| `min_freq` | int | `1` | Minimum frequency of a keyword in its own corpus |
| `positive` | bool | `True` | Positive keywords (more frequent in the target corpus) or negative ones (more frequent in the reference) |
| `top_n` | int | `None` | Number of keywords; `None` - all of them |

## Result

A list of `Keyword` named tuples by descending keyness (ties broken by descending frequency and alphabetically, words of an undefined measure last); `pd.DataFrame(keywords)` gives a table.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `word` | str | Word |
| `freq_target` | int | Frequency in the target corpus |
| `freq_reference` | float | Frequency in the reference corpus |
| `ipm_target` | float | Frequency in the target corpus per million words |
| `ipm_reference` | float | Frequency in the reference corpus per million words |
| `g2` | float | Signed $G^2$ |
| `p_value` | float | p-value of $G^2$ |
| `log_ratio` | float | Log Ratio |
| `score` | float | Value of the chosen measure |

## Example

!!! example "Example"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness

    we = WordsExtractor(use_lexemes=True, lowercase=True)
    target = we.extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    reference = we.extract(
        "El perro estaba en el suelo y dormía. Después el perro comió y volvió a dormir. "
        "Mañana el perro saldrá a pasear."
    )

    keyness(target, reference, top_n=1)
    # [Keyword(word='gato', freq_target=3, freq_reference=0, ipm_target=81081.08108108108,
    #  ipm_reference=0.0, g2=2.79971718756897, p_value=0.09428093556593176,
    #  log_ratio=1.8349407537295037, score=2.79971718756897)]

    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    # [('perro', -5.92), ('comer', -1.97)]
    ```

Against the [frequency dictionary](../datasets/freqdict.md) the words of a play of Lope de Vega from the [corpus of literature](../datasets/spanishliterature.md) give its characters:

!!! example "Example"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness
    from ests.datasets import FreqDict, SpanishLiterature

    text = next(SpanishLiterature().get_texts(author="lope", genre="drama"))
    words = WordsExtractor(lowercase=True).extract(text)
    for k in keyness(words, FreqDict(), top_n=5):
        print(k.word, k.freq_target, round(k.ipm_reference, 2), round(k.g2, 1), round(k.log_ratio, 2))
    # laurencia 135 0.32 2528.4 14.96
    # mengo 105 0.13 2102.3 15.89
    # comendador 154 5.33 2059.6 11.09
    # barrildo 52 0.0 1599.0 28.88
    # frondoso 113 3.84 1515.4 11.12
    ```
