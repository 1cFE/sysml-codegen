/**
 * Thermal Conversion Physics for Fusion Reactors
 * - Implementation Package
 *
 * Calculates thermal cycle efficiency based on hot/cold temperatures and
 * real cycle losses. Implements Carnot efficiency limit with practical
 * derating factors for real thermodynamic cycles.
 *
 * **Package Naming**: This package uses a unique name (FusionPhysics_Thermal)
 * to avoid namespace collisions. Multiple files cannot declare the same package name
 * in SysML v2, as each creates a distinct package element with its own UUID. The
 * underscore naming convention clearly distinguishes implementation packages from
 * the public API package (FusionPhysics).
 *
 * **Qualified Name** (implementation package - direct access):
 *   - FusionPhysics_Thermal::ThermalCycleEfficiency
 *
 * **Public Access** (via aggregator re-export in fusion_physics.sysml):
 *   - FusionPhysics::ThermalCycleEfficiency (recommended for design files)
 *
 * Created: 2025-11-03
 * Restructured: 2025-11-17 (fix qualified name collision)
 * Sources: Web research on fusion thermal conversion (2025), Thermodynamics
 */
package FusionPhysics_Thermal {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Thermal Cycle Efficiency Calculation
     *
     * Calculates the thermal-to-electric conversion efficiency for a heat engine
     * operating between hot (blanket outlet) and cold (heat rejection) temperatures.
     *
     * The efficiency is limited by the Carnot efficiency (thermodynamic maximum)
     * and further reduced by real cycle losses (friction, heat transfer, turbine
     * efficiency, etc.).
     *
     * Carnot Efficiency (ideal):
     *   η_carnot = (T_hot - T_cold) / T_hot = 1 - T_cold/T_hot
     *
     * Real Cycle Efficiency:
     *   η_thermal = η_carnot × η_real
     *
     * where η_real = 0.5-0.9 accounts for:
     * - Turbine isentropic efficiency (85-95%)
     * - Pump/compressor losses (80-90%)
     * - Heat exchanger effectiveness (90-98%)
     * - Pressure drops and piping losses
     * - Condenser/radiator losses
     *
     * Typical Fusion Power Plant Thermal Cycles:
     *
     * 1. Water/Steam Rankine Cycle:
     *    - T_hot: 550°C (823 K) - Limited by blanket materials
     *    - T_cold: 30°C (303 K) - Cooling tower/water
     *    - η_carnot: 63%
     *    - η_real: 0.55-0.65
     *    - η_thermal: 35-41%
     *    - Status: Mature, widely used, reliable
     *
     * 2. Helium Brayton Cycle:
     *    - T_hot: 700°C (973 K) - Helium-cooled blanket
     *    - T_cold: 30°C (303 K)
     *    - η_carnot: 69%
     *    - η_real: 0.55-0.60
     *    - η_thermal: 38-42%
     *    - Status: Demonstrated in HTGR, good for fusion
     *
     * 3. Supercritical CO2 Brayton:
     *    - T_hot: 650°C (923 K) - Advanced materials
     *    - T_cold: 30°C (303 K)
     *    - η_carnot: 67%
     *    - η_real: 0.64-0.70
     *    - η_thermal: 43-47%
     *    - Status: Experimental, high potential
     *
     * Temperature Constraints:
     * - T_hot limited by:
     *   - First wall materials (tungsten, reduced activation steels)
     *   - Blanket structural materials (EUROFER, V-alloys)
     *   - Tritium permeation (higher T increases permeation)
     *   - Typically <750°C for near-term materials
     * - T_cold limited by:
     *   - Ambient conditions (air, water temperature)
     *   - Cooling tower approach (5-15°C)
     *   - Typically 20-40°C
     *
     * Formula:
     *   η_carnot = (T_hot - T_cold) / T_hot
     *   η_thermal = η_carnot × η_real
     *
     * Source: Web research on fusion thermal conversion (2024-2025)
     * Reference: DEMO power conversion system studies
     *            Helium cooling for fusion blankets
     *            Supercritical CO2 Brayton cycle research
     * Typical Values:
     *   T_hot: 550-750°C (823-1023 K)
     *   T_cold: 20-40°C (293-313 K)
     *   η_real: 0.5-0.9
     *   η_thermal: 0.35-0.47
     * Constraints:
     *   - T_hot limited by materials (<750°C typically)
     *   - T_cold limited by environment (20-40°C)
     *   - η_real accounts for all real cycle losses
     * Assumptions:
     *   - Steady-state operation
     *   - No transient temperature variations
     *   - Ideal heat rejection (environment acts as infinite sink)
     * Updates:
     *   - 2025-12-08: Exposed eta_carnot as output for thermodynamic validation
     *     and debugging. Enables verification of 2nd law (eta_thermal < eta_carnot)
     * Last Updated: 2025-12-08
     */
    calc def ThermalCycleEfficiency {
        in attribute t_hot : Real;  // K - Hot side temperature (blanket outlet)
        in attribute t_cold : Real;  // K - Cold side temperature (heat rejection)
        in attribute eta_real : Real;  // Dimensionless - Real cycle efficiency factor (0.5-0.9)

        out attribute eta_carnot : Real = (t_hot - t_cold) / t_hot;  // Dimensionless - Carnot efficiency (exposed for thermodynamic validation)

        out attribute eta_thermal : Real = eta_carnot * eta_real;  // Dimensionless - Real thermal efficiency

        constraint TemperaturePhysical {
            doc /* Hot must exceed cold, both above freezing */
            t_hot > t_cold and t_cold > 273.0
        }

        constraint ReasonableTemperatures {
            doc /* Hot: 500-1200K (material limits), Cold: 273-350K (environment) */
            t_hot > 500.0 and t_hot < 1200.0 and
            t_cold > 273.0 and t_cold < 350.0
        }

        constraint RealEfficiencyRange {
            doc /* Real cycle factor typically 0.4-0.95 */
            eta_real > 0.4 and eta_real < 0.95
        }

        constraint ThermalEfficiencyPhysical {
            doc /* Thermal efficiency must be positive, below Carnot, and below 1.0 */
            eta_thermal > 0 and eta_thermal < eta_carnot and eta_thermal < 1.0
        }
    }
} // package FusionPhysics_Thermal
