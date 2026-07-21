package OccurrenceDemandCycleIndirect {
    private import ScalarValues::*;

    calc def PassThrough {
        in attribute x : Real;
        out attribute y : Real = x;
    }

    constraint def Nonnegative {
        in attribute value : Real;
        value >= 0.0
    }

    part def B;

    part def A {
        attribute reading : Real = 2.0;
        part b : B;
        assert constraint a_check : Nonnegative {
            in value = reading;
        }
    }

    part def B {
        part a : A;
    }

    calc keep_pipeline : PassThrough {
        in x = 1.0;
    }

    part root : A;
}
