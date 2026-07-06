"""Params-coverage collector + V11 strict boundary (Item 7 / REQ-GA-08, D4).

Covers the two-layer coverage check:
  - ``collect_uncovered_params`` (pure, wired half → V11) — INV-3, INV-4.
  - ``collect_unwired_fallthrough`` (pure, unwired half → reconciliation summary).
  - the always-strict generation boundary raising V11 (``_reconcile_params_coverage``).

Real extraction snapshots — no mocks (R1). The unwired-summary partition has no
committed real-fixture that exercises it (every corpus V11 case is wired), so it
is covered by a constructed ``ComputationGraph`` of real Pydantic model objects.

V11 corpus surface (all genuine, pre-existing fell-through ∩ valueless ∩ wired
gaps; see plan.md Phase-2 blocking finding):
  - catf_mfe            cryo_load.magnet_volume   (cross-part EXPOSE; Items 9-11)
  - alias_agg_probe     cost_model.base_cost      (bare-name :>> redefinition; Item 9)
  - issue22_model       cost_model.base_cost      (same class; Item 9)
  - unresolvable_attr_probe  my_calc.x            (dedicated V11 proof fixture)
  - chain_override_probe cost_model.sensitivity   (calc-output ref; A1 keeps it loud)
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
    """alias_agg_probe: exactly one base_cost gap (bare-name :>> redefinition).

    Tracked to Item 9 (RedefinitionData → CalcUsage entry-point default).
    """
    result = collect_uncovered_params(_graph("alias_agg_probe"))
    assert [(u.input, u.module.split("__")[-1]) for u in result] == [
        ("base_cost", "cost_model")
    ]


def test_collector_pins_issue22_model():
    """issue22_model: exactly one base_cost gap (same class as alias_agg_probe)."""
    result = collect_uncovered_params(_graph("issue22_model"))
    assert [(u.input, u.module.split("__")[-1]) for u in result] == [
        ("base_cost", "cost_model")
    ]


def test_collector_pins_unresolvable_attr_probe():
    """unresolvable_attr_probe: exactly one my_calc.x gap (dedicated V11 proof)."""
    result = collect_uncovered_params(_graph("unresolvable_attr_probe"))
    assert [(u.input, u.module.split("__")[-1]) for u in result] == [
        ("x", "my_calc")
    ]


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
    """The generation boundary raises V11 on a wired fell-through-valueless input."""
    from sysml_codegen.cli import _reconcile_params_coverage
    from sysml_codegen.generation import CodeGenerationError

    graph = _graph("unresolvable_attr_probe")
    with pytest.raises(CodeGenerationError, match=r"V11"):
        _reconcile_params_coverage(graph)


def test_seeded_strict_generation_aborts_independently_of_catf_mfe(tmp_path, caplog):
    """Strict generation aborts on the dedicated seeded fixture (V11), proving the
    check fires independently of catf_mfe (B4).

    ``unresolvable_attr_probe`` is the purpose-built, committed seeded fixture
    (spec deviation: satisfies the "new seeded fixture" requirement without a new
    license capture — see plan.md). ``run_codegen`` catches CodeGenerationError
    and returns False (the fail-fast idiom), so the abort is observed as
    ``False`` + a logged V11 line, not a propagated exception.
    """
    from sysml_codegen.cli import GenerationConfig, run_codegen

    config = GenerationConfig(
        output_path=tmp_path,
        from_snapshot=snapshot_fixture("unresolvable_attr_probe"),
        package_name="uap",
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
