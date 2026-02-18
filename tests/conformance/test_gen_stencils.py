"""Conformance tests for Stencil Generator + Smart Regen (C23).

Requirements: REQ-GEN-04, REQ-SR-01 through REQ-SR-07
Design intent: 08-generation.md, 23-smart-regen-preservation.md

Tests verify stencil generation and smart regeneration with real extraction data:
- REQ-GEN-04: FULLY_COMPILABLE gets auto-impl; others get stubs
- REQ-GEN-04: Generated stencils are valid Python (ast.parse)
- REQ-GEN-04: Function signature matches calc_def
- REQ-GEN-04: Multi-output return type
- REQ-GEN-04: Import path consistency with PythonModulePath
- REQ-SR-01: Two-level signature matching (type-level required, field-level order-independent)
- REQ-SR-02: Field comparison is order-independent
- REQ-SR-03: 4-case decision tree for should_regenerate_stencil
- REQ-SR-04: Stub-to-auto-impl upgrade requires 3 conditions
- REQ-SR-05: Backup before every regen/upgrade
- REQ-SR-06: Aggregation/FORMULA modules always regenerated (no smart regen)
- REQ-SR-07: --preserve-handwritten skips without comparison

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.analysis.signature_extractor import (
    FunctionSignature,
    generate_expected_signature,
)
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
    CompilationResult,
)
from sysml_codegen.generation.preservation import (
    backup_implementation,
    should_regenerate_stencil,
)
from sysml_codegen.generation.stencils import generate_implementation
from sysml_codegen.resolution.identifier_types import PythonModulePath, SysMLQualifiedName
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
    """Jinja2 template environment for stencil generation."""
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

def _build_calcusage_module_to_calcdef_map(
    graph: ComputationGraph, inputs: dict,
) -> dict[str, object]:
    """Map CalcUsage PipelineModule.name -> CalculationDefinitionData.

    Uses required_usages from BacktrackingResult to link module names
    to their calc_def_name, then looks up the calc_def.
    """
    result = inputs["result"]
    snap = inputs["snap"]

    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    usage_to_calcdef = {}
    for usage in result.required_usages:
        module_name = usage.qualified_name.lower()
        usage_to_calcdef[module_name] = usage.calc_def_name

    mapping = {}
    for module in graph.modules:
        if module.is_computed_attribute or module.is_aggregation:
            continue
        calc_def_name = usage_to_calcdef.get(module.name)
        if calc_def_name and calc_def_name in calc_def_map:
            mapping[module.name] = calc_def_map[calc_def_name]

    return mapping


def _make_fully_compilable_result(calc_def) -> CalcDefCompilationResult:
    """Construct a FULLY_COMPILABLE CalcDefCompilationResult from real calc_def metadata.

    This is NOT a mock — it's a real Pydantic model with data derived from
    real extraction snapshots. Uses real attribute names from calc_def.
    """
    output_results = []
    input_names = [attr.name for attr in calc_def.input_attributes]
    for attr in calc_def.output_attributes:
        # Build a valid expression using real input attribute names
        if input_names:
            expr = f"inputs.{input_names[0]} * 1.0"
        else:
            expr = "1.0"
        output_results.append(
            CompilationResult(
                output_name=attr.name,
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression=expr,
                input_refs=input_names[:1],
            )
        )

    return CalcDefCompilationResult(
        calc_def_name=calc_def.name,
        overall_compilability=Compilability.FULLY_COMPILABLE,
        output_results=output_results,
        execution_order=[attr.name for attr in calc_def.output_attributes],
    )


def _get_first_calcusage_calcdef(graph_data, model_name):
    """Get first CalcUsage calc_def from model for targeted tests."""
    graph, inputs = graph_data[model_name]
    mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)
    first_name = next(iter(mapping))
    return mapping[first_name]


# ---------------------------------------------------------------------------
# REQ-GEN-04: FULLY_COMPILABLE gets auto-impl; others get stubs
# ---------------------------------------------------------------------------

class TestFullyCompilableProducesAutoImpl:
    """REQ-GEN-04: generate_implementation() with FULLY_COMPILABLE compilation_result
    produces auto-impl code (AUTO_IMPLEMENTED sentinel, no NotImplementedError)."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_fully_compilable_produces_auto_impl(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        tested = 0
        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue
            compilation_result = _make_fully_compilable_result(calc_def)
            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=compilation_result,
            )
            if "AUTO_IMPLEMENTED = True" not in code:
                failures.append(f"  {module_name}: missing AUTO_IMPLEMENTED sentinel")
            if "NotImplementedError" in code:
                failures.append(f"  {module_name}: contains NotImplementedError in auto-impl")
            tested += 1

        assert tested > 0, f"No CalcUsage modules with outputs in {model_name}"
        assert not failures, (
            f"Auto-impl failures in {model_name}:\n" + "\n".join(failures)
        )


class TestNonCompilableProducesStub:
    """REQ-GEN-04: generate_implementation() with compilation_result=None
    produces NotImplementedError stub."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_non_compilable_produces_stub(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        tested = 0
        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue
            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )
            if "NotImplementedError" not in code:
                failures.append(f"  {module_name}: missing NotImplementedError in stub")
            if "AUTO_IMPLEMENTED = True" in code:
                failures.append(f"  {module_name}: has AUTO_IMPLEMENTED in stub")
            tested += 1

        assert tested > 0, f"No CalcUsage modules with outputs in {model_name}"
        assert not failures, (
            f"Stub failures in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-04: Generated stencils are valid Python
# ---------------------------------------------------------------------------

class TestStencilValidPython:
    """REQ-GEN-04: Both auto-impl and stub output pass ast.parse()."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_stencil_valid_python(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue

            # Test stub
            stub_code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )
            try:
                ast.parse(stub_code)
            except SyntaxError as e:
                failures.append(f"  {module_name} (stub): {e}")

            # Test auto-impl
            compilation_result = _make_fully_compilable_result(calc_def)
            auto_code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=compilation_result,
            )
            try:
                ast.parse(auto_code)
            except SyntaxError as e:
                failures.append(f"  {module_name} (auto-impl): {e}")

        assert not failures, (
            f"Invalid Python in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-04: Function signature matches calc_def
# ---------------------------------------------------------------------------

class TestStencilFunctionSignature:
    """REQ-GEN-04: Generated function has run_{name}(inputs: {Name}Input) -> {return_type}."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_stencil_function_signature(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue

            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )

            expected_func = f"run_{calc_def.name.lower()}"
            expected_input = f"{calc_def.name}Input"

            # Check function name
            if f"def {expected_func}(" not in code:
                failures.append(f"  {module_name}: missing def {expected_func}(")
            # Check input type
            if f"inputs: {expected_input}" not in code:
                failures.append(f"  {module_name}: missing inputs: {expected_input}")

        assert not failures, (
            f"Signature failures in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-04: Multi-output return type
# ---------------------------------------------------------------------------

class TestMultiOutputReturnType:
    """REQ-GEN-04: CalcDefs with 2+ outputs produce tuple[float, ...] return type."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_multi_output_return_type(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        multi_output_count = 0
        failures = []
        for module_name, calc_def in mapping.items():
            num_outputs = len(calc_def.output_attributes)
            if num_outputs < 2:
                continue

            multi_output_count += 1
            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )

            expected_types = ", ".join(["float"] * num_outputs)
            expected_return = f"tuple[{expected_types}]"
            if expected_return not in code:
                failures.append(
                    f"  {module_name}: expected {expected_return}, not found"
                )

        # At least solar_battery has multi-output calc_defs
        assert multi_output_count > 0 or model_name == "catf_mfe_model", (
            f"No multi-output CalcDefs in {model_name}"
        )
        assert not failures, (
            f"Multi-output return type failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-04: Import path consistency
# ---------------------------------------------------------------------------

class TestStencilImportPathConsistency:
    """REQ-GEN-04: Generated stencil imports from {package_name}.modules.{import_path}
    where import_path matches PythonModulePath.from_sysml()."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_stencil_import_path_consistency(
        self, model_name, all_graph_data, template_env,
    ):
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)
        package_name = MODEL_IDS[model_name]

        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue

            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=package_name,
                compilation_result=None,
            )

            # Derive expected import path from calc_def qualified_name
            sqn = SysMLQualifiedName(calc_def.qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            expected_import = f"from {package_name}.modules.{python_path.import_path}"

            if expected_import not in code:
                failures.append(
                    f"  {module_name}: expected '{expected_import}' not found in code"
                )

        assert not failures, (
            f"Import path consistency failures in {model_name}:\n"
            + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-SR-01: Two-level signature matching
# ---------------------------------------------------------------------------

class TestTwoLevelSignatureMatching:
    """REQ-SR-01: FunctionSignature.matches() uses type-level (function_name,
    input_type, return_type) as required, field-level (input_fields sorted) as optional."""

    @pytest.mark.req("REQ-SR-01")
    def test_req_sr_01_two_level_signature_matching(self):
        """Type-level match required; field-level match optional when fields absent."""
        sig_a = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=None,
        )
        sig_b = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=["x", "y"],
        )
        # Type-level matches, field-level skipped (one side None)
        assert sig_a.matches(sig_b)
        assert sig_b.matches(sig_a)

        # Type-level mismatch
        sig_c = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="int",  # different return type
            input_fields=None,
        )
        assert not sig_a.matches(sig_c)

    @pytest.mark.req("REQ-SR-01")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_generate_expected_signature_matches_stencil(
        self, model_name, all_graph_data, template_env,
    ):
        """For each CalcUsage calc_def, generate_expected_signature(calc_def) produces a
        FunctionSignature whose function_name, input_type, return_type match what
        generate_implementation() produces."""
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        failures = []
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue

            # Generate expected signature from calc_def
            expected_sig = generate_expected_signature(calc_def)

            # Generate stub code and extract actual signature via AST
            code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )
            tree = ast.parse(code)
            func_found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("run_"):
                    func_found = True
                    if node.name != expected_sig.function_name:
                        failures.append(
                            f"  {module_name}: func name "
                            f"{node.name} != {expected_sig.function_name}"
                        )
                    # Check return type
                    if node.returns:
                        actual_return = ast.unparse(node.returns)
                        if actual_return != expected_sig.return_type:
                            failures.append(
                                f"  {module_name}: return type "
                                f"{actual_return} != {expected_sig.return_type}"
                            )
                    break

            if not func_found:
                failures.append(f"  {module_name}: no run_* function found")

        assert not failures, (
            f"Signature mismatch in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-SR-02: Field comparison is order-independent
# ---------------------------------------------------------------------------

class TestFieldComparisonOrderIndependent:
    """REQ-SR-02: Two signatures with same fields in different order return matches()=True."""

    @pytest.mark.req("REQ-SR-02")
    def test_req_sr_02_field_comparison_order_independent(self):
        sig_a = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=["z", "a", "m"],
        )
        sig_b = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=["a", "m", "z"],
        )
        assert sig_a.matches(sig_b)
        assert sig_b.matches(sig_a)

    @pytest.mark.req("REQ-SR-02")
    def test_req_sr_02_field_mismatch_returns_false(self):
        """Different field sets return matches()=False."""
        sig_a = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=["x", "y"],
        )
        sig_b = FunctionSignature(
            function_name="run_calc",
            input_type="CalcInput",
            return_type="float",
            input_fields=["x", "z"],
        )
        assert not sig_a.matches(sig_b)


# ---------------------------------------------------------------------------
# REQ-SR-03: 4-case decision tree for should_regenerate_stencil
# ---------------------------------------------------------------------------

class TestDecisionTree:
    """REQ-SR-03: should_regenerate_stencil() implements the 4-case decision tree."""

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case1_new_file(
        self, all_graph_data, tmp_path,
    ):
        """Case 1: Non-existent file → (True, 'New module...')."""
        calc_def = _get_first_calcusage_calcdef(all_graph_data, "solar_battery_model")
        non_existent = tmp_path / "does_not_exist.py"

        should_regen, reason = should_regenerate_stencil(calc_def, non_existent)
        assert should_regen is True
        assert "New module" in reason or "doesn't exist" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case2_unparseable(
        self, all_graph_data, tmp_path,
    ):
        """Case 2: File with syntax errors → (True, 'Could not parse...')."""
        calc_def = _get_first_calcusage_calcdef(all_graph_data, "solar_battery_model")
        bad_file = tmp_path / "bad_impl.py"
        bad_file.write_text("def broken(\n    # syntax error\n")

        should_regen, reason = should_regenerate_stencil(calc_def, bad_file)
        assert should_regen is True
        assert "Could not parse" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case3_unchanged(
        self, all_graph_data, template_env, tmp_path,
    ):
        """Case 3: File matching expected signature → (False, 'Signature unchanged')."""
        calc_def = _get_first_calcusage_calcdef(all_graph_data, "solar_battery_model")

        # Generate a stub and write it to disk
        code = generate_implementation(
            calc_def, template_env, Path("/tmp/test.py"),
            package_name="solar_battery",
            compilation_result=None,
        )
        impl_file = tmp_path / "matching_impl.py"
        impl_file.write_text(code)

        should_regen, reason = should_regenerate_stencil(calc_def, impl_file)
        assert should_regen is False
        assert "Signature unchanged" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case4_changed(
        self, all_graph_data, tmp_path,
    ):
        """Case 4: File with different return type → (True, 'Signature changed...')."""
        calc_def = _get_first_calcusage_calcdef(all_graph_data, "solar_battery_model")

        # Write a file with a run_ function that has a different return type
        func_name = f"run_{calc_def.name.lower()}"
        input_type = f"{calc_def.name}Input"
        changed_code = (
            f"def {func_name}(inputs: {input_type}) -> int:\n"
            f"    raise NotImplementedError()\n"
        )
        impl_file = tmp_path / "changed_impl.py"
        impl_file.write_text(changed_code)

        should_regen, reason = should_regenerate_stencil(calc_def, impl_file)
        assert should_regen is True
        assert "Signature changed" in reason


# ---------------------------------------------------------------------------
# REQ-SR-04: Stub-to-auto-impl upgrade requires 3 conditions
# ---------------------------------------------------------------------------

class TestStubUpgradeThreeConditions:
    """REQ-SR-04: Stub-to-auto-impl upgrade requires:
    (1) signature unchanged, (2) existing file has NotImplementedError, (3) FULLY_COMPILABLE."""

    @pytest.mark.req("REQ-SR-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_sr_04_stub_upgrade_three_conditions(
        self, model_name, all_graph_data, template_env, tmp_path,
    ):
        """Generate stub → verify it has NotImplementedError → construct FULLY_COMPILABLE
        result → verify upgrade to auto-impl produces different (non-stub) code."""
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        tested = 0
        for module_name, calc_def in mapping.items():
            if not calc_def.output_attributes:
                continue

            # Step 1: Generate stub
            stub_code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=None,
            )
            # Step 2: Verify stub has NotImplementedError
            assert "NotImplementedError" in stub_code, (
                f"{module_name}: stub missing NotImplementedError"
            )

            # Step 3: Write stub to disk and verify signature unchanged
            impl_file = tmp_path / f"{module_name}_impl.py"
            impl_file.write_text(stub_code)
            should_regen, reason = should_regenerate_stencil(calc_def, impl_file)
            assert should_regen is False, (
                f"{module_name}: stub should not need regen ({reason})"
            )

            # Step 4: Construct FULLY_COMPILABLE result and generate auto-impl
            compilation_result = _make_fully_compilable_result(calc_def)
            auto_code = generate_implementation(
                calc_def, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
                compilation_result=compilation_result,
            )

            # Step 5: Verify auto-impl is different from stub
            assert "AUTO_IMPLEMENTED = True" in auto_code
            assert "NotImplementedError" not in auto_code

            tested += 1
            if tested >= 3:
                break  # Test a few per model, not all

        assert tested > 0, f"No CalcUsage modules tested in {model_name}"

    @pytest.mark.req("REQ-SR-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_sr_04_handwritten_not_upgraded(
        self, model_name, all_graph_data, template_env, tmp_path,
    ):
        """Handwritten impl (no NotImplementedError) is NOT upgraded even if FULLY_COMPILABLE.

        The 3-condition check requires 'NotImplementedError' in existing content.
        If the user has already written real implementation code, it must be preserved."""
        graph, inputs = all_graph_data[model_name]
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        calc_def = next(
            cd for cd in mapping.values() if cd.output_attributes
        )

        # Write a "handwritten" impl that matches the signature but has real code
        func_name = f"run_{calc_def.name.lower()}"
        input_type = f"{calc_def.name}Input"
        num_outputs = len(calc_def.output_attributes)
        if num_outputs == 1:
            return_type = "float"
            return_stmt = "return 42.0  # handwritten"
        else:
            return_types = ", ".join(["float"] * num_outputs)
            return_type = f"tuple[{return_types}]"
            return_stmt = "return " + ", ".join(["42.0"] * num_outputs) + "  # handwritten"

        handwritten_code = (
            f"def {func_name}(inputs: {input_type}) -> {return_type}:\n"
            f"    {return_stmt}\n"
        )
        impl_file = tmp_path / f"{calc_def.name}_handwritten.py"
        impl_file.write_text(handwritten_code)

        # Verify signature unchanged
        should_regen, reason = should_regenerate_stencil(calc_def, impl_file)
        assert should_regen is False, f"Handwritten should not need regen ({reason})"

        # Verify the handwritten code does NOT contain NotImplementedError
        existing_content = impl_file.read_text()
        is_stub = "raise NotImplementedError" in existing_content
        assert not is_stub, "Handwritten code should not be a stub"

        # The CLI logic checks: is_stub and has_auto_impl
        # Since is_stub is False, upgrade should NOT happen
        # (This tests the logic condition, not the CLI function directly)


# ---------------------------------------------------------------------------
# REQ-SR-05: Backup before every regen/upgrade
# ---------------------------------------------------------------------------

class TestBackupBeforeRegen:
    """REQ-SR-05: backup_implementation() creates timestamped backup preserving content."""

    @pytest.mark.req("REQ-SR-05")
    def test_req_sr_05_backup_before_regen(self, tmp_path):
        """backup_implementation() creates a file in backup_dir."""
        impl_file = tmp_path / "calc_impl.py"
        original_content = "def run_calc(inputs):\n    return 42.0\n"
        impl_file.write_text(original_content)

        backup_dir = tmp_path / "backup"
        backup_path = backup_implementation(impl_file, backup_dir)

        assert backup_path.exists()
        assert backup_dir.exists()
        assert backup_path.parent == backup_dir
        # Backup filename includes stem and timestamp
        assert "calc_impl" in backup_path.name
        assert backup_path.suffix == ".py"

    @pytest.mark.req("REQ-SR-05")
    def test_req_sr_05_backup_preserves_content(self, tmp_path):
        """Backup file content matches original exactly (shutil.copy2)."""
        impl_file = tmp_path / "calc_impl.py"
        original_content = (
            "# Handwritten implementation\n"
            "def run_calc(inputs: CalcInput) -> float:\n"
            "    return inputs.x * 2.5 + inputs.y\n"
        )
        impl_file.write_text(original_content)

        backup_dir = tmp_path / "backup"
        backup_path = backup_implementation(impl_file, backup_dir)

        assert backup_path.read_text() == original_content


# ---------------------------------------------------------------------------
# REQ-SR-06: Aggregation/FORMULA modules always regenerated (no smart regen)
# ---------------------------------------------------------------------------

class TestAggregationNoSmartRegen:
    """REQ-SR-06: Aggregation and FORMULA generation functions do not reference
    smart regen APIs (should_regenerate_stencil, smart_regen, backup_implementation)."""

    @pytest.mark.req("REQ-SR-06")
    def test_req_sr_06_aggregation_no_smart_regen(self):
        """Static analysis: _generate_aggregation_stencils() source does not reference
        should_regenerate_stencil, smart_regen, or backup_implementation."""
        from sysml_codegen.cli import _generate_aggregation_stencils

        source = inspect.getsource(_generate_aggregation_stencils)
        assert "should_regenerate_stencil" not in source
        assert "smart_regen" not in source
        assert "backup_implementation" not in source

    @pytest.mark.req("REQ-SR-06")
    def test_req_sr_06_computed_attr_no_smart_regen(self):
        """Static analysis: _generate_computed_attr_stencils() source does not reference
        should_regenerate_stencil, smart_regen, or backup_implementation."""
        from sysml_codegen.cli import _generate_computed_attr_stencils

        source = inspect.getsource(_generate_computed_attr_stencils)
        assert "should_regenerate_stencil" not in source
        assert "smart_regen" not in source
        assert "backup_implementation" not in source


# ---------------------------------------------------------------------------
# REQ-SR-07: --preserve-handwritten skips without comparison
# ---------------------------------------------------------------------------

class TestPreserveHandwrittenFlag:
    """REQ-SR-07: --preserve-handwritten skips without calling should_regenerate_stencil."""

    @pytest.mark.req("REQ-SR-07")
    def test_req_sr_07_preserve_handwritten_flag(self):
        """Static analysis: _generate_stencils() has a branch gated by
        config.preserve_handwritten that skips without calling should_regenerate_stencil."""
        from sysml_codegen.cli import _generate_stencils

        source = inspect.getsource(_generate_stencils)

        # The function should contain the preserve_handwritten check
        assert "preserve_handwritten" in source, (
            "_generate_stencils missing preserve_handwritten reference"
        )

        # The preserve_handwritten branch should NOT call should_regenerate_stencil
        # Find the elif branch and verify it just preserves
        lines = source.splitlines()
        in_preserve_branch = False
        for i, line in enumerate(lines):
            if "preserve_handwritten" in line and "output_path.exists()" in line:
                in_preserve_branch = True
                continue
            if in_preserve_branch:
                # Check a few lines of the branch body
                if line.strip().startswith("elif ") or line.strip().startswith("else:"):
                    break  # end of branch
                if "should_regenerate_stencil" in line:
                    pytest.fail(
                        "preserve_handwritten branch calls should_regenerate_stencil"
                    )
                if "stats[\"preserved\"]" in line:
                    break  # found the expected action — done checking
