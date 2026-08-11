package ArithmeticRaise {
    private import ScalarValues::*;

    // =====================================================================
    // The generated constraint wrapper must let a native arithmetic failure
    // propagate, rather than swallowing it and constructing evidence from a
    // value that was never computed. A ratio predicate is the smallest shape
    // that can raise: with `divisor = 0.0` the predicate body raises
    // ZeroDivisionError before any verdict exists.
    //
    // Authored 2026-08-11 for recovery plan Gate 4C part 7 as the exact-route
    // execution specimen for the arithmetic-exception responsibility carried
    // by `tests/execution/test_constraint_execution.py` (row L-192). Written
    // in D-5 binding form from the start, so the exact route admits it and no
    // variant is needed.
    // =====================================================================

    calc def Identity {
        in attribute value_in : Real;
        out attribute value_out : Real = value_in;
    }

    constraint def 'Ratio Within Bound' {
        in attribute numerator_in : Real;
        in attribute divisor_in : Real;
        in attribute bound_in : Real default 10.0;

        numerator_in / divisor_in <= bound_in
    }

    part def Meter {
        attribute numerator : Real = 6.0;
        attribute divisor : Real = 2.0;

        calc passthrough : Identity {
            in value_in = numerator;
        }

        assert constraint ratio : 'Ratio Within Bound' {
            in numerator_in = numerator;
            in divisor_in = divisor;
        }
    }

    part def Rig {
        part meter : Meter;
    }

    part the_rig : Rig;
}
