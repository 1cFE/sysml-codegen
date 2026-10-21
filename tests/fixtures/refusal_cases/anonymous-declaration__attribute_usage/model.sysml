package fx {
    private import ScalarValues::*;
    part def Site {
        attribute x : Real = 1.0;
        attribute : Real = 2.0;
        attribute y : Real = x * 2.0;
    }
    part site : Site;
}
