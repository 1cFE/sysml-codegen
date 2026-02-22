"""Resolution layer for SysML code generation.

This layer resolves dependencies and builds the computation graph:
- Pydantic models for pipeline configuration
- Graph building from backtracking results
Note: graph_builder is not imported at module level to avoid circular imports.
Import it directly: `from sysml_codegen.resolution.graph_builder import build_computation_graph`
"""

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
