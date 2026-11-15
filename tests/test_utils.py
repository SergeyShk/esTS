import pytest
import spacy
from anyts.utils import has_words, is_punctuation, iter_doc_tokens, iter_doc_words
from spacy.attrs import NORM, ORTH
from spacy.tokens import Doc
from spacy.util import compile_infix_regex

from ests import BasicStats, CohesionStats, StyleStats, WordsExtractor
from ests.constants import TOKENIZER_ABBREVIATIONS
from ests.corpus import kwic, text_features
from ests.exceptions import DatasetNotFoundError, SourceError, SourceTypeError
from ests.utils import (
    add_dash_rules,
    get_nlp,
    iter_text_sents,
    iter_text_words,
    iter_tokens,
    lemmatize,
)
from ests.visualizers import highlight, sentence_lengths


def split_sents(text):
    return [sent for *_, sent in iter_text_sents(text)]


def split_tokens(text):
    return [token for *_, token in iter_tokens(text)]


def dash_tokens(text):
    """Tokens of the tokenizer of a blank pipeline with the rules of add_dash_rules"""
    nlp = spacy.blank("es")
    add_dash_rules(nlp)
    return [token.text for token in nlp(text)]


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
        pytest.param(
            "1.1. Introducción. 1.2. Método.",
            ["1.1. Introducción.", "1.2. Método."],
            marks=pytest.mark.xfail(strict=True, reason="anySeg 0.3 splits 1.2. off a line"),
        ),
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
        pytest.param(
            "Del 3.-5 de mayo.",
            ["Del 3.-5 de mayo."],
            marks=pytest.mark.xfail(strict=True, reason="anySeg 0.3 splits a range after 3."),
        ),
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


@pytest.mark.parametrize(
    "abbreviation",
    [
        pytest.param(
            abbreviation,
            marks=pytest.mark.xfail(strict=True, reason="anySeg 0.3 splits UU. in capitals"),
        )
        if abbreviation == "ee. uu."
        else abbreviation
        for abbreviation in ABBREVIATIONS
    ],
)
def test_abbreviation_in_capitals(abbreviation):
    """An abbreviation in capitals is whole before capitals"""
    upper = abbreviation.upper()
    assert split_tokens(f"DE {upper} ESTO") == ["DE", *upper.split(), "ESTO"]


def test_tokenizer_abbreviations():
    assert all(form == form.lower() and len(form) > 2 for form in TOKENIZER_ABBREVIATIONS)
    # Every abbreviation with a period that spaCy keeps whole is whole in every case or in none
    rules = spacy.blank("es").tokenizer.rules
    spacy_forms = {
        form.lower()
        for form in rules
        if form[:1].isalpha() and form.endswith(".") and len(form) > 2
    }
    for abbreviation in spacy_forms - {"dna."}:
        forms = (abbreviation, abbreviation[:1].upper() + abbreviation[1:], abbreviation.upper())
        assert len({dash_tokens(form) == [form] for form in forms}) == 1, abbreviation
    assert dash_tokens("el sr. Pérez, SR. OBISPO, la Pág. 5 y ee. uu.") == [
        "el",
        "sr.",
        "Pérez",
        ",",
        "SR.",
        "OBISPO",
        ",",
        "la",
        "Pág.",
        "5",
        "y",
        "ee. uu.",
    ]
    # A form takes the attributes of the one the tokenizer of spaCy has
    nlp = spacy.blank("es")
    add_dash_rules(nlp)
    rules = nlp.tokenizer.rules
    for form in ("ud.", "Ud.", "UD."):
        assert rules[form] == [{ORTH: form, NORM: "usted"}]
    # Interjections are left alone, and a tokenizer without any form gets none
    assert dash_tokens("--Ej...") == ["--", "Ej", "..."]
    other = spacy.blank("xx")
    add_dash_rules(other)
    assert [token.text for token in other("el Sr. X y el sr. X")] == [
        "el",
        "Sr",
        ".",
        "X",
        "y",
        "el",
        "sr",
        ".",
        "X",
    ]


def test_add_dash_rules():
    nlp = spacy.blank("es")
    assert [token.text for token in nlp("--No")] == ["--No"]
    add_dash_rules(nlp)
    assert [token.text for token in nlp("--No")] == ["--", "No"]
    # The model of get_nlp has the rules
    text = "--No --dijo él. Y reírse—me decía:—¡Vete!"
    assert [token.text for token in get_nlp()(text)] == dash_tokens(text)
    # The rules a pipeline has already are kept, and a second call adds nothing
    extended = spacy.blank("es")
    extended.tokenizer.infix_finditer = compile_infix_regex(
        (*extended.Defaults.infixes, "§")
    ).finditer
    add_dash_rules(extended)
    assert [token.text for token in extended("a§b --No")] == ["a", "§", "b", "--", "No"]
    rules = [
        extended.tokenizer.prefix_search.__self__.pattern,
        extended.tokenizer.suffix_search.__self__.pattern,
        extended.tokenizer.infix_finditer.__self__.pattern,
    ]
    searches = (extended.tokenizer.prefix_search, extended.tokenizer.suffix_search)
    add_dash_rules(extended)
    # A tokenizer that has every rule is not reloaded
    assert (extended.tokenizer.prefix_search, extended.tokenizer.suffix_search) == searches
    assert extended.tokenizer.prefix_search.__self__.pattern == rules[0]
    assert extended.tokenizer.suffix_search.__self__.pattern == rules[1]
    assert extended.tokenizer.infix_finditer.__self__.pattern == rules[2]
    # A tokenizer without a rule gets the rules alone, one not read from a regular
    # expression is left as it is
    bare = spacy.blank("es")
    bare.tokenizer.prefix_search = None
    bare.tokenizer.suffix_search = None
    bare.tokenizer.infix_finditer = lambda text: iter(())
    add_dash_rules(bare)
    assert [token.text for token in bare("--No sé--")] == ["--", "No", "sé", "--"]
    unread = spacy.blank("es")
    unread.tokenizer.prefix_search = lambda text: None
    unread.tokenizer.suffix_search = lambda text: None
    unread.tokenizer.infix_finditer = None
    add_dash_rules(unread)
    assert [token.text for token in unread("--No sí--dijo")] == ["--No", "sí", "--", "dijo"]
    # A tokenizer of one's own is left as it is
    custom = spacy.blank("es")
    custom.tokenizer = lambda text: Doc(custom.vocab, words=text.split())
    add_dash_rules(custom)
    assert [token.text for token in custom("--No sé")] == ["--No", "sé"]


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
    assert [token.text for token in iter_doc_tokens(get_nlp()(text))] == words


def test_lemmatize_empty():
    assert lemmatize("") == ""


def test_lemmatize_cached():
    lemmatize.cache_clear()
    assert lemmatize("amigos") == "amigo"
    assert lemmatize("amigos") == "amigo"
    assert lemmatize.cache_info().hits == 1
    assert lemmatize.cache_info().misses == 1


def test_iter_doc_tokens():
    doc = spacy.blank("es")("El 50 % de los libros, ¡vaya!")
    assert [token.text for token in iter_doc_tokens(doc)] == [
        "El",
        "50",
        "de",
        "los",
        "libros",
        "vaya",
    ]


def test_iter_doc_tokens_span():
    doc = spacy.blank("es")("El gato duerme. Los niños juegan")
    assert [token.text for token in iter_doc_tokens(doc[4:])] == ["Los", "niños", "juegan"]


def test_iter_doc_words():
    doc = spacy.blank("es")("El gato duerme")
    assert list(iter_doc_words(doc)) == [(0, 2, "El"), (3, 7, "gato"), (8, 14, "duerme")]


def test_get_nlp():
    nlp = get_nlp()
    assert nlp.lang == "es"
    assert nlp("Los niños juegan")[2].pos_ == "VERB"


def test_get_nlp_cached():
    assert get_nlp() is get_nlp()


def test_get_nlp_of_a_saved_pipeline(tmp_path):
    """A pipeline saved with the component of the blank lines gets it once"""
    get_nlp().to_disk(tmp_path)
    nlp = get_nlp(str(tmp_path))
    assert nlp.pipe_names.count("ests_blank_lines") == 1
    # A pipeline without a component that sets the sentences gets none
    blank = spacy.blank("es")
    blank.to_disk(tmp_path / "blank")
    assert "ests_blank_lines" not in get_nlp(str(tmp_path / "blank")).pipe_names


def test_get_nlp_starts_a_sentence_after_a_blank_line():
    nlp = get_nlp()
    assert nlp.pipe_names.index("ests_blank_lines") == nlp.pipe_names.index("parser") - 1
    text = "Novedades\n\nImportación rápida. Menos errores\n\nEl gato duerme"
    sents = [sent.text.strip() for sent in nlp(text).sents]
    assert sents == split_sents(text)


def test_get_nlp_without_the_parser():
    """The starts of ests_blank_lines alone leave the sentences to the extractor"""
    text = (
        "El perro come carne. La casa es grande. El gato duerme\n\nEl perro corre. La casa arde."
    )
    doc = get_nlp()(text, disable=["parser"])
    assert BasicStats(doc).n_sents == BasicStats(text).n_sents == 5
    assert sentence_lengths(doc) == sentence_lengths(text) == [4, 4, 3, 3, 3]
    assert CohesionStats(doc).noun_overlap_adjacent == 0.0


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


def test_lone_surrogate_lemma():
    """A word with a lone surrogate is its own lemma, as simplemma cannot read it"""
    assert lemmatize("\ud800") == "\ud800"
    text = "Hola \ud800 mundo. El gato duerme."
    assert WordsExtractor(use_lexemes=True).extract(text)[1] == "\ud800"
    assert [line.keyword for line in kwic(text, "gato", by_lemma=True)] == ["gato"]
    assert highlight(text).text == text


@pytest.mark.parametrize(
    "parse",
    [
        CohesionStats,
        lambda text: StyleStats(text).verbal_nouns,
        text_features,
    ],
    ids=["CohesionStats", "StyleStats.verbal_nouns", "text_features"],
)
def test_lone_surrogate_of_a_model(parse):
    """The model of spaCy cannot read a character without a UTF-8 form"""
    with pytest.raises(SourceError, match="without a UTF-8 form at 5"):
        parse("Hola \ud800 mundo")
