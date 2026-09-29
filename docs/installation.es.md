# Instalación

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.8 o superior
*   [`anyts`](https://sergeyshk.github.io/anyTS/) 0.2.3 o superior dentro de 0.2, el núcleo independiente del idioma: los extractores, las estadísticas básicas y las fórmulas comunes de legibilidad, las métricas de diversidad léxica, las medidas de corpus, los gráficos y el mecanismo del resaltado vienen de él con el tokenizador, el lematizador, el segmentador de oraciones y las sílabas del español
*   `numpy`, `scipy`, `pandas`, `simplemma` 2
*   `matplotlib` y `graphviz` para las [visualizaciones](visualizers/zipf.md)

Las dependencias se instalan con el paquete. El [árbol de palabras](visualizers/word_tree.md) y la [red de colocaciones](visualizers/corpus.md#collocation_network) los dibujan los ejecutables de [Graphviz](https://graphviz.org/download/), que se instalan aparte (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`).

## Desde PyPI

La distribución en PyPI se llama `pyests` y el paquete que instala es `ests`:

``` bash
pip install pyests
```

## Desde el repositorio

``` bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS
uv sync --all-groups
```

## El modelo de spaCy { #model }

Las estadísticas básicas, la legibilidad, la diversidad léxica, las métricas de estilo salvo los sustantivos deverbales, la fonoestadística y las estadísticas del verso no necesitan ningún modelo entrenado. Las [estadísticas morfológicas](stats/morph_stats.md), las [sintácticas](stats/syntax_stats.md) (con analizador), las [de cohesión](stats/cohesion_stats.md) y las [de complejidad léxica](stats/lexical_stats.md) de una cadena sí lo necesitan, igual que los sustantivos deverbales de las [métricas de estilo](stats/style_stats.md), [`function_words_profile`](corpus/stylometry.md), los rasgos de un texto, la [comparación de corpus](corpus/compare.md) y construir un `Doc` por su cuenta. Las pruebas también lo necesitan; lo instala el grupo de dependencias `test`:

``` bash
python -m spacy download es_core_news_sm
```

## Conjuntos de datos { #datasets }

El [corpus de literatura](datasets/spanishliterature.md), los [sonetos](datasets/spanishsonnets.md) y el [diccionario de frecuencias](datasets/freqdict.md) se descargan una vez con su método `download()`; las estadísticas de [`LexicalStats`](stats/lexical_stats.md) según el diccionario y [`keyness`](corpus/keyness.md) frente a él necesitan `FreqDict().download()`. Los archivos van al directorio `ests_data` junto al paquete instalado (`ests.constants.DEFAULT_DATA_DIR`), `dicts` para el diccionario y `texts` para el corpus y los sonetos. Donde ese directorio no se puede escribir, pase otro en `data_dir` (`FreqDict(data_dir="...")`) o defina la variable de entorno `ESTS_DATA_DIR` antes de importar el paquete:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
