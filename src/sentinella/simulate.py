"""Simulated offices, caseworkers and committee, for testing the alert rule.

Everything produced here is simulated. Real cases are households from the S8
queue; caseworkers and the committee follow the behaviour set in the simulation
section of the demo configuration. No result describes how real caseworkers or
committees behave.

Run from the repository root:

    python -m src.sentinella.simulate history     # one year for the app's monitor
    python -m src.sentinella.simulate detection   # detection delay, false alarms
"""

import argparse
import itertools
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.special import expit, logit

from src.data_dictionary import FACTORS, OFFICE_BLANK
from src.dataset import REPO_ROOT, load_sample, to_english
from src.sentinella import alerts, audit, fragility, metrics, sentinels, store
from src.sentinella.config import Config, Fragility, Simulation, load
from src.sentinella.schema import (
    CASE_PREFIX,
    EXCLUDE,
    INCLUDE,
    Alert,
    Decision,
    Review,
    Sentinel,
    is_sentinel,
)

SCENARIOS = ("control", "drift")
BASELINE_SCREEN = "baseline screen"
CHANGED_SCREEN = "changed screen"
ANSWER = ["shown_score", "shown_category", "shown_recommendation"]


@dataclass(frozen=True)
class Setup:
    """What every run draws on: the sentinel pool and the real households."""

    pool: dict[str, Sentinel]
    pool_table: pd.DataFrame  # sentinels.describe_pool
    office_rows: dict[str, np.ndarray]  # queue rows of each named office
    truth: dict[int, tuple[float, str, str]]  # score, category and reference
    targetable: dict[int, bool]  # fragile in the targeted review rule's sense
    errors: dict[int, list[tuple[float, str, str]]]  # discordant answers


@dataclass(frozen=True)
class Caseworker:
    """A simulated caseworker: pseudonym, office and personal log-odds offset."""

    name: str
    office: str
    offset: float


@dataclass(frozen=True)
class Run:
    """What one simulated run produced."""

    decisions: list[Decision]
    reviews: list[Review]
    alerts: list[Alert]
    checks: pd.DataFrame  # the alert rule, office by office and month by month


def setup(sample: pd.DataFrame, config: Config) -> Setup:
    """Sentinel pool, real households and the answers Cashy can show on them.

    Args:
        sample: The S8 sample with English labels (dataset.to_english).
        config: Demo configuration.
    """
    pool, queue = sentinels.build_pool(sample, config)
    households = fragility.assess(queue[FACTORS], config.demo_rule, config.fragility)
    variants = sentinels.discordant_variants(queue, households, config)
    offices = queue.loc[queue["office"] != OFFICE_BLANK, "office"]
    truth = households[["final_score", "category", "recommendation"]]
    rule = config.targeted_review.fragility
    targetable = (
        pd.Series(True, index=queue.index)
        if rule == "none"
        else fragility.assess(queue[FACTORS], config.demo_rule, Fragility(rule))[
            "fragile"
        ]
    )
    return Setup(
        pool={sentinel.sentinel_id: sentinel for sentinel in pool},
        pool_table=sentinels.describe_pool(pool, config),
        office_rows={
            office: rows.index.to_numpy() for office, rows in offices.groupby(offices)
        },
        truth=dict(zip(truth.index, truth.itertuples(index=False, name=None))),
        targetable=targetable.to_dict(),
        errors={
            row: list(group[ANSWER].itertuples(index=False, name=None))
            for row, group in variants.groupby("row")
        },
    )


def run(setup: Setup, config: Config, scenario: str, seed: int) -> Run:
    """One simulated run of a scenario.

    Each month every caseworker decides cases_per_caseworker real cases drawn
    from the office's households, with sentinels injected blind. On a real case
    that admits a discordant answer, Cashy shows one with probability
    cashy_error_rate. A
    caseworker overrides a discordant answer with a personal probability around
    correct_override, and a concordant one with probability under_reliance. In
    the drift scenario the drift office moves to a changed screen at
    drift_month, and its caseworkers' chance of a correct override falls to
    around drift_correct_override. Each month ends with committee reviews of the
    random audit and targeted selections, then the alert rule in every office.

    Raises:
        ValueError: If the scenario is unknown or the drift office has no
            households.
    """
    settings = config.simulation
    if scenario not in SCENARIOS:
        raise ValueError(f"scenario {scenario!r} is not one of {SCENARIOS}")
    if settings.drift_office not in setup.office_rows:
        raise ValueError(f"no households in the drift office {settings.drift_office}")
    rng = np.random.default_rng(seed)
    months = month_labels(settings)
    staff = hire(sorted(setup.office_rows), settings, rng)
    pool = list(setup.pool.values())
    uses, seen = Counter(), {caseworker.name: set() for caseworker in staff}
    case_numbers, decision_numbers, real_rows = (
        itertools.count(1),
        itertools.count(1),
        {},
    )
    decisions, reviews, raised, checks = [], [], [], []
    for number, month in enumerate(months, start=1):
        month_decisions = []
        for caseworker in staff:
            drifted = (
                scenario == "drift"
                and caseworker.office == settings.drift_office
                and number >= settings.drift_month
            )
            queue = draw_queue(
                setup, caseworker, month, settings, case_numbers, real_rows, rng
            )
            injected = sentinels.inject(
                queue, pool, uses, seen[caseworker.name], config.sentinels, rng
            )
            for case_id in injected["case_id"]:
                shown, reference = answer_and_reference(
                    setup, case_id, real_rows, settings, rng
                )
                chance = override_chance(
                    shown[2] == reference, caseworker, drifted, settings
                )
                month_decisions.append(
                    simulated_decision(
                        f"decision-{next(decision_numbers):07d}",
                        case_id,
                        caseworker,
                        month,
                        drifted,
                        shown,
                        overridden=rng.random() < chance,
                    )
                )
        decisions += month_decisions
        reviews += committee_reviews(
            setup, real_rows, month_decisions, config, len(reviews) + 1, rng
        )
        window = months[max(0, number - config.alerts.window_months) : number]
        outcomes = metrics.sentinel_outcomes(decisions, setup.pool_table)
        month_checks = alerts.check(outcomes, window, config.alerts)
        raised += alerts.raise_alerts(month_checks, window, raised, config.alerts)
        checks.append(month_checks.assign(month=month))
    return Run(decisions, reviews, raised, pd.concat(checks, ignore_index=True))


def month_labels(settings: Simulation) -> list[str]:
    """The simulated months, as YYYY-MM."""
    months = pd.period_range(settings.start_month, periods=settings.months, freq="M")
    return months.astype(str).tolist()


def hire(
    offices: list[str], settings: Simulation, rng: np.random.Generator
) -> list[Caseworker]:
    """The same number of pseudonymous caseworkers in every office."""
    names = itertools.count(1)
    return [
        Caseworker(
            f"caseworker-{next(names):02d}",
            office,
            float(rng.normal(0, settings.caseworker_spread)),
        )
        for office in offices
        for _ in range(settings.caseworkers_per_office)
    ]


def draw_queue(
    setup: Setup,
    caseworker: Caseworker,
    month: str,
    settings: Simulation,
    numbers: Iterator[int],
    real_rows: dict[str, int],
    rng: np.random.Generator,
) -> pd.DataFrame:
    """A month of real cases for one caseworker, drawn from the office's households.

    Households are drawn with replacement, so one household can be several
    cases. real_rows records the household behind each new case ID.
    """
    rows = rng.choice(
        setup.office_rows[caseworker.office], settings.cases_per_caseworker
    )
    case_ids = [f"{CASE_PREFIX}{next(numbers):07d}" for _ in rows]
    real_rows.update(zip(case_ids, rows.tolist()))
    return pd.DataFrame(
        {"case_id": case_ids, "office": caseworker.office, "month": month}
    )


def answer_and_reference(
    setup: Setup,
    case_id: str,
    real_rows: dict[str, int],
    settings: Simulation,
    rng: np.random.Generator,
) -> tuple[tuple[float, str, str], str]:
    """Cashy's displayed answer on a case, and the case's reference decision."""
    if is_sentinel(case_id):
        sentinel = setup.pool[case_id]
        shown = (
            sentinel.shown_score,
            sentinel.shown_category,
            sentinel.shown_recommendation,
        )
        return shown, sentinel.reference_decision
    row = real_rows[case_id]
    options = setup.errors.get(row)
    if options and rng.random() < settings.cashy_error_rate:
        return options[rng.integers(len(options))], setup.truth[row][2]
    return setup.truth[row], setup.truth[row][2]


def override_chance(
    concordant: bool, caseworker: Caseworker, drifted: bool, settings: Simulation
) -> float:
    """Chance that the caseworker overrides Cashy's displayed recommendation."""
    if concordant:
        return settings.under_reliance
    base = settings.drift_correct_override if drifted else settings.correct_override
    return float(expit(logit(base) + caseworker.offset))


def simulated_decision(
    decision_id: str,
    case_id: str,
    caseworker: Caseworker,
    month: str,
    drifted: bool,
    shown: tuple[float, str, str],
    overridden: bool,
) -> Decision:
    """A decision record; ratings, wording and timing are not simulated."""
    return Decision(
        decision_id=decision_id,
        case_id=case_id,
        caseworker=caseworker.name,
        office=caseworker.office,
        month=month,
        variant=CHANGED_SCREEN if drifted else BASELINE_SCREEN,
        shown_score=float(shown[0]),
        shown_category=shown[1],
        shown_recommendation=shown[2],
        reasoning_rating=None,
        answer_rating=None,
        own_category=None,
        hint_factors=None,
        decision=opposite(shown[2]) if overridden else shown[2],
        justification=None,
        opened_at=None,
        decided_at=None,
        simulated=True,
    )


def committee_reviews(
    setup: Setup,
    real_rows: dict[str, int],
    decisions: list[Decision],
    config: Config,
    first_number: int,
    rng: np.random.Generator,
) -> list[Review]:
    """Simulated committee reviews of a month's random-audit and targeted picks.

    Each member votes for the reference decision, except with probability
    committee_noise, and the votes are combined by the committee's rule.
    """
    targetable = {
        decision.case_id
        for decision in decisions
        if not is_sentinel(decision.case_id)
        and setup.targetable[real_rows[decision.case_id]]
    }
    requests = audit.random_audit(decisions, config.random_audit, rng) + audit.targeted(
        decisions, targetable, config.targeted_review
    )
    by_id = {decision.decision_id: decision for decision in decisions}
    noise = config.simulation.committee_noise
    reviews = []
    for number, request in enumerate(requests, start=first_number):
        row = real_rows[by_id[request.decision_id].case_id]
        reference = setup.truth[row][2]
        votes = tuple(
            opposite(reference) if rng.random() < noise else reference
            for _ in range(config.committee.size)
        )
        reviews.append(
            Review(
                review_id=f"review-{number:06d}",
                decision_id=request.decision_id,
                stream=request.stream,
                reason=request.reason,
                votes=votes,
                committee_decision=audit.committee_decision(votes, config.committee),
                reviewed_at=None,
                simulated=True,
            )
        )
    return reviews


def opposite(recommendation: str) -> str:
    """The other recommendation."""
    return EXCLUDE if recommendation == INCLUDE else INCLUDE


def detection(setup: Setup, config: Config, scenario: str) -> pd.DataFrame:
    """Whether and when the rule caught the drift, and its other firings, per run.

    Runs use the seeds seed, seed + 1 and so on, for the configured number of
    runs. Firings are read from the rule's monthly checks, so an alert left
    open in an office does not hide later firings there.

    Returns:
        One row per run: whether the rule fired in the drift office from the
        drift month on, the months from the drift month to that first firing,
        and the firings anywhere else, which are false alarms.
    """
    settings = config.simulation
    number_of = {month: n for n, month in enumerate(month_labels(settings), start=1)}
    rows = []
    for seed in range(settings.seed, settings.seed + settings.runs):
        fired = run(setup, config, scenario, seed).checks.query("fires")
        number = fired["month"].map(number_of)
        caught = fired[
            (scenario == "drift")
            & (fired["office"] == settings.drift_office)
            & (number >= settings.drift_month)
        ]
        rows.append(
            {
                "seed": seed,
                "scenario": scenario,
                "detected": not caught.empty,
                "delay_months": number[caught.index].min() - settings.drift_month,
                "false_firings": len(fired) - len(caught),
            }
        )
    return pd.DataFrame(rows)


def report(drift: pd.DataFrame, control: pd.DataFrame, settings: Simulation) -> str:
    """Detection delay and false alarms of the alert rule, in words.

    Args:
        drift: Output of detection for the drift scenario.
        control: Output of detection for the control scenario.
        settings: Simulation settings of the demo configuration.
    """
    runs, caught = len(drift), int(drift["detected"].sum())
    low, high = metrics.wilson(caught, runs)
    delay = drift.loc[drift["detected"], "delay_months"]
    quartiles = delay.quantile([0.25, 0.5, 0.75]).tolist()
    within = ", ".join(
        f"{(drift['delay_months'] <= months).mean():.1%} within {months}"
        for months in range(settings.months - settings.drift_month + 1)
    )
    alarmed = int((control["false_firings"] > 0).sum())
    alarm_low, alarm_high = metrics.wilson(alarmed, len(control))
    return "\n".join(
        [
            "Simulated under demo values; not a property of any real operation.",
            (
                f"Drift: the rule fired in {settings.drift_office} from month "
                f"{settings.drift_month} on in {caught} of {runs} runs "
                f"({caught / runs:.1%}, 95% CI {low:.1%} to {high:.1%})."
            ),
            (
                "Months from the screen change to the first firing in those runs: "
                f"median {quartiles[1]:g}, quartiles {quartiles[0]:g} to "
                f"{quartiles[2]:g}, at most {delay.max():g}."
            ),
            f"Share of all drift runs caught: {within} months.",
            (
                f"Control: {alarmed} of {len(control)} runs raised at least one false "
                f"alarm ({alarmed / len(control):.1%}, 95% CI {alarm_low:.1%} to "
                f"{alarm_high:.1%}); {int(control['false_firings'].sum())} firings in all."
            ),
        ]
    )


def save(result: Run, setup: Setup, path: Path) -> None:
    """Write one run and its sentinel pool to a new database file."""
    path.unlink(missing_ok=True)
    connection = store.connect(path)
    store.add(
        connection,
        *setup.pool.values(),
        *result.decisions,
        *result.reviews,
        *result.alerts,
    )
    connection.close()


def main() -> None:
    """Write a simulated year for the app, or report detection over many runs."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["history", "detection"])
    command = parser.parse_args().command
    demo = load()
    prepared = setup(to_english(load_sample()), demo)
    if command == "history":
        result = run(prepared, demo, "drift", demo.simulation.seed)
        save(result, prepared, store.SIMULATION_DATABASE)
        print(
            f"{len(result.decisions)} simulated decisions, {len(result.reviews)} "
            f"reviews and {len(result.alerts)} alerts written to "
            f"{store.SIMULATION_DATABASE.relative_to(REPO_ROOT)}"
        )
        return
    drift, control = (
        detection(prepared, demo, scenario) for scenario in SCENARIOS[::-1]
    )
    print(report(drift, control, demo.simulation))


if __name__ == "__main__":
    main()
