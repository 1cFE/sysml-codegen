/**
 * Plasma Confinement Physics - Phase 2 Extension Interfaces
 * - Implementation Package
 *
 * [PHASE 2 INTERFACES - NOT IMPLEMENTED IN PHASE 1]
 *
 * This file defines interfaces for future implementation of plasma confinement
 * scaling laws (ITER98y2). In Phase 1, fusion power is a direct input. In Phase 2,
 * fusion power will be calculated from plasma parameters using empirical scaling laws.
 *
 * The interfaces are designed now to ensure future compatibility without breaking
 * changes to existing models.
 *
 * **Package Naming**: This package uses a unique name (FusionPhysics_Confinement)
 * to avoid namespace collisions. Multiple files cannot declare the same package name
 * in SysML v2, as each creates a distinct package element with its own UUID. The
 * underscore naming convention clearly distinguishes implementation packages from
 * the public API package (FusionPhysics).
 *
 * **Qualified Name** (implementation package - direct access):
 *   - FusionPhysics_Confinement::PlasmaConfinement
 *
 * **Public Access** (via aggregator re-export in fusion_physics.sysml):
 *   - FusionPhysics::PlasmaConfinement (recommended for design files)
 *
 * Created: 2025-11-03
 * Restructured: 2025-11-17 (fix qualified name collision)
 * Sources: ITER Physics Basis (1999), ITER98y2 scaling law
 * Status: INTERFACE ONLY - Implementation in Phase 2
 */
package FusionPhysics_Confinement {
    public import ScalarValues::*;
    public import SI::*;
    public import ISQ::*;

    /**
     * Plasma Confinement Calculation (ITER98y2 Scaling Law)
     *
     * [PHASE 2 - INTERFACE PLACEHOLDER]
     *
     * This calculation will implement the ITER98y2 energy confinement time scaling
     * law to predict plasma performance from machine parameters. In Phase 2, this
     * will replace the direct P_fusion input with a calculation based on:
     * - Plasma current and magnetic field
     * - Machine size (major radius)
     * - Plasma shape (elongation)
     * - Density and auxiliary heating power
     *
     * ITER98y2 Energy Confinement Time Scaling Law:
     *   τ_E = 0.0562 × M^0.19 × I_p^0.93 × R^1.97 × ε^0.58 × κ^0.78 × n_e^0.41 × B_t^0.15 × P_loss^(-0.69)
     *
     * Where:
     * - τ_E: Energy confinement time [s]
     * - M: Average atomic mass [amu] (2.5 for DT)
     * - I_p: Plasma current [MA]
     * - R: Major radius [m]
     * - ε: Inverse aspect ratio (a/R) [dimensionless]
     * - κ: Plasma elongation [dimensionless]
     * - n_e: Line-averaged electron density [10^19 m^-3]
     * - B_t: Toroidal magnetic field on axis [T]
     * - P_loss: Loss power to plasma = P_fusion - P_alpha + P_aux [MW]
     *
     * Validity Range:
     * - Aspect ratio: A = R/a = 2.5 - 5.0
     * - Plasma current: I_p = 0.8 - 24 MA
     * - Toroidal field: B_t = 1.0 - 6.0 T
     * - Major radius: R = 0.9 - 8.0 m
     *
     * CATF MFE Concern:
     * - CATF has A ≈ 2.5 (borderline compact tokamak)
     * - At lower bound of validity range
     * - May need degradation factor or alternative scaling
     * - Compact tokamaks historically show reduced confinement
     *
     * From τ_E, calculate fusion power using:
     * - Triple product: n × T × τ_E (Lawson criterion)
     * - Fusion reactivity: <σv>(T) for DT fuel
     * - Plasma volume and profile factors
     *
     * Phase 1 Behavior (Current):
     *   P_fusion = P_fusion_input (direct passthrough)
     *
     * Phase 2 Behavior (Future):
     *   1. Calculate τ_E from ITER98y2 scaling
     *   2. Calculate aspect ratio A = R/a
     *   3. Calculate plasma volume from R, a, κ
     *   4. Calculate fusion power from n, T, τ_E, <σv>, volume
     *   5. P_fusion = calculated value (not input)
     *
     * Interface Design:
     * - Phase 1: All Phase 2 inputs present but not used
     * - Phase 1: P_fusion comes from p_fusion_input (direct)
     * - Phase 2: P_fusion calculated from plasma parameters
     * - No breaking changes when switching from Phase 1 to Phase 2
     *
     * Source: ITER Physics Basis (1999), Nuclear Fusion 39(12), Equation 7
     * Reference: Web research on ITER98y2 scaling law (2025)
     *            ITER confinement database analysis
     * Validity: A = 2.5-5.0, I_p = 0.8-24 MA
     * Concerns: CATF aspect ratio A ≈ 2.5 at lower bound
     * Status: INTERFACE ONLY - Implementation in Phase 2
     * Last Updated: 2025-11-03
     */
    calc def PlasmaConfinement {
        // Phase 1: Direct fusion power input (current behavior)
        in attribute p_fusion_input : Real;  // MW - Direct fusion power input (Phase 1 only)

        // Phase 2: Plasma parameters for ITER98y2 calculation (future)
        in attribute i_plasma : Real;  // MA - Plasma current (Phase 2)
        in attribute b_toroidal : Real;  // T - Toroidal magnetic field on axis (Phase 2)
        in attribute r_major : Real;  // m - Major radius (Phase 2)
        in attribute elongation : Real;  // Dimensionless - Plasma elongation κ (Phase 2)
        in attribute n_electron : Real;  // 10^19 m^-3 - Line-averaged electron density (Phase 2)
        in attribute p_auxiliary : Real;  // MW - Auxiliary heating power (Phase 2)
        in attribute atomic_mass : Real;  // amu - Average atomic mass (2.5 for DT) (Phase 2)

        // Phase 2: Intermediate calculations (not used in Phase 1)
        out attribute tau_energy : Real;  // s - Energy confinement time (Phase 2 output)
        out attribute aspect_ratio : Real;  // Dimensionless - A = R/a (Phase 2 output)

        // Final output: P_fusion
        // Phase 1: Returns p_fusion_input directly (passthrough)
        // Phase 2: Returns calculated fusion power from ITER98y2 + triple product
        out attribute p_fusion : Real = p_fusion_input;  // MW - Phase 1: input, Phase 2: calculated

        // Phase 1 constraint: Input must be positive
        constraint Phase1PositivePower {
            doc /* Phase 1: Fusion power input must be positive */
            p_fusion_input > 0
        }

        // Phase 2 constraint placeholder (not enforced in Phase 1)
        constraint Phase2PlasmaParametersPhysical {
            doc /* Phase 2: Will validate plasma parameters are physical */
            true  // Placeholder - implement in Phase 2
        }
    }
} // package FusionPhysics_Confinement
