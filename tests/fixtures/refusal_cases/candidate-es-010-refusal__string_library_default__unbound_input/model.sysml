package fx {
    private import ScalarValues::*;
    calc def Labelled { in v : Real; in u : String default "liter"; return r : Real = 2.0 * v; }
    part def Gen { attribute rate : Real; calc t : Labelled { in v = rate; } }
    part gen : Gen { :>> rate = 2.0; }
}
