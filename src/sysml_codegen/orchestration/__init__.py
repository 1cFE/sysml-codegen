"""Orchestration layer: pipeline construction and output registry building.

Extracted from generation/initialization.py (Step 7.1).
PipelineContext moved here from generation/initialization.py (Step 7.6).
"""

from sysml_codegen.orchestration.output_registry_builder import (
    build_output_registry,
)
from sysml_codegen.orchestration.pipeline_builder import (
    _build_chain_aliases,
    _remove_formula_from_design_attrs,
    _rewrite_virtual_bindings,
    _scope_aggregation_expressions,
    build_pipeline_context,
    find_instance_paths_for_partdef,
)
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)

__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    "_build_chain_aliases",
    "_remove_formula_from_design_attrs",
    "_rewrite_virtual_bindings",
    "_scope_aggregation_expressions",
    "build_output_registry",
    "build_pipeline_context",
    "find_instance_paths_for_partdef",
]
