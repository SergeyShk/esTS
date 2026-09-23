# Instalación

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.7 o superior
*   `numpy`, `scipy`, `simplemma`

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

Las estadísticas básicas, la legibilidad y la diversidad léxica no necesitan ningún modelo entrenado: las oraciones, las palabras y los N-gramas de caracteres se extraen por reglas y con el tokenizador del pipeline español vacío, y las sílabas y el acento por la ortografía. Las [estadísticas morfológicas](stats/morph_stats.md) y las [sintácticas](stats/syntax_stats.md) sí lo necesitan - las sintácticas, un pipeline con analizador -, igual que construir un `Doc` para pasarlo a las estadísticas en lugar de una cadena; las pruebas también lo necesitan, donde viene con el grupo de dependencias `test`:

``` bash
python -m spacy download es_core_news_sm
```
