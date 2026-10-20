package fx {
    private import ScalarValues::*;
    part def Rack { attribute cap : Real = 1.0; }
    part def Site {
        attribute x : Real = 1.0;
        part : Rack;
    }
    part site : Site;
}
