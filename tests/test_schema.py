"""Tests of the log records' own rules."""

import dataclasses

import pytest

from src.sentinella.schema import Decision

RECORDED = Decision(
    decision_id="decision-0001",
    case_id="case-0001",
    caseworker="caseworker-07",
    office="sotap",
    month="2025-01",
    variant="baseline screen",
    shown_score=40.69,
    shown_category="High",
    shown_recommendation="Include",
    reasoning_rating=4,
    answer_rating=3,
    own_category=None,
    hint_factors=None,
    decision="Include",
    justification="Housing and negative coping support inclusion.",
    opened_at="2025-01-15T09:00:00",
    decided_at="2025-01-15T09:06:30",
    simulated=False,
)


def test_recorded_decision_needs_a_written_justification():
    with pytest.raises(ValueError, match="justification"):
        dataclasses.replace(RECORDED, justification="  ")
    with pytest.raises(ValueError, match="caseworker entry"):
        dataclasses.replace(RECORDED, justification=None)
    with pytest.raises(ValueError, match="caseworker entry"):
        dataclasses.replace(RECORDED, opened_at=None)


def test_simulated_decision_may_leave_caseworker_entries_empty():
    simulated = dataclasses.replace(
        RECORDED,
        reasoning_rating=None,
        answer_rating=None,
        justification=None,
        opened_at=None,
        decided_at=None,
        simulated=True,
    )
    assert simulated.justification is None
