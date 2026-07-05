// Top-Level System Definition
// Phase 0: Fusion Power Plant system architecture

package FusionLibrary {
    public import ScalarValues::*;
    public import SI::*;

    // Top-level system definition
    part def 'Fusion Power Plant' {
        doc /*
        Top-level fusion power plant system.

        A fusion power plant converts fusion energy into electrical power
        through plasma confinement, neutron breeding, and thermal conversion.

        **Purpose**: Generate net electrical power for the grid
        **Concept**: Magnetic confinement fusion (MFE) or Inertial confinement fusion (ICE)
        **Phase**: Phase 0 - Foundation
        */

        // Mission-level attributes
        attribute net_electric_power : Real {
            doc /* Net electrical power delivered to grid (MW) */
        }

        attribute availability : Real {
            doc /* Plant availability factor (fraction) */
        }

        attribute lcoe : Real {
            doc /* Levelized cost of electricity (USD/MWh) */
        }

        attribute lifetime_years : Real {
            doc /* Design lifetime (years) */
        }

        attribute q_engineering : Real {
            doc /* Engineering gain factor (net electric / auxiliary power) */
        }

        attribute tbr : Real {
            doc /* Tritium breeding ratio */
        }
    }

    // Major subsystem categories (to be elaborated in Phase 1)
    part def 'Fusion Island' {
        doc /*
        Core fusion reactor system (CAS22: Reactor Plant Equipment)
        Contains: magnets, blanket, vacuum, heating, divertor
        */
    }

    part def 'Balance of Plant' {
        doc /*
        Power conversion and heat rejection systems (CAS23-26)
        Contains: turbine, electrical, cooling
        */
    }

    part def 'Auxiliary Systems' {
        doc /*
        Support systems (CAS27)
        Contains: fuel handling, tritium processing
        */
    }
}
