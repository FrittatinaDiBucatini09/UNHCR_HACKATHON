"""Tests of the sentinel pool and of blind injection."""

import dataclasses
import itertools
import re
from collections import Counter

import numpy as np
import pandas as pd
import pytest

from src import scorecard
from src.data_dictionary import ENGLISH_NAMES, FACTORS
from src.dataset import DATA_PATH, load_sample, to_english
from src.score_model import predict
from src.sentinella import config, sentinels
from src.sentinella.schema import (
    CATEGORY_MISMATCH,
    INPUT_MISREAD,
    REASONING_INCONSISTENCY,
    is_sentinel,
)


def synthetic_sample() -> pd.DataFrame:
    """Households covering the factor levels, with household fields that cycle.

    Every fifth combination of factor levels is kept; five shares no factor with
    the level counts, so every level of every factor occurs.
    """
    factors = pd.DataFrame(
        list(itertools.product(*(scorecard.FACTOR_LEVELS[c] for c in FACTORS))),
        columns=FACTORS,
    ).iloc[::5]
    factors.index = range(len(factors))
    position = np.arange(len(factors))
    size = position % 6 + 1
    single = size == 1
    alternate = position % 2 == 0
    return factors.assign(
        NumIntegrantes=size,
        dependencyCategory=np.array(["Low", "Average", "High", "Complete"])[
            position % 4
        ],
        FemaleHeadedHousehold=np.where(
            single,
            "Not applicable",
            np.where(alternate, "Female-headed", "Male-headed"),
        ),
        CuidadorSolo=np.where(
            single, "Not applicable", np.where(alternate, "Yes", "No")
        ),
        HablaEspanol=np.where(alternate, "One or more adults", "No adult"),
        Analfabeta_si=np.where(position % 3 == 0, "One or more adults", "No adult"),
        OficinaACNUR=np.array(["sotap", "fupal", "foten"])[position % 3],
        month=np.array(["2024-01", "2024-02", "2024-03"])[position % 3],
    )


SAMPLE = synthetic_sample()
SETTINGS = config.SentinelSettings(
    pool_size=60,
    discordant_share=0.5,
    exclusion_share=0.5,
    fragile_share=0.7,
    far_share=0.2,
    far_distance=8.0,
    injection_rate=0.2,
    max_uses=2,
    seed=3,
)
# The sections the pool uses are set here; the others come from the demo file.
CONFIG = dataclasses.replace(
    config.load(),
    demo_rule=config.DemoRule(frozenset({"High", "Severe"})),
    fragility=config.Fragility("category"),
    sentinels=SETTINGS,
)


def check_balance(pool, queue, demo, sample):
    table = sentinels.describe_pool(pool, demo)
    counts = sentinels.pool_counts(demo.sentinels)
    concordant, discordant = table[table["concordant"]], table[~table["concordant"]]
    assert len(table) == demo.sentinels.pool_size
    assert len(discordant) == counts["discordant"]
    assert (discordant["direction"] == "Exclude").sum() == counts["exclusion"]
    assert concordant["fragile"].sum() == counts["concordant_fragile"]
    assert discordant["fragile"].sum() == counts["discordant_fragile"]
    assert discordant["far"].sum() >= counts["far"]
    # Every household is either a sentinel or a real case, never both.
    assert len(queue) == len(sample) - len(pool)
    assert queue["case_id"].is_unique


def test_pool_balance_matches_config():
    pool, queue = sentinels.build_pool(SAMPLE, CONFIG)
    check_balance(pool, queue, CONFIG, SAMPLE)


@pytest.mark.skipif(
    not DATA_PATH.exists(), reason="S8 data file not present; see data/README.md"
)
def test_demo_pool_on_s8_matches_demo_config():
    sample = to_english(load_sample())
    demo = config.load()
    pool, queue = sentinels.build_pool(sample, demo)
    check_balance(pool, queue, demo, sample)


def test_pool_is_reproducible():
    first, _ = sentinels.build_pool(SAMPLE, CONFIG)
    second, _ = sentinels.build_pool(SAMPLE, CONFIG)
    assert first == second


def test_every_discordance_shows_on_screen():
    pool, _ = sentinels.build_pool(SAMPLE, CONFIG)
    for sentinel in pool:
        record = {factor: sentinel.record[factor] for factor in FACTORS}
        misread = [f for f in FACTORS if sentinel.shown_factors[f] != record[f]]
        band = predict(sentinel.shown_factors)["category"]
        stated = re.search(r"category (\w+)\.", sentinel.reasoning).group(1)
        if sentinel.discordance_type == INPUT_MISREAD:
            # The reasoning states a factor score that differs from the record.
            (factor,) = misread
            level = sentinel.shown_factors[factor]
            assert f"{ENGLISH_NAMES[factor].lower()} {level:.2f}" in sentinel.reasoning
        elif sentinel.discordance_type == CATEGORY_MISMATCH:
            # The score shown lies outside the band of the category shown.
            assert band != sentinel.shown_category
        elif sentinel.discordance_type == REASONING_INCONSISTENCY:
            # The reasoning concludes the record's category; the answer does not.
            assert stated == predict(record)["category"] != sentinel.shown_category
        else:
            assert not misread
            assert band == stated == sentinel.shown_category
        assert sentinel.concordant == (sentinel.discordance_type is None)


def test_caseworker_never_sees_a_sentinel_twice_and_sentinels_retire():
    pool, queue = sentinels.build_pool(SAMPLE, CONFIG)
    uses, rng = Counter(), np.random.default_rng(0)
    for _ in range(10):
        seen, received = set(), []
        for start in range(0, 400, 100):
            batch = queue.iloc[start : start + 100]
            injected = sentinels.inject(batch, pool, uses, seen, SETTINGS, rng)
            received += [case for case in injected["case_id"] if is_sentinel(case)]
        assert len(received) == len(set(received))
    assert all(count <= SETTINGS.max_uses for count in uses.values())
    assert max(uses.values()) == SETTINGS.max_uses


def test_sentinel_takes_office_and_month_of_the_next_real_case():
    pool, queue = sentinels.build_pool(SAMPLE, CONFIG)
    injected = sentinels.inject(
        queue.iloc[:200], pool, Counter(), set(), SETTINGS, np.random.default_rng(1)
    )
    real = injected[~injected["case_id"].map(is_sentinel)]
    assert real["case_id"].tolist() == queue["case_id"].iloc[:200].tolist()
    following = (
        injected[["office", "month"]]
        .where(~injected["case_id"].map(is_sentinel))
        .bfill()
    )
    assert injected["case_id"].map(is_sentinel).any()
    pd.testing.assert_frame_equal(injected[["office", "month"]], following)
