# Instalación

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.8.17 o superior dentro de 3
*   [`anyts`](https://sergeyshk.github.io/anyTS/) 0.6.4 o superior dentro de 0.6, el núcleo independiente del idioma: los extractores, las estadísticas básicas y las fórmulas comunes de legibilidad, las métricas de diversidad léxica, las medidas de corpus, los gráficos y el mecanismo del resaltado vienen de él con los ganchos del español: los tokens y las oraciones de anySeg, los lemas de esMorph, las sílabas de esTS
*   [`anyseg`](https://github.com/SergeyShk/anySeg) 0.4 o superior dentro de 0.4, el segmentador en tokens y oraciones
*   [`esmorph`](https://github.com/SergeyShk/esMorph) 0.4 o superior dentro de 0.4, el analizador morfológico: los lemas, las categorías gramaticales y los rasgos de un texto; su diccionario, construido a partir de las entradas en español del Wiktionary inglés con el modelo de contexto de los treebanks de UD AnCora y GSD, se distribuye con la licencia [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
*   `numpy`, `scipy`, `pandas`
*   `matplotlib` y `graphviz` para las [visualizaciones](visualizers/zipf.md)

Las dependencias se instalan con el paquete. anySeg y esMorph están escritos en Rust y vienen como wheels para Linux, macOS y Windows en x86-64 y arm64; en otras plataformas pip los compila desde el código fuente, para lo que hace falta [Rust](https://rustup.rs/). `import ests` no carga spaCy, matplotlib ni pandas, y las estadísticas de una cadena prescinden de spaCy, la morfología y el léxico incluidos: llega con las primeras estadísticas que leen el análisis de su modelo - la sintaxis y la cohesión -, y los gráficos y las funciones de corpus al usarlos por primera vez.

!!! warning "Graphviz"
    El paquete `graphviz` de las dependencias es solo un envoltorio: para dibujar el [árbol de palabras](visualizers/word_tree.md) y la [red de colocaciones](visualizers/corpus.md#collocation_network) hacen falta los ejecutables de [Graphviz](https://graphviz.org/download/), que se instalan aparte (`brew install graphviz`, `apt install graphviz`, `conda install graphviz`); sin ellos `render()` y la visualización del grafo en Jupyter fallan con `ExecutableNotFound`. Nada más los necesita. La red de colocaciones usa el motor de disposición `neato`, que las versiones nuevas de Ubuntu distribuyen aparte (`apt install libgvplugin-neato-layout8`).

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

Las estadísticas básicas, la legibilidad, la diversidad léxica, las [estadísticas morfológicas](stats/morph_stats.md) y las [de complejidad léxica](stats/lexical_stats.md), las métricas de estilo, la fonoestadística y las estadísticas del verso de una cadena no necesitan ningún modelo entrenado: la morfología viene de esMorph. Las estadísticas [sintácticas](stats/syntax_stats.md) (con analizador) y las [de cohesión](stats/cohesion_stats.md) de una cadena sí lo necesitan, igual que los rasgos de un texto, la [comparación de corpus](corpus/compare.md) y construir un `Doc` por su cuenta, mejor con [`ests.load_pipeline()`](components.md#load_pipeline), que da a un `Doc` los tokens y las oraciones de su cadena. Las pruebas también lo necesitan; lo instala el grupo de dependencias `test`:

``` bash
python -m spacy download es_core_news_sm
```

## Conjuntos de datos { #datasets }

El [corpus de literatura](datasets/spanishliterature.md), los [sonetos](datasets/spanishsonnets.md) y el [diccionario de frecuencias](datasets/freqdict.md) se descargan una vez con su método `download()`; las estadísticas de [`LexicalStats`](stats/lexical_stats.md) según el diccionario y [`keyness`](corpus/keyness.md) frente a él necesitan `FreqDict().download()`. Los archivos van al directorio `ests_data` junto al paquete instalado (`ests.constants.DEFAULT_DATA_DIR`), `dicts` para el diccionario y `texts` para el corpus y los sonetos. Donde ese directorio no se puede escribir, pase otro en `data_dir` (`FreqDict(data_dir="...")`) o defina la variable de entorno `ESTS_DATA_DIR` antes de importar el paquete:

``` bash
export ESTS_DATA_DIR=~/ests_data
```
