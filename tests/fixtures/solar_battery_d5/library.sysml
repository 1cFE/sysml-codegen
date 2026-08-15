package SolarBatteryLibrary {
    doc /*
    Solar+Battery plant cost modeling library.
    Exercises the full LCOE pipeline using PyFECONS-aligned calculations.

    Follows the coffee maker's Pattern A (nested cost models) and extends it
    with system-level CalcDefs for energy production, O&M, fuel, financial, and LCOE.

    **Reference Pattern**: models/tests/coffee_maker/library.sysml
    **Foundation**: models/library/foundation/costing.sysml
    **Spec**: .project/active/solar-battery-sysml-model/spec.md
    **Last Updated**: 2026-02-01
    */

    // Standard imports
    private import ScalarValues::Real;
    private import ScalarValues::Integer;
    private import NumericalFunctions::sum;

    // Foundation costing package (production interface, not a local copy)
    private import Costing::*;

    // ============================================================
    // SECTION 1: COMPONENT COST CALCDEFS (9 defs)
    // ============================================================

    calc def PVModuleCostCalc {
        doc /*
        Cost calculation for photovoltaic modules.
        Material cost driven by wattage_in and cost per watt.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute wattage_in : Real;
        in attribute efficiency_in : Real;

        in attribute cost_per_watt : Real default := 1.07;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = wattage_in * cost_per_watt;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def InverterCostCalc {
        doc /*
        Cost calculation for string inverters.
        Material cost driven by power rating.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute power_rating_in : Real;

        in attribute cost_per_watt : Real default := 0.286;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = power_rating_in * cost_per_watt;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def ArrayBOSCostCalc {
        doc /*
        Cost calculation for solar array balance-of-system.
        Includes combiners, disconnects, conduit per string and per panel.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute string_count_in : Real;
        in attribute panel_count_in : Real;

        in attribute cost_per_string : Real default := 150.0;
        in attribute cost_per_panel_bos : Real default := 30.0;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = string_count_in * cost_per_string + panel_count_in * cost_per_panel_bos;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def BatteryPackCostCalc {
        doc /*
        Cost calculation for battery packs.
        Material cost driven by capacity and chemistry factor.

        **Source**: Battery industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute capacity_kwh_in : Real;
        in attribute chemistry_factor_in : Real;

        in attribute cost_per_kwh : Real default := 171.5;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = capacity_kwh_in * cost_per_kwh * chemistry_factor_in;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def HybridInverterCostCalc {
        doc /*
        Cost calculation for hybrid (bidirectional) inverters.
        Material cost driven by power rating.

        **Source**: Battery industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute power_rating_in : Real;

        in attribute cost_per_watt : Real default := 0.1714;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = power_rating_in * cost_per_watt;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def BatteryBOSCostCalc {
        doc /*
        Cost calculation for battery balance-of-system.
        Includes management system, wiring, thermal management per pack.

        **Source**: Battery industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute pack_count_in : Real;

        in attribute cost_per_pack_bos : Real default := 71.5;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = pack_count_in * cost_per_pack_bos;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def RackingCostCalc {
        doc /*
        Cost calculation for racking and mounting hardware.
        Material cost driven by panel count. Tilt angle is a design parameter
        but does not affect cost in this simplified model.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute panel_count_in : Real;
        in attribute tilt_angle_in : Real;

        in attribute cost_per_panel_rack : Real default := 57.0;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = panel_count_in * cost_per_panel_rack;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def ElectricalPanelCostCalc {
        doc /*
        Cost calculation for electrical panel and breakers.
        Base cost plus per-circuit cost.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute circuit_count_in : Real;

        in attribute base_cost : Real default := 150.0;
        in attribute cost_per_circuit : Real default := 34.0;
        in attribute fab_factor : Real default := 0.45;
        in attribute install_factor : Real default := 0.30;

        out attribute material_cost : Real = base_cost + circuit_count_in * cost_per_circuit;
        out attribute fab_cost : Real = material_cost * fab_factor;
        out attribute install_cost : Real = material_cost * install_factor;
        out attribute total_cost : Real = material_cost + fab_cost + install_cost;
        out attribute idiot_index : Real = total_cost / material_cost;
    }

    calc def PermittingCostCalc {
        doc /*
        Cost calculation for permitting and interconnection.
        Soft cost — no material/fabrication/installation split.
        Total cost is purely based on system capacity.

        **Source**: Solar industry cost modeling
        **Last Updated**: 2026-02-01
        */

        in attribute system_capacity_kw_in : Real;

        in attribute cost_per_kw : Real default := 187.5;

        out attribute material_cost : Real = 0.0;
        out attribute fab_cost : Real = 0.0;
        out attribute install_cost : Real = 0.0;
        out attribute total_cost : Real = system_capacity_kw_in * cost_per_kw;
        out attribute idiot_index : Real = 0.0;
    }

    // ============================================================
    // SECTION 2: ALLOCATION COST CALCDEF (1 def)
    // ============================================================

    calc def AllocationCostCalc {
        doc /*
        Bundled allocation costs for assembly-level minor items.
        Covers items not modeled as separate parts: fasteners, seals, wiring.

        Duplicated from coffee maker (CoffeeMakerLibrary) — not shared because
        the coffee maker uses a local 'Costed Component' interface.

        **Pattern**: Rule R3 from strategic cost patterns
        **Reference**: models/tests/coffee_maker/library.sysml:195-220
        **Last Updated**: 2026-02-01
        */

        in attribute child_count : Real;
        in attribute total_child_mass : Real;

        in attribute fastener_cost_per_child : Real default := 0.50;
        in attribute seal_cost_per_child : Real default := 0.30;
        in attribute wiring_cost_per_kg : Real default := 2.0;

        out attribute fastener_cost : Real = child_count * fastener_cost_per_child;
        out attribute seal_cost : Real = child_count * seal_cost_per_child;
        out attribute wiring_cost : Real = total_child_mass * wiring_cost_per_kg;
        out attribute total_allocation : Real = fastener_cost + seal_cost + wiring_cost;

        out attribute material_portion : Real = total_allocation * 0.8;
    }

    // ============================================================
    // SECTION 3: SYSTEM-LEVEL CALCDEFS (5 defs)
    // ============================================================

    calc def EnergyProductionCalc {
        doc /*
        Annual energy production calculation.
        Matches PyFECONS lcoe.py denominator: 8760 * p_net * n_mod_in * plant_availability_in.

        **Source**: PyFECONS /home/reid/PyFECONS/pyfecons/costing/calculations/lcoe.py:24
        **Last Updated**: 2026-02-01
        */

        in attribute p_net_mw_in : Real;
        in attribute n_mod_in : Real;
        in attribute plant_availability_in : Real;

        out attribute annual_energy_mwh : Real = 8760.0 * p_net_mw_in * n_mod_in * plant_availability_in;
    }

    calc def AnnualizedOMCalc {
        doc /*
        Annualized operations and maintenance cost.
        Matches PyFECONS cas70_annualized_om.py: om_rate * p_net_kw_in.

        **Source**: PyFECONS /home/reid/PyFECONS/pyfecons/costing/calculations/cas70_annualized_om.py:10
        **Last Updated**: 2026-02-01
        */

        in attribute om_rate_per_kw_year_in : Real;
        in attribute p_net_kw_in : Real;

        out attribute annual_om_cost : Real = om_rate_per_kw_year_in * p_net_kw_in;
    }

    calc def AnnualizedFuelCalc {
        doc /*
        Annualized fuel cost.
        For solar: fuel_unit_cost_in = 0, fuel_consumption_in = 0 → annual_fuel_cost = 0.
        Included for pipeline completeness (fusion plants have non-zero fuel costs).

        **Source**: PyFECONS /home/reid/PyFECONS/pyfecons/costing/calculations/cas80_annualized_fuel.py:14
        **Last Updated**: 2026-02-01
        */

        in attribute fuel_unit_cost_in : Real;
        in attribute fuel_consumption_in : Real;

        out attribute annual_fuel_cost : Real = fuel_unit_cost_in * fuel_consumption_in;
    }

    calc def AnnualizedFinancialCalc {
        doc /*
        Annualized financial cost using Capital Recovery Factor.
        CRF = r * (1+r)^n / ((1+r)^n - 1)
        Computes CRF from discount_rate_in and plant_lifetime_in rather than using
        PyFECONS's hardcoded 0.09 default.

        **Source**: PyFECONS /home/reid/PyFECONS/pyfecons/costing/calculations/cas90_annualized_financial.py:14
        **Last Updated**: 2026-02-01
        */

        in attribute total_capex : Real;
        in attribute discount_rate_in : Real;
        in attribute plant_lifetime_in : Real;

        out attribute capital_recovery_factor : Real =
            discount_rate_in * (1.0 + discount_rate_in) ** plant_lifetime_in
            / ((1.0 + discount_rate_in) ** plant_lifetime_in - 1.0);
        out attribute annualized_capital_cost : Real = capital_recovery_factor * total_capex;
    }

    calc def LCOECalc {
        doc /*
        Levelized Cost of Electricity calculation.
        Matches PyFECONS lcoe.py formula with inflation escalation on O&M and fuel.
        LCOE = (C900000 + (C700000 + C800000) * (1 + inflation)^lifetime) / annual_energy

        **Source**: PyFECONS /home/reid/PyFECONS/pyfecons/costing/calculations/lcoe.py:18-25
        **Last Updated**: 2026-02-01
        */

        in attribute annualized_capital_cost : Real;
        in attribute annual_om_cost : Real;
        in attribute annual_fuel_cost : Real;
        in attribute yearly_inflation_in : Real;
        in attribute plant_lifetime_in : Real;
        in attribute annual_energy_mwh : Real;

        out attribute lcoe_per_mwh : Real =
            (annualized_capital_cost + (annual_om_cost + annual_fuel_cost)
             * (1.0 + yearly_inflation_in) ** plant_lifetime_in)
            / annual_energy_mwh;
    }

    // ============================================================
    // SECTION 4: LEAF PART DEFINITIONS (9 defs)
    // ============================================================

    part def 'PV Module' :> 'Costed Component' {
        doc /*
        Photovoltaic module that converts sunlight to electricity.
        Contains embedded cost model that computes cost from parameters.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS220101;

        // Design parameters (set by usage in design.sysml)
        attribute wattage : Real;
        attribute efficiency : Real;

        // Embedded cost model
        calc cost_model : PVModuleCostCalc {
            in wattage_in = wattage;
            in efficiency_in = efficiency;
        }

        // Expose cost outputs via redefinition
        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'String Inverter' :> 'Costed Component' {
        doc /*
        String inverter for DC-to-AC conversion.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS220107;

        attribute power_rating : Real;

        calc cost_model : InverterCostCalc {
            in power_rating_in = power_rating;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Array BOS' :> 'Costed Component' {
        doc /*
        Solar array balance-of-system: combiners, disconnects, conduit.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS24;

        attribute string_count : Real;
        attribute panel_count : Real;

        calc cost_model : ArrayBOSCostCalc {
            in string_count_in = string_count;
            in panel_count_in = panel_count;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Battery Pack' :> 'Costed Component' {
        doc /*
        Battery pack for energy storage.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS27;

        attribute capacity_kwh : Real;
        attribute chemistry_factor : Real;

        calc cost_model : BatteryPackCostCalc {
            in capacity_kwh_in = capacity_kwh;
            in chemistry_factor_in = chemistry_factor;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Hybrid Inverter' :> 'Costed Component' {
        doc /*
        Bidirectional hybrid inverter for battery charge/discharge.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS220107;

        attribute power_rating : Real;

        calc cost_model : HybridInverterCostCalc {
            in power_rating_in = power_rating;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Battery BOS' :> 'Costed Component' {
        doc /*
        Battery balance-of-system: management, wiring, thermal management.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS2207;

        attribute pack_count : Real;

        calc cost_model : BatteryBOSCostCalc {
            in pack_count_in = pack_count;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Racking & Mounting' :> 'Costed Component' {
        doc /*
        Racking and mounting hardware for solar panels.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS220105;

        attribute panel_count : Real;
        attribute tilt_angle : Real;

        calc cost_model : RackingCostCalc {
            in panel_count_in = panel_count;
            in tilt_angle_in = tilt_angle;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Electrical Panel' :> 'Costed Component' {
        doc /*
        Main electrical panel with breakers.

        **Pattern**: Nested cost model (Pattern A)
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS24;

        attribute circuit_count : Real;

        calc cost_model : ElectricalPanelCostCalc {
            in circuit_count_in = circuit_count;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = cost_model.material_cost;
        :>> fabrication_cost = cost_model.fab_cost;
        :>> installation_cost = cost_model.install_cost;
        :>> idiot_index = cost_model.idiot_index;
    }

    part def 'Permitting & Interconnect' :> 'Costed Component' {
        doc /*
        Permitting and utility interconnection costs.
        Soft cost — no material/fabrication/installation split.

        **Pattern**: Nested cost model (Pattern A) — soft cost variant
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS10;

        attribute system_capacity_kw : Real;

        calc cost_model : PermittingCostCalc {
            in system_capacity_kw_in = system_capacity_kw;
        }

        :>> capital_cost = cost_model.total_cost;
        :>> raw_material_cost = 0.0;
        :>> fabrication_cost = 0.0;
        :>> installation_cost = 0.0;
        :>> idiot_index = 0.0;
    }

    // ============================================================
    // SECTION 5: ASSEMBLY PART DEFINITIONS (3 defs + 1 top-level)
    // ============================================================

    part def 'Solar Array' :> 'Costed Component' {
        doc /*
        Solar array sub-assembly containing PV modules, inverters, and BOS.
        Includes allocation costs for assembly-level minor items.

        **Pattern**: Assembly aggregation + Allocation costs
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS22;

        // Parameterized multiplicity
        attribute module_count : Integer default := 20;
        attribute inverter_count : Integer default := 4;

        // Child parts
        part pv_module : 'PV Module' [module_count];
        part inverter : 'String Inverter' [inverter_count];
        part array_bos : 'Array BOS';

        // Allocation cost model for minor items
        calc allocation_model : AllocationCostCalc {
            in child_count = 25.0;
            in total_child_mass = 50.0;
        }

        attribute misc_hardware_cost : Real = allocation_model.total_allocation;

        // Aggregate costs from children using sum() for arrayed parts
        attribute pv_module_capital_cost : Real = sum(pv_module.capital_cost);
        attribute inverter_capital_cost : Real = sum(inverter.capital_cost);
        attribute array_bos_capital_cost : Real = array_bos.capital_cost;
        :>> capital_cost =
            pv_module_capital_cost +
            inverter_capital_cost +
            array_bos_capital_cost +
            misc_hardware_cost;

        attribute pv_module_raw_material_cost : Real = sum(pv_module.raw_material_cost);
        attribute inverter_raw_material_cost : Real = sum(inverter.raw_material_cost);
        attribute array_bos_raw_material_cost : Real = array_bos.raw_material_cost;
        attribute allocation_model_material_portion : Real = allocation_model.material_portion;
        :>> raw_material_cost =
            pv_module_raw_material_cost +
            inverter_raw_material_cost +
            array_bos_raw_material_cost +
            allocation_model_material_portion;

        attribute pv_module_fabrication_cost : Real = sum(pv_module.fabrication_cost);
        attribute inverter_fabrication_cost : Real = sum(inverter.fabrication_cost);
        attribute array_bos_fabrication_cost : Real = array_bos.fabrication_cost;
        :>> fabrication_cost =
            pv_module_fabrication_cost +
            inverter_fabrication_cost +
            array_bos_fabrication_cost;

        attribute pv_module_installation_cost : Real = sum(pv_module.installation_cost);
        attribute inverter_installation_cost : Real = sum(inverter.installation_cost);
        attribute array_bos_installation_cost : Real = array_bos.installation_cost;
        :>> installation_cost =
            pv_module_installation_cost +
            inverter_installation_cost +
            array_bos_installation_cost;

        :>> idiot_index = capital_cost / raw_material_cost;
    }

    part def 'Battery System' :> 'Costed Component' {
        doc /*
        Battery storage sub-assembly containing packs, hybrid inverter, and BOS.

        **Pattern**: Assembly aggregation
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS25;

        // Parameterized multiplicity
        attribute pack_count : Integer default := 8;

        // Child parts
        part battery_pack : 'Battery Pack' [pack_count];
        part hybrid_inverter : 'Hybrid Inverter';
        part battery_bos : 'Battery BOS';

        // Aggregate costs from children
        attribute battery_pack_capital_cost : Real = sum(battery_pack.capital_cost);
        attribute hybrid_inverter_capital_cost : Real = hybrid_inverter.capital_cost;
        attribute battery_bos_capital_cost : Real = battery_bos.capital_cost;
        :>> capital_cost =
            battery_pack_capital_cost +
            hybrid_inverter_capital_cost +
            battery_bos_capital_cost;

        attribute battery_pack_raw_material_cost : Real = sum(battery_pack.raw_material_cost);
        attribute hybrid_inverter_raw_material_cost : Real = hybrid_inverter.raw_material_cost;
        attribute battery_bos_raw_material_cost : Real = battery_bos.raw_material_cost;
        :>> raw_material_cost =
            battery_pack_raw_material_cost +
            hybrid_inverter_raw_material_cost +
            battery_bos_raw_material_cost;

        attribute battery_pack_fabrication_cost : Real = sum(battery_pack.fabrication_cost);
        attribute hybrid_inverter_fabrication_cost : Real = hybrid_inverter.fabrication_cost;
        attribute battery_bos_fabrication_cost : Real = battery_bos.fabrication_cost;
        :>> fabrication_cost =
            battery_pack_fabrication_cost +
            hybrid_inverter_fabrication_cost +
            battery_bos_fabrication_cost;

        attribute battery_pack_installation_cost : Real = sum(battery_pack.installation_cost);
        attribute hybrid_inverter_installation_cost : Real = hybrid_inverter.installation_cost;
        attribute battery_bos_installation_cost : Real = battery_bos.installation_cost;
        :>> installation_cost =
            battery_pack_installation_cost +
            hybrid_inverter_installation_cost +
            battery_bos_installation_cost;

        :>> idiot_index = capital_cost / raw_material_cost;
    }

    part def 'Site Infrastructure' :> 'Costed Component' {
        doc /*
        Site infrastructure sub-assembly: racking, electrical panel, permitting.
        All singleton children (no arrayed parts).

        Note: idiot_index will be higher than typical physical assemblies because
        permitting (soft cost) contributes zero material cost. This is correct
        behavior — it reflects that most cost is labor/permitting, not materials.

        **Pattern**: Assembly aggregation
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS21;

        // Child parts (all singletons)
        part racking : 'Racking & Mounting';
        part electrical_panel : 'Electrical Panel';
        part permitting : 'Permitting & Interconnect';

        // Aggregate costs from children using + for singletons
        attribute racking_capital_cost : Real = racking.capital_cost;
        attribute electrical_panel_capital_cost : Real = electrical_panel.capital_cost;
        attribute permitting_capital_cost : Real = permitting.capital_cost;
        :>> capital_cost =
            racking_capital_cost +
            electrical_panel_capital_cost +
            permitting_capital_cost;

        attribute racking_raw_material_cost : Real = racking.raw_material_cost;
        attribute electrical_panel_raw_material_cost : Real = electrical_panel.raw_material_cost;
        attribute permitting_raw_material_cost : Real = permitting.raw_material_cost;
        :>> raw_material_cost =
            racking_raw_material_cost +
            electrical_panel_raw_material_cost +
            permitting_raw_material_cost;

        attribute racking_fabrication_cost : Real = racking.fabrication_cost;
        attribute electrical_panel_fabrication_cost : Real = electrical_panel.fabrication_cost;
        attribute permitting_fabrication_cost : Real = permitting.fabrication_cost;
        :>> fabrication_cost =
            racking_fabrication_cost +
            electrical_panel_fabrication_cost +
            permitting_fabrication_cost;

        attribute racking_installation_cost : Real = racking.installation_cost;
        attribute electrical_panel_installation_cost : Real = electrical_panel.installation_cost;
        attribute permitting_installation_cost : Real = permitting.installation_cost;
        :>> installation_cost =
            racking_installation_cost +
            electrical_panel_installation_cost +
            permitting_installation_cost;

        :>> idiot_index = capital_cost / raw_material_cost;
    }

    part def 'Solar Battery Plant' :> 'Costed Component' {
        doc /*
        Top-level assembly representing the complete solar+battery plant.
        Aggregates all subsystems: solar array, battery system, site infrastructure.

        **Pattern**: Assembly aggregation
        **Last Updated**: 2026-02-01
        */

        :>> cas_category = CASCategory::CAS20;

        // Child sub-assemblies
        part solar_array : 'Solar Array';
        part battery_system : 'Battery System';
        part site_infra : 'Site Infrastructure';

        // Top-level aggregation
        attribute solar_array_capital_cost : Real = solar_array.capital_cost;
        attribute battery_system_capital_cost : Real = battery_system.capital_cost;
        attribute site_infra_capital_cost : Real = site_infra.capital_cost;
        :>> capital_cost =
            solar_array_capital_cost +
            battery_system_capital_cost +
            site_infra_capital_cost;

        attribute solar_array_raw_material_cost : Real = solar_array.raw_material_cost;
        attribute battery_system_raw_material_cost : Real = battery_system.raw_material_cost;
        attribute site_infra_raw_material_cost : Real = site_infra.raw_material_cost;
        :>> raw_material_cost =
            solar_array_raw_material_cost +
            battery_system_raw_material_cost +
            site_infra_raw_material_cost;

        attribute solar_array_fabrication_cost : Real = solar_array.fabrication_cost;
        attribute battery_system_fabrication_cost : Real = battery_system.fabrication_cost;
        attribute site_infra_fabrication_cost : Real = site_infra.fabrication_cost;
        :>> fabrication_cost =
            solar_array_fabrication_cost +
            battery_system_fabrication_cost +
            site_infra_fabrication_cost;

        attribute solar_array_installation_cost : Real = solar_array.installation_cost;
        attribute battery_system_installation_cost : Real = battery_system.installation_cost;
        attribute site_infra_installation_cost : Real = site_infra.installation_cost;
        :>> installation_cost =
            solar_array_installation_cost +
            battery_system_installation_cost +
            site_infra_installation_cost;

        :>> idiot_index = capital_cost / raw_material_cost;
    }
}
