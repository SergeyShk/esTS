# Examples

Jupyter notebooks in the [examples/](https://github.com/SergeyShk/esTS/tree/master/examples) directory of the repository, with the library at work on its datasets. Each opens in Google Colab with a button and installs the library - esTS 0.9 or newer - and, if it needs it, the spaCy model; the outputs of all cells are stored in the files, so the notebooks can be read without running.

## Text walkthrough

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb) - a short story by Horacio Quiroga, *El almohadón de pluma*, through every tool of the library - extraction, syllables, the statistics of every class, the highlighting, the plots and the corpus measures - and the spaCy components over the 18 stories of the book into one table.

## Prose writers

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/02_prose_authors.ipynb)

[02_prose_authors.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/02_prose_authors.ipynb) - ten prose writers of `SpanishLiterature`: Burrows's and Cosine Delta between their works, the attribution of held-out works, Zeta and the chi-square of Kilgarriff for Galdós and Pardo Bazán, the comparison of Galdós and Blasco Ibáñez feature by feature and the Mendenhall curves.

## Sonnets

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/03_sonnets.ipynb)

[03_sonnets.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/03_sonnets.ipynb) - meter, types of the endecasílabo, rhyme schemes and sound of the 4,259 sonnets of `SpanishSonnets` from the 15th century to the 20th, checked against the annotation of DISCO, with the seseo of the American poets.

## Corpus measures

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/04_corpus_measures.ipynb)

[04_corpus_measures.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/04_corpus_measures.ipynb) - the prose of Spain and of Spanish America about 1900: keywords against each other and against the frequency dictionary, the dispersion of regional words, collocations, a concordance of voseo, the laws of Zipf and Heaps and the comparison of the corpora.

## Running locally

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

`make notebooks` runs every notebook again, writes the outputs into the files and strips the metadata of the run; a workflow runs them every week and fails when an output the prose quotes has moved.
