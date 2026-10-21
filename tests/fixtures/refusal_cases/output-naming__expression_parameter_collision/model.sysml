package fx {
    private import ScalarValues::*;
    part def Site {
        attribute 'a b' : Real = 1.0;
        attribute a_b : Real = 2.0;
        attribute t : Real = 'a b' + a_b;
    }
    part site : Site;
}
