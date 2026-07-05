package ChainOverrideDesign {
    private import ScalarValues::Real;
    private import ChainOverrideLibrary::*;

    part instrument_design : 'Instrument Package' {

        // Entry-point attribute
        attribute sensor_base_cost : Real = 100.0;

        // =============================================
        // CHAIN DESIGN OVERRIDES on the sensor PartUsage
        // =============================================

        part redefines sensor : 'Sensor' {
            // LITERAL override (baseline — same as solar_battery pattern)
            :>> base_cost = 100.0;

            // CHAIN override — redirect sensitivity to calibration calc output
            // This is a FeatureChainExpression: calibration.calibrated_factor
            // Produces RedefinitionType.CHAIN in design_overrides
            :>> sensitivity = calibration.calibrated_factor;
        }
    }
}
