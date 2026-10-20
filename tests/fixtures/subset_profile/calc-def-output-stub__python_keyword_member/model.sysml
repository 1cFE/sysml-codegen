package fx {
    private import ScalarValues::*;
    calc def C { in v : Real; attribute 'if' : Real = 2.0 * v; return r : Real = 'if' + 1.0; }
    part def Gen { attribute rate : Real = 2.0; calc t : C { in v = rate; } }
    part gen : Gen;
}
