# Collocations

!!! info ""
    **ests.corpus.collocations()**, **ests.corpus.Collocation**

## Description

Collocation extraction - pairs of words that occur together more often than independence would give: fixed expressions (`punto de vista`, `llevar a cabo`), terminology, the combinatorics of a word. The measures of association are those of [Sketch Engine](https://www.sketchengine.eu/wp-content/uploads/ske-statistics.pdf) and of [`nltk.metrics.association`](https://www.nltk.org/api/nltk.metrics.association.html), and the tests check them against NLTK.

Pairs of words are ordered, as in NLTK: the right word occurs no more than `window` words after the left one, and every pair of positions is counted once; `window=1` gives bigrams. Inside the measure the frequency of a pair is divided by the size of the window (Church and Hanks 1990, as in NLTK), so that the expected frequency does not depend on the window and Dice and the minimum sensitivity do not exceed one; the field `freq_pair` keeps the undivided frequency. With `window > 1` the scale of the Dice measures therefore shifts: a pair always side by side gets a logDice of $14 - \log_2 window$ - 13 at a window of 2, 11.68 at 5 - and not 14, as bigrams and Sketch Engine, which computes logDice from the raw co-occurrence, give it; the maximum of 14 is reached only by a pair that occurs at every distance within the window. The parameter `node` keeps the pairs with the given word on the left or on the right - the combinatorics of one word.

Words are compared as they are: case, lemmatization and stop words belong to [`WordsExtractor`](../extractors/words.md); lemmas suit fixed expressions, word forms suit grammatical constructions.

## Measures

For a pair of words of frequencies $f_a$ and $f_b$, a pair frequency $f_{ab}$ and a number of words $N$:

| Measure | Key | Formula | Description |
| :------ | :-- | :------ | :---------- |
| Mutual information | `mi` | $\log_2 \frac{f_{ab} N}{f_a f_b}$ | Church and Hanks (1990); overrates rare pairs |
| MI³ | `mi3` | $\log_2 \frac{f_{ab}^3 N}{f_a f_b}$ | Oakes (1998); favours frequent pairs |
| t-score | `t_score` | $\frac{f_{ab} - f_a f_b / N}{\sqrt{f_{ab}}}$ | Church et al. (1991); favours frequent pairs |
| Dice coefficient | `dice` | $\frac{2 f_{ab}}{f_a + f_b}$ | does not depend on the size of the text |
| logDice | `logdice` | $14 + \log_2 \frac{2 f_{ab}}{f_a + f_b}$ | [Rychlý (2008)](https://www.sketchengine.eu/glossary/logdice/); does not depend on the size of the text, at most 14 (for a window $14 - \log_2 window$), below zero - a weak link; the default measure, as in Sketch Engine |
| Log-likelihood | `log_likelihood` | $G^2 = 2 \sum O \ln \frac{O}{E}$ | Dunning (1993); over the 2×2 contingency table, `nan` if one of the words fills the whole text |
| NPMI | `npmi` | $\frac{MI}{-\log_2 (f_{ab} / N)}$ | Bouma (2009); from −1 to 1, one means the words occur only together |
| Minimum sensitivity | `min_sensitivity` | $\min(\frac{f_{ab}}{f_a}, \frac{f_{ab}}{f_b})$ | Pedersen (1998); from 0 to 1 |

The measures are available as the functions `calc_mi`, `calc_mi3`, `calc_t_score`, `calc_dice`, `calc_logdice`, `calc_log_likelihood`, `calc_npmi`, `calc_min_sensitivity` with the arguments `(freq_a, freq_b, freq_ab, n)` of the module `ests.corpus.collocations` (`from ests.corpus.collocations import calc_logdice`); their names and descriptions are in `ests.constants.COLLOCATION_MEASURES`.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `words` | list[str] | `-` | Words of the text in order |
| `window` | int | `5` | Greatest distance between the words of a pair |
| `measure` | str | `logdice` | Measure of `COLLOCATION_MEASURES` |
| `min_freq` | int | `2` | Minimum frequency of a pair |
| `node` | str | `None` | Word whose combinatorics is needed; `None` - every pair |
| `top_n` | int | `None` | Number of collocations; `None` - all of them |

## Result

A list of `Collocation` named tuples by descending measure and frequency of the pair (ties broken alphabetically); `pd.DataFrame(found)` gives a table.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `left` | str | Left word |
| `right` | str | Right word, occurring within the window after the left one |
| `freq_left` | int | Frequency of the left word |
| `freq_right` | int | Frequency of the right word |
| `freq_pair` | int | Frequency of the co-occurrence |
| `score` | float | Value of the chosen measure |

## Example

!!! example "Example"

    ``` python
    from ests import WordsExtractor
    from ests.corpus import collocations

    words = WordsExtractor(use_lexemes=True, lowercase=True).extract(
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )

    collocations(words, window=2, top_n=1)
    # [Collocation(left='en', right='ventana', freq_left=3, freq_right=3, freq_pair=3, score=13.0)]

    [
        (c.left, c.right, round(c.score, 2))
        for c in collocations(words, window=1, node="gato", min_freq=1, measure="mi")[:2]
    ]
    # [('gato', 'volver', 3.62), ('gato', 'estar', 2.62)]
    ```
