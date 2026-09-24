# Keywords

!!! info ""
    **ests.corpus.keyness()**, **ests.corpus.Keyword**

## Description

Keyword extraction (keyness) for a target corpus against a reference one: the words that occur significantly more often in the target corpus than in the reference. A standard tool of corpus linguistics for comparing genres, authors, translations and periods ([AntConc](https://www.laurenceanthony.net/software/antconc/), [Sketch Engine](https://www.sketchengine.eu/), quanteda `textstat_keyness`).

For every word two values are computed that [Gabrielatos and Marchi](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf) and [Hardie](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/) recommend reading together: the log-likelihood $G^2$ with its p-value (the significance of the difference - whether there is one) and Log Ratio (the size of the effect - how large it is). The chosen measure `score` is computed as well and used for the sorting. The measures of significance ($G^2$, chi-square, BIC, ELL) are signed: negative when the word is more frequent in the reference; the measures of effect (%DIFF, Log Ratio, odds ratio) are directional by construction.

The reference may be a list of words or a mapping of frequencies, with the size of the reference taken as the sum of the counts, or the [frequency dictionary](../datasets/freqdict.md) `FreqDict` of Google Books Ngram. Against the dictionary the target has to be counted the way the dictionary was: word forms, not lemmas - [`lemma_key`](../datasets/freqdict.md#lemma_key) is not idempotent, so a lemma may move on (`estado` - `estar`) and `WordsExtractor(use_lexemes=True)` does not fit - with the stop words kept, as the size of the corpus of the dictionary keeps them. The forms that are not made of the letters of `WORD_PATTERN` - numbers, words with a hyphen or a dot - are left out of the target and of its size, as the dictionary has none. A form goes to its key by `lemma_key`, and the rows of the proper nouns of the dictionary, which keep their forms, go to `lemma_key` of the forms as well (`FreqDict.word_ipm`), so both sides count the same forms under a key: the occurrences of *Roma* in the books are counted under the key `romo` that the word `Roma` reaches, and the label of another lemma (`romo`, `parir`) is all that is left of the missing parts of speech. The frequency of a key in the reference is its ipm times the size of the corpus of the dictionary (`CORPUS_SIZE`, 63 billion words of the books of 1980-2019). A word out of the dictionary gets its least frequency, 0.1 ipm (about 6300 occurrences): the dictionary leaves out the rarer words, so their true frequency lies somewhere below, and a zero would put every word out of the dictionary before the real keywords. The dictionary describes the register of the books, so the negative keywords of a text are the words of scholarly prose (`de`, `social`, `país`).

Against a list or a mapping, words are compared as they are: case, lemmatization and stop words belong to [`WordsExtractor`](../extractors/words.md), and both corpora have to be extracted the same way.

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
| `target` | list[str]/dict[str, int] | `-` | Words of the target corpus or their frequencies; word forms against the frequency dictionary |
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
    # laurencia 135 0.32 2528.7 14.96
    # mengo 105 0.13 2102.5 15.9
    # comendador 154 5.33 2059.9 11.09
    # frondoso 113 3.84 1515.6 11.12
    # barrildo 52 0.1 995.7 15.26
    ```
