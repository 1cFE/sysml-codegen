package fx {
    private import ScalarValues::*;
    constraint def 'Pos-1' { in observed : Real; observed > 0.0 }
    constraint def Pos_1 { in observed : Real; observed > 1.0 }
    part def Site {
        attribute x : Real = 1.0;
        assert constraint p : 'Pos-1' { in observed = x; }
        assert constraint q : Pos_1 { in observed = x; }
    }
    part site : Site;
}
