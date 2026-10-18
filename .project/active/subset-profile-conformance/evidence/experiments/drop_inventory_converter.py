"""pytest plugin: remove the ExpressionInventoryError converter for the whole session.

Its errors then fall to ``except Exception`` (audit-p12 Advisory 1). Run from the codegen
worktree root:
    PYTHONPATH=.project/active/subset-profile-conformance/evidence/experiments \
    uv run --extra dev pytest -p drop_inventory_converter \
        tests/conformance/subset_profile/test_site_reason_reaches_harness.py -q
"""

import pytest


@pytest.fixture(autouse=True, scope="session")
def _drop():
    from sysml_codegen.orchestration import elaborated_pipeline as ep

    real = ep.ExpressionInventoryError
    ep.ExpressionInventoryError = type("NeverRaised", (Exception,), {})
    yield
    ep.ExpressionInventoryError = real
