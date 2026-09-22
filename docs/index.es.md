# Spanish Texts Statistics (esTS)

**esTS** calculará para textos en español lo que normalmente exige juntar varias herramientas sueltas: recuentos básicos, fórmulas de legibilidad, diversidad y sofisticación léxica, estadísticas morfológicas, sintácticas y de cohesión, marcadores de estilo, fonoestadística, métrica y rima, medidas de corpus y estilometría - con fórmulas publicadas y adaptadas al español, resultados deterministas y sin redes neuronales dentro.

Es la biblioteca hermana de [ruTS](https://github.com/SergeyShk/ruTS), la de estadísticas de textos en ruso, y sigue su estructura y sus nombres: cada estadística está disponible como clase con `get_stats()` y como componente de un pipeline de [spaCy](https://github.com/explosion/spaCy).

!!! warning "Estado"
    El proyecto está en desarrollo hacia la 0.1: el repositorio, las herramientas, la integración continua y la documentación existen, y los primeros módulos están escritos: la extracción de oraciones, palabras y N-gramas de caracteres, la silabificación y el acento, las estadísticas básicas. La primera versión (0.1) cubrirá además la legibilidad con preajustes y la diversidad léxica.

## Alcance previsto

*   **Extracción** - oraciones y palabras con la puntuación española (`¿ ¡`), clíticos, lemas con spaCy o `simplemma`.
*   **Sílabas y acento** - silabificación por reglas (diptongos, hiatos, grupos consonánticos) y acento derivado de la ortografía.
*   **Legibilidad** - Fernández Huerta, Szigriszt-Pazos con la escala INFLESZ, Gutiérrez de Polini, Crawford, Legibilidad μ, SOL, con preajustes.
*   **Diversidad léxica** - TTR y sus variantes, MTLD, HD-D, Yule, Herdan, Brunet, entropía, ajustes de Zipf y Heaps, cálculo por ventanas.
*   **Morfología, sintaxis y cohesión** - sobre rasgos y relaciones de Universal Dependencies de los modelos `es_core_news_*` de spaCy; cohesión al estilo de Coh-Metrix con una lista española de marcadores del discurso.
*   **Medidas de corpus y estilometría** - palabras clave, colocaciones, dispersión, KWIC, Delta de Burrows, Zeta, comparación de corpus.
*   **Estilo y sonido** - métricas de estilo SEO, marcadores de lenguaje claro, fonoestadística, métrica silábica y rima (consonante y asonante).

## Enlaces

*   Repositorio: [github.com/SergeyShk/esTS](https://github.com/SergeyShk/esTS)
*   La hermana rusa: [github.com/SergeyShk/ruTS](https://github.com/SergeyShk/ruTS)
