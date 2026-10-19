package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def A { attribute r : Real = 1.0; }
    part def B { attribute t : Real = A::r * 2; }
    part b : B;
}
