# Concordancia KWIC

``` {.python .signature}
kwic(source, keyword, window=5, by_lemma=False, ignore_case=True)
```

<!-- core: corpus/kwic.md:kwic 481d7d1 -->
Una concordancia KWIC (keyword in context) - todas las apariciones de una palabra o de una expresión con su contexto a ambos lados. Las apariciones se buscan entre las palabras del texto por la forma, sin distinguir mayúsculas y minúsculas o distinguiéndolas (`ignore_case=False`), o por el lema (`by_lemma=True`); la palabra clave se lematiza como una cadena, así que con un lematizador una expresión puede escribirse en cualquier forma y sin él se da por lemas. Las palabras de una cadena y de la palabra clave salen del tokenizador, las de un `Doc` de sus tokens: un tokenizador que divide una cadena como lo hace el pipeline encuentra lo mismo en ambos. La puntuación y los símbolos no son palabras; las formas se comparan en la forma compuesta de Unicode (NFC), sin guiones blandos.

Una expresión no cruza el final de un párrafo o de una oración salvo que la palabra clave tenga un signo final o un comienzo de oración en el mismo lugar (`Sr. García`). Una oración termina en un límite de un `Doc` en cualquier punto entre las palabras, incluido un signo de apertura, o, sin límites o con límites parciales (`has_sents`), en un comienzo de oración del segmentador de oraciones, por defecto un signo final ante un espacio. El contexto son `window` palabras a cada lado tal como están escritas, puntuación incluida; los espacios se reducen a uno, y las apariciones no se solapan.

La función llama al `kwic` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) con los ganchos del español. El texto y la palabra clave se dividen en palabras del mismo modo, con el tokenizador del pipeline español vacío, así que `EE. UU.` es una palabra en los dos; las abreviaturas que el tokenizador mantiene enteras (`Sr.`, `pág.`, `etc.`, `EE. UU.`) son una palabra igual en minúsculas, con mayúscula inicial y en mayúsculas, así que `sr. pérez` encuentra `Sr. Pérez` y `SR. PÉREZ`, y la puntuación y los símbolos no son palabras de ninguno: `¿Dónde` encuentra `Dónde`, `20 €` encuentra `20`. Las formas y los lemas se pasan a minúsculas; las tildes forman parte de la forma: `solo` y `sólo` son dos formas. Las oraciones de una cadena, de la palabra clave y del texto de un `Doc` sin límites son las de [`SentsExtractor`](../extractors/sentences.md): unos puntos suspensivos o una exclamación seguidos de una palabra en minúscula no terminan la oración, así que `honrado piensa` encuentra `honrado... piensa`.

Por lema, la palabra clave se lematiza con simplemma, así que una expresión se da por lemas - `mirar a el pájaro` - o tal como se escribe, y una palabra del texto se encuentra por su lema de simplemma y, en un `Doc` que lleva lemas, también por el lema del modelo: `gatos` se encuentra por `gato`. En `Mi amigo vino con una botella de vino` el modelo da `venir` al verbo, así que `venir` encuentra el verbo, donde simplemma, que no ve el contexto, no encontraría nada; `vino` encuentra los dos, porque simplemma lee el verbo como `vino`.

=== "Código"

    ``` python
    from ests.corpus import kwic, print_kwic

    text = (
        "El gato estaba en la ventana y miraba a los pájaros. Los pájaros se fueron y el gato "
        "se durmió en la ventana. Mañana el gato volverá a estar en la ventana y mirará a los pájaros."
    )
    lines = kwic(text, "ventana", by_lemma=True, window=3)
    lines[0]
    print_kwic(lines, width=20)

    [line.keyword for line in kwic(text, "mirar a los pájaros", by_lemma=True)]
    ```

=== "Resultado"

    ```
    Concordance(start=21, end=28, left='estaba en la', keyword='ventana', right='y miraba a')
            estaba en la  ventana  y miraba a
            durmió en la  ventana  . Mañana el gato
             estar en la  ventana  y mirará a
    ['miraba a los pájaros', 'mirará a los pájaros']
    ```

## Parámetros

<!-- core: corpus/kwic.md:kwic-parameters b14c02d -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` | - | Texto u objeto Doc |
| `keyword` | `str` | - | Palabra o expresión |
| `window` | `int` | `5` | Número de palabras de contexto a cada lado |
| `by_lemma` | `bool` | `False` | Comparar lemas en lugar de formas |
| `ignore_case` | `bool` | `True` | No distinguir mayúsculas y minúsculas al comparar formas |

Una palabra clave sin palabras y una ventana que no es un entero o es negativa lanzan `ParameterError`; una fuente que no es ni una cadena ni un `Doc`, una palabra clave que no es una cadena y un gancho que no es invocable lanzan `SourceTypeError`.

## Resultado

<!-- core: corpus/kwic.md:Concordance ce8d89f -->
``` {.python .signature}
Concordance(start, end, left, keyword, right)
```

Una lista de tuplas con nombre `Concordance` en el orden del texto.

| Campo | Tipo | Descripción |
| :---- | :--- | :---------- |
| `start` | `int` | Posición del primer carácter de la aparición en el texto |
| `end` | `int` | Posición tras el último carácter de la aparición |
| `left` | `str` | Contexto a la izquierda |
| `keyword` | `str` | Aparición tal como está escrita en el texto |
| `right` | `str` | Contexto a la derecha |

## Líneas alineadas { #format_kwic }

<!-- core: corpus/kwic.md:format_kwic 4de69b2 -->
``` {.python .signature}
format_kwic(concordances, width=40)
```

Alinea las líneas en la palabra clave en un texto, una línea por aparición: el contexto de la izquierda se recorta por la izquierda y se alinea a la derecha, el de la derecha se recorta por la derecha. Las líneas pueden venir de cualquier iterable y se toman en la forma compuesta de Unicode (NFC), así que las anchuras cuentan los caracteres tal como se ven.

| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `concordances` | `list[Concordance]` | - | Líneas de una concordancia |
| `width` | `int` | `40` | Anchura de un contexto en caracteres |

Unas líneas que son una cadena o que no se pueden iterar lanzan `SourceTypeError`, y un `width` que no es un entero de al menos uno, `ParameterError`.

<!-- core: corpus/kwic.md:print_kwic 3ead3e5 -->
``` {.python .signature}
print_kwic(concordances, width=40)
```

Imprime el resultado de `format_kwic`.
