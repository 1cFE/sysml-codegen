package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    calc def Twice { in x : Real; return r : Real = x * 3; }
    part def Site { attribute a : Real = 1.0; calc c : Twice { in x = a; } }
    part site : Site;
}
