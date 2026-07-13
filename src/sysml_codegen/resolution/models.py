"""Pydantic data models for pipeline code generation.

This module defines the core data models used for building and representing
the computation graph. These models provide validation at construction
time and serve as the single source of truth for pipeline generation.

Key Design Principles:
1. Use Pydantic for validation at boundaries
2. Import existing types (BindingType) rather than redefining
3. Qualified names use __ separator per ADR-001
"""

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

# Import shared types from core for re-export (backward compatibility)
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from sysml_codegen.extraction.expression_compiler import Compilability


class EntryPointType(str, Enum):
    """ADR-001 entry point types.

    Classification of how an entry point value is sourced:
    - LIBRARY_DEFAULT: Unbound param using calc def default value
    - DESIGN_ATTRIBUTE: Literal value defined in design part
    - USAGE_LITERAL: Literal value in calc usage binding
    """

    LIBRARY_DEFAULT = "library_default"
    DESIGN_ATTRIBUTE = "design_attribute"
    USAGE_LITERAL = "usage_literal"


class EntryPoint(BaseModel):
    """A classified entry point parameter.

    This is the DEFINITIVE representation of an entry point.
    Qualified names use __ separator per ADR-001.

    Attributes:
        qualified_name: Unique identifier with __ separator
            (e.g., "CATFMFEPhysics__catf_physics__p_fusion")
        simple_name: The parameter name alone (e.g., "p_fusion")
        entry_type: Classification per ADR-001
        default_value: Default value if available
        source_calc_usage: For LIBRARY_DEFAULT, which calc usage needs this
        param_group: Which JSON file group (e.g., "physics_params")
    """

    qualified_name: str
    simple_name: str
    entry_type: EntryPointType
    default_value: float | None = None
    source_calc_usage: str | None = None
    param_group: str | None = None
    python_type: str = "float"

    @property
    def json_field_name(self) -> str:
        """The field name in the JSON file.

        Uses qualified name for globally unique identification.
        """
        return self.qualified_name


class ParameterGroup(BaseModel):
    """A group of entry points for a single JSON file.

    Groups entry points by source file for organized parameter management.

    Attributes:
        name: Group identifier (e.g., "physics_params")
        class_name: Python class name (e.g., "PhysicsParams")
        source_file: Source SysML file
        parameters: List of entry points in this group
    """

    name: str
    class_name: str
    source_file: Path
    parameters: list[EntryPoint]

    model_config = {"arbitrary_types_allowed": True}

    @property
    def json_filename(self) -> str:
        """Filename for JSON input file."""
        return f"{self.name}.json"

    @property
    def schema_filename(self) -> str:
        """Filename for Pydantic schema file."""
        return f"{self.name}.py"


class InputSource(BaseModel):
    """Source of a module input value.

    Describes where a module input gets its value from:
    - entry_point: From a JSON input file
    - module_output: From an upstream module's output

    Attributes:
        source_type: Either "entry_point" or "module_output"
        param_group: For entry_point, which JSON file
        qualified_name: For entry_point, the qualified parameter name
        producer_channel: For module_output, the upstream channel name
    """

    source_type: str  # "entry_point" or "module_output"
    # For entry_point:
    param_group: str | None = None
    qualified_name: str | None = None
    # For module_output:
    producer_channel: str | None = None


class ModuleInput(BaseModel):
    """An input to a pipeline module.

    Attributes:
        param_name: Parameter name (e.g., "p_fusion")
        python_type: Python type string (e.g., "float")
        source: Where the input value comes from
        description: Human-readable description from CalcDef input attribute
        default_value: Default value from CalcDef input attribute
    """

    param_name: str
    python_type: str
    source: InputSource
    description: str | None = None
    default_value: float | int | str | bool | None = None


class ModuleOutput(BaseModel):
    """An output from a pipeline module.

    Attributes:
        field_name: Field name ("root" for single-output, attr name for multi)
        python_type: Python type string (e.g., "float")
        channel_name: Channel name for wiring (e.g., "alphaneutronsplit_p_neutron")
        description: Human-readable description from CalcDef output attribute
        default_value: Default value from CalcDef output attribute
        unit: Physical unit from CalcDef output attribute
    """

    field_name: str
    python_type: str
    channel_name: str
    description: str | None = None
    default_value: float | int | str | bool | None = None
    unit: str | None = None


class ModuleKind(str, Enum):
    """Kind of a pipeline module — set once at construction, dispatched on at every
    generation seam. Replaces the two accreted Boolean flags PipelineModule carried
    before Item 6."""

    CALCULATION = "calculation"
    FORMULA = "formula"
    AGGREGATION = "aggregation"
    CONSTRAINT = "constraint"
    REPORT_AGGREGATOR = "report_aggregator"


class PipelineModule(BaseModel):
    """A module in the pipeline configuration.

    Represents a calculation usage that will be executed as part of the pipeline.

    Attributes:
        name: Module instance name (lowercase, e.g., "alphaneutronsplit")
        module_type: Module class name (e.g., "AlphaNeutronSplitModule")
        inputs: List of module inputs
        outputs: List of module outputs
        execution_order: Position in topological order
    """

    name: str
    module_type: str
    inputs: list[ModuleInput]
    outputs: list[ModuleOutput]
    execution_order: int
    compilability: Compilability = Compilability.UNKNOWN
    compiled_expression: str | None = None
    module_kind: ModuleKind
    output_schema_type: str | None = None
    auto_impl_context: dict | None = None
    # Metadata from CalcDef / ComputedAttributeData / AggregationExpressionData
    calc_def_name: str | None = None
    calc_def_qualified_name: str | None = None
    doc_comment: str | None = None
    calc_expressions: list[str] | None = None
    source_file: str | None = None
    source_line: int | None = None


class OutputAlias(BaseModel):
    """A modeler's EXPOSE_PURE name surfaced onto a canonical output channel.

    Item 11 (SC-7). The two EXPOSE_PURE shapes both land here, tagged by
    provenance:
    - ``part_def`` (shape A): from the ``_scoped_alias`` registry (a part-def
      derived attribute, e.g. ``total_cost = cost_calc.cost``, expanded per
      instance).
    - ``part_usage`` (shape B): from an ``expose_pure`` ``ChannelAlias`` (a
      derived attribute on a part usage).

    Attributes:
        alias_name: The modeler's sanitized ``python_name`` (Item 5 / REQ-NC-06).
        canonical_channel: The channel the value already flows on (INV-2), read
            from the registry — never re-derived.
        instance_path: The instance scope that qualifies the name so two
            siblings exposing the same name land on distinct output filenames
            (INV-4): the scope half of a ``_scoped_alias`` key (shape A) or the
            owning part's leaf (shape B).
        shape: Which source produced the entry.
    """

    alias_name: str
    canonical_channel: str
    instance_path: str
    shape: Literal["part_def", "part_usage"]

    @property
    def output_filename(self) -> str:
        """Destination filename for this alias's exit-point capture (D2).

        ``{instance_path}__{alias_name}.json`` — instance-qualified so two
        instances exposing the same name never collide (INV-4).
        """
        return f"{self.instance_path}__{self.alias_name}.json"


class ComputationGraph(BaseModel):
    """The complete computation graph derived from BacktrackingResult.

    This is the SINGLE SOURCE OF TRUTH for pipeline generation.
    All downstream generation (YAML, schemas, JSON) derives from this.

    Attributes:
        modules: All pipeline modules in execution order
        entry_point_groups: Entry points grouped by source file
        execution_order: Module names in topological order
        fallback_entry_points: QNs of Step-4 fall-through entry points — bound
            bindings that matched no resolution strategy and no design attribute
            (Item 7 / D4). Carried onto the graph so ``collect_uncovered_params``
            is pure over the graph alone. In-memory analysis artifact consumed at
            the generation boundary; ``exclude=True`` keeps it out of the
            serialized graph so committed baselines do not churn.
        output_aliases: EXPOSE_PURE modeler names surfaced onto their canonical
            output channels (Item 11 / SC-7), stable-sorted by
            ``(instance_path, alias_name)``. A genuine schema field describing
            real generated output — **not** excluded (contrast
            ``fallback_entry_points``): it is serialized on every graph and
            drives the named exit-point captures in the pipeline YAML.
    """

    modules: list[PipelineModule]
    entry_point_groups: list[ParameterGroup]
    execution_order: list[str]
    fallback_entry_points: set[str] = Field(default_factory=set, exclude=True)
    output_aliases: list[OutputAlias] = Field(default_factory=list)


__all__ = [
    "BindingResolution",
    "BindingResolutionType",
    "ComputationGraph",
    "EntryPoint",
    "EntryPointType",
    "InputSource",
    "ModuleInput",
    "ModuleOutput",
    "OutputAlias",
    "ParameterGroup",
    "PipelineModule",
]
