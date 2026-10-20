package fx {
    private import ScalarValues::*;
    part def Rack { attribute cap : Real = 1.0; }
    action def Act;
    part def Site {
        attribute x : Real = 1.0;
        action : Act { part p : Rack; }
    }
    part site : Site;
}
