# Cashy pipeline planning and unresolved design choices

## Canonical user roadmap and current position

Source: user's explicit correction on **2026-10-01**. This replaces the assistant's provisional wording as the canonical roadmap. The user permits justified variation in order but wants broadly this sequence; do not silently mix stages or substitute a new roadmap.

| Step | Cosa decidiamo o produciamo | Current status |
|---|---|---|
| **1. Obiettivo e riferimento** | Che cosa significa “decisione corretta”, su quali casi possiamo verificarlo, quali errori hanno maggiore impatto. | **Settled per the latest user correction. Do not reopen.** Retain existing definitions and limits. |
| **2. Literature review** | Una matrice delle evidenze: intervento, meccanismo, risultati, popolazione, limiti, costo operativo e durata dell'effetto. | Source collection and preliminary references only; no completed evidence matrix. |
| **3. Protocollo decisionale** | Selezione di uno o due interventi, momento in cui intervengono, informazioni mostrate e azioni richieste all'operatore. | Mandatory justification confirmed; two paired operator flows remain candidates for evidence review. No final flow/checklist or UI design. |
| **4. Valutazione e monitoraggio** | Confronto con il processo iniziale, metriche, campionamento, incertezza, gestione degli allarmi e responsabilità del manager. | Commission without AI and manager capabilities confirmed. Random audit across acceptance and override, with separate targeted review, confirmed 2026-10-01. The Sentinella prototype sets counts, intervals and an alert rule as demo values; operational values and the response policy remain open. |
| **5. UI e UX** | Schermate e percorso dell'operatore costruiti sul protocollo concordato. | Prototype screens built in Sentinella (2026-10-02) on the two variants as defined for the prototype; not yet informed by the literature matrix. |
| **6. Coding** | Implementazione del flusso, registrazione delle decisioni, campionamento per audit e dashboard. | Sentinella prototype built in four gated phases, 2026-10-01 to 2026-10-02, started early by the user's deliberate choice; see the [[log|log]]. |
| **7. Verifica e presentazione** | Demo funzionante e piano sperimentale che permetta di valutare l'efficacia. | Not started. |

Step 1 retained from user statements and challenge definitions: increase P(override | incorrect AI), consider correct acceptance secondarily, prioritize wrongful exclusions without a severe-consequences prerequisite, and preserve the operational value of time saved. The challenge's institutional determination is the documented experimental reference, not truth about actual need. Routine live ground truth is not assumed. The user explicitly says objectives and reference are already defined; the assistant's previous attempt to reopen them was a workflow error, not a newly discovered blocker.

The previous question about revising eligibility criteria is **withdrawn**, not answered by inference. Do not broaden the challenge's scope or require that answer to proceed. Future operational reference collection, audit staffing/counts, uncertainty formulas and alerts belong to step 4's implementation/evaluation design. Manager visibility of decision time remains accepted.

**Current focus:** retain the user's latest end-to-end workflow reconstruction and resolve its open dependencies one at a time. The operator protocol is step 3; commission sampling and manager follow-up are step 4. Clarifying the qualitative sampling principle first is an explicit cross-step dependency: it determines what operator performance can be assessed. No completed literature review is inferred. The Sentinella prototype (step 6) was built early by the user's choice; its numbers are demo values, not protocol decisions.

**Latest user response:** independent AI-free commission review, mandatory operator justification, case traceability/timing, manager comparison against commission assessments and manual follow-up/peer-review capabilities are confirmed. Two candidate operator flows are now explicitly paired, but neither selected. The user asks to preserve doubts and resolve them individually. Specific guided checks still lack sufficient operational evidence; do not ask the user to invent them.

**Answered 2026-10-01:** the commission receives a random sample covering both AI acceptance and override, with separately identified targeted reviews that never enter a rate estimate (confirmed when implementation started). Audit proportion, reviewer count and referral thresholds are demo values in the prototype, not operational decisions. The question about rulebook/mentor availability remains parked.

Interview rule: one question at a time with a concrete recommendation and reason; record answers, distinguish source facts from decisions, and state current step and remaining gaps. Do not repeat settled questions or replace this sequence with a menu of follow-ups.

## Current operator-flow alternatives

Source: latest user workflow reconstruction on **2026-10-01**. The user now explicitly pairs presentation and AI timing; this supersedes the earlier ambiguity. No variant is selected. On 2026-10-02 the user delegated their definitions for the prototype, where caseworkers are split at random between the two:

| Variant / choice | Candidate sequence | Status |
|---|---|---|
| A: summary first, AI later | Operator reviews a summary; AI score and explanation are shown at the end, with access to the complete report | Defined for the prototype on 2026-10-02: a summary of every recorded field, with the complete record one click away; on fragile cases the operator records a category before the AI is revealed; fragility hint shown. Not selected on evidence |
| B: complete report, AI first | Complete report with AI score and explanation available from the beginning | Defined for the prototype on 2026-10-02: the fragility hint, shown with the record, is the verification cue; no preliminary judgment. Not selected on evidence |
| Guided checks | Whether either variant requires specific verification actions, rather than only reading | The fragility hint (confirmed 2026-10-01) names the factors to check in both variants. No wider checklist is selected or operationally validated |
| Full evidence access | Operator can inspect the complete case at least at the end | **User requirement**, applies to whichever variant is selected |

The earlier request referred to a guided summary of all fields; do not silently restrict it to high-importance features. Whether a summary is generated or assembled, its fidelity, treatment of missing information and verification content remain design questions. “At the end” does not establish whether a preliminary decision has already been recorded. No four-arm experiment, fixed checklist or summary-generating AI is selected. In the prototype, variant A records a preliminary judgment on fragile cases and its summary is assembled from the recorded fields, without generative AI. Evidence review must still inform the choice between the user's paired candidates.

An optional candidate to examine is a structured, source-faithful presentation of original field values, with expansion to the original form. This is not the same as an LLM-written narrative and does not require adding another predictive/generative AI. Making full-form access available from the start is an assistant suggestion, not an inferred user requirement. Effects on attention, correct override, correct acceptance and time remain to be researched/tested.

## Latest workflow: confirmed decisions and ordered open nodes

Source: user's latest workflow reconstruction on **2026-10-01**. This is a user-directed design baseline, not an empirical finding or deployed system.

Confirmed requirements:

- An independent commission periodically reassesses a subset of operator decisions **without receiving AI advice**. Its one/two/other reviewer count and audit frequency are not fixed. AI-blinding is confirmed; blinding to the first operator's decision and rationale was adopted for the prototype on 2026-10-01.
- Each operator must write a case justification. In case of problems it is to be made available to the household. Wording, structure, timing and disclosure/privacy handling remain open; this does not establish a complete appeal process or prove an attention benefit.
- Each case/request must be traceable, with timing and manager statistics. Do not interpret this as consent to collect unrestricted interaction telemetry or equate time with attention.
- The manager must see operator performance compared with independent commission assessments, not just override rates. Metrics, denominator, case mix, minimum sample and reference/adjudication treatment remain open.
- The manager must be able to follow up with an operator after a serious error and manually refer cases for peer review. The meaning of “richiamo” (discussion, coaching or formal reprimand), who confirms an error, responsibilities and thresholds are unresolved. No automatic punishment is adopted.
- Full-case access remains required at least at the end; the two paired operator-flow candidates above remain open.

Open-node register, proposed interview order rather than final decisions:

| Node | What remains undecided | Roadmap location |
|---|---|---|
| 1. Commission sampling | All decision types versus overrides/suspicious cases only; random versus targeted queues | Step 4 principle, current question; exact proportions later |
| 2. Error impact and follow-up | What counts as a high-impact event, what triggers case review versus broader operator review, and whether lesser confirmed errors accumulate | Step 4 response policy; step 1's exclusion priority is not reopened |
| 3. Operator flow | Choose A or B with literature support; define summary content, specific checks and whether a preliminary judgment is recorded | Steps 2–3, before UX |
| 4. Mandatory justification | Required evidence/reasons, timing, structure and household-facing communication | Steps 2–3; disclosure/recourse safeguards also step 4 |
| 5. Reference review protocol | Reviewer count, original evidence, blinding beyond AI, disagreements and adjudication authority | Step 4 |
| 6. Dashboard and referrals | Traceable events, timing definitions, comparison metrics, uncertainty intervals, manager follow-up and peer-review routing | Step 4 before steps 5–6 |
| 7. Confidence indicator/model | Whether needed, what it measures and whether it can be validated; the user doubts that an extra model will work | Parked candidate, not an implementation dependency |

The user's high-impact idea is a **hypothesis**: one serious error might trigger immediate review, whereas lesser errors might require recurrence. Do not convert it into a selected cutoff. Distinguish review of the household case, review of the operator's wider work and formal discipline. A signal can trigger a case check before error confirmation; a commission disagreement is not yet an adjudicated operator error. See [[topics/cashy-manager-monitoring|monitoring and response policy]].

Sampling principle, **accepted 2026-10-01**: maintain a probability sample across both accepted and overridden AI advice, with separate targeted review for flagged cases. Override does not mean error; acceptance does not mean correctness. Auditing only overrides cannot detect the primary failure mode of accepting wrong AI advice and cannot directly estimate overall operator performance. Exact sample size remains open; targeted-review rates must not be pooled uncritically with random-audit rates.

## How to select concrete guided checks

Source of the problem: the user's earlier guided-check objection on **2026-10-01**. They note that neither they nor the team currently have the evidence to select “a few checks” and that presenting an unspecified list is not enough. This section remains an **assistant proposal**, not user-approved or empirically validated.

Two inputs answer different questions: empirical literature informs the checking mechanism, AI exposure, burden and behavioral effects; operational rules, documented failure cases and domain experts determine which eligibility facts are actually decisive. Literature alone cannot supply a universal Cashy field list. The [[sources/cashy-oversight-challenge-brief|brief]] and [[topics/cashy-data|S8 dictionary]] supply fields, meanings and some case profiles, not a complete released questionnaire plus decision rulebook. S7/S9 are referenced but are not present in the checked workspace. Do not reconstruct the real complete form from 26 synthetic columns or ask to analyze the CSV beyond the mini EDA.

Proposed selection method:

1. Build a candidate register from documented error mechanisms and the applicable rules, not merely high vulnerability-feature importance. Each check needs a specific failure it could catch, exact source fields, a concrete operator question, response choices and a follow-up action.
2. Reject or defer checks whose source evidence, field semantics or rule relevance cannot be established. Validate domain-specific choices with an authorized UNHCR expert. Do not fabricate score cutoffs or treat a high vulnerability score as sufficient eligibility.
3. Pilot surviving checks on documented/simulated cases with and without the targeted defect, including correct AI advice. Measure errors caught, false alarms, correct acceptance and review time. Simulation demonstrates behavior of the prototype, not field effectiveness. Exact study design remains step 4.

Selection considerations are relevance to exclusion failures, actual verifiability, plausible usefulness and measured operational cost. No weighted optimization function or optimum number is claimed. The checked [[sources/nist-ai-rmf-measurement|NIST guidance]] supports domain-informed validation; [[sources/vasconcelos-2023-explanation-verification|Vasconcelos abstract]] motivates investigating verification costs, but its maze-task findings do not validate these Cashy checks.

### Three concrete research candidates supported by available meanings

| Candidate | Example operator question/evidence | What it can establish and cannot |
|---|---|---|
| Faithfulness of a factual AI claim | Compare an AI assertion about household size with `NumIntegrantes`, or a language assertion with `HablaEspanol`; e.g. an illustrative narrative says five people while the record says one | Can reveal a factual contradiction. Does not prove the tabular eligibility answer is wrong; reasoning and answer must remain separately assessed |
| Correct treatment of non-applicable fields | For `NumIntegrantes = 1`, `FemaleHeadedHousehold` and `CuidadorSolo` are not asked. Is a narrative incorrectly treating their blanks as negative findings or failed collection? | The applicability rule is stated in Annex I/main brief. Other blanks must not automatically be generalized as harmless or erroneous |
| Evidence supporting an exclusion reason | If the AI cites duplication, intentions or procedure status, inspect the corresponding recorded administrative flag and the documented meaning. Is the reason supported, contradicted or not verifiable from the supplied material? | Can expose an unsupported stated reason or missing evidence. Cannot derive a final eligibility rule, funding availability or automatic override from the flag alone |

The examples are illustrative checks, not observed S8 narrative errors; S8 contains no AI narrative column. A demo would need explicitly authored/simulated narratives or released redacted material. The first/third checks require AI reasoning to have been revealed; do not claim they are independent pre-AI checks. For an AI-at-end variant they occur after reveal, while evidence review before reveal is a separate protocol element still to define.

Suggested response format: **supported / contradicted / not verifiable**, with a source pointer and reason rather than a generic “I checked” box. A failed reason check flags the reasoning for reassessment; it does not force inclusion or override a potentially correct answer. Unknown evidence is an explicit state, not proof of ineligibility.

The real C2 profile in Annex II describes a sole carer, infant, serious medical conditions and incomplete documentation, with a wrongful-exclusion recommendation. The profile does not identify which feature caused the model error or which field check would have corrected it. Do not use this single case to justify a universal “check health first” rule. Full raw case narratives are withheld/not available here.

### Minimum defensible presentation, proposed

Show at least one fully specified check end to end: triggering condition, original evidence, operator question, recorded answer, and permitted follow-up. Demonstrate both a detectable contradiction and a sound claim so the check is not simply a nudge to override. State which checks are validated only against source semantics and which need operational expert review. A method for configuring future checks can be part of the contribution, but must not replace all concrete examples. Do not claim improved human attention or correct-override rates until tested.

## User requirements and candidate ideas

Source: earlier user messages on 2026-10-01, requesting a grill-me interview and a staged approach to challenge two. The user wants authoritative literature before final protocol/UI/UX and coding. The list retains the original ideas, with current adoption status:

- Prompt the caseworker to revisit questions important to the final score; the user notes that staff may already read the whole file.
- Require a decision justification that the affected household can read: **now confirmed as mandatory**, with household disclosure in case of problems. Participation/appeal mechanism and effects remain unvalidated.
- Give managers operator-level override monitoring with statistically supported anomaly flags and adequate sample size.
- Establish verified early decisions as a baseline, then monitor changes over time despite absent routine ground truth.
- Independently review a subset of decisions: **commission without AI now confirmed**. Random sampling versus restricted/targeted selection remains open.

Latest user update (2026-10-01): decision time and commission-based operator comparison must be visible to the manager; wrongful exclusion is the accepted protection priority without a serious-consequence prerequisite. Manager follow-up and peer-review referral capabilities are confirmed, but exact responses and sanctions remain unresolved. A manager-only uncertainty/review indicator and extra confidence model remain doubtful candidates, not validated measures or requirements. No additional predictive model or automatic routing is selected. Canonical details: [[topics/cashy-manager-monitoring|manager monitoring]].

The user's primary objective is P(override | AI incorrect), with P(acceptance | AI correct) a secondary concern. This goal is retained as settled; precise performance bounds belong to step 4, not another objectives interview. Indiscriminate override is not appropriate reliance. See [[topics/cashy-decision-process|definitions]].

## Operational elaboration of the canonical roadmap

The detail below elaborates the user's seven steps above; it is not a competing roadmap. Quantitative settings and final interventions remain pending:

1. Define the target behavior, error costs, reference standard and available review process. Distinguish audited correctness from unlabeled behavior indicators.
2. Conduct an extensive but targeted literature review. Extract intervention, mechanism, population/task, comparison, sample, uncertainty, burden, longitudinal evidence and applicability. Use peer-reviewed primary studies and authoritative institutional sources; distinguish empirical results from normative guidance. Prioritize automation bias/anchoring, cognitive forcing, verifiable evidence and uncertainty, vigilance/fatigue, accountability/reasons/recourse, blinded second review, and statistically calibrated monitoring. The newly ingested UN principles and targeting mapping are normative/contextual anchors, not a substitute for empirical interface studies.
3. Select a small number of interventions and articulate falsifiable hypotheses and guardrails. Feature importance for vulnerability is not automatically evidence about eligibility or the best attention cue.
4. Specify evaluation before UX: reference labels on sampled cases, baseline/comparator, primary outcome, correct-acceptance constraint, first-stage and total review time, household delay, clustering and sample planning; specify alert interpretation and follow-up. Visibility of decision time to the manager is accepted; operational timing definitions and quality constraints remain to be set.
5. Design review and management UX from the agreed protocol.
6. Implement the minimum demonstrable pipeline with separate reasoning/answer assessments and an audit trail.
7. Validate implementation and present the prototype and evaluation plan. Claims of behavioral effectiveness require an appropriate study, beyond a functioning synthetic-data demo.

## Measurement implications

These are methodological deductions and proposed design considerations, not verified intervention effects:

- Override-rate variation can reflect case mix, AI quality, programme rules or workload. A confidence interval describes sampling uncertainty under a model; it does not isolate automation bias or establish correctness.
- An initially verified baseline does not establish that later decisions remain correct. Label-free monitoring should describe behavior changes and trigger case review.
- Peer agreement measures consistency. Shared errors remain possible, especially when reviewers see the same AI recommendation. Blinded independent reviews and an explicit adjudication process could produce a practical reference on a sampled subset; that reference still has uncertainty and is not objective truth about need.
- A beneficiary-facing rationale and an actual recourse pathway are separate features. Their effect on operator attention must be tested rather than assumed.
- Repeated operator comparisons and monitoring over time need false-alert control and consideration of different case assignments. No sample-size threshold or alert cutoff has yet been selected.

## Preliminary literature anchors

[[sources/bucinca-2021-cognitive-forcing|Buçinca et al 2021]] reports reduced overreliance with cognitive forcing but less favorable user ratings. [[sources/vasconcelos-2023-explanation-verification|Vasconcelos et al 2023]] examines verification cost and conditions where explanations help. [[sources/green-2022-institutional-oversight|Green 2022]] motivates evaluating institutional oversight beyond nominal human involvement. Only abstracts and publication records have been checked so far; a comprehensive full-text review remains to be done.

Two user-supplied documents are now fully ingested: [[sources/un-system-ethical-ai-principles|UN-system AI principles]] (4 pages) and [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR targeting mapping]] (71 pages, research from 2022). They support [[topics/cashy-ethical-guardrails|governance guardrails]] and [[topics/cashy-targeting-context|targeting context]], not empirical claims of guided-review effectiveness. [[sources/nist-ai-rmf-measurement|NIST guidance]] was checked in relevant sections for measurement validity and monitoring, not as a full-text literature-review ingest.

## Operational reference collection: step 4, architecture confirmed

The user has closed step 1; do not turn operational reference collection into another objectives interview. The latest reconstruction confirms an independent commission without AI; it does **not** settle random selection, additional blinding, staffing or adjudication. Clarifying the sampling principle is the current explicit dependency within step 4, not a full quantitative design. The commission can supply candidate reference judgments on sampled cases, with a resolution process still needed for disagreement; no universal live ground truth is asserted.

## Audit size and reviewer count

On 2026-10-01 the user first asked about review counts and suggested one additional reviewer. Their latest reconstruction confirms an independent commission without AI, while explicitly leaving one/two/other reviewer count, case selection and proportions open. Earlier economical one-reviewer suggestions are not an adopted staffing specification.

The assistant recommends defining the method now and retaining quantitative settings for later evaluation design. The audit sample size should follow the desired precision or minimum detectable change, frequency of AI errors, granularity (operator/team), time window, clustering and reviewer capacity. Literature informs methods and prior assumptions; it does not supply a universally valid audit percentage. General statistical basis: [[sources/nist-sample-size-planning|NIST sample-size planning]].

For P(override | AI incorrect), the relevant denominator is the audited subset judged to contain incorrect AI recommendations, not every audited case. A random audit should include accepted and overridden decisions. Sampling enriched by error suspicion would require accounting for selection if estimating population rates.

One additional blinded reviewer per sampled case is a proposed economical first check, not established proof of correctness. They should first assess the original case evidence under the applicable policy and contextual constraints without seeing the AI or first operator's decision/rationale. Disagreement requires an adjudication path; agreement can still contain a shared error. A pilot with two independent additional reviews on a subset could estimate reviewer consistency and guide the final protocol. Exact proportions, minimum counts and adjudication staffing remain pending the literature review, pilot assumptions and statistical design.

## Deferred intervention choice and corrected order

Earlier on 2026-10-01 the user noted premature intervention selection before harm priorities. They subsequently accepted the exclusion priority and now explicitly say step 1 is complete. The latest request focuses the interview on guided versus full-form presentation and beginning/end AI exposure. These remain research candidates, not validated selections. Retain the user's concern about time saved and the burden of reading the entire case twice; review safety jointly with time and sustained workload.

## Error impact and accepted priority

Distinguish classification from valuation. Given an agreed reference, wrongful exclusion means exclusion despite recorded eligibility, and wrongful inclusion means inclusion despite recorded ineligibility. Severity and relative cost require contextual judgments; the brief does not supply a numerical loss matrix or ratio. These operational-reference errors must not be conflated with errors in how eligibility criteria represent actual need.

The [[sources/cashy-oversight-challenge-brief|Cashy brief]] highlights harm from wrongful exclusion and resource displacement under fixed funding when wrongful inclusion occurs. The fact that eight of twelve accepted flawed recommendations in one experimental arm were wrongful exclusions is an observed count, not a severity weighting. [[sources/unhcr-wfp-targeting-guidance|UNHCR-WFP guidance]] supplies a general directional preference in life/livelihood-risk settings while emphasizing context; it does not settle the specific operation's trade-offs.

On 2026-10-01 the user accepted **option A with a correction**: prioritize preventing wrongful exclusions generally; do not make a “grave/serious consequences” classification a prerequisite for this priority. This supersedes the previous pending urgent/severe-exclusion proposal. Wrongful inclusion and finite resources remain relevant; no numeric error-cost ratio or acceptance/override thresholds are adopted. Do not infer that every exclusion is more harmful than every inclusion, or that a wrongful exclusion automatically justifies an operator reprimand.

The mapping adds a source-supported distinction between **implementation** and **design** exclusion errors (p. 24). A Cashy-reference mismatch is not interchangeable with either category; a reference-compliant decision can still miss actual need. See [[topics/cashy-targeting-context|exclusion taxonomy]]. A generalized error-priority decision does not authorize the operator to change programme criteria or allocate unavailable funds.

## Current next dependency: evidence and operational values

Step 1 remains settled, and the sampling principle was accepted on 2026-10-01. The user then had the Sentinella prototype built before the literature matrix, deliberately. Still open: the literature matrix, which must inform the choice between the variants; operational values for audit proportion, reviewer count, adjudication and alert thresholds, which the prototype sets as demo values; the justification's format and disclosure; the response policy after an alert or a confirmed error; and confidence modeling, still parked.
