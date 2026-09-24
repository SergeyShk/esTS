# Resources

## connectors.tsv

255 Spanish discourse markers with their class and kind, compiled for the library by the classification of Martín Zorraquino and Portolés (1999); used by `CohesionStats`.

## google_books_top10000.txt

The 10,000 most frequent Spanish lemmas, one per line in the order of decreasing frequency; used by `LexicalStats` for the frequency bands.

Derived from the Spanish corpus of Google Books Ngram, version 20200217, 1-grams (https://storage.googleapis.com/books/ngrams/books/datasetsv3.html), licensed under the Creative Commons Attribution 3.0 Unported License (https://creativecommons.org/licenses/by/3.0/); this file is distributed under the same licence.

Changes: the forms tagged with a part of speech of the years 1980-2019 were lower-cased, lemmatized by simplemma 2.0.0 and summed by lemma over the parts of speech; the proper nouns (nouns written with a capital letter in 90% of their occurrences), the letters other than the Spanish words (a, e, o, u, y, á, é, ó) and the lemmas of two letters and Roman numerals unknown to simplemma were left out. The list is built by `scripts/build_freq_dict.py` together with the frequency dictionary `FreqDict`.

Source: Michel J.-B. et al. Quantitative analysis of culture using millions of digitized books. Science 331 (6014), 2011.
