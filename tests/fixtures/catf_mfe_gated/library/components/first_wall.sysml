package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for plasma-facing components.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'First Wall' {
        doc /*
        Plasma-facing first wall component absorbing particle and heat flux.

        The first wall is the innermost component directly facing the plasma,
        subject to the most severe operating conditions in the fusion reactor:
        1. High heat flux from plasma radiation and charged particles
        2. High neutron flux causing material damage and activation
        3. Plasma particle bombardment (erosion, sputtering)
        4. Cyclic thermal and mechanical stresses

        **Source**: Plasma-facing component (PFC) design principles
        **Reference**: ITER first wall design, Rieth et al. (2013) tungsten materials review
        **PyFECONS**: Typically included in blanket definition or separate module
        **Used For**: Plasma boundary, armor protection, heat removal
        **Assumptions**:
        - Multi-layer structure: armor + cooling + structural backing
        - Steady-state heat flux (transients handled separately)
        - Uniform coverage (actual design has gaps and castellations)
        **Validation**: Heat flux limits, erosion rates, structural integrity
        **Last Updated**: 2025-11-01
        */

        part armor_layer {
            doc /*
            Plasma-facing armor layer providing erosion resistance.

            The armor layer directly contacts the plasma and must:
            - Withstand high heat flux (5-20 MW/m² steady-state)
            - Resist sputtering and erosion
            - Have high melting point and thermal conductivity
            - Have low plasma contamination (low-Z or high-Z depending on location)
            */

            attribute material : String {
                doc /*
                Armor material selection by location:
                - High-heat-flux regions (divertor): Tungsten (high-Z)
                - Main chamber first wall: Beryllium (low-Z) or Tungsten
                - Future designs: SiC, advanced tungsten alloys
                */
            }

            attribute thickness : Real {
                doc /*
                Armor layer thickness.
                Typical: 2-10 mm for tungsten, 5-15 mm for beryllium.
                Trade-off between erosion lifetime and thermal stress.
                */
            }

            attribute heat_flux_limit : Real {
                doc /*
                Maximum steady-state heat flux capability [MW/m²].
                Material-dependent:
                - Tungsten: 10-20 MW/m² (actively cooled)
                - Beryllium: 5-10 MW/m²
                - Carbon fiber composite: 10-15 MW/m² (legacy, not recommended)
                */
            }

            attribute erosion_rate : Real {
                doc /*
                Physical sputtering erosion rate [mm/year].
                Design-specific, depends on:
                - Plasma edge temperature and density
                - Impurity content in plasma
                - Surface temperature
                Typical: 0.1-1 mm/year for tungsten at fusion conditions
                */
            }

            attribute thermal_conductivity : Real {
                doc /*
                Thermal conductivity of armor material [W/(m·K)].
                Critical for heat removal:
                - Tungsten: ~173 W/(m·K) at room temp, decreases with temperature
                - Beryllium: ~200 W/(m·K)
                */
            }
        }

        part cooling_system {
            doc /*
            Active cooling system to remove heat from first wall.

            High heat flux requires active cooling to maintain acceptable
            temperatures. Cooling channels embedded in or behind armor layer.
            */

            attribute coolant_type : String {
                doc /*
                Coolant fluid:
                - Pressurized water: Most common, well-established technology
                - Helium gas: High temperature capability, chemically inert
                - Liquid metals: Very high heat transfer, complexity challenges
                */
            }

            attribute channel_geometry : String {
                doc /*
                Cooling channel configuration:
                - "finger" = Hypervapotron-type channels (high heat flux capability)
                - "tube" = Circular or rectangular tubes in structural backing
                - "jet" = Impingement cooling for highest heat flux
                */
            }

            attribute flow_rate : Real {
                doc /*
                Coolant volumetric flow rate through first wall.
                Determines pumping power and heat removal capability.
                */
            }

            attribute inlet_temperature : Real {
                doc /*
                Coolant inlet temperature.
                Typical: 100-150°C for water, 300-400°C for helium.
                */
            }

            attribute outlet_temperature : Real {
                doc /*
                Coolant outlet temperature.
                Limited by: coolant properties, structural material limits, thermodynamic efficiency.
                */
            }

            attribute pressure_operating : Real {
                doc /*
                Coolant operating pressure.
                Water: 10-20 MPa (subcritical), Helium: 8-10 MPa.
                */
            }
        }

        part structural_backing {
            doc /*
            Structural support layer behind armor and cooling.

            Provides mechanical strength, contains cooling channels,
            and transfers loads to vacuum vessel or blanket structure.
            */

            attribute material : String {
                doc /*
                Structural material:
                - CuCrZr alloy: High thermal conductivity, good for water-cooled designs
                - Stainless steel (SS316): Standard structural material
                - Advanced alloys: ODS steel, SiC/SiC composites (future)
                */
            }

            attribute thickness : Real {
                doc /*
                Structural backing thickness.
                Typical: 10-30 mm, depends on mechanical loads and cooling design.
                */
            }

            attribute temperature_max : Real {
                doc /*
                Maximum allowable temperature for structural material.
                CuCrZr: ~350°C, SS316: ~550°C
                */
            }
        }

        // Overall first wall attributes
        attribute total_thickness : Real {
            doc /*
            Total radial thickness of first wall assembly.
            Sum of: armor + cooling channels + structural backing.
            Typical: 20-50 mm total.
            */
        }

        attribute surface_area : Real {
            doc /*
            Total plasma-facing surface area of first wall.
            Depends on plasma chamber geometry and coverage fraction.
            */
        }

        attribute heat_flux_average : Real {
            doc /*
            Average heat flux over first wall surface [MW/m²].
            Lower than peak due to radiation distribution.
            Typical: 0.5-2 MW/m² average, 5-10 MW/m² peak.
            */
        }

        attribute heat_flux_peak : Real {
            doc /*
            Peak heat flux at highest-loaded location [MW/m²].
            Design-driving parameter for armor and cooling.
            */
        }

        attribute lifetime_fluence : Real {
            doc /*
            Neutron fluence over component lifetime [MW·yr/m²].
            Determines radiation damage and replacement schedule.
            ITER target: ~0.3 MW·yr/m² for Be first wall
            DEMO target: 2-5 MW·yr/m² for W first wall
            */
        }

        constraint TotalThicknessConsistency {
            doc /*
            Total thickness is sum of constituent layers.
            (Simplified - assumes no gaps or bond layers)
            */
            total_thickness == armor_layer.thickness + structural_backing.thickness
        }
    }
}
