# Cashy requirements, outputs, judging and FAQ

## Design requirements in the challenge brief

The brief says designs should **ideally** meet these participant-facing requirements; they are not instructions for this wiki maintainer:

1. Use the synthetic sample and released materials only; do not link or re-identify households, caseworkers or offices. Present S8 results as synthetic-file properties.
2. Keep AI reasoning and answer separate on screen and record a caseworker judgment of each rather than one generic “agree”.
3. Report correct override, over-reliance, correct acceptance and under-reliance for concordant and discordant cases, with Wilson or equivalent confidence intervals; an overall agreement rate is insufficient.
4. Name the institutional determination as the reference standard and acknowledge it is not ground truth about need.
5. Account for repeated assessments per caseworker; use participant-level or clustered analysis and report a prospective minimum detectable effect, not post-hoc power.
6. If modeling, document the model (model card expected), report inclusion and exclusion recall separately, and explain what available features cannot support.

Every submission should identify where a wrong recommendation would be caught, avoid identifying the small professional caseworker population, and acknowledge the household's absence from/limited ability to contest the decision. The challenge cites protection, accountability to affected populations, inclusion, fairness, transparency, data responsibility and do-no-harm. Sources: [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-faq|FAQ]].

Additional background supplied by the user: [[topics/cashy-ethical-guardrails|full UN-system ethical AI framework]] and [[topics/cashy-targeting-context|UNHCR targeting mapping]]. These do not change the published challenge submission format. The user's requirement to show decision time to the manager and proposed uncertainty/review mechanism are **project design inputs**, not newly discovered organizer requirements; see [[topics/cashy-manager-monitoring|manager monitoring]].

## Outputs: separate the two source statements

The **brief's ideal deliverables** are a code repository with README, a five-minute demo of workflow/measurement/institutional view, and a two-page note covering a pre-specified contrast, outcome measure, needed sample, and the meaning of positive/negative results. The **FAQ and site event section** say final submission requirements will be announced during the event and teams should expect a prototype/concept/framework, short presentation or pitch, documentation and impact-measurement explanation. Thus the brief gives a concrete target, but the final binding format is **not verified**. Sources: [[sources/cashy-oversight-challenge-brief|brief]], [[sources/cashy-oversight-challenge-faq|FAQ]], [[sources/cashy-oversight-challenge-site|site]].

## Judging

| Criterion | Weight | Published emphasis |
|---|---:|---|
| Challenge | 25% | Humanitarian problem and meaningful human oversight |
| Novelty | 20% | Originality and innovation |
| Community impact | 20% | Affected populations, users, responsible AI |
| Solution | 35% | Feasibility, scalability, usability, implementation potential |

The challenge poser additionally weighs fidelity to the research question, rigor of reliance measurement, separate reasoning/answer assessment, practical fit with KoboToolbox/Python/Power BI, do-no-harm, cost/maintainability and reproducibility. Technical sophistication alone earns no automatic advantage. Sources: [[sources/cashy-oversight-challenge-site|site]], [[sources/cashy-oversight-challenge-faq|FAQ]], [[sources/cashy-oversight-challenge-brief|brief]].

## FAQ clarifications

- Multidisciplinary teams are welcome; programming/data-science skill is not a prerequisite. Model improvement is optional; governance, process, research, dashboard and design ideas may qualify. A deployed enterprise product is not required in 48 hours.
- The FAQ says external datasets may be used if their contribution is explained and privacy, security, licensing and ethics are addressed. **This conflicts or at least needs reconciliation with the brief's “work exclusively on S8 and released materials” requirement above**; see [[topics/open-questions|open questions]] before treating outside household data as permitted. Generative AI use is allowed with disclosure, awareness of limits, accountability and responsible-use safeguards; it is not a judging bonus.
- The FAQ anticipated roughly 50 participants, organizers/technical/UNHCR mentors and dedicated Q&A. This is a planning estimate, not a final headcount.
- The site's dates, venue and registration fields are literal TODO placeholders. For verified event details, use [[topics/programme|programme]] and [[topics/venues-and-logistics|logistics]].

Sources: [[sources/cashy-oversight-challenge-faq|FAQ]], [[sources/cashy-oversight-challenge-site|site]].

## Contacts and scope

The [[sources/cashy-oversight-challenge-brief|brief]] lists **Moises Maldonado Alonso**, AI and Data Science Lead at UNHCR Innovation (`maldonam@unhcr.org`), as contact. The site also lists **Breno Valentini** (`valentib@unhcr.org`) as digital-innovation challenge poser. See [[topics/people-and-organizations|people and organizations]] for the programme's different name/role labels. No team, presentation or upload action has been undertaken by this wiki.
