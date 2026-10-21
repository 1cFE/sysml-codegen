package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Wheel { attribute r : Real = 1.0; }
    part def Site {
        part w : Wheel [2];
        attribute t : Real = w.r * 2;
    }
    part site : Site;
}
