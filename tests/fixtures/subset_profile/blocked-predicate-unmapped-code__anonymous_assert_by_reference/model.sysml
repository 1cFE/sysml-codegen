package fx {
    private import ScalarValues::*;
    constraint def Positive { in observed : Real; observed > 0.0 }
    part def Site {
        attribute x : Real = 1.0;
        constraint positive : Positive { in observed = x; }
        assert positive;
    }
    part site : Site;
}
