"""Demonstration requirements and headless end-to-end screen regressions."""

import sqlite3
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app import presentation, state
from src.data_dictionary import OFFICE_BLANK
from src.dataset import DATA_PATH, load_sample, to_english
from src.sentinella import casework, config, store
from src.sentinella.schema import Decision, InitialAssessment, is_sentinel

ROOT = Path(__file__).resolve().parents[1]
DEMO = config.load()


@pytest.fixture(scope="module")
def context():
    if not DATA_PATH.exists():
        pytest.skip("S8 missing")
    book = casework.casebook(to_english(load_sample()), DEMO)
    staff = casework.roster(
        sorted(set(book.queue["office"]) - {OFFICE_BLANK}),
        DEMO.simulation.caseworkers_per_office,
        DEMO.variants,
    )
    return book, staff


@pytest.fixture
def app_context(context, monkeypatch, tmp_path):
    book, staff = context
    monkeypatch.setattr(state, "book", lambda: book)
    monkeypatch.setattr(state, "staff", lambda: staff)
    monkeypatch.setattr(state, "demo", lambda: DEMO)
    database = tmp_path / "test-app.sqlite"
    monkeypatch.setattr(store, "APP_DATABASE", database)
    return book, staff, database


def select(at, label, value):
    next(w for w in at.selectbox if w.label == label).set_value(value).run()
    assert not at.exception


def test_presentation_has_fifteen_stable_cases_with_correct_positions(context):
    book, staff = context
    queue = presentation.case_list(book, staff.iloc[0]["office"])
    assert len(queue) == 15 and queue["case_id"].is_unique
    assert queue.equals(presentation.case_list(book, staff.iloc[0]["office"]))
    assert is_sentinel(queue.iloc[1]["case_id"])
    assert sum(queue["case_id"].map(is_sentinel)) == 1
    assert queue.iloc[2]["flow"] == "human-first"
    assert (queue.drop(2)["flow"] == "summary-first").all()
    assert "sentinel" not in presentation.case_label(2, False).lower()
    assert presentation.case_label(2, False) == "Case 02"
    assert presentation.case_label(2, True) == "Case 02 ✓"


def test_reasoning_hides_only_eligibility_recommendation():
    text = "Factor score 10. Final score 12, category Low. Under the demo rule, Low is recommended for exclusion."
    visible = presentation.score_only_reasoning(text)
    assert visible == "Factor score 10. Final score 12, category Low."
    assert (
        presentation.score_only_reasoning("Factual claim without a recommendation.")
        == "Factual claim without a recommendation."
    )


def test_initial_assessment_is_persistent_and_cannot_be_duplicated(tmp_path):
    db = store.connect(tmp_path / "initial.sqlite")
    initial = InitialAssessment(
        "initial-1",
        "case-1",
        "operator",
        "Include",
        "Original evidence",
        "2026-10-02T09:00:00+00:00",
        "2026-10-02T09:01:00+00:00",
    )
    store.add(db, initial)
    assert store.load(db, InitialAssessment) == [initial]
    with pytest.raises(sqlite3.IntegrityError):
        store.add(db, initial)
    assert store.load(db, InitialAssessment) == [initial]
    with pytest.raises(ValueError):
        InitialAssessment(
            "initial-2", "case-2", "operator", "Include", " ", "now", "now"
        )


def test_caseworker_submission_and_completed_readonly_view(app_context):
    _, _, database = app_context
    at = AppTest.from_file(ROOT / "app/caseworker.py", default_timeout=30).run()
    assert not at.exception
    assert not at.sidebar.selectbox
    cases = next(w for w in at.main.selectbox if w.label == "Case")
    assert cases.options == [f"Case {n:02d}" for n in range(1, 16)]
    assert len(at.metric) == 0
    select(at, "Cashy-AI assessment", "Show score and explanation")
    assert {m.label for m in at.metric} == {
        "Final score",
        "Vulnerability category",
        "AI recommendation",
    }
    assert next(b for b in at.button if b.label == "Submit decision").disabled
    at.radio[0].set_value(4)
    at.radio[1].set_value(4)
    at.radio[2].set_value("Include")
    at.text_area[0].set_value("Source evidence supports this decision.").run()
    next(b for b in at.button if b.label == "Submit decision").click().run()
    assert not at.exception and len(at.radio) == 0
    assert any("read-only" in s.value for s in at.success)
    assert len(store.load(store.connect(database), Decision)) == 1
    cases = next(w for w in at.main.selectbox if w.label == "Case")
    assert cases.options[0] == "Case 01 ✓"
    assert not any("✓" in label for label in cases.options[1:])


def test_human_first_ai_gate_persistence_and_changed_final_decision(app_context):
    book, staff, database = app_context
    cid = presentation.case_list(book, staff.iloc[0]["office"]).iloc[2]["case_id"]
    at = AppTest.from_file(ROOT / "app/caseworker.py", default_timeout=30).run()
    select(at, "Case", cid)
    assert not any(w.label == "Cashy-AI assessment" for w in at.selectbox)
    assert at.button[0].disabled
    at.radio[0].set_value("Include")
    at.text_area[0].set_value("Independent initial rationale.").run()
    at.button[0].click().run()
    assert not at.exception
    db = store.connect(database)
    initial = store.load(db, InitialAssessment)[0]
    assert initial.decision == "Include"
    assert len(store.load(db, Decision)) == 0
    select(at, "Cashy-AI assessment", "Show score and explanation")
    at.radio[0].set_value(3)
    at.radio[1].set_value(3)
    at.radio[2].set_value("Exclude")
    at.text_area[0].set_value("Final rationale after reviewing the AI output.").run()
    next(b for b in at.button if b.label == "Submit decision").click().run()
    assert not at.exception
    assert store.load(db, InitialAssessment)[0] == initial
    assert store.load(db, Decision)[0].decision == "Exclude"
    assert store.load(db, Decision)[0].variant == "C"


def test_manager_dashboard_restores_streams_and_keeps_sources_apart(
    app_context, monkeypatch, tmp_path
):
    _, _, database = app_context
    simulation = tmp_path / "simulation.sqlite"
    monkeypatch.setattr(store, "SIMULATION_DATABASE", simulation)
    at = AppTest.from_file(ROOT / "app/monitor.py", default_timeout=120).run()
    assert not at.exception
    next(b for b in at.button if b.label == "Generate the simulated year").click()
    at.run()
    assert not at.exception and simulation.exists()
    assert any("Simulated year" in w.value for w in at.warning)
    simulated = store.load(store.connect(simulation), Decision)
    assert at.metric[0].value == f"{len(simulated):,}"
    assert len(at.tabs) == 8
    assert not any(b.label == "Close alert" for b in at.button)
    select(at, "Viewing as", "Office manager, sotap")
    assert any(b.label == "Close alert" for b in at.button)
    at.segmented_control[0].set_value("Entered in the app").run()
    assert not at.exception and at.metric[0].value == "0"
    assert store.load(store.connect(database), Decision) == []


def test_sidebar_links_officer_and_manager_and_folds_the_rest(app_context):
    at = AppTest.from_file(ROOT / "app/streamlit_app.py", default_timeout=30).run()
    assert not at.exception
    links = [link.proto.label for link in at.sidebar.get("page_link")]
    folded = [
        link.proto.label for link in at.sidebar.get("popover")[0].get("page_link")
    ]
    assert links[:2] == ["Officer", "Manager"]
    assert folded == ["Start page", "Committee review", "About and limits"]
    assert links[2:] == folded


def test_role_landing_and_independent_review_render(app_context):
    at = AppTest.from_file(ROOT / "app/streamlit_app.py", default_timeout=30).run()
    assert not at.exception and at.title[0].value == "Sentinella"
    committee = AppTest.from_file(ROOT / "app/committee.py", default_timeout=30).run()
    assert not committee.exception
    assert any("No decisions" in message.value for message in committee.info)
