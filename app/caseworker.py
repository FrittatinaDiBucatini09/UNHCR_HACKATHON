"""Single-operator, fifteen-case demonstration workflow."""

from uuid import uuid4

import numpy as np
import streamlit as st

from app import presentation, state
from app.session_keys import case_key
from src.sentinella import casework, store
from src.sentinella.schema import (
    RECOMMENDATIONS,
    Decision,
    InitialAssessment,
    is_sentinel,
)


def rating(item: str, key: str) -> int | None:
    return st.radio(
        item,
        [1, 2, 3, 4, 5],
        index=None,
        horizontal=True,
        key=key,
        format_func=lambda n: {1: "1 — Strongly disagree", 5: "5 — Strongly agree"}.get(
            n, str(n)
        ),
    )


demo, book, staff = state.demo(), state.book(), state.staff()
connection = state.app_records()
# A presentation identity, not a login or an operational staffing choice.
person = staff.iloc[0]
caseworker, office = person["caseworker"], person["office"]
queue = presentation.case_list(book, office)
decisions = store.load(connection, Decision)
mine = {d.case_id: d for d in decisions if d.caseworker == caseworker}
by_id = queue.set_index("case_id")
st.sidebar.caption("One demonstration operator · 15 cases")
case_id = st.sidebar.selectbox(
    "Case",
    queue["case_id"].tolist(),
    key="selected_case",
    format_func=lambda cid: presentation.case_label(
        int(by_id.at[cid, "number"]), cid in mine
    ),
)
case = by_id.loc[case_id]
number = int(case["number"])
human_first = case["flow"] == "human-first"
variant = "C" if human_first else "A"
st.title(f"Case {number:02d}")
st.caption(
    f"Office {office} · interview month {case['month']} · synthetic demonstration data"
)
st.progress(
    len(mine.keys() & set(queue["case_id"])) / len(queue),
    text="Completed demonstration cases",
)

record = book.records[case_id]
st.subheader("Household summary")
sentences, levels = casework.summary(record)
st.write(sentences)
st.dataframe(levels, hide_index=True, width="stretch")
with st.expander("Open complete available record"):
    st.caption(
        "Available household attributes and factor scores; not the complete operational questionnaire."
    )
    st.dataframe(casework.complete_record(record), hide_index=True, width="stretch")
checks = presentation.checks(case_id, book)
if not checks.empty:
    st.subheader("Factors to verify")
    st.dataframe(checks, hide_index=True, width="stretch")
    st.caption(
        "Local one-level sensitivity of the demo score/category, not validated eligibility checks or global feature importance."
    )

shown = casework.display(case_id, book, demo.simulation)
initial = next(
    (
        a
        for a in store.load(connection, InitialAssessment)
        if a.case_id == case_id and a.caseworker == caseworker
    ),
    None,
)
opened_at = (
    initial.opened_at
    if initial
    else st.session_state.setdefault(
        case_key(caseworker, case_id, "opened"), state.now()
    )
)

if case_id in mine:
    saved = mine[case_id]
    st.success("Completed — this decision is read-only.")
    if initial:
        st.write(f"Initial decision: {initial.decision}")
        st.write(initial.justification)
    st.write(f"Final decision: {saved.decision}")
    st.write(saved.justification)
    st.caption(f"Recorded {saved.decided_at}")
    if is_sentinel(case_id):
        st.info(casework.feedback(book.pool[case_id]))
    st.stop()

if human_first and initial is None:
    st.subheader("Your assessment before AI")
    st.caption(
        "Case 03 demonstrates the human-first alternative. Record your decision and reasons before viewing AI advice."
    )
    preliminary = st.radio(
        "Initial decision",
        RECOMMENDATIONS,
        index=None,
        horizontal=True,
        key=case_key(caseworker, case_id, "initial_decision"),
    )
    reason = st.text_area(
        "Initial justification",
        key=case_key(caseworker, case_id, "initial_justification"),
    )
    if st.button(
        "Save initial assessment and unlock AI",
        type="primary",
        disabled=preliminary is None or not reason.strip(),
    ):
        store.add(
            connection,
            InitialAssessment(
                assessment_id=f"initial-{uuid4().hex}",
                case_id=case_id,
                caseworker=caseworker,
                decision=preliminary,
                justification=reason.strip(),
                opened_at=opened_at,
                recorded_at=state.now(),
            ),
        )
        st.rerun()
    st.stop()

if initial:
    st.info(
        f"Your initial decision: {initial.decision}. It is saved and cannot be overwritten."
    )
    with st.expander("Read your initial justification"):
        st.write(initial.justification)

reveal = st.selectbox(
    "Cashy-AI assessment",
    ["Keep hidden", "Show score and explanation"],
    key=case_key(caseworker, case_id, "revealed"),
)
if reveal == "Keep hidden":
    st.caption("Open the AI assessment when ready, then record your final decision.")
    st.stop()
st.subheader("AI assessment")
score, category, recommendation = st.columns(3)
score.metric("Final score", f"{shown.shown_score:.1f}")
category.metric("Vulnerability category", shown.shown_category)
recommendation.metric("AI recommendation", shown.shown_recommendation)
st.caption(
    "Include/Exclude follows the prototype's demo rule, not verified operational eligibility."
)
with st.container(border=True):
    st.write(shown.reasoning)
with st.expander("Score/category bands — demo formula"):
    st.dataframe(casework.category_bands(), hide_index=True)

reasoning_rating = rating(
    "Is the AI explanation relevant to your assessment?",
    case_key(caseworker, case_id, "reasoning"),
)
answer_rating = rating(
    "Are the AI score, vulnerability category and recommendation accurate?",
    case_key(caseworker, case_id, "answer"),
)
st.caption(
    "Ratings: 1 = strongly disagree, 5 = strongly agree. Ratings are not proof of correct reliance."
)
st.subheader("Your final decision")
if initial:
    st.caption(
        "Confirm your initial decision or change it after inspecting the AI assessment."
    )
choice = st.radio(
    "Decision",
    RECOMMENDATIONS,
    index=None,
    horizontal=True,
    key=case_key(caseworker, case_id, "decision"),
)
st.caption(
    "Give a justification suitable for sharing with the household if the decision is questioned."
)
justification = st.text_area(
    "Justification", key=case_key(caseworker, case_id, "justification")
)
complete = None not in (reasoning_rating, answer_rating, choice)
if st.button(
    "Submit decision", type="primary", disabled=not (complete and justification.strip())
):
    decided_at = state.now()
    decision = Decision(
        decision_id=f"decision-{uuid4().hex}",
        case_id=case_id,
        caseworker=caseworker,
        office=office,
        month=decided_at[:7],
        variant=variant,
        shown_score=shown.shown_score,
        shown_category=shown.shown_category,
        # The recommendation was revealed before the final human decision.
        shown_recommendation=shown.shown_recommendation,
        reasoning_rating=reasoning_rating,
        answer_rating=answer_rating,
        own_category=None,
        hint_factors=casework.hint_factors(case_id, book),
        decision=choice,
        justification=justification.strip(),
        opened_at=opened_at,
        decided_at=decided_at,
        simulated=False,
    )
    requests = casework.review_requests(decision, book, demo, np.random.default_rng())
    store.add(connection, decision, *requests)
    st.rerun()
