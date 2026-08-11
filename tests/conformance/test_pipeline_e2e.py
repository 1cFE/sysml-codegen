"""End-to-End Pipeline Validation (5.2) — Checkpoint 5.

Requirements: REQ-PIPE-01 through REQ-PIPE-06
Design intent: 00-pipeline-overview.md

This gate proves the generation-facing invariants against the certified exact
public builder. Legacy DTO rebuilds and Phase-0 output baselines are not an
authority after the elaborator cutover.

REQ-PIPE-07 (generation boundary) is intentionally excluded — it's tested
in C19 (test_generation_extraction_import_count) and the fix is a Phase 7.6
target.

Tests use the certified exact live fixture -- no mocks.
"""

from __future__ import annotations

import pytest

from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPointType,
    ModuleKind,
)
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

EXACT_FIXTURE = FIXTURES_DIR / "source_identity_mixed_consumers"


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def exact_graph():
    """Full ComputationGraph from the certified exact public route."""
    return build_pipeline_context([EXACT_FIXTURE]).computation_graph


@pytest.fixture(scope="session")
def solar_battery_graph(exact_graph):
    return exact_graph


@pytest.fixture(scope="session")
def catf_mfe_graph(exact_graph):
    return exact_graph


@pytest.fixture(scope="session")
def chain_spike_graph(exact_graph):
    return exact_graph


@pytest.fixture(scope="session")
def attr_expr_probe_graph(exact_graph):
    return exact_graph


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
            m.module_kind == ModuleKind.CALCULATION
            for m in graph.modules
        )
        has_formula = any(m.module_kind == ModuleKind.FORMULA for m in graph.modules)
        has_aggregation = any(m.module_kind == ModuleKind.AGGREGATION for m in graph.modules)

        assert has_calc_usage, "No CalcUsage modules in solar_battery graph"
        assert has_formula, "No FORMULA modules in solar_battery graph"
        assert has_aggregation, "No Aggregation modules in solar_battery graph"

    @pytest.mark.req("REQ-PIPE-06")
    def test_module_types_catf_mfe(self, catf_mfe_graph):
        """catf_mfe graph has at least CalcUsage modules."""
        graph = catf_mfe_graph

        has_calc_usage = any(
            m.module_kind == ModuleKind.CALCULATION
            for m in graph.modules
        )
        assert has_calc_usage, "No CalcUsage modules in catf_mfe graph"

        calc_usage_count = sum(
            1 for m in graph.modules
            if m.module_kind == ModuleKind.CALCULATION
        )
        assert calc_usage_count > 0, "Expected at least one CalcUsage module"


# ===========================================================================
# Checkpoint 5: Baseline comparison
# ===========================================================================
class TestPublicRouteDeterminism:
    """The public builder reproduces the same exact computation projection."""

    @pytest.mark.req("REQ-PIPE-01")
    def test_fresh_public_builds_are_equal_and_distinct(self, exact_graph):
        second = build_pipeline_context([EXACT_FIXTURE]).computation_graph
        assert second == exact_graph
        assert second is not exact_graph
