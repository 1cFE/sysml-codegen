"""Supplementary public nodes for lifecycle-remediation Item 1.

Added 2026-07-19 during audit remediation. These live in their own file, and use their
own new fixture directories, because the Phase 0 surface in
`test_constraint_occurrence_demand_acceptance.py` is the RED/GREEN byte anchor: its
SHA-256 must stay `aea7c821...eacb624b` so the recorded RED failures and the candidate's
GREEN passes provably used identical bytes.

Same-checkout replay assertions here are regression evidence; they do not certify
relocation or the composed artifact thread.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from tests.conftest import FIXTURES_DIR, requires_license

ROOT = FIXTURES_DIR / "constraint_occurrence_demand"


@requires_license
def test_r5_indirect_cycle_is_atomic_on_the_public_route() -> None:
    """OD-A05's `A -> B -> A` variant, on the public construction route.

    The stable `cycle/` fixture models only the self-cycle, so the indirect variant the
    approved design specifies (`design.md:598`) had no public proof — only a unit-level
    one over a mock index. This closes that half on the real route.
    """
    with pytest.raises(CodeGenerationError) as caught:
        build_pipeline_context([ROOT / "cycle_indirect"])

    cause = caught.value.__cause__
    assert type(cause).__name__ == "RecursiveContainmentError"
    assert cause.requested_owner_qn == "OccurrenceDemandCycleIndirect__A"
    assert cause.cycle_path == (
        "OccurrenceDemandCycleIndirect__A",
        "OccurrenceDemandCycleIndirect__B",
        "OccurrenceDemandCycleIndirect__A",
    )
    # Closing edge per the design's (owning_definition_qn, feature_name,
    # target_definition_qn) field definition: A contains `b : B`.
    assert cause.edge_owner_qn == "OccurrenceDemandCycleIndirect__A"
    assert cause.edge_feature_name == "b"
    assert cause.edge_type_qn == "OccurrenceDemandCycleIndirect__B"
