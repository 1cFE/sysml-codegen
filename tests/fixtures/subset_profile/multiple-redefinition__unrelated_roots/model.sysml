package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def A { attribute a : Real; attribute b : Real; }
    part def B :> A { attribute x :>> a, b = 1.0; attribute t : Real = x * 2; }
    part site : B;
}
