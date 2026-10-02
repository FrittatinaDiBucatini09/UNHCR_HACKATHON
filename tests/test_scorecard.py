"""Tests of the recovered Scorecard formula on the whole S8 synthetic sample."""

import pytest

from src import scorecard
from src.data_dictionary import DEMOGRAPHIC_FACTORS, NEEDS_FACTORS
from src.dataset import DATA_PATH, load_sample

# Block scores and the index are stored with nine decimals; the final score was
# built from block weights rounded to six decimals.
STORED_TOLERANCE = 1e-6
FINAL_TOLERANCE = 1e-4


@pytest.mark.skipif(
    not DATA_PATH.exists(), reason="S8 data file not present; see data/README.md"
)
def test_formula_reproduces_recorded_scores_on_s8():
    sample = load_sample()
    computed = {
        "Demographics_Score": scorecard.block_score(sample[DEMOGRAPHIC_FACTORS]),
        "NeedsandCoping_Score": scorecard.block_score(sample[NEEDS_FACTORS]),
        "Vulnerability_Score": scorecard.vulnerability_index(sample),
    }
    for column, values in computed.items():
        assert values.to_numpy() == pytest.approx(
            sample[column].to_numpy(), abs=STORED_TOLERANCE
        ), column
    assert scorecard.final_score(sample).to_numpy() == pytest.approx(
        sample["FinalScore"].to_numpy(), abs=FINAL_TOLERANCE
    )
