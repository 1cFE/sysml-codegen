"""A scope-qualified reference is never re-anchored at the consumer's owner (audit F2/F2b).

The `shadowed_reference` fixture holds two same-named attributes with **different**
values — outer `scale = 2.0`, inner shadow `scale = 7.0` — so a re-anchor moves a
number visibly instead of hiding behind a coincidence. The real instance of this bug
(catf_mfe's `kappa`) survived a full audit cycle because both attributes held 3.0.

Round 1 authored that fixture but attached no test to it, so it pinned nothing (F2c).
This is that test.

The discriminator under test is the **written** form, captured at extraction from the
CST (`BindingInfo.source_written_qualifier`). Two earlier attempts discriminated on
resolution — "does `source_path` contain `::`" and "is the resolved QN indexed" — and
both were wrong the same way: resolution makes an owner-relative bare leaf and a
scope-qualified reference identical.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.orchestration.snapshot_context import build_pipeline_context_from_snapshot
from tests.conftest import FIXTURES_DIR, requires_license, snapshot_fixture

ROOT = FIXTURES_DIR / "shadowed_reference"

OUTER_QN = "ShadowedReference__the_outer__scale"
OUTER_VALUE = 2.0
SHADOW_QN = "ShadowedReference__the_outer__inner__scale"
SHADOW_VALUE = 7.0


def _assert_anchored_at_written_scope(graph) -> None:
    entry_points = {
        parameter.qualified_name: parameter.default_value
        for group in graph.entry_point_groups
        for parameter in group.parameters
    }

    # The model writes `ShadowedReference::the_outer::scale` — the OUTER one.
    assert OUTER_QN in entry_points, entry_points
    assert entry_points[OUTER_QN] == OUTER_VALUE

    # The inner shadow must not be selected. If it is, a scope-qualified reference
    # was re-anchored under the consumer's own owner and the value silently moved.
    assert SHADOW_QN not in entry_points, (
        f"scope-qualified reference re-anchored onto the owner-local shadow "
        f"({SHADOW_VALUE} instead of {OUTER_VALUE}): {sorted(entry_points)}"
    )

    consumer_inputs = {
        (module.name, module_input.param_name): module_input.source.qualified_name
        for module in graph.modules
        for module_input in module.inputs
    }
    bound = [qn for (_, param), qn in consumer_inputs.items() if param == "factor"]
    assert bound == [OUTER_QN], consumer_inputs


@requires_license
def test_qualified_reference_anchors_at_written_scope_live() -> None:
    _assert_anchored_at_written_scope(build_pipeline_context([ROOT]).computation_graph)


def test_qualified_reference_anchors_at_written_scope_from_snapshot() -> None:
    context = build_pipeline_context_from_snapshot(snapshot_fixture("shadowed_reference"))
    _assert_anchored_at_written_scope(context.computation_graph)


def test_the_written_qualifier_is_captured_and_survives_the_snapshot() -> None:
    """The field the discriminator reads is present offline, not just live.

    Without this, the snapshot route would silently fall back to treating the
    reference as a bare leaf — which is exactly the pre-fix behaviour.
    """
    from sysml_codegen.snapshot.loader import load_extraction_snapshot

    snapshot = load_extraction_snapshot(snapshot_fixture("shadowed_reference"))
    qualifiers = {
        binding.param_name: binding.source_written_qualifier
        for usage in snapshot["calc_usages"]
        for binding in usage.bindings
    }
    assert qualifiers["factor"] == "ShadowedReference::the_outer"

    # And a bare leaf must carry None, or row 16 would stop serving the shape it exists for.
    shared = load_extraction_snapshot(snapshot_fixture("shared_producer"))
    bare = {
        binding.param_name: binding.source_written_qualifier
        for usage in shared["calc_usages"]
        for binding in usage.bindings
    }
    assert bare["gain"] is None


@pytest.mark.parametrize(
    ("fixture", "module_suffix", "param", "expected"),
    [
        ("shared_producer", "scaler", "gain", "SharedProducer__the_rig__gain"),
        ("fusion_tea", "driver__meier_cost", "driver_efficiency",
         "hif_plant_pkg__hif_plant__driver__efficiency"),
        ("catf_mfe_model", "plasma_region__volume_calc", "kappa",
         "CATFMFERadialBuild__catf_radial_build__elongation"),
    ],
    ids=["bare-leaf-converges", "bare-leaf-stays-instance-scoped", "qualified-anchors-outer"],
)
def test_three_sentinel_bindings(fixture, module_suffix, param, expected) -> None:
    """The three shapes that must be told apart, pinned together.

    They are byte-identical in every field except the written qualifier, which is
    why nothing derived from resolution can separate them.
    """
    context = build_pipeline_context_from_snapshot(snapshot_fixture(fixture))
    resolved = [
        module_input.source.qualified_name or module_input.source.producer_channel
        for module in context.computation_graph.modules
        if module.name.endswith(module_suffix)
        for module_input in module.inputs
        if module_input.param_name == param
    ]
    assert resolved == [expected]
