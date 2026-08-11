/**
 * Thermal Load Analysis Calculations
 *
 * Parasitic power consumption calculations for fusion reactor subsystems.
 * These calculations enable bottom-up power balance validation by computing
 * auxiliary loads from first principles rather than using empirical placeholders.
 *
 * Created: 2025-11-09
 * Sources: PyFECONS thermal.py, cas220103_coils.py, PowerBalance.py
 */
package FusionAnalysesThermalLoads {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Magnet Cryogenic Load
     *
     * Calculates refrigeration power required for superconducting magnet systems.
     *
     * Heat loads include:
     * 1. Nuclear heating from neutron/gamma radiation
     * 2. AC losses from field ramping (small for steady-state)
     * 3. Structural heat leak from room-temperature supports
     *
     * Refrigeration power scales as (T_ambient / T_operating) / carnot_efficiency
     * due to thermodynamic work required to pump heat from cryogenic to ambient.
     *
     * Formula:
     *   thermal_load = nuclear_heating + ac_losses + heat_leak
     *   cooling_power = (thermal_load / operating_temp) × (300K / carnot_eff)
     *
     * Source: PyFECONS thermal.py lines 18-64, cas220103_coils.py lines 230-250
     * Reference: ITER cryogenic system design
     * Typical Values:
     *   - Nuclear heating: 0.05 × P_neutron × (A_magnet / A_total)
     *   - Heat leak: 0.05 MW per m³ of magnet volume
     *   - Carnot efficiency: 0.2-0.4 (realistic refrigerator)
     * Assumptions:
     *   - 5% of neutron power reaches magnets (95% absorbed by blanket/shield)
     *   - Steady-state operation (no transient field ramping)
     *   - Uniform nuclear heating distribution
     * Last Updated: 2025-11-09
     */
    calc def MagnetCryogenicLoad {
        in attribute magnet_volume : Real;           // m³ - Total magnet volume
        in attribute magnet_surface_area : Real;     // m² - Exposed magnet surface
        in attribute first_wall_area : Real;         // m² - Total first wall area
        in attribute p_neutron : Real;               // MW - Neutron power from fusion
        in attribute b_field : Real;                 // T - Peak magnetic field
        in attribute operating_temp : Real;          // K - Magnet operating temperature (4-20K)
        in attribute carnot_efficiency : Real = 0.3; // Dimensionless - Refrigerator efficiency

        // Heat load components (at cryogenic temperature)
        attribute nuclear_heating : Real =
            0.05 * p_neutron * (magnet_surface_area / first_wall_area);  // MW

        attribute ac_losses : Real = 0.0;  // MW - Negligible for steady-state

        attribute heat_leak : Real = magnet_volume * 0.05;  // MW - Structural conduction

        attribute thermal_load_cryo : Real =
            nuclear_heating + ac_losses + heat_leak;  // MW at cryogenic temp

        // Wall-plug refrigeration power (Carnot penalty)
        out attribute cooling_power : Real =
            (thermal_load_cryo / operating_temp) * (300.0 / carnot_efficiency);  // MW

        constraint PositiveInputs {
            doc /* All inputs must be positive */
            magnet_volume > 0 and magnet_surface_area > 0 and
            first_wall_area > 0 and p_neutron > 0 and b_field > 0 and
            operating_temp > 0
        }

        constraint ReasonableCryoTemp {
            doc /* Operating temperature must be cryogenic (< 80K) */
            operating_temp > 1.0 and operating_temp < 80.0
        }

        constraint CarnotEfficiencyPhysical {
            doc /* Carnot efficiency must be between 0 and 1 */
            carnot_efficiency > 0 and carnot_efficiency < 1.0
        }
    }

    /**
     * Coolant Pump Power
     *
     * Calculates mechanical pump power required for primary/secondary coolant loops.
     *
     * Power required to circulate coolant at specified flow rate against system
     * pressure drop. Accounts for pump efficiency (mechanical + hydraulic losses).
     *
     * Formula:
     *   pump_power = (flow_rate × pressure_drop) / pump_efficiency
     *
     * Alternate formulation from PyFECONS:
     *   pump_power = f_pcppf × p_thermal_electric
     *   where f_pcppf = primary coolant pumping power fraction (typically 0.06)
     *
     * Source: PyFECONS PowerBalance.py line 26
     * Reference: Fluid mechanics pump power equation
     * Typical Values:
     *   - f_pcppf = 0.06 (6% of thermal electric power)
     *   - Pump efficiency = 0.5-0.8
     *   - Pressure drop = 0.5-2.0 MPa (depends on loop design)
     * Assumptions:
     *   - Incompressible fluid
     *   - Steady-state flow
     *   - Single-speed pumps (no variable frequency drives)
     * Last Updated: 2025-11-09
     */
    calc def CoolantPumpPower {
        in attribute p_thermal_electric : Real;      // MW - Thermal electric power
        in attribute f_pcppf : Real = 0.06;          // Dimensionless - Pumping power fraction
        in attribute pump_efficiency : Real = 0.5;   // Dimensionless - Pump efficiency

        out attribute pump_power : Real =
            f_pcppf * p_thermal_electric / pump_efficiency;  // MW

        constraint PositiveInput {
            doc /* Thermal electric power must be positive */
            p_thermal_electric > 0
        }

        constraint ReasonableFraction {
            doc /* Pumping fraction typically 2-10% */
            f_pcppf > 0.02 and f_pcppf < 0.10
        }

        constraint PumpEfficiencyPhysical {
            doc /* Pump efficiency must be between 0 and 1 */
            pump_efficiency > 0 and pump_efficiency <= 1.0
        }
    }

    /**
     * Heating Wall-Plug Power
     *
     * Calculates total electrical power consumed by auxiliary heating systems
     * to deliver specified plasma heating power.
     *
     * Heating systems (NBI, ECRH, ICRH) have efficiency losses:
     * - NBI: 30-50% (ion source, accelerator, neutralizer, duct transmission)
     * - ECRH: 40-60% (gyrotron efficiency, transmission, coupling)
     * - ICRH: 50-70% (RF amplifier efficiency, antenna coupling)
     *
     * Formula:
     *   wall_plug_power = delivered_power / heating_efficiency
     *
     * Source: PyFECONS inputs.json lines 35-39
     * Reference: NBI system design (ITER, DEMO)
     * Typical Values:
     *   - NBI efficiency: 0.3-0.5
     *   - ECRH efficiency: 0.4-0.6
     *   - ICRH efficiency: 0.5-0.7
     * Assumptions:
     *   - All delivered power couples to plasma
     *   - Steady-state operation
     *   - No shine-through losses (neutral beams fully absorbed)
     * Last Updated: 2025-11-09
     */
    calc def HeatingWallPlugPower {
        in attribute delivered_power : Real;          // MW - Power delivered to plasma
        in attribute heating_efficiency : Real = 0.5; // Dimensionless - System efficiency

        out attribute wall_plug_power : Real =
            delivered_power / heating_efficiency;  // MW

        constraint PositiveDelivered {
            doc /* Delivered power must be positive */
            delivered_power > 0
        }

        constraint EfficiencyPhysical {
            doc /* Heating efficiency must be between 0 and 1 */
            heating_efficiency > 0 and heating_efficiency < 1.0
        }

        constraint ReasonableEfficiency {
            doc /* Heating efficiency typically 20-80% */
            heating_efficiency > 0.20 and heating_efficiency < 0.80
        }
    }

    /**
     * Vacuum Pump Power
     *
     * Calculates electrical power for mechanical vacuum pumps (roughing, turbo).
     * Does not include cryopump refrigeration (separate calculation).
     *
     * Power scales with pumping speed and operating pressure. Practical vacuum
     * pumps have efficiency 30-50% due to motor and mechanical losses.
     *
     * Formula:
     *   pump_power_per_unit = (pumping_speed × pressure) / 1e6
     *   pump_power = pump_power_per_unit × pump_count / efficiency
     *
     * Source: PyFECONS cas220106_vacuum_system_costs.py
     * Reference: Vacuum technology fundamentals
     * Typical Values:
     *   - Pumping speed: 200 m³/s total (48 pumps × 4.17 m³/s each)
     *   - Base pressure: 1e-4 Pa (10⁻⁶ torr)
     *   - Pump efficiency: 0.3-0.5
     * Assumptions:
     *   - Constant pumping speed (actual speed varies with pressure)
     *   - All pumps operating simultaneously
     *   - No regeneration cycles
     * Last Updated: 2025-11-09
     */
    calc def VacuumPumpPower {
        in attribute pumping_speed_total_in : Real;     // m³/s - Total pumping speed
        in attribute base_pressure : Real;           // Pa - Operating vacuum level
        in attribute pump_count : Real;              // Dimensionless - Number of pumps
        in attribute pump_efficiency : Real = 0.4;   // Dimensionless - Mechanical efficiency

        attribute pump_power_per_unit : Real =
            (pumping_speed_total_in * base_pressure) / 1.0e6;  // MW per pump

        out attribute pump_power : Real =
            pump_power_per_unit * pump_count / pump_efficiency;  // MW

        constraint PositiveInputs {
            doc /* Pumping speed and pressure must be positive */
            pumping_speed_total_in > 0 and base_pressure > 0 and pump_count > 0
        }

        constraint VacuumPressure {
            doc /* Base pressure must be in vacuum range (< 100 Pa) */
            base_pressure > 1.0e-6 and base_pressure < 100.0
        }

        constraint EfficiencyPhysical {
            doc /* Pump efficiency must be between 0 and 1 */
            pump_efficiency > 0 and pump_efficiency <= 1.0
        }
    }

    /**
     * Cryopump Refrigeration Power
     *
     * Calculates refrigeration power for cryogenic vacuum pumps.
     * Distinct from mechanical vacuum pumps - uses cryogenic surfaces to
     * condense/adsorb gas molecules.
     *
     * Refrigeration power determined by:
     * 1. Gas load (molecules condensing release heat of condensation)
     * 2. Radiation heat load from warm surfaces
     * 3. Conduction through supports
     * 4. Carnot penalty (T_ambient / T_cryo)
     *
     * Formula:
     *   thermal_load = cryo_pump_count × pump_capacity × load_factor
     *   refrigeration_power = thermal_load × (T_ambient / T_cryo) / carnot_eff
     *
     * Source: PyFECONS inputs.json line 24
     * Reference: Cryopump design literature
     * Typical Values:
     *   - Load factor: 0.001 MW per m³/s (empirical)
     *   - Operating temp: 10-20K
     *   - Carnot efficiency: 0.2-0.4
     * Assumptions:
     *   - Continuous operation (no regeneration during pulse)
     *   - Uniform gas load distribution
     *   - Steady-state thermal loads
     * Last Updated: 2025-11-09
     */
    calc def CryoPumpRefrigeration {
        in attribute cryo_pump_count : Real;          // Dimensionless - Number of cryopumps
        in attribute pump_capacity : Real;            // m³/s - Capacity per pump
        in attribute operating_temp : Real = 20.0;    // K - Cryopump operating temperature
        in attribute carnot_efficiency : Real = 0.3;  // Dimensionless - Refrigerator efficiency
        in attribute load_factor : Real = 0.001;      // MW per m³/s - Empirical load

        attribute thermal_load : Real =
            cryo_pump_count * pump_capacity * load_factor;  // MW at cryo temp

        out attribute refrigeration_power : Real =
            thermal_load * (300.0 / operating_temp) / carnot_efficiency;  // MW

        constraint PositiveInputs {
            doc /* Pump count and capacity must be positive */
            cryo_pump_count > 0 and pump_capacity > 0
        }

        constraint CryogenicTemp {
            doc /* Operating temperature must be cryogenic (< 80K) */
            operating_temp > 4.0 and operating_temp < 80.0
        }

        constraint CarnotPhysical {
            doc /* Carnot efficiency must be between 0 and 1 */
            carnot_efficiency > 0 and carnot_efficiency < 1.0
        }
    }

    /**
     * Tritium Processing Power
     *
     * Calculates power for tritium fuel cycle systems:
     * - Isotope separation (cryogenic distillation)
     * - Tritium extraction from breeding blanket
     * - Purification and impurity removal
     * - Storage and delivery systems
     *
     * Power scales with tritium throughput, which is proportional to fusion power.
     * Each D-T fusion reaction consumes 1 tritium nucleus, producing 17.58 MeV.
     *
     * Formula:
     *   tritium_burn_rate = fusion_power / 17.58  // MW → reactions/s
     *   processing_power = tritium_burn_rate × processing_factor
     *
     * Source: PyFECONS inputs.json line 29
     * Reference: ITER tritium systems design
     * Typical Values:
     *   - Processing factor: empirical constant ~ 0.004 MW per MW fusion
     *   - Expected for CATF: 10 MW (for 2600 MW fusion)
     * Assumptions:
     *   - Processing power scales linearly with throughput
     *   - Includes all tritium handling systems
     *   - Steady-state fuel cycle (no startup inventory)
     * Last Updated: 2025-11-09
     */
    calc def TritiumProcessingPower {
        in attribute fusion_power : Real;                      // MW - Fusion power
        in attribute processing_factor : Real = 0.00385;       // MW per MW fusion (empirical)

        out attribute processing_power : Real =
            fusion_power * processing_factor;  // MW

        constraint PositiveFusion {
            doc /* Fusion power must be positive */
            fusion_power > 0
        }

        constraint ReasonableFactor {
            doc /* Processing factor typically 0.001-0.01 */
            processing_factor > 0.001 and processing_factor < 0.01
        }
    }

    /**
     * Auxiliary Systems Power
     *
     * Calculates power for plant auxiliary systems:
     * - Building HVAC and lighting
     * - Diagnostics and instrumentation
     * - Control systems and computers
     * - Communication and security systems
     * - Maintenance equipment
     *
     * Power estimated as fraction of gross electric output (empirical scaling).
     *
     * Formula:
     *   auxiliary_power = gross_electric × auxiliary_fraction
     *
     * Source: PyFECONS inputs.json line 30 (p_house)
     * Reference: Power plant auxiliary load studies
     * Typical Values:
     *   - Auxiliary fraction: 0.005-0.015 (0.5-1.5% of gross)
     *   - Expected for CATF: ~10-14 MW (for ~1500 MW gross)
     * Assumptions:
     *   - Auxiliary loads scale with plant size
     *   - Includes all non-process loads
     *   - Steady-state operation
     * Last Updated: 2025-11-09
     */
    calc def AuxiliarySystemsPower {
        in attribute gross_electric : Real;                // MW - Gross electric power
        in attribute auxiliary_fraction : Real = 0.009;    // Dimensionless - Aux load fraction

        out attribute auxiliary_power : Real =
            gross_electric * auxiliary_fraction;  // MW

        constraint PositiveGross {
            doc /* Gross electric must be positive */
            gross_electric > 0
        }

        constraint ReasonableFraction {
            doc /* Auxiliary fraction typically 0.3-2% */
            auxiliary_fraction > 0.003 and auxiliary_fraction < 0.02
        }
    }
}
