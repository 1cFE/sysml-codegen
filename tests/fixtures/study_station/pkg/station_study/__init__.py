from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from station_study.modules.pumpstation.pumpingcost import PumpingCostModule
from station_study.modules.pumpstation.requiredflow import RequiredFlowModule
from station_study.modules.constraints.constraintreportaggregatormodule import ConstraintReportAggregatorModule
from station_study.modules.pumpstation.stationpumpfitconstraintmodule import StationPumpFitConstraintModule

from station_study.schemas.constraint_types import ConstraintEvaluation as ConstraintEvaluation, ConstraintReport as ConstraintReport
from station_study.schemas.station_params import StationParams as StationParams

from station_study.primitives import Float


def create_station_study_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            ConstraintReportAggregatorModule,            PumpingCostModule,            RequiredFlowModule,            StationPumpFitConstraintModule,        ],
        module_type_override={            ConstraintReportAggregatorModule: "constraints.ConstraintReportAggregatorModule",            PumpingCostModule: "pumpstation.PumpingCostModule",            RequiredFlowModule: "pumpstation.RequiredFlowModule",            StationPumpFitConstraintModule: "pumpstation.StationPumpFitConstraintModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    StationParams,    ConstraintEvaluation,    ConstraintReport,    Float,]
