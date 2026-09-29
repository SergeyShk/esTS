# Concordancia KWIC

!!! info ""
    **ests.corpus.kwic()**, **ests.corpus.format_kwic()**, **ests.corpus.print_kwic()**, **ests.corpus.Concordance**

## Descripción

<!-- core: corpus/kwic.md:kwic dadc1ee -->
Una concordancia KWIC (keyword in context) - todas las apariciones de una palabra o de una expresión con su contexto a la izquierda y a la derecha. Las apariciones se buscan entre las palabras del texto por la forma, sin distinguir mayúsculas y minúsculas o distinguiéndolas (`ignore_case=False`), o por el lema (`by_lemma=True`), donde las palabras de la palabra clave se lematizan como palabras de una cadena: con un lematizador una expresión puede escribirse en cualquier forma, sin él se da por lemas. Las palabras de una cadena y de la palabra clave salen del tokenizador, las de un `Doc` de sus tokens, así que un tokenizador que divide una cadena como lo hace el pipeline encuentra en un `Doc` lo que encuentra en su texto; la puntuación y los símbolos no son palabras. Las formas se comparan en la forma compuesta de Unicode (NFC), sin guiones blandos. Una expresión no cruza el final de un párrafo o de una oración - un límite de un `Doc` en cualquier punto entre sus palabras, incluido un signo de apertura, o en un texto sin límites el comienzo de una oración del segmentador de oraciones, por defecto un signo final ante un espacio - salvo que la palabra clave tenga un signo final o el comienzo de una oración en el mismo lugar (`Sr. García`). El contexto son `window` palabras a cada lado tal como están escritas en el texto, con la puntuación entre ellas; los espacios se reducen a uno, y las apariciones no se solapan.

## Ganchos del idioma

La función llama al `kwic` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) con los ganchos del español. El texto y la palabra clave se dividen en palabras del mismo modo, con el tokenizador del pipeline español vacío, así que `EE. UU.` es una palabra en los dos, y la puntuación y los símbolos no son palabras de ninguno: `¿Dónde` encuentra `Dónde`, `20 €` encuentra `20`. Las formas y los lemas se pasan a minúsculas; las tildes forman parte de la forma: `solo` y `sólo` son dos formas. Las oraciones de una cadena, de la palabra clave y del texto de un `Doc` sin límites son las de [`SentsExtractor`](../extractors/sentences.md): unos puntos suspensivos o una exclamación seguidos de una palabra en minúscula no terminan la oración, así que `honrado piensa` encuentra `honrado... piensa`.

Por lema, la palabra clave se lematiza con simplemma, así que una expresión se da por lemas - `mirar a el pájaro` - o tal como se escribe, y una palabra del texto se encuentra por su lema de simplemma y, en un `Doc` que lleva lemas, también por el lema del modelo: `gatos` se encuentra por `gato`. En `Mi amigo vino con una botella de vino` el modelo da `venir` al verbo, así que `venir` encuentra el verbo, donde simplemma, que no ve el contexto, no encontraría nada; `vino` encuentra los dos, porque simplemma lee el verbo como `vino`.

## Parámetros

<!-- core: corpus/kwic.md:kwic-parameters e17a79b -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------: | :--: | :---------: | :---------: |
| `source` | str/Doc | `-` | Texto u objeto Doc |
| `keyword` | str | `-` | Palabra o expresión |
| `window` | int | `5` | Número de palabras de contexto a cada lado |
| `by_lemma` | bool | `False` | Comparar lemas en lugar de formas |
| `ignore_case` | bool | `True` | No distinguir mayúsculas y minúsculas al comparar formas |

Una palabra clave sin palabras y una ventana negativa lanzan `ParameterError`; una fuente que no es ni una cadena ni un `Doc`, una palabra clave que no es una cadena y un gancho que no es invocable lanzan `SourceTypeError`.

<!-- core: corpus/kwic.md:format_kwic 532aaaa -->
`format_kwic(concordances, width=40)` alinea las líneas en la palabra clave: el contexto de la izquierda se recorta por la izquierda y se alinea a la derecha, el de la derecha se recorta por la derecha; `width` es la anchura de un contexto en caracteres, al menos uno. Las líneas pueden venir de cualquier iterable y se toman en la forma compuesta de Unicode (NFC), para que las anchuras cuenten los caracteres tal como se ven.

<!-- core: corpus/kwic.md:print_kwic 92f3d36 -->
`print_kwic(concordances, width=40)` imprime el resultado de `format_kwic`.

## Resultado

<!-- core: corpus/kwic.md:Concordance f0916bd -->
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
