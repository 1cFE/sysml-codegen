/*
 * CATF MFE Vacuum System Design Instance
 *
 * This file defines the specific vacuum vessel and pumping system for the
 * Clean Air Task Force MFE reference design.
 *
 * Parameters extracted from PyFECONS DefineInputs.py lines 241-255.
 */

package CATFMFEVacuum {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // Import thermal load calc defs
    private import FusionAnalysesThermalLoads::VacuumPumpPower;
    private import FusionAnalysesThermalLoads::CryoPumpRefrigeration;

    /*
     * CATF MFE Vacuum Vessel Instance
     */
    part catf_vacuum_vessel {
        doc /*
        CATF MFE vacuum vessel - primary vacuum boundary and structural support.

        **Source**: PyFECONS DefineInputs.py lines 241-255
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py

        **Function**:
        1. Maintain vacuum environment for plasma (< 10^-6 torr base)
        2. Primary structural pressure boundary (1 atm external load)
        3. Secondary confinement for tritium
        4. Support for internal components (blanket, shield, first wall)
        5. Port penetrations for diagnostics, heating, pumping

        **Design Basis**:
        - Material: SS316 stainless steel (standard for vacuum vessels)
        - Wall thickness: 0.2 m (from radial build line 82)
        - Design pressure: 1 atm external, vacuum internal
        - Operating temperature: ~50-100 C (from blanket heat)

        **ASME Code Compliance**:
        - Designed per ASME Section VIII (pressure vessels)
        - Safety factor: 3-4 on ultimate strength
        - Fatigue analysis for thermal cycling

        **Last Updated**: 2025-11-01
        */

        // Geometry (from radial build and PyFECONS vacuum config)
        attribute inner_radius : Real = 6.3 [m];   // From radial build line 82
        attribute wall_thickness : Real = 0.2 [m]; // From radial build line 82
        // Relation (undirected): outer_radius = inner_radius + wall_thickness. A structural
        // identity of the vessel wall, true by construction rather than something to check.
        // Direction is a CHOSEN BASIS, not physics: inner_radius and wall_thickness are taken as
        // free and outer_radius derived. Solving the same relation for wall_thickness would be
        // equally valid. Authority: owner-disposition.md Group A, A8 (derive-instead).
        attribute outer_radius : Real = inner_radius + wall_thickness;  // m
        attribute height : Real = 18.0 [m];        // Estimated from 2*elongation*plasma_outer_radius

        // Material Properties
        attribute material : String = "SS316";
        attribute temperature_operating : Real = 350 [K]; // ~77 C, typical vessel temp

        // Pressure Design
        attribute design_pressure_external : Real = 101325;    // Pa (1 atm)
        attribute design_pressure_internal : Real = 1.0e-4;    // Pa (~10^-6 torr)
        attribute safety_factor : Real = 3.5;

        // Port Configuration
        attribute n_ports : Real = 18;  // Estimated: diagnostic, heating, pumping, maintenance

        // Volume Calculations
        attribute volume_shell : Real = 800;  // m^3, TO BE CALCULATED from geometry
        attribute volume_internal : Real = 1500; // m^3, internal vacuum volume

        // Mass Estimates
        attribute mass_vessel : Real = 400000 [kg];  // TO BE CALCULATED from volume and density

        // Vacuum Performance
        attribute base_pressure : Real = 1.0e-4;     // Pa (~10^-6 torr)
        attribute pumpdown_time : Real = 3600;       // s (1 hour to base pressure)

        // Structural Properties
        attribute stress_max_allowable : Real = 138e6;  // Pa (138 MPa = SS316 yield/2.5)
        attribute stress_operating : Real = 50e6;       // Pa (50 MPa, conservative)

        // Leak Rate
        attribute leak_rate : Real = 1.0e-6;  // Pa*m^3/s (tight vacuum specification)

    }

    /*
     * CATF MFE Vacuum Pumping System
     */
    part catf_vacuum_pumping {
        doc /*
        Vacuum pumping system for CATF MFE reactor.

        **Source**: PyFECONS DefineInputs.py lines 241-255
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py

        **System Components**:
        1. Roughing pumps: Atmospheric to 10^-3 torr
        2. Turbomolecular pumps: 10^-3 to 10^-7 torr
        3. Cryopumps: Operating vacuum maintenance
        4. Getter pumps: Hydrogen isotope pumping

        **Pumping Requirements**:
        - Initial pumpdown: ~1-2 hours to base pressure
        - Between pulses: Remove impurities, maintain base
        - During pulse: Exhaust He ash, maintain pressure

        **Pumping Speed Calculation**:
        From PyFECONS lines 250-254:
        - Assume 1 s vac rate (time constant)
        - Reactor volume: ~200 m^3 (estimated)
        - Required speed: S = V/τ = 200/1 = 200 m^3/s

        **Pump Configuration**:
        From PyFECONS line 254: vpump_cap = 200/48 ≈ 4.17 m^3/s per pump
        Therefore: 48 pumps at 4.17 m^3/s each → Total 200 m^3/s

        **Last Updated**: 2025-11-01
        */

        // Pump Sizing (from PyFECONS lines 250-254)
        attribute volume_to_pump : Real = 200;  // m^3 (reactor volume estimate)
        attribute vacuum_time_constant : Real = 1.0;  // s (line 250)
        attribute pumping_speed_total : Real = 200;  // m^3/s = volume/time_constant

        // Pump Count and Capacity
        attribute n_pumps : Real = 48;  // From PyFECONS line 254 (200/48)
        attribute pump_capacity_each : Real = 4.17;  // m^3/s per pump (line 254)

        // Cost (from PyFECONS line 252)
        attribute cost_per_pump : Real = 40000;  // USD, scaled from 1985 dollars

        // Pump Types
        part roughing_pumps {
            doc /* Mechanical roughing pumps for initial pumpdown */
            attribute n_pumps : Real = 4;
            attribute pumping_speed : Real = 10;  // m^3/s each
            attribute pressure_range_low : Real = 101325;  // Pa (1 atm)
            attribute pressure_range_high : Real = 100;    // Pa (~1 torr)
        }

        part turbo_pumps {
            doc /* Turbomolecular pumps for high vacuum */
            attribute n_pumps : Real = 12;
            attribute pumping_speed : Real = 5;  // m^3/s each
            attribute pressure_range_low : Real = 100;    // Pa
            attribute pressure_range_high : Real = 1.0e-5; // Pa
        }

        part cryo_pumps {
            doc /* Cryogenic pumps for main vacuum maintenance */
            attribute n_pumps : Real = 32;
            attribute pumping_speed : Real = 5;  // m^3/s each at operating pressure
            attribute temperature_operating : Real = 20 [K];  // LN2 or colder
            attribute regeneration_cycle : Real = 86400;  // s (24 hours)
        }

        // Total System Performance
        attribute pumpdown_time_initial : Real = 3600;  // s (1 hour)
        attribute base_pressure_achievable : Real = 1.0e-4;  // Pa

        // Constraint: total pumping speed equals sum of all pumps
        constraint PumpingSpeedConsistency {
            doc /* Total pumping speed should match sum of pump capacities */
            pumping_speed_total == n_pumps * pump_capacity_each
        }

        // Vacuum pump power calculation (mechanical pumps)
        calc pump_load : VacuumPumpPower {
            in pumping_speed_total_in = pumping_speed_total;
            in base_pressure = base_pressure_achievable;
            in pump_count = n_pumps;
            // pump_efficiency defaults to 0.4
        }

        // Cryopump refrigeration power calculation
        calc cryo_load : CryoPumpRefrigeration {
            in cryo_pump_count = cryo_pumps.n_pumps;
            in pump_capacity = cryo_pumps.pumping_speed;
            // operating_temp defaults to 20.0 K (matches cryo_pumps.temperature_operating)
            // carnot_efficiency defaults to 0.3
            // load_factor defaults to 0.001
        }

        attribute pump_power : Real = pump_load.pump_power;  // EXPOSE for physics.sysml
        attribute cryo_power : Real = cryo_load.refrigeration_power;  // EXPOSE for physics.sysml
    }

    /*
     * Vacuum System Spool and Door Configuration
     */
    part catf_vacuum_access {
        doc /*
        Vacuum vessel access ports, spools, and doors for maintenance.

        **Source**: PyFECONS DefineInputs.py lines 243-249
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py

        **Components**:
        - Vacuum spools: Large cylindrical sections for access
        - Vacuum doors: Sealable ports for maintenance
        - Diagnostic ports: Smaller penetrations

        **Design Requirements**:
        - Must maintain vacuum seal during operation
        - Must provide adequate access for maintenance
        - Must support remote handling for activated components

        **Last Updated**: 2025-11-01
        */

        // Spool Geometry (from PyFECONS lines 243-245)
        part vacuum_spool {
            doc /* Large vacuum spool pieces for assembly */
            attribute inner_radius : Real = 2.25 [m];  // Line 243
            attribute outer_radius : Real = 3.15 [m];  // Line 244
            attribute height : Real = 9.0 [m];         // Line 249
            attribute wall_thickness : Real = 0.9 [m]; // outer - inner
        }

        // Door Configuration (from PyFECONS lines 245-248)
        part vacuum_door_bottom {
            doc /* Bottom vacuum door */
            attribute inner_radius : Real = 6.0 [m];   // Line 245
            attribute outer_radius : Real = 6.25 [m];  // Line 246
            attribute thickness : Real = 0.25 [m];
        }

        part vacuum_door_center {
            doc /* Center/main vacuum door */
            attribute inner_radius : Real = 7.81 [m];  // Line 247
            attribute outer_radius : Real = 8.06 [m];  // Line 248
            attribute thickness : Real = 0.25 [m];
        }

        // Port Count
        attribute n_diagnostic_ports : Real = 12;
        attribute n_heating_ports : Real = 4;
        attribute n_pumping_ports : Real = 4;
        attribute n_maintenance_ports : Real = 2;
    }
}
