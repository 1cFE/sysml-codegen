package fx {
    private import ScalarValues::*;
    constraint def Positive { in value : Real; value > 0.0 }
    part def Site {
        attribute x : Real = 1.0;
        assert constraint positive : Positive { in value = x; }
    }
    part site : Site;
}
