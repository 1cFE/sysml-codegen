package fx {
    private import ScalarValues::*;
    calc def Twice { in x : Real; return r : Real = x * 2; }
    part def Wheel { attribute r : Real = 1.0; attribute d : Real = r * 2; }
    part def Site {
        part w : Wheel;
        calc c : Twice { in x = w.d; }
    }
    part site : Site { :>> w.d = 5.0; }
}
