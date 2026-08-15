/*
 * CATF MFE Blanket Design Instance
 *
 * This file defines the specific breeding blanket configuration for the
 * Clean Air Task Force MFE reference design.
 *
 * Parameters extracted from PyFECONS DefineInputs.py lines 44-51.
 */

package CATFMFEBlanket {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // Import thermal load calc def
    private import FusionAnalysesThermalLoads::CoolantPumpPower;

    /*
     * CATF MFE Breeding Blanket Instance
     */
    part catf_blanket {
        doc /*
        CATF MFE breeding blanket - solid breeder with dual coolant system.

        **Source**: PyFECONS DefineInputs.py lines 44-51
        **Reference**: /home/reid/apps/PyFECONS/customers/CATF/mfe/DefineInputs.py
        **Configuration**: Solid first wall with solid breeder (Li2TiO3)

        **Key Features**:
        - Beryllium first wall armor
        - Li2TiO3 ceramic breeder (lithium titanate)
        - Be12Ti neutron multiplier
        - FMS (Ferritic-Martensitic Steel) structure
        - Dual coolant: Li primary, PbLi secondary

        **Target Performance**:
        - TBR ≥ 1.05 for tritium self-sufficiency
        - Energy multiplication M ≈ 1.15-1.3
        - Breeding zone enrichment: 30-90% Li-6 (TBD)

        **Design Philosophy**:
        Solid breeder chosen for:
        - Better tritium extraction than liquid
        - Higher temperature capability
        - Reduced corrosion vs liquid metals
        - Proven in DEMO/ARIES studies

        **Last Updated**: 2025-11-01
        */

        // Breeding Zone Configuration
        part breeding_zone {
            doc /*
            Lithium ceramic breeding zone - primary tritium production region.

            **Breeder Material**: Li2TiO3 (lithium titanate)
            - Chemical formula: Li₂TiO₃
            - Density: 3430 kg/m³
            - Li content: 14% by mass
            - Ceramic pebbles or solid blocks

            **Breeding Reactions**:
            - Li-6 + n → T + He-4 + 4.8 MeV (primary, σ large)
            - Li-7 + n → T + He-4 + n - 2.5 MeV (secondary, requires E>2.5 MeV)

            **Source**: PyFECONS line 46 (BlanketType.SOLID_FIRST_WALL_WITH_A_SOLID_BREEDER_LI2TIO3)
            **Last Updated**: 2025-11-01
            */

            attribute breeder_material : String = "Li2TiO3";
            attribute enrichment_li6 : Real = 0.30;  // 30% Li-6 (natural ~7.5%, needs enrichment)
            attribute thickness_radial : Real = 0.4 [m];  // Estimated from 0.8m total blanket
            attribute volume : Real = 50.0;  // m^3, TO BE CALCULATED from geometry
            attribute temperature_operating : Real = 600 [K];  // ~327°C, typical for ceramic breeders
        }

        // Neutron Multiplier Zone
        part multiplier_zone {
            doc /*
            Neutron multiplier region - increases neutron availability for breeding.

            **Multiplier Material**: Be12Ti (beryllium titanium intermetallic)
            - Density: 2280 kg/m³
            - (n,2n) cross-section favorable
            - Better than pure Be for high-temperature operation
            - Reduced swelling vs pure beryllium

            **Function**: Be-9 + n → 2n + 2α (threshold ~2.7 MeV)
            Each high-energy neutron produces 2 neutrons, increasing TBR

            **Expected Multiplication**: M ≈ 1.2-1.3

            **Source**: PyFECONS line 49 (BlanketNeutronMultiplier.BE12TI)
            **Last Updated**: 2025-11-01
            */

            attribute multiplier_material : String = "Be12Ti";
            attribute thickness_radial : Real = 0.15 [m];  // Estimated
            attribute volume : Real = 20.0;  // m^3, TO BE CALCULATED
            attribute temperature_operating : Real = 600 [K];
        }

        // Structural Backing
        part structural_backing {
            doc /*
            Structural support and containment for breeder and multiplier.

            **Structure Material**: FMS (Ferritic-Martensitic Steel)
            - Examples: EUROFER97, F82H, 9Cr-1MoVNb
            - Density: ~7800 kg/m³
            - Max operating temp: ~550°C
            - Low activation under neutron irradiation
            - Better swelling resistance than austenitic steels

            **Function**:
            - Contain breeder pebbles/blocks
            - Structural support under pressure
            - Coolant channels
            - Neutron shielding (iron attenuates neutrons)

            **Source**: PyFECONS line 50 (BlanketStructure.FERRITIC_MARTENSITIC_STEEL_FMS)
            **Last Updated**: 2025-11-01
            */

            attribute structure_material : String = "FerriticMartensiticSteel";
            attribute thickness : Real = 0.15 [m];  // Estimated
            attribute temperature_max : Real = 823;  // K (550 C), Material limit
        }

        // First Wall Interface
        part first_wall_interface {
            doc /*
            First wall armor interfacing with plasma.

            **Armor Material**: Beryllium
            - Density: 1850 kg/m³
            - Melting point: 1287°C
            - Low-Z (prevents plasma contamination)
            - Good thermal conductivity: 200 W/(m·K)
            - Used on ITER first wall

            **Function**:
            - Withstand particle bombardment
            - Handle heat flux from plasma
            - Protect structural materials
            - Minimize plasma impurity generation

            **Heat Flux Capability**: ~5-10 MW/m² steady-state

            **Source**: PyFECONS line 45 (BlanketFirstWall.BERYLLIUM)
            **Last Updated**: 2025-11-01
            */

            attribute armor_material : String = "Beryllium";
            attribute thickness : Real = 0.1 [m];  // Part of 0.2m first wall layer from radial build
            attribute heat_flux_limit : Real = 10.0e6;  // W/m^2 (10 MW/m^2), Steady-state limit
        }

        // Coolant System Configuration
        attribute coolant_primary : String = "LiquidLithium";  // From PyFECONS line 47
        attribute coolant_secondary : String = "LeadLithium";  // From PyFECONS line 48

        doc /*
        **Dual Coolant Rationale**:

        **Primary Coolant - Liquid Lithium (Li)**:
        - Also contributes to tritium breeding
        - Excellent heat transfer (high thermal conductivity)
        - Low activation
        - MHD challenges in magnetic field
        - Temperature range: 180-600°C

        **Secondary Coolant - Lead-Lithium (PbLi)**:
        - Eutectic: 83% Pb, 17% Li by atomic fraction
        - Higher density (9400 kg/m³) → better shielding
        - Additional breeding contribution
        - Reduces MHD pressure drop vs pure Li
        - Temperature range: 235-550°C

        **Heat Extraction Path**:
        Plasma → First wall → Li coolant → Heat exchanger →
        → Secondary loop (PbLi or H2O) → Steam cycle → Turbine
        */

        // Coverage and Geometry
        attribute coverage_fraction_toroidal : Real = 0.85;  // Estimated (allows for ports)
        attribute coverage_fraction_poloidal : Real = 0.80;  // Estimated (divertor cutouts)

        attribute blanket_thickness_total : Real = 0.8 [m];  // From radial build line 77

        // Performance Metrics (TO BE CALCULATED in physics epic)
        attribute breeding_ratio : Real = 1.10;  // Target TBR, placeholder
        attribute energy_multiplication : Real = 1.20;  // Target M, placeholder
        attribute power_thermal : Real = 2000.0e6;  // W (2000 MW), Placeholder, depends on P_fusion

        // Mass Estimates (TO BE CALCULATED from volumes and densities)
        attribute mass_breeder : Real = 100000 [kg];  // Placeholder
        attribute mass_multiplier : Real = 40000 [kg];  // Placeholder
        attribute mass_structure : Real = 80000 [kg];  // Placeholder
        attribute mass_total : Real = 220000 [kg];  // Placeholder

        // Coolant pump power calculation
        calc pump_load : CoolantPumpPower {
            in p_thermal_electric = 1104.22;  // MW - Temporary, will be cross-reference in Phase 5
            // f_pcppf defaults to 0.06
            // pump_efficiency defaults to 0.5
        }

        attribute pump_power : Real = pump_load.pump_power;  // EXPOSE for physics.sysml
    }
}
