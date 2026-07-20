package NonFiniteLiteral {
    private import ScalarValues::*;

    // =====================================================================
    // A blocking extraction diagnostic, end to end (Item 4, DD-A03).
    //
    // `1.0e400` overflows to `inf`, which `constraint_extraction` reports as
    // `kind="non_finite_literal"` — the one diagnostic kind in the writer-side
    // severity table, classified BLOCKING. A non-finite operand cannot be
    // evaluated downstream, so a generated package that ran with it would
    // publish a number nobody can act on.
    //
    // This fixture exists because the audit found both sinks entirely unpinned
    // (audit F3): correct by direct execution, but with zero test coverage, so
    // an ordering or rendering regression had nothing to catch it.
    //
    // **Source**: authored fixture (CONSTRAINT-LIFECYCLE-REMEDIATION Item 4)
    // **Reference**: audit.md F1/F3; spec DD-R08, DD-R09; DD-A03
    // =====================================================================

    calc def Scale {
        in attribute factor : Real;
        out attribute scaled : Real = factor * 2.0;
    }

    part def Rig;

    part the_rig : Rig {
        attribute reading : Real = 1.0;

        calc scale : Scale {
            in factor = reading;
        }

        assert constraint overflow_check {
            reading <= 1.0e400
        }
    }
}
