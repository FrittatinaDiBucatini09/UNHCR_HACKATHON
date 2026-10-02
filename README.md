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

## Running the prototype

The prototype needs the S8 file in `data/`. Run from the repository root; on
Windows, replace `.venv/bin/python` with `.venv\Scripts\python`.

```
# A simulated year of seven offices for the Monitor page, in a few seconds
.venv/bin/python -m src.sentinella.simulate history

# The app, served at http://localhost:8501
.venv/bin/python -m streamlit run app/streamlit_app.py
```

The app has four pages:

- **Caseworker:** one case at a time, under the caseworker's workflow variant.
- **Committee review:** blind votes on the decisions selected for review.
- **Monitor:** the three streams, the alert queue, decision time and the
  exports. It covers either the simulated year or the decisions entered in the
  app.
- **About:** what the data supports and what it does not.

Decisions entered in the app are kept in `data/sentinella.sqlite` and the
simulated year in `data/simulation.sqlite`. Both files are local and ignored by
git, and the two are never pooled. Delete a file to start it again.

Two more commands:

```
# Detection delay and false alarms of the alert rule, over 200 simulated
# years per scenario, in about four minutes
.venv/bin/python -m src.sentinella.simulate detection

# Tidy CSV tables for Power BI or another BI tool, written to
# data/exports/<source>/ with schema.csv describing every column
.venv/bin/python -m src.sentinella.export simulation
.venv/bin/python -m src.sentinella.export app
```

Every parameter, from the sentinel rate to the alert rule, is in
`config/demo.toml`. Each carries a comment, because they are demo values chosen
to run the prototype on S8, not recommendations for a real operation.

## What each stream measures

The prototype keeps three measurement streams apart, in the records and in
every estimate.

**Random audit.** A random 10% of decisions on real cases, accepted and
overridden alike, goes to a committee of three. The committee sees the
household's record, not Cashy's answer or the caseworker's decision. The audit
estimates how often caseworkers' decisions disagree with the committee on real
cases, separately for accepted and overridden decisions. It does not establish
errors, since the committee can be wrong. Under the demo values a caseworker
has about 50 audited decisions a year, so comparisons of individuals have wide
intervals.

**Targeted reviews.** Some decisions go to the same blind review because they
look risky: those where Cashy recommended exclusion on a case one factor level
away from inclusion, and any decision a manager refers with a written reason.
They find individual cases to correct. Because they are chosen for risk, they
never enter a rate.

**Sentinels.** One decision in ten is on a sentinel: a household from S8 kept
out of the real queue. Its reference decision is the demo rule applied to the
formula category of its record. Cashy's displayed answer is either concordant
with that reference or discordant in one of three ways a caseworker can see on
screen:

- a misread input;
- a category that does not match the score;
- reasoning that does not match the answer.

Sentinels give correct override, over-reliance, correct acceptance and
under-reliance, relative to the reference standard, every month. They measure
how caseworkers treat cases built to test them. They do not show that real
cases get the same treatment; comparing them with the random audit checks
that. Staff know that sentinels exist. Only the caseworker who decided a
sentinel sees its reference decision afterwards, and a sentinel never reaches
the committee or the distribution list.

Each office's correct override on discordant sentinels is checked over four
months. An alert opens when the upper end of its 95% interval falls below
87.5%, provided the window holds at least five decisions. Only the office
manager can close the alert, and only with a written explanation.

In the simulation, under the demo values, correct override in one office fell
from 96.2% to 66.7%, the brief's two experiment arms. The alert caught the fall
in 181 of 200 simulated years (90.5%, 95% CI 85.6 to 93.8), a median of two
months after the change. In the control scenario, 5 of 200 simulated years
raised a false alarm (2.5%, 95% CI 1.1 to 5.7). `simulate detection` prints
these numbers. They describe the simulation, not a real operation.

The caseworker screen adds two aids:

- **Fragility hint:** names the factors whose one-level change would change the
  category, so that the caseworker checks them against the record.
- **Judgment first:** asks for the caseworker's own category before Cashy's
  answer.

Each office's caseworkers are split at random between two workflow variants.
Variant A shows a summary of the record first, asks for the caseworker's own
category on fragile cases, and then shows Cashy's reasoning and answer.
Variant B shows the complete record with Cashy's reasoning and answer from the
start. Both show the hint, and in both the caseworker rates the reasoning and
the answer separately. The Monitor shows recorded decision time for decisions
entered in the app. Recorded time is not attention.

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
app/        Sentinella prototype: Streamlit pages
config/     Demo configuration of the prototype
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
