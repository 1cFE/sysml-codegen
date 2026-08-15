/**
 * Fusion Physics Calculation Library - Aggregator Package
 *
 * **Architecture Pattern: Aggregator with Public Re-Export**
 *
 * This package provides a unified namespace (FusionPhysics) for all fusion physics
 * calculations by re-exporting calc defs from multiple implementation packages.
 *
 * **Problem Solved:**
 * Previously, 5 files all declared "package FusionPhysics", creating namespace
 * collisions where only the first package had a valid qualifiedName per SysML v2
 * specification. This broke type resolution and caused validation tools to report
 * all calc defs as unused (false positives).
 *
 * **Solution:**
 * - Implementation packages use unique names (FusionPhysics_PowerBalance, etc.)
 * - Each implementation package contains specific calc defs
 * - This aggregator package re-exports all calc defs using public imports
 * - Design files import from FusionPhysics (backward compatible)
 * - Type resolution now works correctly (qualified names are unique)
 *
 * **Structure - Five Sub-Domains:**
 *
 * 1. **Power Balance** (FusionPhysics_PowerBalance):
 *    - AlphaNeutronSplit: Fusion power splitting into alpha and neutron components
 *    - BlanketThermalPower: Thermal power with neutron multiplication
 *    - GrossElectricPower: Thermal-to-electric conversion
 *    - NetElectricPower: Net power after parasitic loads
 *
 * 2. **Performance Metrics** (FusionPhysics_PerformanceMetrics):
 *    - ScientificQFactor: Plasma physics performance (Q_sci)
 *    - EngineeringQFactor: System-level performance (Q_eng)
 *    - PlantEfficiency: Overall energy conversion efficiency
 *
 * 3. **Confinement Physics** (FusionPhysics_Confinement):
 *    - PlasmaConfinement: ITER98y2 scaling law (Phase 2 interface)
 *
 * 4. **Neutronics** (FusionPhysics_Neutronics):
 *    - TritiumBreedingRatio: TBR calculation (Phase 2 interface)
 *
 * 5. **Thermal Conversion** (FusionPhysics_Thermal):
 *    - ThermalCycleEfficiency: Carnot efficiency with real cycle losses
 *
 * **Import Patterns for Design Files:**
 *
 * Design files use standard imports (backward compatible):
 * ```sysml
 * private import FusionPhysics::ScientificQFactor;
 * private import FusionPhysics::AlphaNeutronSplit;
 * ```
 *
 * These resolve through public re-exports in this aggregator package.
 *
 * **Qualified Name Mapping:**
 *
 * Implementation package (direct access):
 *   - FusionPhysics_PowerBalance::AlphaNeutronSplit
 *   - FusionPhysics_PerformanceMetrics::ScientificQFactor
 *
 * Public access (via aggregator - recommended for design files):
 *   - FusionPhysics::AlphaNeutronSplit (re-exported)
 *   - FusionPhysics::ScientificQFactor (re-exported)
 *
 * Created: 2025-11-17
 * Purpose: Fix qualified name collisions, provide unified namespace
 * Related: project/active/package-namespace-fix/spec.md
 */
package FusionPhysics {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    // Re-export power balance calculations
    public import FusionPhysics_PowerBalance::AlphaNeutronSplit;
    public import FusionPhysics_PowerBalance::BlanketThermalPower;
    public import FusionPhysics_PowerBalance::GrossElectricPower;
    public import FusionPhysics_PowerBalance::NetElectricPower;

    // Re-export performance metrics
    public import FusionPhysics_PerformanceMetrics::ScientificQFactor;
    public import FusionPhysics_PerformanceMetrics::EngineeringQFactor;
    public import FusionPhysics_PerformanceMetrics::PlantEfficiency;

    // Re-export confinement physics (Phase 2)
    public import FusionPhysics_Confinement::PlasmaConfinement;

    // Re-export neutronics (Phase 2)
    public import FusionPhysics_Neutronics::TritiumBreedingRatio;

    // Re-export thermal analysis
    public import FusionPhysics_Thermal::ThermalCycleEfficiency;
} // package FusionPhysics
