# Word extraction

``` {.python .signature}
WordsExtractor(tokenizer=None, filter_punct=True, filter_nums=False, use_lexemes=False, stopwords=None, lowercase=False, ngram_range=(1, 1), min_len=0, max_len=0)
```

--8<-- "extractors/words.md:WordsExtractor"

The class extends the `WordsExtractor` of the [anyTS](https://sergeyshk.github.io/anyTS/extractors/words/) core with the hooks of Spanish:

| Hook | Spanish |
| :--- | :------ |
| `tokenize(text)` | the rule-based tokenizer of the spaCy Spanish language class, `ests.utils.tokenize` |
| `lemmatize(word)` | the lemmas of simplemma, `ests.utils.lemmatize` |
| `number_pattern` | signed numbers, ranges, fractions, dates, times, percentages and ordinals: `-5`, `+7`, `1990-1995`, `1.500,50`, `12/03/2020`, `3:30`, `10%`, `3.º`, `1.ª`, `2do` |

!!! note "Note"
    The tokenizer needs no trained model. Punctuation marks, including `¿` and `¡`, numbers like `1.500,50`, `3.º`, `1990-1995` and abbreviations like `Sr.`, `EE. UU.` are single tokens, and the abbreviations of `ests.constants.TOKENIZER_ABBREVIATIONS` in every case (`sr.`, `SR.`, `ee. uu.`, `Pág.`, `a.m.`); words with enclitic pronouns (`dámelo`) are not split. The dashes of a dialogue glued to the words are split off: `--No`, `sí--dijo`, `―dijo él―.` give the words `No`, `sí`, `dijo`, `él`, also next to the underscores of italics (`--_Siguro_`), while a hyphen between letters (`franco-alemán`) or before a digit (`-5`) stays in its token; a suffix quoted with its hyphen (`-mente`) loses it as well, and so does the number of an item of a list (`Artículo 1.- El objeto` gives the number `1`). A byte order mark at the start of a text, as in a file read with `utf-8` instead of `utf-8-sig`, is split off and dropped. `ests.utils.add_dash_rules(nlp)` adds the same rules to the ones a spaCy pipeline of one's own has; the model of `get_nlp` has them already, and the [components](../components.md) of the library add them to their pipeline.

!!! note "Note"
    [simplemma](https://github.com/adbar/simplemma) works from a dictionary without a trained model: a known form is mapped to its lower-case lemma (`Tienes` - `tener`, `NIÑOS` - `niño`), an unknown form is returned unchanged (`Madrid`, `dámelo`).

=== "Code"

    ``` python
    from ests import WordsExtractor

    text = "No tengas 100 euros, ten 100 amigos"

    we = WordsExtractor(use_lexemes=True, stopwords=["no"], filter_nums=True, ngram_range=(1, 2))
    we.extract(text)
    ```

=== "Result"

    ```
    ('tener', 'euro', 'tener', 'amigo', 'tener_euro', 'euro_tener', 'tener_amigo')
    ```

## Parameters

--8<-- "extractors/words.md:WordsExtractor-parameters"

!!! note "Note"
    A ready stop word list is `spacy.lang.es.stop_words.STOP_WORDS`; note that it also holds frequent verbs like `tener`.

## Methods

--8<-- "extractors/words.md:WordsExtractor-extract"

With the default tokenizer, a text with a character without a UTF-8 form, as a file read with the wrong encoding gives, raises `SourceError`, and so do the classes and functions that extract the words of a string with it.

--8<-- "extractors/words.md:WordsExtractor-get_most_common"

=== "Code"

    ``` python
    we.get_most_common(3)
    ```

=== "Result"

    ```
    [('tener', 2), ('euro', 1), ('amigo', 1)]
    ```
