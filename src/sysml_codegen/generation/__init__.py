"""Generation layer for SysML code generation.

This layer generates Python code exclusively from ComputationGraph:
- TEAx module wrappers (modules.py)
- Entry point schemas and JSON (entry_point.py)
- Multi-output schema models (schemas.py)
- Implementation stencils (stencils.py)
- Pipeline YAML configuration (pipeline.py)
- Module registry code (registry.py)
- Initialization utilities (initialization.py)
- Preservation logic (preservation.py)
- Test generation (test_gen.py)
"""

from sysml_codegen.generation.entry_point import (
    generate_all_derived_jsons,
    generate_all_derived_jsons_from_graph,
    generate_all_derived_schemas,
    generate_all_derived_schemas_from_graph,
    generate_derived_group_schema,
    generate_inputs_readme,
)
from sysml_codegen.generation.initialization import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.generation.modules import (
    generate_teax_module,
    generate_teax_module_from_graph,
)
from sysml_codegen.generation.pipeline import (
    generate_pipeline_yaml,
)
from sysml_codegen.generation.preservation import (
    backup_implementation,
    should_regenerate_stencil,
    should_regenerate_stencil_from_graph,
)
from sysml_codegen.generation.registry import (
    generate_registry,
    generate_registry_from_graph,
    generate_registry_function,
)
from sysml_codegen.generation.schemas import (
    generate_multioutput_model,
    generate_multioutput_model_from_graph,
)
from sysml_codegen.generation.stencils import (
    generate_backlog_report,
    generate_backlog_report_from_graph,
    generate_implementation,
    generate_implementation_from_graph,
)
from sysml_codegen.generation.test_gen import (
    generate_test_implementations,
    generate_test_implementations_from_graph,
)

__all__ = [
    # entry_point
    "generate_all_derived_jsons",
    "generate_all_derived_jsons_from_graph",
    "generate_all_derived_schemas",
    "generate_all_derived_schemas_from_graph",
    "generate_derived_group_schema",
    "generate_inputs_readme",
    # initialization
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    # modules
    "generate_teax_module",
    "generate_teax_module_from_graph",
    # pipeline
    "generate_pipeline_yaml",
    # preservation
    "backup_implementation",
    "should_regenerate_stencil",
    "should_regenerate_stencil_from_graph",
    # registry
    "generate_registry",
    "generate_registry_from_graph",
    "generate_registry_function",
    # schemas
    "generate_multioutput_model",
    "generate_multioutput_model_from_graph",
    # stencils
    "generate_backlog_report",
    "generate_backlog_report_from_graph",
    "generate_implementation",
    "generate_implementation_from_graph",
    # test_gen
    "generate_test_implementations",
    "generate_test_implementations_from_graph",
]
