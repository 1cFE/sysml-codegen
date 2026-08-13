package FusionMaterials {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    /*
     * Material Library for Fusion Reactor Components
     *
     * This library defines material properties for structural materials,
     * superconductors, breeding materials, armor materials, shielding materials,
     * and coolants used in fusion reactor design and cost estimation.
     *
     * All costs are in 2013 USD unless otherwise noted.
     */

    // ========================================================================
    // STRUCTURAL MATERIALS
    // ========================================================================

    attribute def SS316 {
        doc /*
        Stainless Steel 316 - austenitic stainless steel

        Primary structural material for fusion reactors due to excellent
        corrosion resistance, weldability, and moderate neutron activation.

        **Source**: ASME Boiler & Pressure Vessel Code Section II Part D
        **Properties**: ASM Metals Handbook Vol. 1
        **Cost**: Waganer ARIES Cost Report (2013)
        **Reference**: data/documents/aries_cost_database_2013.pdf
        **Temperature Limits**: For non-irradiated, annealed condition
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 8000.0;  // kg/m³
        attribute cost_per_kg : Real = 7.5;  // USD/kg (2013)
        attribute temperature_max : Real = 550.0;  // °C
        attribute thermal_conductivity : Real = 16.3;  // W/(m·K) at 100°C
        attribute yield_strength : Real = 290.0;  // MPa at room temperature
        attribute elastic_modulus : Real = 193.0;  // GPa at room temperature
    }

    attribute def SS316LN {
        doc /*
        Stainless Steel 316LN - Low Nitrogen variant

        Enhanced variant with controlled nitrogen content for improved
        strength and reduced irradiation-induced swelling. Preferred
        for high-neutron-flux environments.

        **Source**: ASME Boiler & Pressure Vessel Code Section II
        **Reference**: ITER Structural Design Criteria (2001)
        **Cost**: Waganer ARIES Cost Report (2013) with 13% premium
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 8000.0;  // kg/m³
        attribute cost_per_kg : Real = 8.5;  // USD/kg (2013)
        attribute temperature_max : Real = 550.0;  // °C
        attribute thermal_conductivity : Real = 16.3;  // W/(m·K)
        attribute yield_strength : Real = 310.0;  // MPa (slightly higher than 316)
        attribute elastic_modulus : Real = 193.0;  // GPa
    }

    attribute def SS304 {
        doc /*
        Stainless Steel 304 - austenitic stainless steel

        Standard austenitic stainless for non-nuclear applications.
        Lower nickel content than 316, slightly lower corrosion resistance.

        **Source**: ASME Boiler & Pressure Vessel Code Section II
        **Properties**: ASM Metals Handbook Vol. 1
        **Cost**: Waganer ARIES Cost Report (2013)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 8000.0;  // kg/m³
        attribute cost_per_kg : Real = 6.5;  // USD/kg (2013)
        attribute temperature_max : Real = 550.0;  // °C
        attribute thermal_conductivity : Real = 16.2;  // W/(m·K)
        attribute yield_strength : Real = 275.0;  // MPa
        attribute elastic_modulus : Real = 193.0;  // GPa
    }

    attribute def FerriticMartensiticSteel {
        doc /*
        Ferritic-Martensitic Steel (F82H, EUROFER, etc.)

        Advanced reduced-activation ferritic-martensitic steel for
        breeding blanket structures. Lower swelling and better thermal
        properties than austenitic steels in high-neutron environments.

        **Source**: DEMO blanket design studies
        **Reference**: Fusion Engineering and Design 89 (2014) 1586-1590
        **Cost**: Waganer ARIES Cost Report (2013) estimate
        **Assumption**: Cost premium reflects advanced manufacturing
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 7800.0;  // kg/m³
        attribute cost_per_kg : Real = 12.0;  // USD/kg (2013) - ASSUMPTION
        attribute temperature_max : Real = 550.0;  // °C
        attribute thermal_conductivity : Real = 32.0;  // W/(m·K) - much better than SS
        attribute yield_strength : Real = 550.0;  // MPa
        attribute elastic_modulus : Real = 200.0;  // GPa
    }

    // ========================================================================
    // SUPERCONDUCTORS
    // ========================================================================

    attribute def HTS_REBCO {
        doc /*
        High-Temperature Superconductor - REBCO tape (REBa₂Cu₃O₇)

        Second-generation HTS tape conductor (RE = Rare Earth: Y, Gd, etc.).
        Used in high-field magnets for compact fusion designs. Critical for
        >20T fields at 20K operating temperature.

        **Source**: Commonwealth Fusion Systems SPARC design
        **Reference**: SuperPower Inc. 2G HTS wire specification (2020)
        **Cost**: Industry quotes for large-volume orders (2020-2023)
        **Performance**: At 12T, 20K operating point
        **Assumption**: Cost per kA·m based on 400 A/mm² at operating point
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 6300.0;  // kg/m³ (effective, including substrate)
        attribute cost_per_kA_m : Real = 100.0;  // USD/(kA·m) - ASSUMPTION, high uncertainty
        attribute critical_temperature : Real = 93.0;  // K (for YBCO)
        attribute critical_field_20K : Real = 30.0;  // T
        attribute critical_current_density_operating : Real = 400.0;  // A/mm² at 12T, 20K
        attribute thermal_conductivity : Real = 10.0;  // W/(m·K) - tape composite
    }

    attribute def HTS_CICC {
        doc /*
        High-Temperature Superconductor - Cable-In-Conduit Conductor

        REBCO tapes formed into cable-in-conduit conductor (CICC) configuration
        for large magnet systems. Includes structural jacket, insulation, and
        cryogen cooling channel. Effective properties of full conductor assembly.

        **Source**: Commonwealth Fusion Systems / MIT PSFC
        **Reference**: Sorbom et al., Fusion Engineering and Design 100 (2015)
        **Cost**: Estimate based on tape cost + fabrication + jacket
        **Assumption**: 30% tape packing fraction, SS316 jacket
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 7000.0;  // kg/m³ (effective: tape + jacket + void)
        attribute cost_per_kg : Real = 150.0;  // USD/kg - ASSUMPTION
        attribute critical_temperature : Real = 93.0;  // K
        attribute critical_field_20K : Real = 30.0;  // T
        attribute thermal_conductivity : Real = 50.0;  // W/(m·K) - composite with jacket
    }

    attribute def LTS_Nb3Sn {
        doc /*
        Low-Temperature Superconductor - Niobium-3-Tin

        High-performance LTS for ITER TF coils. Higher critical field and
        current density than NbTi, but brittle and requires careful handling.
        Operating temperature 4-5K.

        **Source**: ITER TF coil design
        **Reference**: Mitchell et al., Superconductor Science and Technology 18 (2005)
        **Cost**: Waganer ARIES Cost Report (2013)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 8900.0;  // kg/m³
        attribute cost_per_kg : Real = 80.0;  // USD/kg (2013)
        attribute critical_temperature : Real = 18.0;  // K
        attribute critical_field_4K : Real = 23.0;  // T
        attribute thermal_conductivity : Real = 5.0;  // W/(m·K) at 4K
    }

    attribute def LTS_NbTi {
        doc /*
        Low-Temperature Superconductor - Niobium-Titanium

        Workhorse LTS for moderate fields (<9T). Ductile, easier to fabricate
        than Nb3Sn. Used in many accelerator and some fusion magnets.

        **Source**: Standard superconductor properties
        **Reference**: Wilson, Superconducting Magnets (1983)
        **Cost**: Waganer ARIES Cost Report (2013)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 6100.0;  // kg/m³
        attribute cost_per_kg : Real = 50.0;  // USD/kg (2013)
        attribute critical_temperature : Real = 9.8;  // K
        attribute critical_field_4K : Real = 11.0;  // T
        attribute thermal_conductivity : Real = 8.0;  // W/(m·K) at 4K
    }

    attribute def Copper {
        doc /*
        Copper - for resistive magnets and stabilizer in superconducting magnets

        High-purity copper (OFHC - Oxygen-Free High Conductivity) used as
        stabilizer in superconducting magnets and for resistive PF coils.

        **Source**: Materials properties handbooks
        **Reference**: CRC Handbook of Chemistry and Physics
        **Cost**: Commodity price 2013 (London Metal Exchange average)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 8960.0;  // kg/m³
        attribute cost_per_kg : Real = 10.0;  // USD/kg (2013)
        attribute electrical_resistivity : Real = 1.68e-8;  // Ω·m at 20°C
        attribute thermal_conductivity : Real = 401.0;  // W/(m·K) at 20°C
        attribute melting_point : Real = 1085.0;  // °C
    }

    // ========================================================================
    // BREEDING MATERIALS
    // ========================================================================

    attribute def Li2TiO3 {
        doc /*
        Lithium Titanate (Li₂TiO₃) - ceramic breeder

        Leading solid breeder candidate for DEMO. Good tritium release
        kinetics at 300-900°C, chemical stability, compatibility with
        structural materials.

        **Source**: DEMO blanket design studies
        **Reference**: Federici et al., Fusion Engineering and Design 89 (2014) 882-889
        **Cost**: Estimate based on enrichment requirements - ASSUMPTION
        **Lithium Content**: 14% by mass
        **Assumption**: Cost highly dependent on Li-6 enrichment level
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 3430.0;  // kg/m³ (theoretical density ~85% achieved)
        attribute cost_per_kg : Real = 100.0;  // USD/kg - ASSUMPTION, enrichment-dependent
        attribute lithium_content : Real = 0.14;  // mass fraction
        attribute temperature_max : Real = 900.0;  // °C
        attribute thermal_conductivity : Real = 2.0;  // W/(m·K) - relatively low
        attribute melting_point : Real = 1430.0;  // °C
    }

    attribute def Li4SiO4 {
        doc /*
        Lithium Orthosilicate (Li₄SiO₄) - ceramic breeder

        Alternative solid breeder with higher lithium content than Li2TiO3.
        Good tritium release but lower thermal conductivity.

        **Source**: DEMO blanket studies
        **Reference**: Konys et al., Fusion Engineering and Design 81 (2006)
        **Cost**: Estimate - ASSUMPTION
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 2400.0;  // kg/m³
        attribute cost_per_kg : Real = 90.0;  // USD/kg - ASSUMPTION
        attribute lithium_content : Real = 0.23;  // mass fraction (higher than Li2TiO3)
        attribute temperature_max : Real = 900.0;  // °C
        attribute thermal_conductivity : Real = 1.5;  // W/(m·K)
        attribute melting_point : Real = 1255.0;  // °C
    }

    attribute def Be12Ti {
        doc /*
        Beryllium-12-Titanium (Be₁₂Ti) - neutron multiplier

        Advanced beryllide for neutron multiplication in breeding blankets.
        Higher temperature capability than pure Be, better compatibility
        with coolants.

        **Source**: DEMO blanket studies
        **Reference**: Chakin et al., Journal of Nuclear Materials 307-311 (2002)
        **Cost**: Estimate based on Be market price + processing - ASSUMPTION
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 2280.0;  // kg/m³
        attribute cost_per_kg : Real = 150.0;  // USD/kg - ASSUMPTION
        attribute temperature_max : Real = 650.0;  // °C
        attribute thermal_conductivity : Real = 40.0;  // W/(m·K)
        attribute melting_point : Real = 1480.0;  // °C
    }

    attribute def LiquidLithium {
        doc /*
        Liquid Lithium - self-cooled liquid breeder

        Pure liquid lithium for self-cooled lithium blanket (SCLB) concepts.
        Excellent breeding ratio, but challenging MHD and compatibility issues.

        **Source**: EVOLVE liquid lithium blanket concept
        **Reference**: Smolentsev et al., Fusion Engineering and Design 100 (2015)
        **Cost**: Industrial lithium price (2013)
        **Properties**: At 200°C operating temperature
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 512.0;  // kg/m³ at 200°C
        attribute cost_per_kg : Real = 80.0;  // USD/kg (2013)
        attribute lithium_content : Real = 1.0;  // Pure lithium
        attribute melting_point : Real = 180.5;  // °C
        attribute thermal_conductivity : Real = 42.0;  // W/(m·K) at 200°C
        attribute electrical_conductivity : Real = 3.0e6;  // S/m (important for MHD)
    }

    attribute def LeadLithium {
        doc /*
        Lead-Lithium Eutectic (Pb-17Li) - liquid breeder/coolant

        Eutectic alloy (83% Pb, 17% Li by atom) for dual-coolant lead-lithium
        (DCLL) blanket concepts. Self-cooling and breeding.

        **Source**: DCLL blanket for DEMO/ARIES
        **Reference**: Malang & Mattas, Fusion Technology 27 (1995)
        **Cost**: Weighted average of Pb and Li costs
        **Properties**: At 400°C operating temperature
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 9400.0;  // kg/m³ at 400°C
        attribute cost_per_kg : Real = 20.0;  // USD/kg (2013) - weighted Pb+Li
        attribute lithium_content : Real = 0.08;  // mass fraction (17% atomic is ~8% by mass)
        attribute melting_point : Real = 235.0;  // °C
        attribute thermal_conductivity : Real = 15.0;  // W/(m·K) at 400°C
        attribute electrical_conductivity : Real = 7.0e5;  // S/m
    }

    // ========================================================================
    // ARMOR MATERIALS
    // ========================================================================

    attribute def Tungsten {
        doc /*
        Tungsten (W) - plasma-facing armor

        Primary armor material for divertor and first wall in high-heat-flux
        regions. Highest melting point of any metal, low sputtering yield,
        but brittle at low temperatures.

        **Source**: ITER Materials Assessment Report
        **Reference**: Rieth et al., Journal of Nuclear Materials 432 (2013) 482-500
        **Cost**: Industrial tungsten price (2013) + fabrication premium
        **Heat Flux**: Steady-state capability
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 19250.0;  // kg/m³
        attribute cost_per_kg : Real = 100.0;  // USD/kg (2013)
        attribute melting_point : Real = 3422.0;  // °C
        attribute heat_flux_limit : Real = 10.0;  // MW/m² steady-state
        attribute thermal_conductivity : Real = 173.0;  // W/(m·K) at 20°C
        attribute thermal_expansion : Real = 4.5e-6;  // 1/K
        attribute ductile_brittle_transition : Real = 400.0;  // °C (material-dependent)
    }

    attribute def Beryllium {
        doc /*
        Beryllium (Be) - first wall armor and neutron multiplier

        ITER first wall armor material. Low atomic number reduces plasma
        contamination, good thermal properties, neutron multiplier.
        Toxic - requires careful handling.

        **Source**: ITER first wall design
        **Reference**: Barabash, Physica Scripta T128 (2007) 50-56
        **Cost**: High due to toxicity, processing requirements
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 1850.0;  // kg/m³
        attribute cost_per_kg : Real = 600.0;  // USD/kg (2013) - expensive, toxicity premium
        attribute melting_point : Real = 1287.0;  // °C
        attribute thermal_conductivity : Real = 200.0;  // W/(m·K) at 20°C
        attribute heat_flux_limit : Real = 5.0;  // MW/m² (lower than W)
        attribute thermal_expansion : Real = 11.3e-6;  // 1/K
    }

    attribute def CarbonFiberComposite {
        doc /*
        Carbon Fiber Composite (CFC) - plasma-facing armor

        Carbon-carbon composite for high-heat-flux regions. Used in older
        tokamaks (JET, DIII-D), being replaced by tungsten due to tritium
        retention concerns.

        **Source**: JET first wall experience
        **Reference**: Matthews et al., Journal of Nuclear Materials 390-391 (2009)
        **Cost**: Estimate based on aerospace CFC
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 1800.0;  // kg/m³ (typical for CFC)
        attribute cost_per_kg : Real = 200.0;  // USD/kg - ASSUMPTION
        attribute temperature_max : Real = 2000.0;  // °C (sublimation ~3600°C but structural limit)
        attribute thermal_conductivity : Real = 80.0;  // W/(m·K) parallel to fibers
        attribute heat_flux_limit : Real = 15.0;  // MW/m² (good heat handling)
    }

    // ========================================================================
    // SHIELDING MATERIALS
    // ========================================================================

    attribute def BoratedSteel {
        doc /*
        Borated Steel - neutron shield

        Steel with added boron for enhanced neutron absorption. Used in
        shield regions to reduce neutron fluence to magnets and external
        components.

        **Source**: ITER shield design
        **Reference**: Ioki et al., Fusion Engineering and Design 55 (2001)
        **Cost**: SS316 base + boron addition premium
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 7850.0;  // kg/m³
        attribute cost_per_kg : Real = 15.0;  // USD/kg (2013) - premium over SS316
        attribute boron_content : Real = 0.02;  // 2% by weight (typical)
        attribute thermal_conductivity : Real = 15.0;  // W/(m·K)
        attribute temperature_max : Real = 550.0;  // °C
    }

    attribute def TungstenCarbide {
        doc /*
        Tungsten Carbide (WC) - high-density shield

        High-density material for gamma shielding and neutron moderation.
        Very hard, wear-resistant, but expensive.

        **Source**: General shielding applications
        **Reference**: Radiation shielding handbooks
        **Cost**: Industrial WC price
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 15630.0;  // kg/m³
        attribute cost_per_kg : Real = 50.0;  // USD/kg (2013)
        attribute thermal_conductivity : Real = 110.0;  // W/(m·K)
        attribute melting_point : Real = 2870.0;  // °C
    }

    attribute def Lead {
        doc /*
        Lead (Pb) - gamma shield

        Dense material for gamma ray attenuation. Sometimes used as
        component in multilayer shields or as constituent in PbLi.

        **Source**: Standard radiation shielding
        **Reference**: NCRP Report 144 (2003)
        **Cost**: Commodity lead price (2013)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 11340.0;  // kg/m³
        attribute cost_per_kg : Real = 2.5;  // USD/kg (2013)
        attribute melting_point : Real = 327.5;  // °C
        attribute thermal_conductivity : Real = 35.0;  // W/(m·K)
    }

    attribute def Concrete {
        doc /*
        Concrete - biological shield

        Standard concrete for biological shielding. Outer shield layer
        for neutron and gamma attenuation to protect personnel.

        **Source**: Standard construction materials
        **Reference**: NCRP Report 144 (2003)
        **Cost**: Construction concrete price (2013)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 2400.0;  // kg/m³ (standard concrete)
        attribute cost_per_kg : Real = 0.1;  // USD/kg (2013) - very cheap
        attribute thermal_conductivity : Real = 1.4;  // W/(m·K)
        attribute compressive_strength : Real = 30.0;  // MPa (typical)
    }

    // ========================================================================
    // COOLANTS
    // ========================================================================

    attribute def PressurizedWater {
        doc /*
        Pressurized Water - primary coolant

        Standard pressurized water coolant for breeding blankets and
        first wall. Operates at 15-17 MPa, 285-325°C.

        **Source**: PWR technology
        **Reference**: Todreas & Kazimi, Nuclear Systems Vol. I (2012)
        **Properties**: At 300°C, 15 MPa
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 1000.0;  // kg/m³ (approximate at operating conditions)
        attribute specific_heat : Real = 4186.0;  // J/(kg·K)
        attribute thermal_conductivity : Real = 0.6;  // W/(m·K) at 300°C
        attribute dynamic_viscosity : Real = 1.0e-4;  // Pa·s at 300°C
        attribute operating_pressure : Real = 15.0;  // MPa
        attribute operating_temperature : Real = 300.0;  // °C
    }

    attribute def Helium {
        doc /*
        Helium (He) - inert gas coolant

        High-pressure helium coolant for high-temperature blankets.
        Chemically inert, no activation, but requires high pressure
        (8-10 MPa) for adequate heat removal.

        **Source**: Gas-cooled reactor technology
        **Reference**: Forsberg et al., Progress in Nuclear Energy 47 (2005)
        **Properties**: At operating conditions (8 MPa, 400°C)
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 0.179;  // kg/m³ at STP (much higher at operating pressure)
        attribute density_operating : Real = 3.5;  // kg/m³ at 8 MPa, 400°C
        attribute specific_heat : Real = 5193.0;  // J/(kg·K) (constant for ideal gas)
        attribute thermal_conductivity : Real = 0.23;  // W/(m·K) at 400°C
        attribute operating_pressure : Real = 8.0;  // MPa
        attribute operating_temperature : Real = 400.0;  // °C
    }

    attribute def LiquidMetal {
        doc /*
        Liquid Metal Coolant (generic) - NaK, Pb-Bi, or other

        Generic liquid metal coolant properties. Specific implementations
        might use sodium-potassium (NaK), lead-bismuth eutectic, or others.
        Excellent heat transfer but compatibility and activation concerns.

        **Source**: Advanced reactor coolant studies
        **Reference**: Hejzlar et al., Nuclear Engineering and Design 239 (2009)
        **Properties**: Representative values for NaK-78
        **Assumption**: Generic properties - specific coolant should be defined for detailed design
        **Last Updated**: 2025-11-01
        */

        attribute density : Real = 850.0;  // kg/m³ (NaK-78 at 300°C)
        attribute specific_heat : Real = 1000.0;  // J/(kg·K)
        attribute thermal_conductivity : Real = 25.0;  // W/(m·K) (excellent)
        attribute electrical_conductivity : Real = 3.0e6;  // S/m (MHD considerations)
        attribute operating_temperature : Real = 400.0;  // °C
    }
}
