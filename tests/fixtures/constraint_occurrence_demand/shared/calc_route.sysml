package DemandSharedLibrary {
    private import ScalarValues::*;

    part def Source {
        attribute value : Real;
    }

    calc def Consume {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Nonnegative {
        in attribute value : Real;
        value >= 0.0
    }

    part def Plant {
        part source : Source;
        calc consume : Consume {
            in x = source.value;
        }
        assert constraint shared_check : Nonnegative {
            in value = source.value;
        }
    }
}
