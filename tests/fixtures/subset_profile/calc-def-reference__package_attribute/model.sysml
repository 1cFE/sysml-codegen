package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    attribute k : Real = 3.0;
    calc def Scale { in x : Real; return r : Real = x * k; }
    part def Site { attribute a : Real = 1.0; calc c : Scale { in x = a; } }
    part site : Site;
}
