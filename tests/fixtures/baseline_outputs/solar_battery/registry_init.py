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
from solar_battery.modules.solarbatterydesign.solar_battery_plant.solar_array.capital_cost import capital_costModule as SolarArray_capital_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.solar_array.raw_material_cost import raw_material_costModule as SolarArray_raw_material_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.solar_array.fabrication_cost import fabrication_costModule as SolarArray_fabrication_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.solar_array.installation_cost import installation_costModule as SolarArray_installation_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.solar_array.idiot_index import idiot_indexModule as SolarArray_idiot_indexModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.battery_system.capital_cost import capital_costModule as BatterySystem_capital_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.battery_system.raw_material_cost import raw_material_costModule as BatterySystem_raw_material_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.battery_system.fabrication_cost import fabrication_costModule as BatterySystem_fabrication_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.battery_system.installation_cost import installation_costModule as BatterySystem_installation_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.battery_system.idiot_index import idiot_indexModule as BatterySystem_idiot_indexModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.site_infra.capital_cost import capital_costModule as SiteInfra_capital_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.site_infra.raw_material_cost import raw_material_costModule as SiteInfra_raw_material_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.site_infra.fabrication_cost import fabrication_costModule as SiteInfra_fabrication_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.site_infra.installation_cost import installation_costModule as SiteInfra_installation_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.site_infra.idiot_index import idiot_indexModule as SiteInfra_idiot_indexModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.capital_cost import capital_costModule as SolarBatteryPlant_capital_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.raw_material_cost import raw_material_costModule as SolarBatteryPlant_raw_material_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.fabrication_cost import fabrication_costModule as SolarBatteryPlant_fabrication_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.installation_cost import installation_costModule as SolarBatteryPlant_installation_costModule
from solar_battery.modules.solarbatterydesign.solar_battery_plant.idiot_index import idiot_indexModule as SolarBatteryPlant_idiot_indexModule

from solar_battery.schemas.design_params import DesignParams as DesignParams
from solar_battery.schemas.library_params import LibraryParams as LibraryParams
from solar_battery.schemas.system_design import SystemDesign as SystemDesign

from solar_battery.primitives import Float


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
        [            PVModuleCostCalcModule,            InverterCostCalcModule,            ArrayBOSCostCalcModule,            BatteryPackCostCalcModule,            HybridInverterCostCalcModule,            BatteryBOSCostCalcModule,            RackingCostCalcModule,            ElectricalPanelCostCalcModule,            PermittingCostCalcModule,            AllocationCostCalcModule,            EnergyProductionCalcModule,            AnnualizedOMCalcModule,            AnnualizedFuelCalcModule,            AnnualizedFinancialCalcModule,            LCOECalcModule,            p_net_kwModule,            SolarArray_capital_costModule,            SolarArray_raw_material_costModule,            SolarArray_fabrication_costModule,            SolarArray_installation_costModule,            SolarArray_idiot_indexModule,            BatterySystem_capital_costModule,            BatterySystem_raw_material_costModule,            BatterySystem_fabrication_costModule,            BatterySystem_installation_costModule,            BatterySystem_idiot_indexModule,            SiteInfra_capital_costModule,            SiteInfra_raw_material_costModule,            SiteInfra_fabrication_costModule,            SiteInfra_installation_costModule,            SiteInfra_idiot_indexModule,            SolarBatteryPlant_capital_costModule,            SolarBatteryPlant_raw_material_costModule,            SolarBatteryPlant_fabrication_costModule,            SolarBatteryPlant_installation_costModule,            SolarBatteryPlant_idiot_indexModule,        ],
        module_type_override={            PVModuleCostCalcModule: "solarbatterylibrary.PVModuleCostCalcModule",            InverterCostCalcModule: "solarbatterylibrary.InverterCostCalcModule",            ArrayBOSCostCalcModule: "solarbatterylibrary.ArrayBOSCostCalcModule",            BatteryPackCostCalcModule: "solarbatterylibrary.BatteryPackCostCalcModule",            HybridInverterCostCalcModule: "solarbatterylibrary.HybridInverterCostCalcModule",            BatteryBOSCostCalcModule: "solarbatterylibrary.BatteryBOSCostCalcModule",            RackingCostCalcModule: "solarbatterylibrary.RackingCostCalcModule",            ElectricalPanelCostCalcModule: "solarbatterylibrary.ElectricalPanelCostCalcModule",            PermittingCostCalcModule: "solarbatterylibrary.PermittingCostCalcModule",            AllocationCostCalcModule: "solarbatterylibrary.AllocationCostCalcModule",            EnergyProductionCalcModule: "solarbatterylibrary.EnergyProductionCalcModule",            AnnualizedOMCalcModule: "solarbatterylibrary.AnnualizedOMCalcModule",            AnnualizedFuelCalcModule: "solarbatterylibrary.AnnualizedFuelCalcModule",            AnnualizedFinancialCalcModule: "solarbatterylibrary.AnnualizedFinancialCalcModule",            LCOECalcModule: "solarbatterylibrary.LCOECalcModule",            p_net_kwModule: "solarbatterydesign.solar_battery_plant.p_net_kwModule",            SolarArray_capital_costModule: "solarbatterydesign.solar_battery_plant.solar_array.capital_costModule",            SolarArray_raw_material_costModule: "solarbatterydesign.solar_battery_plant.solar_array.raw_material_costModule",            SolarArray_fabrication_costModule: "solarbatterydesign.solar_battery_plant.solar_array.fabrication_costModule",            SolarArray_installation_costModule: "solarbatterydesign.solar_battery_plant.solar_array.installation_costModule",            SolarArray_idiot_indexModule: "solarbatterydesign.solar_battery_plant.solar_array.idiot_indexModule",            BatterySystem_capital_costModule: "solarbatterydesign.solar_battery_plant.battery_system.capital_costModule",            BatterySystem_raw_material_costModule: "solarbatterydesign.solar_battery_plant.battery_system.raw_material_costModule",            BatterySystem_fabrication_costModule: "solarbatterydesign.solar_battery_plant.battery_system.fabrication_costModule",            BatterySystem_installation_costModule: "solarbatterydesign.solar_battery_plant.battery_system.installation_costModule",            BatterySystem_idiot_indexModule: "solarbatterydesign.solar_battery_plant.battery_system.idiot_indexModule",            SiteInfra_capital_costModule: "solarbatterydesign.solar_battery_plant.site_infra.capital_costModule",            SiteInfra_raw_material_costModule: "solarbatterydesign.solar_battery_plant.site_infra.raw_material_costModule",            SiteInfra_fabrication_costModule: "solarbatterydesign.solar_battery_plant.site_infra.fabrication_costModule",            SiteInfra_installation_costModule: "solarbatterydesign.solar_battery_plant.site_infra.installation_costModule",            SiteInfra_idiot_indexModule: "solarbatterydesign.solar_battery_plant.site_infra.idiot_indexModule",            SolarBatteryPlant_capital_costModule: "solarbatterydesign.solar_battery_plant.capital_costModule",            SolarBatteryPlant_raw_material_costModule: "solarbatterydesign.solar_battery_plant.raw_material_costModule",            SolarBatteryPlant_fabrication_costModule: "solarbatterydesign.solar_battery_plant.fabrication_costModule",            SolarBatteryPlant_installation_costModule: "solarbatterydesign.solar_battery_plant.installation_costModule",            SolarBatteryPlant_idiot_indexModule: "solarbatterydesign.solar_battery_plant.idiot_indexModule",        },
    )


# Custom schema types for TEAx pipeline registration
# Use with: execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)
CUSTOM_SCHEMA_TYPES = [    LibraryParams,    DesignParams,    SystemDesign,    Float,]
