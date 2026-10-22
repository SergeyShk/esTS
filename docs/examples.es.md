# Ejemplos

Cuadernos de Jupyter en el directorio [examples/](https://github.com/SergeyShk/esTS/tree/master/examples) del repositorio, con la biblioteca en funcionamiento sobre sus conjuntos de datos. Cada uno se abre en Google Colab con un botón e instala la biblioteca - esTS 0.7 o posterior - y, si el cuaderno lo necesita, el modelo de spaCy; las salidas de todas las celdas se guardan en los archivos, así que los cuadernos se leen sin ejecutarlos. Los cuadernos están en inglés.

## Un texto con todas las herramientas

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb)

[01_text_walkthrough.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/01_text_walkthrough.ipynb) - un cuento de Horacio Quiroga, *El almohadón de pluma*, analizado con todas las herramientas de la biblioteca - extracción, sílabas, las estadísticas de cada clase, el resaltado, los gráficos y las medidas de corpus - y los componentes de spaCy sobre los 18 cuentos del libro en una tabla.

## Prosistas

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/02_prose_authors.ipynb)

[02_prose_authors.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/02_prose_authors.ipynb) - diez prosistas de `SpanishLiterature`: la Delta de Burrows y la Delta coseno entre sus obras, la atribución de obras apartadas, la Zeta y la ji cuadrado de Kilgarriff para Galdós y Pardo Bazán, la comparación de Galdós y Blasco Ibáñez rasgo por rasgo y las curvas de Mendenhall.

## Sonetos

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/03_sonnets.ipynb)

[03_sonnets.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/03_sonnets.ipynb) - metro, tipos del endecasílabo, esquemas de rima y sonido de los 4259 sonetos de `SpanishSonnets` del siglo XV al XX, contrastados con la anotación de DISCO, con el seseo de los poetas americanos.

## Medidas de corpus

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SergeyShk/esTS/blob/master/examples/04_corpus_measures.ipynb)

[04_corpus_measures.ipynb](https://github.com/SergeyShk/esTS/blob/master/examples/04_corpus_measures.ipynb) - la prosa de España y de Hispanoamérica hacia 1900: palabras clave de una frente a la otra y frente al diccionario de frecuencias, la dispersión de las palabras regionales, colocaciones, una concordancia del voseo, las leyes de Zipf y de Heaps y la comparación de los corpus.

## Ejecución en local

``` bash
uv sync --group examples
uv run jupyter lab examples/
```

`make notebooks` vuelve a ejecutar todos los cuadernos, escribe las salidas en los archivos y quita los metadatos de la ejecución; un workflow los ejecuta cada semana y falla cuando se mueve una salida que cita el texto.
