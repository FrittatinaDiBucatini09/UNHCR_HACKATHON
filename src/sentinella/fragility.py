"""Sensitivity of the category and demo recommendation to one-level factor moves.

Each factor of a case is moved one level down and one level up within its levels,
and the final score, category and demo recommendation are recomputed with the
recovered Scorecard formula. A case is fragile when one such move changes the
outcome named in the configuration.
"""

from itertools import pairwise

import numpy as np
import pandas as pd

from src import scorecard
from src.data_dictionary import FACTORS, VALUE_LABELS
from src.score_model import level_of
from src.sentinella.config import CATEGORIES, DemoRule, Fragility

DIRECTIONS = (-1, 1)
BOUNDARIES = tuple(f"{lower} | {upper}" for lower, upper in pairwise(CATEGORIES))


def snap(factors: pd.DataFrame) -> pd.DataFrame:
    """The eight factor scores of each case, snapped to their exact levels.

    Raises:
        ValueError: If a factor score is not one of that factor's levels.
    """
    return pd.DataFrame(
        {
            factor: factors[factor].map(
                {value: level_of(factor, value) for value in factors[factor].unique()}
            )
            for factor in FACTORS
        },
        index=factors.index,
    )


def outcomes(levels: pd.DataFrame, rule: DemoRule) -> pd.DataFrame:
    """Final score, category and demo recommendation of each case."""
    index = scorecard.vulnerability_index(levels)
    category = scorecard.category(index).map(VALUE_LABELS["Vulnerability_Category"])
    return pd.DataFrame(
        {
            "final_score": scorecard.final_from_index(index),
            "category": category,
            "recommendation": category.map(rule.recommend),
        }
    )


def shifts(factors: pd.DataFrame, rule: DemoRule) -> pd.DataFrame:
    """Every move of one factor by one level that stays within its levels.

    Returns:
        One row per case, factor and direction (-1 down, +1 up) for which the
        adjacent level exists, with the final score, category and demo
        recommendation before and after the move. A factor at its lowest or
        highest level has no move in that direction. Rows are sorted by case,
        by factor in FACTORS order and by direction.
    """
    levels = snap(factors)
    before = outcomes(levels, rule)
    moves = []
    for factor in FACTORS:
        ladder = scorecard.FACTOR_LEVELS[factor]
        position = levels[factor].map(ladder.index)
        for direction in DIRECTIONS:
            movable = (position + direction).between(0, len(ladder) - 1)
            if not movable.any():
                continue
            moved = levels[movable].copy()
            moved[factor] = np.asarray(ladder)[position[movable] + direction]
            after = outcomes(moved, rule)
            moves.append(
                pd.DataFrame(
                    {
                        "case": moved.index,
                        "factor": factor,
                        "direction": direction,
                        "level": levels.loc[movable, factor].to_numpy(),
                        "shifted_level": moved[factor].to_numpy(),
                        "final_score": before.loc[movable, "final_score"].to_numpy(),
                        "shifted_final_score": after["final_score"].to_numpy(),
                        "category": before.loc[movable, "category"].to_numpy(),
                        "shifted_category": after["category"].to_numpy(),
                        "recommendation": before.loc[
                            movable, "recommendation"
                        ].to_numpy(),
                        "shifted_recommendation": after["recommendation"].to_numpy(),
                    }
                )
            )
    table = pd.concat(moves, ignore_index=True)
    table["category_changes"] = table["category"] != table["shifted_category"]
    table["recommendation_changes"] = (
        table["recommendation"] != table["shifted_recommendation"]
    )
    order = {factor: rank for rank, factor in enumerate(FACTORS)}
    return table.sort_values(
        ["case", "factor", "direction"],
        key=lambda column: column.map(order) if column.name == "factor" else column,
        ignore_index=True,
    )


def boundary_distance(final: pd.Series) -> pd.DataFrame:
    """Nearest category boundary to each final score, and the distance in points."""
    points = [scorecard.final_from_index(cut) for cut in scorecard.CATEGORY_CUTPOINTS]
    distance = pd.DataFrame(
        {name: (final - point).abs() for name, point in zip(BOUNDARIES, points)}
    )
    return pd.DataFrame(
        {
            "nearest_boundary": distance.idxmin(axis=1),
            "boundary_distance": distance.min(axis=1),
        }
    )


def assess(factors: pd.DataFrame, rule: DemoRule, settings: Fragility) -> pd.DataFrame:
    """Fragility of each case under the configured rule.

    Returns:
        One row per case, in input order: final score, category, demo
        recommendation, whether the case is fragile, the factors whose one-level
        move makes it fragile (in FACTORS order), and the nearest category
        boundary with its distance in final-score points.
    """
    levels = snap(factors)
    result = outcomes(levels, rule)
    moves = shifts(levels, rule)
    triggering = moves[moves[f"{settings.changes}_changes"]]
    hints = (
        triggering.drop_duplicates(["case", "factor"])
        .groupby("case")["factor"]
        .agg(tuple)
    )
    hint_factors = [hints.get(case, ()) for case in result.index]
    result["fragile"] = [bool(names) for names in hint_factors]
    result["hint_factors"] = hint_factors
    return result.join(boundary_distance(result["final_score"]))
