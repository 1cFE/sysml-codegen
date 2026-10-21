package fx {
    private import ScalarValues::*;
    constraint def Positive { in observed : Real; observed > 0.0 }
    part def Site {
        attribute x : Real = 1.0;
        constraint k1 : Positive { in observed = x; }
        assert constraint k2 :> k1;
    }
    part site : Site;
}
