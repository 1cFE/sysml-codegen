package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Site { calc c : Twice { in x = *; } }
    part site : Site;
}
