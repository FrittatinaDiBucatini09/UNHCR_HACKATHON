# UNHCR Hackathon knowledge index

Persistent knowledge layer for the **Data & Innovation for Refugee Inclusion Hackathon**, University of Trento and UNHCR Innovation, Trento 2026.

## Start here

- [[overview|Overview]] - Scope, key dates, operating frame, and the document's central narrative.
- [[topics/programme|Detailed programme]] - Complete chronological agenda from Day 0 through Day 2.
- [[topics/people-and-organizations|People and organizations]] - All named people, roles, affiliations, and programme involvement.
- [[topics/design-principles|Design principles]] - The event's stated learning and solution-development logic.
- [[topics/venues-and-logistics|Venues and logistics]] - Locations, access details, meals, streaming, and closing times.
- [[topics/open-questions|Open questions and limits]] - Information explicitly absent, intentionally deferred, or ambiguous.
- [[topics/csv-mini-eda|CSV mini EDA]] - Aggregate profile of the synthetic CSV: coverage, outcomes, scores, and missing values.
- [[topics/chat-context|Chat context and decisions]] - User instructions and relevant prior answers, with source boundaries.
- [[topics/participation-and-prizes|Participation and prizes]] - Eligibility, team formation, language, registration, contact, and stated award from official event pages.
- [[topics/cashy-challenge|Cashy Oversight Challenge]] - Problem, Cashy prototype, two questions and six solution tracks.
- [[topics/cashy-decision-process|Decision process and challenge two]] - Existing Scorecard process, Cashy prototype, experiment, appropriate reliance and the user's current focus.
- [[topics/cashy-pipeline-planning|Pipeline planning and research]] - **Read first for chat state:** latest confirmed workflow, mandatory justification, two paired operator variants and ordered doubts; random audit across acceptance and override confirmed, Sentinella prototype built with both variants defined for it. Step 1 settled; canonical roadmap retained.
- [[topics/cashy-manager-monitoring|Manager monitoring]] - Confirmed AI-free commission, case/time tracking, comparison and follow-up/referral capabilities, random audit plus targeted review; Sentinella's demo alert rule and operator view; severity triggers, reference limits and confidence modeling remain open.
- [[topics/cashy-ethical-guardrails|Ethical guardrails]] - Ten UN-system AI principles, project interpretations and distinction from persuasive assurance banners.
- [[topics/cashy-targeting-context|Targeting and exclusion context]] - Implementation versus design exclusions, contextual methods, resources, appeals and country-case map.
- [[topics/cashy-data|Cashy S8 data and dictionary]] - Verified source identity, 26-column map, synthetic-data and modeling boundaries.
- [[topics/cashy-experiment|Cashy experiment]] - Thirty-one-caseworker trial, five reference cases, reliance decomposition and uncertainty.
- [[topics/cashy-submission|Cashy requirements and judging]] - Participant-facing guardrails, expected outputs, FAQ clarifications and rubric.

## Sources

- [[sources/unhcr-unitn-hackathon-programme|UNHCR–UniTrento Hackathon Advanced Programme]] - Six-page programme, updated 2026-09-23; complete ingest of schedule, people, locations, and design principles.
- [[sources/s8-synthetic-cashy-sample|S8 synthetic cashy sample]] - Full immutable CSV and its provenance; analytical detail is restricted to the requested mini EDA.
- [[sources/official-hackathon-site|Official hackathon site]] - Dedicated UniTrento site, checked 2026-10-01, with participation, mentorship, and prize details.
- [[sources/unitn-event-listing|UniTrento event listing]] - Institutional listing, checked 2026-10-01, with registration deadline and organizing committee.
- [[sources/speckandtech-ticket-page|Speck&Tech ticket page]] - Public opening event, access and livestream links, speaker abstracts, and a talk-title discrepancy with the PDF.
- [[sources/cashy-oversight-challenge-site|Cashy challenge site]] - Live page checked with all expandable sections open, including dictionary, experiment, FAQ, resources and rubric.
- [[sources/cashy-oversight-challenge-site-paste|User's Cashy site paste]] - Immutable attached text; distinguish from expandable live-site content.
- [[sources/cashy-oversight-challenge-brief|Cashy challenge brief]] - Full public DOCX with Annexes I–IV and experiment instruments.
- [[sources/cashy-oversight-challenge-faq|Cashy FAQ]] - Public DOCX with participation, data, solution, evaluation and submission clarifications.
- [[sources/bucinca-2021-cognitive-forcing|Buçinca et al 2021]] - Preliminary abstract review: cognitive forcing, overreliance and user-rating trade-off.
- [[sources/vasconcelos-2023-explanation-verification|Vasconcelos et al 2023]] - Preliminary abstract review: explanation verification costs and reliance.
- [[sources/green-2022-institutional-oversight|Green 2022]] - Preliminary abstract review: limits of nominal human oversight and institutional responsibility.
- [[sources/nist-sample-size-planning|NIST sample-size planning]] - Statistical guidance for relating audit size to precision and available resources; no Cashy-specific numerical setting.
- [[sources/unhcr-wfp-targeting-guidance|UNHCR–WFP targeting guidance]] - Context-sensitive targeting and error-impact priorities; overview and indexed section excerpt checked, full PDF ingest pending.
- [[sources/un-system-ethical-ai-principles|UN-system ethical AI principles]] - Complete 4-page CEB/2022/2/Add.1 framework, all ten principles and lifecycle/affected-person safeguards.
- [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR targeting mapping]] - Complete 71-page report, research from 2022, contextual approaches, exclusion taxonomy and country cases; not the joint guidance.
- [[sources/nist-ai-rmf-measurement|NIST measurement and monitoring]] - Selected official AI RMF/Playbook sections on proxy validity, independent review, monitoring and non-AI alternatives.

## Maintenance

- [[log|Wiki log]] - Append-only history of ingests, decisions, maintenance, and lint passes.

## Coverage status

- Sources ingested: 11 (programme PDF, synthetic CSV, dedicated event site, UniTrento listing, Speck&Tech ticket page, Cashy live site, user's site paste, Cashy brief and FAQ, UN ethical AI principles PDF and UNHCR targeting mapping PDF)
- Additional research sources registered: 3 publication/abstract records; these have not yet received a full-text literature-review ingest.
- Additional methodological reference: NIST sample-size planning guidance, checked for the audit-sizing question.
- Institutional targeting guidance checked for harm prioritization: official WFP overview and indexed UNHCR–WFP section excerpt; no full PDF ingest claimed.
- Additional official monitoring reference: selected NIST AI RMF Core and Playbook sections; not a full framework/Playbook ingest.
- PDF text coverage: 81 of 81 pages (programme 6, ethical principles 4, targeting mapping 71). Programme visually inspected in full; the added principles table and mapping's relevant diagrams were visually checked.
- CSV rows retained in `raw/`: 1,900 of 1,900; wiki stores only aggregate mini EDA, plus the source-provided data dictionary. The site's CSV download is byte-identical to this source.
- Known source discrepancy: Breno Elias Valentini's Day 0 talk title differs between the PDF and the linked ticket page; see [[topics/open-questions|open questions]]
- General UniTrento event framing (sub-Saharan Africa/real-world data) and detailed Cashy brief (Latin America/synthetic S8) differ; see [[topics/open-questions|open questions]].
- Excel workbook mentioned earlier: not present in the checked workspace or current attachments as of 2026-10-01. The user's Cashy site paste and linked materials are now ingested.
- Open or missing details: tracked in [[topics/open-questions|Open questions and limits]]
