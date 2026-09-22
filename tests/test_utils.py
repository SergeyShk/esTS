import pytest

from ests.utils import get_tokenizer, is_punctuation, lemmatize, sentenize, tokenize


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        (".", True),
        ("?!", True),
        ("!..", True),
        ("--", True),
        ("…", True),
        ("¿", True),
        ("¡", True),
        ("«", True),
        ("”", True),
        ("€", True),
        ("%", True),
        ("·", True),
        ("", True),
        ("a", False),
        ("ñ", False),
        ("3.º", False),
        ("n.º", False),
        ("teórico-práctico", False),
    ],
)
def test_is_punctuation(token, expected):
    assert is_punctuation(token) is expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", []),
        ("   \n\n  ", []),
        ("Sin punto final", ["Sin punto final"]),
        (
            "¿No tienes cien euros? ¡Ten cien amigos!",
            ["¿No tienes cien euros?", "¡Ten cien amigos!"],
        ),
        ("Dámelo, por favor... El resto mañana.", ["Dámelo, por favor...", "El resto mañana."]),
        ("Bueno... no sé. Vamos… ¡Ya!", ["Bueno... no sé.", "Vamos…", "¡Ya!"]),
        ("¡Ay! me duele. ¿Qué? nada.", ["¡Ay! me duele.", "¿Qué? nada."]),
        (
            "El 3.º y los años 1990-1995. Costó 1.500,50 euros.",
            ["El 3.º y los años 1990-1995.", "Costó 1.500,50 euros."],
        ),
        (
            "Nació en 1990. Luego murió. 2020 fue duro.",
            ["Nació en 1990.", "Luego murió.", "2020 fue duro."],
        ),
        ("«Hola», dijo él; “adiós”, dijo ella.", ["«Hola», dijo él; “adiós”, dijo ella."]),
        (
            "«¿Vienes?» Preguntó. «Sí.» Y se fue. Dijo: «No». (Nada más.) Fin.",
            [
                "«¿Vienes?»",
                "Preguntó.",
                "«Sí.»",
                "Y se fue.",
                "Dijo: «No».",
                "(Nada más.)",
                "Fin.",
            ],
        ),
        ("«¡Hola!» dijo. \"Adiós.\" 'Fin.'", ["«¡Hola!» dijo.", '"Adiós."', "'Fin.'"]),
        ("—Hola —dijo—. ¿Qué tal? —Bien.", ["—Hola —dijo—.", "¿Qué tal?", "—Bien."]),
        ("- Hola. - Adiós.", ["- Hola.", "- Adiós."]),
        (
            "El Sr. García y la Dra. López llegaron. Vino Dña. María.",
            ["El Sr. García y la Dra. López llegaron.", "Vino Dña. María."],
        ),
        (
            "Vino J. L. Borges. Vino M. Vargas Llosa.",
            ["Vino J. L. Borges.", "Vino M. Vargas Llosa."],
        ),
        (
            "Véase p. 45 y pág. 7. Cf. cap. 3. En el s. XIX.",
            ["Véase p. 45 y pág. 7.", "Cf. cap. 3.", "En el s. XIX."],
        ),
        (
            "Llegó a las 3 p. m. Comimos. Murió en 44 a. C. Nació en 10 d. C. Luego.",
            ["Llegó a las 3 p. m. Comimos.", "Murió en 44 a. C. Nació en 10 d. C. Luego."],
        ),
        (
            "Los EE. UU. Son grandes. Frutas, p. ej. Manzanas.",
            ["Los EE. UU. Son grandes.", "Frutas, p. ej. Manzanas."],
        ),
        (
            "Pesas, etc. Además, no. Es el mar. Luego.",
            ["Pesas, etc.", "Además, no.", "Es el mar.", "Luego."],
        ),
        ("(Véase p. 45.) Sí.", ["(Véase p. 45.)", "Sí."]),
        (
            "Título sin punto\n\nPrimera frase. Segunda\nfrase con salto. Tercera",
            ["Título sin punto", "Primera frase.", "Segunda\nfrase con salto.", "Tercera"],
        ),
        ("Uno.\n\n\n\nDos.\n \t\nTres.", ["Uno.", "Dos.", "Tres."]),
        ("Uno.\nDos.\nTres", ["Uno.", "Dos.", "Tres"]),
        ("Él vino. Ñandú corrió. Ángel durmió.", ["Él vino.", "Ñandú corrió.", "Ángel durmió."]),
        ("¿Qué?!! ¡¿Cómo?! Así...  ¿Sí?", ["¿Qué?!!", "¡¿Cómo?!", "Así...", "¿Sí?"]),
        ("Bueno...¿qué? Nada.", ["Bueno...¿qué?", "Nada."]),
    ],
)
def test_sentenize(text, expected):
    assert list(sentenize(text)) == expected


def test_tokenize():
    text = "¿No  tienes\n\n100 euros?  Dámelo 1.500,50 3.º EE. UU. Sr. García"
    assert list(tokenize(text)) == [
        "¿",
        "No",
        "tienes",
        "100",
        "euros",
        "?",
        "Dámelo",
        "1.500,50",
        "3.º",
        "EE. UU.",
        "Sr.",
        "García",
    ]
    assert list(tokenize("")) == []
    assert list(tokenize("  \n ")) == []


def test_get_tokenizer_cached():
    assert get_tokenizer() is get_tokenizer()


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("tienes", "tener"),
        ("Tienes", "tener"),
        ("NIÑOS", "niño"),
        ("dijo", "decir"),
        ("Los", "el"),
        ("cantándole", "cantar"),
        ("decírselo", "decir"),
        ("dámelo", "dámelo"),
        ("Madrid", "Madrid"),
        ("1990", "1990"),
        ("3.º", "3.º"),
    ],
)
def test_lemmatize(word, expected):
    assert lemmatize(word) == expected


def test_lemmatize_cached():
    lemmatize.cache_clear()
    assert lemmatize("amigos") == "amigo"
    assert lemmatize("amigos") == "amigo"
    assert lemmatize.cache_info().hits == 1
    assert lemmatize.cache_info().misses == 1
