"""Manager dashboard: the three streams, the alert queue and the office manager's follow-up.

Aggregates come with their intervals, and a row that rests on fewer
caseworkers than the configured minimum is hidden. The one view of individual
caseworkers is the office manager's comparison of their own staff with the
committee, as the team's monitoring requirements ask. Simulated records and
records entered in the app are never pooled.
"""

import dataclasses
from datetime import datetime

import pandas as pd
import streamlit as st

from app import state
from src.dataset import REPO_ROOT
from src.sentinella import alerts, audit, export, metrics, sentinels, simulate, store
from src.sentinella.schema import (
    TARGETED,
    Alert,
    Decision,
    InitialAssessment,
    Review,
    ReviewRequest,
    Sentinel,
    is_sentinel,
)

SOURCES = {"Simulated year": "simulation", "Entered in the app": "app"}
PROGRAMME = "Programme manager"
# Offices take the theme's palette in order; the floor is grey so that it never
# shares a colour with an office.
OFFICE_COLORS = [
    "#0072BC",
    "#18375F",
    "#00B398",
    "#EF4A60",
    "#8EBEFF",
    "#F2A900",
    "#6E4C9E",
]
FLOOR_COLOR = "#5B6F82"
FLOOR = "floor (demo value)"


def percent(values: pd.Series) -> pd.Series:
    """Shares as percentages; a hidden value reads hidden."""
    return values.map(lambda v: "hidden" if pd.isna(v) else f"{v:.1%}")


def interval(low: pd.Series, high: pd.Series) -> list[str]:
    """Interval ends as a percentage range; blank when hidden."""
    return ["" if pd.isna(a) else f"{a:.1%} to {b:.1%}" for a, b in zip(low, high)]


def readable(table: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    """Label columns, n, and the rate with its intervals as percentages."""
    out = table[[*labels, "n"]].copy()
    out["rate"] = percent(table["rate"])
    out["95% CI"] = interval(table["ci_low"], table["ci_high"])
    if "cluster_ci_low" in table:
        out["95% CI, caseworkers resampled"] = interval(
            table["cluster_ci_low"], table["cluster_ci_high"]
        )
    out["caseworkers"] = table["caseworkers"]
    return out


def breakdown(table: pd.DataFrame, choices: dict[str, list[str]], key: str) -> None:
    """A breakdown chosen by the viewer, shown with its intervals."""
    name = st.selectbox("Breakdown", list(choices), key=key, width=300)
    labels = choices[name] + [c for c in ("measure", "action") if c in table]
    st.dataframe(readable(table[table["breakdown"] == name], labels), hide_index=True)


def parameters(config: object) -> pd.DataFrame:
    """Every parameter of the demo configuration, one row each."""
    rows = []
    for section, values in dataclasses.asdict(config).items():
        for name, value in values.items():
            if isinstance(value, frozenset):
                value = ", ".join(sorted(value))
            rows.append((section, name, str(value)))
    return pd.DataFrame(rows, columns=["Section", "Parameter", "Demo value"])


def rule_view(outcomes: pd.DataFrame) -> pd.DataFrame:
    """The alert rule's check in every month, each over the window ending there."""
    months = sorted(outcomes["month"].unique())
    checks = [
        alerts.check(
            outcomes,
            months[max(0, end + 1 - demo.alerts.window_months) : end + 1],
            demo.alerts,
        ).assign(month=months[end])
        for end in range(len(months))
    ]
    return pd.concat(checks, ignore_index=True) if checks else pd.DataFrame()


def human_first(initials: list[InitialAssessment], decisions: list[Decision]) -> list:
    """Each initial assessment with the final decision on the same case, if any."""
    finals = {(d.case_id, d.caseworker): d for d in decisions}
    return [
        (initial, finals[(initial.case_id, initial.caseworker)])
        for initial in initials
        if (initial.case_id, initial.caseworker) in finals
    ]


@st.cache_data(show_spinner="Computing the aggregates")
def tables(
    source: str, counts: tuple, _decisions, _reviews, _requests, _pool_table
) -> dict[str, pd.DataFrame]:
    """Monitoring tables of a source; counts of its records key the cache."""
    return {
        "reliance": export.reliance_table(_decisions, _pool_table, demo, source),
        "disagreement": export.disagreement_table(_decisions, _reviews, demo, source),
        "targeted": export.targeted_table(
            _decisions, _reviews, _requests, demo, source
        ),
        "times": export.times_table(_decisions, demo, source),
    }


demo, staff = state.demo(), state.staff()
offices = sorted(staff["office"].unique())
st.title("Manager dashboard", icon=":material/monitoring:")
st.caption(
    "Sentinels, the random audit and targeted reviews, kept apart. Every "
    "parameter is a demo value, not a recommendation."
)
with st.container(horizontal=True, vertical_alignment="bottom"):
    label = st.segmented_control(
        "Records", list(SOURCES), default="Simulated year", required=True
    )
    role = st.selectbox(
        "Viewing as",
        [PROGRAMME, *[alerts.owner(office, demo.alerts) for office in offices]],
        width=300,
    )
source = SOURCES[label]

if source == "simulation":
    if not store.SIMULATION_DATABASE.exists():
        st.info(
            "No simulated year yet. Generate it here, or from the repository root "
            "run: python -m src.sentinella.simulate history",
            icon=":material/info:",
        )
        if st.button(
            "Generate the simulated year", type="primary", icon=":material/play_arrow:"
        ):
            with st.spinner("Simulating a year of seven offices"):
                simulate.write_history(demo, store.SIMULATION_DATABASE)
            st.rerun()
        st.stop()
    connection = store.connect(store.SIMULATION_DATABASE)
    st.warning(
        "Simulated year: simulated caseworkers and committee under demo values. "
        "Nothing here describes a real operation.",
        icon=":material/science:",
    )
else:
    connection = state.app_records()
    st.caption(
        "Decisions entered in this prototype on synthetic cases; never pooled "
        "with the simulated year."
    )

decisions = store.load(connection, Decision)
reviews = store.load(connection, Review)
requests = store.load(connection, ReviewRequest)
initials = store.load(connection, InitialAssessment)
pool_table = sentinels.describe_pool(store.load(connection, Sentinel), demo)
outcomes = metrics.sentinel_outcomes(decisions, pool_table)
if source == "app" and not outcomes.empty:
    month = state.now()[:7]
    window = pd.period_range(end=month, periods=demo.alerts.window_months, freq="M")
    window = window.astype(str).tolist()
    store.add(
        connection,
        *alerts.raise_alerts(
            alerts.check(outcomes, window, demo.alerts),
            window,
            store.load(connection, Alert),
            demo.alerts,
        ),
    )
stored = store.load(connection, Alert)
computed = tables(
    source,
    (len(decisions), len(reviews), len(requests)),
    decisions,
    reviews,
    requests,
    pool_table,
)

with st.container(horizontal=True):
    st.metric("Decisions", f"{len(decisions):,}", border=True)
    st.metric(
        "On sentinels",
        f"{sum(is_sentinel(d.case_id) for d in decisions):,}",
        border=True,
    )
    st.metric("Committee reviews", f"{len(reviews):,}", border=True)
    st.metric(
        "Waiting for review",
        f"{len({r.decision_id for r in audit.pending(requests, reviews)}):,}",
        border=True,
    )
    st.metric(
        "Open alerts", sum(alert.closed_at is None for alert in stored), border=True
    )
st.caption(
    f"Rows resting on fewer than {demo.monitor.minimum_caseworkers} caseworkers "
    "are hidden."
)

(
    alerts_tab,
    sentinels_tab,
    audit_tab,
    targeted_tab,
    office_tab,
    time_tab,
    values_tab,
    exports_tab,
) = st.tabs(
    [
        ":material/notifications: Alerts",
        ":material/verified: Sentinels",
        ":material/shuffle: Random audit",
        ":material/flag: Targeted reviews",
        ":material/supervisor_account: Office follow-up",
        ":material/timer: Decision time",
        ":material/tune: Demo values",
        ":material/download: Exports",
    ]
)

with alerts_tab:
    st.caption(f"{alerts.describe(demo.alerts)}. Demo values.")
    for alert in [a for a in stored if a.closed_at is None]:
        with st.container(border=True):
            st.markdown(f"**{alert.office}**, opened {alert.opened_at}")
            st.write(alert.evidence)
            if role != alert.owner:
                st.caption(
                    f"Only the named owner, {alert.owner}, can close this alert, "
                    "with a written explanation."
                )
                continue
            explanation = st.text_area("Explanation", key=f"explain-{alert.alert_id}")
            if st.button(
                "Close alert",
                key=f"close-{alert.alert_id}",
                disabled=not explanation.strip(),
            ):
                store.update(
                    connection,
                    alerts.close(alert, role, explanation.strip(), state.now()),
                )
                st.rerun()
    closed = [vars(a) for a in stored if a.closed_at is not None]
    if closed:
        st.subheader("Closed alerts")
        st.dataframe(pd.DataFrame(closed), hide_index=True)
    if not stored:
        st.info("No alert has been raised.")
    st.caption(
        "No automatic disciplinary action follows an alert; the owner explains "
        "it and decides the follow-up."
    )
    view = rule_view(outcomes)
    if not view.empty:
        with st.container(border=True):
            st.subheader("Correct override by office, over the rule's window")
            chart = view.pivot(index="month", columns="office", values="rate")
            offices_shown = list(chart.columns)
            chart[FLOOR] = demo.alerts.floor
            st.line_chart(
                chart,
                y=[*offices_shown, FLOOR],
                color=[
                    *(
                        OFFICE_COLORS[i % len(OFFICE_COLORS)]
                        for i in range(len(offices_shown))
                    ),
                    FLOOR_COLOR,
                ],
                x_label="Last month of the window",
                y_label="Correct override",
            )

with sentinels_tab:
    st.caption(
        "Decisions on sentinels, relative to the reference standard: the demo "
        "rule applied to the formula category of the sentinel's record, not the "
        "truth about a household's need. Correct override and over-reliance are "
        "shares of decisions on discordant sentinels; correct acceptance and "
        "under-reliance, of decisions on concordant ones."
    )
    breakdown(computed["reliance"], export.RELIANCE_BREAKDOWNS, "reliance")

with audit_tab:
    st.caption(
        "Decisions on real cases sampled at random, accepted and overridden "
        "alike, compared with the blind committee. Disagreement with the "
        "committee is not an established error. Accepted and overridden "
        "decisions are never pooled."
    )
    breakdown(computed["disagreement"], export.DISAGREEMENT_BREAKDOWNS, "audit")

with targeted_tab:
    st.caption(
        "Decisions selected by the targeted rule or referred by a manager. They "
        "are chosen because they look risky, so these counts are cases to follow "
        "up, never a rate."
    )
    st.dataframe(computed["targeted"].drop(columns="source"), hide_index=True)

with office_tab:
    if role == PROGRAMME:
        st.info("Choose an office manager under Viewing as.", icon=":material/badge:")
    else:
        office = role.removeprefix(f"{demo.alerts.owner}, ")
        mine = set(staff.loc[staff["office"] == office, "caseworker"])
        by_id = {d.decision_id: d for d in decisions}
        with st.container(border=True):
            st.subheader("Targeted reviews where the committee decided otherwise")
            rows = [
                (
                    r.decision_id,
                    by_id[r.decision_id].caseworker,
                    by_id[r.decision_id].month,
                    by_id[r.decision_id].decision,
                    r.committee_decision,
                    r.reason,
                )
                for r in reviews
                if r.stream == TARGETED
                and by_id[r.decision_id].office == office
                and r.committee_decision != by_id[r.decision_id].decision
            ]
            st.dataframe(
                pd.DataFrame(
                    rows,
                    columns=[
                        "decision",
                        "caseworker",
                        "month",
                        "caseworker's decision",
                        "committee",
                        "selected because",
                    ],
                ),
                hide_index=True,
            )
        with st.container(border=True):
            st.subheader("Caseworkers compared with the committee")
            st.caption(
                "Random-audit decisions of each caseworker in the office, accepted "
                "and overridden apart. A disagreement is not an established error "
                "and no sanction follows from these numbers. Comparing several "
                "caseworkers at 95% means about one interval in twenty excludes "
                "the office's rate by chance alone."
            )
            people = metrics.committee_disagreement(decisions, reviews, ["caseworker"])
            if not people.empty:
                people = people[people["caseworker"].isin(mine)]
                st.dataframe(
                    readable(people, ["caseworker", "action"]), hide_index=True
                )
        pairs = [
            (initial, final)
            for initial, final in human_first(initials, decisions)
            if final.office == office
        ]
        if pairs:
            with st.container(border=True):
                st.subheader("Human first: before and after the AI assessment")
                st.dataframe(
                    pd.DataFrame(
                        [
                            {
                                "caseworker": final.caseworker,
                                "initial decision": initial.decision,
                                "final decision": final.decision,
                                "changed": initial.decision != final.decision,
                                "initial justification": initial.justification,
                                "final justification": final.justification,
                            }
                            for initial, final in pairs
                        ]
                    ),
                    hide_index=True,
                )
                st.caption(
                    "A change after seeing the AI assessment is not, on its own, "
                    "evidence of improvement or of bias."
                )
        if source == "app":
            with st.container(border=True):
                st.subheader("Refer a decision for blind review")
                referable = [
                    d
                    for d in reversed(decisions)
                    if d.office == office and not is_sentinel(d.case_id)
                ]
                chosen = st.selectbox(
                    "Decision",
                    referable,
                    index=None,
                    format_func=lambda d: (
                        f"{d.decision_id}: {d.caseworker}, {d.decided_at}, decided "
                        f"{d.decision}, Cashy recommended {d.shown_recommendation}"
                    ),
                )
                reason = st.text_area("Reason for the referral")
                if st.button("Refer", disabled=chosen is None or not reason.strip()):
                    store.add(connection, audit.refer(chosen, reason.strip()))
                    st.success("Referred to the committee.")

with time_tab:
    st.caption(
        "Recorded time from opening a case to submitting the decision, for "
        "decisions entered in the app; the simulation does not model time. "
        "Recorded time is not attention: a long or short time is a prompt to "
        "look, not a finding."
    )
    times = computed["times"]
    if times.empty:
        st.info("No decision with recorded times.")
    else:
        shown = times[["office", "variant", "n", "caseworkers"]].copy()
        shown["median, minutes"] = (times["median_seconds"] / 60).round(1)
        shown["90th percentile, minutes"] = (times["p90_seconds"] / 60).round(1)
        st.dataframe(shown, hide_index=True)
    pairs = human_first(initials, decisions)
    if pairs:
        with st.container(border=True):
            st.subheader("Human first: time before and after the initial assessment")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "office": final.office,
                            "minutes before the initial assessment": round(
                                (
                                    datetime.fromisoformat(initial.recorded_at)
                                    - datetime.fromisoformat(initial.opened_at)
                                ).total_seconds()
                                / 60,
                                1,
                            ),
                            "minutes from it to the final decision": round(
                                (
                                    datetime.fromisoformat(final.decided_at)
                                    - datetime.fromisoformat(initial.recorded_at)
                                ).total_seconds()
                                / 60,
                                1,
                            ),
                        }
                        for initial, final in pairs
                    ]
                ),
                hide_index=True,
            )
            st.caption(
                "The second period includes the time before opening the AI "
                "assessment; it is not time spent reading it."
            )

with values_tab:
    st.caption("Demo values chosen to run the prototype on S8, not recommendations.")
    st.dataframe(parameters(demo), hide_index=True)

with exports_tab:
    folder = export.EXPORT_DIR / source
    st.caption(
        "Tidy CSV tables for Power BI or any BI tool, with schema.csv describing "
        f"every column, written to {folder.relative_to(REPO_ROOT)}."
    )
    if st.button("Write CSV exports", icon=":material/save:"):
        paths = export.write_all(connection, demo, source, folder)
        st.success(", ".join(path.name for path in paths))
    if initials:
        st.download_button(
            "Download human-first assessments",
            pd.DataFrame([vars(a) for a in initials]).to_csv(index=False),
            file_name="human-first-assessments.csv",
            mime="text/csv",
            icon=":material/download:",
        )
