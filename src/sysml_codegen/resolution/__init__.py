"""Resolution layer for SysML code generation.

This layer carries the Pydantic models for pipeline configuration, the params-coverage
collectors and the producer-completeness check. The string-resolution graph builder
retired with the v5 family (retirement step 2).
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
