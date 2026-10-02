"""Demo configuration of the prototype, read from config/demo.toml."""

import re
from dataclasses import dataclass
from pathlib import Path

import tomllib

from src.data_dictionary import VALUE_LABELS
from src.dataset import REPO_ROOT
from src.scorecard import FINAL_MAX_SCORE
from src.sentinella.schema import EXCLUDE, INCLUDE, RECOMMENDATIONS

CONFIG_PATH = REPO_ROOT / "config" / "demo.toml"
CATEGORIES = tuple(VALUE_LABELS["Vulnerability_Category"].values())
FRAGILITY_CHANGES = ("category", "recommendation")
TARGETED_FRAGILITY = (*FRAGILITY_CHANGES, "none")
JUDGMENT_FIRST = ("fragile", "all", "none")
SHARES = ("discordant_share", "exclusion_share", "fragile_share", "far_share")
SECTIONS = {
    "demo_rule": {"include"},
    "fragility": {"changes"},
    "sentinels": {
        "pool_size",
        *SHARES,
        "far_distance",
        "injection_rate",
        "max_uses",
        "seed",
    },
    "random_audit": {"fraction"},
    "targeted_review": {"recommendations", "fragility"},
    "committee": {"size", "rule"},
    "alerts": {"window_months", "floor", "minimum_discordant", "owner"},
    "variants": {"judgment_first", "seed"},
    "monitor": {"minimum_caseworkers"},
    "metrics": {"bootstrap_replicates", "seed"},
    "simulation": {
        "start_month",
        "months",
        "caseworkers_per_office",
        "cases_per_caseworker",
        "cashy_error_rate",
        "correct_override",
        "under_reliance",
        "caseworker_spread",
        "committee_noise",
        "drift_office",
        "drift_month",
        "drift_correct_override",
        "runs",
        "seed",
    },
}
COMMITTEE_RULES = ("majority",)


@dataclass(frozen=True)
class DemoRule:
    """Stand-in for Cashy's recommendation; not the operation's eligibility rule."""

    include: frozenset[str]

    def recommend(self, category: str) -> str:
        """Demo recommendation, Include or Exclude, for a vulnerability category."""
        return INCLUDE if category in self.include else EXCLUDE


@dataclass(frozen=True)
class Fragility:
    """Outcome that a one-level move must change for a case to be fragile."""

    changes: str


@dataclass(frozen=True)
class SentinelSettings:
    """Size and balance of the sentinel pool, and how sentinels are injected."""

    pool_size: int
    discordant_share: float
    exclusion_share: float
    fragile_share: float
    far_share: float
    far_distance: float
    injection_rate: float
    max_uses: int
    seed: int


@dataclass(frozen=True)
class RandomAudit:
    """Share of decisions on real cases that the committee re-reviews."""

    fraction: float


@dataclass(frozen=True)
class TargetedReview:
    """Rule that sends a decision to a blind second review.

    fragility is the outcome a one-level move must change for the rule to select
    a case, or "none" to select whatever the case.
    """

    recommendations: frozenset[str]
    fragility: str


@dataclass(frozen=True)
class Committee:
    """Size of the review committee and how its votes become one decision."""

    size: int
    rule: str


@dataclass(frozen=True)
class AlertRule:
    """When an office's correct override on sentinels raises an alert, and who owns it."""

    window_months: int
    floor: float
    minimum_discordant: int
    owner: str


@dataclass(frozen=True)
class Variants:
    """Cases on which variant A asks for judgment first, and the variant assignment."""

    judgment_first: str
    seed: int


@dataclass(frozen=True)
class Monitor:
    """Fewest caseworkers an aggregate may rest on before it is hidden."""

    minimum_caseworkers: int


@dataclass(frozen=True)
class MetricSettings:
    """Resampling of caseworkers for clustered intervals."""

    bootstrap_replicates: int
    seed: int


@dataclass(frozen=True)
class Simulation:
    """Simulated offices, caseworkers and committee, and the drift scenario."""

    start_month: str
    months: int
    caseworkers_per_office: int
    cases_per_caseworker: int
    cashy_error_rate: float
    correct_override: float
    under_reliance: float
    caseworker_spread: float
    committee_noise: float
    drift_office: str
    drift_month: int
    drift_correct_override: float
    runs: int
    seed: int


@dataclass(frozen=True)
class Config:
    """Demo configuration, one attribute per section of the file."""

    demo_rule: DemoRule
    fragility: Fragility
    sentinels: SentinelSettings
    random_audit: RandomAudit
    targeted_review: TargetedReview
    committee: Committee
    alerts: AlertRule
    variants: Variants
    monitor: Monitor
    metrics: MetricSettings
    simulation: Simulation


def load(path: Path = CONFIG_PATH) -> Config:
    """Read and validate the demo configuration.

    Raises:
        ValueError: If a section or key is missing or unknown, or a value is not
            allowed.
        TypeError: If a value has the wrong type.
    """
    with path.open("rb") as file:
        raw = tomllib.load(file)
    check_keys("config", raw, set(SECTIONS))
    for section, keys in SECTIONS.items():
        check_keys(section, raw[section], keys)
    changes = check_choice(
        "fragility.changes", raw["fragility"]["changes"], FRAGILITY_CHANGES
    )
    targeted = raw["targeted_review"]
    variants = raw["variants"]
    return Config(
        demo_rule=DemoRule(
            check_subset("demo_rule.include", raw["demo_rule"]["include"], CATEGORIES)
        ),
        fragility=Fragility(changes),
        sentinels=sentinel_settings(raw["sentinels"]),
        random_audit=RandomAudit(
            check_number("random_audit.fraction", raw["random_audit"]["fraction"], 0, 1)
        ),
        targeted_review=TargetedReview(
            check_subset(
                "targeted_review.recommendations",
                targeted["recommendations"],
                RECOMMENDATIONS,
            ),
            check_choice(
                "targeted_review.fragility", targeted["fragility"], TARGETED_FRAGILITY
            ),
        ),
        committee=committee(raw["committee"]),
        alerts=alert_rule(raw["alerts"]),
        variants=Variants(
            check_choice(
                "variants.judgment_first", variants["judgment_first"], JUDGMENT_FIRST
            ),
            check_integer("variants.seed", variants["seed"], 0),
        ),
        monitor=Monitor(
            check_integer(
                "monitor.minimum_caseworkers", raw["monitor"]["minimum_caseworkers"], 1
            )
        ),
        metrics=MetricSettings(
            check_integer(
                "metrics.bootstrap_replicates",
                raw["metrics"]["bootstrap_replicates"],
                1,
            ),
            check_integer("metrics.seed", raw["metrics"]["seed"], 0),
        ),
        simulation=simulation(raw["simulation"]),
    )


def sentinel_settings(table: dict) -> SentinelSettings:
    """Validated settings of the sentinels section."""
    rate = check_number("sentinels.injection_rate", table["injection_rate"], 0, 1)
    if rate == 1:
        raise ValueError("sentinels.injection_rate must be below 1")
    return SentinelSettings(
        pool_size=check_integer("sentinels.pool_size", table["pool_size"], 1),
        **{
            name: check_number(f"sentinels.{name}", table[name], 0, 1)
            for name in SHARES
        },
        far_distance=check_number(
            "sentinels.far_distance", table["far_distance"], 0, FINAL_MAX_SCORE
        ),
        injection_rate=rate,
        max_uses=check_integer("sentinels.max_uses", table["max_uses"], 1),
        seed=check_integer("sentinels.seed", table["seed"], 0),
    )


def committee(table: dict) -> Committee:
    """Validated settings of the committee section."""
    if table["rule"] not in COMMITTEE_RULES:
        raise ValueError(
            f"committee.rule = {table['rule']!r} is not one of {COMMITTEE_RULES}"
        )
    size = check_integer("committee.size", table["size"], 1)
    if size % 2 == 0:
        raise ValueError("committee.size must be odd, so that a majority always exists")
    return Committee(size, table["rule"])


def alert_rule(table: dict) -> AlertRule:
    """Validated settings of the alerts section."""
    return AlertRule(
        window_months=check_integer("alerts.window_months", table["window_months"], 1),
        floor=check_number("alerts.floor", table["floor"], 0, 1),
        minimum_discordant=check_integer(
            "alerts.minimum_discordant", table["minimum_discordant"], 1
        ),
        owner=check_text("alerts.owner", table["owner"]),
    )


def simulation(table: dict) -> Simulation:
    """Validated settings of the simulation section."""
    start = check_text("simulation.start_month", table["start_month"])
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", start):
        raise ValueError(f"simulation.start_month = {start!r} is not a YYYY-MM month")
    months = check_integer("simulation.months", table["months"], 1)
    drift_month = check_integer("simulation.drift_month", table["drift_month"], 1)
    if drift_month > months:
        raise ValueError("simulation.drift_month falls after the last simulated month")
    return Simulation(
        start_month=start,
        months=months,
        caseworkers_per_office=check_integer(
            "simulation.caseworkers_per_office", table["caseworkers_per_office"], 1
        ),
        cases_per_caseworker=check_integer(
            "simulation.cases_per_caseworker", table["cases_per_caseworker"], 1
        ),
        **{
            name: check_number(f"simulation.{name}", table[name], 0, 1)
            for name in ("cashy_error_rate", "under_reliance", "committee_noise")
        },
        **{
            name: check_inner_probability(f"simulation.{name}", table[name])
            for name in ("correct_override", "drift_correct_override")
        },
        caseworker_spread=check_number(
            "simulation.caseworker_spread", table["caseworker_spread"], 0, float("inf")
        ),
        drift_office=check_text("simulation.drift_office", table["drift_office"]),
        drift_month=drift_month,
        runs=check_integer("simulation.runs", table["runs"], 1),
        seed=check_integer("simulation.seed", table["seed"], 0),
    )


def check_keys(name: str, table: dict, expected: set[str]) -> None:
    """Raise ValueError unless table has exactly the expected keys."""
    missing, unknown = expected - table.keys(), table.keys() - expected
    if missing or unknown:
        raise ValueError(
            f"{name}: missing keys {sorted(missing)}, unknown keys {sorted(unknown)}"
        )


def check_number(name: str, value: object, low: float, high: float) -> float:
    """The value as a float, if it is a number from low to high."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(f"{name} = {value!r} is not a number")
    if not low <= value <= high:
        raise ValueError(f"{name} = {value!r} is not between {low} and {high}")
    return float(value)


def check_integer(name: str, value: object, low: int) -> int:
    """The value, if it is an integer of at least low."""
    if isinstance(value, bool) or not isinstance(value, int) or value < low:
        raise ValueError(f"{name} = {value!r} is not an integer of at least {low}")
    return value


def check_subset(name: str, values: list, allowed: tuple) -> frozenset[str]:
    """The values as a set, if each one is allowed."""
    unknown = sorted(set(values) - set(allowed))
    if unknown:
        raise ValueError(f"{name} has values {unknown} outside {allowed}")
    return frozenset(values)


def check_inner_probability(name: str, value: object) -> float:
    """The value, if it is a probability strictly between 0 and 1.

    The simulation works on the log-odds of these probabilities, which 0 and 1
    do not have.
    """
    probability = check_number(name, value, 0, 1)
    if probability in (0, 1):
        raise ValueError(f"{name} must lie strictly between 0 and 1")
    return probability


def check_text(name: str, value: object) -> str:
    """The value, if it is a non-blank string."""
    if not isinstance(value, str):
        raise TypeError(f"{name} = {value!r} is not text")
    if not value.strip():
        raise ValueError(f"{name} is blank")
    return value


def check_choice(name: str, value: object, allowed: tuple) -> str:
    """The value, if it is one of allowed."""
    if value not in allowed:
        raise ValueError(f"{name} = {value!r} is not one of {allowed}")
    return value
