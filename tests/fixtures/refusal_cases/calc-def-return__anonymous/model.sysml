package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    calc def Anon { in x : Real; return : Real = x * 2; }
    part def Site { attribute a : Real = 1.0; calc c : Anon { in x = a; } }
    part site : Site;
}
