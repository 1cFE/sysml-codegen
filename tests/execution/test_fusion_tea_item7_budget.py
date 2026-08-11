"""Customer-scale budget evidence for the accepted Item 7 authority."""

from pathlib import Path

import pytest

from scripts.measure_item7_acceptance import measure_fusion_tea_acceptance

pytestmark = pytest.mark.execution

CANDIDATE_DIR = Path("/tmp/elaborator-cutover-item7-candidate")


def test_fusion_tea_warmup_and_three_measured_runs_meet_budgets() -> None:
    evidence = measure_fusion_tea_acceptance(CANDIDATE_DIR)

    assert evidence["warmup_runs"] == 1
    assert len(evidence["measurements"]) == 3
    assert evidence["stable_counts_and_digests"] is True
    assert evidence["all_budgets_met"] is True
