"""Lifecycle Item 12: legacy snapshot + tracking-identity closure.

RED-first coverage for the six coordinates of the combined spec+design
(`.project/active/constraint-lifecycle-legacy-identity/spec-design.md`):

- RED-6: the from-snapshot context reports its snapshot's *real* lowering mode
  (D4) — the gate signal must be trustworthy before the gate exists.
- RED-1/2: normal product generation fails closed on ``grandfathered_off`` before
  any output is written, so a grandfathered snapshot provably cannot seal (D1).
- RED-3: grandfathered extraction-only probes stay loadable for inspection — the
  gate lives on the product path, not at load (D1/D2 regression fence).
- RED-4: a full-pipeline model can no longer be captured ``grandfathered_off`` —
  the capture-time opt-out is gone (D2).
- RED-5: ``tracking_key`` no longer exists (D3).

License-free throughout: every case runs from a committed snapshot.
"""

from __future__ import annotations

import inspect
import json

import pytest

from tests.conftest import snapshot_fixture

# The 7 committed extraction-only probes captured ``grandfathered_off`` (all carry
# zero constraint usages — inspection artifacts, never lowered).
_GRANDFATHERED_PROBES = [
    "agg_literal_probe",
    "chain_override_probe",
    "expression_binding_probe",
    "invocation_binding_probe",
    "self_named_binding_trap",
    "shadowed_reference",
    "unresolvable_attr_probe",
]


def _grandfathered_with_usages(tmp_path):
    """A crafted ``grandfathered_off`` snapshot that *carries* constraint usages.

    Flips the mode on a lowered, constraint-bearing snapshot. Pre-gate this is the
    exact silent-drop bug: the offline rebuild warns, drops the usages, and seals a
    certifying package without them. Post-gate the product path refuses it.
    """
    payload = json.loads(snapshot_fixture("constraint_multi_instance").read_text())
    assert payload["constraint_facts"]["usages"], "fixture must carry usages to prove the drop"
    payload["constraint_lowering_mode"] = "grandfathered_off"
    path = tmp_path / "extraction_snapshot.json"
    path.write_text(json.dumps(payload))
    return path


# ---------------------------------------------------------------------------
# RED-6 (D4): the from-snapshot context reports the snapshot's real mode.
# ---------------------------------------------------------------------------
def test_from_snapshot_context_reports_real_lowering_mode():
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture("constraint_multi_instance"))
    # RED today: the context omits the field and inherits the dataclass default
    # "grandfathered_off", so an *applied* snapshot mis-reports as grandfathered.
    assert ctx.constraint_lowering_mode == "applied"


# ---------------------------------------------------------------------------
# RED-1 (D1): product generation fails closed on grandfathered_off, contextually.
# ---------------------------------------------------------------------------
def test_generate_from_grandfathered_snapshot_fails_closed(tmp_path):
    from sysml_codegen.cli import GenerationConfig, run_codegen

    snap = _grandfathered_with_usages(tmp_path)
    config = GenerationConfig(
        output_path=tmp_path / "out",
        from_snapshot=snap,
        package_name="multi_instance",
        overwrite=True,
    )
    # RED today: the offline path warns-and-drops, then seals -> returns True.
    assert run_codegen(config) is False


def test_grandfathered_gate_raises_contextual_error(tmp_path):
    from sysml_codegen.snapshot import (
        GrandfatheredSnapshotError,
        assert_snapshot_certifiable,
    )

    snap = _grandfathered_with_usages(tmp_path)
    with pytest.raises(GrandfatheredSnapshotError) as excinfo:
        assert_snapshot_certifiable("grandfathered_off", snap)
    message = str(excinfo.value).lower()
    assert "recapture" in message
    assert "lowering" in message


# ---------------------------------------------------------------------------
# RED-2 (D1): a grandfathered snapshot provably cannot seal — no package written.
# ---------------------------------------------------------------------------
def test_grandfathered_snapshot_writes_no_sealed_package(tmp_path):
    from sysml_codegen.cli import GenerationConfig, run_codegen

    out = tmp_path / "out"
    snap = _grandfathered_with_usages(tmp_path)
    config = GenerationConfig(
        output_path=out,
        from_snapshot=snap,
        package_name="multi_instance",
        overwrite=True,
    )
    run_codegen(config)
    # The gate precedes output creation and sealing entirely.
    assert not (out / "contracts" / "package_contract.json").exists()


# ---------------------------------------------------------------------------
# RED-3 (D1/D2 fence): grandfathered probes stay loadable for inspection.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("probe", _GRANDFATHERED_PROBES)
def test_grandfathered_probe_still_loads_for_inspection(probe):
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )
    from sysml_codegen.snapshot import build_full_graph_from_snapshot

    # Inspection loads must not be gated — the fail-closed lives on the product
    # generate path only. Both inspection entry points must succeed.
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(probe))
    assert graph is not None
    ctx = build_pipeline_context_from_snapshot(snapshot_fixture(probe))
    assert ctx.constraint_lowering_mode == "grandfathered_off"


# ---------------------------------------------------------------------------
# RED-4 (D2): a full-pipeline model can no longer be captured grandfathered_off.
# ---------------------------------------------------------------------------
def test_capture_snapshot_has_no_lowering_optout():
    from sysml_codegen.snapshot import capture_snapshot

    # RED today: the ``lower_constraints_enabled`` capture-time opt-out exists.
    assert "lower_constraints_enabled" not in inspect.signature(capture_snapshot).parameters


# ---------------------------------------------------------------------------
# RED-5 (D3): tracking_key no longer exists on ConcreteConstraint.
# ---------------------------------------------------------------------------
def test_tracking_key_field_is_deleted():
    from sysml_codegen.resolution.models import ConcreteConstraint

    # RED today: the dead correlation field is present.
    assert "tracking_key" not in ConcreteConstraint.model_fields
