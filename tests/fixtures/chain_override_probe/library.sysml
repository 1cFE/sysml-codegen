package ChainOverrideLibrary {
    private import ScalarValues::Real;

    // Simple CalcDef for the sensor cost model
    calc def SensorCostCalc {
        in attribute sensitivity : Real;
        in attribute base_cost : Real;

        out attribute total_cost : Real = base_cost * sensitivity;
    }

    // CalcDef that produces a calibration output used for CHAIN override
    calc def CalibrationCalc {
        in attribute raw_factor : Real;

        out attribute calibrated_factor : Real = raw_factor * 1.1;
    }

    // Leaf PartDef with an embedded template CalcUsage
    part def 'Sensor' {
        // Design parameters (set via :>> in design)
        attribute sensitivity : Real;
        attribute base_cost : Real;

        // Template CalcUsage — bindings will be overridden by design
        calc cost_model : SensorCostCalc {
            in sensitivity = sensitivity;
            in base_cost = base_cost;
        }
    }

    // Assembly PartDef containing a Sensor child + a CalcUsage
    part def 'Instrument Package' {
        part sensor : 'Sensor';

        // This CalcUsage produces an output the design can use for CHAIN override
        calc calibration : CalibrationCalc {
            in raw_factor = 1.0;
        }
    }
}
