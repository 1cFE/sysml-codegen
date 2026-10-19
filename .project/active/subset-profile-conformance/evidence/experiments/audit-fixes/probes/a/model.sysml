package fx {
    private import ScalarValues::*;
    part def Rack { attribute cap : Real = 1.0; }
    item def Thing { part rk : Rack; }
    part def Site {
        item it : Thing;
        attribute y : Real = 2.0;
    }
    part site : Site;
}
