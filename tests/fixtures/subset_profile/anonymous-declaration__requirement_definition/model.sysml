package fx {
    private import ScalarValues::*;
    requirement def { attribute q : Real = 1.0; }
    part def Site { attribute x : Real = 1.0; attribute y : Real = x * 2.0; }
    part site : Site;
}
