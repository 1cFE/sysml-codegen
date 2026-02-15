"""End-to-end integration tests for hierarchy bugfixes (BF-1 through BF-7).

Validates extraction, wiring, and codegen against the real solar_battery_model
SysML fixture. These tests complement the mock-based unit tests by running the
actual pipeline on real SysIDE AST data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.generation.initialization import PipelineContext, build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

# Assembly PartDef short names that should produce aggregation expressions
EXPECTED_ASSEMBLIES = {"Solar_Array", "Battery_System", "Solar_Battery_Plant"}

# Parts with parameterized multiplicities (arrayed children)
ARRAYED_PARTS = {"pv_module", "inverter", "battery_pack"}


# ---------------------------------------------------------------------------
# Class 1: Extraction-layer E2E validation
# ---------------------------------------------------------------------------


class TestHierarchyExtractionE2E:
    """Validates hierarchy extraction against real SysIDE AST."""

    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_aggregation_expressions_extracted(
        self, pipeline_context: PipelineContext,
    ):
        """Baseline: aggregation expressions are non-empty and multiplicities
        exist for arrayed parts."""
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None, "hierarchy_data should be populated"
        assert len(hierarchy.aggregation_expressions) > 0, (
            "Expected at least one aggregation expression"
        )

        # Multiplicities should exist for arrayed child parts
        mult_names = {m.part_usage_name for m in hierarchy.multiplicities}
        for part_name in ARRAYED_PARTS:
            assert part_name in mult_names, (
                f"Expected multiplicity for arrayed part '{part_name}', "
                f"got: {mult_names}"
            )

    def test_bf1_no_unsupported_nodes(
        self, pipeline_context: PipelineContext,
    ):
        """BF-1: All aggregation expressions should be fully transformed
        (no unsupported AST nodes, no 'Evaluation' artifacts)."""
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        for agg in hierarchy.aggregation_expressions:
            assert not agg.has_unsupported_nodes, (
                f"Aggregation '{agg.owning_part_name}.{agg.attribute_name}' "
                f"has unsupported nodes"
            )
            assert "Evaluation" not in agg.transformed_expression, (
                f"Aggregation '{agg.owning_part_name}.{agg.attribute_name}' "
                f"contains 'Evaluation' artifact in transformed expression: "
                f"{agg.transformed_expression}"
            )

    def test_bf1_sum_terms_have_real_names(
        self, pipeline_context: PipelineContext,
    ):
        """BF-1: sum_terms[].part_usage_name should be real part names,
        not garbage from failed AST traversal."""
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        # Collect all sum term part names across all expressions
        all_sum_part_names = set()
        for agg in hierarchy.aggregation_expressions:
            for term in agg.sum_terms:
                all_sum_part_names.add(term.part_usage_name)

        # At least some arrayed parts should appear as sum terms
        assert all_sum_part_names & ARRAYED_PARTS, (
            f"Expected some arrayed parts in sum terms, "
            f"got: {all_sum_part_names}"
        )

        # No sum term name should be empty or look like an AST artifact
        for name in all_sum_part_names:
            assert name, "sum term part_usage_name should not be empty"
            assert "Evaluation" not in name, (
                f"sum term part_usage_name '{name}' looks like an AST artifact"
            )

    def test_bf6_all_assemblies_scoped(
        self, pipeline_context: PipelineContext,
    ):
        """BF-6: Aggregation expressions should cover Solar Array,
        Battery System, and Solar Battery Plant instance paths.

        Note: Site Infrastructure has zero multiplicity children (all singletons).
        If it's missing, that confirms the mock-test gap documented in the plan.
        """
        scoped = pipeline_context.aggregation_expressions
        scoped_instance_paths = {s.instance_path for s in scoped}

        # These assemblies should be scoped to design instances
        for assembly in EXPECTED_ASSEMBLIES:
            matching = [p for p in scoped_instance_paths if assembly.lower() in p.lower()]
            assert matching, (
                f"No scoped aggregation found for assembly '{assembly}'. "
                f"Scoped paths: {sorted(scoped_instance_paths)}"
            )

    def test_bf7_capital_cost_aggregation_exists(
        self, pipeline_context: PipelineContext,
    ):
        """BF-7: Solar Battery Plant's capital_cost aggregation is extracted.

        The 'total_capex' param_name alias was previously enriched by Step 3.6
        (_enrich_aliases_from_bindings), but Phase 1 diagnostic confirmed it is
        redundant with OutputRegistry Phase 1b BF-7 registration. Step 3.6
        was removed as dead code. The aggregation itself is the important
        extraction result; resolution of 'total_capex' bindings is validated
        by E2E YAML diff tests.
        """
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        # Find Solar Battery Plant's capital_cost aggregation
        plant_capital = [
            agg for agg in hierarchy.aggregation_expressions
            if "Solar_Battery_Plant" in agg.owning_part_qn
            and agg.attribute_name == "capital_cost"
        ]
        assert plant_capital, (
            "Expected aggregation for Solar_Battery_Plant.capital_cost"
        )


# ---------------------------------------------------------------------------
# Class 2: Computation graph wiring E2E validation
# ---------------------------------------------------------------------------


class TestHierarchyWiringE2E:
    """Validates computation graph wiring for hierarchy features."""

    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_bf7_total_capex_wired_to_module_output(
        self, pipeline_context: PipelineContext,
    ):
        """BF-7: annualized_financial's total_capex input should be wired to
        an upstream module_output (from capital_cost aggregation), NOT an
        entry_point."""
        graph = pipeline_context.computation_graph

        # Find the annualized_financial module (full name contains
        # 'annualized_financial' with underscore)
        fin_modules = [
            m for m in graph.modules
            if "annualized_financial" in m.name
        ]
        assert fin_modules, (
            f"Expected annualized_financial module in graph. "
            f"Module names: {[m.name for m in graph.modules]}"
        )

        fin_module = fin_modules[0]

        # Find its total_capex input
        capex_inputs = [
            inp for inp in fin_module.inputs
            if inp.param_name == "total_capex"
        ]
        assert capex_inputs, (
            f"Expected 'total_capex' input on {fin_module.name}. "
            f"Inputs: {[i.param_name for i in fin_module.inputs]}"
        )

        capex_input = capex_inputs[0]
        assert capex_input.source.source_type == "module_output", (
            f"total_capex should be wired as module_output (from aggregation), "
            f"not '{capex_input.source.source_type}'. "
            f"Source: {capex_input.source}"
        )

    def test_aggregation_modules_in_graph(
        self, pipeline_context: PipelineContext,
    ):
        """BF-1/3: Aggregation modules for cost attributes (capital_cost,
        raw_material_cost, etc.) should exist in graph with non-empty inputs.

        Note: idiot_index aggregations (capital_cost / raw_material_cost) may
        have zero inputs since they reference self-attributes; we exclude those.
        """
        graph = pipeline_context.computation_graph

        agg_modules = [m for m in graph.modules if m.is_aggregation]
        assert len(agg_modules) > 0, (
            "Expected at least one aggregation module in computation graph"
        )

        # Cost-attribute aggregation modules (not idiot_index) should have inputs
        cost_agg_modules = [
            m for m in agg_modules
            if "idiot_index" not in m.name
        ]
        assert len(cost_agg_modules) > 0, (
            "Expected at least one cost-attribute aggregation module"
        )

        for module in cost_agg_modules:
            assert len(module.inputs) > 0, (
                f"Aggregation module '{module.name}' has no inputs"
            )


# ---------------------------------------------------------------------------
# Class 3: Codegen output E2E validation
# ---------------------------------------------------------------------------


class TestHierarchyCodegenE2E:
    """Validates generated file structure after full codegen."""

    @pytest.fixture(scope="class")
    def codegen_output(self, tmp_path_factory: pytest.TempPathFactory) -> Path:
        model_path = FIXTURES_DIR / "solar_battery_model"
        output_path = tmp_path_factory.mktemp("hierarchy_e2e")
        config = GenerationConfig(
            models_path=model_path,
            output_path=output_path,
            package_name="solar_battery",
        )
        success = run_codegen(config)
        assert success, "Solar battery codegen should succeed"
        return output_path

    def test_bf3_aggregation_wrappers_have_inputs(
        self, codegen_output: Path,
    ):
        """BF-3: Aggregation module wrapper files should have real inputs
        (not just empty Input classes)."""
        modules_dir = codegen_output / "modules"
        assert modules_dir.exists(), f"modules dir missing: {codegen_output}"

        # Aggregation wrappers are identified by "aggregation" in their content
        # and containing an Input class (named like capital_costInput)
        agg_wrappers = []
        for py_file in modules_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            content = py_file.read_text()
            if "aggregation" in content.lower() and "Input(BaseModel)" in content:
                agg_wrappers.append(py_file)

        assert agg_wrappers, (
            "Expected at least one aggregation module wrapper file"
        )

        # Check that at least some wrappers have non-empty Input classes
        # (idiot_index has empty inputs, but capital_cost etc. should not)
        wrappers_with_inputs = []
        for wrapper in agg_wrappers:
            content = wrapper.read_text()
            # Check if the Input class has Field(...) declarations
            if "Field(" in content:
                wrappers_with_inputs.append(wrapper)

        assert wrappers_with_inputs, (
            "Expected at least one aggregation wrapper with non-empty inputs. "
            f"Wrappers found: {[w.name for w in agg_wrappers]}"
        )

    def test_bf4_bf5_instance_scoped_paths(
        self, codegen_output: Path,
    ):
        """BF-4/5: Module wrapper directories should use design-instance paths
        (contain 'solar_battery_plant'), not library-level PartDef paths."""
        modules_dir = codegen_output / "modules"
        assert modules_dir.exists()

        # Find aggregation-related module files
        agg_files = []
        for py_file in modules_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            content = py_file.read_text()
            if "aggregation" in content.lower() and "Input(BaseModel)" in content:
                agg_files.append(py_file)

        assert agg_files, "Expected at least one aggregation module file"

        for agg_file in agg_files:
            # The file path should reference the design instance
            file_path_str = str(agg_file).lower()
            assert "solar_battery_plant" in file_path_str, (
                f"Aggregation module should use design-instance path "
                f"(contain 'solar_battery_plant'), got: {agg_file}"
            )

    def test_aggregation_yaml_no_evaluation_artifacts(
        self, codegen_output: Path,
    ):
        """BF-1: Pipeline YAML input channel names should not contain
        'Evaluation()' artifacts."""
        pipelines_dir = codegen_output / "pipelines"
        assert pipelines_dir.exists(), f"pipelines dir missing: {codegen_output}"

        yaml_files = list(pipelines_dir.glob("*.yaml"))
        assert yaml_files, "Expected at least one pipeline YAML file"

        for yaml_file in yaml_files:
            content = yaml_file.read_text()
            assert "Evaluation" not in content, (
                f"Pipeline YAML {yaml_file.name} contains 'Evaluation' artifact"
            )
