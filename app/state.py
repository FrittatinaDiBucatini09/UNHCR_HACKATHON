"""Configuration, cases and databases shared by the pages."""

import sqlite3
from datetime import UTC, datetime

import pandas as pd
import streamlit as st

from src.data_dictionary import OFFICE_BLANK
from src.dataset import DATA_PATH, REPO_ROOT, load_sample, to_english
from src.sentinella import casework, store
from src.sentinella.config import Config, load
from src.sentinella.schema import Sentinel


def now() -> str:
    """The current UTC time as an ISO 8601 string, to the second."""
    return datetime.now(UTC).isoformat(timespec="seconds")


@st.cache_resource
def demo() -> Config:
    """The demo configuration."""
    return load()


@st.cache_resource
def book() -> casework.Casebook:
    """Sentinel pool and real cases drawn from S8."""
    if not DATA_PATH.exists():
        st.error("The S8 data file is missing; data/README.md says where to put it.")
        st.stop()
    return casework.casebook(to_english(load_sample()), demo())


@st.cache_resource
def staff() -> pd.DataFrame:
    """Pseudonymous caseworkers with their offices and variants."""
    offices = sorted(set(book().queue["office"]) - {OFFICE_BLANK})
    return casework.roster(
        offices, demo().simulation.caseworkers_per_office, demo().variants
    )


def app_records() -> sqlite3.Connection:
    """The app's database, with the sentinel pool stored on first use.

    Stops the page if the database holds a pool drawn under another
    configuration, since its decisions would no longer match the sentinels.
    """
    connection = store.connect(store.APP_DATABASE)
    pool = list(book().pool.values())
    stored = store.load(connection, Sentinel)
    if not stored:
        store.add(connection, *pool)
    elif stored != pool:
        st.error(
            f"{store.APP_DATABASE.relative_to(REPO_ROOT)} holds sentinels drawn "
            "under another configuration. Delete it to start again."
        )
        st.stop()
    return connection
