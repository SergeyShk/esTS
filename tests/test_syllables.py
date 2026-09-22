import unicodedata
from pathlib import Path

import pytest

from ests.syllables import (
    _analyze,
    count_syllables,
    stress_type,
    syllabify,
    word_stress,
    word_stresses,
)

DATA = Path(__file__).parent / "data" / "syllables.tsv"

# Word, syllables, stressed syllables; checked by hand against the RAE rules
WORDS = [
    # Diphthongs, hiatuses, triphthongs
    ("casa", "ca-sa", [0]),
    ("aire", "ai-re", [0]),
    ("puente", "puen-te", [0]),
    ("ruido", "rui-do", [0]),
    ("ciudad", "ciu-dad", [1]),
    ("viuda", "viu-da", [0]),
    ("diario", "dia-rio", [0]),
    ("cuidado", "cui-da-do", [1]),
    ("diurno", "diur-no", [0]),
    ("jesuita", "je-sui-ta", [1]),
    ("poeta", "po-e-ta", [1]),
    ("leer", "le-er", [1]),
    ("caos", "ca-os", [0]),
    ("aéreo", "a-é-re-o", [1]),
    ("día", "dí-a", [0]),
    ("país", "pa-ís", [1]),
    ("baúl", "ba-úl", [1]),
    ("reír", "re-ír", [1]),
    ("oía", "o-í-a", [1]),
    ("creíamos", "cre-í-a-mos", [1]),
    ("actúe", "ac-tú-e", [1]),
    ("continúo", "con-ti-nú-o", [2]),
    ("situó", "si-tuó", [1]),
    ("veintiún", "vein-tiún", [1]),
    ("averiguáis", "a-ve-ri-guáis", [3]),
    ("estudiéis", "es-tu-diéis", [2]),
    ("buey", "buey", [0]),
    ("miau", "miau", [0]),
    ("Uruguay", "u-ru-guay", [2]),
    ("chiita", "chi-i-ta", [1]),
    ("chií", "chi-í", [1]),
    ("chiíes", "chi-í-es", [1]),
    ("friísimo", "fri-í-si-mo", [1]),
    ("casuística", "ca-suís-ti-ca", [1]),
    ("duunviro", "du-un-vi-ro", [2]),
    ("huir", "huir", [0]),
    ("fluir", "fluir", [0]),
    ("guion", "guion", [0]),
    ("truhan", "truhan", [0]),
    ("rio", "rio", [0]),
    ("río", "rí-o", [0]),
    # h between vowels
    ("ahumado", "ahu-ma-do", [1]),
    ("prohibir", "prohi-bir", [1]),
    ("prohíbo", "pro-hí-bo", [1]),
    ("desahucio", "de-sahu-cio", [1]),
    ("ahora", "a-ho-ra", [1]),
    ("ahí", "a-hí", [1]),
    ("búho", "bú-ho", [0]),
    ("rehén", "re-hén", [1]),
    ("vehículo", "ve-hí-cu-lo", [1]),
    ("bahía", "ba-hí-a", [1]),
    ("chihuahua", "chi-hua-hua", [1]),
    ("cacahuete", "ca-ca-hue-te", [2]),
    ("ahuecar", "a-hue-car", [2]),
    ("alcohol", "al-co-hol", [2]),
    ("deshacer", "des-ha-cer", [2]),
    ("exhausto", "ex-haus-to", [1]),
    # Silent u, ü
    ("queso", "que-so", [0]),
    ("quórum", "quó-rum", [0]),
    ("guerra", "gue-rra", [0]),
    ("guitarra", "gui-ta-rra", [1]),
    ("agua", "a-gua", [0]),
    ("antiguo", "an-ti-guo", [1]),
    ("pingüino", "pin-güi-no", [1]),
    ("vergüenza", "ver-güen-za", [1]),
    ("lingüística", "lin-güís-ti-ca", [1]),
    ("ambigüedad", "am-bi-güe-dad", [3]),
    # y
    ("rey", "rey", [0]),
    ("hoy", "hoy", [0]),
    ("muy", "muy", [0]),
    ("y", "y", [0]),
    ("jersey", "jer-sey", [1]),
    ("whisky", "whis-ky", [0]),
    ("mayo", "ma-yo", [0]),
    ("yo", "yo", [0]),
    ("kayak", "ka-yak", [1]),
    ("ayer", "a-yer", [1]),
    ("leyes", "le-yes", [0]),
    ("pyme", "py-me", [0]),
    # Consonants between vowels
    ("mucho", "mu-cho", [0]),
    ("calle", "ca-lle", [0]),
    ("perro", "pe-rro", [0]),
    ("hablar", "ha-blar", [1]),
    ("otro", "o-tro", [0]),
    ("acto", "ac-to", [0]),
    ("isla", "is-la", [0]),
    ("atlas", "at-las", [0]),
    ("atleta", "at-le-ta", [1]),
    ("ritmo", "rit-mo", [0]),
    ("himno", "him-no", [0]),
    ("innovar", "in-no-var", [2]),
    ("pizza", "piz-za", [0]),
    ("compra", "com-pra", [0]),
    ("construir", "cons-truir", [1]),
    ("instituto", "ins-ti-tu-to", [2]),
    ("obstáculo", "obs-tá-cu-lo", [1]),
    ("istmo", "ist-mo", [0]),
    ("transporte", "trans-por-te", [1]),
    ("abstracto", "abs-trac-to", [1]),
    ("adscribir", "ads-cri-bir", [2]),
    ("hámster", "háms-ter", [0]),
    ("tungsteno", "tungs-te-no", [1]),
    ("gángster", "gángs-ter", [0]),
    ("perspectiva", "pers-pec-ti-va", [2]),
    ("solsticio", "sols-ti-cio", [1]),
    ("examen", "e-xa-men", [1]),
    ("éxtasis", "éx-ta-sis", [0]),
    ("México", "mé-xi-co", [0]),
    ("psicología", "psi-co-lo-gí-a", [3]),
    ("gnomo", "gno-mo", [0]),
    ("acción", "ac-ción", [1]),
    # Stress by accent and ending
    ("camión", "ca-mión", [1]),
    ("árbol", "ár-bol", [0]),
    ("murciélago", "mur-cié-la-go", [1]),
    ("dígamelo", "dí-ga-me-lo", [0]),
    ("decírselo", "de-cír-se-lo", [1]),
    ("joven", "jo-ven", [0]),
    ("jóvenes", "jó-ve-nes", [0]),
    ("canciones", "can-cio-nes", [1]),
    ("lunes", "lu-nes", [0]),
    ("virus", "vi-rus", [0]),
    ("reloj", "re-loj", [1]),
    ("papel", "pa-pel", [1]),
    ("robots", "ro-bots", [1]),
    ("tictacs", "tic-tacs", [1]),
    ("bíceps", "bí-ceps", [0]),
    ("análisis", "a-ná-li-sis", [1]),
    ("régimen", "ré-gi-men", [0]),
    ("carácter", "ca-rác-ter", [1]),
    ("café", "ca-fé", [1]),
    ("dieciséis", "die-ci-séis", [2]),
    ("Ñandú", "ñan-dú", [1]),
    # Adverbs in -mente and look-alikes
    ("fácilmente", "fá-cil-men-te", [0, 2]),
    ("felizmente", "fe-liz-men-te", [1, 2]),
    ("claramente", "cla-ra-men-te", [0, 2]),
    ("comúnmente", "co-mún-men-te", [1, 2]),
    ("regularmente", "re-gu-lar-men-te", [2, 3]),
    ("cortésmente", "cor-tés-men-te", [1, 2]),
    ("demente", "de-men-te", [1]),
    ("vehemente", "ve-he-men-te", [2]),
    ("lamente", "la-men-te", [1]),
    ("mente", "men-te", [0]),
    ("cruelmente", "cruel-men-te", [0, 1]),
    ("fielmente", "fiel-men-te", [0, 1]),
    ("vilmente", "vil-men-te", [0, 1]),
    ("clemente", "cle-men-te", [1]),
    ("fundamente", "fun-da-men-te", [2]),
    ("complemente", "com-ple-men-te", [2]),
    ("atormente", "a-tor-men-te", [2]),
    ("sedimente", "se-di-men-te", [2]),
    ("comente", "co-men-te", [1]),
    # Compounds, foreign letters, case
    ("teórico-práctico", "te-ó-ri-co-prác-ti-co", [1, 4]),
    ("socio-económico", "so-cio-e-co-nó-mi-co", [0, 4]),
    ("d'Alcalà", "al-ca-là", [2]),
    ("François", "fran-çois", [0]),
    ("Björk", "björk", [0]),
    ("Lluïsa", "llu-ï-sa", [1]),
    ("Montjuïc", "mont-ju-ïc", [2]),
    ("Citroën", "ci-tro-ën", [2]),
    ("Schäuble", "schäu-ble", [0]),
    ("São", "são", [0]),
    ("Camões", "ca-mões", [1]),
    ("João", "jo-ão", [1]),
    ("naïve", "na-ï-ve", [1]),
    ("CASA", "ca-sa", [0]),
    # No vowels
    ("sh", "", []),
    ("3.º", "", []),
    ("1990", "", []),
    ("n.º", "", []),
    ("", "", []),
]


@pytest.mark.parametrize(("word", "syllables", "stresses"), WORDS, ids=[w[0] for w in WORDS])
def test_words(word, syllables, stresses):
    assert syllabify(word) == (syllables.split("-") if syllables else [])
    assert word_stresses(word) == stresses
    assert word_stress(word) == (stresses[-1] if stresses else None)
    assert count_syllables(word) == (len(syllables.split("-")) if syllables else 0)


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("camión", "aguda"),
        ("y", "aguda"),
        ("casa", "llana"),
        ("fácilmente", "llana"),
        ("murciélago", "esdrújula"),
        ("teórico-práctico", "esdrújula"),
        ("dígamelo", "sobresdrújula"),
        ("sh", None),
    ],
)
def test_stress_type(word, expected):
    assert stress_type(word) == expected


def test_results_are_copies():
    assert syllabify("casa") is not syllabify("casa")
    first = word_stresses("fácilmente")
    first.append(9)
    assert word_stresses("fácilmente") == [0, 2]


@pytest.mark.parametrize("word", ["camión", "día", "país", "ñandú", "pingüino", "fácilmente"])
def test_decomposed_input(word):
    decomposed = unicodedata.normalize("NFD", word)
    assert decomposed != word
    assert syllabify(decomposed) == syllabify(word)
    assert word_stresses(decomposed) == word_stresses(word)
    assert stress_type(decomposed) == stress_type(word)


def test_single_analysis_cache():
    _analyze.cache_clear()
    count_syllables("murciélago")
    word_stress("murciélago")
    stress_type("murciélago")
    assert _analyze.cache_info().misses == 1
    assert _analyze.cache_info().hits == 3


def test_stop_words():
    """Syllables and stress of the spaCy stop words, frozen in tests/data/syllables.tsv"""
    rows = [
        line.split("\t")
        for line in DATA.read_text(encoding="utf-8").splitlines()
        if not line.startswith("#")
    ]
    assert len(rows) == 520
    differences = [
        (word, syllabify(word), word_stress(word), syllables, int(stress))
        for word, syllables, stress in rows
        if syllabify(word) != syllables.split("-") or word_stress(word) != int(stress)
    ]
    assert not differences, differences
