"""Loading of the S8 synthetic sample and its English labelling."""

from pathlib import Path

import pandas as pd

from src.data_dictionary import BLANK_LABELS, VALUE_LABELS

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = REPO_ROOT / "data" / "S8.synthetic_cashy_sample.csv"


def load_sample(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the sample as published, with blank cells left missing."""
    return pd.read_csv(path)


def to_english(df: pd.DataFrame) -> pd.DataFrame:
    """Copy with Spanish values translated and blanks as an explicit category.

    Translated columns become ordered categoricals so that tables and figures
    keep the dictionary order. Offices are ordered by number of interviews.
    """
    out = df.copy()
    for column, labels in VALUE_LABELS.items():
        values = df[column].map(labels)
        unknown = df[column].notna() & values.isna()
        if unknown.any():
            found = sorted(df.loc[unknown, column].astype(str).unique())
            raise ValueError(f"{column} has values outside the dictionary: {found}")
        order = list(labels.values())
        if column in BLANK_LABELS:
            values = values.fillna(BLANK_LABELS[column])
            order.append(BLANK_LABELS[column])
        out[column] = pd.Categorical(values, categories=order, ordered=True)
    offices = df["OficinaACNUR"].value_counts().index.tolist()
    out["OficinaACNUR"] = pd.Categorical(
        df["OficinaACNUR"].fillna(BLANK_LABELS["OficinaACNUR"]),
        categories=offices + [BLANK_LABELS["OficinaACNUR"]],
    )
    return out
