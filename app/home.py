"""Role-oriented landing page for the hackathon prototype."""

import streamlit as st

from app import brand

st.image(str(brand.LOGO), width=280)
st.title("Sentinella")
st.subheader("Human oversight, one case at a time")
st.caption(brand.NOTICE)
officer, manager = st.columns(2)
with officer.container(border=True):
    st.subheader("Officer", icon=":material/assignment_ind:")
    st.write(
        "Review 15 demonstration cases, check the record against the AI "
        "assessment and record a justified decision."
    )
    st.page_link(
        "caseworker.py",
        label="Open the officer workspace",
        icon=":material/arrow_forward:",
    )
with manager.container(border=True):
    st.subheader("Manager", icon=":material/monitoring:")
    st.write(
        "Follow sentinels, the random audit and targeted reviews, close alerts "
        "with an explanation and refer cases for blind review."
    )
    st.page_link(
        "monitor.py",
        label="Open the manager dashboard",
        icon=":material/arrow_forward:",
    )
st.caption("Independent committee review remains a separate, AI-blind workspace.")
st.page_link(
    "committee.py", label="Open committee review", icon=":material/fact_check:"
)
