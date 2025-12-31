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
    from sysml_codegen.extraction.usage_extractor import BindingType
    from agentic_mbse.sysml.types import BindingType as AgenticBindingType

    # Should be the same enum (imported, not redefined)
    assert BindingType is AgenticBindingType


def test_calculation_definition_data_uses_attribute_info():
    """Verify CalculationDefinitionData uses shared AttributeInfo."""
    from sysml_codegen.extraction.data_models import CalculationDefinitionData, AttributeInfo

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
