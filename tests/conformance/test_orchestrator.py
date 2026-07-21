"""Conformance tests for Orchestrator Step Ordering (C19).

Requirements: REQ-ORCH-01 through REQ-ORCH-07, REQ-PIPE-01 through REQ-PIPE-07
Design intent: 02-orchestration.md, 00-pipeline-overview.md

Tests verify the orchestration layer:
- Static analysis: build_pipeline_context() call ordering matches DAG
- FORMULA removal before ParameterGroupDeriver
- OutputRegistry 4-phase registration ordering
- Aggregation scoping produces >= expression count
- CHAIN alias unresolvable = warning, not error
- Pipeline-level invariants across 4 models (via build_full_graph_from_snapshot)
- ComputationGraph is the generation boundary

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
import logging
import textwrap
from pathlib import Path

import pytest

from sysml_codegen.core.identifier_types import ScopedKey
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ScopedAggregationData,
)
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.orchestration.pipeline_builder import (
    _remove_formula_from_design_attrs,
    _scope_aggregation_expressions,
    build_pipeline_context,
)
from sysml_codegen.resolution.graph_builder import build_computation_graph
from sysml_codegen.resolution.models import (
    ComputationGraph,
    EntryPointType,
    ModuleKind,
    PipelineModule,
)
from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import requires_license, snapshot_fixture
from sysml_codegen.snapshot import load_extraction_snapshot

FIXTURES_DIR = Path(__file__).resolve().parents[1] / "fixtures"


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
    params=["solar_battery_model", "catf_mfe_model", "chain_spike_model", "attr_expr_probe"],
)
def pipeline_graph(request):
    """Parametrized ComputationGraph across 4 models."""
    graph, _inputs = build_full_graph_from_snapshot(snapshot_fixture(request.param))
    return graph


# ===========================================================================
# Static Analysis: Step Ordering (REQ-ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-06)
# ===========================================================================
def _get_call_lines_in_function(func, call_names: list[str]) -> dict[str, list[int]]:
    """Parse a function's source and find line numbers for named function calls.

    Returns dict mapping call_name -> list of line numbers where that call appears.
    """
    source = textwrap.dedent(inspect.getsource(func))
    tree = ast.parse(source)

    result: dict[str, list[int]] = {name: [] for name in call_names}

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name in result:
                result[func_name].append(node.lineno)

    return result


class TestStepOrdering:
    """REQ-ORCH-01: build_pipeline_context() calls appear in strict DAG order."""

    @pytest.mark.req("REQ-ORCH-01")
    def test_step_ordering_call_sequence(self):
        """Call sites in build_pipeline_context appear in strict DAG order.

        Expected order (Item 10 / INV-G: ParameterGroupDeriver moved AFTER
        build_output_registry so it consumes design_attrs with the confirm pass's
        final classifications):
        extract_calculation_definitions → extract_calculation_usages →
        _extract_hierarchy_and_rewrite_bindings → extract_design_attributes →
        _extract_and_filter_computed_attributes → build_output_registry →
        ParameterGroupDeriver → DependencyBacktracker → compile_calc_def →
        build_computation_graph
        """
        ordered_calls = [
            "extract_calculation_definitions",
            "extract_calculation_usages",
            "_extract_hierarchy_and_rewrite_bindings",
            "extract_design_attributes",
            "_extract_and_filter_computed_attributes",
            "build_output_registry",
            "ParameterGroupDeriver",
            "DependencyBacktracker",
            "compile_calc_def",
            "build_computation_graph",
        ]

        lines = _get_call_lines_in_function(build_pipeline_context, ordered_calls)

        # Every call should appear at least once
        for name in ordered_calls:
            assert len(lines[name]) > 0, (
                f"Expected call to {name} in build_pipeline_context, not found"
            )

        # Verify strict ordering: first occurrence of each call before first of next
        for i in range(len(ordered_calls) - 1):
            current = ordered_calls[i]
            next_call = ordered_calls[i + 1]
            assert min(lines[current]) < min(lines[next_call]), (
                f"{current} (line {min(lines[current])}) should appear before "
                f"{next_call} (line {min(lines[next_call])}) in build_pipeline_context"
            )

    @pytest.mark.req("REQ-ORCH-02")
    def test_vbr_before_registry_and_backtracker(self):
        """_extract_hierarchy_and_rewrite_bindings appears before registry and backtracker."""
        calls = [
            "_extract_hierarchy_and_rewrite_bindings",
            "build_output_registry",
            "DependencyBacktracker",
        ]
        lines = _get_call_lines_in_function(build_pipeline_context, calls)

        for name in calls:
            assert len(lines[name]) > 0, f"{name} not found in build_pipeline_context"

        vbr_line = min(lines["_extract_hierarchy_and_rewrite_bindings"])
        registry_line = min(lines["build_output_registry"])
        backtracker_line = min(lines["DependencyBacktracker"])

        assert vbr_line < registry_line, (
            f"VBR (line {vbr_line}) should be before build_output_registry (line {registry_line})"
        )
        assert vbr_line < backtracker_line, (
            f"VBR (line {vbr_line}) should be before DependencyBacktracker (line {backtracker_line})"
        )

    @pytest.mark.req("REQ-ORCH-02")
    def test_virtual_binding_mutated_in_place_by_step_3_5(self):
        """Step 3.5's rewrite actually mutates `binding_type` in the `CalcUsageData`
        the rest of the pipeline reads -- not just source-order proof.

        The source-order test above confirms VBR runs before the registry/backtracker
        read `calc_usages`, but never observes that the rewrite itself changes
        anything. This constructs a virtual binding backed by a design override (the
        same shape `_rewrite_virtual_bindings`'s own unit tests use) and asserts the
        binding's `binding_type` and `source_path` are different after the call --
        the in-place mutation downstream steps depend on.
        """
        from agentic_mbse.sysml.types import BindingType

        from sysml_codegen.extraction.data_models import (
            HierarchyExtractionResult,
            RedefinitionData,
            RedefinitionType,
        )
        from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
        from sysml_codegen.orchestration.pipeline_builder import _rewrite_virtual_bindings

        binding = BindingInfo(
            param_name="total_cost",
            source_path="Lib::CostModel::total_cost",
            binding_type=BindingType.REFERENCE,
        )
        usage = CalcUsageData(
            instance_name="Design__plant__cost_model",
            calc_def_name="CostModel",
            calc_def_qualified_name="Lib__CostModel",
            module_type="CostModelModule",
            bindings=[binding],
            qualified_name="Design__plant__cost_model",
            is_template=False,
            owning_part_def_qn=None,
        )
        hierarchy_data = HierarchyExtractionResult(
            redefinitions=[],
            design_overrides=[
                RedefinitionData(
                    owning_part_qn="Design__plant",
                    attribute_name="total_cost",
                    redefinition_type=RedefinitionType.LITERAL,
                    literal_value=999.0,
                    is_deep_path=False,
                ),
            ],
            multiplicities=[],
            aggregation_expressions=[],
            warnings=[],
        )
        original_binding_type = binding.binding_type
        original_source_path = binding.source_path

        rewritten = _rewrite_virtual_bindings([usage], hierarchy_data)

        assert rewritten == 1
        assert usage.bindings[0].binding_type != original_binding_type, (
            "binding_type was not mutated in place"
        )
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].source_path != original_source_path

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_before_pgd_in_source(self):
        """_extract_and_filter_computed_attributes (which calls _remove_formula_from_design_attrs)
        appears before ParameterGroupDeriver in build_pipeline_context."""
        calls = ["_extract_and_filter_computed_attributes", "ParameterGroupDeriver"]
        lines = _get_call_lines_in_function(build_pipeline_context, calls)

        for name in calls:
            assert len(lines[name]) > 0, f"{name} not found in build_pipeline_context"

        formula_line = min(lines["_extract_and_filter_computed_attributes"])
        pgd_line = min(lines["ParameterGroupDeriver"])

        assert formula_line < pgd_line, (
            f"FORMULA removal (line {formula_line}) should be before "
            f"ParameterGroupDeriver (line {pgd_line})"
        )

    @pytest.mark.req("REQ-ORCH-04")
    def test_registry_before_backtracker_in_source(self):
        """build_output_registry appears before DependencyBacktracker."""
        calls = ["build_output_registry", "DependencyBacktracker"]
        lines = _get_call_lines_in_function(build_pipeline_context, calls)

        for name in calls:
            assert len(lines[name]) > 0, f"{name} not found in build_pipeline_context"

        assert min(lines["build_output_registry"]) < min(lines["DependencyBacktracker"]), (
            "build_output_registry should appear before DependencyBacktracker"
        )

    @pytest.mark.req("REQ-ORCH-06")
    def test_computation_graph_is_last_step(self):
        """build_computation_graph is the last significant call before return PipelineContext."""
        source = textwrap.dedent(inspect.getsource(build_pipeline_context))
        tree = ast.parse(source)

        # Find all function calls and their line numbers
        all_calls: list[tuple[int, str]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr
                if func_name:
                    all_calls.append((node.lineno, func_name))

        # Find line number for build_computation_graph and PipelineContext
        graph_lines = [ln for ln, name in all_calls if name == "build_computation_graph"]
        context_lines = [ln for ln, name in all_calls if name == "PipelineContext"]

        assert len(graph_lines) >= 1, "build_computation_graph not found"
        assert len(context_lines) >= 1, "PipelineContext not found"

        graph_line = max(graph_lines)
        context_line = min(context_lines)

        # No other "significant" pipeline calls between graph and context
        significant_calls = {
            "extract_calculation_definitions",
            "extract_calculation_usages",
            "_extract_hierarchy_and_rewrite_bindings",
            "extract_design_attributes",
            "_extract_and_filter_computed_attributes",
            "ParameterGroupDeriver",
            "build_output_registry",
            "DependencyBacktracker",
            "find_required_modules",
        }
        between_calls = [
            (ln, name) for ln, name in all_calls
            if graph_line < ln < context_line and name in significant_calls
        ]
        assert len(between_calls) == 0, (
            f"Significant calls between build_computation_graph and PipelineContext: "
            f"{between_calls}"
        )

    @pytest.mark.req("REQ-ORCH-06")
    @pytest.mark.req("REQ-PIPE-07")
    @requires_license
    def test_computation_graph_identity_is_the_generation_boundary(self):
        """`PipelineContext.computation_graph` IS the object build_computation_graph
        returned -- not a copy, not a re-derived value.

        The source-order test above (`test_computation_graph_is_last_step`) proves
        `build_computation_graph` runs immediately before `PipelineContext(...)` is
        constructed, but never observes what actually flows into the field. This
        runs the real pipeline against a small fixture and asserts object identity,
        which is what makes ComputationGraph the generation boundary REQ-PIPE-07
        also pins (`TestGenerationBoundary`): everything downstream of `ctx` must
        see the exact same graph `build_computation_graph` produced.
        """
        from sysml_codegen.resolution import graph_builder

        captured: list[ComputationGraph] = []
        original = graph_builder.build_computation_graph

        def _spy(*args, **kwargs):
            graph = original(*args, **kwargs)
            captured.append(graph)
            return graph

        import sysml_codegen.orchestration.pipeline_builder as pipeline_builder_module

        pipeline_builder_module.build_computation_graph = _spy
        try:
            # lower_constraints_enabled=False: wi014_toy carries an admitted
            # assertion, and P3 EXTEND reassigns `computation_graph` to a new
            # object post-`build_computation_graph` (Item 5) — orthogonal to
            # what this test pins (identity up to that boundary).
            ctx = build_pipeline_context(
                [FIXTURES_DIR / "wi014_toy"], lower_constraints_enabled=False
            )
        finally:
            pipeline_builder_module.build_computation_graph = original

        assert len(captured) == 1
        assert ctx.computation_graph is captured[0], (
            "PipelineContext.computation_graph is not the exact object "
            "build_computation_graph returned"
        )


class TestInnerStepOrdering:
    """REQ-RES-05: build_computation_graph()'s INTERNAL milestones in source order.

    Distinct from TestStepOrdering above, which pins the OUTER
    build_pipeline_context DAG (REQ-ORCH-01) — a different function. This pins
    the inner sequence the docs state (03-resolution-overview.md):
    classify → build modules → rebuild groups → toposort → validate.

    Documented-milestone → real-call-name map (the doc uses simplified names):
    classify = _classify_entry_points; build modules = the three
    _build_*_module factories; rebuild groups = derive_groups() (there is no
    literal "rebuild_groups" call); toposort = _unified_topological_sort;
    validate = _validate_channel_references.
    """

    @pytest.mark.req("REQ-RES-05")
    def test_inner_step_ordering_source(self):
        """The five milestones each appear, in the documented source order."""
        milestones = [
            ["_classify_entry_points"],
            [
                "_build_pipeline_module",
                "_build_computed_attr_module",
                "_build_aggregation_module",
            ],
            ["derive_groups"],
            ["_unified_topological_sort"],
            ["_validate_channel_references"],
        ]
        flat = [c for group in milestones for c in group]
        lines = _get_call_lines_in_function(build_computation_graph, flat)

        for group in milestones:
            assert any(lines[c] for c in group), f"missing milestone: {group}"

        # First occurrence of each milestone must be in documented order; for
        # the build-modules milestone, ALL three factories must sit between
        # classify and derive_groups (a single min() would let one drift).
        classify_first = min(lines["_classify_entry_points"])
        build_firsts = [min(lines[c]) for c in milestones[1] if lines[c]]
        groups_first = min(lines["derive_groups"])
        topo_first = min(lines["_unified_topological_sort"])
        validate_first = min(lines["_validate_channel_references"])

        for ln in build_firsts:
            assert classify_first < ln < groups_first, (
                f"a module factory call (line {ln}) is outside the "
                f"classify({classify_first}) .. derive_groups({groups_first}) window"
            )
        assert groups_first < topo_first < validate_first, (
            f"rebuild-groups({groups_first}) → toposort({topo_first}) → "
            f"validate({validate_first}) out of source order"
        )


# ===========================================================================
# FORMULA Removal (REQ-ORCH-03)
# ===========================================================================
class TestFormulaRemoval:
    """REQ-ORCH-03: FORMULA attrs removed from design_attrs before PGD."""

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_attr_expr_probe(self, extraction_snapshots):
        """_remove_formula_from_design_attrs with attr_expr_probe: runs without error.

        attr_expr_probe has 14 FORMULA CAs but their QNs don't overlap with
        design attribute QNs (different extraction sources). The function
        correctly returns 0 — the safety net isn't needed for this model.
        """
        snap = extraction_snapshots["attr_expr_probe"]
        computed_attrs = snap["computed_attributes"]
        design_attrs = {Path(k): list(v) for k, v in snap["design_attributes"].items()}

        # Count FORMULA CAs
        formula_count = sum(
            1 for ca in computed_attrs
            if ca.classification == ComputedAttributeClassification.FORMULA
        )
        assert formula_count > 0, "attr_expr_probe should have FORMULA computed attrs"

        before_count = sum(len(v) for v in design_attrs.values())
        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)
        after_count = sum(len(v) for v in design_attrs.values())

        assert removed == before_count - after_count, (
            f"removed={removed} but count delta={before_count - after_count}"
        )

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_constructed_overlap(self, extraction_snapshots):
        """Constructed test: inject a design_attr whose QN matches a FORMULA QN."""
        from sysml_codegen.analysis.parameter_groups import DesignAttributeData
        from sysml_codegen.core.qualified_names import sysml_to_python_qualified_name

        snap = extraction_snapshots["attr_expr_probe"]
        computed_attrs = snap["computed_attributes"]

        # Find a FORMULA CA to use as the overlap target
        formula_cas = [
            ca for ca in computed_attrs
            if ca.classification == ComputedAttributeClassification.FORMULA
        ]
        assert len(formula_cas) > 0
        target_ca = formula_cas[0]

        # Build the QN that _remove_formula_from_design_attrs would match
        part_qn_python = sysml_to_python_qualified_name(target_ca.owning_part_qualified_name)
        formula_qn = f"{part_qn_python}__{target_ca.python_name}"

        # Inject a synthetic design_attr with matching QN
        synthetic_attr = DesignAttributeData(
            name=target_ca.python_name,
            sysml_type="Real",
            default_value=None,
            unit=None,
            source_file=Path("synthetic"),
            source_line=0,
            parent_part=target_ca.owning_part_name,
            qualified_name=formula_qn,
        )
        design_attrs: dict[Path, list[DesignAttributeData]] = {
            Path("synthetic"): [synthetic_attr],
        }

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)
        assert removed == 1, f"Expected 1 removal for constructed overlap, got {removed}"
        assert len(design_attrs[Path("synthetic")]) == 0, "Synthetic attr not removed"

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_solar_battery(self, extraction_snapshots):
        """_remove_formula_from_design_attrs with solar_battery: FORMULA CA QNs removed."""
        snap = extraction_snapshots["solar_battery_model"]
        computed_attrs = snap["computed_attributes"]
        design_attrs = {Path(k): list(v) for k, v in snap["design_attributes"].items()}

        formula_count = sum(
            1 for ca in computed_attrs
            if ca.classification == ComputedAttributeClassification.FORMULA
        )

        removed = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        if formula_count == 0:
            assert removed == 0, "No FORMULA CAs but removed > 0"
        # Either way, function should not raise

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_preserves_non_formula(self, extraction_snapshots):
        """Non-FORMULA design_attrs survive removal."""
        snap = extraction_snapshots["attr_expr_probe"]
        computed_attrs = snap["computed_attributes"]
        design_attrs = {Path(k): list(v) for k, v in snap["design_attributes"].items()}

        # Build FORMULA QN set (same logic as production code)
        from sysml_codegen.core.qualified_names import sysml_to_python_qualified_name

        formula_qns: set[str] = set()
        for ca in computed_attrs:
            if ca.classification == ComputedAttributeClassification.FORMULA:
                part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
                formula_qns.add(f"{part_qn_python}__{ca.python_name}")

        # Collect non-FORMULA QNs before removal
        non_formula_before = []
        for attrs in design_attrs.values():
            for attr in attrs:
                if attr.qualified_name not in formula_qns:
                    non_formula_before.append(attr.qualified_name)

        _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        # Collect non-FORMULA QNs after removal
        non_formula_after = []
        for attrs in design_attrs.values():
            for attr in attrs:
                non_formula_after.append(attr.qualified_name)

        # All non-formula attrs should still be present
        assert set(non_formula_before) == set(non_formula_after), (
            f"Non-FORMULA attrs changed during removal:\n"
            f"  Lost: {set(non_formula_before) - set(non_formula_after)}\n"
            f"  Gained: {set(non_formula_after) - set(non_formula_before)}"
        )

    @pytest.mark.req("REQ-ORCH-03")
    def test_formula_removal_idempotent(self, extraction_snapshots):
        """Calling _remove_formula_from_design_attrs twice: second call returns same or 0."""
        from sysml_codegen.analysis.parameter_groups import DesignAttributeData
        from sysml_codegen.core.qualified_names import sysml_to_python_qualified_name

        snap = extraction_snapshots["attr_expr_probe"]
        computed_attrs = snap["computed_attributes"]

        # Build design_attrs with constructed overlap to ensure first call removes > 0
        formula_cas = [
            ca for ca in computed_attrs
            if ca.classification == ComputedAttributeClassification.FORMULA
        ]
        assert len(formula_cas) > 0

        synthetic_attrs: list[DesignAttributeData] = []
        for ca in formula_cas[:3]:  # Use first 3 FORMULA CAs
            part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
            formula_qn = f"{part_qn_python}__{ca.python_name}"
            synthetic_attrs.append(DesignAttributeData(
                name=ca.python_name,
                sysml_type="Real",
                default_value=None,
                unit=None,
                source_file=Path("synthetic"),
                source_line=0,
                parent_part=ca.owning_part_name,
                qualified_name=formula_qn,
            ))
        design_attrs: dict[Path, list[DesignAttributeData]] = {
            Path("synthetic"): synthetic_attrs,
        }

        first = _remove_formula_from_design_attrs(computed_attrs, design_attrs)
        second = _remove_formula_from_design_attrs(computed_attrs, design_attrs)

        assert first > 0, "First call should remove at least 1"
        assert second == 0, f"Second call should remove 0, got {second}"


# ===========================================================================
# Registry Phase Ordering (REQ-ORCH-04)
# ===========================================================================
class TestRegistryPhaseOrdering:
    """REQ-ORCH-04: OutputRegistry 4-phase registration ordering."""

    # Hand-transcribed from the solar_battery fixture (Item-6 anchoring rule: the
    # expectation is written independently, NEVER computed by the code under test →
    # INV-E). Each is a Phase-1a Key_A alias (`{usage_qn}.{attr}`) whose target is
    # the canonical channel `{usage_qn}__{attr}`. register_alias's phase-order guard
    # (REQ-OR-04: target must already be in _canonical) registers these only because
    # Phase 1a's register_scoped runs BEFORE its register_alias. Swap that order and
    # the guard drops them — which the red-mutation gate below proves.
    EXPECTED_KEY_A_ALIASES = {
        "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model.total_allocation":
            "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model__total_allocation",
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model.total_cost":
            "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost",
        "SolarBatteryDesign__solar_battery_plant__site_infra__permitting__cost_model.material_cost":
            "SolarBatteryDesign__solar_battery_plant__site_infra__permitting__cost_model__material_cost",
    }

    @pytest.mark.req("REQ-ORCH-04")
    def test_expected_key_a_aliases_present_solar_battery(self, extraction_snapshots):
        """PRESENCE assertion (C1): each hand-transcribed Phase-1a Key_A alias
        resolves to its canonical channel on the real corpus.

        This is NOT a survivors-are-canonical check (which holds by construction —
        the guard drops mis-ordered aliases before they enter _alias, so iterating
        _alias can never see a dropped one). A phase-order regression that swaps
        Phase-1a's register_scoped/register_alias order makes the expected alias
        VANISH from the registry; this assertion then fails. Proven by the
        red-mutation gate recorded in the Item 7 R4 table."""
        snap = extraction_snapshots["solar_battery_model"]
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )
        missing = []
        for alias, canonical in self.EXPECTED_KEY_A_ALIASES.items():
            got = registry.alias_lookup(ScopedKey(alias))
            if got is None or str(got) != canonical:
                missing.append(f"{alias} → expected {canonical}, got {got}")
        assert not missing, (
            "Expected Phase-1a Key_A aliases absent (phase-order regression?):\n"
            + "\n".join(missing)
        )

    @pytest.mark.req("REQ-ORCH-04")
    def test_all_aliases_target_canonical_channels_solar_battery(
        self, extraction_snapshots
    ):
        """Every alias_lookup result is in registry.canonical_channels for solar_battery."""
        snap = extraction_snapshots["solar_battery_model"]
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        canonical_set = registry.canonical_channels
        assert len(canonical_set) > 0, "No canonical channels registered"

        # Check every alias resolves to a canonical channel
        for alias_key, channel in registry._alias.items():
            assert channel in canonical_set, (
                f"Alias {alias_key} → {channel} not in canonical_channels"
            )

    @pytest.mark.req("REQ-ORCH-04")
    def test_all_aliases_target_canonical_channels_catf_mfe(
        self, extraction_snapshots
    ):
        """Every alias_lookup result is in registry.canonical_channels for catf_mfe."""
        snap = extraction_snapshots["catf_mfe_model"]
        registry = build_output_registry(
            calc_usages=snap["calc_usages"],
            calc_defs=snap["calc_defs"],
            aggregation_data=snap["aggregation_expressions"],
            computed_attributes=snap["computed_attributes"],
            channel_aliases=snap.get("channel_aliases", []),
            design_attributes=snap.get("design_attributes", {}),
        )

        canonical_set = registry.canonical_channels
        assert len(canonical_set) > 0, "No canonical channels registered"

        for alias_key, channel in registry._alias.items():
            assert channel in canonical_set, (
                f"Alias {alias_key} → {channel} not in canonical_channels"
            )


# ===========================================================================
# Aggregation Scoping (REQ-ORCH-05)
# ===========================================================================
class TestAggregationScoping:
    """REQ-ORCH-05: Each aggregation expression scoped to design instances."""

    @pytest.mark.req("REQ-ORCH-05")
    def test_every_aggregation_expression_produces_a_scoped_instance(
        self, extraction_snapshots
    ):
        """Every source expression appears in the scoped output at least once.

        A bare `len(scoped) >= len(expressions)` count floor lets one
        over-producing expression (multiple design instances) mask another
        scoping to zero -- the totals can still satisfy `>=` while a real
        expression is silently dropped. Assert set membership instead: every
        (owning_part_qn, attribute_name) pair from the source expressions must
        be represented by at least one scoped entry.
        """
        snap = extraction_snapshots["solar_battery_model"]
        hierarchy_data = snap["hierarchy_data"]
        calc_usages = snap["calc_usages"]

        expressions = hierarchy_data.aggregation_expressions
        assert len(expressions) > 0, "solar_battery has no aggregation expressions"

        scoped = _scope_aggregation_expressions(hierarchy_data, calc_usages)

        scoped_ids = {
            (s.expression.owning_part_qn, s.expression.attribute_name) for s in scoped
        }
        missing = [
            (e.owning_part_qn, e.attribute_name)
            for e in expressions
            if (e.owning_part_qn, e.attribute_name) not in scoped_ids
        ]
        assert not missing, (
            f"{len(missing)} aggregation expression(s) produced zero scoped "
            f"instances: {missing}"
        )


# ===========================================================================
# CHAIN Alias Warning (REQ-ORCH-07)
# ===========================================================================
class TestChainAliasWarning:
    """REQ-ORCH-07: Unresolvable CHAIN alias logs warning, not error."""

    @pytest.mark.req("REQ-ORCH-07")
    def test_unresolvable_chain_alias_logs_warning(
        self, extraction_snapshots, caplog
    ):
        """Build registry with unresolvable CHAIN alias → WARNING logged, no exception."""
        snap = extraction_snapshots["solar_battery_model"]

        # Add a constructed unresolvable CHAIN alias
        fake_alias = ChannelAlias(
            alias_name="fake.unresolvable_alias",
            canonical_name="nonexistent.channel.that.does.not.exist",
            owning_part_qn="TestPartDef",
            source="redefinition",
        )
        aliases = list(snap.get("channel_aliases", [])) + [fake_alias]

        with caplog.at_level(logging.WARNING, logger="sysml_codegen.orchestration.output_registry_builder"):
            registry = build_output_registry(
                calc_usages=snap["calc_usages"],
                calc_defs=snap["calc_defs"],
                aggregation_data=snap["aggregation_expressions"],
                computed_attributes=snap["computed_attributes"],
                channel_aliases=aliases,
                design_attributes=snap.get("design_attributes", {}),
            )

        # Verify warning was logged
        warning_records = [
            r for r in caplog.records
            if r.levelno >= logging.WARNING
            and "nonexistent.channel.that.does.not.exist" in r.message
        ]
        assert len(warning_records) > 0, (
            "Expected WARNING log for unresolvable CHAIN alias, got none. "
            f"Log records: {[r.message for r in caplog.records]}"
        )

        # Registry was still returned (no exception)
        assert registry is not None

    @pytest.mark.req("REQ-ORCH-07")
    def test_resolvable_chain_aliases_no_warning_solar_battery(
        self, extraction_snapshots, caplog
    ):
        """Build registry with solar_battery data → no Phase 2 warning logged."""
        snap = extraction_snapshots["solar_battery_model"]

        with caplog.at_level(logging.WARNING, logger="sysml_codegen.orchestration.output_registry_builder"):
            build_output_registry(
                calc_usages=snap["calc_usages"],
                calc_defs=snap["calc_defs"],
                aggregation_data=snap["aggregation_expressions"],
                computed_attributes=snap["computed_attributes"],
                channel_aliases=snap.get("channel_aliases", []),
                design_attributes=snap.get("design_attributes", {}),
            )

        phase2_warnings = [
            r for r in caplog.records
            if r.levelno >= logging.WARNING and "Phase 2" in r.message
        ]
        assert len(phase2_warnings) == 0, (
            f"Unexpected Phase 2 warnings for solar_battery: "
            f"{[r.message for r in phase2_warnings]}"
        )


# ===========================================================================
# Pipeline Invariants (REQ-PIPE-01 through REQ-PIPE-06)
# Parametrized over 4 models via pipeline_graph fixture
# ===========================================================================
class TestProducesComputationGraph:
    """REQ-PIPE-01: Pipeline produces a ComputationGraph instance."""

    @pytest.mark.req("REQ-PIPE-01")
    def test_produces_computation_graph(self, pipeline_graph):
        """build_full_graph_from_snapshot returns a ComputationGraph instance."""
        assert isinstance(pipeline_graph, ComputationGraph)
        assert len(pipeline_graph.modules) > 0, "Graph has no modules"
        assert len(pipeline_graph.execution_order) > 0, "Graph has no execution_order"


class TestEveryModuleInputWired:
    """REQ-PIPE-02: Every ModuleInput has a valid source."""

    @pytest.mark.req("REQ-PIPE-02")
    def test_every_module_input_wired(self, pipeline_graph):
        """Every ModuleInput has source_type in {module_output, entry_point}."""
        valid_types = {"module_output", "entry_point"}
        for module in pipeline_graph.modules:
            for inp in module.inputs:
                assert inp.source.source_type in valid_types, (
                    f"Module {module.name} input {inp.param_name} has invalid "
                    f"source_type: {inp.source.source_type}"
                )


class TestEveryProducerChannelDeclared:
    """REQ-PIPE-03: Every producer_channel resolves to a declared ModuleOutput."""

    @pytest.mark.req("REQ-PIPE-03")
    def test_every_producer_channel_declared(self, pipeline_graph):
        """Every module_output input's producer_channel exists as a declared output."""
        declared_channels: set[str] = set()
        for m in pipeline_graph.modules:
            for out in m.outputs:
                declared_channels.add(out.channel_name)

        for m in pipeline_graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output":
                    channel = inp.source.producer_channel
                    assert channel and channel in declared_channels, (
                        f"Module {m.name} input {inp.param_name} references "
                        f"undeclared channel: {channel}"
                    )


class TestValidTopologicalSort:
    """REQ-PIPE-04: execution_order is a valid topological sort."""

    @pytest.mark.req("REQ-PIPE-04")
    def test_valid_topological_sort(self, pipeline_graph):
        """No module reads from a module with a higher execution_order."""
        name_to_order = {m.name: m.execution_order for m in pipeline_graph.modules}

        channel_to_module: dict[str, str] = {}
        for m in pipeline_graph.modules:
            for out in m.outputs:
                channel_to_module[out.channel_name] = m.name

        for m in pipeline_graph.modules:
            for inp in m.inputs:
                if inp.source.source_type == "module_output" and inp.source.producer_channel:
                    producer = channel_to_module.get(inp.source.producer_channel)
                    if producer and producer != m.name:
                        assert name_to_order[producer] < name_to_order[m.name], (
                            f"Module {m.name} (order={name_to_order[m.name]}) reads from "
                            f"{producer} (order={name_to_order[producer]})"
                        )


class TestEveryEntryPointClassified:
    """REQ-PIPE-05: Every entry point has an EntryPointType."""

    @pytest.mark.req("REQ-PIPE-05")
    def test_every_entry_point_classified(self, pipeline_graph):
        """Every EP in entry_point_groups has entry_type in EntryPointType."""
        for group in pipeline_graph.entry_point_groups:
            for param in group.parameters:
                assert param.entry_type is not None, (
                    f"EP {param.qualified_name} in group {group.name} has None entry_type"
                )
                assert param.entry_type in EntryPointType, (
                    f"EP {param.qualified_name} has invalid entry_type: {param.entry_type}"
                )


class TestAllThreeModuleTypes:
    """REQ-PIPE-06: Graph includes all 3 module types for appropriate models."""

    @pytest.mark.req("REQ-PIPE-06")
    def test_all_three_module_types_solar_battery(self, solar_battery_graph):
        """solar_battery graph has CalcUsage, FORMULA, and Aggregation modules."""
        has_calc_usage = any(
            m.module_kind == ModuleKind.CALCULATION
            for m in solar_battery_graph.modules
        )
        has_formula = any(
            m.module_kind == ModuleKind.FORMULA for m in solar_battery_graph.modules
        )
        has_aggregation = any(
            m.module_kind == ModuleKind.AGGREGATION for m in solar_battery_graph.modules
        )

        assert has_calc_usage, "No CalcUsage modules in solar_battery graph"
        assert has_formula, "No FORMULA modules in solar_battery graph"
        assert has_aggregation, "No Aggregation modules in solar_battery graph"


# ===========================================================================
# Generation Boundary (REQ-PIPE-07)
# ===========================================================================
class TestGenerationBoundary:
    """REQ-PIPE-07: ComputationGraph is the generation boundary."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_computation_graph_has_all_generation_fields(self):
        """ComputationGraph has modules, entry_point_groups, execution_order."""
        fields = set(ComputationGraph.model_fields.keys())
        assert "modules" in fields, "ComputationGraph missing 'modules' field"
        assert "entry_point_groups" in fields, "ComputationGraph missing 'entry_point_groups' field"
        assert "execution_order" in fields, "ComputationGraph missing 'execution_order' field"

    @pytest.mark.req("REQ-PIPE-07")
    def test_generation_extraction_import_count(self):
        """REQ-PIPE-07: Zero generation/ files import from extraction/ or analysis/.

        Phase 7.6 achieved the zero-violation target. This test guards against regression.
        """
        gen_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "generation"
        assert gen_dir.exists(), f"generation/ directory not found at {gen_dir}"

        violating_files: list[str] = []
        for py_file in sorted(gen_dir.glob("*.py")):
            content = py_file.read_text()
            for line in content.splitlines():
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                if (
                    "from sysml_codegen.extraction" in stripped
                    or "from sysml_codegen.analysis" in stripped
                    or "import sysml_codegen.extraction" in stripped
                    or "import sysml_codegen.analysis" in stripped
                ):
                    violating_files.append(py_file.name)
                    break

        assert len(violating_files) == 0, (
            f"generation/ files importing from extraction/analysis: {violating_files}. "
            "REQ-PIPE-07 requires zero extraction/analysis imports in generation/."
        )
