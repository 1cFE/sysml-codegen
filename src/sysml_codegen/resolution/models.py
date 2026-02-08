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

from pydantic import BaseModel

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
    """

    param_name: str
    python_type: str
    source: InputSource


class ModuleOutput(BaseModel):
    """An output from a pipeline module.

    Attributes:
        field_name: Field name ("root" for single-output, attr name for multi)
        python_type: Python type string (e.g., "float")
        channel_name: Channel name for wiring (e.g., "alphaneutronsplit_p_neutron")
    """

    field_name: str
    python_type: str
    channel_name: str


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


class ComputationGraph(BaseModel):
    """The complete computation graph derived from BacktrackingResult.

    This is the SINGLE SOURCE OF TRUTH for pipeline generation.
    All downstream generation (YAML, schemas, JSON) derives from this.

    Attributes:
        modules: All pipeline modules in execution order
        entry_point_groups: Entry points grouped by source file
        execution_order: Module names in topological order
    """

    modules: list[PipelineModule]
    entry_point_groups: list[ParameterGroup]
    execution_order: list[str]


__all__ = [
    "BindingResolution",
    "BindingResolutionType",
    "ComputationGraph",
    "EntryPoint",
    "EntryPointType",
    "InputSource",
    "ModuleInput",
    "ModuleOutput",
    "ParameterGroup",
    "PipelineModule",
]
