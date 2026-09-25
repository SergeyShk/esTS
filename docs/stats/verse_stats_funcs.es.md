# Funciones de las estadísticas

## Algoritmo { #algorithm }

Un verso español se mide por sus sílabas métricas, que no son las sílabas de sus palabras una por una:

1.  **Sílabas y acentos.** Cada palabra se divide en sílabas con [`syllabify`](../syllables.md) y se acentúa con [`word_stresses`](../syllables.md#word_stresses): la tilde marca el acento, y si no, las reglas ortográficas (llana tras vocal, `n` o `s`, aguda tras otra consonante); un adverbio en `-mente` tiene dos acentos. Las palabras átonas del verso (`VERSE_PROCLITICS`) no llevan acento: los artículos, las preposiciones salvo `según`, las conjunciones, los relativos (`que`, `cual`, `donde`, `como`, `cuanto`), los pronombres clíticos (`me`, `te`, `se`, `le`, `nos`), los posesivos antepuestos (`mi`, `tu`, `su`, `nuestro`, `vuestro`), los tratamientos ante un nombre (`don`, `fray`, `san`), `tan`, `aun` y las interjecciones `oh`, `ay`, `ah`, que las escansiones de DISCO y de rantanplan dejan átonas también. La última palabra de un verso siempre es tónica.
2.  **La lectura llana.** La vocal final de una palabra y la primera de la siguiente forman una sílaba - la sinalefa (*cuan-do‿a-pe-nas*, *tie-rra‿y‿a-gua*). La `h` muda la deja pasar (*oh‿al-ma*), mientras que `hi` y `hu` ante vocal (*hierba*, *hueso*) e `y` ante vocal (*ya*, *yo*) son consonantes y la impiden; una consonante al final de la palabra la impide también (*el | al-ma*).
3.  **La ley del acento final.** Un verso cuenta hasta su última sílaba acentuada y una sílaba más: un verso que termina en aguda gana una sílaba (*cuan-do‿ha-ce-la-ca-lor* - 6 + 1 = 7), uno que termina en esdrújula pierde una (*el pá-ja-ro* - 3).
4.  **El metro.** El metro de un poema es la medida de la mayoría de las lecturas llanas; en caso de empate, desde tres versos, se prueban todas las medidas empatadas con nombre (una línea de prosa de 40 sílabas no da metro de todos modos) y gana la de menos versos fuera de ella (un cuarteto de dos versos de 10 y dos de 11 sílabas en la lectura llana es un cuarteto de endecasílabos). Cada verso se ajusta a él con los menos cambios de su lectura llana: un verso más largo une dos vocales de un hiato en una palabra - la sinéresis (*poe-ta*), las que tienen una `i` o una `u` con tilde (*dí-a*) al final; uno más corto deshace sus sinalefas desde el final del verso - el hiato, y después divide un diptongo de una sílaba acentuada - la diéresis (*su-a-ve*, *ru-i-do*, *con-fi-a-do*). La diéresis escrita es la marca del poeta de un hiato (*sü-a-ve*, *glo-rï-o-sa*), y ninguna sinéresis la une. Un verso que no alcanza el metro conserva su lectura llana y cuenta como fuera de él. Un poema sin metro ajusta en cambio sus versos a sus medidas comunes (las 7 y las 11 sílabas de una lira), si estas ocupan más de la mitad de los versos.
5.  **El verso compuesto.** Un verso compuesto de dos hemistiquios iguales (`VERSE_HEMISTICHS`: 5 + 5, 6 + 6, 7 + 7, 8 + 8, 9 + 9) se prueba cuando más de la mitad de las lecturas llanas se dividen en sus hemistiquios y su medida difiere en una sílaba de la de la mayoría de los versos o es igual a ella; gana la lectura con menos versos fuera del metro, el verso compuesto en caso de empate. La cesura cae tras una palabra tónica, impide la sinalefa, y cada hemistiquio sigue la ley del acento final por su cuenta: el alejandrino *La princesa está pálida | en su silla de oro* es 7 + 7, la esdrújula ante la cesura pierde una sílaba y el hiato *de | oro* da una.

La precisión se comprobó sobre los 60 209 versos de los 4259 sonetos de [SpanishSonnets](../datasets/spanishsonnets.md), frente a la escansión automática de DISCO y a la de [rantanplan](https://github.com/linhd-postdata/rantanplan) (ejecutada aparte: necesita spaCy 2.2.4, que funciona con Python 3.8 como mucho). La medida de un verso coincide con DISCO en el 97,0% de los versos y con rantanplan en el 97,7%, el acento de una sílaba métrica de los versos de igual medida en el 97,4% y el 99,6%, el esquema entero de un verso en el 77% y el 96%. En los versos simples las medidas coinciden en el 98,2% y el 99,1%; la mayor parte del resto son alejandrinos, que ambos cuentan como versos simples, sin los hemistiquios. La mayoría de las demás diferencias con DISCO son elecciones suyas: acentúa los pronombres clíticos `me`, `te` y `le` en el 84% de sus apariciones y `tan` en el 96%, y da a las palabras con un `-os` enclítico (*encareceros*, *quereros*) un segundo acento y una sílaba de más.

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
