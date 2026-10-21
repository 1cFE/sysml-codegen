package fx {
    private import ScalarValues::*;
    calc def WithMid { in v : Real; attribute t : Real = 3.0 * v; return r : Real = t; }
    part def Site {
        attribute x : Real = 1.0;
        calc c : WithMid { in v = x; }
        attribute y : Real = c.t * 2.0;
    }
    part site : Site;
}
