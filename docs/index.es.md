# Spanish Texts Statistics (esTS)

**esTS** calcula para textos en español lo que normalmente exige juntar varias herramientas sueltas: recuentos básicos, fórmulas de legibilidad, diversidad léxica y, en las versiones por venir, estadísticas morfológicas, sintácticas y de cohesión, marcadores de estilo, fonoestadística, métrica y rima, medidas de corpus y estilometría - con fórmulas publicadas y adaptadas al español, resultados deterministas y sin redes neuronales dentro.

Es la biblioteca hermana de [ruTS](https://github.com/SergeyShk/ruTS), la de estadísticas de textos en ruso, y sigue su estructura y sus nombres: cada estadística es una clase con `get_stats()`. Los componentes para un pipeline de [spaCy](https://github.com/explosion/spaCy) llegan con la morfología y la sintaxis de la 0.2.

!!! note "Estado"
    La 0.1 es la primera versión. Cubre la extracción de texto, las sílabas y el acento, las estadísticas básicas, la legibilidad y la diversidad léxica; la morfología, la sintaxis y la cohesión sobre Universal Dependencies llegan en la 0.2.

## Qué calcula

Versión 0.1:

*   [**Extracción**](extractors/sentences.md) - oraciones con la puntuación española (`¿ ¡`, rayas de diálogo, abreviaturas), palabras con clíticos, lemas con `simplemma`, N-gramas de caracteres.
*   [**Sílabas y acento**](syllables.md) - silabificación por reglas (diptongos, hiatos, grupos consonánticos) y acento deducido de la ortografía.
*   [**Estadísticas básicas**](stats/basic_stats.md) - oraciones, palabras, letras, sílabas y signos de puntuación por tipo, con distribuciones y proporciones normalizadas.
*   [**Legibilidad**](stats/readability_stats.md) - Fernández Huerta, Szigriszt-Pazos con la escala INFLESZ, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, LIX y RIX, con preajustes, etapas escolares y tiempo de lectura.
*   [**Diversidad léxica**](stats/diversity_stats.md) - TTR y sus variantes, MATTR, MSTTR, MTLD, HD-D, Yule, Herdan, Brunet, entropía, ajustes de Zipf y Heaps, cálculo por ventanas.

Previsto:

*   **Morfología, sintaxis y cohesión** (0.2) - sobre rasgos y relaciones de Universal Dependencies de los modelos `es_core_news_*` de spaCy; cohesión al estilo de Coh-Metrix con una lista española de marcadores del discurso; componentes de pipeline.
*   **Medidas de corpus y estilometría** (0.3) - palabras clave, colocaciones, dispersión, KWIC, Delta de Burrows, Zeta, comparación de corpus.
*   **Estilo y sonido** (0.4) - métricas de estilo SEO, marcadores de lenguaje claro, fonoestadística, métrica silábica y rima (consonante y asonante).

## Enlaces

*   Repositorio: [github.com/SergeyShk/esTS](https://github.com/SergeyShk/esTS)
*   La hermana rusa: [github.com/SergeyShk/ruTS](https://github.com/SergeyShk/ruTS)
