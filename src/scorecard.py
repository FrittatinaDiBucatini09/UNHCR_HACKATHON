"""Scorecard arithmetic recovered from the S8 synthetic sample.

A block score rescales the geometric mean of the block's four factor scores so
that all factors at 1.0 give 0 and all factors at their highest level give 50.
The vulnerability index is the sum of the two block geometric means, and the
final score rescales that sum so that the highest possible combination gives 100.
"""

import numpy as np
import pandas as pd

from src.data_dictionary import CATEGORY_ORDER, DEMOGRAPHIC_FACTORS, NEEDS_FACTORS

# Levels as stored in the sample; Annex I prints them rounded to two decimals.
FACTOR_LEVELS = {
    "Demographics.HH.Head": (1.0, 1.599560907, 2.070141643, 2.700708215),
    "Demographics.Language": (1.0, 1.525552408, 2.051104816),
    "Demographics.Profiles": (1.0, 1.249197356, 2.578385269, 3.251728045),
    "Demographics.Documentation": (1.0, 1.564135978, 2.128271955),
    "Needs_and_Coping.BasicNeeds": (1.0, 1.776038647),
    "Needs_and_Coping.Housing": (1.0, 1.498900966, 2.117608696, 2.823478261),
    "Needs_and_Coping.Neg.mechanism": (1.0, 1.790108696, 2.580217391),
    "Needs_and_Coping.Dependency": (1.0, 1.043888889, 1.738466184, 2.544987923),
}
BLOCK_MAX_SCORE = 50.0
FINAL_MAX_SCORE = 100.0
# Vulnerability index cutpoints Low|Moderate, Moderate|High, High|Severe. The
# sample pins each one only to a narrow interval; these round values lie inside.
CATEGORY_CUTPOINTS = (2.7, 2.9, 3.5)


def geometric_mean(factors: pd.DataFrame) -> pd.Series:
    """Row-wise geometric mean."""
    return np.exp(np.log(factors).mean(axis=1))


def top_geometric_mean(columns: list[str]) -> float:
    """Geometric mean when every factor in columns is at its highest level."""
    return float(np.exp(np.mean([np.log(max(FACTOR_LEVELS[c])) for c in columns])))


def block_score(factors: pd.DataFrame) -> pd.Series:
    """Score of one block, 0 to 50, from that block's four factor columns."""
    top = top_geometric_mean(list(factors.columns))
    return BLOCK_MAX_SCORE * (geometric_mean(factors) - 1) / (top - 1)


def vulnerability_index(df: pd.DataFrame) -> pd.Series:
    """Sum of the two block geometric means; 2.0 when every factor is 1.0."""
    return geometric_mean(df[DEMOGRAPHIC_FACTORS]) + geometric_mean(df[NEEDS_FACTORS])


def final_from_index(index: pd.Series | float) -> pd.Series | float:
    """Final score, 0 to 100, as a linear function of the vulnerability index."""
    top = top_geometric_mean(DEMOGRAPHIC_FACTORS) + top_geometric_mean(NEEDS_FACTORS)
    return FINAL_MAX_SCORE * (index - 2) / (top - 2)


def final_score(df: pd.DataFrame) -> pd.Series:
    """Final score from the eight factor scores."""
    return final_from_index(vulnerability_index(df))


def block_weights() -> tuple[float, float]:
    """Weights of the demographics and needs-and-coping scores in the final score.

    Each block is rescaled to 50 on its own, so the final score is a weighted
    rather than a plain sum of the two block scores.
    """
    excess_d = top_geometric_mean(DEMOGRAPHIC_FACTORS) - 1
    excess_n = top_geometric_mean(NEEDS_FACTORS) - 1
    share = FINAL_MAX_SCORE / BLOCK_MAX_SCORE / (excess_d + excess_n)
    return share * excess_d, share * excess_n


def category(index: pd.Series) -> pd.Series:
    """Vulnerability category, as recorded in the sample, from the index."""
    codes = np.digitize(index, CATEGORY_CUTPOINTS)
    return pd.Series(np.asarray(CATEGORY_ORDER)[codes], index=index.index)
