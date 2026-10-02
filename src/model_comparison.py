"""Metrics, resampling and cross-validation for comparing score models.

A candidate is a function (train, test) -> predicted final scores for test, so
the recovered formula and fitted models are evaluated the same way.
"""

from collections.abc import Callable, Iterable

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import (
    max_error,
    mean_absolute_error,
    r2_score,
    root_mean_squared_error,
)

from src import scorecard
from src.data_dictionary import VALUE_LABELS

TARGET = "FinalScore"
SCORE_METRICS = {
    "r2": r2_score,
    "mae": mean_absolute_error,
    "rmse": root_mean_squared_error,
    "max_abs_error": max_error,
}
Candidate = Callable[[pd.DataFrame, pd.DataFrame], np.ndarray]


def fitted_candidate(
    make_model: Callable[[], object], features: Callable[[pd.DataFrame], pd.DataFrame]
) -> Candidate:
    """Candidate that fits a fresh scikit-learn style model on each training set."""

    def fit_predict(train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
        model = make_model().fit(features(train), train[TARGET])
        return model.predict(features(test))

    return fit_predict


def predicted_category(predicted: np.ndarray, index: pd.Index) -> pd.Series:
    """English vulnerability category of predicted final scores."""
    category = scorecard.score_category(pd.Series(predicted, index=index))
    return category.map(VALUE_LABELS["Vulnerability_Category"])


def score_metrics(test: pd.DataFrame, predicted: np.ndarray) -> dict[str, float]:
    """The SCORE_METRICS of the predicted final scores, plus category accuracy.

    The category accuracy compares the band of the predicted score with the
    category recorded in the English frame from `dataset.to_english`.
    """
    observed = test[TARGET].to_numpy()
    metrics = {
        name: metric(observed, predicted) for name, metric in SCORE_METRICS.items()
    }
    category = predicted_category(predicted, test.index)
    recorded = test["Vulnerability_Category"].astype(str)
    metrics["category_accuracy"] = (category == recorded).mean()
    return metrics


def cross_validate(
    candidates: dict[str, Candidate],
    data: pd.DataFrame,
    splits: Iterable[tuple[np.ndarray, np.ndarray]],
) -> pd.DataFrame:
    """Metrics of every candidate on every (train positions, test positions) split."""
    rows = []
    for fold, (train_rows, test_rows) in enumerate(splits):
        train, test = data.iloc[train_rows], data.iloc[test_rows]
        for name, fit_predict in candidates.items():
            metrics = score_metrics(test, fit_predict(train, test))
            rows.append({"candidate": name, "fold": fold, **metrics})
    return pd.DataFrame(rows)


def bootstrap_interval(
    statistic: Callable[[np.ndarray, np.ndarray], float],
    observed: np.ndarray,
    predicted: np.ndarray,
    n_resamples: int,
    seed: int,
) -> tuple[float, float]:
    """Percentile bootstrap 95% interval of statistic, resampling households."""
    result = stats.bootstrap(
        (np.asarray(observed), np.asarray(predicted)),
        statistic,
        paired=True,
        vectorized=False,
        n_resamples=n_resamples,
        method="percentile",
        rng=np.random.default_rng(seed),
    )
    return float(result.confidence_interval.low), float(result.confidence_interval.high)
