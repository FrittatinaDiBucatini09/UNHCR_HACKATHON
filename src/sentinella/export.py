"""Exports of the prototype's records: the distribution list and tidy CSV tables.

The monitoring tables are aggregates in long form, one row per group and
measure, so that a BI tool such as Power BI can filter and plot them without
reshaping. A row that rests on fewer caseworkers than the configured minimum
keeps its number of decisions but not its values. schema.csv, written with the
tables, describes every column.

Run from the repository root:

    python -m src.sentinella.export simulation
    python -m src.sentinella.export app
"""

import argparse
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

from src.dataset import REPO_ROOT
from src.sentinella import audit, metrics, sentinels, store
from src.sentinella.config import Config, load
from src.sentinella.schema import (
    CASE_PREFIX,
    INCLUDE,
    TARGETED,
    Alert,
    Decision,
    Review,
    ReviewRequest,
    Sentinel,
)

EXPORT_DIR = REPO_ROOT / "data" / "exports"
SOURCES = {"simulation": store.SIMULATION_DATABASE, "app": store.APP_DATABASE}
DISTRIBUTION_COLUMNS = ["case_id", "office", "month"]

RELIANCE_BREAKDOWNS = {
    "all": [],
    "office": ["office"],
    "month": ["month"],
    "office and month": ["office", "month"],
    "category": ["category"],
    "direction": ["direction"],
    "discordance type": ["discordance_type"],
    "variant": ["variant"],
}
DISAGREEMENT_BREAKDOWNS = {
    "all": [],
    "office": ["office"],
    "month": ["month"],
    "office and month": ["office", "month"],
    "variant": ["variant"],
    "decision": ["decision"],
}

COLUMNS = {
    "source": "simulation for the simulated year, app for decisions entered in "
    "the app; the two are never pooled",
    "breakdown": "grouping of the row; the grouping columns it does not use are blank",
    "office": "UNHCR field office of the decision",
    "month": "month of the decision, YYYY-MM",
    "category": "vulnerability category the Scorecard formula gives the "
    "sentinel's record",
    "direction": "Cashy's displayed recommendation on a discordant sentinel: "
    "Exclude means Cashy excluded a household the reference decision includes",
    "discordance_type": "how Cashy's answer was made discordant: input_misread, "
    "category_mismatch or reasoning_inconsistency",
    "variant": "workflow variant of the caseworker screen, A or B; in the "
    "simulation, baseline screen or changed screen",
    "decision": "the caseworker's decision, Include or Exclude",
    "action": "accepted or overridden: whether the caseworker's decision followed "
    "Cashy's displayed recommendation",
    "measure": "reliance rate relative to the reference standard: correct "
    "override, over-reliance, correct acceptance or under-reliance",
    "n": "decisions the rate is a share of",
    "count": "decisions among n that meet the measure; blank when hidden",
    "rate": "count divided by n; blank when hidden",
    "ci_low": "lower end of the Wilson 95% interval of the rate; blank when hidden",
    "ci_high": "upper end of the Wilson 95% interval of the rate; blank when hidden",
    "cluster_ci_low": "lower end of a 95% interval from resampling caseworkers, "
    "which allows for decisions by one caseworker not being independent; blank "
    "when hidden",
    "cluster_ci_high": "upper end of the interval from resampling caseworkers; "
    "blank when hidden",
    "caseworkers": "distinct caseworkers behind the row",
    "hidden": "true when the row rests on fewer caseworkers than the configured "
    "minimum; its values are then blank",
    "reviewed": "targeted reviews the committee has completed",
    "committee_differs": "completed targeted reviews whose committee decision "
    "differs from the caseworker's; a count to follow up, not a rate",
    "waiting": "targeted review requests the committee has not yet completed",
    "median_seconds": "median recorded time from opening the case to submitting "
    "the decision; recorded time is not attention",
    "p90_seconds": "90th percentile of the same recorded time",
    "alert_id": "alert identifier",
    "rule": "the alert rule in words, with its demo values",
    "evidence": "the numbers that met the rule",
    "opened_at": "month in which the alert opened",
    "owner": "named owner who must explain the alert",
    "explanation": "the owner's written explanation; blank while open",
    "closed_by": "who closed the alert; always its owner",
    "closed_at": "when the alert was closed",
    "case_id": "real case to pay; sentinels never appear",
}
TABLES = {
    "sentinel_reliance": (
        "Reliance on sentinels relative to the reference standard",
        [
            "source",
            "breakdown",
            "office",
            "month",
            "category",
            "direction",
            "discordance_type",
            "variant",
            "measure",
            "n",
            "count",
            "rate",
            "ci_low",
            "ci_high",
            "cluster_ci_low",
            "cluster_ci_high",
            "caseworkers",
            "hidden",
        ],
    ),
    "committee_disagreement": (
        (
            "Disagreement with the committee on the random audit, accepted and "
            "overridden decisions apart; disagreement is not an established error"
        ),
        [
            "source",
            "breakdown",
            "office",
            "month",
            "variant",
            "decision",
            "action",
            "n",
            "count",
            "rate",
            "ci_low",
            "ci_high",
            "caseworkers",
            "hidden",
        ],
    ),
    "targeted_reviews": (
        "Targeted reviews by office and month, as counts; they never estimate a rate",
        [
            "source",
            "office",
            "month",
            "reviewed",
            "committee_differs",
            "waiting",
            "caseworkers",
            "hidden",
        ],
    ),
    "decision_times": (
        (
            "Recorded decision time by office and variant, for decisions entered in "
            "the app"
        ),
        [
            "source",
            "office",
            "variant",
            "n",
            "median_seconds",
            "p90_seconds",
            "caseworkers",
            "hidden",
        ],
    ),
    "alerts": (
        "Alert log",
        [
            "source",
            "alert_id",
            "office",
            "rule",
            "evidence",
            "opened_at",
            "owner",
            "explanation",
            "closed_by",
            "closed_at",
        ],
    ),
    "distribution_list": (
        (
            "Real cases decided Include, the only rows that can reach cash "
            "distribution; written for the app only"
        ),
        DISTRIBUTION_COLUMNS,
    ),
}


def distribution_list(decisions: list[Decision]) -> pd.DataFrame:
    """Real cases decided Include: the only rows that can reach cash distribution.

    Rows are chosen by the real-case ID namespace, so a decision on a sentinel
    is never exported, whatever its outcome.
    """
    return pd.DataFrame(
        [
            (decision.case_id, decision.office, decision.month)
            for decision in decisions
            if decision.case_id.startswith(CASE_PREFIX) and decision.decision == INCLUDE
        ],
        columns=DISTRIBUTION_COLUMNS,
    )


def reliance_table(
    decisions: list[Decision], pool_table: pd.DataFrame, config: Config, source: str
) -> pd.DataFrame:
    """Reliance on sentinels under every breakdown, with small cells hidden."""
    outcomes = metrics.sentinel_outcomes(decisions, pool_table)
    rng = np.random.default_rng(config.metrics.seed)
    parts = [
        metrics.reliance(outcomes, by, config.metrics.bootstrap_replicates, rng).assign(
            breakdown=name
        )
        for name, by in RELIANCE_BREAKDOWNS.items()
    ]
    return finished(parts, "sentinel_reliance", config, source)


def disagreement_table(
    decisions: list[Decision], reviews: list[Review], config: Config, source: str
) -> pd.DataFrame:
    """Random-audit disagreement with the committee under every breakdown."""
    parts = [
        metrics.committee_disagreement(decisions, reviews, by).assign(breakdown=name)
        for name, by in DISAGREEMENT_BREAKDOWNS.items()
    ]
    return finished(parts, "committee_disagreement", config, source)


def targeted_table(
    decisions: list[Decision],
    reviews: list[Review],
    requests: list[ReviewRequest],
    config: Config,
    source: str,
) -> pd.DataFrame:
    """Completed and waiting targeted reviews per office and month."""
    by_id = {decision.decision_id: decision for decision in decisions}
    rows = [
        (
            by_id[r.decision_id],
            "reviewed",
            r.committee_decision != by_id[r.decision_id].decision,
        )
        for r in reviews
        if r.stream == TARGETED
    ] + [
        (by_id[r.decision_id], "waiting", False)
        for r in audit.pending(requests, reviews)
        if r.stream == TARGETED
    ]
    table = pd.DataFrame(
        [
            (d.office, d.month, d.caseworker, state, differs)
            for d, state, differs in rows
        ],
        columns=["office", "month", "caseworker", "state", "differs"],
    )
    counts = table.groupby(["office", "month"]).agg(
        reviewed=("state", lambda s: int((s == "reviewed").sum())),
        committee_differs=("differs", "sum"),
        waiting=("state", lambda s: int((s == "waiting").sum())),
        caseworkers=("caseworker", "nunique"),
    )
    return finished([counts.reset_index()], "targeted_reviews", config, source)


def times_table(decisions: list[Decision], config: Config, source: str) -> pd.DataFrame:
    """Recorded decision time per office and variant."""
    times = metrics.decision_times(decisions, ["office", "variant"])
    return finished([times], "decision_times", config, source)


def finished(
    parts: list[pd.DataFrame], name: str, config: Config, source: str
) -> pd.DataFrame:
    """The parts as one table in its documented columns, with small cells hidden.

    Rows without decisions are dropped.
    """
    columns = TABLES[name][1]
    table = pd.concat(parts, ignore_index=True).reindex(columns=columns)
    if "n" in columns:
        table = table[table["n"] > 0]
    table = metrics.hide_small(table, config.monitor.minimum_caseworkers)
    return table.assign(source=source).reset_index(drop=True)


def write_all(
    connection: sqlite3.Connection, config: Config, source: str, folder: Path
) -> list[Path]:
    """Every table of one source, and schema.csv, written as CSV files.

    Returns:
        The paths written.
    """
    decisions = store.load(connection, Decision)
    reviews = store.load(connection, Review)
    pool = store.load(connection, Sentinel)
    tables = {
        "sentinel_reliance": reliance_table(
            decisions, sentinels.describe_pool(pool, config), config, source
        ),
        "committee_disagreement": disagreement_table(
            decisions, reviews, config, source
        ),
        "targeted_reviews": targeted_table(
            decisions, reviews, store.load(connection, ReviewRequest), config, source
        ),
        "decision_times": times_table(decisions, config, source),
        "alerts": pd.DataFrame(
            [vars(alert) for alert in store.load(connection, Alert)],
            columns=TABLES["alerts"][1][1:],
        ).assign(source=source)[TABLES["alerts"][1]],
    }
    if source == "app":
        tables["distribution_list"] = distribution_list(decisions)
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, table in tables.items():
        paths.append(folder / f"{name}.csv")
        table.to_csv(paths[-1], index=False)
    paths.append(folder / "schema.csv")
    schema().to_csv(paths[-1], index=False)
    return paths


def schema() -> pd.DataFrame:
    """One row per table and column, with what the column holds."""
    return pd.DataFrame(
        [
            (name, description, column, COLUMNS[column])
            for name, (description, columns) in TABLES.items()
            for column in columns
        ],
        columns=["table", "table_description", "column", "description"],
    )


def main() -> None:
    """Write the CSV tables of one source to data/exports/<source>/."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("source", choices=list(SOURCES))
    source = parser.parse_args().source
    if not SOURCES[source].exists():
        parser.error(f"{SOURCES[source]} does not exist yet")
    connection = store.connect(SOURCES[source])
    for path in write_all(connection, load(), source, EXPORT_DIR / source):
        print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
