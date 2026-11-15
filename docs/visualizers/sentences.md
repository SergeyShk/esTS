# Sentence lengths

``` {.python .signature}
sentence_lengths_plot(source, window=10, inset=True, ax=None, labels=None, sents_extractor=None, words_extractor=None)
```

--8<-- "visualizers/sentences.md:sentence_lengths_plot"

The functions are those of the [anyTS](https://sergeyshk.github.io/anyTS/visualizers/sentences/) core; by default esTS reads the sentences of the document of a string, a `Doc` or a `Document` (the segmenter [anySeg](https://github.com/SergeyShk/anySeg)) and their words with a letter or a digit; with the `sents_extractor` or `words_extractor` parameter a string or a `Doc` without sentences is split by the extractors, the Spanish [`SentsExtractor`](../extractors/sentences.md) and [`WordsExtractor`](../extractors/words.md) for the one not given, while a `Doc` with sentences and a `Document` keep theirs. The default labels are the English ones of `VISUALIZER_LABELS` in `anyts.constants`; `labels` replaces any of them.

The curve of the second window of 2000 words of *Niebla* by Unamuno from the [corpus of literature](../datasets/spanishliterature.md); a window is cut by words, so it opens with the end of a sentence:

``` python
from ests.corpus import split_windows
from ests.datasets import SpanishLiterature
from ests.visualizers import sentence_lengths_plot

sl = SpanishLiterature()
sl.download()
text = next(
    record["text"] for record in sl.get_records(author="unamuno") if record["title"] == "Niebla"
)
chapter = split_windows(text, 2000)[1]
sentence_lengths_plot(chapter, window=10)
```

![ests](../img/sentences.png){: .center }

## Parameters

--8<-- "visualizers/sentences.md:sentence_lengths_plot-parameters"

## Lengths of the sentences { #sentence_lengths }

``` {.python .signature}
sentence_lengths(source, sents_extractor=None, words_extractor=None)
```

The lengths of the sentences in words, in order: the sentences of the document of a string, a `Doc` or a `Document` and their words with a letter or a digit, or, with an extractor, the sentences of the sentence extractor and their words of the word extractor on a string or a `Doc` without sentences; a `Doc` with sentences and a `Document` keep theirs. Sentences without words are skipped. Ready lengths (non-negative integers in a sequence or an iterator) are used as they are. The arguments are those of `sentence_lengths_plot`.

Raises:

- `SourceTypeError` - an object that is not a string, a `Doc`, a `Document`, a sequence or an iterator, a table, a set, a mapping, bytes, a length that is not an integer, an extractor of another type;
- `SourceError` - a negative length.

=== "Code"

    ``` python
    from ests.visualizers import sentence_lengths

    sentence_lengths("El gato duerme. ¿Y el perro? —Come —dijo ella.")
    sentence_lengths(chapter)[:5]
    ```

=== "Result"

    ```
    [3, 3, 3]
    [1, 30, 41, 41, 14]
    ```
