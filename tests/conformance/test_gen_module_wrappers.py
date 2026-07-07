"""Conformance tests for Module Wrapper Generator (C21).

Requirements: REQ-GEN-02
Design intent: 08-generation.md

Tests verify generate_teax_module() behavior with real PipelineModule data:
- REQ-GEN-02: One wrapper per CalcUsage PipelineModule
- REQ-GEN-02: Generated code is valid Python (ast.parse)
- REQ-GEN-02: Class name matches PipelineModule.module_type
- REQ-GEN-02: Impl import path consistency with PythonModulePath
- REQ-GEN-02: Input names match PipelineModule.inputs
- REQ-GEN-02: Input types match PipelineModule.inputs[i].python_type
- REQ-GEN-02: Single-output returns Float, multi-output returns named class
- REQ-GEN-02: Type cross-reference with ComputationGraph
- REQ-GEN-02: map_sysml_type_to_python() covers all SysML primitive types
- REQ-GEN-02: Static analysis — modules.py has zero extraction imports
- REQ-GEN-02: Static analysis — stub template is dead code
- REQ-GEN-02: Wrapper coverage by module type

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.modules import (
    generate_teax_module,
)
from sysml_codegen.generation.type_mapping import map_sysml_type_to_python
from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
from sysml_codegen.resolution.models import ComputationGraph

from sysml_codegen.snapshot import (
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
SRC_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen"

PARAMETRIZED_MODELS = [
    "solar_battery_model",
    "catf_mfe_model",
]

MODEL_IDS = {
    "solar_battery_model": "solar_battery",
    "catf_mfe_model": "catf_mfe",
}


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment for module wrapper generation."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture(scope="session")
def all_graph_data() -> dict[str, tuple[ComputationGraph, dict]]:
    """Build ComputationGraphs + inputs for all models (once per session)."""
    data = {}
    for model_name in PARAMETRIZED_MODELS:
        graph, inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        data[model_name] = (graph, inputs)
    return data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_calcusage_modules(graph: ComputationGraph) -> list:
    """Get CalcUsage PipelineModules from graph (not FORMULA, not aggregation)."""
    return [
        m for m in graph.modules
        if not m.is_computed_attribute and not m.is_aggregation
    ]


def _generate_wrapper(module, template_env, package_name="generated_code") -> str:
    """Generate wrapper code for a PipelineModule using a temp output path."""
    return generate_teax_module(
        module,
        template_env=template_env,
        output_path=Path("/tmp/test_wrapper.py"),
        package_name=package_name,
    )


def _extract_class_names_from_code(code: str) -> list[str]:
    """Extract all class names from generated Python code via AST."""
    tree = ast.parse(code)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def _extract_field_names_from_input_class(code: str, input_class_name: str) -> list[str]:
    """Extract field names from the BaseModel input class via AST.

    Fields are class-level assignments with type annotations.
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == input_class_name:
            fields = []
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    fields.append(item.target.id)
            return fields
    return []


# ---------------------------------------------------------------------------
# REQ-GEN-02: One wrapper per CalcUsage PipelineModule
# ---------------------------------------------------------------------------

class TestOneWrapperPerCalcUsageModule:
    """Every CalcUsage PipelineModule has a corresponding calc_def that
    produces non-empty wrapper code."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_one_wrapper_per_calcusage_module(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        assert len(calcusage_modules) > 0, f"No CalcUsage modules in {model_name}"

        # Every CalcUsage module produces non-empty wrapper code
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)
            assert len(code.strip()) > 0, (
                f"Empty wrapper for {module.name} in {model_name}"
            )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Generated code is valid Python
# ---------------------------------------------------------------------------

class TestGeneratedCodeValidPython:
    """Every generated wrapper passes ast.parse() — valid Python."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_generated_code_valid_python(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        failures = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)
            try:
                ast.parse(code)
            except SyntaxError as e:
                failures.append(f"  {module.name}: {e}")

        assert not failures, (
            f"Invalid Python in {model_name} wrappers:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Class name matches module_type
# ---------------------------------------------------------------------------

class TestClassNameMatchesModuleType:
    """Generated class name == PipelineModule.module_type.split('.')[-1]."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_class_name_matches_module_type(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        mismatches = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)
            class_names = _extract_class_names_from_code(code)

            expected_class = module.module_type.split(".")[-1]

            if expected_class not in class_names:
                mismatches.append(
                    f"  {module.name}: expected {expected_class}, "
                    f"found classes {class_names}"
                )

        assert not mismatches, (
            f"Class name mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Impl import path consistency
# ---------------------------------------------------------------------------

class TestImplImportPathConsistency:
    """impl_import_path in generated code matches PythonModulePath derivation."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_impl_import_path_consistency(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        mismatches = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)

            # Derive expected impl_import_path from module.calc_def_qualified_name
            sqn = SysMLQualifiedName(module.calc_def_qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            expected_impl_path = python_path.impl_import_path

            # Check that the expected path appears in the generated code
            if expected_impl_path not in code:
                mismatches.append(
                    f"  {module.name}: expected '{expected_impl_path}' "
                    f"not found in generated code"
                )

        assert not mismatches, (
            f"Impl import path mismatches in {model_name}:\n"
            + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Input names match calc_def
# ---------------------------------------------------------------------------

class TestInputNamesMatchModule:
    """Input field names in generated BaseModel match PipelineModule.inputs."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_input_names_match_module(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        mismatches = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)
            input_class_name = f"{module.calc_def_name}Input"

            generated_fields = _extract_field_names_from_input_class(
                code, input_class_name
            )
            expected_fields = [inp.param_name for inp in module.inputs]

            if generated_fields != expected_fields:
                mismatches.append(
                    f"  {module.name}: expected {expected_fields}, "
                    f"got {generated_fields}"
                )

        assert not mismatches, (
            f"Input name mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Input types match map_sysml_type_to_python()
# ---------------------------------------------------------------------------

class TestInputTypesMatchModule:
    """Input type hints in generated code match PipelineModule.inputs[i].python_type."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_input_types_match_module(
        self, model_name, all_graph_data, template_env,
    ):
        # NOTE (Item 6, L5): template-fidelity check -- expected types come from
        # module.inputs[i].python_type and the generated code renders from the same graph,
        # so both sides derive from one source. Residual value: the Jinja template faithfully
        # renders the graph's types. The type-map CONTENT is pinned by the literal sibling
        # test_gen_schemas.py:359-381. Kept as a fidelity guard; sibling-pinned for content.
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        mismatches = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)

            # Parse type hints from generated code
            tree = ast.parse(code)
            input_class_name = f"{module.calc_def_name}Input"

            # Build expected types from PipelineModule inputs
            expected_types = {inp.param_name: inp.python_type for inp in module.inputs}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == input_class_name:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            expected_type = expected_types.get(field_name)
                            if expected_type is None:
                                continue
                            actual_type = ast.unparse(item.annotation)
                            if actual_type != expected_type:
                                mismatches.append(
                                    f"  {module.name}.{field_name}: "
                                    f"expected '{expected_type}', got '{actual_type}'"
                                )

        assert not mismatches, (
            f"Input type mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Single-output returns Float
# ---------------------------------------------------------------------------

class TestSingleOutputReturnsFloat:
    """Single-output modules return Float in run() method."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_single_output_returns_float(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        tested = 0
        failures = []
        for module in calcusage_modules:
            if len(module.outputs) != 1:
                continue

            code = _generate_wrapper(module, template_env)
            tested += 1

            # Single-output: ModuleBase[InputClass, Float]
            if "ModuleBase[" not in code:
                failures.append(f"  {module.name}: no ModuleBase[] found")
                continue

            # Check for Float return type pattern
            pattern = rf"ModuleBase\[{module.calc_def_name}Input, Float\]"
            if not re.search(pattern, code):
                failures.append(
                    f"  {module.name}: expected ModuleBase[{module.calc_def_name}Input, Float]"
                )

        assert tested > 0, f"No single-output modules in {model_name}"
        assert not failures, (
            f"Single-output return type failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Multi-output returns named output class
# ---------------------------------------------------------------------------

class TestMultiOutputReturnsNamedClass:
    """Multi-output modules return named output class."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_multi_output_returns_named_class(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        tested = 0
        failures = []
        for module in calcusage_modules:
            if len(module.outputs) < 2:
                continue

            code = _generate_wrapper(module, template_env)
            tested += 1

            output_class_name = f"{module.calc_def_name}Output"

            # Multi-output: ModuleBase[InputClass, OutputClass]
            pattern = rf"ModuleBase\[{module.calc_def_name}Input, {output_class_name}\]"
            if not re.search(pattern, code):
                failures.append(
                    f"  {module.name}: expected ModuleBase[{module.calc_def_name}Input, {output_class_name}]"
                )

            # Output class import should be present
            if f"import {output_class_name}" not in code:
                failures.append(
                    f"  {module.name}: missing import for {output_class_name}"
                )

        assert tested > 0, f"No multi-output modules in {model_name}"
        assert not failures, (
            f"Multi-output return type failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Type cross-reference with ComputationGraph
# ---------------------------------------------------------------------------

class TestInputTypeCrossReferenceWithGraph:
    """Generated code input types match PipelineModule.inputs[i].python_type."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_input_type_cross_reference_with_graph(
        self, model_name, all_graph_data, template_env,
    ):
        # NOTE (Item 6, L6): same template-fidelity shape as test_input_types_match_module
        # (L5) -- compares generated type hints against module.inputs[i].python_type, both
        # from one graph. This test is a near-duplicate of L5; a future cleanup could dedup
        # the two (not done here -- dedup is not Item 6's call). Content sibling-pinned by
        # the literal type-map test (test_gen_schemas.py:359-381).
        graph, _inputs = all_graph_data[model_name]
        calcusage_modules = _get_calcusage_modules(graph)

        mismatches = []
        for module in calcusage_modules:
            code = _generate_wrapper(module, template_env)
            tree = ast.parse(code)
            input_class_name = f"{module.calc_def_name}Input"

            # Build expected types from PipelineModule inputs
            expected_types = {inp.param_name: inp.python_type for inp in module.inputs}

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == input_class_name:
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            field_name = item.target.id
                            expected_type = expected_types.get(field_name)
                            if expected_type is None:
                                continue
                            actual_type = ast.unparse(item.annotation)
                            if actual_type != expected_type:
                                mismatches.append(
                                    f"  {module.name}.{field_name}: "
                                    f"generated='{actual_type}', graph='{expected_type}'"
                                )

        assert not mismatches, (
            f"Type mismatches in {model_name}:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: map_sysml_type_to_python() covers all SysML primitive types
# ---------------------------------------------------------------------------

class TestTypeMappingCoversAllTypes:
    """map_sysml_type_to_python() handles Real, Integer, Boolean, String and their
    ScalarValues:: prefixed forms."""

    @pytest.mark.req("REQ-GEN-02")
    def test_type_mapping_covers_all_sysml_types(self):
        """All known SysML primitive types map to Python types."""
        test_cases = {
            "Real": "float",
            "ScalarValues::Real": "float",
            "Integer": "int",
            "ScalarValues::Integer": "int",
            "String": "str",
            "ScalarValues::String": "str",
            "Boolean": "bool",
            "ScalarValues::Boolean": "bool",
        }

        for sysml_type, expected_python_type in test_cases.items():
            result = map_sysml_type_to_python(sysml_type)
            assert result == expected_python_type, (
                f"map_sysml_type_to_python({sysml_type}) = '{result}', "
                f"expected '{expected_python_type}'"
            )

    @pytest.mark.req("REQ-GEN-02")
    def test_type_mapping_passthrough_for_unknown(self):
        """Unknown SysML types pass through unchanged."""
        result = map_sysml_type_to_python("PlasmaParams")
        assert result == "PlasmaParams"


# ---------------------------------------------------------------------------
# REQ-GEN-02: Static analysis — modules.py imports from extraction
# ---------------------------------------------------------------------------

class TestModulesNoExtractionImports:
    """Static analysis: modules.py has zero extraction imports (7.6 complete)."""

    @pytest.mark.req("REQ-GEN-02")
    def test_modules_py_zero_extraction_imports(self):
        """modules.py has zero imports from extraction/ (REQ-PIPE-07 satisfied)."""
        modules_path = SRC_DIR / "generation" / "modules.py"
        source = modules_path.read_text()
        tree = ast.parse(source)

        extraction_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "extraction" in node.module:
                    extraction_imports.append(
                        f"  line {node.lineno}: from {node.module}"
                    )

        assert len(extraction_imports) == 0, (
            "modules.py still imports from extraction:\n"
            + "\n".join(extraction_imports)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Static analysis — stub template is dead code
# ---------------------------------------------------------------------------

class TestStubTemplateUnused:
    """teax_module_stub.py.jinja2 is not referenced in any source file."""

    @pytest.mark.req("REQ-GEN-02")
    def test_stub_template_unused(self):
        """No .py source file references teax_module_stub.py.jinja2."""
        stub_name = "teax_module_stub.py.jinja2"

        # Search all Python source files
        py_files = list(SRC_DIR.rglob("*.py"))
        references = []
        for py_file in py_files:
            content = py_file.read_text()
            if stub_name in content:
                references.append(str(py_file))

        assert not references, (
            f"Stub template '{stub_name}' is referenced in: {references}"
        )


# ---------------------------------------------------------------------------
# REQ-GEN-02: Wrapper coverage by module type
# ---------------------------------------------------------------------------

class TestWrapperCoverageByModuleType:
    """Count CalcUsage, FORMULA, aggregation PipelineModules in graph;
    document which generator covers each type."""

    @pytest.mark.req("REQ-GEN-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_wrapper_coverage_by_module_type(
        self, model_name, all_graph_data,
    ):
        graph, _ = all_graph_data[model_name]

        calcusage_count = 0
        formula_count = 0
        aggregation_count = 0
        for m in graph.modules:
            if m.is_aggregation:
                aggregation_count += 1
            elif m.is_computed_attribute:
                formula_count += 1
            else:
                calcusage_count += 1

        total = len(graph.modules)
        assert total == calcusage_count + formula_count + aggregation_count

        # CalcUsage modules are covered by generate_teax_module()
        # FORMULA modules are covered by _generate_computed_attr_modules() in cli
        # Aggregation modules are covered by _generate_aggregation_modules() in cli
        # This test documents the breakdown
        assert calcusage_count > 0, f"No CalcUsage modules in {model_name}"

        # Coverage note: generate_teax_module() covers only CalcUsage modules
        # The fraction of total modules it covers:
        coverage_pct = calcusage_count / total * 100 if total > 0 else 0
        assert coverage_pct > 0, (
            f"generate_teax_module() covers 0% of modules in {model_name}"
        )
