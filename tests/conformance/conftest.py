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
# The two conformance files whose subject is extraction itself (test_extractor.py,
# test_expression_compiler.py) read these. Only the live calc-def extractor runs here:
# the calc-usage and hierarchy facts retired with the legacy extraction lane
# (REPO-CLEANUP Move C). See ``tests/helpers/live_extraction.py``.
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
