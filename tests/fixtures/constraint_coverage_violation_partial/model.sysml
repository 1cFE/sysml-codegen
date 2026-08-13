package constraint_coverage_violation_partial {
    private import ScalarValues::*;

    // Coverage survives a higher-precedence headline. One gate is assessed and fails; a
    // second applicable gate is never checked. The headline reads `violation` -- the top
    // precedence arm, unchanged -- and the account beside it still says
    // `coverage_state = "partial"` with one unassessed gate.
    //
    // That combination is spec success criterion 2, and it is the distinction the study
    // policy needs: "rejected on physics, fully covered" is a different candidate from
    // "rejected on physics, and a gate nobody checked".
    //
    // The verdict is hand-derived, not read back: `reading` is 3.0 against a bound of 10.0,
    // so `3.0 > 10.0` is false and the margin is -7.0.
    //
    // Expected account (source-derived, expected-coverage.md):
    //   2 / 2 / 1 / 1 / 0 / {owner_has_no_occurrences: 1} / partial
    part def Live {
        attribute reading : Real = 3.0;
        assert constraint failing_gate {
            reading > 10.0
        }
    }

    // Asserted, unmarked, and nothing types it -- so it stays in the denominator as an
    // unassessed gate rather than dropping out of it.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint unreached_gate {
            value > 0.0
        }
    }

    part the_live : Live;
}
