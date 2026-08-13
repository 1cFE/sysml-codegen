package constraint_domain_inapplicable {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Positive {
        in v : Real;
        v > 0.0
    }

    // An explicitly-marked vacuous gate. The annotation is a coverage statement: it tells
    // a later feasibility count that this gate was never meant to be part of the set. It
    // does not, and must not, change the gate's disposition.
    part def Detached {
        attribute value : Real = 5.0;
        assert constraint marked_vacuous : Positive {
            doc /* @inapplicable: no build of this variant is planned */
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
