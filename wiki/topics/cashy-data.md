# Cashy S8 data and dictionary

## What S8 is

`S8.synthetic_cashy_sample.csv` is the **challenge's released synthetic Scorecard sample**, 1,900 rows × 26 columns, one row per household interview, with months 2023-06 through 2024-07. The [[sources/cashy-oversight-challenge-site|site]] links to a CSV whose SHA-256 exactly matches the file retained in [[sources/s8-synthetic-cashy-sample|raw/]]. The [[sources/cashy-oversight-challenge-brief|brief]] explicitly identifies S8 as the challenge dataset. It derives from historical Scorecard structure, value sets and score arithmetic but **does not reproduce the real operational distribution** or contain real households. Its results must not be described as findings about actual beneficiaries. The only requested statistical treatment is [[topics/csv-mini-eda|mini EDA]]; this page is a source-provided *dictionary*, not a fuller analysis.

## Reference standard and modeling boundary

`FinalScore` is a need-oriented Scorecard total (`Demographics_Score + NeedsandCoping_Score`, with up to 1.5-point synthetic rounding differences); `Vulnerability_Score` is a monotonic transform; `Vulnerability_Category` bands the final score, with slight overlap in the synthetic sample. `EligibilityTarget` is the operation's recorded inclusion/exclusion determination, derived from the six-value `Elegibilidad`; it is **not a direct truth label for need**. Funding and administrative checks affect eligibility. Neither `EligibilityTarget` nor `Elegibilidad` should be used as model input when predicting that target. The interviewer-perception free text shown in the original review workflow is withheld from S8 because it could identify a household; a design needing it must simulate it and disclose that choice. Source: [[sources/cashy-oversight-challenge-site|site dictionary]], [[sources/cashy-oversight-challenge-brief|brief Annex I]].

S8 eligibility is nearly unrelated to score (brief: mean 28.7 for inclusion, 27.5 for exclusion; both labels occur in every vulnerability band). This exaggerates the issue seen in real data. **Do not benchmark eligibility performance on S8 against the 67.6% from the real held-out test.** Use S8 to build and instrument the workflow, not to assert real-world predictive quality.

## 26-column dictionary

These are source-provided meanings, not freshly inferred relationships. Counts are in [[topics/csv-mini-eda|mini EDA]] where useful.

| Block | Column | Meaning / boundary |
|---|---|---|
| Interview | `month` | Targeting interview month, YYYY-MM. |
| Interview | `OficinaACNUR` | Anonymized field-office code; seven non-null codes, not names. |
| Household | `NumIntegrantes` | Household size. |
| Household | `dependencyCategory` | Dependency-ratio category. |
| Household | `FemaleHeadedHousehold` | Sex of head in the applicable households; blank for single-person households. |
| Household | `CuidadorSolo` | Sole carer of dependents; blank for single-person households. |
| Household | `HablaEspanol` | Whether at least one adult speaks Spanish. |
| Household | `Analfabeta_si` | Whether any adult in the household cannot read. |
| Factor score | `Demographics.HH.Head` | Household-head profile. |
| Factor score | `Demographics.Language` | Language barrier. |
| Factor score | `Demographics.Profiles` | Specific-needs profiles. |
| Factor score | `Demographics.Documentation` | Documentation status. |
| Factor score | `Needs_and_Coping.BasicNeeds` | Unmet food, water and hygiene needs. |
| Factor score | `Needs_and_Coping.Housing` | Housing stability. |
| Factor score | `Needs_and_Coping.Neg.mechanism` | Negative coping mechanisms. |
| Factor score | `Needs_and_Coping.Dependency` | Dependency burden. |
| Administrative | `ScoreCOMAR_PIL` | National asylum-procedure status; 0 or ±500 where applicable. |
| Administrative | `ScoreIntenciones` | Stated intentions incompatible with programme; 0 or −500. |
| Administrative | `ScoreDuplicidad` | Duplicate registration; 0 or −500. |
| Aggregate | `Demographics_Score` | Demographics block total. |
| Aggregate | `NeedsandCoping_Score` | Needs/coping block total. |
| Aggregate | `Vulnerability_Score` | Monotonic vulnerability index from final score. |
| Aggregate | `FinalScore` | Scorecard total, higher = more vulnerable. |
| Outcome | `Vulnerability_Category` | Four-band category derived from final score. |
| Outcome | `Elegibilidad` | Six-value recorded status; encodes the binary target. |
| Outcome | `EligibilityTarget` | `INCLUSION`/`EXCLUSION`; **target, never an input feature**. |

Factor scores have small discrete sets, broadly 1.0–3.25, where higher means more vulnerability on that factor. The source dictionary provides exact value sets in [[sources/cashy-oversight-challenge-brief|Annex I]] and on the [[sources/cashy-oversight-challenge-site|website]]. This page preserves meanings and guardrails without duplicating all source-level frequencies.

## Missingness is structural

The 925 single-person rows have blank `FemaleHeadedHousehold` and `CuidadorSolo` because those questions did not apply. `ScoreCOMAR_PIL` is blank for 960 rows where that check did not apply; `OficinaACNUR` is blank for 21. Do not automatically impute these as errors. `EligibilityTarget` has 427 inclusion and 1,473 exclusion rows; the source says these are synthetic proportions, not real programme rates. See [[topics/csv-mini-eda|mini EDA]].

## Other referenced material

The site and brief list a participant briefing (S1), open-comment codebook (S2), analysis code (S3), de-identified assessment records (S4, 155 assessments), principle ratings (S5), model card (S6), Cashy AutoML code (S7) and redacted narratives (S9) **where released**. They are referenced, not confirmed present in this workspace. Raw household records and free-text comments are withheld for identifiability reasons. Sources: [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-site|site]].
