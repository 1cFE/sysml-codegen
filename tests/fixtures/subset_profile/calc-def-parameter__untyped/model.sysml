package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    calc def U { in x; return r : Real = 2.0; }
    part def Site { attribute a : Real = 1.0; calc c : U { in x = a; } }
    part site : Site;
}
