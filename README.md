# Sentinella

A Streamlit prototype for human oversight of AI-assisted cash-assistance
assessment. It uses the synthetic S8 dataset released for the
[Cashy Oversight Challenge](https://maldonam.github.io/public/).

## Setup and launch

Use Python 3.12. Run these commands from the repository root.

Windows (PowerShell):

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app/streamlit_app.py
```

macOS / Linux:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app/streamlit_app.py
```

Before reviewing cases, place the unchanged S8 CSV at
`data/S8.synthetic_cashy_sample.csv`; see [data instructions](data/README.md).
The CSV and generated databases are intentionally not distributed in Git.
No analysis notebook or model-training run is needed to launch the application.

## Workspaces

- **Caseworker:** one demonstration identity and 15 selectable cases, marked
  pending or completed. Review a deterministic household summary and the
  available source record, then open the AI assessment when ready. AI shows
  score, vulnerability category, explanation and an Include/Exclude
  recommendation. The final human decision requires a written justification.
- **Case 02:** an engineered sentinel with post-decision reference feedback.
- **Case 03:** a human-first example. Initial decision and justification must
  be saved before AI is unlocked. A separate final decision may confirm or
  change the initial judgment; neither overwrites the initial assessment.
- **Manager:** overview/follow-up, independent reviews and elapsed decision
  time. Clearly labelled illustrative mock records, app-entered decisions and
  optional legacy simulation are separate sources and are never pooled.
  Managers can manually refer non-sentinel decisions for independent review.
- **Independent review:** reviewers see available case evidence without AI
  advice, the first operator's decision or justification, or selection reason.

Technical settings and exports are collapsed in the dashboard. SQLite logs
are created locally in `data/`; a new table preserves human-first assessments
without deleting existing decisions. Mock dashboard records are ephemeral.

## Tests

Install `requirements-dev.txt` in the same environment, then run:

```sh
python -m pytest -q
python -m ruff check app src tests
```

Tests that need S8 skip when it is absent. To verify the complete workflow,
provide the released CSV before running the suite.

## Interpretation and limits

This is an unofficial hackathon prototype, not an operational UNHCR service.
Role navigation is not production authentication or authorization.
The available record is not the complete operational questionnaire.
Score sensitivity hints are demo aids, not a validated eligibility checklist.

Acceptance/override compare a human decision with AI advice actually shown;
neither alone proves correctness. Sentinel correctness is relative to a
synthetic demo reference. Commission disagreement is not an established error.
Elapsed time includes interruptions and is not a measurement of attention.
Mock timings and decisions are invented examples, not measured performance.

Audit proportions, reviewer counts and thresholds are demonstration settings,
not operational recommendations. No automatic disciplinary policy is adopted.
The project does not demonstrate improved reliance or sustained attention
without an appropriate independent evaluation.
