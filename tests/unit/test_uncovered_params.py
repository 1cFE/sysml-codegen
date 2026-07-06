"""Params-coverage collector + V11 strict boundary (Item 7 / REQ-GA-08, D4).

Covers the two-layer coverage check:
  - ``collect_uncovered_params`` (pure, wired half → V11) — INV-3, INV-4.
  - ``collect_unwired_fallthrough`` (pure, unwired half → reconciliation summary).
  - the always-strict generation boundary raising V11 (``_reconcile_params_coverage``).

Real extraction snapshots — no mocks (R1). The unwired-summary partition has no
committed real-fixture that exercises it (every corpus V11 case is wired), so it
is covered by a constructed ``ComputationGraph`` of real Pydantic model objects.

V11 corpus surface after Item 9 (genuine fell-through ∩ valueless ∩ wired gaps that
remain — the plain-usage LITERAL class is now pre-filled and drops off this list):
  - catf_mfe            cryo_load.magnet_volume   (cross-part CHAIN; Items 10-11 wire it)
  - ife_plant shape-4   cryo_load.magnet_volume   (cross-part CHAIN; the committed
                                                   non-catf_mfe strict-V11 proof)
  - chain_override_probe cost_model.sensitivity   (calc-output ref; A1 keeps it loud)

The dedicated committed V11 proof is now catf_mfe (strict raise, ``test_reconcile_
raises_v11_on_wired_gap``) + ife_plant shape-4 (strict abort, ``test_seeded_strict_
generation_aborts_independently_of_catf_mfe``). alias_agg_probe / issue22_model /
unresolvable_attr_probe are pre-filled by Item 9's plain-usage literal capture and
now generate cleanly (their collector lists go empty below).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from sysml_codegen.resolution.graph_builder import (
    UncoveredInput,
    collect_uncovered_params,
    collect_unwired_fallthrough,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ParameterGroup,
    PipelineModule,
)
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from tests.conftest import snapshot_fixture


def _graph(name: str) -> ComputationGraph:
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(name))
    return graph


# ---------------------------------------------------------------------------
# INV-3: the collector is pure — returns a list, raises nothing.
# ---------------------------------------------------------------------------
def test_collector_is_pure_on_clean_graph():
    """A clean fixture yields an empty list, no raise (INV-3).

    solar_battery has 10 fell-through EPs, but every one is back-filled to a
    value by the deriver merge → valued, not valueless → not a V11 violation.
    """
    assert collect_uncovered_params(_graph("solar_battery_model")) == []


# ---------------------------------------------------------------------------
# INV-4: catf_mfe collector list is pinned exactly.
# ---------------------------------------------------------------------------
def test_collector_pins_catf_mfe_dangle():
    """catf_mfe collector returns exactly the one magnet_volume gap (INV-4).

    Grow/shrink fails: the list content is pinned. Tracked to Items 9-11 — the
    cross-part ``tf_coil.volume`` EXPOSE they wire flips this to ``[]``.
    """
    result = collect_uncovered_params(_graph("catf_mfe_model"))
    assert result == [
        UncoveredInput(
            module="catfmfemagnets__catf_tf_system__cryo_load",
            input="magnet_volume",
            missing_key=(
                "magnets_params."
                "CATFMFEMagnets__catf_tf_system__cryo_load__magnet_volume"
            ),
        )
    ]


def test_collector_pins_alias_agg_probe():
    """alias_agg_probe: no uncovered params — Item 9 pre-fills base_cost.

    The plain-usage ``:>> widget.base_cost = 50.0`` override is now captured, and the
    virtual ``cost_model.base_cost`` binding is rewritten to LITERAL 50.0 before it can
    become a valueless entry point, so the collector list is empty (REQ-HR-08).
    """
    result = collect_uncovered_params(_graph("alias_agg_probe"))
    assert result == []


def test_collector_pins_issue22_model():
    """issue22_model: no uncovered params — same class as alias_agg_probe (100.0)."""
    result = collect_uncovered_params(_graph("issue22_model"))
    assert result == []


def test_collector_pins_unresolvable_attr_probe():
    """unresolvable_attr_probe: no uncovered params — Item 9 fills my_calc.x.

    ``:>> local_val = 5.0`` on the plain ``design_derived_instance`` is captured and
    rewrites the ``my_calc.x = local_val`` binding to LITERAL 5.0. Its valueless-ness
    was itself the dropped-plain-usage-override bug Item 9 fixes, so the dedicated
    committed V11 proof moves to catf_mfe + ife_plant shape-4 (D5).
    """
    result = collect_uncovered_params(_graph("unresolvable_attr_probe"))
    assert result == []


def test_collector_pins_chain_override_probe():
    """chain_override_probe: exactly one sensitivity gap.

    ``calibration.calibrated_factor`` is a calc-def OUTPUT attribute, which the
    Bug-B leaf-unique pool restriction (DEV-2 / A1) deliberately excludes, so the
    reference stays unresolved and LOUD rather than cross-wiring into a
    DESIGN_ATTRIBUTE. V11 firing here is the intended safety property.
    """
    result = collect_uncovered_params(_graph("chain_override_probe"))
    assert [(u.input, u.module.split("__")[-1]) for u in result] == [
        ("sensitivity", "cost_model")
    ]


# ---------------------------------------------------------------------------
# Strict boundary raises V11 (explicit raises-assertion, pins the behavior).
# ---------------------------------------------------------------------------
def test_reconcile_raises_v11_on_wired_gap():
    """The generation boundary raises V11 on a wired fell-through-valueless input.

    Anchored on catf_mfe's ``cryo_load.magnet_volume`` — a cross-part CHAIN gap the
    LITERAL filter deliberately keeps out of design_overrides, so it stays
    wired-valueless and trips V11 (the committed real-fixture proof; Items 10-11
    wire it). Re-anchored off unresolvable_attr_probe, which Item 9 now pre-fills.
    """
    from sysml_codegen.cli import _reconcile_params_coverage
    from sysml_codegen.generation import CodeGenerationError

    graph = _graph("catf_mfe_model")
    with pytest.raises(CodeGenerationError, match=r"V11"):
        _reconcile_params_coverage(graph)


def test_seeded_strict_generation_aborts_independently_of_catf_mfe(tmp_path, caplog):
    """Strict generation aborts on ife_plant (V11), proving the check fires
    independently of catf_mfe (B4).

    ife_plant's shape-4 ``cryo_load.magnet_volume`` is a cross-part CHAIN that stays
    wired-valueless until Item 10 wires it — a non-catf_mfe fixture that still trips
    strict V11 at generation. ``run_codegen`` catches CodeGenerationError and returns
    False (the fail-fast idiom), so the abort is observed as ``False`` + a logged V11
    line, not a propagated exception. Re-anchored off unresolvable_attr_probe, which
    Item 9 now pre-fills (D5).
    """
    from sysml_codegen.cli import GenerationConfig, run_codegen

    config = GenerationConfig(
        output_path=tmp_path,
        from_snapshot=snapshot_fixture("ife_plant"),
        package_name="ife",
        overwrite=True,
    )
    with caplog.at_level(logging.ERROR):
        assert run_codegen(config) is False
    assert any("V11" in r.message for r in caplog.records), (
        "strict generation must log the V11 diagnostic on abort"
    )


# ---------------------------------------------------------------------------
# DEV-4: fallback_entry_points is an in-memory artifact, not serialized — so
# committed baselines do not churn, yet the collector fires on the in-memory
# graph. This also verifies snapshot-driven generation regenerates the field in
# memory (build_full_graph_from_snapshot re-runs the backtracker), so V11 fires
# identically on the --from-snapshot path.
# ---------------------------------------------------------------------------
def test_fallback_entry_points_populated_in_memory_but_not_serialized():
    graph = _graph("catf_mfe_model")
    # In-memory: populated by the (snapshot-driven) backtracker run.
    assert graph.fallback_entry_points, "backtracker must populate the field in memory"
    assert collect_uncovered_params(graph), "collector fires on the in-memory graph"

    # Serialized: excluded — the committed computation_graph.json contract is
    # unchanged, so baselines do not churn.
    dumped = graph.model_dump()
    assert "fallback_entry_points" not in dumped
    assert "fallback_entry_points" not in graph.model_dump_json()

    # Round-trip: a graph rebuilt from the serialized form has an empty set (the
    # field is never read from a deserialized graph — the collector only runs at
    # the generation boundary on a freshly-built graph).
    reloaded = ComputationGraph.model_validate(dumped)
    assert reloaded.fallback_entry_points == set()


# ---------------------------------------------------------------------------
# Unwired-summary partition (M1). No committed fixture exercises it (every corpus
# V11 case is wired), so build a minimal real ComputationGraph directly.
# ---------------------------------------------------------------------------
def test_unwired_fallthrough_partition():
    """A fell-through, valueless, UNWIRED entry point → summary list, not V11."""
    dangling_qn = "Lib__plant__orphan_calc__p"

    # One module whose sole input is wired to a DIFFERENT (covered) EP, so the
    # dangling EP is genuinely unwired.
    module = PipelineModule(
        name="lib__plant__orphan_calc",
        module_type="OrphanCalcModule",
        inputs=[
            ModuleInput(
                param_name="q",
                python_type="float",
                source=InputSource(
                    source_type="entry_point",
                    param_group="design_params",
                    qualified_name="Lib__plant__orphan_calc__q",
                ),
            )
        ],
        outputs=[],
        execution_order=0,
    )
    group = ParameterGroup(
        name="design_params",
        class_name="DesignParams",
        source_file=Path("design.sysml"),
        parameters=[
            EntryPoint(
                qualified_name="Lib__plant__orphan_calc__q",
                simple_name="q",
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                default_value=1.0,
            ),
            EntryPoint(
                qualified_name=dangling_qn,
                simple_name="p",
                entry_type=EntryPointType.USAGE_LITERAL,
                default_value=None,  # valueless
            ),
        ],
    )
    graph = ComputationGraph(
        modules=[module],
        entry_point_groups=[group],
        execution_order=["lib__plant__orphan_calc"],
        fallback_entry_points={dangling_qn},  # fell through
    )

    # Unwired + valueless → summary partition.
    assert collect_unwired_fallthrough(graph) == [dangling_qn]
    # Not wired → NOT a V11 violation.
    assert collect_uncovered_params(graph) == []
