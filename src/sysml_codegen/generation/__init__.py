"""Generation layer for SysML code generation.

This layer generates Python code from the computed pipeline structure:
- TEAx module wrappers (modules.py)
- Entry point schemas and JSON (entry_point.py)
- Multi-output schema models (schemas.py)
- Implementation stencils (stencils.py)
- Pipeline YAML configuration (pipeline.py)
- Module registry code (registry.py)
- Constraint comments (constraint_comments.py)
- Initialization utilities (initialization.py)
- Preservation logic (preservation.py)
- Test generation (test_gen.py)
"""

from sysml_codegen.generation.constraint_comments import (
    generate_field_constraint_comments,
)
from sysml_codegen.generation.entry_point import (
    collect_entry_point_attributes,
    generate_all_derived_jsons,
    generate_all_derived_jsons_from_graph,
    generate_all_derived_schemas,
    generate_all_derived_schemas_from_graph,
    generate_derived_group_json,
    generate_derived_group_schema,
    generate_entry_point_schema,
    generate_input_json,
    generate_inputs_readme,
)
from sysml_codegen.generation.initialization import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.generation.modules import (
    generate_teax_module,
    is_multioutput,
)
from sysml_codegen.generation.pipeline import (
    generate_pipeline_yaml,
)
from sysml_codegen.generation.preservation import (
    backup_implementation,
    should_regenerate_stencil,
)
from sysml_codegen.generation.registry import (
    generate_registry_function,
)
from sysml_codegen.generation.schemas import (
    generate_multioutput_model,
    prepare_input_fields_with_constraints,
    should_use_multioutput,
)
from sysml_codegen.generation.stencils import (
    generate_backlog_report,
    generate_implementation,
    generate_implementation_stencil,
)
from sysml_codegen.generation.test_gen import (
    generate_test_implementations,
)

__all__ = [
    # constraint_comments
    "generate_field_constraint_comments",
    # entry_point
    "collect_entry_point_attributes",
    "generate_all_derived_jsons",
    "generate_all_derived_jsons_from_graph",
    "generate_all_derived_schemas",
    "generate_all_derived_schemas_from_graph",
    "generate_derived_group_json",
    "generate_derived_group_schema",
    "generate_entry_point_schema",
    "generate_input_json",
    "generate_inputs_readme",
    # initialization
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    # modules
    "generate_teax_module",
    "is_multioutput",
    # pipeline
    "generate_pipeline_yaml",
    # preservation
    "backup_implementation",
    "should_regenerate_stencil",
    # registry
    "generate_registry_function",
    # schemas
    "generate_multioutput_model",
    "prepare_input_fields_with_constraints",
    "should_use_multioutput",
    # stencils
    "generate_backlog_report",
    "generate_implementation",
    "generate_implementation_stencil",
    # test_gen
    "generate_test_implementations",
]
