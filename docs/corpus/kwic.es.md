# Concordancia KWIC

!!! info ""
    **ests.corpus.kwic()**, **ests.corpus.format_kwic()**, **ests.corpus.print_kwic()**, **ests.corpus.Concordance**

## Descripción

Una concordancia KWIC (keyword in context) - todas las apariciones de una palabra o de una expresión con su contexto a la izquierda y a la derecha, como en [AntConc](https://www.laurenceanthony.net/software/antconc/) y textacy `keyword_in_context`. Muestra cómo se usa una palabra en un texto: con qué se combina, en qué formas y sentidos.

Las apariciones se buscan entre las palabras del texto: por la forma sin distinguir la caja, distinguiéndola (`ignore_case=False`) o por el lema (`by_lemma=True`: `gatos` se encuentra por `gato`, y una expresión se da por lemas - `mirar a el pájaro` - o tal como se escribe, porque cada una de sus palabras se lematiza). El texto y la palabra clave se dividen en palabras del mismo modo, con el tokenizador del pipeline español vacío, así que `EE. UU.` es una palabra en los dos, y la puntuación y los símbolos no son palabras de ninguno: `¿Dónde` encuentra `Dónde`, `20 €` encuentra `20`. Las tildes forman parte de la forma: `solo` y `sólo` son dos formas.

Por lema, la palabra clave se lematiza con simplemma, y una palabra del texto se encuentra por su lema de simplemma y, en un `Doc` que lleva lemas, también por el lema del modelo. Los dos lematizadores se equivocan en sitios distintos y cada uno cubre al otro: en `Mi amigo vino con una botella de vino` el modelo da `venir` al verbo y `vino` al sustantivo, así que `venir` encuentra solo el verbo, donde simplemma, que no ve el contexto, no encontraría nada; en `¿Dónde pusiste las llaves?` el modelo lee `pusiste` como `pusistar`, y simplemma deja que `poner` lo encuentre igualmente. El precio es que `vino` encuentra también el verbo, porque simplemma lo lee así.

El contexto son `window` palabras a cada lado tal como están escritas en el texto, con la puntuación entre ellas; los espacios se reducen a uno, y las apariciones no se solapan.

`format_kwic` alinea las líneas en la palabra clave: el contexto de la izquierda se recorta por la izquierda y se alinea a la derecha, el de la derecha se recorta por la derecha; `print_kwic` imprime el resultado.

## Parámetros

| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Texto u objeto Doc |
| `keyword` | str | `-` | Palabra o expresión (palabras separadas por espacios) |
| `window` | int | `5` | Número de palabras de contexto a cada lado |
| `by_lemma` | bool | `False` | Comparar lemas en lugar de formas |
| `ignore_case` | bool | `True` | No distinguir la caja al comparar formas |

`format_kwic(concordances, width=40)` y `print_kwic(concordances, width=40)`: `width` es la anchura de un contexto en caracteres, al menos uno; los saltos de línea dentro de la expresión se sustituyen por espacios.

## Resultado

Una lista de tuplas con nombre `Concordance` en el orden del texto.

| Campo | Tipo | Descripción |
| :---: | :--: | :---------- |
| `start` | int | Posición del primer carácter de la aparición en el texto |
| `end` | int | Posición tras el último carácter de la aparición |
| `left` | str | Contexto a la izquierda |
| `keyword` | str | Aparición tal como está escrita en el texto |
| `right` | str | Contexto a la derecha |

## Ejemplo

!!! example "Ejemplo"

    ``` python
    from ests.corpus import kwic, print_kwic

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    lines = kwic(text, "ventana", by_lemma=True, window=3)
    lines[0]
    # Concordance(start=21, end=28, left='estaba en la', keyword='ventana', right='y miraba a')

    print_kwic(lines, width=20)
    #         estaba en la  ventana  y miraba a
    #         durmió en la  ventana  . Mañana el gato
    #          estar en la  ventana  y mirará a

    [line.keyword for line in kwic(text, "mirar a los pájaros", by_lemma=True)]
    # ['miraba a los pájaros', 'mirará a los pájaros']
    ```
