<p align="right"><img src="../docs/images/unhcr_emblem.png" alt="UNHCR emblem" width="56"></p>

# Model card: Scorecard score model

The score model behind the AI assessment of the Sentinella prototype, called the "Answer" panel
in the phase reports. It reproduces the
Scorecard final score and vulnerability category of a household from its eight factor scores
and breaks the score down by factor. Numbers link to the tables in [`tables/`](tables/), produced
by [`notebooks/02_score_model.ipynb`](../notebooks/02_score_model.ipynb) unless stated otherwise.
The analysis behind the model is in [01_data_exploration.md](01_data_exploration.md) and
[02_score_model.md](02_score_model.md).

## Model details

- **What it is:** a closed-form formula, not a trained model. It was recovered from the S8
  synthetic sample in phase 1 and has no fitted parameters.
- **Code:** [`src/scorecard.py`](../src/scorecard.py) holds the formula, its constants and the
  attributions; [`src/score_model.py`](../src/score_model.py) holds `predict(row)`; the unit tests
  are in [`tests/test_score_model.py`](../tests/test_score_model.py).
- **Developed by:** the Sentinella team, for the Cashy Oversight Challenge (University of Trento
  and UNHCR Innovation), October 2026.

With g_D and g_N the geometric means of the four demographic and the four needs and coping factor
scores, and G_D = 2.4883 and G_N = 2.3955 their values when every factor is at its highest level
([scorecard_constants](tables/scorecard_constants.csv), from notebook 01):

| Output | Formula |
| :--- | :--- |
| Final score | 100 x (g_D + g_N - 2) / (G_D + G_N - 2), from 0 to 100 |
| Vulnerability index | g_D + g_N, from 2.0 to 4.88 |
| Category | Low below an index of 2.7, Moderate from 2.7, High from 2.9, Severe from 3.5 (final scores 24.27, 31.21 and 52.01) |
| Attribution of a factor | its exact Shapley value in points, with 1.0 as the level that adds nothing |

## Intended use

- Supplying the score and category of the AI assessment in the prototype's officer workspace,
  shown apart from the reasoning text. The delivered workspace does not show the factor
  breakdown.
- Building review-screen material, override audits and training sessions on synthetic data.
- Explaining how the Scorecard turns factor scores into a score.

## Out-of-scope uses

- Deciding or recommending whether a household receives cash, or ranking households under a
  budget.
- Scoring real households, or standing in for the operation's Scorecard, before the formula and
  the cutpoints have been checked against the operation's own specification.
- Replacing the caseworker's review of a case.
- Judging whether the factor scores themselves were recorded correctly.

## Inputs and outputs

The input is the eight factor scores, keyed by their column names in the sample:
`Demographics.HH.Head`, `Demographics.Language`, `Demographics.Profiles`,
`Demographics.Documentation`, `Needs_and_Coping.BasicNeeds`, `Needs_and_Coping.Housing`,
`Needs_and_Coping.Neg.mechanism` and `Needs_and_Coping.Dependency`. Each must be one of the
factor's levels in Annex I; values rounded to two decimals are accepted and any other value
raises an error. No household attribute, administrative flag, month, office or outcome is used.

The output is a dict with the final score (0 to 100), the category (Low, Moderate, High or
Severe) and the attribution of each factor in points. The attributions add up to the score.

## Data

The S8 synthetic sample: 1,900 synthetic households and 26 columns, released for the challenge
and described in [`data/README.md`](../data/README.md). It contains no real household and keeps
the Scorecard's arithmetic but not the operation's distribution. Nothing is fitted, so no
training data is needed; for the comparison with learned models the sample was split into 1,520
training and 380 test households, stratified by recorded category
([score_model_split](tables/score_model_split.csv)).

## Performance

On the 380 held-out test households, with 95% bootstrap intervals
([score_model_test_metrics](tables/score_model_test_metrics.csv)):

| Metric | Score model | Best learned model (LightGBM), for comparison |
| :--- | ---: | ---: |
| R² | 1.0000 | 0.9984 |
| Mean absolute error (points) | 0.0000049 (0.0000045 to 0.0000052) | 0.30 (0.25 to 0.35) |
| Largest absolute error (points) | 0.000015 | 6.32 |
| Category reproduced | 99.5% (98.7% to 100%) | 97.4% (95.5% to 98.9%) |

On all 1,900 households, `predict` differs from the recorded final score by at most 0.000015
points and reproduces the recorded category for 1,890 ([predict_checks](tables/predict_checks.csv)).
The error is the same in repeated cross-validation, on factor combinations absent from the
training data and on later months
([score_model_cv_summary](tables/score_model_cv_summary.csv),
[score_model_grouped_cv_summary](tables/score_model_grouped_cv_summary.csv),
[score_model_temporal](tables/score_model_temporal.csv)), and below 0.0001 points in every
subgroup of household size, category and office
([score_model_test_subgroups](tables/score_model_test_subgroups.csv)).

The 10 households whose recorded category the model does not reproduce are recorded Moderate
with scores in the High band. Six of them have the same factor scores as households recorded
High, so no rule based on the score can reproduce them; 99.5% is the ceiling on this sample
([category_agreement](tables/category_agreement.csv), from notebook 01).

## Explanations

Each attribution is the factor's exact Shapley value under the formula: its average contribution
over every order in which the factors are raised from 1.0. The attributions of a household add up
to its score, to within 3 x 10⁻¹⁴ points, and are never negative
([shapley_checks](tables/shapley_checks.csv)). Factors in the same block reinforce each other, and
their joint effect is shared between them; the two blocks add up separately.

An attribution says how many points a factor adds to the Scorecard score, given the household's
other factors. It does not describe the household beyond what the factor records.

## Limitations

- The formula was recovered from synthetic data. It is confirmed on the 493 factor combinations
  present in the sample, not on the other 13,331 possible ones
  ([duplicates](tables/duplicates.csv), from notebook 01).
- The category cutpoints are known only within narrow intervals, and the sample cannot tell
  whether the operation bands the vulnerability index or the final score. The choice changes the
  category of 52 of the 13,824 possible factor combinations and of no household in the sample
  ([category_cutpoint_uncertainty](tables/category_cutpoint_uncertainty.csv), from notebook 01).
- The recorded final scores were built with block weights rounded to six decimals, which accounts
  for the 0.000015-point difference.
- The model knows only the factor levels of Annex I. A change to the Scorecard's levels or
  weights requires updating the constants in `src/scorecard.py` and rerunning both notebooks.
- The score uses only the factor scores. It ignores the interviewer's view of the household, which
  is not in the sample, and anything else a caseworker reads in the record.

## Ethical considerations

- **Need, not eligibility.** The score measures need as the Scorecard's designers defined it. In
  the sample, the inclusion decision is almost unrelated to the category (Cramér's V 0.02) and
  depends far more on the interview month (V 0.31)
  ([eligibility_association](tables/eligibility_association.csv), from notebook 01). The score
  must not be presented as a recommendation to include or exclude.
- **An exact answer can look more authoritative than it is.** In the experiment described in the
  brief, general statements about the system's conduct lowered correct overrides from 96.2% to
  66.7% ([challenge brief](../docs/challenge_website.md)). The panel should present the score as
  the Scorecard's output, keep it apart from the reasoning, and leave the decision with the
  caseworker.
- **Recording errors pass through.** A wrongly recorded factor score produces a wrong score,
  exactly. The model cannot catch it; only a review of the record can.
- **Affected people.** Households never see the decision or the score and cannot contest them.
  The model is used only on synthetic data; offices appear only as anonymized codes, and nothing
  in the analysis identifies a household, caseworker or office.

## Decisions the features can and cannot support

The eight factor scores can support:

- reproducing the Scorecard final score and vulnerability category;
- showing which factors produce a score and by how much;
- checking a recorded score or category against the Scorecard arithmetic, which is how the 10
  inconsistent categories in the sample were found.

They cannot support:

- deciding whether a household receives cash: eligibility depends on funding and on
  administrative checks that the factors do not capture;
- prioritising households within a budget;
- judging whether the factor scores were recorded correctly, or need that the factors do not
  record;
- any conclusion about real households or about the real operation.
