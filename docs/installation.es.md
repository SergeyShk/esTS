# Instalación

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.7 o superior
*   `numpy`, `scipy`, `pandas`, `simplemma` 2
*   `matplotlib` y `graphviz` para las [visualizaciones](visualizers/zipf.md)

Las dependencias se instalan con el paquete. `graphviz` es la interfaz de Python; el [árbol de palabras](visualizers/word_tree.md) y la [red de colocaciones](visualizers/corpus.md#collocation_network) los dibujan los ejecutables de [Graphviz](https://graphviz.org/download/), que se instalan aparte (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`).

## Desde PyPI

El distribuible en PyPI se llama `pyests` y el paquete que instala es `ests`:

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

Las estadísticas básicas, la legibilidad y la diversidad léxica no necesitan ningún modelo entrenado: las oraciones, las palabras y los N-gramas de caracteres se extraen por reglas y con el tokenizador del pipeline español vacío, y las sílabas y el acento por la ortografía. Las [estadísticas morfológicas](stats/morph_stats.md), las [sintácticas](stats/syntax_stats.md), las [de cohesión](stats/cohesion_stats.md) y las [de complejidad léxica](stats/lexical_stats.md) de una cadena sí lo necesitan - las sintácticas, un pipeline con analizador -, igual que el perfil de las palabras funcionales ([`function_words_profile`](corpus/stylometry.md)), los rasgos de un texto y la [comparación de corpus](corpus/compare.md), y construir un `Doc` para pasarlo a las estadísticas en lugar de una cadena; las pruebas también lo necesitan, donde viene con el grupo de dependencias `test`:

``` bash
python -m spacy download es_core_news_sm
```

## Conjuntos de datos { #datasets }

El [corpus de literatura](datasets/spanishliterature.md) y el [diccionario de frecuencias](datasets/freqdict.md) se descargan una vez con su método `download()`; las estadísticas de [`LexicalStats`](stats/lexical_stats.md) según el diccionario y [`keyness`](corpus/keyness.md) frente a él necesitan `FreqDict().download()`. Los archivos van al directorio `ests_data` junto al paquete instalado (`ests.constants.DEFAULT_DATA_DIR`), `dicts` para el diccionario y `texts` para el corpus. Donde ese directorio no se puede escribir - un Python del sistema, un entorno compartido - pase otro en `data_dir` (`FreqDict(data_dir="...")`) o defina la variable de entorno `ESTS_DATA_DIR` antes de importar el paquete:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
