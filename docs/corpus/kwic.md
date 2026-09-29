# KWIC concordance

!!! info ""
    **ests.corpus.kwic()**, **ests.corpus.format_kwic()**, **ests.corpus.print_kwic()**, **ests.corpus.Concordance**

## Description

--8<-- "corpus/kwic.md:kwic"

## Language hooks

The function calls the `kwic` of the [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) core with the hooks of Spanish. The text and the keyword are split into words the same way, by the tokenizer of the blank Spanish pipeline, so `EE. UU.` is one word in both, and punctuation and symbols are words of neither: `¿Dónde` finds `Dónde`, `20 €` finds `20`. The word forms and the lemmas are lower-cased; accents are part of the word form: `solo` and `sólo` are two forms. The sentences of a string, and of the text of a `Doc` without boundaries, are those of [`SentsExtractor`](../extractors/sentences.md): an ellipsis or an exclamation followed by a lower-case word does not end a sentence, so `honrado piensa` finds `honrado... piensa`.

By lemma, the keyword is lemmatized by simplemma, so a phrase is given by lemmas - `mirar a el pájaro` - or as it is written, and a word of the text is found by its lemma of simplemma and, in a `Doc` that carries lemmas, by the lemma of the model as well: `gatos` is found by `gato`. In `Mi amigo vino con una botella de vino` the model gives `venir` to the verb, so `venir` finds the verb, where simplemma, which sees no context, would find nothing; `vino` finds both, since simplemma reads the verb as `vino`.

## Parameters

--8<-- "corpus/kwic.md:kwic-parameters"

--8<-- "corpus/kwic.md:format_kwic"

--8<-- "corpus/kwic.md:print_kwic"

## Result

--8<-- "corpus/kwic.md:Concordance"

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
