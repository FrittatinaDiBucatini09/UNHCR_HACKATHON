"""Random audit and targeted review: which decisions go to the blind committee.

The random audit selects decisions on real cases with a fixed probability,
whether Cashy's advice was accepted or overridden, so its results can estimate
rates for the whole queue. Targeted reviews select decisions by rule or by a
manager's referral; they exist to catch problems and never enter a rate
estimate. Sentinels never go to the committee.
"""

from collections.abc import Mapping

import numpy as np

from src.sentinella.config import Committee, RandomAudit, TargetedReview
from src.sentinella.schema import (
    EXCLUDE,
    INCLUDE,
    RANDOM_AUDIT,
    RECORD_FIELDS,
    TARGETED,
    Decision,
    Review,
    ReviewRequest,
    is_sentinel,
)


def random_audit(
    decisions: list[Decision], settings: RandomAudit, rng: np.random.Generator
) -> list[ReviewRequest]:
    """Each decision on a real case, accepted or overridden, with equal probability."""
    reason = f"random audit, selection probability {settings.fraction:g}"
    return [
        ReviewRequest(decision.decision_id, RANDOM_AUDIT, reason)
        for decision in decisions
        if not is_sentinel(decision.case_id) and rng.random() < settings.fraction
    ]


def targeted(
    decisions: list[Decision], fragile_cases: set[str], rule: TargetedReview
) -> list[ReviewRequest]:
    """Decisions on real cases that the targeted review rule selects.

    Args:
        decisions: Decisions to screen.
        fragile_cases: IDs of the real cases that a one-level move of one factor
            makes fragile in the rule's sense (rule.fragility).
        rule: Targeted review settings of the demo configuration.
    """
    reason = "rule: Cashy recommended " + " or ".join(sorted(rule.recommendations))
    if rule.fragility != "none":
        reason += f" on a case one factor level away from another {rule.fragility}"
    return [
        ReviewRequest(decision.decision_id, TARGETED, reason)
        for decision in decisions
        if not is_sentinel(decision.case_id)
        and decision.shown_recommendation in rule.recommendations
        and (rule.fragility == "none" or decision.case_id in fragile_cases)
    ]


def refer(decision: Decision, reason: str) -> ReviewRequest:
    """A manager's referral of one decision to blind second review.

    Raises:
        ValueError: If the reason is blank or the decision is on a sentinel.
    """
    if not reason.strip():
        raise ValueError("a referral needs a written reason")
    if is_sentinel(decision.case_id):
        raise ValueError("sentinels are not sent to the committee")
    return ReviewRequest(decision.decision_id, TARGETED, f"manual referral: {reason}")


def reviewer_view(decision: Decision, record: Mapping[str, object]) -> dict:
    """What a committee reviewer sees: the case's record, office and month.

    The view is assembled from the record fields alone, so the first decision,
    its justification, the caseworker and everything Cashy displayed stay out.
    """
    return {
        "case_id": decision.case_id,
        "office": decision.office,
        "month": decision.month,
    } | {field: record[field] for field in RECORD_FIELDS}


def committee_decision(votes: tuple[str, ...], committee: Committee) -> str:
    """The committee's decision from its members' votes, by majority.

    Raises:
        ValueError: If the number of votes differs from the committee's size.
    """
    if len(votes) != committee.size:
        raise ValueError(f"{len(votes)} votes for a committee of {committee.size}")
    return INCLUDE if votes.count(INCLUDE) > len(votes) / 2 else EXCLUDE


def pending(
    requests: list[ReviewRequest], reviews: list[Review]
) -> list[ReviewRequest]:
    """Requests still waiting for the committee, one per decision and stream.

    A review of a decision in a stream answers every request for that decision
    in that stream, such as a rule selection and a manual referral.
    """
    answered = {(review.decision_id, review.stream) for review in reviews}
    waiting = []
    for request in requests:
        key = (request.decision_id, request.stream)
        if key not in answered:
            answered.add(key)
            waiting.append(request)
    return waiting


def estimation_sample(reviews: list[Review]) -> list[Review]:
    """The reviews a rate may be estimated from: those of the random audit.

    Targeted reviews are selected because a decision looks risky, so their
    disagreement with the committee says nothing about the queue as a whole.
    """
    return [review for review in reviews if review.stream == RANDOM_AUDIT]
