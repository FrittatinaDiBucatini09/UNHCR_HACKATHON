"""Current presentation workflow and its measurement limits."""

import streamlit as st

from app import state

demo = state.demo()
st.title("About Sentinella")
st.markdown(
    f"""
This is an unofficial hackathon prototype for the Cashy Oversight Challenge,
not an operational UNHCR service. All case records come from the released
synthetic S8 sample, not actual households.

### Current caseworker demonstration

One demonstration operator has **15 selectable cases**, labelled pending or
completed. The usual flow is a structured household summary, source-record
access, optional opening of AI score/category and explanation, then a human
Include/Exclude decision with a mandatory justification.

**Case 02** is an engineered sentinel. Its identity is disclosed only after
submission. **Case 03** demonstrates a human-first alternative: an initial
Include/Exclude decision and justification must be saved before unlocking AI.
The final assessment is separate and may confirm or change the initial one.
This example is not a validated experiment or a selected operational policy.

The summary uses deterministic templates, not another generative AI. The factor
checks are local sensitivity examples under the demo score/category formula;
they are not a validated eligibility checklist or global feature importance.
The available record contains household attributes and factor scores, not
the full operational questionnaire or all administrative evidence.

### Manager and independent review

The dashboard separates **illustrative mock**, **entered app decisions** and
the optional legacy simulated year. Mock decisions, assessments and timings
are invented presentation examples, never real activity or observed performance.
Time includes pauses and is not a measurement of attention.

The commission sees source case evidence without AI advice. Random audit and
targeted/manual review remain separate. Commission disagreement does not itself
establish an operator error, and no automatic disciplinary action is adopted.

### Important metric limitation

The AI panel includes score, category, explanation and an Include/Exclude
recommendation. Acceptance
and override compare the final human decision with that displayed recommendation.
Correctness requires a separate reference, and the prototype's eligibility rule
is only a **demo rule**, not the actual operation's eligibility criteria.
Operational eligibility cannot be recovered from score and vulnerability category alone.

The existing {demo.random_audit.fraction:.0%} audit setting and
{demo.committee.size}-member commission are demonstration parameters, not
recommended operational numbers. The presentation's one
sentinel in fifteen cases is curated, not the configured operational injection
rate. A full literature review and evaluation protocol are still pending.
"""
)
