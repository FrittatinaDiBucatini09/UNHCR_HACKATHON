"""Chart builders shared by several report figures."""

import textwrap

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter

from src.data_dictionary import NOT_APPLICABLE, OFFICE_BLANK
from src.plot_style import BLUE, INK_SECONDARY, MUTED, SURFACE

# Drawn in gray so that a structural blank does not read as a substantive level.
BLANK_LEVELS = (NOT_APPLICABLE, OFFICE_BLANK)


def plot_counts(ax: plt.Axes, counts: pd.Series, label_values: bool = True) -> None:
    """Columns of counts per level, with structural blanks in gray."""
    labels = [str(level) for level in counts.index]
    positions = np.arange(len(labels))
    colors = [MUTED if label in BLANK_LEVELS else BLUE for label in labels]
    ax.bar(positions, counts.to_numpy(), width=0.6, color=colors)
    ax.set_xticks(positions, [textwrap.fill(label, 14) for label in labels])
    if label_values:
        for x, value in zip(positions, counts.to_numpy()):
            ax.annotate(
                f"{value:,}",
                (x, value),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=12,
                color=INK_SECONDARY,
            )
    ax.margins(y=0.15)


def plot_rates(ax: plt.Axes, rates: pd.DataFrame, reference: float) -> None:
    """Rate per group with its Wilson 95% interval, against a reference rate.

    Expects the columns of `descriptive.rate_table`. Hollow markers flag groups
    with fewer than 30 households.
    """
    positions = np.arange(len(rates))
    rate = rates["rate"].to_numpy()
    small = rates["small_group"].to_numpy()
    ax.axhline(
        reference,
        color=MUTED,
        linewidth=1,
        zorder=1,
        label=f"All households, {reference:.1%}",
    )
    ax.vlines(
        positions, rates["ci_low"], rates["ci_high"], color=BLUE, linewidth=2, zorder=2
    )
    marker = {"s": 90, "linewidth": 2, "zorder": 3}
    ax.scatter(positions[~small], rate[~small], color=BLUE, edgecolor=SURFACE, **marker)
    if small.any():
        ax.scatter(
            positions[small],
            rate[small],
            color=SURFACE,
            edgecolor=BLUE,
            label="Fewer than 30 households",
            **marker,
        )
    ax.legend(loc="upper right")
    labels = [f"{group}\nn={n:,}" for group, n in zip(rates["group"], rates["n"])]
    ax.set_xticks(positions, labels)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0, decimals=0))
    # Headroom above the highest interval keeps the legend clear of the data.
    ax.set_ylim(0, rates["ci_high"].max() * 1.35)
    ax.margins(x=0.08)
