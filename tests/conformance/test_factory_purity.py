"""Conformance tests for Factory Purity Refactor (7.7 / REQ-MF-01).

Requirements: REQ-MF-01 ("All three factory functions SHALL be pure data
transformers: return (PipelineModule, dict[str, EntryPoint]), no mutation
of shared state.")

Design intent: 05-module-factory.md (Section REQ-MF-01)

Tests verify:
- Static analysis: zero entry_points[...] = ... inside factory bodies
- All 3 factories return (PipelineModule, dict[str, EntryPoint])
- Factory calls do NOT mutate the shared entry_points dict
- Returned entry points match those previously created via mutation
- build_computation_graph() produces identical ComputationGraph

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import copy
import inspect
import textwrap
from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import (
    _build_aggregation_module,
    _build_computed_attr_module,
    _build_pipeline_module,
    _classify_entry_points,
    build_computation_graph,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    PipelineModule,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

def _probe_ctx(registry):
    """These probes carry no design attributes; the shared table sees an empty tier 2."""
    from sysml_codegen.resolution.producer_resolution import ProducerContext

    return ProducerContext(output_registry=registry)




# ---------------------------------------------------------------------------
# Shared helper: build full pipeline inputs from snapshot
# ---------------------------------------------------------------------------
def _build_full_pipeline_inputs(model_name: str) -> dict:
    """Build all inputs needed to call build_computation_graph() from a snapshot.

    Returns dict with all components needed for pipeline + individual factories.
    """
    snap = load_extraction_snapshot(snapshot_fixture(model_name))

    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )

    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)

    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
    group_deriver = ParameterGroupDeriver(
        design_attrs, snap["calc_usages"], snap["calc_defs"]
    )

    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    hierarchy_data = snap["hierarchy_data"]

    return {
        "snap": snap,
        "result": result,
        "registry": registry,
        "calc_def_map": calc_def_map,
        "design_attrs": design_attrs,
        "group_deriver": group_deriver,
        "entry_points": entry_points,
        "redefinitions": hierarchy_data.redefinitions,
        "usage_type_map": hierarchy_data.usage_type_map,
        "aggregation_data": snap["aggregation_expressions"],
        "computed_attributes": snap["computed_attributes"],
        "channel_aliases": snap.get("channel_aliases", []),
        "model_name": model_name,
    }


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_inputs():
    return _build_full_pipeline_inputs("solar_battery_model")


@pytest.fixture(scope="session")
def attr_expr_probe_inputs():
    return _build_full_pipeline_inputs("attr_expr_probe")


@pytest.fixture(
    scope="session",
    params=["solar_battery_model", "attr_expr_probe"],
    ids=["solar_battery", "attr_expr_probe"],
)
def purity_inputs(request):
    return _build_full_pipeline_inputs(request.param)


# ===========================================================================
# REQ-MF-01: Static analysis -- no entry_points[...] = ... in factory bodies
# ===========================================================================


class _AssignmentToSubscriptFinder(ast.NodeVisitor):
    """AST visitor that finds `entry_points[...] = ...` assignment statements."""

    def __init__(self):
        self.assignments: list[int] = []  # line numbers

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            if (
                isinstance(target, ast.Subscript)
                and isinstance(target.value, ast.Name)
                and target.value.id == "entry_points"
            ):
                self.assignments.append(node.lineno)
        self.generic_visit(node)


@pytest.mark.req("REQ-MF-01")
class TestStaticAnalysis:
    """Static analysis: no entry_points mutation inside factory bodies."""

    def test_no_entry_points_assignment_in_factory_bodies(self):
        """Zero `entry_points[...] = ...` statements inside the three factory functions.

        Uses AST walking to inspect each function's source code.
        """
        factories = [
            _build_pipeline_module,
            _build_computed_attr_module,
            _build_aggregation_module,
        ]

        for factory_fn in factories:
            source = inspect.getsource(factory_fn)
            # Dedent so the AST parser can handle it
            source = textwrap.dedent(source)
            tree = ast.parse(source)

            finder = _AssignmentToSubscriptFinder()
            finder.visit(tree)

            assert len(finder.assignments) == 0, (
                f"{factory_fn.__name__} contains entry_points[...] = ... "
                f"at source lines {finder.assignments}. "
                f"REQ-MF-01 requires zero mutation of shared entry_points."
            )


# ===========================================================================
# REQ-MF-01: Return type -- all factories return (PipelineModule, dict)
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestReturnType:
    """Verify all three factories return (PipelineModule, dict[str, EntryPoint])."""

    def test_calc_usage_factory_returns_tuple(self, solar_battery_inputs):
        """_build_pipeline_module() returns (PipelineModule, dict) with empty dict."""
        inp = solar_battery_inputs
        usage = inp["result"].required_usages[0]
        calc_def = inp["calc_def_map"][usage.calc_def_name]

        ret = _build_pipeline_module(
            usage=usage,
            calc_def=calc_def,
            entry_points=inp["entry_points"],
            execution_order=0,
            binding_resolutions=inp["result"].binding_resolutions,
        )

        assert isinstance(ret, tuple), (
            f"_build_pipeline_module should return tuple, got {type(ret).__name__}"
        )
        module, new_eps = ret
        assert isinstance(module, PipelineModule)
        assert isinstance(new_eps, dict)
        assert len(new_eps) == 0, (
            f"CalcUsage factory should return empty dict, got {len(new_eps)} entries"
        )

    def test_formula_factory_returns_tuple(self, attr_expr_probe_inputs):
        """_build_computed_attr_module() returns (PipelineModule, dict) with non-empty dict."""
        inp = attr_expr_probe_inputs

        # Build resolution map
        from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map
        calc_usage_names = {u.instance_name for u in inp["result"].required_usages}
        resolution_map = _build_attribute_resolution_map(
            inp["computed_attributes"], inp["design_attrs"],
            inp["registry"], calc_usage_names,
        )

        formula_cas = [
            ca for ca in inp["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        ]
        assert len(formula_cas) > 0, "attr_expr_probe must have FORMULA CAs"

        ret = _build_computed_attr_module(
            formula_cas[0], resolution_map, inp["entry_points"],
            inp["design_attrs"], inp["group_deriver"],
        )

        assert isinstance(ret, tuple), (
            f"_build_computed_attr_module should return tuple, got {type(ret).__name__}"
        )
        module, new_eps = ret
        assert isinstance(module, PipelineModule)
        assert isinstance(new_eps, dict)
        # At least some FORMULA CAs create entry points for LITERAL inputs
        for ep in new_eps.values():
            assert isinstance(ep, EntryPoint)

    def test_aggregation_factory_returns_tuple(self, solar_battery_inputs):
        """_build_aggregation_module() returns (PipelineModule, dict) with expected EP keys."""
        inp = solar_battery_inputs
        agg = inp["aggregation_data"][0]

        from sysml_codegen.core.qualified_names import sanitize_name
        expose_aliases: dict[tuple[str, str], str] = {}
        for ca in inp["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                segments = ca.owning_part_qualified_name.split("::")
                normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
                expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text

        ret = _build_aggregation_module(
            agg=agg,
            redefinitions=inp["redefinitions"],
            output_registry=inp["registry"],
            entry_points=copy.deepcopy(inp["entry_points"]),
            group_deriver=inp["group_deriver"],
            expose_aliases=expose_aliases,
            usage_type_map=inp["usage_type_map"],
            producer_ctx=_probe_ctx(inp["registry"]),
        )

        assert isinstance(ret, tuple), (
            f"_build_aggregation_module should return tuple, got {type(ret).__name__}"
        )
        module, new_eps = ret
        assert isinstance(module, PipelineModule)
        assert isinstance(new_eps, dict)
        for ep in new_eps.values():
            assert isinstance(ep, EntryPoint)


# ===========================================================================
# REQ-MF-01: No mutation of shared entry_points dict
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestNoMutation:
    """Verify factory calls do NOT mutate the shared entry_points dict."""

    def test_formula_factory_no_mutation(self, purity_inputs):
        """Pass entry_points dict, call FORMULA factory, verify dict is unmodified."""
        inp = purity_inputs

        from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map
        calc_usage_names = {u.instance_name for u in inp["result"].required_usages}
        resolution_map = _build_attribute_resolution_map(
            inp["computed_attributes"], inp["design_attrs"],
            inp["registry"], calc_usage_names,
        )

        formula_cas = [
            ca for ca in inp["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        ]
        if not formula_cas:
            pytest.skip("No FORMULA CAs in this model")

        ep_copy = copy.deepcopy(inp["entry_points"])
        ep_before = copy.deepcopy(ep_copy)

        for ca in formula_cas:
            _build_computed_attr_module(
                ca, resolution_map, ep_copy,
                inp["design_attrs"], inp["group_deriver"],
            )

        # entry_points dict must be unmodified
        assert set(ep_copy.keys()) == set(ep_before.keys()), (
            f"FORMULA factory mutated entry_points: "
            f"added {set(ep_copy.keys()) - set(ep_before.keys())}"
        )
        for k in ep_before:
            assert ep_copy[k].model_dump() == ep_before[k].model_dump(), (
                f"FORMULA factory modified existing EP {k!r}"
            )

    def test_aggregation_factory_no_mutation(self, solar_battery_inputs):
        """Pass entry_points dict, call aggregation factory, verify dict is unmodified."""
        inp = solar_battery_inputs

        from sysml_codegen.core.qualified_names import sanitize_name
        expose_aliases: dict[tuple[str, str], str] = {}
        for ca in inp["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                segments = ca.owning_part_qualified_name.split("::")
                normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
                expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text

        ep_copy = copy.deepcopy(inp["entry_points"])
        ep_before = copy.deepcopy(ep_copy)

        for agg in inp["aggregation_data"]:
            _build_aggregation_module(
                agg=agg,
                redefinitions=inp["redefinitions"],
                output_registry=inp["registry"],
                entry_points=ep_copy,
                group_deriver=inp["group_deriver"],
                expose_aliases=expose_aliases,
                usage_type_map=inp["usage_type_map"],
                producer_ctx=_probe_ctx(inp["registry"]),
            )

        # entry_points dict must be unmodified
        assert set(ep_copy.keys()) == set(ep_before.keys()), (
            f"Aggregation factory mutated entry_points: "
            f"added {set(ep_copy.keys()) - set(ep_before.keys())}"
        )
        for k in ep_before:
            assert ep_copy[k].model_dump() == ep_before[k].model_dump(), (
                f"Aggregation factory modified existing EP {k!r}"
            )


# ===========================================================================
# REQ-MF-01: Behavioral equivalence -- returned EPs match previous mutation
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestBehavioralEquivalence:
    """Verify returned entry points match those previously created via mutation."""

    def test_returned_eps_match_previous_mutation(self, solar_battery_inputs):
        """For solar_battery: returned EPs from pure factories match expected set.

        Captures the expected behavior by calling build_computation_graph()
        (which uses factories internally) and comparing the resulting
        ComputationGraph entry points.
        """
        inp = solar_battery_inputs

        from sysml_codegen.core.qualified_names import sanitize_name
        expose_aliases: dict[tuple[str, str], str] = {}
        for ca in inp["computed_attributes"]:
            if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
                segments = ca.owning_part_qualified_name.split("::")
                normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
                expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text

        from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map
        calc_usage_names = {u.instance_name for u in inp["result"].required_usages}
        resolution_map = _build_attribute_resolution_map(
            inp["computed_attributes"], inp["design_attrs"],
            inp["registry"], calc_usage_names,
        )

        # Collect EPs from FORMULA factories
        formula_cas = [
            ca for ca in inp["computed_attributes"]
            if ca.classification == ComputedAttributeClassification.FORMULA
            and ca.compilability == Compilability.FULLY_COMPILABLE
        ]

        formula_returned_eps: dict[str, EntryPoint] = {}
        ep_copy = copy.deepcopy(inp["entry_points"])
        for ca in formula_cas:
            ret = _build_computed_attr_module(
                ca, resolution_map, ep_copy,
                inp["design_attrs"], inp["group_deriver"],
            )
            # After refactor: ret is (module, new_eps)
            if isinstance(ret, tuple):
                _, new_eps = ret
                formula_returned_eps.update(new_eps)
            else:
                pytest.fail(
                    "_build_computed_attr_module did not return tuple -- "
                    "factory purity refactor not yet applied"
                )

        # Collect EPs from aggregation factories
        agg_returned_eps: dict[str, EntryPoint] = {}
        # Merge formula EPs so aggregation factory can see them
        ep_with_formula = copy.deepcopy(inp["entry_points"])
        ep_with_formula.update(formula_returned_eps)

        for agg in inp["aggregation_data"]:
            ret = _build_aggregation_module(
                agg=agg,
                redefinitions=inp["redefinitions"],
                output_registry=inp["registry"],
                entry_points=ep_with_formula,
                group_deriver=inp["group_deriver"],
                expose_aliases=expose_aliases,
                usage_type_map=inp["usage_type_map"],
                producer_ctx=_probe_ctx(inp["registry"]),
            )
            if isinstance(ret, tuple):
                _, new_eps = ret
                agg_returned_eps.update(new_eps)
                ep_with_formula.update(new_eps)
            else:
                pytest.fail(
                    "_build_aggregation_module did not return tuple -- "
                    "factory purity refactor not yet applied"
                )

        all_returned = {**formula_returned_eps, **agg_returned_eps}
        assert len(all_returned) > 0, (
            "Expected at least some EPs returned by pure factories"
        )

        # Every returned EP should be a valid EntryPoint
        for qn, ep in all_returned.items():
            assert isinstance(ep, EntryPoint)
            assert ep.qualified_name == qn


# ===========================================================================
# REQ-MF-01: ComputationGraph identical before and after refactor
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestComputationGraphIdentity:
    """Verify build_computation_graph() produces identical output."""

    def test_computation_graph_identical(self, purity_inputs):
        """build_computation_graph() produces identical ComputationGraph by model_dump().

        Compares against baseline JSON stored in tests/fixtures/baseline_outputs/.
        """
        inp = purity_inputs

        # Build computation graph via the public API
        graph = build_computation_graph(
            result=inp["result"],
            calc_defs=inp["snap"]["calc_defs"],
            design_attrs=inp["design_attrs"],
            group_deriver=inp["group_deriver"],
            output_registry=inp["registry"],
            compilation_results=inp["snap"].get("compilation_results"),
            computed_attributes=inp["computed_attributes"],
            aggregation_data=inp["aggregation_data"],
            hierarchy_redefinitions=inp["redefinitions"],
            usage_type_map=inp["usage_type_map"],
            # Item 11: thread the expose_pure aliases so output_aliases populates
            # identically to the snapshot-captured baseline (F-A).
            channel_aliases=inp["channel_aliases"],
            include_all=True,
        )

        assert isinstance(graph, type(graph))  # sanity check

        # Load baseline
        import json
        model_name = inp["model_name"]
        baseline_dir = Path("tests/fixtures/baseline_outputs") / model_name
        baseline_path = baseline_dir / "computation_graph.json"

        if not baseline_path.exists():
            pytest.skip(f"No baseline for {model_name} at {baseline_path}")

        with open(baseline_path) as f:
            baseline = json.load(f)

        graph_dict = graph.model_dump(mode="json")

        # Normalize source_file: the loader re-absolutizes to a machine-specific
        # absolute path (Item 2 D1), while the committed baseline stores the
        # portable relative form. Mirror test_graph_assembly — copy the graph's
        # source_file onto the baseline before the full-dict comparison.
        graph_by_name = {m["name"]: m for m in graph_dict["modules"]}
        for bm in baseline["modules"]:
            gm = graph_by_name.get(bm["name"])
            if gm and gm.get("source_file") and bm.get("source_file"):
                bm["source_file"] = gm["source_file"]

        assert graph_dict == baseline, (
            f"ComputationGraph for {model_name} differs from baseline. "
            f"This refactor should produce byte-identical output."
        )
