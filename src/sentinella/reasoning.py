"""Template text for Cashy's reasoning panel, built from the inputs Cashy used.

It stands in for the reasoning engine's narrative: it states the household, the
factor scores the answer was computed from and the conclusion, so that each of
these can be checked against the record on screen.
"""

from collections.abc import Mapping

from src.data_dictionary import ENGLISH_NAMES, FACTORS, NOT_APPLICABLE
from src.sentinella.schema import INCLUDE

SOLE_CARER = {
    "Yes": "The head is the sole carer of dependents.",
    "No": "The head is not the sole carer of dependents.",
}
SPEAKS_SPANISH = {
    "One or more adults": "One or more adults speak Spanish.",
    "No adult": "No adult speaks Spanish.",
}
ADULT_ILLITERACY = {
    "No adult": "Every adult can read.",
    "One or more adults": "One or more adults cannot read.",
}


def reasoning(
    record: Mapping[str, object],
    factors: Mapping[str, float],
    final_score: float,
    category: str,
    recommendation: str,
) -> str:
    """Reasoning text for one household.

    Args:
        record: Household fields with English labels, as in schema.household_record.
        factors: The eight factor scores the text says were used.
        final_score: Final score the text states.
        category: Vulnerability category the text states.
        recommendation: Demo recommendation the text states, Include or Exclude.
    """
    used = ", ".join(
        f"{ENGLISH_NAMES[factor].lower()} {factors[factor]:.2f}" for factor in FACTORS
    )
    outcome = "inclusion" if recommendation == INCLUDE else "exclusion"
    return " ".join(
        [
            household_summary(record),
            f"Factor scores used: {used}.",
            f"Final score {final_score:.1f}, category {category}.",
            f"Under the demo rule, {category} is recommended for {outcome}.",
        ]
    )


def household_summary(record: Mapping[str, object]) -> str:
    """Sentences describing the household attributes in the record."""
    size = record["NumIntegrantes"]
    head = record["FemaleHeadedHousehold"]
    opening = f"Household of {size} {'person' if size == 1 else 'people'}"
    if head != NOT_APPLICABLE:
        opening += f", {str(head).lower()}"
    sentences = [opening + "."]
    if record["CuidadorSolo"] != NOT_APPLICABLE:
        sentences.append(SOLE_CARER[record["CuidadorSolo"]])
    sentences += [
        f"Dependency ratio: {str(record['dependencyCategory']).lower()}.",
        SPEAKS_SPANISH[record["HablaEspanol"]],
        ADULT_ILLITERACY[record["Analfabeta_si"]],
    ]
    return " ".join(sentences)
