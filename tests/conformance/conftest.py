"""Conformance test configuration and fixtures.

Provides:
- Marker registration (req, baseline)
- Session-scoped live extraction facts, and the per-model conveniences over them

The v5 half — the session-scoped extraction-snapshot fixtures, the eleven per-model
conveniences and ``offline_input_sources`` — retired with the v5 read path (retirement
step 1). Every one of them read a committed extraction snapshot through the v5 loader or
``snapshot_context``.
"""

from __future__ import annotations

import pytest


def pytest_configure(config):
    config.addinivalue_line("markers", "req(id): map test to requirement ID")
    config.addinivalue_line("markers", "baseline: pipeline baseline comparison test")


# ---------------------------------------------------------------------------
# Live extraction facts
#
# The four conformance files whose subject is extraction itself read these. They run the
# three extractors live; see ``tests/helpers/live_extraction.py`` for why the v6
# instance-graph snapshot is not a substitute.
# ---------------------------------------------------------------------------

# The models the extraction-fact sweeps range over.
EXTRACTION_FACT_MODELS = [
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
    "wi014_toy",
    "ife_plant",
    "self_named_binding_trap",
    "plant_values",
    # B6: PlantValueShapesLib::ChamberSelectCalc::wall has the user-defined
    # PlantValueShapesLib::'Wall Kind' typing. It is a named SI_TYPE_INVALID
    # refusal, proved separately instead of poisoning every eager sweep row.
    "gate_a",
    "gate_a_package_owner",
    "agg_localterm_probe",
    "shared_producer",
]


@pytest.fixture(scope="session")
def live_extraction_facts():
    """Every sweep model's live extraction facts, keyed by model name.

    License-gated here rather than by a ``requires_license`` mark on each of the ~110
    reading nodes: the gate belongs to the evidence, and a node that stops reading this
    fixture stops being gated with no mark to remember to remove. The skip reason is the
    shared one, so the battery's "zero ``no live syside license`` skip lines" proof still
    counts these nodes.
    """
    from tests.conftest import _license_available
    from tests.helpers.live_extraction import live_facts

    if not _license_available():
        pytest.skip("no live syside license")
    return {name: live_facts(name) for name in EXTRACTION_FACT_MODELS}


@pytest.fixture
def solar_battery_facts(live_extraction_facts):
    """Live extraction facts for solar_battery_model."""
    return live_extraction_facts["solar_battery_model"]


@pytest.fixture
def catf_mfe_facts(live_extraction_facts):
    """Live extraction facts for catf_mfe_model."""
    return live_extraction_facts["catf_mfe_model"]


@pytest.fixture
def issue22_facts(live_extraction_facts):
    """Live extraction facts for issue22_model."""
    return live_extraction_facts["issue22_model"]


@pytest.fixture
def expression_binding_facts(live_extraction_facts):
    """Live extraction facts for expression_binding_probe."""
    return live_extraction_facts["expression_binding_probe"]


@pytest.fixture
def alias_agg_probe_facts(live_extraction_facts):
    """Live extraction facts for alias_agg_probe."""
    return live_extraction_facts["alias_agg_probe"]
