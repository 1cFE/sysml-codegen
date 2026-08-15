package UnitLaneComputedDisagreement {
    private import ScalarValues::*;

    calc def MetreConsumer {
        in attribute value : Real;  // m
        out attribute result : Real = value;  // m
    }

    part disagreement {
        attribute shared_length : Real = 100.0;  // cm
        attribute doubled : Real = shared_length * 2.0;  // cm
        calc length_calc : MetreConsumer {
            in value = shared_length;
        }
    }
}
