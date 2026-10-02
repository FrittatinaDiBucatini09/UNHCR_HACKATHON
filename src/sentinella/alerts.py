"""Alert rule on each office's correct override on sentinels, and its explanation log.

An office raises an alert when its correct-override rate on discordant
sentinels, relative to the reference standard, is credibly below the floor:
over the window it has at least the minimum number of such decisions, and the
upper end of their Wilson 95% interval is under the floor. An alert stays open
until its named owner closes it with a written explanation.
"""

import dataclasses

import pandas as pd

from src.sentinella.config import AlertRule
from src.sentinella.metrics import wilson
from src.sentinella.schema import Alert

CHECK_COLUMNS = ["office", "n", "count", "rate", "ci_low", "ci_high", "fires"]


def describe(rule: AlertRule) -> str:
    """The rule in words, as stored with each alert."""
    return (
        f"Correct override on discordant sentinels over {rule.window_months} "
        f"months: upper end of the 95% interval below {rule.floor * 100:g}%, with at "
        f"least {rule.minimum_discordant} decisions"
    )


def owner(office: str, rule: AlertRule) -> str:
    """The named owner of an office's alerts."""
    return f"{rule.owner}, {office}"


def check(outcomes: pd.DataFrame, window: list[str], rule: AlertRule) -> pd.DataFrame:
    """Each office's correct-override rate over the window, and whether the rule fires.

    Args:
        outcomes: Output of metrics.sentinel_outcomes.
        window: The months the rate covers.
        rule: Alert settings of the demo configuration.

    Returns:
        One row per office with decisions on discordant sentinels in the window.
    """
    in_window = outcomes[outcomes["month"].isin(window) & ~outcomes["concordant"]]
    rows = []
    for office, group in in_window.groupby("office", sort=True):
        n, count = len(group), int(group["overridden"].sum())
        low, high = wilson(count, n)
        fires = n >= rule.minimum_discordant and high < rule.floor
        rows.append((office, n, count, count / n, low, high, fires))
    return pd.DataFrame(rows, columns=CHECK_COLUMNS)


def raise_alerts(
    checks: pd.DataFrame,
    window: list[str],
    alerts: list[Alert],
    rule: AlertRule,
) -> list[Alert]:
    """New alerts for the offices where the rule fires.

    An office with an open alert, or with an alert already opened in the last
    month of the window, gets no new one; once an owner closes an alert, the
    rule can raise another from the next month on.

    Args:
        checks: Output of check for the window.
        window: The months the checks cover; an alert opens in the last one.
        alerts: Alerts raised so far, open or closed.
        rule: Alert settings of the demo configuration.
    """
    skipped = {
        alert.office
        for alert in alerts
        if alert.closed_at is None or alert.opened_at == window[-1]
    }
    new = []
    for row in checks[checks["fires"]].itertuples(index=False):
        if row.office in skipped:
            continue
        new.append(
            Alert(
                alert_id=f"alert-{len(alerts) + len(new) + 1:04d}",
                office=row.office,
                rule=describe(rule),
                evidence=(
                    f"{row.count} of {row.n} decisions on discordant sentinels "
                    f"overrode Cashy ({row.rate:.0%}, 95% CI {row.ci_low:.0%} to "
                    f"{row.ci_high:.0%}), {window[0]} to {window[-1]}"
                ),
                opened_at=window[-1],
                owner=owner(row.office, rule),
                explanation=None,
                closed_by=None,
                closed_at=None,
            )
        )
    return new


def close(alert: Alert, closed_by: str, explanation: str, closed_at: str) -> Alert:
    """The alert, closed with its owner's written explanation.

    Raises:
        ValueError: If the alert is already closed, closed_by is not its named
            owner or the explanation is blank.
    """
    if alert.closed_at is not None:
        raise ValueError(f"{alert.alert_id} is already closed")
    return dataclasses.replace(
        alert, explanation=explanation, closed_by=closed_by, closed_at=closed_at
    )
