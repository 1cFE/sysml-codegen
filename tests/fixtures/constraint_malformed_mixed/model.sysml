package constraint_malformed_mixed {
    private import ScalarValues::*;

    calc def Noop {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    part def MalformedHost {
        attribute value : Real = 5.0;
        attribute flag : Boolean = true;

        assert constraint mixed_claim {
            value > 0.0 and flag
        }
    }

    part the_host : MalformedHost;
}
