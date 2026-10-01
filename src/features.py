"""Feature matrices for the learned models compared with the Scorecard formula."""

import itertools

import numpy as np
import pandas as pd

from src.data_dictionary import (
    DEMOGRAPHIC_FACTORS,
    FACTORS,
    HOUSEHOLD_ATTRIBUTES,
    NEEDS_FACTORS,
)


def factor_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature set A: the eight factor scores."""
    return df[FACTORS]


def log_factor_features(df: pd.DataFrame) -> pd.DataFrame:
    """Logarithms of the eight factor scores."""
    return np.log(df[FACTORS])


def interaction_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature set A plus the product of every pair of factors in the same block."""
    pairs = {
        f"{first}_x_{second}": df[first] * df[second]
        for block in (DEMOGRAPHIC_FACTORS, NEEDS_FACTORS)
        for first, second in itertools.combinations(block, 2)
    }
    return pd.concat([df[FACTORS], pd.DataFrame(pairs, index=df.index)], axis=1)


def attribute_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Household size and the other household attributes, one-hot encoded.

    Expects the frame from `dataset.to_english`, whose fixed categories give every
    split the same columns.
    """
    categorical = [
        column for column in HOUSEHOLD_ATTRIBUTES if column != "NumIntegrantes"
    ]
    dummies = pd.get_dummies(df[categorical], drop_first=True, dtype=float)
    # LightGBM rejects whitespace in feature names.
    dummies.columns = dummies.columns.str.replace(" ", "_")
    return pd.concat([df[["NumIntegrantes"]], dummies], axis=1)


def attribute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature set B: set A plus the household attributes."""
    return pd.concat([factor_features(df), attribute_columns(df)], axis=1)


def interaction_attribute_features(df: pd.DataFrame) -> pd.DataFrame:
    """Within-block interactions plus the household attributes."""
    return pd.concat([interaction_features(df), attribute_columns(df)], axis=1)
