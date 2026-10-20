package fx {
    private import ScalarValues::*;
    calc def C { in v : Real; attribute a : Real = b + v; attribute b : Real = a + v; return r : Real = a; }
    part def Gen { attribute rate : Real = 2.0; calc t : C { in v = rate; } }
    part gen : Gen;
}
