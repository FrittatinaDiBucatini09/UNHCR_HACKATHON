"""Log records of the prototype: decisions, reviews, sentinels and alerts.

Timestamps are ISO 8601 strings. Real households and sentinels have separate ID
namespaces, so a sentinel can be told from a real case by its ID alone and kept
out of the distribution list. The IDs are internal: a caseworker must never see
them, since the prefix would give a sentinel away.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from src.data_dictionary import FACTORS, HOUSEHOLD_ATTRIBUTES

INCLUDE = "Include"
EXCLUDE = "Exclude"
RECOMMENDATIONS = (INCLUDE, EXCLUDE)

RANDOM_AUDIT = "random_audit"
TARGETED = "targeted"
STREAMS = (RANDOM_AUDIT, TARGETED)

INPUT_MISREAD = "input_misread"
CATEGORY_MISMATCH = "category_mismatch"
REASONING_INCONSISTENCY = "reasoning_inconsistency"
DISCORDANCE_TYPES = (INPUT_MISREAD, CATEGORY_MISMATCH, REASONING_INCONSISTENCY)

CASE_PREFIX = "case-"
SENTINEL_PREFIX = "sentinel-"

# Fields of the household record a caseworker sees. The administrative flags are
# left out because the demo rule ignores them; office and month come with the
# queue the case is in.
RECORD_FIELDS = (*HOUSEHOLD_ATTRIBUTES, *FACTORS)

# What a caseworker enters with a real decision. Simulated decisions leave these
# empty, because the simulation does not model ratings, wording or timing.
CASEWORKER_ENTRIES = (
    "reasoning_rating",
    "answer_rating",
    "justification",
    "opened_at",
    "decided_at",
)


def is_sentinel(case_id: str) -> bool:
    """Whether a case ID belongs to the sentinel namespace."""
    return case_id.startswith(SENTINEL_PREFIX)


def household_record(row: Mapping[str, object]) -> dict[str, object]:
    """The record fields of one household with English labels, as plain values."""
    return {
        field: int(row[field]) if field == "NumIntegrantes" else str(row[field])
        for field in HOUSEHOLD_ATTRIBUTES
    } | {factor: float(row[factor]) for factor in FACTORS}


def check_value(name: str, value: object, allowed: tuple) -> None:
    """Raise ValueError unless value is one of allowed."""
    if value not in allowed:
        raise ValueError(f"{name} = {value!r} is not one of {allowed}")


@dataclass(frozen=True)
class Decision:
    """A caseworker's decision on one case, real or sentinel."""

    decision_id: str
    case_id: str
    caseworker: str  # pseudonym
    office: str
    month: str
    variant: str
    shown_score: float
    shown_category: str
    shown_recommendation: str
    reasoning_rating: int | None
    answer_rating: int | None
    own_category: str | None  # recorded before Cashy's answer under judgment first
    # Factors named by the fragility hint, empty when no hint was shown; None in
    # simulated decisions, since the simulation does not model the screen.
    hint_factors: tuple[str, ...] | None
    decision: str
    justification: str | None
    opened_at: str | None
    decided_at: str | None
    simulated: bool

    def __post_init__(self) -> None:
        if not self.case_id.startswith((CASE_PREFIX, SENTINEL_PREFIX)):
            raise ValueError(f"case_id {self.case_id!r} is in neither ID namespace")
        check_value("shown_recommendation", self.shown_recommendation, RECOMMENDATIONS)
        check_value("decision", self.decision, RECOMMENDATIONS)
        if not self.simulated:
            missing = [
                name for name in CASEWORKER_ENTRIES if getattr(self, name) is None
            ]
            if missing or not self.justification.strip():
                raise ValueError(
                    f"a recorded decision needs every caseworker entry; missing {missing}"
                    " or a blank justification"
                )

    @property
    def overridden(self) -> bool:
        """Whether the decision differs from Cashy's displayed recommendation."""
        return self.decision != self.shown_recommendation


@dataclass(frozen=True)
class Review:
    """A blind committee review of one decision, tagged by its stream."""

    review_id: str
    decision_id: str
    stream: str
    reason: str  # why the decision was selected, with the selection probability
    votes: tuple[str, ...]
    committee_decision: str
    reviewed_at: str | None  # None in simulated reviews
    simulated: bool

    def __post_init__(self) -> None:
        check_value("stream", self.stream, STREAMS)
        if not self.simulated and self.reviewed_at is None:
            raise ValueError("a recorded review needs its time")
        for vote in self.votes:
            check_value("vote", vote, RECOMMENDATIONS)
        check_value("committee_decision", self.committee_decision, RECOMMENDATIONS)


@dataclass(frozen=True)
class ReviewRequest:
    """A decision selected for blind committee review, with its stream and reason."""

    decision_id: str
    stream: str
    reason: str

    def __post_init__(self) -> None:
        check_value("stream", self.stream, STREAMS)
        if not self.reason.strip():
            raise ValueError("a review request needs a written reason")


@dataclass(frozen=True)
class Sentinel:
    """A case whose reference decision is known in advance, injected blind.

    Cashy's displayed answer is concordant with the reference decision or
    deliberately discordant with it; a discordant sentinel records how.
    """

    sentinel_id: str
    record: dict[str, object]  # household fields shown to the caseworker
    shown_factors: dict[str, float]  # factor scores Cashy's answer was computed from
    shown_score: float
    shown_category: str
    shown_recommendation: str
    reasoning: str
    reference_decision: str
    discordance_type: str | None
    altered_factor: str | None
    fragile: bool

    def __post_init__(self) -> None:
        if not is_sentinel(self.sentinel_id):
            raise ValueError(
                f"sentinel_id {self.sentinel_id!r} is outside the sentinel namespace"
            )
        check_value("shown_recommendation", self.shown_recommendation, RECOMMENDATIONS)
        check_value("reference_decision", self.reference_decision, RECOMMENDATIONS)
        if self.concordant != (self.discordance_type is None):
            raise ValueError(
                "a discordance type is required exactly when the shown "
                "recommendation differs from the reference decision"
            )
        if self.discordance_type is not None:
            check_value("discordance_type", self.discordance_type, DISCORDANCE_TYPES)

    @property
    def concordant(self) -> bool:
        """Whether Cashy's displayed recommendation agrees with the reference."""
        return self.shown_recommendation == self.reference_decision

    @property
    def direction(self) -> str | None:
        """Cashy's displayed recommendation on a discordant sentinel, else None.

        "Exclude" means Cashy excludes a case that the reference decision
        includes; "Include" the reverse.
        """
        return None if self.concordant else self.shown_recommendation


@dataclass(frozen=True)
class Alert:
    """An alert raised for one office, closed only by its named owner's explanation."""

    alert_id: str
    office: str
    rule: str
    evidence: str  # the numbers that met the rule
    opened_at: str
    owner: str
    explanation: str | None
    closed_by: str | None
    closed_at: str | None

    def __post_init__(self) -> None:
        if self.closed_at is None:
            return
        if self.closed_by != self.owner:
            raise ValueError(f"only the named owner, {self.owner}, can close an alert")
        if not (self.explanation or "").strip():
            raise ValueError("an alert is closed only with a written explanation")
