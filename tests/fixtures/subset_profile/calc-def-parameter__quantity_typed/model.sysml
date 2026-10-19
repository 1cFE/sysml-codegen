package fx {
    private import ScalarValues::*;
    private import ISQ::*;
    calc def U { in m : MassValue; return r : Real = 2.0; }
    part def Site { attribute a : MassValue; calc c : U { in m = a; } }
    part site : Site;
}
