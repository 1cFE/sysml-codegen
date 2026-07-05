from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from catf_mfe.modules.fusionanalysesthermalloads.auxiliarysystemspower import AuxiliarySystemsPowerModule
from catf_mfe.modules.fusionanalysesthermalloads.coolantpumppower import CoolantPumpPowerModule
from catf_mfe.modules.fusionanalysesthermalloads.cryopumprefrigeration import CryoPumpRefrigerationModule
from catf_mfe.modules.fusionanalysesthermalloads.heatingwallplugpower import HeatingWallPlugPowerModule
from catf_mfe.modules.fusionanalysesthermalloads.magnetcryogenicload import MagnetCryogenicLoadModule
from catf_mfe.modules.fusionanalysesthermalloads.tritiumprocessingpower import TritiumProcessingPowerModule
from catf_mfe.modules.fusionanalysesthermalloads.vacuumpumppower import VacuumPumpPowerModule
from catf_mfe.modules.fusionphysics_performancemetrics.engineeringqfactor import EngineeringQFactorModule
from catf_mfe.modules.fusionphysics_performancemetrics.plantefficiency import PlantEfficiencyModule
from catf_mfe.modules.fusionphysics_performancemetrics.scientificqfactor import ScientificQFactorModule
from catf_mfe.modules.fusionphysics_powerbalance.alphaneutronsplit import AlphaNeutronSplitModule
from catf_mfe.modules.fusionphysics_powerbalance.blanketthermalpower import BlanketThermalPowerModule
from catf_mfe.modules.fusionphysics_powerbalance.grosselectricpower import GrossElectricPowerModule
from catf_mfe.modules.fusionphysics_powerbalance.netelectricpower import NetElectricPowerModule
from catf_mfe.modules.fusionphysicsgeometry.magnetsurfacearea import MagnetSurfaceAreaModule
from catf_mfe.modules.fusionphysicsgeometry.torusminorradius import TorusMinorRadiusModule
from catf_mfe.modules.fusionphysicsgeometry.torussurfacearea import TorusSurfaceAreaModule
from catf_mfe.modules.fusionphysicsgeometry.torusvolume import TorusVolumeModule

from catf_mfe.schemas.blanket_params import BlanketParams as BlanketParams
from catf_mfe.schemas.heating_params import HeatingParams as HeatingParams
from catf_mfe.schemas.magnets_params import MagnetsParams as MagnetsParams
from catf_mfe.schemas.physics_params import PhysicsParams as PhysicsParams
from catf_mfe.schemas.radial_build_params import RadialBuildParams as RadialBuildParams
from catf_mfe.schemas.system_params import SystemParams as SystemParams
from catf_mfe.schemas.tritium_params import TritiumParams as TritiumParams
from catf_mfe.schemas.vacuum_params import VacuumParams as VacuumParams

from catf_mfe.primitives import Float


def create_catf_mfe_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            AuxiliarySystemsPowerModule,            CoolantPumpPowerModule,            CryoPumpRefrigerationModule,            HeatingWallPlugPowerModule,            MagnetCryogenicLoadModule,            TritiumProcessingPowerModule,            VacuumPumpPowerModule,            EngineeringQFactorModule,            PlantEfficiencyModule,            ScientificQFactorModule,            AlphaNeutronSplitModule,            BlanketThermalPowerModule,            GrossElectricPowerModule,            NetElectricPowerModule,            MagnetSurfaceAreaModule,            TorusMinorRadiusModule,            TorusSurfaceAreaModule,            TorusVolumeModule,        ],
        module_type_override={            AuxiliarySystemsPowerModule: "fusionanalysesthermalloads.AuxiliarySystemsPowerModule",            CoolantPumpPowerModule: "fusionanalysesthermalloads.CoolantPumpPowerModule",            CryoPumpRefrigerationModule: "fusionanalysesthermalloads.CryoPumpRefrigerationModule",            HeatingWallPlugPowerModule: "fusionanalysesthermalloads.HeatingWallPlugPowerModule",            MagnetCryogenicLoadModule: "fusionanalysesthermalloads.MagnetCryogenicLoadModule",            TritiumProcessingPowerModule: "fusionanalysesthermalloads.TritiumProcessingPowerModule",            VacuumPumpPowerModule: "fusionanalysesthermalloads.VacuumPumpPowerModule",            EngineeringQFactorModule: "fusionphysics_performancemetrics.EngineeringQFactorModule",            PlantEfficiencyModule: "fusionphysics_performancemetrics.PlantEfficiencyModule",            ScientificQFactorModule: "fusionphysics_performancemetrics.ScientificQFactorModule",            AlphaNeutronSplitModule: "fusionphysics_powerbalance.AlphaNeutronSplitModule",            BlanketThermalPowerModule: "fusionphysics_powerbalance.BlanketThermalPowerModule",            GrossElectricPowerModule: "fusionphysics_powerbalance.GrossElectricPowerModule",            NetElectricPowerModule: "fusionphysics_powerbalance.NetElectricPowerModule",            MagnetSurfaceAreaModule: "fusionphysicsgeometry.MagnetSurfaceAreaModule",            TorusMinorRadiusModule: "fusionphysicsgeometry.TorusMinorRadiusModule",            TorusSurfaceAreaModule: "fusionphysicsgeometry.TorusSurfaceAreaModule",            TorusVolumeModule: "fusionphysicsgeometry.TorusVolumeModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    BlanketParams,    HeatingParams,    MagnetsParams,    PhysicsParams,    RadialBuildParams,    SystemParams,    TritiumParams,    VacuumParams,    Float,]
