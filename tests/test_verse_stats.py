import re
import shutil
import unicodedata
from collections import Counter
from itertools import combinations
from math import isnan
from pathlib import Path

import pytest
import spacy

from ests import VerseStats, verse_stats
from ests.constants import VERSE_STATS_DESC
from ests.datasets import (
    SpanishLiterature,
    SpanishSonnets,
    spanish_literature as literature_module,
    spanish_sonnets as sonnets_module,
)
from ests.exceptions import SourceError, SourceTypeError
from ests.verse_stats import (
    _default_joins,
    _endecasyllable_type,
    _ending,
    _fit,
    _parse_line,
    _scan,
    accentuate,
    detect_meter,
    rhyme_scheme,
    split_stanzas,
)

GARCILASO = """Cuando me paro a contemplar mi estado
y a ver los pasos por do me han traído,
hallo, según por do anduve perdido,
que a mayor mal pudiera haber llegado."""
SONATINA = """La princesa está triste... ¿qué tendrá la princesa?
Los suspiros se escapan de su boca de fresa,
que ha perdido la risa, que ha perdido el color.
La princesa está pálida en su silla de oro,
está mudo el teclado de su clave sonoro,
y en un vaso olvidada se desmaya una flor."""
ROMANCE = """Que por mayo era, por mayo,
cuando hace la calor,
cuando los trigos encañan
y están los campos en flor,"""
# The first three liras of the Vida retirada by Fray Luis de León: 7-11-7-7-11
LIRAS = """¡Qué descansada vida
la del que huye el mundanal ruido
y sigue la escondida
senda por donde han ido
los pocos sabios que en el mundo han sido!

Que no le enturbia el pecho
de los soberbios grandes el estado,
ni del dorado techo
se admira, fabricado
del sabio moro, en jaspes sustentado.

No cura si la fama
canta con voz su nombre pregonera,
ni cura si encarama
la lengua lisonjera
lo que condena la verdad sincera."""
# The sonnet X of Garcilaso de la Vega
SONNET = """Cuando me paro a contemplar mi estado
y a ver los pasos por do me han traído,
hallo, según por do anduve perdido,
que a mayor mal pudiera haber llegado;

mas cuando del camino estó olvidado,
a tanto mal no sé por dó he venido;
sé que me acabo, y más he yo sentido
ver acabar comigo mi cuidado.

Yo acabaré, que me entregué sin arte
a quien sabrá perderme y acabarme
si quisiere, y aún sabrá querello;

que pues mi voluntad puede matarme,
la suya, que no es tanto de mi parte,
pudiendo, ¿qué hará sino hacello?"""
# The beginning of La tierra de Alvargonzález by Antonio Machado
ROMANCE_MACHADO = """Siendo mozo Alvargonzález,
dueño de mediana hacienda,
que en otras tierras se dice
bienestar y aquí, opulencia,
en la feria de Berlanga
prendóse de una doncella,
y la tomó por mujer
al año de conocerla.
Muy ricas las bodas fueron,
y quien las vió las recuerda;
sonadas las tornabodas
que hizo Alvar en su aldea;
hubo gaitas, tamboriles,
flauta, bandurria y vihuela,
fuegos a la valenciana
y danza a la aragonesa."""
# Traditional, Romance del conde Arnaldos: the even lines in á, nine of them in -ar
ARNALDOS = """¡Quién hubiera tal ventura
sobre las aguas del mar
como hubo el conde Arnaldos
la mañana de San Juan!
Andando a buscar la caza
para su falcón cebar,
vio venir una galera
que a tierra quiere llegar;
las velas trae de sedas,
la ejarcia de oro torzal,
áncoras tiene de plata,
tablas de fino coral.
Marinero que la guía,
diciendo viene un cantar,
que la mar ponía en calma,
los vientos hace amainar;
los peces que andan al hondo,
arriba los hace andar;
las aves que van volando,
al mástil vienen posar.
Allí habló el conde Arnaldos,
bien oiréis lo que dirá:
—Por tu vida, el marinero,
dígasme ora ese cantar.
Respondióle el marinero,
tal respuesta le fue a dar:
—Yo no digo mi canción
sino a quien conmigo va."""
# Gustavo Adolfo Bécquer, Rimas LIII (the first two stanzas) and XXI
RIMA_LIII = """Volverán las oscuras golondrinas
en tu balcón sus nidos a colgar,
y otra vez con el ala a sus cristales
jugando llamarán.

Pero aquellas que el vuelo refrenaban
tu hermosura y mi dicha a contemplar,
aquellas que aprendieron nuestros nombres...
ésas... ¡no volverán!"""
RIMA_XXI = """¿Qué es poesía?, dices mientras clavas
en mi pupila tu pupila azul.
¿Qué es poesía? ¿Y tú me lo preguntas?
Poesía... eres tú."""
STROPHES = {
    # Calderón de la Barca, La vida es sueño
    "décima": """Cuentan de un sabio que un día
tan pobre y mísero estaba,
que sólo se sustentaba
de unas yerbas que cogía.
¿Habrá otro, entre sí decía,
más pobre y triste que yo?;
y cuando el rostro volvió
halló la respuesta, viendo
que otro sabio iba cogiendo
las hierbas que él arrojó.""",
    # Jorge Manrique, Coplas por la muerte de su padre
    "estrofa manriqueña": """Recuerde el alma dormida,
avive el seso y despierte
contemplando
cómo se pasa la vida,
cómo se viene la muerte
tan callando;""",
    # Alonso de Ercilla, La Araucana
    "octava real": """No las damas, amor, no gentilezas
de caballeros canto enamorados,
ni las muestras, regalos y ternezas
de amorosos afectos y cuidados;
mas el valor, los hechos, las proezas
de aquellos españoles esforzados,
que a la cerviz de Arauco no domada
pusieron duro yugo por la espada.""",
    # Sor Juana Inés de la Cruz
    "redondilla": """Hombres necios que acusáis
a la mujer sin razón,
sin ver que sois la ocasión
de lo mismo que culpáis.""",
    # Popular
    "seguidilla": """Por la calle abajito
va quien yo quiero;
no le veo la cara
con el sombrero.""",
}
SONNETS_ARCHIVE = Path(__file__).parents[1] / "ests" / "datasets" / "data" / sonnets_module.ARCHIVE
LITERATURE_ARCHIVE = (
    Path(__file__).parents[1] / "ests" / "datasets" / "data" / literature_module.ARCHIVE
)


@pytest.fixture(scope="module")
def literature(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_data")
    shutil.copy(LITERATURE_ARCHIVE, path / literature_module.ARCHIVE)
    dataset = SpanishLiterature(data_dir=path)
    dataset.download()
    return dataset


def scan(text, length=None):
    """Syllables, stresses, length and tail of a line, fitted to a length if one is given"""
    _, units, bounds = _parse_line(text)
    return _fit(units, bounds, length) if length else _scan(units, _default_joins(bounds))


def nfc(text):
    return unicodedata.normalize("NFC", text)


@pytest.fixture(scope="module")
def sonnets(tmp_path_factory):
    path = tmp_path_factory.mktemp("ests_data")
    shutil.copy(SONNETS_ARCHIVE, path / sonnets_module.ARCHIVE)
    dataset = SpanishSonnets(data_dir=path)
    # The archive is in the repository next to the code, the network is not needed
    dataset.download()
    return dataset


@pytest.mark.parametrize("source", ["", "¿? ...", "1810"])
def test_init_source_error(source):
    with pytest.raises(SourceError):
        VerseStats(source)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(SourceTypeError):
        VerseStats(source)


def test_no_spanish_syllables():
    vs = VerseStats("цвет и свет")
    assert (vs.n_lines, vs.n_stanzas, vs.meter, vs.n_feet) == (0, 0, None, None)
    assert vs.lines == vs.patterns == vs.stress_profile == ()
    assert vs.c_feet == vs.c_rhythms == vs.c_clausulas == vs.c_stressed_vowels == {}
    assert vs.c_rhymes == {}
    assert vs.rhyme_schemes == vs.strophes == ()
    assert vs.form is None
    assert isnan(vs.p_rhymed)
    for stat in ("p_deviations", "p_pyrrhics", "p_masculine", "mean_line_len"):
        assert isnan(getattr(vs, stat))


def test_endecasyllables():
    vs = VerseStats(GARCILASO)
    assert (vs.n_lines, vs.n_stanzas, vs.meter, vs.n_feet) == (4, 1, "endecasílabo", 11)
    assert (vs.p_deviations, vs.p_pyrrhics) == (0.0, 0.0)
    assert vs.c_feet == {11: 4}
    assert vs.mean_line_len == 11.0
    assert vs.syllables[0] == (
        "cuan", "do", "me", "pa", "ro‿a", "con", "tem", "plar", "mi‿es", "ta", "do"
    )  # fmt: skip
    # cuando and me are unstressed: 4-8-10
    assert vs.stresses[0] == (3, 7, 9)
    assert vs.patterns == ("---+---+-+-", "-+-+---+-+-", "+--+--+--+-", "--++-+-+-+-")
    assert vs.c_rhythms == {"4-8-10": 2, "4-7-10": 1, "3-6-10": 1}
    assert vs.stress_profile[9] == 1.0
    assert vs.stress_profile[10] == 0.0
    assert vs.stress_profile[3] == 1.0
    assert vs.stress_profile[5] == 0.25
    assert vs.c_clausulas == {"llana": 4}
    assert (vs.p_masculine, vs.p_feminine, vs.p_dactylic) == (0.0, 1.0, 0.0)
    assert vs.c_stressed_vowels == {"a": 8, "e": 3, "i": 2, "u": 2, "o": 1}
    assert vs.caesuras == (None, None, None, None)


def test_alexandrines():
    vs = VerseStats(SONATINA)
    assert (vs.meter, vs.n_feet, vs.p_deviations, vs.p_pyrrhics) == ("alejandrino", 14, 0.0, 0.0)
    assert vs.c_feet == {14: 6}
    # An aguda at the end of a hemistich adds a syllable: que ha perdido el color is 6 + 1
    assert vs.syllables[2][7:] == ("que‿ha", "per", "di", "do‿el", "co", "lor")
    # An esdrújula takes one off, and the caesura blocks the synalepha: pálida | en
    assert vs.syllables[3] == (
        "la", "prin", "ce", "sa‿es", "tá", "pá", "li", "da", "en", "su", "si", "lla", "de", "o", "ro"
    )  # fmt: skip
    assert vs.patterns[3] == "--+-++---+--+-"
    # The stresses index the syllables, the patterns keep the metrical syllables
    assert vs.stresses[3] == (2, 4, 5, 10, 13)
    assert [vs.syllables[3][index] for index in vs.stresses[3]] == ["ce", "tá", "pá", "si", "o"]
    assert vs.caesuras == (7, 7, 7, 8, 7, 7)
    # The last syllables of the hemistichs are always stressed
    assert vs.stress_profile[5] == vs.stress_profile[12] == 1.0
    assert vs.c_clausulas == {"aguda": 2, "llana": 4}
    assert vs.c_rhythms == {}


def test_octosyllables():
    vs = VerseStats(ROMANCE)
    assert (vs.meter, vs.n_feet, vs.p_deviations, vs.p_pyrrhics) == ("octosílabo", 8, 0.0, 0.0)
    # The synalepha cuando‿hace is broken to reach 8 syllables
    assert vs.syllables[1] == ("cuan", "do", "ha", "ce", "la", "ca", "lor")
    assert vs.c_clausulas == {"aguda": 2, "llana": 2}
    assert vs.p_masculine == 0.5


@pytest.mark.parametrize(
    ("text", "syllables"),
    [
        # a silent h lets the synalepha through, hi and hu before a vowel are consonants
        ("oh alma mía", ("oh‿al", "ma", "mí", "a")),
        ("hierba y hueso", ("hier", "ba‿y", "hue", "so")),
        ("la hierba", ("la", "hier", "ba")),
        # y before a vowel is a consonant, the conjunction y joins both neighbours
        ("mira ya", ("mi", "ra", "ya")),
        ("tierra y agua", ("tie", "rra‿y‿a", "gua")),
        # no synalepha after a consonant
        ("el alma", ("el", "al", "ma")),
    ],
)
def test_synalepha(text, syllables):
    assert scan(text).syllables == syllables


@pytest.mark.parametrize(
    ("text", "length", "syllables"),
    [
        # a dieresis splits the diphthong of a stressed syllable
        (
            "Hacer con un rocín mucho ruido",
            11,
            ("ha", "cer", "con", "un", "ro", "cín", "mu", "cho", "ru", "i", "do"),
        ),
        ("vuestra suave musa", 7, ("vues", "tra", "su", "a", "ve", "mu", "sa")),
        # a synaeresis joins the hiatus of a word
        ("el poeta cantaba", 6, ("el", "poe", "ta", "can", "ta", "ba")),
        # a synalepha is broken from the end of the line
        ("cuando hace la calor", 8, ("cuan", "do", "ha", "ce", "la", "ca", "lor")),
        ("que a mí me mira a veces", 8, ("que‿a", "mí", "me", "mi", "ra", "a", "ve", "ces")),
        # the silent u of que is no vowel to split
        ("que quiero", 4, ("que", "quie", "ro")),
        # a length out of reach leaves the plain reading
        ("el perro ladra", 10, ("el", "pe", "rro", "la", "dra")),
        ("que a mí me mira a veces", 12, ("que‿a", "mí", "me", "mi", "ra‿a", "ve", "ces")),
        ("el poeta cantaba", 4, ("el", "po", "e", "ta", "can", "ta", "ba")),
        # a synaeresis after the last stress moves nothing
        ("la luz del día", 4, ("la", "luz", "del", "dí", "a")),
    ],
)
def test_fit(text, length, syllables):
    assert scan(text, length).syllables == syllables


@pytest.mark.parametrize(
    ("text", "length", "tail"),
    [
        # the law of the final stress: a line counts up to its last stress and one more
        ("la calor", 4, 0),
        ("el árbol", 3, 1),
        ("el pájaro", 3, 2),
        ("dígamelo", 2, 3),
        # the last word is always stressed, an unstressed word inside is not
        ("dime que", 4, 0),
        ("la casa de mi padre", 7, 1),
    ],
)
def test_final_stress(text, length, tail):
    scansion = scan(text)
    assert (scansion.length, scansion.tail) == (length, tail)


def test_unstressed_words():
    assert scan("la casa de mi padre").stresses == (1, 5)
    assert scan("fácilmente").stresses == (0, 2)


def test_no_meter():
    polymetric = "Cuando me paro a contemplar mi estado\nla luz del día\nque a mayor mal pudiera haber llegado\nen la ventana"
    vs = VerseStats(polymetric)
    assert (vs.meter, vs.n_feet) == (None, None)
    assert isnan(vs.p_deviations)
    assert isnan(vs.p_pyrrhics)
    assert vs.stress_profile == ()
    assert vs.c_feet == {5: 2, 11: 2}
    # the lines of 11 syllables still have their types
    assert sum(vs.c_rhythms.values()) == 2
    # a single line has no meter
    assert VerseStats("Cuando me paro a contemplar mi estado").meter is None


def test_tied_lengths():
    # Two lines of 10 syllables in the plain reading, two of 11: the hiatus brings all to 11
    stanza = """Feliz eternamente y escondido
viviré de ocuparle satisfecho
¡De tantos mundos como Dios ha hecho,
este espacio no más a Dios le pido!"""
    vs = VerseStats(stanza)
    assert (vs.meter, vs.c_feet) == ("endecasílabo", {11: 4})
    # two lines of two lengths keep the shorter one
    assert VerseStats("Cuando me paro a contemplar mi estado\nla luz del día").meter is None


def test_distinct_lengths(monkeypatch):
    # Prose lines of distinct lengths: the unnamed lengths are no candidates, and a line
    # out of reach of a meter costs one reading
    lines = [" ".join(["la casa blanca"] * repeats) for repeats in range(10, 50)]
    lines += [GARCILASO.split("\n")[0], "la luz del día", SONATINA.split("\n")[0]]
    calls = 0
    scan = verse_stats._scan

    def counting(*args):
        nonlocal calls
        calls += 1
        return scan(*args)

    monkeypatch.setattr(verse_stats, "_scan", counting)
    vs = VerseStats("\n".join(lines))
    assert vs.meter is None
    assert len(vs.c_feet) == len(lines)
    assert calls < 10 * len(lines)


def test_polymetric():
    vs = VerseStats(LIRAS)
    assert (vs.meter, vs.n_feet) == (None, None)
    assert isnan(vs.p_deviations)
    # the lines are fitted to the common lengths: ruido takes a hiatus twice to reach 11
    assert vs.c_feet == {7: 9, 11: 6}
    assert vs.syllables[1] == (
        "la", "del", "que", "hu", "ye", "el", "mun", "da", "nal", "rui", "do"
    )  # fmt: skip
    assert sum(vs.c_rhythms.values()) == 5
    # free verse without a common length keeps the plain readings
    free = (
        "El mar\nla noche entera sobre los tejados\ny nadie pasa por la calle vacía de la ciudad"
    )
    assert VerseStats(free).c_feet == {3: 1, 11: 1, 17: 1}


def test_diaeresis():
    # a written diaeresis splits the diphthong and no synaeresis joins it back
    assert scan("Viose un guerrero en lides y rüinas").syllables[-3:] == ("rü", "i", "nas")
    assert scan("la glorïosa luz de la poesía", 11).syllables == (
        "la", "glo", "rï", "o", "sa", "luz", "de", "la", "poe", "sí", "a"
    )  # fmt: skip
    assert scan("vuestra süave musa").length == 7


@pytest.mark.parametrize(
    ("word", "consonant", "assonant"),
    [
        ("estado", "ado", ("a", "o")),
        # an aguda has its stressed vowel alone
        ("corazón", "on", ("o",)),
        ("rey", "ei", ("e",)),
        # the vowels between the stressed and the last one are left out
        ("pálido", "alido", ("a", "o")),
        # a diphthong gives its stressed vowel
        ("cielo", "elo", ("e", "o")),
        ("gracia", "aθia", ("a", "a")),
        # a final i and u sound as e and o
        ("fácil", "aθil", ("a", "e")),
        ("Venus", "enus", ("e", "o")),
        # the letters of one sound: rr, b and v, ll and y, h, ch, the u of gue and güe
        ("guerra", "eRa", ("e", "a")),
        ("lava", "aba", ("a", "a")),
        ("calle", "aʝe", ("a", "e")),
        ("haya", "aʝa", ("a", "a")),
        ("hecho", "eʧo", ("e", "o")),
        ("exige", "ixe", ("i", "e")),
        ("sigue", "ige", ("i", "e")),
        ("pingüe", "ingwe", ("i", "e")),
        ("taxi", "aksi", ("a", "e")),
    ],
)
def test_ending(word, consonant, assonant):
    assert _ending(word, seseo=False) == (consonant, assonant)


def test_seseo():
    assert _ending("caza", seseo=False).consonant == "aθa"
    assert _ending("caza", seseo=True).consonant == "asa"
    # voz and dos rhyme with seseo only: two neighbouring lines of one assonance are none
    assert VerseStats("La voz\nde los dos").c_rhymes == {}
    assert VerseStats("La voz\nde los dos", seseo=True).c_rhymes == {"consonante": 2}


def test_sonnet():
    vs = VerseStats(SONNET)
    assert vs.rhyme_schemes == ("ABBA", "ABBA", "CDE", "DCE")
    assert rhyme_scheme(SONNET) == "ABBA ABBA CDE DCE"
    assert vs.strophes == ("cuarteto", "cuarteto", "terceto", "terceto")
    assert vs.form == "soneto"
    assert (vs.p_rhymed, vs.c_rhymes) == (1.0, {"consonante": 14})
    assert vs.get_stats()["p_rhymed"] == 1.0


def test_romance():
    vs = VerseStats(ROMANCE_MACHADO)
    # the even lines share the assonance e-a, the odd ones are unrhymed
    assert vs.rhyme_schemes == ("-a-a-a-a-a-a-a-a",)
    assert (vs.form, vs.c_rhymes, vs.p_rhymed) == ("romance", {"asonante": 8}, 0.5)
    # a stanza of more than ten lines has no strophe
    assert vs.strophes == (None,)


def test_alternate_assonance():
    # The even lines in á rhyme by assonance, the nine in -ar among them as well
    vs = VerseStats(ARNALDOS)
    assert vs.rhyme_schemes[0][:20] == "-a-a-a-a-a-a-a-a-a-a"
    assert vs.form == "romance"
    assert vs.c_rhymes["asonante"] == 14
    # the assonant lines of Bécquer rhyme in full two by two, colgar - contemplar
    assert VerseStats(RIMA_LIII).rhyme_schemes == ("-A-a", "-A-a")
    assert VerseStats(RIMA_XXI).rhyme_schemes == ("-A-a",)


def test_changing_assonance(literature):
    # La tierra de Alvargonzález changes its assonance from part to part, and a title of a
    # part on a line of its own does not shift the even lines
    text = next(literature.get_records(author="machado"))["text"]
    start = text.index("Siendo mozo Alvargonzález")
    vs = VerseStats(text[start : text.index("A UN OLMO SECO")])
    assert vs.n_lines == 726
    assert vs.form == "romance"
    assert vs.p_rhymed > 0.45
    assert vs.c_rhymes["asonante"] > 300


def test_prose_is_unrhymed(literature):
    # Sentences of prose as lines share an assonance by chance, which is no rhyme
    text = next(literature.get_texts(author="galdos", genre="prose"))
    sentences = [" ".join(sentence.split()) for sentence in re.split(r"(?<=[.!?])\s+", text)]
    sentences = [sentence for sentence in sentences if 3 <= len(sentence.split()) <= 40]
    for n_lines in (5, 6, 8, 14):
        chunks = [sentences[i : i + n_lines] for i in range(0, 200 * n_lines, n_lines)]
        assonant = sum("asonante" in VerseStats("\n".join(chunk)).c_rhymes for chunk in chunks)
        assert assonant / len(chunks) < 0.05


def test_assonance():
    # A full rhyme of the same vowels as the assonance keeps its kind
    poem = """cantando por el amor
la niña va por la vida
y lleva en la mano una flor
que le dieron aquel día
y se acerca al mar
con la voz tan fina
y la luz
de la pobre niña"""
    vs = VerseStats(poem)
    assert vs.rhyme_schemes == ("abAb-b-b",)
    assert vs.c_rhymes == {"consonante": 2, "asonante": 4}
    # in a quatrain of -ado and -ano every line has its full rhyme: no assonance
    quatrain = "Cuando me paro a ver mi estado\nme das la mano\ncon el amor lejano\nde mi cuidado"
    assert VerseStats(quatrain).rhyme_schemes == ("Abba",)


@pytest.mark.parametrize(("strophe", "text"), list(STROPHES.items()))
def test_strophes(strophe, text):
    vs = VerseStats(text)
    assert vs.strophes == (strophe,)
    assert vs.form == strophe


def test_strophe_schemes():
    assert VerseStats(STROPHES["décima"]).rhyme_schemes == ("abbaaccddc",)
    assert VerseStats(STROPHES["estrofa manriqueña"]).rhyme_schemes == ("abcabc",)
    # a single lira is fitted to its 7 and 11 syllables
    lira = VerseStats(LIRAS.split("\n\n")[0])
    assert (lira.strophes, lira.rhyme_schemes, lira.c_feet) == (
        ("lira",),
        ("aBabB",),
        {7: 3, 11: 2},
    )
    # liras with no stanza breaks make a silva, a strophe or stanzas of one pattern do not
    silva = VerseStats(LIRAS.replace("\n\n", "\n"))
    assert (silva.strophes, silva.form) == ((None,), "silva")
    assert VerseStats(RIMA_XXI).form is None
    assert VerseStats(RIMA_LIII + "\n\n" + RIMA_LIII + "\n\n" + RIMA_LIII).form is None
    # a quintet of no strophe keeps its lines
    assert VerseStats("la luz\nel sol que va\nmi luz\nla voz\nel sol").strophes == (None,)
    # the other strophes by their lines alone
    assert VerseStats("la luz del día\nla noche fría").strophes == ("pareado",)


def test_scheme_letters():
    # After 26 rhyme groups the letter of a closed group is taken again
    endings = [consonant + vowel for vowel in "aeio" for consonant in "bdfglmnprst"][:30]
    poem = "\n".join(f"{article} ta{ending}" for ending in endings for article in ("la", "una"))
    scheme = VerseStats(poem).rhyme_schemes[0]
    assert scheme[:6] == "aabbcc"
    assert scheme[52:54] == "aa"


def test_pyrrhics():
    vs = VerseStats("Cuando me paro a contemplar mi estado\nsólo el serviros de encarecimiento")
    assert vs.meter == "endecasílabo"
    assert vs.patterns[1] == "+--+-----+-"
    assert vs.p_pyrrhics == 0.5
    assert vs.c_rhythms == {"4-8-10": 1}


@pytest.mark.parametrize(
    ("stresses", "rhythm"),
    [
        ((0, 5, 9), "1-6-10"),
        ((1, 5, 9), "2-6-10"),
        ((2, 5, 9), "3-6-10"),
        ((3, 5, 9), "4-6-10"),
        ((5, 9), "6-10"),
        ((1, 3, 7, 9), "4-8-10"),
        ((3, 6, 9), "4-7-10"),
        ((0, 4, 9), None),
    ],
)
def test_endecasyllable_type(stresses, rhythm):
    assert _endecasyllable_type(stresses) == rhythm


def test_stanzas():
    vs = VerseStats(GARCILASO + "\n\n\n" + ROMANCE)
    assert vs.n_stanzas == 2
    assert vs.stanzas[1][0] == "Que por mayo era, por mayo,"
    assert vs.accentuate().count("\n\n") == 1


def test_accentuate():
    assert nfc(VerseStats(GARCILASO).accentuate()).split("\n")[0] == (
        "Cuando me páro a contemplár mi estádo"
    )
    # the marks are combining characters apart from the written accents
    assert VerseStats(GARCILASO).accentuate().count("\u0301") == 14
    text = "El gato duerme tranquilamente en la ventana, muy teórico-práctico"
    assert nfc(accentuate(text)) == (
        "El gáto duérme tranquílaménte en la ventána, muý teórico-práctico"
    )
    assert nfc(accentuate("quiso la guerra, cuida la ley")) == "quíso la guérra, cuída la léy"


def test_split_stanzas():
    # the roman numerals of the parts of a poem are no lines
    assert split_stanzas("I\nuno dos\n\n(II)\nMI casa\nIV.") == [["uno dos"], ["MI casa"]]
    assert split_stanzas("uno dos\n\n\n  tres  \n1810\n***\nцвет\ncuatro") == [
        ["uno dos"],
        ["tres", "cuatro"],
    ]


def test_detect_meter():
    assert detect_meter(GARCILASO) == "endecasílabo"
    assert detect_meter(SONATINA) == "alejandrino"


def test_doc():
    doc = spacy.blank("es")(ROMANCE)
    assert VerseStats(doc).get_stats() == VerseStats(ROMANCE).get_stats()


def test_get_stats():
    vs = VerseStats(GARCILASO)
    stats = vs.get_stats()
    assert list(stats) == list(VERSE_STATS_DESC)
    assert stats["meter"] == "endecasílabo"


def test_print_stats(capsys):
    VerseStats(GARCILASO).print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(VERSE_STATS_DESC) + 1
    assert "endecasílabo" in captured.out


def rhyme_pairs(labels):
    """Pairs of the lines with the same rhyme label"""
    return {
        (first, second)
        for first, second in combinations(range(len(labels)), 2)
        if labels[first] not in ("", "-") and labels[first].lower() == labels[second].lower()
    }


def test_sonnets(sonnets):
    # Agreement with the automatic scansion and rhyme of DISCO
    meters = Counter()
    forms = Counter()
    lengths = syllables = agreed = 0
    n_lines = 0
    pairs = gold_pairs = common = 0
    for record in sonnets:
        vs = VerseStats(record["text"])
        meters[vs.meter] += 1
        forms[vs.form] += 1
        assert vs.n_lines == len(record["meter"])
        for pattern, reference in zip(vs.patterns, record["meter"], strict=True):
            n_lines += 1
            if len(pattern) == len(reference):
                lengths += 1
                syllables += len(reference)
                agreed += sum(a == b for a, b in zip(pattern, reference, strict=True))
        if any(record["rhyme"]):
            ours, gold = rhyme_pairs("".join(vs.rhyme_schemes)), rhyme_pairs(record["rhyme"])
            pairs += len(ours)
            gold_pairs += len(gold)
            common += len(ours & gold)
    assert n_lines == 60209
    assert lengths / n_lines > 0.965
    assert agreed / syllables > 0.97
    assert meters["endecasílabo"] > 3850
    assert meters["alejandrino"] > 310
    assert meters[None] < 30
    assert common / pairs > 0.98
    assert common / gold_pairs > 0.975
    assert forms["soneto"] > 3650
