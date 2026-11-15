# Components

``` {.python .signature}
StatsComponent(nlp, name)
```

--8<-- "components.md:StatsComponent"

The components of esTS are subclasses of the `StatsComponent` of the [anyTS](https://sergeyshk.github.io/anyTS/components/) core, one for every class of statistics.

!!! note "Note"
    The examples below use the model `es_core_news_sm`, which is installed apart: `python -m spacy download es_core_news_sm` (see [installation](installation.md)).

=== "Code"

    ``` python
    import ests

    nlp = ests.load_pipeline()
    nlp.add_pipe("ests_basic", name="basic")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.basic.n_words, doc._.basic.c_letters
    nlp("?!")._.basic is None
    ```

=== "Result"

    ```
    (12, {2: 5, 3: 1, 4: 1, 5: 1, 6: 3, 7: 1})
    True
    ```

## Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `nlp` | `Language` | - | Pipeline the component is added to |
| `name` | `str` | - | Name of the component in the pipeline and of the extension |

spaCy sets both at `nlp.add_pipe(factory, name=...)`; the other parameters of a component are passed in the `config` dictionary of the same call.

## Names { #names }

The factories carry the prefix of the library: `ests_basic`, `ests_readability`, `ests_unadapted_readability`, `ests_diversity`, `ests_morph`, `ests_syntax`, `ests_cohesion`, `ests_lexical`, `ests_style`, `ests_phon`, `ests_verse`. They are declared as entry points of `spacy_factories`, so a pipeline saved with these components (`nlp.to_disk(path)`, `spacy package`) loads with `spacy.load(path)` without importing the library. `import ests` does not load the components while spaCy is not loaded - the entry points find them, and `ests.StyleStatsComponent` loads them on first use; from the sources without an installed package, `import ests.components` comes before `add_pipe`.

--8<-- "components.md:StatsComponent-names"

In `ests_lexical` a document of numbers alone passes untouched as well, and in `ests_verse` a document without letters.

--8<-- "components.md:StatsComponent-serialization"

A component reads the `Doc` of its pipeline as it is and leaves its tokenizer alone: the words and the sentences of the string API come with the pipeline of [`load_pipeline`](#load_pipeline), where `sí--dijo` is two words and a dash and a blank line ends a sentence.

## Components of the classes of statistics { #class-components }

| Component | Factory | Class of statistics | Parameters |
| :-------- | :------ | :------------------ | :--------- |
| [`BasicStatsComponent`](#BasicStatsComponent) | `ests_basic` | [`BasicStats`](stats/basic_stats.md) | - |
| [`ReadabilityStatsComponent`](#ReadabilityStatsComponent) | `ests_readability` | [`ReadabilityStats`](stats/readability_stats.md) | `preset`, `basic` |
| [`UnadaptedReadabilityStatsComponent`](#UnadaptedReadabilityStatsComponent) | `ests_unadapted_readability` | [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md) | `basic` |
| [`DiversityStatsComponent`](#DiversityStatsComponent) | `ests_diversity` | [`DiversityStats`](stats/diversity_stats.md) | `window_len`, `mtld_threshold`, `mtld_min_len`, `hdd_sample_size`, `log_base` |
| [`MorphStatsComponent`](#MorphStatsComponent) | `ests_morph` | [`MorphStats`](stats/morph_stats.md) | - |
| [`SyntaxStatsComponent`](#SyntaxStatsComponent) | `ests_syntax` | [`SyntaxStats`](stats/syntax_stats.md) | - |
| [`CohesionStatsComponent`](#CohesionStatsComponent) | `ests_cohesion` | [`CohesionStats`](stats/cohesion_stats.md) | `blank_lines` |
| [`LexicalStatsComponent`](#LexicalStatsComponent) | `ests_lexical` | [`LexicalStats`](stats/lexical_stats.md) | `data_dir` |
| [`StyleStatsComponent`](#StyleStatsComponent) | `ests_style` | [`StyleStats`](stats/style_stats.md) | `stopwords`, `top_n`, `nausea_stopwords`, `cliches` |
| [`PhonStatsComponent`](#PhonStatsComponent) | `ests_phon` | [`PhonStats`](stats/phon_stats.md) | `window_len` |
| [`VerseStatsComponent`](#VerseStatsComponent) | `ests_verse` | [`VerseStats`](stats/verse_stats.md) | `seseo` |

The basic, readability, diversity, phonetic and verse statistics and the formulas of other languages need no annotation of a model. In the pipeline of `es_core_news_sm` the parts of speech come from the `morphologizer` (or a `tagger` with an `attribute_ruler`; a `tagger` alone does not give them), the parse from the `parser` and the lemmas from the `lemmatizer`. A component whose annotation is missing, `excluded` components included, raises `SourceError` when the document goes through it; `ests_lexical` needs only the parts of speech, and `ests_style` raises when `verbal_nouns` or `markers()` is read.

### Basic statistics { #BasicStatsComponent }

``` {.python .signature}
BasicStatsComponent(nlp, name)
```

--8<-- "components.md:BasicStatsComponent"

### Readability metrics { #ReadabilityStatsComponent }

``` {.python .signature}
ReadabilityStatsComponent(nlp, name, preset=None, basic=None)
```

--8<-- "components.md:ReadabilityStatsComponent"

The [presets](stats/readability_stats.md#presets) of esTS are `general` and `classic`, the preset of the class `general`. In esTS the class of statistics and its `basic_stats_class` are set, so the errors of `stats_class` and `SourceTypeError` do not occur. The component named by `basic` comes before this one in the pipeline; the message of `SourceError` names the component `ests_basic` (`basic_factory`) to add there.

=== "Code"

    ``` python
    nlp.add_pipe("ests_readability", name="readability")
    config = {"preset": "classic", "basic": "basic"}
    nlp.add_pipe("ests_readability", name="readability_classic", config=config)
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.readability.flesch_reading_easy, 2)
    round(doc._.readability_classic.flesch_reading_easy, 2)
    ```

=== "Result"

    ```
    102.19
    105.72
    ```

### Formulas of other languages { #UnadaptedReadabilityStatsComponent }

``` {.python .signature}
UnadaptedReadabilityStatsComponent(nlp, name, basic=None)
```

--8<-- "components.md:UnadaptedReadabilityStatsComponent"

The formulas are those of [`UnadaptedReadabilityStats`](stats/unadapted_readability_stats.md), with their own coefficients and no calibration for Spanish. As for `ReadabilityStatsComponent`, the errors of `stats_class` and `SourceTypeError` do not occur in esTS, and the message of `SourceError` names the component `ests_basic` to add before it.

=== "Code"

    ``` python
    nlp.add_pipe("ests_unadapted_readability", name="unadapted", config={"basic": "basic"})
    doc = nlp(
        "El gato estaba en la ventana y miraba a los pájaros que volaban "
        "sobre los tejados de las casas."
    )
    doc._.unadapted.gulpease, doc._.unadapted.forcast
    doc._.unadapted.bs is doc._.basic
    ```

=== "Result"

    ```
    (64.78947368421052, 12.105263157894736)
    True
    ```

### Lexical diversity metrics { #DiversityStatsComponent }

``` {.python .signature}
DiversityStatsComponent(nlp, name, window_len=50, mtld_threshold=0.72, mtld_min_len=10, hdd_sample_size=42, log_base=10)
```

--8<-- "components.md:DiversityStatsComponent"

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `window_len` | `int` | `50` | Window size for MATTR and segment size for MSTTR |
| `mtld_threshold` | `float` | `0.72` | TTR threshold for MTLD, MA-MTLD and MTLD-W |
| `mtld_min_len` | `int` | `10` | Minimum factor length for MTLD, MA-MTLD and MTLD-W |
| `hdd_sample_size` | `int` | `42` | Sample size for HD-D |
| `log_base` | `float` | `10` | Logarithm base for the Summer, Maas and Dugast metrics |

=== "Code"

    ``` python
    config = {"window_len": 100, "log_base": 2.718281828459045}
    nlp.add_pipe("ests_diversity", name="diversity", config=config)
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    round(doc._.diversity.ttr, 3), round(doc._.diversity.sttr, 3)
    ```

=== "Result"

    ```
    (0.833, 0.916)
    ```

### Morphological statistics { #MorphStatsComponent }

``` {.python .signature}
MorphStatsComponent(nlp, name)
```

--8<-- "components.md:MorphStatsComponent"

In esTS the pipeline needs a `lemmatizer` before the component as well; the factory requires `token.pos` and `token.lemma`, so `nlp.analyze_pipes()` names a pipeline without one of them.

Raises:

- `SourceError` - a document without the parts of speech or the lemmas.

=== "Code"

    ``` python
    nlp.add_pipe("ests_morph", name="morph")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.morph.pos[:4]
    ```

=== "Result"

    ```
    ('DET', 'NOUN', 'VERB', 'ADP')
    ```

### Syntactic statistics { #SyntaxStatsComponent }

``` {.python .signature}
SyntaxStatsComponent(nlp, name)
```

--8<-- "components.md:SyntaxStatsComponent"

In esTS they need a `lemmatizer` before it as well; the factory requires `token.dep`, `token.head`, `token.pos` and `token.lemma`, so `nlp.analyze_pipes()` names a pipeline without one of them.

Raises:

- `SourceError` - a document without a dependency parse, the parts of speech or the lemmas.

=== "Code"

    ``` python
    nlp.add_pipe("ests_syntax", name="syntax")
    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    doc._.syntax.tree_depth, doc._.syntax.mean_dependency_distance
    ```

=== "Result"

    ```
    (2.0, 1.6)
    ```

### Cohesion statistics { #CohesionStatsComponent }

``` {.python .signature}
CohesionStatsComponent(nlp, name, blank_lines=False)
```

--8<-- "components.md:CohesionStatsComponent"

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `blank_lines` | `bool` | `False` | Start the paragraphs after the blank lines alone, for a text whose lines are wrapped inside its paragraphs; after every line break by default |

In the pipeline of `es_core_news_sm` the parts of speech and the lemmas come from the `morphologizer` and the `lemmatizer`; the factory requires `token.pos` and `token.lemma`, so `nlp.analyze_pipes()` names a pipeline without one of them, and a document without them raises `SourceError`. The texts of [`SpanishLiterature`](datasets/spanishliterature.md) are wrapped inside their paragraphs and need `blank_lines`.

=== "Code"

    ``` python
    nlp.add_pipe("ests_cohesion", name="cohesion")
    nlp.add_pipe("ests_cohesion", name="paragraphs", config={"blank_lines": True})
    doc = nlp("El informe fue aprobado. Sin embargo, el informe\nno resuelve el problema.")
    (
        doc._.cohesion.noun_overlap_adjacent,
        round(doc._.cohesion.connectors, 2),
        doc._.cohesion.n_paragraphs,
        doc._.paragraphs.n_paragraphs,
    )
    ```

=== "Result"

    ```
    (1.0, 83.33, 2, 1)
    ```

### Lexical sophistication statistics { #LexicalStatsComponent }

``` {.python .signature}
LexicalStatsComponent(nlp, name, data_dir=None)
```

--8<-- "components.md:LexicalStatsComponent"

In esTS `freq_dict` is the [frequency dictionary](datasets/freqdict.md) `FreqDict` of the directory `data_dir`, and `is_number` takes the numbers of the Spanish `NUMBER_PATTERN` (`2020`, `1.500,50`, `3.º`). The pipeline needs a `morphologizer` before the component, and the factory requires `token.pos`; the lemmas of the model are not used. The frequency bands and the lexical density are computed without the dictionary, the statistics by the dictionary need it downloaded.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `data_dir` | `str` | `None` | Directory of the frequency dictionary; the default one if not given |

Raises:

- `SourceError` - a document without the parts of speech;
- `DatasetNotFoundError` - the statistics by the dictionary and `get_stats()` when the dictionary is not downloaded;
- `ParameterError` - a `data_dir` that is not a string.

=== "Code"

    ``` python
    nlp.add_pipe("ests_lexical", name="lexical")
    doc = nlp("El felinólogo examinaba al minino con parsimonia.")
    round(doc._.lexical.coverage, 3), round(doc._.lexical.p_top1000, 3)
    nlp("2020 1.500,50 3.º")._.lexical is None
    ```

=== "Result"

    ```
    (0.857, 0.429)
    True
    ```

### Style metrics { #StyleStatsComponent }

``` {.python .signature}
StyleStatsComponent(nlp, name, stopwords=None, top_n=10, nausea_stopwords=None, cliches=None)
```

--8<-- "components.md:StyleStatsComponent"

Without the lists the water content takes the stopwords of `STOPWORDS` and the one-word parenthetical expressions, the academic nausea leaves out the words of `is_stopword`, and the clichés come from `OFFICIALESE_CLICHES`; `NAUSEA_TOP_N` is a constant of `anyts.constants`. The verbal nouns need a `morphologizer` and a `lemmatizer` before the component, and without them reading `verbal_nouns`, `markers()` or `get_stats()` raises `SourceError`; the other metrics read the words alone.

=== "Code"

    ``` python
    nlp.add_pipe("ests_style", name="style")
    doc = nlp("Se procedió a la revisión del expediente a la mayor brevedad.")
    round(doc._.style.cliches, 2), round(doc._.style.verbal_nouns, 2)
    nlp.add_pipe("ests_style", name="style_cliches", config={"cliches": ["se procedió a"]})
    doc = nlp("Se procedió a la revisión del expediente a la mayor brevedad.")
    round(doc._.style_cliches.cliches, 2)
    ```

=== "Result"

    ```
    (18.18, 33.33)
    9.09
    ```

### Phonostatistics { #PhonStatsComponent }

``` {.python .signature}
PhonStatsComponent(nlp, name, window_len=3)
```

--8<-- "components.md:PhonStatsComponent"

=== "Code"

    ``` python
    nlp.add_pipe("ests_phon", name="phon", config={"window_len": 5})
    doc = nlp("Tres tristes tigres tragaban trigo en un trigal")
    round(doc._.phon.hardness, 3), round(doc._.phon.alliteration, 3)
    ```

=== "Result"

    ```
    (0.458, 0.975)
    ```

### Verse statistics { #VerseStatsComponent }

``` {.python .signature}
VerseStatsComponent(nlp, name, seseo=False)
```

`VerseStatsComponent` puts the verse statistics into the extension. The statistics read the line breaks and blank lines of the document, so pass the text of a poem to `nlp` with its lines not joined; the component needs no annotation of a model. A document with no letter passes untouched, and a text with letters but no Spanish syllables gives empty statistics.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `seseo` | `bool` | `False` | Pronounce `c` and `z` before `e` and `i` as `s` in the rhyme |

Raises:

- `ParameterError` - a `seseo` that is not a boolean.

=== "Code"

    ``` python
    nlp.add_pipe("ests_verse", name="verse")
    doc = nlp(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    doc._.verse.meter, doc._.verse.c_clausulas
    ```

=== "Result"

    ```
    ('octosílabo', {'aguda': 2, 'llana': 2})
    ```

## Recommended pipeline { #load_pipeline }

``` {.python .signature}
load_pipeline(model='es_core_news_sm', exclude=(), **kwargs)
```

A spaCy model with the tokenizer `anyseg.Tokenizer.v1` and the component `anyseg_sentencizer` first, both of [anySeg](https://github.com/SergeyShk/anySeg): the tokens and the sentences of a `Doc` are those the [extractors](extractors/sentences.md) give its text, so the statistics of a `Doc` and of the string count the same words and sentences. The tags, the lemmas, the parser and the other components are the model's. A contraction (`del`, `al`) is one token, with its words in `token._.anyseg_words`. A saved pipeline loads with `spacy.load(path)`, as the factories of anySeg are entry points. `ests.utils.get_nlp`, which parses the strings of the morphological, syntactic, cohesion, lexical and style statistics, loads it once per process and model.

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `model` | `str` | `'es_core_news_sm'` | Name or path of a spaCy model: `es_core_news_sm`, `es_core_news_md`, `es_core_news_lg` |
| `exclude` | `str` / `list[str]` | `()` | Components of the model not to load, e.g. `ner` |
| `**kwargs` | | | The other parameters of `spacy.load`; the tokenizer of `config` is replaced by that of anySeg |

Raises:

- `DatasetNotFoundError` - a model that is not installed.

A pipeline of one's own, such as `spacy.load("es_core_news_sm")`, keeps the tokenizer of spaCy: `sí--dijo` is one token there, and the parser joins a paragraph without a final mark to the next sentence across a blank line, so the statistics of its `Doc` differ from those of the string.

=== "Code"

    ``` python
    import ests

    nlp = ests.load_pipeline()
    doc = nlp("Novedades\n\nImportación rápida. Menos errores\n\n--Sí --dijo él. Vino del pueblo.")
    [sent.text.strip() for sent in doc.sents]
    [(token.text, token._.anyseg_words) for token in doc if token.text == "del"]
    ```

=== "Result"

    ```
    ['Novedades', 'Importación rápida.', 'Menos errores', '--Sí --dijo él.', 'Vino del pueblo.']
    [('del', [{'form': 'de'}, {'form': 'el'}])]
    ```

## Everything in one pipeline { #pipeline }

The eleven components can share one pipeline.

=== "Code"

    ``` python
    import ests

    nlp = ests.load_pipeline()
    factories = (
        "basic",
        "readability",
        "unadapted_readability",
        "diversity",
        "morph",
        "syntax",
        "cohesion",
        "lexical",
        "style",
        "phon",
        "verse",
    )
    for factory in factories:
        nlp.add_pipe(f"ests_{factory}", name=factory)

    doc = nlp("El gato duerme en la ventana. Los niños juegan en el parque.")
    (
        doc._.basic.n_words,
        round(doc._.readability.flesch_reading_easy, 2),
        round(doc._.unadapted_readability.gulpease, 2),
        round(doc._.diversity.ttr, 3),
        doc._.morph.pos[:2],
        doc._.syntax.tree_depth,
        doc._.cohesion.p_given,
        round(doc._.lexical.p_top1000, 3),
        round(doc._.style.water, 2),
        round(doc._.phon.p_vowels, 3),
        doc._.verse.n_lines,
    )
    ```

=== "Result"

    ```
    (12, 102.19, 99.83, 0.833, ('DET', 'NOUN'), 2.0, 0.0, 0.667, 50.0, 0.457, 1)
    ```
