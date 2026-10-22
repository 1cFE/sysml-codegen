package fx {
    private import ScalarValues::*;
    calc def { in v : Real; return r : Real = 2.0 * v; }
    part def Site { attribute x : Real = 1.0; attribute y : Real = x * 2.0; }
    part site : Site;
}
