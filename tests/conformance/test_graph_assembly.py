"""Conformance tests for Graph Assembly (C18).

Requirements: REQ-GA-01 through REQ-GA-07
Design intent: 07-graph-assembly.md

Tests verify _unified_topological_sort(), _validate_channel_references(),
and ComputationGraph assembly with real extraction data:
- Valid topological sort (no forward references)
- Cycle detection with CircularDependencyError
- Channel reference validation (no dangling wires)
- No self-dependency
- ComputationGraph has exactly 5 fields
- execution_order matches module ordering
- Kahn's algorithm with deque (static analysis)

Plus Checkpoint 4 baseline comparison tests.

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
import json
import textwrap
from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import CircularDependencyError
from sysml_codegen.resolution.graph_builder import (
    _unified_topological_sort,
    _validate_channel_references,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)
from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
BASELINE_DIR = Path(__file__).parent.parent / "fixtures" / "baseline_outputs"


def _make_module(
    name: str,
    inputs: list[tuple[str, str | None]] | None = None,
    outputs: list[str] | None = None,
) -> PipelineModule:
    """Build a minimal PipelineModule for synthetic tests.

    Args:
        name: Module name.
        inputs: List of (param_name, producer_channel). None channel = entry_point.
        outputs: List of output channel names.
    """
    module_inputs = []
    for param_name, producer_channel in (inputs or []):
        if producer_channel:
            source = InputSource(
                source_type="module_output",
                producer_channel=producer_channel,
            )
        else:
            source = InputSource(
                source_type="entry_point",
                qualified_name=f"{name}__{param_name}",
                param_group="test_params",
            )
        module_inputs.append(ModuleInput(
            param_name=param_name,
            python_type="float",
            source=source,
        ))

    module_outputs = [
        ModuleOutput(
            field_name="root" if len(outputs or []) <= 1 else ch.split("__")[-1],
            python_type="float",
            channel_name=ch,
        )
        for ch in (outputs or [f"{name}__output"])
    ]

    return PipelineModule(
        name=name,
        module_type=f"{name}Module",
        inputs=module_inputs,
        outputs=module_outputs,
        execution_order=0,
    )


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_graph():
    """Full ComputationGraph for solar_battery_model."""
    graph, inputs = build_full_graph_from_snapshot(snapshot_fixture("solar_battery_model"))
    return graph


@pytest.fixture(scope="session")
def catf_mfe_graph():
    """Full ComputationGraph for catf_mfe_model."""
    graph, inputs = build_full_graph_from_snapshot(snapshot_fixture("catf_mfe_model"))
    return graph


@pytest.fixture(scope="session")
def chain_spike_graph():
    """Full ComputationGraph for chain_spike_model."""
    graph, inputs = build_full_graph_from_snapshot(snapshot_fixture("chain_spike_model"))
    return graph


@pytest.fixture(scope="session")
def attr_expr_probe_graph():
    """Full ComputationGraph for attr_expr_probe."""
    graph, inputs = build_full_graph_from_snapshot(snapshot_fixture("attr_expr_probe"))
    return graph


@pytest.fixture(
    scope="session",
    params=["solar_battery_model", "catf_mfe_model", "chain_spike_model"],
)
def real_graph(request):
    """Parametrized ComputationGraph across 3 models."""
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(request.param))
    return graph


# ===========================================================================
# REQ-BASE-06: entry_point_groups sorted by name (I1)
# ===========================================================================
ALL_BASELINE_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
    "chain_spike_model",
    "attr_expr_probe",
    "sample_model",
]


@pytest.mark.req("REQ-BASE-06")
@pytest.mark.parametrize("model_name", ALL_BASELINE_MODELS)
def test_entry_point_groups_sorted_by_name(model_name):
    """I1: every ComputationGraph's entry_point_groups is name-sorted, so a
    model-discovery-order shift can never redden a byte-exact baseline again."""
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
    names = [g.name for g in graph.entry_point_groups]
    assert names == sorted(names), (
        f"{model_name}: entry_point_groups not name-sorted: {names}"
    )


# ===========================================================================
# REQ-GA-01: Topological sort validity
# ===========================================================================
class TestTopologicalSortValid:
    """REQ-GA-01: execution_order is a valid topological sort."""

    @pytest.mark.req("REQ-GA-01")
    def test_topological_sort_valid(self, real_graph):
        """For every module_output input, the producer executes earlier."""
        graph = real_graph
        name_to_order = {m.name: m.execution_order for m in graph.modules}

        # Build channel -> module name index
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

    @pytest.mark.req("REQ-GA-01")
    def test_no_forward_references(self, real_graph):
        """For every module_output reference, the producer appears earlier in modules list."""
        graph = real_graph
        module_positions = {m.name: i for i, m in enumerate(graph.modules)}

        channel_to_module: dict[str, str] = {}
        for m in graph.modules:
            for out in m.outputs:
                channel_to_module[out.channel_name] = m.name

        for m in graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    producer = channel_to_module.get(inp.source.producer_channel)
                    if producer and producer != m.name:
                        assert module_positions[producer] < module_positions[m.name], (
                            f"Module {m.name} at position {module_positions[m.name]} "
                            f"references {producer} at position {module_positions[producer]}"
                        )

    @pytest.mark.req("REQ-GA-01")
    def test_all_three_module_types_present(self, solar_battery_graph):
        """solar_battery graph contains CalcUsage, FORMULA, and Aggregation modules."""
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

    @pytest.mark.req("REQ-GA-01")
    def test_empty_module_list(self):
        """_unified_topological_sort([]) returns empty list."""
        result = _unified_topological_sort([])
        assert result == []

    @pytest.mark.req("REQ-GA-01")
    def test_single_module_no_deps(self):
        """Single module with no deps gets execution_order=0."""
        m = _make_module("solo", inputs=[("x", None)], outputs=["solo__output"])
        result = _unified_topological_sort([m])
        assert len(result) == 1
        assert result[0].name == "solo"
        assert result[0].execution_order == 0


# ===========================================================================
# REQ-GA-02: Cycle detection
# ===========================================================================
class TestCycleDetection:
    """REQ-GA-02: Cycles raise CircularDependencyError."""

    @pytest.mark.req("REQ-GA-02")
    def test_cycle_detection_raises(self):
        """Two modules forming a cycle raise CircularDependencyError."""
        # A depends on B's output, B depends on A's output
        a = _make_module("mod_a", inputs=[("x", "b_output")], outputs=["a_output"])
        b = _make_module("mod_b", inputs=[("y", "a_output")], outputs=["b_output"])

        with pytest.raises(CircularDependencyError):
            _unified_topological_sort([a, b])

    @pytest.mark.req("REQ-GA-02")
    def test_cycle_detection_names_participants(self):
        """CircularDependencyError message contains cycle participant names."""
        a = _make_module("mod_a", inputs=[("x", "b_output")], outputs=["a_output"])
        b = _make_module("mod_b", inputs=[("y", "a_output")], outputs=["b_output"])

        with pytest.raises(CircularDependencyError, match="mod_a") as exc_info:
            _unified_topological_sort([a, b])

        msg = str(exc_info.value)
        assert "mod_a" in msg, f"mod_a not in error message: {msg}"
        assert "mod_b" in msg, f"mod_b not in error message: {msg}"


# ===========================================================================
# REQ-GA-03: Channel reference validation
# ===========================================================================
class TestChannelReferenceValidation:
    """REQ-GA-03: Every module_output producer_channel resolves to a declared channel."""

    @pytest.mark.req("REQ-GA-03")
    def test_all_channel_references_valid(self, real_graph):
        """All module_output references point to existing channels."""
        graph = real_graph
        declared_channels: set[str] = set()
        for m in graph.modules:
            for out in m.outputs:
                declared_channels.add(out.channel_name)

        for m in graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output":
                    channel = inp.source.producer_channel
                    if channel:
                        assert channel in declared_channels, (
                            f"Module {m.name} input {inp.param_name} references "
                            f"unknown channel {channel}"
                        )

    @pytest.mark.req("REQ-GA-03")
    def test_dangling_channel_raises(self):
        """Module with reference to nonexistent channel raises ValueError."""
        m = _make_module(
            "bad_ref",
            inputs=[("x", "nonexistent_channel")],
            outputs=["bad_ref__output"],
        )

        with pytest.raises(ValueError, match="nonexistent_channel"):
            _validate_channel_references([m])


# ===========================================================================
# REQ-GA-04: No self-dependency
# ===========================================================================
class TestNoSelfDependency:
    """REQ-GA-04: Modules do not depend on themselves."""

    @pytest.mark.req("REQ-GA-04")
    def test_no_self_dependency(self, real_graph):
        """No module in the real graph depends on its own output."""
        graph = real_graph
        for m in graph.modules:
            own_channels = {out.channel_name for out in m.outputs}
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    assert inp.source.producer_channel not in own_channels, (
                        f"Module {m.name} references its own output channel "
                        f"{inp.source.producer_channel}"
                    )

    @pytest.mark.req("REQ-GA-04")
    def test_self_reference_skipped_in_toposort(self):
        """Module whose input references its own output still sorts (self-edge ignored)."""
        m = _make_module(
            "self_ref",
            inputs=[("x", "self_ref__output"), ("y", None)],
            outputs=["self_ref__output"],
        )
        result = _unified_topological_sort([m])
        assert len(result) == 1
        assert result[0].name == "self_ref"
        assert result[0].execution_order == 0


# ===========================================================================
# REQ-GA-05: ComputationGraph has exactly 5 fields
# ===========================================================================
class TestComputationGraphShape:
    """REQ-GA-05: ComputationGraph has exactly modules, entry_point_groups,
    execution_order, fallback_entry_points, output_aliases."""

    @pytest.mark.req("REQ-GA-05")
    def test_computation_graph_has_exactly_three_fields(self):
        """ComputationGraph model has exactly 5 fields.

        Item 7 (REQ-GA-08) adds ``fallback_entry_points`` — an in-memory
        analysis artifact (``exclude=True``, kept out of the serialized graph)
        that the V11 collector reads. Item 11 (REQ-DM-09) adds
        ``output_aliases`` — a serialized field carrying the surfaced EXPOSE_PURE
        names. This exact-set flip red-then-green is the graph-rev discipline
        working.
        """
        assert set(ComputationGraph.model_fields.keys()) == {
            "modules",
            "entry_point_groups",
            "execution_order",
            "fallback_entry_points",
            "output_aliases",
        }

    @pytest.mark.req("REQ-GA-05")
    def test_graph_shape_from_real_data(self, real_graph):
        """Real ComputationGraph has correct types for its three collection fields
        (modules, entry_point_groups, execution_order)."""
        graph = real_graph
        assert isinstance(graph.modules, list)
        assert all(isinstance(m, PipelineModule) for m in graph.modules)

        assert isinstance(graph.entry_point_groups, list)
        assert all(isinstance(g, ParameterGroup) for g in graph.entry_point_groups)

        assert isinstance(graph.execution_order, list)
        assert all(isinstance(name, str) for name in graph.execution_order)


class TestReqDm09OutputAliasesField:
    """REQ-DM-09: `output_aliases` is a real serialized field (not `exclude=True`,
    contrast `fallback_entry_points`), stable-sorted by `(instance_path,
    alias_name)` (INV-5), and every entry's channel is a declared graph output
    (INV-3). The prior test only pinned the 4 OutputAlias field names -- not
    the sort, the validation, or the non-exclusion -- so a regression in any of
    those could ship silently."""

    @pytest.mark.req("REQ-DM-09")
    def test_output_aliases_is_not_excluded_from_serialization(self):
        """Contrast with `fallback_entry_points`, which IS `exclude=True`."""
        fields = ComputationGraph.model_fields
        assert fields["output_aliases"].exclude is not True, (
            "output_aliases must be serialized (exclude != True)"
        )
        assert fields["fallback_entry_points"].exclude is True, (
            "fallback_entry_points is the in-memory-only contrast case"
        )

    @pytest.mark.req("REQ-DM-09")
    def test_output_aliases_stable_sorted_by_instance_and_alias_name(
        self, catf_mfe_graph
    ):
        """catf_mfe_model has 44 output_aliases across many instance_paths --
        enough entries to actually exercise the sort, unlike solar_battery's
        single entry."""
        graph = catf_mfe_graph
        assert len(graph.output_aliases) > 1, (
            "Need multiple output_aliases entries to test sort order"
        )
        keys = [(a.instance_path, a.alias_name) for a in graph.output_aliases]
        assert keys == sorted(keys), (
            "output_aliases is not sorted by (instance_path, alias_name)"
        )

    @pytest.mark.req("REQ-DM-09")
    def test_every_output_alias_channel_is_a_declared_output(self, catf_mfe_graph):
        """INV-3: every emitted OutputAlias's canonical_channel is a real
        declared output channel, not a dangling reference."""
        graph = catf_mfe_graph
        declared_channels = {
            output.channel_name for module in graph.modules for output in module.outputs
        }
        undeclared = [
            a.canonical_channel
            for a in graph.output_aliases
            if a.canonical_channel not in declared_channels
        ]
        assert not undeclared, (
            f"output_aliases entries reference undeclared channels: {undeclared}"
        )


# ===========================================================================
# REQ-GA-06: execution_order matches module ordering
# ===========================================================================
class TestExecutionOrderMatchesModules:
    """REQ-GA-06: execution_order list equals [m.name for m in modules]."""

    @pytest.mark.req("REQ-GA-06")
    def test_execution_order_matches_module_names(self, real_graph):
        """execution_order == [m.name for m in modules]."""
        graph = real_graph
        assert graph.execution_order == [m.name for m in graph.modules]

    @pytest.mark.req("REQ-GA-06")
    def test_execution_order_indices_match_list_position(self, real_graph):
        """Every module at index i has execution_order == i."""
        graph = real_graph
        for i, m in enumerate(graph.modules):
            assert m.execution_order == i, (
                f"Module {m.name} at position {i} has execution_order={m.execution_order}"
            )


# ===========================================================================
# REQ-GA-07: Kahn's algorithm with deque (static analysis)
# ===========================================================================
class TestKahnsAlgorithm:
    """REQ-GA-07: Implementation uses Kahn's algorithm with deque."""

    @pytest.mark.req("REQ-GA-07")
    def test_toposort_uses_deque_and_popleft(self):
        """Static analysis: _unified_topological_sort uses deque and popleft()."""
        source = textwrap.dedent(inspect.getsource(_unified_topological_sort))
        tree = ast.parse(source)

        # Check for deque usage
        has_deque = False
        has_popleft = False

        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == "deque":
                has_deque = True
            if isinstance(node, ast.Attribute) and node.attr == "popleft":
                has_popleft = True

        assert has_deque, "deque not found in _unified_topological_sort source"
        assert has_popleft, "popleft() not found in _unified_topological_sort source"

    @pytest.mark.req("REQ-GA-07")
    def test_toposort_uses_kahn_pattern(self):
        """Static analysis: source contains in_degree, successors, and deque variables."""
        source = textwrap.dedent(inspect.getsource(_unified_topological_sort))
        tree = ast.parse(source)

        # Collect all Name identifiers used in assignments or as variables
        identifiers: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                identifiers.add(node.id)

        assert "in_degree" in identifiers, "in_degree not found in source"
        assert "successors" in identifiers, "successors not found in source"
        assert "deque" in identifiers, "deque not found in source"
        assert "sorted_names" in identifiers, "sorted_names not found in source"


# ===========================================================================
# Checkpoint 4: Baseline comparison
# ===========================================================================
class TestBaselineComparison:
    """Checkpoint 4: ComputationGraph matches Phase 0 baselines."""

    def _load_baseline(self, model_name: str) -> dict:
        """Load baseline ComputationGraph JSON."""
        baseline_path = BASELINE_DIR / model_name / "computation_graph.json"
        with open(baseline_path) as f:
            return json.load(f)

    def _compare_graph_to_baseline(self, graph: ComputationGraph, baseline: dict):
        """Compare a ComputationGraph against its baseline JSON.

        Note: CalcUsage modules have compilability='unknown' because
        build_full_graph_from_snapshot() passes compilation_results=None
        (AST fields are null in snapshots -- Phase 0 serialization boundary).
        FORMULA and aggregation modules set compilability directly in their
        factories, so those match. The full JSON comparison normalizes
        compilability for CalcUsage modules to account for this.
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
            assert m.name in baseline_by_name, (
                f"Module {m.name} not in baseline"
            )
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

        # Full JSON comparison with two normalizations:
        # 1. CalcUsage compilability: 'unknown' from snapshot (no compilation_results)
        #    vs 'fully_compilable' from live pipeline.
        # 2. entry_point_groups parameter ordering: dict iteration order differs
        #    between live and snapshot pipelines. Sort parameters by qualified_name
        #    within each group for stable comparison.
        graph_json = json.loads(graph.model_dump_json())
        baseline_normalized = json.loads(json.dumps(baseline))

        for gm, bm in zip(graph_json["modules"], baseline_normalized["modules"]):
            if not gm["is_computed_attribute"] and not gm["is_aggregation"]:
                bm["compilability"] = gm["compilability"]
            # Normalize source_file: snapshot uses relative paths,
            # capture script uses absolute paths
            if gm.get("source_file") and bm.get("source_file"):
                bm["source_file"] = gm["source_file"]

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

    @pytest.mark.baseline
    @pytest.mark.req("REQ-GA-01")
    def test_baseline_comparison_solar_battery(self, solar_battery_graph):
        """ComputationGraph for solar_battery matches Phase 0 baseline."""
        baseline = self._load_baseline("solar_battery")
        self._compare_graph_to_baseline(solar_battery_graph, baseline)

    @pytest.mark.baseline
    @pytest.mark.req("REQ-GA-01")
    def test_baseline_comparison_chain_spike(self, chain_spike_graph):
        """ComputationGraph for chain_spike matches Phase 0 baseline."""
        baseline = self._load_baseline("chain_spike")
        self._compare_graph_to_baseline(chain_spike_graph, baseline)

    @pytest.mark.baseline
    @pytest.mark.req("REQ-GA-01")
    def test_baseline_comparison_attr_expr_probe(self, attr_expr_probe_graph):
        """ComputationGraph for attr_expr_probe matches Phase 0 baseline."""
        baseline = self._load_baseline("attr_expr_probe")
        self._compare_graph_to_baseline(attr_expr_probe_graph, baseline)
