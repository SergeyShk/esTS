# Métricas de estilo

!!! info ""
    **ests.style_stats.StyleStats**

## Descripción

Módulo para calcular las métricas de estilo de un texto: los indicadores SEO de los servicios [Advego](https://advego.com/text/seo/) y [Text.ru](https://text.ru/seo) - náusea, contenido de agua, índice de spam, naturalidad de la distribución de las palabras según la ley de Zipf y densidad de palabras clave - y los marcadores léxicos del estilo burocrático contra los que advierten las guías españolas de lenguaje claro: los sustantivos derivados de un verbo, las locuciones prepositivas del estilo administrativo, las expresiones parentéticas y los clichés. La fuente de datos puede ser un texto o un objeto `Doc` de la biblioteca [spaCy](https://github.com/explosion/spaCy).

Las fórmulas exactas de los servicios no se han publicado, así que se implementan las definiciones generalmente aceptadas; se describen en la sección de [funciones](style_stats_funcs.md). Por defecto las palabras se extraen en minúsculas sin lematizar, así que las formas de una palabra cuentan como palabras distintas, como en Advego. Para calcular por lemas, pase un objeto [`WordsExtractor`](../extractors/words.md) con `use_lexemes=True` y `lowercase=True`.

Los marcadores del estilo burocrático se cuentan sobre las formas sin filtrar (`forms`), sea cual sea el extractor, según las listas `COMPOUND_PREPOSITIONS`, `PARENTHETICALS` y `OFFICIALESE_CLICHES` de `ests.constants`. Una expresión que termina en `a` o `de` también encuentra la contracción con el artículo (`a efectos del`, `conforme al`), y una expresión que empieza por un infinitivo vale por todas las formas del verbo: `proceder a` encuentra `se procedió a`, `dar cumplimiento` encuentra `dio cumplimiento`. Los sustantivos deverbales necesitan las categorías gramaticales y los lemas: un `Doc` da su propia anotación, y una cadena se analiza con [`es_core_news_sm`](../installation.md#model) o con el pipeline pasado en `nlp` la primera vez que se lee `verbal_nouns`; las demás métricas de una cadena no necesitan modelo.

!!! note "Nota"
    Las métricas se calculan al acceder al atributo correspondiente o al llamar al método `get_stats` del objeto `StyleStats`. Las normas de los servicios están pensadas para textos de varios cientos de palabras; en textos cortos la náusea y el spam dicen poco.

## Parámetros

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `source` | str/Doc | `-` | Fuente de datos (una cadena o un objeto Doc) |
| `words_extractor` | WordsExtractor | `None` | Herramienta de extracción de palabras |
| `stopwords` | list[str] | `None` | Palabras vacías para el contenido de agua; si no se dan, se usan `STOPWORDS` y las expresiones parentéticas de una palabra |
| `top_n` | int | `10` | Número de las palabras más frecuentes para la náusea académica y la naturalidad según Zipf |
| `cliches` | list[str] | `None` | Lista de clichés; si no se da, se usa `OFFICIALESE_CLICHES` |
| `nlp` | Language | `None` | Pipeline de spaCy que analiza una cadena para los sustantivos deverbales; sin él se carga el modelo `es_core_news_sm` |

## Atributos

| Atributo | Tipo | Descripción |
| :------: | :--: | :---------: |
| `words` | tuple[str] | Tupla de las palabras extraídas |
| `forms` | tuple[str] | Tupla de las formas sin filtrar en minúsculas; sobre ellas se cuentan los marcadores del estilo burocrático |
| `classic_nausea` | float | Náusea clásica |
| `academic_nausea` | float | Náusea académica en porcentaje |
| `water` | float | Contenido de agua en porcentaje |
| `spam` | float | Índice de spam en porcentaje |
| `zipf_naturalness` | float | Naturalidad según la ley de Zipf en porcentaje |
| `verbal_nouns` | float | Proporción de sustantivos deverbales entre los sustantivos en porcentaje |
| `compound_prepositions` | float | Locuciones prepositivas por cada 100 palabras |
| `parentheticals` | float | Expresiones parentéticas por cada 100 palabras |
| `cliches` | float | Clichés por cada 100 palabras |

Normas de los servicios:

| Métrica | Norma |
| :-----: | :---: |
| Náusea clásica | como máximo 7, en la práctica 1-5 (Advego) |
| Náusea académica | 5-15% (Advego) |
| Contenido de agua | hasta 15% - natural, 15-30% - excesivo, más de 30% - alto (Text.ru) |
| Índice de spam | hasta 30% - natural, 30-60% - texto optimizado para SEO, más de 60% - texto saturado (Text.ru) |
| Naturalidad según Zipf | al menos 50% (pr-cy, megaindex) |

!!! warning "El contenido de agua del español"
    Las normas de Text.ru están pensadas para el ruso, que no tiene artículos. Un texto en español tiene más agua solo por su gramática: los 150 textos del [corpus de literatura](../datasets/spanishliterature.md) tienen un 42-54%, la prosa un 49% de mediana. Compare el contenido de agua de los textos entre sí, no con la norma.

## Métodos

### keyword_density

Devuelve la densidad de las palabras y frases clave: la frecuencia de cada una por cada 100 palabras del texto. Una frase de varias palabras separadas por espacios se busca como una secuencia de palabras, sin distinguir mayúsculas.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `keywords` | tuple[str] | `-` | Palabras o frases clave |

!!! example "Ejemplo"

    ``` python
    from ests import StyleStats

    text = "Tres tristes tigres tragaban trigo en un trigal, en tres tristes trastos"
    StyleStats(text).keyword_density("tres tristes", "trigo")
    # {'tres tristes': 16.666666666666668, 'trigo': 8.333333333333334}
    ```

### get_stats

Devuelve un diccionario con las métricas de estilo calculadas.

### print_stats

Muestra una tabla con las métricas de estilo calculadas.

## Ejemplo de uso

El mismo aviso escrito en estilo administrativo y en lenguaje claro.

!!! example "Ejemplo"

    _Código_:

    ``` python
    from ests import StyleStats

    official = (
        "En el marco del procedimiento de referencia, y a efectos de dar cumplimiento a lo "
        "dispuesto en la normativa vigente, se procedió a la revisión de la documentación "
        "presentada. No obstante, en virtud de la resolución de la comisión, se llevará a cabo "
        "la notificación de la misma a la mayor brevedad, en tiempo y forma."
    )
    plain = (
        "Hemos revisado los documentos que nos envió, como pide la ley. La comisión ha "
        "decidido su caso y le avisaremos lo antes posible."
    )

    StyleStats(official).print_stats()
    StyleStats(plain).get_stats()
    ```

    _Resultado_:

    ``` bash
                          Metric                      |  Value
    ------------------------------------------------------------
    Classic nausea                                    |   2.83
    Academic nausea (%)                               |  55.36
    Water content (%)                                 |  57.14
    Spam score (%)                                    |  37.50
    Naturalness by Zipf's law (%)                     |  53.57
    Verbal nouns (% of nouns)                         |  47.06
    Compound prepositions (per 100 words)             |   5.36
    Parenthetical expressions (per 100 words)         |   1.79
    Officialese clichés (per 100 words)               |   8.93

    {'classic_nausea': 1.4142135623730951,
     'academic_nausea': 47.82608695652174,
     'water': 43.47826086956522,
     'spam': 4.3478260869565215,
     'zipf_naturalness': 100.0,
     'verbal_nouns': 25.0,
     'compound_prepositions': 0.0,
     'parentheticals': 0.0,
     'cliches': 0.0}
    ```

El aviso de 56 palabras tiene tres locuciones prepositivas (`en el marco del`, `a efectos de`, `en virtud de`), cinco clichés (`dar cumplimiento`, `se procedió a`, `se llevará a cabo`, `a la mayor brevedad`, `en tiempo y forma`) y una expresión parentética, y casi la mitad de sus sustantivos son deverbales (`revisión`, `notificación`, `resolución`); la versión clara de 23 palabras no tiene ninguno de los marcadores. El anafórico `de la misma`, que las guías también desaconsejan, no se cuenta: distinguirlo de `el mismo día` requiere la sintaxis.
