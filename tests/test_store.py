"""Tests of the SQLite log store and its ID namespaces."""

import dataclasses
import sqlite3

import pytest

from src.sentinella import alerts, store
from src.sentinella.schema import Alert, Decision, Review, ReviewRequest, Sentinel

# Cashy reads negative coping one level too high: the record scores 24.04 (Low,
# Exclude under the demo rule) but Cashy shows 32.17 (High, Include).
SENTINEL = Sentinel(
    sentinel_id="sentinel-0001",
    record={
        "NumIntegrantes": 2,
        "FemaleHeadedHousehold": "Female-headed",
        "Needs_and_Coping.Neg.mechanism": 1.0,
    },
    shown_factors={"Needs_and_Coping.Neg.mechanism": 1.790108696},
    shown_score=32.17,
    shown_category="High",
    shown_recommendation="Include",
    reasoning="Negative coping is recorded at its second level.",
    reference_decision="Exclude",
    discordance_type="input_misread",
    altered_factor="Needs_and_Coping.Neg.mechanism",
    fragile=True,
)
SENTINEL_DECISION = Decision(
    decision_id="decision-0001",
    case_id="sentinel-0001",
    caseworker="caseworker-07",
    office="sotap",
    month="2024-01",
    variant="B",
    shown_score=32.17,
    shown_category="High",
    shown_recommendation="Include",
    reasoning_rating=2,
    answer_rating=1,
    own_category=None,
    hint_factors=("Needs_and_Coping.Neg.mechanism",),
    decision="Exclude",
    justification="The record shows no negative coping mechanism.",
    opened_at="2024-01-15T09:00:00",
    decided_at="2024-01-15T09:06:30",
    simulated=True,
)
CASE_DECISION = dataclasses.replace(
    SENTINEL_DECISION,
    decision_id="decision-0002",
    case_id="case-0001",
    hint_factors=None,
    decision="Include",
    justification="Housing and basic needs support inclusion.",
)
REVIEW = Review(
    review_id="review-0001",
    decision_id="decision-0002",
    stream="random_audit",
    reason="random audit, selection probability 0.1",
    votes=("Include", "Include", "Exclude"),
    committee_decision="Include",
    reviewed_at="2024-02-01T10:00:00",
    simulated=True,
)
REQUEST = ReviewRequest(
    decision_id="decision-0002",
    stream="targeted",
    reason="manual referral: housing does not match the narrative",
)
ALERT = Alert(
    alert_id="alert-0001",
    office="sotap",
    rule="Demo alert rule",
    evidence="3 of 9 overridden",
    opened_at="2024-02",
    owner="Office manager, sotap",
    explanation=None,
    closed_by=None,
    closed_at=None,
)


def test_records_round_trip_through_sqlite():
    connection = store.connect(":memory:")
    store.add(
        connection,
        SENTINEL,
        SENTINEL_DECISION,
        CASE_DECISION,
        REVIEW,
        REQUEST,
        ALERT,
    )
    assert store.load(connection, Sentinel) == [SENTINEL]
    assert store.load(connection, Decision) == [SENTINEL_DECISION, CASE_DECISION]
    assert store.load(connection, Review) == [REVIEW]
    assert store.load(connection, ReviewRequest) == [REQUEST]
    assert store.load(connection, Alert) == [ALERT]


def test_closed_alert_replaces_the_open_one():
    connection = store.connect(":memory:")
    store.add(connection, ALERT)
    closed = alerts.close(
        ALERT, "Office manager, sotap", "Screen reverted.", "2024-03-01T10:00:00"
    )
    store.update(connection, closed)
    assert store.load(connection, Alert) == [closed]
    with pytest.raises(KeyError, match="alert-0002"):
        store.update(connection, dataclasses.replace(closed, alert_id="alert-0002"))


def test_sentinel_id_outside_its_namespace_is_rejected():
    with pytest.raises(ValueError, match="sentinel namespace"):
        dataclasses.replace(SENTINEL, sentinel_id="case-0001")
    connection = store.connect(":memory:")
    row = store.to_row(SENTINEL) | {"sentinel_id": "case-0001"}
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        store.insert(connection, "sentinels", row)
