from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from ife_plant.modules.ifeplantlib.chamberyieldcalc import ChamberYieldCalcModule
from ife_plant.modules.ifeplantlib.coilvolume import CoilVolumeModule
from ife_plant.modules.ifeplantlib.cryoload import CryoLoadModule
from ife_plant.modules.ifeplantlib.driverpowercalc import DriverPowerCalcModule
from ife_plant.modules.ifeplantlib.hifcostcalc import HifCostCalcModule
from ife_plant.modules.ifeplantlib.plantlcoe import PlantLcoeModule

from ife_plant.schemas.design_params import DesignParams as DesignParams
from ife_plant.schemas.library_params import LibraryParams as LibraryParams

from ife_plant.primitives import Float


def create_ife_plant_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            ChamberYieldCalcModule,            CoilVolumeModule,            CryoLoadModule,            DriverPowerCalcModule,            HifCostCalcModule,            PlantLcoeModule,        ],
        module_type_override={            ChamberYieldCalcModule: "ifeplantlib.ChamberYieldCalcModule",            CoilVolumeModule: "ifeplantlib.CoilVolumeModule",            CryoLoadModule: "ifeplantlib.CryoLoadModule",            DriverPowerCalcModule: "ifeplantlib.DriverPowerCalcModule",            HifCostCalcModule: "ifeplantlib.HifCostCalcModule",            PlantLcoeModule: "ifeplantlib.PlantLcoeModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    DesignParams,    LibraryParams,    Float,]
