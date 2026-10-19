package fx {
    private import ScalarValues::*;
    item def Thing { attribute w : Real = 1.0; }
    part def Rack { attribute cap : Real = 1.0; }
    part def Site {
        item it : Thing { part rk : Rack; }
        attribute y : Real = 2.0;
    }
    part site : Site;
}
