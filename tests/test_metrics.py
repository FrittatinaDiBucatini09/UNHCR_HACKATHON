"""Tests of the reliance and disagreement measures."""

import dataclasses

import numpy as np
import pandas as pd
import pytest

from src.sentinella import metrics
from src.sentinella.schema import Decision, Review

# Counts and Wilson 95% intervals, in percent, printed in Annex II of the brief.
ANNEX_II = [
    (25, 26, 81.1, 99.3),
    (1, 26, 0.7, 18.9),
    (26, 26, 87.1, 100.0),
    (0, 26, 0.0, 12.9),
    (54, 65, 72.2, 90.3),
    (24, 36, 50.3, 79.8),
    (12, 36, 20.2, 49.7),
    (36, 36, 90.4, 100.0),
    (0, 36, 0.0, 9.6),
    (62, 90, 58.7, 77.5),
]
DECISION = Decision(
    decision_id="decision-0000",
    case_id="case-0000",
    caseworker="caseworker-01",
    office="sotap",
    month="2025-01",
    variant="baseline screen",
    shown_score=40.69,
    shown_category="High",
    shown_recommendation="Include",
    reasoning_rating=None,
    answer_rating=None,
    own_category=None,
    hint_factors=None,
    decision="Include",
    justification=None,
    opened_at=None,
    decided_at=None,
    simulated=True,
)


def outcomes(rows: list[tuple]) -> pd.DataFrame:
    """Sentinel outcomes from (caseworker, concordant, overridden) rows."""
    return pd.DataFrame(rows, columns=["caseworker", "concordant", "overridden"])


def review(number: int, decision: Decision, stream: str, committee: str) -> Review:
    return Review(
        review_id=f"review-{number:04d}",
        decision_id=decision.decision_id,
        stream=stream,
        reason="random audit, selection probability 0.1"
        if stream == "random_audit"
        else "rule: Cashy recommended Exclude on a fragile case",
        votes=(committee,) * 3,
        committee_decision=committee,
        reviewed_at=None,
        simulated=True,
    )


@pytest.mark.parametrize(("count", "n", "low", "high"), ANNEX_II)
def test_wilson_interval_matches_annex_ii(count, n, low, high):
    interval = metrics.wilson(count, n)
    assert [round(100 * bound, 1) for bound in interval] == [low, high]


def test_reliance_splits_sentinel_decisions_into_four_rates():
    # 10 decisions on discordant sentinels, 7 overridden; 20 on concordant
    # sentinels, 1 overridden.
    table = outcomes(
        [("a", False, True)] * 7
        + [("a", False, False)] * 3
        + [("b", True, False)] * 19
        + [("b", True, True)]
    )
    result = metrics.reliance(table).set_index("measure")
    assert list(result.index) == list(metrics.RELIANCE)
    assert result.loc["correct override", ["count", "n"]].tolist() == [7, 10]
    assert result.loc["over-reliance", ["count", "n"]].tolist() == [3, 10]
    assert result.loc["correct acceptance", ["count", "n"]].tolist() == [19, 20]
    assert result.loc["under-reliance", ["count", "n"]].tolist() == [1, 20]


def test_caseworker_bootstrap_widens_when_caseworkers_differ():
    # 100 decisions on discordant sentinels, half overridden in both tables:
    # alike, every caseworker overrides half the time; apart, half the
    # caseworkers always override and half never do.
    alike = outcomes([(f"cw{i}", False, j < 5) for i in range(10) for j in range(10)])
    apart = outcomes([(f"cw{i}", False, i < 5) for i in range(10) for j in range(10)])

    def correct_override(table):
        result = metrics.reliance(table, replicates=2000, rng=np.random.default_rng(0))
        return result.set_index("measure").loc["correct override"]

    alike_row, apart_row = correct_override(alike), correct_override(apart)
    assert alike_row["ci_low"] == apart_row["ci_low"]
    assert alike_row["cluster_ci_high"] - alike_row["cluster_ci_low"] == 0
    wilson_width = apart_row["ci_high"] - apart_row["ci_low"]
    assert apart_row["cluster_ci_high"] - apart_row["cluster_ci_low"] > wilson_width


def test_committee_disagreement_keeps_accepted_and_overridden_apart():
    # Four decisions accept Cashy and the committee differs on one; two
    # override it and the committee differs on both.
    decisions = [
        dataclasses.replace(DECISION, decision_id=f"decision-{n:04d}") for n in range(4)
    ] + [
        dataclasses.replace(
            DECISION, decision_id=f"decision-{n:04d}", decision="Exclude"
        )
        for n in range(4, 6)
    ]
    committee = ["Include", "Include", "Include", "Exclude", "Include", "Include"]
    reviews = [
        review(n, decision, "random_audit", verdict)
        for n, (decision, verdict) in enumerate(zip(decisions, committee))
    ]
    result = metrics.committee_disagreement(decisions, reviews).set_index("action")
    assert list(result.index) == ["accepted", "overridden"]
    assert result.loc["accepted", ["count", "n"]].tolist() == [1, 4]
    assert result.loc["overridden", ["count", "n"]].tolist() == [2, 2]


def test_targeted_reviews_never_change_committee_disagreement():
    decisions = [
        dataclasses.replace(
            DECISION,
            decision_id=f"decision-{n:04d}",
            caseworker=f"caseworker-0{n % 3}",
            decision="Include" if n % 4 else "Exclude",
        )
        for n in range(30)
    ]
    audited = [review(n, d, "random_audit", "Include") for n, d in enumerate(decisions)]
    # Targeted reviews of the same decisions, all disagreeing with them.
    targeted = [
        review(
            100 + n, d, "targeted", "Exclude" if d.decision == "Include" else "Include"
        )
        for n, d in enumerate(decisions)
    ]
    for by in ([], ["caseworker"], ["office", "month"]):
        pd.testing.assert_frame_equal(
            metrics.committee_disagreement(decisions, audited, by),
            metrics.committee_disagreement(decisions, audited + targeted, by),
        )


def test_rows_resting_on_too_few_caseworkers_lose_their_values():
    table = pd.DataFrame(
        {
            "n": [40, 6],
            "count": [30, 2],
            "rate": [0.75, 1 / 3],
            "ci_low": [0.60, 0.10],
            "ci_high": [0.86, 0.70],
            "caseworkers": [3, 2],
        }
    )
    shown = metrics.hide_small(table, minimum=3)
    assert shown["hidden"].tolist() == [False, True]
    assert shown.loc[1, ["count", "rate", "ci_low", "ci_high"]].isna().all()
    assert shown.loc[0, "count"] == 30
    assert shown["n"].tolist() == [40, 6]


def test_decision_times_come_only_from_decisions_entered_in_the_app():
    entered = dataclasses.replace(
        DECISION,
        reasoning_rating=4,
        answer_rating=3,
        justification="Housing matches the record.",
        opened_at="2026-10-02T09:00:00+00:00",
        decided_at="2026-10-02T09:05:00+00:00",
        simulated=False,
    )
    times = metrics.decision_times([entered, DECISION])
    assert times.loc[0, "n"] == 1
    assert times.loc[0, "median_seconds"] == 300
