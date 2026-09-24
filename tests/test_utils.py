import hashlib
import tarfile
import zipfile
from pathlib import Path

import pytest
import spacy
from spacy.tokens import Doc
from spacy.util import compile_infix_regex

from ests import utils as utils_module
from ests.exceptions import DataFileError, DatasetNotFoundError, DownloadError
from ests.utils import (
    add_dash_rules,
    download_file,
    extract_archive,
    get_nlp,
    get_tokenizer,
    has_words,
    is_punctuation,
    iter_doc_tokens,
    iter_doc_words,
    iter_text_sents,
    iter_text_words,
    lemmatize,
    sentenize,
    sha256,
    to_path,
    tokenize,
)

LICENSE_URL = "https://github.com/SergeyShk/esTS/raw/master/LICENSE.txt"


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
        # the remark of the narrator after a dash continues the line of dialogue
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
        # Abbreviations wrapped in brackets and quotes
        ("Vivo en (EE. UU. Es grande) desde 2020.", ["Vivo en (EE. UU. Es grande) desde 2020."]),
        ("Llegó a las 3 (a. m. Comimos bien).", ["Llegó a las 3 (a. m. Comimos bien)."]),
        ("Frutas («p. ej. Manzanas»). Fin.", ["Frutas («p. ej. Manzanas»).", "Fin."]),
        ("Dijo: «(Sr. García) vino». Sí.", ["Dijo: «(Sr. García) vino».", "Sí."]),
        # List markers at the start of a sentence or a line
        ("1. Primero. 2. Segundo.", ["1. Primero.", "2. Segundo."]),
        ("1.1. Introducción. 1.2. Método.", ["1.1. Introducción.", "1.2. Método."]),
        ("IV. Capítulo. Fue Felipe IV. Luego.", ["IV. Capítulo.", "Fue Felipe IV.", "Luego."]),
        ("b. Dos.", ["b. Dos."]),
        ("1. Primero\n2. Segundo", ["1. Primero\n2. Segundo"]),
        ("1. Primero.\n2. Segundo.", ["1. Primero.", "2. Segundo."]),
        ("Índice:\n1. Uno\n2. Dos\n3. Tres. Fin.", ["Índice:\n1. Uno\n2. Dos\n3. Tres.", "Fin."]),
        ("Página 1. Luego.", ["Página 1.", "Luego."]),
        ("1990. Luego.", ["1990. Luego."]),
        ("―¿Vienes? ―preguntó ella. ―Sí.", ["―¿Vienes? ―preguntó ella.", "―Sí."]),
    ],
)
def test_sentenize(text, expected):
    assert list(sentenize(text)) == expected


def test_sentenize_long_token():
    text = "El " + "a" * 70 + "p. Mañana."
    assert list(sentenize(text)) == ["El " + "a" * 70 + "p.", "Mañana."]


def test_sentenize_long_paragraph():
    text = "El Sr. García llegó a las 3 p. m. y compró 1.500,50 kilos. ¿No? ¡Sí! " * 10000
    assert sum(1 for _ in sentenize(text)) == 30000


def test_iter_text_sents():
    text = "  El Sr. García llegó.\n\n¿Vienes?  -Sí -dijo él-. Adiós.  "
    sents = list(iter_text_sents(text))
    assert [sent for _, _, sent in sents] == list(sentenize(text))
    assert all(text[start:stop] == sent for start, stop, sent in sents)
    assert sents[0][:2] == (2, 22)
    assert list(iter_text_sents("")) == []
    assert list(iter_text_sents(" \n ")) == []


def test_iter_text_words():
    text = "¡Hola, mundo! EE. UU. compró 1.500,50 € de café."
    words = list(iter_text_words(text))
    assert [word for _, _, word in words] == [
        "Hola",
        "mundo",
        "EE. UU.",
        "compró",
        "1.500,50",
        "de",
        "café",
    ]
    assert [word for _, _, word in words] == [w for w in tokenize(text) if not is_punctuation(w)]
    assert all(text[start:stop] == word for start, stop, word in words)
    assert words[0] == (1, 5, "Hola")


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
        # The horizontal bar of some digitized texts is a raya
        ("―¿Qué? ―dijo él―.", ["―", "¿", "Qué", "?", "―", "dijo", "él", "―", "."]),
        # The underscores of the italics of Project Gutenberg
        ("--_Siguro_ lux_--dijo", ["--", "_", "Siguro", "_", "lux", "_", "--", "dijo"]),
        (
            "Pharsalia--_quiere nivolas_—concluyó",
            ["Pharsalia", "--", "_", "quiere", "nivolas", "_", "—", "concluyó"],
        ),
        ("_e-mail_", ["_", "e-mail", "_"]),
        # A hyphen between letters or before a digit is left alone
        ("franco-alemán e-mail", ["franco-alemán", "e-mail"]),
        ("-5 grados, 1990-1995, 1990–1995", ["-5", "grados", ",", "1990-1995", ",", "1990–1995"]),
    ],
)
def test_tokenize_dialogue_dashes(text, expected):
    assert list(tokenize(text)) == expected


def test_add_dash_rules():
    nlp = spacy.blank("es")
    assert [token.text for token in nlp("--No")] == ["--No"]
    add_dash_rules(nlp)
    assert [token.text for token in nlp("--No")] == ["--", "No"]
    # The model of get_nlp has the rules, so its words are the words of the tokenizer
    text = "--No --dijo él. Y reírse—me decía:—¡Vete!"
    assert [token.text for token in get_nlp()(text)] == list(tokenize(text))
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
    add_dash_rules(extended)
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


def test_to_path():
    assert to_path("/usr/local/") == Path("/usr/local/")
    path = Path("/usr/local/")
    assert to_path(path) is path


@pytest.mark.parametrize("path", [666, ["a", "b"], {"a": "b"}])
def test_to_path_type_error(path):
    with pytest.raises(TypeError):
        to_path(path)


@pytest.mark.network
def test_download_file(tmp_path):
    assert download_file(LICENSE_URL, dirpath=tmp_path) == str(tmp_path / "LICENSE.txt")
    assert download_file(LICENSE_URL, filename="licence.txt", dirpath=tmp_path) == str(
        tmp_path / "licence.txt"
    )
    assert download_file(LICENSE_URL, dirpath=tmp_path) == ""
    assert "MIT" in (tmp_path / "LICENSE.txt").read_text(encoding="utf-8")


@pytest.mark.network
def test_download_file_missing(tmp_path):
    with pytest.raises(DownloadError):
        download_file(LICENSE_URL + ".missing", dirpath=tmp_path, force=True)


def test_download_file_offline(tmp_path, monkeypatch):
    import io

    def fake_urlopen(request, timeout=None):
        return io.BytesIO(b"datos")

    monkeypatch.setattr(utils_module.urllib.request, "urlopen", fake_urlopen)
    url = "https://example.com/files/datos%20v1.txt"
    assert download_file(url, dirpath=tmp_path) == str(tmp_path / "datos v1.txt")
    assert (tmp_path / "datos v1.txt").read_bytes() == b"datos"
    assert download_file(url, dirpath=tmp_path) == ""
    assert sorted(path.name for path in tmp_path.iterdir()) == ["datos v1.txt"]


def test_download_file_partial_cleanup(tmp_path, monkeypatch):
    class BrokenResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            raise OSError("connection reset")

    calls = {}

    def fake_urlopen(request, timeout=None):
        calls["timeout"] = timeout
        calls["agent"] = request.get_header("User-agent")
        return BrokenResponse()

    monkeypatch.setattr(utils_module.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(DownloadError):
        download_file("https://example.com/data.zip", dirpath=tmp_path, force=True)
    assert calls == {"timeout": utils_module.DOWNLOAD_TIMEOUT, "agent": "esTS"}
    assert list(tmp_path.iterdir()) == []


def test_download_file_mkdir_error(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("not a directory", encoding="utf-8")
    with pytest.raises(DownloadError):
        download_file("https://example.com/data.zip", dirpath=blocker / "data")


def test_extract_archive_traversal(tmp_path):
    payload = tmp_path / "payload.txt"
    payload.write_text("evil", encoding="utf-8")
    archive = tmp_path / "evil.tar"
    with tarfile.open(archive, mode="w") as tar_file:
        tar_file.add(payload, arcname="../evil.txt")
    with pytest.raises(DataFileError):
        extract_archive(archive, tmp_path / "out")
    assert not (tmp_path / "evil.txt").exists()
    zipped = tmp_path / "evil.zip"
    with zipfile.ZipFile(zipped, "w") as zip_file:
        zip_file.writestr("../evil.txt", "evil")
    with pytest.raises(DataFileError):
        extract_archive(zipped, tmp_path / "zip_out")
    assert not (tmp_path / "evil.txt").exists()
    assert not (tmp_path / "zip_out" / "evil.txt").exists()
    broken = tmp_path / "broken.zip"
    with zipfile.ZipFile(broken, "w") as zip_file:
        zip_file.writestr("good.txt", "good")
    broken.write_bytes(b"\x00" * 4 + broken.read_bytes()[4:])
    with pytest.raises(DataFileError):
        extract_archive(broken, tmp_path / "broken_out")


@pytest.fixture
def tar_archive(tmp_path):
    payload = tmp_path / "payload.txt"
    payload.write_text("texto", encoding="utf-8")
    path = tmp_path / "corpus_v1.tar.xz"
    with tarfile.open(path, mode="w:xz") as archive:
        archive.add(payload, arcname="corpus/prose/a.txt")
        archive.add(payload, arcname="corpus/metadata.tsv")
    return path


def test_extract_archive_zip(tmp_path):
    path = tmp_path / "words.zip"
    with zipfile.ZipFile(path, mode="w") as archive:
        archive.writestr("words/spanish", "el\nla\n")
        archive.writestr("words/english", "the\n")
    extract_dir = tmp_path / "extract"
    assert extract_archive(path, extract_dir=extract_dir) == str(extract_dir / "words")
    assert (extract_dir / "words" / "spanish").is_file()


def test_extract_archive_tar_renames_root(tar_archive):
    extracted = extract_archive(tar_archive)
    assert extracted == str(tar_archive.parent / "corpus_v1")
    assert (Path(extracted) / "prose" / "a.txt").is_file()
    # A second extraction replaces the renamed directory instead of nesting a copy in it
    assert extract_archive(tar_archive) == extracted
    assert not (Path(extracted) / "corpus").exists()


def test_extract_archive_not_an_archive(tmp_path):
    not_an_archive = tmp_path / "words.tar.xz"
    not_an_archive.write_text("el\nla\n", encoding="utf-8")
    with pytest.raises(DataFileError):
        extract_archive(not_an_archive)


def test_extract_archive_mkdir_error(tar_archive):
    blocker = tar_archive.parent / "file"
    blocker.write_text("not a directory", encoding="utf-8")
    with pytest.raises(DataFileError):
        extract_archive(tar_archive, blocker / "out")


def test_extract_archive_single_file(tmp_path):
    nested = tmp_path / "nested.zip"
    with zipfile.ZipFile(nested, "w") as zip_file:
        zip_file.writestr("corpus-abc/corpus.xml", "<items />")
    extracted = Path(extract_archive(nested, tmp_path))
    assert extracted == tmp_path / "nested"
    assert (extracted / "corpus.xml").read_text() == "<items />"
    flat = tmp_path / "flat.zip"
    with zipfile.ZipFile(flat, "w") as zip_file:
        zip_file.writestr("corpus.xml", "<items />")
    assert extract_archive(flat, tmp_path / "flat") == str(tmp_path / "flat")
    assert (tmp_path / "flat" / "corpus.xml").read_text() == "<items />"


def test_extract_archive_dotted_names(tmp_path):
    archive = tmp_path / "dotted.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("dotted-abc/README.md", "readme")
        zip_file.writestr("dotted-abc/a/¡Qué....txt", "texto")
        zip_file.writestr("dotted-abc/a/normal.txt", "texto")
    extracted = Path(extract_archive(archive, tmp_path))
    assert extracted == tmp_path / "dotted"
    assert sorted(path.name for path in extracted.joinpath("a").iterdir()) == [
        "normal.txt",
        "¡Qué....txt",
    ]


def test_sha256(tmp_path):
    path = tmp_path / "data.txt"
    path.write_bytes(b"esTS")
    assert sha256(path) == hashlib.sha256(b"esTS").hexdigest()
    assert sha256(tmp_path / "missing.txt") == ""
