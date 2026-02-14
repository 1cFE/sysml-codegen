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
from enum import Enum
from pathlib import Path
from typing import Any

# Import shared types from agentic-mbse
from agentic_mbse.sysml.data_models import AttributeInfo as BaseAttributeInfo
from agentic_mbse.sysml.types import BindingType, ExpressionRef

from .expression_compiler import Compilability

__all__ = [
    "AggregationExpressionData",
    "AttributeInfo",
    "BaseAttributeInfo",  # Export base class for type checking
    "BindingType",  # Re-export from agentic-mbse
    "CalculationDefinitionData",
    "ComputedAttributeClassification",
    "ComputedAttributeData",
    "ConstraintInfo",
    "HierarchyExtractionResult",
    "LocalTerm",
    "MultiplicityData",
    "PartDefinitionData",
    "RedefinitionData",
    "RedefinitionType",
    "ScopedAggregationData",
    "SingletonTerm",
    "SumTerm",
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


@dataclass
class ConstraintInfo:
    """Extracted constraint information.

    Attributes:
        expression: SysML constraint expression
        description: Human-readable description
        affected_attributes: Attributes involved in constraint
        constraint_type: 'simple' or 'complex'
        source_line: Line number in source file
    """

    expression: str
    description: str
    affected_attributes: list[str]
    constraint_type: str  # 'simple' or 'complex'
    source_line: int = 0


@dataclass
class PartDefinitionData:
    """Structured data from SysML part definition.

    Attributes:
        name: Part definition name
        qualified_name: Full SysML path (Package::PartDef)
        doc_comment: Documentation comment
        attributes: List of AttributeInfo
        constraints: List of ConstraintInfo
        source_file: Path to source SysML file
        source_line: Line number in source file
        source_hash: SHA256 hash for change detection
    """

    name: str
    qualified_name: str
    doc_comment: str
    attributes: list[AttributeInfo]
    constraints: list[ConstraintInfo]
    source_file: Path
    source_line: int = 0
    source_hash: str = ""


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

    # Raw syside AST nodes for each output attribute's expression.
    # Key: sanitized output attribute name. Value: raw syside AST node.
    output_expression_asts: dict[str, Any] = field(default_factory=dict)

    # All owned_member names from the raw CalcDef element.
    # Needed by expression compiler for undeclared intermediate resolution.
    all_member_names: set[str] = field(default_factory=set)

    # Raw syside AST nodes for non-input/non-output members.
    # Key: sanitized member name. Value: raw syside AST node.
    member_expressions: dict[str, Any] = field(default_factory=dict)


class ComputedAttributeClassification(str, Enum):
    """Classification of a PartDef/PartUsage attribute expression.

    Determined by qualified-name analysis of expression references:
    - FORMULA: all refs are sibling attributes (generates synthetic module)
    - EXPOSE_PURE: single FeatureChainExpression to calc output (channel alias)
    - EXPOSE_COMPUTED: FeatureChainExpression inside arithmetic (deferred)
    - LITERAL: pure constant, no feature references (not a computed attribute)
    - UNRESOLVABLE: contains references that cannot be resolved
    """

    FORMULA = "formula"
    EXPOSE_PURE = "expose_pure"
    EXPOSE_COMPUTED = "expose_computed"
    LITERAL = "literal"
    UNRESOLVABLE = "unresolvable"


@dataclass
class ComputedAttributeData:
    """Extracted data for a computed attribute on a PartDef/PartUsage.

    Produced by extract_computed_attributes(). LITERAL attributes are
    excluded (they stay in the design_attributes path). UNRESOLVABLE
    attributes are included so the caller can report them.

    Attributes:
        name: Attribute name (e.g., "area")
        python_name: Sanitized Python identifier
        owning_part_name: PartDef/PartUsage name
        owning_part_qualified_name: SysML :: format
        expression_ast: Raw syside AST node (source of truth for compilation)
        expression_text: Display-only text from reconstruct_expression()
        references: Refs from extract_feature_refs (structurally paired name+qn)
        classification: Computed attribute classification
        compilability: Reuse from expression_compiler
        compiled_expression: Python expr string (FORMULA only, None otherwise)
        source_file: Path to source SysML file
        source_line: Line number in source file
    """

    name: str
    python_name: str
    owning_part_name: str
    owning_part_qualified_name: str
    expression_ast: Any
    expression_text: str
    references: list[ExpressionRef]
    classification: ComputedAttributeClassification
    compilability: Compilability
    compiled_expression: str | None = None
    is_on_part_definition: bool = False  # True if owning element is a PartDefinition
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0


# ---------------------------------------------------------------------------
# Hierarchy Resolution Data Models (Item 3 — COST-PATTERN)
# ---------------------------------------------------------------------------


class RedefinitionType(str, Enum):
    """Classification of a :>> redefinition's RHS expression."""

    LITERAL = "literal"  # :>> wattage = 400.0
    CHAIN = "chain"  # :>> capital_cost = cost_model.total_cost
    EXPRESSION = "expression"  # :>> capital_cost = sum(pv_module.capital_cost) + ...


@dataclass
class RedefinitionData:
    """Extracted data for a single :>> redefinition on a PartDef or design PartUsage.

    Represents the resolution of one ReferenceUsage with owned_redefinitions.
    """

    owning_part_qn: str  # QN of the PartDef/PartUsage this :>> lives on
    attribute_name: str  # The redefined attribute (e.g., "capital_cost")
    redefinition_type: RedefinitionType
    # For LITERAL:
    literal_value: float | int | str | bool | None = None
    # For CHAIN:
    source_path: str | None = None  # e.g., "cost_model.total_cost"
    # For EXPRESSION:
    expression_ast: Any = None  # Raw syside AST for downstream transformation
    expression_text: str = ""  # Display text from reconstruct_expression()
    # Deep-path info (for design-level overrides):
    target_path: list[str] = field(default_factory=list)
    # e.g., ["pv_module", "wattage"] for :>> pv_module.wattage = 400.0
    is_deep_path: bool = False
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0


@dataclass
class MultiplicityData:
    """Multiplicity information for a PartUsage within a PartDef.

    count is defensively cast to int() at extraction time because
    cached_lower_bound may return a float or other numeric type from syside.
    """

    part_usage_name: str  # e.g., "pv_module"
    owning_part_def_qn: str  # QN of the owning PartDef (e.g., "Lib__Solar_Array")
    count: int | None  # Resolved literal count (e.g., 20), or None if unresolvable
    count_attribute_name: str | None  # Name of the multiplicity attribute (e.g., "module_count")
    default_value: int | None  # Default value of the count attribute


@dataclass
class SumTerm:
    """One sum() operand in an aggregation expression."""

    part_usage_name: str  # e.g., "pv_module"
    attribute_name: str  # e.g., "capital_cost"
    multiplicity_attr: str | None  # e.g., "module_count" (None if singleton)
    multiplicity_count: int | None  # e.g., 20


@dataclass
class SingletonTerm:
    """A non-sum child attribute reference in an aggregation expression."""

    source_path: str  # e.g., "allocation_model.total_allocation"


@dataclass
class LocalTerm:
    """A PartDef-local attribute reference in an aggregation expression."""

    attribute_name: str  # e.g., "misc_hardware_cost"


@dataclass
class AggregationExpressionData:
    """Extracted and transformed aggregation expression from a PartDef :>> attribute.

    Produced by hierarchy_resolver after scanning :>> EXPRESSION redefinitions
    that contain sum() calls. The expression has been decomposed into typed terms
    and the sum() calls transformed to parametric multiply.

    compilability is set to UNKNOWN at extraction time because the transformed
    expression still contains symbolic channel references (e.g., "pv_module.capital_cost")
    that Item 4 must resolve to actual pipeline channels.

    has_unsupported_nodes signals whether the AST walk encountered any node types
    it could not process. If True, Item 4 should expect MANUAL_REQUIRED after
    channel resolution.
    """

    owning_part_qn: str  # Assembly PartDef QN (e.g., "Lib__Solar_Array")
    owning_part_name: str  # Short name (e.g., "Solar_Array")
    attribute_name: str  # Redefined attribute (e.g., "capital_cost")
    raw_expression_text: str  # Before transformation
    transformed_expression: str  # After parametric multiply (symbolic channel refs)
    sum_terms: list[SumTerm]
    singleton_terms: list[SingletonTerm]
    local_terms: list[LocalTerm]
    input_channels: list[str]  # All upstream channel references (for Item 4 wiring)
    entry_points: list[str]  # Multiplicity count attrs → pipeline entry points
    compilability: Compilability = Compilability.UNKNOWN
    has_unsupported_nodes: bool = False
    aliases: list[str] = field(default_factory=list)  # CHAIN redef aliases (e.g., ["total_capex"])
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0


@dataclass
class HierarchyExtractionResult:
    """Complete extraction result for hierarchy patterns."""

    redefinitions: list[RedefinitionData]
    design_overrides: list[RedefinitionData]
    multiplicities: list[MultiplicityData]
    aggregation_expressions: list[AggregationExpressionData]
    warnings: list[str]
    part_usage_names: dict[str, set[str]] = field(default_factory=dict)


@dataclass
class ScopedAggregationData:
    """Aggregation expression scoped to a specific design instance.

    Produced by Step 4.7 from PartDef-level AggregationExpressionData.
    Each ScopedAggregationData maps a PartDef aggregation to one design
    instance path. Uses composition to avoid field drift with
    AggregationExpressionData.
    """

    expression: AggregationExpressionData  # All PartDef-level data (delegated)
    instance_path: str  # Design scope (e.g., "solar_battery_plant__solar_array")

    @property
    def module_eqn(self) -> str:
        """Module execution qualified name (ADR-003).

        Single source of truth -- used by backtracker (D.2), graph builder
        (E.2, E.4), and CLI generation (F.1).
        """
        return f"{self.instance_path}__{self.expression.attribute_name}"
