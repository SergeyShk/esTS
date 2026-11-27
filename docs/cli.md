# Command line

The command `ests` counts the statistics of texts without Python code: it prints them as a table, JSON or CSV, for the whole text or its parts, writes an HTML report and downloads the frequency dictionary. It is installed with the library; `python -m ests` is the same.

``` bash
ests download
ests stats texto.txt
ests stats -f json capitulo1.txt capitulo2.txt
ests stats -s basic,readability -p sentences -f csv -o oraciones.csv texto.txt
cat texto.txt | ests stats -f json
ests report texto.txt -t "Mi texto" -o informe.html
```

## Command { #Command }

--8<-- "cli.md:Command"

In esTS anySeg splits the text and esMorph analyzes it in the context of its sentences once for all the classes, without spaCy, and the classes of `-s` are:

| Name | Class |
| :--- | :---- |
| `basic` | [`BasicStats`](stats/basic_stats.md) |
| `readability` | [`ReadabilityStats`](stats/readability_stats.md) |
| `unadapted_readability` | [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md) |
| `diversity` | [`DiversityStats`](stats/diversity_stats.md) |
| `morph` | [`MorphStats`](stats/morph_stats.md) |
| `lexical` | [`LexicalStats`](stats/lexical_stats.md) |
| `style` | [`StyleStats`](stats/style_stats.md) |
| `phon` | [`PhonStats`](stats/phon_stats.md) |
| `cohesion` | [`CohesionStats`](stats/cohesion_stats.md) |
| `verse` | [`VerseStats`](stats/verse_stats.md), only by its name in `-s` |

The command has no syntactic statistics, as it parses no dependencies, and `cohesion` reads the analyses of esMorph without a parse: the [`si` that opens no condition](stats/cohesion_stats.md#is_connector_blocked) is known after an opening `¡` and after a verb that takes an indirect question, with a clitic joined to the verb (`indíquelo si es necesario`) as the only complement it sees. Its words are those of anySeg and esMorph, with the contractions and the clitics split (`del` as `de el`), where `CohesionStats(text)` in Python reads the words of a spaCy `Doc`: on 30 fragments of the [corpus of literature](datasets/spanishliterature.md) the argument overlap of the command is 10-19% higher, the share of the pronouns 7-9% higher and the connectors per 1000 words 3% lower, while the overlap of the content words and of the nouns is the same. `ests download` downloads the [frequency dictionary](datasets/freqdict.md) `freq_dict` for `lexical`; without it the class is not counted, and its error names this command.

## Report { #Report }

--8<-- "report.md:Report"

In esTS `Report` is in `ests.report`: its classes are `STATS_CLASSES` of the same module, the classes of the command but `verse`; a string is analyzed as by the command; the columns of the sentences are the characters, the words, the syllables, the Flesch reading ease and the water; the highlighting is [`HighlightedText`](visualizers/highlight.md) with its default layers. The texts of the report are in English, as those of `print_stats`, and the readings keep the names of the bands of their scales (`bastante fácil`).

=== "Code"

    ``` python
    from ests.report import Report

    report = Report(
        "El gato duerme en la ventana. El perro ladra en el patio.",
        title="Dos oraciones",
        skip_errors=True,
    )
    report.save("informe.html")
    report.stats["basic"].n_words, len(report.document.sentences)
    ```

=== "Result"

    ```
    (12, 2)
    ```
