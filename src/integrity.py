"""Checks of the sample against the Annex I data dictionary."""

import numpy as np
import pandas as pd

from src.data_dictionary import (
    BLANK_LABELS,
    DOCUMENTED_COUNTS,
    DOCUMENTED_FACTOR_LEVELS,
    DOCUMENTED_RANGES,
    ENGLISH_NAMES,
    INCLUSION_STATUSES,
    VALUE_LABELS,
)

# Annex I prints ranges and means to one or two decimals.
RANGE_TOLERANCE = 0.05


def english_value(column: str, value: object) -> object:
    """English label of a recorded value; None stands for a blank cell."""
    if value is None:
        return BLANK_LABELS.get(column, "Blank")
    return VALUE_LABELS.get(column, {}).get(value, value)


def value_count_check(df: pd.DataFrame) -> pd.DataFrame:
    """Observed against documented count of every value in the dictionary."""
    rows = []
    for column, documented in DOCUMENTED_COUNTS.items():
        counts = df[column].value_counts(dropna=False)
        observed = {None if pd.isna(v) else v: n for v, n in counts.items()}
        for value in dict.fromkeys([*documented, *observed]):
            rows.append(
                {
                    "column": ENGLISH_NAMES[column],
                    "value_recorded": "(blank)" if value is None else value,
                    "value_english": english_value(column, value),
                    "documented": documented.get(value),
                    "observed": observed.get(value, 0),
                }
            )
    table = pd.DataFrame(rows)
    table["match"] = table["documented"] == table["observed"]
    return table


def factor_level_check(df: pd.DataFrame) -> pd.DataFrame:
    """Distinct factor levels, rounded to two decimals, against Annex I."""
    rows = []
    for column, documented in DOCUMENTED_FACTOR_LEVELS.items():
        observed = tuple(sorted(df[column].round(2).unique()))
        rows.append(
            {
                "factor": ENGLISH_NAMES[column],
                "documented_levels": ", ".join(f"{v:.2f}" for v in documented),
                "observed_levels": ", ".join(f"{v:.2f}" for v in observed),
                "n_levels": len(observed),
                "match": observed == documented,
            }
        )
    return pd.DataFrame(rows)


def range_check(df: pd.DataFrame) -> pd.DataFrame:
    """Minimum, maximum and mean of the aggregated scores against Annex I."""
    rows = []
    for column, documented in DOCUMENTED_RANGES.items():
        observed = (df[column].min(), df[column].max(), df[column].mean())
        for statistic, doc, obs in zip(("min", "max", "mean"), documented, observed):
            rows.append(
                {
                    "column": ENGLISH_NAMES[column],
                    "statistic": statistic,
                    "documented": doc,
                    "observed": obs,
                    "match": abs(obs - doc) <= RANGE_TOLERANCE,
                }
            )
    return pd.DataFrame(rows)


def blank_pattern_check(df: pd.DataFrame) -> pd.DataFrame:
    """Blank cells per column and how many fall on single-person households."""
    single = df["NumIntegrantes"].eq(1)
    rows = []
    for column in BLANK_LABELS:
        blank = df[column].isna()
        rows.append(
            {
                "column": ENGLISH_NAMES[column],
                "blank": int(blank.sum()),
                "blank_single_person": int((blank & single).sum()),
                "filled_single_person": int((~blank & single).sum()),
                "single_person_households": int(single.sum()),
            }
        )
    return pd.DataFrame(rows)


def target_rule_mismatches(df: pd.DataFrame) -> int:
    """Rows where EligibilityTarget breaks the rule INCLUSION = an Elegible status."""
    derived = np.where(
        df["Elegibilidad"].isin(INCLUSION_STATUSES), "INCLUSION", "EXCLUSION"
    )
    return int((derived != df["EligibilityTarget"]).sum())
