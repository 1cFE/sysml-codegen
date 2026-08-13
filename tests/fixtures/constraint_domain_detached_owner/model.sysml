package constraint_domain_detached_owner {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    // `Detached` is an attachable owner kind with zero occurrences: nothing in the
    // design types it. Its asserted gate is vacuous -- warning grade, generation
    // continues (invariant 61's coverage case, not invariant 9's authoring error).
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint vacuous_gate {
            value > 0.0
        }
    }

    part def Live {
        attribute reading : Real = 3.0;
        assert constraint reached_gate {
            reading > 0.0
        }
    }

    part the_live : Live;
}
