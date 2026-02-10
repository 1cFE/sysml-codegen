"""Unit tests for implementation generation (auto-impl + stub dispatch).

Tests:
- Auto-impl template produces syntactically valid Python
- Auto-impl has AUTO_IMPLEMENTED = True sentinel
- Stub used for MANUAL_REQUIRED, UNKNOWN, None compilation results
- PARTIALLY_COMPILABLE falls through to stub (FR-12)
- Auto-impl and stub share identical function signatures (preservation)
- Backlog report excludes FULLY_COMPILABLE CalcDefs
- Undeclared intermediates emitted as local variables
- Multi-output CalcDefs produce tuple return
- Smart-regen stub-to-auto-impl upgrade (Bug 5)
"""

from __future__ import annotations

import ast
from pathlib import Path

import jinja2

from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
    CompilationResult,
)
from sysml_codegen.generation.stencils import (
    generate_backlog_report,
    generate_implementation,
)


def _get_template_env() -> jinja2.Environment:
    """Create Jinja2 environment pointing at package templates."""
    template_dir = (
        Path(__file__).parent.parent.parent
        / "src"
        / "sysml_codegen"
        / "templates"
    )
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _make_calc_def(
    name: str = "TestCalc",
    qualified_name: str = "TestCalc",
    num_inputs: int = 1,
    num_outputs: int = 1,
) -> CalculationDefinitionData:
    """Build a minimal CalculationDefinitionData for testing."""
    inputs = [
        AttributeInfo(
            name=f"x{i}" if num_inputs > 1 else "x",
            sysml_type="Real",
            python_type="float",
        )
        for i in range(num_inputs)
    ]
    outputs = [
        AttributeInfo(
            name=f"out{i}" if num_outputs > 1 else "result",
            sysml_type="Real",
            python_type="float",
        )
        for i in range(num_outputs)
    ]
    return CalculationDefinitionData(
        name=name,
        qualified_name=qualified_name,
        doc_comment="Test calculation",
        calc_expressions=["result = x * 2"],
        input_attributes=inputs,
        output_attributes=outputs,
        references=[],
        source_file=Path("test.sysml"),
    )


def _make_compilable_result(
    calc_def_name: str = "TestCalc",
    output_name: str = "result",
    expression: str = "(inputs.x * 2)",
) -> CalcDefCompilationResult:
    """Build a FULLY_COMPILABLE result for a single-output CalcDef."""
    return CalcDefCompilationResult(
        calc_def_name=calc_def_name,
        overall_compilability=Compilability.FULLY_COMPILABLE,
        output_results=[
            CompilationResult(
                output_name=output_name,
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression=expression,
                input_refs=["x"],
            ),
        ],
        execution_order=[output_name],
    )


def _make_manual_result(
    calc_def_name: str = "TestCalc",
) -> CalcDefCompilationResult:
    """Build a MANUAL_REQUIRED result."""
    return CalcDefCompilationResult(
        calc_def_name=calc_def_name,
        overall_compilability=Compilability.MANUAL_REQUIRED,
        output_results=[
            CompilationResult(
                output_name="result",
                compilability=Compilability.MANUAL_REQUIRED,
                unsupported_reason="test reason",
            ),
        ],
        execution_order=["result"],
    )


def _make_partial_result(
    calc_def_name: str = "TestCalc",
) -> CalcDefCompilationResult:
    """Build a PARTIALLY_COMPILABLE result."""
    return CalcDefCompilationResult(
        calc_def_name=calc_def_name,
        overall_compilability=Compilability.PARTIALLY_COMPILABLE,
        output_results=[],
        execution_order=[],
    )


def _extract_def_line(code: str) -> str | None:
    """Extract the function definition line from generated code."""
    for line in code.splitlines():
        if line.strip().startswith("def "):
            return line.strip()
    return None


# --- Auto-impl template tests ---


def test_auto_impl_template_produces_valid_python():
    """Auto-impl template output passes ast.parse()."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    result = _make_compilable_result()

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    ast.parse(code)


def test_auto_impl_has_auto_implemented_sentinel():
    """Auto-impl output contains AUTO_IMPLEMENTED = True module-level constant."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    result = _make_compilable_result()

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    assert "AUTO_IMPLEMENTED = True" in code


def test_auto_impl_contains_return_expression():
    """Auto-impl output contains the compiled expression in a return statement."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    result = _make_compilable_result(expression="(inputs.x * 2)")

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    assert "return (inputs.x * 2)" in code
    assert "NotImplementedError" not in code


# --- Stub fallback tests ---


def test_stub_template_used_for_manual_required():
    """MANUAL_REQUIRED falls through to NotImplementedError stub."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    result = _make_manual_result()

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


def test_stub_template_used_when_no_compilation_result():
    """None compilation_result -> stub template."""
    env = _get_template_env()
    calc_def = _make_calc_def()

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=None,
    )

    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


def test_partially_compilable_falls_through_to_stub():
    """FR-12: PARTIALLY_COMPILABLE gets stub, not auto-impl."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    result = _make_partial_result()

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


# --- Signature preservation test ---


def test_auto_impl_same_function_signature_as_stub():
    """Auto-impl and stub produce identical function signatures for preservation."""
    env = _get_template_env()
    calc_def = _make_calc_def()
    compilable = _make_compilable_result()

    auto_code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=compilable,
    )
    stub_code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=None,
    )

    auto_sig = _extract_def_line(auto_code)
    stub_sig = _extract_def_line(stub_code)

    assert auto_sig is not None
    assert stub_sig is not None
    assert auto_sig == stub_sig


# --- Backlog report test ---


def test_backlog_report_excludes_fully_compilable():
    """generate_backlog_report skips FULLY_COMPILABLE CalcDefs."""
    compilable_cd = _make_calc_def(name="Compilable", qualified_name="Compilable")
    manual_cd = _make_calc_def(name="Manual", qualified_name="Manual")

    compilation_results = {
        "Compilable": CalcDefCompilationResult(
            calc_def_name="Compilable",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[],
            execution_order=[],
        ),
    }

    report = generate_backlog_report(
        [compilable_cd, manual_cd],
        Path("backlog.md"),
        "test_pkg",
        compilation_results=compilation_results,
    )

    # Only Manual should appear in the backlog table
    lines = report.splitlines()
    table_lines = [line for line in lines if line.startswith("| [ ]")]
    assert len(table_lines) == 1
    assert "Manual" in table_lines[0]
    assert "1 functions to implement" in report


# --- Complex template tests ---


def test_auto_impl_with_undeclared_intermediates():
    """Undeclared intermediates appear as local variable assignments."""
    env = _get_template_env()
    calc_def = _make_calc_def()

    result = CalcDefCompilationResult(
        calc_def_name="TestCalc",
        overall_compilability=Compilability.FULLY_COMPILABLE,
        output_results=[
            CompilationResult(
                output_name="temp",
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression="(inputs.x + 1)",
                input_refs=["x"],
                is_undeclared_intermediate=True,
            ),
            CompilationResult(
                output_name="result",
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression="(temp * 2)",
                intermediate_refs=["temp"],
            ),
        ],
        execution_order=["temp", "result"],
    )

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    ast.parse(code)
    assert "temp = (inputs.x + 1)" in code
    assert "return (temp * 2)" in code
    assert "AUTO_IMPLEMENTED = True" in code


def test_auto_impl_multi_output():
    """Multi-output CalcDef produces tuple return."""
    env = _get_template_env()
    calc_def = _make_calc_def(num_outputs=2)

    result = CalcDefCompilationResult(
        calc_def_name="TestCalc",
        overall_compilability=Compilability.FULLY_COMPILABLE,
        output_results=[
            CompilationResult(
                output_name="out0",
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression="(inputs.x * 2)",
                input_refs=["x"],
            ),
            CompilationResult(
                output_name="out1",
                compilability=Compilability.FULLY_COMPILABLE,
                python_expression="(inputs.x + 1)",
                input_refs=["x"],
            ),
        ],
        execution_order=["out0", "out1"],
    )

    code = generate_implementation(
        calc_def, env, Path("out.py"), "test_pkg",
        compilation_result=result,
    )

    ast.parse(code)
    assert "return (" in code
    assert "(inputs.x * 2)," in code
    assert "(inputs.x + 1)," in code


# --- Multi-output cross-reference tests (Item 4.1 fix) ---


class TestAutoImplOutputCrossRefs:
    """Tests for multi-output CalcDefs with declared output cross-references.

    Covers Item 4.1 fix: declared outputs that reference other declared outputs
    must be emitted as local variable assignments, not inlined in return tuple.
    """

    def test_full_cascade_3_outputs(self):
        """A->B->C: all outputs in a dependency chain become local vars."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="CascadeCalc", qualified_name="CascadeCalc",
            num_inputs=2, num_outputs=3,
        )
        result = CalcDefCompilationResult(
            calc_def_name="CascadeCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="out0",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x0 + inputs.x1)",
                    input_refs=["x0", "x1"],
                ),
                CompilationResult(
                    output_name="out1",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out0 * 2)",
                    intermediate_refs=["out0"],
                ),
                CompilationResult(
                    output_name="out2",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out1 - inputs.x0)",
                    input_refs=["x0"],
                    intermediate_refs=["out1"],
                ),
            ],
            execution_order=["out0", "out1", "out2"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        # All outputs assigned as local vars
        assert "out0 = (inputs.x0 + inputs.x1)" in code
        assert "out1 = (out0 * 2)" in code
        assert "out2 = (out1 - inputs.x0)" in code
        # Return tuple uses names, not inlined expressions
        assert "return (" in code
        assert "(inputs.x0 + inputs.x1)," not in code

    def test_partial_cascade_some_crossrefs(self):
        """A standalone, B refs A, C standalone: all become local vars when any cross-ref."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="PartialCalc", qualified_name="PartialCalc",
            num_inputs=2, num_outputs=3,
        )
        result = CalcDefCompilationResult(
            calc_def_name="PartialCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="out0",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x0 * 2)",
                    input_refs=["x0"],
                ),
                CompilationResult(
                    output_name="out1",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out0 + inputs.x1)",
                    input_refs=["x1"],
                    intermediate_refs=["out0"],
                ),
                CompilationResult(
                    output_name="out2",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x1 * 3)",
                    input_refs=["x1"],
                ),
            ],
            execution_order=["out0", "out1", "out2"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        # ALL outputs assigned as local vars (even standalone out2)
        assert "out0 = (inputs.x0 * 2)" in code
        assert "out1 = (out0 + inputs.x1)" in code
        assert "out2 = (inputs.x1 * 3)" in code
        assert "return (" in code
        # Inlined expressions should NOT appear in return tuple
        assert "(inputs.x0 * 2)," not in code

    def test_independent_multi_output_no_crossrefs(self):
        """Two independent outputs: inline in return tuple (regression guard)."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="IndependentCalc", qualified_name="IndependentCalc",
            num_inputs=2, num_outputs=2,
        )
        result = CalcDefCompilationResult(
            calc_def_name="IndependentCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="out0",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x0 * 2)",
                    input_refs=["x0"],
                ),
                CompilationResult(
                    output_name="out1",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x1 + 1)",
                    input_refs=["x1"],
                ),
            ],
            execution_order=["out0", "out1"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        # Outputs inlined in return tuple (no local var assignments)
        assert "return (" in code
        assert "(inputs.x0 * 2)," in code
        assert "(inputs.x1 + 1)," in code
        # Should NOT have local var assignments for outputs
        # (use " = (" to avoid matching docstring examples like ">>> out0, out1 = run_...")
        assert "out0 = (" not in code
        assert "out1 = (" not in code

    def test_single_output_regression(self):
        """Single output: inline return, not local var (regression guard)."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="SimpleCalc", qualified_name="SimpleCalc",
            num_inputs=1, num_outputs=1,
        )
        result = CalcDefCompilationResult(
            calc_def_name="SimpleCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="result",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x * 2)",
                    input_refs=["x"],
                ),
            ],
            execution_order=["result"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        assert "return (inputs.x * 2)" in code
        # " = (" avoids matching docstring example ">>> result = run_simplecalc(inputs)"
        assert "result = (" not in code

    def test_mixed_undeclared_intermediates_and_crossrefs(self):
        """Undeclared intermediate + declared cross-refs coexist."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="MixedCalc", qualified_name="MixedCalc",
            num_inputs=1, num_outputs=2,
        )
        result = CalcDefCompilationResult(
            calc_def_name="MixedCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="temp",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x + 1)",
                    input_refs=["x"],
                    is_undeclared_intermediate=True,
                ),
                CompilationResult(
                    output_name="out0",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(temp * 2)",
                    intermediate_refs=["temp"],
                ),
                CompilationResult(
                    output_name="out1",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out0 + 3)",
                    intermediate_refs=["out0"],
                ),
            ],
            execution_order=["temp", "out0", "out1"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        # Undeclared intermediate as local var
        assert "temp = (inputs.x + 1)" in code
        # Declared outputs promoted to local vars due to cross-ref
        assert "out0 = (temp * 2)" in code
        assert "out1 = (out0 + 3)" in code
        # Return tuple uses names
        assert "return (" in code
        assert "(temp * 2)," not in code

    def test_diamond_pattern_4_outputs(self):
        """Diamond: A standalone, B and C ref A, D refs B and C."""
        env = _get_template_env()
        calc_def = _make_calc_def(
            name="DiamondCalc", qualified_name="DiamondCalc",
            num_inputs=1, num_outputs=4,
        )
        result = CalcDefCompilationResult(
            calc_def_name="DiamondCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(
                    output_name="out0",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(inputs.x * 2)",
                    input_refs=["x"],
                ),
                CompilationResult(
                    output_name="out1",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out0 + 1)",
                    intermediate_refs=["out0"],
                ),
                CompilationResult(
                    output_name="out2",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out0 - 1)",
                    intermediate_refs=["out0"],
                ),
                CompilationResult(
                    output_name="out3",
                    compilability=Compilability.FULLY_COMPILABLE,
                    python_expression="(out1 * out2)",
                    intermediate_refs=["out1", "out2"],
                ),
            ],
            execution_order=["out0", "out1", "out2", "out3"],
        )

        code = generate_implementation(
            calc_def, env, Path("out.py"), "test_pkg",
            compilation_result=result,
        )
        ast.parse(code)
        # All outputs assigned as local vars in topological order
        assert "out0 = (inputs.x * 2)" in code
        assert "out1 = (out0 + 1)" in code
        assert "out2 = (out0 - 1)" in code
        assert "out3 = (out1 * out2)" in code
        assert "return (" in code
        assert "(inputs.x * 2)," not in code


# --- Smart-regen stub upgrade tests (Bug 5) ---


class TestSmartRegenStubUpgrade:
    """Bug 5: --smart-regen upgrades stubs when auto-impl available."""

    def _run_smart_regen(self, tmp_path, existing_content, compilation_result):
        """Run _generate_stencils with smart_regen=True, return stencil path."""
        from types import SimpleNamespace
        from unittest.mock import patch

        from sysml_codegen.cli import GenerationConfig, _generate_stencils

        output_path = tmp_path / "output"
        handwritten_dir = output_path / "handwritten"
        handwritten_dir.mkdir(parents=True)

        calc_def = _make_calc_def()

        stencil_path = handwritten_dir / "testcalc_impl.py"
        stencil_path.write_text(existing_content)

        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output_path,
            package_name="test_pkg",
            smart_regen=True,
        )

        ctx = SimpleNamespace(
            calc_defs=[calc_def],
            compilation_results=(
                {"TestCalc": compilation_result} if compilation_result else {}
            ),
        )

        template_env = _get_template_env()

        with patch(
            "sysml_codegen.generation.should_regenerate_stencil",
            return_value=(False, "Signature unchanged"),
        ):
            _generate_stencils(ctx, config, template_env)

        return stencil_path

    def test_stub_upgraded_when_fully_compilable(self, tmp_path):
        """Stub file + FULLY_COMPILABLE -> upgraded to auto-impl."""
        stub = 'def run_testcalc(inputs):\n    raise NotImplementedError("TODO")\n'
        result = _make_compilable_result()

        path = self._run_smart_regen(tmp_path, stub, result)

        content = path.read_text()
        assert "raise NotImplementedError" not in content
        assert "AUTO_IMPLEMENTED = True" in content

    def test_handwritten_preserved_when_fully_compilable(self, tmp_path):
        """Handwritten file + FULLY_COMPILABLE -> preserved."""
        handwritten = "def run_testcalc(inputs):\n    return inputs.x * 2\n"
        result = _make_compilable_result()

        path = self._run_smart_regen(tmp_path, handwritten, result)

        assert path.read_text() == handwritten

    def test_auto_impl_preserved_when_fully_compilable(self, tmp_path):
        """Auto-implemented file + FULLY_COMPILABLE -> preserved."""
        auto_impl = (
            "AUTO_IMPLEMENTED = True\n"
            "def run_testcalc(inputs):\n"
            "    return inputs.x * 2\n"
        )
        result = _make_compilable_result()

        path = self._run_smart_regen(tmp_path, auto_impl, result)

        assert path.read_text() == auto_impl

    def test_stub_preserved_when_not_compilable(self, tmp_path):
        """Stub file + no compilation result -> preserved."""
        stub = 'def run_testcalc(inputs):\n    raise NotImplementedError("TODO")\n'

        path = self._run_smart_regen(tmp_path, stub, None)

        assert "raise NotImplementedError" in path.read_text()
