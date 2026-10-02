"""Small, deterministic presentation helpers; no eligibility model or new AI."""

import pandas as pd

from src.data_dictionary import ENGLISH_NAMES
from src.sentinella import casework

DEMO_CASES = 15


def case_list(book: casework.Casebook, office: str) -> pd.DataFrame:
    """Fifteen stable cases: number 2 is a sentinel, number 3 is human-first.

    This is a curated presentation queue, not the operational sampling policy.
    Internal case/sentinel identifiers never appear in its public labels.
    """
    real = book.queue[book.queue["office"] == office].sort_values(["month", "case_id"])
    rows = real.head(DEMO_CASES - 1).to_dict("records")
    if len(rows) != DEMO_CASES - 1:
        raise ValueError(
            "The presentation needs fourteen cases in the selected office."
        )
    sentinel = next((s for s in book.pool.values() if not s.concordant), None)
    if sentinel is None:
        raise ValueError("The presentation needs a discordant sentinel.")
    rows.insert(
        1,
        {"case_id": sentinel.sentinel_id, "office": office, "month": rows[0]["month"]},
    )
    result = pd.DataFrame(rows)
    result["number"] = range(1, DEMO_CASES + 1)
    result["flow"] = [
        "human-first" if n == 3 else "summary-first" for n in result["number"]
    ]
    return result


def case_label(number: int, done: bool) -> str:
    return f"Case {number:02d} — {'Completed' if done else 'To review'}"


def score_only_reasoning(text: str) -> str:
    """Remove only the template's explicit eligibility recommendation.

    Keep factual claims and discrepancies unchanged; rebuilding the narrative
    from the answer would erase reasoning-inconsistency sentinels.
    """
    return text.split("Under the demo rule,", maxsplit=1)[0].strip()


def checks(case_id: str, book: casework.Casebook) -> pd.DataFrame:
    """Source values of locally sensitive factors, not an operational checklist."""
    return pd.DataFrame(
        [
            (
                ENGLISH_NAMES[f],
                book.records[case_id][f],
                "Verify against source evidence",
            )
            for f in casework.hint_factors(case_id, book)
        ],
        columns=["Factor to verify", "Recorded value", "Action"],
    )
