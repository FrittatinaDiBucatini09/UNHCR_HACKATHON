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
st.navigation(
    [
        st.Page("caseworker.py", title="Caseworker", default=True),
        st.Page("committee.py", title="Committee review"),
        st.Page("monitor.py", title="Monitor"),
        st.Page("about.py", title="About"),
    ]
).run()
