"""Tests of the alert rule and of closing alerts."""

import pandas as pd
import pytest

from src.sentinella import alerts, config

RULE = config.AlertRule(
    window_months=3, floor=0.85, minimum_discordant=5, owner="Office manager"
)
WINDOW = ["2025-01", "2025-02", "2025-03"]


def outcomes(rows: list[tuple]) -> pd.DataFrame:
    """Sentinel outcomes from (office, month, concordant, overridden) rows."""
    return pd.DataFrame(rows, columns=["office", "month", "concordant", "overridden"])


def discordant(office: str, month: str, overridden: int, accepted: int) -> list:
    return [(office, month, False, True)] * overridden + [
        (office, month, False, False)
    ] * accepted


def checks_for(rows: list) -> pd.DataFrame:
    return alerts.check(outcomes(rows), WINDOW, RULE).set_index("office")


def test_rule_fires_when_upper_bound_is_below_floor():
    # 3 of 10 overridden: the upper end of the Wilson interval is 0.60.
    checks = checks_for(discordant("sotap", "2025-03", 3, 7))
    assert checks.loc["sotap", "fires"]
    assert checks.loc["sotap", "ci_high"] < RULE.floor


def test_rule_holds_while_upper_bound_reaches_floor():
    # 8 of 10 overridden: the upper end of the Wilson interval is 0.94.
    assert not checks_for(discordant("sotap", "2025-03", 8, 2)).loc["sotap", "fires"]


def test_rule_waits_for_minimum_discordant_decisions():
    # None of 4 overridden is below the floor, but 4 decisions are too few.
    checks = checks_for(discordant("sotap", "2025-03", 0, 4))
    assert checks.loc["sotap", "ci_high"] < RULE.floor
    assert not checks.loc["sotap", "fires"]


def test_only_discordant_sentinels_in_the_window_count():
    rows = (
        discordant("sotap", "2025-02", 6, 4)
        + discordant("sotap", "2024-12", 0, 20)
        + [("sotap", "2025-02", True, False)] * 30
    )
    assert checks_for(rows).loc["sotap", "n"] == 10


def test_office_with_open_alert_gets_no_second_alert():
    checks = alerts.check(outcomes(discordant("sotap", "2025-03", 3, 7)), WINDOW, RULE)
    first = alerts.raise_alerts(checks, WINDOW, [], RULE)
    assert [(alert.office, alert.opened_at) for alert in first] == [
        ("sotap", "2025-03")
    ]
    assert alerts.raise_alerts(checks, WINDOW, first, RULE) == []


def test_closed_alert_reopens_from_the_next_month_if_the_rule_still_fires():
    rows = discordant("sotap", "2025-03", 3, 7)
    first = alerts.raise_alerts(
        alerts.check(outcomes(rows), WINDOW, RULE), WINDOW, [], RULE
    )
    closed = alerts.close(
        first[0], "Office manager, sotap", "Screen reverted.", "2025-03"
    )
    same_month = alerts.check(outcomes(rows), WINDOW, RULE)
    assert alerts.raise_alerts(same_month, WINDOW, [closed], RULE) == []
    later = ["2025-02", "2025-03", "2025-04"]
    next_month = alerts.check(outcomes(rows), later, RULE)
    reopened = alerts.raise_alerts(next_month, later, [closed], RULE)
    assert [(alert.office, alert.opened_at) for alert in reopened] == [
        ("sotap", "2025-04")
    ]


def test_alert_closes_only_with_owner_explanation():
    checks = alerts.check(outcomes(discordant("sotap", "2025-03", 3, 7)), WINDOW, RULE)
    (alert,) = alerts.raise_alerts(checks, WINDOW, [], RULE)
    assert alert.owner == "Office manager, sotap"
    with pytest.raises(ValueError, match="named owner"):
        alerts.close(alert, "Office manager, fupal", "Screen reverted.", "2025-04")
    with pytest.raises(ValueError, match="written explanation"):
        alerts.close(alert, alert.owner, "  ", "2025-04")
    closed = alerts.close(alert, alert.owner, "Screen reverted.", "2025-04")
    assert (closed.closed_by, closed.explanation) == (alert.owner, "Screen reverted.")
    with pytest.raises(ValueError, match="already closed"):
        alerts.close(closed, alert.owner, "Again.", "2025-05")
