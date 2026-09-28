---
title: esTS
emoji: 📊
colorFrom: red
colorTo: yellow
sdk: gradio
sdk_version: 6.28.0
python_version: "3.12"
app_file: app.py
pinned: false
license: mit
short_description: Statistics of Spanish texts and highlighting of fragments
---

# esTS

A demo of the [esTS](https://github.com/SergeyShk/esTS) library: paste a text in Spanish and get its
readability with the school stage and the age of the reader, lexical diversity, the morphological
and syntactic profile by the model `es_core_news_sm`, cohesion, word frequency by the dictionary of
Google Books Ngram, the SEO metrics of style, phonostatistics, the meter and rhyme of verse,
keywords and collocations, the plots of Zipf's law and of sentence lengths, and the highlighting
of the fragments these numbers come from: long sentences, complex words, passive voice, chains of
`de`, split predicates, clichés and alliterations.

The documentation of the library: <https://sergeyshk.github.io/esTS/>. The code of the demo lives
in the [`demo`](https://github.com/SergeyShk/esTS/tree/master/demo) folder of the repository and is
updated with every release.

To run it locally from the repository - `make demo`, to upload it to the Space - `make demo-login`
and `make demo-upload`. From a clone of the Space:

```bash
pip install -r requirements.txt
python app.py
```
