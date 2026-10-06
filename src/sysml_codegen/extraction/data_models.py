"""Codegen-specific data models for SysML extraction results.

These extend shared types from agentic-mbse with codegen-specific fields.

AttributeInfo extends agentic_mbse.sysml.data_models.AttributeInfo with:
- python_type: Mapped Python type for code generation
- description: Human-readable description for docstrings
- unit: Physical unit for documentation
- source_line: Line number for traceability

BindingType is imported directly from agentic-mbse.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import UUID

# Import shared types from agentic-mbse
from agentic_mbse.sysml.data_models import (
    AttributeInfo as BaseAttributeInfo,
)
from agentic_mbse.sysml.types import BindingType

__all__ = [
    "AttributeInfo",
    "BaseAttributeInfo",  # Export base class for type checking
    "BindingType",  # Re-export from agentic-mbse
    "CalculationDefinitionData",
]


@dataclass
class AttributeInfo(BaseAttributeInfo):
    """Extended attribute info for code generation.

    Extends agentic_mbse.sysml.data_models.AttributeInfo with fields needed
    for Python code generation.

    Inherited from BaseAttributeInfo:
        name: Attribute name (e.g., "power_output")
        sysml_type: SysML type annotation (e.g., "Real", "Power")
        default_value: Default value if specified
        binding_type: How the attribute receives its value
        is_input: True if marked as input
        is_output: True if marked as output

    Added for codegen:
        python_type: Mapped Python type (e.g., "float", "int")
        description: Human-readable description for docstrings
        unit: Physical unit (MW, m, kg, etc.)
        source_line: Line number in source SysML file
        is_optional: True if attribute has a default value
    """

    # Codegen-specific fields (all have defaults to work with dataclass inheritance)
    python_type: str = "Any"
    description: str = ""
    unit: str | None = None
    source_line: int = 0
    is_optional: bool = False

    # Live exact-route sidecar. Snapshot v5 deliberately omits parser UUIDs.
    element_id: UUID | None = field(
        default=None,
        metadata={"snapshot_exclude": True},
    )


@dataclass
class CalculationDefinitionData:
    """Structured data from SysML calc definition.

    This is the primary data model for code generation.

    Attributes:
        name: Calculation definition name (e.g., "AlphaNeutronSplit")
        qualified_name: Full SysML path (e.g., "FusionPhysics::AlphaNeutronSplit")
        doc_comment: Documentation comment
        calc_expressions: SysML calc expressions (preserved as-is)
        input_attributes: List of input AttributeInfo
        output_attributes: List of output AttributeInfo
        references: Citations from doc comments (e.g., PyFECONS line numbers)
        source_file: Path to source SysML file
        source_line: Line number in source file
        source_hash: SHA256 hash for change detection
    """

    name: str
    qualified_name: str
    doc_comment: str
    calc_expressions: list[str]
    input_attributes: list[AttributeInfo]
    output_attributes: list[AttributeInfo]
    references: list[str]
    source_file: Path
    source_line: int = 0
    source_hash: str = ""

    # Exact declaration identity is the compiler payload. Names remain rendering metadata.
    element_id: UUID | None = field(
        default=None,
        metadata={"snapshot_exclude": True},
    )
    output_expression_asts_by_id: dict[UUID, Any] = field(
        default_factory=dict,
        metadata={"snapshot_exclude": True},
    )
    all_member_ids: set[UUID] = field(
        default_factory=set,
        metadata={"snapshot_exclude": True},
    )
    member_expressions_by_id: dict[UUID, Any] = field(
        default_factory=dict,
        metadata={"snapshot_exclude": True},
    )
    member_names_by_id: dict[UUID, str] = field(
        default_factory=dict,
        metadata={"snapshot_exclude": True},
    )
