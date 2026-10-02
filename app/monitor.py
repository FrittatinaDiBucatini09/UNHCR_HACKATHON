"""Focused manager dashboard; mock, app and legacy simulation stay separate."""

import dataclasses
from datetime import datetime

import pandas as pd
import streamlit as st

from app import mock_data, state
from src.sentinella import alerts, audit, export, metrics, sentinels, store
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

SOURCES = {
    "Illustrative mock": "mock",
    "Entered in the app": "app",
    "Legacy simulated year": "simulation",
}
demo, book, staff = state.demo(), state.book(), state.staff()
st.title("Manager dashboard")
source = SOURCES[st.sidebar.selectbox("Data source", list(SOURCES))]
offices = sorted(staff["office"].unique())
office = st.sidebar.selectbox("Office", offices)
owner = alerts.owner(office, demo.alerts)
st.sidebar.caption("Demo navigation only — role selection is not authentication.")
if source == "mock":
    connection = mock_data.connection(book, staff, demo)
    st.warning(
        "ILLUSTRATIVE MOCK — invented decisions, reviews, times and follow-up. These are not app activity, beneficiary statistics or measured performance."
    )
elif source == "simulation":
    if not store.SIMULATION_DATABASE.exists():
        st.info(
            "No legacy simulated year is available. Use the mock for the presentation."
        )
        st.stop()
    connection = store.connect(store.SIMULATION_DATABASE)
    st.warning(
        "Legacy simulated year — no real operator or operational performance is represented."
    )
else:
    connection = state.app_records()
    st.caption(
        "Decisions actually entered in this synthetic-case prototype; never pooled with mock records."
    )

all_decisions = store.load(connection, Decision)
decisions = [d for d in all_decisions if d.office == office]
ids = {d.decision_id for d in decisions}
by_id = {d.decision_id: d for d in decisions}
reviews = [r for r in store.load(connection, Review) if r.decision_id in ids]
requests = [r for r in store.load(connection, ReviewRequest) if r.decision_id in ids]
waiting = audit.pending(requests, reviews)
initials = [
    a
    for a in store.load(connection, InitialAssessment)
    if any(d.case_id == a.case_id and d.caseworker == a.caseworker for d in decisions)
]

overview, quality, time = st.tabs(
    ["Overview and follow-up", "Independent review", "Decision time"]
)
with overview:
    a, b, c = st.columns(3)
    a.metric("Decisions", len(decisions))
    b.metric("Independently reviewed cases", len({r.decision_id for r in reviews}))
    c.metric("Cases awaiting review", len({r.decision_id for r in waiting}))
    st.caption(
        "Random audits and targeted reviews are separate. Small samples and disagreement do not establish operator error."
    )
    stored_alerts = [a for a in store.load(connection, Alert) if a.office == office]
    for alert in stored_alerts:
        with st.container(border=True):
            st.subheader("Follow-up" if alert.closed_at is None else "Closed follow-up")
            st.write(alert.evidence)
            st.caption(f"Owner: {alert.owner}")
            if alert.closed_at:
                st.write(alert.explanation)
            elif source == "app" and alert.owner == owner:
                explanation = st.text_area(
                    "Follow-up explanation", key=f"followup-{alert.alert_id}"
                )
                if st.button(
                    "Close follow-up",
                    key=f"close-{alert.alert_id}",
                    disabled=not explanation.strip(),
                ):
                    store.update(
                        connection,
                        alerts.close(alert, owner, explanation.strip(), state.now()),
                    )
                    st.rerun()
    if not stored_alerts:
        st.info("No stored follow-up for this office.")
    st.caption(
        "No automatic disciplinary action. Existing thresholds remain demonstration values, not operational policy."
    )

with quality:
    st.subheader("Operators compared with the independent commission")
    st.caption(
        "Only the random-audit stream contributes to these rates. A commission disagreement is not an established error; no sanction follows automatically."
    )
    people = metrics.committee_disagreement(decisions, reviews, ["caseworker"])
    if people.empty:
        st.info("No random-audit assessment yet.")
    else:
        people["action"] = people["action"].map(
            {"accepted": "Accepted AI advice", "overridden": "Overrode AI advice"}
        )
        people["disagreement"] = people["rate"].map(lambda x: f"{x:.0%}")
        people["95% interval"] = [
            f"{a:.0%}–{b:.0%}" for a, b in zip(people["ci_low"], people["ci_high"])
        ]
        st.dataframe(
            people[["caseworker", "action", "n", "disagreement", "95% interval"]],
            hide_index=True,
        )
    st.caption(
        "Acceptance/override compare the final human decision with the displayed AI recommendation. They do not, by themselves, establish correctness; the eligibility rule and all records are synthetic demonstration material."
    )
    st.subheader("Targeted cases to inspect")
    rows = [
        {
            "Operator": by_id[r.decision_id].caseworker,
            "Operator decision": by_id[r.decision_id].decision,
            "Commission decision": r.committee_decision,
            "Selection reason": r.reason,
        }
        for r in reviews
        if r.stream == TARGETED
    ]
    if rows:
        st.dataframe(pd.DataFrame(rows), hide_index=True)
    else:
        st.info("No completed targeted review.")
    if initials:
        st.subheader("Human-first: before and after AI")
        compared = []
        for initial in initials:
            final = next(
                d
                for d in decisions
                if d.case_id == initial.case_id and d.caseworker == initial.caseworker
            )
            compared.append(
                {
                    "Operator": final.caseworker,
                    "Initial decision": initial.decision,
                    "Final decision": final.decision,
                    "Changed": initial.decision != final.decision,
                    "Initial justification": initial.justification,
                    "Final justification": final.justification,
                }
            )
        st.dataframe(pd.DataFrame(compared), hide_index=True)
        st.caption(
            "A change after AI is not, on its own, evidence of improvement or bias."
        )
    if source == "app":
        st.subheader("Refer a case for independent review")
        already = {r.decision_id for r in requests if r.stream == TARGETED}
        candidates = [
            d
            for d in reversed(decisions)
            if not is_sentinel(d.case_id) and d.decision_id not in already
        ]
        chosen = st.selectbox(
            "Decision to refer",
            candidates,
            index=None,
            format_func=lambda d: f"{d.caseworker} · {d.decided_at} · {d.decision}",
        )
        reason = st.text_area("Referral reason")
        if st.button("Refer for review", disabled=chosen is None or not reason.strip()):
            store.add(connection, audit.refer(chosen, reason.strip()))
            st.rerun()

with time:
    st.caption(
        "Elapsed time from opening the case to submitting it. Includes pauses; it is not a measurement of attention. Mock times are invented."
    )
    times = metrics.decision_times(decisions, ["caseworker", "variant"])
    if times.empty:
        st.info("No decisions with timestamps.")
    else:
        times["Median minutes"] = (times["median_seconds"] / 60).round(2)
        times["90th percentile minutes"] = (times["p90_seconds"] / 60).round(2)
        st.dataframe(
            times[
                [
                    "caseworker",
                    "variant",
                    "n",
                    "Median minutes",
                    "90th percentile minutes",
                ]
            ],
            hide_index=True,
        )
        st.bar_chart(times, x="caseworker", y="Median minutes", color="variant")
    if initials:
        timing = []
        for initial in initials:
            final = next(
                d
                for d in decisions
                if d.case_id == initial.case_id and d.caseworker == initial.caseworker
            )
            start = datetime.fromisoformat(initial.opened_at)
            first = datetime.fromisoformat(initial.recorded_at)
            end = datetime.fromisoformat(final.decided_at)
            timing.append(
                {
                    "Operator": final.caseworker,
                    "Before AI, minutes": round(
                        (first - start).total_seconds() / 60, 2
                    ),
                    "After initial assessment, minutes": round(
                        (end - first).total_seconds() / 60, 2
                    ),
                }
            )
        st.dataframe(pd.DataFrame(timing), hide_index=True)
        st.caption(
            "The second period includes the interval before selecting AI reveal; it is not precise AI-reading time."
        )

with st.expander("Advanced: engineered cases, demo settings and exports"):
    st.caption(
        "Kept outside the main dashboard to simplify the presentation. Every configured rate and threshold is a demo value, not an operational recommendation."
    )
    pool_table = sentinels.describe_pool(store.load(connection, Sentinel), demo)
    if decisions:
        outcomes = metrics.sentinel_outcomes(decisions, pool_table)
        if not outcomes.empty:
            st.write(
                "Appropriate reliance on engineered cases, relative to the synthetic demo reference, not truth about real household need."
            )
            rates = metrics.reliance(outcomes)
            st.dataframe(rates, hide_index=True)
    settings = [
        {"Section": section, "Parameter": name, "Demo value": str(value)}
        for section, values in dataclasses.asdict(demo).items()
        for name, value in values.items()
    ]
    st.dataframe(pd.DataFrame(settings), hide_index=True)
    if source == "app":
        st.caption(
            "CSV metrics concern this synthetic prototype, not real operational performance. Human-first assessments are supplied separately."
        )
        if st.button("Write legacy CSV exports"):
            paths = export.write_all(
                connection, demo, source, export.EXPORT_DIR / source
            )
            st.success(", ".join(p.name for p in paths))
        if initials:
            st.download_button(
                "Download human-first assessments",
                pd.DataFrame([vars(a) for a in initials]).to_csv(index=False),
                file_name="human-first-assessments.csv",
                mime="text/csv",
            )
