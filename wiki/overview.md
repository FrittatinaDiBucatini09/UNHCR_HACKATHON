# Overview

## Event

**Data & Innovation for Refugee Inclusion Hackathon - Advanced Programme** is a University of Trento and UNHCR Innovation initiative in Trento, Italy, running from **30 September to 2 October 2026**. The programme was updated on **23 September 2026**.

The three-day experience begins with a public English-language conversation about AI in humanitarian action. It then moves through challenge reveal, lived experience, data exploration, multidisciplinary teamwork, mentoring, prototyping, pitching, and awards.

## Three-part arc

| Date | Programme phase | Emphasis |
|---|---|---|
| 30 Sep 2026 | Open the conversation | Speck&Tech #88: AI in Humanitarian Action |
| 1 Oct 2026 | Understand + build | Challenge reveal, human context, data exploration, teamwork |
| 2 Oct 2026 | Refine + present | Final build, pitch, jury deliberation, and awards |

The programme intentionally puts people, context, ethics, and operational consequences before rapid solution-building. Teams are expected to produce not only a prototype but an accountable proposition: what it does, why it matters, how it could be used responsibly, and where its limitations remain.

## Revealed challenge

The separately published [[topics/cashy-challenge|Cashy Oversight Challenge]] concerns AI-assisted cash targeting and preserving caseworkers' ability to override wrong recommendations. Its core is **measuring and monitoring appropriate reliance**, not merely improving model accuracy. The [[topics/cashy-experiment|earlier experiment]] observed lower correct-override rates when generic Responsible-AI assurance statements appeared on screen. The released [[topics/cashy-data|S8 dataset]] is synthetic and suited to testing the workflow, not estimating real beneficiary outcomes. [[topics/cashy-submission|Requirements and judging]] describe expected outputs while noting that the final event submission format is not yet verified.

Current user-led design direction: prioritize wrongful exclusions without a severe-harm prerequisite. Confirmed workflow requirements include periodic independent commission review without AI, mandatory operator justification made available to the household in case of problems, case traceability/time, manager comparison against commission assessments and follow-up/peer-review referral capabilities. **Step 1's objectives and reference remain settled.** The user's [[topics/cashy-pipeline-planning|canonical seven-step roadmap and current single question]] remain authoritative. Two paired variants are now explicit but unselected: summary with AI/full-report access at the end, or complete report with AI from the beginning. Current interview dependency is commission sampling across acceptance and override; quantitative settings, severity responses, disagreements and specific checks remain open. Literature synthesis is incomplete; no final UX or code is selected. Confidence modeling remains a doubtful candidate. [[topics/cashy-ethical-guardrails|UN principles]] and [[topics/cashy-targeting-context|UNHCR targeting context]] anchor governance, not behavioral-effectiveness claims.

## Core themes

- AI and data use in humanitarian action.
- Fairness, transparency, explainability, and human oversight in high-stakes contexts.
- Lived experience of forced displacement.
- Responsible interpretation and use of UNHCR data.
- Multidisciplinary problem framing and teamwork.
- Evidence-based prototyping, feedback, impact framing, storytelling, and pitching.

## Navigation

- See [[topics/programme|Detailed programme]] for every scheduled block.
- See [[topics/people-and-organizations|People and organizations]] for all named participants and affiliations.
- See [[topics/design-principles|Design principles]] for the programme's pedagogical and ethical progression.
- See [[topics/venues-and-logistics|Venues and logistics]] for practical information.
- See [[topics/open-questions|Open questions and limits]] before assuming any detail not printed in the programme.

## Provenance

Source: [[sources/unhcr-unitn-hackathon-programme|UNHCR–UniTrento Hackathon Advanced Programme]], especially pages 1-5. Raw evidence: [`raw/UNHCR_Unitn_Hackathon_Programme.pdf`](../raw/UNHCR_Unitn_Hackathon_Programme.pdf).

## Source boundaries

The S8 CSV first located in Downloads is **byte-identical** to the CSV linked from the [[sources/cashy-oversight-challenge-site|challenge site]], and the [[sources/cashy-oversight-challenge-brief|brief]] explicitly identifies it as the challenge sample. Its 1,900 rows are preserved unchanged under `raw/`; [[topics/csv-mini-eda|mini EDA]] stores only macro-level measures. The user's [[sources/cashy-oversight-challenge-site-paste|site paste]], site brief and FAQ are now preserved as separate evidence.

The [[sources/official-hackathon-site|general UniTrento event site]] refers to real-world data and sub-Saharan Africa; the more detailed Cashy brief concerns a Latin American operation and a synthetic release. Do not merge those descriptions into a single unqualified claim. The discrepancy and remaining open items are in [[topics/open-questions|open questions]]. An Excel workbook mentioned earlier in chat is still not available in the workspace or attachments checked to date.
