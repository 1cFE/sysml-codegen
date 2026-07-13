from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from constraint_multi_instance.modules.constraint_multi_instance.power_calc import Power_CalcModule
from constraint_multi_instance.modules.constraint_multi_instance.thedesignccell0nonnegconstraintmodule import TheDesignCCell0NonnegConstraintModule
from constraint_multi_instance.modules.constraint_multi_instance.thedesignccell1nonnegconstraintmodule import TheDesignCCell1NonnegConstraintModule
from constraint_multi_instance.modules.constraint_multi_instance.thedesignccell2nonnegconstraintmodule import TheDesignCCell2NonnegConstraintModule
from constraint_multi_instance.modules.constraints.constraintreportaggregatormodule import ConstraintReportAggregatorModule

from constraint_multi_instance.schemas.constraint_types import ConstraintEvaluation as ConstraintEvaluation, ConstraintReport as ConstraintReport
from constraint_multi_instance.schemas.model_params import ModelParams as ModelParams

from constraint_multi_instance.primitives import Float


def create_constraint_multi_instance_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            Power_CalcModule,            TheDesignCCell0NonnegConstraintModule,            TheDesignCCell1NonnegConstraintModule,            TheDesignCCell2NonnegConstraintModule,            ConstraintReportAggregatorModule,        ],
        module_type_override={            Power_CalcModule: "constraint_multi_instance.Power_CalcModule",            TheDesignCCell0NonnegConstraintModule: "constraint_multi_instance.TheDesignCCell0NonnegConstraintModule",            TheDesignCCell1NonnegConstraintModule: "constraint_multi_instance.TheDesignCCell1NonnegConstraintModule",            TheDesignCCell2NonnegConstraintModule: "constraint_multi_instance.TheDesignCCell2NonnegConstraintModule",            ConstraintReportAggregatorModule: "constraints.ConstraintReportAggregatorModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    ModelParams,    ConstraintEvaluation,    ConstraintReport,    Float,]
