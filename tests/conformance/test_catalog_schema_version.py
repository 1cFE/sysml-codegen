"""Item 8: CATALOG_SCHEMA_VERSION is a deliberately-bumped pin, embedded in the contract.

Mirrors the ``TRUSTED_VERIFIER_SHA256`` drift-guard shape: a literal pin plus a test, so a
schema-shape change that forgets to bump the token (and re-vendor the accepted set in TEAx)
fails loudly here rather than shipping a silent skew. Cross-repo agreement rests on this
constant plus manual re-vendoring — B3 forbids TEAx importing this repo, so no automated
cross-repo check is possible from here (the TEAx side owns ``ACCEPTED_CATALOG_SCHEMA_VERSIONS``).
"""

from __future__ import annotations

from sysml_codegen.contracts.versions import CATALOG_SCHEMA_VERSION


def test_catalog_schema_version_is_the_reviewed_pin():
    # Bumping this is a deliberate act: it means the embedded-catalog schema shape changed and
    # the TEAx-vendored accepted set has been updated in lockstep. 2.0.0 is the Item-8 shape
    # (admitted-usage tier + five projected entry fields).
    assert CATALOG_SCHEMA_VERSION == "2.0.0"


def test_catalog_schema_version_rides_the_model_contract_payload():
    """The token sits inside the fingerprinted payload, so a bump moves semantic_fingerprint."""
    from sysml_codegen.contracts.model_contract import build_model_contract
    from sysml_codegen.resolution.models import ComputationGraph

    graph = ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])
    contract = build_model_contract(graph)
    assert contract.catalog_schema_version == CATALOG_SCHEMA_VERSION
