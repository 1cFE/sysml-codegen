/**
 * Neutronics and Tritium Breeding - Phase 2 Extension Interfaces
 * - Implementation Package
 *
 * [PHASE 2 INTERFACES - NOT IMPLEMENTED IN PHASE 1]
 *
 * This file defines interfaces for future implementation of explicit tritium
 * breeding ratio (TBR) calculations. In Phase 1, TBR is assumed = 1.0 (breed-to-burn,
 * implicit in PyFECONS). In Phase 2, TBR will be calculated from blanket geometry,
 * materials, and Li-6 enrichment.
 *
 * The interfaces are designed now to ensure future compatibility without breaking
 * changes to existing models.
 *
 * **Package Naming**: This package uses a unique name (FusionPhysics_Neutronics)
 * to avoid namespace collisions. Multiple files cannot declare the same package name
 * in SysML v2, as each creates a distinct package element with its own UUID. The
 * underscore naming convention clearly distinguishes implementation packages from
 * the public API package (FusionPhysics).
 *
 * **Qualified Name** (implementation package - direct access):
 *   - FusionPhysics_Neutronics::TritiumBreedingRatio
 *
 * **Public Access** (via aggregator re-export in fusion_physics.sysml):
 *   - FusionPhysics::TritiumBreedingRatio (recommended for design files)
 *
 * Created: 2025-11-03
 * Restructured: 2025-11-17 (fix qualified name collision)
 * Sources: Web research on tritium breeding (2024-2025), DEMO blanket studies
 * Status: INTERFACE ONLY - Implementation in Phase 2
 */
package FusionPhysics_Neutronics {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Tritium Breeding Ratio Calculation
     *
     * [PHASE 2 - INTERFACE PLACEHOLDER]
     *
     * This calculation will implement a simplified 1D neutronics model to estimate
     * tritium breeding ratio from blanket design parameters. TBR is critical for
     * fusion reactor fuel self-sufficiency - must be ≥ 1.05 to account for:
     * - Tritium decay (12.3 year half-life)
     * - Processing losses
     * - Startup inventory requirements
     * - Operational margin
     *
     * Tritium Breeding Reactions:
     *   Li-6 + n → T + He-4 + 4.8 MeV  (primary, all neutron energies)
     *   Li-7 + n → T + He-4 + n - 2.5 MeV  (secondary, threshold E_n > 2.5 MeV)
     *
     * Simplified 1D Beer-Lambert Neutronics Model:
     *   Φ(x) = Φ_0 × exp(-Σ_t × x)
     *
     * Where:
     * - Φ(x): Neutron flux at depth x [neutrons/cm²/s]
     * - Φ_0: Neutron flux at first wall
     * - Σ_t: Macroscopic total cross section [cm^-1]
     * - x: Depth into blanket [cm]
     *
     * TBR Calculation Steps (Phase 2):
     * 1. Calculate neutron flux profile through blanket
     * 2. Account for neutron multiplication (beryllium, lead)
     * 3. Calculate Li-6 breeding rate (fast + thermal neutrons)
     * 4. Calculate Li-7 breeding rate (fast neutrons only, threshold reaction)
     * 5. Apply geometric coverage factor (ports, penetrations reduce effective area)
     * 6. TBR = (T atoms produced) / (fusion neutron)
     *
     * Target TBR: ≥ 1.05 for self-sufficiency with margin
     * Typical Modern Designs: 1.12 - 1.15 with optimization
     *
     * Key Parameters:
     * - Blanket thickness: 40-80 cm typical
     * - Li-6 enrichment: 30-90% (natural = 7.5%, higher = better TBR)
     * - Breeder material: Li, Li2O, Li4SiO4, LiPb eutectic, FLiBe
     * - Neutron multiplier: Beryllium (increases TBR by 10-20%)
     * - Blanket coverage: 70-85% (geometric, reduced by ports)
     *
     * Phase 1 Behavior (Current):
     *   TBR = tbr_assumed (typically 1.0, breed-to-burn assumption)
     *
     * Phase 2 Behavior (Future):
     *   1. Calculate neutron flux profile in blanket
     *   2. Calculate breeding from Li-6 and Li-7 reactions
     *   3. Apply neutron multiplication factor
     *   4. Apply geometric coverage factor
     *   5. TBR = calculated value (not input)
     *
     * Simplified 1D Model Accuracy:
     * - ±10-20% compared to full 3D Monte Carlo (MCNP, Serpent)
     * - Sufficient for early design screening
     * - Phase 3: Integrate with full Monte Carlo for final design
     *
     * Interface Design:
     * - Phase 1: All Phase 2 inputs present but not used
     * - Phase 1: TBR comes from tbr_assumed (direct)
     * - Phase 2: TBR calculated from blanket parameters
     * - No breaking changes when switching from Phase 1 to Phase 2
     *
     * Source: Web research on tritium breeding (2024-2025)
     * Reference: DEMO blanket studies (HCPB, WCLL concepts)
     *            Li-6/Li-7 nuclear data (ENDF/B-VIII)
     *            Beryllium neutron multiplication
     * Target: TBR ≥ 1.05 (self-sufficient with margin)
     * Typical: TBR = 1.12-1.15 with optimization
     * Status: INTERFACE ONLY - Implementation in Phase 2
     * Last Updated: 2025-11-03
     */
    calc def TritiumBreedingRatio {
        // Phase 1: Assumed TBR (current behavior)
        in attribute tbr_assumed : Real;  // Dimensionless - Assumed TBR (Phase 1, typically 1.0)

        // Phase 2: Blanket design parameters for TBR calculation (future)
        in attribute blanket_thickness : Real;  // m - Radial blanket thickness (Phase 2)
        in attribute li6_enrichment : Real;  // Fraction - Li-6 enrichment 0.3-0.9 (Phase 2)
        in attribute breeder_material : String;  // Material type: Li, LiPb, Li2O, etc (Phase 2)
        in attribute neutron_multiplier : Real;  // Dimensionless - Energy multiplication M = 1.1-1.3 (Phase 2)
        in attribute blanket_coverage : Real;  // Fraction - Geometric coverage 0.7-0.85 (Phase 2)

        // Phase 2: Intermediate neutronics calculations (not used in Phase 1)
        out attribute neutron_flux_profile : Real;  // Neutrons/cm²/s - Flux at first wall (Phase 2)
        out attribute breeding_rate : Real;  // T atoms/fusion neutron - Breeding rate (Phase 2)

        // Final output: TBR
        // Phase 1: Returns tbr_assumed directly (passthrough)
        // Phase 2: Returns calculated TBR from 1D neutronics model
        out attribute tbr : Real = tbr_assumed;  // Dimensionless - Phase 1: assumed, Phase 2: calculated

        // Phase 1 constraint: Assumed TBR should be reasonable
        constraint Phase1ReasonableTBR {
            doc /* Phase 1: Assumed TBR typically 0.9-1.3 */
            tbr_assumed > 0.9 and tbr_assumed < 1.3
        }

    }
} // package FusionPhysics_Neutronics
