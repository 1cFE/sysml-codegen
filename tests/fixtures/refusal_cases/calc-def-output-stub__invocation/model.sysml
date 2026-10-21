package fx {
    private import ScalarValues::*;
    private import NumericalFunctions::sum;
    calc def C { in v : Real; return r : Real = sum((v, 1.0)); }
    part def Gen { attribute rate : Real = 2.0; calc t : C { in v = rate; } }
    part gen : Gen;
}
