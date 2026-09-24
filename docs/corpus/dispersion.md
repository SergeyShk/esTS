# Word dispersion

!!! info ""
    **ests.corpus.dispersion()**, **ests.corpus.Dispersion**

## Description

The dispersion of a word is how evenly it is spread over the parts of a text or of a corpus. Frequency does not tell a word that occurs once in every chapter from a word gathered in one of them; the measures of dispersion ([Gries 2008](https://www.stgries.info/research/2008_STG_Dispersion_IJCL.pdf), [2020](https://www.stgries.info/research/2020_STG_Dispersion_PHCL.pdf)) complement frequency and serve to choose the vocabulary of dictionaries and of word lists for learners.

The text is split into parts: `parts` is the number of parts of about equal size or the sizes of the parts in order (sentences, paragraphs, chapters, documents of a corpus), which add up to the number of words. For every word its frequencies by part and six measures are computed; Gries recommends DP as the main one.

Words are compared as they are: case and lemmatization belong to [`WordsExtractor`](../extractors/words.md).

## Measures

For $n$ parts of shares $s_i$ of the text, frequencies of the word by part $v_i$ and a total frequency $f = \sum v_i$; $p_i = v_i / n_i$ is the relative frequency in a part of size $n_i$:

| Measure | Field | Formula | Values |
| :------ | :---- | :------ | :----- |
| Deviation of proportions DP | `dp` | $\frac{1}{2} \sum \left\lvert \frac{v_i}{f} - s_i \right\rvert$ | 0 - in proportion to the sizes of the parts, tends to 1 - in one part; Gries (2008) |
| Normalized DP | `dp_norm` | $\frac{DP}{1 - \min s_i}$ | the maximum is one whatever the split; Lijffijt and Gries (2012) |
| Juilland's D | `juilland_d` | $1 - \frac{V}{\sqrt{n - 1}}$, $V = \frac{\sigma(p)}{\mu(p)}$ | 1 - even, 0 - in one part; Juilland and Chang-Rodríguez (1964) |
| Carroll's D2 | `carroll_d2` | $\frac{H(p)}{\log_2 n}$ | entropy of the distribution $p_i$; 1 - even, 0 - in one part; Carroll (1970) |
| Rosengren's S | `rosengren_s` | $\frac{(\sum \sqrt{s_i v_i})^2}{f}$ | 1 - in proportion, tends to $1/n$ when gathered in one of equal parts; Rosengren (1971) |
| Kullback-Leibler divergence | `kl_divergence` | $\sum \frac{v_i}{f} \log_2 \frac{v_i / f}{s_i}$ | in bits; 0 - in proportion, grows when gathered in small parts; Gries (2020) |

The measures are available as the functions `calc_dp`, `calc_dp_norm`, `calc_juilland_d`, `calc_carroll_d2`, `calc_rosengren_s`, `calc_kl_divergence` with the arguments `(frequencies, sizes)` - the frequencies of the word by part and the sizes of the parts - of the module `ests.corpus.dispersion` (`from ests.corpus.dispersion import calc_dp`); their names are in `ests.constants.DISPERSION_STATS_DESC`. For a word of zero frequency every measure is `nan`. The function `dispersion` computes the same measures for every word at once over the non-zero cells of the word × part matrix, so the memory is linear in the number of words and a split by sentences costs little.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text in order |
| `parts` | int/list[int] | `10` | Number of parts (from 2 to the number of words) or sizes of the parts |
| `word` | str | `None` | Word whose dispersion is needed; `None` - every word |
| `min_freq` | int | `1` | Minimum frequency of a word |

## Result

A list of `Dispersion` named tuples by descending frequency: `word`, `freq` and the six measures of the table; `pd.DataFrame(result)` gives a table.

## Example

!!! example "Example"

    ``` python
    from ests import SentsExtractor, WordsExtractor
    from ests.corpus import dispersion

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    we = WordsExtractor(use_lexemes=True, lowercase=True)
    words = we.extract(text)
    sizes = [len(we.extract(sent)) for sent in SentsExtractor().extract(text)]
    sizes
    # [11, 12, 14]

    dispersion(words, parts=sizes, word="gato")
    # [Dispersion(word='gato', freq=3, dp=0.04504504504504503, dp_norm=0.06410256410256408,
    #  juilland_d=0.9307654905484509, carroll_d2=0.9955884389001025,
    #  rosengren_s=0.9974825285744621, kl_divergence=0.007241184435774255)]

    # Three equal parts: a and pájaro are gathered at the edges of the text
    [(d.word, round(d.dp, 2)) for d in dispersion(words, parts=3, min_freq=3)]
    # [('el', 0.1), ('gato', 0.02), ('en', 0.02), ('ventana', 0.02), ('y', 0.02), ('a', 0.34), ('pájaro', 0.32)]
    ```
