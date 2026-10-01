# Wiki log

Chronological record, oldest entry first. Entry format: `## [YYYY-MM-DD] operation | title`.

## [2026-09-28] setup + ingest | UNHCR–UniTrento Hackathon Advanced Programme

- Initialized the project-local LLM Wiki and durable `AGENTS.md` conventions.
- Preserved the supplied PDF unchanged at `raw/UNHCR_Unitn_Hackathon_Programme.pdf`.
- Verified the raw copy against the supplied file by SHA-256; hashes matched.
- Read and visually inspected all 6 pages.
- Added a source page plus canonical pages for the programme, people and organizations, design principles, venues and logistics, and open questions.
- No contradictions were found inside the source. Missing or deferred details were recorded without inference.

## [2026-09-28] lint | Initial wiki integrity check

- Verified that every wikilink and relative Markdown file link resolves.
- Verified that all 8 non-index wiki pages are represented in `wiki/index.md`.
- Rechecked the preserved raw PDF hash: `43944CC4979616EA13DC904EA3D7B79C26FF2EB87359CCB43AB86009F21786C5`.
- Found no broken links, orphan pages, unsupported factual pages, or unacknowledged contradictions.

## [2026-10-01] review + ingest | Recheck wiki and add synthetic CSV

- Re-read all six pages of the immutable programme PDF and all accessible user requests and prior assistant final messages in this chat. The existing programme schedule, people, venue, and design pages remain supported by the PDF.
- Located `S8.synthetic_cashy_sample.csv` in Downloads and preserved all 1,900 rows unchanged under `raw/`; source and raw SHA-256 hashes match.
- Added the source page, aggregate-only mini EDA, and chat decision page. Updated the index, overview, open questions, and project guidance.
- Excel workbook, site URL, and pasted site text mentioned by the user were not available in the accessible chat or project directory. Requested the missing sources; their content has not been guessed.
- The CSV is described as a synthetic sample; no official link to the hackathon dataset is asserted.
- Final link and index check: all 12 wiki pages are indexed or are the index itself; all wikilinks and local Markdown links resolve.

## [2026-10-01] ingest | Official event pages

- Found the dedicated UniTrento hackathon site through the institutional event listing and checked both live pages.
- Added source summaries and a participation/prizes page; updated overview, people, logistics, open questions, chat context, and index.
- Recorded that the sites describe real-world humanitarian data in sub-Saharan Africa, while the local CSV is labeled synthetic; no relationship between them is asserted.
- The user's earlier site paste remains unavailable and has not been conflated with the independently found pages.
- Followed the dedicated site's public-event link and added the Speck&Tech ticket page. It provides a ticket/waiting-list page, a livestream hyperlink, and speaker abstracts. Its title for Breno Elias Valentini's talk differs from the PDF; both titles and the discrepancy are recorded.
- Final check: all 16 wiki pages are indexed or are the index itself; all wikilinks and local file links resolve. Both immutable raw files still match their external originals by SHA-256.

## [2026-10-01] ingest + reconciliation | Cashy challenge site, paste, brief and FAQ

- Preserved the user's pasted Cashy page text unchanged in `raw/` and checked the live challenge page with all expandable sections open. Downloaded the public challenge brief and FAQ DOCX files and preserved unchanged copies; external/local SHA-256 hashes match for all three new raw files.
- Downloaded the S8 CSV linked by the Cashy page and verified its SHA-256 `a9f009737a034c4756003a477365c5dbcdddb96562f329fd4c56c26281fe71c1` exactly matches the previously ingested raw CSV. The brief explicitly names it as the released challenge sample, resolving the prior dataset-provenance uncertainty.
- Added source summaries and canonical pages for the challenge, 26-column data dictionary and limits, earlier experiment and reference results, and participant-facing requirements/judging. Kept the user's CSV mini-EDA boundary; no household-level analysis or modeling was added.
- Corrected the overview, CSV, participation, people, open-questions and chat-context pages and the index where older text said the challenge, paste or CSV connection was unknown. Preserved the unresolved difference between the generic UniTrento event site's sub-Saharan-Africa/real-world-data framing and the Cashy brief's Latin-American/synthetic-data description.
- Recorded the brief's concrete ideal deliverables separately from the FAQ's statement that final submission requirements will be given during the event. The Excel workbook mentioned earlier remains unavailable and was not guessed.

## [2026-10-01] lint | Cashy wiki integration

- Checked all 24 Markdown wiki pages: every Obsidian wikilink and relative local-file link resolves, and every topic/source page is represented in the index. Existing `#` section anchors were checked against their page path rather than misclassified as missing files.
- Searched current pages for stale “challenge unknown / site paste missing / CSV unlinked” statements and corrected the affected current pages; historical log entries remain unchanged as an append-only record.
- Rechecked new raw-source hashes against their downloaded or attached originals. No raw source was edited after copying.
- Recorded an additional within-challenge ambiguity: the brief's synthetic/released-materials-only requirement versus the FAQ's conditional permission to use external datasets. Both claims are retained pending organizer clarification.

## [2026-10-01] query + decision | Understand decision process and focus on challenge two

- Recorded the user's focus on the second challenge, without selecting a solution track on their behalf.
- Checked the raw brief's humanitarian-challenge description, requirements and Annex II screen sequence. Distinguished the incumbent Scorecard process, Cashy prototype and study's blind review/reveal procedure; live deployment is not established.
- Added a canonical process explanation and appropriate-reliance matrix. Recorded the measurement inference that production decision logs alone cannot establish correctness without reference judgments.
- Updated the index, challenge, chat-context and open-questions pages. The raw sources and mini-EDA scope remain unchanged.

## [2026-10-01] planning + research discovery | Grill-me pipeline for challenge two

- Recorded the user's candidate interventions and requested order: evidence and behavioral protocol first, UI/UX next, implementation last.
- Added a provisional roadmap and marked all assistant proposals as pending. Distinguished override frequency, peer agreement, adjudicated correctness and causal claims about AI bias.
- Checked author/university abstract pages for Buçinca et al 2021, Vasconcelos et al 2023 and Green 2022; registered them as preliminary references, not a completed full-text review.
- Began the one-question-at-a-time interview with the dependency of a reference standard on sampled cases. No thresholds, sample sizes, selected interventions or operator judgments have been inferred.

## [2026-10-01] query + planning | Audit size and additional reviewers

- Addressed the user's proposal of one additional reviewer and question about literature-derived audit counts. Checked NIST guidance on sample-size planning.
- Recorded that exact audit counts need a project-specific statistical design; the conditional correct-override metric depends on the number of incorrect AI recommendations identified in the audited subset.
- Recorded a proposed economical protocol of one blinded additional review plus adjudication of disagreements and pilot duplicate reviews on a subset. This is provisional, not an adopted numerical rule or proven reference standard.
- Deferred exact audit proportions, counts and staffing until evidence and design inputs are available; moved the interview to timing of the initial operator judgment relative to AI exposure.

## [2026-10-01] correction + query | Return to objectives and error impact

- Acknowledged that the prior interview question advanced to intervention choice before resolving the step-1 harm priorities. Returned the interview to objectives; AI-first, human-first and hybrid guided checks remain hypotheses for the literature review.
- Rechecked the immutable brief's account of wrongful inclusion, wrongful exclusion, fixed resources and institutional reference standard. No numerical error-cost ratio is supplied.
- Checked the WFP official guidance overview and an indexed excerpt of the UNHCR-WFP joint guidance, section 2.6.1, printed page 41. Direct PDF access failed (429); no full ingest is claimed.
- Recorded the distinction between reference-based error classification and context-dependent severity; institutional guidance supplies a general protection priority without a universal Cashy-specific cost function.
- Updated planning, chat context and index; the user's time-saving concern is retained as a design/evaluation consideration. All final harm weights and intervention choices remain pending.

## [2026-10-01] ingest + decision | UN principles, targeting mapping and manager requirements

- Preserved both user-supplied PDFs unchanged under `raw/`: UN-system ethical AI principles (4 pages) and UNHCR targeting mapping (71 pages). External/local SHA-256 hashes match; all text was read and relevant principles tables/diagrams visually inspected.
- Added source summaries with provenance, dates, coverage and limits. The mapping reports research from 2022; no 2026-current country practices or identity of the Cashy operation were inferred. It remains distinct from the partially accessed UNHCR-WFP joint guidance.
- Added canonical pages for all ten ethical principles, targeting/exclusion context and manager monitoring. Distinguished the study's five assurance statements from the full ten-principle framework, implementation/design exclusions from reference mismatches, and appeals-buffer capacity from audit sampling.
- Recorded accepted user requirements: decision time visible to the manager and priority to wrongful exclusions generally, superseding the earlier serious-consequence prerequisite. Numerical error weights remain open.
- Recorded manager-only uncertainty/selective human review as candidates. Proposed transparent review reasons without a new predictive AI; no calibrated error probability, cutoff, automatic route, audit quota, reviewer staffing or operator sanction was adopted.
- Checked selected official NIST AI RMF/Playbook sections for measurement validity, monitoring, independent review and non-AI alternatives. Registered access scope, not a comprehensive literature review.
- Updated overview, process, submission, planning, chat context, open questions and index. Guided operator-mode selection remains explicitly after evidence review; no UI/system code or further CSV analysis was added.

## [2026-10-01] lint | Additional institutional documents and planning consistency

- Checked all 37 wiki Markdown pages: no broken wikilinks, missing local-file references or unindexed topic/source pages found.
- Rechecked the two new raw PDFs against their supplied originals; matching hashes remained unchanged after wiki edits. The preserved S8 hash also remains unchanged.
- Checked current planning/monitoring/index wording for stale serious-harm prerequisites, unsupported per-case probabilities and automatic sanctions. Historical log entries were preserved; current pages distinguish accepted requirements from proposals and unavailable evidence.

## [2026-10-01] correction + decision | Restore the user's roadmap and active grill-me interview

- Preserved the user's seven-step roadmap as the canonical plan, with broadly justified flexibility rather than silent stage changes; added durable working rules to AGENTS.md.
- Corrected the prior claim that the next work was already the literature review: unresolved step-1 scope/reference choices come first. Source collection is not a completed review; candidate dashboard/protocol ideas are not adopted designs.
- Recorded current step, accepted decisions and remaining dependencies. Parked intervention choices under step 3 and quantitative audit/uncertainty/alert design under step 4.
- Resumed one-question-at-a-time interviewing with a recommendation about existing-rule correctness versus criteria revision; no user answer or additional solution choice has been inferred.
- Updated planning, overview, chat context and index. Raw sources and CSV mini-EDA scope remain unchanged.

## [2026-10-01] correction + maintenance | Step 1 settled; resume operator-flow interview

- Rechecked Karpathy's original LLM Wiki gist and the local implementation: immutable raw sources, linked Markdown wiki, index, append-only log and project AGENTS.md are already established. Maintained the existing wiki rather than rebuilding or installing unrelated tools.
- The user explicitly corrected the prior assistant status: objectives/reference are already defined. Marked step 1 settled and withdrew the criteria-revision question; no unspoken answer or policy redesign was inferred.
- Recorded the current alternatives: guided view/summary of all fields versus full form, AI score/explanation at beginning versus end, and required full-case access at least at the end. Pairing and operator actions remain unresolved.
- Updated project guidance, planning, overview, index, chat context and open questions so the latest user correction takes precedence over stale assistant status. Numerical audit/uncertainty design stays in step 4; no final protocol/UI, model or code added.
- Continued grill-me with one question about readable summary versus explicit guided evidence checks; recommendation is a candidate for research, not an effectiveness claim. The seven-step roadmap and mini-EDA boundary remain unchanged.

## [2026-10-01] lint | Remove stale objectives status

- Checked all 37 wiki pages for broken wikilinks: none found. Re-read the updated current-state block and project guidance.
- Verified that current planning, index and overview no longer instruct reopening step 1. Earlier log/chat entries are preserved as historical context and explicitly superseded by the latest correction.

## [2026-10-01] query + planning | Concrete guided-check selection, not placeholders

- Addressed the user's objection that unspecified guided checks are not a presentable protocol and that they lack the evidence to choose them.
- Rechecked the immutable Cashy brief's humanitarian/model description, complete Annex I field meanings, Annex II case profiles and Annex III questions. No CSV analysis, row selection or modeling was performed.
- Recorded a proposed method linking documented failures, exact evidence, operator question/action, domain validation and later pilot assessment; separated what literature can establish from eligibility-policy content.
- Added three concrete, provisional evidence-support checks: factual narrative consistency, correct non-applicability handling, and support for exclusion reasons. Disclosed unavailable narratives/rulebook, after-AI timing, no automatic override and no proven behavioral benefit.
- Rechecked the Vasconcelos author abstract and official NIST guidance; no full literature review claimed. Harvard's Buçinca publication-page request failed, so no new full-text evidence was inferred.
- Updated planning/current question, chat context, open questions, source access note and index. Step 1 stays closed; no user selection, operational approval, UI or code inferred.

## [2026-10-01] lint | Concrete-check planning consistency

- Checked all 37 Markdown wiki pages: no broken wikilinks found.
- Re-read the current planning block and index; proposed checks remain explicitly provisional, operational rules and source narratives remain unavailable, and step 1 stays settled.

## [2026-10-01] decision + maintenance | User reconstructs the complete review workflow

- Recorded user-confirmed requirements: periodic independent commission review without AI advice; mandatory operator case justification made available to the household in case of problems; case traceability/time; manager comparison against commission assessments; follow-up and manual peer-review referral capabilities.
- Replaced the earlier pairing ambiguity with the user's two explicit candidates: summary followed by AI score/explanation and full-report access at the end, versus full report with AI from the beginning. Neither variant, concrete guided checks nor preliminary human judgment is selected.
- Preserved reviewer count, sampling, adjudication, severity response, dashboard metrics, justification format and doubtful confidence modeling as open nodes. One serious error versus repeated lesser errors is a hypothesis, not a selected threshold or automatic sanction.
- Moved the current single interview question to random audit across acceptance and override, with separate targeted review; this is an assistant recommendation awaiting approval. Explained the step-4 measurement dependency without reopening step 1 or claiming the literature review complete. Parked rulebook/mentor availability, not falsely answered.
- Rechecked official NIST sample-size and AI RMF pages for existing methodological context; no universal audit count or Cashy-specific trigger inferred. No additional CSV analysis, source edits, UI or code.
- Updated planning, monitoring, open questions, chat context, overview, index and project guidance, preserving prior log history and unrelated content.

## [2026-10-01] lint | Reconstructed workflow and interview state

- Checked all 37 wiki Markdown pages: no broken wikilinks, missing local references or unindexed pages.
- Re-read current planning, monitoring and project guidance; confirmed commission/justification requirements and explicit paired variants are consistent. Earlier chat/log statuses remain historical and superseded.
- Verified the current question is sampling coverage, not the parked rulebook-access question. Raw sources and CSV mini-EDA scope were not changed.

## [2026-10-01] maintenance | Handoff exported to Windows temporary directory

- At the user's explicit handoff request, read the handoff skill and exported `%TEMP%/unhcr-cashy-handoff-2026-10-01-audit-workflow.md`, outside the workspace as required by the skill.
- Referenced canonical wiki pages instead of copying the full plan; included suggested skills and the precise unanswered sampling question. The handoff request does not approve random-plus-targeted sampling or make any new protocol decision.
- Re-read the exported document and checked its 11 project-file references: all exist. No participant names, beneficiary-level records or credentials included.
- Wiki content/status and index remain unchanged because no project knowledge changed; only this append-only export record was added. Raw sources and mini-EDA scope were preserved.

## [2026-10-01] maintenance + lint | Wiki-only ZIP for colleague

- The user requested a ZIP of the complete project wiki, excluding raw files, for sharing with a colleague.
- Checked the export scope: 37 files, all Markdown, with no symbolic/reparse-point items and no broken internal wikilinks.
- Archive target: `unhcr-wiki-2026-10-01.zip` in the workspace. Package only the `wiki/` directory, preserving its index, log, topic pages, source summaries and relative structure; no original documents or datasets from `raw/`.
- References to raw evidence are preserved as provenance, but their target documents are intentionally absent from this wiki-only export.
- No project decision, source content or analysis changed; the index remains current. This entry records the export request, scope and pre-packaging checks.
