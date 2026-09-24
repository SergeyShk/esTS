# KWIC concordance

!!! info ""
    **ests.corpus.kwic()**, **ests.corpus.format_kwic()**, **ests.corpus.print_kwic()**, **ests.corpus.Concordance**

## Description

A KWIC concordance (keyword in context) - every occurrence of a word or a phrase with its context on the left and on the right, as in [AntConc](https://www.laurenceanthony.net/software/antconc/) and textacy `keyword_in_context`. It shows how a word is used in a text: what it combines with, in which forms and senses.

The occurrences are looked for among the words of the text: by the word form ignoring case, respecting it (`ignore_case=False`) or by the lemma (`by_lemma=True`: `gatos` is found by `gato`, a phrase is given by lemmas - `mirar a el pájaro` - or as it is written, since every word of it is lemmatized). The text and the keyword are split into words the same way, by the tokenizer of the blank Spanish pipeline, so `EE. UU.` is one word in both, and punctuation and symbols are words of neither: `¿Dónde` finds `Dónde`, `20 €` finds `20`. Accents are part of the word form: `solo` and `sólo` are two forms.

By lemma, the keyword is lemmatized by simplemma, and a word of the text is found by its lemma of simplemma and, in a `Doc` that carries lemmas, by the lemma of the model as well. The two lemmatizers err in different places, and each covers the other: in `Mi amigo vino con una botella de vino` the model gives `venir` to the verb and `vino` to the noun, so `venir` finds the verb alone, where simplemma, which sees no context, would find nothing; in `¿Dónde pusiste las llaves?` the model reads `pusiste` as `pusistar`, and simplemma lets `poner` find it anyway. The price is that `vino` finds the verb too, since simplemma reads it so.

The context is `window` words on each side as they are written in the text, with the punctuation between them; whitespace collapses into one space, and occurrences do not overlap.

`format_kwic` aligns the lines on the keyword: the left context is cut on the left and aligned to the right, the right one is cut on the right; `print_kwic` prints the result.

## Parameters

| Parameter | Type | Default | Description |
| :-------: | :--: | :-----: | :---------: |
| `source` | str/Doc | `-` | Text or Doc object |
| `keyword` | str | `-` | Word or phrase (words separated by spaces) |
| `window` | int | `5` | Number of words of context on each side |
| `by_lemma` | bool | `False` | Compare lemmas instead of word forms |
| `ignore_case` | bool | `True` | Ignore case when comparing word forms |

`format_kwic(concordances, width=40)` and `print_kwic(concordances, width=40)`: `width` is the width of a context in characters, at least one; line breaks inside the keyword phrase are replaced with spaces.

## Result

A list of `Concordance` named tuples in the order of the text.

| Field | Type | Description |
| :---: | :--: | :---------- |
| `start` | int | Position of the first character of the occurrence in the text |
| `end` | int | Position after the last character of the occurrence |
| `left` | str | Context on the left |
| `keyword` | str | Occurrence as written in the text |
| `right` | str | Context on the right |

## Example

!!! example "Example"

    ``` python
    from ests.corpus import kwic, print_kwic

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    lines = kwic(text, "ventana", by_lemma=True, window=3)
    lines[0]
    # Concordance(start=21, end=28, left='estaba en la', keyword='ventana', right='y miraba a')

    print_kwic(lines, width=20)
    #         estaba en la  ventana  y miraba a
    #         durmió en la  ventana  . Mañana el gato
    #          estar en la  ventana  y mirará a

    [line.keyword for line in kwic(text, "mirar a los pájaros", by_lemma=True)]
    # ['miraba a los pájaros', 'mirará a los pájaros']
    ```
