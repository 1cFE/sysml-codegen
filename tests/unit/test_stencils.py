"""Unit tests for implementation generation (auto-impl + stub dispatch).

Tests:
- Auto-impl template produces syntactically valid Python
- Auto-impl has AUTO_IMPLEMENTED = True sentinel
- Stub used for MANUAL_REQUIRED, UNKNOWN, None auto_impl_context
- PARTIALLY_COMPILABLE falls through to stub (FR-12)
- Auto-impl and stub share identical function signatures (preservation)
- Backlog report excludes FULLY_COMPILABLE modules
- Undeclared intermediates emitted as local variables
- Multi-output modules produce tuple return
- Smart-regen stub-to-auto-impl upgrade (Bug 5)

NOTE: Tests adapted for 7.6 — generation functions now take PipelineModule
instead of CalculationDefinitionData. auto_impl_context dict replaces
compilation_result parameter.
"""

from __future__ import annotations

import ast
from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.generation.stencils import (
    generate_backlog_report,
    generate_implementation,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleInput,
    ModuleOutput,
    PipelineModule,
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


def _make_pipeline_module(
    name: str = "testcalc",
    calc_def_name: str = "TestCalc",
    qualified_name: str = "TestCalc",
    num_inputs: int = 1,
    num_outputs: int = 1,
    auto_impl_context: dict | None = None,
    compilability: Compilability = Compilability.UNKNOWN,
) -> PipelineModule:
    """Build a minimal PipelineModule for testing."""
    inputs = [
        ModuleInput(
            param_name=f"x{i}" if num_inputs > 1 else "x",
            python_type="float",
            source={"source_type": "entry_point", "qualified_name": f"ep_{i}"},
            description=f"Input x{i}" if num_inputs > 1 else "Input x",
        )
        for i in range(num_inputs)
    ]

    if num_outputs == 1:
        outputs = [
            ModuleOutput(
                field_name="root",
                python_type="float",
                channel_name=f"{name}__result",
                description="Result output",
            )
        ]
    else:
        outputs = [
            ModuleOutput(
                field_name=f"out{i}",
                python_type="float",
                channel_name=f"{name}__out{i}",
                description=f"Output out{i}",
            )
            for i in range(num_outputs)
        ]

    return PipelineModule(
        name=name,
        module_type=f"{calc_def_name}Module",
        inputs=inputs,
        outputs=outputs,
        execution_order=0,
        compilability=compilability,
        is_computed_attribute=False,
        is_aggregation=False,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=qualified_name,
        doc_comment="Test calculation",
        calc_expressions=["result = x * 2"],
        source_file="test.sysml",
        source_line=1,
        auto_impl_context=auto_impl_context,
    )


def _make_auto_impl_context(
    output_name: str = "result",
    expression: str = "(inputs.x * 2)",
) -> dict:
    """Build a FULLY_COMPILABLE auto_impl_context for a single-output module."""
    return {
        "execution_steps": [],
        "output_expressions": [{"name": output_name, "expression": expression}],
        "output_count": 1,
        "single_output_expression": expression,
    }


def _make_multi_output_auto_impl_context(
    output_results: list[dict],
    has_crossrefs: bool = False,
) -> dict:
    """Build auto_impl_context for multi-output modules.

    Args:
        output_results: List of {"name": str, "expression": str, ...} dicts
        has_crossrefs: If True, all outputs become execution_steps
    """
    if has_crossrefs:
        execution_steps = [
            {"name": r["name"], "expression": r["expression"]}
            for r in output_results
        ]
        output_expressions = [
            {"name": r["name"], "expression": r["name"]}
            for r in output_results
            if not r.get("is_undeclared_intermediate", False)
        ]
    else:
        execution_steps = [
            {"name": r["name"], "expression": r["expression"]}
            for r in output_results
            if r.get("is_undeclared_intermediate", False)
        ]
        output_expressions = [
            {"name": r["name"], "expression": r["expression"]}
            for r in output_results
            if not r.get("is_undeclared_intermediate", False)
        ]

    return {
        "execution_steps": execution_steps,
        "output_expressions": output_expressions,
        "output_count": len(output_expressions),
        "single_output_expression": (
            output_expressions[0]["expression"]
            if len(output_expressions) == 1
            else None
        ),
    }


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
    module = _make_pipeline_module(
        auto_impl_context=_make_auto_impl_context(),
        compilability=Compilability.FULLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    ast.parse(code)


def test_auto_impl_has_auto_implemented_sentinel():
    """Auto-impl output contains AUTO_IMPLEMENTED = True module-level constant."""
    env = _get_template_env()
    module = _make_pipeline_module(
        auto_impl_context=_make_auto_impl_context(),
        compilability=Compilability.FULLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    assert "AUTO_IMPLEMENTED = True" in code


def test_auto_impl_contains_return_expression():
    """Auto-impl output contains the compiled expression in a return statement."""
    env = _get_template_env()
    module = _make_pipeline_module(
        auto_impl_context=_make_auto_impl_context(expression="(inputs.x * 2)"),
        compilability=Compilability.FULLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    assert "return (inputs.x * 2)" in code
    assert "NotImplementedError" not in code


# --- Stub fallback tests ---


def test_stub_template_used_for_manual_required():
    """MANUAL_REQUIRED (no auto_impl_context) falls through to NotImplementedError stub."""
    env = _get_template_env()
    module = _make_pipeline_module(
        auto_impl_context=None,
        compilability=Compilability.MANUAL_REQUIRED,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


def test_stub_template_used_when_no_compilation_result():
    """None auto_impl_context -> stub template."""
    env = _get_template_env()
    module = _make_pipeline_module(
        auto_impl_context=None,
        compilability=Compilability.UNKNOWN,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


def test_partially_compilable_falls_through_to_stub():
    """FR-12: PARTIALLY_COMPILABLE (no auto_impl_context) gets stub, not auto-impl."""
    env = _get_template_env()
    module = _make_pipeline_module(
        auto_impl_context=None,
        compilability=Compilability.PARTIALLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    assert "NotImplementedError" in code
    assert "AUTO_IMPLEMENTED" not in code


# --- Signature preservation test ---


def test_auto_impl_same_function_signature_as_stub():
    """Auto-impl and stub produce identical function signatures for preservation."""
    env = _get_template_env()

    auto_module = _make_pipeline_module(
        auto_impl_context=_make_auto_impl_context(),
        compilability=Compilability.FULLY_COMPILABLE,
    )
    stub_module = _make_pipeline_module(
        auto_impl_context=None,
        compilability=Compilability.UNKNOWN,
    )

    auto_code = generate_implementation(auto_module, env, Path("out.py"), "test_pkg")
    stub_code = generate_implementation(stub_module, env, Path("out.py"), "test_pkg")

    auto_sig = _extract_def_line(auto_code)
    stub_sig = _extract_def_line(stub_code)

    assert auto_sig is not None
    assert stub_sig is not None
    assert auto_sig == stub_sig


# --- Backlog report test ---


def test_backlog_report_excludes_fully_compilable():
    """generate_backlog_report skips FULLY_COMPILABLE modules."""
    compilable = _make_pipeline_module(
        name="compilable",
        calc_def_name="Compilable",
        qualified_name="Compilable",
        auto_impl_context=_make_auto_impl_context(),
        compilability=Compilability.FULLY_COMPILABLE,
    )
    manual = _make_pipeline_module(
        name="manual",
        calc_def_name="Manual",
        qualified_name="Manual",
        auto_impl_context=None,
        compilability=Compilability.UNKNOWN,
    )

    graph = ComputationGraph(
        modules=[compilable, manual],
        entry_point_groups=[],
        execution_order=["compilable", "manual"],
    )

    report = generate_backlog_report(graph, Path("backlog.md"), "test_pkg")

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
    module = _make_pipeline_module(
        auto_impl_context=_make_multi_output_auto_impl_context(
            output_results=[
                {"name": "temp", "expression": "(inputs.x + 1)", "is_undeclared_intermediate": True},
                {"name": "result", "expression": "(temp * 2)"},
            ],
            has_crossrefs=False,
        ),
        compilability=Compilability.FULLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    ast.parse(code)
    assert "temp = (inputs.x + 1)" in code
    assert "return (temp * 2)" in code
    assert "AUTO_IMPLEMENTED = True" in code


def test_auto_impl_multi_output():
    """Multi-output module produces tuple return."""
    env = _get_template_env()
    module = _make_pipeline_module(
        num_outputs=2,
        auto_impl_context={
            "execution_steps": [],
            "output_expressions": [
                {"name": "out0", "expression": "(inputs.x * 2)"},
                {"name": "out1", "expression": "(inputs.x + 1)"},
            ],
            "output_count": 2,
            "single_output_expression": None,
        },
        compilability=Compilability.FULLY_COMPILABLE,
    )

    code = generate_implementation(module, env, Path("out.py"), "test_pkg")
    ast.parse(code)
    assert "return (" in code
    assert "(inputs.x * 2)," in code
    assert "(inputs.x + 1)," in code


# --- Multi-output cross-reference tests (Item 4.1 fix) ---


class TestAutoImplOutputCrossRefs:
    """Tests for multi-output modules with declared output cross-references."""

    def test_full_cascade_3_outputs(self):
        """A->B->C: all outputs in a dependency chain become local vars."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="cascadecalc",
            calc_def_name="CascadeCalc",
            qualified_name="CascadeCalc",
            num_inputs=2,
            num_outputs=3,
            auto_impl_context=_make_multi_output_auto_impl_context(
                output_results=[
                    {"name": "out0", "expression": "(inputs.x0 + inputs.x1)"},
                    {"name": "out1", "expression": "(out0 * 2)"},
                    {"name": "out2", "expression": "(out1 - inputs.x0)"},
                ],
                has_crossrefs=True,
            ),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "out0 = (inputs.x0 + inputs.x1)" in code
        assert "out1 = (out0 * 2)" in code
        assert "out2 = (out1 - inputs.x0)" in code
        assert "return (" in code
        assert "(inputs.x0 + inputs.x1)," not in code

    def test_partial_cascade_some_crossrefs(self):
        """A standalone, B refs A, C standalone: all become local vars when any cross-ref."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="partialcalc",
            calc_def_name="PartialCalc",
            qualified_name="PartialCalc",
            num_inputs=2,
            num_outputs=3,
            auto_impl_context=_make_multi_output_auto_impl_context(
                output_results=[
                    {"name": "out0", "expression": "(inputs.x0 * 2)"},
                    {"name": "out1", "expression": "(out0 + inputs.x1)"},
                    {"name": "out2", "expression": "(inputs.x1 * 3)"},
                ],
                has_crossrefs=True,
            ),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "out0 = (inputs.x0 * 2)" in code
        assert "out1 = (out0 + inputs.x1)" in code
        assert "out2 = (inputs.x1 * 3)" in code
        assert "return (" in code
        assert "(inputs.x0 * 2)," not in code

    def test_independent_multi_output_no_crossrefs(self):
        """Two independent outputs: inline in return tuple (regression guard)."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="independentcalc",
            calc_def_name="IndependentCalc",
            qualified_name="IndependentCalc",
            num_inputs=2,
            num_outputs=2,
            auto_impl_context={
                "execution_steps": [],
                "output_expressions": [
                    {"name": "out0", "expression": "(inputs.x0 * 2)"},
                    {"name": "out1", "expression": "(inputs.x1 + 1)"},
                ],
                "output_count": 2,
                "single_output_expression": None,
            },
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "return (" in code
        assert "(inputs.x0 * 2)," in code
        assert "(inputs.x1 + 1)," in code
        assert "out0 = (" not in code
        assert "out1 = (" not in code

    def test_single_output_regression(self):
        """Single output: inline return, not local var (regression guard)."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="simplecalc",
            calc_def_name="SimpleCalc",
            qualified_name="SimpleCalc",
            num_inputs=1,
            num_outputs=1,
            auto_impl_context=_make_auto_impl_context(
                output_name="result",
                expression="(inputs.x * 2)",
            ),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "return (inputs.x * 2)" in code
        assert "result = (" not in code

    def test_mixed_undeclared_intermediates_and_crossrefs(self):
        """Undeclared intermediate + declared cross-refs coexist."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="mixedcalc",
            calc_def_name="MixedCalc",
            qualified_name="MixedCalc",
            num_inputs=1,
            num_outputs=2,
            auto_impl_context=_make_multi_output_auto_impl_context(
                output_results=[
                    {"name": "temp", "expression": "(inputs.x + 1)", "is_undeclared_intermediate": True},
                    {"name": "out0", "expression": "(temp * 2)"},
                    {"name": "out1", "expression": "(out0 + 3)"},
                ],
                has_crossrefs=True,
            ),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "temp = (inputs.x + 1)" in code
        assert "out0 = (temp * 2)" in code
        assert "out1 = (out0 + 3)" in code
        assert "return (" in code
        assert "(temp * 2)," not in code

    def test_diamond_pattern_4_outputs(self):
        """Diamond: A standalone, B and C ref A, D refs B and C."""
        env = _get_template_env()
        module = _make_pipeline_module(
            name="diamondcalc",
            calc_def_name="DiamondCalc",
            qualified_name="DiamondCalc",
            num_inputs=1,
            num_outputs=4,
            auto_impl_context=_make_multi_output_auto_impl_context(
                output_results=[
                    {"name": "out0", "expression": "(inputs.x * 2)"},
                    {"name": "out1", "expression": "(out0 + 1)"},
                    {"name": "out2", "expression": "(out0 - 1)"},
                    {"name": "out3", "expression": "(out1 * out2)"},
                ],
                has_crossrefs=True,
            ),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        code = generate_implementation(module, env, Path("out.py"), "test_pkg")
        ast.parse(code)
        assert "out0 = (inputs.x * 2)" in code
        assert "out1 = (out0 + 1)" in code
        assert "out2 = (out0 - 1)" in code
        assert "out3 = (out1 * out2)" in code
        assert "return (" in code
        assert "(inputs.x * 2)," not in code


# --- Smart-regen stub upgrade tests (Bug 5) ---


class TestSmartRegenStubUpgrade:
    """Bug 5: --smart-regen upgrades stubs when auto-impl available."""

    def _run_smart_regen(self, tmp_path, existing_content, module):
        """Run _generate_stencils with smart_regen=True, return stencil path."""
        from types import SimpleNamespace

        from sysml_codegen.cli import GenerationConfig, _generate_stencils

        output_path = tmp_path / "output"
        handwritten_dir = output_path / "handwritten"
        handwritten_dir.mkdir(parents=True)

        stencil_path = handwritten_dir / "testcalc_impl.py"
        stencil_path.write_text(existing_content)

        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output_path,
            package_name="test_pkg",
            smart_regen=True,
        )

        graph = ComputationGraph(
            modules=[module],
            entry_point_groups=[],
            execution_order=[module.name],
        )

        ctx = SimpleNamespace(computation_graph=graph)

        template_env = _get_template_env()
        _generate_stencils(ctx, config, template_env)

        return stencil_path

    def test_stub_upgraded_when_fully_compilable(self, tmp_path):
        """Stub file + FULLY_COMPILABLE -> upgraded to auto-impl."""
        stub = 'def run_testcalc(inputs: TestCalcInput) -> float:\n    raise NotImplementedError("TODO")\n'
        module = _make_pipeline_module(
            auto_impl_context=_make_auto_impl_context(),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        path = self._run_smart_regen(tmp_path, stub, module)

        content = path.read_text()
        assert "raise NotImplementedError" not in content
        assert "AUTO_IMPLEMENTED = True" in content

    def test_handwritten_preserved_when_fully_compilable(self, tmp_path):
        """Handwritten file + FULLY_COMPILABLE -> preserved."""
        handwritten = "def run_testcalc(inputs: TestCalcInput) -> float:\n    return inputs.x * 2\n"
        module = _make_pipeline_module(
            auto_impl_context=_make_auto_impl_context(),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        path = self._run_smart_regen(tmp_path, handwritten, module)
        assert path.read_text() == handwritten

    def test_auto_impl_preserved_when_fully_compilable(self, tmp_path):
        """Auto-implemented file + FULLY_COMPILABLE -> preserved."""
        auto_impl = (
            "AUTO_IMPLEMENTED = True\n"
            "def run_testcalc(inputs: TestCalcInput) -> float:\n"
            "    return inputs.x * 2\n"
        )
        module = _make_pipeline_module(
            auto_impl_context=_make_auto_impl_context(),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        path = self._run_smart_regen(tmp_path, auto_impl, module)
        assert path.read_text() == auto_impl

    def test_stub_preserved_when_not_compilable(self, tmp_path):
        """Stub file + no auto_impl_context -> preserved."""
        stub = 'def run_testcalc(inputs: TestCalcInput) -> float:\n    raise NotImplementedError("TODO")\n'
        module = _make_pipeline_module(
            auto_impl_context=None,
            compilability=Compilability.UNKNOWN,
        )

        path = self._run_smart_regen(tmp_path, stub, module)
        assert "raise NotImplementedError" in path.read_text()

    @pytest.mark.req("REQ-SR-05")
    def test_backup_created_before_regen_through_real_stencil_path(self, tmp_path):
        """REQ-SR-05: driven through the real `_generate_stencils` upgrade path
        (not `backup_implementation()` called in isolation) -- a stub gets
        upgraded to auto-impl, and a backup preserving the PRE-regen (stub)
        content must exist in `handwritten/backup/` afterward. Writes only to
        `tmp_path`, never a committed baseline (no byte-identity risk)."""
        stub = 'def run_testcalc(inputs: TestCalcInput) -> float:\n    raise NotImplementedError("TODO")\n'
        module = _make_pipeline_module(
            auto_impl_context=_make_auto_impl_context(),
            compilability=Compilability.FULLY_COMPILABLE,
        )

        path = self._run_smart_regen(tmp_path, stub, module)

        # The stub was actually upgraded (regen happened).
        assert "AUTO_IMPLEMENTED = True" in path.read_text()

        # A backup of the PRE-regen stub content exists.
        backup_dir = path.parent / "backup"
        assert backup_dir.exists(), "backup_implementation was not called before regen"
        backups = list(backup_dir.glob(f"{path.stem}_*.py"))
        assert len(backups) == 1, f"Expected exactly one backup, found {backups}"
        assert backups[0].read_text() == stub, (
            "Backup content does not match the pre-regen stub -- backup ran "
            "after the file was already overwritten, or backed up the wrong file"
        )
