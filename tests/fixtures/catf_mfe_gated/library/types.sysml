package FusionTypes {
    doc /*
    Custom type definitions for fusion modeling.
    Defines material types and other domain-specific attributes not in standard libraries.
    */

    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // Material type definition
    attribute def Material {
        doc /*
        Material specification with physical and cost properties.
        Base type for all material definitions in the fusion model.
        */

        attribute density : Real {
            doc /* Material density [kg/m³] */
        }

        attribute cost_per_kg : Real {
            doc /* Material cost per kilogram [USD/kg] in 2013 dollars */
        }

        attribute temperature_max : Real {
            doc /* Maximum operating temperature [°C or K] */
        }

        attribute thermal_conductivity : Real {
            doc /* Thermal conductivity [W/(m·K)] */
        }
    }

    // Magnet material type enumeration
    enum def MagnetMaterialType {
        HTS_REBCO;
        HTS_CICC;
        HTS_PANCAKE;
        LTS_Nb3Sn;
        LTS_NbTi;
        COPPER;
    }
}
