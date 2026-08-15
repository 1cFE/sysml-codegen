package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for magnet systems, blanket, shield, etc.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Toroidal Field Coil' {
        doc /*
        Toroidal field coil system for magnetic plasma confinement.

        Provides the primary toroidal magnetic field for plasma confinement in
        tokamak and spherical tokamak configurations. The TF coils create the
        dominant component of the confining magnetic field.

        **Source**: General tokamak/ST design principles
        **Reference**: ITER magnets design, Commonwealth Fusion SPARC, PyFECONS DefineInputs.py lines 96-109
        **Used For**: Primary magnetic confinement field generation
        **Assumptions**:
        - Axisymmetric configuration (coils equally spaced toroidally)
        - Bulk properties represented (not modeling individual conductor turns)
        - D-shaped or circular cross-section depending on configuration
        **Validation**: Compare geometry and field values with PyFECONS TF coil specifications
        **Last Updated**: 2025-11-01
        */

        // Geometric attributes
        attribute n_coils : Integer {
            doc /* Number of discrete TF coils around torus (typically 12-18) */
        }

        attribute r_centre : Real {
            doc /* Major radius to coil geometric center (for ST: inner leg radius) */
        }

        attribute z_centre : Real {
            doc /* Vertical position of coil center from midplane */
        }

        attribute thickness_radial : Real {
            doc /* Coil radial thickness (dr) - conductor plus structure */
        }

        attribute thickness_vertical : Real {
            doc /* Coil vertical thickness (dz) - conductor plus structure */
        }

        // Magnetic properties
        attribute field_on_axis : Real {
            doc /* Magnetic field strength at plasma geometric axis */
        }

        attribute field_at_coil : Real {
            doc /* Peak magnetic field at conductor (critical for superconductor performance) */
        }

        // Electrical properties
        attribute current_total : Real {
            doc /* Total current in TF coil system */
        }

        attribute temperature_operating : Real {
            doc /* Operating temperature (4K for LTS, 20K for HTS, 300K for resistive) */
        }

        // Material specifications
        attribute material_conductor : String {
            doc /* Superconductor or conductor type (HTS_CICC, LTS_Nb3Sn, Copper, etc.) */
        }

        attribute material_structure : String {
            doc /* Structural case material (typically SS316 or high-strength alloy) */
        }

        attribute fraction_insulation : Real {
            doc /* Volume fraction occupied by electrical insulation (0.0-0.3 typical) */
        }

        // Manufacturing
        attribute manufacturing_factor : Real {
            doc /* Manufacturing complexity multiplier for cost (1.0 = material cost only, 5.0 = high complexity) */
        }

        // Volumes (typically calculated from geometry)
        attribute volume_conductor : Real {
            doc /* Total volume of conductor material */
        }

        attribute volume_structure : Real {
            doc /* Total volume of structural material */
        }
    }

    part def 'Poloidal Field Coil' {
        doc /*
        Poloidal field coil for plasma shaping and position control.

        PF coils generate poloidal magnetic fields for plasma shaping (creating
        elongation and triangularity), vertical position control, and plasma
        current drive assistance. Multiple PF coils arranged at different radial
        and vertical positions provide the required field distribution.

        **Source**: General tokamak control system design
        **Reference**: ITER PF system, PyFECONS DefineInputs.py lines 123-232
        **Used For**: Plasma shaping, position control, scenario control
        **Assumptions**:
        - Circular or rectangular cross-section
        - May be single coil or symmetric pair (above/below midplane)
        - Independent current control for each coil
        **Validation**: Compare positions and currents with PyFECONS PF specifications
        **Last Updated**: 2025-11-01
        */

        // Identification
        attribute name : String {
            doc /* Coil identifier (e.g., "PF1", "PF2", ..., "PF8") */
        }

        // Geometric attributes
        attribute coil_count : Integer {
            doc /* Number of physical coils: 1 for single, 2 for symmetric pair */
        }

        attribute r_centre : Real {
            doc /* Radial position of coil center from machine axis */
        }

        attribute z_centre : Real {
            doc /* Vertical position from midplane (positive = above, negative = below) */
        }

        attribute thickness_radial : Real {
            doc /* Coil cross-section radial dimension */
        }

        attribute thickness_vertical : Real {
            doc /* Coil cross-section vertical dimension */
        }

        // Electrical properties
        attribute current : Real {
            doc /* Operating current (may vary during pulse for control) */
        }

        attribute temperature_operating : Real {
            doc /* Operating temperature (depends on conductor type) */
        }

        // Material specifications
        attribute material_conductor : String {
            doc /* Conductor type (Copper, HTS_CICC, HTS_PANCAKE, etc.) */
        }

        attribute material_structure : String {
            doc /* Structural case material */
        }

        attribute fraction_insulation : Real {
            doc /* Volume fraction for electrical insulation */
        }

        // Manufacturing
        attribute manufacturing_factor : Real {
            doc /* Manufacturing complexity multiplier */
        }

        // Volumes
        attribute volume_conductor : Real {
            doc /* Volume of conductor per coil */
        }

        attribute volume_structure : Real {
            doc /* Volume of structure per coil */
        }
    }

    part def 'Central Solenoid Coil' {
        doc /*
        Central solenoid coil for inductive plasma current drive.

        The CS provides the changing magnetic flux that inductively drives the
        plasma current in a tokamak. Located at the center of the machine, it
        undergoes flux swing cycles to maintain plasma current during pulses.

        **Source**: Tokamak plasma initiation and current drive principles
        **Reference**: ITER CS design, PyFECONS DefineInputs.py lines 110-122
        **Used For**: Inductive plasma current drive, plasma initiation
        **Assumptions**:
        - Cylindrical geometry (solenoid)
        - Modeled as single component (may be multiple modules in practice)
        - Flux swing capability determines pulse length
        **Validation**: Compare flux swing and geometry with PyFECONS CS specifications
        **Last Updated**: 2025-11-01
        */

        // Geometric attributes (cylindrical)
        attribute inner_radius : Real {
            doc /* Inner radius of CS winding (limited by bore access requirements) */
        }

        attribute outer_radius : Real {
            doc /* Outer radius of CS winding */
        }

        attribute height : Real {
            doc /* Vertical height of CS winding */
        }

        attribute z_centre : Real {
            doc /* Vertical position of CS center from midplane (typically 0) */
        }

        // Electromagnetic properties
        attribute flux_swing : Real {
            doc /* Available flux swing for plasma current drive [Wb] */
        }

        attribute field_max : Real {
            doc /* Maximum magnetic field during flux swing (critical for conductor) */
        }

        attribute current_max : Real {
            doc /* Maximum operating current */
        }

        // Material specifications
        attribute material_conductor : String {
            doc /* Superconductor type (typically HTS or LTS for high field capability) */
        }

        attribute material_structure : String {
            doc /* Structural support material */
        }

        attribute temperature_operating : Real {
            doc /* Operating temperature */
        }

        // Manufacturing
        attribute manufacturing_factor : Real {
            doc /* Manufacturing complexity multiplier */
        }

        // Volumes
        attribute volume_conductor : Real {
            doc /* Total conductor volume */
        }

        attribute volume_structure : Real {
            doc /* Total structural volume */
        }
    }
}
