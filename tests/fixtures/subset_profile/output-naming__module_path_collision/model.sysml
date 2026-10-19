package fx {
    private import ScalarValues::*;
    calc def 'Twice-x' { in x : Real; return r : Real = x * 2; }
    calc def Twice_x { in x : Real; return r : Real = x * 3; }
    part def Site {
        attribute a : Real = 1.0;
        calc p : 'Twice-x' { in x = a; }
        calc q : Twice_x { in x = a; }
    }
    part site : Site;
}
