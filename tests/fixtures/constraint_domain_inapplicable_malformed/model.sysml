package constraint_domain_inapplicable_malformed {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    // The marker with no `: <reason>` after it. A near-miss must halt: silently ignoring
    // it is indistinguishable from never having written it.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint typo_marker : Positive {
            doc /* @inapplicable no colon and no reason */
            in v = value;
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
