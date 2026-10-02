# Manager monitoring: time, review priority and uncertainty

## Status and provenance

Source of requirements: user's **2026-10-01** background-document message and latest end-to-end workflow reconstruction. Institutional background: [[sources/un-system-ethical-ai-principles|UN AI principles]], [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR mapping]] and [[sources/nist-ai-rmf-measurement|NIST measurement guidance]]. Explicit user requirements are marked below; remaining design details are **proposals**, not a tested system or requirements specified by those sources.

- **Accepted requirement:** decision time is fundamental and must be visible to the manager/dashboard. The Sentinella prototype shows recorded time from opening a case to submitting the decision, for decisions entered in the app, labelled as not a measure of attention (2026-10-02).
- **Accepted requirement:** trace each case/request and show operator performance compared with assessments by an independent commission that receives no AI advice. Commission reviewer count, frequency, case-selection policy and disagreement resolution are not fixed.
- **Accepted requirement:** manager can follow up with an operator after a serious error and manually refer cases to peer review. What “richiamo” entails, error confirmation, responsibility and disciplinary procedure remain open; this is not an automatic punishment rule.
- **Accepted requirement:** operators must write a case justification, made available to the household in case of problems. Its form, timing and disclosure safeguards remain open; see [[topics/cashy-pipeline-planning|operator protocol]].
- **Accepted harm priority:** the user accepts option A's priority on wrongful exclusions, but removes the proposed restriction to cases with “serious consequences.” Numerical weights, inclusion/resource limits and definitions still need refinement.
- **Candidate:** manager-only per-decision uncertainty/review indicator, potentially routing high-priority cases to another human. No scoring method, cutoff or automatic route is accepted yet.
- **Concern:** do not assume an additional predictive AI is necessary; the user worries about complexity and an additional source of performance degradation. This is a concern, not evidence that any extra model necessarily worsens outcomes.
- **Unresolved:** review quotas/staffing, adjudication authority, severity-trigger policy, exact manager response and guided operator workflow. An extra confidence model remains a doubtful candidate; no calibrated error probability or additional predictive AI is adopted.

## Independent commission: what the dashboard can claim

User-confirmed architecture: periodically reviewed cases receive independent human assessments without AI advice. Commission size and who may participate remain open. Hiding the initial operator decision and justification from the reviewer was adopted for the prototype on 2026-10-01: the committee sees the household record only. Independent commission assessment and ad hoc peer-review referral are distinct functions; neither automatically resolves disagreements.

Until the reference/adjudication protocol is specified, a disagreement is a **disagreement**, not a confirmed operator error. Show reviewed case counts, unresolved disagreements and the reference status alongside comparison metrics. Only a suitably confirmed reference can support labels such as reviewed error or correct override, and shared errors can remain even after agreement. Commission-based assessment does not establish universal truth about actual household need.

Sampling exclusively from overrides would omit potentially wrong acceptance of AI advice. Override itself is not an error: it can be correct or incorrect; acceptance can likewise be correct or incorrect. A random audit spanning both actions, with separate targeted review, was **confirmed on 2026-10-01**. See [[topics/cashy-pipeline-planning|planning]].

## Time: what should be measured

Proposed definitions, pending instrumentation and validation:

| Quantity | Intended meaning | Important limit |
|---|---|---|
| Recorded active review time | Time spent in the case-review task, with pauses/idle periods handled explicitly | Screen-open duration is not verified cognitive attention; do not overstate telemetry |
| Elapsed decision time | Case opening/assignment to submitted decision, with start point documented | Can include interruptions, queues and other work |
| Total case resolution delay | Assignment to completed decision, including any second review/appeal | Captures household delay and review capacity, not only first operator speed |
| Additional review burden | Time spent on second review, evidence collection and adjudication | Needed to assess whether first-stage speed is offset elsewhere |

Show case-level timings and team/operator distributions with case count, task/complexity and time window. Median and upper-percentile summaries are candidate displays, not fixed requirements. Compare audited outcomes and workload alongside time. A very fast or slow decision is an investigative signal, **not proof** of negligence, correctness or automation bias. No minimum reading time, productivity target or time-based sanction is selected.

## “Uncertainty” is not one measured object

| Candidate signal | What it actually measures | Availability/limit |
|---|---|---|
| Operator-reported doubt/confidence | Subjective judgment | Requires collecting it; not automatically a calibrated probability; operator necessarily knows their own input |
| Missing, outdated or contradictory evidence | Evidence quality or incomplete verification | Transparent rule checks possible if the necessary fields/evidence exist; each flag must give a reason |
| Sensitivity to unresolved evidence/rule boundaries | Decision fragility under documented plausible alternatives | Needs actual policy/rule access; vulnerability-score proximity alone may not describe eligibility |
| Model confidence/uncertainty, if available | Properties of the model prediction | Not uncertainty of the final human decision; calibration and access are not established |
| Independent reviewers' disagreement | Consistency of judgments on reviewed cases | Only known after additional review; agreement is not proof of correctness |
| Confidence interval for an operator-level rate | Sampling uncertainty of an aggregate estimate | Not an uncertainty value for each individual decision |

Do not combine these into an unexplained numerical percentage. A statistical interval on an override rate does not solve the case-level measurement problem.

## Recommended starting hypothesis: reason-based review priority, no new predictive AI

For an initial prototype, test a transparent set of **review reasons** rather than assert P(final decision incorrect). Candidate reasons include unresolved evidence, operator-requested help, and a decision relying on an unverified eligibility-critical fact. Their exact definition and weights must come from the applicable policy, literature and operational validation, not fabricated from S8 correlations. Use explicit “not assessed / insufficient information” states; absence of flags does not mean low error probability.

The internal review-priority display would be manager-only as proposed by the user. It should not conceal decision reasons or recourse from the household. The manager can inspect the reason and request a blinded second review; any automatic routing, whether it happens before a decision takes effect, and how it avoids unacceptable delays remain to be decided.

An actual probability claim would require defined reference judgments and validation/calibration on suitable audited cases. Observed error frequencies for a case group can be estimated statistically without a new predictive model, if counts and sampling support it, but are not an exact per-case probability. S8 synthetic labels cannot establish production calibration or human attention effects.

## Random audit plus targeted review

Sampling principle, confirmed on 2026-10-01: retain a random audit alongside targeted review because confident/unflagged decisions may also be wrong. Include acceptance and override; preserve selection reason/probability and distinguish audit from targeted queues. A raw error rate from targeted suspicious cases is not the population rate. Quantities, reviewer count and selection policy remain open in [[topics/cashy-pipeline-planning|audit planning]].

Manager follow-up and manual peer-review referral capabilities are now **user-confirmed**. Proposed response details, not adopted: confirm facts, distinguish AI/data/policy/operator contributors, correct the household decision where authorized, and consider coaching or process repair. A single outlier or disagreement does not establish operator misconduct. Formal disciplinary decisions need a separately defined fair governance procedure; no automatic reprimand is specified.

## Error impact and review triggers: open response policy

Latest user hypothesis: a single high-impact error might trigger immediate review, while lesser errors might require repetition. This has **not** established a severity definition, count, time window or automatic response. It changes the possible step-4 response policy; it does not reopen step 1's general priority to wrongful exclusions.

Distinguish three actions before selecting thresholds:

1. **Review the household case:** a serious signal may justify prompt verification and authorized remediation; it is not already proof of operator error.
2. **Review the operator's wider work:** one confirmed serious event or a pattern of lesser confirmed errors could motivate an expanded audit/coaching review. This is a candidate, not a selected trigger.
3. **Discipline:** neither a suspected error nor commission disagreement automatically warrants a reprimand. Attribution, policy, evidence and managerial authority remain to be specified.

The dashboard should not silently equate severity, error certainty and operator responsibility. Less severe detected errors still need case correction when appropriate; “accumulate before broader review” must not mean “leave those household decisions unaddressed.” Serious signals also cannot be assumed detectable on unaudited cases without a defined reporting/flag mechanism. Severity can prioritize follow-up, but is not a substitute for unbiased audit coverage.

## Literature-review questions before UX

1. Which guided verification tasks identify eligibility-relevant errors without requiring a redundant complete review?
2. How do AI-first, independent-human-first and guided-checks-before-AI compare on correct override, correct acceptance, time and sustained attention?
3. Do self-reported confidence or transparent review flags identify useful review subsets; what errors do they miss?
4. What audit/adjudication design supports reference judgments and stable monitoring given reviewer capacity?
5. How should alerts lead to household remedy and process improvement without encouraging gaming or suppressing doubt?

These questions operationalize the next [[topics/cashy-pipeline-planning|research stage]], not a completed literature review or selected UX.

## Sentinella prototype: what the manager sees

Built on 2026-10-02 (see the [[log|log]]). Every number below is a demo value, not an operational choice.

- **Alerts per office:** correct override on discordant sentinels over 4 months; an alert opens when the upper end of its 95% interval falls below 87.5% with at least 5 decisions. Only the named owner, the office manager, can close it, with a written explanation; a closed alert can reopen from the next month if the rule still fires.
- **Operator view:** only the office manager sees their own caseworkers compared with the committee on the random audit, accepted and overridden apart, with intervals. There are no flags and no sanction follows. Across many caseworkers, about one interval in twenty excludes the office's rate by chance.
- **Hidden cells:** aggregates and the monitoring exports hide cells that rest on fewer than 3 caseworkers. The exports are aggregate tables, plus the alert log and the distribution list.
- **Sentinels:** staff are told that queues contain sentinels. Only the caseworker who decided one sees its reference decision; the manager sees sentinel results by office, category, direction and variant, not by person.
- **Known limit:** an office alert from a window in which only one or two caseworkers decided sentinels describes those caseworkers.
