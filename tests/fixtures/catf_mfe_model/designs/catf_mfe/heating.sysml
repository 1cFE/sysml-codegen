/*
 * CATF MFE Heating System Design Instance
 *
 * Auxiliary plasma heating system for CATF MFE design.
 * Uses Neutral Beam Injection (NBI) to deliver 50 MW to plasma.
 */
package CATFMFEHeating {
    public import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    private import FusionAnalysesThermalLoads::HeatingWallPlugPower;

    part catf_heating {
        doc /*
        CATF MFE auxiliary heating system - NBI configuration.

        **Source**: PyFECONS inputs.json lines 35-39
        **System**: Neutral Beam Injection (NBI)
        **Delivered Power**: 50 MW to plasma
        **Efficiency**: 50% (η_pin)
        **Wall-Plug Power**: 100 MW

        **Last Updated**: 2025-11-09
        */

        attribute delivered_power : Real = 50.0;  // MW - Power to plasma
        attribute system_type : String = "NBI";

        calc wall_plug : HeatingWallPlugPower {
            in delivered_power = catf_heating::delivered_power;
            // heating_efficiency defaults to 0.5 in calc def
        }

        attribute wall_plug_power : Real = wall_plug.wall_plug_power;  // EXPOSE
    }
}
