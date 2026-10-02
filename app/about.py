"""Current presentation workflow and its measurement limits."""

import streamlit as st

from app import brand, state

demo = state.demo()
st.title("About Sentinella", icon=":material/info:")
st.markdown(
    f"""
This is an unofficial hackathon prototype for the Cashy Oversight Challenge,
not an operational UNHCR service. All case records come from the released
synthetic S8 sample, not actual households. The UNHCR logo marks the
challenge the prototype answers; it does not mean UNHCR endorses the
prototype.

### Officer workspace

One demonstration officer has **15 cases**, chosen from a dropdown by case
number; a check mark shows the cases whose final decision is recorded. The
usual flow is a structured household summary, source-record
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

The dashboard shows either the **simulated year**, in which simulated
caseworkers and a simulated committee follow the demo values, or the
**decisions entered in the app**. The two are never pooled, and neither
describes a real operation. Alerts close only with a written explanation from
their named owner. Time includes pauses and is not a measurement of attention.

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
st.caption(brand.NOTICE)
