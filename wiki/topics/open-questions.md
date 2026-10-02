# Open questions and limits

These are details not yet resolved across the available sources. The programme PDF alone did not specify the challenge, but the later [[sources/cashy-oversight-challenge-site|Cashy site]] and [[sources/cashy-oversight-challenge-brief|brief]] now do. Do not preserve the earlier “challenge unknown” state as current knowledge.

## Challenge and data

- The exact challenge and released S8 CSV are now documented under [[topics/cashy-challenge|Cashy challenge]] and [[topics/cashy-data|Cashy data]]. The PDF scheduled a 1 October reveal, while the challenge page is publicly accessible; the wiki does not infer when the page was first published or what was actually revealed in the room.
- The challenge sources mention supplementary S1–S7 and S9 materials **where released**, but they are not in the checked workspace. Their availability, access rules and licenses remain unverified.
- The operation's expected stack (KoboToolbox, Python, Power BI) is stated; exact hackathon accounts, infrastructure, API access, security controls and submission platform are not.
- The challenge brief specifies privacy and measurement guardrails. Operational approval/deployment procedures and actual household recourse or appeal mechanisms are not established.
- Cashy is described as a prototype. The simplified website chain does not establish live deployment. A production correct-override monitor would require reference judgments in addition to decision logs; the sources do not specify how independent reference judgments would be obtained for live cases. See [[topics/cashy-decision-process|decision process]].
- The user confirms an independent commission without AI advice for periodic review of a subset of decisions. A random audit across acceptance and override, with separate targeted review, was confirmed on 2026-10-01, and the prototype's committee is blind to the first decision. Operational reviewer count, audit proportion, disagreement resolution and reference authority remain open; the Sentinella prototype uses demo values. See [[topics/cashy-pipeline-planning|planning and ordered open nodes]].
- Manager visibility of time, case traceability, comparison against commission assessments, operator follow-up after serious errors and manual peer-review referral capabilities are confirmed. Timing definitions, dashboard metrics, minimum sample, attribution, severity thresholds and what a “richiamo” entails remain open. One serious error versus repeated lesser errors is a hypothesis, not a selected response rule. A confidence indicator/model remains doubtful and uncalibrated; no automatic disciplinary policy is adopted. See [[topics/cashy-manager-monitoring|manager monitoring]].
- Objectives/reference (step 1) remain settled. The user now explicitly pairs two research candidates: summary first with AI score/explanation and full-report access at the end; or complete report with AI score/explanation from the beginning. On 2026-10-02 the user delegated their definitions for the prototype: a summary of every recorded field and a preliminary judgment on fragile cases in A, the fragility hint in both, with caseworkers split at random between them. Which variant serves oversight better is untested, and the literature synthesis is not complete. Every operator must write a case justification, to be made available to the household in case of problems; format, timing and disclosure safeguards are unresolved. See [[topics/cashy-pipeline-planning|planning]].
- Staff are told that their queues contain sentinels (2026-10-02). Whether that knowledge changes how caseworkers treat real cases is untested; comparing sentinel reliance with the random audit is the prototype's check.
- Specific guided checks are not selected. The supplied S8 dictionary is not the complete operative questionnaire or full eligibility rulebook. Three proposed evidence-support checks can be specified from existing meanings, but narrative checks require released/simulated AI narratives and occur after AI reveal. Access to operative rules or UNHCR expert validation for this team is unknown; this question is parked rather than answered or made a blocker for sampling discussion. The user's earlier objection still rules out presenting an unspecified checklist as a finished protocol; see [[topics/cashy-pipeline-planning|check-selection proposal]].
- **Cross-source discrepancy:** the general [[sources/official-hackathon-site|UniTrento event site]] describes real-world data about vulnerable populations in sub-Saharan Africa; the [[sources/cashy-oversight-challenge-brief|Cashy brief]] describes a Latin American cash-targeting operation and releases synthetic S8 data. These may be different levels of event framing or a changed/parallel challenge, but no source explains the relationship. Ask organizers which description applies to the task being judged; do not infer that S8 represents sub-Saharan Africa or real individuals.
- **Within-challenge tension on external data:** the [[sources/cashy-oversight-challenge-brief|brief's design requirements]] and [[sources/cashy-oversight-challenge-site|site requirements]] say to work exclusively on S8 and released materials; the [[sources/cashy-oversight-challenge-faq|FAQ]] and site FAQ say external datasets can be used if documented and ethically safe. The permission may refer to non-household contextual data, but that distinction is not stated. Before adding external data to a submission, obtain organizer clarification on its scope.

## Participation and teams

- Who are the participants and students on the lived-experience panel?
- Actual participant/team count is unknown. The [[sources/cashy-oversight-challenge-faq|FAQ]] says approximately 50 participants were expected, a planning assumption.
- What are the actual teams and disciplines represented? The [[topics/participation-and-prizes|official site]] allows pre-formed teams or individual applications matched into teams, but does not list the final composition.
- What materials participants must bring is not specified. The site says there are no technical prerequisites and that some data-analysis experience is helpful.

## Judging and outputs

- A rubric is published in [[topics/cashy-submission|submission and judging]]. The brief proposes a repository/README, five-minute demo and two-page note, while the FAQ says **final submission requirements will be shared during the event**. The actual binding format, deadline, upload channel and pitch length remain unverified.
- Who comprises the complete jury? Daniele Miorandi and Giorgio Comai are explicitly listed as jury members, but completeness is not claimed.
- Are there awards beyond the dedicated site's stated one-year *Internazionale* subscription for the winning team?
- Will prototypes, presentations, data, or code be published, licensed, or retained?

## Logistics

- The linked [[sources/speckandtech-ticket-page|Speck&Tech ticket page]] provides a livestream hyperlink redirecting to the Speck&Tech YouTube live channel; stream availability was not confirmed.
- Are Thursday/Friday attendance and meals restricted to registered participants?
- Are accessibility, travel, parking, room, Wi-Fi, emergency-contact, or accommodation details available?
- What are the Day 2 lunch arrangements?

## Source status

- The source calls itself an **Advanced Programme** and says it was updated 23 September 2026; it does not explicitly say “final programme.”
- No contradiction was found among the PDF's own dates, times, venues, people, or affiliations during ingest.
- **Cross-source discrepancy:** the PDF lists Breno Elias Valentini's Day 0 talk as *How Humanitarian Organizations are using AI: opportunities, risks, and emerging practice*. The linked Speck&Tech ticket page calls it *From responsible AI to humanitarian impact: designing digital solutions for refugee response*. This may reflect a later title change, but neither source dates that change. Check with organizers before treating one as final.
- “Three-day initiative” includes Day 0 (30 September), Day 1 (1 October), and Day 2 (2 October); this is consistent with the cover's date range.
- The user's [[sources/cashy-oversight-challenge-site-paste|paste]] and linked [[sources/cashy-oversight-challenge-site|site]] are now available. The site was checked with all expandable panels open. Its DOCX brief and FAQ were downloaded and preserved. The Excel workbook mentioned in the earlier request remains unavailable in the checked workspace and current attachments; no Excel-specific facts have been invented.
- The `S8.synthetic_cashy_sample.csv` download from the site is byte-identical to the preserved raw CSV; the brief supplies its [[topics/cashy-data|dictionary and generation limits]]. Its macro-level description remains in [[topics/csv-mini-eda|mini EDA]].
- Both additional user PDFs are now unchanged local evidence: [[sources/un-system-ethical-ai-principles|UN-system principles]] (4 pages) and [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR mapping]] (71 pages). The latter describes research from 2022, not verified current country procedures. It is a different source from the 2018 joint guidance, whose full ingest remains pending.

## Source

[[sources/unhcr-unitn-hackathon-programme|programme]], [[sources/official-hackathon-site|general event site]], [[sources/cashy-oversight-challenge-site|Cashy site]], [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-faq|FAQ]], and the user's [[sources/cashy-oversight-challenge-site-paste|paste]].

Additional context and project decisions: [[sources/un-system-ethical-ai-principles|UN AI principles]], [[sources/unhcr-targeting-and-prioritization-mapping|UNHCR mapping]], [[topics/chat-context|user statements]].
