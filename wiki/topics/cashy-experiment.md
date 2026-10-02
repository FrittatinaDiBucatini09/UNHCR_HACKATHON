# Cashy experiment and appropriate reliance

## Design and core result

An earlier **randomized between-subjects experiment** in the Latin American operation involved 31 caseworkers, each assessing five real, already-decided household cases: 155 assessments total. Thirteen caseworkers used plain Cashy; eighteen saw two generic Responsible-AI panels between the reasoning and answer. The panels described *Process-of-Thought* (how the LLM supposedly reads cases generally) and *Process-Guarantees* (transparency, accountability and human final decision). Neither contained a verifiable claim about the case on screen. The effects of the two panels cannot be separated because they were shown together. Source: [[sources/cashy-oversight-challenge-brief|brief Annex II]], [[sources/cashy-oversight-challenge-site|site Annex II]].

The caseworker saw registration record, roughly 400-word reasoning in seven parts, statements if assigned, then answer (score/category/recommendation). They rated effectiveness, agreement, reasons for disagreement, intention to override, answer correctness, reasoning relevance and appropriateness (items EC1–EC7). The incumbent Scorecard determination was hidden until the first submission, then revealed for a second decision. The post-session form rated five UN-system AI principles and gathered an open comment. `EC4` captures override; `EC6 − EC5` is the reasoning–answer rating gap. These instruments and full wording are in the [[sources/cashy-oversight-challenge-brief|brief]], and nearly all appear in the site's expanded panels.

| Outcome | Plain AI, 13 caseworkers | Assurance statements, 18 caseworkers |
|---|---:|---:|
| Correct override on C1/C2 (discordant) | 25/26 = 96.2% (Wilson 95% CI 81.1–99.3) | 24/36 = 66.7% (50.3–79.8) |
| Over-reliance on C1/C2 | 1/26 = 3.8% (0.7–18.9) | 12/36 = 33.3% (20.2–49.7) |
| Correct acceptance on C4/C5 (concordant) | 26/26 = 100% (87.1–100) | 36/36 = 100% (90.4–100) |
| Under-reliance on C4/C5 | 0/26 = 0% (0–12.9) | 0/36 = 0% (0–9.6) |
| End-to-end decision accuracy, all five | 54/65 = 83.1% (72.2–90.3) | 62/90 = 68.9% (58.7–77.5) |

The participant-level correct-override risk difference was **29.5 percentage points** (95% CI 11.9–47.0; Mann–Whitney p=.007; reported GEE OR 0.080 [0.010–0.639]). Eight of the twelve flawed recommendations accepted in the statements arm would have excluded a household that the operation had recorded as eligible. The source extrapolates these observed rates to roughly 295 more decisions against the institutional standard per 1,000 discordant cases; this is a scenario calculation, **not** a measured deployment count. Nobody in either arm overrode a sound recommendation. Sources: [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-site|site]].

## Five reference cases

The numbers below come from real, previously decided cases used in the study, **not S8 rows**. The full household narratives are not included in the wiki.

| Case | Relation and direction | Cashy | Scorecard / institution | Confirmatory? |
|---|---|---|---|---|
| C1 | Discordant; Cashy +29.38; exclusion → inclusion | 43.09 / include | 13.71 / exclude | Yes |
| C2 | Discordant; Cashy −9.88; inclusion → exclusion | 25.52 / exclude | 35.40 / include | Yes |
| C3 | Discordant hard case; Cashy +14.47; exclusion → inclusion | 55.54 / include | 41.07 / exclude on non-need criteria | No; contested reference label |
| C4 | Concordant; Cashy −8.59 | 15.79 / exclude | 24.38 / exclude | Concordant control |
| C5 | Concordant; no score gap | 65.57 / include | 65.57 / include | Concordant control |

## Interpretation and measurement limits

- This is evidence of **behavior under the tested screen conditions**, not proof that every Responsible-AI statement always reduces oversight. Sample: only 31 professionals and five cases, with case-specific and error-direction limits. The brief's 80%-power minimum detectable effect is large: *d*=1.06 for the confirmatory contrast and *d*=1.15 for the post-session instrument.
- Ratings did not reliably reveal the decline: top-box answer correctness increased from 7.7% to 27.8% (Holm-adjusted p=.005); mean correctness and appropriateness did not differ. Reasoning–answer gaps on confirmatory cases were +0.81 vs +0.64 (p=.65). Among 28 linked post-session respondents, uncorrected accountability and transparency scores were higher in the statements arm, but **none of the principle-rating comparisons survived Holm correction**.
- “Correct” is defined against the operation's recorded determination, not against the household's true need. C3 highlights the fragility of that standard. The study cannot identify the separate effects of Process-of-Thought and Process-Guarantees.
- An audit should separate correct override, over-reliance, correct acceptance and under-reliance, use confidence intervals, and treat repeated assessments from one caseworker as clustered. See [[topics/cashy-submission|challenge requirements]].

Sources: [[sources/cashy-oversight-challenge-brief|brief Annex II]], [[sources/cashy-oversight-challenge-site|site experiment panels]].
