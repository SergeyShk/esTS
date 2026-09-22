import random
import warnings
from collections import Counter
from math import e, inf, isnan, log, log2, log10, nan, nextafter, sqrt

import pytest
import spacy
from scipy.special import comb

from ests import DiversityStats, diversity_stats
from ests.constants import DIVERSITY_STATS_DESC
from ests.diversity_stats import (
    WindowStats,
    _max_types,
    _mtld_factor_lengths,
    calc_alpha2,
    calc_baayen_p,
    calc_brunet_w,
    calc_dugast_k,
    calc_entropy,
    calc_evenness,
    calc_frequency_spectrum,
    calc_gini_simpson_index,
    calc_hapax_index,
    calc_hapax_ratio,
    calc_hdd,
    calc_heaps_beta,
    calc_herdan_vm,
    calc_honore_r,
    calc_inverse_simpson_index,
    calc_mamtld,
    calc_mattr,
    calc_michea_m,
    calc_msttr,
    calc_mtld,
    calc_mtldw,
    calc_mttr,
    calc_perplexity,
    calc_sichel_s,
    calc_simpson_index,
    calc_sttr,
    calc_ttr,
    calc_windowed,
    calc_yule_i,
    calc_yule_k,
    calc_zipf_alpha,
    fit_zipf_mandelbrot,
)
from ests.exceptions import ParameterError

TEXT = (
    "Los tesauros son una clase especial de recursos lexicográficos que se caracterizan por"
    " los siguientes rasgos: la completitud de los significados del vocabulario de una lengua"
    " o de alguno de sus segmentos; la ordenación temática, o ideográfica, de los significados"
    " de las palabras. La diferencia entre los tesauros y las ontologías formales consiste en"
    " la salida hacia la esfera de los significados léxicos, en el establecimiento de"
    " relaciones no solo entre los significados y las palabras que los expresan, sino también"
    " entre los propios significados (el registro de diversas relaciones semánticas dentro del"
    " diccionario)."
)
RIDDLE_TEXT = (
    "Pies no tengo, ando; boca no tengo, hablo: cuándo dormir, cuándo levantarse,"
    " cuándo empezar labores"
)
# 15 words, 11 lexemes, frequency spectrum {1: 8, 2: 2, 3: 1}
riddle = (
    "pies", "no", "tengo", "ando", "boca", "no", "tengo", "hablo",
    "cuándo", "dormir", "cuándo", "levantarse", "cuándo", "empezar", "labores",
)  # fmt: skip


@pytest.fixture(scope="module")
def ds():
    return DiversityStats(TEXT)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"window_len": 0},
        {"mtld_threshold": 0},
        {"mtld_threshold": 1},
        {"mtld_min_len": -1},
        {"hdd_sample_size": 0},
        {"log_base": 1},
    ],
)
def test_init_params_error(kwargs):
    with pytest.raises(ValueError):
        DiversityStats(TEXT, **kwargs)


def test_init_params():
    ds = DiversityStats(TEXT, window_len=20, mtld_threshold=0.9, mtld_min_len=5, log_base=e)
    assert ds.mattr == pytest.approx(calc_mattr(ds.words, 20))
    assert ds.msttr == pytest.approx(calc_msttr(ds.words, 20))
    assert ds.mtld == pytest.approx(calc_mtld(ds.words, 5, 0.9))
    assert ds.mttr == pytest.approx(calc_mttr(ds.words, e))
    assert ds.mttr != pytest.approx(calc_mttr(ds.words))
    assert ds.dugast_k == pytest.approx(calc_dugast_k(ds.words, e))


def test_init_value_error():
    with pytest.raises(ValueError):
        DiversityStats("+ _")


@pytest.mark.parametrize("text", [666, ["a", "b"], {"a": "b"}])
def test_init_type_error(text):
    with pytest.raises(TypeError):
        DiversityStats(text)


def test_init_doc_lowercase():
    doc = spacy.blank("es")(RIDDLE_TEXT)
    assert DiversityStats(doc).words == DiversityStats(RIDDLE_TEXT).words == riddle
    assert DiversityStats(doc).ttr == DiversityStats(RIDDLE_TEXT).ttr


def test_single_word_nan():
    ds = DiversityStats("palabra")
    for stat in ("simpson_index", "inverse_simpson_index", "gini_simpson_index", "hapax_index"):
        assert isnan(getattr(ds, stat))


@pytest.mark.parametrize(
    "func",
    [calc_simpson_index, calc_inverse_simpson_index, calc_gini_simpson_index, calc_hapax_index],
)
def test_short_text_nan(func):
    assert isnan(func(["palabra"]))
    assert isnan(func([]))


def test_words(ds):
    assert len(ds.words) == 94
    assert len(set(ds.words)) == 55
    assert ds.frequency_spectrum == {1: 39, 2: 10, 3: 2, 5: 2, 9: 1, 10: 1}


def test_ttr(ds):
    assert ds.ttr == pytest.approx(55 / 94)


def test_rttr(ds):
    assert ds.rttr == pytest.approx(55 / sqrt(94))


def test_cttr(ds):
    assert ds.cttr == pytest.approx(55 / sqrt(2 * 94))


def test_httr(ds):
    assert ds.httr == pytest.approx(log(55) / log(94))


def test_sttr(ds):
    assert ds.sttr == pytest.approx(log10(log10(55)) / log10(log10(94)))


def test_mttr(ds):
    assert ds.mttr == pytest.approx((log10(94) - log10(55)) / log10(94) ** 2)


def test_dttr(ds):
    assert ds.dttr == pytest.approx(log10(94) ** 2 / (log10(94) - log10(55)))


def test_mattr(ds):
    assert ds.mattr == pytest.approx(0.6471111111111114)


def test_mattr_n_words():
    text = ["revolución", "socialista"]
    assert calc_mattr(text, 50) == calc_ttr(text)


def test_msttr(ds):
    assert ds.msttr == pytest.approx(0.66)


def test_msttr_n_words():
    text = ["revolución", "socialista"]
    assert calc_msttr(text, 50) == calc_ttr(text)


def test_mtld(ds):
    assert ds.mtld == pytest.approx(35.123446561723284)
    assert calc_mtld(riddle) == 15.0


def test_mtld_threshold():
    # forward pass: a factor closes exactly at the threshold (9 lexemes on 13 words),
    # backward: the threshold is not reached, a partial factor remains (11 lexemes on 15 words)
    threshold = 9 / 13
    backward = 15 / ((1 - 11 / 15) / (1 - threshold))
    assert calc_mtld(riddle, 10, threshold) == pytest.approx((15 + backward) / 2)
    assert calc_mtld(["a", "b", "c"]) == inf


def test_mtld_partial_factor():
    # an incomplete factor counts partially
    words = ["a", "b", "c", "d", "a", "b", "c", "d", "a", "b", "c"]
    factors = 1 + (1 - 4 / 5) / (1 - 0.72)
    assert calc_mtld(words, 4, 0.72) == pytest.approx(len(words) / factors)


def test_mtld_partial_factor_clamp():
    # a tail shorter than the minimum length with a TTR below the threshold weighs at most one factor
    words = [*"abcdefghij", "a", "a", "a", "a", "a", "b", "b", "b"]
    assert calc_mtld(words) == pytest.approx((18 / 2 + 18 / 1) / 2)


def test_mamtld(ds):
    assert ds.mamtld == pytest.approx(30.059322033898304)
    assert calc_mamtld(riddle) == 12.0


def test_mtldw(ds):
    assert ds.mtldw == pytest.approx(37.712765957446805)
    assert calc_mtldw(riddle) == 13.25
    assert calc_mtldw(riddle) != calc_mamtld(riddle)


def mtld_factor_lengths_by_sets(text, threshold, min_len, wrap):
    # direct enumeration with a set of lexemes per start - the reference for the block computation
    n_words = len(text)
    source = tuple(text) + tuple(text) if wrap else tuple(text)
    lengths = []
    for start in range(n_words):
        types = set()
        end = start + n_words if wrap else n_words
        for pos in range(start, end):
            types.add(source[pos])
            factor_len = pos - start + 1
            if len(types) / factor_len <= threshold and factor_len >= min_len:
                lengths.append(factor_len)
                break
    return lengths


@pytest.mark.parametrize("wrap", [False, True])
@pytest.mark.parametrize(
    "threshold, min_len",
    [(0.72, 10), (0.72, 0), (0.5, 3), (0.9, 1), (0.66, 25), (1.0, 5), (1 / 3, 2)],
)
def test_mtld_factor_lengths_match_sets(wrap, threshold, min_len, monkeypatch):
    # a block of 16 starts: the same texts go through several blocks with carried counters
    monkeypatch.setattr(diversity_stats, "MTLD_BLOCK_SIZE", 16)
    rng = random.Random(0)
    for _ in range(60):
        n_words = rng.randint(0, 200)
        vocabulary = rng.randint(1, 60)
        words = [f"w{rng.randint(0, vocabulary)}" for _ in range(n_words)]
        assert _mtld_factor_lengths(words, threshold, min_len, wrap) == (
            mtld_factor_lengths_by_sets(words, threshold, min_len, wrap)
        )
    assert _mtld_factor_lengths(riddle, 0.72, 10, wrap) == (
        mtld_factor_lengths_by_sets(riddle, 0.72, 10, wrap)
    )


def test_mtld_factor_lengths_blocks():
    rng = random.Random(1)
    words = [f"w{rng.randint(0, 40)}" for _ in range(2 * diversity_stats.MTLD_BLOCK_SIZE + 100)]
    for wrap in (False, True):
        assert _mtld_factor_lengths(words, 0.72, 10, wrap) == (
            mtld_factor_lengths_by_sets(words, 0.72, 10, wrap)
        )


def test_mtld_factor_lengths_edges():
    assert _mtld_factor_lengths([], 0.72, 10, wrap=True) == []
    assert _mtld_factor_lengths(["a"], 0.72, 1, wrap=False) == []
    assert _mtld_factor_lengths(["a"], 1.0, 1, wrap=False) == [1]
    assert _mtld_factor_lengths(["a", "a"], 0.5, 1, wrap=False) == [2]
    assert _mtld_factor_lengths(["a", "b"], 0.5, 1, wrap=True) == []
    assert _mtld_factor_lengths(["a"] * 100, 0.72, 10, wrap=False) == [10] * 91
    unique = [str(i) for i in range(100)]
    assert _mtld_factor_lengths(unique, 0.72, 10, wrap=True) == []
    assert isnan(calc_mamtld(unique)) and isnan(calc_mtldw(unique))
    assert calc_mtldw(["a"] * 500) == 10.0


@pytest.mark.parametrize(
    "threshold", [0.72, 0.5, 1 / 3, 0.66, 0.75, 1.0, 0.1, 0.29, 0.58, nextafter(0.1, 0)]
)
def test_max_types(threshold):
    # 0.29 and 0.58: floor(threshold · length) is one too low (100, 200);
    # nextafter(0.1, 0): the product rounds up, floor is too high (50, 90, 100)
    allowed = _max_types(threshold, 300)
    assert allowed[0] == -1
    for length in range(1, 301):
        assert allowed[length] / length <= threshold
        assert allowed[length] == length or (allowed[length] + 1) / length > threshold


def test_hdd(ds):
    assert ds.hdd == pytest.approx(0.7133870198529969)


def test_hdd_n_words():
    text = ["revolución", "socialista"]
    assert isnan(calc_hdd(text))


def test_hdd_params(ds):
    for sample_size in (0, -1):
        with pytest.raises(ParameterError):
            calc_hdd(ds.words, sample_size)
    for func, kwargs in (
        (calc_mattr, {"window_len": 0}),
        (calc_msttr, {"segment_len": 0}),
        (calc_mtld, {"threshold": 1.0}),
        (calc_mamtld, {"min_len": -1}),
        (calc_mtldw, {"threshold": 0.0}),
    ):
        with pytest.raises(ParameterError):
            func(ds.words, **kwargs)


def test_hdd_long_text():
    # C(N, k) overflows at N of thousands of words and k = 200; in logarithms the value is finite
    rng = random.Random(0)
    words = [str(rng.randrange(1000)) for _ in range(3000)]
    value = calc_hdd(words, 200)
    assert 0.9 < value < 0.92
    assert calc_hdd(words, 42) == pytest.approx(
        sum(
            (1 - comb(3000 - freq, 42, exact=True) / comb(3000, 42, exact=True)) / 42
            for freq in Counter(words).values()
        )
    )


def test_hdd_sample_size_longer_than_text(ds):
    assert isnan(calc_hdd(ds.words, len(ds.words) + 1))
    assert isnan(DiversityStats(TEXT, hdd_sample_size=100).hdd)
    assert DiversityStats(TEXT, hdd_sample_size=30).hdd == pytest.approx(calc_hdd(ds.words, 30))


def test_simpson_index(ds):
    # Σ n(n-1) over the spectrum {1: 39, 2: 10, 3: 2, 5: 2, 9: 1, 10: 1} is 234
    assert ds.simpson_index == pytest.approx(234 / (94 * 93))


def test_simpson_index_unique_words():
    text = ["revolución", "socialista"]
    assert calc_simpson_index(text) == 0.0


def test_inverse_simpson_index(ds):
    assert ds.inverse_simpson_index == pytest.approx(94 * 93 / 234)


def test_inverse_simpson_index_unique_words():
    text = ["revolución", "socialista"]
    assert calc_inverse_simpson_index(text) == inf


def test_gini_simpson_index(ds):
    assert ds.gini_simpson_index == pytest.approx(1 - 234 / (94 * 93))


def test_hapax_index(ds):
    assert ds.hapax_index == pytest.approx(100 * log(94) / (1 - 39 / 55))


def test_hapax_index_all_hapaxes():
    text = ["revolución", "socialista"]
    assert calc_hapax_index(text) == inf


def test_honore_r(ds):
    assert ds.honore_r == ds.hapax_index
    assert calc_honore_r is calc_hapax_index


def test_frequency_spectrum(ds):
    assert calc_frequency_spectrum(riddle) == {1: 8, 2: 2, 3: 1}
    assert ds.frequency_spectrum == {1: 39, 2: 10, 3: 2, 5: 2, 9: 1, 10: 1}


def test_yule_k(ds):
    assert calc_yule_k(riddle) == pytest.approx(1e4 * (25 - 15) / 15**2)
    # Σ i²·V_i over the fixture spectrum is 328
    assert ds.yule_k == pytest.approx(1e4 * (328 - 94) / 94**2)
    assert isnan(calc_yule_k(["palabra"]))


def test_yule_i(ds):
    assert calc_yule_i(riddle) == pytest.approx(11**2 / (25 - 11))
    assert calc_yule_i(["a", "b"]) == inf
    assert isnan(calc_yule_i(["palabra"]))


def test_herdan_vm(ds):
    assert calc_herdan_vm(riddle) == pytest.approx(sqrt(25 / 15**2 - 1 / 11))
    assert calc_herdan_vm(["a", "b"]) == 0.0
    assert isnan(calc_herdan_vm(["palabra"]))


def test_sichel_s_michea_m(ds):
    assert calc_sichel_s(riddle) == pytest.approx(2 / 11)
    assert calc_michea_m(riddle) == pytest.approx(11 / 2)
    assert calc_michea_m(["a", "b"]) == inf
    assert ds.sichel_s == pytest.approx(10 / 55)


def test_brunet_w(ds):
    assert calc_brunet_w(riddle) == pytest.approx(15 ** (11**-0.172))
    assert ds.brunet_w == pytest.approx(94 ** (55**-0.172))
    assert isnan(calc_brunet_w([]))


def test_dugast_k(ds):
    assert calc_dugast_k(riddle) == pytest.approx(log10(11) / log10(log10(15)))
    assert calc_dugast_k(riddle, e) == pytest.approx(log(11) / log(log(15)))
    assert isnan(calc_dugast_k(["a"] * 10))


def test_hapax_measures(ds):
    assert calc_baayen_p(riddle) == pytest.approx(8 / 15)
    assert calc_hapax_ratio(riddle) == pytest.approx(8 / 11)
    assert calc_alpha2(riddle) == pytest.approx(1 - 2 * 2 / 8)
    assert isnan(calc_alpha2(["a", "a"]))
    assert ds.baayen_p == pytest.approx(39 / 94)


def test_entropy(ds):
    expected = -(8 / 15 * log2(1 / 15) + 4 / 15 * log2(2 / 15) + 3 / 15 * log2(3 / 15))
    assert calc_entropy(riddle) == pytest.approx(expected)
    assert calc_perplexity(riddle) == pytest.approx(2**expected)
    assert calc_evenness(riddle) == pytest.approx(expected / log2(11))
    assert calc_entropy(["a", "a"]) == 0.0
    assert calc_perplexity(["a", "b", "c", "d"]) == pytest.approx(4.0)
    assert isnan(calc_evenness(["a", "a"]))
    assert ds.evenness == pytest.approx(0.9230945052617391)


def test_zipf_alpha(ds):
    # the frequencies 12, 6, 4, 3 on ranks 1-4 follow the law f = 12 / r exactly
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    assert calc_zipf_alpha(words) == pytest.approx(1.0)
    assert ds.zipf_alpha == pytest.approx(0.5913962565283234)
    assert isnan(calc_zipf_alpha(["palabra"]))


def test_fit_zipf_mandelbrot(ds):
    words = ["a"] * 12 + ["b"] * 6 + ["c"] * 4 + ["d"] * 3
    fit = fit_zipf_mandelbrot(words)
    assert fit.c == pytest.approx(12, rel=1e-3)
    assert fit.q == pytest.approx(0, abs=1e-3)
    assert fit.s == pytest.approx(1, rel=1e-3)
    assert fit.r2 == pytest.approx(1)
    # the frequencies 1000 / (r + 2)^1.5 on ranks 1-40, rounded to integers
    frequencies = [round(1000 / (rank + 2) ** 1.5) for rank in range(1, 41)]
    words = [f"palabra{rank}" for rank, freq in enumerate(frequencies) for _ in range(freq)]
    fit = fit_zipf_mandelbrot(words)
    assert fit.c == pytest.approx(1000, rel=0.1)
    assert fit.q == pytest.approx(2, rel=0.1)
    assert fit.s == pytest.approx(1.5, rel=0.05)
    assert fit.r2 > 0.99
    fit = fit_zipf_mandelbrot(ds.words)
    assert fit.q >= 0 and fit.s > 0 and 0 < fit.r2 <= 1
    assert all(isnan(value) for value in fit_zipf_mandelbrot(["a", "b"]))
    assert all(isnan(value) for value in fit_zipf_mandelbrot([]))
    assert all(isnan(value) for value in fit_zipf_mandelbrot([f"w{i % 10}" for i in range(70)]))
    assert all(isnan(value) for value in fit_zipf_mandelbrot([f"w{i % 10}" for i in range(30)]))
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        fit_zipf_mandelbrot(["a", "b", "c"])
        fit = fit_zipf_mandelbrot(Counter({"a": 12, "b": 6, "c": 4, "d": 0}))
    assert fit.s == pytest.approx(1, rel=1e-3)


def test_heaps_beta(ds):
    assert calc_heaps_beta(["a", "b", "c", "d"]) == pytest.approx(1.0)
    assert calc_heaps_beta(["a"] * 10) == pytest.approx(0.0)
    assert ds.heaps_beta == pytest.approx(0.8180436061700801)
    assert isnan(calc_heaps_beta(["palabra"]))


def test_windowed(ds):
    stats = ds.windowed("ttr", window_len=20)
    assert isinstance(stats, WindowStats)
    assert stats.n_windows == 4
    assert stats.mean == pytest.approx(0.8125)
    assert stats.lower < stats.mean < stats.upper
    assert ds.windowed("ttr", window_len=20, step=10).n_windows == 8
    assert ds.windowed("ttr", window_len=20, confidence=0.99).upper > stats.upper


def test_windowed_riddle():
    ds = DiversityStats(RIDDLE_TEXT)
    stats = ds.windowed("ttr", window_len=5)
    assert stats == WindowStats(
        pytest.approx(0.9333333333333332),
        pytest.approx(0.11547005383792512),
        pytest.approx(0.6464898180167025),
        pytest.approx(1.220176848649964),
        3,
    )
    assert ds.windowed("ttr", window_len=5, step=2).n_windows == 6


def test_windowed_short_text():
    stats = calc_windowed(riddle, calc_ttr, window_len=100)
    assert stats.mean == calc_ttr(riddle) and stats.n_windows == 1 and isnan(stats.upper)


def test_windowed_nan_windows():
    assert calc_windowed(riddle, calc_hdd, window_len=5) == WindowStats(nan, nan, nan, nan, 0)


def test_windowed_inf_windows():
    # four windows of unique words give inf, the fifth 1.0: the mean is infinite, all windows count
    words = [*"abcdefghijklmnop", "s", "s", "s", "s"]
    stats = calc_windowed(words, calc_inverse_simpson_index, window_len=4)
    assert stats.mean == inf
    assert stats.n_windows == 5
    assert isnan(stats.std) and isnan(stats.lower) and isnan(stats.upper)


def test_windowed_errors(ds):
    with pytest.raises(ValueError):
        ds.windowed("unknown")
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, window_len=0)
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, step=0)
    with pytest.raises(ValueError):
        calc_windowed(riddle, calc_ttr, confidence=1)


def test_sttr_base():
    assert calc_sttr(riddle, e) != pytest.approx(calc_sttr(riddle))
    assert calc_sttr(["a"], e) == 0


def test_get_stats(ds):
    stats = ds.get_stats()
    assert isinstance(stats, dict)
    for key in DIVERSITY_STATS_DESC:
        assert stats[key] == pytest.approx(getattr(ds, key), nan_ok=True)


def test_print_stats(capsys, ds):
    ds.print_stats()
    captured = capsys.readouterr()
    assert captured.out.count("|") == len(DIVERSITY_STATS_DESC) + 1
    assert "Yule's characteristic K" in captured.out


def test_custom_words_extractor():
    from ests import WordsExtractor

    extractor = WordsExtractor(lowercase=True, stopwords=["no", "cuándo"])
    ds = DiversityStats(RIDDLE_TEXT, words_extractor=extractor)
    assert ds.words == tuple(word for word in riddle if word not in ("no", "cuándo"))
    assert ds.ttr == pytest.approx(9 / 10)


def test_mtld_factor_closes_at_the_end():
    # the last word closes a factor, so no partial factor remains
    assert calc_mtld(["a"] * 10) == 10.0
    assert calc_mtld(["a"] * 20) == 10.0


def test_entropy_empty():
    assert isnan(calc_entropy([]))
    assert isnan(calc_perplexity([]))


def test_fit_zipf_mandelbrot_divergence(monkeypatch):
    def failing(*args, **kwargs):
        raise RuntimeError("Optimal parameters not found")

    monkeypatch.setattr(diversity_stats, "curve_fit", failing)
    assert all(isnan(value) for value in fit_zipf_mandelbrot(["a"] * 3 + ["b"] * 2 + ["c"]))
