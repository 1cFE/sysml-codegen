"""Conformance tests for CalcUsage Module Factory (C14).

Requirements: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08
Design intent: 05-module-factory.md (Section 2)

Tests verify _build_pipeline_module() behavior with real extraction data:
- Pure data transformer (no mutation of inputs)
- Fail-fast on missing binding_resolutions or entry_points
- Every ModuleInput has exactly one InputSource (module_output or entry_point)
- Single-output field_name="root", multi-output uses attribute names
- Module name, type, input/output counts all derived from real calc defs

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.core.qualified_names import get_channel_name, get_module_name
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import _build_pipeline_module, _classify_entry_points
from sysml_codegen.resolution.models import (
    EntryPoint,
    PipelineModule,
)
from tests.helpers.snapshot_loader import load_extraction_snapshot


# ---------------------------------------------------------------------------
# Helper: build factory inputs from snapshot
# ---------------------------------------------------------------------------
def build_factory_inputs_from_snapshot(
    model_name: str,
) -> tuple[BacktrackingResult, dict[str, EntryPoint], dict, dict]:
    """Build all inputs needed to call _build_pipeline_module() from a snapshot.

    Replicates Steps 1 + 3.5–6 + 4 of build_computation_graph():
    1. Load extraction snapshot
    2. Build OutputRegistry via build_output_registry()
    3. Run DependencyBacktracker to get BacktrackingResult
    4. Build calc_def_map
    5. Build ParameterGroupDeriver
    6. Classify entry points via _classify_entry_points()

    Returns:
        (BacktrackingResult, entry_points, calc_def_map, snapshot_dict)
    """
    snap = load_extraction_snapshot(model_name)

    # Build registry (Steps 3.5 of build_pipeline_context)
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )

    # Run backtracker (Step 6)
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)

    # Build calc_def_map (Step 1 of build_computation_graph)
    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    # Build ParameterGroupDeriver (needed for _classify_entry_points)
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
    group_deriver = ParameterGroupDeriver(
        design_attrs, snap["calc_usages"], snap["calc_defs"]
    )

    # Classify entry points (Step 4 of build_computation_graph)
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    return result, entry_points, calc_def_map, snap


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive — build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_factory():
    """Factory inputs for solar_battery_model."""
    return build_factory_inputs_from_snapshot("solar_battery_model")


@pytest.fixture(scope="session")
def catf_mfe_factory():
    """Factory inputs for catf_mfe_model."""
    return build_factory_inputs_from_snapshot("catf_mfe_model")


@pytest.fixture(scope="session")
def chain_spike_factory():
    """Factory inputs for chain_spike_model."""
    return build_factory_inputs_from_snapshot("chain_spike_model")


@pytest.fixture(scope="session", params=[
    "solar_battery_model",
    "catf_mfe_model",
    "chain_spike_model",
])
def factory_inputs(request):
    """Parametrized factory inputs across all 3 models."""
    return build_factory_inputs_from_snapshot(request.param)


def _build_all_modules(
    result: BacktrackingResult,
    entry_points: dict[str, EntryPoint],
    calc_def_map: dict,
) -> list[tuple[PipelineModule, object, object]]:
    """Build all modules from a BacktrackingResult.

    Returns list of (module, usage, calc_def) tuples for verification.
    """
    modules = []
    for idx, usage in enumerate(result.required_usages):
        calc_def = calc_def_map.get(usage.calc_def_name)
        if not calc_def:
            continue
        module = _build_pipeline_module(
            usage=usage,
            calc_def=calc_def,
            entry_points=entry_points,
            execution_order=idx,
            binding_resolutions=result.binding_resolutions,
        )
        modules.append((module, usage, calc_def))
    return modules


# ===========================================================================
# REQ-MF-01: Pure data transformer — no mutation, correct return type
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestPureDataTransformer:
    """Verify _build_pipeline_module is a pure data transformer."""

    def test_no_mutation_of_entry_points(self, factory_inputs):
        """entry_points dict must not be mutated by factory call."""
        result, entry_points, calc_def_map, snap = factory_inputs
        ep_before = copy.deepcopy(entry_points)

        _build_all_modules(result, entry_points, calc_def_map)

        # Compare keys
        assert set(entry_points.keys()) == set(ep_before.keys())
        # Compare values via model_dump
        for k in entry_points:
            assert entry_points[k].model_dump() == ep_before[k].model_dump()

    def test_no_mutation_of_binding_resolutions(self, factory_inputs):
        """binding_resolutions dict must not be mutated by factory call."""
        result, entry_points, calc_def_map, snap = factory_inputs
        br_before = {
            k: v.model_dump() for k, v in result.binding_resolutions.items()
        }

        _build_all_modules(result, entry_points, calc_def_map)

        for k in result.binding_resolutions:
            assert result.binding_resolutions[k].model_dump() == br_before[k]

    def test_returns_pipeline_module(self, factory_inputs):
        """Return type is PipelineModule with non-empty fields."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)
        assert len(modules) > 0, "Expected at least one module"

        for module, usage, calc_def in modules:
            assert isinstance(module, PipelineModule)
            assert module.name, f"Module name must be non-empty for {usage.instance_name}"
            assert module.module_type, f"Module type must be non-empty for {usage.instance_name}"
            assert len(module.outputs) > 0, f"Module must have outputs for {usage.instance_name}"

    def test_module_name_matches_eqn(self, factory_inputs):
        """module.name == get_module_name(usage.qualified_name) for every module."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            expected = get_module_name(usage.qualified_name)
            assert module.name == expected, (
                f"Module name mismatch for {usage.instance_name}: "
                f"{module.name!r} != {expected!r}"
            )

    def test_module_type_derives_from_calc_def(self, factory_inputs):
        """module.module_type == derive_module_type(calc_def.qualified_name)."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            expected = derive_module_type(calc_def.qualified_name)
            assert module.module_type == expected, (
                f"Module type mismatch for {usage.instance_name}: "
                f"{module.module_type!r} != {expected!r}"
            )

    def test_execution_order_assigned(self, factory_inputs):
        """execution_order parameter is passed through to module."""
        result, entry_points, calc_def_map, snap = factory_inputs

        for idx, usage in enumerate(result.required_usages):
            calc_def = calc_def_map.get(usage.calc_def_name)
            if not calc_def:
                continue
            module = _build_pipeline_module(
                usage=usage,
                calc_def=calc_def,
                entry_points=entry_points,
                execution_order=idx,
                binding_resolutions=result.binding_resolutions,
            )
            assert module.execution_order == idx

    def test_default_flags(self, factory_inputs):
        """CalcUsage modules: is_computed_attribute=False, is_aggregation=False, compilability=UNKNOWN."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            assert module.is_computed_attribute is False, (
                f"CalcUsage module {module.name} should not be computed_attribute"
            )
            assert module.is_aggregation is False, (
                f"CalcUsage module {module.name} should not be aggregation"
            )
            assert module.compilability == Compilability.UNKNOWN, (
                f"CalcUsage module {module.name} compilability should be UNKNOWN, "
                f"got {module.compilability}"
            )


# ===========================================================================
# REQ-MF-02: Fail-fast on missing binding_resolutions or entry_points
# ===========================================================================


@pytest.mark.req("REQ-MF-02")
class TestFailFast:
    """Verify fail-fast behavior on missing data."""

    def test_missing_binding_resolution(self, solar_battery_factory):
        """ValueError with 'ADR-003 VIOLATION' when binding_resolution is missing."""
        result, entry_points, calc_def_map, snap = solar_battery_factory

        # Find a usage with at least one binding resolution
        usage = result.required_usages[0]
        calc_def = calc_def_map[usage.calc_def_name]

        # Create binding_resolutions missing the first input's key
        first_input = calc_def.input_attributes[0]
        missing_key = f"{usage.qualified_name}|{first_input.name}"

        incomplete_resolutions = {
            k: v for k, v in result.binding_resolutions.items()
            if k != missing_key
        }

        with pytest.raises(ValueError, match="ADR-003 VIOLATION"):
            _build_pipeline_module(
                usage=usage,
                calc_def=calc_def,
                entry_points=entry_points,
                execution_order=0,
                binding_resolutions=incomplete_resolutions,
            )

    def test_missing_entry_point(self, solar_battery_factory):
        """ValueError with 'ADR-003 VIOLATION' when entry_point is missing."""
        result, entry_points, calc_def_map, snap = solar_battery_factory

        # Find a usage that has at least one ENTRY_POINT resolution
        ep_usage = None
        ep_calc_def = None
        for usage in result.required_usages:
            calc_def = calc_def_map.get(usage.calc_def_name)
            if not calc_def:
                continue
            for input_attr in calc_def.input_attributes:
                key = f"{usage.qualified_name}|{input_attr.name}"
                res = result.binding_resolutions.get(key)
                if res and res.resolution_type == BindingResolutionType.ENTRY_POINT:
                    ep_usage = usage
                    ep_calc_def = calc_def
                    break
            if ep_usage:
                break

        if not ep_usage:
            pytest.skip("No ENTRY_POINT resolutions found in solar_battery")

        # Remove the entry point that this resolution refers to
        ep_key = None
        for input_attr in ep_calc_def.input_attributes:
            key = f"{ep_usage.qualified_name}|{input_attr.name}"
            res = result.binding_resolutions.get(key)
            if res and res.resolution_type == BindingResolutionType.ENTRY_POINT:
                ep_key = res.qualified_name
                break

        incomplete_eps = {k: v for k, v in entry_points.items() if k != ep_key}

        with pytest.raises(ValueError, match="ADR-003 VIOLATION"):
            _build_pipeline_module(
                usage=ep_usage,
                calc_def=ep_calc_def,
                entry_points=incomplete_eps,
                execution_order=0,
                binding_resolutions=result.binding_resolutions,
            )

    def test_wiring_covers_all_bindings(self, factory_inputs):
        """Every input_attribute in the calc_def has a corresponding ModuleInput."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            expected_params = {attr.name for attr in calc_def.input_attributes}
            actual_params = {inp.param_name for inp in module.inputs}
            assert actual_params == expected_params, (
                f"Module {module.name}: input params mismatch. "
                f"Missing: {expected_params - actual_params}, "
                f"Extra: {actual_params - expected_params}"
            )


# ===========================================================================
# REQ-MF-05: Every ModuleInput has exactly one InputSource
# ===========================================================================


@pytest.mark.req("REQ-MF-05")
class TestInputWiring:
    """Verify every input has exactly one source of the correct type."""

    def test_every_input_has_exactly_one_source(self, factory_inputs):
        """Every ModuleInput.source.source_type in {'module_output', 'entry_point'}."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            for inp in module.inputs:
                assert inp.source.source_type in {"module_output", "entry_point"}, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"unexpected source_type {inp.source.source_type!r}"
                )

    def test_module_output_wiring(self, factory_inputs):
        """MODULE_OUTPUT bindings wire to correct producer_channel."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            for inp in module.inputs:
                if inp.source.source_type != "module_output":
                    continue
                # Find the binding resolution for this input
                key = f"{usage.qualified_name}|{inp.param_name}"
                res = result.binding_resolutions[key]
                assert res.resolution_type == BindingResolutionType.MODULE_OUTPUT
                assert inp.source.producer_channel == res.qualified_name, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"producer_channel {inp.source.producer_channel!r} != "
                    f"resolution qn {res.qualified_name!r}"
                )

    def test_entry_point_wiring(self, factory_inputs):
        """ENTRY_POINT bindings wire to correct entry point with param_group."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        found_ep = False
        for module, usage, calc_def in modules:
            for inp in module.inputs:
                if inp.source.source_type != "entry_point":
                    continue
                found_ep = True
                # Find the binding resolution for this input
                key = f"{usage.qualified_name}|{inp.param_name}"
                res = result.binding_resolutions[key]
                assert res.resolution_type == BindingResolutionType.ENTRY_POINT

                # Verify qualified_name matches
                assert inp.source.qualified_name == res.qualified_name, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"EP qn {inp.source.qualified_name!r} != "
                    f"resolution qn {res.qualified_name!r}"
                )

                # Verify param_group matches entry_points dict
                ep = entry_points[res.qualified_name]
                assert inp.source.param_group == ep.param_group, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"param_group {inp.source.param_group!r} != "
                    f"EP param_group {ep.param_group!r}"
                )

        # At least one entry point should exist across models
        # (solar_battery and catf_mfe definitely have them)
        if not found_ep:
            pytest.skip("No ENTRY_POINT inputs found in this model")

    def test_input_count_matches_calc_def(self, factory_inputs):
        """len(module.inputs) == len(calc_def.input_attributes) for every module."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            assert len(module.inputs) == len(calc_def.input_attributes), (
                f"Module {module.name}: input count {len(module.inputs)} != "
                f"calc_def input_attributes count {len(calc_def.input_attributes)}"
            )


# ===========================================================================
# REQ-MF-08: Output field naming and channel naming
# ===========================================================================


@pytest.mark.req("REQ-MF-08")
class TestOutputNaming:
    """Verify output field_name and channel_name conventions."""

    def test_single_output_field_name_root(self, factory_inputs):
        """For calc defs with exactly 1 output: field_name == 'root'."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        found_single = False
        for module, usage, calc_def in modules:
            if len(calc_def.output_attributes) == 1:
                found_single = True
                assert module.outputs[0].field_name == "root", (
                    f"Module {module.name}: single-output field_name should be 'root', "
                    f"got {module.outputs[0].field_name!r}"
                )

        assert found_single, "Expected at least one single-output calc def"

    def test_multi_output_field_names_match_attrs(self, solar_battery_factory):
        """For calc defs with >1 output: each field_name == attr.name.

        If no natural multi-output fixture exists, constructs minimal test data.
        """
        result, entry_points, calc_def_map, snap = solar_battery_factory
        modules = _build_all_modules(result, entry_points, calc_def_map)

        # First check if any natural multi-output exists
        for module, usage, calc_def in modules:
            if len(calc_def.output_attributes) > 1:
                # Verify natural multi-output
                for i, output_attr in enumerate(calc_def.output_attributes):
                    assert module.outputs[i].field_name == output_attr.name, (
                        f"Module {module.name}: multi-output field_name "
                        f"{module.outputs[i].field_name!r} != attr name {output_attr.name!r}"
                    )
                return  # Found and verified a natural case

        # No natural multi-output — construct test with real usage data.
        # Use the first usage and modify its calc_def to have 2 outputs.
        usage = result.required_usages[0]
        calc_def = calc_def_map[usage.calc_def_name]

        # Import the AttributeInfo class from the actual output_attribute
        if not calc_def.output_attributes:
            pytest.skip("No output attributes to construct multi-output test")

        # Create a modified calc_def with 2 output attributes
        # Use copy of existing output attrs to construct a second one
        from dataclasses import replace
        original_attr = calc_def.output_attributes[0]
        second_attr = replace(original_attr, name="secondary_output")
        modified_calc_def = replace(
            calc_def,
            output_attributes=[original_attr, second_attr],
        )

        module = _build_pipeline_module(
            usage=usage,
            calc_def=modified_calc_def,
            entry_points=entry_points,
            execution_order=0,
            binding_resolutions=result.binding_resolutions,
        )

        assert len(module.outputs) == 2
        assert module.outputs[0].field_name == original_attr.name
        assert module.outputs[1].field_name == "secondary_output"

    def test_channel_name_is_pqn(self, factory_inputs):
        """Every output channel_name == get_channel_name(usage.qn, attr.name)."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            for i, output_attr in enumerate(calc_def.output_attributes):
                expected = get_channel_name(usage.qualified_name, output_attr.name)
                assert module.outputs[i].channel_name == expected, (
                    f"Module {module.name}, output {output_attr.name}: "
                    f"channel_name {module.outputs[i].channel_name!r} != "
                    f"expected {expected!r}"
                )

    def test_output_count_matches_calc_def(self, factory_inputs):
        """len(module.outputs) == len(calc_def.output_attributes) for every module."""
        result, entry_points, calc_def_map, snap = factory_inputs
        modules = _build_all_modules(result, entry_points, calc_def_map)

        for module, usage, calc_def in modules:
            assert len(module.outputs) == len(calc_def.output_attributes), (
                f"Module {module.name}: output count {len(module.outputs)} != "
                f"calc_def output_attributes count {len(calc_def.output_attributes)}"
            )
