package constraint_coverage_eligible_inapplicable {
    private import ScalarValues::*;

    // D9's refusal fixture. GENERATION MUST FAIL ON THIS MODEL -- that is the whole point,
    // and any corpus sweep that generates every fixture has to expect the refusal.
    //
    // The gate is asserted, its owner is instantiated, so it expands to a concrete entry and
    // produces a real verdict. It also carries an inapplicability marker, which states the
    // gate is not part of the feasible set. Both cannot be true: the gate demonstrably ran.
    // (The marker token is written only in the doc comment below -- the source scanner
    // behind `test_constraint_population_oracle.py` counts every occurrence in the file.)
    //
    // Honouring the marker would make one doc comment a silent kill-switch for a live
    // physics check -- delete the gate from the denominator and the headline reads full
    // satisfaction over a set that quietly shrank. Item 2's mint deliberately reads the
    // marker independently of the disposition and never rewrites it, so the contradiction is
    // only visible once someone asks the coverage question. This item asks it, and refuses.
    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint live_but_marked : Positive {
            doc /* @inapplicable: this gate is not part of the feasible set */
            in v = reading;
        }
    }

    part the_live : Live;
}
