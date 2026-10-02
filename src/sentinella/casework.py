"""The caseworker screen: queues, what each case displays and the variant steps.

The prototype defines two workflow variants:

- A, summary first: a summary of the record, with the complete record one click
  away. Cashy's reasoning and answer appear when the caseworker asks for them,
  after the caseworker has recorded a category of their own on the cases that
  judgment first covers.
- B, Cashy first: the complete record with Cashy's reasoning and answer from the
  start.

In both, a fragile case carries the fragility hint, which names the factors to
check against the record. Caseworkers are assigned to a variant at random, half
of each office to each, so that the caseworker is the unit the variants compare.

On a real case the prototype's stand-in for Cashy shows the formula's answer,
except on a share of the cases that admit a discordant answer (cashy_error_rate),
where it shows one of the same kinds as the sentinels'. A discordant answer is
therefore no sign of a sentinel.
"""

import itertools
from collections import Counter
from dataclasses import dataclass

import numpy as np
import pandas as pd

from src import scorecard
from src.data_dictionary import ENGLISH_NAMES, FACTORS, VALUE_LABELS
from src.sentinella import audit, fragility, sentinels
from src.sentinella.config import (
    CATEGORIES,
    Config,
    Fragility,
    SentinelSettings,
    Simulation,
    Variants,
)
from src.sentinella.reasoning import household_summary
from src.sentinella.schema import (
    CASE_PREFIX,
    CATEGORY_MISMATCH,
    INPUT_MISREAD,
    Decision,
    ReviewRequest,
    Sentinel,
    household_record,
    is_sentinel,
)
from src.sentinella.sentinels import Display

VARIANTS = ("A", "B")


@dataclass(frozen=True)
class Casebook:
    """Every case the app can put in a queue, real or sentinel."""

    pool: dict[str, Sentinel]
    pool_table: pd.DataFrame  # sentinels.describe_pool
    queue: pd.DataFrame  # real cases: case_id, office and interview month
    records: dict[str, dict[str, object]]  # record fields of every case
    # By case ID: the formula's answer, fragility, the factors the hint names,
    # those that would change the recommendation, and whether the targeted
    # review rule can select the case.
    households: pd.DataFrame
    variants: dict[str, pd.DataFrame]  # discordant answers each real case admits


def casebook(sample: pd.DataFrame, config: Config) -> Casebook:
    """Sentinel pool and real cases drawn from the sample, as the simulation draws them.

    Args:
        sample: The S8 sample with English labels (dataset.to_english).
        config: Demo configuration.
    """
    pool, queue = sentinels.build_pool(sample, config)
    real = queue.set_index("case_id")
    factors = pd.concat(
        [
            real[FACTORS],
            pd.DataFrame(
                [{factor: s.record[factor] for factor in FACTORS} for s in pool],
                index=[s.sentinel_id for s in pool],
            ),
        ]
    )
    households = fragility.assess(factors, config.demo_rule, config.fragility)
    households["decisive_factors"] = fragility.assess(
        factors, config.demo_rule, Fragility("recommendation")
    )["hint_factors"]
    rule = config.targeted_review.fragility
    households["targetable"] = (
        True
        if rule == "none"
        else fragility.assess(factors, config.demo_rule, Fragility(rule))["fragile"]
    )
    rows = households.loc[queue["case_id"]].set_axis(queue.index)
    options = sentinels.discordant_variants(queue, rows, config)
    return Casebook(
        pool={s.sentinel_id: s for s in pool},
        pool_table=sentinels.describe_pool(pool, config),
        queue=queue[["case_id", "office", "month"]].reset_index(drop=True),
        records={case_id: household_record(row) for case_id, row in real.iterrows()}
        | {s.sentinel_id: s.record for s in pool},
        households=households,
        variants={
            queue.at[row, "case_id"]: group for row, group in options.groupby("row")
        },
    )


def roster(offices: list[str], per_office: int, settings: Variants) -> pd.DataFrame:
    """Pseudonymous caseworkers of each office and the variant each is assigned.

    Within each office the variants alternate over a random order of the
    caseworkers, from a random first variant, so each office is split as evenly
    as its size allows.

    Returns:
        One row per caseworker: caseworker, office and variant.
    """
    rng = np.random.default_rng(settings.seed)
    numbers = itertools.count(1)
    rows = []
    for office in sorted(offices):
        names = [f"caseworker-{next(numbers):02d}" for _ in range(per_office)]
        first = int(rng.integers(len(VARIANTS)))
        for position, name in enumerate(rng.permutation(names)):
            variant = VARIANTS[(first + position) % len(VARIANTS)]
            rows.append((str(name), office, variant))
    table = pd.DataFrame(rows, columns=["caseworker", "office", "variant"])
    return table.sort_values("caseworker", ignore_index=True)


def caseworker_queue(
    book: Casebook,
    staff: pd.DataFrame,
    caseworker: str,
    decisions: list[Decision],
    settings: SentinelSettings,
) -> pd.DataFrame:
    """The caseworker's open cases, in interview-month order, with sentinels injected.

    The real cases of an office are shared out in turn among its caseworkers,
    so each is decided once. Sentinels are injected blind as in the
    simulation; uses and the sentinels the caseworker has already decided come
    from the decisions so far.

    Args:
        book: Output of casebook.
        staff: Output of roster.
        caseworker: The caseworker's pseudonym.
        decisions: Every decision recorded so far.
        settings: Sentinel settings of the demo configuration.

    Returns:
        case_id, office and month of each case still to decide.
    """
    office = staff.loc[staff["caseworker"] == caseworker, "office"].item()
    colleagues = staff.loc[staff["office"] == office, "caseworker"].tolist()
    cases = book.queue[book.queue["office"] == office].sort_values(["month", "case_id"])
    mine = cases.iloc[colleagues.index(caseworker) :: len(colleagues)]
    uses = Counter(d.case_id for d in decisions if is_sentinel(d.case_id))
    decided = {d.case_id for d in decisions if d.caseworker == caseworker}
    rng = np.random.default_rng(
        [settings.seed, int(caseworker.rsplit("-", maxsplit=1)[1])]
    )
    queue = sentinels.inject(
        mine,
        list(book.pool.values()),
        uses,
        {case for case in decided if is_sentinel(case)},
        settings,
        rng,
    )
    return queue[~queue["case_id"].isin(decided)].reset_index(drop=True)


def display(case_id: str, book: Casebook, settings: Simulation) -> Display:
    """What Cashy shows on a case: the sentinel's display, or the stand-in's answer.

    A real case's answer depends only on the case and the simulation seed, so
    it stays the same however often the case is opened.
    """
    if is_sentinel(case_id):
        s = book.pool[case_id]
        return Display(
            s.shown_factors,
            s.shown_score,
            s.shown_category,
            s.shown_recommendation,
            s.reasoning,
            s.discordance_type,
            s.altered_factor,
        )
    rng = np.random.default_rng([settings.seed, int(case_id.removeprefix(CASE_PREFIX))])
    options = book.variants.get(case_id)
    variant = None
    if options is not None and rng.random() < settings.cashy_error_rate:
        variant = options.iloc[rng.integers(len(options))]
    return sentinels.displayed_answer(
        book.records[case_id], book.households.loc[case_id], variant
    )


def hint_factors(case_id: str, book: Casebook) -> tuple[str, ...]:
    """Factors the fragility hint names, those that would change the recommendation first.

    Empty when the case is not fragile.
    """
    household = book.households.loc[case_id]
    decisive = household["decisive_factors"]
    return (*decisive, *(f for f in household["hint_factors"] if f not in decisive))


def hint_text(case_id: str, book: Casebook) -> str | None:
    """The fragility hint as shown on screen, or None when the case is not fragile."""
    named = hint_factors(case_id, book)
    if not named:
        return None
    decisive = book.households.at[case_id, "decisive_factors"]
    text = (
        "Check against the record: "
        + ", ".join(ENGLISH_NAMES[factor] for factor in named)
        + ". Moving any one of them by one level would change the category."
    )
    if decisive:
        text += (
            " For "
            + ", ".join(ENGLISH_NAMES[factor] for factor in decisive)
            + ", it would also change the recommendation under the demo rule."
        )
    return text


def review_requests(
    decision: Decision, book: Casebook, config: Config, rng: np.random.Generator
) -> list[ReviewRequest]:
    """The random audit and the targeted review rule applied to one new decision."""
    targetable = (
        {decision.case_id}
        if not is_sentinel(decision.case_id)
        and book.households.at[decision.case_id, "targetable"]
        else set()
    )
    return audit.random_audit([decision], config.random_audit, rng) + audit.targeted(
        [decision], targetable, config.targeted_review
    )


def asks_judgment_first(variant: str, fragile: bool, settings: Variants) -> bool:
    """Whether the screen asks for the caseworker's own category before Cashy's answer."""
    if variant != "A":
        return False
    return settings.judgment_first == "all" or (
        settings.judgment_first == "fragile" and fragile
    )


def summary(record: dict[str, object]) -> tuple[str, pd.DataFrame]:
    """Variant A's summary: the household in sentences and each factor's level."""
    levels = pd.DataFrame(
        [
            (
                ENGLISH_NAMES[factor],
                (
                    f"level {scorecard.FACTOR_LEVELS[factor].index(record[factor]) + 1}"
                    f" of {len(scorecard.FACTOR_LEVELS[factor])}"
                ),
                record[factor],
            )
            for factor in FACTORS
        ],
        columns=["Factor", "Level", "Score"],
    )
    return household_summary(record), levels


def complete_record(record: dict[str, object]) -> pd.DataFrame:
    """Every field of the record with its English name, in the sample's order."""
    return pd.DataFrame(
        [(ENGLISH_NAMES[field], str(value)) for field, value in record.items()],
        columns=["Field", "Value"],
    )


def category_bands() -> pd.DataFrame:
    """Final-score range of each category under the recovered formula."""
    points = [
        float(scorecard.final_from_index(cut)) for cut in scorecard.CATEGORY_CUTPOINTS
    ]
    return pd.DataFrame(
        {
            "Category": CATEGORIES,
            "From": [0.0, *points],
            "To": [*points, scorecard.FINAL_MAX_SCORE],
        }
    )


def band(score: float) -> str:
    """The category whose band holds a final score."""
    code = scorecard.score_category(pd.Series([score])).iloc[0]
    return VALUE_LABELS["Vulnerability_Category"][code]


def feedback(sentinel: Sentinel) -> str:
    """Private feedback after a decision on a sentinel.

    It gives the reference decision and, when Cashy's answer was discordant,
    what on screen was discordant with the record.
    """
    opening = (
        "This case was a sentinel. Its reference decision is "
        f"{sentinel.reference_decision}: the demo rule applied to the category that "
        "the Scorecard formula gives its record."
    )
    if sentinel.concordant:
        return f"{opening} Cashy's answer was concordant with it."
    if sentinel.discordance_type == CATEGORY_MISMATCH:
        return (
            f"{opening} Cashy's answer was discordant with it: the score "
            f"{sentinel.shown_score:.1f} lies in the {band(sentinel.shown_score)} "
            f"band, but Cashy showed {sentinel.shown_category}."
        )
    factor = sentinel.altered_factor
    name = ENGLISH_NAMES[factor].lower()
    recorded, shown = sentinel.record[factor], sentinel.shown_factors[factor]
    if sentinel.discordance_type == INPUT_MISREAD:
        return (
            f"{opening} Cashy's answer was discordant with it: Cashy read {name} as "
            f"{shown:.2f} where the record has {recorded:.2f}, and its reasoning "
            "states the misread score."
        )
    return (
        f"{opening} Cashy's answer was discordant with it: the reasoning matches "
        f"the record, but the answer was computed with {name} at {shown:.2f} "
        f"instead of {recorded:.2f}, so the reasoning and the answer disagree."
    )
