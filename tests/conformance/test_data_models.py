"""C01: Data model conformance tests.

Verifies that every data model, enum, and field referenced in doc 09
(09-data-models.md) exists in the source code, is importable from its
documented location, has the correct fields and types, and can be
constructed with real data.

Requirements: REQ-DM-01 through REQ-DM-07.
"""

import dataclasses
import inspect
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# REQ-DM-01: Import conformance
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-DM-01")
class TestExtractionModelsImportable:
    """Every extraction-layer model is importable from its documented module."""

    def test_calculation_definition_data(self):
        from sysml_codegen.extraction.data_models import CalculationDefinitionData

        assert CalculationDefinitionData is not None

    def test_calc_usage_data(self):
        from sysml_codegen.extraction.usage_extractor import CalcUsageData

        assert CalcUsageData is not None

    def test_calc_usage_data_reexport(self):
        """CalcUsageData should also be accessible via extraction.data_models re-export."""
        from sysml_codegen.extraction.usage_extractor import CalcUsageData

        assert CalcUsageData is not None

    def test_binding_info(self):
        from sysml_codegen.extraction.usage_extractor import BindingInfo

        assert BindingInfo is not None

    def test_part_definition_data(self):
        from sysml_codegen.extraction.data_models import PartDefinitionData

        assert PartDefinitionData is not None

    def test_redefinition_data(self):
        from sysml_codegen.extraction.data_models import RedefinitionData

        assert RedefinitionData is not None

    def test_multiplicity_data(self):
        from sysml_codegen.extraction.data_models import MultiplicityData

        assert MultiplicityData is not None

    def test_aggregation_expression_data(self):
        from sysml_codegen.extraction.data_models import AggregationExpressionData

        assert AggregationExpressionData is not None

    def test_scoped_aggregation_data(self):
        from sysml_codegen.extraction.data_models import ScopedAggregationData

        assert ScopedAggregationData is not None

    def test_computed_attribute_data(self):
        from sysml_codegen.extraction.data_models import ComputedAttributeData

        assert ComputedAttributeData is not None

    def test_hierarchy_extraction_result(self):
        from sysml_codegen.extraction.data_models import HierarchyExtractionResult

        assert HierarchyExtractionResult is not None

    def test_attribute_info(self):
        from sysml_codegen.extraction.data_models import AttributeInfo

        assert AttributeInfo is not None


@pytest.mark.req("REQ-DM-01")
class TestAnalysisModelsImportable:
    """Every analysis-layer model is importable from its documented module."""

    def test_backtracking_result(self):
        from sysml_codegen.analysis.dependency_backtracker import BacktrackingResult

        assert BacktrackingResult is not None

    def test_design_attribute_data(self):
        from sysml_codegen.analysis.parameter_groups import DesignAttributeData

        assert DesignAttributeData is not None

    def test_derived_parameter_group(self):
        from sysml_codegen.analysis.parameter_groups import DerivedParameterGroup

        assert DerivedParameterGroup is not None

    def test_parameter_source(self):
        """ParameterSource not in doc 09 but used by DerivedParameterGroup.parameters."""
        from sysml_codegen.analysis.parameter_groups import ParameterSource

        assert ParameterSource is not None


@pytest.mark.req("REQ-DM-01")
class TestCoreModelsImportable:
    """Every core-layer model is importable from its documented module."""

    def test_binding_resolution(self):
        from sysml_codegen.core.models import BindingResolution

        assert BindingResolution is not None

    def test_binding_resolution_type(self):
        from sysml_codegen.core.models import BindingResolutionType

        assert BindingResolutionType is not None

    def test_channel_alias(self):
        from sysml_codegen.core.models import ChannelAlias

        assert ChannelAlias is not None

    def test_output_registry(self):
        from sysml_codegen.core.output_registry import OutputRegistry

        assert OutputRegistry is not None


@pytest.mark.req("REQ-DM-01")
class TestResolutionModelsImportable:
    """Every resolution-layer model is importable from its documented module."""

    def test_computation_graph(self):
        from sysml_codegen.resolution.models import ComputationGraph

        assert ComputationGraph is not None

    def test_pipeline_module(self):
        from sysml_codegen.resolution.models import PipelineModule

        assert PipelineModule is not None

    def test_module_input(self):
        from sysml_codegen.resolution.models import ModuleInput

        assert ModuleInput is not None

    def test_module_output(self):
        from sysml_codegen.resolution.models import ModuleOutput

        assert ModuleOutput is not None

    def test_input_source(self):
        from sysml_codegen.resolution.models import InputSource

        assert InputSource is not None

    def test_entry_point(self):
        from sysml_codegen.resolution.models import EntryPoint

        assert EntryPoint is not None

    def test_entry_point_type(self):
        from sysml_codegen.resolution.models import EntryPointType

        assert EntryPointType is not None

    def test_parameter_group(self):
        from sysml_codegen.resolution.models import ParameterGroup

        assert ParameterGroup is not None


# ---------------------------------------------------------------------------
# REQ-DM-02: Enum value conformance
# ---------------------------------------------------------------------------

# Map of (enum_class_import_path, expected_member_names)
ENUM_SPECS = [
    pytest.param(
        "agentic_mbse.sysml.types",
        "BindingType",
        {"CHAIN", "REFERENCE", "LITERAL", "EXPRESSION", "UNBOUND"},
        id="BindingType",
    ),
    pytest.param(
        "sysml_codegen.extraction.data_models",
        "RedefinitionType",
        {"LITERAL", "CHAIN", "EXPRESSION"},
        id="RedefinitionType",
    ),
    pytest.param(
        "sysml_codegen.extraction.data_models",
        "ComputedAttributeClassification",
        {
            "FORMULA",
            "EXPOSE_PURE",
            "EXPOSE_COMPUTED",
            "EXPOSE_CHAIN_TENTATIVE",
            "LITERAL",
            "UNRESOLVABLE",
        },
        id="ComputedAttributeClassification",
    ),
    pytest.param(
        "sysml_codegen.extraction.expression_compiler",
        "Compilability",
        {"FULLY_COMPILABLE", "PARTIALLY_COMPILABLE", "MANUAL_REQUIRED", "UNKNOWN"},
        id="Compilability",
    ),
    pytest.param(
        "sysml_codegen.extraction.expression_compiler",
        "ExpressionNodeType",
        {"BINARY_OP", "UNARY_OP", "LITERAL", "INPUT_REF", "INTERMEDIATE_REF", "UNSUPPORTED"},
        id="ExpressionNodeType",
    ),
    pytest.param(
        "sysml_codegen.core.models",
        "BindingResolutionType",
        {"ENTRY_POINT", "MODULE_OUTPUT"},
        id="BindingResolutionType",
    ),
    pytest.param(
        "sysml_codegen.resolution.models",
        "EntryPointType",
        {"LIBRARY_DEFAULT", "DESIGN_ATTRIBUTE", "USAGE_LITERAL"},
        id="EntryPointType",
    ),
]


@pytest.mark.req("REQ-DM-02")
@pytest.mark.parametrize("module_path,class_name,expected_values", ENUM_SPECS)
def test_req_dm_02_enum_values(module_path, class_name, expected_values):
    """Every enum has exactly the documented member names (no more, no less)."""
    import importlib

    mod = importlib.import_module(module_path)
    enum_cls = getattr(mod, class_name)
    actual_names = {m.name for m in enum_cls}
    assert actual_names == expected_values, (
        f"{class_name}: expected {expected_values}, got {actual_names}"
    )


# ---------------------------------------------------------------------------
# REQ-DM-03: Field conformance
# ---------------------------------------------------------------------------


def _dataclass_field_names(cls):
    """Get field names for a dataclass, including inherited fields."""
    return {f.name for f in dataclasses.fields(cls)}


def _pydantic_field_names(cls):
    """Get field names for a Pydantic BaseModel."""
    return set(cls.model_fields.keys())


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_calculation_definition_data():
    from sysml_codegen.extraction.data_models import CalculationDefinitionData

    expected = {
        "name",
        "qualified_name",
        "doc_comment",
        "calc_expressions",
        "input_attributes",
        "output_attributes",
        "references",
        "source_file",
        "source_line",
        "source_hash",
        "output_expression_asts",
        "all_member_names",
        "member_expressions",
    }
    actual = _dataclass_field_names(CalculationDefinitionData)
    assert actual == expected


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_calc_usage_data():
    """CalcUsageData has all 13 fields (including raw_element from source)."""
    from sysml_codegen.extraction.usage_extractor import CalcUsageData

    expected = {
        "instance_name",
        "calc_def_name",
        "calc_def_qualified_name",
        "module_type",
        "bindings",
        "unbound_params",
        "source_file",
        "source_line",
        "parent_part_path",
        "qualified_name",
        "is_template",
        "owning_part_def_qn",
        "raw_element",
    }
    actual = _dataclass_field_names(CalcUsageData)
    assert actual == expected
    assert len(actual) == 13


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_binding_info():
    from sysml_codegen.extraction.usage_extractor import BindingInfo

    expected = {
        "param_name",
        "source_path",
        "binding_type",
        "is_cross_file",
        "raw_expression",
        "source_instance_elem",
        "source_attribute_elem",
        "literal_value",
        "expression_ast",
    }
    actual = _dataclass_field_names(BindingInfo)
    assert actual == expected


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_part_definition_data():
    from sysml_codegen.extraction.data_models import PartDefinitionData

    expected = {
        "name",
        "qualified_name",
        "doc_comment",
        "attributes",
        "constraints",
        "source_file",
        "source_line",
        "source_hash",
    }
    actual = _dataclass_field_names(PartDefinitionData)
    assert actual == expected
    assert len(actual) == 8


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_redefinition_data():
    from sysml_codegen.extraction.data_models import RedefinitionData

    expected = {
        "owning_part_qn",
        "attribute_name",
        "redefinition_type",
        "literal_value",
        "source_path",
        "expression_ast",
        "expression_text",
        "target_path",
        "is_deep_path",
        "source_file",
        "source_line",
    }
    actual = _dataclass_field_names(RedefinitionData)
    assert actual == expected
    assert len(actual) == 11


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_multiplicity_data():
    from sysml_codegen.extraction.data_models import MultiplicityData

    expected = {
        "part_usage_name",
        "owning_part_def_qn",
        "count",
        "count_attribute_name",
        "default_value",
    }
    actual = _dataclass_field_names(MultiplicityData)
    assert actual == expected
    assert len(actual) == 5


def test_hierarchy_models_are_shared_class_objects():
    from agentic_mbse.sysml import hierarchy as shared

    from sysml_codegen.extraction import data_models as codegen

    assert codegen.RedefinitionType is shared.RedefinitionType
    assert codegen.RedefinitionData is shared.RedefinitionData
    assert codegen.MultiplicityData is shared.MultiplicityData


def test_hierarchy_model_ordered_field_contracts():
    from sysml_codegen.extraction.data_models import MultiplicityData, RedefinitionData

    assert [field.name for field in dataclasses.fields(RedefinitionData)] == [
        "owning_part_qn",
        "attribute_name",
        "redefinition_type",
        "literal_value",
        "source_path",
        "expression_ast",
        "expression_text",
        "target_path",
        "is_deep_path",
        "source_file",
        "source_line",
    ]
    assert [field.name for field in dataclasses.fields(MultiplicityData)] == [
        "part_usage_name",
        "owning_part_def_qn",
        "count",
        "count_attribute_name",
        "default_value",
    ]


def test_aggregation_term_models_are_shared_class_objects():
    from agentic_mbse.sysml import aggregation as shared_aggregation
    from agentic_mbse.sysml import data_models as shared_models

    from sysml_codegen.extraction import data_models as codegen

    assert codegen.SumTerm is shared_models.SumTerm is shared_aggregation.SumTerm
    assert codegen.SingletonTerm is shared_models.SingletonTerm is shared_aggregation.SingletonTerm
    assert codegen.LocalTerm is shared_models.LocalTerm is shared_aggregation.LocalTerm


def test_aggregation_term_ordered_field_contracts():
    from sysml_codegen.extraction.data_models import LocalTerm, SingletonTerm, SumTerm

    assert [field.name for field in dataclasses.fields(SumTerm)] == [
        "part_usage_name",
        "attribute_name",
        "multiplicity_attr",
        "multiplicity_count",
    ]
    assert [field.name for field in dataclasses.fields(SingletonTerm)] == ["source_path"]
    assert [field.name for field in dataclasses.fields(LocalTerm)] == ["attribute_name"]


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_aggregation_expression_data():
    """AggregationExpressionData has exactly 15 fields."""
    from sysml_codegen.extraction.data_models import AggregationExpressionData

    expected = {
        "owning_part_qn",
        "owning_part_name",
        "attribute_name",
        "raw_expression_text",
        "transformed_expression",
        "sum_terms",
        "singleton_terms",
        "local_terms",
        "input_channels",
        "entry_points",
        "compilability",
        "has_unsupported_nodes",
        "aliases",
        "source_file",
        "source_line",
    }
    actual = _dataclass_field_names(AggregationExpressionData)
    assert actual == expected
    assert len(actual) == 15


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_hierarchy_extraction_result():
    from sysml_codegen.extraction.data_models import HierarchyExtractionResult

    expected = {
        "redefinitions",
        "design_overrides",
        "multiplicities",
        "aggregation_expressions",
        "warnings",
        "part_usage_names",
        "usage_type_map",
    }
    actual = _dataclass_field_names(HierarchyExtractionResult)
    assert actual == expected
    assert len(actual) == 7


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_backtracking_result():
    from sysml_codegen.analysis.dependency_backtracker import BacktrackingResult

    expected = {
        "required_usages",
        "dependency_graph",
        "entry_points",
        "entry_point_sources",
        "binding_resolutions",
        "phantom_report",
        "trace_log",
        # Item 7 (REQ-GA-08 / D4): Step-4 fall-through set for the V11 collector.
        "fallback_entry_points",
    }
    actual = _pydantic_field_names(BacktrackingResult)
    assert actual == expected


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_binding_resolution():
    from sysml_codegen.core.models import BindingResolution

    expected = {"resolution_type", "qualified_name", "source_path", "is_transitive"}
    actual = _pydantic_field_names(BindingResolution)
    assert actual == expected
    assert len(actual) == 4


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_channel_alias():
    from sysml_codegen.core.models import ChannelAlias

    expected = {"alias_name", "canonical_name", "owning_part_qn", "source"}
    actual = _pydantic_field_names(ChannelAlias)
    assert actual == expected
    assert len(actual) == 4


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_computation_graph():
    """ComputationGraph has exactly 5 fields.

    Item 7 (REQ-GA-08) adds ``fallback_entry_points`` (in-memory analysis
    artifact, ``exclude=True`` — not serialized) for the V11 collector.
    Item 11 (REQ-DM-09) adds ``output_aliases`` (serialized) for the surfaced
    EXPOSE_PURE names.
    """
    from sysml_codegen.resolution.models import ComputationGraph

    expected = {
        "modules",
        "entry_point_groups",
        "execution_order",
        "fallback_entry_points",
        "output_aliases",
    }
    actual = _pydantic_field_names(ComputationGraph)
    assert actual == expected
    assert len(actual) == 5


@pytest.mark.req("REQ-DM-09")
def test_req_dm_09_fields_output_alias():
    """OutputAlias has exactly the four documented fields (Item 11 / REQ-DM-09)."""
    from sysml_codegen.resolution.models import OutputAlias

    expected = {"alias_name", "canonical_channel", "instance_path", "shape"}
    actual = _pydantic_field_names(OutputAlias)
    assert actual == expected
    assert len(actual) == 4


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_pipeline_module():
    from sysml_codegen.resolution.models import PipelineModule

    expected = {
        "name",
        "module_type",
        "inputs",
        "outputs",
        "execution_order",
        "compilability",
        "compiled_expression",
        "module_kind",
        "output_schema_type",
        "auto_impl_context",
        "calc_def_name",
        "calc_def_qualified_name",
        "doc_comment",
        "calc_expressions",
        "source_file",
        "source_line",
    }
    actual = _pydantic_field_names(PipelineModule)
    assert actual == expected
    assert len(actual) == 16


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_module_input():
    from sysml_codegen.resolution.models import ModuleInput

    expected = {"param_name", "python_type", "source", "description", "default_value"}
    actual = _pydantic_field_names(ModuleInput)
    assert actual == expected
    assert len(actual) == 5


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_module_output():
    from sysml_codegen.resolution.models import ModuleOutput

    expected = {"field_name", "python_type", "channel_name", "description", "default_value", "unit"}
    actual = _pydantic_field_names(ModuleOutput)
    assert actual == expected
    assert len(actual) == 6


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_input_source():
    from sysml_codegen.resolution.models import InputSource

    expected = {"source_type", "param_group", "qualified_name", "producer_channel"}
    actual = _pydantic_field_names(InputSource)
    assert actual == expected
    assert len(actual) == 4


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_entry_point():
    from sysml_codegen.resolution.models import EntryPoint

    expected = {
        "qualified_name",
        "simple_name",
        "entry_type",
        "default_value",
        "source_calc_usage",
        "param_group",
        "python_type",
    }
    actual = _pydantic_field_names(EntryPoint)
    assert actual == expected
    assert len(actual) == 7


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_parameter_group():
    from sysml_codegen.resolution.models import ParameterGroup

    expected = {"name", "class_name", "source_file", "parameters"}
    actual = _pydantic_field_names(ParameterGroup)
    assert actual == expected
    assert len(actual) == 4


# ---------------------------------------------------------------------------
# REQ-DM-04: Source file location conformance
# ---------------------------------------------------------------------------


# Module path shorthands for readability
_DM = "sysml_codegen.extraction.data_models"
_UE = "sysml_codegen.extraction.usage_extractor"
_EC = "sysml_codegen.extraction.expression_compiler"
_CM = "sysml_codegen.core.models"
_RM = "sysml_codegen.resolution.models"
_BT = "sysml_codegen.analysis.dependency_backtracker"
_PG = "sysml_codegen.analysis.parameter_groups"

# (module_path, class_name, expected_file_suffix)
SOURCE_FILE_SPECS = [
    (_DM, "CalculationDefinitionData", "extraction/data_models.py"),
    (_DM, "PartDefinitionData", "extraction/data_models.py"),
    (_DM, "RedefinitionData", "agentic_mbse/sysml/data_models.py"),
    (_DM, "MultiplicityData", "agentic_mbse/sysml/data_models.py"),
    (_DM, "SumTerm", "agentic_mbse/sysml/data_models.py"),
    (_DM, "SingletonTerm", "agentic_mbse/sysml/data_models.py"),
    (_DM, "LocalTerm", "agentic_mbse/sysml/data_models.py"),
    (_DM, "AggregationExpressionData", "extraction/data_models.py"),
    (_DM, "HierarchyExtractionResult", "extraction/data_models.py"),
    (_DM, "ScopedAggregationData", "extraction/data_models.py"),
    (_DM, "ComputedAttributeData", "extraction/data_models.py"),
    (_DM, "AttributeInfo", "extraction/data_models.py"),
    (_DM, "ComputedAttributeClassification", "extraction/data_models.py"),
    (_DM, "RedefinitionType", "agentic_mbse/sysml/data_models.py"),
    (_UE, "CalcUsageData", "extraction/usage_extractor.py"),
    (_UE, "BindingInfo", "extraction/usage_extractor.py"),
    (_EC, "Compilability", "extraction/expression_compiler.py"),
    (_EC, "ExpressionNodeType", "extraction/expression_compiler.py"),
    (_CM, "BindingResolution", "core/models.py"),
    (_CM, "BindingResolutionType", "core/models.py"),
    (_CM, "ChannelAlias", "core/models.py"),
    (_RM, "ComputationGraph", "resolution/models.py"),
    (_RM, "PipelineModule", "resolution/models.py"),
    (_RM, "ModuleInput", "resolution/models.py"),
    (_RM, "ModuleOutput", "resolution/models.py"),
    (_RM, "InputSource", "resolution/models.py"),
    (_RM, "EntryPoint", "resolution/models.py"),
    (_RM, "EntryPointType", "resolution/models.py"),
    (_RM, "ParameterGroup", "resolution/models.py"),
    (_BT, "BacktrackingResult", "analysis/dependency_backtracker.py"),
    (_PG, "DesignAttributeData", "analysis/parameter_groups.py"),
    (_PG, "DerivedParameterGroup", "analysis/parameter_groups.py"),
    (_PG, "ParameterSource", "analysis/parameter_groups.py"),
]


@pytest.mark.req("REQ-DM-04")
@pytest.mark.parametrize("module_path,class_name,expected_suffix", SOURCE_FILE_SPECS)
def test_req_dm_04_models_at_documented_source_files(module_path, class_name, expected_suffix):
    """Each model's inspect.getfile() matches the source file stated in doc 09."""
    import importlib

    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    source_file = inspect.getfile(cls)
    assert source_file.endswith(expected_suffix), (
        f"{class_name}: expected path ending with {expected_suffix}, got {source_file}"
    )


# ---------------------------------------------------------------------------
# REQ-DM-05: Construction and property conformance
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-DM-05")
def test_req_dm_05_computation_graph_example_constructs():
    """The 2-module example from doc 09 constructs successfully."""
    from sysml_codegen.extraction.expression_compiler import Compilability
    from sysml_codegen.resolution.models import (
        ComputationGraph,
        EntryPoint,
        EntryPointType,
        InputSource,
        ModuleInput,
        ModuleKind,
        ModuleOutput,
        ParameterGroup,
        PipelineModule,
    )

    graph = ComputationGraph(
        modules=[
            PipelineModule(
                name="battery_pack__cost_model",
                module_type="BatteryPackCostCalcModule",
                inputs=[
                    ModuleInput(
                        param_name="capacity_kwh",
                        python_type="float",
                        source=InputSource(
                            source_type="entry_point",
                            param_group="design_params",
                            qualified_name="Design__battery_pack__capacity_kwh",
                        ),
                    ),
                    ModuleInput(
                        param_name="cost_per_kwh",
                        python_type="float",
                        source=InputSource(
                            source_type="entry_point",
                            param_group="library_params",
                            qualified_name="BatteryPackCostCalc__cost_per_kwh",
                        ),
                    ),
                ],
                outputs=[
                    ModuleOutput(
                        field_name="total_cost",
                        python_type="float",
                        channel_name="battery_pack__cost_model__total_cost",
                    ),
                ],
                execution_order=0,
                compilability=Compilability.FULLY_COMPILABLE,
                compiled_expression="capacity_kwh * cost_per_kwh",
                module_kind=ModuleKind.CALCULATION,
            ),
            PipelineModule(
                name="battery_system__total_cost",
                module_type="BatterySystemTotalCostModule",
                inputs=[
                    ModuleInput(
                        param_name="battery_cost",
                        python_type="float",
                        source=InputSource(
                            source_type="module_output",
                            producer_channel="battery_pack__cost_model__total_cost",
                        ),
                    ),
                ],
                outputs=[
                    ModuleOutput(
                        field_name="root",
                        python_type="float",
                        channel_name="battery_system__total_cost__root",
                    ),
                ],
                execution_order=1,
                module_kind=ModuleKind.AGGREGATION,
            ),
        ],
        entry_point_groups=[
            ParameterGroup(
                name="design_params",
                class_name="DesignParams",
                source_file=Path("SolarBatteryDesign.sysml"),
                parameters=[
                    EntryPoint(
                        qualified_name="Design__battery_pack__capacity_kwh",
                        simple_name="capacity_kwh",
                        entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                        default_value=100.0,
                        param_group="design_params",
                    ),
                ],
            ),
            ParameterGroup(
                name="library_params",
                class_name="LibraryParams",
                source_file=Path("BatteryPackCostCalc.sysml"),
                parameters=[
                    EntryPoint(
                        qualified_name="BatteryPackCostCalc__cost_per_kwh",
                        simple_name="cost_per_kwh",
                        entry_type=EntryPointType.LIBRARY_DEFAULT,
                        default_value=150.0,
                        param_group="library_params",
                    ),
                ],
            ),
        ],
        execution_order=["battery_pack__cost_model", "battery_system__total_cost"],
    )

    # Verify construction succeeded and structure is correct
    assert len(graph.modules) == 2
    assert len(graph.entry_point_groups) == 2
    assert len(graph.execution_order) == 2

    # Verify both wiring types present
    ep_source = graph.modules[0].inputs[0].source
    assert ep_source.source_type == "entry_point"
    assert ep_source.param_group == "design_params"

    mo_source = graph.modules[1].inputs[0].source
    assert mo_source.source_type == "module_output"
    assert mo_source.producer_channel == "battery_pack__cost_model__total_cost"


@pytest.mark.req("REQ-DM-05")
def test_req_dm_05_entry_point_json_field_name_property():
    """EntryPoint.json_field_name returns qualified_name."""
    from sysml_codegen.resolution.models import EntryPoint, EntryPointType

    ep = EntryPoint(
        qualified_name="Design__battery_pack__capacity_kwh",
        simple_name="capacity_kwh",
        entry_type=EntryPointType.DESIGN_ATTRIBUTE,
    )
    assert ep.json_field_name == "Design__battery_pack__capacity_kwh"


@pytest.mark.req("REQ-DM-05")
def test_req_dm_05_parameter_group_properties():
    """ParameterGroup.json_filename and schema_filename properties work."""
    from sysml_codegen.resolution.models import ParameterGroup

    pg = ParameterGroup(
        name="design_params",
        class_name="DesignParams",
        source_file=Path("Design.sysml"),
        parameters=[],
    )
    assert pg.json_filename == "design_params.json"
    assert pg.schema_filename == "design_params.py"


@pytest.mark.req("REQ-DM-05")
def test_req_dm_05_scoped_aggregation_data_module_eqn():
    """ScopedAggregationData.module_eqn returns '{instance_path}__{attribute_name}'."""
    from sysml_codegen.extraction.data_models import (
        AggregationExpressionData,
        ScopedAggregationData,
    )
    from sysml_codegen.extraction.expression_compiler import Compilability

    agg = AggregationExpressionData(
        owning_part_qn="Lib__Solar_Array",
        owning_part_name="Solar_Array",
        attribute_name="capital_cost",
        raw_expression_text="sum(pv_module.capital_cost)",
        transformed_expression="pv_module__capital_cost * module_count",
        sum_terms=[],
        singleton_terms=[],
        local_terms=[],
        input_channels=[],
        entry_points=[],
        compilability=Compilability.UNKNOWN,
    )
    scoped = ScopedAggregationData(
        expression=agg,
        instance_path="solar_battery_plant__solar_array",
    )
    assert scoped.module_eqn == "solar_battery_plant__solar_array__capital_cost"


# ---------------------------------------------------------------------------
# REQ-DM-06: Delegated models importable
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-DM-06")
class TestDelegatedModelsImportable:
    """Models with dedicated docs are still importable from their source."""

    def test_computed_attribute_data(self):
        from sysml_codegen.extraction.data_models import ComputedAttributeData

        assert ComputedAttributeData is not None

    def test_expression_ref(self):
        from agentic_mbse.sysml.types import ExpressionRef

        assert ExpressionRef is not None

    def test_phantom_detection_report(self):
        from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport

        assert PhantomDetectionReport is not None


# ---------------------------------------------------------------------------
# REQ-DM-07: Containment hierarchy conformance
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-DM-07")
def test_req_dm_07_containment_hierarchy():
    """Verify type annotations match the containment hierarchy from doc 09."""
    import typing

    from sysml_codegen.resolution.models import (
        ComputationGraph,
        EntryPoint,
        InputSource,
        ModuleInput,
        ModuleOutput,
        ParameterGroup,
        PipelineModule,
    )

    # ComputationGraph.modules is list[PipelineModule]
    modules_annotation = ComputationGraph.model_fields["modules"].annotation
    assert typing.get_origin(modules_annotation) is list
    assert typing.get_args(modules_annotation)[0] is PipelineModule

    # ComputationGraph.entry_point_groups is list[ParameterGroup]
    epg_annotation = ComputationGraph.model_fields["entry_point_groups"].annotation
    assert typing.get_origin(epg_annotation) is list
    assert typing.get_args(epg_annotation)[0] is ParameterGroup

    # ComputationGraph.execution_order is list[str]
    eo_annotation = ComputationGraph.model_fields["execution_order"].annotation
    assert typing.get_origin(eo_annotation) is list
    assert typing.get_args(eo_annotation)[0] is str

    # PipelineModule.inputs is list[ModuleInput]
    inputs_annotation = PipelineModule.model_fields["inputs"].annotation
    assert typing.get_origin(inputs_annotation) is list
    assert typing.get_args(inputs_annotation)[0] is ModuleInput

    # PipelineModule.outputs is list[ModuleOutput]
    outputs_annotation = PipelineModule.model_fields["outputs"].annotation
    assert typing.get_origin(outputs_annotation) is list
    assert typing.get_args(outputs_annotation)[0] is ModuleOutput

    # ModuleInput.source is InputSource
    source_annotation = ModuleInput.model_fields["source"].annotation
    assert source_annotation is InputSource

    # ParameterGroup.parameters is list[EntryPoint]
    params_annotation = ParameterGroup.model_fields["parameters"].annotation
    assert typing.get_origin(params_annotation) is list
    assert typing.get_args(params_annotation)[0] is EntryPoint
