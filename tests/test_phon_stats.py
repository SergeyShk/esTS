import random
from collections import Counter
from math import isnan, log2, nan

import pytest
import spacy

from ests import PhonStats
from ests.constants import PHON_STATS_DESC
from ests.phon_stats import (
    CONSONANT_SOUNDS,
    VOWEL_SOUNDS,
    _calc_repetition_index,
    calc_alliteration,
    calc_assonance,
    calc_consonant_clusters,
    calc_cv_entropy,
    calc_hiatus,
    cv_pattern,
    is_open_syllable,
    transcribe,
)

text = "Tres tristes tigres tragaban trigo en un trigal"


@pytest.fixture(scope="module")
def ps():
    return PhonStats(text)


def test_init_value_error():
    with pytest.raises(ValueError):
        PhonStats("¿? ...")
    with pytest.raises(ValueError):
        PhonStats(text, window_len=1)


@pytest.mark.parametrize("source", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(source):
    with pytest.raises(TypeError):
        PhonStats(source)


def test_init_extractor(ps):
    from ests import WordsExtractor

    extracted = PhonStats(text, words_extractor=WordsExtractor(min_len=4))
    assert extracted.words == tuple(word for word in ps.words if len(word) >= 4)


def test_init_doc(ps):
    doc = spacy.blank("es")(text)
    assert PhonStats(doc).words == ps.words
    assert PhonStats(doc).get_stats() == ps.get_stats()


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        # the vowels lose their accents and the diaeresis
        ("canción", "k a n θ i o n"),
        ("pingüino", "p i n g u i n o"),
        # h has no sound, ch is one sound, hi before a vowel is ʝ
        ("ahora", "a o r a"),
        ("hechizo", "e tʃ i θ o"),
        ("hielo", "ʝ e l o"),
        ("deshielo", "d e s ʝ e l o"),
        ("hijo", "i x o"),
        # c and g before e and i, qu and gu
        ("cena", "θ e n a"),
        ("casa", "k a s a"),
        ("gente", "x e n t e"),
        ("gato", "g a t o"),
        ("queso", "k e s o"),
        ("guerra", "g e r a"),
        ("guapo", "g u a p o"),
        ("acción", "a k θ i o n"),
        # ll and y, and y at the end of a syllable
        ("calle", "k a ʝ e"),
        ("yo", "ʝ o"),
        ("hoy", "o i"),
        ("rey", "r e i"),
        ("y", "i"),
        # rr and r, ñ, j, v, z
        ("perro", "p e r o"),
        ("niño", "n i ɲ o"),
        ("jarra", "x a r a"),
        ("vaca", "b a k a"),
        ("zapato", "θ a p a t o"),
        # x inside and at the start of a word, w
        ("examen", "e k s a m e n"),
        ("xilófono", "s i l o f o n o"),
        ("whisky", "u i s k i"),
        # no Spanish letters, and the letters of other alphabets have no sound
        ("2020", ""),
        ("façade", "f a a d e"),
        ("", ""),
    ],
)
def test_transcribe(word, expected):
    assert transcribe(word) == tuple(expected.split())


def test_transcribe_is_case_insensitive():
    assert transcribe("QUESO") == transcribe("Queso") == transcribe("queso")


@pytest.mark.parametrize(
    ("word", "expected"),
    [("queso", "CVCV"), ("hora", "VCV"), ("examen", "VCCVCVC"), ("instrumento", "VCCCCVCVCCV")],
)
def test_cv_pattern(word, expected):
    assert cv_pattern(transcribe(word)) == expected


@pytest.mark.parametrize(
    ("syllable", "expected"),
    [(("k", "a"), True), (("o", "i"), True), (("k", "a", "r"), False), ((), False)],
)
def test_is_open_syllable(syllable, expected):
    assert is_open_syllable(syllable) is expected


def test_sound_counts(ps):
    # tres tristes tigres tragaban trigo en un trigal: 14 vowels, 26 consonants
    assert ps.n_vowels == 14
    assert ps.n_consonants == 26
    assert ps.n_sonorants + ps.n_voiced + ps.n_voiceless == ps.n_consonants
    assert ps.p_vowels == pytest.approx(14 / 40)
    assert ps.consonant_vowel_ratio == pytest.approx(26 / 14)
    assert ps.hardness == pytest.approx(ps.n_voiceless / (ps.n_vowels + ps.n_sonorants))
    assert ps.sounds[0] == ("t", "r", "e", "s")


def test_silent_letters_are_not_counted():
    # h and the u of que are no sounds: hoja has 3, que has 2
    ps = PhonStats("hoja que")
    assert ps.n_vowels + ps.n_consonants == 5


def test_consonant_clusters(ps):
    assert calc_consonant_clusters(["instrumento", "calle"]) == {1: 3, 2: 1, 4: 1}
    # the digraphs are one sound, x is two
    assert calc_consonant_clusters(["perro", "chico", "extra"]) == {1: 4, 4: 1}
    assert calc_consonant_clusters(["2020"]) == {}
    assert ps.p_heavy_clusters == 0.0
    # n; n s t r, m, n t; k s t r, ɲ: 2 of 6 clusters of 3 consonants or more
    assert PhonStats("un instrumento extraño").p_heavy_clusters == pytest.approx(2 / 6)


def test_hiatus(ps):
    assert calc_hiatus(["poeta", "búho", "cielo", "aéreo"]) == 4
    assert calc_hiatus(["ciudad", "hielo", "guerra"]) == 0
    assert ps.p_hiatus == 0.0
    # po-e-ta and le-í-a (two): 3 hiatuses in 3 words
    assert PhonStats("el poeta leía").p_hiatus == pytest.approx(3 / 3)


def test_cv_entropy(ps):
    assert calc_cv_entropy(["casa", "pato", "sol", "mar"]) == pytest.approx(1.0)
    assert calc_cv_entropy(["casa", "casa"]) == 0.0
    assert isnan(calc_cv_entropy(["2020", "123"]))
    assert ps.cv_entropy == pytest.approx(2.75)
    assert ps.cv_entropy <= log2(len(ps.words))


def test_alliteration():
    # the repetitions of m and r gather at the start of the text - more often than expected
    clustered = ["mar", "mero", "mira", "gato", "lis", "sol", "gol", "pez"]
    assert calc_alliteration(clustered, window_len=2) > 1
    # the expected number comes from the text itself: with m in every word the repetitions
    # of m are no more than expected
    assert calc_alliteration(["mar", "mesa", "mío", "mudo"], window_len=2) <= 1
    # a window longer than the text
    assert isnan(calc_alliteration(["mamá", "mima"], window_len=3))
    # no consonant repeats in a window
    assert calc_alliteration(["dos", "pie", "luz"], window_len=2) == 0.0
    # the sounds count, not the letters: casa and queso repeat k
    assert calc_alliteration(["casa", "queso"], window_len=2) > 0.0


def repetition_index_by_windows(text, sounds, window_len):
    # a direct count over the windows - the reference for the vectorized computation
    tokens = [{sound for sound in transcribe(word) if sound in sounds} for word in text]
    n_words = len(tokens)
    if n_words < window_len:
        return nan
    n_windows = n_words - window_len + 1
    observed = 0
    for i in range(n_windows):
        counts = Counter(sound for token in tokens[i : i + window_len] for sound in token)
        observed += sum(1 for count in counts.values() if count >= 2)
    expected = 0.0
    for count in Counter(sound for token in tokens for sound in token).values():
        p = count / n_words
        p_single = window_len * p * (1 - p) ** (window_len - 1)
        expected += n_windows * (1 - (1 - p) ** window_len - p_single)
    return observed / expected if expected else nan


@pytest.mark.parametrize("window_len", [2, 3, 5])
def test_repetition_index_matches_windows(window_len):
    rng = random.Random(0)
    alphabet = "abcdefghijlmnñopqrstuvxyzáéíóúü-1"
    for _ in range(80):
        words = [
            "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 8)))
            for _ in range(rng.randint(0, 30))
        ]
        for sounds in (CONSONANT_SOUNDS, VOWEL_SOUNDS):
            expected = repetition_index_by_windows(words, sounds, window_len)
            actual = _calc_repetition_index(words, sounds, window_len)
            assert actual == pytest.approx(expected, nan_ok=True)


def test_assonance(ps):
    # a gathers in the first three words and i in the next two: 3 windows with a repetition
    # against 1.94 expected
    clustered = ["pan", "mar", "sal", "mil", "pis", "sol"]
    assert calc_assonance(clustered, window_len=2) == pytest.approx(3 / (5 / 4 + 5 / 9 + 5 / 36))
    assert calc_assonance(["pan", "mar", "sal", "sal"], window_len=2) == pytest.approx(1.0)
    assert calc_assonance(["pan", "pie", "sol"], window_len=2) == 0.0
    assert ps.assonance == pytest.approx(calc_assonance(ps.words))
    assert PhonStats(text, window_len=5).alliteration != pytest.approx(ps.alliteration)


def test_syllable_stats(ps):
    assert ps.syllables[:3] == (("tres",), ("tris", "tes"), ("ti", "gres"))
    assert ps.c_syllable_patterns == {"CCV": 3, "CCVC": 3, "CV": 3, "CVC": 3, "VC": 2}
    assert ps.p_open_syllables == pytest.approx(6 / 14)
    assert ps.mean_syllable_len == pytest.approx(40 / 14)
    assert PhonStats("mamá come papaya").p_open_syllables == 1.0
    # a word without a syllable (a number) adds nothing
    assert PhonStats("tres 2020").c_syllable_patterns == {"CCVC": 1}


def test_get_stats(ps):
    stats = ps.get_stats()
    assert list(stats) == list(PHON_STATS_DESC)
    for key in PHON_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ps, key), nan_ok=True)


def test_print_stats(capsys, ps):
    ps.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(PHON_STATS_DESC) + 1
