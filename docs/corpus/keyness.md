# Keywords

``` {.python .signature}
keyness(target, reference, measure='log_likelihood', min_freq=1, positive=True, top_n=None)
```

--8<-- "corpus/keyness.md:keyness"

The function wraps `keyness` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/keyness/) core and also takes the [frequency dictionary](../datasets/freqdict.md) `FreqDict` as the reference; `FrequencyReference` is in `ests.corpus` next to it. Words are extracted with [`WordsExtractor`](../extractors/words.md).

=== "Code"

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
    [(k.word, round(k.g2, 2)) for k in keyness(target, reference, positive=False, top_n=2)]
    ```

=== "Result"

    ```
    [Keyword(word='gato', freq_target=3, freq_reference=0.0, ipm_target=81081.08108108108, ipm_reference=0.0, g2=2.79971718756897, p_value=0.09428093556593176, log_ratio=1.8349407537295037, score=2.79971718756897)]
    [('perro', -5.92), ('comer', -1.97)]
    ```

## Parameters

--8<-- "corpus/keyness.md:keyness-parameters"

`reference` may also be `FreqDict`, against which `target` is word forms. A frequency dictionary that is not downloaded raises `DatasetNotFoundError`. `keyness` checks its parameters and the target with `check_keyness_params` before it reads `FreqDict`, so a wrong argument fails before the dictionary is loaded.

--8<-- "corpus/keyness.md:check_keyness_params"

## Reference by frequencies

--8<-- "corpus/keyness.md:FrequencyReference"

The frequency dictionary `FreqDict` of Google Books Ngram passed as `reference` is turned into such a reference:

| Field | `FreqDict` |
| :---- | :--------- |
| `counts` | the ipm of `FreqDict.word_ipm`, the proper nouns included, converted to occurrences in the corpus of the dictionary |
| `size` | `CORPUS_SIZE`, 63 billion words of the books of 1980-2019 |
| `missing` | the least frequency of the dictionary `FreqDict.min_ipm`, 0.1 ipm (about 6300 occurrences) |
| `key` | [`lemma_key`](../datasets/freqdict.md#lemma_key): a keyword may carry the label of another lemma, *Roma* is counted under `romo` |
| `keep` | the forms made of the letters of `WORD_PATTERN`; numbers and words with a hyphen or a dot are left out |

The target has to be counted the way the dictionary was: word forms with the stop words kept, not lemmas - `lemma_key` is not idempotent (`estado` - `estar`), so `WordsExtractor(use_lexemes=True)` does not fit. The dictionary describes the register of the books, so the negative keywords of a text are the words of scholarly prose (`de`, `social`, `país`).

Against the dictionary the words of a play of Lope de Vega from the [corpus of literature](../datasets/spanishliterature.md) give its characters:

=== "Code"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import keyness
    from ests.datasets import FreqDict, SpanishLiterature

    text = next(SpanishLiterature().get_texts(author="lope", genre="drama"))
    words = WordsExtractor(lowercase=True).extract(text)
    for k in keyness(words, FreqDict(), top_n=5):
        print(k.word, k.freq_target, round(k.ipm_reference, 2), round(k.g2, 1), round(k.log_ratio, 2))
    ```

=== "Result"

    ```
    laurencia 135 0.32 2528.7 14.96
    mengo 105 0.13 2102.5 15.9
    comendador 154 5.33 2059.9 11.09
    frondoso 113 3.84 1515.6 11.12
    barrildo 52 0.1 995.7 15.26
    ```

## Result

--8<-- "corpus/keyness.md:Keyword"

## Measures

--8<-- "corpus/keyness.md:keyness-measures"

The module `ests.corpus.keyness` re-exports the functions of the measures (`from ests.corpus.keyness import calc_log_likelihood`).

<div class="metric-card" markdown>

### Log-likelihood { #log_likelihood }

`log_likelihood` · `g2` · `p_value` · [Rayson and Garside (2000)](https://ucrel.lancs.ac.uk/llwizard.html)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_log_likelihood"

--8<-- "corpus/keyness.md:calc_p_value"

</div>

<div class="metric-card" markdown>

### Chi-square { #chi2 }

`chi2`
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_chi2"

</div>

<div class="metric-card" markdown>

### %DIFF { #diff }

`diff` · [Gabrielatos and Marchi (2011)](http://eprints.lancs.ac.uk/51449/4/Gabrielatos_Marchi_Keyness.pdf)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_diff"

</div>

<div class="metric-card" markdown>

### Log Ratio { #log_ratio }

`log_ratio` · [Hardie (2014)](http://cass.lancs.ac.uk/log-ratio-an-informal-introduction/)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_log_ratio"

</div>

<div class="metric-card" markdown>

### BIC { #bic }

`bic` · Wilson (2013)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_bic"

</div>

<div class="metric-card" markdown>

### ELL { #ell }

`ell` · Johnston, Berry and Mielke (2006)
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_ell"

</div>

<div class="metric-card" markdown>

### Odds ratio { #odds_ratio }

`odds_ratio`
{ .metric-meta }

--8<-- "corpus/keyness.md:calc_odds_ratio"

</div>
