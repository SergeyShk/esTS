import importlib
import inspect
import pkgutil

import pytest
import spacy
from anyts.document import document_words
from anyts.utils import has_words, is_punctuation

import ests
from ests import BasicStats, CohesionStats, load_pipeline
from ests.exceptions import DatasetNotFoundError, SourceTypeError
from ests.utils import (
    get_document,
    get_nlp,
    iter_text_sents,
    iter_text_words,
    iter_tokens,
    lemmatize,
)
from ests.visualizers import sentence_lengths


def split_sents(text):
    return [sent for *_, sent in iter_text_sents(text)]


def split_tokens(text):
    return [token for *_, token in iter_tokens(text)]


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
        ("Fin.--" + " " * 100_000 + "1", ["Fin.--", "1"]),
        ("Grita" + "!" * 100_000 + "x", ["Grita" + "!" * 100_000 + "x"]),
    ],
    ids=["spaces after a glued dash", "a run of marks"],
)
def test_sentences_long_runs(text, expected):
    """Long runs of spaces and of marks"""
    assert split_sents(text) == expected


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
        # A remark of the narrator after a dash continues the sentence
        (
            "—¿Vienes? —preguntó María. —Sí —dijo él.",
            ["—¿Vienes? —preguntó María.", "—Sí —dijo él."],
        ),
        ("¡Ay! —gritó—. ¿Qué pasa? —dijo Juan.", ["¡Ay! —gritó—.", "¿Qué pasa? —dijo Juan."]),
        ("-¿Vienes? -preguntó ella.", ["-¿Vienes? -preguntó ella."]),
        ("–Ya está. –Bien.", ["–Ya está.", "–Bien."]),
        ("¿Cuánto? —5 euros.", ["¿Cuánto?", "—5 euros."]),
        ("Dijo: —Ven. —Ya voy.", ["Dijo: —Ven.", "—Ya voy."]),
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
        # The period of an abbreviation that may end a sentence ends it before a capital
        (
            "Llegó a las 3 p. m. Comimos. Murió en 44 a. C. Nació en 10 d. C. Luego.",
            [
                "Llegó a las 3 p. m.",
                "Comimos.",
                "Murió en 44 a. C.",
                "Nació en 10 d. C.",
                "Luego.",
            ],
        ),
        (
            "Los EE. UU. Son grandes. Frutas, p. ej. Manzanas.",
            ["Los EE. UU.", "Son grandes.", "Frutas, p. ej. Manzanas."],
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
        ("Título\n\u00a0\u3000\nEl gato duerme", ["Título", "El gato duerme"]),
        ("Uno.\nDos.\nTres", ["Uno.", "Dos.", "Tres"]),
        ("Él vino. Ñandú corrió. Ángel durmió.", ["Él vino.", "Ñandú corrió.", "Ángel durmió."]),
        ("¿Qué?!! ¡¿Cómo?! Así...  ¿Sí?", ["¿Qué?!!", "¡¿Cómo?!", "Así...", "¿Sí?"]),
        ("Bueno...¿qué? Nada.", ["Bueno...¿qué?", "Nada."]),
        # Abbreviations wrapped in brackets and quotes
        (
            "Vivo en (EE. UU. Es grande) desde 2020.",
            ["Vivo en (EE. UU.", "Es grande) desde 2020."],
        ),
        ("Llegó a las 3 (a. m. Comimos bien).", ["Llegó a las 3 (a. m.", "Comimos bien)."]),
        ("Frutas («p. ej. Manzanas»). Fin.", ["Frutas («p. ej. Manzanas»).", "Fin."]),
        ("Dijo: «(Sr. García) vino». Sí.", ["Dijo: «(Sr. García) vino».", "Sí."]),
        # List markers at the start of a sentence or a line
        ("1. Primero. 2. Segundo.", ["1. Primero.", "2. Segundo."]),
        ("IV. Capítulo. Fue Felipe IV. Luego.", ["IV. Capítulo.", "Fue Felipe IV.", "Luego."]),
        ("b. Dos.", ["b. Dos."]),
        # A line without a final mark, an item of a list or a heading, is a sentence
        ("1. Primero\n2. Segundo", ["1. Primero", "2. Segundo"]),
        ("1. Primero.\n2. Segundo.", ["1. Primero.", "2. Segundo."]),
        (
            "Índice:\n1. Uno\n2. Dos\n3. Tres. Fin.",
            ["Índice:", "1. Uno", "2. Dos", "3. Tres.", "Fin."],
        ),
        ("Página 1. Luego.", ["Página 1.", "Luego."]),
        ("1990. Luego.", ["1990. Luego."]),
        ("―¿Vienes? ―preguntó ella. ―Sí.", ["―¿Vienes? ―preguntó ella.", "―Sí."]),
        # A dash glued to the mark, as the editions of Project Gutenberg type it
        ("Está muy baja.--Tiene fiebre.", ["Está muy baja.", "--Tiene fiebre."]),
        ("Uno, cuatro.-¿Cinco?", ["Uno, cuatro.", "-¿Cinco?"]),
        ("Era tarde.—Ven.", ["Era tarde.", "—Ven."]),
        ("Dijo que sí.--dijo él.", ["Dijo que sí.--dijo él."]),
        ("Sí. --dijo él. Luego salió.", ["Sí. --dijo él.", "Luego salió."]),
        ("El Sr.--Pérez llegó.", ["El Sr.--Pérez llegó."]),
        # A closing dash before punctuation or a blank line keeps its sentence
        (
            "Se verían las piernas--¡qué horror!--, los pantalones.",
            ["Se verían las piernas--¡qué horror!--, los pantalones."],
        ),
        (
            "--Eso--dijo él vivamente...--. Es preciso.",
            ["--Eso--dijo él vivamente...--.", "Es preciso."],
        ),
        (
            "--La educaré.--\n\nLas mujeres eran pobres.",
            ["--La educaré.--", "Las mujeres eran pobres."],
        ),
        ("¿Vienes?--Sí.", ["¿Vienes?", "--Sí."]),
        # A dash at the end of a line closes its line of dialogue
        (
            "Para asombro de Mahoma.--\nOtra lengua clama.",
            ["Para asombro de Mahoma.--", "Otra lengua clama."],
        ),
        ("¡Traidores!--  \n¡Adiós!", ["¡Traidores!--", "¡Adiós!"]),
        ("¡Está lejos!--\n  al ángel de la muerte.", ["¡Está lejos!--\n  al ángel de la muerte."]),
        ("La viuda.-- El niño llegó.", ["La viuda.--", "El niño llegó."]),
        ("Mahoma.--\r\nOtra lengua.", ["Mahoma.--", "Otra lengua."]),
        # An abbreviation, an initial or a list marker before a closing dash ends nothing
        ("El Sr.--\nGarcía vino.", ["El Sr.--\nGarcía vino."]),
        ("IV.--\nDe los fines.", ["IV.--\nDe los fines."]),
        ("Era tarde.--«Ven», dijo.", ["Era tarde.", "--«Ven», dijo."]),
        # A single hyphen before a word numbers an article or joins two names
        ("Artículo 1.- Objeto del reglamento.", ["Artículo 1.- Objeto del reglamento."]),
        ("PRIMERO.- Aprobar el plan.", ["PRIMERO.- Aprobar el plan."]),
        ("EE.UU.-China firmaron.", ["EE.UU.-China firmaron."]),
    ],
)
def test_sentences(text, expected):
    assert split_sents(text) == expected


def test_sentences_long_token():
    text = "El " + "a" * 70 + "p. Mañana."
    assert split_sents(text) == ["El " + "a" * 70 + "p.", "Mañana."]


def test_sentences_long_paragraph():
    text = "El Sr. García llegó a las 3 p. m. y compró 1.500,50 kilos. ¿No? ¡Sí! " * 10000
    assert len(split_sents(text)) == 30000


def test_iter_text_sents():
    text = "  El Sr. García llegó.\n\n¿Vienes?  -Sí -dijo él-. Adiós.  "
    sents = list(iter_text_sents(text))
    assert [sent for _, _, sent in sents] == split_sents(text)
    assert all(text[start:stop] == sent for start, stop, sent in sents)
    assert sents[0][:2] == (2, 22)
    assert list(iter_text_sents("")) == []
    assert list(iter_text_sents(" \n ")) == []
    for split in (iter_text_sents, iter_tokens, iter_text_words):
        with pytest.raises(SourceTypeError):
            split(5)


def test_iter_text_words():
    text = "¡Hola, mundo! EE. UU. compró 1.500,50 € de café."
    words = list(iter_text_words(text))
    assert [word for _, _, word in words] == [
        "Hola",
        "mundo",
        "EE.",
        "UU.",
        "compró",
        "1.500,50",
        "de",
        "café",
    ]
    assert [word for _, _, word in words] == [
        w for w in split_tokens(text) if not is_punctuation(w)
    ]
    assert all(text[start:stop] == word for start, stop, word in words)
    assert words[0] == (1, 5, "Hola")


def test_tokens():
    text = "¿No  tienes\n\n100 euros?  Dámelo 1.500,50 3.º EE. UU. Sr. García"
    assert split_tokens(text) == [
        "¿",
        "No",
        "tienes",
        "100",
        "euros",
        "?",
        "Dámelo",
        "1.500,50",
        "3.º",
        "EE.",
        "UU",
        ".",
        "Sr.",
        "García",
    ]
    assert split_tokens("") == []
    assert split_tokens("  \n ") == []


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("--No --dijo él.", ["--", "No", "--", "dijo", "él", "."]),
        ("-¿Qué? -dijo Nela.", ["-", "¿", "Qué", "?", "-", "dijo", "Nela", "."]),
        ("sí--dijo", ["sí", "--", "dijo"]),
        ("de----- -----Adiós", ["de", "-----", "-----", "Adiós"]),
        ("Juan- y", ["Juan", "-", "y"]),
        ("reírse—me decía", ["reírse", "—", "me", "decía"]),
        ("dijo:—¡Mis ojos!", ["dijo", ":", "—", "¡", "Mis", "ojos", "!"]),
        ("cuatro.-¿Cinco?", ["cuatro", ".", "-", "¿", "Cinco", "?"]),
        ("capítulo -II-", ["capítulo", "-", "II", "-"]),
        ("Pues sí-¿y qué?", ["Pues", "sí", "-", "¿", "y", "qué", "?"]),
        # The horizontal bar as a raya
        ("―¿Qué? ―dijo él―.", ["―", "¿", "Qué", "?", "―", "dijo", "él", "―", "."]),
        # The underscores of the italics of Project Gutenberg
        ("--_Siguro_ lux_--dijo", ["--", "_", "Siguro", "_", "lux", "_", "--", "dijo"]),
        (
            "Pharsalia--_quiere nivolas_—concluyó",
            ["Pharsalia", "--", "_", "quiere", "nivolas", "_", "—", "concluyó"],
        ),
        ("_e-mail_", ["_", "e-mail", "_"]),
        # A dotted acronym keeps its period, the marks after it are split off
        ("la S.A.—dijo", ["la", "S.A.", "—", "dijo"]),
        ("el año 50 a.C.,—dijo", ["el", "año", "50", "a.C.", ",", "—", "dijo"]),
        ("»P.D.--El", ["»", "P.D.", "--", "El"]),
        ("la S.A.»—dijo", ["la", "S.A.", "»", "—", "dijo"]),
        ("¿Qué...a?—preguntó", ["¿", "Qué", "...", "a", "?", "—", "preguntó"]),
        # A hyphen between letters or before a digit is left alone
        ("franco-alemán e-mail", ["franco-alemán", "e-mail"]),
        ("-5 grados, 1990-1995, 1990–1995", ["-5", "grados", ",", "1990-1995", ",", "1990–1995"]),
        # The hyphens after the period of a number of a list
        ("Artículo 1.- El objeto", ["Artículo", "1", ".", "-", "El", "objeto"]),
        ("el 3.º piso", ["el", "3.º", "piso"]),
    ],
)
def test_tokens_dialogue_dashes(text, expected):
    assert split_tokens(text) == expected


ABBREVIATIONS = ["sr.", "dña.", "pág.", "núm.", "etc.", "p. ej.", "a.m.", "ee. uu."]


@pytest.mark.parametrize("abbreviation", ABBREVIATIONS)
def test_abbreviation_case(abbreviation):
    """An abbreviation is whole in lower case and capitalized"""
    capitalized = abbreviation[:1].upper() + abbreviation[1:]
    assert split_tokens(f"de {abbreviation} y") == ["de", *abbreviation.split(), "y"]
    assert split_tokens(f"de {capitalized} y") == ["de", *capitalized.split(), "y"]


@pytest.mark.parametrize("abbreviation", ["sr.", "dña.", "pág.", "núm.", "etc.", "p. ej.", "a.m."])
def test_abbreviation_in_capitals(abbreviation):
    """An abbreviation in capitals is whole before capitals"""
    upper = abbreviation.upper()
    assert split_tokens(f"DE {upper} ESTO") == ["DE", *upper.split(), "ESTO"]


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
        ("dámelo", "dar"),
        ("del", "de"),
        ("Madrid", "Madrid"),
        ("1990", "1990"),
        ("3.º", "3.º"),
        ("xqzw", "xqzw"),
    ],
)
def test_lemmatize(word, expected):
    assert lemmatize(word) == expected


@pytest.mark.parametrize(
    ("word", "pos", "expected"),
    [("vino", "VERB", "venir"), ("vino", "NOUN", "vino"), ("vino", "ADV", "vino")],
)
def test_lemmatize_pos(word, pos, expected):
    """The lemma of the first analysis with the part of speech, of the first one without it"""
    assert lemmatize(word, pos) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("\ufeffHola mundo. \ufeff Adiós.", ["Hola", "mundo", ".", "Adiós", "."]),
        ("\ufeff—Hola —dijo.", ["—", "Hola", "—", "dijo", "."]),
        ("\ufeff¿Vienes? ¡Sí!", ["¿", "Vienes", "?", "¡", "Sí", "!"]),
    ],
)
def test_tokens_byte_order_mark(text, expected):
    """A text read with utf-8 from a file saved with a byte order mark"""
    assert split_tokens(text) == expected
    words = [token for token in expected if not is_punctuation(token)]
    assert [word for _, _, word in iter_text_words(text)] == words
    assert list(document_words(get_document(get_nlp()(text)))) == words


def test_lemmatize_empty():
    assert lemmatize("") == ""


def test_lemmatize_cached():
    lemmatize.cache_clear()
    assert lemmatize("amigos") == "amigo"
    assert lemmatize("amigos") == "amigo"
    assert lemmatize.cache_info().hits == 1
    assert lemmatize.cache_info().misses == 1


def test_get_nlp():
    nlp = get_nlp()
    assert nlp.lang == "es"
    assert nlp("Los niños juegan")[2].pos_ == "VERB"


def test_get_nlp_cached():
    assert get_nlp() is get_nlp()


def test_get_nlp_of_a_saved_pipeline(tmp_path):
    """A saved pipeline of load_pipeline loads as it is"""
    get_nlp().to_disk(tmp_path)
    assert get_nlp(str(tmp_path)).pipe_names == get_nlp().pipe_names


def test_get_nlp_starts_a_sentence_after_a_blank_line():
    text = "Novedades\n\nImportación rápida. Menos errores\n\nEl gato duerme"
    sents = [sent.text.strip() for sent in get_nlp()(text).sents]
    assert sents == split_sents(text)


def test_get_nlp_without_the_parser():
    """The sentences of anyseg_sentencizer alone are those of the string"""
    text = (
        "El perro come carne. La casa es grande. El gato duerme\n\nEl perro corre. La casa arde."
    )
    doc = get_nlp()(text, disable=["parser"])
    assert BasicStats(doc).n_sents == BasicStats(text).n_sents == 5
    assert sentence_lengths(doc) == sentence_lengths(text) == [4, 4, 3, 3, 3]
    assert CohesionStats(doc).noun_overlap_adjacent == 0.0


TEXTS = [
    "--Dámelo --dijo el Sr. García.\n\nVino del pueblo al mar, etc. Luego se fue.",
    "—¿Vienes? —preguntó María. —Sí —dijo él.\n1. Primero\n2. Segundo",
    "Llegó a las 3 p. m. Comimos en EE. UU. el 3.º día; costó 1.500,50 euros.",
    "Título sin punto\n\nPrimera frase. Segunda\nfrase con salto. Tercera",
]


@pytest.mark.parametrize("text", TEXTS)
def test_load_pipeline_segments_like_a_string(text):
    """The tokens and the sentences of a Doc are those of the string"""
    doc = get_nlp()(text)
    assert [token.text for token in doc if not token.is_space] == split_tokens(text)
    assert [sent.text.strip() for sent in doc.sents] == split_sents(text)
    assert BasicStats(doc).n_words == BasicStats(text).n_words
    assert BasicStats(doc).n_sents == BasicStats(text).n_sents


def test_load_pipeline():
    nlp = load_pipeline(exclude="ner")
    assert nlp.pipe_names == [
        "anyseg_sentencizer",
        "esmorph",
        "tok2vec",
        "parser",
        "attribute_ruler",
    ]
    assert nlp.config["nlp"]["tokenizer"] == {"@tokenizers": "anyseg.Tokenizer.v1"}
    assert "ner" not in load_pipeline(exclude=["ner", "parser"]).component_names
    contraction = nlp("Vino del pueblo")[1]
    assert contraction.text == "del"
    assert [word["form"] for word in contraction._.anyseg_words] == ["de", "el"]
    # The other parameters go to spacy.load, the tokenizer of config is replaced
    custom = load_pipeline(config={"nlp": {"batch_size": 7, "tokenizer": {"@tokenizers": "x"}}})
    assert custom.batch_size == 7
    assert custom.config["nlp"]["tokenizer"] == {"@tokenizers": "anyseg.Tokenizer.v1"}


def test_load_pipeline_not_installed(tmp_path):
    with pytest.raises(DatasetNotFoundError, match="spacy download es_core_news_xxl"):
        load_pipeline("es_core_news_xxl")
    # A path is a saved pipeline, not a model to download
    with pytest.raises(DatasetNotFoundError, match=r"^No spaCy pipeline at .*my_pipeline: "):
        load_pipeline(str(tmp_path / "my_pipeline"))


def test_get_nlp_not_installed():
    with pytest.raises(DatasetNotFoundError, match="spacy download"):
        get_nlp("es_core_news_xxl")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("El gato duerme", True),
        ("5 %", True),
        ("3.º", True),
        ("¿?", False),
        ("...", False),
        ("«»", False),
        ("€ + %", False),
        ("   ", False),
        ("", False),
    ],
)
def test_has_words(text, expected):
    assert has_words(text) is expected


@pytest.mark.parametrize("text", ["El gato duerme", "¿?", ""])
def test_has_words_of_a_doc(text):
    assert has_words(spacy.blank("es")(text)) is has_words(text)


def test_has_words_of_a_span():
    doc = spacy.blank("es")("El gato duerme. ¿?")
    assert [has_words(sent) for sent in (doc[0:3], doc[4:])] == [True, False]


def test_lone_surrogate():
    """A lone surrogate (from JSON) is a token of its own, the positions are those of the string"""
    text = "Hola \ud800 mundo. Otra."
    assert split_tokens(text) == ["Hola", "\ud800", "mundo", ".", "Otra", "."]
    assert list(iter_text_sents(text)) == [(0, 13, "Hola \ud800 mundo."), (14, 19, "Otra.")]


def _word_functions():
    """Public functions of the package whose first parameter is a word of the tree or words"""
    found = []
    for info in pkgutil.walk_packages(ests.__path__, "ests."):
        if info.name.endswith("__main__"):
            continue
        module = importlib.import_module(info.name)
        for name, function in vars(module).items():
            if name.startswith("_") or not inspect.isfunction(function):
                continue
            params = list(inspect.signature(function).parameters.values())
            if (
                function.__module__ == module.__name__
                and params
                and "TreeWord" in str(params[0].annotation)
            ):
                found.append(function)
    return found


@pytest.mark.parametrize(
    "function",
    _word_functions(),
    ids=lambda function: f"{function.__module__}.{function.__name__}",
)
def test_word_functions_check_the_word(function):
    """A function of a word of the tree refuses a spaCy Token and a string"""
    params = list(inspect.signature(function).parameters.values())
    many = "Iterable" in str(params[0].annotation)
    for value in (get_nlp()("El libro fue escrito por él.")[2], "libro"):
        others = [value] * (len(params) - 1)
        with pytest.raises(SourceTypeError):
            function([value] if many else value, *others)
