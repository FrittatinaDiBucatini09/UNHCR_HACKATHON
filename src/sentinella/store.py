"""SQLite persistence of the log records."""

import json
import sqlite3
from dataclasses import fields
from pathlib import Path
from types import NoneType, UnionType
from typing import get_args, get_origin, get_type_hints

from src.dataset import REPO_ROOT
from src.sentinella.schema import (
    CASE_PREFIX,
    SENTINEL_PREFIX,
    Alert,
    Decision,
    Review,
    ReviewRequest,
    Sentinel,
)

# Records entered in the app, and the simulated year shown beside them; kept in
# separate files so that simulated and entered records are never pooled.
APP_DATABASE = REPO_ROOT / "data" / "sentinella.sqlite"
SIMULATION_DATABASE = REPO_ROOT / "data" / "simulation.sqlite"

Record = Decision | Review | ReviewRequest | Sentinel | Alert
TABLES = {
    Decision: "decisions",
    Review: "reviews",
    ReviewRequest: "review_requests",
    Sentinel: "sentinels",
    Alert: "alerts",
}

# The ID checks repeat the schema's namespaces so that the database itself
# refuses a sentinel ID outside its namespace, whatever code writes to it.
SCHEMA = f"""
CREATE TABLE IF NOT EXISTS decisions (
    decision_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL
        CHECK (case_id GLOB '{CASE_PREFIX}*' OR case_id GLOB '{SENTINEL_PREFIX}*'),
    caseworker TEXT NOT NULL,
    office TEXT NOT NULL,
    month TEXT NOT NULL,
    variant TEXT NOT NULL,
    shown_score REAL NOT NULL,
    shown_category TEXT NOT NULL,
    shown_recommendation TEXT NOT NULL,
    reasoning_rating INTEGER,
    answer_rating INTEGER,
    own_category TEXT,
    hint_factors TEXT,
    decision TEXT NOT NULL,
    justification TEXT,
    opened_at TEXT,
    decided_at TEXT,
    simulated INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS reviews (
    review_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES decisions (decision_id),
    stream TEXT NOT NULL,
    reason TEXT NOT NULL,
    votes TEXT NOT NULL,
    committee_decision TEXT NOT NULL,
    reviewed_at TEXT,
    simulated INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS review_requests (
    decision_id TEXT NOT NULL REFERENCES decisions (decision_id),
    stream TEXT NOT NULL,
    reason TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sentinels (
    sentinel_id TEXT PRIMARY KEY CHECK (sentinel_id GLOB '{SENTINEL_PREFIX}*'),
    record TEXT NOT NULL,
    shown_factors TEXT NOT NULL,
    shown_score REAL NOT NULL,
    shown_category TEXT NOT NULL,
    shown_recommendation TEXT NOT NULL,
    reasoning TEXT NOT NULL,
    reference_decision TEXT NOT NULL,
    discordance_type TEXT,
    altered_factor TEXT,
    fragile INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS alerts (
    alert_id TEXT PRIMARY KEY,
    office TEXT NOT NULL,
    rule TEXT NOT NULL,
    evidence TEXT NOT NULL,
    opened_at TEXT NOT NULL,
    owner TEXT NOT NULL,
    explanation TEXT,
    closed_by TEXT,
    closed_at TEXT
);
"""


def connect(path: str | Path) -> sqlite3.Connection:
    """Open the log database, creating its tables if they are missing.

    Args:
        path: Database file, or ":memory:" for a database held in memory.
    """
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection


def add(connection: sqlite3.Connection, *records: Record) -> None:
    """Insert records of any type in one transaction."""
    with connection:
        for record in records:
            insert(connection, TABLES[type(record)], to_row(record))


def insert(connection: sqlite3.Connection, table: str, row: dict) -> None:
    """Insert one row, given as a mapping of column names to values."""
    columns = ", ".join(row)
    placeholders = ", ".join(f":{column}" for column in row)
    connection.execute(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", row)


def update(connection: sqlite3.Connection, record: Decision | Review | Alert) -> None:
    """Overwrite a stored record, found by its ID, the record's first field.

    Raises:
        KeyError: If no stored record has that ID.
    """
    row = to_row(record)
    key = fields(record)[0].name
    assignments = ", ".join(f"{column} = :{column}" for column in row if column != key)
    with connection:
        cursor = connection.execute(
            f"UPDATE {TABLES[type(record)]} SET {assignments} WHERE {key} = :{key}", row
        )
    if cursor.rowcount != 1:
        raise KeyError(f"no stored record with {key} {row[key]!r}")


def load(connection: sqlite3.Connection, record_type: type[Record]) -> list[Record]:
    """All records of one type, in the order they were added."""
    cursor = connection.execute(f"SELECT * FROM {TABLES[record_type]} ORDER BY rowid")
    columns = [description[0] for description in cursor.description]
    return [from_row(record_type, dict(zip(columns, values))) for values in cursor]


def to_row(record: Record) -> dict:
    """Column values of a record; dicts and tuples are stored as JSON text."""
    row = {}
    for field in fields(record):
        value = getattr(record, field.name)
        row[field.name] = (
            json.dumps(value) if isinstance(value, (dict, tuple)) else value
        )
    return row


def from_row(record_type: type[Record], row: dict) -> Record:
    """Record rebuilt from its column values, decoded by field type."""
    types = get_type_hints(record_type)
    return record_type(
        **{name: decode(value, types[name]) for name, value in row.items()}
    )


def decode(value: object, hint: object) -> object:
    """A column value as the field's type expects; NULL stays None."""
    if value is None:
        return None
    if get_origin(hint) is UnionType:
        hint = next(arg for arg in get_args(hint) if arg is not NoneType)
    if hint is bool:
        return bool(value)
    if get_origin(hint) is dict:
        return json.loads(value)
    if get_origin(hint) is tuple:
        return tuple(json.loads(value))
    return value
