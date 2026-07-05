package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for breeding blanket and tritium systems.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Breeding Blanket' {
        doc /*
        Tritium breeding blanket surrounding the plasma.

        The breeding blanket serves multiple critical functions:
        1. Tritium breeding via Li-6(n,α)T and Li-7(n,n'α)T reactions
        2. Neutron multiplication to enhance breeding ratio
        3. Energy conversion (neutron kinetic energy → heat)
        4. Neutron shielding (protecting magnets and vessel)

        **Source**: Fusion blanket design principles
        **Reference**: DEMO blanket studies, ARIES blanket designs, ITER Test Blanket Modules
        **PyFECONS**: DefineInputs.py lines 44-51
        **Used For**: Tritium self-sufficiency, power extraction, radiation protection
        **Assumptions**:
        - Simplified representation (actual blankets have complex internal structure)
        - Homogenized material properties in zones
        - Coverage fraction accounts for ports and gaps
        **Validation**: Compare TBR (tritium breeding ratio) with neutronic calculations
        **Last Updated**: 2025-11-01
        */

        part breeding_zone {
            doc /*
            Zone containing lithium compound for tritium breeding.

            Ceramic breeders (Li2TiO3, Li4SiO4) or liquid breeders (PbLi, liquid Li)
            provide lithium for neutron reactions producing tritium fuel.
            */

            attribute breeder_material : String {
                doc /* Lithium-bearing material (Li2TiO3, Li4SiO4, PbLi, liquid Li) */
            }

            attribute enrichment_li6 : Real {
                doc /*
                Li-6 enrichment fraction (natural = 0.075, enriched up to 0.90).
                Higher enrichment increases breeding but increases cost.
                */
            }

            attribute thickness_radial : Real {
                doc /* Radial thickness of breeding zone */
            }

            attribute volume : Real {
                doc /* Total volume of breeding material */
            }

            attribute lithium_mass : Real {
                doc /* Total mass of lithium in breeder (for inventory tracking) */
            }
        }

        part multiplier_zone {
            doc /*
            Neutron multiplier zone to enhance breeding ratio.

            Materials like beryllium or lead undergo (n,2n) reactions,
            doubling the number of neutrons available for breeding.
            */

            attribute multiplier_material : String {
                doc /* Neutron multiplier (Be, Be12Ti, Pb) */
            }

            attribute thickness_radial : Real {
                doc /* Radial thickness of multiplier zone */
            }

            attribute volume : Real {
                doc /* Total volume of multiplier */
            }
        }

        part structural_backing {
            doc /*
            Structural support and containment for breeding materials.

            Provides mechanical support, channels for coolant, and
            containment of breeding materials.
            */

            attribute structure_material : String {
                doc /* Structural material (SS316, FMS/RAFM steel) */
            }

            attribute thickness : Real {
                doc /* Thickness of structural elements */
            }

            attribute volume : Real {
                doc /* Total volume of structure */
            }
        }

        part first_wall_interface {
            doc /*
            Plasma-facing interface of the blanket.

            May include armor layer (W, Be) and cooling channels.
            Overlap with 'First Wall' component - may be modeled separately.
            */

            attribute armor_material : String {
                doc /* Armor material (W, Be, SiC) */
            }

            attribute thickness : Real {
                doc /* Armor thickness */
            }
        }

        // Coolant system
        attribute coolant_primary : String {
            doc /*
            Primary coolant circulating through blanket.
            Options: He, H2O, PbLi (dual-purpose breeder-coolant)
            */
        }

        attribute coolant_secondary : String {
            doc /*
            Secondary coolant for power conversion (if applicable).
            May be same as primary or different (e.g., water for steam cycle).
            */
        }

        // Coverage attributes
        attribute coverage_fraction_toroidal : Real {
            doc /*
            Fraction of toroidal circumference covered by blanket (accounts for gaps).
            Typical: 0.75-0.85 (gaps for ports, diagnostics, heating systems)
            */
        }

        attribute coverage_fraction_poloidal : Real {
            doc /*
            Fraction of poloidal cross-section covered by blanket.
            Typical: 0.70-0.80 (gaps for divertor, ports, structural supports)
            */
        }

        // Performance metrics
        attribute breeding_ratio : Real {
            doc /*
            Tritium breeding ratio (T produced per T burned in plasma).
            Must be > 1.0 for self-sufficiency (typically target 1.05-1.15).
            Calculated from neutronics, not input parameter.
            */
        }

        attribute energy_multiplication : Real {
            doc /*
            Neutron energy multiplication factor.
            Ratio of energy deposited in blanket to 14.1 MeV neutron energy.
            Typical: 1.1-1.3 (neutron multiplication adds energy)
            */
        }
    }
}
