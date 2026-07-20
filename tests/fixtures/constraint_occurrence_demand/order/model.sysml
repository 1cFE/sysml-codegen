package DemandOrder {
    private import ScalarValues::*;

    part def Source {
        attribute a_collision : Real;
        attribute b_nonliteral : Real;
        attribute c_clean : Real;
    }

    calc def Consume {
        in attribute a : Real;
        in attribute b : Real;
        in attribute c : Real;
        out attribute total : Real = a + b + c;
    }

    constraint def Positive {
        in attribute value : Real;
        value >= 0.0
    }

    part def Plant {
        part source : Source;
        calc consume : Consume {
            in a = source.a_collision;
            in b = source.b_nonliteral;
            in c = source.c_clean;
        }
        assert constraint a_check : Positive {
            in value = source.a_collision;
        }
        assert constraint b_check : Positive {
            in value = source.b_nonliteral;
        }
        assert constraint c_check : Positive {
            in value = source.c_clean;
        }
    }

    part plant : Plant {
        :>> source.a_collision = 11.0;
        :>> source.b_nonliteral = 22.0;
        :>> source.c_clean = 33.0;
    }
}
