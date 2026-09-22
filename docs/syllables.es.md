# Sílabas y acento

!!! info ""
    **ests.syllables**

## Descripción

Módulo que divide una palabra española en sílabas y localiza su sílaba tónica a partir de la escritura. La ortografía española codifica ambas cosas: los límites silábicos se deducen de las vocales y de los grupos consonánticos, y el acento se deduce de la tilde o, en su ausencia, de la terminación de la palabra. No hace falta ningún diccionario ni modelo entrenado. Estas funciones son la base de las estadísticas básicas (recuento de sílabas), las fórmulas de legibilidad, la fonoestadística y la métrica.

Las reglas siguen la *Ortografía de la lengua española* (RAE, 2010). Conviene conocer dos convenciones: dos vocales débiles forman siempre diptongo, como exigen las reglas ortográficas (`huir`, `cons-truir`, `je-sui-ta`, `guion` tienen una sílaba menos que en algunos silabeadores fonéticos), y `tl` se separa como en España (`at-las`).

## Silabificación { #syllabify }

!!! info ""
    **ests.syllables.syllabify()**

División de una palabra en sílabas. Cada sílaba se construye alrededor de un núcleo vocálico: una vocal, un diptongo o un triptongo.

| Regla | Ejemplo |
| :--- | :-----: |
| una vocal débil (`i`, `u`, `ü` sin tilde) junto a otra vocal forma diptongo | ai-re, puen-te, rui-do, ciu-dad |
| dos vocales fuertes forman hiato, igual que dos débiles idénticas | po-e-ta, le-er, a-é-re-o, chi-i-ta |
| una vocal débil con tilde es fuerte | dí-a, pa-ís, ba-úl |
| una vocal débil entre otras dos da un triptongo | a-ve-ri-guáis, buey |
| una vocal débil ante una fuerte se une a esa vocal | chi-hua-hua, ca-ca-hue-te |
| una `h` entre vocales no rompe el diptongo | ahu-ma-do, prohi-bir, de-sahu-cio |
| la `u` de `qu`, y la de `gu` ante `e` e `i`, es muda; `ü` es vocal | que-so, gue-rra, pin-güi-no |
| `y` es vocal a final de palabra y consonante ante vocal | rey, U-ru-guay, ma-yo |
| una consonante o dígrafo aislado pasa a la sílaba siguiente | ca-sa, mu-cho, pe-rro |
| una obstruyente con `l` o `r` pasa a la sílaba siguiente | ha-blar, o-tro |
| los demás pares de consonantes se separan | ac-to, is-la, at-las, rit-mo |
| de tres o más consonantes, las dos últimas pasan a la sílaba siguiente cuando forman uno de esos grupos; si no, se quedan las dos primeras | com-pra, cons-truir, ins-ti-tu-to, obs-tá-cu-lo |

Las letras se pasan a minúsculas. La palabra se divide en partes por cifras, guiones y otros caracteres que no son letras, cada parte se silabifica por separado (`te-ó-ri-co-prác-ti-co`), y una parte sin vocales (una abreviatura como `sh`) no produce sílabas.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `word` | str | `-` | Palabra |

!!! example "Ejemplo"

    ``` python
    from ests.syllables import syllabify

    syllabify("murciélago")
    # ['mur', 'cié', 'la', 'go']

    syllabify("averiguáis")
    # ['a', 've', 'ri', 'guáis']
    ```

## Recuento de sílabas { #count_syllables }

!!! info ""
    **ests.syllables.count_syllables()**

El número de sílabas según `syllabify`, con caché por forma de palabra.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `word` | str | `-` | Palabra |

!!! example "Ejemplo"

    ``` python
    from ests.syllables import count_syllables

    count_syllables("Uruguay")
    # 3
    ```

## Acento de la palabra { #word_stress }

!!! info ""
    **ests.syllables.word_stress()**

El índice de la sílaba tónica, contado desde cero como en `syllabify`; `None` para una palabra sin vocales.

| Regla | Ejemplo |
| :--- | :-----: |
| la tilde marca la sílaba tónica | ca-**mión**, **ár**-bol, mur-**cié**-la-go |
| una palabra terminada en vocal, en `n` o `s` tras vocal, o en `y` tras consonante lleva el acento en la penúltima sílaba | **ca**-sa, **jo**-ven, **lu**-nes, **whis**-ky |
| cualquier otra palabra lleva el acento en la última sílaba | pa-**pel**, re-**loj**, ro-**bots**, U-ru-**guay** |
| un monosílabo lleva el acento en su única sílaba | rey, y |

Los pronombres enclíticos no necesitan tratamiento aparte: sus formas llevan la tilde según las mismas reglas (`dí-ga-me-lo`, `de-cír-se-lo`). En un adverbio en `-mente` y en un compuesto con guion el acento principal es el último de `word_stresses` (`fá-cil-men-te` - 2).

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `word` | str | `-` | Palabra |

!!! example "Ejemplo"

    ``` python
    from ests.syllables import word_stress

    word_stress("camión"), word_stress("casa"), word_stress("murciélago")
    # (1, 0, 1)
    ```

## Todos los acentos { #word_stresses }

!!! info ""
    **ests.syllables.word_stresses()**

Todas las sílabas tónicas de una palabra en orden ascendente. Un solo índice para la mayoría de las palabras. Dos índices para un adverbio en `-mente`, que conserva el acento de su adjetivo (`fá-cil-men-te` - 0 y 2, `fe-liz-men-te` - 1 y 2), y un índice por cada parte de un compuesto con guion (`te-ó-ri-co-prác-ti-co` - 1 y 4).

El adverbio se reconoce por su forma: al menos dos sílabas antes de `-mente` y una base que termina como un adjetivo (en vocal, `l`, `r`, `z`, `n` o `s`) o lleva tilde. Las palabras de `NON_ADVERBS_MENTE` (`vehemente`) quedan excluidas, mientras que un subjuntivo raro con la misma forma (`fundamente`) también recibe un segundo acento.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `word` | str | `-` | Palabra |

!!! example "Ejemplo"

    ``` python
    from ests.syllables import word_stresses

    word_stresses("fácilmente")
    # [0, 2]
    ```

## Tipo de acentuación { #stress_type }

!!! info ""
    **ests.syllables.stress_type()**

La clase de la palabra según la posición de su acento principal: `aguda` en la última sílaba (`ca-mión`), `llana` en la penúltima (`ca-sa`), `esdrújula` en la antepenúltima (`mur-cié-la-go`), `sobresdrújula` antes (`dí-ga-me-lo`); `None` para una palabra sin vocales.

Parámetros:

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `word` | str | `-` | Palabra |

!!! example "Ejemplo"

    ``` python
    from ests.syllables import stress_type

    stress_type("dígamelo")
    # 'sobresdrújula'
    ```
