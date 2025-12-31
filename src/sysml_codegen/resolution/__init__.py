"""Resolution layer for SysML code generation.

This layer resolves dependencies and builds the computation graph:
- Pydantic models for pipeline configuration
- Graph building from backtracking results
- Identifier type transformations for ADR-003

Note: graph_builder is not imported at module level to avoid circular imports.
Import it directly: `from sysml_codegen.resolution.graph_builder import build_computation_graph`
"""

# Import from core for shared types (re-export for backward compatibility)
from sysml_codegen.core.identifier_types import (
    ElementQualifiedName,
    ModuleType,
    PythonModulePath,
    SysMLQualifiedName,
    derive_module_type,
    derive_python_path,
)
from sysml_codegen.resolution.models import (
    BindingResolution,
    BindingResolutionType,
    ComputationGraph,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)

# NOTE: graph_builder imports are deferred to avoid circular imports
# Use: from sysml_codegen.resolution.graph_builder import build_computation_graph

__all__ = [
    # identifier_types
    "ElementQualifiedName",
    "ModuleType",
    "PythonModulePath",
    "SysMLQualifiedName",
    "derive_module_type",
    "derive_python_path",
    # models
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
