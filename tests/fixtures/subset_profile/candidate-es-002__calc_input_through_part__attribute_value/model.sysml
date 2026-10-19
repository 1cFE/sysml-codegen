package fx {
    private import ScalarValues::*;
    calc def TwiceOut { in v : Real; out attribute r : Real = 2.0 * v; }
    part def Inner { attribute x : Real = 1.0; calc c : TwiceOut { in v = x; } }
    part def Site {
        part p : Inner;
        attribute y : Real = p.c.v * 2.0;
    }
    part site : Site;
}
