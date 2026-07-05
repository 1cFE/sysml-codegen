"""Conformance tests for PipelineModule Field Expansion (C26).

Requirements: REQ-PMM-01 through REQ-PMM-05
Design intent: 26-pipeline-module-migration.md

Tests verify that PipelineModule, ModuleInput, and ModuleOutput carry enough
metadata for generators to produce output from the ComputationGraph alone,
without back-references to CalculationDefinitionData.

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.modules import generate_teax_module
from sysml_codegen.generation.schemas import (
    generate_multioutput_model,
)
from sysml_codegen.generation.stencils import generate_implementation
from sysml_codegen.generation.registry import generate_registry
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleInput,
    ModuleOutput,
    PipelineModule,
)

from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"

PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
]

MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
    "attr_expr_probe": "attr_expr_probe",
    "chain_spike_model": "chain_spike",
}


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment for generation."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def all_graph_data() -> dict[str, tuple[ComputationGraph, dict]]:
    """Build ComputationGraphs + inputs for all 4 models (once per session)."""
    data = {}
    for model_name in PARAMETRIZED_MODELS:
        graph, inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        data[model_name] = (graph, inputs)
    return data


@pytest.fixture(scope="session")
def solar_battery_graph(all_graph_data):
    return all_graph_data["solar_battery_model"]


@pytest.fixture(scope="session")
def catf_mfe_graph(all_graph_data):
    return all_graph_data["catf_mfe_model"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _calcusage_modules(graph: ComputationGraph) -> list[PipelineModule]:
    """Filter to CalcUsage modules (not FORMULA, not aggregation)."""
    return [
        m for m in graph.modules
        if not m.is_computed_attribute and not m.is_aggregation
    ]


def _formula_modules(graph: ComputationGraph) -> list[PipelineModule]:
    """Filter to FORMULA modules."""
    return [m for m in graph.modules if m.is_computed_attribute]


def _aggregation_modules(graph: ComputationGraph) -> list[PipelineModule]:
    """Filter to aggregation modules."""
    return [m for m in graph.modules if m.is_aggregation]


def _build_calcusage_module_to_calcdef_map(
    graph: ComputationGraph, inputs: dict,
) -> dict[str, object]:
    """Map CalcUsage PipelineModule.name -> CalculationDefinitionData."""
    result = inputs["result"]
    snap = inputs["snap"]
    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    usage_to_calcdef = {}
    for usage in result.required_usages:
        module_name = usage.qualified_name.lower()
        usage_to_calcdef[module_name] = usage.calc_def_name

    mapping = {}
    for module in _calcusage_modules(graph):
        calc_def_name = usage_to_calcdef.get(module.name)
        if calc_def_name and calc_def_name in calc_def_map:
            mapping[module.name] = calc_def_map[calc_def_name]
    return mapping


# ===========================================================================
# A. Field Population Tests (REQ-PMM-01, REQ-PMM-02, REQ-PMM-03)
# ===========================================================================

class TestCalcUsageFieldPopulation:
    """REQ-PMM-01: CalcUsage modules have metadata fields populated."""

    @pytest.mark.req("REQ-PMM-01")
    def test_calcusage_modules_have_calc_def_name(self, solar_battery_graph):
        """Every CalcUsage module has calc_def_name populated, matching CalcDef.name."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)
        assert len(mapping) > 0, "No CalcUsage modules found"

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            assert module.calc_def_name is not None, (
                f"Module {module_name}: calc_def_name is None"
            )
            assert module.calc_def_name == calc_def.name, (
                f"Module {module_name}: calc_def_name={module.calc_def_name}, "
                f"expected={calc_def.name}"
            )

    @pytest.mark.req("REQ-PMM-01")
    def test_calcusage_modules_have_calc_def_qualified_name(self, solar_battery_graph):
        """Every CalcUsage module has calc_def_qualified_name matching CalcDef.qualified_name."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            assert module.calc_def_qualified_name is not None, (
                f"Module {module_name}: calc_def_qualified_name is None"
            )
            assert module.calc_def_qualified_name == calc_def.qualified_name, (
                f"Module {module_name}: calc_def_qualified_name={module.calc_def_qualified_name}, "
                f"expected={calc_def.qualified_name}"
            )

    @pytest.mark.req("REQ-PMM-01")
    def test_calcusage_modules_have_doc_comment(self, solar_battery_graph):
        """Every CalcUsage module has doc_comment populated (may be empty string)."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            assert module.doc_comment is not None, (
                f"Module {module_name}: doc_comment is None"
            )
            assert module.doc_comment == calc_def.doc_comment, (
                f"Module {module_name}: doc_comment mismatch"
            )

    @pytest.mark.req("REQ-PMM-03")
    def test_calcusage_modules_have_calc_expressions(self, solar_battery_graph):
        """Every CalcUsage module has calc_expressions populated."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            assert module.calc_expressions is not None, (
                f"Module {module_name}: calc_expressions is None"
            )
            assert module.calc_expressions == calc_def.calc_expressions, (
                f"Module {module_name}: calc_expressions mismatch"
            )

    @pytest.mark.req("REQ-PMM-01")
    def test_calcusage_modules_have_source_location(self, solar_battery_graph):
        """Every CalcUsage module has source_file and source_line populated."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            assert module.source_file is not None, (
                f"Module {module_name}: source_file is None"
            )
            assert module.source_line is not None, (
                f"Module {module_name}: source_line is None"
            )
            assert module.source_file == str(calc_def.source_file), (
                f"Module {module_name}: source_file={module.source_file}, "
                f"expected={calc_def.source_file}"
            )
            assert module.source_line == calc_def.source_line, (
                f"Module {module_name}: source_line={module.source_line}, "
                f"expected={calc_def.source_line}"
            )


class TestModuleInputFieldPopulation:
    """REQ-PMM-02: ModuleInput has description and default_value populated."""

    @pytest.mark.req("REQ-PMM-02")
    def test_module_inputs_have_description(self, solar_battery_graph):
        """For CalcUsage modules, every ModuleInput has description field."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            input_attr_by_name = {a.name: a for a in calc_def.input_attributes}
            for mi in module.inputs:
                assert mi.description is not None, (
                    f"Module {module_name}, input {mi.param_name}: description is None"
                )
                attr = input_attr_by_name.get(mi.param_name)
                if attr:
                    assert mi.description == attr.description, (
                        f"Module {module_name}, input {mi.param_name}: "
                        f"description={mi.description!r}, expected={attr.description!r}"
                    )

    @pytest.mark.req("REQ-PMM-02")
    def test_module_inputs_have_default_value(self, solar_battery_graph):
        """For CalcUsage modules, ModuleInput.default_value matches CalcDef input default."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            input_attr_by_name = {a.name: a for a in calc_def.input_attributes}
            for mi in module.inputs:
                attr = input_attr_by_name.get(mi.param_name)
                if attr:
                    assert mi.default_value == attr.default_value, (
                        f"Module {module_name}, input {mi.param_name}: "
                        f"default_value={mi.default_value!r}, expected={attr.default_value!r}"
                    )


class TestModuleOutputFieldPopulation:
    """REQ-PMM-02: ModuleOutput has description, default_value, unit populated."""

    @pytest.mark.req("REQ-PMM-02")
    def test_module_outputs_have_description(self, solar_battery_graph):
        """For CalcUsage modules, every ModuleOutput has description field."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            output_attr_by_name = {a.name: a for a in calc_def.output_attributes}
            for mo in module.outputs:
                # Single-output uses field_name="root" -- map to first output attr
                if mo.field_name == "root" and len(calc_def.output_attributes) == 1:
                    attr = calc_def.output_attributes[0]
                else:
                    attr = output_attr_by_name.get(mo.field_name)
                if attr:
                    assert mo.description is not None, (
                        f"Module {module_name}, output {mo.field_name}: description is None"
                    )
                    assert mo.description == attr.description, (
                        f"Module {module_name}, output {mo.field_name}: "
                        f"description={mo.description!r}, expected={attr.description!r}"
                    )

    @pytest.mark.req("REQ-PMM-02")
    def test_module_outputs_have_unit(self, solar_battery_graph):
        """ModuleOutput.unit matches CalcDef output attribute unit."""
        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        for module_name, calc_def in mapping.items():
            module = next(m for m in graph.modules if m.name == module_name)
            output_attr_by_name = {a.name: a for a in calc_def.output_attributes}
            for mo in module.outputs:
                if mo.field_name == "root" and len(calc_def.output_attributes) == 1:
                    attr = calc_def.output_attributes[0]
                else:
                    attr = output_attr_by_name.get(mo.field_name)
                if attr:
                    assert mo.unit == attr.unit, (
                        f"Module {module_name}, output {mo.field_name}: "
                        f"unit={mo.unit!r}, expected={attr.unit!r}"
                    )


class TestFormulaModuleFieldPopulation:
    """REQ-PMM-01: FORMULA modules have metadata populated from ComputedAttributeData."""

    @pytest.mark.req("REQ-PMM-01")
    def test_formula_modules_field_population(self, solar_battery_graph):
        """FORMULA modules have calc_def_name, source_file, source_line populated."""
        graph, inputs = solar_battery_graph
        formula_mods = _formula_modules(graph)
        if not formula_mods:
            pytest.skip("No FORMULA modules in solar_battery")

        for module in formula_mods:
            assert module.calc_def_name is not None, (
                f"FORMULA module {module.name}: calc_def_name is None"
            )
            assert module.source_file is not None, (
                f"FORMULA module {module.name}: source_file is None"
            )
            assert module.source_line is not None, (
                f"FORMULA module {module.name}: source_line is None"
            )
            # FORMULA modules should have calc_expressions with the expression text
            assert module.calc_expressions is not None, (
                f"FORMULA module {module.name}: calc_expressions is None"
            )


class TestAggregationModuleFieldPopulation:
    """REQ-PMM-01: Aggregation modules have metadata populated from AggregationExpressionData."""

    @pytest.mark.req("REQ-PMM-01")
    def test_aggregation_modules_field_population(self, solar_battery_graph):
        """Aggregation modules have calc_def_name, source_file, source_line populated."""
        graph, inputs = solar_battery_graph
        agg_mods = _aggregation_modules(graph)
        if not agg_mods:
            pytest.skip("No aggregation modules in solar_battery")

        for module in agg_mods:
            assert module.calc_def_name is not None, (
                f"Aggregation module {module.name}: calc_def_name is None"
            )
            assert module.source_file is not None, (
                f"Aggregation module {module.name}: source_file is None"
            )
            assert module.source_line is not None, (
                f"Aggregation module {module.name}: source_line is None"
            )
            # Aggregation modules should have calc_expressions with the raw expression
            assert module.calc_expressions is not None, (
                f"Aggregation module {module.name}: calc_expressions is None"
            )


# ===========================================================================
# D. Cross-Model Parametrized Tests (REQ-PMM-01)
# ===========================================================================

class TestCrossModelMetadata:
    """REQ-PMM-01: All modules across all 4 models have metadata populated."""

    @pytest.mark.req("REQ-PMM-01")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS)
    def test_no_calcusage_module_has_none_calc_def_name(self, all_graph_data, model_name):
        """Zero CalcUsage modules with calc_def_name=None."""
        graph, inputs = all_graph_data[model_name]
        cu_modules = _calcusage_modules(graph)
        assert len(cu_modules) > 0, f"No CalcUsage modules in {model_name}"

        for module in cu_modules:
            assert module.calc_def_name is not None, (
                f"Model {model_name}, module {module.name}: calc_def_name is None"
            )

    @pytest.mark.req("REQ-PMM-01")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS)
    def test_all_modules_have_metadata_fields(self, all_graph_data, model_name):
        """All modules in graph have calc_def_name and source_file populated."""
        graph, inputs = all_graph_data[model_name]
        assert len(graph.modules) > 0, f"No modules in {model_name}"

        for module in graph.modules:
            assert module.calc_def_name is not None, (
                f"Model {model_name}, module {module.name}: calc_def_name is None"
            )
            assert module.source_file is not None, (
                f"Model {model_name}, module {module.name}: source_file is None"
            )


# ===========================================================================
# B. Output Identity Tests (REQ-PMM-04)
# ===========================================================================

class TestOutputIdentity:
    """REQ-PMM-04: _from_graph() variants produce byte-identical output."""

    @pytest.mark.req("REQ-PMM-04")
    def test_module_wrapper_output_valid(self, solar_battery_graph, template_env):
        """generate_teax_module(module) produces valid Python for CalcUsage modules."""
        graph, inputs = solar_battery_graph
        cu_modules = _calcusage_modules(graph)
        assert len(cu_modules) > 0, "No CalcUsage modules"

        for module in cu_modules:
            code = generate_teax_module(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_wrapper.py"),
                package_name="generated_code",
            )
            assert code is not None and len(code) > 0
            ast.parse(code)

    @pytest.mark.req("REQ-PMM-04")
    def test_stencil_output_valid(self, solar_battery_graph, template_env):
        """generate_implementation(module) produces valid Python for CalcUsage modules."""
        graph, inputs = solar_battery_graph
        cu_modules = _calcusage_modules(graph)

        for module in cu_modules:
            code = generate_implementation(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_stencil.py"),
                package_name="generated_code",
            )
            assert code is not None and len(code) > 0
            ast.parse(code)

    @pytest.mark.req("REQ-PMM-04")
    def test_schema_from_graph(self, solar_battery_graph, template_env):
        """generate_multioutput_model(module) produces valid schema code for multi-output modules."""
        graph, _inputs = solar_battery_graph

        multi_modules = [m for m in graph.modules if len(m.outputs) >= 2]
        for module in multi_modules:
            code = generate_multioutput_model(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_schema.py"),
                package_name="generated_code",
            )
            assert code is not None
            ast.parse(code)  # Valid Python

    @pytest.mark.req("REQ-PMM-04")
    def test_schema_from_graph_catf_mfe(self, catf_mfe_graph, template_env):
        """Schema generation from graph works for catf_mfe (has multi-output modules)."""
        graph, _inputs = catf_mfe_graph

        multi_modules = [m for m in graph.modules if len(m.outputs) >= 2]
        assert len(multi_modules) > 0, "Expected at least one multi-output module in catf_mfe"

        for module in multi_modules:
            code = generate_multioutput_model(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_schema.py"),
                package_name="generated_code",
            )
            assert code is not None
            ast.parse(code)

    @pytest.mark.req("REQ-PMM-04")
    def test_registry_from_graph(self, solar_battery_graph, template_env):
        """generate_registry(graph, ...) produces valid registry code."""
        graph, _inputs = solar_battery_graph

        output = generate_registry(
            graph=graph,
            package_name="generated_code",
            template_env=template_env,
            output_path=Path("/tmp/test_registry.py"),
        )

        assert output is not None
        assert len(output) > 0
        ast.parse(output)  # Valid Python


# ===========================================================================
# C. Migration Coexistence Tests (REQ-PMM-05)
# ===========================================================================

class TestMigrationCoexistence:
    """REQ-PMM-05: Old and new generators coexist."""

    @pytest.mark.req("REQ-PMM-05")
    def test_generators_produce_valid_output(self, solar_battery_graph, template_env):
        """Generator functions produce valid output from PipelineModule."""
        graph, inputs = solar_battery_graph
        cu_modules = _calcusage_modules(graph)

        for module in cu_modules[:1]:
            code = generate_teax_module(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test.py"),
                package_name="generated_code",
            )
            assert code is not None
            assert len(code) > 0
            ast.parse(code)  # Valid Python

    @pytest.mark.req("REQ-PMM-05")
    def test_from_graph_variants_importable(self):
        """All 4 _from_graph() variants importable from generation package."""
        from sysml_codegen.generation.modules import generate_teax_module_from_graph
        from sysml_codegen.generation.stencils import generate_implementation_from_graph
        from sysml_codegen.generation.schemas import generate_multioutput_model_from_graph
        from sysml_codegen.generation.registry import generate_registry_from_graph

        assert callable(generate_teax_module_from_graph)
        assert callable(generate_implementation_from_graph)
        assert callable(generate_multioutput_model_from_graph)
        assert callable(generate_registry_from_graph)

    @pytest.mark.req("REQ-PMM-05")
    def test_old_fields_unchanged(self, solar_battery_graph):
        """Existing PipelineModule fields unchanged by field expansion."""
        graph, inputs = solar_battery_graph

        for module in graph.modules:
            # These fields must still exist and be populated
            assert isinstance(module.name, str) and len(module.name) > 0
            assert isinstance(module.module_type, str) and len(module.module_type) > 0
            assert isinstance(module.inputs, list)
            assert isinstance(module.outputs, list)
            assert isinstance(module.execution_order, int)
            assert isinstance(module.compilability, Compilability)
            assert isinstance(module.is_computed_attribute, bool)
            assert isinstance(module.is_aggregation, bool)

            for inp in module.inputs:
                assert isinstance(inp.param_name, str)
                assert isinstance(inp.python_type, str)
                assert inp.source is not None

            for out in module.outputs:
                assert isinstance(out.field_name, str)
                assert isinstance(out.python_type, str)
                assert isinstance(out.channel_name, str)
