"""Item 8 handoff gate (INV-8): deterministic catalog fingerprint across repeated live loads.

Not a live/snapshot parity gate — a current snapshot cannot carry constraint facts until
Item 8 (snapshot v3). This is the determinism property Item 8 needs to build that parity on:
two independent fresh live loads of the same constraint-bearing fixture must fingerprint
identically.
"""

from __future__ import annotations

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license


@requires_license
def test_catalog_fingerprint_deterministic_across_repeated_live_loads():
    a = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    b = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    catalog_a = a.computation_graph.constraint_catalog
    catalog_b = b.computation_graph.constraint_catalog
    assert catalog_a is not None and catalog_b is not None
    assert catalog_a.fingerprint == catalog_b.fingerprint
    assert [e.constraint_id for e in catalog_a.concrete_entries] == [
        e.constraint_id for e in catalog_b.concrete_entries
    ]


@requires_license
def test_catalog_fingerprint_differs_for_different_models():
    a = build_pipeline_context(
        [FIXTURES_DIR / "wi014_toy"], lower_constraints_enabled=True
    )
    b = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    catalog_a = a.computation_graph.constraint_catalog
    catalog_b = b.computation_graph.constraint_catalog
    assert catalog_a is not None and catalog_b is not None
    assert catalog_a.fingerprint != catalog_b.fingerprint
