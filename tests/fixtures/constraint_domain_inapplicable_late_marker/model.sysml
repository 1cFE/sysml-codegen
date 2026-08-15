package constraint_domain_inapplicable_late_marker {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    // The marker on a second documentation body. The annotation is read only on the first
    // line of the joined documentation, so this halts rather than being quietly missed.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint late_marker : Positive {
            doc /* an ordinary description */
            doc /* @inapplicable: buried where nothing reads it */
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
