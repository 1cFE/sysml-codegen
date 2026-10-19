package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Site {
        attribute v : Real = 1.0;
        attribute w : Real = 2.0;
        calc a : Twice { in x = v; }
        calc b : Twice { in x = w; }
        attribute 'out x' : Real = a.r;
        attribute out_x : Real = b.r;
    }
    part site : Site;
}
