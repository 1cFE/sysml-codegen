package DemandConstraintOnly {
    private import ScalarValues::*;

    calc def Identity {
        in attribute x : Real = 1.0;
        out attribute y : Real = x;
    }

    constraint def Nonnegative {
        in attribute value : Real;
        value >= 0.0
    }

    part def Source {
        attribute value : Real;
    }

    part def Plant {
        part source : Source;
        calc keep_pipeline : Identity;
        assert constraint constraint_only_check : Nonnegative {
            in value = source.value;
        }
    }

    part plant : Plant {
        :>> source.value = 23.0;
    }
}
