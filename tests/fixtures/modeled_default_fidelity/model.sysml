package ModeledDefaultFidelity {
    private import ScalarValues::*;
    public import ISQ::*;
    public import SI::*;

    // =====================================================================
    // Signed and unit-annotated modeled defaults (Item 4, DD-R20 / DD-A11).
    //
    // Both shapes below reached the MODELED_DEFAULT formal as a `None` value
    // before Item 4: `:= -0.1` parses as an OperatorNode over a literal and
    // `= 40.0 [W]` as a UnitAnnotationNode, and the default lane only
    // understood a bare LiteralNode. The generated JSON then omitted the key
    // entirely, so a value the model states became one the user must re-supply.
    //
    // `unsupported_default` pins the other half of the contract (DD-R21): an
    // unsupported default IR must stay explicitly unresolved and diagnosed,
    // never silently omitted and never invented.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 4)
    // **Reference**: spec.md DD-R20, DD-R21, DD-R25; design.md Phase 3
    // =====================================================================

    constraint def 'Drift Bound' {
        in attribute reading : Real;
        in attribute drift : Real default -0.1;

        reading >= drift
    }

    constraint def 'Power Floor' {
        in attribute delivered : Real;
        in attribute rated_power : Real default 40.0 [W];

        delivered >= rated_power
    }

    constraint def 'Derived Bound' {
        // A binary operator is not an explicitly modeled scalar default: it is
        // the unsupported-IR case, and must stay explicitly unresolved.
        in attribute observed : Real;
        in attribute limit : Real default 2.0 + 3.0;

        observed >= limit
    }

    calc def Scale {
        in attribute raw : Real;
        out attribute scaled : Real = raw * 2.0;
    }

    part def Rig;

    part the_rig : Rig {
        attribute sensor_reading : Real = 0.5;
        attribute delivered_power : Real = 55.0;
        attribute observed_value : Real = 9.0;

        calc scale : Scale {
            in raw = sensor_reading;
        }

        assert constraint drift_check : 'Drift Bound' {
            in reading = sensor_reading;
        }

        assert constraint power_check : 'Power Floor' {
            in delivered = delivered_power;
        }

        assert constraint derived_check : 'Derived Bound' {
            in observed = observed_value;
        }
    }
}
