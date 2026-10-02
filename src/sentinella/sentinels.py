"""Sentinel pool drawn from the S8 sample, and blind injection into queues.

A sentinel is a household whose reference decision is known in advance: the demo
rule applied to the category the Scorecard formula gives its record. Cashy's
displayed answer is either concordant with that reference or deliberately
discordant with it, in one of three ways that can each be seen on screen:

- input misread: answer and reasoning are computed with one factor moved by one
  level, so a factor score stated by Cashy differs from the record;
- category mismatch: the score is right but the category shown is the adjacent
  one, so the score lies outside the band of the category shown;
- reasoning-answer inconsistency: the reasoning is faithful to the record but the
  answer is computed with one factor moved by one level, so the two disagree.

Only discordant answers whose demo recommendation differs from the reference are
used.
"""

from collections import Counter
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp

from src.data_dictionary import FACTORS
from src.sentinella import fragility
from src.sentinella.config import CATEGORIES, Config, SentinelSettings
from src.sentinella.reasoning import reasoning
from src.sentinella.schema import (
    CASE_PREFIX,
    CATEGORY_MISMATCH,
    EXCLUDE,
    INCLUDE,
    INPUT_MISREAD,
    REASONING_INCONSISTENCY,
    RECORD_FIELDS,
    SENTINEL_PREFIX,
    Sentinel,
    household_record,
)


def build_pool(
    sample: pd.DataFrame, config: Config
) -> tuple[list[Sentinel], pd.DataFrame]:
    """Sentinels drawn from the sample, and the real queue of the other households.

    Args:
        sample: The S8 sample with English labels (dataset.to_english), indexed by
            row position.
        config: Demo configuration; its sentinels section sets the balance.

    Returns:
        The sentinels in random order, and the queue: one row per remaining
        household with its case ID, office, month and record fields.

    Raises:
        ValueError: If the sample cannot supply the balance the settings ask for.
    """
    settings = config.sentinels
    rng = np.random.default_rng(settings.seed)
    households = fragility.assess(sample[FACTORS], config.demo_rule, config.fragility)
    households["far"] = households["boundary_distance"] >= settings.far_distance
    households["direction"] = np.where(
        households["recommendation"] == INCLUDE, EXCLUDE, INCLUDE
    )
    variants = discordant_variants(sample, households, config)
    drawn = draw_households(
        households, variants, sample["NumIntegrantes"], pool_counts(settings), rng
    )
    shuffled = [drawn[position] for position in rng.permutation(len(drawn))]
    pool = [
        make_sentinel(
            f"{SENTINEL_PREFIX}{number:04d}",
            sample.loc[row],
            households.loc[row],
            variant,
        )
        for number, (row, variant) in enumerate(shuffled, start=1)
    ]
    return pool, real_queue(sample.drop(index=[row for row, _ in drawn]))


def draw_households(
    households: pd.DataFrame,
    variants: pd.DataFrame,
    sizes: pd.Series,
    counts: dict[str, int],
    rng: np.random.Generator,
) -> list[tuple]:
    """Households for the pool, each with the discordant variant to show or None.

    Discordant households are drawn first, cell by cell as allocate plans, and
    the concordant ones from the rest. Each draw is weighted towards the
    household-size mix of the whole sample.
    """
    target = sizes.value_counts(normalize=True)
    discordant = households.loc[variants["row"].unique()]
    plan = allocate(discordant.groupby(["fragile", "direction", "far"]).size(), counts)
    options = dict(tuple(variants.groupby("row")))
    drawn = []
    for (fragile, direction, far), n in plan.items():
        in_cell = (
            (discordant["fragile"] == fragile)
            & (discordant["direction"] == direction)
            & (discordant["far"] == far)
        )
        for row in draw(discordant.index[in_cell.to_numpy()], n, sizes, target, rng):
            drawn.append((row, options[row].iloc[rng.integers(len(options[row]))]))
    rest = households.drop(index=[row for row, _ in drawn])
    for fragile, n in (
        (True, counts["concordant_fragile"]),
        (False, counts["concordant"] - counts["concordant_fragile"]),
    ):
        cell = rest.index[(rest["fragile"] == fragile).to_numpy()]
        drawn += [(row, None) for row in draw(cell, n, sizes, target, rng)]
    return drawn


def real_queue(rows: pd.DataFrame) -> pd.DataFrame:
    """Real cases: case ID, office, month and record fields of each household."""
    return pd.DataFrame(
        {
            "case_id": [f"{CASE_PREFIX}{row:04d}" for row in rows.index],
            "office": rows["OficinaACNUR"].astype(str),
            "month": rows["month"],
        },
        index=rows.index,
    ).join(rows[list(RECORD_FIELDS)])


def discordant_variants(
    sample: pd.DataFrame, households: pd.DataFrame, config: Config
) -> pd.DataFrame:
    """Every discordant answer Cashy could display for each household.

    Args:
        sample: The sample the households come from.
        households: Output of fragility.assess for the sample.
        config: Demo configuration.

    Returns:
        One row per household and variant: the type of discordance, the factor
        moved and its new level (for the two types that move one), and the
        answer shown. Every variant changes the demo recommendation.
    """
    moves = fragility.shifts(sample[FACTORS], config.demo_rule)
    moves = moves[moves["recommendation_changes"]]
    variants = [
        pd.DataFrame(
            {
                "row": moves["case"],
                "discordance_type": kind,
                "factor": moves["factor"],
                "shown_level": moves["shifted_level"],
                "shown_score": moves["shifted_final_score"],
                "shown_category": moves["shifted_category"],
                "shown_recommendation": moves["shifted_recommendation"],
            }
        )
        for kind in (INPUT_MISREAD, REASONING_INCONSISTENCY)
    ]
    mismatches = []
    for row, household in households.iterrows():
        position = CATEGORIES.index(household["category"])
        for adjacent in (position - 1, position + 1):
            if not 0 <= adjacent < len(CATEGORIES):
                continue
            recommendation = config.demo_rule.recommend(CATEGORIES[adjacent])
            if recommendation != household["recommendation"]:
                mismatches.append(
                    {
                        "row": row,
                        "discordance_type": CATEGORY_MISMATCH,
                        "factor": None,
                        "shown_level": np.nan,
                        "shown_score": household["final_score"],
                        "shown_category": CATEGORIES[adjacent],
                        "shown_recommendation": recommendation,
                    }
                )
    variants.append(pd.DataFrame(mismatches, columns=variants[0].columns))
    return pd.concat(variants, ignore_index=True)


def pool_counts(settings: SentinelSettings) -> dict[str, int]:
    """Sentinels in each balance group implied by the settings."""
    discordant = round(settings.pool_size * settings.discordant_share)
    concordant = settings.pool_size - discordant
    return {
        "concordant": concordant,
        "concordant_fragile": round(concordant * settings.fragile_share),
        "discordant": discordant,
        "discordant_fragile": round(discordant * settings.fragile_share),
        "exclusion": round(discordant * settings.exclusion_share),
        "far": round(discordant * settings.far_share),
    }


def allocate(available: pd.Series, counts: dict[str, int]) -> dict[tuple, int]:
    """Discordant sentinels to draw from each fragility, direction and distance cell.

    The fragile and exclusion totals are met exactly, with fragility and
    direction as close to independent as the available households allow. At
    least the far total come from households far from every boundary.

    Args:
        available: Discordant candidate households per (fragile, direction, far).
        counts: Output of pool_counts.

    Raises:
        ValueError: If no allocation meets the totals.
    """

    def capacity(key: tuple, far: bool) -> int:
        return int(available.get((*key, far), 0))

    total, fragile = counts["discordant"], counts["discordant_fragile"]
    exclusion = counts["exclusion"]

    def cells(fragile_exclusion: int) -> dict[tuple, int]:
        return {
            (True, EXCLUDE): fragile_exclusion,
            (True, INCLUDE): fragile - fragile_exclusion,
            (False, EXCLUDE): exclusion - fragile_exclusion,
            (False, INCLUDE): total - fragile - exclusion + fragile_exclusion,
        }

    feasible = [
        t
        for t in range(min(fragile, exclusion) + 1)
        if all(
            0 <= n <= capacity(key, True) + capacity(key, False)
            for key, n in cells(t).items()
        )
    ]
    if not feasible:
        raise ValueError(
            "the sample cannot supply the fragility and direction balance asked for"
        )
    independent = fragile * exclusion / total if total else 0
    sizes = cells(min(feasible, key=lambda t: abs(t - independent)))
    # Far households first where a cell runs out of near ones, then more far
    # households, from the cells with most to spare, up to the far total.
    far = {key: max(0, n - capacity(key, False)) for key, n in sizes.items()}
    spare = {key: min(n, capacity(key, True)) - far[key] for key, n in sizes.items()}
    missing = counts["far"] - sum(far.values())
    for key in sorted(spare, key=spare.get, reverse=True):
        extra = min(max(missing, 0), spare[key])
        far[key] += extra
        missing -= extra
    if missing > 0:
        raise ValueError("the sample cannot supply the far sentinels asked for")
    plan = {}
    for key, n in sizes.items():
        plan[(*key, True)] = far[key]
        plan[(*key, False)] = n - far[key]
    return {key: n for key, n in plan.items() if n > 0}


def draw(
    candidates: pd.Index,
    n: int,
    sizes: pd.Series,
    target: pd.Series,
    rng: np.random.Generator,
) -> list:
    """n households from candidates, weighted towards the target household sizes.

    Raises:
        ValueError: If there are fewer than n candidates.
    """
    if n > len(candidates):
        raise ValueError(f"{n} households asked for, only {len(candidates)} available")
    if n == 0:
        return []
    size = sizes.loc[candidates]
    weights = size.map(target) / size.map(size.value_counts(normalize=True))
    chosen = rng.choice(
        len(candidates), size=n, replace=False, p=(weights / weights.sum()).to_numpy()
    )
    return list(candidates[chosen])


@dataclass(frozen=True)
class Display:
    """What Cashy displays on one case: its reasoning and its answer."""

    shown_factors: dict[str, float]  # factor scores the answer was computed from
    shown_score: float
    shown_category: str
    shown_recommendation: str
    reasoning: str
    discordance_type: str | None  # None when concordant with the reference
    altered_factor: str | None


def displayed_answer(
    record: dict[str, object], household: pd.Series, variant: pd.Series | None
) -> Display:
    """Cashy's display for a household: faithful, or the discordant variant given.

    Args:
        record: The household's fields, as in schema.household_record.
        household: The household's row of fragility.assess.
        variant: A row of discordant_variants for the household, or None.
    """
    factors = {factor: record[factor] for factor in FACTORS}
    truth = (
        float(household["final_score"]),
        household["category"],
        household["recommendation"],
    )
    faithful = reasoning(record, factors, *truth)
    if variant is None:
        return Display(factors, *truth, faithful, None, None)
    kind = variant["discordance_type"]
    shown_factors = dict(factors)
    altered = None if kind == CATEGORY_MISMATCH else variant["factor"]
    if altered is not None:
        shown_factors[altered] = float(variant["shown_level"])
    answer = (
        float(variant["shown_score"]),
        variant["shown_category"],
        variant["shown_recommendation"],
    )
    text = (
        faithful
        if kind == REASONING_INCONSISTENCY
        else reasoning(record, shown_factors, *answer)
    )
    return Display(shown_factors, *answer, text, kind, altered)


def make_sentinel(
    sentinel_id: str,
    row: pd.Series,
    household: pd.Series,
    variant: pd.Series | None,
) -> Sentinel:
    """Sentinel built from one household and, if discordant, the answer to show."""
    record = household_record(row)
    return Sentinel(
        sentinel_id=sentinel_id,
        record=record,
        **asdict(displayed_answer(record, household, variant)),
        reference_decision=household["recommendation"],
        fragile=bool(household["fragile"]),
    )


def inject(
    queue: pd.DataFrame,
    pool: list[Sentinel],
    uses: Counter,
    seen: set[str],
    settings: SentinelSettings,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """One caseworker's queue with sentinels inserted blind.

    Every position of the returned queue holds a sentinel with probability
    injection_rate. A sentinel takes the office and month of the real case that
    follows it, so neither gives it away. It is never given twice to the same
    caseworker and retires after max_uses decisions.

    Args:
        queue: The caseworker's real cases in order, with case_id, office and
            month columns.
        pool: The sentinel pool.
        uses: Decisions each sentinel has received so far; updated in place.
        seen: Sentinels this caseworker has received so far; updated in place.
        settings: Sentinel settings of the demo configuration.
        rng: Random generator.

    Returns:
        The queue with the sentinels in it, with the same three columns.
    """
    rows = []
    for case in queue[["case_id", "office", "month"]].itertuples(index=False):
        while rng.random() < settings.injection_rate:
            eligible = [
                sentinel.sentinel_id
                for sentinel in pool
                if uses[sentinel.sentinel_id] < settings.max_uses
                and sentinel.sentinel_id not in seen
            ]
            if not eligible:
                break
            chosen = eligible[rng.integers(len(eligible))]
            uses[chosen] += 1
            seen.add(chosen)
            rows.append((chosen, case.office, case.month))
        rows.append(tuple(case))
    return pd.DataFrame(rows, columns=["case_id", "office", "month"])


def describe_pool(pool: list[Sentinel], config: Config) -> pd.DataFrame:
    """One row per sentinel: balance attributes, record category, household size."""
    factors = pd.DataFrame(
        [{f: sentinel.record[f] for f in FACTORS} for sentinel in pool]
    )
    assessed = fragility.assess(factors, config.demo_rule, config.fragility)
    distance = assessed["boundary_distance"]
    return pd.DataFrame(
        {
            "sentinel_id": [sentinel.sentinel_id for sentinel in pool],
            "concordant": [sentinel.concordant for sentinel in pool],
            "discordance_type": [sentinel.discordance_type for sentinel in pool],
            "direction": [sentinel.direction for sentinel in pool],
            "category": assessed["category"],
            "fragile": [sentinel.fragile for sentinel in pool],
            "far": distance >= config.sentinels.far_distance,
            "boundary_distance": distance,
            "NumIntegrantes": [sentinel.record["NumIntegrantes"] for sentinel in pool],
        }
    )


def distribution_checks(sentinels: pd.DataFrame, real: pd.DataFrame) -> pd.DataFrame:
    """Sentinels against real cases: standardized mean differences and KS tests.

    Household size and month (counted in months) are compared as numbers, with
    a two-sample KS test; the office as one indicator per office. Only columns
    present in both frames are compared.
    """
    rows = []
    for column in ("NumIntegrantes", "month"):
        if column not in sentinels or column not in real:
            continue
        a, b = as_number(sentinels[column]), as_number(real[column])
        test = ks_2samp(a, b)
        rows.append(
            {
                "variable": column,
                "level": None,
                "sentinels": a.mean(),
                "real": b.mean(),
                "smd": standardized_difference(a, b),
                "ks_statistic": test.statistic,
                "ks_pvalue": test.pvalue,
            }
        )
    if "office" in sentinels and "office" in real:
        for office in sorted(set(real["office"]) | set(sentinels["office"])):
            a = (sentinels["office"] == office).astype(float)
            b = (real["office"] == office).astype(float)
            rows.append(
                {
                    "variable": "office",
                    "level": office,
                    "sentinels": a.mean(),
                    "real": b.mean(),
                    "smd": standardized_difference(a, b),
                }
            )
    return pd.DataFrame(rows)


def as_number(values: pd.Series) -> pd.Series:
    """Values as floats; months written YYYY-MM become a count of months."""
    if values.name == "month":
        return (
            values.str.slice(0, 4).astype(int) * 12 + values.str.slice(5, 7).astype(int)
        ).astype(float)
    return values.astype(float)


def standardized_difference(a: pd.Series, b: pd.Series) -> float:
    """Difference in means divided by the pooled standard deviation."""
    spread = np.sqrt((a.var() + b.var()) / 2)
    if spread == 0:
        return 0.0 if a.mean() == b.mean() else float("inf")
    return float((a.mean() - b.mean()) / spread)
