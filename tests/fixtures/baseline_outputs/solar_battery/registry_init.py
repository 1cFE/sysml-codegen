from simkit.core.registry_builder import create_registry
from simkit.core.pipeline_registry import PipelineModuleRegistry

from solar_battery.modules.solarbatterylibrary.allocationcostcalc import AllocationCostCalcModule
from solar_battery.modules.solarbatterylibrary.annualizedfinancialcalc import AnnualizedFinancialCalcModule
from solar_battery.modules.solarbatterylibrary.annualizedfuelcalc import AnnualizedFuelCalcModule
from solar_battery.modules.solarbatterylibrary.annualizedomcalc import AnnualizedOMCalcModule
from solar_battery.modules.solarbatterylibrary.arrayboscostcalc import ArrayBOSCostCalcModule
from solar_battery.modules.solarbatterylibrary.batteryboscostcalc import BatteryBOSCostCalcModule
from solar_battery.modules.solarbatterylibrary.batterypackcostcalc import BatteryPackCostCalcModule
from solar_battery.modules.solarbatterylibrary.electricalpanelcostcalc import ElectricalPanelCostCalcModule
from solar_battery.modules.solarbatterylibrary.energyproductioncalc import EnergyProductionCalcModule
from solar_battery.modules.solarbatterylibrary.hybridinvertercostcalc import HybridInverterCostCalcModule
from solar_battery.modules.solarbatterylibrary.invertercostcalc import InverterCostCalcModule
from solar_battery.modules.solarbatterylibrary.lcoecalc import LCOECalcModule
from solar_battery.modules.solarbatterylibrary.permittingcostcalc import PermittingCostCalcModule
from solar_battery.modules.solarbatterylibrary.pvmodulecostcalc import PVModuleCostCalcModule
from solar_battery.modules.solarbatterylibrary.rackingcostcalc import RackingCostCalcModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.p_net_kw import p_net_kwModule
from solar_battery.modules.solarbatterylibrary__solar_array.capital_cost import capital_costModule
from solar_battery.modules.solarbatterylibrary__solar_array.raw_material_cost import raw_material_costModule
from solar_battery.modules.solarbatterylibrary__solar_array.fabrication_cost import fabrication_costModule
from solar_battery.modules.solarbatterylibrary__solar_array.installation_cost import installation_costModule
from solar_battery.modules.solarbatterylibrary__solar_array.idiot_index import idiot_indexModule
from solar_battery.modules.solarbatterylibrary__battery_system.capital_cost import capital_costModule
from solar_battery.modules.solarbatterylibrary__battery_system.raw_material_cost import raw_material_costModule
from solar_battery.modules.solarbatterylibrary__battery_system.fabrication_cost import fabrication_costModule
from solar_battery.modules.solarbatterylibrary__battery_system.installation_cost import installation_costModule
from solar_battery.modules.solarbatterylibrary__battery_system.idiot_index import idiot_indexModule
from solar_battery.modules.solarbatterylibrary__site_infrastructure.capital_cost import capital_costModule
from solar_battery.modules.solarbatterylibrary__site_infrastructure.raw_material_cost import raw_material_costModule
from solar_battery.modules.solarbatterylibrary__site_infrastructure.fabrication_cost import fabrication_costModule
from solar_battery.modules.solarbatterylibrary__site_infrastructure.installation_cost import installation_costModule
from solar_battery.modules.solarbatterylibrary__site_infrastructure.idiot_index import idiot_indexModule
from solar_battery.modules.solarbatterylibrary__solar_battery_plant.capital_cost import capital_costModule
from solar_battery.modules.solarbatterylibrary__solar_battery_plant.raw_material_cost import raw_material_costModule
from solar_battery.modules.solarbatterylibrary__solar_battery_plant.fabrication_cost import fabrication_costModule
from solar_battery.modules.solarbatterylibrary__solar_battery_plant.installation_cost import installation_costModule
from solar_battery.modules.solarbatterylibrary__solar_battery_plant.idiot_index import idiot_indexModule

from solar_battery.schemas.design_params import DesignParams as DesignParams
from solar_battery.schemas.library_params import LibraryParams as LibraryParams
from solar_battery.schemas.system_design import SystemDesign as SystemDesign



def create_solar_battery_registry() -> PipelineModuleRegistry:
    """Create registry for all modules using auto-introspection.

    Pure auto-registration pattern:
    - All modules (single-output and multi-output) use create_registry()
    - TEAx introspection handles RootModel[T] and BaseModel fields correctly

    ADR-003: Uses module_type_override to register modules with namespaced
    module types (e.g., "fusionphysics_powerbalance.AlphaNeutronSplitModule")
    while keeping Python class names unchanged (e.g., "AlphaNeutronSplitModule").
    """
    return create_registry(
        [            PVModuleCostCalcModule,            InverterCostCalcModule,            ArrayBOSCostCalcModule,            BatteryPackCostCalcModule,            HybridInverterCostCalcModule,            BatteryBOSCostCalcModule,            RackingCostCalcModule,            ElectricalPanelCostCalcModule,            PermittingCostCalcModule,            AllocationCostCalcModule,            EnergyProductionCalcModule,            AnnualizedOMCalcModule,            AnnualizedFuelCalcModule,            AnnualizedFinancialCalcModule,            LCOECalcModule,            p_net_kwModule,            capital_costModule,            raw_material_costModule,            fabrication_costModule,            installation_costModule,            idiot_indexModule,            capital_costModule,            raw_material_costModule,            fabrication_costModule,            installation_costModule,            idiot_indexModule,            capital_costModule,            raw_material_costModule,            fabrication_costModule,            installation_costModule,            idiot_indexModule,            capital_costModule,            raw_material_costModule,            fabrication_costModule,            installation_costModule,            idiot_indexModule,        ],
        module_type_override={            PVModuleCostCalcModule: "solarbatterylibrary.PVModuleCostCalcModule",            InverterCostCalcModule: "solarbatterylibrary.InverterCostCalcModule",            ArrayBOSCostCalcModule: "solarbatterylibrary.ArrayBOSCostCalcModule",            BatteryPackCostCalcModule: "solarbatterylibrary.BatteryPackCostCalcModule",            HybridInverterCostCalcModule: "solarbatterylibrary.HybridInverterCostCalcModule",            BatteryBOSCostCalcModule: "solarbatterylibrary.BatteryBOSCostCalcModule",            RackingCostCalcModule: "solarbatterylibrary.RackingCostCalcModule",            ElectricalPanelCostCalcModule: "solarbatterylibrary.ElectricalPanelCostCalcModule",            PermittingCostCalcModule: "solarbatterylibrary.PermittingCostCalcModule",            AllocationCostCalcModule: "solarbatterylibrary.AllocationCostCalcModule",            EnergyProductionCalcModule: "solarbatterylibrary.EnergyProductionCalcModule",            AnnualizedOMCalcModule: "solarbatterylibrary.AnnualizedOMCalcModule",            AnnualizedFuelCalcModule: "solarbatterylibrary.AnnualizedFuelCalcModule",            AnnualizedFinancialCalcModule: "solarbatterylibrary.AnnualizedFinancialCalcModule",            LCOECalcModule: "solarbatterylibrary.LCOECalcModule",            p_net_kwModule: "solarbatterydesign.solar_battery_plant.p_net_kwModule",            capital_costModule: "solarbatterylibrary__solar_array.capital_costModule",            raw_material_costModule: "solarbatterylibrary__solar_array.raw_material_costModule",            fabrication_costModule: "solarbatterylibrary__solar_array.fabrication_costModule",            installation_costModule: "solarbatterylibrary__solar_array.installation_costModule",            idiot_indexModule: "solarbatterylibrary__solar_array.idiot_indexModule",            capital_costModule: "solarbatterylibrary__battery_system.capital_costModule",            raw_material_costModule: "solarbatterylibrary__battery_system.raw_material_costModule",            fabrication_costModule: "solarbatterylibrary__battery_system.fabrication_costModule",            installation_costModule: "solarbatterylibrary__battery_system.installation_costModule",            idiot_indexModule: "solarbatterylibrary__battery_system.idiot_indexModule",            capital_costModule: "solarbatterylibrary__site_infrastructure.capital_costModule",            raw_material_costModule: "solarbatterylibrary__site_infrastructure.raw_material_costModule",            fabrication_costModule: "solarbatterylibrary__site_infrastructure.fabrication_costModule",            installation_costModule: "solarbatterylibrary__site_infrastructure.installation_costModule",            idiot_indexModule: "solarbatterylibrary__site_infrastructure.idiot_indexModule",            capital_costModule: "solarbatterylibrary__solar_battery_plant.capital_costModule",            raw_material_costModule: "solarbatterylibrary__solar_battery_plant.raw_material_costModule",            fabrication_costModule: "solarbatterylibrary__solar_battery_plant.fabrication_costModule",            installation_costModule: "solarbatterylibrary__solar_battery_plant.installation_costModule",            idiot_indexModule: "solarbatterylibrary__solar_battery_plant.idiot_indexModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    LibraryParams,    DesignParams,    SystemDesign,]
