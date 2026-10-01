"""Annex I data dictionary as code: column groups, English labels, documented counts."""

DEMOGRAPHIC_FACTORS = [
    "Demographics.HH.Head",
    "Demographics.Language",
    "Demographics.Profiles",
    "Demographics.Documentation",
]
NEEDS_FACTORS = [
    "Needs_and_Coping.BasicNeeds",
    "Needs_and_Coping.Housing",
    "Needs_and_Coping.Neg.mechanism",
    "Needs_and_Coping.Dependency",
]
FACTORS = DEMOGRAPHIC_FACTORS + NEEDS_FACTORS
HOUSEHOLD_ATTRIBUTES = [
    "NumIntegrantes",
    "dependencyCategory",
    "FemaleHeadedHousehold",
    "CuidadorSolo",
    "HablaEspanol",
    "Analfabeta_si",
]
ADMIN_FLAGS = ["ScoreCOMAR_PIL", "ScoreIntenciones", "ScoreDuplicidad"]
INTERVIEW_RECORD = ["month", "OficinaACNUR"]
AGGREGATED_SCORES = [
    "FinalScore",
    "Demographics_Score",
    "NeedsandCoping_Score",
    "Vulnerability_Score",
    "Vulnerability_Category",
]
OUTCOMES = ["EligibilityTarget", "Elegibilidad"]

COLUMN_GROUPS = {
    "Scorecard factor score": FACTORS,
    "Household attribute": HOUSEHOLD_ATTRIBUTES,
    "Administrative flag": ADMIN_FLAGS,
    "Interview record": INTERVIEW_RECORD,
    "Aggregated score": AGGREGATED_SCORES,
    "Outcome": OUTCOMES,
}

ENGLISH_NAMES = {
    "month": "Month",
    "Elegibilidad": "Eligibility status",
    "Vulnerability_Category": "Vulnerability category",
    "Demographics.HH.Head": "Head of household",
    "Demographics.Language": "Language barrier",
    "Demographics.Profiles": "Specific needs",
    "Demographics.Documentation": "Documentation",
    "Needs_and_Coping.BasicNeeds": "Basic needs",
    "Needs_and_Coping.Housing": "Housing",
    "Needs_and_Coping.Neg.mechanism": "Negative coping",
    "Needs_and_Coping.Dependency": "Dependency",
    "OficinaACNUR": "UNHCR field office",
    "NumIntegrantes": "Household size",
    "dependencyCategory": "Dependency category",
    "FemaleHeadedHousehold": "Sex of household head",
    "CuidadorSolo": "Sole carer",
    "HablaEspanol": "Speaks Spanish",
    "Analfabeta_si": "Adult illiteracy",
    "ScoreCOMAR_PIL": "Asylum procedure flag",
    "ScoreIntenciones": "Intentions flag",
    "ScoreDuplicidad": "Duplicate flag",
    "Demographics_Score": "Demographics score",
    "NeedsandCoping_Score": "Needs and coping score",
    "Vulnerability_Score": "Vulnerability index",
    "FinalScore": "Final score",
    "EligibilityTarget": "Eligibility target",
}

NOT_APPLICABLE = "Not applicable"
OFFICE_BLANK = "Blank"

# English labels in their display order; blanks get their own label.
VALUE_LABELS = {
    "Elegibilidad": {
        "Elegible": "Eligible",
        "Elegible por Proceso Acelerado": "Eligible, accelerated process",
        "Lista de Reserva": "Waiting list",
        "No Elegible": "Not eligible",
        "No Elegible por Intenciones": "Not eligible, stated intentions",
        "No Elegible por Duplicidad": "Not eligible, duplicate registration",
    },
    "Vulnerability_Category": {
        "Vulnerabilidad Baja": "Low",
        "Vulnerabilidad Moderada": "Moderate",
        "Vulnerabilidad Elevada": "High",
        "Vulnerabilidad Severa": "Severe",
    },
    "EligibilityTarget": {"INCLUSION": "Inclusion", "EXCLUSION": "Exclusion"},
    "dependencyCategory": {
        "low": "Low",
        "average": "Average",
        "high": "High",
        "complete": "Complete",
    },
    "FemaleHeadedHousehold": {
        "jefatura_femenina": "Female-headed",
        "jefatura_masculina": "Male-headed",
    },
    "CuidadorSolo": {"si": "Yes", "no": "No"},
    "HablaEspanol": {
        "espanol_uno_mas_adultos": "One or more adults",
        "espanol_ningun_adulto": "No adult",
    },
    "Analfabeta_si": {
        "adultos_ninguno_analfabeta": "No adult",
        "adultos_uno_mas_analfabeta": "One or more adults",
    },
    "ScoreCOMAR_PIL": {-500: "-500", 0: "0", 500: "+500"},
    "ScoreIntenciones": {-500: "-500", 0: "0"},
    "ScoreDuplicidad": {-500: "-500", 0: "0"},
}
BLANK_LABELS = {
    "FemaleHeadedHousehold": NOT_APPLICABLE,
    "CuidadorSolo": NOT_APPLICABLE,
    "ScoreCOMAR_PIL": NOT_APPLICABLE,
    "OficinaACNUR": OFFICE_BLANK,
}
CATEGORY_ORDER = list(VALUE_LABELS["Vulnerability_Category"])

# Value counts as printed in Annex I; None stands for a blank cell.
DOCUMENTED_COUNTS = {
    "EligibilityTarget": {"INCLUSION": 427, "EXCLUSION": 1473},
    "Elegibilidad": {
        "Elegible": 414,
        "Elegible por Proceso Acelerado": 13,
        "Lista de Reserva": 451,
        "No Elegible": 932,
        "No Elegible por Intenciones": 52,
        "No Elegible por Duplicidad": 38,
    },
    "Vulnerability_Category": {
        "Vulnerabilidad Baja": 775,
        "Vulnerabilidad Moderada": 394,
        "Vulnerabilidad Elevada": 612,
        "Vulnerabilidad Severa": 119,
    },
    "dependencyCategory": {"low": 1148, "average": 610, "complete": 94, "high": 48},
    "FemaleHeadedHousehold": {
        "jefatura_femenina": 484,
        "jefatura_masculina": 491,
        None: 925,
    },
    "CuidadorSolo": {"si": 373, "no": 602, None: 925},
    "HablaEspanol": {"espanol_uno_mas_adultos": 1622, "espanol_ningun_adulto": 278},
    "Analfabeta_si": {
        "adultos_ninguno_analfabeta": 1664,
        "adultos_uno_mas_analfabeta": 236,
    },
    "ScoreCOMAR_PIL": {0: 771, -500: 155, 500: 14, None: 960},
    "ScoreIntenciones": {0: 1844, -500: 56},
    "ScoreDuplicidad": {0: 1852, -500: 48},
    "OficinaACNUR": {
        "sotap": 1278,
        "fupal": 190,
        "foten": 186,
        "pcr_cdmx": 127,
        "futij": 47,
        "fomon": 36,
        "fusal": 15,
        None: 21,
    },
}

# Factor levels as printed in Annex I (rounded to two decimals).
DOCUMENTED_FACTOR_LEVELS = {
    "Demographics.HH.Head": (1.0, 1.60, 2.07, 2.70),
    "Demographics.Language": (1.0, 1.53, 2.05),
    "Demographics.Profiles": (1.0, 1.25, 2.58, 3.25),
    "Demographics.Documentation": (1.0, 1.56, 2.13),
    "Needs_and_Coping.BasicNeeds": (1.0, 1.78),
    "Needs_and_Coping.Housing": (1.0, 1.50, 2.12, 2.82),
    "Needs_and_Coping.Neg.mechanism": (1.0, 1.79, 2.58),
    "Needs_and_Coping.Dependency": (1.0, 1.04, 1.74, 2.54),
}

# Documented ranges and means of the numeric columns: (min, max, mean).
DOCUMENTED_RANGES = {
    "FinalScore": (0.0, 81.1, 27.7),
    "Demographics_Score": (0.0, 43.8, 8.1),
    "NeedsandCoping_Score": (0.0, 50.0, 20.1),
    "Vulnerability_Score": (2.0, 4.34, 2.80),
}

# The two "Elegible" statuses make up INCLUSION (Annex I).
INCLUSION_STATUSES = ("Elegible", "Elegible por Proceso Acelerado")
