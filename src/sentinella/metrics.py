"""Reliance and disagreement measures, each with its interval.

Sentinels give the four reliance rates of the challenge, always relative to the
reference standard. The random audit gives disagreement with the committee,
separately for accepted and overridden decisions. Neither is pooled into a
single agreement rate. Decisions by the same caseworker are not independent,
so intervals can also be computed by resampling caseworkers.
"""

from collections.abc import Iterable, Iterator
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import binomtest

from src.sentinella import audit
from src.sentinella.schema import Decision, Review, is_sentinel

# Each reliance rate as (decision on a concordant sentinel, overridden). Correct
# override and over-reliance are shares of decisions on discordant sentinels;
# correct acceptance and under-reliance of decisions on concordant ones.
RELIANCE = {
    "correct override": (False, True),
    "over-reliance": (False, False),
    "correct acceptance": (True, False),
    "under-reliance": (True, True),
}
POOL_COLUMNS = [
    "sentinel_id",
    "concordant",
    "discordance_type",
    "direction",
    "category",
    "fragile",
    "far",
]
# Values a cell loses when it is hidden; its number of decisions stays.
HIDDEN_VALUES = [
    "count",
    "committee_differs",
    "rate",
    "ci_low",
    "ci_high",
    "cluster_ci_low",
    "cluster_ci_high",
    "median_seconds",
    "p90_seconds",
]


def wilson(count: int, n: int) -> tuple[float, float]:
    """Wilson 95% interval of count successes in n trials; NaN when n is 0."""
    if n == 0:
        return np.nan, np.nan
    interval = binomtest(count, n).proportion_ci(method="wilson")
    return float(interval.low), float(interval.high)


def sentinel_outcomes(
    decisions: Iterable[Decision], pool_table: pd.DataFrame
) -> pd.DataFrame:
    """Decisions on sentinels, each with the attributes of its sentinel.

    Args:
        decisions: Decisions; only those on sentinels are kept.
        pool_table: Output of sentinels.describe_pool.
    """
    columns = [
        "decision_id",
        "sentinel_id",
        "caseworker",
        "office",
        "month",
        "variant",
        "overridden",
    ]
    rows = [
        (
            d.decision_id,
            d.case_id,
            d.caseworker,
            d.office,
            d.month,
            d.variant,
            d.overridden,
        )
        for d in decisions
        if is_sentinel(d.case_id)
    ]
    table = pd.DataFrame(rows, columns=columns)
    return table.merge(
        pool_table[POOL_COLUMNS], on="sentinel_id", how="left", validate="many_to_one"
    )


def reliance(
    outcomes: pd.DataFrame,
    by: Iterable[str] = (),
    replicates: int = 0,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """The four reliance rates relative to the reference standard, per group.

    Args:
        outcomes: Output of sentinel_outcomes.
        by: Columns to group by; none gives one row per rate.
        replicates: Resamples of caseworkers for a clustered interval; 0 skips it.
        rng: Random generator for the resampling.

    Returns:
        One row per group and rate, in long form, with the decisions it counts,
        the number of caseworkers behind them, a Wilson 95% interval and, if
        replicates is positive, a 95% interval from resampling caseworkers.
    """
    rows = []
    for key, group in groups(outcomes, list(by)):
        for measure, (concordant, overridden) in RELIANCE.items():
            subset = group[group["concordant"] == concordant]
            hits = (subset["overridden"] == overridden).to_numpy()
            n, count = len(subset), int(hits.sum())
            row = key | {
                "measure": measure,
                "n": n,
                "count": count,
                "rate": count / n if n else np.nan,
                "caseworkers": subset["caseworker"].nunique(),
            }
            row["ci_low"], row["ci_high"] = wilson(count, n)
            if replicates:
                row["cluster_ci_low"], row["cluster_ci_high"] = caseworker_interval(
                    hits, subset["caseworker"].to_numpy(), replicates, rng
                )
            rows.append(row)
    return pd.DataFrame(rows)


def caseworker_interval(
    hits: np.ndarray,
    caseworkers: np.ndarray,
    replicates: int,
    rng: np.random.Generator,
) -> tuple[float, float]:
    """95% interval of a rate from resampling caseworkers with replacement.

    Each replicate draws as many caseworkers as there are and pools all their
    decisions, so the interval widens when caseworkers differ from each other.
    """
    if len(hits) == 0:
        return np.nan, np.nan
    names, codes = np.unique(caseworkers, return_inverse=True)
    successes = np.bincount(codes, weights=hits, minlength=len(names))
    totals = np.bincount(codes, minlength=len(names))
    draws = rng.integers(0, len(names), size=(replicates, len(names)))
    rates = successes[draws].sum(axis=1) / totals[draws].sum(axis=1)
    low, high = np.percentile(rates, [2.5, 97.5])
    return float(low), float(high)


def committee_disagreement(
    decisions: Iterable[Decision], reviews: Iterable[Review], by: Iterable[str] = ()
) -> pd.DataFrame:
    """Disagreement of caseworkers' decisions with the committee, per group.

    Only random-audit reviews count (audit.estimation_sample). Accepted and
    overridden decisions are reported in separate rows and never pooled.

    Args:
        decisions: Decisions, looked up by the reviews.
        reviews: Committee reviews of any stream.
        by: Columns to group by besides accepted or overridden: caseworker,
            office, month, variant or decision (the caseworker's).
    """
    by_id = {decision.decision_id: decision for decision in decisions}
    columns = [
        "caseworker",
        "office",
        "month",
        "variant",
        "decision",
        "action",
        "disagrees",
    ]
    rows = []
    for review in audit.estimation_sample(list(reviews)):
        decision = by_id[review.decision_id]
        rows.append(
            (
                decision.caseworker,
                decision.office,
                decision.month,
                decision.variant,
                decision.decision,
                "overridden" if decision.overridden else "accepted",
                decision.decision != review.committee_decision,
            )
        )
    table = pd.DataFrame(rows, columns=columns)
    results = []
    for key, group in groups(table, [*by, "action"]):
        n, count = len(group), int(group["disagrees"].sum())
        row = key | {
            "n": n,
            "count": count,
            "rate": count / n,
            "caseworkers": group["caseworker"].nunique(),
        }
        row["ci_low"], row["ci_high"] = wilson(count, n)
        results.append(row)
    return pd.DataFrame(results)


def decision_times(
    decisions: Iterable[Decision], by: Iterable[str] = ()
) -> pd.DataFrame:
    """Recorded time from opening a case to submitting the decision, per group.

    Ordinary simulation records have no times. Authored presentation mocks may
    carry illustrative times, but their source must remain separate. Time is not
    attention: a case can stay open while the
    caseworker does something else, and a quick decision can be a careful one.

    Args:
        decisions: Decisions with both timestamps; never pool different sources.
        by: Columns to group by: caseworker, office, month or variant.
    """
    columns = ["caseworker", "office", "month", "variant", "seconds"]
    rows = [
        (
            d.caseworker,
            d.office,
            d.month,
            d.variant,
            (
                datetime.fromisoformat(d.decided_at)
                - datetime.fromisoformat(d.opened_at)
            ).total_seconds(),
        )
        for d in decisions
        if d.opened_at is not None and d.decided_at is not None
    ]
    table = pd.DataFrame(rows, columns=columns)
    results = []
    for key, group in groups(table, list(by)):
        results.append(
            key
            | {
                "n": len(group),
                "caseworkers": group["caseworker"].nunique(),
                "median_seconds": group["seconds"].median(),
                "p90_seconds": group["seconds"].quantile(0.9),
            }
        )
    return pd.DataFrame(results)


def hide_small(table: pd.DataFrame, minimum: int) -> pd.DataFrame:
    """The table with every cell that rests on fewer than minimum caseworkers hidden.

    A hidden cell keeps its number of decisions and caseworkers but loses its
    count, rate, intervals and times, and is marked in a hidden column.
    """
    out = table.copy()
    out["hidden"] = out["caseworkers"] < minimum
    for column in HIDDEN_VALUES:
        if column in out:
            integer = pd.api.types.is_integer_dtype(out[column])
            values = out[column].astype("Int64" if integer else float)
            out[column] = values.where(~out["hidden"])
    return out


def groups(table: pd.DataFrame, by: list[str]) -> Iterator[tuple[dict, pd.DataFrame]]:
    """Each group of the table with its key as a dict; the whole table if no by."""
    if not by:
        yield {}, table
        return
    for key, group in table.groupby(by, sort=True):
        yield dict(zip(by, key)), group
