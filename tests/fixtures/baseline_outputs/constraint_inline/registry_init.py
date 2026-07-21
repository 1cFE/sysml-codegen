from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from constraint_inline.modules.constraint_inline.thehostpositiveconstraintmodule import TheHostPositiveConstraintModule
from constraint_inline.modules.constraints.constraintreportaggregatormodule import ConstraintReportAggregatorModule

from constraint_inline.schemas.constraint_types import ConstraintEvaluation as ConstraintEvaluation, ConstraintReport as ConstraintReport
from constraint_inline.schemas.model_params import ModelParams as ModelParams



def create_constraint_inline_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            TheHostPositiveConstraintModule,            ConstraintReportAggregatorModule,        ],
        module_type_override={            TheHostPositiveConstraintModule: "constraint_inline.TheHostPositiveConstraintModule",            ConstraintReportAggregatorModule: "constraints.ConstraintReportAggregatorModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    ModelParams,    ConstraintEvaluation,    ConstraintReport,]
