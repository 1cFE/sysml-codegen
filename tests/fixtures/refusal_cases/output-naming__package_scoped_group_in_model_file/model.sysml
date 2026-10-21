package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    attribute a : Real = 1.0;
    calc c : Twice { in x = a; }
}
