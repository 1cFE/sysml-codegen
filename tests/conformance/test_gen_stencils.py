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

from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.preservation import (
    FunctionSignature,
    backup_implementation,
    should_regenerate_stencil,
)
from sysml_codegen.generation.stencils import generate_implementation
from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
from sysml_codegen.resolution.models import ComputationGraph, PipelineModule
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
        graph, inputs = build_full_graph_from_snapshot(snapshot_fixture(model_name))
        data[model_name] = (graph, inputs)
    return data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_calcusage_modules(graph: ComputationGraph) -> list[PipelineModule]:
    """Get CalcUsage PipelineModules (not FORMULA or aggregation)."""
    return [
        m for m in graph.modules
        if not m.is_computed_attribute and not m.is_aggregation
    ]


def _make_test_auto_impl_context(module: PipelineModule) -> dict:
    """Create a test auto_impl_context from a PipelineModule's existing fields.

    Uses real input/output names from the module to build a synthetic
    but structurally valid auto_impl_context dict.
    """
    input_names = [inp.param_name for inp in module.inputs]
    if input_names:
        expr = f"inputs.{input_names[0]} * 1.0"
    else:
        expr = "1.0"

    output_names = []
    for out in module.outputs:
        name = out.field_name if out.field_name != "root" else out.channel_name.split("__")[-1]
        output_names.append(name)

    output_expressions = [
        {"name": name, "expression": expr}
        for name in output_names
    ]

    return {
        "execution_steps": [],
        "output_expressions": output_expressions,
        "output_count": len(output_expressions),
        "single_output_expression": expr if len(output_expressions) == 1 else None,
    }


def _get_first_calcusage_module(graph_data, model_name) -> PipelineModule:
    """Get first CalcUsage PipelineModule from model for targeted tests."""
    graph, _inputs = graph_data[model_name]
    modules = _get_calcusage_modules(graph)
    return modules[0]


# ---------------------------------------------------------------------------
# REQ-GEN-04: FULLY_COMPILABLE gets auto-impl; others get stubs
# ---------------------------------------------------------------------------

class TestFullyCompilableProducesAutoImpl:
    """REQ-GEN-04: generate_implementation() with auto_impl_context populated
    produces auto-impl code (AUTO_IMPLEMENTED sentinel, no NotImplementedError)."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_fully_compilable_produces_auto_impl(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        tested = 0
        failures = []
        for module in modules:
            if not module.outputs:
                continue
            # Create a version with auto_impl_context to force auto-impl path
            auto_module = module.model_copy(update={
                "auto_impl_context": _make_test_auto_impl_context(module),
            })
            code = generate_implementation(
                auto_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            if "AUTO_IMPLEMENTED = True" not in code:
                failures.append(f"  {module.name}: missing AUTO_IMPLEMENTED sentinel")
            if "NotImplementedError" in code:
                failures.append(f"  {module.name}: contains NotImplementedError in auto-impl")
            tested += 1

        assert tested > 0, f"No CalcUsage modules with outputs in {model_name}"
        assert not failures, (
            f"Auto-impl failures in {model_name}:\n" + "\n".join(failures)
        )


class TestNonCompilableProducesStub:
    """REQ-GEN-04: generate_implementation() with auto_impl_context=None
    produces NotImplementedError stub."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_non_compilable_produces_stub(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        tested = 0
        failures = []
        for module in modules:
            if not module.outputs:
                continue
            # Ensure auto_impl_context is None to get stub path
            stub_module = module.model_copy(update={"auto_impl_context": None})
            code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            if "NotImplementedError" not in code:
                failures.append(f"  {module.name}: missing NotImplementedError in stub")
            if "AUTO_IMPLEMENTED = True" in code:
                failures.append(f"  {module.name}: has AUTO_IMPLEMENTED in stub")
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
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        failures = []
        for module in modules:
            if not module.outputs:
                continue

            # Test stub
            stub_module = module.model_copy(update={"auto_impl_context": None})
            stub_code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            try:
                ast.parse(stub_code)
            except SyntaxError as e:
                failures.append(f"  {module.name} (stub): {e}")

            # Test auto-impl
            auto_module = module.model_copy(update={
                "auto_impl_context": _make_test_auto_impl_context(module),
            })
            auto_code = generate_implementation(
                auto_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            try:
                ast.parse(auto_code)
            except SyntaxError as e:
                failures.append(f"  {module.name} (auto-impl): {e}")

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
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        failures = []
        for module in modules:
            if not module.outputs:
                continue

            stub_module = module.model_copy(update={"auto_impl_context": None})
            code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )

            expected_func = f"run_{module.calc_def_name.lower()}"
            expected_input = f"{module.calc_def_name}Input"

            if f"def {expected_func}(" not in code:
                failures.append(f"  {module.name}: missing def {expected_func}(")
            if f"inputs: {expected_input}" not in code:
                failures.append(f"  {module.name}: missing inputs: {expected_input}")

        assert not failures, (
            f"Signature failures in {model_name}:\n" + "\n".join(failures)
        )


# ---------------------------------------------------------------------------
# REQ-GEN-04: Multi-output return type
# ---------------------------------------------------------------------------

class TestMultiOutputReturnType:
    """REQ-GEN-04: Modules with 2+ outputs produce tuple[float, ...] return type."""

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_gen_04_multi_output_return_type(
        self, model_name, all_graph_data, template_env,
    ):
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        multi_output_count = 0
        failures = []
        for module in modules:
            num_outputs = len(module.outputs)
            if num_outputs < 2:
                continue

            multi_output_count += 1
            stub_module = module.model_copy(update={"auto_impl_context": None})
            code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )

            expected_types = ", ".join(["float"] * num_outputs)
            expected_return = f"tuple[{expected_types}]"
            if expected_return not in code:
                failures.append(
                    f"  {module.name}: expected {expected_return}, not found"
                )

        # At least solar_battery has multi-output modules
        assert multi_output_count > 0 or model_name == "catf_mfe_model", (
            f"No multi-output modules in {model_name}"
        )
        assert not failures, (
            f"Multi-output return type failures in {model_name}:\n"
            + "\n".join(failures)
        )

    @pytest.mark.req("REQ-GEN-04")
    def test_multi_output_return_type_literal(self, all_graph_data, template_env):
        """A known 5-output module renders the exact literal tuple return type.

        The parametrized test above builds its expected string as
        f"tuple[{', '.join(['float']*n)}]" -- self-shaped on n, so it can't catch a wrong
        arity. Pin one named module's full return string as a literal.
        """
        graph, _inputs = all_graph_data["solar_battery_model"]
        module = next(
            m for m in _get_calcusage_modules(graph)
            if m.name
            == "solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model"
        )
        # provenance: pv_module cost_model has 5 outputs (material_cost, fab_cost,
        #   install_cost, total_cost, idiot_index) -- library.sysml PVModuleCostCalc.
        stub_module = module.model_copy(update={"auto_impl_context": None})
        code = generate_implementation(
            stub_module, template_env, Path("/tmp/test.py"), package_name="solar_battery",
        )
        assert "tuple[float, float, float, float, float]" in code, (
            "pv_module cost_model should render a 5-float tuple return type"
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
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)
        package_name = MODEL_IDS[model_name]

        failures = []
        for module in modules:
            if not module.outputs:
                continue

            stub_module = module.model_copy(update={"auto_impl_context": None})
            code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=package_name,
            )

            # Derive expected import path from module's calc_def_qualified_name
            sqn = SysMLQualifiedName(module.calc_def_qualified_name)
            python_path = PythonModulePath.from_sysml(sqn)
            expected_import = f"from {package_name}.modules.{python_path.import_path}"

            if expected_import not in code:
                failures.append(
                    f"  {module.name}: expected '{expected_import}' not found in code"
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
        """For each CalcUsage PipelineModule, the expected signature derived from module
        fields matches what generate_implementation() produces."""
        from sysml_codegen.generation.preservation import _generate_expected_signature_from_module

        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        failures = []
        for module in modules:
            if not module.outputs:
                continue

            # Generate expected signature from PipelineModule
            expected_sig = _generate_expected_signature_from_module(module)

            # Generate stub code and extract actual signature via AST
            stub_module = module.model_copy(update={"auto_impl_context": None})
            code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            tree = ast.parse(code)
            func_found = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith("run_"):
                    func_found = True
                    if node.name != expected_sig.function_name:
                        failures.append(
                            f"  {module.name}: func name "
                            f"{node.name} != {expected_sig.function_name}"
                        )
                    # Check return type
                    if node.returns:
                        actual_return = ast.unparse(node.returns)
                        if actual_return != expected_sig.return_type:
                            failures.append(
                                f"  {module.name}: return type "
                                f"{actual_return} != {expected_sig.return_type}"
                            )
                    break

            if not func_found:
                failures.append(f"  {module.name}: no run_* function found")

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
        module = _get_first_calcusage_module(all_graph_data, "solar_battery_model")
        non_existent = tmp_path / "does_not_exist.py"

        should_regen, reason = should_regenerate_stencil(module, non_existent)
        assert should_regen is True
        assert "New module" in reason or "doesn't exist" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case2_unparseable(
        self, all_graph_data, tmp_path,
    ):
        """Case 2 (D3-14, Item 5): a NON-EMPTY file that fails to parse is a
        *transient* parse error — preserve the (maybe-valid handwritten) impl,
        do NOT stub over it. Was (True, 'Could not parse'); now preserved."""
        module = _get_first_calcusage_module(all_graph_data, "solar_battery_model")
        bad_file = tmp_path / "bad_impl.py"
        bad_file.write_text("def broken(\n    # syntax error\n")

        should_regen, reason = should_regenerate_stencil(module, bad_file)
        assert should_regen is False
        assert "Preserved" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_empty_impl_regenerates(self, all_graph_data, tmp_path):
        """D3-14 boundary: a genuinely-EMPTY impl has nothing to preserve →
        regenerate (distinct from the transient non-empty parse error)."""
        module = _get_first_calcusage_module(all_graph_data, "solar_battery_model")
        empty_file = tmp_path / "empty_impl.py"
        empty_file.write_text("   \n")

        should_regen, reason = should_regenerate_stencil(module, empty_file)
        assert should_regen is True
        assert "Empty" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case3_unchanged(
        self, all_graph_data, template_env, tmp_path,
    ):
        """Case 3: File matching expected signature → (False, 'Signature unchanged')."""
        module = _get_first_calcusage_module(all_graph_data, "solar_battery_model")

        # Generate a stub and write it to disk
        stub_module = module.model_copy(update={"auto_impl_context": None})
        code = generate_implementation(
            stub_module, template_env, Path("/tmp/test.py"),
            package_name="solar_battery",
        )
        impl_file = tmp_path / "matching_impl.py"
        impl_file.write_text(code)

        should_regen, reason = should_regenerate_stencil(module, impl_file)
        assert should_regen is False
        assert "Signature unchanged" in reason

    @pytest.mark.req("REQ-SR-03")
    def test_req_sr_03_decision_tree_case4_changed(
        self, all_graph_data, tmp_path,
    ):
        """Case 4: File with different return type → (True, 'Signature changed...')."""
        module = _get_first_calcusage_module(all_graph_data, "solar_battery_model")

        # Write a file with a run_ function that has a different return type
        func_name = f"run_{module.calc_def_name.lower()}"
        input_type = f"{module.calc_def_name}Input"
        changed_code = (
            f"def {func_name}(inputs: {input_type}) -> int:\n"
            f"    raise NotImplementedError()\n"
        )
        impl_file = tmp_path / "changed_impl.py"
        impl_file.write_text(changed_code)

        should_regen, reason = should_regenerate_stencil(module, impl_file)
        assert should_regen is True
        assert "Signature changed" in reason


# ---------------------------------------------------------------------------
# REQ-SR-04: Stub-to-auto-impl upgrade requires 3 conditions
# ---------------------------------------------------------------------------

class TestStubUpgradeThreeConditions:
    """REQ-SR-04: Stub-to-auto-impl upgrade requires:
    (1) signature unchanged, (2) existing file has NotImplementedError, (3) auto_impl_context."""

    @pytest.mark.req("REQ-SR-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                             ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
    def test_req_sr_04_stub_upgrade_three_conditions(
        self, model_name, all_graph_data, template_env, tmp_path,
    ):
        """Generate stub → verify NotImplementedError → add auto_impl_context →
        verify upgrade to auto-impl produces different (non-stub) code."""
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        tested = 0
        for module in modules:
            if not module.outputs:
                continue

            # Step 1: Generate stub
            stub_module = module.model_copy(update={"auto_impl_context": None})
            stub_code = generate_implementation(
                stub_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
            )
            # Step 2: Verify stub has NotImplementedError
            assert "NotImplementedError" in stub_code, (
                f"{module.name}: stub missing NotImplementedError"
            )

            # Step 3: Write stub to disk and verify signature unchanged
            impl_file = tmp_path / f"{module.name}_impl.py"
            impl_file.write_text(stub_code)
            should_regen, reason = should_regenerate_stencil(module, impl_file)
            assert should_regen is False, (
                f"{module.name}: stub should not need regen ({reason})"
            )

            # Step 4: Add auto_impl_context and generate auto-impl
            auto_module = module.model_copy(update={
                "auto_impl_context": _make_test_auto_impl_context(module),
            })
            auto_code = generate_implementation(
                auto_module, template_env, Path("/tmp/test.py"),
                package_name=MODEL_IDS[model_name],
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
        """Handwritten impl (no NotImplementedError) is NOT upgraded even if auto_impl_context.

        The 3-condition check requires 'NotImplementedError' in existing content.
        If the user has already written real implementation code, it must be preserved."""
        graph, _inputs = all_graph_data[model_name]
        modules = _get_calcusage_modules(graph)

        module = next(m for m in modules if m.outputs)

        # Write a "handwritten" impl that matches the signature but has real code
        func_name = f"run_{module.calc_def_name.lower()}"
        input_type = f"{module.calc_def_name}Input"
        num_outputs = len(module.outputs)
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
        impl_file = tmp_path / f"{module.calc_def_name}_handwritten.py"
        impl_file.write_text(handwritten_code)

        # Verify signature unchanged
        should_regen, reason = should_regenerate_stencil(module, impl_file)
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
    """REQ-SR-06: The unified _generate_stencils handles all module types including
    aggregation and FORMULA through the same smart regen code path. Aggregation and
    FORMULA modules with auto_impl_context will get auto-impl upgrades from stubs."""

    @pytest.mark.req("REQ-SR-06")
    def test_req_sr_06_unified_stencils_handles_all_types(self):
        """Static analysis: _generate_stencils() (unified) handles all module types
        through a single iteration over ctx.computation_graph.modules."""
        from sysml_codegen.cli import _generate_stencils

        source = inspect.getsource(_generate_stencils)
        # The unified function iterates over computation_graph.modules
        assert "computation_graph.modules" in source
        # It uses generate_implementation (the graph-only function)
        assert "generate_implementation" in source

    @pytest.mark.req("REQ-SR-06")
    def test_req_sr_06_no_separate_type_specific_stencil_functions(self):
        """The CLI no longer has separate _generate_aggregation_stencils or
        _generate_computed_attr_stencils functions — all types unified."""
        import sysml_codegen.cli as cli_module
        assert not hasattr(cli_module, "_generate_aggregation_stencils"), (
            "Separate _generate_aggregation_stencils should be removed"
        )
        assert not hasattr(cli_module, "_generate_computed_attr_stencils"), (
            "Separate _generate_computed_attr_stencils should be removed"
        )


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
