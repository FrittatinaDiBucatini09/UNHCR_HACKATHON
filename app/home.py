"""Role-oriented landing page for the hackathon prototype."""

import streamlit as st

st.title("Sentinella")
st.subheader("Human oversight, one case at a time")
st.write(
    "Choose your workspace. This is a hackathon prototype, not an operational UNHCR service."
)
operator, manager = st.columns(2)
with operator.container(border=True):
    st.subheader("Caseworker")
    st.write(
        "Review 15 demonstration cases, inspect the record and record a justified decision."
    )
    st.page_link(
        "caseworker.py", label="Open caseworker workspace", icon=":material/assignment:"
    )
with manager.container(border=True):
    st.subheader("Manager")
    st.write(
        "Compare independent reviews, inspect decision time and refer cases for review."
    )
    st.page_link(
        "monitor.py", label="Open manager dashboard", icon=":material/monitoring:"
    )
st.caption("Independent committee review remains a separate, AI-blind workspace.")
st.page_link(
    "committee.py", label="Open independent review", icon=":material/fact_check:"
)
