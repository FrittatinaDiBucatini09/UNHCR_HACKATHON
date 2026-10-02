"""Tests of the exports."""

import dataclasses

import pandas as pd

from src.data_dictionary import FACTORS
from src.sentinella import config, export, store
from src.sentinella.export import distribution_list
from src.sentinella.schema import (
    Decision,
    Review,
    ReviewRequest,
    Sentinel,
    is_sentinel,
)

BASE = Decision(
    decision_id="decision-0000",
    case_id="case-0000",
    caseworker="caseworker-01",
    office="sotap",
    month="2024-01",
    variant="B",
    shown_score=40.69,
    shown_category="High",
    shown_recommendation="Include",
    reasoning_rating=4,
    answer_rating=4,
    own_category=None,
    hint_factors=None,
    decision="Include",
    justification="Housing and negative coping support inclusion.",
    opened_at="2024-01-15T09:00:00",
    decided_at="2024-01-15T09:05:00",
    simulated=True,
)


def test_no_sentinel_id_reaches_the_distribution_list():
    # Every decision is Include, a third of them on sentinels.
    decisions = [
        dataclasses.replace(
            BASE,
            decision_id=f"decision-{n:04d}",
            case_id=f"sentinel-{n:04d}" if n % 3 == 0 else f"case-{n:04d}",
        )
        for n in range(90)
    ]
    exported = distribution_list(decisions)
    assert not exported["case_id"].map(is_sentinel).any()
    assert exported["case_id"].tolist() == [
        d.case_id for d in decisions if not is_sentinel(d.case_id)
    ]


def test_excluded_real_cases_are_not_distributed():
    decisions = [
        dataclasses.replace(BASE, decision_id="decision-0001", case_id="case-0001"),
        dataclasses.replace(
            BASE, decision_id="decision-0002", case_id="case-0002", decision="Exclude"
        ),
    ]
    assert distribution_list(decisions)["case_id"].tolist() == ["case-0001"]


# A household with every factor at its lowest level: final score 0, Low, Exclude.
RECORD = {
    "NumIntegrantes": 2,
    "dependencyCategory": "Average",
    "FemaleHeadedHousehold": "Female-headed",
    "CuidadorSolo": "No",
    "HablaEspanol": "One or more adults",
    "Analfabeta_si": "No adult",
} | dict.fromkeys(FACTORS, 1.0)
SENTINEL = Sentinel(
    sentinel_id="sentinel-0001",
    record=RECORD,
    shown_factors=dict.fromkeys(FACTORS, 1.0),
    shown_score=0.0,
    shown_category="Low",
    shown_recommendation="Exclude",
    reasoning="Every factor is at its lowest level.",
    reference_decision="Exclude",
    discordance_type=None,
    altered_factor=None,
    fragile=False,
)


def test_every_exported_column_is_documented_and_sentinels_stay_out(tmp_path):
    entered = dataclasses.replace(BASE, simulated=False)
    decisions = [
        dataclasses.replace(entered, decision_id=f"decision-{n:04d}", case_id=case)
        for n, case in enumerate(["case-0001", "case-0002", "sentinel-0001"])
    ]
    connection = store.connect(":memory:")
    store.add(
        connection,
        SENTINEL,
        *decisions,
        Review(
            review_id="review-0001",
            decision_id="decision-0000",
            stream="random_audit",
            reason="random audit, selection probability 0.1",
            votes=("Include", "Include", "Exclude"),
            committee_decision="Include",
            reviewed_at="2024-02-01T10:00:00",
            simulated=False,
        ),
        ReviewRequest("decision-0001", "targeted", "manual referral: check housing"),
    )
    paths = export.write_all(connection, config.load(), "app", tmp_path)
    schema = pd.read_csv(tmp_path / "schema.csv")
    documented = schema.groupby("table")["column"].agg(list)
    assert {path.stem for path in paths} == {*export.TABLES, "schema"}
    for path in paths:
        if path.stem != "schema":
            assert list(pd.read_csv(path).columns) == documented[path.stem]
    exported = pd.read_csv(tmp_path / "distribution_list.csv")
    assert exported["case_id"].tolist() == ["case-0001", "case-0002"]
