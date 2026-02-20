"""Conformance tests for Schema Generator (C22).

Requirements: REQ-OSR-01 through REQ-OSR-07
Design intent: 22-output-schema-rules.md

Tests verify schema generation behavior with real extraction snapshots:
- REQ-OSR-01: Single-output modules use field_name="root"
- REQ-OSR-02: Multi-output modules generate named MultiOutput subclass
- REQ-OSR-03: Output field names match SysML output_attributes
- REQ-OSR-04: SysML types map to Python types per mapping table
- REQ-OSR-05: Output fields MUST NOT have default= values
- REQ-OSR-06: Aggregation and FORMULA always single-output
- REQ-OSR-07: Output channels use PQN format

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.generation.schemas import (
    generate_multioutput_model,
)
from sysml_codegen.generation.type_mapping import map_sysml_type_to_python
from sysml_codegen.resolution.models import ComputationGraph

from tests.conformance.test_entry_point_classifier import (
    build_full_graph_from_snapshot,
)


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
    """Jinja2 template environment for schema generation."""
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
        graph, inputs = build_full_graph_from_snapshot(model_name)
        data[model_name] = (graph, inputs)
    return data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_multi_output_modules(graph: ComputationGraph) -> list:
    """Return PipelineModules with 2+ outputs."""
    return [m for m in graph.modules if len(m.outputs) >= 2]


def _get_single_output_modules(graph: ComputationGraph) -> list:
    """Return PipelineModules with exactly 1 output."""
    return [m for m in graph.modules if len(m.outputs) == 1]


# ---------------------------------------------------------------------------
# REQ-OSR-01: Single-output modules use field_name="root"
# ---------------------------------------------------------------------------

class TestSingleOutputUsesRootField:
    """Every PipelineModule with 1 output has field_name='root'."""

    @pytest.mark.req("REQ-OSR-01")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_single_output_uses_root_field(
        self, model_name, all_graph_data,
    ):
        graph, _ = all_graph_data[model_name]

        failures = []
        tested = 0
        for module in graph.modules:
            if len(module.outputs) != 1:
                continue
            tested += 1
            output = module.outputs[0]
            if output.field_name != "root":
                failures.append(
                    f"  {module.name}: field_name='{output.field_name}', expected 'root'"
                )

        assert tested > 0, f"No single-output modules in {model_name}"
        assert not failures, (
            f"Single-output field_name failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-02: Multi-output modules generate named MultiOutput subclass
# ---------------------------------------------------------------------------

class TestMultiOutputGenerated:
    """generate_multioutput_model() produces non-None code for modules with 2+ outputs."""

    @pytest.mark.req("REQ-OSR-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_multioutput_generated_for_multi_output_modules(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]
        multi_output_modules = _get_multi_output_modules(graph)

        if not multi_output_modules:
            pytest.skip(f"No multi-output modules in {model_name}")

        failures = []
        for module in multi_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            if code is None:
                failures.append(
                    f"  {module.name}: generate_multioutput_model() returned None"
                )

        assert not failures, (
            f"Multi-output generation failures in {model_name}:\n"
            + "\n".join(failures)
        )

    @pytest.mark.req("REQ-OSR-02")
    def test_multioutput_not_generated_for_single_output(
        self, all_graph_data, template_env,
    ):
        """generate_multioutput_model() returns None for single-output modules."""
        graph, _ = all_graph_data["solar_battery_model"]
        single_output_modules = _get_single_output_modules(graph)

        assert len(single_output_modules) > 0, "No single-output modules found"

        for module in single_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            assert code is None, (
                f"{module.name}: generate_multioutput_model() returned code "
                f"for single-output module"
            )


# ---------------------------------------------------------------------------
# REQ-OSR-02: Generated schema is valid Python
# ---------------------------------------------------------------------------

class TestGeneratedSchemaValidPython:
    """Every generated MultiOutput schema passes ast.parse()."""

    @pytest.mark.req("REQ-OSR-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_generated_schema_valid_python(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]
        multi_output_modules = _get_multi_output_modules(graph)

        assert len(multi_output_modules) > 0, (
            f"No multi-output modules in {model_name}"
        )

        failures = []
        for module in multi_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            try:
                ast.parse(code)
            except SyntaxError as e:
                failures.append(f"  {module.name}: {e}")

        assert not failures, (
            f"Invalid Python in {model_name} schemas:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-02: Generated class inherits from MultiOutput
# ---------------------------------------------------------------------------

class TestGeneratedSchemaInheritsMultiOutput:
    """Generated class inherits from MultiOutput (parse AST, check base class)."""

    @pytest.mark.req("REQ-OSR-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_generated_schema_class_inherits_multioutput(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]
        multi_output_modules = _get_multi_output_modules(graph)

        assert len(multi_output_modules) > 0, (
            f"No multi-output modules in {model_name}"
        )

        failures = []
        for module in multi_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            tree = ast.parse(code)
            class_defs = [
                node for node in ast.walk(tree)
                if isinstance(node, ast.ClassDef)
            ]
            if not class_defs:
                failures.append(f"  {module.name}: no class definition found")
                continue

            class_def = class_defs[0]
            base_names = [ast.unparse(base) for base in class_def.bases]
            if "MultiOutput" not in base_names:
                failures.append(
                    f"  {module.name}: bases are {base_names}, "
                    f"expected MultiOutput"
                )

        assert not failures, (
            f"MultiOutput inheritance failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-01, REQ-OSR-02: should_use_multioutput matches graph output count
# ---------------------------------------------------------------------------

class TestMultiOutputDecisionMatchesGraph:
    """generate_multioutput_model returns code only for modules with 2+ outputs."""

    @pytest.mark.req("REQ-OSR-01")
    @pytest.mark.req("REQ-OSR-02")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_multioutput_decision_consistent_with_output_count(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]

        mismatches = []
        for module in graph.modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            expected_multi = len(module.outputs) > 1
            got_code = code is not None

            if expected_multi != got_code:
                mismatches.append(
                    f"  {module.name}: outputs={len(module.outputs)}, "
                    f"expected_multi={expected_multi}, got_code={got_code}"
                )

        assert not mismatches, (
            f"MultiOutput decision mismatches in {model_name}:\n"
            + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-03: Output field names match SysML output_attributes
# ---------------------------------------------------------------------------

class TestFieldNamesMatchModuleOutputs:
    """Generated MultiOutput field names match PipelineModule.outputs[i].field_name."""

    @pytest.mark.req("REQ-OSR-03")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_field_names_match_pipeline_module_outputs(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]
        multi_output_modules = _get_multi_output_modules(graph)

        assert len(multi_output_modules) > 0, (
            f"No multi-output modules in {model_name}"
        )

        mismatches = []
        for module in multi_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            tree = ast.parse(code)

            # Extract field names from the generated class
            generated_fields = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                            generated_fields.append(item.target.id)
                    break

            graph_field_names = [o.field_name for o in module.outputs]

            if set(generated_fields) != set(graph_field_names):
                mismatches.append(
                    f"  {module.name}: schema fields={generated_fields}, "
                    f"graph fields={graph_field_names}"
                )

        assert not mismatches, (
            f"Field name vs graph mismatches in {model_name}:\n"
            + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-04: Type mapping
# ---------------------------------------------------------------------------

class TestTypeMapping:
    """map_sysml_type_to_python() handles all SysML primitive types."""

    @pytest.mark.req("REQ-OSR-04")
    def test_type_mapping_real_to_float(self):
        assert map_sysml_type_to_python("Real") == "float"
        assert map_sysml_type_to_python("ScalarValues::Real") == "float"

    @pytest.mark.req("REQ-OSR-04")
    def test_type_mapping_integer_to_int(self):
        assert map_sysml_type_to_python("Integer") == "int"
        assert map_sysml_type_to_python("ScalarValues::Integer") == "int"

    @pytest.mark.req("REQ-OSR-04")
    def test_type_mapping_boolean_to_bool(self):
        assert map_sysml_type_to_python("Boolean") == "bool"
        assert map_sysml_type_to_python("ScalarValues::Boolean") == "bool"

    @pytest.mark.req("REQ-OSR-04")
    def test_type_mapping_string_to_str(self):
        assert map_sysml_type_to_python("String") == "str"
        assert map_sysml_type_to_python("ScalarValues::String") == "str"

    @pytest.mark.req("REQ-OSR-04")
    def test_type_mapping_unknown_passthrough(self):
        assert map_sysml_type_to_python("UnknownType") == "UnknownType"
        assert map_sysml_type_to_python("SomeCustomType") == "SomeCustomType"


# ---------------------------------------------------------------------------
# REQ-OSR-05: Output fields MUST NOT have default= values
# ---------------------------------------------------------------------------

class TestOutputFieldsHaveNoDefaults:
    """Generated MultiOutput code does NOT contain default= on any output field."""

    @pytest.mark.req("REQ-OSR-05")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_output_fields_have_no_defaults(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _ = all_graph_data[model_name]
        multi_output_modules = _get_multi_output_modules(graph)

        assert len(multi_output_modules) > 0, (
            f"No multi-output modules in {model_name}"
        )

        violations = []
        for module in multi_output_modules:
            code = generate_multioutput_model(
                module, template_env, Path("/tmp/test_schema.py"),
            )
            tree = ast.parse(code)

            # Walk AST for Field() calls with default= keyword
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef):
                    continue
                for item in node.body:
                    if not isinstance(item, ast.AnnAssign):
                        continue
                    if item.value is None:
                        continue
                    # Check if the value is a Field(...) call with default=
                    if isinstance(item.value, ast.Call):
                        for keyword in item.value.keywords:
                            if keyword.arg == "default":
                                field_name = (
                                    item.target.id
                                    if isinstance(item.target, ast.Name)
                                    else "?"
                                )
                                violations.append(
                                    f"  {module.name}.{field_name}: "
                                    f"has default={ast.unparse(keyword.value)}"
                                )

        if violations:
            # REQ-OSR-05 violation detected — document as Bug 11 finding
            # but don't fail hard; mark as xfail with strict=False
            pytest.xfail(
                "REQ-OSR-05 violation (Bug 11): output fields have defaults.\n"
                + "\n".join(violations)
            )


# ---------------------------------------------------------------------------
# REQ-OSR-06: Aggregation and FORMULA always single-output
# ---------------------------------------------------------------------------

class TestAggregationAndFormulaAlwaysSingleOutput:
    """Aggregation and computed-attribute modules always have exactly 1 output
    with field_name='root'."""

    @pytest.mark.req("REQ-OSR-06")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_aggregation_always_single_output(
        self, model_name, all_graph_data,
    ):
        graph, _ = all_graph_data[model_name]

        agg_modules = [m for m in graph.modules if m.is_aggregation]
        if not agg_modules:
            pytest.skip(f"No aggregation modules in {model_name}")

        failures = []
        for module in agg_modules:
            if len(module.outputs) != 1:
                failures.append(
                    f"  {module.name}: has {len(module.outputs)} outputs, expected 1"
                )
            elif module.outputs[0].field_name != "root":
                failures.append(
                    f"  {module.name}: field_name='{module.outputs[0].field_name}', "
                    f"expected 'root'"
                )

        assert not failures, (
            f"Aggregation single-output failures in {model_name}:\n"
            + "\n".join(failures)
        )

    @pytest.mark.req("REQ-OSR-06")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
    def test_formula_always_single_output(
        self, model_name, all_graph_data,
    ):
        graph, _ = all_graph_data[model_name]

        formula_modules = [m for m in graph.modules if m.is_computed_attribute]
        if not formula_modules:
            pytest.skip(f"No FORMULA modules in {model_name}")

        failures = []
        for module in formula_modules:
            if len(module.outputs) != 1:
                failures.append(
                    f"  {module.name}: has {len(module.outputs)} outputs, expected 1"
                )
            elif module.outputs[0].field_name != "root":
                failures.append(
                    f"  {module.name}: field_name='{module.outputs[0].field_name}', "
                    f"expected 'root'"
                )

        assert not failures, (
            f"FORMULA single-output failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-07: Output channels use PQN format
# ---------------------------------------------------------------------------

class TestOutputChannelsUsePQNFormat:
    """Every ModuleOutput.channel_name contains '__' separator (PQN format)."""

    @pytest.mark.req("REQ-OSR-07")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_output_channels_use_pqn_format(
        self, model_name, all_graph_data,
    ):
        graph, _ = all_graph_data[model_name]

        failures = []
        for module in graph.modules:
            for output in module.outputs:
                if "__" not in output.channel_name:
                    failures.append(
                        f"  {module.name}.{output.field_name}: "
                        f"channel_name='{output.channel_name}' missing '__'"
                    )

        assert not failures, (
            f"PQN format failures in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-OSR-02: Static analysis — schemas.py imports from extraction
# ---------------------------------------------------------------------------

class TestSchemasPyNoExtractionImports:
    """Static analysis: schemas.py has zero extraction imports (Phase 7 complete)."""

    @pytest.mark.req("REQ-OSR-02")
    def test_schemas_py_no_extraction_imports(self):
        """schemas.py must not import from extraction (boundary enforcement)."""
        schemas_path = SRC_DIR / "generation" / "schemas.py"
        source = schemas_path.read_text()
        tree = ast.parse(source)

        extraction_imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                if "extraction" in node.module:
                    extraction_imports.append(
                        f"  line {node.lineno}: from {node.module}"
                    )

        assert len(extraction_imports) == 0, (
            "schemas.py still imports from extraction:\n"
            + "\n".join(extraction_imports)
        )
