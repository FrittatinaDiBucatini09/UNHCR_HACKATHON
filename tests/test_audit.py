"""Tests of the random audit, targeted review routing and the reviewer view."""

import dataclasses

import numpy as np
import pytest

from src.sentinella import audit, config
from src.sentinella.schema import (
    RANDOM_AUDIT,
    RECORD_FIELDS,
    TARGETED,
    Decision,
    Review,
    ReviewRequest,
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
# One decision in four is on a sentinel. Cashy's recommendation alternates, and
# the decisions follow a different cycle, so some accept it and some override it.
DECISIONS = [
    dataclasses.replace(
        BASE,
        decision_id=f"decision-{n:04d}",
        case_id=f"sentinel-{n:04d}" if n % 4 == 3 else f"case-{n:04d}",
        shown_recommendation="Include" if n % 2 else "Exclude",
        decision="Include" if n % 3 else "Exclude",
    )
    for n in range(200)
]
# Record of an S8 household scoring 40.69 (High), with household fields added.
RECORD = {
    "NumIntegrantes": 3,
    "dependencyCategory": "Average",
    "FemaleHeadedHousehold": "Female-headed",
    "CuidadorSolo": "Yes",
    "HablaEspanol": "One or more adults",
    "Analfabeta_si": "No adult",
    "Demographics.HH.Head": 1.0,
    "Demographics.Language": 1.525552408,
    "Demographics.Profiles": 2.578385269,
    "Demographics.Documentation": 1.0,
    "Needs_and_Coping.BasicNeeds": 1.776038647,
    "Needs_and_Coping.Housing": 2.117608696,
    "Needs_and_Coping.Neg.mechanism": 2.580217391,
    "Needs_and_Coping.Dependency": 1.0,
}
EXCLUSION_ON_FRAGILE = config.TargetedReview(frozenset({"Exclude"}), "recommendation")


def review(number: int, request) -> Review:
    return Review(
        review_id=f"review-{number:04d}",
        decision_id=request.decision_id,
        stream=request.stream,
        reason=request.reason,
        votes=("Include", "Include", "Exclude"),
        committee_decision="Include",
        reviewed_at="2024-02-01T10:00:00",
        simulated=True,
    )


def test_reviewer_view_never_contains_the_first_decision():
    hidden = {field.name for field in dataclasses.fields(Decision)} - {
        "case_id",
        "office",
        "month",
    }
    for decision in DECISIONS:
        if is_sentinel(decision.case_id):
            continue
        view = audit.reviewer_view(decision, RECORD)
        assert set(view) == {"case_id", "office", "month", *RECORD_FIELDS}
        assert hidden.isdisjoint(view)
        assert decision.decision not in view.values()
        assert decision.justification not in view.values()
        assert decision.caseworker not in view.values()


def test_targeted_reviews_are_excluded_from_rate_estimates():
    random_requests = audit.random_audit(
        DECISIONS, config.RandomAudit(0.3), np.random.default_rng(0)
    )
    fragile = {decision.case_id for decision in DECISIONS[::2]}
    targeted_requests = audit.targeted(DECISIONS, fragile, EXCLUSION_ON_FRAGILE) + [
        audit.refer(DECISIONS[0], "Housing does not match the narrative.")
    ]
    reviews = [
        review(number, request)
        for number, request in enumerate(random_requests + targeted_requests)
    ]
    estimated_from = audit.estimation_sample(reviews)
    assert [r.decision_id for r in estimated_from] == [
        request.decision_id for request in random_requests
    ]
    assert all(r.stream == RANDOM_AUDIT for r in estimated_from)
    # Some decisions are in both streams; only their random-audit review counts.
    both = {r.decision_id for r in random_requests} & {
        r.decision_id for r in targeted_requests
    }
    assert both
    assert len(reviews) - len(estimated_from) == len(targeted_requests)


def test_random_audit_covers_accepted_and_overridden_real_decisions():
    requests = audit.random_audit(
        DECISIONS, config.RandomAudit(0.5), np.random.default_rng(1)
    )
    by_id = {decision.decision_id: decision for decision in DECISIONS}
    selected = [by_id[request.decision_id] for request in requests]
    assert not any(is_sentinel(decision.case_id) for decision in selected)
    assert {decision.overridden for decision in selected} == {True, False}
    assert {request.reason for request in requests} == {
        "random audit, selection probability 0.5"
    }


def test_targeted_rule_selects_exclusion_recommendations_on_fragile_real_cases():
    fragile = {decision.case_id for decision in DECISIONS[::3]}
    requests = audit.targeted(DECISIONS, fragile, EXCLUSION_ON_FRAGILE)
    assert requests
    for request in requests:
        decision = next(d for d in DECISIONS if d.decision_id == request.decision_id)
        assert not is_sentinel(decision.case_id)
        assert decision.shown_recommendation == "Exclude"
        assert decision.case_id in fragile
        assert request.stream == TARGETED
    assert len(requests) == sum(
        not is_sentinel(d.case_id)
        and d.shown_recommendation == "Exclude"
        and d.case_id in fragile
        for d in DECISIONS
    )


def test_manual_referral_needs_a_reason_and_never_takes_a_sentinel():
    with pytest.raises(ValueError, match="reason"):
        audit.refer(DECISIONS[0], "  ")
    with pytest.raises(ValueError, match="sentinel"):
        audit.refer(DECISIONS[3], "Check the record.")
    request = audit.refer(DECISIONS[0], "Check the record.")
    assert request.stream == TARGETED
    assert request.reason == "manual referral: Check the record."


def test_waiting_requests_leave_out_streams_already_reviewed():
    first, second = DECISIONS[0].decision_id, DECISIONS[1].decision_id
    requests = [
        ReviewRequest(first, RANDOM_AUDIT, "random audit, selection probability 0.1"),
        ReviewRequest(first, TARGETED, "rule: Cashy recommended Exclude"),
        ReviewRequest(second, TARGETED, "rule: Cashy recommended Exclude"),
        ReviewRequest(second, TARGETED, "manual referral: housing looks wrong"),
    ]
    assert audit.pending(requests, [review(1, requests[0])]) == requests[1:3]
