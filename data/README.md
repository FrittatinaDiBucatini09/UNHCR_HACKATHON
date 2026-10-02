<p align="right"><img src="../docs/images/unhcr_emblem.png" alt="UNHCR emblem" width="56"></p>

# Data

This folder holds the S8 synthetic sample released for the Cashy Oversight Challenge and the
local files the prototype writes. Everything in it except this README is kept out of git by
`.gitignore`.

> [!WARNING]
> Do not commit the sample, the databases, the exports or copies of any of them.

## ⬇️ Getting the sample

Download "S8 synthetic sample (CSV, 1,900 rows)" from the Data section of the
[challenge page](https://maldonam.github.io/public/) and save it in this folder without
renaming or editing it:

```
data/S8.synthetic_cashy_sample.csv
```

The code reads it from that path, resolved from the repository root. To check that you have
the same file the analyses were run on:

| Property | Expected value |
| :--- | :--- |
| Rows | 1,900, plus a header row |
| Columns | 26 |
| Size | 471,761 bytes |
| SHA-256 | `a9f009737a034c4756003a477365c5dbcdddb96562f329fd4c56c26281fe71c1` |

```
# macOS
shasum -a 256 data/S8.synthetic_cashy_sample.csv

# Windows (PowerShell)
Get-FileHash data\S8.synthetic_cashy_sample.csv -Algorithm SHA256
```

## 🗄️ Files the prototype writes

| File | Written by | Content |
| :--- | :--- | :--- |
| `sentinella.sqlite` | The app, on first use | Decisions entered in the app, human-first initial assessments, review requests, committee reviews, alerts and the sentinel pool |
| `simulation.sqlite` | The dashboard's Generate button, or `python -m src.sentinella.simulate history` | A simulated year of seven offices |
| `exports/<source>/` | The dashboard's Exports tab, or `python -m src.sentinella.export <source>` | CSV tables, with `schema.csv` describing every column |

The two databases are never pooled. Delete a file to start it again. If `sentinella.sqlite`
holds a sentinel pool drawn under another configuration, the app stops and asks for the file
to be deleted.

## 📋 What the sample contains

One row is one household assessed at a targeting interview. The sample is synthetic and
contains no real household. It keeps the Scorecard's structure, value sets and score
arithmetic, but not the distribution of the real operation, so every result computed from it
is a property of the sample only.

The full data dictionary (Annex I), with an English name for each column and translations of
the Spanish values, is in [docs/challenge_website.md](../docs/challenge_website.md); the code
uses it through `src/data_dictionary.py`. The columns fall into six groups:

| Group | Columns | Notes |
| :--- | :--- | :--- |
| Outcomes | `EligibilityTarget`, `Elegibilidad` | Never model inputs |
| Aggregated scores | `FinalScore`, `Demographics_Score`, `NeedsandCoping_Score`, `Vulnerability_Score`, `Vulnerability_Category` | Derived from the inputs; never inputs when predicting the score |
| Scorecard factor scores | `Demographics.HH.Head`, `Demographics.Language`, `Demographics.Profiles`, `Demographics.Documentation`, `Needs_and_Coping.BasicNeeds`, `Needs_and_Coping.Housing`, `Needs_and_Coping.Neg.mechanism`, `Needs_and_Coping.Dependency` | Two to four discrete values each, from 1.0 to 3.25 |
| Household attributes | `NumIntegrantes`, `dependencyCategory`, `FemaleHeadedHousehold`, `CuidadorSolo`, `HablaEspanol`, `Analfabeta_si` | Household size (1 to 11) and categorical answers, mostly coded in Spanish |
| Administrative flags | `ScoreCOMAR_PIL`, `ScoreIntenciones`, `ScoreDuplicidad` | 0 or ±500; can override the score |
| Interview record | `month`, `OficinaACNUR` | Month (YYYY-MM) and anonymized field office code |

Blanks mean "not applicable", not missing data, and are kept as an explicit category instead
of being imputed:

- `FemaleHeadedHousehold` and `CuidadorSolo` are blank for exactly the 925 single-person
  households (`NumIntegrantes` = 1), because the questions are not asked of them.
- `ScoreCOMAR_PIL` is blank for 960 rows where the asylum procedure check did not apply.
- `OficinaACNUR` is blank for 21 rows.

## ⚠️ Use

Work only with this synthetic sample and the other released materials. Do not try to
re-identify, link or reconstruct households, caseworkers or offices. The sample and its labels
do not establish real-world distributions or operational eligibility.
