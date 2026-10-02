"""Illustrative dashboard fixtures, never pooled with app or field records."""

from datetime import UTC, datetime, timedelta

from src.sentinella import alerts, casework, store
from src.sentinella.schema import (
    RANDOM_AUDIT,
    TARGETED,
    Alert,
    Decision,
    Review,
    ReviewRequest,
)


def connection(book, staff, config):
    """Ephemeral, deterministic mock; no writes to either persistent database.

    Timings, decisions, reviews and alerts are authored presentation examples.
    The review fraction here is not an audit recommendation or model benchmark.
    """
    db = store.connect(":memory:")
    office = staff.iloc[0]["office"]
    people = staff.loc[staff["office"] == office, "caseworker"].head(3)
    real = book.queue.loc[book.queue["office"] == office, "case_id"].tolist()
    pool = list(book.pool.values())
    store.add(db, *pool)
    number = 0
    for person in people:
        for month in range(6, 10):
            for slot in range(4):
                number += 1
                case_id = (
                    pool[number % len(pool)].sentinel_id
                    if slot == 0
                    else real[number % len(real)]
                )
                shown = casework.display(case_id, book, config.simulation)
                choice = shown.shown_recommendation
                if number % 7 == 0:
                    choice = "Exclude" if choice == "Include" else "Include"
                opened = datetime(2026, month, 10, 9, tzinfo=UTC) + timedelta(
                    minutes=number * 13
                )
                submitted = opened + timedelta(seconds=90 + (number % 8) * 45)
                decision = Decision(
                    decision_id=f"mock-decision-{number:03d}",
                    case_id=case_id,
                    caseworker=person,
                    office=office,
                    month=f"2026-{month:02d}",
                    variant="A",
                    shown_score=shown.shown_score,
                    shown_category=shown.shown_category,
                    shown_recommendation=shown.shown_recommendation,
                    reasoning_rating=4,
                    answer_rating=4,
                    own_category=None,
                    hint_factors=None,
                    decision=choice,
                    justification="Illustrative mock justification, not an actual assessment.",
                    opened_at=opened.isoformat(),
                    decided_at=submitted.isoformat(),
                    simulated=True,
                )
                store.add(db, decision)
                if slot == 0:
                    continue
                stream = TARGETED if slot == 2 else RANDOM_AUDIT
                reason = "Illustrative mock selection, not operational sampling"
                store.add(db, ReviewRequest(decision.decision_id, stream, reason))
                if stream == TARGETED and month % 2:
                    continue
                outcome = choice
                if number % 5 == 0:
                    outcome = "Exclude" if choice == "Include" else "Include"
                store.add(
                    db,
                    Review(
                        review_id=f"mock-review-{number:03d}",
                        decision_id=decision.decision_id,
                        stream=stream,
                        reason=reason,
                        votes=(outcome,) * config.committee.size,
                        committee_decision=outcome,
                        reviewed_at=submitted.isoformat(),
                        simulated=True,
                    ),
                )
    store.add(
        db,
        Alert(
            alert_id="mock-alert-001",
            office=office,
            rule="Authored presentation example",
            evidence="Illustrative follow-up: inspect a reviewed exclusion and discuss it with the operator. Not an established error or an automatic sanction.",
            opened_at="2026-09",
            owner=alerts.owner(office, config.alerts),
            explanation=None,
            closed_by=None,
            closed_at=None,
        ),
    )
    return db
