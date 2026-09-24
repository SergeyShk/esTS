from math import isnan, sqrt

import numpy as np
import pandas as pd
import pytest
from scipy.stats import mannwhitneyu

from ests.constants import MORPHOLOGY_MARKERS_DESC, MORPHOLOGY_STATS_DESC
from ests.corpus import (
    bootstrap_median_diff,
    calc_cliff_delta,
    calc_cohen_d,
    compare_corpora,
    compare_features,
    corpus_features,
    holm_correction,
    sentence_rhythm,
    split_windows,
    text_features,
)
from ests.corpus.compare import COMPARISON_COLUMNS, compare_values
from ests.exceptions import ParameterError, SourceError, SourceTypeError
from ests.utils import get_nlp

text = (
    "El gato estaba en la ventana. Miraba los pájaros, pero los pájaros se fueron. "
    "El gato durmió. Mañana volverá a estar en la ventana y mirará los pájaros."
)
short = [
    "El gato duerme. El perro come. Llueve mucho. El gato salta. Sale el sol. El niño lee.",
    "Era de noche. La luz ardía. El gato esperaba. Un ratón corrió. El gato saltó. Todo calló.",
    "Llegó la mañana. Cantaban los pájaros. El gato despertó. Salió el sol. Brillaba el rocío.",
]
long = [
    "Cuando al otro lado de la ventana amanecía un día largo y brumoso, el viejo gato se "
    "levantaba despacio del sillón hundido y se acercaba al cristal frío, tras el cual "
    "despertaba el patio.",
    "El perro, que había vivido once años en aquella casa y conocía cada rincón, cada tabla "
    "que crujía y cada olor, estaba tumbado junto a la puerta esperando a que el dueño "
    "tomara la correa.",
    "La lluvia, que había empezado ya por la noche, no terminaba nunca, y los chorros grises "
    "corrían por los cristales, por los tejados y por las hojas del viejo tilo, bajo el cual "
    "había un banco olvidado.",
]


def test_split_windows():
    assert split_windows(text, 5) == [
        "El gato estaba en la",
        "ventana. Miraba los pájaros, pero",
        "los pájaros se fueron. El",
        "gato durmió. Mañana volverá a",
        "estar en la ventana",
        "y mirará los pájaros.",
    ]
    assert split_windows(text, None) == [text]
    assert split_windows(text, 100) == [text]
    assert split_windows(" \n" + text + "\n ", None) == [text]
    assert len(split_windows(text, 8)) == 4
    assert split_windows("¿Quién es?! Nadie… ¡¡Se fueron!!", None) == [
        "¿Quién es?! Nadie… ¡¡Se fueron!!"
    ]
    # Opening marks stay with the first word of the next window
    assert split_windows("El gato duerme mucho. ¿Dónde está el perro?", 4) == [
        "El gato duerme mucho.",
        "¿Dónde está el perro?",
    ]
    assert split_windows("(Gato) duerme. «Perro» come.", 2) == ["(Gato) duerme.", "«Perro» come."]
    assert split_windows("—Se fueron —dijo él—. —Todos se fueron.", 3) == [
        "—Se fueron —dijo él—.",
        "—Todos se fueron.",
    ]
    assert split_windows("«Gato» duerme.\n¡Perro! come", 2) == ["«Gato» duerme.", "¡Perro! come"]
    assert (
        text_features("—Se fueron —dijo él.")["punct_dash"]
        == corpus_features(["—Se fueron —dijo él."], None)["punct_dash"].iloc[0]
    )
    assert [len(chunk.split()) for chunk in split_windows(" ".join(["a"] * 1500), 1000)] == [
        750,
        750,
    ]
    assert len(split_windows(" ".join(["a"] * 2500), 1000)) == 3
    assert len(split_windows(" ".join(["a"] * 3500), 1000)) == 4
    assert len(split_windows(" ".join(["a"] * 1499), 1000)) == 1
    assert split_windows("", 5) == []
    assert split_windows("... ¡!", 5) == []
    with pytest.raises(ParameterError):
        split_windows(text, 0)


def test_text_features():
    features = text_features(text)
    prefixes = {key.split("_", 1)[0] for key in features}
    assert prefixes == {"basic", "readability", "diversity", "morph", "sents", "punct"}
    assert features["basic_words_per_sent"] == 7.0
    assert features["basic_letters_per_word"] == pytest.approx(4.5, rel=0.2)
    assert features["morph_pos_NOUN"] == pytest.approx(7 / 28)
    assert features["morph_pos_INTJ"] == 0.0
    assert features["morph_mood_Sub"] == 0.0
    assert isnan(text_features("El gato, el perro, la casa.")["morph_tense_Past"])
    n_morph = sum(len(desc["values"]) for desc in MORPHOLOGY_STATS_DESC.values())
    assert sum(1 for key in features if key.startswith("morph_")) == n_morph + len(
        MORPHOLOGY_MARKERS_DESC
    )
    assert features["morph_number_Sing"] + features["morph_number_Plur"] == pytest.approx(1.0)
    assert set(MORPHOLOGY_MARKERS_DESC) <= {key.removeprefix("morph_") for key in features}
    assert features["sents_mean"] == 7.0
    assert features["punct_period"] == pytest.approx(4 / 28 * 1000)
    assert isnan(features["punct_inverted_share"])
    assert text_features("¿Vienes? ¡Ven!")["punct_inverted_share"] == 0.5
    assert all(isinstance(value, float) for value in features.values())
    assert text_features(text, nlp=get_nlp()) == pytest.approx(features, nan_ok=True)
    with pytest.raises(SourceError):
        text_features("...")


def test_sentence_rhythm():
    rhythm = sentence_rhythm([4, 8, 2, 7])
    assert rhythm["sents_mean"] == 5.25
    assert rhythm["sents_std"] == pytest.approx(np.std([4, 8, 2, 7], ddof=1))
    assert rhythm["sents_cv"] == pytest.approx(rhythm["sents_std"] / 5.25)
    centered = np.array([4, 8, 2, 7]) - 5.25
    assert rhythm["sents_autocorr"] == pytest.approx(
        (centered[:-1] * centered[1:]).sum() / (centered**2).sum()
    )
    assert sentence_rhythm([5, 5, 5])["sents_std"] == 0
    assert isnan(sentence_rhythm([5, 5, 5])["sents_autocorr"])
    assert isnan(sentence_rhythm([3])["sents_std"])
    assert isnan(sentence_rhythm([3, 4])["sents_autocorr"])
    assert all(isnan(value) for value in sentence_rhythm([]).values())


def test_corpus_features():
    table = corpus_features([text, "El gato duerme."], window=8)
    assert table.index.names == ["text", "window"]
    assert list(table.index) == [(0, 0), (0, 1), (0, 2), (0, 3), (1, 0)]
    assert "morph_pos_NOUN" in table.columns
    assert table.dtypes.eq(float).all()
    custom = corpus_features([text], window=None, features=lambda t: {"length": len(t)})
    assert custom.loc[(0, 0), "length"] == len(text)
    assert corpus_features([text, "..."], window=None).shape[0] == 1
    with pytest.raises(SourceError):
        corpus_features(["...", ""])
    with pytest.raises(SourceTypeError):
        corpus_features(text)


def test_compare_corpora():
    result = compare_corpora(
        short, long, window=None, labels=("cortos", "largos"), n_bootstrap=200
    )
    columns = [
        column.replace("_a", "_cortos").replace("_b", "_largos") for column in COMPARISON_COLUMNS
    ]
    assert list(result.columns) == columns
    row = result.loc["sents_mean"]
    assert row["mean_cortos"] < row["mean_largos"]
    assert row["cliff_delta"] == -1.0
    assert row["auc"] == 0.0
    assert row["ci_low"] <= row["median_diff"] <= row["ci_high"]
    assert row["n_cortos"] == 3 and row["n_largos"] == 3
    assert result["n_cortos"].dtype.kind == "i"
    assert result["cliff_delta"].abs().dropna().is_monotonic_decreasing
    assert (result["p_holm"].dropna() >= result["p_value"].dropna()).all()
    assert abs(result.iloc[0]["cliff_delta"]) == 1.0
    assert result["cliff_delta"].isna().sum() == result["u"].isna().sum()
    assert np.isfinite(result.drop(columns=["p_holm"]).dropna()).all().all()
    undefined = result[result["cliff_delta"].isna()]
    assert list(undefined.index) == list(result.index[-len(undefined) :])
    # One sentence per long text: no standard deviation of the lengths
    assert result.loc["sents_std", "n_largos"] == 0


def test_compare_features():
    table_short = corpus_features(short, window=None)
    table_long = corpus_features(long, window=None)
    result = compare_features(table_short, table_long, labels=("cortos", "largos"), seed=1)
    expected = compare_corpora(short, long, window=None, labels=("cortos", "largos"), seed=1)
    pd.testing.assert_frame_equal(result, expected)
    # A feature in one table only gives nan, the number of samples is checked
    extra = table_short.assign(extra=1.0)
    assert isnan(compare_features(extra, table_long, n_bootstrap=10).loc["extra", "cliff_delta"])
    with pytest.raises(ParameterError):
        compare_features(table_short, table_long, n_bootstrap=0)


def test_compare_corpora_rare_values():
    a = ["¡Ay! El gato duerme en casa. ¡Oh! El gato duerme en la cama."] * 3
    b = ["El gato duerme en casa. El gato duerme en la cama."] * 3
    result = compare_corpora(a, b, window=None, n_bootstrap=10)
    row = result.loc["morph_pos_INTJ"]
    assert row["mean_A"] == pytest.approx(2 / 13)
    assert row["mean_B"] == 0.0
    assert row["cliff_delta"] == 1.0
    assert (row["n_A"], row["n_B"]) == (3, 3)
    # Without question and exclamation marks in B the share of the inverted ones is undefined
    # there, and a side without values leaves the feature without statistics
    inverted = result.loc["punct_inverted_share"]
    assert isnan(inverted["mean_A"]) and isnan(inverted["cliff_delta"])
    assert (inverted["n_A"], inverted["n_B"]) == (3, 0)


def test_compare_corpora_options():
    def lengths(text):
        return {"length": float(len(text)), "constant": 1.0}

    result = compare_corpora(short, long, window=None, features=lengths, n_bootstrap=50, seed=1)
    assert list(result.index) == ["length", "constant"]
    assert result.loc["length", "cliff_delta"] == -1.0
    assert isnan(result.loc["constant", "cohen_d"])
    assert result.loc["constant", "cliff_delta"] == 0.0
    repeated = compare_corpora(short, long, window=None, features=lengths, n_bootstrap=50, seed=1)
    assert result.equals(repeated)
    windowed = compare_corpora(short, long, window=5, features=lengths, n_bootstrap=50)
    assert windowed.loc["length", "n_A"] > 3
    with pytest.raises(ParameterError):
        compare_corpora(short, long, features=lengths, n_bootstrap=0)
    with pytest.raises(SourceError):
        compare_corpora(["..."], long, features=lengths)
    single = compare_corpora(short[:1], long, window=None, features=lengths, n_bootstrap=50)
    assert isnan(single.loc["length", "cliff_delta"])
    assert (single.loc["length", "n_A"], single.loc["length", "n_B"]) == (1, 3)


def test_compare_values():
    a = np.array([1.0, 2.0, 3.0, 4.0])
    b = np.array([3.0, 4.0, 5.0, 6.0])
    values = compare_values(a, b, n_bootstrap=100, rng=np.random.default_rng(0))
    assert len(values) == len(COMPARISON_COLUMNS)
    assert values[:5] == (2.5, 4.5, 2.5, 4.5, -2.0)
    assert values[8] == pytest.approx(calc_cliff_delta(a, b))
    assert values[9] == pytest.approx(mannwhitneyu(a, b)[0] / 16)
    assert values[11] == pytest.approx(mannwhitneyu(a, b, alternative="two-sided")[1])
    assert isnan(values[12])
    assert values[13:] == (4, 4)
    assert all(isnan(value) for value in compare_values(np.array([1.0]), b)[:13])
    assert compare_values(np.array([1.0]), b)[13:] == (1, 4)


def test_effect_sizes():
    a = [2.0, 4.0, 6.0, 8.0]
    b = [1.0, 3.0, 5.0, 7.0]
    assert calc_cohen_d(a, b) == pytest.approx(1 / sqrt(20 / 3))
    assert isnan(calc_cohen_d([1.0, 1.0], [1.0, 1.0]))
    assert isnan(calc_cohen_d([1.0], [2.0, 3.0]))
    assert calc_cliff_delta(a, b) == pytest.approx((10 - 6) / 16)
    assert calc_cliff_delta([1, 1], [1, 1]) == 0.0
    assert calc_cliff_delta([5, 6], [1, 2]) == 1.0
    assert isnan(calc_cliff_delta([], [1.0]))
    low, high = bootstrap_median_diff(a, b, n_bootstrap=500, rng=np.random.default_rng(0))
    assert low <= 1.0 <= high
    assert bootstrap_median_diff([3.0, 3.0, 3.0], [1.0, 1.0, 1.0], n_bootstrap=10) == (2.0, 2.0)
    assert all(isnan(value) for value in bootstrap_median_diff([], [1.0]))
    with pytest.raises(ParameterError):
        bootstrap_median_diff(a, b, n_bootstrap=0)
    with pytest.raises(ParameterError):
        bootstrap_median_diff(a, b, confidence=1.0)


def test_holm_correction():
    adjusted = holm_correction([0.01, 0.04, 0.03, float("nan")])
    assert adjusted[:3] == pytest.approx([0.03, 0.06, 0.06])
    assert isnan(adjusted[3])
    assert list(holm_correction([0.5, 0.9])) == [1.0, 1.0]
    assert list(holm_correction([])) == []
    assert all(isnan(value) for value in holm_correction([float("nan")]))
