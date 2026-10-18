package fx {
    private import ScalarValues::*;
    calc def C { in v : Real; out attribute o : Real; return r : Real = v * 2.0; }
    part def Gen { attribute rate : Real = 2.0; calc t : C { in v = rate; } }
    part gen : Gen;
}
