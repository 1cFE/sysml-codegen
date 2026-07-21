"""End-to-end integration tests for hierarchy bugfixes (BF-1 through BF-7).

Validates extraction, wiring, and codegen against the real solar_battery_model
SysML fixture. These tests complement the mock-based unit tests by running the
actual pipeline on real SysIDE AST data.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.generation.initialization import PipelineContext
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from sysml_codegen.resolution.models import ModuleKind

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

        agg_modules = [m for m in graph.modules if m.module_kind == ModuleKind.AGGREGATION]
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

    @pytest.fixture(scope="class")
    def codegen_agg_filenames(self) -> set[str]:
        """Get aggregation module filenames from computation graph metadata."""
        model_path = FIXTURES_DIR / "solar_battery_model"
        ctx = build_pipeline_context([model_path])
        return {
            m.calc_def_name.lower() + ".py"
            for m in ctx.computation_graph.modules
            if m.module_kind == ModuleKind.AGGREGATION
        }

    def test_bf3_aggregation_wrappers_have_inputs(
        self, codegen_output: Path, codegen_agg_filenames: set[str],
    ):
        """BF-3: Aggregation module wrapper files should have real inputs
        (not just empty Input classes)."""
        modules_dir = codegen_output / "modules"
        assert modules_dir.exists(), f"modules dir missing: {codegen_output}"

        # Identify aggregation wrappers by matching filenames from the
        # computation graph (graph-only approach per REQ-PIPE-07).
        agg_wrappers = []
        for py_file in modules_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if py_file.name in codegen_agg_filenames:
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
        self, codegen_output: Path, codegen_agg_filenames: set[str],
    ):
        """BF-4/5: Module wrapper directories should use design-instance paths
        (contain 'solar_battery_plant'), not library-level PartDef paths."""
        modules_dir = codegen_output / "modules"
        assert modules_dir.exists()

        # Find aggregation-related module files via graph metadata
        agg_files = []
        for py_file in modules_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if py_file.name in codegen_agg_filenames:
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


# ---------------------------------------------------------------------------
# Class 4: Aggregation FCE/OE ordering validation
# ---------------------------------------------------------------------------


class TestAggregationFCEOrdering:
    """Validates Bug A fix: FeatureChainExpression check before OperatorExpression.

    In SysIDE's type system, FCE is a subtype of OE — both is_instance() checks
    return True on the same node. The FCE check must come first in all dispatch
    sites to prevent dotted refs like array_bos.capital_cost from entering the
    OE handler and being misclassified.

    These tests use the real solar_battery fixture because mock classes cannot
    reproduce the FCE/OE subtype relationship.
    """

    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_fce_nodes_classified_as_singleton_terms(
        self, pipeline_context: PipelineContext,
    ):
        """Bug A1: FeatureChainExpression nodes must classify as SingletonTerms,
        not LocalTerms. FCE is a subtype of OE in SysIDE's type system — the
        FCE check must run before OE to prevent dotted refs like
        array_bos.capital_cost from entering the OE handler.

        Spike B verified: {sum: 12, singleton: 37, local: 9}."""
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        total_sum = sum(
            len(a.sum_terms) for a in hierarchy.aggregation_expressions
        )
        total_singleton = sum(
            len(a.singleton_terms) for a in hierarchy.aggregation_expressions
        )
        total_local = sum(
            len(a.local_terms) for a in hierarchy.aggregation_expressions
        )

        assert total_sum == 12, (
            f"SumTerm count {total_sum} != 12 (regression)"
        )
        assert total_singleton == 37, (
            f"SingletonTerm count {total_singleton} != 37 (FCE misclassified)"
        )
        assert total_local == 9, (
            f"LocalTerm count {total_local} != 9 (FCE misclassified)"
        )

    def test_singleton_terms_have_dotted_source_paths(
        self, pipeline_context: PipelineContext,
    ):
        """Bug A1: SingletonTerms from FCE nodes must have dotted source paths
        (e.g., 'allocation_model.total_allocation'), not bare names."""
        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None

        for agg in hierarchy.aggregation_expressions:
            for st in agg.singleton_terms:
                assert "." in st.source_path, (
                    f"SingletonTerm in {agg.owning_part_name}.{agg.attribute_name} "
                    f"has bare source_path '{st.source_path}' — FCE misclassified as FRE"
                )

    def test_no_unsupported_dot_operator_in_compilation(
        self, pipeline_context: PipelineContext,
    ):
        """Bug A2: FCE nodes must not produce 'unsupported operator: .' diagnostic.
        This happens when FCE enters the OE handler in syside->IR dispatch."""
        for calc_name, comp_result in pipeline_context.compilation_results.items():
            for output_result in comp_result.output_results:
                if output_result.unsupported_reason:
                    assert "unsupported operator: ." not in output_result.unsupported_reason, (
                        f"CalcDef '{calc_name}' output '{output_result.output_name}' "
                        f"has Bug A2 artifact: {output_result.unsupported_reason}"
                    )

    def test_no_mangled_dot_parenthesized_expressions(
        self, pipeline_context: PipelineContext,
    ):
        """Bug A3: FCE nodes must not produce '.(name)' mangled text.
        This happens when FCE enters reconstruct_operator_expression()."""
        import re
        mangled_pattern = re.compile(r"\.\([a-zA-Z_]+\)")

        hierarchy = pipeline_context.hierarchy_data
        assert hierarchy is not None
        for agg in hierarchy.aggregation_expressions:
            assert not mangled_pattern.search(agg.transformed_expression), (
                f"Aggregation {agg.owning_part_name}.{agg.attribute_name} "
                f"has Bug A3 artifact in: {agg.transformed_expression}"
            )


# ---------------------------------------------------------------------------
# Class 5: Aggregation LITERAL redefinition + EXPOSE_PURE alias wiring
# ---------------------------------------------------------------------------


class TestAggregationLiteralAndAlias:
    """Validates Fix A (LITERAL redefinition propagation) and Fix B
    (EXPOSE_PURE alias resolution) in aggregation builder.

    Fix A: Permitting defines `:>> raw_material_cost = 0.0` etc. — these
    LITERAL redefinitions should propagate as entry point default_value.

    Fix B: Solar Array defines `misc_hardware_cost = allocation_model.total_allocation`
    (EXPOSE_PURE alias) — should wire to the allocation_model module output,
    not fall through to an entry point.
    """

    @pytest.fixture(scope="class")
    def pipeline_context(self) -> PipelineContext:
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    def test_permitting_literal_redefinitions_have_defaults(
        self, pipeline_context: PipelineContext,
    ):
        """Fix A: Permitting sub-costs (raw_material_cost, fabrication_cost,
        installation_cost) with `:>> attr = 0.0` should produce entry points
        with default_value == 0.0, not None."""
        graph = pipeline_context.computation_graph

        # Find site_infra aggregation modules (they reference permitting sub-costs)
        site_infra_aggs = [
            m for m in graph.modules
            if m.module_kind == ModuleKind.AGGREGATION and "site_infra" in m.name.lower()
        ]
        assert site_infra_aggs, (
            f"Expected site_infra aggregation modules. "
            f"Aggregation modules: {[m.name for m in graph.modules if m.module_kind == ModuleKind.AGGREGATION]}"
        )

        # Collect entry point qualified names from site_infra aggregation inputs
        # that reference permitting sub-costs
        permitting_cost_attrs = {"raw_material_cost", "fabrication_cost", "installation_cost"}
        found_defaults: dict[str, float | None] = {}

        for module in site_infra_aggs:
            for inp in module.inputs:
                # Check if this input references a permitting cost attribute
                for attr in permitting_cost_attrs:
                    if attr in inp.param_name and "permitting" in inp.param_name:
                        if inp.source.source_type == "entry_point" and inp.source.qualified_name:
                            ep = pipeline_context.computation_graph.entry_point_groups
                            # Look up the entry point default from the groups
                            for group in ep:
                                for param in group.parameters:
                                    if param.qualified_name == inp.source.qualified_name:
                                        found_defaults[attr] = param.default_value

        # At least some permitting cost entry points should have been found
        assert found_defaults, (
            f"Expected to find permitting cost entry points in site_infra agg modules. "
            f"Site infra agg input names: "
            f"{[inp.param_name for m in site_infra_aggs for inp in m.inputs]}"
        )

        # Each found entry point should have default_value == 0.0
        for attr, default in found_defaults.items():
            assert default == 0.0, (
                f"Permitting '{attr}' entry point default_value should be 0.0, got {default}"
            )

    def test_misc_hardware_cost_wired_to_module_output(
        self, pipeline_context: PipelineContext,
    ):
        """Fix B: Solar Array's misc_hardware_cost should be wired to
        allocation_model's total_allocation output (module_output), NOT
        an entry_point."""
        graph = pipeline_context.computation_graph

        # Find the solar_array capital_cost aggregation module
        solar_array_capital = [
            m for m in graph.modules
            if m.module_kind == ModuleKind.AGGREGATION
            and "solar_array" in m.name.lower()
            and "capital_cost" in m.name.lower()
        ]
        assert solar_array_capital, (
            f"Expected solar_array capital_cost aggregation module. "
            f"Aggregation modules: {[m.name for m in graph.modules if m.module_kind == ModuleKind.AGGREGATION]}"
        )

        module = solar_array_capital[0]

        # Find the misc_hardware_cost input
        misc_hw_inputs = [
            inp for inp in module.inputs
            if inp.param_name == "misc_hardware_cost"
        ]
        assert misc_hw_inputs, (
            f"Expected 'misc_hardware_cost' input on {module.name}. "
            f"Inputs: {[i.param_name for i in module.inputs]}"
        )

        misc_hw_input = misc_hw_inputs[0]
        assert misc_hw_input.source.source_type == "module_output", (
            f"misc_hardware_cost should be wired as module_output "
            f"(from allocation_model), not '{misc_hw_input.source.source_type}'. "
            f"Source: {misc_hw_input.source}"
        )

        # Verify the channel references allocation_model and total_allocation
        channel = misc_hw_input.source.producer_channel
        assert channel is not None, "producer_channel should not be None"
        assert "allocation_model" in channel, (
            f"Channel should reference allocation_model, got: {channel}"
        )
        assert "total_allocation" in channel, (
            f"Channel should reference total_allocation, got: {channel}"
        )

    def test_no_none_default_aggregation_cost_entry_points(
        self, pipeline_context: PipelineContext,
    ):
        """Fix A+B: Aggregation cost inputs that fall back to entry points
        should have non-None defaults (from LITERAL redefinitions) or be
        wired to module_output (from EXPOSE_PURE aliases).

        Multiplicity entry points (module_count, etc.) are excluded from
        this check since they have their own default propagation path.
        """
        graph = pipeline_context.computation_graph

        # Collect all aggregation module entry-point inputs with None defaults
        none_default_eps: list[str] = []
        multiplicity_names = {"module_count", "inverter_count", "pack_count",
                              "string_count", "cell_count"}

        for module in graph.modules:
            if module.module_kind != ModuleKind.AGGREGATION:
                continue
            for inp in module.inputs:
                if inp.source.source_type != "entry_point":
                    continue
                if inp.param_name in multiplicity_names:
                    continue
                # Look up the entry point to check default_value
                ep_qn = inp.source.qualified_name
                if ep_qn:
                    ep_default = None
                    for group in graph.entry_point_groups:
                        for param in group.parameters:
                            if param.qualified_name == ep_qn:
                                ep_default = param.default_value
                                break
                    if ep_default is None:
                        none_default_eps.append(
                            f"{module.name}.{inp.param_name} (ep={ep_qn})"
                        )

        # Allow a baseline of known None-default entry points (library params, etc.)
        # The permitting sub-costs and misc_hardware_cost should NOT be in this list.
        for ep_desc in none_default_eps:
            assert "raw_material_cost" not in ep_desc, (
                f"raw_material_cost should have default from LITERAL redef: {ep_desc}"
            )
            assert "fabrication_cost" not in ep_desc, (
                f"fabrication_cost should have default from LITERAL redef: {ep_desc}"
            )
            assert "installation_cost" not in ep_desc, (
                f"installation_cost should have default from LITERAL redef: {ep_desc}"
            )
            assert "misc_hardware_cost" not in ep_desc, (
                f"misc_hardware_cost should be wired to module_output, not entry_point: {ep_desc}"
            )
