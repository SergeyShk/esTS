# Instalación

## Requisitos

*   `python` 3.11 o superior
*   `spaCy` 3.7 o superior
*   `numpy`, `scipy`, `simplemma`

## Desde PyPI

``` bash
pip install ests
```

## Desde el repositorio

``` bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS
uv sync --all-groups
```

## El modelo de spaCy { #model }

Las estadísticas de la versión 0.1 no necesitan ningún modelo entrenado: las oraciones, las palabras y los N-gramas de caracteres se extraen por reglas y con el tokenizador del pipeline español vacío, y las sílabas y el acento por la ortografía. El modelo solo hace falta para construir un `Doc` y pasarlo a las estadísticas en lugar de una cadena, y para ejecutar las pruebas, donde viene con el grupo de dependencias `test`:

``` bash
python -m spacy download es_core_news_sm
```
