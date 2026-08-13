/**
 * Power Balance Physics Models
 * - Implementation Package
 *
 * Core energy flow calculations for fusion reactors: fusion power splitting into
 * alpha and neutron components, blanket thermal power with neutron multiplication,
 * gross electric power from thermal conversion, and net electric power after
 * parasitic loads.
 *
 * These calculations implement the PyFECONS power balance methodology exactly.
 *
 * **Package Naming**: This package uses a unique name (FusionPhysics_PowerBalance)
 * to avoid namespace collisions. Multiple files cannot declare the same package name
 * in SysML v2, as each creates a distinct package element with its own UUID. The
 * underscore naming convention clearly distinguishes implementation packages from
 * the public API package (FusionPhysics).
 *
 * **Qualified Names** (implementation package - direct access):
 *   - FusionPhysics_PowerBalance::AlphaNeutronSplit
 *   - FusionPhysics_PowerBalance::BlanketThermalPower
 *   - FusionPhysics_PowerBalance::GrossElectricPower
 *   - FusionPhysics_PowerBalance::NetElectricPower
 *
 * **Public Access** (via aggregator re-export in fusion_physics.sysml):
 *   - FusionPhysics::AlphaNeutronSplit (recommended for design files)
 *   - FusionPhysics::BlanketThermalPower
 *   - FusionPhysics::GrossElectricPower
 *   - FusionPhysics::NetElectricPower
 *
 * Created: 2025-11-03
 * Restructured: 2025-11-17 (fix qualified name collision)
 * Sources: PyFECONS PowerBalance.py, Nuclear fusion physics
 */
package FusionPhysics_PowerBalance {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Alpha-Neutron Power Split from DT Fusion
     *
     * In deuterium-tritium fusion, each reaction releases 17.58 MeV total energy:
     * - Alpha particle (He-4): 3.52 MeV (20.0%)
     * - Neutron: 14.06 MeV (80.0%)
     *
     * The alpha particle is charged and deposits energy in the plasma (self-heating),
     * while the neutron is neutral and deposits energy in the blanket/first wall.
     *
     * Formula:
     *   P_alpha = P_fusion × (3.52 / 17.58) = P_fusion × 0.200227
     *   P_neutron = P_fusion × (14.06 / 17.58) = P_fusion × 0.799773
     *
     * Source: Nuclear reaction kinematics (D + T → He-4 + n)
     * Reference: PyFECONS PowerBalance.py lines 94-105
     *            https://en.wikipedia.org/wiki/Deuterium-tritium_fusion
     * Assumptions:
     *   - 50-50 D-T fuel mix
     *   - Complete fusion reaction (no partially burned fuel)
     *   - Standard DT reaction energetics
     * Last Updated: 2025-11-03
     */
    calc def AlphaNeutronSplit {
        in attribute p_fusion : Real;  // MW - Total fusion power

        out attribute p_alpha : Real = p_fusion * 3.52 / 17.58;  // MW - Alpha particle power (20%)
        // Relation (undirected): p_alpha + p_neutron = p_fusion. The DT branching ratios
        // 3.52/17.58 and 14.06/17.58 sum to exactly 1, so this holds by construction.
        // Direction is a CHOSEN BASIS, not physics: p_alpha is taken as the free branch and
        // p_neutron derived as the remainder. The reverse basis is equally valid.
        // Authority: owner-disposition.md Group C, C37 (derive-instead); pairs with A1.
        out attribute p_neutron : Real = p_fusion - p_alpha;  // MW - Neutron power (80%)

        constraint PositivePower {
            doc /* Fusion power must be positive */
            p_fusion > 0
        }
    }

    /**
     * Blanket Thermal Power with Neutron Multiplication
     *
     * Calculates total thermal power deposited in the blanket from:
     * 1. Neutron energy deposition with breeding multiplication (M_n × P_neutron)
     * 2. Auxiliary input power thermalized (P_input)
     * 3. Recovered waste heat from pumping and subsystems
     *
     * Neutron multiplication (M_n = 1.1-1.3) comes from:
     * - Tritium breeding reactions (Li-6 + n → T + α + 4.8 MeV)
     * - Beryllium neutron multiplication (Be-9 + n → 2n + ...)
     * - Additional exothermic nuclear reactions in blanket materials
     *
     * Waste heat recovery accounts for:
     * - Coolant pumping inefficiency (f_pump × η_pump)
     * - Subsystem waste heat (f_subsystem)
     * Both scale with thermal power available for conversion
     *
     * Formula:
     *   P_thermal = (M_n × P_neutron) + P_input +
     *               η_thermal × (f_pump × η_pump + f_subsystem) × (M_n × P_neutron)
     *
     * Source: PyFECONS PowerBalance.py lines 15-21
     * Reference: DEMO blanket studies, ITER blanket design documentation
     * Typical Values:
     *   M_n = 1.1-1.3 (neutron energy multiplication)
     *   f_pump = 0.06 (6% pumping power fraction)
     *   η_pump = 0.5 (50% pumping efficiency)
     *   f_subsystem = 0.03 (3% subsystem power fraction)
     * Assumptions:
     *   - Uniform blanket energy deposition
     *   - All auxiliary power thermalizes in blanket
     *   - Pump and subsystem waste heat is recoverable
     * Last Updated: 2025-11-03
     */
    calc def BlanketThermalPower {
        in attribute p_neutron : Real;  // MW - Neutron power from fusion
        in attribute p_input : Real;  // MW - Auxiliary heating power
        in attribute m_neutron : Real;  // Dimensionless - Neutron energy multiplication (1.1-1.3)
        in attribute eta_thermal : Real;  // Dimensionless - Thermal conversion efficiency (0.35-0.47)
        in attribute f_pump : Real;  // Dimensionless - Pumping power fraction (typically 0.06)
        in attribute eta_pump : Real;  // Dimensionless - Pumping efficiency (typically 0.5)
        in attribute f_subsystem : Real;  // Dimensionless - Subsystem power fraction (typically 0.03)

        out attribute p_thermal : Real =
            (m_neutron * p_neutron) + p_input +
            eta_thermal * (f_pump * eta_pump + f_subsystem) * (m_neutron * p_neutron);
            // MW - Total thermal power in blanket

        constraint PositiveInputs {
            doc /* Neutron and input power must be positive */
            p_neutron > 0 and p_input >= 0
        }

        constraint ReasonableMultiplication {
            doc /* Neutron multiplication should be physical (1.0 to 1.5) */
            m_neutron >= 1.0 and m_neutron <= 1.5
        }

        constraint ReasonableEfficiencies {
            doc /* All efficiency parameters must be between 0 and 1 */
            eta_thermal > 0 and eta_thermal <= 1.0 and
            f_pump >= 0 and f_pump <= 1.0 and
            eta_pump > 0 and eta_pump <= 1.0 and
            f_subsystem >= 0 and f_subsystem <= 1.0
        }
    }

    /**
     * Gross Electric Power from Thermal and Direct Conversion
     *
     * Converts thermal energy to electricity through two parallel paths:
     * 1. Thermal conversion (blanket → steam/gas → turbine → electricity)
     * 2. Direct conversion (alpha particles → electricity, experimental)
     *
     * Thermal Conversion (η_thermal = 0.35-0.47):
     * - Limited by Carnot efficiency: η_carnot = 1 - T_cold/T_hot
     * - Material temperature limits (blanket outlet ~550-750°C)
     * - Real cycle losses reduce Carnot efficiency by 10-20%
     * - Water/steam Rankine: 35-41%
     * - Helium Brayton: 38-42%
     * - Supercritical CO2: 43-47%
     *
     * Direct Conversion (η_direct = 0.0 or 0.5-0.85):
     * - Phase 1 baseline: η_direct = 0.0 (all alpha thermalizes)
     * - Future: Magnetic expansion or traveling wave direct converter
     * - Experimental technology, not mature
     *
     * Formula:
     *   P_electric_gross = η_thermal × P_thermal + η_direct × P_alpha
     *
     * Source: PyFECONS PowerBalance.py lines 22-27
     * Reference: Rankine/Brayton cycle thermodynamics
     *            DEMO power conversion system design
     *            Direct conversion experimental results
     * Typical Values:
     *   η_thermal = 0.35-0.47 (thermal cycle efficiency)
     *   η_direct = 0.0 (Phase 1) or 0.5-0.85 (future)
     * Assumptions:
     *   - Phase 1: All alpha energy thermalizes (η_direct = 0)
     *   - Material temperature limits constrain thermal cycle
     *   - Thermal efficiency ≈ 0.8-0.9 × Carnot efficiency
     * Last Updated: 2025-11-03
     */
    calc def GrossElectricPower {
        in attribute p_thermal : Real;  // MW - Total thermal power
        in attribute p_alpha : Real;  // MW - Alpha particle power
        in attribute eta_thermal : Real;  // Dimensionless - Thermal conversion efficiency (0.35-0.47)
        in attribute eta_direct : Real;  // Dimensionless - Direct conversion efficiency (0.0 or 0.5-0.85)

        out attribute p_electric_gross : Real = eta_thermal * p_thermal + eta_direct * p_alpha;  // MW - Gross electric power

        constraint PositivePowers {
            doc /* Thermal power must be positive, alpha non-negative */
            p_thermal > 0 and p_alpha >= 0
        }

        constraint ThermalEfficiencyPhysical {
            doc /* Thermal efficiency must be positive and less than Carnot limit (~0.5) */
            eta_thermal > 0 and eta_thermal < 0.5
        }

        constraint DirectConversionRange {
            doc /* Direct conversion efficiency between 0 (none) and 0.9 (optimistic) */
            eta_direct >= 0 and eta_direct <= 0.9
        }
    }

    /**
     * Net Electric Power after Parasitic Loads
     *
     * Subtracts all auxiliary power consumption from gross electric output to
     * calculate net power delivered to the grid. Parasitic loads include:
     *
     * 1. P_coils: Magnet system power (superconducting coil cryogenics, resistive losses)
     * 2. P_heating: Plasma heating systems (NBI, ECRH, ICRH - wall-plug power)
     * 3. P_pumps: Coolant circulation pumps (primary, secondary loops)
     * 4. P_cryo: Cryogenic refrigeration (magnet cooling, fuel systems)
     * 5. P_vacuum: Vacuum pumping (torus, divertor, roughing pumps)
     * 6. P_tritium: Tritium processing and fuel cycle (separation, purification)
     * 7. P_auxiliary: Other auxiliary systems (control, diagnostics, building services)
     *
     * Typical parasitic power fraction: 10-30% of gross electric
     * - Q_eng = 1.1: ~91% parasitics (CATF minimum viable)
     * - Q_eng = 1.5: ~67% parasitics (good)
     * - Q_eng = 5-10: ~10-20% parasitics (excellent)
     *
     * Formula:
     *   P_parasitic_total = P_coils + P_heating + P_pumps + P_cryo + P_vacuum + P_tritium + P_auxiliary
     *   P_net = P_electric_gross - P_parasitic_total
     *
     * Source: PyFECONS PowerBalance.py lines 29-48
     * Reference: ITER auxiliary power estimates
     *            DEMO plant power balance studies
     * Typical Parasitic Fraction: 10-30% of P_gross (Q_eng = 1.1 to 10)
     * Assumptions:
     *   - All parasitics supplied from gross electric output
     *   - Steady-state operation (no transient startup power)
     *   - No external grid power or energy storage
     * Updates:
     *   - 2025-12-08: Exposed p_parasitic_total as output for Q_eng calculation
     *     and power balance validation. See Issue C in research doc:
     *     project/research/20251208-152235_codegen-pipeline-test-failures.md
     * Last Updated: 2025-12-08
     */
    calc def NetElectricPower {
        in attribute p_electric_gross : Real;  // MW - Gross electric power
        in attribute p_coils : Real;  // MW - Magnet system power
        in attribute p_heating : Real;  // MW - Plasma heating power (wall-plug)
        in attribute p_pumps : Real;  // MW - Coolant pumps
        in attribute p_cryo : Real;  // MW - Cryogenic systems
        in attribute p_vacuum : Real;  // MW - Vacuum pumping
        in attribute p_tritium : Real;  // MW - Tritium processing
        in attribute p_auxiliary : Real;  // MW - Other auxiliary systems

        out attribute p_parasitic_total : Real = p_coils + p_heating + p_pumps + p_cryo + p_vacuum + p_tritium + p_auxiliary;  // MW - Total parasitic load (exposed for Q_eng calculation)

        out attribute p_net : Real = p_electric_gross - p_parasitic_total;  // MW - Net electric power to grid

        constraint PositiveGrossElectric {
            doc /* Gross electric power must be positive */
            p_electric_gross > 0
        }

        constraint NonNegativeParasitics {
            doc /* All parasitic loads must be non-negative */
            p_coils >= 0 and p_heating >= 0 and p_pumps >= 0 and
            p_cryo >= 0 and p_vacuum >= 0 and p_tritium >= 0 and
            p_auxiliary >= 0
        }

        constraint ReasonableParasiticFraction {
            doc /* Total parasitics should not exceed gross electric (Q_eng > 1.0) */
            p_parasitic_total < p_electric_gross
        }
    }
} // package FusionPhysics_PowerBalance
