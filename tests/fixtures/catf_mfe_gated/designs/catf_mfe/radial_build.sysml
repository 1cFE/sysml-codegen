/*
 * CATF MFE Radial Build Design Instance
 *
 * This file defines the specific radial build for the Clean Air Task Force
 * MFE (Magnetic Fusion Energy) reference design, with 13 concentric layers
 * from plasma axis to biological shield.
 *
 * All thickness values extracted from PyFECONS DefineInputs.py lines 71-87.
 */

package CATFMFERadialBuild {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // ADR-002: Import geometry calc defs from library
    private import FusionPhysicsGeometry::TorusMinorRadius;
    private import FusionPhysicsGeometry::TorusVolume;
    private import FusionPhysicsGeometry::TorusSurfaceArea;
    private import FusionPhysicsGeometry::MagnetSurfaceArea;

    /*
     * Complete CATF MFE Radial Build
     */
    part catf_radial_build {
        doc /*
        CATF MFE radial build - 13 concentric cylindrical layers defining the
        reactor geometry from plasma axis to biological shield.

        **Source**: PyFECONS DefineInputs.py lines 71-87
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py
        **Design Type**: Spherical Tokamak with elongation = 3.0

        **Key Features**:
        - Total radial extent: 8.55 m from axis to outer bioshield
        - Compact central column (0.18 m inner radius) for ST geometry
        - Solid breeder blanket with Li2TiO3
        - Dual shield layers (HT and LT) for neutron attenuation
        - Minimal gap thicknesses (0.5 m) for maintenance access

        **Coordinate System**: Cylindrical (r, z, θ) with z=0 at midplane

        **Updates**:
        - 2025-11-09: Added volume calculations for all layers (hollow torus formula)
        - 2025-11-09: Added aggregated volumes and surface areas for subsystem references

        **Last Updated**: 2025-11-09
        */

        // From PyFECONS line 72 - plasma elongation (vertical/horizontal aspect)
        attribute elongation : Real = 3.0;

        // Major radius for volume calculations (center of plasma)
        attribute major_radius : Real = 3.0 [m];  // axis_region.outer_radius

        // Layer 1: Axis to Plasma Inner Edge
        part axis_region {
            doc /*
            Central region from machine axis (r=0) to plasma inner edge.

            In a spherical tokamak, this region is minimal due to the compact
            central column design. Contains the inner leg of the TF coils and CS.

            **Source**: PyFECONS line 73 (axis_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Axis to Plasma";
            attribute inner_radius : Real = 0.0 [m];
            attribute thickness : Real = 3.0 [m];  // From line 73
            attribute outer_radius : Real = 3.0 [m];  // Calculated
            attribute material_primary : String = "None";  // Plasma region
        }

        // Layer 2: Plasma
        part plasma_region {
            doc /*
            Plasma region - hot fusion fuel at ~100 million K.

            For CATF MFE, the plasma extends from r=3.0m to r=4.1m with
            elongation κ=3.0, creating a tall, thin plasma cross-section
            typical of spherical tokamaks.

            **Source**: PyFECONS line 74 (plasma_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Plasma";
            attribute inner_radius : Real = 3.0 [m];
            attribute thickness : Real = 1.1 [m];  // From line 74
            attribute outer_radius : Real = 4.1 [m];
            attribute material_primary : String = "DT Plasma";
            attribute elongation : Real = 3.0;  // Inherited from parent

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = plasma_region::inner_radius;
                in r_outer = plasma_region::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern for cross-file access
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 3: Vacuum Gap
        part vacuum_gap {
            doc /*
            Vacuum gap between plasma edge and first wall.

            Provides clearance for plasma edge physics (scrape-off layer)
            and allows for plasma position control without wall contact.

            **Source**: PyFECONS line 75 (vacuum_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Vacuum Gap";
            attribute inner_radius : Real = 4.1 [m];
            attribute thickness : Real = 0.1 [m];  // From line 75
            attribute outer_radius : Real = 4.2 [m];
            attribute material_primary : String = "Vacuum";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = vacuum_gap::inner_radius;
                in r_outer = vacuum_gap::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 4: First Wall
        part first_wall {
            doc /*
            First wall - plasma-facing armor layer.

            **Material**: Beryllium (from PyFECONS blanket config line 45)
            **Function**: Withstand particle bombardment and heat flux
            **Heat Flux**: ~10 MW/m² steady-state (typical for ST)

            **Source**: PyFECONS line 76 (firstwall_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "First Wall";
            attribute inner_radius : Real = 4.2 [m];
            attribute thickness : Real = 0.2 [m];  // From line 76
            attribute outer_radius : Real = 4.4 [m];
            attribute material_primary : String = "Beryllium";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = first_wall::inner_radius;
                in r_outer = first_wall::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 5: Blanket
        part blanket {
            doc /*
            Breeding blanket - tritium production and heat extraction.

            **Breeder**: Li2TiO3 solid ceramic (from PyFECONS line 46)
            **Multiplier**: Be12Ti (from PyFECONS line 49)
            **Structure**: Ferritic-Martensitic Steel (from PyFECONS line 50)
            **Coolant**: Li primary, PbLi secondary (lines 47-48)

            **Function**:
            - Breed tritium via Li-6(n,α)T reaction
            - Extract fusion neutron energy as heat
            - Shield inner components from neutron damage

            **Target TBR**: ≥1.05 for self-sufficiency

            **Source**: PyFECONS line 77 (blanket1_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Blanket";
            attribute inner_radius : Real = 4.4 [m];
            attribute thickness : Real = 0.8 [m];  // From line 77
            attribute outer_radius : Real = 5.2 [m];
            attribute material_primary : String = "Li2TiO3";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = blanket::inner_radius;
                in r_outer = blanket::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 6: Reflector
        part reflector {
            doc /*
            Neutron reflector - returns escaping neutrons back to blanket.

            **Function**: Improve TBR by reflecting neutrons for additional
            breeding reactions and energy multiplication.

            **Material**: Typically beryllium or lead

            **Source**: PyFECONS line 78 (reflector_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Reflector";
            attribute inner_radius : Real = 5.2 [m];
            attribute thickness : Real = 0.2 [m];  // From line 78
            attribute outer_radius : Real = 5.4 [m];
            attribute material_primary : String = "Beryllium";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = reflector::inner_radius;
                in r_outer = reflector::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 7: High Temperature Shield
        part ht_shield {
            doc /*
            High-temperature shield - primary neutron and gamma shielding.

            **Function**: Attenuate neutron flux and gamma radiation to protect
            components outside the vacuum vessel.

            **Material**: Likely borated steel or tungsten carbide (from PyFECONS
            shield config lines 89-94, f_BFS=0.9 suggests borated steel dominant)

            **Source**: PyFECONS line 79 (ht_shield_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "HT Shield";
            attribute inner_radius : Real = 5.4 [m];
            attribute thickness : Real = 0.2 [m];  // From line 79
            attribute outer_radius : Real = 5.6 [m];
            attribute material_primary : String = "BoratedSteel";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = ht_shield::inner_radius;
                in r_outer = ht_shield::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 8: Structure
        part structure {
            doc /*
            Primary structural layer - supports internal components.

            **Material**: SS316 stainless steel (standard structural material)
            **Function**: Mechanical support, load bearing, pressure boundary

            **Source**: PyFECONS line 80 (structure_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Structure";
            attribute inner_radius : Real = 5.6 [m];
            attribute thickness : Real = 0.2 [m];  // From line 80
            attribute outer_radius : Real = 5.8 [m];
            attribute material_primary : String = "SS316";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = structure::inner_radius;
                in r_outer = structure::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 9: Gap 1
        part gap1 {
            doc /*
            First maintenance gap - clearance between internal components and vessel.

            **Function**: Access for maintenance, inspection, and component removal.
            Filled with vacuum or low-pressure gas during operation.

            **Source**: PyFECONS line 81 (gap1_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Gap 1";
            attribute inner_radius : Real = 5.8 [m];
            attribute thickness : Real = 0.5 [m];  // From line 81
            attribute outer_radius : Real = 6.3 [m];
            attribute material_primary : String = "Vacuum";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = gap1::inner_radius;
                in r_outer = gap1::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 10: Vacuum Vessel
        part vessel {
            doc /*
            Vacuum vessel - primary vacuum boundary.

            **Material**: SS316 stainless steel
            **Function**:
            - Maintain vacuum environment for plasma
            - Structural pressure boundary (1 atm external)
            - Secondary confinement barrier

            **Pressure**: Atmospheric external, vacuum internal

            **Source**: PyFECONS line 82 (vessel_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Vacuum Vessel";
            attribute inner_radius : Real = 6.3 [m];
            attribute thickness : Real = 0.2 [m];  // From line 82
            attribute outer_radius : Real = 6.5 [m];
            attribute material_primary : String = "SS316";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = vessel::inner_radius;
                in r_outer = vessel::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 11: TF Coil
        part tf_coil {
            doc /*
            Toroidal field coil layer - location of TF magnets.

            **Material**: HTS CICC (conductor) + SS316 (case)
            **Function**: Generate toroidal magnetic field for plasma confinement

            **Note**: This is the radial thickness allocated to TF coils in the
            build. The actual 12 discrete TF coils defined in magnets.sysml
            occupy this space toroidally.

            **Source**: PyFECONS line 83 (coil_t = tf_dr from line 25)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "TF Coil";
            attribute inner_radius : Real = 6.5 [m];
            attribute thickness : Real = 0.25 [m];  // From line 83 (= tf_dr)
            attribute outer_radius : Real = 6.75 [m];
            attribute material_primary : String = "HTS_CICC";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = tf_coil::inner_radius;
                in r_outer = tf_coil::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 12: Gap 2
        part gap2 {
            doc /*
            Second maintenance gap - clearance between magnets and outer shield.

            **Function**: Access for TF coil maintenance, cryogenic systems,
            and feedthroughs. May contain cryostat walls and insulation.

            **Source**: PyFECONS line 84 (gap2_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Gap 2";
            attribute inner_radius : Real = 6.75 [m];
            attribute thickness : Real = 0.5 [m];  // From line 84
            attribute outer_radius : Real = 7.25 [m];
            attribute material_primary : String = "Air";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = gap2::inner_radius;
                in r_outer = gap2::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 13: Low Temperature Shield
        part lt_shield {
            doc /*
            Low-temperature (cryogenic) shield - protects superconducting magnets.

            **Function**:
            - Thermal radiation shield for cryogenic magnets
            - Additional neutron/gamma attenuation
            - Reduces heat load to cryogenic system

            **Material**: Likely aluminum or steel with cryogenic insulation

            **Source**: PyFECONS line 85 (lt_shield_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "LT Shield";
            attribute inner_radius : Real = 7.25 [m];
            attribute thickness : Real = 0.3 [m];  // From line 85
            attribute outer_radius : Real = 7.55 [m];
            attribute material_primary : String = "Aluminum";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = lt_shield::inner_radius;
                in r_outer = lt_shield::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Layer 14: Biological Shield
        part bioshield {
            doc /*
            Biological shield - final radiation barrier for personnel protection.

            **Material**: Concrete (high-density concrete, possibly borated)
            **Function**:
            - Attenuate residual neutron and gamma radiation to safe levels
            - Structural support for building
            - Massive radiation barrier (1m thick)

            **Requirement**: Reduce dose rate to <2.5 µSv/hr at outer surface
            for unlimited personnel access (IAEA BSS)

            **Source**: PyFECONS line 86 (bioshield_t)
            **Last Updated**: 2025-11-01
            */

            attribute name : String = "Biological Shield";
            attribute inner_radius : Real = 7.55 [m];
            attribute thickness : Real = 1.0 [m];  // From line 86
            attribute outer_radius : Real = 8.55 [m];
            attribute material_primary : String = "Concrete";

            // Geometry calculations using library calc defs (ADR-002 compliant)
            calc minor_calc : TorusMinorRadius {
                in r_inner = bioshield::inner_radius;
                in r_outer = bioshield::outer_radius;
                in r_major = catf_radial_build::major_radius;
            }

            calc volume_calc : TorusVolume {
                in r_major = catf_radial_build::major_radius;
                in a = minor_calc.a;
                in kappa = catf_radial_build::elongation;
            }

            // EXPOSE pattern
            attribute minor_radius : Real = minor_calc.a;
            attribute volume : Real = volume_calc.volume;
        }

        // Aggregated volumes and surface areas for subsystem references
        // Source: PyFECONS cas220101_reactor_equipment.py lines 91-205
        // Note: These are valid EXPOSE patterns (pure value propagation from calc outputs)
        attribute magnet_volume_total : Real = tf_coil.volume;  // m^3 - TF coils only
        attribute blanket_volume_total : Real = blanket.volume;  // m^3 - Breeding blanket

        // First wall surface area (inner plasma-facing surface)
        // ADR-002 compliant: calc usage + EXPOSE pattern
        calc first_wall_area_calc : TorusSurfaceArea {
            in r_major = catf_radial_build::major_radius;
            in a = plasma_region.minor_radius;  // From calc EXPOSE
            in kappa = catf_radial_build::elongation;
        }
        attribute first_wall_area : Real = first_wall_area_calc.area;  // [m^2]

        // Magnet surface area (exposed TF surface - approximate)
        // ADR-002 compliant: calc usage + EXPOSE pattern
        calc magnet_surface_calc : MagnetSurfaceArea {
            in r_inner = tf_coil.inner_radius;
            in thickness = tf_coil.thickness;
            in kappa = catf_radial_build::elongation;
            // f_exposed uses default := 0.5
        }
        attribute magnet_surface_area : Real = magnet_surface_calc.area;  // [m^2]

        constraint LayerContinuity {
            doc /* Each layer must begin where the previous layer ends (no gaps or overlaps) */

            plasma_region.inner_radius == axis_region.outer_radius and
            vacuum_gap.inner_radius == plasma_region.outer_radius and
            first_wall.inner_radius == vacuum_gap.outer_radius and
            blanket.inner_radius == first_wall.outer_radius and
            reflector.inner_radius == blanket.outer_radius and
            ht_shield.inner_radius == reflector.outer_radius and
            structure.inner_radius == ht_shield.outer_radius and
            gap1.inner_radius == structure.outer_radius and
            vessel.inner_radius == gap1.outer_radius and
            tf_coil.inner_radius == vessel.outer_radius and
            gap2.inner_radius == tf_coil.outer_radius and
            lt_shield.inner_radius == gap2.outer_radius and
            bioshield.inner_radius == lt_shield.outer_radius
        }

        constraint RadiusThicknessConsistency {
            doc /* Each layer's outer radius must equal inner radius plus thickness */

            axis_region.outer_radius == axis_region.inner_radius + axis_region.thickness and
            plasma_region.outer_radius == plasma_region.inner_radius + plasma_region.thickness and
            vacuum_gap.outer_radius == vacuum_gap.inner_radius + vacuum_gap.thickness and
            first_wall.outer_radius == first_wall.inner_radius + first_wall.thickness and
            blanket.outer_radius == blanket.inner_radius + blanket.thickness and
            reflector.outer_radius == reflector.inner_radius + reflector.thickness and
            ht_shield.outer_radius == ht_shield.inner_radius + ht_shield.thickness and
            structure.outer_radius == structure.inner_radius + structure.thickness and
            gap1.outer_radius == gap1.inner_radius + gap1.thickness and
            vessel.outer_radius == vessel.inner_radius + vessel.thickness and
            tf_coil.outer_radius == tf_coil.inner_radius + tf_coil.thickness and
            gap2.outer_radius == gap2.inner_radius + gap2.thickness and
            lt_shield.outer_radius == lt_shield.inner_radius + lt_shield.thickness and
            bioshield.outer_radius == bioshield.inner_radius + bioshield.thickness
        }
    }
}
