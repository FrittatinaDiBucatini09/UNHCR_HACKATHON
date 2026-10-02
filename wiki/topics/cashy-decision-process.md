# Cashy decision process and challenge two

## Existing operation, prototype and experiment

The brief describes three distinct layers. The incumbent operational instrument is an expert-designed Scorecard completed during registration interviews. Cashy is an AI decision-support prototype built in KoboToolbox. The randomized experiment tested that prototype on previously decided cases. The simplified chain on the challenge website is useful for understanding the intended AI-assisted workflow, but does not establish that Cashy is currently deployed in live cash decisions. Source: [[sources/cashy-oversight-challenge-brief|brief, humanitarian challenge and Annex II]], [[sources/cashy-oversight-challenge-site|site]].

The incumbent process starts with household information and interviewer observations; the Scorecard scores demographics, needs and coping and applies administrative checks. It produces a vulnerability category and eligibility determination. A caseworker's targeting assessment determines inclusion or exclusion. Funding constrains assistance and prioritization, so vulnerability alone does not establish receipt of cash. The sources do not fully specify all operational thresholds, approval roles or timing of budget allocation. Household need and the institution's eligibility determination are separate concepts.

The separately ingested [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR mapping]] adds institutional background, not proof of this operation's exact process. It distinguishes implementation exclusions from design exclusions and shows contexts combining scorecards, protection assessments, appeals and panels. A second person applying the same rule can miss needs that the rule itself omits. See [[topics/cashy-targeting-context|targeting context]]; do not identify Cashy with any named country case study without a source.

In the prototype, an AutoGluon model predicts score, category and eligibility, while a separate LLM writes a narrative about the case. The narrative should not be presumed to explain the actual computations of the tabular prediction model. A human assesses the recommendation and can accept or override it. The study screen presented the registration record, reasoning, generic assurance panels in one arm, answer, and assessment items. The recorded institutional determination was withheld until after submission, then revealed for a second decision. This reveal is an experiment/audit procedure, not a documented standard live workflow. See [[topics/cashy-experiment|experiment]].

## What challenge two asks for

The source asks teams to design, measure and monitor appropriate reliance: help caseworkers override incorrect AI advice, preserve appropriate acceptance of correct advice, and make weakening oversight visible to the institution. The target is selective judgment, not a larger override count. “Correct” in the supplied evaluation means agreement with the operation's recorded determination; it is not proof of the household's true need.

| AI against reference | Human accepts | Human overrides |
|---|---|---|
| AI agrees with institutional determination | Correct acceptance | Under-reliance |
| AI conflicts with institutional determination | Over-reliance | Correct override |

The correct-override rate uses discordant cases as its denominator. A production log of acceptance and override alone cannot identify which overrides are correct: it also needs a reference judgment. This is a measurement inference from the definitions, not a source claim that an independent live adjudication system already exists. A design should specify how audited cases obtain a reference, how many cases remain unevaluated, and who reviews concerning trends. Without that, a dashboard can show override frequency but cannot demonstrate appropriate reliance.

Possible scoped contributions from the brief are a review interface, an audit toolkit, a monitoring dashboard, governance procedures or a research design. A coherent submission should explain its intervention, the behavior it measures, its comparator or confirmatory contrast, and the institutional response. Teams do not have to implement every track. The [[topics/cashy-submission|submission page]] records ideal outputs and unresolved final event requirements.

## User focus

On 2026-10-01 the user stated they are working mainly on the second challenge and asked to understand the existing decision process before interpreting the task. This is the current project focus; no specific solution track has yet been selected. Source: user statement in this chat, recorded also in [[topics/chat-context|chat context]].

The user subsequently accepted wrongful exclusions as the protection priority, without a separate severe-harm condition, and requires decision time in the institutional/manager view. A manager-only review-priority/uncertainty indicator remains a hypothesis; routine logs still do not establish decision correctness. See [[topics/cashy-manager-monitoring|manager monitoring]] and [[topics/cashy-pipeline-planning|planning]].
