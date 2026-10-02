# Cashy Oversight Challenge

## The problem

For the operational sequence and the distinction between the incumbent Scorecard, the Cashy prototype and the study procedure, start with [[topics/cashy-decision-process|decision process and challenge two]]. The website's simplified AI-assisted chain does not confirm Cashy is deployed in live decisions.

The challenge concerns **human oversight of AI-supported cash-assistance targeting** in a UNHCR country operation in Latin America. Assistance is rationed. Registration staff interview a displaced household; an expert-designed Scorecard combines demographics, needs/coping and administrative checks; Cashy supplies a score, vulnerability band, inclusion/exclusion recommendation and separate narrative reasoning; a caseworker accepts or overrides; eligible households are prioritized within available funding. Caseworkers receive no outcome feedback, and households do not participate in or contest this decision. A wrongful inclusion also uses resources that could serve another household. The operation's recorded determination is an institutional reference standard, **not** an objective measure of need. Sources: [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-site|site]].

Cashy is a **prototype** in KoboToolbox, not a proven production deployment. Its answer engine is an AutoGluon tabular model trained on about 19,900 historical Scorecard records. Its reasoning engine is an LLM given the same anonymized household data. These engines and their outputs must not be conflated. On a class-balanced held-out set of 1,828 real records, the answer engine reproduced score (R² 0.9998; MAE 0.03) and category (99.6% accuracy) but was weak on eligibility (67.6% accuracy; AUC 0.70; inclusion recall 82%, exclusion recall 53%). Funding and administrative criteria are not fully captured by the model features. Source: [[sources/cashy-oversight-challenge-brief|brief]].

## Two questions

1. **Prediction:** Can teams improve prediction of cash eligibility with calibrated uncertainty and show which parts of a case-level recommendation are actually supported by the available data?
2. **Core question — appropriate reliance:** How can caseworkers continue overriding Cashy when it is wrong, and how can the institution detect erosion of correct override before and after deployment? A better model does not eliminate the need for this control.

The earlier experiment found that generic Responsible-AI assurances placed on the decision screen reduced correct overrides despite caseworkers being able to rate the answer as flawed. Therefore the brief offers three starting points, not limits: keep such statements in training/documentation rather than on the decision screen; audit override before deployment; log and monitor override in production. See [[topics/cashy-experiment|experiment and its limits]].

## Solution space

The brief and site explicitly allow a multidisciplinary response and list six non-exclusive tracks:

| Track | What it would test or deliver |
|---|---|
| Instrumented targeting prototype | Separate answer and reasoning, require separate human judgments, log agreement/override/reasons and reasoning–answer rating gap; use S8 for workflow testing. |
| Override audit toolkit | Blind review of already-adjudicated concordant/discordant cases, reveal institutional determination, decompose reliance with confidence intervals, account for clustered caseworker assessments and sample size. |
| Decision-screen design and experiment | Test case-level cues, cognitive forcing or uncertainty; separate the two assurance panels; pre-specify confirmatory contrast and minimum detectable effect. |
| Production override monitor | Power BI-compatible trends by office, vulnerability band and error direction, with an owner accountable for investigating falling correct override. |
| Behavior-first governance | Combine principles, model cards and checklists with observed behavior; do not equate positive ratings with effective oversight. |
| Follow-up research | Independent answer/reasoning review, second comment coder, participation by affected households, or replication elsewhere. |

The operation's practical stack is KoboToolbox, Python and Power BI; feasibility, cost, maintainability and reproducibility matter. Governance or process designs without complete software, and non-production-ready concepts, are permitted by the [[sources/cashy-oversight-challenge-faq|FAQ]].

## Annex III research agenda

The brief proposes seven open questions, not mandatory tasks: (1) which on-screen cues change behavior rather than only reported opinion, and whether the two assurance panels have different effects; (2) whether the reasoning–answer rating gap can flag individual at-risk assessments or only groups; (3) the smallest, appropriately balanced override audit capable of detecting a 15-point decline with 80% power; (4) how to monitor production override without turning override frequency into a perverse target; (5) whether S8 can communicate, case by case, the distinction between support for score/category and weak support for eligibility; (6) how to combine principle ratings, model cards and checklists with behavioral evidence; and (7) how to evaluate from the viewpoint of displaced households and involve them in setting oversight standards. Source: [[sources/cashy-oversight-challenge-brief|brief Annex III]].

Annex IV groups a reading list into humanitarian targeting and institutional AI principles; appropriate reliance, over-reliance and oversight; and ethical/human-rights considerations. It specifically points to the UNHCR AI Approach, UN-system ethical AI principles, UNHCR–WFP targeting principles, and UNHCR targeting guidance. The [[sources/cashy-oversight-challenge-site|site]] supplies the full set of live links; the [[sources/cashy-oversight-challenge-brief|brief]] contains the corresponding bibliography. Listing a work here does not mean this wiki has independently verified its findings.

## Where to go next

- [[topics/cashy-data|S8, data dictionary, and interpretation limits]]
- [[topics/cashy-experiment|Randomized study, five cases, and appropriate-reliance reference values]]
- [[topics/cashy-submission|Requirements, ideal deliverables, FAQ, judging, and contacts]]
- [[topics/open-questions|Cross-source discrepancies and unresolved details]]
