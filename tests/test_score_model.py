"""Tests of the score model on households from the S8 synthetic sample."""

import pytest

from src import scorecard
from src.data_dictionary import FACTORS
from src.score_model import predict

# Factor scores (in the order of FACTORS), recorded final score and recorded
# category of S8 households: one per category, then the two households on either
# side of the Low | Moderate and the High | Severe cutpoints.
RECORDED = [
    (
        (1.0, 2.051104816, 1.0, 1.0, 1.776038647, 2.823478261, 1.0, 1.0),
        24.036863632451063,
        "Low",
    ),
    (
        (2.700708215, 1.0, 1.249197356, 1.0, 1.0, 2.117608696, 2.580217391, 1.0),
        30.65974840868563,
        "Moderate",
    ),
    (
        (
            1.0,
            1.525552408,
            2.578385269,
            1.0,
            1.776038647,
            2.117608696,
            2.580217391,
            1.0,
        ),
        40.685069357186286,
        "High",
    ),
    (
        (
            1.599560907,
            2.051104816,
            3.251728045,
            1.0,
            1.776038647,
            2.823478261,
            2.580217391,
            1.043888889,
        ),
        59.79452340158775,
        "Severe",
    ),
    (
        (2.700708215, 1.0, 1.0, 1.0, 1.0, 1.498900966, 2.580217391, 1.043888889),
        24.254152154793587,
        "Low",
    ),
    (
        (1.0, 2.051104816, 1.0, 1.0, 1.776038647, 2.823478261, 1.0, 1.043888889),
        24.597090538408825,
        "Moderate",
    ),
    (
        (
            2.700708215,
            1.0,
            2.578385269,
            1.0,
            1.776038647,
            1.498900966,
            1.790108696,
            2.544987923,
        ),
        51.689151876183416,
        "High",
    ),
    (
        (
            2.700708215,
            1.0,
            3.251728045,
            1.0,
            1.776038647,
            2.117608696,
            2.580217391,
            1.043888889,
        ),
        52.20547205133984,
        "Severe",
    ),
]
# The recorded final scores were built with block weights rounded to six decimals.
RECORDED_TOLERANCE = 1e-4


@pytest.mark.parametrize(("factors", "final_score", "category"), RECORDED)
def test_predict_reproduces_recorded_score_and_category(factors, final_score, category):
    result = predict(dict(zip(FACTORS, factors)))
    assert result["score"] == pytest.approx(final_score, abs=RECORDED_TOLERANCE)
    assert result["category"] == category


@pytest.mark.parametrize("factors", [factors for factors, _, _ in RECORDED])
def test_attributions_add_up_to_the_score(factors):
    result = predict(dict(zip(FACTORS, factors)))
    assert sum(result["attributions"].values()) == pytest.approx(
        result["score"], abs=1e-9
    )


def test_lowest_levels_give_zero_score_and_zero_attributions():
    result = predict({column: 1.0 for column in FACTORS})
    assert result["score"] == pytest.approx(0.0, abs=1e-12)
    assert result["category"] == "Low"
    assert all(
        value == pytest.approx(0.0, abs=1e-12)
        for value in result["attributions"].values()
    )


def test_highest_levels_give_score_of_one_hundred():
    result = predict(
        {column: max(levels) for column, levels in scorecard.FACTOR_LEVELS.items()}
    )
    assert result["score"] == pytest.approx(100.0)
    assert result["category"] == "Severe"


def test_single_raised_factor_receives_the_whole_score():
    row = {column: 1.0 for column in FACTORS} | {"Demographics.Profiles": 3.251728045}
    result = predict(row)
    assert result["attributions"]["Demographics.Profiles"] == pytest.approx(
        result["score"]
    )
    assert result["score"] == pytest.approx(11.889, abs=1e-3)


def test_levels_rounded_as_in_annex_i_give_the_same_prediction():
    exact = dict(zip(FACTORS, RECORDED[3][0]))
    rounded = {column: round(value, 2) for column, value in exact.items()}
    assert predict(rounded) == predict(exact)


def test_value_between_levels_is_rejected():
    row = {column: 1.0 for column in FACTORS} | {"Demographics.Language": 1.3}
    with pytest.raises(ValueError, match="Demographics.Language"):
        predict(row)


def test_blank_factor_value_is_rejected():
    row = {column: 1.0 for column in FACTORS} | {"Demographics.Language": float("nan")}
    with pytest.raises(ValueError, match="Demographics.Language"):
        predict(row)
