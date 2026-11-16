# Concordancia KWIC

``` {.python .signature}
kwic(source, keyword, window=5, by_lemma=False, ignore_case=True)
```

<!-- core: corpus/kwic.md:kwic 8e91237 -->
Una concordancia KWIC (keyword in context) - todas las apariciones de una palabra o de una expresión con su contexto a ambos lados. Las apariciones se buscan entre las palabras del texto por la forma, sin distinguir mayúsculas y minúsculas o distinguiéndolas (`ignore_case=False`), o por el lema (`by_lemma=True`); la palabra clave se lematiza como una cadena, así que con un lematizador una expresión puede escribirse en cualquier forma y sin él se da por lemas. Las palabras son las del [documento](https://sergeyshk.github.io/anyTS/document/) del texto - los tokens de una cadena, del tokenizador, y los de un `Doc` o de un `Document`, los suyos propios - y la palabra clave se divide como una cadena: un tokenizador que divide una cadena como lo hace el pipeline encuentra lo mismo en ambos. Una palabra tiene una letra o una cifra, así que la puntuación y los símbolos no son palabras; las formas se comparan en la forma compuesta de Unicode (NFC), sin guiones blandos, y las formas y los lemas, sin el punto final de una palabra con una letra: un tokenizador según Universal Dependencies deja el punto de una abreviatura con ella dentro de una oración y lo separa al final, así que la palabra clave `Sr.` encuentra la palabra de `El Sr. García vino` y `EE. UU.` las palabras de `Viajó a EE. UU. en mayo`.

Una expresión no cruza el final de una oración o de un párrafo del documento salvo que la palabra clave tenga un signo final o un comienzo de oración en el mismo lugar (`U.S. Army`). Las oraciones son las de un `Doc` o de un `Document`, o las del segmentador de oraciones para una cadena, la palabra clave y un `Doc` sin ellas (por defecto, las de `SentsExtractor`). El contexto son `window` palabras a cada lado tal como están escritas, puntuación incluida; los espacios se reducen a uno, y las apariciones no se solapan.

La función llama al `kwic` del núcleo [anyTS](https://sergeyshk.github.io/anyTS/corpus/kwic/) con los ganchos del español. El texto y la palabra clave se dividen en palabras del mismo modo, con el segmentador [anySeg](https://github.com/SergeyShk/anySeg), y una palabra se compara sin el punto de una abreviatura, que el final de una oración separa: `Sr.` encuentra `Sr.` en medio de una oración y al final, y `sr. pérez` encuentra `Sr. Pérez` y `SR. PÉREZ`. La puntuación y los símbolos no son palabras de ninguno: `¿Dónde` encuentra `Dónde`, `20 €` encuentra `20`. Las formas y los lemas se pasan a minúsculas; las tildes forman parte de la forma: `solo` y `sólo` son dos formas. Las oraciones de una cadena, de la palabra clave y del texto de un `Doc` sin límites son las de [`SentsExtractor`](../extractors/sentences.md): unos puntos suspensivos o una exclamación seguidos de una palabra en minúscula no terminan la oración, así que `honrado piensa` encuentra `honrado... piensa`.

Por lema, una palabra del texto se encuentra por el lema de `ests.utils.lemmatize` con su categoría gramatical - el de [esMorph](https://github.com/SergeyShk/esMorph) en el contexto de su oración para una cadena, el del pipeline para un `Doc` -, una palabra de un `Doc` o de un `Document` sin categorías gramaticales por su primer análisis, y una palabra de la palabra clave, que no tiene contexto, por los lemas de todos sus análisis, así que una expresión se da por lemas - `mirar a el pájaro` - o tal como se escribe: `gatos` se encuentra por `gato`. En `Mi amigo vino con una botella de vino` el primer `vino` es el verbo, así que `venir` lo encuentra y `vino` encuentra los dos.

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

<!-- core: corpus/kwic.md:kwic-parameters cb6665e -->
| Parámetro | Tipo | Por defecto | Descripción |
| :-------- | :--- | :------ | :---------- |
| `source` | `str` / `Doc` / `Document` | - | Texto u objeto Doc o Document |
| `keyword` | `str` | - | Palabra o expresión |
| `window` | `int` | `5` | Número de palabras de contexto a cada lado |
| `by_lemma` | `bool` | `False` | Comparar lemas en lugar de formas |
| `ignore_case` | `bool` | `True` | No distinguir mayúsculas y minúsculas al comparar formas |

Una palabra clave sin palabras, una ventana que no es un entero o es negativa y un `by_lemma` o un `ignore_case` que no es un `bool` lanzan `ParameterError`; una fuente que no es ni una cadena, ni un `Doc`, ni un `Document`, una palabra clave que no es una cadena y un gancho que no es invocable lanzan `SourceTypeError`, y un `Doc` con un token que cruza una línea en blanco, `SourceError`.

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
