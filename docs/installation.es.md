# Instalación

La biblioteca todavía no está publicada. Hasta la primera versión se instala desde el repositorio.

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.7 o superior con el modelo `es_core_news_sm` para morfología y sintaxis
*   `numpy`, `pandas`, `scipy`, `matplotlib`

## Desde el repositorio

``` bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS
uv sync --all-groups
```

El modelo de spaCy se instala junto con el grupo de dependencias `test`; para un entorno aparte:

``` bash
python -m spacy download es_core_news_sm
```

## Desde PyPI

Tras la primera versión:

``` bash
pip install ests
```
