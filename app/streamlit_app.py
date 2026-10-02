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

from app import brand

st.set_page_config(page_title="Sentinella", page_icon=str(brand.EMBLEM), layout="wide")
st.logo(str(brand.LOGO), icon_image=str(brand.EMBLEM), size="large")

officer = st.Page("caseworker.py", title="Officer", icon=":material/assignment_ind:")
manager = st.Page("monitor.py", title="Manager", icon=":material/monitoring:")
secondary = [
    st.Page("home.py", title="Start page", icon=":material/home:", default=True),
    st.Page("committee.py", title="Committee review", icon=":material/fact_check:"),
    st.Page("about.py", title="About and limits", icon=":material/info:"),
]
page = st.navigation([officer, manager, *secondary], position="hidden")

# The two workspaces stay one click away; everything else sits in one dropdown.
with st.sidebar:
    st.page_link(officer)
    st.page_link(manager)
    with st.popover("More", icon=":material/menu:", width="stretch"):
        for item in secondary:
            st.page_link(item)
    st.caption(brand.NOTICE)
page.run()
