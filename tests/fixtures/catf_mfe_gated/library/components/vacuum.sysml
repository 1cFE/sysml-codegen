package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for vacuum systems.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Vacuum Vessel' {
        doc /*
        Vacuum vessel containing the plasma and first-wall/blanket assembly.

        The vacuum vessel provides multiple critical functions:
        1. Primary vacuum boundary (maintains ultra-high vacuum for plasma)
        2. Structural support for in-vessel components (blanket, divertor, first wall)
        3. Confinement of tritium and activated materials
        4. Support for disruption-induced electromagnetic loads
        5. Neutron shielding contribution

        **Source**: Vacuum vessel design requirements for fusion reactors
        **Reference**: ITER vacuum vessel design, ARIES vessel studies
        **PyFECONS**: DefineInputs.py lines 241-255
        **Used For**: Vacuum containment, structural support, safety barrier
        **Assumptions**:
        - Toroidal shell with double-wall construction (typical)
        - Simplified geometry (actual vessel has ports, penetrations)
        - Design pressure includes disruption loads and coolant failure scenarios
        **Validation**: Structural analysis, leak rate < 10^-6 Pa·m³/s
        **Last Updated**: 2025-11-01
        */

        // Geometry attributes
        attribute inner_radius : Real {
            doc /*
            Inner radius of vacuum vessel at midplane.
            Interface with blanket/first-wall assembly.
            */
        }

        attribute outer_radius : Real {
            doc /*
            Outer radius of vacuum vessel at midplane.
            Determined by wall thickness and structural requirements.
            */
        }

        attribute wall_thickness : Real {
            doc /*
            Radial thickness of vessel wall.
            Typically double-wall design: inner shell + ribs + outer shell.
            Range: 0.1-0.3 m depending on size and loads.
            */
        }

        attribute height : Real {
            doc /*
            Vertical extent of vacuum vessel.
            Determined by plasma elongation and clearances.
            */
        }

        // Material
        attribute material : String {
            doc /*
            Vacuum vessel structural material.
            Typically: SS316L, SS316LN (low activation variants preferred).
            Requirements: vacuum compatibility, weldability, radiation resistance.
            */
        }

        // Port configuration
        attribute n_ports : Integer {
            doc /*
            Number of major ports in vacuum vessel.
            Ports required for: neutral beam injection, RF heating, diagnostics,
            pumping, remote handling access, coolant connections.
            Typical: 12-24 ports depending on machine size.
            */
        }

        attribute port_penetration_fraction : Real {
            doc /*
            Fraction of vessel surface area occupied by ports.
            Affects structural integrity and neutronics.
            Typical: 0.10-0.20
            */
        }

        // Design parameters
        attribute design_pressure_external : Real {
            doc /*
            Design pressure for external loading (atmospheric pressure).
            Vessel must withstand atmospheric pressure when evacuated internally.
            Typically: 101325 Pa (1 atm)
            */
        }

        attribute design_pressure_internal : Real {
            doc /*
            Design pressure for internal overpressure scenarios.
            Includes coolant leak accidents (loss of coolant accident - LOCA).
            Typical: 0.2-0.5 MPa for water-cooled blanket LOCA.
            */
        }

        attribute design_temperature : Real {
            doc /*
            Maximum design temperature for vessel.
            Typical: 200-250°C (baking temperature for conditioning).
            */
        }

        // Vacuum performance
        attribute base_pressure : Real {
            doc /*
            Base vacuum pressure during operation.
            Typical: 10^-6 to 10^-7 Pa for fusion plasma operation.
            */
        }

        attribute leak_rate : Real {
            doc /*
            Maximum allowable leak rate [Pa·m³/s].
            Regulatory requirement for tritium confinement.
            Typical: < 10^-6 Pa·m³/s
            */
        }

        // Structural performance
        attribute disruption_load_capacity : Real {
            doc /*
            Maximum force capacity for plasma disruption loads.
            Disruptions induce large electromagnetic forces on vessel.
            Design-specific, calculated from disruption scenarios.
            */
        }

        // Volumes
        attribute volume_shell : Real {
            doc /*
            Total volume of vacuum vessel shell material.
            Used for mass and cost calculations.
            */
        }

        attribute volume_internal : Real {
            doc /*
            Internal volume enclosed by vacuum vessel.
            Used for pumping speed and inventory calculations.
            */
        }

        constraint ThicknessConsistency {
            doc /*
            Outer radius must equal inner radius plus wall thickness.
            */
            outer_radius == inner_radius + wall_thickness
        }
    }
}
