"""C01: Data model conformance tests.

Verifies that every data model, enum, and field referenced in doc 09
(09-data-models.md) exists in the source code, is importable from its
documented location, has the correct fields and types, and can be
constructed with real data.

Doc 09 is the mixed reference document: part of it describes the retired string-
resolution stack. The eleven nodes that covered that part — the analysis-layer
importables, ``OutputRegistry``, ``PhantomDetectionReport``, ``BacktrackingResult``'s
field set, and their four documented-source-file rows — retired with the v5 family
(retirement step 2), together with the doc-09 rows they checked. What is left covers
only models the product still ships.

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

    def test_attribute_info(self):
        from sysml_codegen.extraction.data_models import AttributeInfo

        assert AttributeInfo is not None


@pytest.mark.req("REQ-DM-01")
class TestCoreModelsImportable:
    """Every core-layer model is importable from its documented module."""

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
        "sysml_codegen.extraction.expression_compiler",
        "Compilability",
        {"FULLY_COMPILABLE", "PARTIALLY_COMPILABLE", "MANUAL_REQUIRED", "UNKNOWN"},
        id="Compilability",
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
        "element_id",
        "output_expression_asts_by_id",
        "all_member_ids",
        "member_expressions_by_id",
        "member_names_by_id",
    }
    actual = _dataclass_field_names(CalculationDefinitionData)
    assert actual == expected


@pytest.mark.req("REQ-DM-03")
def test_req_dm_03_fields_computation_graph():
    """ComputationGraph has exactly 6 fields.

    Item 7 (REQ-GA-08) adds ``fallback_entry_points`` (in-memory analysis
    artifact, ``exclude=True`` — not serialized) for the V11 collector.
    Item 11 (REQ-DM-09) adds ``output_aliases`` (serialized) for the surfaced
    EXPOSE_PURE names. CONSTRAINT-EXEC Item 7 (D6) adds ``constraint_catalog``
    (in-memory generation-boundary artifact, ``exclude=True`` — not serialized).
    """
    from sysml_codegen.resolution.models import ComputationGraph

    expected = {
        "modules",
        "entry_point_groups",
        "execution_order",
        "fallback_entry_points",
        "output_aliases",
        "constraint_catalog",
    }
    actual = _pydantic_field_names(ComputationGraph)
    assert actual == expected
    assert len(actual) == 6


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

    expected = {
        "param_name",
        "python_type",
        "source",
        "description",
        "default_value",
        "formal_identity",
    }
    actual = _pydantic_field_names(ModuleInput)
    assert actual == expected
    assert len(actual) == 6


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
        # Item 4 Phase 3: a modeled default's unit, carried never converted
        # (DD-R25), and the IR node kind that stopped resolution, which is what
        # makes "explicitly unresolved" observable rather than indistinguishable
        # from "no default at all" (DD-R22).
        "unit_text",
        "unresolved_default_kind",
    }
    actual = _pydantic_field_names(EntryPoint)
    assert actual == expected
    assert len(actual) == 9


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
_EC = "sysml_codegen.extraction.expression_compiler"
_CM = "sysml_codegen.core.models"
_RM = "sysml_codegen.resolution.models"

# (module_path, class_name, expected_file_suffix)
SOURCE_FILE_SPECS = [
    (_DM, "CalculationDefinitionData", "extraction/data_models.py"),
    (_DM, "AttributeInfo", "extraction/data_models.py"),
    (_EC, "Compilability", "extraction/expression_compiler.py"),
    (_RM, "ComputationGraph", "resolution/models.py"),
    (_RM, "PipelineModule", "resolution/models.py"),
    (_RM, "ModuleInput", "resolution/models.py"),
    (_RM, "ModuleOutput", "resolution/models.py"),
    (_RM, "InputSource", "resolution/models.py"),
    (_RM, "EntryPoint", "resolution/models.py"),
    (_RM, "EntryPointType", "resolution/models.py"),
    (_RM, "ParameterGroup", "resolution/models.py"),
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


# ---------------------------------------------------------------------------
# REQ-DM-06: Delegated models importable
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-DM-06")
class TestDelegatedModelsImportable:
    """Models with dedicated docs are still importable from their source."""

    def test_expression_ref_is_retired(self):
        import agentic_mbse.sysml.types as delegated_types

        assert not hasattr(delegated_types, "ExpressionRef")

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
