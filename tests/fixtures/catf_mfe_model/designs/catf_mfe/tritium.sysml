/*
 * CATF MFE Tritium Processing System Design Instance
 */
package CATFMFETritium {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    private import FusionAnalysesThermalLoads::TritiumProcessingPower;

    part catf_tritium {
        doc /*
        CATF MFE tritium fuel cycle processing system.

        **Functions**:
        - Isotope separation (D, T, He)
        - Tritium extraction from blanket
        - Purification and storage
        - Fuel delivery to plasma

        **Source**: PyFECONS inputs.json line 29
        **Last Updated**: 2025-11-09
        */

        attribute fusion_power : Real = 2600.0;  // MW - From physics

        calc processing_load : TritiumProcessingPower {
            in fusion_power = catf_tritium::fusion_power;
            // processing_factor defaults to 0.00385 in calc def (tuned for 10 MW at 2600 MW fusion)
        }

        attribute processing_power : Real = processing_load.processing_power;  // EXPOSE
    }
}
