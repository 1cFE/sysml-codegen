package constraint_coverage_zero_eligible {
    private import ScalarValues::*;

    // The asserted-with-zero-eligible shape: the model authors a real gate, the gate is
    // applicable (asserted, unmarked), and nothing ever instantiates its owner -- so the
    // feasibility denominator is 1 and the assessed count is 0.
    //
    // This is the partial branch of the zero-input aggregator. The package ships a report
    // with an empty input set whose headline is `partial_coverage`, which is the only way a
    // consumer can tell "one gate, never checked" from "no gates at all". Contrast
    // `constraint_domain_plain_forms`, whose bare usages are not asserted and read
    // `not_assessed`.
    //
    // Expected account (source-derived, expected-coverage.md):
    //   1 / 1 / 0 / 1 / 0 / {owner_has_no_occurrences: 1} / partial
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint unreached_gate {
            value > 0.0
        }
    }

    // A live part with no gate at all, so the package has ordinary content beside the
    // constraint domain and the aggregator's emptiness is the gate's doing, not the model's.
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
