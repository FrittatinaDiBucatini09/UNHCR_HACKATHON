"""Sentinella prototype: entry point of the Streamlit app.

Run from the repository root:

    python -m streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

import streamlit as st

# The pages import src and app as packages of the repository root.
ROOT = str(Path(__file__).resolve().parents[1])
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

st.set_page_config(page_title="Sentinella", layout="wide")
st.sidebar.markdown("### Sentinella")
st.sidebar.caption("UNHCR challenge · unofficial hackathon prototype")
st.navigation(
    {
        "Start": [st.Page("home.py", title="Choose your workspace", default=True)],
        "Caseworker": [st.Page("caseworker.py", title="Review cases")],
        "Manager": [st.Page("monitor.py", title="Dashboard")],
        "Independent review": [st.Page("committee.py", title="Committee review")],
        "Prototype": [st.Page("about.py", title="About and limits")],
    }
).run()
