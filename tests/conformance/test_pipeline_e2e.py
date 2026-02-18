"""End-to-End Pipeline Validation (5.2) — Checkpoint 5.

Requirements: REQ-PIPE-01 through REQ-PIPE-06
Design intent: 00-pipeline-overview.md

This is the Checkpoint 5 validation gate: it proves the refactored pipeline
(extraction snapshots -> registry -> backtracker -> classifier -> module
factories -> graph assembly) produces ComputationGraphs that match Phase 0
baselines. It runs the full pipeline end-to-end on multiple fixture models
and validates every pipeline-level requirement.

REQ-PIPE-07 (generation boundary) is intentionally excluded — it's tested
in C19 (test_generation_extraction_import_count) and the fix is a Phase 7.6
target.

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPointType,
)
from tests.conformance.test_entry_point_classifier import (
    build_full_graph_from_snapshot,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
BASELINE_DIR = Path(__file__).parent.parent / "fixtures" / "baseline_outputs"


def _load_baseline(model_name: str) -> dict:
    """Load baseline ComputationGraph JSON."""
    baseline_path = BASELINE_DIR / model_name / "computation_graph.json"
    with open(baseline_path) as f:
        return json.load(f)


def _compare_graph_to_baseline(graph: ComputationGraph, baseline: dict):
    """Compare a ComputationGraph against its baseline JSON.

    Applies two normalizations for snapshot-vs-live differences:
    1. CalcUsage compilability: 'unknown' from snapshot (no compilation_results)
       vs 'fully_compilable' from live pipeline.
    2. entry_point_groups parameter ordering: dict iteration order differs
       between live and snapshot pipelines.
    """
    # Compare execution_order exactly
    assert graph.execution_order == baseline["execution_order"], (
        f"execution_order mismatch: "
        f"got {graph.execution_order}, expected {baseline['execution_order']}"
    )

    # Compare module count
    assert len(graph.modules) == len(baseline["modules"]), (
        f"Module count: {len(graph.modules)} vs baseline {len(baseline['modules'])}"
    )

    # Compare each module by name
    baseline_by_name = {m["name"]: m for m in baseline["modules"]}
    for m in graph.modules:
        assert m.name in baseline_by_name, f"Module {m.name} not in baseline"
        bm = baseline_by_name[m.name]

        assert m.module_type == bm["module_type"], (
            f"Module {m.name}: module_type {m.module_type} vs {bm['module_type']}"
        )
        assert len(m.inputs) == len(bm["inputs"]), (
            f"Module {m.name}: {len(m.inputs)} inputs vs {len(bm['inputs'])}"
        )
        assert len(m.outputs) == len(bm["outputs"]), (
            f"Module {m.name}: {len(m.outputs)} outputs vs {len(bm['outputs'])}"
        )
        assert m.execution_order == bm["execution_order"], (
            f"Module {m.name}: order {m.execution_order} vs {bm['execution_order']}"
        )
        assert m.is_computed_attribute == bm["is_computed_attribute"], (
            f"Module {m.name}: is_computed_attribute mismatch"
        )
        assert m.is_aggregation == bm["is_aggregation"], (
            f"Module {m.name}: is_aggregation mismatch"
        )

        # Verify compilability for FORMULA/aggregation modules (set by factory)
        if m.is_computed_attribute or m.is_aggregation:
            assert m.compilability.value == bm["compilability"], (
                f"Module {m.name}: compilability {m.compilability.value} "
                f"vs {bm['compilability']}"
            )

    # Compare channel name sets
    graph_channels = sorted(
        {out.channel_name for m in graph.modules for out in m.outputs}
    )
    baseline_channels = sorted(
        {out["channel_name"] for m in baseline["modules"] for out in m["outputs"]}
    )
    assert graph_channels == baseline_channels, (
        f"Channel name mismatch:\n"
        f"  Only in graph: {set(graph_channels) - set(baseline_channels)}\n"
        f"  Only in baseline: {set(baseline_channels) - set(graph_channels)}"
    )

    # Full JSON comparison with normalizations
    graph_json = json.loads(graph.model_dump_json())
    baseline_normalized = json.loads(json.dumps(baseline))

    for gm, bm in zip(graph_json["modules"], baseline_normalized["modules"]):
        if not gm["is_computed_attribute"] and not gm["is_aggregation"]:
            bm["compilability"] = gm["compilability"]

    # Sort parameters within each group by qualified_name
    for groups in (graph_json["entry_point_groups"],
                   baseline_normalized["entry_point_groups"]):
        for group in groups:
            group["parameters"] = sorted(
                group["parameters"], key=lambda p: p["qualified_name"]
            )

    assert graph_json == baseline_normalized, (
        "Full ComputationGraph JSON does not match baseline "
        "(after normalizing CalcUsage compilability and parameter ordering)"
    )


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_graph():
    """Full ComputationGraph for solar_battery_model."""
    graph, _inputs = build_full_graph_from_snapshot("solar_battery_model")
    return graph


@pytest.fixture(scope="session")
def catf_mfe_graph():
    """Full ComputationGraph for catf_mfe_model."""
    graph, _inputs = build_full_graph_from_snapshot("catf_mfe_model")
    return graph


@pytest.fixture(scope="session")
def chain_spike_graph():
    """Full ComputationGraph for chain_spike_model."""
    graph, _inputs = build_full_graph_from_snapshot("chain_spike_model")
    return graph


@pytest.fixture(scope="session")
def attr_expr_probe_graph():
    """Full ComputationGraph for attr_expr_probe."""
    graph, _inputs = build_full_graph_from_snapshot("attr_expr_probe")
    return graph


# ===========================================================================
# REQ-PIPE-01: Pipeline produces a ComputationGraph
# ===========================================================================
class TestPipelineProducesGraph:
    """REQ-PIPE-01: Pipeline produces exactly one ComputationGraph."""

    @pytest.mark.req("REQ-PIPE-01")
    def test_solar_battery_produces_computation_graph(self, solar_battery_graph):
        """solar_battery pipeline produces a ComputationGraph with modules and execution_order."""
        graph = solar_battery_graph
        assert isinstance(graph, ComputationGraph)
        assert len(graph.modules) > 0, "ComputationGraph has no modules"
        assert len(graph.execution_order) > 0, "ComputationGraph has no execution_order"

    @pytest.mark.req("REQ-PIPE-01")
    def test_catf_mfe_produces_computation_graph(self, catf_mfe_graph):
        """catf_mfe pipeline produces a ComputationGraph (larger model, 21 calc defs)."""
        graph = catf_mfe_graph
        assert isinstance(graph, ComputationGraph)
        assert len(graph.modules) > 0, "ComputationGraph has no modules"
        assert len(graph.execution_order) > 0, "ComputationGraph has no execution_order"


# ===========================================================================
# REQ-PIPE-02: Every ModuleInput wired
# ===========================================================================
class TestEveryInputWired:
    """REQ-PIPE-02: Every ModuleInput is wired to module_output or entry_point."""

    @pytest.mark.req("REQ-PIPE-02")
    def test_every_input_wired_solar_battery(self, solar_battery_graph):
        """Every ModuleInput in solar_battery has source_type in {module_output, entry_point}."""
        for m in solar_battery_graph.modules:
            for inp in m.inputs:
                assert inp.source.source_type in {"module_output", "entry_point"}, (
                    f"Module {m.name} input {inp.param_name} has "
                    f"source_type={inp.source.source_type}"
                )

    @pytest.mark.req("REQ-PIPE-02")
    def test_every_input_wired_catf_mfe(self, catf_mfe_graph):
        """Every ModuleInput in catf_mfe has source_type in {module_output, entry_point}."""
        for m in catf_mfe_graph.modules:
            for inp in m.inputs:
                assert inp.source.source_type in {"module_output", "entry_point"}, (
                    f"Module {m.name} input {inp.param_name} has "
                    f"source_type={inp.source.source_type}"
                )


# ===========================================================================
# REQ-PIPE-03: Every producer_channel declared
# ===========================================================================
class TestEveryChannelDeclared:
    """REQ-PIPE-03: Every module_output reference resolves to a declared channel."""

    def _get_declared_channels(self, graph: ComputationGraph) -> set[str]:
        """Collect all declared output channel names."""
        return {out.channel_name for m in graph.modules for out in m.outputs}

    @pytest.mark.req("REQ-PIPE-03")
    def test_every_producer_channel_declared_solar_battery(self, solar_battery_graph):
        """Every module_output producer_channel in solar_battery resolves to a declared output."""
        declared = self._get_declared_channels(solar_battery_graph)
        for m in solar_battery_graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    assert inp.source.producer_channel in declared, (
                        f"Module {m.name} input {inp.param_name} references "
                        f"undeclared channel {inp.source.producer_channel}"
                    )

    @pytest.mark.req("REQ-PIPE-03")
    def test_every_producer_channel_declared_catf_mfe(self, catf_mfe_graph):
        """Every module_output producer_channel in catf_mfe resolves to a declared output."""
        declared = self._get_declared_channels(catf_mfe_graph)
        for m in catf_mfe_graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    assert inp.source.producer_channel in declared, (
                        f"Module {m.name} input {inp.param_name} references "
                        f"undeclared channel {inp.source.producer_channel}"
                    )


# ===========================================================================
# REQ-PIPE-04: Valid topological sort
# ===========================================================================
class TestTopologicalSort:
    """REQ-PIPE-04: execution_order is a valid topological sort."""

    def _check_topological_order(self, graph: ComputationGraph):
        """Verify no module reads from a module with higher execution_order."""
        name_to_order = {m.name: m.execution_order for m in graph.modules}

        channel_to_module: dict[str, str] = {}
        for m in graph.modules:
            for out in m.outputs:
                channel_to_module[out.channel_name] = m.name

        for m in graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    producer = channel_to_module.get(inp.source.producer_channel)
                    if producer and producer != m.name:
                        assert name_to_order[producer] < name_to_order[m.name], (
                            f"Module {m.name} (order={name_to_order[m.name]}) reads from "
                            f"{producer} (order={name_to_order[producer]}) -- forward reference"
                        )

    @pytest.mark.req("REQ-PIPE-04")
    def test_valid_topological_sort_solar_battery(self, solar_battery_graph):
        """No module in solar_battery reads from a module with higher execution_order."""
        self._check_topological_order(solar_battery_graph)

    @pytest.mark.req("REQ-PIPE-04")
    def test_valid_topological_sort_catf_mfe(self, catf_mfe_graph):
        """No module in catf_mfe reads from a module with higher execution_order."""
        self._check_topological_order(catf_mfe_graph)


# ===========================================================================
# REQ-PIPE-05: Every entry point classified
# ===========================================================================
class TestEntryPointsClassified:
    """REQ-PIPE-05: Every entry point has a valid EntryPointType."""

    @pytest.mark.req("REQ-PIPE-05")
    def test_every_entry_point_classified_solar_battery(self, solar_battery_graph):
        """Every EP in solar_battery has entry_type in EntryPointType."""
        for group in solar_battery_graph.entry_point_groups:
            for ep in group.parameters:
                assert ep.entry_type in {t.value for t in EntryPointType}, (
                    f"Entry point {ep.qualified_name} has "
                    f"unrecognized entry_type={ep.entry_type}"
                )

    @pytest.mark.req("REQ-PIPE-05")
    def test_every_entry_point_classified_catf_mfe(self, catf_mfe_graph):
        """Every EP in catf_mfe has entry_type in EntryPointType."""
        for group in catf_mfe_graph.entry_point_groups:
            for ep in group.parameters:
                assert ep.entry_type in {t.value for t in EntryPointType}, (
                    f"Entry point {ep.qualified_name} has "
                    f"unrecognized entry_type={ep.entry_type}"
                )


# ===========================================================================
# REQ-PIPE-06: Module types
# ===========================================================================
class TestModuleTypes:
    """REQ-PIPE-06: Graph includes appropriate module types."""

    @pytest.mark.req("REQ-PIPE-06")
    def test_all_three_module_types_solar_battery(self, solar_battery_graph):
        """solar_battery graph includes CalcUsage, FORMULA, and Aggregation modules."""
        graph = solar_battery_graph

        has_calc_usage = any(
            not m.is_computed_attribute and not m.is_aggregation
            for m in graph.modules
        )
        has_formula = any(m.is_computed_attribute for m in graph.modules)
        has_aggregation = any(m.is_aggregation for m in graph.modules)

        assert has_calc_usage, "No CalcUsage modules in solar_battery graph"
        assert has_formula, "No FORMULA modules in solar_battery graph"
        assert has_aggregation, "No Aggregation modules in solar_battery graph"

    @pytest.mark.req("REQ-PIPE-06")
    def test_module_types_catf_mfe(self, catf_mfe_graph):
        """catf_mfe graph has at least CalcUsage modules."""
        graph = catf_mfe_graph

        has_calc_usage = any(
            not m.is_computed_attribute and not m.is_aggregation
            for m in graph.modules
        )
        assert has_calc_usage, "No CalcUsage modules in catf_mfe graph"

        # Document which types are present (catf_mfe may not have all 3)
        has_formula = any(m.is_computed_attribute for m in graph.modules)
        has_aggregation = any(m.is_aggregation for m in graph.modules)

        calc_usage_count = sum(
            1 for m in graph.modules
            if not m.is_computed_attribute and not m.is_aggregation
        )
        formula_count = sum(1 for m in graph.modules if m.is_computed_attribute)
        agg_count = sum(1 for m in graph.modules if m.is_aggregation)

        # Informational: log module type breakdown
        assert calc_usage_count > 0, "Expected at least one CalcUsage module"


# ===========================================================================
# Checkpoint 5: Baseline comparison
# ===========================================================================
class TestBaselineComparison:
    """Checkpoint 5: ComputationGraph matches baselines for all 4 models."""

    @pytest.mark.baseline
    @pytest.mark.req("REQ-PIPE-01")
    def test_baseline_comparison_solar_battery(self, solar_battery_graph):
        """ComputationGraph for solar_battery matches Phase 0 baseline."""
        baseline = _load_baseline("solar_battery")
        _compare_graph_to_baseline(solar_battery_graph, baseline)

    @pytest.mark.baseline
    @pytest.mark.req("REQ-PIPE-01")
    def test_baseline_comparison_catf_mfe(self, catf_mfe_graph):
        """ComputationGraph for catf_mfe matches baseline."""
        baseline = _load_baseline("catf_mfe")
        _compare_graph_to_baseline(catf_mfe_graph, baseline)

    @pytest.mark.baseline
    @pytest.mark.req("REQ-PIPE-01")
    def test_baseline_comparison_chain_spike(self, chain_spike_graph):
        """ComputationGraph for chain_spike matches Phase 0 baseline."""
        baseline = _load_baseline("chain_spike")
        _compare_graph_to_baseline(chain_spike_graph, baseline)

    @pytest.mark.baseline
    @pytest.mark.req("REQ-PIPE-01")
    def test_baseline_comparison_attr_expr_probe(self, attr_expr_probe_graph):
        """ComputationGraph for attr_expr_probe matches Phase 0 baseline."""
        baseline = _load_baseline("attr_expr_probe")
        _compare_graph_to_baseline(attr_expr_probe_graph, baseline)
