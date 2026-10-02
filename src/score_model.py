"""Score model behind the Answer panel: the recovered Scorecard formula."""

from collections.abc import Mapping

import numpy as np
import pandas as pd

from src import scorecard
from src.data_dictionary import FACTORS, VALUE_LABELS

# Annex I prints the factor levels to two decimals, so a value within this distance
# of a level is read as that level.
LEVEL_TOLERANCE = 0.01


def predict(row: Mapping[str, float]) -> dict:
    """Final score, vulnerability category and factor attributions for one household.

    Args:
        row: The eight factor scores, keyed by their column names in the sample.
            Other keys are ignored. Levels rounded as in Annex I are accepted.

    Returns:
        A dict with "score" (0 to 100), "category" (Low, Moderate, High or
        Severe) and "attributions": the exact Shapley value of each factor in
        points, keyed by column name. The attributions add up to the score.

    Raises:
        ValueError: If a factor score is not one of that factor's levels.
    """
    factors = pd.DataFrame(
        [{column: level_of(column, row[column]) for column in FACTORS}]
    )
    index = scorecard.vulnerability_index(factors)
    category = scorecard.category(index).map(VALUE_LABELS["Vulnerability_Category"])
    return {
        "score": float(scorecard.final_from_index(index).iloc[0]),
        "category": category.iloc[0],
        "attributions": scorecard.shapley_values(factors).iloc[0].to_dict(),
    }


def level_of(column: str, value: float) -> float:
    """The level of factor column closest to value, if within LEVEL_TOLERANCE."""
    levels = np.asarray(scorecard.FACTOR_LEVELS[column])
    nearest = levels[np.abs(levels - float(value)).argmin()]
    # Written as "not within" so that a blank (NaN) value, which fails every
    # comparison, is rejected instead of being read as the lowest level.
    if not abs(nearest - float(value)) <= LEVEL_TOLERANCE:
        allowed = ", ".join(f"{level:.2f}" for level in levels)
        raise ValueError(f"{column} = {value} is not one of its levels: {allowed}")
    return float(nearest)
