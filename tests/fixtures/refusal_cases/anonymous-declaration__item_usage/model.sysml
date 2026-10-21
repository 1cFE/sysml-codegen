package fx {
    private import ScalarValues::*;
    item def Thing { attribute w : Real = 1.0; }
    part def Site {
        attribute x : Real = 1.0;
        item : Thing;
        attribute y : Real = x * 2.0;
    }
    part site : Site;
}
