from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from plant_value_shapes.modules.plantvalueshapeslib.chamberselectcalc import ChamberSelectCalcModule
from plant_value_shapes.modules.plantvalueshapeslib.flowcalc import FlowCalcModule
from plant_value_shapes.modules.plantvalueshapeslib.mixed_output_style import Mixed_Output_StyleModule
from plant_value_shapes.modules.plantvalueshapeslib.netcostcalc import NetCostCalcModule
from plant_value_shapes.modules.plantvalueshapeslib.quoted_return_calc import Quoted_Return_CalcModule
from plant_value_shapes.modules.plantvalueshapeslib.ratedcostcalc import RatedCostCalcModule

from plant_value_shapes.schemas.design_params import DesignParams as DesignParams
from plant_value_shapes.schemas.library_params import LibraryParams as LibraryParams

from plant_value_shapes.primitives import Float


def create_plant_value_shapes_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            ChamberSelectCalcModule,            FlowCalcModule,            Mixed_Output_StyleModule,            NetCostCalcModule,            Quoted_Return_CalcModule,            RatedCostCalcModule,        ],
        module_type_override={            ChamberSelectCalcModule: "plantvalueshapeslib.ChamberSelectCalcModule",            FlowCalcModule: "plantvalueshapeslib.FlowCalcModule",            Mixed_Output_StyleModule: "plantvalueshapeslib.Mixed_Output_StyleModule",            NetCostCalcModule: "plantvalueshapeslib.NetCostCalcModule",            Quoted_Return_CalcModule: "plantvalueshapeslib.Quoted_Return_CalcModule",            RatedCostCalcModule: "plantvalueshapeslib.RatedCostCalcModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    DesignParams,    LibraryParams,    Float,]
