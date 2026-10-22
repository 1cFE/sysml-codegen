package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Site {
        attribute a : Real = 1.0;
        calc t_a : Twice { in x = a; }
        calc T_a : Twice { in x = a; }
    }
    part site : Site;
}
