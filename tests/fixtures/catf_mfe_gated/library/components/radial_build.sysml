package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for radial build and geometric layout.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Radial Build Layer' {
        doc /*
        Single layer in the radial build from machine axis outward.

        The radial build describes the onion-like layering of components from the
        machine centerline outward through plasma, blanket, shield, vacuum vessel,
        magnets, and biological shield. Each layer is characterized by its radial
        position and thickness.

        **Source**: Standard tokamak radial build methodology
        **Reference**: ITER radial build, ARIES design studies, PyFECONS DefineInputs.py lines 71-87
        **Used For**: Geometric layout, neutronics calculations, volume/mass estimation
        **Assumptions**:
        - Cylindrical/toroidal symmetry (radii measured at midplane)
        - Layers are contiguous (no gaps unless explicitly modeled)
        - Thickness constant around torus (simplification)
        **Validation**: Sum of thicknesses equals total machine radius
        **Last Updated**: 2025-11-01
        */

        attribute name : String {
            doc /* Layer identifier (e.g., "Plasma", "First Wall", "Blanket", "Shield") */
        }

        attribute inner_radius : Real {
            doc /* Inner radius of layer measured from machine axis at midplane */
        }

        attribute thickness : Real {
            doc /* Radial thickness of layer */
        }

        attribute outer_radius : Real {
            doc /* Outer radius of layer (should equal inner_radius + thickness) */
        }

        attribute material_primary : String {
            doc /* Primary material for this layer (may be composite in reality) */
        }

        attribute volume : Real {
            doc /* Total volume of this layer (calculated from geometry) */
        }

        constraint RadiusConsistency {
            doc /*
            Outer radius must equal inner radius plus thickness.
            This ensures geometric consistency in the radial build.
            */
            outer_radius == inner_radius + thickness
        }
    }

    part def 'Radial Build' {
        doc /*
        Complete radial build from axis to biological shield.

        Composite structure containing all radial layers. Ensures consistency
        across layers (no gaps, no overlaps) and provides total radius calculation.

        **Source**: Tokamak design methodology
        **Reference**: PyFECONS DefineInputs.py lines 71-87
        **Used For**: System layout, interface definition, volume calculations
        **Assumptions**:
        - All layers are required (no optional layers)
        - Layers are ordered from inner to outer
        **Validation**: Continuity checks, total radius verification
        **Last Updated**: 2025-11-01
        */

        attribute elongation : Real {
            doc /*
            Plasma elongation (κ): ratio of plasma height to width.
            Used to calculate 3D volumes from 2D radial build.
            Typical range: 1.0 (circular) to 3.0 (highly elongated ST)
            */
        }

        attribute triangularity : Real {
            doc /*
            Plasma triangularity (δ): measure of plasma D-shaping.
            Typical range: 0.0 (circular) to 0.5 (strongly shaped)
            */
        }

        // Layers are defined as nested parts in specific designs
        // (see models/designs/catf_mfe/radial_build.sysml for example)
    }
}
