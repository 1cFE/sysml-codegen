"""Generation Boundary Enforcement (7.6) — Conformance Tests.

Requirements: REQ-PIPE-07, REQ-GEN-01, REQ-GEN-04
Design intent: 00-pipeline-overview.md, 08-generation.md, 26-pipeline-module-migration.md

This test file enforces that the generation/ package consumes ONLY the
ComputationGraph — no back-references to extraction/ or analysis/ models.

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ModuleKind,
)

from tests.conftest import exact_graph_from_fixture


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
GEN_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "generation"

# The D-5 migrated variants, not the corpus originals: the exact route refuses all three
# originals (SI_SELF_BINDING, plus a same-name rollup collision for solar), so a
# generation-layer test that reads them can only ever exercise the legacy route. The
# variants carry the same models in the form the exact route accepts. `attr_expr_probe`
# is accepted as authored and needs no variant. See each fixture's PROVENANCE.md and the
# Gate 4C part 6 notes.
PARAMETRIZED_MODELS = [
    "solar_battery_d5",
    "catf_mfe_d5",
    "attr_expr_probe",
    "chain_spike_d5",
]

MODEL_IDS = {
    "solar_battery_d5": "solar_battery",
    "catf_mfe_d5": "catf_mfe",
    "attr_expr_probe": "attr_expr_probe",
    "chain_spike_d5": "chain_spike",
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
def all_graph_data() -> dict[str, ComputationGraph]:
    """Project each model's sealed v6 graph, once per session.

    The legacy call returned ``(graph, classifier_inputs)`` and every consumer here bound
    the second element to ``_inputs``, so the exact route's graph-only result loses nothing.
    """
    return {name: exact_graph_from_fixture(name) for name in PARAMETRIZED_MODELS}


@pytest.fixture(scope="session")
def solar_battery_graph(all_graph_data):
    return all_graph_data["solar_battery_d5"]


@pytest.fixture(scope="session")
def catf_mfe_graph(all_graph_data):
    return all_graph_data["catf_mfe_d5"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _scan_generation_imports(package: str) -> list[str]:
    """Scan generation/ *.py files for imports from the given package.

    Skips comment lines. Returns list of filenames that violate the boundary.
    """
    violating: list[str] = []
    for py_file in sorted(GEN_DIR.glob("*.py")):
        content = py_file.read_text()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if (
                f"from sysml_codegen.{package}" in stripped
                or f"import sysml_codegen.{package}" in stripped
            ):
                violating.append(py_file.name)
                break
    return violating


# ===========================================================================
# A. Static Boundary Tests (REQ-PIPE-07)
# ===========================================================================

class TestStaticBoundary:
    """REQ-PIPE-07: Zero extraction/analysis imports in generation/."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_zero_extraction_imports_in_generation(self):
        """No generation/ file imports from extraction/."""
        violating = _scan_generation_imports("extraction")
        assert len(violating) == 0, (
            f"generation/ files importing from extraction/: {violating}. "
            "REQ-PIPE-07 requires zero extraction imports in generation/."
        )

    @pytest.mark.req("REQ-PIPE-07")
    def test_zero_analysis_imports_in_generation(self):
        """No generation/ file imports from analysis/."""
        violating = _scan_generation_imports("analysis")
        assert len(violating) == 0, (
            f"generation/ files importing from analysis/: {violating}. "
            "REQ-PIPE-07 requires zero analysis imports in generation/."
        )

    @pytest.mark.req("REQ-PIPE-07")
    def test_pipeline_context_is_not_in_generation(self):
        """``PipelineContext`` is defined nowhere in generation/, and nowhere at all.

        The class was moved out of ``generation/initialization.py`` to ``orchestration/``
        at Step 7.6, and this node checked the move by importing it from its new home.
        It retired with the v5 family (retirement step 2) — it carried the legacy string-
        resolution route's state — so the node checks the boundary the move existed to
        establish: generation/ holds no pipeline-context class, under any spelling.
        """
        for module in GEN_DIR.rglob("*.py"):
            assert "class PipelineContext" not in module.read_text(), (
                f"{module.name} defines PipelineContext; generation/ consumes only a "
                f"ComputationGraph."
            )

    @pytest.mark.req("REQ-GEN-01")
    def test_pipeline_yaml_still_graph_only(self):
        """pipeline.py has zero imports from extraction/ or analysis/ (regression guard)."""
        pipeline_path = GEN_DIR / "pipeline.py"
        assert pipeline_path.exists(), "generation/pipeline.py not found"

        content = pipeline_path.read_text()
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            assert "from sysml_codegen.extraction" not in stripped, (
                f"pipeline.py imports from extraction: {stripped}"
            )
            assert "from sysml_codegen.analysis" not in stripped, (
                f"pipeline.py imports from analysis: {stripped}"
            )

    @pytest.mark.req("REQ-PIPE-07")
    def test_cli_generates_without_extraction_in_generation(self):
        """CLI _generate_* functions don't use function-scope extraction imports."""
        import ast

        cli_path = (
            Path(__file__).parent.parent.parent
            / "src" / "sysml_codegen" / "cli" / "__init__.py"
        )
        source = cli_path.read_text()
        tree = ast.parse(source)

        # Find all _generate_* functions and check for extraction/analysis imports
        violations = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if not node.name.startswith("_generate"):
                    continue
                # Check body for import statements referencing extraction/analysis
                for child in ast.walk(node):
                    if isinstance(child, ast.ImportFrom):
                        if child.module and (
                            "extraction" in child.module
                            or "analysis" in child.module
                        ):
                            violations.append(
                                f"{node.name}: from {child.module} import ..."
                            )
        assert len(violations) == 0, (
            f"CLI _generate_* functions have extraction/analysis imports: {violations}"
        )


# ===========================================================================
# B. Auto-Impl Dispatch Tests (REQ-GEN-04)
# ===========================================================================

class TestAutoImplDispatch:
    """REQ-GEN-04: Stencil _from_graph() dispatches on auto-impl context."""

    @pytest.mark.req("REQ-GEN-04")
    def test_from_graph_stencil_auto_impl_dispatch(self, solar_battery_graph, template_env):
        """FULLY_COMPILABLE module produces auto-impl (not stub) via _from_graph()."""
        from sysml_codegen.generation.stencils import generate_implementation_from_graph

        graph = solar_battery_graph

        # Find a FULLY_COMPILABLE module (FORMULA or aggregation modules are always FC)
        fc_modules = [
            m for m in graph.modules
            if m.compilability == Compilability.FULLY_COMPILABLE
        ]
        assert len(fc_modules) > 0, "No FULLY_COMPILABLE modules in solar_battery"

        module = fc_modules[0]
        code = generate_implementation_from_graph(
            module=module,
            template_env=template_env,
            output_path=Path("/tmp/test_auto_impl.py"),
            package_name="generated_code",
        )

        assert code is not None
        assert len(code) > 0
        # Auto-impl should NOT have raise NotImplementedError
        assert "raise NotImplementedError" not in code, (
            f"Module {module.name} is FULLY_COMPILABLE but got stub.\n"
            f"Code:\n{code[:500]}"
        )
        # Should have a return statement with an expression
        assert "return " in code, (
            f"Module {module.name}: auto-impl should have a return statement"
        )

    @pytest.mark.req("REQ-GEN-04")
    def test_from_graph_stencil_stub_dispatch(self, solar_battery_graph, template_env):
        """Non-FULLY_COMPILABLE module produces stub with NotImplementedError."""
        from sysml_codegen.generation.stencils import generate_implementation_from_graph

        graph = solar_battery_graph

        # With compilation_results threaded from the snapshot (SC-10), solar_battery
        # CalcUsage modules are FULLY_COMPILABLE and auto-implement. Synthesize the
        # non-FC case to exercise the generator's stub dispatch directly: take a
        # CalcUsage module and force it non-compilable.
        calc_usage = next(
            m for m in graph.modules
            if m.module_kind == ModuleKind.CALCULATION
        )
        module = calc_usage.model_copy(
            update={"compilability": Compilability.UNKNOWN, "auto_impl_context": None}
        )
        code = generate_implementation_from_graph(
            module=module,
            template_env=template_env,
            output_path=Path("/tmp/test_stub.py"),
            package_name="generated_code",
        )

        assert code is not None
        assert "raise NotImplementedError" in code, (
            f"Module {module.name} is {module.compilability} but got auto-impl"
        )

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS, ids=MODEL_IDS.values())
    def test_auto_impl_context_populated(self, model_name, all_graph_data):
        """Every FULLY_COMPILABLE module has auto_impl_context set."""
        graph = all_graph_data[model_name]

        fc_modules = [
            m for m in graph.modules
            if m.compilability == Compilability.FULLY_COMPILABLE
        ]

        for module in fc_modules:
            assert module.auto_impl_context is not None, (
                f"Model {model_name}, module {module.name}: "
                "compilability=FULLY_COMPILABLE but auto_impl_context is None"
            )

    @pytest.mark.req("REQ-GEN-04")
    @pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS, ids=MODEL_IDS.values())
    def test_auto_impl_context_none_for_manual(self, model_name, all_graph_data):
        """Every non-FULLY_COMPILABLE module has auto_impl_context=None."""
        graph = all_graph_data[model_name]

        non_fc = [
            m for m in graph.modules
            if m.compilability != Compilability.FULLY_COMPILABLE
        ]

        for module in non_fc:
            assert module.auto_impl_context is None, (
                f"Model {model_name}, module {module.name}: "
                f"compilability={module.compilability} but auto_impl_context is set"
            )


# ===========================================================================
# C. Graph-Only Output Validation Tests
# ===========================================================================

class TestGraphOnlyBacklog:
    """Backlog report generates valid output from graph."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_backlog_report_from_graph(self, solar_battery_graph):
        """generate_backlog_report(graph) produces valid markdown with module rows."""
        from sysml_codegen.generation.stencils import generate_backlog_report

        graph = solar_battery_graph

        output = generate_backlog_report(
            graph=graph,
            output_path=Path("/tmp/backlog.md"),
            package_name="generated_code",
        )

        assert output is not None
        assert "# Implementation Backlog" in output
        # Should contain table rows for non-auto-impl CalcUsage modules
        non_auto = [
            m for m in graph.modules
            if m.module_kind == ModuleKind.CALCULATION
            and m.auto_impl_context is None
        ]
        if non_auto:
            assert "| [ ] |" in output


class TestGraphOnlyTestGen:
    """Test generation produces valid output from graph."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_test_gen_from_graph(self, solar_battery_graph, template_env):
        """generate_test_implementations(graph) produces test classes."""
        import re

        from sysml_codegen.generation.test_gen import generate_test_implementations

        graph = solar_battery_graph

        output = generate_test_implementations(
            graph=graph,
            package_name="generated_code",
            template_env=template_env,
            output_path=Path("/tmp/test_impls.py"),
        )

        assert output is not None
        test_classes = re.findall(r"class (Test\w+Runnable):", output)
        # Should have test classes for CalcUsage modules
        calcusage_count = sum(
            1 for m in graph.modules
            if m.module_kind == ModuleKind.CALCULATION
        )
        assert len(test_classes) == calcusage_count


class TestGraphOnlyPreservation:
    """Preservation logic works with PipelineModule."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_preservation_nonexistent_file(self, solar_battery_graph, tmp_path):
        """should_regenerate_stencil(module, nonexistent) returns (True, reason)."""
        from sysml_codegen.generation.preservation import should_regenerate_stencil

        graph = solar_battery_graph
        module = graph.modules[0]
        fake_path = tmp_path / "nonexistent_impl.py"

        result, reason = should_regenerate_stencil(module, fake_path)
        assert result is True
        assert "doesn't exist" in reason

    @pytest.mark.req("REQ-PIPE-07")
    def test_preservation_matching_signature(self, solar_battery_graph, tmp_path):
        """should_regenerate_stencil(module, matching_file) returns (False, reason)."""
        from sysml_codegen.generation.preservation import should_regenerate_stencil

        graph = solar_battery_graph
        # Find a CalcUsage module with a single output
        module = next(
            m for m in graph.modules
            if m.module_kind == ModuleKind.CALCULATION
            and len(m.outputs) == 1
        )

        func_name = f"run_{module.calc_def_name.lower()}"
        input_class = f"{module.calc_def_name}Input"
        impl_path = tmp_path / f"{module.calc_def_name.lower()}_impl.py"
        impl_path.write_text(
            f"def {func_name}(inputs: {input_class}) -> float:\n"
            f"    raise NotImplementedError('{func_name}')\n"
        )

        result, reason = should_regenerate_stencil(module, impl_path)
        assert result is False
        assert "unchanged" in reason.lower()


# ===========================================================================
# D. All Module Types Test (REQ-PIPE-07)
# ===========================================================================

class TestAllModuleTypesRender:
    """REQ-PIPE-07: All module types render via _from_graph()."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_all_module_types_render_via_from_graph(self, solar_battery_graph, template_env):
        """CalcUsage, FORMULA, and aggregation modules all render via _from_graph()."""
        from sysml_codegen.generation.modules import generate_teax_module_from_graph

        graph = solar_battery_graph

        calcusage_count = 0
        formula_count = 0
        agg_count = 0

        for module in graph.modules:
            code = generate_teax_module_from_graph(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_module.py"),
                package_name="generated_code",
            )
            assert code is not None and len(code) > 0, (
                f"Module {module.name}: generate_teax_module_from_graph returned empty"
            )

            if module.module_kind == ModuleKind.FORMULA:
                formula_count += 1
            elif module.module_kind == ModuleKind.AGGREGATION:
                agg_count += 1
            else:
                calcusage_count += 1

        assert calcusage_count > 0, "No CalcUsage modules rendered"
        assert formula_count > 0, "No FORMULA modules rendered"
        assert agg_count > 0, "No aggregation modules rendered"
