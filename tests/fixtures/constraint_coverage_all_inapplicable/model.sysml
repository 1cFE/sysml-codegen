package constraint_coverage_all_inapplicable {
    private import ScalarValues::*;

    // D4's ruling, in its degenerate form: every asserted gate the model authors carries an
    // explicit inapplicability marker, so the feasibility denominator is empty and there is
    // no gate left to have passed.
    //
    // The ruling is that this reads `not_assessed`, not `full_satisfaction`. Appendix C's
    // vacuous-gate cell drops a marked gate out of the denominator and reads full
    // satisfaction "when every remaining gate passed" -- with zero remaining gates that
    // antecedent is vacuous, and awarding the vocabulary's strongest claim for zero
    // assessments is the defect this item exists to end.
    //
    // What separates this from a descriptive-only model like `catf_mfe_d5` is
    // `inapplicable_gate_count`: positive here, zero there. A consumer that wants "all gates
    // were deliberately waived" reads that field.
    //
    // Expected account (source-derived, expected-coverage.md):
    //   1 / 0 / 0 / 0 / 1 / {} / none
    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    part def Detached {
        attribute value : Real = 5.0;
        assert constraint waived_gate : Positive {
            doc /* @inapplicable: this variant is documentation only */
            in v = value;
        }
    }

    calc def Doubler {
        in attribute seed : Real;
        out attribute doubled : Real = seed * 2.0;
    }

    part def Live {
        attribute reading : Real = 3.0;
        calc double : Doubler {
            in seed = reading;
        }
    }

    part the_live : Live;
}
