package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for radiation shielding.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Shield Assembly' {
        doc /*
        Radiation shielding assembly protecting magnets and personnel.

        The shield assembly provides multiple layers of protection:
        1. Neutron shielding - attenuates fast neutron flux
        2. Gamma shielding - absorbs gamma radiation
        3. Thermal shielding - reduces heat load to cryogenic magnets
        4. Biological shielding - protects personnel and environment

        **Source**: Radiation shielding principles for fusion reactors
        **Reference**: ITER shield design, ARIES shielding studies
        **PyFECONS**: DefineInputs.py lines 89-94
        **Used For**: Magnet protection (dose limits), personnel safety
        **Assumptions**:
        - Simplified representation (actual shields have heterogeneous composition)
        - Cylindrical/toroidal geometry
        - Attenuation factors from transport calculations
        **Validation**: Neutron flux at magnet < 10^18 n/m²/s, lifetime dose < limits
        **Last Updated**: 2025-11-01
        */

        part neutron_shield {
            doc /*
            Primary neutron attenuation layer.

            Uses materials with high neutron scattering and absorption cross-sections
            to reduce neutron flux reaching magnets and outer components.
            */

            attribute material : String {
                doc /*
                Neutron shielding material (SS316, borated steel, WC).
                Iron and steel good for fast neutron moderation.
                Boron compounds for thermal neutron absorption.
                */
            }

            attribute thickness : Real {
                doc /* Radial thickness of neutron shield layer */
            }

            attribute attenuation_factor : Real {
                doc /*
                Neutron flux attenuation factor (ratio of exit flux to entrance flux).
                Calculated from transport code (MCNP, Serpent, ADVANTG).
                Typical: 1e-3 to 1e-5 for adequate shielding.
                */
            }

            attribute volume : Real {
                doc /* Total volume of neutron shielding material */
            }
        }

        part gamma_shield {
            doc /*
            Gamma radiation shielding layer.

            Absorbs gamma rays from neutron capture reactions and activation.
            High-Z materials (lead, tungsten) most effective for gamma attenuation.
            */

            attribute material : String {
                doc /* Gamma shielding material (Pb, W, dense concrete) */
            }

            attribute thickness : Real {
                doc /* Radial thickness of gamma shield */
            }

            attribute attenuation_factor : Real {
                doc /* Gamma flux attenuation factor */
            }

            attribute volume : Real {
                doc /* Total volume of gamma shielding material */
            }
        }

        part thermal_shield {
            doc /*
            Thermal radiation shield for cryogenic systems.

            Reduces radiative heat load from warm components (plasma, blanket)
            to cryogenic components (superconducting magnets). Typically uses
            reflective surfaces or actively cooled panels.
            */

            attribute material : String {
                doc /* Thermal shield material (typically cooled steel or aluminum) */
            }

            attribute thickness : Real {
                doc /* Radial thickness of thermal shield */
            }

            attribute heat_load_reduction : Real {
                doc /*
                Factor by which thermal shield reduces radiative heat load.
                Typical: 0.1-0.01 (90-99% reduction)
                */
            }

            attribute volume : Real {
                doc /* Total volume of thermal shield material */
            }
        }

        part biological_shield {
            doc /*
            Outermost biological shield protecting personnel.

            Thick concrete or concrete-and-steel composite shield surrounding
            entire reactor to limit radiation dose to personnel in reactor hall.
            Design goal typically: < 2.5 μSv/hr at outer surface (hands-on maintenance).
            */

            attribute material : String {
                doc /* Biological shield material (concrete, borated concrete) */
            }

            attribute thickness : Real {
                doc /*
                Radial thickness of biological shield.
                Typical: 1-2 meters for hands-on maintenance access.
                */
            }

            attribute dose_limit : Real {
                doc /*
                Maximum allowable dose rate at shield outer surface [μSv/hr].
                Regulatory limit for hands-on maintenance: typically 2.5 μSv/hr.
                */
            }

            attribute volume : Real {
                doc /* Total volume of biological shield */
            }
        }

        // Total thickness
        attribute thickness_total : Real {
            doc /*
            Total radial thickness of all shield layers combined.
            Sum of: neutron shield + gamma shield + thermal shield + biological shield.
            */
        }

        constraint TotalThicknessConsistency {
            doc /*
            Total thickness must equal sum of individual layer thicknesses.
            (Simplified - assumes no gaps between layers)
            */
            thickness_total == neutron_shield.thickness + gamma_shield.thickness +
                               thermal_shield.thickness + biological_shield.thickness
        }
    }
}
