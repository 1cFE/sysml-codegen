/*
 * CATF MFE Shield Design Instance
 *
 * This file defines the specific shielding configuration for the
 * Clean Air Task Force MFE reference design.
 *
 * Parameters extracted from PyFECONS DefineInputs.py lines 89-94.
 */

package CATFMFEShield {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    /*
     * CATF MFE Shield Assembly Instance
     */
    part catf_shield {
        doc /*
        CATF MFE shield assembly - neutron and gamma radiation attenuation.

        **Source**: PyFECONS DefineInputs.py lines 89-94
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py

        **Configuration**:
        From PyFECONS Shield configuration (lines 89-94):
        - f_SiC = 0.00 (0% silicon carbide)
        - FPCPPFbLi = 0.1 (10% lead-lithium)
        - f_W = 0.00 (0% tungsten)
        - f_BFS = 0.9 (90% borated ferritic steel)

        **Shielding Strategy**:
        - Borated ferritic steel (BFS) dominant (90%)
        - Lead-lithium (PbLi) secondary (10%)
        - No exotic materials (SiC, W) to reduce cost

        **Function**:
        1. Attenuate 14.1 MeV fusion neutrons to thermal energies
        2. Reduce gamma radiation from neutron capture
        3. Protect superconducting magnets from radiation damage
        4. Reduce nuclear heating in TF/PF coils
        5. Minimize activation of components outside vessel

        **Target Attenuation**:
        - Neutron flux reduction: 10^5 to 10^6 through combined blanket+shield
        - Magnet dose: <10^9 n/cm^2/FPY at TF coil
        - Personnel dose: <2.5 µSv/hr at bioshield exterior

        **Last Updated**: 2025-11-01
        */

        // Neutron Shield Configuration
        part neutron_shield {
            doc /*
            Primary neutron attenuation layer.

            **Material Composition**: 90% Borated Ferritic Steel (BFS)
            - Base: Ferritic steel (Fe with ~9-12% Cr)
            - Boron content: ~2% by weight
            - Boron-10 has high thermal neutron cross-section (3840 barns)
            - Iron provides inelastic scattering to thermalize fast neutrons

            **Attenuation Mechanism**:
            1. Fast neutrons (14.1 MeV) → inelastic scattering → medium energy
            2. Medium energy → elastic scattering → thermal
            3. Thermal neutrons → B-10(n,α) capture

            **Expected Attenuation**: ~10^4 reduction in neutron flux

            **Source**: PyFECONS line 93 (f_BFS = 0.9)
            **Last Updated**: 2025-11-01
            */

            attribute material : String = "BoratedSteel";
            attribute thickness : Real = 0.36 [m];  // 90% of 0.4m total shield (0.2m HT + 0.2m structure)
            attribute fraction_volume : Real = 0.90;  // From PyFECONS line 93
            attribute boron_content : Real = 0.02;  // 2% by weight, typical for BFS
            attribute attenuation_factor : Real = 10000.0;  // Approximate, to be validated
        }

        // Gamma Shield Configuration
        part gamma_shield {
            doc /*
            Secondary gamma radiation attenuation.

            **Material Composition**: 10% Lead-Lithium (PbLi)
            - Formula: Pb₈₃Li₁₇ (eutectic, atomic %)
            - Density: 9400 kg/m³ (very high for gamma shielding)
            - Lead is excellent gamma absorber (high Z, high density)
            - Lithium provides additional neutron moderation

            **Gamma Sources**:
            1. Prompt gammas from fusion reactions
            2. Capture gammas from n+material reactions
            3. Activation gammas from radioactive decay

            **Expected Attenuation**: ~10^2-10^3 reduction in gamma dose

            **Source**: PyFECONS line 91 (FPCPPFbLi = 0.1)
            **Last Updated**: 2025-11-01
            */

            attribute material : String = "LeadLithium";
            attribute thickness : Real = 0.04 [m];  // 10% of 0.4m total shield
            // Relation (undirected): neutron_shield.fraction_volume + gamma_shield.fraction_volume = 1.0.
            // A composition closure over two terms, so the last term is derived rather than checked.
            // Direction is a CHOSEN BASIS, not physics: neutron_shield.fraction_volume is taken as
            // the free term and gamma derived as the remainder. The reverse basis is equally valid.
            // Authority: owner-disposition.md Group A, A7 (derive-instead); basis ruled there.
            // Model debt (O3): the closure covers 2 of the 4 shield layers — thermal_shield and
            // biological_shield carry no fraction_volume. Recorded in PROVENANCE §4, not embedded.
            attribute fraction_volume : Real = 1.0 - neutron_shield.fraction_volume;
            attribute density : Real = 9400 [kg/m^3];
        }

        // Thermal Shield (part of shielding system)
        part thermal_shield {
            doc /*
            Thermal radiation shield - protects cryogenic components.

            **Material**: Aluminum or multi-layer insulation (MLI)
            **Function**:
            - Reduce radiative heat load to superconducting magnets
            - Operating at intermediate temperature (~80 K)
            - Intercepts thermal radiation from warm (300 K) components

            **Heat Load Reduction**: ~50x with proper MLI design

            **Note**: This is distinct from radial build lt_shield layer.
            Thermal shielding is distributed throughout cryogenic system.

            **Last Updated**: 2025-11-01
            */

            attribute material : String = "Aluminum";
            attribute thickness : Real = 0.005 [m];  // Thin, MLI-based
            attribute temperature_operating : Real = 80 [K];
        }

        // Biological Shield (final barrier)
        part biological_shield {
            doc /*
            Outer biological shield - personnel protection.

            **Material**: Concrete (high-density, possibly borated)
            - Density: 2400 kg/m³ (standard concrete)
            - Or 3500-4000 kg/m³ (magnetite or barite aggregate)
            - May include boron admixture for enhanced neutron capture

            **Function**:
            - Final barrier for neutron and gamma radiation
            - Structural support for reactor building
            - Massive thickness (1.0 m) for personnel safety

            **Requirement**: Dose rate <2.5 µSv/hr at outer surface
            (IAEA Basic Safety Standards for unrestricted access)

            **Source**: From radial build line 86 (bioshield_t = 1.0 m)
            **Last Updated**: 2025-11-01
            */

            attribute material : String = "Concrete";
            attribute thickness : Real = 1.0 [m];  // From radial build
            attribute density : Real = 2400 [kg/m^3];
            attribute dose_rate_limit : Real = 2.5e-6;  // Sv/hr at outer surface
        }

        // Overall Shield Properties
        attribute thickness_total : Real = 0.4 [m];  // HT shield + structure layers
        attribute mass_total : Real = 500000 [kg];  // TO BE CALCULATED

        // Radiation Performance (TO BE CALCULATED with neutronics codes)
        attribute neutron_attenuation_total : Real = 1.0e5;  // Total flux reduction
        attribute gamma_attenuation_total : Real = 1.0e3;   // Total dose reduction
        attribute dose_rate_at_magnets : Real = 1.0e-4;     // Sv/hr, placeholder

        // Material fractions from PyFECONS (lines 89-94)
        attribute f_SiC : Real = 0.0;   // No silicon carbide
        attribute f_W : Real = 0.0;     // No tungsten
        attribute f_BFS : Real = 0.9;   // 90% borated ferritic steel
        attribute f_PbLi : Real = 0.1;  // 10% lead-lithium
    }
}
