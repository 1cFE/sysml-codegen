package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part p { attribute a : Real = 1.0; }
    part q { private import p::*; attribute t : Real = a * 2; }
}
