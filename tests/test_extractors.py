import re

import pytest
from spacy.lang.es.stop_words import STOP_WORDS

from ests import CharNgramsExtractor, SentsExtractor, WordsExtractor
from ests.exceptions import ParameterError, SourceTypeError


@pytest.fixture(scope="module")
def text():
    return (
        "Los tesauros son una clase especial de recursos lexicográficos que se caracterizan por"
        " los siguientes rasgos: la completitud de los significados del vocabulario de una lengua"
        " o de alguno de sus segmentos; la ordenación temática, o ideográfica, de los significados"
        " de las palabras. La diferencia entre los tesauros y las ontologías formales consiste en"
        " la salida hacia la esfera de los significados léxicos, en el establecimiento de"
        " relaciones no solo entre los significados y las palabras que los expresan, sino también"
        " entre los propios significados (el registro de diversas relaciones semánticas dentro del"
        " diccionario)."
    )


class TestSentsExtractor:
    def test_init_value_error(self):
        with pytest.raises(ValueError):
            SentsExtractor(min_len=10, max_len=5)

    def test_extract(self, text):
        se = SentsExtractor()
        assert len(tuple(se.extract(text))) == 2
        assert se.sents[0].startswith("Los tesauros")
        assert se.sents[1].startswith("La diferencia")

    def test_extract_type_error(self, text):
        tokenizers = [666, ["a", "b"], {"a": "b"}, lambda text: 42]
        for tokenizer in tokenizers:
            with pytest.raises(SourceTypeError):
                se = SentsExtractor(tokenizer=tokenizer)  # type: ignore
                se.extract(text)

    def test_tokenizer_errors_propagate(self, text):
        def failing(text):
            raise KeyError("the tokenizer's own error")

        with pytest.raises(KeyError):
            SentsExtractor(tokenizer=failing).extract(text)

    def test_extract_drops_empty(self):
        se = SentsExtractor(tokenizer=re.compile(r"[.]"))
        assert se.extract("El gato duerme. El perro ladra.") == (
            "El gato duerme",
            " El perro ladra",
        )
        assert se.extract("...") == ()
        assert SentsExtractor(tokenizer=re.compile(r"\n")).extract("Gato.\n\n\nPerro.") == (
            "Gato.",
            "Perro.",
        )

    def test_extract_spanish_marks(self):
        se = SentsExtractor()
        assert se.extract("¿No tienes cien euros? ¡Ten cien amigos! Dámelo... Ya.") == (
            "¿No tienes cien euros?",
            "¡Ten cien amigos!",
            "Dámelo...",
            "Ya.",
        )

    @pytest.mark.parametrize(
        "tokenizer, expected",
        [(None, 2), (re.compile(r"[;.]"), 3), (str.splitlines, 1)],
    )
    def test_extract_tokenizer(self, text, tokenizer, expected):
        se = SentsExtractor(tokenizer=tokenizer)
        assert len(tuple(se.extract(text))) == expected

    @pytest.mark.parametrize(
        "min_len, expected",
        [(400, 0), (300, 1)],
    )
    def test_extract_min_len(self, text, min_len, expected):
        se = SentsExtractor(min_len=min_len)
        assert len(tuple(se.extract(text))) == expected

    @pytest.mark.parametrize(
        "max_len, expected",
        [(300, 1), (100, 0)],
    )
    def test_extract_max_len(self, text, max_len, expected):
        se = SentsExtractor(max_len=max_len)
        assert len(tuple(se.extract(text))) == expected


class TestWordsExtractor:
    def test_init_value_error_1(self):
        with pytest.raises(ValueError):
            WordsExtractor(ngram_range=(2, 1))
        for ngram_range in ((0, 1), (-1, 1)):
            with pytest.raises(ParameterError):
                WordsExtractor(ngram_range=ngram_range)

    def test_init_value_error_2(self):
        with pytest.raises(ValueError):
            WordsExtractor(min_len=10, max_len=5)

    def test_extract(self, text):
        we = WordsExtractor()
        assert len(we.extract(text)) == 94
        assert we.words[:3] == ("Los", "tesauros", "son")

    @pytest.mark.parametrize("tokenizer", [666, ["a", "b"], {"a": "b"}])
    def test_extract_type_error(self, text, tokenizer):
        with pytest.raises(TypeError):
            we = WordsExtractor(tokenizer=tokenizer)
            we.extract(text)

    @pytest.mark.parametrize(
        "tokenizer, expected",
        [
            (None, 94),
            (re.compile(r"[^\w]+"), 94),
            (str.split, 94),
        ],
    )
    def test_extract_tokenizer(self, text, tokenizer, expected):
        we = WordsExtractor(tokenizer=tokenizer)
        assert len(we.extract(text)) == expected

    def test_extract_stopwords_after_lowercase(self):
        we = WordsExtractor(stopwords=["no", "y"], lowercase=True)
        text = "No tengas cien euros, y ten cien amigos. Y no así."
        assert we.extract(text) == ("tengas", "cien", "euros", "ten", "cien", "amigos", "así")

    def test_extract_stopwords_case_insensitive(self):
        text = "Los tesauros. La diferencia entre los tesauros."
        assert WordsExtractor(stopwords=STOP_WORDS).extract(text) == (
            "tesauros",
            "diferencia",
            "tesauros",
        )
        assert WordsExtractor(stopwords=["LOS", "La"]).extract(text) == (
            "tesauros",
            "diferencia",
            "entre",
            "tesauros",
        )

    def test_stopwords_stored_as_frozenset(self):
        assert WordsExtractor(stopwords=["A", "b"]).stopwords == frozenset({"a", "b"})
        assert WordsExtractor(stopwords=[]).stopwords is None
        assert WordsExtractor().stopwords is None

    @pytest.mark.parametrize(
        ("token", "is_number"),
        [
            ("100", True),
            ("1990-1995", True),
            ("1.500,50", True),
            ("5,5", True),
            ("12/03/2020", True),
            ("3:30", True),
            ("10%", True),
            ("3.º", True),
            ("1.ª", True),
            ("1º", True),
            ("2.ª", True),
            ("1.er", True),
            ("1.ᵉʳ", True),
            ("2do", True),
            ("3ro", True),
            ("4TA", True),
            ("-5", True),
            ("+7", True),
            ("−5", True),
            ("-5,5%", True),
            ("−x", False),
            ("palabra", False),
            ("teórico-práctico", False),
            ("n.º", False),
            ("3-mya", False),
            ("1os", False),
        ],
    )
    def test_extract_filter_nums_tokens(self, token, is_number):
        we = WordsExtractor(filter_nums=True)
        expected = ("palabra", "palabra") if is_number else ("palabra", token, "palabra")
        assert we.extract(f"palabra {token} palabra") == expected

    def test_extract_filter_multichar_punct(self):
        text = "¿Qué?! ¡Sí!!! No... Palabra -- palabra … n.º 5 – sí «así» “aquí” ‘allí’ 5 % 100 €"
        expected = (
            "Qué",
            "Sí",
            "No",
            "Palabra",
            "palabra",
            "n.º",
            "5",
            "sí",
            "así",
            "aquí",
            "allí",
            "5",
            "100",
        )
        assert WordsExtractor().extract(text) == expected

    def test_extract_clitics_and_abbreviations(self):
        text = "Dámelo, Sr. García: decírselo a los EE. UU. costó 1.500,50 euros."
        assert WordsExtractor().extract(text) == (
            "Dámelo",
            "Sr.",
            "García",
            "decírselo",
            "a",
            "los",
            "EE. UU.",
            "costó",
            "1.500,50",
            "euros",
        )

    def test_extract_drops_empty(self):
        """re.split leaves an empty string after a final separator"""
        we = WordsExtractor(tokenizer=re.compile(r"\W+"), filter_punct=False)
        assert we.extract("Hola, mundo.") == ("Hola", "mundo")
        assert WordsExtractor(tokenizer=re.compile(r"\W+")).extract("Hola, mundo.") == (
            "Hola",
            "mundo",
        )
        assert WordsExtractor(tokenizer=re.compile(r"\W+"), filter_punct=False).extract("") == ()

    def test_extract_filter_punct(self, text):
        we = WordsExtractor(filter_punct=False)
        assert len(we.extract(text)) == 104

    def test_extract_filter_nums(self, text):
        we = WordsExtractor(filter_nums=True)
        assert len(we.extract(text + " 33.5 + 99")) == 94

    def test_extract_use_lexemes(self, text):
        we = WordsExtractor(use_lexemes=True)
        lemmas = set(we.extract(text))
        assert {"tesauro", "ontología", "significado", "relación"} <= lemmas
        assert "significados" not in lemmas

    @pytest.mark.parametrize(
        "stopwords, expected",
        [
            (STOP_WORDS, 38),
            (["de", "la", "los", "y"], 68),
        ],
    )
    def test_extract_stopwords(self, text, stopwords, expected):
        we = WordsExtractor(stopwords=stopwords)
        assert len(we.extract(text)) == expected

    @pytest.mark.parametrize(
        "min_len, expected",
        [(6, 41), (3, 69)],
    )
    def test_extract_min_len(self, text, min_len, expected):
        we = WordsExtractor(min_len=min_len)
        assert len(we.extract(text)) == expected

    @pytest.mark.parametrize(
        "max_len, expected",
        [(6, 59), (3, 46)],
    )
    def test_extract_max_len(self, text, max_len, expected):
        we = WordsExtractor(max_len=max_len)
        assert len(we.extract(text)) == expected

    def test_extract_ngram_range(self, text):
        we = WordsExtractor(ngram_range=(1, 3))
        assert len(we.extract(text)) == 279
        assert "ontologías_formales_consiste" in we.words
        assert WordsExtractor(ngram_range=(2, 2)).extract("un dos tres") == ("un_dos", "dos_tres")

    def test_get_most_common_value_error(self):
        with pytest.raises(ValueError):
            we = WordsExtractor()
            we.get_most_common(0)

    def test_get_most_common(self, text):
        we = WordsExtractor()
        we.extract(text)
        assert we.get_most_common(2) == [("de", 10), ("los", 8)]


class TestCharNgramsExtractor:
    text = "El gato dormía  en la ventana,\ny el perro - en el suelo."

    def test_extract(self):
        ce = CharNgramsExtractor()
        ngrams = ce.extract(self.text)
        assert ngrams[:8] == ("El", "l ", " g", "ga", "at", "to", "o ", " d")
        assert len(ngrams) == 54
        assert ce.ngrams == ngrams
        assert CharNgramsExtractor(n=1).extract("ñu") == ("ñ", "u")
        assert CharNgramsExtractor(n=4).extract("ñu") == ()
        assert CharNgramsExtractor().extract("") == ()

    def test_lowercase(self):
        ce = CharNgramsExtractor(n=3, lowercase=True)
        assert ce.extract(self.text)[:6] == ("el ", "l g", " ga", "gat", "ato", "to ")
        assert ce.get_most_common(2) == [("el ", 3), (" en", 2)]

    def test_within_words(self):
        ce = CharNgramsExtractor(n=4, lowercase=True, within_words=True)
        assert ce.extract(self.text) == (
            "gato",
            "dorm",
            "ormí",
            "rmía",
            "vent",
            "enta",
            "ntan",
            "tana",
            "perr",
            "erro",
            "suel",
            "uelo",
        )
        assert CharNgramsExtractor(n=5, within_words=True).extract("Gato en la ventana") == (
            "venta",
            "entan",
            "ntana",
        )
        ce = CharNgramsExtractor(n=2, within_words=True, tokenizer=re.compile(r"[\s,.-]+"))
        assert ce.extract("Gato - ñu") == ("Ga", "at", "to", "ñu")
        ce = CharNgramsExtractor(n=2, within_words=True, tokenizer=str.split)
        assert ce.extract("Gato ñu") == ("Ga", "at", "to", "ñu")

    def test_errors(self):
        with pytest.raises(ValueError):
            CharNgramsExtractor(n=0)
        with pytest.raises(ValueError):
            CharNgramsExtractor().get_most_common(0)
        with pytest.raises(TypeError):
            CharNgramsExtractor(within_words=True, tokenizer=42).extract(self.text)
