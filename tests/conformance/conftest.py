"""Conformance test configuration and fixtures.

Provides:
- Marker registration (req, baseline)
- Session-scoped extraction snapshot fixtures
- Per-model convenience fixtures
"""

from __future__ import annotations

import pytest

from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture


def offline_input_sources(model_name: str) -> dict[tuple[str, str], object]:
    """Build a fixture's ComputationGraph offline (license-free) and return a map
    from ``(module_name, param_name)`` to that input's ``InputSource``.

    Used by the stage-(b) companion-fixture conformance tests (Item 10) to assert
    whether a consumer input is currently an entry point (the incomplete pin) or
    wired to an upstream producer channel (post Phase-7 resolver). Reads only the
    committed extraction snapshot, so it needs no syside license.
    """
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(model_name))
    return {
        (m.name, inp.param_name): inp.source
        for m in ctx.computation_graph.modules
        for inp in m.inputs
    }

# All models with extraction snapshots
SNAPSHOT_MODELS = [
    "sample_model",
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
    "issue22_model",
    "expression_binding_probe",
    "chain_override_probe",
    "unresolvable_attr_probe",
    "alias_agg_probe",
    # Plant-idiom conformance fixtures (Item 8, UPSTREAM-FINDINGS).
    "wi014_toy",
    "ife_plant",
    "self_named_binding_trap",
    # Plant-Value & Blind-Spot fixtures (PIPELINE-TRUTH Item 1).
    "plant_values",
    "plant_value_shapes",
    # Gate A fixtures (Item 2) — the usage-owned/package-owned owner-classification pair.
    "gate_a",
    "gate_a_package_owner",
    # Cutover fixtures (Item 2 phase group 2). `shared_producer` is recorded
    # known-incomplete (SR-A02 referred to Item 4) — see its PROVENANCE.md.
    "agg_localterm_probe",
    "shared_producer",
    # deep_cross_scope_probe is deliberately NOT registered here. Historically its
    # Pattern-A deep CHAIN truncated to the first segment; TRUTH-DEBT Item 2 retired
    # that (extraction now emits the full-path CHAIN and the backtracker climbs), but
    # the probe stays unregistered: it is a dedicated-probe fixture whose pins
    # (test_deep_cross_scope_probe.py, test_res08_consumer_scope_paths.py) load it
    # directly, so it needs no session-snapshot registration.
]


def pytest_configure(config):
    config.addinivalue_line("markers", "req(id): map test to requirement ID")
    config.addinivalue_line("markers", "baseline: pipeline baseline comparison test")


@pytest.fixture(scope="session")
def extraction_snapshots():
    """Load all extraction snapshots once per session."""
    return {
        name: load_extraction_snapshot(snapshot_fixture(name))
        for name in SNAPSHOT_MODELS
    }


@pytest.fixture
def solar_battery_snapshot(extraction_snapshots):
    """Convenience fixture for solar_battery_model snapshot."""
    return extraction_snapshots["solar_battery_model"]


@pytest.fixture
def catf_mfe_snapshot(extraction_snapshots):
    """Convenience fixture for catf_mfe_model snapshot."""
    return extraction_snapshots["catf_mfe_model"]


@pytest.fixture
def sample_model_snapshot(extraction_snapshots):
    """Convenience fixture for sample_model snapshot."""
    return extraction_snapshots["sample_model"]


@pytest.fixture
def attr_expr_probe_snapshot(extraction_snapshots):
    """Convenience fixture for attr_expr_probe snapshot."""
    return extraction_snapshots["attr_expr_probe"]


@pytest.fixture
def chain_spike_snapshot(extraction_snapshots):
    """Convenience fixture for chain_spike_model snapshot."""
    return extraction_snapshots["chain_spike_model"]


@pytest.fixture
def issue22_snapshot(extraction_snapshots):
    """Convenience fixture for issue22_model snapshot."""
    return extraction_snapshots["issue22_model"]


@pytest.fixture
def expression_binding_snapshot(extraction_snapshots):
    """Convenience fixture for expression_binding_probe snapshot."""
    return extraction_snapshots["expression_binding_probe"]


@pytest.fixture
def chain_override_snapshot(extraction_snapshots):
    """Convenience fixture for chain_override_probe snapshot."""
    return extraction_snapshots["chain_override_probe"]


@pytest.fixture
def unresolvable_attr_snapshot(extraction_snapshots):
    """Convenience fixture for unresolvable_attr_probe snapshot."""
    return extraction_snapshots["unresolvable_attr_probe"]


@pytest.fixture
def alias_agg_probe_snapshot(extraction_snapshots):
    """Convenience fixture for alias_agg_probe snapshot."""
    return extraction_snapshots["alias_agg_probe"]
