"""About page: what the prototype measures, on what data, and its limits."""

import streamlit as st

from app import state
from src.sentinella.config import CATEGORIES

demo = state.demo()
included = " and ".join(c for c in CATEGORIES if c in demo.demo_rule.include)
rule = demo.targeted_review
selected = "Cashy recommended " + " or ".join(sorted(rule.recommendations))
if rule.fragility != "none":
    selected += f" on a case one factor level away from another {rule.fragility}"
JUDGMENT_FIRST = {
    "fragile": "after the caseworker's own category on fragile cases",
    "all": "after the caseworker's own category",
    "none": "without asking for the caseworker's own category",
}

st.title("About Sentinella")
st.markdown(
    f"""
Cashy, an AI prototype, recommends whether a household should receive cash
assistance, and a caseworker decides. Sentinella keeps a record of how
caseworkers use Cashy's advice, so that a fall in correct override can be seen
by a named owner before it reaches many households.

### What the data supports, and what it does not

All households are from S8, the synthetic sample released for the challenge.
No record describes a real household, and no result here describes the real
operation, its caseworkers or its offices.

The sample supports the **score and the category**. The recovered Scorecard
formula reproduces the recorded final scores, and its category bands reproduce
1,890 of the 1,900 recorded categories (reports/01_data_exploration.md).

It does not support **eligibility**. Real eligibility depends on funding and on
administrative checks that the sample does not describe. Cashy's
recommendation here follows a demo rule, not the operation's: {included} are
recommended for inclusion, the other categories for exclusion. No model of
eligibility is built or evaluated.

The reference standard is that demo rule applied to the formula category of a
record. It is the standard the prototype holds decisions to, not the truth
about a household's need.

### Three measurement streams, kept apart

**Random audit.** A random {demo.random_audit.fraction:.0%} of decisions on
real cases, accepted and overridden alike, goes to a committee of
{demo.committee.size} that sees only the household's record. It estimates
disagreement with the committee on real cases. It does not establish errors:
the committee can be wrong too.

**Targeted reviews.** Decisions that look risky go to the same blind review:
those where {selected}, and any decision a manager refers with a written
reason. They catch
problems in individual cases. Because they are chosen for risk, they never
enter a rate.

**Sentinels.** About one decision in {1 / demo.sentinels.injection_rate:.0f} is
on a sentinel: a synthetic case whose reference decision is known in advance,
with Cashy's answer concordant with it or deliberately discordant in a way
that can be seen on screen. Sentinels give correct override, over-reliance,
correct acceptance and under-reliance, relative to the reference standard,
continuously. They measure how caseworkers treat Cashy's answer on cases like
these; if their results and the random audit's diverge, the sentinels are not
realistic enough.

Staff are told that their queues contain sentinels. A sentinel never reaches
the committee or the distribution list. After deciding one, the caseworker who
decided it sees its reference decision and what was discordant; nobody else
sees individual sentinel results.

### Decision-time aids and the two workflow variants

The **fragility hint** names the factors whose one-level change would change
the case's category, and which of them would also change the recommendation,
so that the caseworker checks those against the record. **Judgment first**
asks caseworkers for their own category before Cashy's answer.

- **Variant A, summary first.** A summary of the record, with the complete
  record one click away. Cashy's reasoning and answer appear on request,
  {JUDGMENT_FIRST[demo.variants.judgment_first]}.
- **Variant B, Cashy first.** The complete record with Cashy's reasoning and
  answer from the start.

Both show the fragility hint. Each office's caseworkers are split at random
between the variants, so the caseworker is the unit the variants compare.

### Demo values

Every parameter, from the sentinel rate to the alert rule, is a demo value
chosen to run the prototype on S8, not a recommendation for a real operation.
The Monitor lists them all.
"""
)
