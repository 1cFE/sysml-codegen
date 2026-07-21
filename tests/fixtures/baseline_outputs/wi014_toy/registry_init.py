from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from wi014_toy.modules.toy_library.panel_area import Panel_AreaModule
from wi014_toy.modules.toy_library.panel_cost import Panel_CostModule
from wi014_toy.modules.constraints.constraintreportaggregatormodule import ConstraintReportAggregatorModule
from wi014_toy.modules.toy_plant.demoplantaffordableconstraintmodule import DemoPlantAffordableConstraintModule

from wi014_toy.schemas.constraint_types import ConstraintEvaluation as ConstraintEvaluation, ConstraintReport as ConstraintReport
from wi014_toy.schemas.toy_plant_params import ToyPlantParams as ToyPlantParams

from wi014_toy.primitives import Float


def create_wi014_toy_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            ConstraintReportAggregatorModule,            Panel_AreaModule,            Panel_CostModule,            DemoPlantAffordableConstraintModule,        ],
        module_type_override={            ConstraintReportAggregatorModule: "constraints.ConstraintReportAggregatorModule",            Panel_AreaModule: "toy_library.Panel_AreaModule",            Panel_CostModule: "toy_library.Panel_CostModule",            DemoPlantAffordableConstraintModule: "toy_plant.DemoPlantAffordableConstraintModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    ToyPlantParams,    ConstraintEvaluation,    ConstraintReport,    Float,]
