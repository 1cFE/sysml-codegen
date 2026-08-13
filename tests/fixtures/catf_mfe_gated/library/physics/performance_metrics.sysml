/**
 * Performance Metrics for Fusion Reactors
 * - Implementation Package
 *
 * Defines key performance indicators for fusion power plants:
 * - Q_sci (Scientific Q): Plasma physics performance (fusion/input)
 * - Q_eng (Engineering Q): System-level performance (gross/parasitics)
 * - Plant Efficiency: Overall conversion efficiency (net/fusion)
 *
 * These metrics enable comparison between designs and assessment of
 * economic viability.
 *
 * **Package Naming**: This package uses a unique name (FusionPhysics_PerformanceMetrics)
 * to avoid namespace collisions. Multiple files cannot declare the same package name
 * in SysML v2, as each creates a distinct package element with its own UUID. The
 * underscore naming convention clearly distinguishes implementation packages from
 * the public API package (FusionPhysics).
 *
 * **Qualified Names** (implementation package - direct access):
 *   - FusionPhysics_PerformanceMetrics::ScientificQFactor
 *   - FusionPhysics_PerformanceMetrics::EngineeringQFactor
 *   - FusionPhysics_PerformanceMetrics::PlantEfficiency
 *
 * **Public Access** (via aggregator re-export in fusion_physics.sysml):
 *   - FusionPhysics::ScientificQFactor (recommended for design files)
 *   - FusionPhysics::EngineeringQFactor
 *   - FusionPhysics::PlantEfficiency
 *
 * Created: 2025-11-03
 * Restructured: 2025-11-17 (fix qualified name collision)
 * Sources: PyFECONS PowerBalance.py, Fusion energy system engineering
 */
package FusionPhysics_PerformanceMetrics {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Scientific Q Factor (Plasma Physics Performance)
     *
     * Q_sci measures the plasma's ability to produce fusion power relative to
     * the external heating power required to sustain the plasma. It is the
     * fundamental metric of plasma confinement quality.
     *
     * Performance levels:
     * - Q < 1: Sub-ignition (net energy sink in plasma)
     * - Q = 1: Break-even (fusion power equals input)
     * - Q = 5-10: High-gain (good confinement)
     * - Q > 20: Approaching ignition (self-sustaining)
     * - Q = ∞: Ignition (no external heating needed)
     *
     * Formula:
     *   Q_sci = P_fusion / P_input
     *
     * ITER Target: Q_sci = 10
     *   - 500 MW fusion power
     *   - 50 MW heating power
     *   - Demonstrates scientific feasibility of fusion energy
     *
     * CATF MFE Baseline: Q_sci = 52
     *   - 2600 MW fusion power
     *   - 50 MW heating power
     *   - Excellent plasma performance
     *
     * Source: Standard fusion plasma physics definition
     * Reference: PyFECONS PowerBalance.py line 28
     *            ITER Physics Basis (1999)
     * Assumptions:
     *   - Steady-state operation
     *   - All heating power couples to plasma
     *   - No transient startup/shutdown effects
     * Last Updated: 2025-11-03
     */
    calc def ScientificQFactor {
        in attribute p_fusion : Real;  // MW - Fusion power
        in attribute p_input : Real;  // MW - Auxiliary heating power

        out attribute q_sci : Real = p_fusion / p_input;  // Dimensionless - Scientific Q factor

        constraint PositivePowers {
            doc /* Both powers must be positive */
            p_fusion > 0 and p_input > 0
        }

        constraint ReasonableRange {
            doc /* Q should be between 0.01 and 1000 for realistic designs */
            q_sci > 0.01 and q_sci < 1000
        }
    }

    /**
     * Engineering Q Factor (System-Level Performance)
     *
     * Q_eng measures the overall system's ability to produce gross electric power
     * relative to ALL auxiliary power consumption. Unlike Q_sci which only considers
     * plasma heating, Q_eng accounts for:
     * - Plasma heating systems
     * - Magnet cryogenics and power supplies
     * - Coolant pumps
     * - Vacuum systems
     * - Tritium processing
     * - All other auxiliary loads
     *
     * Q_eng determines economic viability - the reactor must produce more electric
     * power than it consumes.
     *
     * Performance levels:
     * - Q_eng < 1.0: Power sink (not viable)
     * - Q_eng = 1.0: Break-even (no net power)
     * - Q_eng = 1.1: Minimum viable (CATF target)
     * - Q_eng = 1.5: Good performance
     * - Q_eng = 5-10: Excellent (commercial target)
     *
     * Recirculating Power Relationship:
     *   f_recirc = 1 / Q_eng  (fraction of gross power consumed internally)
     *   P_net = (1 - 1/Q_eng) × P_gross = (1 - f_recirc) × P_gross
     *
     * Example (CATF target Q_eng = 1.1):
     *   f_recirc = 1/1.1 = 0.909 = 91% recirculated
     *   P_net = (1 - 0.909) × P_gross = 0.091 × P_gross = 9% to grid
     *
     * Formula:
     *   Q_eng = P_electric_gross / P_auxiliary_total
     *
     * Source: PyFECONS PowerBalance.py lines 29-48
     * Reference: Fusion energy system engineering analysis
     *            DEMO plant power balance studies
     * Typical Values:
     *   CATF Target: Q_eng ≥ 1.1
     *   Commercial Target: Q_eng = 1.2-2.0
     * Assumptions:
     *   - All auxiliary power supplied from gross electric
     *   - Steady-state operation
     *   - No external grid power or energy storage
     * Updates:
     *   - 2025-12-08: Exposed f_recirculating as output for economic validation
     *     and reporting. Referenced in CATF design at designs/catf_mfe/physics.sysml:121
     * Last Updated: 2025-12-08
     */
    calc def EngineeringQFactor {
        in attribute p_electric_gross : Real;  // MW - Gross electric power
        in attribute p_auxiliary_total : Real;  // MW - Total auxiliary power (all parasitics)

        out attribute q_eng : Real = p_electric_gross / p_auxiliary_total;  // Dimensionless - Engineering Q factor

        out attribute f_recirculating : Real = 1.0 / q_eng;  // Dimensionless - Recirculating power fraction (exposed for economic validation)

        out attribute p_net : Real = p_electric_gross * (1.0 - f_recirculating);  // MW - Net electric power to grid

        constraint PositivePowers {
            doc /* Both powers must be positive */
            p_electric_gross > 0 and p_auxiliary_total > 0
        }

        constraint ViabilityCheck {
            doc /* Q_eng must exceed 1.0 for viable power plant */
            q_eng > 1.0
        }

        constraint ReasonableRange {
            doc /* Q_eng unlikely to exceed 50 in practical systems */
            q_eng < 50
        }
    }

    /**
     * Plant Efficiency (Overall Energy Conversion)
     *
     * η_plant measures the overall efficiency of converting fusion energy to
     * net electric power delivered to the grid. It accounts for:
     * - Thermal conversion efficiency (Carnot limit, cycle losses)
     * - Direct conversion efficiency (if any)
     * - All parasitic loads and auxiliary power
     *
     * This is the key metric for comparing fusion to other energy sources.
     *
     * Typical Plant Efficiencies:
     * - Fusion without direct conversion: 25-35%
     * - Fusion with direct conversion: 30-40%
     * - Best case fusion: 40-45%
     *
     * Comparison to Other Technologies:
     * - Coal (subcritical): 33-37%
     * - Coal (supercritical): 37-40%
     * - Natural gas combined cycle: 50-60%
     * - Nuclear fission (PWR/BWR): 30-35%
     * - Solar PV: 15-20%
     * - Wind: 35-45% (capacity factor limited)
     *
     * CATF MFE Target: η_plant ≈ 30-35%
     * - Competitive with fission
     * - Lower than gas, but carbon-free baseload
     *
     * Formula:
     *   η_plant = P_net / P_fusion
     *
     * Source: Derived from PyFECONS power balance
     * Reference: Fusion power plant system studies
     *            Energy technology comparison literature
     * Assumptions:
     *   - All fusion energy thermalizes or converts directly
     *   - No energy storage losses
     *   - Steady-state operation
     * Last Updated: 2025-11-03
     */
    calc def PlantEfficiency {
        in attribute p_fusion : Real;  // MW - Fusion power
        in attribute p_net : Real;  // MW - Net electric power to grid

        out attribute eta_plant : Real = p_net / p_fusion;  // Dimensionless - Plant efficiency (0.0-1.0)

        constraint PositivePowers {
            doc /* Both powers must be positive */
            p_fusion > 0 and p_net > 0
        }

        constraint EfficiencyPhysical {
            doc /* Efficiency must be between 0 and 1 */
            eta_plant > 0 and eta_plant < 1.0
        }

        constraint ReasonableEfficiency {
            doc /* Plant efficiency typically 15-50% for real systems */
            eta_plant > 0.15 and eta_plant < 0.50
        }
    }
} // package FusionPhysics_PerformanceMetrics
