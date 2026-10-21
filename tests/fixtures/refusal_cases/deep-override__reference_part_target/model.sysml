package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Wheel { attribute r : Real = 1.0; }
    part def Site {
        ref part w : Wheel;
        attribute t : Real = 2.0;
    }
    part site : Site { :>> w.r = 5.0; }
}
