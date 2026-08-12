"""Unit tests for data models and shared type imports.

Tests:
- AttributeInfo extends agentic-mbse AttributeInfo with codegen fields
- BindingType is imported from agentic-mbse
- CalculationDefinitionData uses extended AttributeInfo
"""

from __future__ import annotations

from pathlib import Path


def test_attribute_info_extends_base():
    """Verify AttributeInfo extends agentic-mbse AttributeInfo."""
    from sysml_codegen.extraction.data_models import AttributeInfo, BaseAttributeInfo

    # Verify inheritance
    assert issubclass(AttributeInfo, BaseAttributeInfo)

    # Create an instance with both base and extended fields
    attr = AttributeInfo(
        name="test",
        sysml_type="Real",
        python_type="float",  # codegen-specific
        description="Test attr",  # codegen-specific
        unit="MW",  # codegen-specific
    )

    # Verify base class fields (inherited from agentic-mbse)
    assert hasattr(attr, "name")
    assert hasattr(attr, "sysml_type")
    assert hasattr(attr, "default_value")
    assert hasattr(attr, "binding_type")
    assert hasattr(attr, "is_input")
    assert hasattr(attr, "is_output")

    # Verify codegen-specific fields (extended)
    assert hasattr(attr, "python_type")
    assert hasattr(attr, "description")
    assert hasattr(attr, "unit")
    assert hasattr(attr, "is_optional")
    assert hasattr(attr, "source_line")


def test_binding_type_from_agentic_mbse():
    """Verify BindingType is imported from agentic-mbse."""
    from agentic_mbse.sysml.types import BindingType as AgenticBindingType

    from sysml_codegen.extraction.usage_extractor import BindingType

    # Should be the same enum (imported, not redefined)
    assert BindingType is AgenticBindingType


def test_calculation_definition_data_uses_attribute_info():
    """Verify CalculationDefinitionData uses shared AttributeInfo."""
    from sysml_codegen.extraction.data_models import AttributeInfo, CalculationDefinitionData

    attr = AttributeInfo(
        name="p_fusion",
        sysml_type="Real",
        python_type="float",
        description="Fusion power",
    )

    calc_def = CalculationDefinitionData(
        name="TestCalc",
        qualified_name="TestPackage::TestCalc",
        doc_comment="Test calculation",
        calc_expressions=[],
        input_attributes=[attr],
        output_attributes=[],
        references=[],
        source_file=Path("test.sysml"),
    )

    assert len(calc_def.input_attributes) == 1
    assert calc_def.input_attributes[0].name == "p_fusion"


def test_attribute_info_fields():
    """Verify AttributeInfo has expected fields."""
    from sysml_codegen.extraction.data_models import AttributeInfo

    attr = AttributeInfo(
        name="test_attr",
        sysml_type="Real",
        python_type="float",
        description="A test attribute",
        unit="MW",
    )

    assert attr.name == "test_attr"
    assert attr.sysml_type == "Real"
    assert attr.python_type == "float"
    assert attr.description == "A test attribute"
    assert attr.unit == "MW"


def test_binding_type_enum_values():
    """Verify BindingType has expected enum values."""
    from sysml_codegen.extraction.usage_extractor import BindingType

    # Check expected enum members exist
    assert hasattr(BindingType, "CHAIN")
    assert hasattr(BindingType, "REFERENCE")
    assert hasattr(BindingType, "LITERAL")
    assert hasattr(BindingType, "UNBOUND")


def test_calculation_definition_data_fields():
    """Verify CalculationDefinitionData has all expected fields."""
    from sysml_codegen.extraction.data_models import CalculationDefinitionData

    # Create a minimal instance
    calc_def = CalculationDefinitionData(
        name="TestCalc",
        qualified_name="TestPackage::TestCalc",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[],
        output_attributes=[],
        references=[],
        source_file=Path("test.sysml"),
    )

    # Verify required fields are present
    assert calc_def.name == "TestCalc"
    assert calc_def.qualified_name == "TestPackage::TestCalc"
    assert calc_def.input_attributes == []
    assert calc_def.output_attributes == []


def test_calculation_definition_data_has_exact_expression_identity_fields():
    """Exact compiler payload fields have empty defaults."""
    from sysml_codegen.extraction.data_models import CalculationDefinitionData

    cd = CalculationDefinitionData(
        name="Test",
        qualified_name="Test",
        doc_comment="",
        calc_expressions=[],
        input_attributes=[],
        output_attributes=[],
        references=[],
        source_file=Path("test.sysml"),
    )
    assert cd.element_id is None
    assert cd.output_expression_asts_by_id == {}
    assert cd.all_member_ids == set()
    assert cd.member_expressions_by_id == {}
    assert cd.member_names_by_id == {}


def test_binding_info_has_expression_ast_field():
    """BindingInfo.expression_ast defaults to None (backward compat)."""
    from agentic_mbse.sysml.types import BindingType

    from sysml_codegen.extraction.usage_extractor import BindingInfo

    bi = BindingInfo(param_name="x", source_path=None, binding_type=BindingType.UNBOUND)
    assert bi.expression_ast is None


def test_pipeline_module_has_compilability_field():
    """PipelineModule.compilability defaults to UNKNOWN (backward compat)."""
    from sysml_codegen.extraction.expression_compiler import Compilability
    from sysml_codegen.resolution.models import ModuleKind, PipelineModule

    m = PipelineModule(
        name="t", module_type="T", inputs=[], outputs=[], execution_order=0,
        module_kind=ModuleKind.CALCULATION,
    )
    assert m.compilability == Compilability.UNKNOWN
