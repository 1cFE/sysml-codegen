package FusionComponents {
    doc /*
    Component library for fusion reactor subsystems.
    Contains reusable part definitions for divertor and power exhaust systems.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    part def 'Divertor' {
        doc /*
        Divertor system for exhaust of plasma particles and impurities.

        The divertor is the most critical and challenging plasma-facing component:
        1. Exhaust heat and particles from confined plasma (power exhaust)
        2. Remove helium ash from fusion reactions (impurity control)
        3. Control plasma edge conditions and stability
        4. Withstand extreme heat flux (up to 20 MW/m² steady-state)

        The divertor operates at the intersection of magnetic field lines
        leaving the confined plasma, creating a localized region where
        plasma particles strike target plates.

        **Source**: Divertor physics and engineering principles
        **Reference**: ITER divertor design, Pitts et al. (2019) physics basis
        **PyFECONS**: Often simplified or included in blanket cost estimates
        **Used For**: Real exhaust, particle exhaust, impurity control
        **Assumptions**:
        - Modular cassette design (toroidally discrete units)
        - Water-cooled tungsten targets (baseline technology)
        - Detached plasma regime for heat flux management
        **Validation**: Heat flux distribution, erosion lifetime, pumping efficiency
        **Last Updated**: 2025-11-01
        */

        part target_plates {
            doc /*
            Plasma-facing target plates where particles strike divertor.

            Target plates are divided into:
            - Inner target: Attached to inner leg of divertor
            - Outer target: Attached to outer leg of divertor
            - Strike points: Locations where separatrix intersects targets

            The targets experience the highest heat flux in the fusion reactor.
            */

            attribute armor_material : String {
                doc /*
                Target armor material - must withstand extreme conditions.

                Tungsten (W) is baseline choice:
                - Very high melting point (3422°C)
                - High thermal conductivity (~173 W/(m·K))
                - Good erosion resistance
                - Challenges: Embrittlement, cracking, melt damage during transients

                Alternatives under development:
                - Tungsten alloys (W-Re, W-La)
                - Liquid metal targets (Li, Sn)
                - Advanced cooling schemes
                */
            }

            attribute cooling_configuration : String {
                doc /*
                Cooling technology for target plates:
                - "monoblock" = W blocks brazed to CuCrZr cooling tube (ITER baseline)
                - "flat_tile" = W tiles on cooling substrate
                - "finger" = Hypervapotron-style high heat flux cooling
                - "liquid_metal" = Flowing liquid metal film cooling (advanced concept)
                */
            }

            attribute heat_flux_capability : Real {
                doc /*
                Maximum steady-state heat flux capability [MW/m²].

                ITER baseline: 10 MW/m² steady-state, 20 MW/m² slow transient.
                Future reactors need: 10-20 MW/m² with margin for reliability.

                Heat flux management strategies:
                - Plasma detachment (reduces heat flux via volumetric losses)
                - Flux expansion (spreads heat over larger area)
                - Radiative dissipation (impurity seeding)
                */
            }

            attribute peak_heat_flux : Real {
                doc /*
                Peak heat flux during normal operation [MW/m²].
                Occurs near strike point, design-specific from plasma modeling.
                */
            }

            attribute surface_area_inner : Real {
                doc /* Surface area of inner divertor target */
            }

            attribute surface_area_outer : Real {
                doc /* Surface area of outer divertor target */
            }

            attribute erosion_rate : Real {
                doc /*
                Tungsten erosion rate [mm/year].
                Mechanisms: Physical sputtering, chemical erosion (if carbon present),
                melt damage during transients.
                Typical: 0.5-2 mm/year depending on plasma conditions.
                Determines replacement interval.
                */
            }
        }

        part cassette_structure {
            doc /*
            Structural cassette containing targets, baffles, cooling manifolds.

            The divertor cassette is a removable, replaceable module that contains:
            - Target plates and structural supports
            - Cooling water manifolds and distribution
            - Baffle structures (guide plasma flow)
            - Pumping duct interfaces
            - Diagnostic integrations
            */

            attribute structural_material : String {
                doc /*
                Cassette structural material.
                Typically: SS316 or CuCrZr alloy.
                Requirements: Radiation resistance, thermal management, remote handling compatibility.
                */
            }

            attribute coolant_manifolds : String {
                doc /*
                Cooling manifold configuration.
                Complexity: Multiple parallel cooling circuits, headers, pressure boundaries.
                Critical for reliability - cooling failure leads to component melt.
                */
            }

            attribute cassette_mass : Real {
                doc /*
                Mass of single divertor cassette.
                Important for remote handling equipment design.
                ITER cassettes: ~10 tonnes each.
                */
            }

            attribute replacement_interval : Real {
                doc /*
                Design lifetime before cassette replacement [years or full-power-years].
                Limited by: Neutron damage, erosion, fatigue, recrystallization.
                ITER: ~2 years full-power operation
                DEMO target: 2-4 full-power years
                */
            }
        }

        // Overall divertor system attributes
        attribute n_divertor_modules : Integer {
            doc /*
            Number of divertor cassette modules around torus.
            Toroidally segmented for: manufacturing, installation, replacement.
            Typical: 24-54 modules depending on machine size.
            ITER: 54 cassettes
            */
        }

        attribute divertor_configuration : String {
            doc /*
            Divertor magnetic topology:
            - "single_null" = Single X-point, divertor at bottom (most common)
            - "double_null" = Two X-points, divertors top and bottom (alternate flux sharing)
            - "snowflake" = Modified X-point topology (advanced configuration)
            - "super_X" = Extended divertor leg for enhanced detachment (ST concept)
            */
        }

        attribute total_heat_load : Real {
            doc /*
            Total power flowing to divertor targets.
            Typically 60-80% of fusion power (rest radiated in core/edge).
            Example: 500 MW fusion → ~100 MW to divertor (with radiation).
            Critical design parameter driving cooling requirements.
            */
        }

        attribute particle_exhaust_rate : Real {
            doc /*
            Particle exhaust rate [particles/s].
            Must equal: DT fuel throughput + He ash production + impurities.
            Coupled to vacuum pumping system design.
            */
        }

        attribute pumping_speed : Real {
            doc /*
            Effective pumping speed at divertor [m³/s].
            Determines pressure control and impurity removal.
            Typical: 50-200 m³/s for DT, higher for He.
            */
        }

        attribute detachment_margin : Real {
            doc /*
            Operating margin to plasma detachment threshold.
            Detachment: Plasma cools and recombines before striking target,
            greatly reducing heat flux but requiring careful control.
            Typical target: 1.5-2.0× threshold for operational margin.
            */
        }

        constraint HeatLoadBalance {
            doc /*
            Heat load to divertor must be manageable by cooling system.
            Simplified: Total heat load < (Number of modules) × (Target area per module) × (Heat flux capability)
            */
            total_heat_load <= n_divertor_modules *
                (target_plates.surface_area_inner + target_plates.surface_area_outer) *
                target_plates.heat_flux_capability
        }
    }
}
