"""Conformance tests for FORMULA Module Factory (C15).

Requirements: REQ-MF-01, REQ-MF-03, REQ-MF-05
Design intent: 05-module-factory.md (Section 3), 16-computed-attributes.md

Tests verify _build_computed_attr_module() behavior with real extraction data:
- Returns PipelineModule with correct naming and flags
- is_computed_attribute=True, FULLY_COMPILABLE for all FORMULA modules
- Inputs parsed from compiled_expression, wired via attribute resolution map
- FORMULA/EXPOSE_ALIAS inputs -> module_output, LITERAL inputs -> entry_point
- Single output with field_name="root" and PQN channel name
- Factory-created entry points typed DESIGN_ATTRIBUTE

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
from sysml_codegen.core.identifier_types import derive_module_type
from sysml_codegen.core.qualified_names import (
    get_channel_name,
    get_module_name,
    sysml_to_python_qualified_name,
)
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import (
    AttributeResolution,
    AttributeResolutionKind,
    _build_attribute_resolution_map,
    _build_computed_attr_module,
    _classify_entry_points,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    EntryPointType,
    PipelineModule,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Helper: build factory inputs from snapshot (extends C14 pattern)
# ---------------------------------------------------------------------------
def build_formula_factory_inputs_from_snapshot(
    model_name: str,
) -> tuple[
    list[ComputedAttributeData],
    dict[str, dict[str, AttributeResolution]],
    dict[str, EntryPoint],
    dict[Path, list],
    ParameterGroupDeriver,
    dict,
]:
    """Build all inputs needed to call _build_computed_attr_module() from a snapshot.

    Extends the C14 pattern with FORMULA-specific data:
    1. Load extraction snapshot
    2. Build OutputRegistry via build_output_registry()
    3. Run DependencyBacktracker to get BacktrackingResult
    4. Build calc_def_map, ParameterGroupDeriver, design_attrs
    5. Classify entry points via _classify_entry_points()
    6. Build calc_usage_names from result.required_usages
    7. Build attr_resolution_map via _build_attribute_resolution_map()
    8. Filter computed_attributes to FORMULA + FULLY_COMPILABLE only

    Returns:
        (formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap)
    """
    snap = load_extraction_snapshot(snapshot_fixture(model_name))
    snap["_model_name"] = model_name

    # Build registry
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )

    # Run backtracker
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)

    # Build calc_def_map
    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    # Build design_attrs with Path keys
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}

    # Build ParameterGroupDeriver
    group_deriver = ParameterGroupDeriver(
        design_attrs, snap["calc_usages"], snap["calc_defs"]
    )

    # Classify entry points (replicates build_computation_graph Step 4)
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    # Build calc_usage_names (Step 3 of build_computation_graph)
    calc_usage_names = {u.instance_name for u in result.required_usages}

    # Build attribute resolution map (Step 3 of build_computation_graph)
    resolution_map = _build_attribute_resolution_map(
        snap["computed_attributes"], design_attrs, registry, calc_usage_names
    )

    # Filter to FORMULA + FULLY_COMPILABLE only
    formula_cas = [
        ca
        for ca in snap["computed_attributes"]
        if ca.classification == ComputedAttributeClassification.FORMULA
        and ca.compilability == Compilability.FULLY_COMPILABLE
    ]

    return formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap


def _build_all_formula_modules(
    formula_cas: list[ComputedAttributeData],
    resolution_map: dict[str, dict[str, AttributeResolution]],
    entry_points: dict[str, EntryPoint],
    design_attrs: dict[Path, list],
    group_deriver: ParameterGroupDeriver,
) -> list[tuple[PipelineModule, ComputedAttributeData]]:
    """Build all FORMULA modules and return (module, ca) pairs.

    Merges returned entry points into entry_points dict after each call.
    """
    results = []
    for ca in formula_cas:
        module, new_eps = _build_computed_attr_module(
            ca, resolution_map, entry_points, design_attrs, group_deriver
        )
        entry_points.update(new_eps)
        results.append((module, ca))
    return results


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def attr_expr_probe_formula():
    """Factory inputs for attr_expr_probe."""
    return build_formula_factory_inputs_from_snapshot("attr_expr_probe")


@pytest.fixture(scope="session")
def solar_battery_formula():
    """Factory inputs for solar_battery_model."""
    return build_formula_factory_inputs_from_snapshot("solar_battery_model")


@pytest.fixture(
    scope="session",
    params=["attr_expr_probe", "solar_battery_model"],
    ids=["attr_expr_probe", "solar_battery_model"],
)
def formula_inputs(request):
    """Parametrized factory inputs across both models."""
    return build_formula_factory_inputs_from_snapshot(request.param)


# ===========================================================================
# REQ-MF-01: PipelineModule construction -- return type, naming, execution_order
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestPipelineModuleConstruction:
    """Verify _build_computed_attr_module produces correct PipelineModule."""

    def test_returns_pipeline_module(self, formula_inputs):
        """Return type is PipelineModule with non-empty name, module_type, outputs."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )
        assert len(modules) > 0, "Expected at least one FORMULA module"

        for module, ca in modules:
            assert isinstance(module, PipelineModule)
            assert module.name, f"Module name must be non-empty for {ca.name}"
            assert module.module_type, f"Module type must be non-empty for {ca.name}"
            assert len(module.outputs) > 0, f"Module must have outputs for {ca.name}"

    def test_module_name_from_ca_qn(self, formula_inputs):
        """module.name == get_module_name(sysml_to_python_qualified_name(sysml_qn))."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            module_eqn = sysml_to_python_qualified_name(sysml_qn)
            expected = get_module_name(module_eqn)
            assert module.name == expected, (
                f"Module name mismatch for {ca.name}: "
                f"{module.name!r} != {expected!r}"
            )

    def test_module_type_from_ca_qn(self, formula_inputs):
        """module.module_type == derive_module_type(sysml_qn)."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            expected = derive_module_type(sysml_qn)
            assert module.module_type == expected, (
                f"Module type mismatch for {ca.name}: "
                f"{module.module_type!r} != {expected!r}"
            )

    def test_entry_point_creation(self, formula_inputs):
        """Factory adds new entry points for LITERAL inputs with correct ep_qname format."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )

        # Snapshot EP keys before building any FORMULA modules
        # We need fresh entry_points to track creation, so rebuild
        fresh = build_formula_factory_inputs_from_snapshot(snap["_model_name"])
        f_cas, f_map, f_eps, f_das, f_gd, _ = fresh

        eps_before = set(f_eps.keys())

        _build_all_formula_modules(f_cas, f_map, f_eps, f_das, f_gd)

        eps_after = set(f_eps.keys())
        new_eps = eps_after - eps_before

        # There should be new entry points (at least for LITERAL inputs)
        # For attr_expr_probe: rate, markup, height, r_inner, r_outer, r_major,
        # eta_thermal, eta_direct, m_neutron, f_pump, eta_pump, f_subsystem, etc.
        assert len(new_eps) > 0, "Expected FORMULA factory to create new entry points"

        # Every new EP qname should be in {part_eqn}__{input_name} format
        for ep_key in new_eps:
            assert "__" in ep_key, (
                f"New entry point {ep_key!r} should contain '__' separator"
            )

    def test_entry_points_returned_by_factory(self, formula_inputs):
        """FORMULA factory returns new entry points via tuple (REQ-MF-01 pure interface).

        Post-refactor: _build_computed_attr_module() returns (PipelineModule, dict)
        and does NOT mutate the shared entry_points dict. New EPs are returned in
        the dict and the caller merges them.
        """
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )

        # Build fresh to isolate tracking
        fresh = build_formula_factory_inputs_from_snapshot(snap["_model_name"])
        f_cas, f_map, f_eps, f_das, f_gd, _ = fresh

        ep_before = copy.deepcopy(f_eps)

        # _build_all_formula_modules merges returned EPs into f_eps
        _build_all_formula_modules(f_cas, f_map, f_eps, f_das, f_gd)

        # After merging returned EPs, entry_points dict should have grown
        new_keys = set(f_eps.keys()) - set(ep_before.keys())
        assert len(new_keys) > 0, (
            "Expected new entry points returned by FORMULA factory"
        )

        # Existing keys must not have been modified
        for k in ep_before:
            assert f_eps[k].model_dump() == ep_before[k].model_dump(), (
                f"Existing entry point {k!r} was modified by FORMULA factory"
            )

    def test_execution_order_zero(self, formula_inputs):
        """execution_order == 0 for all FORMULA modules (reassigned during unified toposort)."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            assert module.execution_order == 0, (
                f"FORMULA module {module.name} should have execution_order=0, "
                f"got {module.execution_order}"
            )


# ===========================================================================
# REQ-MF-03: FORMULA-specific flags
# ===========================================================================


@pytest.mark.req("REQ-MF-03")
class TestFormulaFlags:
    """Verify FORMULA-specific flags on produced modules."""

    def test_is_computed_attribute_true(self, formula_inputs):
        """is_computed_attribute == True for every FORMULA module."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            assert module.is_computed_attribute is True, (
                f"FORMULA module {module.name} should have is_computed_attribute=True"
            )

    def test_compilability_fully_compilable(self, formula_inputs):
        """compilability == FULLY_COMPILABLE for every FORMULA module."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            assert module.compilability == Compilability.FULLY_COMPILABLE, (
                f"FORMULA module {module.name} compilability should be FULLY_COMPILABLE, "
                f"got {module.compilability}"
            )

    def test_is_aggregation_false(self, formula_inputs):
        """is_aggregation == False for every FORMULA module."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            assert module.is_aggregation is False, (
                f"FORMULA module {module.name} should have is_aggregation=False"
            )

    def test_raises_on_missing_compiled_expression(self, attr_expr_probe_formula):
        """ValueError raised when ca.compiled_expression is None."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            attr_expr_probe_formula
        )

        # Use a real CA but set compiled_expression to None
        ca = formula_cas[0]
        # ComputedAttributeData is a dataclass, use dataclasses.replace
        from dataclasses import replace

        bad_ca = replace(ca, compiled_expression=None)

        with pytest.raises(ValueError, match="no compiled_expression"):
            _build_computed_attr_module(
                bad_ca, resolution_map, entry_points, design_attrs, group_deriver
            )


# ===========================================================================
# REQ-MF-05: Input wiring -- source types, resolution map fidelity
# ===========================================================================


@pytest.mark.req("REQ-MF-05")
class TestInputWiring:
    """Verify input wiring via attribute resolution map."""

    def test_every_input_has_one_source(self, formula_inputs):
        """Each input.source.source_type in {"module_output", "entry_point"}."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            for inp in module.inputs:
                assert inp.source.source_type in {"module_output", "entry_point"}, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"unexpected source_type {inp.source.source_type!r}"
                )

    def test_input_names_match_compiled_expression(self, formula_inputs):
        """Input param_name set matches inputs.(\\w+) regex from ca.compiled_expression."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            # Extract unique input names preserving order from compiled_expression
            raw_inputs = re.findall(r"inputs\.(\w+)", ca.compiled_expression)
            seen: set[str] = set()
            expected_names: list[str] = []
            for name in raw_inputs:
                if name not in seen:
                    seen.add(name)
                    expected_names.append(name)

            actual_names = [inp.param_name for inp in module.inputs]
            assert actual_names == expected_names, (
                f"Module {module.name}: input names {actual_names} != "
                f"expected from expression {expected_names}"
            )

    def test_formula_inputs_wire_to_module_output(self, formula_inputs):
        """FORMULA/EXPOSE_ALIAS inputs wire to module_output with correct producer_channel."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        found_module_output = False
        for module, ca in modules:
            part_resolutions = resolution_map.get(ca.owning_part_name, {})

            for inp in module.inputs:
                attr_res = part_resolutions.get(inp.param_name)
                wirable = (
                    AttributeResolutionKind.FORMULA,
                    AttributeResolutionKind.EXPOSE_ALIAS,
                )
                if attr_res and attr_res.kind in wirable and attr_res.channel_name:
                    found_module_output = True
                    assert inp.source.source_type == "module_output", (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"resolution kind={attr_res.kind} should wire to module_output, "
                        f"got {inp.source.source_type!r}"
                    )
                    assert inp.source.producer_channel == attr_res.channel_name, (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"producer_channel {inp.source.producer_channel!r} != "
                        f"resolution channel {attr_res.channel_name!r}"
                    )

        # solar_battery has only 1 FORMULA (p_net_kw = p_net_mw * 1000.0) where
        # p_net_mw is LITERAL, so no module_output wiring. Skip gracefully.
        if not found_module_output:
            pytest.skip(
                "No FORMULA/EXPOSE_ALIAS inputs found -- "
                "model has only LITERAL-input FORMULA modules"
            )

    def test_literal_inputs_wire_to_entry_point(self, formula_inputs):
        """Inputs not in resolution map (or kind=LITERAL) wire to entry_point."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        found_entry_point = False
        for module, ca in modules:
            part_resolutions = resolution_map.get(ca.owning_part_name, {})
            part_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)

            for inp in module.inputs:
                attr_res = part_resolutions.get(inp.param_name)
                wirable = (
                    AttributeResolutionKind.FORMULA,
                    AttributeResolutionKind.EXPOSE_ALIAS,
                )
                is_wirable = (
                    attr_res
                    and attr_res.kind in wirable
                    and attr_res.channel_name
                )
                if not is_wirable:
                    found_entry_point = True
                    assert inp.source.source_type == "entry_point", (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"non-wirable input should be entry_point, "
                        f"got {inp.source.source_type!r}"
                    )
                    expected_qn = f"{part_eqn}__{inp.param_name}"
                    assert inp.source.qualified_name == expected_qn, (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"EP qualified_name {inp.source.qualified_name!r} != "
                        f"expected {expected_qn!r}"
                    )

        assert found_entry_point, (
            "Expected at least one LITERAL input wired to entry_point"
        )

    def test_formula_to_formula_wiring(self, attr_expr_probe_formula):
        """In attr_expr_probe: verify FORMULA-to-FORMULA chain wiring.

        - cost: inputs.area[FORMULA] + inputs.rate[LITERAL]
        - marked_up_cost: inputs.cost[FORMULA] + inputs.markup[LITERAL]
        - cost_density: inputs.cost[FORMULA] + inputs.volume[FORMULA]
        """
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            attr_expr_probe_formula
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        # Build name -> module lookup
        module_by_ca_name = {ca.name: (module, ca) for module, ca in modules}

        # Verify cost: area -> module_output, rate -> entry_point
        assert "cost" in module_by_ca_name, "cost FORMULA module not found"
        cost_mod, cost_ca = module_by_ca_name["cost"]
        cost_inputs = {inp.param_name: inp for inp in cost_mod.inputs}
        assert "area" in cost_inputs
        assert cost_inputs["area"].source.source_type == "module_output", (
            "cost.area should wire to module_output (area is FORMULA)"
        )
        assert "rate" in cost_inputs
        assert cost_inputs["rate"].source.source_type == "entry_point", (
            "cost.rate should wire to entry_point (rate is LITERAL)"
        )

        # Verify marked_up_cost: cost -> module_output, markup -> entry_point
        assert "marked_up_cost" in module_by_ca_name, "marked_up_cost FORMULA module not found"
        muc_mod, muc_ca = module_by_ca_name["marked_up_cost"]
        muc_inputs = {inp.param_name: inp for inp in muc_mod.inputs}
        assert "cost" in muc_inputs
        assert muc_inputs["cost"].source.source_type == "module_output", (
            "marked_up_cost.cost should wire to module_output (cost is FORMULA)"
        )
        assert "markup" in muc_inputs
        assert muc_inputs["markup"].source.source_type == "entry_point", (
            "marked_up_cost.markup should wire to entry_point (markup is LITERAL)"
        )

        # Verify cost_density: cost -> module_output, volume -> module_output
        assert "cost_density" in module_by_ca_name, "cost_density FORMULA module not found"
        cd_mod, cd_ca = module_by_ca_name["cost_density"]
        cd_inputs = {inp.param_name: inp for inp in cd_mod.inputs}
        assert "cost" in cd_inputs
        assert cd_inputs["cost"].source.source_type == "module_output", (
            "cost_density.cost should wire to module_output (cost is FORMULA)"
        )
        assert "volume" in cd_inputs
        assert cd_inputs["volume"].source.source_type == "module_output", (
            "cost_density.volume should wire to module_output (volume is FORMULA)"
        )

    def test_expose_alias_input_wiring(self, attr_expr_probe_formula):
        """If any FORMULA input resolves via EXPOSE_ALIAS, verify module_output wiring."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            attr_expr_probe_formula
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        found_alias = False
        for module, ca in modules:
            part_resolutions = resolution_map.get(ca.owning_part_name, {})

            for inp in module.inputs:
                attr_res = part_resolutions.get(inp.param_name)
                if attr_res and attr_res.kind == AttributeResolutionKind.EXPOSE_ALIAS:
                    found_alias = True
                    assert inp.source.source_type == "module_output", (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"EXPOSE_ALIAS should wire to module_output"
                    )
                    assert inp.source.producer_channel == attr_res.channel_name, (
                        f"Module {module.name}, input {inp.param_name}: "
                        f"producer_channel mismatch for EXPOSE_ALIAS"
                    )

        # EXPOSE_ALIAS may not exist in attr_expr_probe -- document but don't fail
        if not found_alias:
            pytest.skip("No EXPOSE_ALIAS inputs found in attr_expr_probe FORMULA modules")


# ===========================================================================
# REQ-MF-05: Output naming and entry point properties
# ===========================================================================


@pytest.mark.req("REQ-MF-05")
class TestOutputNaming:
    """Verify output naming and entry point properties."""

    def test_single_output_field_name_root(self, formula_inputs):
        """len(module.outputs) == 1 and outputs[0].field_name == "root"."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            assert len(module.outputs) == 1, (
                f"FORMULA module {module.name} should have exactly 1 output, "
                f"got {len(module.outputs)}"
            )
            assert module.outputs[0].field_name == "root", (
                f"FORMULA module {module.name} output field_name should be 'root', "
                f"got {module.outputs[0].field_name!r}"
            )

    def test_output_channel_name_pqn(self, formula_inputs):
        """output channel_name == get_channel_name(module_eqn, ca.python_name)."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )
        modules = _build_all_formula_modules(
            formula_cas, resolution_map, entry_points, design_attrs, group_deriver
        )

        for module, ca in modules:
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            module_eqn = sysml_to_python_qualified_name(sysml_qn)
            expected = get_channel_name(module_eqn, ca.python_name)
            assert module.outputs[0].channel_name == expected, (
                f"FORMULA module {module.name}: channel_name "
                f"{module.outputs[0].channel_name!r} != expected {expected!r}"
            )

    def test_factory_entry_points_design_attribute(self, formula_inputs):
        """Every entry point created by the factory has entry_type == DESIGN_ATTRIBUTE."""
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            formula_inputs
        )

        # Rebuild with fresh entry_points to track creation
        fresh = build_formula_factory_inputs_from_snapshot(snap["_model_name"])
        f_cas, f_map, f_eps, f_das, f_gd, _ = fresh

        eps_before = set(f_eps.keys())
        _build_all_formula_modules(f_cas, f_map, f_eps, f_das, f_gd)
        eps_after = set(f_eps.keys())

        new_eps = eps_after - eps_before
        for ep_key in new_eps:
            ep = f_eps[ep_key]
            assert ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE, (
                f"Factory-created EP {ep_key!r} should be DESIGN_ATTRIBUTE, "
                f"got {ep.entry_type!r}"
            )

    def test_default_value_from_design_attrs(self, solar_battery_formula):
        """Entry points for LITERAL inputs have default_value from design_attrs when available.

        solar_battery p_net_kw = p_net_mw * 1000.0 -- p_net_mw is a LITERAL input.
        Check if the factory populates default_value from design_attrs.
        """
        formula_cas, resolution_map, entry_points, design_attrs, group_deriver, snap = (
            solar_battery_formula
        )

        # Build fresh to track new EPs
        fresh = build_formula_factory_inputs_from_snapshot("solar_battery_model")
        f_cas, f_map, f_eps, f_das, f_gd, _ = fresh

        eps_before = set(f_eps.keys())
        _build_all_formula_modules(f_cas, f_map, f_eps, f_das, f_gd)
        eps_after = set(f_eps.keys())

        new_eps = eps_after - eps_before
        # Verify that new EPs that have design_attr matches got default_value populated
        # Build design_attr lookup for comparison
        design_attr_by_qname: dict[str, object] = {}
        for attrs in f_das.values():
            for attr in attrs:
                if attr.qualified_name:
                    design_attr_by_qname[attr.qualified_name] = attr

        for ep_key in new_eps:
            ep = f_eps[ep_key]
            da = design_attr_by_qname.get(ep_key)
            if da and da.default_value:
                try:
                    expected = float(da.default_value)
                    assert ep.default_value == expected, (
                        f"EP {ep_key}: default_value {ep.default_value} != "
                        f"design_attr default {expected}"
                    )
                except (ValueError, TypeError):
                    pass  # Non-numeric default, skip
