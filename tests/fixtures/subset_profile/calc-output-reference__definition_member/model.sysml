package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Site {
        attribute a : Real = 1.0;
        calc c1 : Twice { in x = a; }
        calc c2 : Twice { in x = a; }
        attribute t : Real = Twice::r;
    }
    part site : Site;
}
