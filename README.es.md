# Spanish Texts Statistics (esTS)

[![Build](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml/badge.svg)](https://github.com/SergeyShk/esTS/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

English version: [README.md](https://github.com/SergeyShk/esTS/blob/master/README.md)

**esTS** calcula para textos en español lo que normalmente exige juntar varias herramientas sueltas: recuentos básicos, fórmulas de legibilidad, diversidad léxica y, en las versiones por venir, estadísticas morfológicas, sintácticas y de cohesión, marcadores de estilo, fonoestadística, métrica y rima, medidas de corpus y estilometría - con fórmulas publicadas y adaptadas al español, resultados deterministas y sin redes neuronales dentro.

Es la biblioteca hermana de [ruTS](https://github.com/SergeyShk/ruTS), la de estadísticas de textos en ruso, y sigue su estructura y sus nombres: cada estadística es una clase con `get_stats()`. Los componentes para un pipeline de [spaCy](https://github.com/explosion/spaCy) llegan con la morfología y la sintaxis de la 0.2.

> **Estado:** la 0.1 es la primera versión. Cubre la extracción de texto, las sílabas y el acento, las estadísticas básicas, la legibilidad y la diversidad léxica; la morfología, la sintaxis y la cohesión sobre Universal Dependencies llegan en la 0.2.

## Qué calcula

Versión 0.1:

* **Extracción** - oraciones con la puntuación española (`¿ ¡`, rayas de diálogo, abreviaturas), palabras con clíticos, lemas con `simplemma`, N-gramas de caracteres
* **Sílabas y acento** - silabificación por reglas y acento deducido de la ortografía, sin diccionario
* **Estadísticas básicas** - oraciones, palabras, letras, sílabas y signos de puntuación por tipo, con distribuciones y proporciones normalizadas
* **Legibilidad** - Fernández Huerta, Szigriszt-Pazos con la escala INFLESZ, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, LIX y RIX, con preajustes, etapas escolares y tiempo de lectura
* **Diversidad léxica** - TTR y sus variantes, MATTR, MSTTR, MTLD, HD-D, Yule, Herdan, Brunet, entropía, ajustes de Zipf y Heaps, cálculo por ventanas

Previsto:

* **Morfología, sintaxis y cohesión** (0.2) - sobre rasgos y relaciones de Universal Dependencies de los modelos `es_core_news_*` de spaCy, con componentes de pipeline
* **Medidas de corpus y estilometría** (0.3) - palabras clave, colocaciones, dispersión, KWIC, Delta de Burrows, Zeta, comparación de corpus
* **Estilo y sonido** (0.4) - métricas de estilo SEO, marcadores de lenguaje claro, fonoestadística, métrica silábica y rima

## Instalación

``` bash
pip install ests
```

Python 3.11 o superior. Las estadísticas de la 0.1 no necesitan ningún modelo entrenado de spaCy; el modelo solo hace falta para pasar un `Doc` analizado en lugar de una cadena.

## Primeros pasos

``` python
from ests import BasicStats, ReadabilityStats

text = "Hay tres clases de mentiras: mentiras, malditas mentiras y estadísticas"
BasicStats(text).n_syllables
# 23
ReadabilityStats(text).describe_level()
# 'algo difícil'
```

## Desarrollo

El proyecto usa [uv](https://docs.astral.sh/uv/) para las dependencias y [ruff](https://docs.astral.sh/ruff/) para el análisis y el formato del código. Se requiere Python 3.11 o superior.

```bash
git clone https://github.com/SergeyShk/esTS.git
cd esTS

make deps                   # crear el entorno e instalar todas las dependencias
uv run pre-commit install   # hooks: linters al hacer commit, tests al hacer push
make lint                   # ruff check, ruff format --check, mypy
make test                   # pytest con doctests
make docs-build             # mkdocs build --strict
```

La lista completa de comandos está en `make help`. Las pautas de contribución están en [CONTRIBUTING.md](CONTRIBUTING.md).

## Licencia

[MIT](LICENSE.txt)
