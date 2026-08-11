"""Real TEAx execution evidence for live and relocated Fusion Tea packages."""

from pathlib import Path

import pytest

from scripts.measure_item7_acceptance import run_real_teax_acceptance

pytestmark = pytest.mark.execution

CANDIDATE_DIR = Path("/tmp/elaborator-cutover-item7-candidate")


def test_real_teax_executes_both_verified_public_packages() -> None:
    evidence = run_real_teax_acceptance(CANDIDATE_DIR)

    assert evidence["packages"] == ["live", "relocated"]
    assert evidence["trusted_verifier_agreement"] is True
    assert evidence["public_registry"] is True
    assert evidence["lcoe_matches"] is True
    assert evidence["c25_every_and_only"] is True
    assert evidence["c2_every_and_only"] is True
