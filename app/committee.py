"""Committee review page: blind review of the decisions selected for review."""

import streamlit as st

from app import state
from src.sentinella import audit, casework, store
from src.sentinella.schema import (
    RECOMMENDATIONS,
    RECORD_FIELDS,
    Decision,
    Review,
    ReviewRequest,
)

demo, book = state.demo(), state.book()
connection = state.app_records()
decisions = {d.decision_id: d for d in store.load(connection, Decision)}
reviews = store.load(connection, Review)
waiting = audit.pending(store.load(connection, ReviewRequest), reviews)

st.title("Committee review", icon=":material/fact_check:")
st.caption(
    "Each member votes on the household's record alone. Cashy's answer, the "
    "caseworker's decision and justification, and the reason the case was "
    "selected are not shown."
)
if not waiting:
    st.info("No decisions are waiting for review.")
    st.stop()

decision_ids = list(dict.fromkeys(request.decision_id for request in waiting))
decision = decisions[decision_ids[0]]
view = audit.reviewer_view(decision, book.records[decision.case_id])
st.subheader(f"Review 1 of {len(decision_ids)}")
st.caption(f"Office {view['office']}, decided in {view['month']}.")
record = {field: view[field] for field in RECORD_FIELDS}
st.dataframe(casework.complete_record(record), hide_index=True)

votes = [
    st.radio(
        f"Member {member}",
        RECOMMENDATIONS,
        index=None,
        horizontal=True,
        key=f"vote-{decision.decision_id}-{member}",
    )
    for member in range(1, demo.committee.size + 1)
]
if st.button("Record the committee's decision", type="primary", disabled=None in votes):
    outcome = audit.committee_decision(tuple(votes), demo.committee)
    reviewed_at = state.now()
    # One vote answers every stream that selected the decision; each stream
    # keeps its own review record.
    answered = [r for r in waiting if r.decision_id == decision.decision_id]
    store.add(
        connection,
        *[
            Review(
                review_id=f"review-{len(reviews) + number:06d}",
                decision_id=decision.decision_id,
                stream=request.stream,
                reason=request.reason,
                votes=tuple(votes),
                committee_decision=outcome,
                reviewed_at=reviewed_at,
                simulated=False,
            )
            for number, request in enumerate(answered, start=1)
        ],
    )
    st.rerun()
