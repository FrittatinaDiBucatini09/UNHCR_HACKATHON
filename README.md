# Sentinella

Sentinella is our entry to the Cashy Oversight Challenge, a 48-hour hackathon
run by the University of Trento and UNHCR Innovation. UNHCR targets cash
assistance to displaced households with an expert-designed Scorecard; Cashy, an
AI prototype, predicts the Scorecard result and recommends include or exclude,
and a caseworker makes the decision. Sentinella measures whether caseworkers
keep overriding Cashy when its recommendation is wrong, so that the operation
can see when they stop.

The data science part of the project explores the synthetic sample and then
builds a model that reproduces the Scorecard final score, with a per-case
explanation of which factors drive it. That model powers the prototype's
"Answer" panel.

The challenge brief, including the data dictionary, the judging criteria and
the reference results of the earlier caseworker experiment, is in
[docs/challenge_website.md](docs/challenge_website.md).

## Data

All work uses the S8 synthetic sample released for the challenge: 1,900
synthetic households, 26 columns, no real household. The file is not tracked
in git. [data/README.md](data/README.md) explains where to put it and how to
check it is the right file.

## Setup

Python 3.12, CPU only. From the repository root:

```
# macOS
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt

# Windows (PowerShell)
py -3.12 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

On macOS, LightGBM also needs the OpenMP runtime: `brew install libomp`.

## Running

Notebooks are executed headless so that their outputs are saved in the file.
Every notebook resolves paths from the repository root, fixes its random seeds
and must run top to bottom on a fresh kernel.

```
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/01_data_exploration.ipynb
.venv/bin/jupyter nbconvert --to notebook --execute --inplace notebooks/02_score_model.ipynb
```

The first notebook writes the exploration report's tables and figures, the
second those of the score model; the reports are
[reports/01_data_exploration.md](reports/01_data_exploration.md) and
[reports/02_score_model.md](reports/02_score_model.md).

Tests and style checks:

```
.venv/bin/python -m pytest
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```

On Windows, replace `.venv/bin/` with `.venv\Scripts\`.

## Score model

The Answer panel uses the Scorecard formula recovered in phase 1. It needs no
training and no data file. Given the eight factor scores of a household,
`predict` returns the final score, the vulnerability category and how many
points each factor contributes:

```python
from src.score_model import predict

result = predict(
    {
        "Demographics.HH.Head": 2.70,
        "Demographics.Language": 1.0,
        "Demographics.Profiles": 1.0,
        "Demographics.Documentation": 1.0,
        "Needs_and_Coping.BasicNeeds": 1.78,
        "Needs_and_Coping.Housing": 2.12,
        "Needs_and_Coping.Neg.mechanism": 1.79,
        "Needs_and_Coping.Dependency": 1.0,
    }
)
# result["score"] 30.96, result["category"] "Moderate", result["attributions"]
```

What the model can and cannot be used for is in the
[model card](reports/model_card.md).

## Repository layout

```
app/        Sentinella prototype
data/       Synthetic sample (not tracked) and its README
docs/       Challenge brief
notebooks/  Analyses, numbered in the order they run
reports/    Written reports and model card, with figures/ (PNG) and tables/ (CSV)
src/        Python code imported by the notebooks, tests and app
tests/      Unit tests
```

## Ground rules

These come from the challenge brief and apply to every analysis here.

- Results describe the synthetic sample, not the real operation.
- No attempt is made to re-identify, link or reconstruct households,
  caseworkers or offices.
- Eligibility is not benchmarked on this sample, and no result is compared
  with the 67.6% accuracy reported for Cashy on real data.
- "Correct" means agreement with the operation's recorded determination. That
  is the institution's standard, not the truth about a household's need.
- Breakdowns by office, month or category report the group size, and groups
  with fewer than 30 households are flagged as unreliable.
