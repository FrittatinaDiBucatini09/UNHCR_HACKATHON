"""Tests of the caseworker screen: variants, queues, displays, hints and feedback."""

import dataclasses

import numpy as np
import pytest

from src.data_dictionary import ENGLISH_NAMES, OFFICE_BLANK
from src.dataset import DATA_PATH, load_sample, to_english
from src.sentinella import casework, config
from src.sentinella.schema import (
    CATEGORY_MISMATCH,
    DISCORDANCE_TYPES,
    INPUT_MISREAD,
    REASONING_INCONSISTENCY,
    Decision,
    is_sentinel,
)

DEMO = config.load()
OFFICES = ["fomon", "foten", "fupal", "fusal", "futij", "pcr_cdmx", "sotap"]


@pytest.fixture(scope="module")
def book():
    if not DATA_PATH.exists():
        pytest.skip("S8 data file not present; see data/README.md")
    return casework.casebook(to_english(load_sample()), DEMO)


@pytest.fixture(scope="module")
def staff(book):
    offices = sorted(set(book.queue["office"]) - {OFFICE_BLANK})
    return casework.roster(
        offices, DEMO.simulation.caseworkers_per_office, DEMO.variants
    )


def decision_on(case_id: str, caseworker: str, number: int) -> Decision:
    return Decision(
        decision_id=f"decision-{number:07d}",
        case_id=case_id,
        caseworker=caseworker,
        office="sotap",
        month="2026-10",
        variant="A",
        shown_score=20.0,
        shown_category="Low",
        shown_recommendation="Exclude",
        reasoning_rating=3,
        answer_rating=3,
        own_category=None,
        hint_factors=(),
        decision="Exclude",
        justification="Every factor matches the record.",
        opened_at="2026-10-02T09:00:00+00:00",
        decided_at="2026-10-02T09:03:00+00:00",
        simulated=False,
    )


def test_variants_split_every_office_between_a_and_b():
    staff = casework.roster(OFFICES, 3, DEMO.variants)
    assert staff.equals(casework.roster(OFFICES, 3, DEMO.variants))
    for _, office in staff.groupby("office"):
        assert set(office["variant"]) == set(casework.VARIANTS)
    counts = staff["variant"].value_counts()
    assert abs(counts["A"] - counts["B"]) <= len(OFFICES)


def test_judgment_first_is_asked_only_in_variant_a():
    for setting, fragile, expected in [
        ("fragile", True, True),
        ("fragile", False, False),
        ("all", False, True),
        ("none", True, False),
    ]:
        settings = config.Variants(setting, seed=1)
        assert casework.asks_judgment_first("A", fragile, settings) is expected
        assert not casework.asks_judgment_first("B", fragile, settings)


def test_each_real_case_of_an_office_falls_to_one_caseworker(book, staff):
    colleagues = staff.loc[staff["office"] == "fupal", "caseworker"]
    shares = [
        {
            case
            for case in casework.caseworker_queue(
                book, staff, name, [], DEMO.sentinels
            )["case_id"]
            if not is_sentinel(case)
        }
        for name in colleagues
    ]
    office = set(book.queue.loc[book.queue["office"] == "fupal", "case_id"])
    assert set().union(*shares) == office
    assert sum(len(share) for share in shares) == len(office)


def test_queue_drops_decided_cases_and_never_repeats_a_sentinel(book, staff):
    first = casework.caseworker_queue(book, staff, "caseworker-19", [], DEMO.sentinels)
    sentinel = next(case for case in first["case_id"] if is_sentinel(case))
    real = next(case for case in first["case_id"] if not is_sentinel(case))
    decided = [
        decision_on(sentinel, "caseworker-19", 1),
        decision_on(real, "caseworker-19", 2),
    ]
    again = casework.caseworker_queue(
        book, staff, "caseworker-19", decided, DEMO.sentinels
    )
    assert not {sentinel, real} & set(again["case_id"])


def test_real_case_display_is_stable_and_discordant_only_as_sentinels_are(book):
    discordant = 0
    for case_id in book.queue["case_id"]:
        shown = casework.display(case_id, book, DEMO.simulation)
        assert shown == casework.display(case_id, book, DEMO.simulation)
        reference = book.households.at[case_id, "recommendation"]
        if shown.discordance_type is None:
            assert shown.shown_recommendation == reference
        else:
            discordant += 1
            assert shown.discordance_type in DISCORDANCE_TYPES
            assert shown.shown_recommendation != reference
    assert 0 < discordant < len(book.queue) * DEMO.simulation.cashy_error_rate


def test_hint_names_recommendation_changing_factors_first(book):
    for case_id, household in book.households.head(300).iterrows():
        named = casework.hint_factors(case_id, book)
        decisive = household["decisive_factors"]
        assert set(named) == set(household["hint_factors"])
        assert named[: len(decisive)] == tuple(decisive)
        assert (casework.hint_text(case_id, book) is None) == (not named)


def test_feedback_names_what_was_discordant(book):
    for sentinel in book.pool.values():
        text = casework.feedback(sentinel)
        assert f"reference decision is {sentinel.reference_decision}" in text
        if sentinel.discordance_type in (INPUT_MISREAD, REASONING_INCONSISTENCY):
            assert ENGLISH_NAMES[sentinel.altered_factor].lower() in text
        elif sentinel.discordance_type == CATEGORY_MISMATCH:
            assert f"Cashy showed {sentinel.shown_category}" in text
        else:
            assert "concordant" in text


def test_sentinel_decision_is_never_sent_for_review(book):
    sentinel = next(iter(book.pool))
    audit_everything = dataclasses.replace(
        DEMO,
        random_audit=config.RandomAudit(1.0),
        targeted_review=config.TargetedReview(frozenset({"Exclude"}), "none"),
    )
    requests = casework.review_requests(
        decision_on(sentinel, "caseworker-19", 1),
        book,
        audit_everything,
        np.random.default_rng(0),
    )
    assert requests == []
