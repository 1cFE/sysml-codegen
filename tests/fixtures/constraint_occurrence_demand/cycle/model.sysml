package OccurrenceDemandCycle {
    private import ScalarValues::*;

    calc def PassThrough {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Nonnegative {
        in attribute value : Real;
        value >= 0.0
    }

    part def Leaf {
        attribute reading : Real = 1.0;
    }

    part def Node {
        attribute reading : Real = 2.0;
        part finite : Leaf;
        part recursive : Node;
        calc pass : PassThrough {
            in x = reading;
        }
        assert constraint cycle_check : Nonnegative {
            in value = reading;
        }
    }

    part root : Node;
}
