package UnitLaneConstraintDisagreement {
    private import ScalarValues::*;

    calc def LengthConsumer {
        in attribute value : Real;  // m
        out attribute result : Real = value;  // m
    }

    constraint def CentimetreGuard {
        in observed : Real;  // cm
        observed > 0.0
    }

    part disagreement {
        attribute shared_length : Real = 1.0;  // m
        calc length_calc : LengthConsumer {
            in value = shared_length;
        }
        assert constraint length_guard : CentimetreGuard {
            in observed = shared_length;
        }
    }
}
