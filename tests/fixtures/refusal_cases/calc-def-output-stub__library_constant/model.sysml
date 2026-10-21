package fx {
    private import ScalarValues::*;
    private import TrigFunctions::pi;
    calc def C { in v : Real; return r : Real = v * pi; }
    part def Gen { attribute rate : Real = 2.0; calc t : C { in v = rate; } }
    part gen : Gen;
}
