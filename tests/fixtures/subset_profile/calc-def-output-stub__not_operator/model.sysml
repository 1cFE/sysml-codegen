package fx {
    private import ScalarValues::*;
    calc def C { in b : Boolean; return r : Boolean = not b; }
    part def Gen { attribute on : Boolean = true; calc t : C { in b = on; } }
    part gen : Gen;
}
