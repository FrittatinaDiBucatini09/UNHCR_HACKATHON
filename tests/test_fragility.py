"""Tests of the single-factor fragility of the category and demo recommendation."""

import itertools

import pandas as pd
import pytest

from src import scorecard
from src.data_dictionary import FACTORS
from src.sentinella import config, fragility

# Every combination of the eight factor levels: 13,824 households.
ALL_COMBINATIONS = pd.DataFrame(
    list(itertools.product(*(scorecard.FACTOR_LEVELS[c] for c in FACTORS))),
    columns=FACTORS,
)
RULE = config.DemoRule(include=frozenset({"High", "Severe"}))
CATEGORY_TRIGGER = config.Fragility("category")
# An S8 household scoring 24.04 (Low). Another S8 household differs from it only
# in having the dependency factor one level higher, and scores 24.60 (Moderate).
NEAR_LOW_MODERATE = (1.0, 2.051104816, 1.0, 1.0, 1.776038647, 2.823478261, 1.0, 1.0)
DEPENDENCY_RAISED_SCORE = 24.597090538408825
# Final score at the Low | Moderate cutpoint, 24.2736, minus 24.0369.
LOW_MODERATE_DISTANCE = 0.2368


def household(factors: tuple[float, ...]) -> pd.DataFrame:
    return pd.DataFrame([factors], columns=FACTORS)


def test_fragility_is_deterministic_and_independent_of_row_order():
    first = fragility.assess(ALL_COMBINATIONS, RULE, CATEGORY_TRIGGER)
    second = fragility.assess(ALL_COMBINATIONS, RULE, CATEGORY_TRIGGER)
    reversed_rows = fragility.assess(
        ALL_COMBINATIONS.iloc[::-1], RULE, CATEGORY_TRIGGER
    )
    pd.testing.assert_frame_equal(first, second)
    pd.testing.assert_frame_equal(first, reversed_rows.loc[first.index])
    pd.testing.assert_frame_equal(
        fragility.shifts(ALL_COMBINATIONS, RULE),
        fragility.shifts(ALL_COMBINATIONS.iloc[::-1], RULE),
    )


def test_shifts_stay_within_each_factors_levels():
    moves = fragility.shifts(ALL_COMBINATIONS, RULE)
    for factor, levels in scorecard.FACTOR_LEVELS.items():
        rows = moves[moves["factor"] == factor]
        assert rows["shifted_level"].isin(levels).all(), factor
        steps = rows["shifted_level"].map(levels.index) - rows["level"].map(
            levels.index
        )
        assert (steps == rows["direction"]).all(), factor
        # Every household moves the factor both ways, except one way from an end
        # level, so no move is lost and none goes past an end.
        expected = len(ALL_COMBINATIONS) * 2 * (len(levels) - 1) // len(levels)
        assert len(rows) == expected, factor


def test_dependency_step_moves_household_from_low_to_moderate():
    moves = fragility.shifts(household(NEAR_LOW_MODERATE), RULE)
    step = moves[
        (moves["factor"] == "Needs_and_Coping.Dependency") & (moves["direction"] == 1)
    ].iloc[0]
    assert step["category"] == "Low"
    assert step["shifted_category"] == "Moderate"
    assert step["shifted_final_score"] == pytest.approx(
        DEPENDENCY_RAISED_SCORE, abs=1e-4
    )
    assert step["recommendation"] == step["shifted_recommendation"] == "Exclude"
    assert not step["recommendation_changes"]


def test_household_near_low_moderate_boundary_is_fragile():
    result = fragility.assess(
        household(NEAR_LOW_MODERATE), RULE, CATEGORY_TRIGGER
    ).iloc[0]
    assert result["fragile"]
    assert "Needs_and_Coping.Dependency" in result["hint_factors"]
    assert result["nearest_boundary"] == "Low | Moderate"
    assert result["boundary_distance"] == pytest.approx(LOW_MODERATE_DISTANCE, abs=1e-4)


def test_household_with_every_factor_at_one_is_not_fragile():
    result = fragility.assess(household((1.0,) * 8), RULE, CATEGORY_TRIGGER).iloc[0]
    assert result["final_score"] == pytest.approx(0.0, abs=1e-12)
    assert not result["fragile"]
    assert result["hint_factors"] == ()
