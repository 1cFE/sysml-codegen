"""Conformance tests for Aggregation Module Factory (C16).

Requirements: REQ-MF-01, REQ-MF-04, REQ-MF-05, REQ-MF-06, REQ-MF-07,
              REQ-LVP-01 through REQ-LVP-07
Design intent: 05-module-factory.md (Section 4), 18-literal-value-propagation.md

Tests verify _build_aggregation_module() behavior with real extraction data:
- Returns PipelineModule with correct name, type, outputs
- Creates expected entry points in the entry_points dict (mutation pattern)
- Handles all three term types: SumTerm, SingletonTerm, LocalTerm
- _find_literal_redefinition() strategy order (type-aware first)
- LocalTerm does NOT use literal redef fallback
- Default backfill replaces None with literal values
- FULLY_COMPILABLE vs MANUAL_REQUIRED compilability
- Single output with field_name="root"
- Compiled expression substitution

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import copy
from dataclasses import replace
from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
from sysml_codegen.core.qualified_names import (
    sanitize_name,
)
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import (
    _build_aggregation_module,
    _classify_entry_points,
    _find_literal_redefinition,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    EntryPointType,
    ModuleKind,
    PipelineModule,
)
from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

def _probe_ctx(registry):
    """These probes carry no design attributes; the shared table sees an empty tier 2."""
    from sysml_codegen.resolution.producer_resolution import ProducerContext

    return ProducerContext(output_registry=registry)




# ---------------------------------------------------------------------------
# Helper: build aggregation factory inputs from snapshot
# ---------------------------------------------------------------------------
def build_aggregation_factory_inputs(model_name: str) -> dict:
    """Build all inputs needed to call _build_aggregation_module() from a snapshot.

    Replicates the graph_builder pipeline steps:
    1. Load extraction snapshot
    2. Build OutputRegistry via build_output_registry()
    3. Run DependencyBacktracker (for entry_points dict baseline)
    4. Build calc_def_map, ParameterGroupDeriver, _classify_entry_points()
    5. Build expose_aliases map (Step 6.6b replication)
    6. Extract hierarchy_redefinitions, usage_type_map, aggregation_data

    Returns dict with all components.
    """
    snap = load_extraction_snapshot(snapshot_fixture(model_name))

    # Build registry
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )

    # Run backtracker for entry_points baseline
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)

    # Build calc_def_map
    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    # Build ParameterGroupDeriver
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
    group_deriver = ParameterGroupDeriver(
        design_attrs, snap["calc_usages"], snap["calc_defs"]
    )

    # Classify entry points
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    # Build expose_aliases (Step 6.6b replication)
    expose_aliases: dict[tuple[str, str], str] = {}
    for ca in snap["computed_attributes"]:
        if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
            segments = ca.owning_part_qualified_name.split("::")
            normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
            expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text

    # Extract hierarchy data
    hierarchy_data = snap["hierarchy_data"]
    redefinitions = hierarchy_data.redefinitions
    usage_type_map = hierarchy_data.usage_type_map
    aggregation_data = snap["aggregation_expressions"]

    return {
        "snap": snap,
        "registry": registry,
        "entry_points": entry_points,
        "group_deriver": group_deriver,
        "expose_aliases": expose_aliases,
        "redefinitions": redefinitions,
        "usage_type_map": usage_type_map,
        "aggregation_data": aggregation_data,
    }


def _build_all_agg_modules(
    inputs: dict,
) -> list[tuple[PipelineModule, ScopedAggregationData, dict[str, EntryPoint]]]:
    """Build all aggregation modules, merging returned entry points.

    Returns list of (module, agg, entry_points_snapshot_after) tuples.
    """
    results = []
    for agg in inputs["aggregation_data"]:
        module, new_eps = _build_aggregation_module(
            agg=agg,
            redefinitions=inputs["redefinitions"],
            output_registry=inputs["registry"],
            entry_points=inputs["entry_points"],
            group_deriver=inputs["group_deriver"],
            expose_aliases=inputs["expose_aliases"],
            usage_type_map=inputs["usage_type_map"],
            producer_ctx=_probe_ctx(inputs["registry"]),
        )
        inputs["entry_points"].update(new_eps)
        results.append((module, agg, inputs["entry_points"]))
    return results


def _select_agg(inputs: dict, instance_path: str, attribute_name: str) -> ScopedAggregationData:
    """Select one aggregation by (instance_path, attribute_name), not by list index.

    Index is a DFS-order artifact not stored in the snapshot -- a reorder must not move
    a pin. Fails loudly if the identified aggregation is absent from the fixture.
    """
    match = next(
        (a for a in inputs["aggregation_data"]
         if a.instance_path == instance_path
         and a.expression.attribute_name == attribute_name),
        None,
    )
    assert match is not None, (
        f"aggregation ({instance_path!r}, {attribute_name!r}) not in fixture "
        f"aggregation_data"
    )
    return match


def _build_one(inputs: dict, agg: ScopedAggregationData) -> PipelineModule:
    """Build a single aggregation module from a fresh copy of the entry points."""
    module, _new_eps = _build_aggregation_module(
        agg=agg,
        redefinitions=inputs["redefinitions"],
        output_registry=inputs["registry"],
        entry_points=copy.deepcopy(inputs["entry_points"]),
        group_deriver=inputs["group_deriver"],
        expose_aliases=inputs["expose_aliases"],
        usage_type_map=inputs["usage_type_map"],
        producer_ctx=_probe_ctx(inputs["registry"]),
    )
    return module


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_agg():
    """Aggregation factory inputs for solar_battery_model."""
    return build_aggregation_factory_inputs("solar_battery_model")


@pytest.fixture(scope="session")
def issue22_agg():
    """Aggregation factory inputs for issue22_model."""
    return build_aggregation_factory_inputs("issue22_model")


@pytest.fixture(scope="session", params=["solar_battery_model", "issue22_model"])
def agg_inputs(request):
    """Parametrized aggregation factory inputs."""
    return build_aggregation_factory_inputs(request.param)


# ===========================================================================
# REQ-MF-01: Returns PipelineModule with correct structure
# ===========================================================================


@pytest.mark.req("REQ-MF-01")
class TestReturnsPipelineModule:
    """Verify _build_aggregation_module returns correct PipelineModule."""

    def test_returns_pipeline_module(self, agg_inputs):
        """Return type is PipelineModule with non-empty name, module_type, outputs."""
        for agg in agg_inputs["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=agg_inputs["redefinitions"],
                output_registry=agg_inputs["registry"],
                entry_points=copy.deepcopy(agg_inputs["entry_points"]),
                group_deriver=agg_inputs["group_deriver"],
                expose_aliases=agg_inputs["expose_aliases"],
                usage_type_map=agg_inputs["usage_type_map"],
                producer_ctx=_probe_ctx(agg_inputs["registry"]),
            )
            assert isinstance(module, PipelineModule)
            assert module.name, f"Module name must be non-empty for {agg.module_eqn}"
            assert module.module_type, f"Module type must be non-empty for {agg.module_eqn}"
            assert len(module.outputs) > 0, f"Module must have outputs for {agg.module_eqn}"

    def test_module_name_format(self, solar_battery_agg):
        """Aggregation module name is the fully-lowercased EQN of the selected module.

        The former body computed ``expected = get_module_name(agg.module_eqn)`` -- the
        exact call production makes -- so it could never fail. Anchor to a literal on an
        aggregation selected by (instance_path, attribute_name), not by list index.
        """
        agg = _select_agg(
            solar_battery_agg,
            "SolarBatteryDesign__solar_battery_plant__solar_array",
            "capital_cost",
        )
        module = _build_one(solar_battery_agg, agg)
        # provenance: get_module_name lowercases the whole EQN (core/qualified_names.py);
        #   the design prefix "SolarBatteryDesign" is lowercased too -- only a literal
        #   catches the lowercasing.
        expected = "solarbatterydesign__solar_battery_plant__solar_array__capital_cost"
        assert module.name == expected, f"module.name mismatch: {module.name!r}"

    def test_creates_expected_entry_points(self, solar_battery_agg):
        """Factory returns new entry points via tuple (merged by caller)."""
        ep_before = copy.deepcopy(solar_battery_agg["entry_points"])
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        before_count = len(ep_working)

        for agg in solar_battery_agg["aggregation_data"]:
            _module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )
            ep_working.update(_new_eps)

        after_count = len(ep_working)
        assert after_count >= before_count, (
            f"Expected entry points to grow: before={before_count}, after={after_count}"
        )

        # Every newly added EP should have entry_type=DESIGN_ATTRIBUTE
        new_keys = set(ep_working.keys()) - set(ep_before.keys())
        for key in new_keys:
            ep = ep_working[key]
            assert ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE, (
                f"New EP {key} has entry_type={ep.entry_type!r}, "
                f"expected DESIGN_ATTRIBUTE"
            )


# ===========================================================================
# REQ-MF-04: Handles all three term types
# ===========================================================================


@pytest.mark.req("REQ-MF-04")
class TestTermTypeHandling:
    """Verify SumTerm, SingletonTerm, and LocalTerm handling."""

    def test_handles_all_three_term_types(self, solar_battery_agg):
        """Across all modules: at least one of each term type produces an input."""
        found_sum = False
        found_singleton = False
        found_local = False

        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )

            input_names = {inp.param_name for inp in module.inputs}

            # SumTerm inputs: param_name = f"{term.part_usage_name}_{term.attribute_name}"
            for term in agg.expression.sum_terms:
                expected_param = f"{term.part_usage_name}_{term.attribute_name}"
                if expected_param in input_names:
                    found_sum = True

            # SingletonTerm inputs: param_name = s_term.source_path.replace(".", "_")
            for s_term in agg.expression.singleton_terms:
                expected_param = s_term.source_path.replace(".", "_")
                if expected_param in input_names:
                    found_singleton = True

            # LocalTerm inputs: param_name = l_term.attribute_name
            for l_term in agg.expression.local_terms:
                if l_term.attribute_name in input_names:
                    found_local = True

        assert found_sum, "No SumTerm-derived input found across all solar_battery modules"
        assert found_singleton, (
            "No SingletonTerm-derived input found across all solar_battery modules"
        )
        assert found_local, "No LocalTerm-derived input found across all solar_battery modules"

    def test_sumterm_wiring(self, solar_battery_agg):
        """SumTerm with channel resolution success: source_type='module_output'."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_wired_sum = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )

            canonical = solar_battery_agg["registry"].canonical_channels
            for term in agg.expression.sum_terms:
                expected_param = f"{term.part_usage_name}_{term.attribute_name}"
                for inp in module.inputs:
                    if (inp.param_name == expected_param
                            and inp.source.source_type == "module_output"):
                        assert inp.source.producer_channel in canonical, (
                            f"SumTerm {expected_param}: producer_channel "
                            f"{inp.source.producer_channel!r} not in canonical_channels"
                        )
                        found_wired_sum = True

        assert found_wired_sum, "No SumTerm with successful channel resolution found"

    def test_sumterm_multiplicity_entry_point(self, solar_battery_agg):
        """SumTerms with multiplicity_attr produce a second ModuleInput for multiplicity."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_mult = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )
            ep_working.update(_new_eps)

            for term in agg.expression.sum_terms:
                if term.multiplicity_attr:
                    # Find the multiplicity input
                    mult_inputs = [
                        inp for inp in module.inputs
                        if inp.param_name == term.multiplicity_attr
                    ]
                    assert len(mult_inputs) == 1, (
                        f"Expected exactly 1 multiplicity input for {term.multiplicity_attr}, "
                        f"got {len(mult_inputs)}"
                    )
                    mult_inp = mult_inputs[0]
                    assert mult_inp.python_type == "float", (
                        f"Multiplicity input type should be 'float', got {mult_inp.python_type!r}"
                    )
                    assert mult_inp.source.source_type == "entry_point"
                    # Default value should be the multiplicity count
                    if term.multiplicity_count is not None:
                        ep = ep_working[mult_inp.source.qualified_name]
                        assert ep.default_value == float(term.multiplicity_count), (
                            f"Multiplicity EP default {ep.default_value} != "
                            f"count {float(term.multiplicity_count)}"
                        )
                    found_mult = True

        assert found_mult, "No SumTerm with multiplicity_attr found in solar_battery"

    def test_sumterm_no_multiplicity_attr(self, issue22_agg):
        """SumTerm with multiplicity_attr=None: no multiplicity input added."""
        ep_working = copy.deepcopy(issue22_agg["entry_points"])

        for agg in issue22_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=issue22_agg["redefinitions"],
                output_registry=issue22_agg["registry"],
                entry_points=ep_working,
                group_deriver=issue22_agg["group_deriver"],
                expose_aliases=issue22_agg["expose_aliases"],
                usage_type_map=issue22_agg["usage_type_map"],
                producer_ctx=_probe_ctx(issue22_agg["registry"]),
            )

            for term in agg.expression.sum_terms:
                if term.multiplicity_attr is None:
                    # Only the base attribute input should exist, no multiplicity
                    base_param = f"{term.part_usage_name}_{term.attribute_name}"
                    param_names = [inp.param_name for inp in module.inputs]
                    assert base_param in param_names, (
                        f"Base SumTerm input {base_param} not found"
                    )
                    # No multiplicity-named input should exist from this term
                    # (There's no multiplicity_attr to name it after)

    def test_singleton_term_wiring(self, solar_battery_agg):
        """SingletonTerm with channel resolution success: source_type='module_output'."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_wired_singleton = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )

            for s_term in agg.expression.singleton_terms:
                expected_param = s_term.source_path.replace(".", "_")
                for inp in module.inputs:
                    if (inp.param_name == expected_param
                            and inp.source.source_type == "module_output"):
                        found_wired_singleton = True

        assert found_wired_singleton, "No SingletonTerm with successful channel resolution found"

    def test_module_kind_equals_aggregation(self, agg_inputs):
        """module.module_kind == ModuleKind.AGGREGATION for all aggregation modules."""
        ep_working = copy.deepcopy(agg_inputs["entry_points"])
        for agg in agg_inputs["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=agg_inputs["redefinitions"],
                output_registry=agg_inputs["registry"],
                entry_points=ep_working,
                group_deriver=agg_inputs["group_deriver"],
                expose_aliases=agg_inputs["expose_aliases"],
                usage_type_map=agg_inputs["usage_type_map"],
                producer_ctx=_probe_ctx(agg_inputs["registry"]),
            )
            assert module.module_kind == ModuleKind.AGGREGATION, (
                f"Module {module.name} should have module_kind=ModuleKind.AGGREGATION"
            )

    def test_has_unsupported_nodes_forces_manual_required(self, solar_battery_agg):
        """If agg.expression.has_unsupported_nodes=True: compilability == MANUAL_REQUIRED."""
        # Use the first aggregation expression and modify it
        agg = solar_battery_agg["aggregation_data"][0]
        modified_expr = replace(agg.expression, has_unsupported_nodes=True)
        modified_agg = replace(agg, expression=modified_expr)

        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        module, _new_eps = _build_aggregation_module(
            agg=modified_agg,
            redefinitions=solar_battery_agg["redefinitions"],
            output_registry=solar_battery_agg["registry"],
            entry_points=ep_working,
            group_deriver=solar_battery_agg["group_deriver"],
            expose_aliases=solar_battery_agg["expose_aliases"],
            usage_type_map=solar_battery_agg["usage_type_map"],
            producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
        )
        assert module.compilability == Compilability.MANUAL_REQUIRED, (
            f"Module with unsupported nodes should be MANUAL_REQUIRED, "
            f"got {module.compilability}"
        )

    def test_compiled_expression_substitution(self, solar_battery_agg):
        """compiled_expression replaces symbolic refs with 'inputs.X' form."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_compiled = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )

            if (module.compilability == Compilability.FULLY_COMPILABLE
                    and module.compiled_expression):
                found_compiled = True
                # No raw symbolic refs should remain
                for term in agg.expression.sum_terms:
                    raw_ref = f"{term.part_usage_name}.{term.attribute_name}"
                    assert raw_ref not in module.compiled_expression, (
                        f"Raw symbolic ref {raw_ref!r} found in compiled expression "
                        f"{module.compiled_expression!r}"
                    )
                for s_term in agg.expression.singleton_terms:
                    assert s_term.source_path not in module.compiled_expression, (
                        f"Raw symbolic ref {s_term.source_path!r} found in compiled expression "
                        f"{module.compiled_expression!r}"
                    )
                # Should contain "inputs." references
                assert "inputs." in module.compiled_expression, (
                    f"Compiled expression should contain 'inputs.' references: "
                    f"{module.compiled_expression!r}"
                )

        assert found_compiled, "No FULLY_COMPILABLE module with compiled expression found"


# ===========================================================================
# REQ-MF-05: Every ModuleInput has exactly one InputSource
# ===========================================================================


@pytest.mark.req("REQ-MF-05")
class TestInputSourceWiring:
    """Verify every input has exactly one source of correct type."""

    def test_every_input_has_exactly_one_source(self, agg_inputs):
        """Every ModuleInput.source.source_type in {'module_output', 'entry_point'}."""
        ep_working = copy.deepcopy(agg_inputs["entry_points"])
        for agg in agg_inputs["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=agg_inputs["redefinitions"],
                output_registry=agg_inputs["registry"],
                entry_points=ep_working,
                group_deriver=agg_inputs["group_deriver"],
                expose_aliases=agg_inputs["expose_aliases"],
                usage_type_map=agg_inputs["usage_type_map"],
                producer_ctx=_probe_ctx(agg_inputs["registry"]),
            )

            for inp in module.inputs:
                assert inp.source.source_type in {"module_output", "entry_point"}, (
                    f"Module {module.name}, input {inp.param_name}: "
                    f"unexpected source_type {inp.source.source_type!r}"
                )

    def test_single_output_field_name_root(self, agg_inputs):
        """Every aggregation module has single output with field_name='root'."""
        ep_working = copy.deepcopy(agg_inputs["entry_points"])
        for agg in agg_inputs["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=agg_inputs["redefinitions"],
                output_registry=agg_inputs["registry"],
                entry_points=ep_working,
                group_deriver=agg_inputs["group_deriver"],
                expose_aliases=agg_inputs["expose_aliases"],
                usage_type_map=agg_inputs["usage_type_map"],
                producer_ctx=_probe_ctx(agg_inputs["registry"]),
            )
            assert len(module.outputs) == 1, (
                f"Aggregation module {module.name} should have exactly 1 output, "
                f"got {len(module.outputs)}"
            )
            assert module.outputs[0].field_name == "root", (
                f"Module {module.name}: output field_name should be 'root', "
                f"got {module.outputs[0].field_name!r}"
            )

    def test_output_channel_name_format(self, solar_battery_agg):
        """Aggregation output channel is the doubled ADR-003 PQN literal.

        The former body computed ``expected = get_channel_name(agg.module_eqn, attr)`` --
        production's exact call -- so it could never fail. Anchor to a literal on an
        aggregation selected by (instance_path, attribute_name), not by list index.
        """
        agg = _select_agg(
            solar_battery_agg,
            "SolarBatteryDesign__solar_battery_plant__solar_array",
            "capital_cost",
        )
        module = _build_one(solar_battery_agg, agg)
        # The trailing "capital_cost" is DOUBLED on purpose -- not a typo. Per ADR-003,
        # get_channel_name composes usage_qn + "__" + output_name
        # (core/qualified_names.py:98-100), and an aggregation module's EQN already ends
        # in the attribute name, so the PQN repeats it. Do NOT de-double.
        assert module.outputs[0].channel_name == (
            "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost"
        ), f"channel_name mismatch: {module.outputs[0].channel_name!r}"


# ===========================================================================
# REQ-MF-06: Literal redefinition fallback for SumTerm/SingletonTerm
# ===========================================================================


@pytest.mark.req("REQ-MF-06")
class TestLiteralFallback:
    """Verify LITERAL :>> redefinition as fallback for entry point defaults."""

    @pytest.mark.req("REQ-LVP-02")
    def test_sumterm_literal_fallback(self, solar_battery_agg):
        """SumTerm where channel fails but LITERAL redef exists: EP default matches literal.

        No natural SumTerm literal fallback exists in solar_battery (all SumTerm
        channels resolve successfully; literal redefs are on Permitting_Interconnect
        which is referenced as SingletonTerms). Construct a test using real data:
        replace a SumTerm's part_usage_name with 'permitting' so the channel lookup
        fails but _find_literal_redefinition finds the 0.0 value.
        """
        from sysml_codegen.extraction.data_models import SumTerm

        # Find an agg that belongs to Site_Infrastructure (which owns permitting)
        target_agg = None
        for agg in solar_battery_agg["aggregation_data"]:
            if agg.expression.owning_part_qn == "SolarBatteryLibrary__Site_Infrastructure":
                if agg.expression.sum_terms:
                    target_agg = agg
                    break

        if target_agg is None:
            # Construct from any agg -- use Site_Infrastructure raw_material_cost
            # which has SingletonTerms for permitting. Create a synthetic SumTerm.
            for agg in solar_battery_agg["aggregation_data"]:
                if (agg.expression.owning_part_qn == "SolarBatteryLibrary__Site_Infrastructure"
                        and agg.expression.attribute_name == "raw_material_cost"):
                    # Add a synthetic SumTerm referencing permitting.raw_material_cost
                    synth_term = SumTerm(
                        part_usage_name="permitting",
                        attribute_name="raw_material_cost",
                        multiplicity_attr=None,
                        multiplicity_count=None,
                    )
                    modified_expr = replace(
                        agg.expression,
                        sum_terms=[synth_term],
                        transformed_expression="permitting.raw_material_cost",
                    )
                    target_agg = replace(agg, expression=modified_expr)
                    break

        assert target_agg is not None, "Could not construct SumTerm literal fallback test"

        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        module, _new_eps = _build_aggregation_module(
            agg=target_agg,
            redefinitions=solar_battery_agg["redefinitions"],
            output_registry=solar_battery_agg["registry"],
            entry_points=ep_working,
            group_deriver=solar_battery_agg["group_deriver"],
            expose_aliases=solar_battery_agg["expose_aliases"],
            usage_type_map=solar_battery_agg["usage_type_map"],
            producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
        )
        ep_working.update(_new_eps)

        # Find the SumTerm EP and verify it has the literal default
        for term in target_agg.expression.sum_terms:
            param = f"{term.part_usage_name}_{term.attribute_name}"
            for inp in module.inputs:
                if inp.param_name == param and inp.source.source_type == "entry_point":
                    ep = ep_working[inp.source.qualified_name]
                    lit_val = _find_literal_redefinition(
                        term.part_usage_name,
                        term.attribute_name,
                        solar_battery_agg["redefinitions"],
                        solar_battery_agg["usage_type_map"],
                        target_agg.expression.owning_part_qn,
                    )
                    assert lit_val is not None, (
                        f"_find_literal_redefinition should find 0.0 for "
                        f"permitting.{term.attribute_name}"
                    )
                    assert ep.default_value == lit_val, (
                        f"EP default {ep.default_value} != literal {lit_val}"
                    )

    @pytest.mark.req("REQ-LVP-03")
    def test_singleton_literal_fallback(self, solar_battery_agg):
        """SingletonTerm where channel fails but LITERAL redef exists: EP default matches."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_literal_default = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )
            ep_working.update(_new_eps)

            for s_term in agg.expression.singleton_terms:
                expected_param = s_term.source_path.replace(".", "_")
                for inp in module.inputs:
                    if inp.param_name == expected_param and inp.source.source_type == "entry_point":
                        ep = ep_working[inp.source.qualified_name]
                        if ep.default_value is not None and "." in s_term.source_path:
                            s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)
                            lit_val = _find_literal_redefinition(
                                s_part_usage,
                                s_attr,
                                solar_battery_agg["redefinitions"],
                                solar_battery_agg["usage_type_map"],
                                agg.expression.owning_part_qn,
                            )
                            if lit_val is not None:
                                assert ep.default_value == lit_val, (
                                    f"EP default {ep.default_value} != literal {lit_val}"
                                )
                                found_literal_default = True

        if not found_literal_default:
            pytest.skip(
                "No SingletonTerm with literal redef default found in solar_battery"
            )


# ===========================================================================
# REQ-MF-07: LocalTerm 3-strategy cascade
# ===========================================================================


@pytest.mark.req("REQ-MF-07")
class TestLocalTermResolution:
    """Verify LocalTerm resolution strategies: sibling, expose alias, entry point."""

    def test_localterm_sibling_agg_output(self, solar_battery_agg):
        """LocalTerm resolved via sibling aggregation output wires the doubled PQN literal.

        Converted from pass-or-skip to pass-or-FAIL. The former body set found_sibling
        only inside nested ifs (a miss flipped nothing) and ended on pytest.skip -- so it
        could pass or skip but never fail. Worse, its inner comparison rebuilt the channel
        with the exact two lines production runs, so even a match proved nothing.

        The idiot_index aggregation at solar_array has local_terms
        [capital_cost, raw_material_cost], both sibling aggregations at that scope, so both
        resolve via the sibling strategy. Anchor capital_cost's producer_channel to a
        hardcoded literal and end on an unconditional assert found.
        """
        agg = _select_agg(
            solar_battery_agg,
            "SolarBatteryDesign__solar_battery_plant__solar_array",
            "idiot_index",
        )
        module = _build_one(solar_battery_agg, agg)

        found = False
        for inp in module.inputs:
            if inp.param_name == "capital_cost":
                assert inp.source.source_type == "module_output", (
                    f"capital_cost LocalTerm should resolve to a sibling module_output, "
                    f"got {inp.source.source_type!r}"
                )
                # provenance: sibling aggregation channel PQN. capital_cost is itself an
                #   aggregation on solar_array; get_channel_name doubles the trailing attr
                #   (ADR-003, core/qualified_names.py:98-100) -- do NOT de-double.
                assert inp.source.producer_channel == (
                    "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost"
                ), f"producer_channel mismatch: {inp.source.producer_channel!r}"
                found = True

        assert found, (
            "idiot_index/solar_array aggregation with capital_cost LocalTerm not found"
        )

    def test_localterm_expose_alias(self, solar_battery_agg):
        """LocalTerm resolved via EXPOSE_PURE alias wires the aliased channel literal.

        Converted from pass-or-skip to pass-or-FAIL (same defect shape as
        test_localterm_sibling_agg_output). The capital_cost aggregation on solar_array
        has local_terms [misc_hardware_cost], an EXPOSE_PURE alias resolving to the
        allocation_model total_allocation channel.
        """
        agg = _select_agg(
            solar_battery_agg,
            "SolarBatteryDesign__solar_battery_plant__solar_array",
            "capital_cost",
        )
        module = _build_one(solar_battery_agg, agg)

        found = False
        for inp in module.inputs:
            if inp.param_name == "misc_hardware_cost":
                assert inp.source.source_type == "module_output", (
                    f"misc_hardware_cost LocalTerm should resolve via its expose alias to "
                    f"a module_output, got {inp.source.source_type!r}"
                )
                # provenance: EXPOSE_PURE alias misc_hardware_cost = allocation_model.
                #   total_allocation (tests/fixtures/solar_battery_model/library.sysml:612);
                #   allocation_model at library.sysml:607.
                assert inp.source.producer_channel == (
                    "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model__total_allocation"
                ), f"producer_channel mismatch: {inp.source.producer_channel!r}"
                found = True

        assert found, (
            "capital_cost/solar_array aggregation with misc_hardware_cost LocalTerm not found"
        )

    def test_localterm_entry_point_fallback(self, solar_battery_agg):
        """LocalTerm unresolvable -> source_type='entry_point'.

        Constructed: all 9 solar_battery LocalTerms resolve naturally (8 sibling,
        1 expose alias). Add a synthetic LocalTerm with a name that has no sibling
        agg output and no expose alias to force the EP fallback.
        """
        from sysml_codegen.extraction.data_models import LocalTerm

        # Use an existing agg and add a synthetic unresolvable LocalTerm
        agg = solar_battery_agg["aggregation_data"][0]
        synth_local = LocalTerm(attribute_name="nonexistent_cost_attr")
        modified_expr = replace(
            agg.expression,
            local_terms=list(agg.expression.local_terms) + [synth_local],
            transformed_expression=(
                agg.expression.transformed_expression + " + nonexistent_cost_attr"
            ),
        )
        modified_agg = replace(agg, expression=modified_expr)

        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        module, _new_eps = _build_aggregation_module(
            agg=modified_agg,
            redefinitions=solar_battery_agg["redefinitions"],
            output_registry=solar_battery_agg["registry"],
            entry_points=ep_working,
            group_deriver=solar_battery_agg["group_deriver"],
            expose_aliases=solar_battery_agg["expose_aliases"],
            usage_type_map=solar_battery_agg["usage_type_map"],
            producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
        )

        # Find the synthetic LocalTerm's input
        found = False
        for inp in module.inputs:
            if inp.param_name == "nonexistent_cost_attr":
                assert inp.source.source_type == "entry_point", (
                    f"Unresolvable LocalTerm should fall back to entry_point, "
                    f"got {inp.source.source_type!r}"
                )
                expected_ep_qn = f"{modified_agg.module_eqn}__nonexistent_cost_attr"
                assert inp.source.qualified_name == expected_ep_qn, (
                    f"LocalTerm EP qn {inp.source.qualified_name!r} != "
                    f"expected {expected_ep_qn!r}"
                )
                found = True

        assert found, "Synthetic unresolvable LocalTerm input not found in module"


# ===========================================================================
# REQ-LVP-01: _find_literal_redefinition type-aware first
# ===========================================================================


@pytest.mark.req("REQ-LVP-01")
class TestFindLiteralRedefinition:
    """Verify _find_literal_redefinition() strategy order."""

    def test_find_literal_redef_type_aware_first(self, solar_battery_agg):
        """Strategy 1 (type-aware via usage_type_map) finds value for permitting costs.

        Literal redefs exist for Permitting_Interconnect (raw_material_cost=0.0, etc.).
        These are referenced as SingletonTerms in Site_Infrastructure aggregations.
        """
        redefinitions = solar_battery_agg["redefinitions"]
        usage_type_map = solar_battery_agg["usage_type_map"]

        # Test with permitting SingletonTerms from Site_Infrastructure aggs
        found = False
        for agg in solar_battery_agg["aggregation_data"]:
            if agg.expression.owning_part_qn != "SolarBatteryLibrary__Site_Infrastructure":
                continue
            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                part, attr = s_term.source_path.rsplit(".", 1)

                # With usage_type_map (Strategy 1)
                val_with_map = _find_literal_redefinition(
                    part, attr, redefinitions,
                    usage_type_map, agg.expression.owning_part_qn,
                )
                # Without usage_type_map (Strategy 2 only)
                val_without_map = _find_literal_redefinition(
                    part, attr, redefinitions, None, agg.expression.owning_part_qn,
                )

                if val_with_map is not None:
                    found = True
                    # Strategy 2 may NOT find the same value when the usage name
                    # differs from the PartDef name (e.g., "permitting" usage →
                    # "Permitting_Interconnect" PartDef). This is exactly why
                    # Strategy 1 (type-aware) exists.
                    if val_without_map is None:
                        # Strategy 1 uniquely resolves this -- confirms type-aware
                        # strategy is necessary for aliased usage names
                        pass
                    else:
                        assert val_with_map == val_without_map, (
                            f"Strategy values disagree: S1={val_with_map}, "
                            f"S2={val_without_map} for {s_term.source_path}"
                        )

        assert found, (
            "No literal redefinition found with type-aware strategy in solar_battery"
        )


# ===========================================================================
# REQ-LVP-04: LocalTerm does NOT use literal redef
# ===========================================================================


@pytest.mark.req("REQ-LVP-04")
class TestLocalTermNoLiteralRedef:
    """Verify LocalTerm entry points do not call _find_literal_redefinition()."""

    def test_localterm_no_literal_redef(self, solar_battery_agg):
        """LocalTerm entry points have default_value=None (no literal redef fallback)."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )
            ep_working.update(_new_eps)

            for l_term in agg.expression.local_terms:
                for inp in module.inputs:
                    if (inp.param_name == l_term.attribute_name
                            and inp.source.source_type == "entry_point"):
                        ep = ep_working[inp.source.qualified_name]
                        assert ep.default_value is None, (
                            f"LocalTerm EP {ep.qualified_name} should have "
                            f"default_value=None (no literal redef), got {ep.default_value}"
                        )


# ===========================================================================
# REQ-LVP-05: Default backfill
# ===========================================================================


@pytest.mark.req("REQ-LVP-05")
class TestDefaultBackfill:
    """Verify entry point default backfill replaces None with literal values."""

    def test_default_backfill(self, solar_battery_agg):
        """Entry point created with None default is backfilled by later term's literal.

        Constructed scenario: pre-create an entry point with None default for a
        SingletonTerm QN where _find_literal_redefinition finds 0.0 (permitting costs).
        """
        redefinitions = solar_battery_agg["redefinitions"]
        usage_type_map = solar_battery_agg["usage_type_map"]

        # Find a SingletonTerm with a literal redef value
        target_agg = None
        target_part = None
        target_attr = None
        target_lit = None
        for agg in solar_battery_agg["aggregation_data"]:
            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                part, attr = s_term.source_path.rsplit(".", 1)
                lit_val = _find_literal_redefinition(
                    part, attr, redefinitions, usage_type_map,
                    agg.expression.owning_part_qn,
                )
                if lit_val is not None:
                    target_agg = agg
                    target_part = part
                    target_attr = attr
                    target_lit = lit_val
                    break
            if target_agg:
                break

        assert target_agg is not None, (
            "No SingletonTerm with literal redef for backfill test"
        )

        # Pre-create the entry point with None default
        param_name = f"{target_part}_{target_attr}"
        ep_qn = f"{target_agg.module_eqn}__{param_name}"
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        ep_working[ep_qn] = EntryPoint(
            qualified_name=ep_qn,
            simple_name=param_name,
            entry_type=EntryPointType.DESIGN_ATTRIBUTE,
            default_value=None,
        )

        # Call factory -- should backfill the None default via returned EPs
        _module, _new_eps = _build_aggregation_module(
            agg=target_agg,
            redefinitions=solar_battery_agg["redefinitions"],
            output_registry=solar_battery_agg["registry"],
            entry_points=ep_working,
            group_deriver=solar_battery_agg["group_deriver"],
            expose_aliases=solar_battery_agg["expose_aliases"],
            usage_type_map=solar_battery_agg["usage_type_map"],
            producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
        )
        ep_working.update(_new_eps)

        # Verify backfill
        assert ep_working[ep_qn].default_value == target_lit, (
            f"Backfill failed: EP {ep_qn} default_value={ep_working[ep_qn].default_value}, "
            f"expected {target_lit}"
        )


# ===========================================================================
# REQ-LVP-06: usage_type_map threaded through
# ===========================================================================


@pytest.mark.req("REQ-LVP-06")
class TestUsageTypeMap:
    """Verify usage_type_map from HierarchyExtractionResult is threaded through."""

    def test_usage_type_map_threaded(self, solar_battery_agg):
        """usage_type_map is available and non-empty."""
        assert solar_battery_agg["usage_type_map"], (
            "usage_type_map should be non-empty for solar_battery"
        )

    def test_usage_type_map_resolves_usage_names(self, solar_battery_agg):
        """At least one literal redef resolution uses type-aware strategy.

        Permitting SingletonTerms in Site_Infrastructure have literal redefs
        resolved via usage_type_map → Permitting_Interconnect type.
        """
        redefinitions = solar_battery_agg["redefinitions"]
        usage_type_map = solar_battery_agg["usage_type_map"]
        found = False

        for agg in solar_battery_agg["aggregation_data"]:
            # Check both SumTerms and SingletonTerms
            for term in agg.expression.sum_terms:
                key = (agg.expression.owning_part_qn, term.part_usage_name)
                if key in usage_type_map:
                    val = _find_literal_redefinition(
                        term.part_usage_name, term.attribute_name,
                        redefinitions, usage_type_map, agg.expression.owning_part_qn,
                    )
                    if val is not None:
                        found = True

            for s_term in agg.expression.singleton_terms:
                if "." not in s_term.source_path:
                    continue
                part, attr = s_term.source_path.rsplit(".", 1)
                key = (agg.expression.owning_part_qn, part)
                if key in usage_type_map:
                    val = _find_literal_redefinition(
                        part, attr, redefinitions, usage_type_map,
                        agg.expression.owning_part_qn,
                    )
                    if val is not None:
                        found = True

        assert found, "No literal redef resolution used type-aware strategy"


# ===========================================================================
# REQ-LVP-07: Compilability determination
# ===========================================================================


@pytest.mark.req("REQ-LVP-07")
class TestCompilability:
    """Verify FULLY_COMPILABLE vs MANUAL_REQUIRED determination."""

    def test_compilability_fully_compilable(self, solar_battery_agg):
        """Modules where all terms resolved: compilability == FULLY_COMPILABLE."""
        ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
        found_fully = False

        for agg in solar_battery_agg["aggregation_data"]:
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=solar_battery_agg["redefinitions"],
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )
            if module.compilability == Compilability.FULLY_COMPILABLE:
                found_fully = True
                # Verify this module actually has resolved terms
                assert not agg.expression.has_unsupported_nodes

        assert found_fully, "No FULLY_COMPILABLE aggregation module found in solar_battery"

    def test_compilability_manual_required_on_unresolved(self, solar_battery_agg):
        """SumTerm/SingletonTerm with no channel and no literal: MANUAL_REQUIRED.

        Constructed: use a Site_Infrastructure agg but strip BOTH CHAIN and LITERAL
        redefinitions so the SingletonTerm channel resolution fails and no literal
        default is available.
        """
        # Find a Site_Infrastructure agg with SingletonTerms
        for agg in solar_battery_agg["aggregation_data"]:
            if not agg.expression.singleton_terms:
                continue

            # Strip all redefinitions so channel resolution fails for CHAIN-dependent
            # terms, and literal lookup finds nothing
            ep_working = copy.deepcopy(solar_battery_agg["entry_points"])
            module, _new_eps = _build_aggregation_module(
                agg=agg,
                redefinitions=[],  # No redefinitions at all
                output_registry=solar_battery_agg["registry"],
                entry_points=ep_working,
                group_deriver=solar_battery_agg["group_deriver"],
                expose_aliases=solar_battery_agg["expose_aliases"],
                usage_type_map=solar_battery_agg["usage_type_map"],
                producer_ctx=_probe_ctx(solar_battery_agg["registry"]),
            )

            # Check if any non-LocalTerm input is EP without default
            has_unresolved = False
            for inp in module.inputs:
                if inp.source.source_type == "entry_point":
                    ep = ep_working.get(inp.source.qualified_name)
                    if ep and ep.default_value is None:
                        is_local = any(
                            lt.attribute_name == inp.param_name
                            for lt in agg.expression.local_terms
                        )
                        if not is_local:
                            has_unresolved = True

            if has_unresolved:
                assert module.compilability == Compilability.MANUAL_REQUIRED, (
                    f"Module {module.name} has unresolved SumTerm/SingletonTerm "
                    f"without literal default but compilability={module.compilability}"
                )
                return  # Found and verified

        pytest.skip(
            "No scenario where SumTerm/SingletonTerm falls to EP without literal default"
        )
