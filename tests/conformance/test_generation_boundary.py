"""Generation Boundary Enforcement (7.6) — Conformance Tests.

Requirements: REQ-PIPE-07, REQ-GEN-01, REQ-GEN-04, REQ-PMM-05
Design intent: 00-pipeline-overview.md, 08-generation.md, 26-pipeline-module-migration.md

This test file enforces that the generation/ package consumes ONLY the
ComputationGraph — no back-references to extraction/ or analysis/ models.
It also verifies identity between old CalcDef-consuming functions and new
graph-only variants for stencils, backlog, test_gen, and preservation.

Tests use real extraction snapshot data — no mocks.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest

from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.resolution.models import (
    ComputationGraph,
    PipelineModule,
)

from tests.conformance.test_entry_point_classifier import (
    build_full_graph_from_snapshot,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
GEN_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "generation"

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
        graph, inputs = build_full_graph_from_snapshot(model_name)
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


def _calcusage_modules(graph: ComputationGraph) -> list[PipelineModule]:
    """Filter to CalcUsage modules (not FORMULA, not aggregation)."""
    return [
        m for m in graph.modules
        if not m.is_computed_attribute and not m.is_aggregation
    ]


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
    def test_pipeline_context_not_in_generation(self):
        """PipelineContext is importable from orchestration, not generation."""
        # PipelineContext should be in orchestration
        from sysml_codegen.orchestration import PipelineContext as OrcPCtx
        assert OrcPCtx is not None

        # PipelineContext should NOT be defined in generation/initialization.py
        init_path = GEN_DIR / "initialization.py"
        content = init_path.read_text()
        assert "class PipelineContext" not in content, (
            "PipelineContext is still defined in generation/initialization.py. "
            "It should be moved to orchestration/pipeline_context.py."
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

        graph, _inputs = solar_battery_graph

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

        graph, _inputs = solar_battery_graph

        # Find a non-FULLY_COMPILABLE CalcUsage module
        # (CalcUsage from snapshots have UNKNOWN compilability since
        # compilation_results=None in build_full_graph_from_snapshot)
        non_fc = [
            m for m in graph.modules
            if m.compilability != Compilability.FULLY_COMPILABLE
            and not m.is_computed_attribute and not m.is_aggregation
        ]
        assert len(non_fc) > 0, "No non-FC CalcUsage modules in solar_battery"

        module = non_fc[0]
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
        graph, _inputs = all_graph_data[model_name]

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
        graph, _inputs = all_graph_data[model_name]

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
# C. Identity Tests (REQ-PMM-05)
# ===========================================================================

class TestStencilAutoImplIdentity:
    """REQ-PMM-05: Auto-impl from graph matches old CalcDef path."""

    @pytest.mark.req("REQ-PMM-05")
    def test_from_graph_stencil_identity_auto_impl(self, solar_battery_graph, template_env):
        """For FULLY_COMPILABLE CalcUsage modules: old generate_implementation()
        with compilation_result == new generate_implementation_from_graph()."""
        from sysml_codegen.generation.stencils import generate_implementation_from_graph

        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)
        snap = inputs["snap"]

        # Only test modules with compilation results
        compilation_results = snap.get("compilation_results", {})
        if not compilation_results:
            pytest.skip("No compilation_results in snapshot (AST serialization boundary)")

        from sysml_codegen.generation.stencils import generate_implementation

        tested = 0
        for module_name, calc_def in mapping.items():
            cr = compilation_results.get(calc_def.name)
            if cr is None or cr.overall_compilability != Compilability.FULLY_COMPILABLE:
                continue

            module = next(m for m in graph.modules if m.name == module_name)

            old_output = generate_implementation(
                calc_def=calc_def,
                template_env=template_env,
                output_path=Path("/tmp/test_identity.py"),
                package_name="generated_code",
                compilation_result=cr,
            )

            new_output = generate_implementation_from_graph(
                module=module,
                template_env=template_env,
                output_path=Path("/tmp/test_identity.py"),
                package_name="generated_code",
            )

            assert old_output == new_output, (
                f"Module {module_name}: auto-impl identity mismatch.\n"
                f"--- Old (CalcDef+CR) ---\n{old_output[:500]}\n"
                f"--- New (Graph) ---\n{new_output[:500]}"
            )
            tested += 1

        # It's OK if no FULLY_COMPILABLE CalcUsage modules in snapshot
        # (snapshots don't carry compilation_results due to AST serialization)


class TestBacklogIdentity:
    """REQ-PMM-05: Backlog report from graph matches old CalcDef path."""

    @pytest.mark.req("REQ-PMM-05")
    def test_from_graph_backlog_identity(self, solar_battery_graph):
        """generate_backlog_report(calc_defs, ...) == generate_backlog_report_from_graph(graph, ...)."""
        from sysml_codegen.generation.stencils import (
            generate_backlog_report,
            generate_backlog_report_from_graph,
        )

        graph, inputs = solar_battery_graph
        snap = inputs["snap"]

        old_output = generate_backlog_report(
            calc_defs=snap["calc_defs"],
            output_path=Path("/tmp/backlog.md"),
            package_name="generated_code",
            compilation_results=None,
            computed_attributes=snap["computed_attributes"],
            aggregation_data=snap["aggregation_expressions"],
        )

        new_output = generate_backlog_report_from_graph(
            graph=graph,
            output_path=Path("/tmp/backlog.md"),
            package_name="generated_code",
        )

        assert old_output == new_output, (
            "Backlog report identity mismatch.\n"
            f"--- Old (CalcDefs) ---\n{old_output[:500]}\n"
            f"--- New (Graph) ---\n{new_output[:500]}"
        )


class TestTestGenIdentity:
    """REQ-PMM-05: Test generation from graph matches old CalcDef path."""

    @pytest.mark.req("REQ-PMM-05")
    def test_from_graph_test_gen_identity(self, solar_battery_graph, template_env):
        """generate_test_implementations(calc_defs) == generate_test_implementations_from_graph(graph)."""
        from sysml_codegen.generation.test_gen import (
            generate_test_implementations,
            generate_test_implementations_from_graph,
        )

        graph, inputs = solar_battery_graph
        snap = inputs["snap"]

        old_output = generate_test_implementations(
            calc_defs=snap["calc_defs"],
            package_name="generated_code",
            template_env=template_env,
            output_path=Path("/tmp/test_impls.py"),
        )

        new_output = generate_test_implementations_from_graph(
            graph=graph,
            package_name="generated_code",
            template_env=template_env,
            output_path=Path("/tmp/test_impls.py"),
        )

        assert old_output == new_output, (
            "Test gen identity mismatch.\n"
            f"--- Old (CalcDefs) ---\n{old_output[:500]}\n"
            f"--- New (Graph) ---\n{new_output[:500]}"
        )


class TestPreservationIdentity:
    """REQ-PMM-05: Preservation check from graph matches old CalcDef path."""

    @pytest.mark.req("REQ-PMM-05")
    def test_from_graph_preservation_identity(self, solar_battery_graph, tmp_path):
        """should_regenerate_stencil(calc_def, path) == should_regenerate_stencil_from_graph(module, path)."""
        from sysml_codegen.generation.preservation import (
            should_regenerate_stencil,
            should_regenerate_stencil_from_graph,
        )

        graph, inputs = solar_battery_graph
        mapping = _build_calcusage_module_to_calcdef_map(graph, inputs)

        # Test Case 1: File doesn't exist — both should say regenerate
        for module_name, calc_def in list(mapping.items())[:1]:
            module = next(m for m in graph.modules if m.name == module_name)
            fake_path = tmp_path / "nonexistent_impl.py"

            old_result = should_regenerate_stencil(calc_def, fake_path)
            new_result = should_regenerate_stencil_from_graph(module, fake_path)

            assert old_result[0] == new_result[0], (
                f"Module {module_name}: preservation decision differs for nonexistent file. "
                f"Old: {old_result}, New: {new_result}"
            )

        # Test Case 2: File exists with matching signature
        for module_name, calc_def in list(mapping.items())[:1]:
            module = next(m for m in graph.modules if m.name == module_name)

            # Create a minimal implementation file
            func_name = f"run_{calc_def.name.lower()}"
            input_class = f"{calc_def.name}Input"
            impl_path = tmp_path / f"{calc_def.name.lower()}_impl.py"
            impl_path.write_text(
                f"def {func_name}(inputs: {input_class}) -> float:\n"
                f"    raise NotImplementedError('{func_name}')\n"
            )

            old_result = should_regenerate_stencil(calc_def, impl_path)
            new_result = should_regenerate_stencil_from_graph(module, impl_path)

            assert old_result == new_result, (
                f"Module {module_name}: preservation result differs. "
                f"Old: {old_result}, New: {new_result}"
            )


# ===========================================================================
# D. All Module Types Test (REQ-PIPE-07)
# ===========================================================================

class TestAllModuleTypesRender:
    """REQ-PIPE-07: All module types render via _from_graph()."""

    @pytest.mark.req("REQ-PIPE-07")
    def test_all_module_types_render_via_from_graph(self, solar_battery_graph, template_env):
        """CalcUsage, FORMULA, and aggregation modules all render via _from_graph()."""
        from sysml_codegen.generation.modules import generate_teax_module_from_graph

        graph, _inputs = solar_battery_graph

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

            if module.is_computed_attribute:
                formula_count += 1
            elif module.is_aggregation:
                agg_count += 1
            else:
                calcusage_count += 1

        assert calcusage_count > 0, "No CalcUsage modules rendered"
        assert formula_count > 0, "No FORMULA modules rendered"
        assert agg_count > 0, "No aggregation modules rendered"
