"""Tests of the simulation of offices, caseworkers and committee, on S8."""

import pytest

from src.dataset import DATA_PATH, load_sample, to_english
from src.sentinella import config, simulate

pytestmark = pytest.mark.skipif(
    not DATA_PATH.exists(), reason="S8 data file not present; see data/README.md"
)
DEMO = config.load()


@pytest.fixture(scope="module")
def setup():
    return simulate.setup(to_english(load_sample()), DEMO)


def test_alert_fires_in_the_drift_office_after_the_screen_change(setup):
    result = simulate.run(setup, DEMO, "drift", seed=DEMO.simulation.seed)
    months = simulate.month_labels(DEMO.simulation)
    changed = months[DEMO.simulation.drift_month - 1]
    drift_alerts = [
        a for a in result.alerts if a.office == DEMO.simulation.drift_office
    ]
    assert drift_alerts
    assert drift_alerts[0].opened_at >= changed


def test_only_the_drift_office_changes_screen(setup):
    drift = simulate.run(setup, DEMO, "drift", seed=2)
    control = simulate.run(setup, DEMO, "control", seed=2)
    changed = {
        (d.office, d.month)
        for d in drift.decisions
        if d.variant == simulate.CHANGED_SCREEN
    }
    months = simulate.month_labels(DEMO.simulation)
    assert {office for office, _ in changed} == {DEMO.simulation.drift_office}
    assert min(month for _, month in changed) == months[DEMO.simulation.drift_month - 1]
    assert all(d.variant == simulate.BASELINE_SCREEN for d in control.decisions)


def test_simulated_records_are_labelled_simulated(setup):
    result = simulate.run(setup, DEMO, "control", seed=3)
    assert result.decisions and result.reviews
    assert all(decision.simulated for decision in result.decisions)
    assert all(review.simulated for review in result.reviews)


def test_run_is_reproducible(setup):
    first = simulate.run(setup, DEMO, "drift", seed=4)
    second = simulate.run(setup, DEMO, "drift", seed=4)
    assert first.decisions == second.decisions
    assert first.reviews == second.reviews
    assert first.alerts == second.alerts
