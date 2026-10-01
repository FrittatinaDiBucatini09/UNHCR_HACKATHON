"""Writers for the report tables, figures and headline numbers."""

import json

import matplotlib.pyplot as plt
import pandas as pd

from src.dataset import REPO_ROOT
from src.plot_style import FIGURE_DPI

REPORTS_DIR = REPO_ROOT / "reports"
TABLES_DIR = REPORTS_DIR / "tables"
FIGURES_DIR = REPORTS_DIR / "figures"
KEY_STATS_PATH = REPORTS_DIR / "key_stats.json"


def save_table(table: pd.DataFrame, name: str) -> pd.DataFrame:
    """Write table to reports/tables/<name>.csv and return it for display."""
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(TABLES_DIR / f"{name}.csv", index=False)
    return table


def save_figure(fig: plt.Figure, name: str) -> None:
    """Write fig to reports/figures/<name>.png."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=FIGURE_DPI)


def update_key_stats(section: str, stats: dict) -> None:
    """Replace one section of key_stats.json and keep the other sections."""
    current = json.loads(KEY_STATS_PATH.read_text()) if KEY_STATS_PATH.exists() else {}
    current[section] = stats
    # default= converts numpy scalars, which json cannot serialise.
    text = json.dumps(current, indent=2, default=lambda value: value.item())
    KEY_STATS_PATH.write_text(text + "\n")
