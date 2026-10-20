package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def P;
    calc def Mk { in x : Real; out part p : P; return r : Real = x; }
    part def Site {
        attribute a : Real = 1.0;
        calc c : Mk { in x = a; }
    }
    part site : Site;
}
