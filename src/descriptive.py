"""Descriptive statistics for group rates and associations."""

import numpy as np
import pandas as pd
from scipy.stats import binomtest, chi2_contingency

# Groups below this size are flagged as unreliable in every breakdown.
SMALL_GROUP_N = 30


def rate_table(flags: pd.Series, groups: pd.Series) -> pd.DataFrame:
    """Share of True flags per group, with a Wilson 95% interval."""
    rows = []
    for group, values in flags.groupby(groups, observed=True):
        count, n = int(values.sum()), int(values.size)
        interval = binomtest(count, n).proportion_ci(method="wilson")
        rows.append(
            {
                "group": group,
                "n": n,
                "count": count,
                "rate": count / n,
                "ci_low": interval.low,
                "ci_high": interval.high,
                "small_group": n < SMALL_GROUP_N,
            }
        )
    return pd.DataFrame(rows)


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    """Bias-corrected Cramér's V (Bergsma 2013) between two categorical series."""
    table = pd.crosstab(x, y)
    table = table.loc[table.sum(axis=1) > 0, table.sum(axis=0) > 0].to_numpy()
    n = table.sum()
    rows, cols = table.shape
    chi2 = chi2_contingency(table, correction=False).statistic
    phi2 = max(0.0, chi2 / n - (rows - 1) * (cols - 1) / (n - 1))
    rows_corrected = rows - (rows - 1) ** 2 / (n - 1)
    cols_corrected = cols - (cols - 1) ** 2 / (n - 1)
    return float(np.sqrt(phi2 / min(rows_corrected - 1, cols_corrected - 1)))


def correlation_ratio(groups: pd.Series, values: pd.Series) -> float:
    """Correlation ratio (eta) of a numeric series on a categorical one."""
    deviations = values - values.mean()
    group_means = deviations.groupby(groups, observed=True).transform("mean")
    return float(np.sqrt((group_means**2).sum() / (deviations**2).sum()))
