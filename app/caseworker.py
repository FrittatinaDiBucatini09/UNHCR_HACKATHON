"""Caseworker page: one case at a time, under the caseworker's workflow variant."""

import numpy as np
import streamlit as st

from app import state
from src.sentinella import casework, store
from src.sentinella.config import CATEGORIES
from src.sentinella.schema import RECOMMENDATIONS, Decision, is_sentinel

# Items EC6 and EC5 of the brief's experiment, so that the logged gap between
# the two ratings can be compared with Annex II.
REASONING_ITEM = (
    "Does Cashy-AI provide content that is relevant to help you make an "
    "informed decision?"
)
REASONING_ENDS = ("Strongly disagree", "Strongly agree")
ANSWER_ITEM = "Does Cashy-AI provide a correct and accurate recommendation?"
ANSWER_ENDS = ("Completely inaccurate", "Completely accurate")


def rating(item: str, ends: tuple[str, str], key: str) -> int | None:
    """A rating from 1 to 5 with labelled ends, unset until chosen."""
    labels = {1: f"1 {ends[0]}", 5: f"5 {ends[1]}"}
    return st.radio(
        item,
        [1, 2, 3, 4, 5],
        index=None,
        horizontal=True,
        format_func=lambda value: labels.get(value, str(value)),
        key=key,
    )


demo, book, staff = state.demo(), state.book(), state.staff()
connection = state.app_records()
office_of = dict(zip(staff["caseworker"], staff["office"]))
variant_of = dict(zip(staff["caseworker"], staff["variant"]))

caseworker = st.sidebar.selectbox(
    "Caseworker", staff["caseworker"], format_func=lambda n: f"{n}, {office_of[n]}"
)
variant = variant_of[caseworker]
st.sidebar.caption(f"Screen variant {variant}.")
st.sidebar.caption(
    "Your queue includes sentinels: cases whose reference decision is known in "
    "advance. After deciding one you see its reference decision; nobody else "
    "sees how you decided it."
)

decisions = store.load(connection, Decision)
queue_key, feedback_key = f"queue-{caseworker}", f"feedback-{caseworker}"
if queue_key not in st.session_state:
    st.session_state[queue_key] = casework.caseworker_queue(
        book, staff, caseworker, decisions, demo.sentinels
    )
queue = st.session_state[queue_key]

if feedback_key in st.session_state:
    st.title("Sentinel")
    st.info(st.session_state[feedback_key])
    if st.button("Continue to the next case"):
        del st.session_state[feedback_key]
        st.rerun()
    st.stop()

decided = {d.case_id for d in decisions if d.caseworker == caseworker}
remaining = queue[~queue["case_id"].isin(decided)]
if remaining.empty:
    st.success("No cases left in your queue.")
    st.stop()
case = remaining.iloc[0]
case_id = case["case_id"]
opened_at = st.session_state.setdefault(f"opened-{case_id}", state.now())

st.title(f"Case {len(queue) - len(remaining) + 1} of {len(queue)}")
st.caption(f"Office {case['office']}, interviewed in {case['month']}.")
record = book.records[case_id]
if variant == "A":
    st.subheader("Summary")
    sentences, levels = casework.summary(record)
    st.write(sentences)
    st.dataframe(levels, hide_index=True)
    with st.expander("Complete record"):
        st.dataframe(casework.complete_record(record), hide_index=True)
else:
    st.subheader("Complete record")
    st.dataframe(casework.complete_record(record), hide_index=True)
hint = casework.hint_text(case_id, book)
if hint:
    st.info(hint)

fragile = bool(book.households.at[case_id, "fragile"])
revealed_key, own_key = f"revealed-{case_id}", f"own-{case_id}"
if variant == "A" and not st.session_state.get(revealed_key):
    if casework.asks_judgment_first(variant, fragile, demo.variants):
        own = st.radio(
            "Your category for this household, before Cashy's answer",
            CATEGORIES,
            index=None,
            horizontal=True,
        )
        if st.button(
            "Record my category and show Cashy's reasoning and answer",
            disabled=own is None,
        ):
            st.session_state[own_key] = own
            st.session_state[revealed_key] = True
            st.rerun()
    elif st.button("Show Cashy's reasoning and answer"):
        st.session_state[revealed_key] = True
        st.rerun()
    st.stop()

shown = casework.display(case_id, book, demo.simulation)
st.subheader("Cashy's reasoning")
with st.container(border=True):
    st.write(shown.reasoning)
reasoning_rating = rating(REASONING_ITEM, REASONING_ENDS, f"reasoning-{case_id}")

st.subheader("Cashy's answer")
with st.container(border=True):
    score, category, recommendation = st.columns(3)
    score.metric("Final score", f"{shown.shown_score:.1f}")
    category.metric("Vulnerability category", shown.shown_category)
    recommendation.metric("Recommendation, demo rule", shown.shown_recommendation)
    included = [c for c in CATEGORIES if c in demo.demo_rule.include]
    st.caption(
        "Recommendation under the demo rule, not the operation's: "
        f"{' and '.join(included)} are recommended for inclusion. Category "
        "bands of the final score:"
    )
    st.dataframe(
        casework.category_bands(),
        hide_index=True,
        column_config={
            "From": st.column_config.NumberColumn(format="%.2f"),
            "To": st.column_config.NumberColumn(format="%.2f"),
        },
    )
answer_rating = rating(ANSWER_ITEM, ANSWER_ENDS, f"answer-{case_id}")

st.subheader("Your decision")
choice = st.radio(
    "Decision", RECOMMENDATIONS, index=None, horizontal=True, key=f"decision-{case_id}"
)
st.caption(
    "Write the reasons for the household: they may be shared with them if the "
    "decision is questioned."
)
justification = st.text_area("Justification", key=f"justification-{case_id}")
complete = None not in (reasoning_rating, answer_rating, choice)
if st.button(
    "Submit decision", type="primary", disabled=not (complete and justification.strip())
):
    decided_at = state.now()
    decision = Decision(
        decision_id=f"decision-{len(decisions) + 1:07d}",
        case_id=case_id,
        caseworker=caseworker,
        office=office_of[caseworker],
        month=decided_at[:7],
        variant=variant,
        shown_score=shown.shown_score,
        shown_category=shown.shown_category,
        shown_recommendation=shown.shown_recommendation,
        reasoning_rating=reasoning_rating,
        answer_rating=answer_rating,
        own_category=st.session_state.get(own_key),
        hint_factors=casework.hint_factors(case_id, book),
        decision=choice,
        justification=justification.strip(),
        opened_at=opened_at,
        decided_at=decided_at,
        simulated=False,
    )
    requests = casework.review_requests(decision, book, demo, np.random.default_rng())
    store.add(connection, decision, *requests)
    if is_sentinel(case_id):
        st.session_state[feedback_key] = casework.feedback(book.pool[case_id])
    st.rerun()
