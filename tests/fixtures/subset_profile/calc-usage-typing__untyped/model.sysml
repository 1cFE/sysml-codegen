package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Site {
        attribute a : Real = 1.0;
        calc c { in x = a; }
        calc d : Twice { in x = a; }
    }
    part site : Site;
}
