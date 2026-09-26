# Funciones de las estadísticas

## Algoritmo { #algorithm }

Un verso español se mide por sus sílabas métricas, que no son las sílabas de sus palabras una por una:

1.  **Sílabas y acentos.** Cada palabra se divide en sílabas con [`syllabify`](../syllables.md) y se acentúa por las reglas ortográficas de [`word_stresses`](../syllables.md#word_stresses); un adverbio en `-mente` tiene dos acentos. Las palabras átonas del verso (`VERSE_PROCLITICS`) no llevan acento: los artículos, las preposiciones salvo `según`, las conjunciones, los relativos (`que`, `cual`, `donde`, `como`, `cuanto`), los pronombres clíticos (`me`, `te`, `se`, `le`, `nos`), los posesivos antepuestos (`mi`, `tu`, `su`, `nuestro`, `vuestro`), los tratamientos ante un nombre (`don`, `fray`, `san`), `tan`, `aun` y las interjecciones `oh`, `ay`, `ah`. La última palabra de un verso siempre es tónica.
2.  **La lectura llana.** La vocal final de una palabra y la primera de la siguiente forman una sílaba - la sinalefa (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). La `h` muda la deja pasar (*oh‿al-ma*), mientras que `hi` y `hu` ante vocal (*hierba*, *hueso*) e `y` ante vocal (*ya*, *yo*) son consonantes y la impiden; una consonante al final de la palabra la impide también (*el | al-ma*).
3.  **La ley del acento final.** Un verso cuenta hasta su última sílaba acentuada y una sílaba más: un verso que termina en aguda gana una sílaba (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), uno que termina en esdrújula pierde una (*el pá-ja-ro* - 3).
4.  **El metro.** El metro de un poema es la medida de la mayoría de las lecturas llanas; en caso de empate, desde tres versos, gana la medida empatada con nombre que deja menos versos fuera de ella. Cada verso se ajusta a él con los menos cambios de su lectura llana: un verso más largo une dos vocales de un hiato en una palabra - la sinéresis (*poe-ta*), las que tienen una `i` o una `u` con tilde (*dí-a*) al final; uno más corto deshace sus sinalefas desde el final del verso - el hiato, y después divide un diptongo de una sílaba acentuada - la diéresis (*su-a-ve*, *ru-i-do*). La diéresis escrita marca un hiato (*sü-a-ve*) que ninguna sinéresis une. Un verso que no alcanza el metro conserva su lectura llana y cuenta como fuera de él. Un poema sin metro ajusta en cambio sus versos a sus medidas comunes, si estas ocupan más de la mitad de los versos.
5.  **El verso compuesto.** Un verso compuesto de dos hemistiquios iguales (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) se prueba cuando más de la mitad de las lecturas llanas se dividen en sus hemistiquios y su medida es igual a la de la mayoría de los versos o difiere de ella en una sílaba; gana la lectura con menos versos fuera del metro, el verso compuesto en caso de empate. La cesura cae tras una palabra tónica e impide la sinalefa, y cada hemistiquio sigue la ley del acento final por su cuenta: el alejandrino *La princesa está pálida | en su silla de oro* es 7 + 7.

Sobre los 60 209 versos de los 4259 sonetos de [SpanishSonnets](../datasets/spanishsonnets.md), la medida de un verso coincide con la escansión automática de DISCO en el 97,0% de los versos y con la de [rantanplan](https://github.com/linhd-postdata/rantanplan) en el 97,7%, y el acento de una sílaba métrica de los versos de igual medida en el 97,4% y el 99,6%.

La rima se describe en el [módulo](verse_stats.md#rhyme). Frente a la rima automática de DISCO (RhymeTagger), el 99,1% de los pares de versos que riman que encontramos son pares suyos, y encontramos el 97,9% de sus pares.

## Acentuación { #accentuate }

!!! info ""
    **ests.verse_stats.accentuate()**

Marca los acentos de un texto por las reglas ortográficas: se pone un acento agudo (U+0301) tras la vocal acentuada de cada palabra sin tilde, los dos acentos de un adverbio en `-mente` y de un compuesto con guion; las palabras átonas del verso (`VERSE_PROCLITICS`) quedan sin marca. El texto se normaliza a NFC. Para los versos de un poema, donde la última palabra siempre es tónica, sirve el método [`VerseStats.accentuate`](verse_stats.md#accentuate).

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | str | `-` | Texto |

!!! example "Ejemplo"

    ``` python
    import unicodedata
    from ests.verse_stats import accentuate

    text = "Yo soy aquel que ayer no más decía el verso azul y la canción profana"
    unicodedata.normalize("NFC", accentuate(text))
    # 'Yó sóy aquél que ayér nó más decía el vérso azúl y la canción profána'
    ```

## Metro { #detect_meter }

!!! info ""
    **ests.verse_stats.detect_meter()**

Determina el metro de un poema: el nombre del verso por sus sílabas métricas (`octosílabo`, `endecasílabo`, `alejandrino`...), o `None` si más de una décima parte de los versos tienen otra medida o el texto tiene un solo verso.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | str | `-` | Texto de un poema |

!!! example "Ejemplo"

    ``` python
    from ests.verse_stats import detect_meter

    # El comienzo del Romance del prisionero
    detect_meter(
        "Que por mayo era, por mayo,\ncuando hace la calor,\ncuando los trigos encañan\ny están los campos en flor,"
    )
    # 'octosílabo'
    ```

## Esquema de rima { #rhyme_scheme }

!!! info ""
    **ests.verse_stats.rhyme_scheme()**

Determina el esquema de rima de un poema: los esquemas de las estrofas separados por espacios, las letras en el orden de los grupos de rima del poema, mayúsculas para los versos de arte mayor y minúsculas para los de arte menor, los versos sin rima como un guion.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | str | `-` | Texto de un poema |
| `seseo` | bool | `False` | Pronunciar `c` y `z` ante `e` e `i` como `s` en la rima |

!!! example "Ejemplo"

    ``` python
    from ests.verse_stats import rhyme_scheme

    # Sor Juana Inés de la Cruz
    rhyme_scheme(
        "Hombres necios que acusáis\na la mujer sin razón,\nsin ver que sois la ocasión\nde lo mismo que culpáis."
    )
    # 'abba'
    ```

## Estrofas { #split_stanzas }

!!! info ""
    **ests.verse_stats.split_stanzas()**

Divide un texto en estrofas y versos: las estrofas se separan por líneas en blanco, y los versos sin una sílaba española (números, asteriscos, otros alfabetos) se omiten. El texto se normaliza a NFC.

Parámetros:

| Parámetro | Tipo | Valor por defecto | Descripción |
| :-------: | :--: | :---------------: | :---------: |
| `text` | str | `-` | Texto de un poema |

!!! example "Ejemplo"

    ``` python
    from ests.verse_stats import split_stanzas

    split_stanzas(
        "Cuando me paro a contemplar mi estado\n"
        "y a ver los pasos por do me han traído,\n\n* * *\n\n"
        "hallo, según por do anduve perdido,"
    )
    # [['Cuando me paro a contemplar mi estado', 'y a ver los pasos por do me han traído,'],
    #  ['hallo, según por do anduve perdido,']]
    ```
