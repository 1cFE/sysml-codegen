package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def A { attribute r : Real = 1.0; }
    part def B { attribute s : Real = 2.0; }
    part p : A, B { attribute t : Real = r + s; }
}
